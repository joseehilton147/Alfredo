from abc import ABC, abstractmethod


class AIProviderInterface(ABC):

    @abstractmethod
    async def transcribe_audio(self, audio_path: str, language: str = "pt") -> str:
        pass

    @abstractmethod
    async def summarize_text(self, text: str, context: str = "") -> str:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass
