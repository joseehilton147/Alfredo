"""
Testes unitários para validadores de resumo.

Este módulo testa todas as funções de validação específicas para
entidades de resumo, garantindo que as regras de negócio sejam
aplicadas corretamente.
"""

import pytest
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError
from src.domain.validators.summary_validators import (
    validate_summary_text,
    validate_summary_type,
    validate_summary_language,
    validate_summary_provider,
    validate_summary_model,
    validate_summary_confidence,
    validate_processing_time,
)


class TestValidateSummaryText:
    """Testes para validação de texto do resumo."""
    
    def test_valid_text(self):
        """Testa textos válidos."""
        valid_texts = [
            "Este é um resumo válido.",
            "Resumo com múltiplas linhas\ne caracteres especiais: áéíóú!",
            "A" * 100_000,  # Texto longo mas dentro do limite
        ]
        
        for text in valid_texts:
            # Não deve lançar exceção
            validate_summary_text(text)
    
    def test_empty_text(self):
        """Testa texto vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_text("")
        
        assert exc_info.value.field == "summary_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_text(self):
        """Testa texto apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_text("   \n\t  ")
        
        assert exc_info.value.field == "summary_text"
        assert "vazio" in exc_info.value.constraint
    
    def test_text_too_long(self):
        """Testa texto muito longo."""
        long_text = "a" * 100_001  # Acima do limite
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_text(long_text)
        
        assert exc_info.value.field == "summary_text"
        assert "100,000" in exc_info.value.constraint
        assert exc_info.value.details["current_length"] == 100_001


class TestValidateSummaryType:
    """Testes para validação de tipo do resumo."""
    
    def test_supported_types(self):
        """Testa tipos suportados."""
        supported_types = [
            "general", "bullet_points", "structured", "executive",
            "detailed", "key_insights", "timeline", "topics"
        ]
        
        for summary_type in supported_types:
            # Não deve lançar exceção
            validate_summary_type(summary_type)
    
    def test_empty_type(self):
        """Testa tipo vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_type("")
        
        assert exc_info.value.field == "summary_type"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_type(self):
        """Testa tipo apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_type("   ")
        
        assert exc_info.value.field == "summary_type"
        assert "vazio" in exc_info.value.constraint
    
    def test_unsupported_type(self):
        """Testa tipo não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_type("invalid_type")
        
        assert exc_info.value.field == "summary_type"
        assert "não suportado" in exc_info.value.constraint
        assert "general" in exc_info.value.constraint  # Deve listar tipos aceitos
    
    def test_case_insensitive(self):
        """Testa que a validação é case-insensitive."""
        # Deve aceitar maiúsculas/minúsculas
        validate_summary_type("GENERAL")
        validate_summary_type("General")
        validate_summary_type("gEnErAl")


class TestValidateSummaryLanguage:
    """Testes para validação de idioma do resumo."""
    
    def test_supported_languages(self):
        """Testa idiomas suportados."""
        supported_languages = [
            "pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "pt-br", "en-us", "en-gb", "es-es", "fr-fr"
        ]
        
        for language in supported_languages:
            # Não deve lançar exceção
            validate_summary_language(language)
    
    def test_empty_language(self):
        """Testa idioma vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_language("")
        
        assert exc_info.value.field == "summary_language"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_language(self):
        """Testa idioma apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_language("   ")
        
        assert exc_info.value.field == "summary_language"
        assert "vazio" in exc_info.value.constraint
    
    def test_unsupported_language(self):
        """Testa idioma não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_language("xyz")
        
        assert exc_info.value.field == "summary_language"
        assert "não suportado" in exc_info.value.constraint
        assert "pt" in exc_info.value.constraint  # Deve listar idiomas aceitos
    
    def test_case_insensitive(self):
        """Testa que a validação é case-insensitive."""
        # Deve aceitar maiúsculas/minúsculas
        validate_summary_language("PT")
        validate_summary_language("En")
        validate_summary_language("PT-BR")


class TestValidateSummaryProvider:
    """Testes para validação de provedor do resumo."""
    
    def test_valid_providers(self):
        """Testa provedores válidos."""
        valid_providers = [
            "groq", "ollama", "openai", "azure", "google", "aws", "anthropic"
        ]
        
        for provider in valid_providers:
            # Não deve lançar exceção
            validate_summary_provider(provider)
    
    def test_none_provider(self):
        """Testa provedor None (deve ser aceito)."""
        # Não deve lançar exceção
        validate_summary_provider(None)
    
    def test_empty_provider(self):
        """Testa provedor vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_provider("")
        
        assert exc_info.value.field == "summary_provider"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_provider(self):
        """Testa provedor apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_provider("   ")
        
        assert exc_info.value.field == "summary_provider"
        assert "vazio" in exc_info.value.constraint
    
    def test_unknown_provider(self):
        """Testa provedor desconhecido (deve ser aceito)."""
        # Provedores desconhecidos são aceitos, apenas registrados
        validate_summary_provider("unknown_provider")


class TestValidateSummaryModel:
    """Testes para validação de modelo do resumo."""
    
    def test_valid_models(self):
        """Testa modelos válidos."""
        valid_models = [
            "llama-3.3-70b-versatile", "gpt-4", "gpt-3.5-turbo",
            "llama3:8b", "mistral:7b", "codellama:7b"
        ]
        
        for model in valid_models:
            # Não deve lançar exceção
            validate_summary_model(model)
    
    def test_none_model(self):
        """Testa modelo None (deve ser aceito)."""
        # Não deve lançar exceção
        validate_summary_model(None)
    
    def test_empty_model(self):
        """Testa modelo vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_model("")
        
        assert exc_info.value.field == "summary_model"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_model(self):
        """Testa modelo apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_model("   ")
        
        assert exc_info.value.field == "summary_model"
        assert "vazio" in exc_info.value.constraint
    
    def test_unknown_model(self):
        """Testa modelo desconhecido (deve ser aceito)."""
        # Modelos desconhecidos são aceitos, apenas registrados
        validate_summary_model("unknown_model")


class TestValidateSummaryConfidence:
    """Testes para validação de confiança do resumo."""
    
    def test_valid_confidence_values(self):
        """Testa valores válidos de confiança."""
        valid_values = [0.0, 0.5, 0.8, 0.95, 1.0]
        
        for confidence in valid_values:
            # Não deve lançar exceção
            validate_summary_confidence(confidence)
    
    def test_none_confidence(self):
        """Testa confiança None (deve ser aceito)."""
        # Não deve lançar exceção
        validate_summary_confidence(None)
    
    def test_negative_confidence(self):
        """Testa confiança negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_confidence(-0.1)
        
        assert exc_info.value.field == "summary_confidence"
        assert "maior ou igual a 0.0" in exc_info.value.constraint
    
    def test_confidence_above_one(self):
        """Testa confiança acima de 1.0."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_summary_confidence(1.1)
        
        assert exc_info.value.field == "summary_confidence"
        assert "menor ou igual a 1.0" in exc_info.value.constraint


class TestValidateProcessingTime:
    """Testes para validação de tempo de processamento."""
    
    def test_valid_processing_times(self):
        """Testa tempos válidos de processamento."""
        valid_times = [0.0, 1.5, 60.0, 1800.0, 3600.0]  # 0s a 1h
        
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
            validate_processing_time(3601.0)  # Acima de 1 hora
        
        assert exc_info.value.field == "processing_time"
        assert "muito alto" in exc_info.value.constraint
        assert exc_info.value.details["max_processing_time"] == 3600


class TestSummaryValidatorsEdgeCases:
    """Testes para casos extremos dos validadores de resumo."""
    
    def test_boundary_text_length(self):
        """Testa comprimentos limítrofes de texto."""
        # Exatamente no limite
        max_text = "a" * 100_000
        validate_summary_text(max_text)
        
        # Um caractere acima do limite
        with pytest.raises(InvalidVideoFormatError):
            validate_summary_text("a" * 100_001)
    
    def test_unicode_text(self):
        """Testa texto com caracteres Unicode."""
        unicode_text = "Resumo com émojis 🎥📝 e acentos: áéíóú àèìòù âêîôû ãõ ç"
        validate_summary_text(unicode_text)
    
    def test_confidence_boundary_values(self):
        """Testa valores limítrofes de confiança."""
        # Exatamente nos limites
        validate_summary_confidence(0.0)
        validate_summary_confidence(1.0)
        
        # Fora dos limites
        with pytest.raises(InvalidVideoFormatError):
            validate_summary_confidence(-0.000001)
        
        with pytest.raises(InvalidVideoFormatError):
            validate_summary_confidence(1.000001)
    
    def test_processing_time_boundary_values(self):
        """Testa valores limítrofes de tempo de processamento."""
        # Exatamente no limite
        validate_processing_time(3600.0)  # 1 hora
        
        # Fora do limite
        with pytest.raises(InvalidVideoFormatError):
            validate_processing_time(3600.1)
    
    def test_type_with_whitespace(self):
        """Testa tipo com espaços extras."""
        # Deve funcionar após strip
        validate_summary_type("  general  ")
        validate_summary_type("\tstructured\n")
    
    def test_language_with_whitespace(self):
        """Testa idioma com espaços extras."""
        # Deve funcionar após strip
        validate_summary_language("  pt  ")
        validate_summary_language("\ten\n")