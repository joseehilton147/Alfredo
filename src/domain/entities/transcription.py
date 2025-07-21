from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from ..validators.transcription_validators import (
    validate_transcription_text,
    validate_transcription_language,
    validate_transcription_confidence,
)


@dataclass
class TranscriptionSegment:
    """
    Representa um segmento individual da transcrição com timestamp.
    """
    
    text: str
    start_time: float
    end_time: float
    confidence: Optional[float] = None
    
    def __post_init__(self) -> None:
        self._validate_segment()
    
    def _validate_segment(self) -> None:
        """Valida o segmento de transcrição."""
        if not self.text or not self.text.strip():
            from ..exceptions.alfredo_errors import InvalidVideoFormatError
            raise InvalidVideoFormatError(
                field="segment_text",
                value=self.text,
                constraint="texto do segmento não pode ser vazio"
            )
        
        if self.start_time < 0:
            from ..exceptions.alfredo_errors import InvalidVideoFormatError
            raise InvalidVideoFormatError(
                field="start_time",
                value=self.start_time,
                constraint="tempo inicial não pode ser negativo"
            )
        
        if self.end_time <= self.start_time:
            from ..exceptions.alfredo_errors import InvalidVideoFormatError
            raise InvalidVideoFormatError(
                field="end_time",
                value=self.end_time,
                constraint="tempo final deve ser maior que tempo inicial"
            )
        
        if self.confidence is not None:
            validate_transcription_confidence(self.confidence)
    
    def get_duration(self) -> float:
        """Retorna a duração do segmento em segundos."""
        return self.end_time - self.start_time
    
    def get_formatted_time(self) -> str:
        """Retorna o tempo formatado como [MM:SS - MM:SS]."""
        start_min, start_sec = divmod(int(self.start_time), 60)
        end_min, end_sec = divmod(int(self.end_time), 60)
        return f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}]"


@dataclass
class Transcription:
    """
    Entidade que representa a transcrição completa de um áudio.
    
    Esta entidade encapsula o texto transcrito, metadados de qualidade
    e informações sobre o processo de transcrição.
    """
    
    text: str
    language: str = "pt"
    confidence: Optional[float] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    segments: Optional[List[TranscriptionSegment]] = None
    created_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, str]] = None
    source_audio_path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.segments is None:
            self.segments = []

        # Executar validações robustas
        self._validate_text()
        self._validate_language()
        self._validate_confidence()

    def _validate_text(self) -> None:
        """Valida o texto da transcrição."""
        validate_transcription_text(self.text)

    def _validate_language(self) -> None:
        """Valida o idioma da transcrição."""
        validate_transcription_language(self.language)

    def _validate_confidence(self) -> None:
        """Valida o nível de confiança da transcrição."""
        if self.confidence is not None:
            validate_transcription_confidence(self.confidence)

    def get_word_count(self) -> int:
        """Retorna o número de palavras na transcrição."""
        return len(self.text.split()) if self.text else 0

    def get_character_count(self) -> int:
        """Retorna o número de caracteres na transcrição."""
        return len(self.text) if self.text else 0

    def get_estimated_reading_time(self) -> float:
        """Retorna o tempo estimado de leitura em minutos (200 palavras/min)."""
        word_count = self.get_word_count()
        return word_count / 200.0 if word_count > 0 else 0.0

    def get_confidence_level(self) -> str:
        """Retorna o nível de confiança como string descritiva."""
        if self.confidence is None:
            return "Desconhecido"
        
        if self.confidence >= 0.9:
            return "Muito Alta"
        elif self.confidence >= 0.8:
            return "Alta"
        elif self.confidence >= 0.7:
            return "Média"
        elif self.confidence >= 0.6:
            return "Baixa"
        else:
            return "Muito Baixa"

    def get_segments_count(self) -> int:
        """Retorna o número de segmentos da transcrição."""
        return len(self.segments) if self.segments else 0

    def get_total_duration(self) -> float:
        """Retorna a duração total baseada nos segmentos."""
        if not self.segments:
            return 0.0
        
        return max(segment.end_time for segment in self.segments)

    def get_text_with_timestamps(self) -> str:
        """Retorna o texto com timestamps dos segmentos."""
        if not self.segments:
            return self.text
        
        formatted_segments = []
        for segment in self.segments:
            formatted_segments.append(f"{segment.get_formatted_time()} {segment.text}")
        
        return "\n".join(formatted_segments)

    def get_quality_metrics(self) -> Dict[str, str]:
        """Retorna métricas de qualidade da transcrição."""
        metrics = {
            "confidence_level": self.get_confidence_level(),
            "word_count": str(self.get_word_count()),
            "character_count": str(self.get_character_count()),
            "segments_count": str(self.get_segments_count()),
        }
        
        if self.provider:
            metrics["provider"] = self.provider
        
        if self.model:
            metrics["model"] = self.model
        
        if self.processing_time:
            metrics["processing_time"] = f"{self.processing_time:.2f}s"
        
        return metrics