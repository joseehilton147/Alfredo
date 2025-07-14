from abc import ABC, abstractmethod
from core.interfaces import IAIProvider


class AIProvider(ABC, IAIProvider):
    """Base class for AI providers.
    
    Implementa a interface IAIProvider para compatibilidade
    com o novo sistema arquitetural.
    """
    
    @abstractmethod
    async def transcribe(self, audio_path: str) -> str:
        """Transcreve áudio para texto.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Texto transcrito
        """
        pass

    @abstractmethod
    async def summarize(self, transcription: str, video_title: str) -> str:
        """Gera resumo a partir da transcrição.
        
        Args:
            transcription: Texto transcrito
            video_title: Título do vídeo
            
        Returns:
            Resumo gerado
        """
        pass
