"""
Testes unitários para validadores de transcrição.

Este módulo testa todas as funções de validação específicas para
entidades de transcrição, garantindo que as regras de negócio sejam
aplicadas corretamente.
"""

import pytest
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError
from src.domain.validators.transcription_validators import (
    validate_transcription_text,
    validate_transcription_language,
    validate_transcription_confidence,
    validate_transcription_provider,
    validate_transcription_model,
    validate_processing_time,
)


class TestValidateTranscriptionText:
    """Testes para validação de texto da transcrição."""
    
    def test_valid_text(self):
        """Testa textos válidos."""
        valid_texts = [
            "Esta é uma transcrição válida.",
            "Transcrição com múltiplas linhas\ne caracteres especiais: áéíóú!",
            "A" * 1_000_000,  # Texto longo mas dentro do limite
        ]
        
        for text in valid_texts:
            # Não deve lançar exceção
            validate_transcription_text(text)
    
    def test_empty_text(self):
        """Testa texto vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_text("")
        
        assert exc_info.value.field == "transcription_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_text(self):
        """Testa texto apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_text("   \n\t  ")
        
        assert exc_info.value.field == "transcription_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_text_too_long(self):
        """Testa texto muito longo."""
        long_text = "a" * 1_000_001  # Acima do limite
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_text(long_text)
        
        assert exc_info.value.field == "transcription_text"
        assert "1,000,000" in exc_info.value.constraint
        assert exc_info.value.details["current_length"] == 1_000_001


class TestValidateTranscriptionLanguage:
    """Testes para validação de idioma da transcrição."""
    
    def test_supported_languages(self):
        """Testa idiomas suportados."""
        supported_languages = [
            "pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "pt-br", "en-us", "en-gb", "es-es", "fr-fr"
        ]
        
        for language in supported_languages:
            # Não deve lançar exceção
            validate_transcription_language(language)
    
    def test_empty_language(self):
        """Testa idioma vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_language("")
        
        assert exc_info.value.field == "transcription_language"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_language(self):
        """Testa idioma apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_language("   ")
        
        assert exc_info.value.field == "transcription_language"
        assert "vazio" in exc_info.value.constraint
    
    def test_unsupported_language(self):
        """Testa idioma não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_language("xyz")
        
        assert exc_info.value.field == "transcription_language"
        assert "não suportado" in exc_info.value.constraint
        assert "pt" in exc_info.value.constraint  # Deve listar idiomas aceitos
    
    def test_case_insensitive(self):
        """Testa que a validação é case-insensitive."""
        # Deve aceitar maiúsculas/minúsculas
        validate_transcription_language("PT")
        validate_transcription_language("En")
        validate_transcription_language("PT-BR")


class TestValidateTranscriptionConfidence:
    """Testes para validação de confiança da transcrição."""
    
    def test_valid_confidence_values(self):
        """Testa valores válidos de confiança."""
        valid_values = [0.0, 0.5, 0.8, 0.95, 1.0]
        
        for confidence in valid_values:
            # Não deve lançar exceção
            validate_transcription_confidence(confidence)
    
    def test_negative_confidence(self):
        """Testa confiança negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_confidence(-0.1)
        
        assert exc_info.value.field == "transcription_confidence"
        assert "maior ou igual a 0.0" in exc_info.value.constraint
    
    def test_confidence_above_one(self):
        """Testa confiança acima de 1.0."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_confidence(1.1)
        
        assert exc_info.value.field == "transcription_confidence"
        assert "menor ou igual a 1.0" in exc_info.value.constraint


class TestValidateTranscriptionProvider:
    """Testes para validação de provedor da transcrição."""
    
    def test_valid_providers(self):
        """Testa provedores válidos."""
        valid_providers = [
            "whisper", "groq", "ollama", "openai", "azure", "google", "aws"
        ]
        
        for provider in valid_providers:
            # Não deve lançar exceção
            validate_transcription_provider(provider)
    
    def test_none_provider(self):
        """Testa provedor None (deve ser aceito)."""
        # Não deve lançar exceção
        validate_transcription_provider(None)
    
    def test_empty_provider(self):
        """Testa provedor vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_provider("")
        
        assert exc_info.value.field == "transcription_provider"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_provider(self):
        """Testa provedor apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_provider("   ")
        
        assert exc_info.value.field == "transcription_provider"
        assert "vazio" in exc_info.value.constraint
    
    def test_unknown_provider(self):
        """Testa provedor desconhecido (deve ser aceito)."""
        # Provedores desconhecidos são aceitos, apenas registrados
        validate_transcription_provider("unknown_provider")


class TestValidateTranscriptionModel:
    """Testes para validação de modelo da transcrição."""
    
    def test_valid_models(self):
        """Testa modelos válidos."""
        valid_models = [
            "tiny", "base", "small", "medium", "large", "large-v2", "large-v3"
        ]
        
        for model in valid_models:
            # Não deve lançar exceção
            validate_transcription_model(model)
    
    def test_none_model(self):
        """Testa modelo None (deve ser aceito)."""
        # Não deve lançar exceção
        validate_transcription_model(None)
    
    def test_empty_model(self):
        """Testa modelo vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_model("")
        
        assert exc_info.value.field == "transcription_model"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_model(self):
        """Testa modelo apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_transcription_model("   ")
        
        assert exc_info.value.field == "transcription_model"
        assert "vazio" in exc_info.value.constraint
    
    def test_unknown_model(self):
        """Testa modelo desconhecido (deve ser aceito)."""
        # Modelos desconhecidos são aceitos, apenas registrados
        validate_transcription_model("unknown_model")


class TestValidateProcessingTime:
    """Testes para validação de tempo de processamento."""
    
    def test_valid_processing_times(self):
        """Testa tempos válidos de processamento."""
        valid_times = [0.0, 1.5, 60.0, 1800.0, 86400.0]  # 0s a 24h
        
        for time in valid_times:
            # Não deve lançar exceção
            validate_processing_time(time)
    
    def test_none_processing_time(self):
        """Testa tempo None (deve ser aceito)."""
        # Não deve lançar exceção
        validate_processing_time(None)
    
    def test_negative_processing_time(self):
        """Testa tempo negativo."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_processing_time(-1.0)
        
        assert exc_info.value.field == "processing_time"
        assert "não pode ser negativo" in exc_info.value.constraint
    
    def test_processing_time_too_high(self):
        """Testa tempo muito alto."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_processing_time(86401.0)  # Acima de 24 horas
        
        assert exc_info.value.field == "processing_time"
        assert "muito alto" in exc_info.value.constraint
        assert exc_info.value.details["max_processing_time"] == 86400


class TestTranscriptionValidatorsEdgeCases:
    """Testes para casos extremos dos validadores de transcrição."""
    
    def test_boundary_text_length(self):
        """Testa comprimentos limítrofes de texto."""
        # Exatamente no limite
        max_text = "a" * 1_000_000
        validate_transcription_text(max_text)
        
        # Um caractere acima do limite
        with pytest.raises(InvalidVideoFormatError):
            validate_transcription_text("a" * 1_000_001)
    
    def test_unicode_text(self):
        """Testa texto com caracteres Unicode."""
        unicode_text = "Transcrição com émojis 🎥📝 e acentos: áéíóú àèìòù âêîôû ãõ ç"
        validate_transcription_text(unicode_text)
    
    def test_confidence_boundary_values(self):
        """Testa valores limítrofes de confiança."""
        # Exatamente nos limites
        validate_transcription_confidence(0.0)
        validate_transcription_confidence(1.0)
        
        # Fora dos limites
        with pytest.raises(InvalidVideoFormatError):
            validate_transcription_confidence(-0.000001)
        
        with pytest.raises(InvalidVideoFormatError):
            validate_transcription_confidence(1.000001)
    
    def test_processing_time_boundary_values(self):
        """Testa valores limítrofes de tempo de processamento."""
        # Exatamente no limite
        validate_processing_time(86400.0)  # 24 horas
        
        # Fora do limite
        with pytest.raises(InvalidVideoFormatError):
            validate_processing_time(86400.1)
    
    def test_language_with_whitespace(self):
        """Testa idioma com espaços extras."""
        # Deve funcionar após strip
        validate_transcription_language("  pt  ")
        validate_transcription_language("\ten\n")
    
    def test_provider_with_whitespace(self):
        """Testa provedor com espaços extras."""
        # Deve funcionar após strip
        validate_transcription_provider("  whisper  ")
        validate_transcription_provider("\tgroq\n")
    
    def test_model_with_whitespace(self):
        """Testa modelo com espaços extras."""
        # Deve funcionar após strip
        validate_transcription_model("  base  ")
        validate_transcription_model("\tlarge\n")