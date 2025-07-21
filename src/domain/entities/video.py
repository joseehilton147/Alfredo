from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from ..validators.video_validators import (
    validate_video_id,
    validate_video_title,
    validate_video_duration,
    validate_video_sources,
)


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

        # Sincronizar url e source_url para compatibilidade retroativa
        if self.source_url is None and self.url is not None:
            self.source_url = self.url
        elif self.url is None and self.source_url is not None:
            self.url = self.source_url

        # Executar validações robustas
        self._validate_id()
        self._validate_title()
        self._validate_sources()
        self._validate_duration()

    def _validate_id(self) -> None:
        """Valida o ID do vídeo usando validador específico."""
        validate_video_id(self.id)

    def _validate_title(self) -> None:
        """Valida o título do vídeo usando validador específico."""
        validate_video_title(self.title)

    def _validate_sources(self) -> None:
        """Valida as fontes do vídeo (file_path e URL) usando validador específico."""
        validate_video_sources(self.file_path, self.source_url)

    def _validate_duration(self) -> None:
        """Valida a duração do vídeo usando validador específico."""
        validate_video_duration(self.duration)

    def is_local(self) -> bool:
        return self.file_path is not None

    def is_remote(self) -> bool:
        return self.source_url is not None

    def get_source(self) -> str:
        if self.is_local() and self.file_path:
            return self.file_path
        if self.is_remote() and self.source_url:
            return self.source_url
        return ""
