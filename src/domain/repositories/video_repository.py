from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.video import Video


class VideoRepository(ABC):

    @abstractmethod
    async def save(self, video: Video) -> Video:
        pass

    @abstractmethod
    async def find_by_id(self, video_id: str) -> Optional[Video]:
        pass

    @abstractmethod
    async def find_by_url(self, url: str) -> Optional[Video]:
        pass

    @abstractmethod
    async def list_all(self) -> List[Video]:
        pass

    @abstractmethod
    async def delete(self, video_id: str) -> bool:
        pass
