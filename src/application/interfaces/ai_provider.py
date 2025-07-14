"""Interface para provedores de IA."""
from abc import ABC, abstractmethod
from typing import Optional


class AIProviderInterface(ABC):
    """Interface para provedores de serviços de IA."""
    
    @abstractmethod
    async def transcribe_audio(
        self, 
        audio_path: str, 
        language: Optional[str] = None
    ) -> str:
        """Transcreve áudio para texto.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)
            
        Returns:
            Texto transcrito
        """
        pass
        
    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados.
        
        Returns:
            Lista de códigos de idioma
        """
        pass
