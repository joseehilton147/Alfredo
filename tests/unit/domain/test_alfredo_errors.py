"""
Testes unitários para a hierarquia de exceções customizadas do Alfredo AI.

Este módulo testa todas as funcionalidades das exceções específicas do domínio,
incluindo serialização, preservação de detalhes e propagação de causas.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.domain.exceptions import (
    AlfredoError,
    ProviderUnavailableError,
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
)


class TestAlfredoError:
    """Testes para a classe base AlfredoError."""
    
    def test_basic_initialization(self):
        """Testa inicialização básica da exceção."""
        error = AlfredoError("Erro de teste")
        
        assert error.message == "Erro de teste"
        assert error.details == {}
        assert error.cause is None
        assert isinstance(error.timestamp, datetime)
        assert str(error) == "Erro de teste"
    
    def test_initialization_with_details(self):
        """Testa inicialização com detalhes estruturados."""
        details = {"key1": "value1", "key2": 42}
        error = AlfredoError("Erro com detalhes", details=details)
        
        assert error.message == "Erro com detalhes"
        assert error.details == details
        assert "key1=value1" in str(error)
        assert "key2=42" in str(error)
    
    def test_initialization_with_cause(self):
        """Testa inicialização com exceção causa."""
        original_error = ValueError("Erro original")
        error = AlfredoError("Erro derivado", cause=original_error)
        
        assert error.message == "Erro derivado"
        assert error.cause == original_error
    
    def test_to_dict_serialization(self):
        """Testa serialização para dicionário."""
        details = {"test_key": "test_value"}
        original_error = RuntimeError("Erro original")
        error = AlfredoError("Teste serialização", details=details, cause=original_error)
        
        result = error.to_dict()
        
        assert result["error_type"] == "AlfredoError"
        assert result["message"] == "Teste serialização"
        assert result["details"] == details
        assert result["cause"] == "Erro original"
        assert result["cause_type"] == "RuntimeError"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
    
    def test_to_dict_without_cause(self):
        """Testa serialização sem exceção causa."""
        error = AlfredoError("Teste sem causa")
        result = error.to_dict()
        
        assert result["cause"] is None
        assert result["cause_type"] is None
    
    def test_repr_representation(self):
        """Testa representação técnica da exceção."""
        details = {"key": "value"}
        cause = ValueError("causa")
        error = AlfredoError("teste", details=details, cause=cause)
        
        repr_str = repr(error)
        assert "AlfredoError" in repr_str
        assert "message='teste'" in repr_str
        assert "details={'key': 'value'}" in repr_str
        assert "cause=causa" in repr_str


class TestProviderUnavailableError:
    """Testes para ProviderUnavailableError."""
    
    def test_basic_initialization(self):
        """Testa inicialização básica."""
        error = ProviderUnavailableError("whisper", "API indisponível")
        
        assert error.provider_name == "whisper"
        assert error.reason == "API indisponível"
        assert "Provider whisper indisponível" in error.message
        assert error.details["provider_name"] == "whisper"
        assert error.details["reason"] == "API indisponível"
    
    def test_initialization_with_details(self):
        """Testa inicialização com detalhes adicionais."""
        extra_details = {"timeout": 30, "retry_count": 3}
        error = ProviderUnavailableError("groq", "Timeout", details=extra_details)
        
        assert error.details["provider_name"] == "groq"
        assert error.details["reason"] == "Timeout"
        assert error.details["timeout"] == 30
        assert error.details["retry_count"] == 3
    
    def test_to_dict_serialization(self):
        """Testa serialização específica."""
        error = ProviderUnavailableError("ollama", "Conexão recusada")
        result = error.to_dict()
        
        assert result["error_type"] == "ProviderUnavailableError"
        assert result["details"]["provider_name"] == "ollama"
        assert result["details"]["reason"] == "Conexão recusada"


class TestDownloadFailedError:
    """Testes para DownloadFailedError."""
    
    def test_basic_initialization(self):
        """Testa inicialização básica."""
        url = "https://youtube.com/watch?v=test"
        error = DownloadFailedError(url, "Vídeo não encontrado")
        
        assert error.url == url
        assert error.reason == "Vídeo não encontrado"
        assert error.http_code is None
        assert f"Falha no download de {url}" in error.message
    
    def test_initialization_with_http_code(self):
        """Testa inicialização com código HTTP."""
        url = "https://example.com/video.mp4"
        error = DownloadFailedError(url, "Not Found", http_code=404)
        
        assert error.url == url
        assert error.reason == "Not Found"
        assert error.http_code == 404
        assert error.details["http_code"] == 404
    
    def test_initialization_with_details(self):
        """Testa inicialização com detalhes extras."""
        url = "https://test.com/video"
        extra_details = {"file_size": 0, "content_type": "text/html"}
        error = DownloadFailedError(url, "Formato inválido", 
                                  http_code=200, details=extra_details)
        
        assert error.details["url"] == url
        assert error.details["reason"] == "Formato inválido"
        assert error.details["http_code"] == 200
        assert error.details["file_size"] == 0
        assert error.details["content_type"] == "text/html"


class TestTranscriptionError:
    """Testes para TranscriptionError."""
    
    def test_basic_initialization(self):
        """Testa inicialização básica."""
        audio_path = "/path/to/audio.wav"
        error = TranscriptionError(audio_path, "Arquivo corrompido")
        
        assert error.audio_path == audio_path
        assert error.reason == "Arquivo corrompido"
        assert error.provider is None
        assert f"Erro na transcrição de {audio_path}" in error.message
    
    def test_initialization_with_provider(self):
        """Testa inicialização com provedor especificado."""
        audio_path = "/tmp/test.wav"
        error = TranscriptionError(audio_path, "Timeout", provider="whisper")
        
        assert error.audio_path == audio_path
        assert error.reason == "Timeout"
        assert error.provider == "whisper"
        assert error.details["provider"] == "whisper"
    
    def test_initialization_with_details(self):
        """Testa inicialização com detalhes extras."""
        audio_path = "/audio/file.mp3"
        extra_details = {"duration": 120.5, "sample_rate": 16000}
        error = TranscriptionError(audio_path, "Formato não suportado",
                                 provider="groq", details=extra_details)
        
        assert error.details["audio_path"] == audio_path
        assert error.details["reason"] == "Formato não suportado"
        assert error.details["provider"] == "groq"
        assert error.details["duration"] == 120.5
        assert error.details["sample_rate"] == 16000


class TestInvalidVideoFormatError:
    """Testes para InvalidVideoFormatError."""
    
    def test_basic_initialization(self):
        """Testa inicialização básica."""
        error = InvalidVideoFormatError("duration", -10, "deve ser positiva")
        
        assert error.field == "duration"
        assert error.value == -10
        assert error.constraint == "deve ser positiva"
        assert "Campo duration inválido" in error.message
    
    def test_initialization_with_complex_value(self):
        """Testa inicialização com valor complexo."""
        invalid_url = "not-a-url"
        error = InvalidVideoFormatError("url", invalid_url, "deve ser URL válida")
        
        assert error.field == "url"
        assert error.value == invalid_url
        assert error.constraint == "deve ser URL válida"
        assert error.details["field"] == "url"
        assert error.details["value"] == invalid_url
    
    def test_initialization_with_details(self):
        """Testa inicialização com detalhes extras."""
        extra_details = {"min_length": 1, "max_length": 255}
        error = InvalidVideoFormatError("title", "", "não pode ser vazio",
                                      details=extra_details)
        
        assert error.details["field"] == "title"
        assert error.details["value"] == ""
        assert error.details["constraint"] == "não pode ser vazio"
        assert error.details["min_length"] == 1
        assert error.details["max_length"] == 255


class TestConfigurationError:
    """Testes para ConfigurationError."""
    
    def test_basic_initialization(self):
        """Testa inicialização básica."""
        error = ConfigurationError("api_key", "não pode ser vazia")
        
        assert error.config_key == "api_key"
        assert error.reason == "não pode ser vazia"
        assert error.expected is None
        assert "Configuração api_key inválida" in error.message
    
    def test_initialization_with_expected(self):
        """Testa inicialização com valor esperado."""
        error = ConfigurationError("timeout", "deve ser positivo", expected="> 0")
        
        assert error.config_key == "timeout"
        assert error.reason == "deve ser positivo"
        assert error.expected == "> 0"
        assert error.details["expected"] == "> 0"
    
    def test_initialization_with_details(self):
        """Testa inicialização com detalhes extras."""
        extra_details = {"current_value": -5, "valid_range": "1-3600"}
        error = ConfigurationError("max_duration", "fora do range válido",
                                 expected="1-3600", details=extra_details)
        
        assert error.details["config_key"] == "max_duration"
        assert error.details["reason"] == "fora do range válido"
        assert error.details["expected"] == "1-3600"
        assert error.details["current_value"] == -5
        assert error.details["valid_range"] == "1-3600"


class TestExceptionHierarchy:
    """Testes para verificar a hierarquia de exceções."""
    
    def test_all_exceptions_inherit_from_alfredo_error(self):
        """Verifica que todas as exceções herdam de AlfredoError."""
        exceptions = [
            ProviderUnavailableError("test", "test"),
            DownloadFailedError("test", "test"),
            TranscriptionError("test", "test"),
            InvalidVideoFormatError("test", "test", "test"),
            ConfigurationError("test", "test"),
        ]
        
        for exception in exceptions:
            assert isinstance(exception, AlfredoError)
            assert isinstance(exception, Exception)
    
    def test_exception_cause_propagation(self):
        """Testa propagação de exceção causa através da hierarquia."""
        original_error = ValueError("Erro original")
        
        # Testa com diferentes tipos de exceção
        exceptions = [
            ProviderUnavailableError("test", "test"),
            DownloadFailedError("test", "test"),
            TranscriptionError("test", "test"),
            InvalidVideoFormatError("test", "test", "test"),
            ConfigurationError("test", "test"),
        ]
        
        for exception in exceptions:
            # Simula propagação de causa
            exception.cause = original_error
            
            result = exception.to_dict()
            assert result["cause"] == "Erro original"
            assert result["cause_type"] == "ValueError"
    
    def test_details_preservation_across_hierarchy(self):
        """Verifica que detalhes são preservados em toda a hierarquia."""
        test_details = {"custom_field": "custom_value", "number": 42}
        
        exceptions = [
            ProviderUnavailableError("test", "test", details=test_details),
            DownloadFailedError("test", "test", details=test_details),
            TranscriptionError("test", "test", details=test_details),
            InvalidVideoFormatError("test", "test", "test", details=test_details),
            ConfigurationError("test", "test", details=test_details),
        ]
        
        for exception in exceptions:
            assert "custom_field" in exception.details
            assert exception.details["custom_field"] == "custom_value"
            assert exception.details["number"] == 42
            
            # Verifica serialização
            result = exception.to_dict()
            assert "custom_field" in result["details"]
            assert result["details"]["custom_field"] == "custom_value"