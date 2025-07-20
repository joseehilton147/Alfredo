"""Interface Strategy para provedores de IA."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AIStrategy(ABC):
    """Interface Strategy para diferentes provedores de IA.
    
    Esta interface define o contrato para estratégias de IA que podem
    realizar transcrição e sumarização de conteúdo.
    """

    @abstractmethod
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcreve áudio para texto.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito

        Raises:
            TranscriptionError: Quando falha a transcrição
            ProviderUnavailableError: Quando o provedor está indisponível
        """
        pass

    @abstractmethod
    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """Gera resumo do texto fornecido.

        Args:
            text: Texto para sumarizar
            context: Contexto adicional (título do vídeo, etc.)

        Returns:
            Resumo gerado

        Raises:
            TranscriptionError: Quando falha a sumarização
            ProviderUnavailableError: Quando o provedor está indisponível
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados.

        Returns:
            Lista de códigos de idioma
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Retorna o nome da estratégia.

        Returns:
            Nome identificador da estratégia
        """
        pass

    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """Retorna configuração específica da estratégia.

        Returns:
            Dicionário com configurações da estratégia
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se a estratégia está disponível para uso.

        Returns:
            True se disponível, False caso contrário
        """
        pass