"""
Testes unitários para a entidade Transcription.
"""

import pytest
from datetime import datetime

from src.domain.entities.transcription import Transcription, TranscriptionSegment
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestTranscriptionSegmentCreation:
    """Testes para criação da entidade TranscriptionSegment."""
    
    def test_create_valid_segment(self):
        """Testa criação de segmento válido."""
        segment = TranscriptionSegment(
            text="Este é um segmento de teste.",
            start_time=10.0,
            end_time=15.0,
            confidence=0.95
        )
        
        assert segment.text == "Este é um segmento de teste."
        assert segment.start_time == 10.0
        assert segment.end_time == 15.0
        assert segment.confidence == 0.95
    
    def test_create_segment_without_confidence(self):
        """Testa criação de segmento sem confiança."""
        segment = TranscriptionSegment(
            text="Segmento sem confiança.",
            start_time=0.0,
            end_time=5.0
        )
        
        assert segment.text == "Segmento sem confiança."
        assert segment.confidence is None


class TestTranscriptionSegmentValidation:
    """Testes para validação da entidade TranscriptionSegment."""
    
    def test_invalid_empty_text(self):
        """Testa texto vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            TranscriptionSegment(text="", start_time=0.0, end_time=5.0)
        
        assert exc_info.value.field == "segment_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_negative_start_time(self):
        """Testa tempo inicial negativo."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            TranscriptionSegment(text="Teste", start_time=-1.0, end_time=5.0)
        
        assert exc_info.value.field == "start_time"
        assert "negativo" in exc_info.value.constraint
    
    def test_invalid_end_time_before_start(self):
        """Testa tempo final antes do inicial."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            TranscriptionSegment(text="Teste", start_time=10.0, end_time=5.0)
        
        assert exc_info.value.field == "end_time"
        assert "maior que tempo inicial" in exc_info.value.constraint
    
    def test_invalid_confidence_negative(self):
        """Testa confiança negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            TranscriptionSegment(
                text="Teste", 
                start_time=0.0, 
                end_time=5.0, 
                confidence=-0.1
            )
        
        assert exc_info.value.field == "transcription_confidence"
        assert "maior ou igual a 0.0" in exc_info.value.constraint
    
    def test_invalid_confidence_above_one(self):
        """Testa confiança acima de 1.0."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            TranscriptionSegment(
                text="Teste", 
                start_time=0.0, 
                end_time=5.0, 
                confidence=1.1
            )
        
        assert exc_info.value.field == "transcription_confidence"
        assert "menor ou igual a 1.0" in exc_info.value.constraint


class TestTranscriptionSegmentMethods:
    """Testes para métodos da entidade TranscriptionSegment."""
    
    def test_get_duration(self):
        """Testa cálculo da duração."""
        segment = TranscriptionSegment(
            text="Teste", 
            start_time=10.0, 
            end_time=15.5
        )
        
        assert segment.get_duration() == 5.5
    
    def test_get_formatted_time(self):
        """Testa formatação do tempo."""
        segment = TranscriptionSegment(
            text="Teste", 
            start_time=65.0,  # 1:05
            end_time=125.0    # 2:05
        )
        
        assert segment.get_formatted_time() == "[01:05 - 02:05]"


class TestTranscriptionCreation:
    """Testes para criação da entidade Transcription."""
    
    def test_create_valid_transcription(self):
        """Testa criação de transcrição válida."""
        transcription = Transcription(
            text="Esta é uma transcrição de teste.",
            language="pt",
            confidence=0.9,
            provider="whisper",
            model="base"
        )
        
        assert transcription.text == "Esta é uma transcrição de teste."
        assert transcription.language == "pt"
        assert transcription.confidence == 0.9
        assert transcription.provider == "whisper"
        assert transcription.model == "base"
        assert isinstance(transcription.created_at, datetime)
        assert transcription.metadata == {}
        assert transcription.segments == []
    
    def test_create_transcription_minimal(self):
        """Testa criação de transcrição com campos mínimos."""
        transcription = Transcription(text="Transcrição mínima.")
        
        assert transcription.text == "Transcrição mínima."
        assert transcription.language == "pt"  # Padrão
        assert transcription.confidence is None
        assert transcription.provider is None
    
    def test_create_transcription_with_segments(self):
        """Testa criação de transcrição com segmentos."""
        segments = [
            TranscriptionSegment("Primeiro segmento.", 0.0, 5.0),
            TranscriptionSegment("Segundo segmento.", 5.0, 10.0)
        ]
        
        transcription = Transcription(
            text="Primeiro segmento. Segundo segmento.",
            segments=segments
        )
        
        assert len(transcription.segments) == 2
        assert transcription.segments[0].text == "Primeiro segmento."


class TestTranscriptionValidation:
    """Testes para validação da entidade Transcription."""
    
    def test_invalid_empty_text(self):
        """Testa texto vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Transcription(text="")
        
        assert exc_info.value.field == "transcription_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_text_too_long(self):
        """Testa texto muito longo."""
        long_text = "a" * 1_000_001  # Acima do limite
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Transcription(text=long_text)
        
        assert exc_info.value.field == "transcription_text"
        assert "1,000,000 caracteres" in exc_info.value.constraint
    
    def test_invalid_language_empty(self):
        """Testa idioma vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Transcription(text="Teste", language="")
        
        assert exc_info.value.field == "transcription_language"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_language_unsupported(self):
        """Testa idioma não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Transcription(text="Teste", language="xyz")
        
        assert exc_info.value.field == "transcription_language"
        assert "não suportado" in exc_info.value.constraint
    
    def test_invalid_confidence_negative(self):
        """Testa confiança negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Transcription(text="Teste", confidence=-0.1)
        
        assert exc_info.value.field == "transcription_confidence"
        assert "maior ou igual a 0.0" in exc_info.value.constraint


class TestTranscriptionMethods:
    """Testes para métodos da entidade Transcription."""
    
    def test_get_word_count(self):
        """Testa contagem de palavras."""
        transcription = Transcription(text="Esta é uma transcrição de teste.")
        assert transcription.get_word_count() == 6
        
        # Teste com texto mínimo válido
        transcription_single = Transcription(text="palavra")
        assert transcription_single.get_word_count() == 1
    
    def test_get_character_count(self):
        """Testa contagem de caracteres."""
        transcription = Transcription(text="Teste")
        assert transcription.get_character_count() == 5
    
    def test_get_estimated_reading_time(self):
        """Testa tempo estimado de leitura."""
        # 200 palavras = 1 minuto
        text_200_words = " ".join(["palavra"] * 200)
        transcription = Transcription(text=text_200_words)
        assert transcription.get_estimated_reading_time() == 1.0
        
        # 100 palavras = 0.5 minutos
        text_100_words = " ".join(["palavra"] * 100)
        transcription_half = Transcription(text=text_100_words)
        assert transcription_half.get_estimated_reading_time() == 0.5
    
    def test_get_confidence_level(self):
        """Testa nível de confiança descritivo."""
        test_cases = [
            (0.95, "Muito Alta"),
            (0.85, "Alta"),
            (0.75, "Média"),
            (0.65, "Baixa"),
            (0.5, "Muito Baixa"),
            (None, "Desconhecido")
        ]
        
        for confidence, expected in test_cases:
            transcription = Transcription(text="Teste", confidence=confidence)
            assert transcription.get_confidence_level() == expected
    
    def test_get_segments_count(self):
        """Testa contagem de segmentos."""
        segments = [
            TranscriptionSegment("Seg 1", 0.0, 5.0),
            TranscriptionSegment("Seg 2", 5.0, 10.0)
        ]
        
        transcription = Transcription(text="Seg 1 Seg 2", segments=segments)
        assert transcription.get_segments_count() == 2
        
        transcription_no_segments = Transcription(text="Teste")
        assert transcription_no_segments.get_segments_count() == 0
    
    def test_get_total_duration(self):
        """Testa duração total baseada nos segmentos."""
        segments = [
            TranscriptionSegment("Seg 1", 0.0, 5.0),
            TranscriptionSegment("Seg 2", 5.0, 12.0),
            TranscriptionSegment("Seg 3", 8.0, 15.0)  # Ordem correta: start < end
        ]
        
        transcription = Transcription(text="Teste", segments=segments)
        assert transcription.get_total_duration() == 15.0  # Máximo end_time
    
    def test_get_text_with_timestamps(self):
        """Testa texto com timestamps."""
        segments = [
            TranscriptionSegment("Primeiro", 0.0, 5.0),
            TranscriptionSegment("Segundo", 65.0, 70.0)  # 1:05 - 1:10
        ]
        
        transcription = Transcription(text="Teste", segments=segments)
        result = transcription.get_text_with_timestamps()
        
        assert "[00:00 - 00:05] Primeiro" in result
        assert "[01:05 - 01:10] Segundo" in result
    
    def test_get_quality_metrics(self):
        """Testa métricas de qualidade."""
        transcription = Transcription(
            text="Esta é uma transcrição de teste.",
            confidence=0.9,
            provider="whisper",
            model="base",
            processing_time=10.5
        )
        
        metrics = transcription.get_quality_metrics()
        
        assert metrics["confidence_level"] == "Muito Alta"
        assert metrics["word_count"] == "6"
        assert metrics["character_count"] == "32"  # Contagem correta de caracteres
        assert metrics["provider"] == "whisper"
        assert metrics["model"] == "base"
        assert metrics["processing_time"] == "10.50s"


class TestTranscriptionEdgeCases:
    """Testes para casos extremos da entidade Transcription."""
    
    def test_maximum_text_length(self):
        """Testa texto com comprimento máximo permitido."""
        max_text = "a" * 1_000_000  # Exatamente o máximo
        transcription = Transcription(text=max_text)
        assert len(transcription.text) == 1_000_000
    
    def test_supported_languages(self):
        """Testa idiomas suportados."""
        supported_langs = ['pt', 'en', 'es', 'fr', 'de', 'pt-br', 'en-us']
        
        for lang in supported_langs:
            # Não deve lançar exceção
            transcription = Transcription(text="Teste", language=lang)
            assert transcription.language == lang
    
    def test_confidence_boundary_values(self):
        """Testa valores limítrofes de confiança."""
        # Valores válidos
        valid_confidences = [0.0, 0.5, 1.0]
        
        for confidence in valid_confidences:
            transcription = Transcription(text="Teste", confidence=confidence)
            assert transcription.confidence == confidence
    
    def test_unicode_text(self):
        """Testa texto com caracteres Unicode."""
        unicode_text = "Transcrição com acentos: ção, ã, é, ü, 🎥"
        transcription = Transcription(text=unicode_text)
        assert transcription.text == unicode_text
    
    def test_empty_segments_list(self):
        """Testa lista de segmentos vazia."""
        transcription = Transcription(text="Teste", segments=[])
        assert transcription.get_segments_count() == 0
        assert transcription.get_total_duration() == 0.0