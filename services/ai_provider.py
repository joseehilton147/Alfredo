from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str) -> str:
        pass

    @abstractmethod
    async def summarize(self, transcription: str, video_title: str) -> str:
        pass
