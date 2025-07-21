from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from ..validators.audio_validators import (
    validate_audio_file_path,
    validate_audio_duration,
    validate_audio_format,
)


@dataclass
class AudioTrack:
    """
    Entidade que representa uma faixa de áudio extraída de um vídeo.
    
    Esta entidade encapsula todas as informações relacionadas ao áudio
    extraído, incluindo metadados técnicos e validações de negócio.
    """
    
    file_path: str
    duration: float = 0.0
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None
    source_video_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

        # Executar validações robustas
        self._validate_file_path()
        self._validate_duration()
        self._validate_format()

    def _validate_file_path(self) -> None:
        """Valida o caminho do arquivo de áudio."""
        validate_audio_file_path(self.file_path)

    def _validate_duration(self) -> None:
        """Valida a duração do áudio."""
        validate_audio_duration(self.duration)

    def _validate_format(self) -> None:
        """Valida o formato do arquivo de áudio."""
        if self.format:
            validate_audio_format(self.format)

    def get_file_size_mb(self) -> float:
        """Retorna o tamanho do arquivo em MB."""
        if self.size_bytes:
            return self.size_bytes / (1024 * 1024)
        return 0.0

    def get_duration_formatted(self) -> str:
        """Retorna a duração formatada como MM:SS."""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def is_stereo(self) -> bool:
        """Verifica se o áudio é estéreo."""
        return self.channels == 2 if self.channels else False

    def is_mono(self) -> bool:
        """Verifica se o áudio é mono."""
        return self.channels == 1 if self.channels else False

    def get_quality_info(self) -> Dict[str, str]:
        """Retorna informações de qualidade do áudio."""
        quality_info = {}
        
        if self.sample_rate:
            if self.sample_rate >= 44100:
                quality_info["sample_rate_quality"] = "Alta"
            elif self.sample_rate >= 22050:
                quality_info["sample_rate_quality"] = "Média"
            else:
                quality_info["sample_rate_quality"] = "Baixa"
        
        if self.channels:
            quality_info["channel_type"] = "Estéreo" if self.is_stereo() else "Mono"
        
        return quality_info