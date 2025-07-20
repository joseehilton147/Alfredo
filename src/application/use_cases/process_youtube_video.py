"""Use case for processing YouTube videos."""

import logging
from dataclasses import dataclass
from typing import Callable, Optional

from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError, 
    TranscriptionError, 
    InvalidVideoFormatError,
    ConfigurationError
)


@dataclass
class ProcessYouTubeVideoRequest:
    """Request for processing YouTube video."""

    url: str
    language: str = "pt"
    output_dir: str = "data/input/youtube"
    progress_callback: Optional[Callable[[int, str], None]] = None


@dataclass
class ProcessYouTubeVideoResponse:
    """Response for YouTube video processing."""

    video: Video
    transcription: str
    downloaded_file: str


class ProcessYouTubeVideoUseCase:
    """Use case for downloading and processing YouTube videos."""

    def __init__(
        self, 
        downloader: VideoDownloaderGateway,
        extractor: AudioExtractorGateway,
        ai_provider: AIProviderInterface,
        storage: StorageGateway,
        config: AlfredoConfig
    ):
        """Initialize the use case with injected dependencies.

        Args:
            downloader: Gateway for video downloading
            extractor: Gateway for audio extraction
            ai_provider: AI provider for transcription
            storage: Gateway for data storage
            config: Application configuration
        """
        self.downloader = downloader
        self.extractor = extractor
        self.ai_provider = ai_provider
        self.storage = storage
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cancelled = False

    async def execute(
        self, request: ProcessYouTubeVideoRequest
    ) -> ProcessYouTubeVideoResponse:
        """Execute YouTube video processing.

        Args:
            request: Processing request

        Returns:
            Processing response with video and transcription

        Raises:
            DownloadFailedError: If video download fails
            TranscriptionError: If audio transcription fails
            InvalidVideoFormatError: If video format is invalid
            ConfigurationError: If configuration is invalid
        """
        try:
            # Step 1: Extract video info first
            if self._cancelled:
                raise DownloadFailedError(request.url, "Processamento cancelado pelo usuário")

            if request.progress_callback:
                request.progress_callback(5, "Extraindo informações do vídeo...")

            video_info = await self.downloader.extract_info(request.url)
            
            # Step 2: Create video entity
            video = Video(
                id=f"youtube_{video_info['id']}",
                title=video_info["title"],
                source_url=request.url,
                duration=video_info.get("duration", 0),
                metadata=video_info
            )

            # Step 3: Check if already processed
            existing_video = await self.storage.load_video(video.id)
            if existing_video and not getattr(request, 'force_reprocess', False):
                self.logger.info(f"Video already processed: {video.title}")
                existing_transcription = await self.storage.load_transcription(video.id)
                return ProcessYouTubeVideoResponse(
                    video=existing_video,
                    transcription=existing_transcription or "",
                    downloaded_file=existing_video.file_path or ""
                )

            # Step 4: Download video
            if self._cancelled:
                raise DownloadFailedError(request.url, "Processamento cancelado pelo usuário")

            if request.progress_callback:
                request.progress_callback(20, "Baixando vídeo...")

            downloaded_file = await self.downloader.download(
                request.url, 
                request.output_dir,
                getattr(request, 'quality', 'best')
            )
            video.file_path = downloaded_file

            # Step 5: Extract audio
            if self._cancelled:
                raise TranscriptionError(downloaded_file, "Processamento cancelado pelo usuário")

            if request.progress_callback:
                request.progress_callback(40, "Extraindo áudio...")

            audio_path = str(self.config.temp_dir / f"{video.id}.wav")
            await self.extractor.extract_audio(
                downloaded_file,
                audio_path,
                format="wav",
                sample_rate=self.config.audio_sample_rate
            )

            # Step 6: Transcribe audio
            if self._cancelled:
                raise TranscriptionError(audio_path, "Processamento cancelado pelo usuário")

            if request.progress_callback:
                request.progress_callback(70, "Transcrevendo áudio...")

            transcription = await self.ai_provider.transcribe_audio(
                audio_path, request.language
            )

            # Step 7: Save results
            if self._cancelled:
                raise TranscriptionError(audio_path, "Processamento cancelado pelo usuário")

            if request.progress_callback:
                request.progress_callback(90, "Salvando resultados...")

            video.transcription = transcription
            await self.storage.save_video(video)
            await self.storage.save_transcription(
                video.id, 
                transcription,
                {
                    "language": request.language,
                    "provider": self.ai_provider.__class__.__name__,
                    "audio_sample_rate": self.config.audio_sample_rate
                }
            )

            # Step 8: Cleanup temporary files
            try:
                import os
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup temp file {audio_path}: {e}")

            if request.progress_callback:
                request.progress_callback(100, "Concluído!")

            self.logger.info(f"YouTube video processed successfully: {video.title}")

            return ProcessYouTubeVideoResponse(
                video=video,
                transcription=transcription,
                downloaded_file=downloaded_file,
            )

        except (DownloadFailedError, TranscriptionError, InvalidVideoFormatError, ConfigurationError):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error processing YouTube video {request.url}: {str(e)}")
            # Convert unexpected errors to domain exceptions
            raise ConfigurationError(
                "unexpected_error",
                f"Erro inesperado no processamento: {str(e)}",
                expected="processamento bem-sucedido",
                details={"url": request.url, "error": str(e)}
            )



    async def cancel_processing(self) -> None:
        """Cancel ongoing processing operation."""
        self.logger.info("Processing cancellation requested")
        self._cancelled = True
