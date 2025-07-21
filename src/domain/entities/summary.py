from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from ..validators.summary_validators import (
    validate_summary_text,
    validate_summary_type,
    validate_summary_language,
)


@dataclass
class SummarySection:
    """
    Representa uma seção individual do resumo.
    """
    
    title: str
    content: str
    order: int = 0
    
    def __post_init__(self) -> None:
        self._validate_section()
    
    def _validate_section(self) -> None:
        """Valida a seção do resumo."""
        if not self.title or not self.title.strip():
            from ..exceptions.alfredo_errors import InvalidVideoFormatError
            raise InvalidVideoFormatError(
                field="section_title",
                value=self.title,
                constraint="título da seção não pode ser vazio"
            )
        
        if not self.content or not self.content.strip():
            from ..exceptions.alfredo_errors import InvalidVideoFormatError
            raise InvalidVideoFormatError(
                field="section_content",
                value=self.content,
                constraint="conteúdo da seção não pode ser vazio"
            )
    
    def get_word_count(self) -> int:
        """Retorna o número de palavras na seção."""
        return len(self.content.split()) if self.content else 0


@dataclass
class Summary:
    """
    Entidade que representa um resumo gerado a partir de uma transcrição.
    
    Esta entidade encapsula o resumo estruturado, metadados de geração
    e informações sobre o processo de sumarização.
    """
    
    text: str
    summary_type: str = "general"  # general, bullet_points, structured, etc.
    language: str = "pt"
    provider: Optional[str] = None
    model: Optional[str] = None
    sections: Optional[List[SummarySection]] = None
    key_points: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, str]] = None
    source_transcription_id: Optional[str] = None
    confidence: Optional[float] = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.sections is None:
            self.sections = []
        if self.key_points is None:
            self.key_points = []

        # Executar validações robustas
        self._validate_text()
        self._validate_type()
        self._validate_language()

    def _validate_text(self) -> None:
        """Valida o texto do resumo."""
        validate_summary_text(self.text)

    def _validate_type(self) -> None:
        """Valida o tipo do resumo."""
        validate_summary_type(self.summary_type)

    def _validate_language(self) -> None:
        """Valida o idioma do resumo."""
        validate_summary_language(self.language)

    def get_word_count(self) -> int:
        """Retorna o número de palavras no resumo."""
        return len(self.text.split()) if self.text else 0

    def get_character_count(self) -> int:
        """Retorna o número de caracteres no resumo."""
        return len(self.text) if self.text else 0

    def get_estimated_reading_time(self) -> float:
        """Retorna o tempo estimado de leitura em minutos (200 palavras/min)."""
        word_count = self.get_word_count()
        return word_count / 200.0 if word_count > 0 else 0.0

    def get_sections_count(self) -> int:
        """Retorna o número de seções do resumo."""
        return len(self.sections) if self.sections else 0

    def get_key_points_count(self) -> int:
        """Retorna o número de pontos-chave."""
        return len(self.key_points) if self.key_points else 0

    def get_compression_ratio(self, original_word_count: int) -> float:
        """
        Calcula a taxa de compressão do resumo em relação ao texto original.
        
        Args:
            original_word_count: Número de palavras do texto original
            
        Returns:
            Taxa de compressão (0.0 a 1.0)
        """
        if original_word_count == 0:
            return 0.0
        
        summary_word_count = self.get_word_count()
        return summary_word_count / original_word_count

    def get_structured_content(self) -> Dict[str, str]:
        """Retorna o conteúdo estruturado por seções."""
        if not self.sections:
            return {"resumo": self.text}
        
        structured = {}
        for section in sorted(self.sections, key=lambda s: s.order):
            structured[section.title] = section.content
        
        return structured

    def get_formatted_summary(self) -> str:
        """Retorna o resumo formatado com seções e pontos-chave."""
        formatted_parts = []
        
        # Adicionar resumo principal
        if self.text:
            formatted_parts.append("## Resumo")
            formatted_parts.append(self.text)
            formatted_parts.append("")
        
        # Adicionar seções estruturadas
        if self.sections:
            formatted_parts.append("## Detalhes")
            for section in sorted(self.sections, key=lambda s: s.order):
                formatted_parts.append(f"### {section.title}")
                formatted_parts.append(section.content)
                formatted_parts.append("")
        
        # Adicionar pontos-chave
        if self.key_points:
            formatted_parts.append("## Pontos-Chave")
            for i, point in enumerate(self.key_points, 1):
                formatted_parts.append(f"{i}. {point}")
            formatted_parts.append("")
        
        return "\n".join(formatted_parts)

    def get_quality_metrics(self) -> Dict[str, str]:
        """Retorna métricas de qualidade do resumo."""
        metrics = {
            "type": self.summary_type,
            "word_count": str(self.get_word_count()),
            "character_count": str(self.get_character_count()),
            "sections_count": str(self.get_sections_count()),
            "key_points_count": str(self.get_key_points_count()),
            "estimated_reading_time": f"{self.get_estimated_reading_time():.1f} min",
        }
        
        if self.provider:
            metrics["provider"] = self.provider
        
        if self.model:
            metrics["model"] = self.model
        
        if self.processing_time:
            metrics["processing_time"] = f"{self.processing_time:.2f}s"
        
        if self.confidence:
            metrics["confidence"] = f"{self.confidence:.2f}"
        
        return metrics

    def is_structured(self) -> bool:
        """Verifica se o resumo tem estrutura de seções."""
        return bool(self.sections and len(self.sections) > 0)

    def has_key_points(self) -> bool:
        """Verifica se o resumo tem pontos-chave."""
        return bool(self.key_points and len(self.key_points) > 0)