from dataclasses import dataclass

from src.application.interfaces.ai_provider import AIProviderInterface
from src.domain.entities.video import Video
from src.domain.repositories.video_repository import VideoRepository


@dataclass
class TranscribeAudioRequest:
    video_id: str
    audio_path: str
    language: str = "pt"


@dataclass
class TranscribeAudioResponse:
    video: Video
    transcription: str


class TranscribeAudioUseCase:

    def __init__(
        self, video_repository: VideoRepository, ai_provider: AIProviderInterface
    ):
        self.video_repository = video_repository
        self.ai_provider = ai_provider

    async def execute(self, request: TranscribeAudioRequest) -> TranscribeAudioResponse:
        video = await self.video_repository.find_by_id(request.video_id)
        if not video:
            raise ValueError(f"Vídeo {request.video_id} não encontrado")

        transcription = await self.ai_provider.transcribe_audio(
            request.audio_path, request.language
        )

        return TranscribeAudioResponse(video=video, transcription=transcription)
