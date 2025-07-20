"""Use case for processing local video files."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


@dataclass
class ProcessLocalVideoRequest:
    """Request for processing local video."""

    file_path: str
    language: str = "pt"
    force_reprocess: bool = False
    progress_callback: Optional[Callable[[int, str], None]] = None


@dataclass
class ProcessLocalVideoResponse:
    """Response for local video processing."""

    video: Video
    transcription: str
    was_cached: bool = False


class ProcessLocalVideoUseCase:
    """Use case for processing local video files."""

    def __init__(
        self,
        extractor: AudioExtractorGateway,
        ai_provider: AIProviderInterface,
        storage: StorageGateway,
        config: AlfredoConfig
    ):
        """Initialize the use case with injected dependencies.

        Args:
            extractor: Gateway for audio extraction
            ai_provider: AI provider for transcription
            storage: Gateway for data storage
            config: Application configuration
        """
        self.extractor = extractor
        self.ai_provider = ai_provider
        self.storage = storage
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cancelled = False

    async def execute(
        self, request: ProcessLocalVideoRequest
    ) -> ProcessLocalVideoResponse:
        """Execute local video processing.

        Args:
            request: Processing request

        Returns:
            Processing response with video and transcription

        Raises:
            InvalidVideoFormatError: If video file is invalid
            TranscriptionError: If audio transcription fails
            ConfigurationError: If configuration is invalid
        """
        try:
            # Step 1: Validate video file
            if self._cancelled:
                raise TranscriptionError(
                    request.file_path, 
                    "Processamento cancelado pelo usuário"
                )

            if request.progress_callback:
                request.progress_callback(5, "Validando arquivo de vídeo...")

            video_path = Path(request.file_path)
            if not video_path.exists():
                raise InvalidVideoFormatError(
                    "file_path",
                    request.file_path,
                    "Arquivo não encontrado"
                )

            if not self._is_supported_video_format(video_path):
                raise InvalidVideoFormatError(
                    "file_format",
                    video_path.suffix,
                    "Formato de vídeo não suportado"
                )

            # Step 2: Create video entity
            video_id = f"local_{video_path.stem}_{video_path.stat().st_mtime}"
            video = Video(
                id=video_id,
                title=video_path.name,
                file_path=str(video_path.absolute()),
                duration=0,  # Will be updated after audio extraction
                metadata={
                    "file_size": video_path.stat().st_size,
                    "file_extension": video_path.suffix,
                    "source_type": "local"
                }
            )

            # Step 3: Check if already processed
            if not request.force_reprocess:
                existing_video = await self.storage.load_video(video.id)
                if existing_video:
                    existing_transcription = await self.storage.load_transcription(
                        video.id
                    )
                    if existing_transcription:
                        self.logger.info(f"Video already processed: {video.title}")
                        return ProcessLocalVideoResponse(
                            video=existing_video,
                            transcription=existing_transcription,
                            was_cached=True
                        )

            # Step 4: Extract audio information first
            if self._cancelled:
                raise TranscriptionError(
                    request.file_path, 
                    "Processamento cancelado pelo usuário"
                )

            if request.progress_callback:
                request.progress_callback(20, "Analisando informações do vídeo...")

            audio_info = await self.extractor.get_audio_info(str(video_path))
            if audio_info.get('duration'):
                video.duration = float(audio_info['duration'])

            # Step 5: Extract audio
            if self._cancelled:
                raise TranscriptionError(
                    request.file_path, 
                    "Processamento cancelado pelo usuário"
                )

            if request.progress_callback:
                request.progress_callback(40, "Extraindo áudio...")

            audio_path = str(self.config.temp_dir / f"{video.id}.wav")
            await self.extractor.extract_audio(
                str(video_path),
                audio_path,
                format="wav",
                sample_rate=self.config.audio_sample_rate
            )

            # Step 6: Transcribe audio
            if self._cancelled:
                raise TranscriptionError(
                    audio_path, 
                    "Processamento cancelado pelo usuário"
                )

            if request.progress_callback:
                request.progress_callback(70, "Transcrevendo áudio...")

            transcription = await self.ai_provider.transcribe_audio(
                audio_path, request.language
            )

            if not transcription or not transcription.strip():
                raise TranscriptionError(
                    audio_path,
                    "Transcrição resultou em texto vazio",
                    provider=self.ai_provider.__class__.__name__
                )

            # Step 7: Save results
            if self._cancelled:
                raise TranscriptionError(
                    audio_path, 
                    "Processamento cancelado pelo usuário"
                )

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
                    "audio_sample_rate": self.config.audio_sample_rate,
                    "source_type": "local"
                }
            )

            # Step 8: Cleanup temporary files
            try:
                import os
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                self.logger.warning(
                    f"Failed to cleanup temp file {audio_path}: {e}"
                )

            if request.progress_callback:
                request.progress_callback(100, "Concluído!")

            self.logger.info(f"Local video processed successfully: {video.title}")

            return ProcessLocalVideoResponse(
                video=video,
                transcription=transcription,
                was_cached=False
            )

        except (InvalidVideoFormatError, TranscriptionError, ConfigurationError):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            self.logger.error(
                f"Error processing local video {request.file_path}: {str(e)}"
            )
            # Convert unexpected errors to domain exceptions
            raise ConfigurationError(
                "unexpected_error",
                f"Erro inesperado no processamento: {str(e)}",
                expected="processamento bem-sucedido",
                details={"file_path": request.file_path, "error": str(e)}
            )

    def _is_supported_video_format(self, video_path: Path) -> bool:
        """
        Check if video format is supported.

        Args:
            video_path: Path to video file

        Returns:
            True if format is supported, False otherwise
        """
        supported_extensions = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', 
            '.flv', '.webm', '.m4v', '.3gp', '.ogv'
        }
        return video_path.suffix.lower() in supported_extensions

    async def cancel_processing(self) -> None:
        """Cancel ongoing processing operation."""
        self.logger.info("Processing cancellation requested")
        self._cancelled = True