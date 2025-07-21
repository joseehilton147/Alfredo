"""Testes unitários para OllamaStrategy."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile
import aiohttp

from src.infrastructure.providers.ollama_strategy import OllamaStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    ProviderUnavailableError
)


@pytest.fixture
def mock_config():
    """Configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.get_provider_config.return_value = {
        "model": "llama3:8b",
        "timeout": 600
    }
    return config


@pytest.fixture
def temp_audio_file():
    """Arquivo de áudio temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(b"fake audio content")
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestOllamaStrategyInitialization:
    """Testes para inicialização do OllamaStrategy."""
    
    def test_initialization_success(self, mock_config):
        """Testa inicialização bem-sucedida."""
        strategy = OllamaStrategy(mock_config)
        
        assert strategy.config == mock_config
        assert strategy.model_name == "llama3:8b"
        assert strategy.base_url == "http://localhost:11434"
        assert strategy.timeout == 600
        assert strategy.logger is not None
    
    def test_initialization_without_config(self):
        """Testa inicialização sem configuração."""
        with patch('src.infrastructure.providers.ollama_strategy.AlfredoConfig') as mock_config_class:
            mock_config_instance = Mock()
            mock_config_instance.get_provider_config.return_value = {
                "model": "llama3:8b",
                "timeout": 600
            }
            mock_config_class.return_value = mock_config_instance
            
            strategy = OllamaStrategy()
            
            assert strategy.config == mock_config_instance
            assert strategy.model_name == "llama3:8b"
    
    def test_initialization_custom_model(self):
        """Testa inicialização com modelo customizado."""
        mock_config = Mock()
        mock_config.get_provider_config.return_value = {
            "model": "llama3:13b",
            "timeout": 1200
        }
        
        strategy = OllamaStrategy(mock_config)
        
        assert strategy.model_name == "llama3:13b"
        assert strategy.timeout == 1200


class TestOllamaStrategyTranscribe:
    """Testes para método transcribe."""
    
    def test_transcribe_not_supported(self, mock_config, temp_audio_file):
        """Testa que transcrição não é suportada pelo Ollama."""
        strategy = OllamaStrategy(mock_config)
        
        with pytest.raises(ProviderUnavailableError) as exc_info:
            asyncio.run(strategy.transcribe(temp_audio_file))
        
        assert "ollama" in str(exc_info.value)
        assert "não possui capacidade nativa de transcrição" in str(exc_info.value)
        assert "WhisperStrategy ou GroqStrategy" in str(exc_info.value)
    
    def test_transcribe_with_language(self, mock_config, temp_audio_file):
        """Testa transcrição com idioma especificado."""
        strategy = OllamaStrategy(mock_config)
        
        with pytest.raises(ProviderUnavailableError) as exc_info:
            asyncio.run(strategy.transcribe(temp_audio_file, "pt"))
        
        assert "ollama" in str(exc_info.value)
        assert temp_audio_file in str(exc_info.value.details["audio_path"])


class TestOllamaStrategySummarize:
    """Testes para método summarize."""
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_success(self, mock_post, mock_config):
        """Testa sumarização bem-sucedida."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Resumo de teste do Ollama"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act
        result = asyncio.run(strategy.summarize("Texto para resumir", "Título do Vídeo"))
        
        # Assert
        assert result == "Resumo de teste do Ollama"
        mock_post.assert_called_once()
        
        # Verificar URL da chamada
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"
        
        # Verificar payload
        payload = call_args[1]["json"]
        assert payload["model"] == "llama3:8b"
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0.3
        assert payload["options"]["num_predict"] == 500
        assert "Título do Vídeo" in payload["prompt"]
        assert "Texto para resumir" in payload["prompt"]
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_without_context(self, mock_post, mock_config):
        """Testa sumarização sem contexto."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Resumo sem contexto"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act
        result = asyncio.run(strategy.summarize("Texto para resumir"))
        
        # Assert
        assert result == "Resumo sem contexto"
        
        # Verificar que contexto não foi incluído
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "Contexto:" not in payload["prompt"]
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_http_error(self, mock_post, mock_config):
        """Testa sumarização com erro HTTP."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "Falha na sumarização" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"
    
    @patch('aiohttp.ClientSession.post', side_effect=aiohttp.ClientError("Connection failed"))
    def test_summarize_connection_error(self, mock_post, mock_config):
        """Testa sumarização com erro de conexão."""
        strategy = OllamaStrategy(mock_config)
        
        with pytest.raises(ProviderUnavailableError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "ollama" in str(exc_info.value)
        assert "Não foi possível conectar ao Ollama" in str(exc_info.value)
        assert "Verifique se o serviço está rodando" in str(exc_info.value)
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_timeout(self, mock_post, mock_config):
        """Testa sumarização com timeout."""
        # Arrange
        mock_post.side_effect = asyncio.TimeoutError()
        
        strategy = OllamaStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(ProviderUnavailableError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "ollama" in str(exc_info.value)
        assert "Timeout após 600s" in str(exc_info.value)
        assert "O modelo pode estar sendo baixado" in str(exc_info.value)
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_invalid_json(self, mock_post, mock_config):
        """Testa sumarização com JSON inválido."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "Resposta inválida do Ollama" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_empty_response(self, mock_post, mock_config):
        """Testa sumarização com resposta vazia."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": ""
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "Resposta vazia do Ollama" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_generic_error(self, mock_post, mock_config):
        """Testa sumarização com erro genérico."""
        # Arrange
        mock_post.side_effect = Exception("Generic error")
        
        strategy = OllamaStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "Falha na sumarização" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"


class TestOllamaStrategyUtilities:
    """Testes para métodos utilitários."""
    
    def test_get_supported_languages(self, mock_config):
        """Testa obtenção de idiomas suportados."""
        strategy = OllamaStrategy(mock_config)
        
        languages = strategy.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "pt" in languages
        assert "es" in languages
        assert "fr" in languages
        assert len(languages) > 10
    
    def test_get_strategy_name(self, mock_config):
        """Testa obtenção do nome da estratégia."""
        strategy = OllamaStrategy(mock_config)
        
        assert strategy.get_strategy_name() == "ollama"
    
    def test_get_configuration(self, mock_config):
        """Testa obtenção da configuração."""
        strategy = OllamaStrategy(mock_config)
        
        config = strategy.get_configuration()
        
        assert isinstance(config, dict)
        assert config["model"] == "llama3:8b"
        assert config["base_url"] == "http://localhost:11434"
        assert config["timeout"] == 600
        assert config["supports_summarization"] is True
        assert config["supports_transcription"] is False
        assert config["requires_local_service"] is True
    
    @patch('aiohttp.ClientSession.get')
    def test_is_available_success(self, mock_get, mock_config):
        """Testa verificação de disponibilidade bem-sucedida."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act
        result = strategy.is_available()
        
        # Assert
        assert result is True
    
    @patch('aiohttp.ClientSession.get')
    def test_is_available_connection_error(self, mock_get, mock_config):
        """Testa verificação de disponibilidade com erro de conexão."""
        # Arrange
        mock_get.side_effect = aiohttp.ClientError("Connection failed")
        
        strategy = OllamaStrategy(mock_config)
        
        # Act
        result = strategy.is_available()
        
        # Assert
        assert result is False
    
    @patch('aiohttp.ClientSession.get')
    def test_is_available_http_error(self, mock_get, mock_config):
        """Testa verificação de disponibilidade com erro HTTP."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        
        # Act
        result = strategy.is_available()
        
        # Assert
        assert result is False
    
    def test_is_available_generic_error(self, mock_config):
        """Testa verificação de disponibilidade com erro genérico."""
        with patch('asyncio.new_event_loop', side_effect=Exception("Generic error")):
            strategy = OllamaStrategy(mock_config)
            
            result = strategy.is_available()
            
            assert result is False


class TestOllamaStrategyConfiguration:
    """Testes para configuração personalizada."""
    
    def test_custom_base_url(self, mock_config):
        """Testa configuração com URL base customizada."""
        strategy = OllamaStrategy(mock_config)
        
        # URL base é fixa no código atual
        assert strategy.base_url == "http://localhost:11434"
    
    def test_custom_timeout(self):
        """Testa configuração com timeout customizado."""
        mock_config = Mock()
        mock_config.get_provider_config.return_value = {
            "model": "llama3:8b",
            "timeout": 1200
        }
        
        strategy = OllamaStrategy(mock_config)
        
        assert strategy.timeout == 1200
    
    def test_custom_model(self):
        """Testa configuração com modelo customizado."""
        mock_config = Mock()
        mock_config.get_provider_config.return_value = {
            "model": "codellama:7b",
            "timeout": 600
        }
        
        strategy = OllamaStrategy(mock_config)
        
        assert strategy.model_name == "codellama:7b"


class TestOllamaStrategyIntegration:
    """Testes de integração para OllamaStrategy."""
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_with_long_text(self, mock_post, mock_config):
        """Testa sumarização com texto longo."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Resumo de texto longo"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        long_text = "Este é um texto muito longo. " * 100
        
        # Act
        result = asyncio.run(strategy.summarize(long_text, "Documento Longo"))
        
        # Assert
        assert result == "Resumo de texto longo"
        
        # Verificar que o texto longo foi incluído no prompt
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert long_text in payload["prompt"]
    
    @patch('aiohttp.ClientSession.post')
    def test_summarize_with_special_characters(self, mock_post, mock_config):
        """Testa sumarização com caracteres especiais."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Resumo com acentos: ção, ã, é"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        strategy = OllamaStrategy(mock_config)
        text_with_accents = "Texto com acentuação: ção, informação, não, é, à"
        
        # Act
        result = asyncio.run(strategy.summarize(text_with_accents))
        
        # Assert
        assert result == "Resumo com acentos: ção, ã, é"
        
        # Verificar que caracteres especiais foram preservados
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert text_with_accents in payload["prompt"]
    
    @patch('aiohttp.ClientSession.post')
    def test_multiple_summarize_calls(self, mock_post, mock_config):
        """Testa múltiplas chamadas de sumarização."""
        # Arrange
        responses = [
            {"response": "Primeiro resumo"},
            {"response": "Segundo resumo"},
            {"response": "Terceiro resumo"}
        ]
        
        mock_response_objects = []
        for response_data in responses:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = response_data
            mock_response_objects.append(mock_response)
        
        mock_post.return_value.__aenter__.side_effect = mock_response_objects
        
        strategy = OllamaStrategy(mock_config)
        
        # Act
        results = []
        for i in range(3):
            result = asyncio.run(strategy.summarize(f"Texto {i+1}"))
            results.append(result)
        
        # Assert
        assert results == ["Primeiro resumo", "Segundo resumo", "Terceiro resumo"]
        assert mock_post.call_count == 3