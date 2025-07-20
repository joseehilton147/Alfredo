"""Use case for transcribing audio files."""

import logging
from dataclasses import dataclass
from typing import Optional

from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.storage_gateway import StorageGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    InvalidVideoFormatError,
    TranscriptionError,
    ConfigurationError
)


@dataclass
class TranscribeAudioRequest:
    """Request for audio transcription."""
    video_id: str
    audio_path: str
    language: str = "pt"
    save_transcription: bool = True


@dataclass
class TranscribeAudioResponse:
    """Response for audio transcription."""
    video: Video
    transcription: str
    was_cached: bool = False


class TranscribeAudioUseCase:
    """Use case for transcribing audio files."""

    def __init__(
        self, 
        ai_provider: AIProviderInterface,
        storage: StorageGateway,
        config: AlfredoConfig
    ):
        """Initialize the use case with injected dependencies.

        Args:
            ai_provider: AI provider for transcription
            storage: Gateway for data storage
            config: Application configuration
        """
        self.ai_provider = ai_provider
        self.storage = storage
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def execute(self, request: TranscribeAudioRequest) -> TranscribeAudioResponse:
        """Execute audio transcription.

        Args:
            request: Transcription request

        Returns:
            Transcription response with video and transcription

        Raises:
            InvalidVideoFormatError: If video is not found
            TranscriptionError: If transcription fails
            ConfigurationError: If configuration is invalid
        """
        try:
            # Step 1: Load video
            video = await self.storage.load_video(request.video_id)
            if not video:
                raise InvalidVideoFormatError(
                    "video_id",
                    request.video_id,
                    "Vídeo não encontrado",
                    details={"video_id": request.video_id}
                )

            # Step 2: Check if transcription already exists
            existing_transcription = await self.storage.load_transcription(request.video_id)
            if existing_transcription and not getattr(request, 'force_retranscribe', False):
                self.logger.info(f"Using cached transcription for video: {request.video_id}")
                return TranscribeAudioResponse(
                    video=video,
                    transcription=existing_transcription,
                    was_cached=True
                )

            # Step 3: Validate audio file
            import os
            if not os.path.exists(request.audio_path):
                raise TranscriptionError(
                    request.audio_path,
                    "Arquivo de áudio não encontrado",
                    details={
                        "audio_path": request.audio_path,
                        "video_id": request.video_id
                    }
                )

            # Step 4: Transcribe audio
            self.logger.info(f"Transcribing audio for video: {request.video_id}")
            transcription = await self.ai_provider.transcribe_audio(
                request.audio_path, request.language
            )

            if not transcription or not transcription.strip():
                raise TranscriptionError(
                    request.audio_path,
                    "Transcrição resultou em texto vazio",
                    provider=self.ai_provider.__class__.__name__,
                    details={
                        "audio_path": request.audio_path,
                        "language": request.language,
                        "video_id": request.video_id
                    }
                )

            # Step 5: Save transcription if requested
            if request.save_transcription:
                await self.storage.save_transcription(
                    request.video_id,
                    transcription,
                    {
                        "language": request.language,
                        "provider": self.ai_provider.__class__.__name__,
                        "audio_path": request.audio_path
                    }
                )

                # Update video with transcription
                video.transcription = transcription
                await self.storage.save_video(video)

            self.logger.info(f"Audio transcribed successfully for video: {request.video_id}")

            return TranscribeAudioResponse(
                video=video,
                transcription=transcription,
                was_cached=False
            )

        except (InvalidVideoFormatError, TranscriptionError, ConfigurationError):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error transcribing audio for video {request.video_id}: {str(e)}")
            # Convert unexpected errors to domain exceptions
            raise TranscriptionError(
                request.audio_path,
                f"Erro inesperado na transcrição: {str(e)}",
                details={
                    "video_id": request.video_id,
                    "audio_path": request.audio_path,
                    "language": request.language,
                    "error": str(e)
                }
            )
