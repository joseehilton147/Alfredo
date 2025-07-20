"""
Comando CLI para processamento em lote de arquivos de vídeo.

Implementa o comando específico para processamento de múltiplos arquivos,
incluindo processamento paralelo controlado, relatório de progresso e
tratamento individual de erros sem parar o lote completo.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm

from src.presentation.cli.base_command import Command
from src.presentation.cli.local_video_command import LocalVideoCommand
from src.application.use_cases.process_local_video import (
    ProcessLocalVideoUseCase,
    ProcessLocalVideoRequest,
    ProcessLocalVideoResponse
)
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
    AlfredoError
)


@dataclass
class BatchProcessingResult:
    """Resultado do processamento em lote."""
    
    total_files: int
    successful: int
    failed: int
    skipped: int
    results: List[Tuple[str, bool, Optional[str]]]  # (file_path, success, error_msg)
    total_transcription_chars: int
    processing_time: float


class BatchCommand(Command):
    """
    Comando para processamento em lote de arquivos de vídeo.
    
    Responsabilidades:
    - Descobrir arquivos de vídeo em diretórios
    - Processar múltiplos arquivos com controle de paralelismo
    - Gerar relatório detalhado de resultados
    - Tratar erros individuais sem parar o lote
    """

    # Formatos de vídeo suportados (herdados do LocalVideoCommand)
    SUPPORTED_FORMATS = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', 
        '.flv', '.webm', '.m4v', '.3gp', '.ogv'
    }

    def __init__(self, config: AlfredoConfig, factory: InfrastructureFactory):
        """
        Inicializa o comando de processamento em lote.
        
        Args:
            config: Configuração do Alfredo AI
            factory: Factory para criação de dependências
        """
        super().__init__(config, factory)
        self.use_case: Optional[ProcessLocalVideoUseCase] = None
        self._progress_bar: Optional[tqdm] = None
        self._cancelled = False

    def validate_args(self, directory: str, **kwargs) -> bool:
        """
        Valida argumentos específicos do comando de lote.
        
        Args:
            directory: Diretório com arquivos de vídeo
            **kwargs: Argumentos adicionais
            
        Returns:
            True se argumentos são válidos, False caso contrário
        """
        if not directory:
            print("❌ Diretório é obrigatório para processamento em lote")
            return False

        # Verificar se diretório existe
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ Diretório não encontrado: {directory}")
            return False

        # Verificar se é um diretório
        if not dir_path.is_dir():
            print(f"❌ Caminho deve ser um diretório: {directory}")
            return False

        # Verificar permissões de leitura
        import os
        if not os.access(dir_path, os.R_OK):
            print(f"❌ Sem permissão de leitura para o diretório: {directory}")
            return False

        # Validar idioma se fornecido
        language = kwargs.get('language', 'pt')
        supported_languages = ['pt', 'en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh']
        
        if language not in supported_languages:
            print(f"❌ Idioma '{language}' não suportado")
            print(f"   Idiomas suportados: {', '.join(supported_languages)}")
            return False

        # Validar max_workers se fornecido
        max_workers = kwargs.get('max_workers', self.config.max_concurrent_downloads)
        if max_workers < 1 or max_workers > 10:
            print(f"❌ max_workers deve estar entre 1 e 10, recebido: {max_workers}")
            return False

        return True

    async def execute(
        self,
        directory: str,
        language: str = "pt",
        recursive: bool = False,
        force_reprocess: bool = False,
        max_workers: int = None,
        file_pattern: str = "*"
    ) -> BatchProcessingResult:
        """
        Executa o processamento em lote de arquivos de vídeo.
        
        Args:
            directory: Diretório com arquivos de vídeo
            language: Idioma para transcrição (padrão: pt)
            recursive: Buscar arquivos recursivamente em subdiretórios
            force_reprocess: Forçar reprocessamento mesmo se já existe
            max_workers: Número máximo de workers paralelos
            file_pattern: Padrão para filtrar arquivos (ex: "*.mp4")
            
        Returns:
            Resultado do processamento em lote
            
        Raises:
            InvalidVideoFormatError: Se diretório for inválido
            ConfigurationError: Se configuração for inválida
        """
        import time
        start_time = time.time()

        # Validar argumentos
        if max_workers is None:
            max_workers = self.config.max_concurrent_downloads

        if not self.validate_args(directory, language=language, max_workers=max_workers):
            raise InvalidVideoFormatError(
                "arguments", 
                directory, 
                "argumentos inválidos"
            )

        # Descobrir arquivos de vídeo
        video_files = self._discover_video_files(
            directory, recursive, file_pattern
        )

        if not video_files:
            print(f"⚠️  Nenhum arquivo de vídeo encontrado em: {directory}")
            return BatchProcessingResult(
                total_files=0,
                successful=0,
                failed=0,
                skipped=0,
                results=[],
                total_transcription_chars=0,
                processing_time=0
            )

        self.log_execution_start(
            "processamento em lote",
            directory=directory,
            total_files=len(video_files),
            language=language,
            max_workers=max_workers
        )

        # Criar use case com dependências injetadas
        self.use_case = ProcessLocalVideoUseCase(
            extractor=self.factory.create_audio_extractor(),
            ai_provider=self.factory.create_ai_provider(),
            storage=self.factory.create_storage(),
            config=self.config
        )

        try:
            # Inicializar barra de progresso
            self._progress_bar = tqdm(
                total=len(video_files),
                desc="🎬 Processando lote",
                unit="arquivo",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} arquivos {desc}"
            )

            # Processar arquivos com controle de paralelismo
            results = await self._process_files_parallel(
                video_files, language, force_reprocess, max_workers
            )

            # Finalizar barra de progresso
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None

            # Calcular estatísticas
            processing_time = time.time() - start_time
            batch_result = self._calculate_batch_statistics(
                video_files, results, processing_time
            )

            # Exibir relatório
            self._display_batch_report(batch_result)

            self.log_execution_success(
                "processamento em lote",
                total_files=batch_result.total_files,
                successful=batch_result.successful,
                failed=batch_result.failed,
                processing_time=processing_time
            )

            return batch_result

        except KeyboardInterrupt:
            # Cancelar processamento se interrompido
            self._cancelled = True
            
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None
                
            print("\n⚠️  Processamento em lote cancelado pelo usuário")
            raise ConfigurationError(
                "batch_processing",
                "Processamento cancelado pelo usuário",
                expected="processamento completo"
            )

        except Exception as error:
            # Fechar barra de progresso em caso de erro
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None

            self.log_execution_error(
                "processamento em lote",
                error,
                directory=directory,
                total_files=len(video_files)
            )
            
            # Re-lançar exceções específicas do domínio
            if isinstance(error, (InvalidVideoFormatError, ConfigurationError)):
                raise
            
            # Converter erros inesperados
            raise ConfigurationError(
                "batch_processing",
                f"Erro inesperado no processamento em lote: {str(error)}",
                expected="processamento bem-sucedido"
            )

    def _discover_video_files(
        self, directory: str, recursive: bool, file_pattern: str
    ) -> List[Path]:
        """
        Descobre arquivos de vídeo no diretório.
        
        Args:
            directory: Diretório para buscar
            recursive: Buscar recursivamente
            file_pattern: Padrão de arquivos
            
        Returns:
            Lista de caminhos de arquivos de vídeo
        """
        dir_path = Path(directory)
        video_files = []

        # Função para buscar arquivos
        if recursive:
            pattern_func = dir_path.rglob
        else:
            pattern_func = dir_path.glob

        # Buscar arquivos que correspondem ao padrão
        for file_path in pattern_func(file_pattern):
            if (file_path.is_file() and 
                file_path.suffix.lower() in self.SUPPORTED_FORMATS):
                video_files.append(file_path)

        # Ordenar por nome para processamento consistente
        video_files.sort(key=lambda x: x.name.lower())
        
        return video_files

    async def _process_files_parallel(
        self,
        video_files: List[Path],
        language: str,
        force_reprocess: bool,
        max_workers: int
    ) -> List[Tuple[str, bool, Optional[str], Optional[ProcessLocalVideoResponse]]]:
        """
        Processa arquivos em paralelo com controle de concorrência.
        
        Args:
            video_files: Lista de arquivos para processar
            language: Idioma para transcrição
            force_reprocess: Forçar reprocessamento
            max_workers: Número máximo de workers
            
        Returns:
            Lista de resultados (file_path, success, error_msg, response)
        """
        semaphore = asyncio.Semaphore(max_workers)
        tasks = []

        for video_file in video_files:
            if self._cancelled:
                break
                
            task = self._process_single_file_with_semaphore(
                semaphore, video_file, language, force_reprocess
            )
            tasks.append(task)

        # Executar todas as tarefas
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados e exceções
        processed_results = []
        for i, result in enumerate(results):
            file_path = str(video_files[i])
            
            if isinstance(result, Exception):
                processed_results.append((file_path, False, str(result), None))
            else:
                processed_results.append(result)

        return processed_results

    async def _process_single_file_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        video_file: Path,
        language: str,
        force_reprocess: bool
    ) -> Tuple[str, bool, Optional[str], Optional[ProcessLocalVideoResponse]]:
        """
        Processa um único arquivo com controle de semáforo.
        
        Args:
            semaphore: Semáforo para controle de concorrência
            video_file: Arquivo a ser processado
            language: Idioma para transcrição
            force_reprocess: Forçar reprocessamento
            
        Returns:
            Tupla com resultado do processamento
        """
        async with semaphore:
            if self._cancelled:
                return (str(video_file), False, "Cancelado pelo usuário", None)

            try:
                # Criar request
                request = ProcessLocalVideoRequest(
                    file_path=str(video_file),
                    language=language,
                    force_reprocess=force_reprocess,
                    progress_callback=None  # Sem callback individual para lote
                )

                # Executar processamento
                response = await self.use_case.execute(request)

                # Atualizar barra de progresso
                if self._progress_bar:
                    self._progress_bar.update(1)
                    self._progress_bar.set_description(
                        f"🎬 Processado: {video_file.name}"
                    )

                return (str(video_file), True, None, response)

            except AlfredoError as e:
                # Erro específico do domínio
                if self._progress_bar:
                    self._progress_bar.update(1)
                    self._progress_bar.set_description(
                        f"❌ Erro: {video_file.name}"
                    )
                
                return (str(video_file), False, e.message, None)

            except Exception as e:
                # Erro inesperado
                if self._progress_bar:
                    self._progress_bar.update(1)
                    self._progress_bar.set_description(
                        f"❌ Erro: {video_file.name}"
                    )
                
                return (str(video_file), False, str(e), None)

    def _calculate_batch_statistics(
        self,
        video_files: List[Path],
        results: List[Tuple[str, bool, Optional[str], Optional[ProcessLocalVideoResponse]]],
        processing_time: float
    ) -> BatchProcessingResult:
        """
        Calcula estatísticas do processamento em lote.
        
        Args:
            video_files: Lista de arquivos processados
            results: Resultados do processamento
            processing_time: Tempo total de processamento
            
        Returns:
            Resultado consolidado do lote
        """
        successful = sum(1 for _, success, _, _ in results if success)
        failed = sum(1 for _, success, _, _ in results if not success)
        skipped = 0  # Para implementação futura
        
        total_chars = 0
        simple_results = []
        
        for file_path, success, error_msg, response in results:
            simple_results.append((file_path, success, error_msg))
            
            if success and response and response.transcription:
                total_chars += len(response.transcription)

        return BatchProcessingResult(
            total_files=len(video_files),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=simple_results,
            total_transcription_chars=total_chars,
            processing_time=processing_time
        )

    def _display_batch_report(self, result: BatchProcessingResult) -> None:
        """
        Exibe relatório detalhado do processamento em lote.
        
        Args:
            result: Resultado do processamento em lote
        """
        print(f"\n📊 Relatório do Processamento em Lote")
        print(f"{'='*50}")
        print(f"📁 Total de arquivos: {result.total_files}")
        print(f"✅ Processados com sucesso: {result.successful}")
        print(f"❌ Falharam: {result.failed}")
        print(f"⏭️  Ignorados: {result.skipped}")
        print(f"📝 Total de caracteres transcritos: {result.total_transcription_chars:,}")
        print(f"⏱️  Tempo total: {result.processing_time:.1f}s")
        
        if result.total_files > 0:
            success_rate = (result.successful / result.total_files) * 100
            print(f"📈 Taxa de sucesso: {success_rate:.1f}%")

        # Exibir erros se houver
        failed_files = [(path, error) for path, success, error in result.results 
                       if not success and error]
        
        if failed_files:
            print(f"\n❌ Arquivos com erro:")
            for file_path, error_msg in failed_files[:10]:  # Mostrar apenas os primeiros 10
                file_name = Path(file_path).name
                print(f"   • {file_name}: {error_msg}")
            
            if len(failed_files) > 10:
                print(f"   ... e mais {len(failed_files) - 10} arquivos")

    def get_command_info(self) -> dict:
        """
        Retorna informações específicas do comando de lote.
        
        Returns:
            Dicionário com informações do comando
        """
        return {
            "name": "batch",
            "description": "Processa múltiplos arquivos de vídeo em lote",
            "class": self.__class__.__name__,
            "usage": "batch <directory> [--language pt] [--recursive] [--max-workers 3]",
            "supported_formats": list(self.SUPPORTED_FORMATS),
            "examples": [
                "batch /path/to/videos/",
                "batch ./videos --language en --recursive",
                "batch ~/Downloads --max-workers 2 --force"
            ]
        }