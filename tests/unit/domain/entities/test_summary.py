"""
Testes unitários para a entidade Summary.
"""

import pytest
from datetime import datetime

from src.domain.entities.summary import Summary, SummarySection
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestSummarySectionCreation:
    """Testes para criação da entidade SummarySection."""
    
    def test_create_valid_section(self):
        """Testa criação de seção válida."""
        section = SummarySection(
            title="Introdução",
            content="Este é o conteúdo da introdução.",
            order=1
        )
        
        assert section.title == "Introdução"
        assert section.content == "Este é o conteúdo da introdução."
        assert section.order == 1
    
    def test_create_section_default_order(self):
        """Testa criação de seção com ordem padrão."""
        section = SummarySection(
            title="Seção",
            content="Conteúdo da seção."
        )
        
        assert section.order == 0


class TestSummarySectionValidation:
    """Testes para validação da entidade SummarySection."""
    
    def test_invalid_empty_title(self):
        """Testa título vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            SummarySection(title="", content="Conteúdo")
        
        assert exc_info.value.field == "section_title"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_empty_content(self):
        """Testa conteúdo vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            SummarySection(title="Título", content="")
        
        assert exc_info.value.field == "section_content"
        assert "vazio" in exc_info.value.constraint


class TestSummarySectionMethods:
    """Testes para métodos da entidade SummarySection."""
    
    def test_get_word_count(self):
        """Testa contagem de palavras na seção."""
        section = SummarySection(
            title="Teste",
            content="Esta seção tem cinco palavras."
        )
        
        assert section.get_word_count() == 5


class TestSummaryCreation:
    """Testes para criação da entidade Summary."""
    
    def test_create_valid_summary(self):
        """Testa criação de resumo válido."""
        summary = Summary(
            text="Este é um resumo de teste.",
            summary_type="general",
            language="pt",
            provider="groq",
            model="llama-3.3-70b-versatile"
        )
        
        assert summary.text == "Este é um resumo de teste."
        assert summary.summary_type == "general"
        assert summary.language == "pt"
        assert summary.provider == "groq"
        assert summary.model == "llama-3.3-70b-versatile"
        assert isinstance(summary.created_at, datetime)
        assert summary.metadata == {}
        assert summary.sections == []
        assert summary.key_points == []
    
    def test_create_summary_minimal(self):
        """Testa criação de resumo com campos mínimos."""
        summary = Summary(text="Resumo mínimo.")
        
        assert summary.text == "Resumo mínimo."
        assert summary.summary_type == "general"  # Padrão
        assert summary.language == "pt"  # Padrão
        assert summary.provider is None
    
    def test_create_summary_with_sections(self):
        """Testa criação de resumo com seções."""
        sections = [
            SummarySection("Introdução", "Conteúdo da introdução.", 1),
            SummarySection("Desenvolvimento", "Conteúdo do desenvolvimento.", 2)
        ]
        
        summary = Summary(
            text="Resumo estruturado.",
            summary_type="structured",
            sections=sections
        )
        
        assert len(summary.sections) == 2
        assert summary.sections[0].title == "Introdução"
    
    def test_create_summary_with_key_points(self):
        """Testa criação de resumo com pontos-chave."""
        key_points = [
            "Primeiro ponto importante",
            "Segundo ponto importante",
            "Terceiro ponto importante"
        ]
        
        summary = Summary(
            text="Resumo com pontos-chave.",
            key_points=key_points
        )
        
        assert len(summary.key_points) == 3
        assert summary.key_points[0] == "Primeiro ponto importante"


class TestSummaryValidation:
    """Testes para validação da entidade Summary."""
    
    def test_invalid_empty_text(self):
        """Testa texto vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Summary(text="")
        
        assert exc_info.value.field == "summary_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_text_too_long(self):
        """Testa texto muito longo."""
        long_text = "a" * 100_001  # Acima do limite
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Summary(text=long_text)
        
        assert exc_info.value.field == "summary_text"
        assert "100,000 caracteres" in exc_info.value.constraint
    
    def test_invalid_summary_type_empty(self):
        """Testa tipo vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Summary(text="Teste", summary_type="")
        
        assert exc_info.value.field == "summary_type"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_summary_type_unsupported(self):
        """Testa tipo não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Summary(text="Teste", summary_type="invalid_type")
        
        assert exc_info.value.field == "summary_type"
        assert "não suportado" in exc_info.value.constraint
    
    def test_invalid_language_empty(self):
        """Testa idioma vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Summary(text="Teste", language="")
        
        assert exc_info.value.field == "summary_language"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_language_unsupported(self):
        """Testa idioma não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Summary(text="Teste", language="xyz")
        
        assert exc_info.value.field == "summary_language"
        assert "não suportado" in exc_info.value.constraint


class TestSummaryMethods:
    """Testes para métodos da entidade Summary."""
    
    def test_get_word_count(self):
        """Testa contagem de palavras."""
        summary = Summary(text="Este é um resumo de teste.")
        assert summary.get_word_count() == 6
    
    def test_get_character_count(self):
        """Testa contagem de caracteres."""
        summary = Summary(text="Teste")
        assert summary.get_character_count() == 5
    
    def test_get_estimated_reading_time(self):
        """Testa tempo estimado de leitura."""
        # 200 palavras = 1 minuto
        text_200_words = " ".join(["palavra"] * 200)
        summary = Summary(text=text_200_words)
        assert summary.get_estimated_reading_time() == 1.0
    
    def test_get_sections_count(self):
        """Testa contagem de seções."""
        sections = [
            SummarySection("Seção 1", "Conteúdo 1"),
            SummarySection("Seção 2", "Conteúdo 2")
        ]
        
        summary = Summary(text="Teste", sections=sections)
        assert summary.get_sections_count() == 2
    
    def test_get_key_points_count(self):
        """Testa contagem de pontos-chave."""
        key_points = ["Ponto 1", "Ponto 2", "Ponto 3"]
        
        summary = Summary(text="Teste", key_points=key_points)
        assert summary.get_key_points_count() == 3
    
    def test_get_compression_ratio(self):
        """Testa cálculo da taxa de compressão."""
        summary = Summary(text="Resumo com cinco palavras.")  # 4 palavras
        
        # Texto original com 20 palavras -> ratio = 4/20 = 0.2
        ratio = summary.get_compression_ratio(20)
        assert ratio == 0.2
        
        # Texto original com 0 palavras -> ratio = 0
        ratio_zero = summary.get_compression_ratio(0)
        assert ratio_zero == 0.0
    
    def test_get_structured_content(self):
        """Testa conteúdo estruturado."""
        sections = [
            SummarySection("Conclusão", "Conteúdo da conclusão.", 3),
            SummarySection("Introdução", "Conteúdo da introdução.", 1),
            SummarySection("Desenvolvimento", "Conteúdo do desenvolvimento.", 2)
        ]
        
        summary = Summary(text="Teste", sections=sections)
        structured = summary.get_structured_content()
        
        # Deve estar ordenado por order
        keys = list(structured.keys())
        assert keys == ["Introdução", "Desenvolvimento", "Conclusão"]
        assert structured["Introdução"] == "Conteúdo da introdução."
    
    def test_get_structured_content_no_sections(self):
        """Testa conteúdo estruturado sem seções."""
        summary = Summary(text="Resumo simples.")
        structured = summary.get_structured_content()
        
        assert structured == {"resumo": "Resumo simples."}
    
    def test_get_formatted_summary(self):
        """Testa resumo formatado."""
        sections = [
            SummarySection("Introdução", "Conteúdo da introdução.", 1)
        ]
        key_points = ["Ponto importante 1", "Ponto importante 2"]
        
        summary = Summary(
            text="Resumo principal.",
            sections=sections,
            key_points=key_points
        )
        
        formatted = summary.get_formatted_summary()
        
        assert "## Resumo" in formatted
        assert "Resumo principal." in formatted
        assert "## Detalhes" in formatted
        assert "### Introdução" in formatted
        assert "## Pontos-Chave" in formatted
        assert "1. Ponto importante 1" in formatted
    
    def test_get_quality_metrics(self):
        """Testa métricas de qualidade."""
        summary = Summary(
            text="Este é um resumo de teste.",
            summary_type="general",
            provider="groq",
            model="llama-3.3-70b-versatile",
            processing_time=5.2,
            confidence=0.85
        )
        
        metrics = summary.get_quality_metrics()
        
        assert metrics["type"] == "general"
        assert metrics["word_count"] == "6"
        assert metrics["provider"] == "groq"
        assert metrics["model"] == "llama-3.3-70b-versatile"
        assert metrics["processing_time"] == "5.20s"
        assert metrics["confidence"] == "0.85"
    
    def test_is_structured(self):
        """Testa verificação de estrutura."""
        summary_with_sections = Summary(
            text="Teste",
            sections=[SummarySection("Seção", "Conteúdo")]
        )
        assert summary_with_sections.is_structured() is True
        
        summary_without_sections = Summary(text="Teste")
        assert summary_without_sections.is_structured() is False
    
    def test_has_key_points(self):
        """Testa verificação de pontos-chave."""
        summary_with_points = Summary(
            text="Teste",
            key_points=["Ponto 1", "Ponto 2"]
        )
        assert summary_with_points.has_key_points() is True
        
        summary_without_points = Summary(text="Teste")
        assert summary_without_points.has_key_points() is False


class TestSummaryEdgeCases:
    """Testes para casos extremos da entidade Summary."""
    
    def test_maximum_text_length(self):
        """Testa texto com comprimento máximo permitido."""
        max_text = "a" * 100_000  # Exatamente o máximo
        summary = Summary(text=max_text)
        assert len(summary.text) == 100_000
    
    def test_supported_summary_types(self):
        """Testa tipos de resumo suportados."""
        supported_types = [
            'general', 'bullet_points', 'structured', 'executive',
            'detailed', 'key_insights', 'timeline', 'topics'
        ]
        
        for summary_type in supported_types:
            # Não deve lançar exceção
            summary = Summary(text="Teste", summary_type=summary_type)
            assert summary.summary_type == summary_type
    
    def test_supported_languages(self):
        """Testa idiomas suportados."""
        supported_langs = ['pt', 'en', 'es', 'fr', 'de', 'pt-br', 'en-us']
        
        for lang in supported_langs:
            # Não deve lançar exceção
            summary = Summary(text="Teste", language=lang)
            assert summary.language == lang
    
    def test_unicode_text(self):
        """Testa texto com caracteres Unicode."""
        unicode_text = "Resumo com acentos: ção, ã, é, ü, 🎥"
        summary = Summary(text=unicode_text)
        assert summary.text == unicode_text
    
    def test_empty_sections_and_points(self):
        """Testa listas vazias."""
        summary = Summary(text="Teste", sections=[], key_points=[])
        assert summary.get_sections_count() == 0
        assert summary.get_key_points_count() == 0
        assert not summary.is_structured()
        assert not summary.has_key_points()
    
    def test_confidence_boundary_values(self):
        """Testa valores limítrofes de confiança."""
        # Valores válidos (testados indiretamente através dos validadores)
        valid_confidences = [0.0, 0.5, 1.0, None]
        
        for confidence in valid_confidences:
            summary = Summary(text="Teste", confidence=confidence)
            assert summary.confidence == confidence