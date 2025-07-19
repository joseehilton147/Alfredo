"""Interface para repositório de vídeos."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.video import Video


class VideoRepository(ABC):
    """Interface para repositório de vídeos."""

    @abstractmethod
    async def find_by_id(self, video_id: str) -> Optional[Video]:
        """Busca um vídeo pelo ID.

        Args:
            video_id: ID do vídeo

        Returns:
            Vídeo encontrado ou None
        """
        pass

    @abstractmethod
    async def save(self, video: Video) -> None:
        """Salva um vídeo no repositório.

        Args:
            video: Vídeo a ser salvo
        """
        pass

    @abstractmethod
    async def delete(self, video_id: str) -> bool:
        """Remove um vídeo do repositório.

        Args:
            video_id: ID do vídeo

        Returns:
            True se removido com sucesso
        """
        pass

    @abstractmethod
    async def list_all(self) -> List[Video]:
        """Lista todos os vídeos no repositório.

        Returns:
            Lista de vídeos
        """
        pass
