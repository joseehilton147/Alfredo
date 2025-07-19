from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Video:
    id: str
    title: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    duration: float = 0.0
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None
    transcription: Optional[str] = None
    source_url: Optional[str] = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

    def is_local(self) -> bool:
        return self.file_path is not None

    def is_remote(self) -> bool:
        return self.url is not None

    def get_source(self) -> str:
        if self.is_local() and self.file_path:
            return self.file_path
        if self.is_remote() and self.url:
            return self.url
        return ""
