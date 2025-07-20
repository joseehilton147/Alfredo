"""
Comando CLI para processamento de vídeos do YouTube.

Implementa o comando específico para download e processamento de URLs do YouTube,
incluindo validação de argumentos, feedback de progresso e integração com o
ProcessYouTubeVideoUseCase. Versão expandida com suporte a flags e sub-comandos.
"""

import re
import argparse
from pathlib import Path
from typing import Optional
from tqdm import tqdm

from src.presentation.cli.base_command import Command, CommandMetadata, CommandFlag
from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoUseCase,
    ProcessYouTubeVideoRequest,
    ProcessYouTubeVideoResponse
)
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


class YouTubeCommand(Command):
    """
    Comando para processamento de vídeos do YouTube.
    
    Responsabilidades:
    - Validar URLs do YouTube
    - Executar download e processamento via use case
    - Exibir progresso com tqdm
    - Tratar erros específicos do YouTube
    - Suporte a flags avançadas e sub-comandos
    """

    def __init__(self, config: AlfredoConfig, factory: InfrastructureFactory):
        """
        Inicializa o comando YouTube.
        
        Args:
            config: Configuração do Alfredo AI
            factory: Factory para criação de dependências
        """
        super().__init__(config, factory)
        self.use_case: Optional[ProcessYouTubeVideoUseCase] = None

    def _initialize_metadata(self) -> None:
        """Inicializa metadados do comando YouTube."""
        self._metadata = CommandMetadata(
            name="youtube",
            description="Processa vídeos do YouTube para transcrição e resumo",
            usage="alfredo youtube <URL> [opções]",
            examples=[
                "youtube https://youtube.com/watch?v=VIDEO_ID",
                "youtube https://youtu.be/VIDEO_ID --language en",
                "youtube https://youtube.com/watch?v=VIDEO_ID --summary --force",
                "youtube info https://youtube.com/watch?v=VIDEO_ID"
            ],
            supported_formats=["YouTube URLs", "youtu.be URLs"],
            category="video",
            aliases=["yt", "youtube-dl"],
            sub_commands={
                "info": "Extrai apenas informações do vídeo sem processar",
                "download": "Apenas baixa o vídeo sem processar",
                "process": "Processa vídeo já baixado"
            }
        )
        
        # Definir flags específicas
        self._flags = [
            CommandFlag(
                name="url",
                description="URL do vídeo do YouTube",
                type=str,
                required=True
            ),
            CommandFlag(
                name="language",
                short_name="l",
                description="Idioma para transcrição",
                type=str,
                default="pt",
                choices=["pt", "en", "es", "fr", "de"]
            ),
            CommandFlag(
                name="summary",
                short_name="s",
                description="Gerar resumo além da transcrição",
                type=bool,
                default=False
            ),
            CommandFlag(
                name="force",
                short_name="f",
                description="Forçar reprocessamento mesmo se já existe",
                type=bool,
                default=False
            ),
            CommandFlag(
                name="quality",
                short_name="q",
                description="Qualidade do vídeo para download",
                type=str,
                default="best",
                choices=["best", "worst", "720p", "480p", "360p"]
            ),
            CommandFlag(
                name="provider",
                short_name="p",
                description="Provedor de IA para processamento",
                type=str,
                choices=["whisper", "groq", "ollama"]
            )
        ]
        self._progress_bar: Optional[tqdm] = None

    def validate_args(self, url: str, **kwargs) -> bool:
        """
        Valida argumentos específicos do comando YouTube.
        
        Args:
            url: URL do YouTube a ser validada
            **kwargs: Argumentos adicionais
            
        Returns:
            True se argumentos são válidos, False caso contrário
        """
        if not url:
            print("❌ URL é obrigatória para processamento do YouTube")
            return False

        if not url.startswith(('http://', 'https://')):
            print("❌ URL deve começar com http:// ou https://")
            return False

        # Validar se é uma URL do YouTube válida
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
        ]

        is_youtube_url = any(re.match(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)
        
        if not is_youtube_url:
            print("❌ URL deve ser uma URL válida do YouTube")
            print("   Formatos suportados:")
            print("   - https://www.youtube.com/watch?v=VIDEO_ID")
            print("   - https://youtu.be/VIDEO_ID")
            print("   - https://www.youtube.com/embed/VIDEO_ID")
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
        url: str, 
        language: str = "pt", 
        output_dir: Optional[str] = None,
        force_reprocess: bool = False,
        quality: str = "best"
    ) -> ProcessYouTubeVideoResponse:
        """
        Executa o processamento de vídeo do YouTube.
        
        Args:
            url: URL do vídeo do YouTube
            language: Idioma para transcrição (padrão: pt)
            output_dir: Diretório de saída (opcional)
            force_reprocess: Forçar reprocessamento mesmo se já existe
            quality: Qualidade do vídeo (best, worst, ou formato específico)
            
        Returns:
            Resposta do processamento com vídeo e transcrição
            
        Raises:
            DownloadFailedError: Se falhar o download
            TranscriptionError: Se falhar a transcrição
            InvalidVideoFormatError: Se formato for inválido
            ConfigurationError: Se configuração for inválida
        """
        # Validar argumentos
        if not self.validate_args(url, language=language):
            raise InvalidVideoFormatError("arguments", url, "argumentos inválidos")

        # Configurar diretório de saída
        if output_dir is None:
            output_dir = str(self.config.data_dir / "input" / "youtube")

        # Criar use case com dependências injetadas
        self.use_case = ProcessYouTubeVideoUseCase(
            downloader=self.factory.create_video_downloader(),
            extractor=self.factory.create_audio_extractor(),
            ai_provider=self.factory.create_ai_provider(),
            storage=self.factory.create_storage(),
            config=self.config
        )

        # Configurar request
        request = ProcessYouTubeVideoRequest(
            url=url,
            language=language,
            output_dir=output_dir,
            progress_callback=self._update_progress
        )
        
        # Adicionar atributos extras se necessário
        if force_reprocess:
            request.force_reprocess = force_reprocess
        if quality != "best":
            request.quality = quality

        self.log_execution_start(
            "processamento de vídeo do YouTube",
            url=url,
            language=language,
            quality=quality
        )

        try:
            # Inicializar barra de progresso
            self._progress_bar = tqdm(
                total=100,
                desc="🎬 Processando vídeo do YouTube",
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
            self._display_youtube_result(response)

            self.log_execution_success(
                "processamento de vídeo do YouTube",
                video_title=response.video.title,
                transcription_length=len(response.transcription),
                file_path=response.downloaded_file
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
            raise DownloadFailedError(url, "Processamento cancelado pelo usuário")

        except Exception as error:
            # Fechar barra de progresso em caso de erro
            if self._progress_bar:
                self._progress_bar.close()
                self._progress_bar = None

            self.log_execution_error(
                "processamento de vídeo do YouTube",
                error,
                url=url,
                language=language
            )
            
            # Re-lançar exceções específicas do domínio
            if isinstance(error, (DownloadFailedError, TranscriptionError, 
                                InvalidVideoFormatError, ConfigurationError)):
                raise
            
            # Converter erros inesperados
            raise ConfigurationError(
                "youtube_processing",
                f"Erro inesperado no processamento do YouTube: {str(error)}",
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

    def _display_youtube_result(self, response: ProcessYouTubeVideoResponse) -> None:
        """
        Exibe resultado específico do processamento do YouTube.
        
        Args:
            response: Resposta do processamento
        """
        video = response.video
        
        print(f"\n✅ Vídeo do YouTube processado com sucesso!")
        print(f"📺 Título: {video.title}")
        print(f"🔗 URL: {video.source_url}")
        
        if video.duration:
            duration_min = int(video.duration // 60)
            duration_sec = int(video.duration % 60)
            print(f"⏱️  Duração: {duration_min}:{duration_sec:02d}")
        
        print(f"📝 Transcrição: {len(response.transcription)} caracteres")
        print(f"💾 Arquivo baixado: {Path(response.downloaded_file).name}")
        
        # Exibir informações de metadados se disponíveis
        if video.metadata:
            if 'uploader' in video.metadata:
                print(f"👤 Canal: {video.metadata['uploader']}")
            if 'view_count' in video.metadata:
                views = video.metadata['view_count']
                if views:
                    print(f"👁️  Visualizações: {views:,}")

    def get_command_info(self) -> dict:
        """
        Retorna informações específicas do comando YouTube.
        
        Returns:
            Dicionário com informações do comando
        """
        return {
            "name": "youtube",
            "description": "Processa vídeos do YouTube com download e transcrição",
            "class": self.__class__.__name__,
            "usage": "youtube <url> [--language pt] [--quality best] [--force]",
            "examples": [
                "youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "youtube https://youtu.be/dQw4w9WgXcQ --language en",
                "youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ --quality worst --force"
            ]
        }

    async def execute_from_parsed_args(self, args: argparse.Namespace) -> Optional[ProcessYouTubeVideoResponse]:
        """
        Executa comando com argumentos parseados.
        
        Args:
            args: Argumentos parseados pelo argparse
            
        Returns:
            Resposta do processamento ou None se falhou
        """
        try:
            # Verificar se é um sub-comando
            if hasattr(args, 'sub_command') and args.sub_command:
                return await self._execute_sub_command(args.sub_command, args)
            
            # Executar comando principal
            return await self._execute_main_command(args)
            
        except Exception as e:
            self.handle_error(e, {"url": getattr(args, 'url', 'N/A')})
            return None

    async def _execute_sub_command(self, sub_command: str, args: argparse.Namespace) -> Optional[ProcessYouTubeVideoResponse]:
        """Executa sub-comando específico."""
        if sub_command == "info":
            return await self._execute_info_command(args)
        elif sub_command == "download":
            return await self._execute_download_command(args)
        elif sub_command == "process":
            return await self._execute_process_command(args)
        else:
            print(f"❌ Sub-comando '{sub_command}' não implementado")
            return None

    async def _execute_main_command(self, args: argparse.Namespace) -> ProcessYouTubeVideoResponse:
        """Executa comando principal de processamento completo."""
        self.log_execution_start("processamento de vídeo YouTube", url=args.url)
        
        # Criar use case se não existe
        if not self.use_case:
            dependencies = self.factory.create_all_dependencies()
            self.use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        # Criar request
        request = ProcessYouTubeVideoRequest(
            url=args.url,
            language=getattr(args, 'language', 'pt'),
            generate_summary=getattr(args, 'summary', False),
            force_reprocess=getattr(args, 'force', False),
            quality=getattr(args, 'quality', 'best')
        )
        
        # Executar com barra de progresso
        with tqdm(desc="Processando vídeo YouTube", unit="etapa") as pbar:
            def progress_callback(step: str):
                pbar.set_description(f"Processando: {step}")
                pbar.update(1)
            
            response = await self.use_case.execute(request, progress_callback)
            pbar.set_description("Concluído")
        
        # Exibir resultado
        self._display_processing_result(response)
        self.log_execution_success("processamento de vídeo YouTube", 
                                 video_title=response.video.title)
        
        return response

    async def _execute_info_command(self, args: argparse.Namespace) -> ProcessYouTubeVideoResponse:
        """Executa sub-comando de informações."""
        print("🔍 Extraindo informações do vídeo...")
        
        # Usar downloader para extrair apenas informações
        downloader = self.factory.create_video_downloader()
        info = await downloader.extract_info(args.url)
        
        print(f"📹 Título: {info.get('title', 'N/A')}")
        print(f"⏱️  Duração: {info.get('duration', 0)} segundos")
        print(f"👤 Canal: {info.get('uploader', 'N/A')}")
        print(f"📅 Data: {info.get('upload_date', 'N/A')}")
        print(f"👀 Visualizações: {info.get('view_count', 'N/A')}")
        
        return None

    async def _execute_download_command(self, args: argparse.Namespace) -> ProcessYouTubeVideoResponse:
        """Executa sub-comando de download."""
        print("⬇️ Baixando vídeo...")
        
        downloader = self.factory.create_video_downloader()
        output_dir = self.config.data_dir / "input" / "youtube"
        
        video_path = await downloader.download(
            args.url, 
            str(output_dir),
            getattr(args, 'quality', 'best')
        )
        
        print(f"✅ Vídeo baixado: {video_path}")
        return None

    async def _execute_process_command(self, args: argparse.Namespace) -> ProcessYouTubeVideoResponse:
        """Executa sub-comando de processamento de vídeo já baixado."""
        # Implementação similar ao comando principal, mas assumindo que o vídeo já foi baixado
        return await self._execute_main_command(args)

    def _display_processing_result(self, response: ProcessYouTubeVideoResponse) -> None:
        """Exibe resultado do processamento de forma detalhada."""
        if response.was_cached:
            print(f"✅ Vídeo já processado (cache): {response.video.title}")
        else:
            print(f"✅ Vídeo processado com sucesso: {response.video.title}")
        
        print(f"🆔 ID: {response.video.id}")
        print(f"⏱️  Duração: {response.video.duration:.1f} segundos")
        
        if response.video.transcription:
            char_count = len(response.video.transcription)
            print(f"📝 Transcrição: {char_count} caracteres")
        
        if response.video.summary:
            char_count = len(response.video.summary)
            print(f"📋 Resumo: {char_count} caracteres")
        
        if response.processing_time:
            print(f"⏱️  Tempo de processamento: {response.processing_time:.1f}s")

    def validate_parsed_args(self, args: argparse.Namespace) -> bool:
        """
        Valida argumentos parseados específicos do YouTube.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se válidos, False caso contrário
        """
        # Validar URL se fornecida
        if hasattr(args, 'url') and args.url:
            if not self._is_valid_youtube_url(args.url):
                print("❌ URL do YouTube inválida")
                print("   Formatos aceitos:")
                print("   - https://youtube.com/watch?v=VIDEO_ID")
                print("   - https://youtu.be/VIDEO_ID")
                return False
        
        return True

    def _is_valid_youtube_url(self, url: str) -> bool:
        """
        Valida se a URL é do YouTube.
        
        Args:
            url: URL a ser validada
            
        Returns:
            True se válida, False caso contrário
        """
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(www\.)?youtu\.be/[\w-]+',
            r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
            r'^https?://(www\.)?youtube\.com/v/[\w-]+'
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)

    # Manter compatibilidade com implementação anterior
    async def execute(self, url: str, language: str = "pt", 
                     generate_summary: bool = False, force: bool = False) -> Optional[ProcessYouTubeVideoResponse]:
        """
        Método de compatibilidade para execução direta.
        
        Args:
            url: URL do vídeo do YouTube
            language: Idioma para transcrição
            generate_summary: Se deve gerar resumo
            force: Se deve forçar reprocessamento
            
        Returns:
            Resposta do processamento
        """
        # Criar namespace simulado
        args = argparse.Namespace(
            url=url,
            language=language,
            summary=generate_summary,
            force=force,
            quality="best"
        )
        
        return await self.execute_from_parsed_args(args)

    def validate_args(self, url: str, **kwargs) -> bool:
        """
        Método de compatibilidade para validação.
        
        Args:
            url: URL a ser validada
            **kwargs: Argumentos adicionais
            
        Returns:
            True se válidos, False caso contrário
        """
        if not url:
            print("❌ URL é obrigatória")
            return False
        
        return self._is_valid_youtube_url(url)