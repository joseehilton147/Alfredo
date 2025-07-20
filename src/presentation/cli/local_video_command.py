"""
Comando CLI para processamento de arquivos de vídeo locais.

Implementa o comando específico para processamento de arquivos de vídeo locais,
incluindo validação de arquivos, suporte a diferentes formatos e integração
com o ProcessLocalVideoUseCase.
"""

import os
from pathlib import Path
from typing import Optional
from tqdm import tqdm

from src.presentation.cli.base_command import Command
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
    ConfigurationError
)


class LocalVideoCommand(Command):
    """
    Comando para processamento de arquivos de vídeo locais.
    
    Responsabilidades:
    - Validar existência e formato de arquivos
    - Executar processamento via use case
    - Exibir progresso com tqdm
    - Suportar diferentes formatos de vídeo
    """

    # Formatos de vídeo suportados
    SUPPORTED_FORMATS = {
        '.mp4': 'MP4 Video',
        '.avi': 'AVI Video',
        '.mkv': 'Matroska Video',
        '.mov': 'QuickTime Video',
        '.wmv': 'Windows Media Video',
        '.flv': 'Flash Video',
        '.webm': 'WebM Video',
        '.m4v': 'iTunes Video',
        '.3gp': '3GPP Video',
        '.ogv': 'Ogg Video'
    }

    def __init__(self, config: AlfredoConfig, factory: InfrastructureFactory):
        """
        Inicializa o comando de vídeo local.
        
        Args:
            config: Configuração do Alfredo AI
            factory: Factory para criação de dependências
        """
        super().__init__(config, factory)
        self.use_case: Optional[ProcessLocalVideoUseCase] = None
        self._progress_bar: Optional[tqdm] = None

    def validate_args(self, file_path: str, **kwargs) -> bool:
        """
        Valida argumentos específicos do comando de vídeo local.
        
        Args:
            file_path: Caminho do arquivo de vídeo
            **kwargs: Argumentos adicionais
            
        Returns:
            True se argumentos são válidos, False caso contrário
        """
        if not file_path:
            print("❌ Caminho do arquivo é obrigatório")
            return False

        # Verificar se arquivo existe
        video_path = Path(file_path)
        if not video_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False

        # Verificar se é um arquivo (não diretório)
        if not video_path.is_file():
            print(f"❌ Caminho deve ser um arquivo, não um diretório: {file_path}")
            return False

        # Verificar formato suportado
        file_extension = video_path.suffix.lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            print(f"❌ Formato de arquivo não suportado: {file_extension}")
            print("   Formatos suportados:")
            for ext, desc in self.SUPPORTED_FORMATS.items():
                print(f"   - {ext} ({desc})")
            return False

        # Verificar tamanho do arquivo
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        max_size_mb = self.config.max_file_size_mb
        
        if file_size_mb > max_size_mb:
            print(f"❌ Arquivo muito grande: {file_size_mb:.1f}MB")
            print(f"   Tamanho máximo permitido: {max_size_mb}MB")
            return False

        # Verificar permissões de leitura
        if not os.access(video_path, os.R_OK):
            print(f"❌ Sem permissão de leitura para o arquivo: {file_path}")
            return False

        # Validar idioma se fornecido
        language = kwargs.get('language', 'pt')
        supported_languages = ['pt', 'en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh']
        
        if language not in supported_languages:
            print(f"❌ Idioma '{language}' não suportado")
            print(f"   Idiomas suportados: {', '.join(supported_languages)}")
            return False

        return True

    async def execute(
        self,
        file_path: str,
        language: str = "pt",
        force_reprocess: bool = False
    ) -> ProcessLocalVideoResponse:
        """
        Executa o processamento de arquivo de vídeo local.
        
        Args:
            file_path: Caminho do arquivo de vídeo
            language: Idioma para transcrição (padrão: pt)
            force_reprocess: Forçar reprocessamento mesmo se já existe
            
        Returns:
            Resposta do processamento com vídeo e transcrição
            
        Raises:
            InvalidVideoFormatError: Se arquivo for inválido
            TranscriptionError: Se falhar a transcrição
            ConfigurationError: Se configuração for inválida
        """
        # Validar argumentos
        if not self.validate_args(file_path, language=language):
            raise InvalidVideoFormatError(
                "arguments", 
                file_path, 
                "argumentos inválidos"
            )

        # Obter caminho absoluto
        absolute_path = str(Path(file_path).resolve())

        # Criar use case com dependências injetadas
        self.use_case = ProcessLocalVideoUseCase(
            extractor=self.factory.create_audio_extractor(),
            ai_provider=self.factory.create_ai_provider(),
            storage=self.factory.create_storage(),
            config=self.config
        )

        # Configurar request
        request = ProcessLocalVideoRequest(
            file_path=absolute_path,
            language=language,
            force_reprocess=force_reprocess,
            progress_callback=self._update_progress
        )

        self.log_execution_start(
            "processamento de vídeo local",
            file_path=absolute_path,
            language=language,
            file_size_mb=Path(absolute_path).stat().st_size / (1024 * 1024)
        )

        try:
            # Inicializar barra de progresso
            self._progress_bar = tqdm(
                total=100,
                desc="🎬 Processando vídeo local",
                unit="%",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {desc}"
            )

            # Executar processamento
            response = await self.use_case.execute(request)

            # Finalizar barra de progresso
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None

            # Exibir resultado
            self._display_local_video_result(response)

            self.log_execution_success(
                "processamento de vídeo local",
                video_title=response.video.title,
                transcription_length=len(response.transcription),
                was_cached=response.was_cached
            )

            return response

        except KeyboardInterrupt:
            # Cancelar processamento se interrompido
            if self.use_case:
                await self.use_case.cancel_processing()
            
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None
                
            print("\n⚠️  Processamento cancelado pelo usuário")
            raise TranscriptionError(
                absolute_path, 
                "Processamento cancelado pelo usuário"
            )

        except Exception as error:
            # Fechar barra de progresso em caso de erro
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None

            self.log_execution_error(
                "processamento de vídeo local",
                error,
                file_path=absolute_path,
                language=language
            )
            
            # Re-lançar exceções específicas do domínio
            if isinstance(error, (TranscriptionError, InvalidVideoFormatError, 
                                ConfigurationError)):
                raise
            
            # Converter erros inesperados
            raise ConfigurationError(
                "local_video_processing",
                f"Erro inesperado no processamento: {str(error)}",
                expected="processamento bem-sucedido"
            )

    def _update_progress(self, percentage: int, message: str) -> None:
        """
        Atualiza a barra de progresso.
        
        Args:
            percentage: Porcentagem de progresso (0-100)
            message: Mensagem de status atual
        """
        if self._progress_bar:
            # Atualizar progresso
            self._progress_bar.n = percentage
            self._progress_bar.set_description(f"🎬 {message}")
            self._progress_bar.refresh()

    def _display_local_video_result(self, response: ProcessLocalVideoResponse) -> None:
        """
        Exibe resultado específico do processamento de vídeo local.
        
        Args:
            response: Resposta do processamento
        """
        video = response.video
        video_path = Path(video.file_path)
        
        print(f"\n✅ Vídeo local processado com sucesso!")
        print(f"📁 Arquivo: {video_path.name}")
        print(f"📂 Diretório: {video_path.parent}")
        
        # Exibir informações do arquivo
        if video.metadata:
            file_size_mb = video.metadata.get('file_size', 0) / (1024 * 1024)
            print(f"💾 Tamanho: {file_size_mb:.1f} MB")
            
            file_ext = video.metadata.get('file_extension', '')
            if file_ext in self.SUPPORTED_FORMATS:
                print(f"🎞️  Formato: {self.SUPPORTED_FORMATS[file_ext]}")
        
        if video.duration:
            duration_min = int(video.duration // 60)
            duration_sec = int(video.duration % 60)
            print(f"⏱️  Duração: {duration_min}:{duration_sec:02d}")
        
        print(f"📝 Transcrição: {len(response.transcription)} caracteres")
        
        if response.was_cached:
            print("♻️  Resultado obtido do cache (já processado anteriormente)")
        else:
            print("🆕 Novo processamento realizado")

    def get_supported_formats(self) -> dict:
        """
        Retorna formatos de vídeo suportados.
        
        Returns:
            Dicionário com extensões e descrições dos formatos suportados
        """
        return self.SUPPORTED_FORMATS.copy()

    def get_command_info(self) -> dict:
        """
        Retorna informações específicas do comando de vídeo local.
        
        Returns:
            Dicionário com informações do comando
        """
        return {
            "name": "local",
            "description": "Processa arquivos de vídeo locais com transcrição",
            "class": self.__class__.__name__,
            "usage": "local <file_path> [--language pt] [--force]",
            "supported_formats": list(self.SUPPORTED_FORMATS.keys()),
            "examples": [
                "local /path/to/video.mp4",
                "local ./video.avi --language en",
                "local ~/Downloads/video.mkv --force"
            ]
        }