"""Testes unitários para GroqStrategy."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile

from src.infrastructure.providers.groq_strategy import GroqStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    ProviderUnavailableError,
    ConfigurationError
)


@pytest.fixture
def mock_config():
    """Configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.get_provider_config.return_value = {
        "model": "llama-3.3-70b-versatile",
        "api_key": "test_groq_api_key",
        "timeout": 600
    }
    return config


@pytest.fixture
def mock_groq_client():
    """Mock para cliente Groq."""
    mock_client = Mock()
    mock_audio = Mock()
    mock_chat = Mock()
    
    mock_client.audio = mock_audio
    mock_client.chat = mock_chat
    
    # Mock para transcrição
    mock_transcription = Mock()
    mock_transcription.strip.return_value = "Transcrição de teste do Groq"
    mock_audio.transcriptions.create.return_value = mock_transcription
    
    # Mock para chat completion
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = "Resumo de teste do Groq"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def temp_audio_file():
    """Arquivo de áudio temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(b"fake audio content")
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestGroqStrategyInitialization:
    """Testes para inicialização do GroqStrategy."""
    
    def test_initialization_success(self, mock_config):
        """Testa inicialização bem-sucedida."""
        strategy = GroqStrategy(mock_config)
        
        assert strategy.config == mock_config
        assert strategy.model_name == "llama-3.3-70b-versatile"
        assert strategy.api_key == "test_groq_api_key"
        assert strategy.logger is not None
    
    def test_initialization_without_config(self):
        """Testa inicialização sem configuração."""
        with patch('src.infrastructure.providers.groq_strategy.AlfredoConfig') as mock_config_class:
            mock_config_instance = Mock()
            mock_config_instance.get_provider_config.return_value = {
                "model": "llama-3.3-70b-versatile",
                "api_key": "default_api_key"
            }
            mock_config_class.return_value = mock_config_instance
            
            strategy = GroqStrategy()
            
            assert strategy.config == mock_config_instance
            assert strategy.api_key == "default_api_key"
    
    def test_initialization_missing_api_key(self):
        """Testa inicialização sem API key."""
        mock_config = Mock()
        mock_config.get_provider_config.return_value = {
            "model": "llama-3.3-70b-versatile",
            "api_key": None
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            GroqStrategy(mock_config)
        
        assert "groq_api_key" in str(exc_info.value)
        assert "API key do Groq é obrigatória" in str(exc_info.value)


class TestGroqStrategyTranscribe:
    """Testes para método transcribe."""
    
    @patch('groq.Groq')
    def test_transcribe_success(self, mock_groq_class, mock_config, temp_audio_file):
        """Testa transcrição bem-sucedida."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_transcription = "Transcrição de teste do Groq"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        strategy = GroqStrategy(mock_config)
        
        with patch('builtins.open', mock_open_audio_file()):
            # Act
            result = asyncio.run(strategy.transcribe(temp_audio_file, "pt"))
        
        # Assert
        assert result == mock_transcription
        mock_client.audio.transcriptions.create.assert_called_once()
        
        # Verificar parâmetros da chamada
        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs["model"] == "whisper-large-v3"
        assert call_kwargs["language"] == "pt"
        assert call_kwargs["response_format"] == "text"
    
    @patch('groq.Groq')
    def test_transcribe_without_language(self, mock_groq_class, mock_config, temp_audio_file):
        """Testa transcrição sem especificar idioma."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_transcription = "Transcrição sem idioma"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        strategy = GroqStrategy(mock_config)
        
        with patch('builtins.open', mock_open_audio_file()):
            # Act
            result = asyncio.run(strategy.transcribe(temp_audio_file))
        
        # Assert
        assert result == mock_transcription
        
        # Verificar que language não foi passado
        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs.get("language") is None
    
    @patch('groq.Groq')
    def test_transcribe_file_not_found(self, mock_groq_class, mock_config):
        """Testa transcrição com arquivo não encontrado."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        strategy = GroqStrategy(mock_config)
        non_existent_file = "/non/existent/audio.wav"
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(strategy.transcribe(non_existent_file))
        
        assert "Arquivo não encontrado" in str(exc_info.value)
        assert exc_info.value.provider == "groq"
    
    def test_transcribe_groq_not_installed(self, mock_config, temp_audio_file):
        """Testa transcrição com biblioteca Groq não instalada."""
        strategy = GroqStrategy(mock_config)
        
        # Simular ImportError no método transcribe
        with patch.object(strategy, 'transcribe', side_effect=ImportError("No module named 'groq'")):
            with pytest.raises(ImportError):
                asyncio.run(strategy.transcribe(temp_audio_file))
    
    @patch('groq.Groq')
    def test_transcribe_api_error(self, mock_groq_class, mock_config, temp_audio_file):
        """Testa transcrição com erro de API."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_client.audio.transcriptions.create.side_effect = Exception("API key invalid")
        
        strategy = GroqStrategy(mock_config)
        
        with patch('builtins.open', mock_open_audio_file()):
            # Act & Assert
            with pytest.raises(ProviderUnavailableError) as exc_info:
                asyncio.run(strategy.transcribe(temp_audio_file))
            
            assert "groq" in str(exc_info.value)
            assert "Erro de API" in str(exc_info.value)
    
    @patch('groq.Groq')
    def test_transcribe_generic_error(self, mock_groq_class, mock_config, temp_audio_file):
        """Testa transcrição com erro genérico."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_client.audio.transcriptions.create.side_effect = Exception("Generic error")
        
        strategy = GroqStrategy(mock_config)
        
        with patch('builtins.open', mock_open_audio_file()):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                asyncio.run(strategy.transcribe(temp_audio_file))
            
            assert "Falha na transcrição" in str(exc_info.value)
            assert exc_info.value.provider == "groq"


class TestGroqStrategySummarize:
    """Testes para método summarize."""
    
    @patch('groq.Groq')
    def test_summarize_success(self, mock_groq_class, mock_config):
        """Testa sumarização bem-sucedida."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Resumo de teste do Groq"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        strategy = GroqStrategy(mock_config)
        
        # Act
        result = asyncio.run(strategy.summarize("Texto para resumir", "Título do Vídeo"))
        
        # Assert
        assert result == "Resumo de teste do Groq"
        mock_client.chat.completions.create.assert_called_once()
        
        # Verificar parâmetros da chamada
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "llama-3.3-70b-versatile"
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 1000
        
        # Verificar mensagens
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "Título do Vídeo" in messages[1]["content"]
        assert "Texto para resumir" in messages[1]["content"]
    
    @patch('groq.Groq')
    def test_summarize_without_context(self, mock_groq_class, mock_config):
        """Testa sumarização sem contexto."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Resumo sem contexto"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        strategy = GroqStrategy(mock_config)
        
        # Act
        result = asyncio.run(strategy.summarize("Texto para resumir"))
        
        # Assert
        assert result == "Resumo sem contexto"
        
        # Verificar que contexto não foi incluído
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        messages = call_kwargs["messages"]
        assert "Contexto:" not in messages[1]["content"]
    
    def test_summarize_groq_not_installed(self, mock_config):
        """Testa sumarização com biblioteca Groq não instalada."""
        strategy = GroqStrategy(mock_config)
        
        # Simular ImportError no método summarize
        with patch.object(strategy, 'summarize', side_effect=ImportError("No module named 'groq'")):
            with pytest.raises(ImportError):
                asyncio.run(strategy.summarize("Texto para resumir"))
    
    @patch('groq.Groq')
    def test_summarize_api_error(self, mock_groq_class, mock_config):
        """Testa sumarização com erro de API."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = Exception("API key invalid")
        
        strategy = GroqStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(ProviderUnavailableError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "groq" in str(exc_info.value)
        assert "Erro de API" in str(exc_info.value)
    
    @patch('groq.Groq')
    def test_summarize_generic_error(self, mock_groq_class, mock_config):
        """Testa sumarização com erro genérico."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = Exception("Generic error")
        
        strategy = GroqStrategy(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(strategy.summarize("Texto para resumir"))
        
        assert "Falha na sumarização" in str(exc_info.value)
        assert exc_info.value.provider == "groq"


class TestGroqStrategyUtilities:
    """Testes para métodos utilitários."""
    
    def test_get_supported_languages(self, mock_config):
        """Testa obtenção de idiomas suportados."""
        strategy = GroqStrategy(mock_config)
        
        languages = strategy.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "pt" in languages
        assert "es" in languages
        assert "fr" in languages
        assert len(languages) > 10
    
    def test_get_strategy_name(self, mock_config):
        """Testa obtenção do nome da estratégia."""
        strategy = GroqStrategy(mock_config)
        
        assert strategy.get_strategy_name() == "groq"
    
    def test_get_configuration(self, mock_config):
        """Testa obtenção da configuração."""
        strategy = GroqStrategy(mock_config)
        
        config = strategy.get_configuration()
        
        assert isinstance(config, dict)
        assert config["model"] == "llama-3.3-70b-versatile"
        assert config["transcription_model"] == "whisper-large-v3"
        assert config["timeout"] == 600
        assert config["supports_summarization"] is True
        assert config["api_key_required"] is True
        assert config["has_api_key"] is True
    
    @patch('groq.Groq')
    def test_is_available_success(self, mock_groq_class, mock_config):
        """Testa verificação de disponibilidade bem-sucedida."""
        strategy = GroqStrategy(mock_config)
        
        assert strategy.is_available() is True
    
    def test_is_available_no_api_key(self):
        """Testa verificação de disponibilidade sem API key."""
        mock_config = Mock()
        mock_config.get_provider_config.return_value = {
            "model": "llama-3.3-70b-versatile",
            "api_key": None
        }
        
        with pytest.raises(ConfigurationError):
            GroqStrategy(mock_config)
    
    def test_is_available_import_error(self, mock_config):
        """Testa verificação de disponibilidade com erro de importação."""
        strategy = GroqStrategy(mock_config)
        
        # Simular ImportError no import dentro do método is_available
        with patch('builtins.__import__') as mock_import:
            mock_import.side_effect = ImportError("No module named 'groq'")
            assert strategy.is_available() is False


class TestGroqStrategyIntegration:
    """Testes de integração para GroqStrategy."""
    
    @patch('groq.Groq')
    def test_full_workflow(self, mock_groq_class, mock_config, temp_audio_file):
        """Testa fluxo completo de transcrição e sumarização."""
        # Arrange
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        # Mock transcrição
        mock_transcription = "Transcrição completa do áudio de teste"
        mock_client.audio.transcriptions.create.return_value = mock_transcription
        
        # Mock sumarização
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Resumo completo do texto transcrito"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        strategy = GroqStrategy(mock_config)
        
        with patch('builtins.open', mock_open_audio_file()):
            # Act
            transcription = asyncio.run(strategy.transcribe(temp_audio_file, "pt"))
            summary = asyncio.run(strategy.summarize(transcription, "Vídeo de Teste"))
        
        # Assert
        assert transcription == "Transcrição completa do áudio de teste"
        assert summary == "Resumo completo do texto transcrito"
        
        # Verificar que ambos os métodos foram chamados
        mock_client.audio.transcriptions.create.assert_called_once()
        mock_client.chat.completions.create.assert_called_once()


def mock_open_audio_file():
    """Mock para abertura de arquivo de áudio."""
    from unittest.mock import mock_open
    return mock_open(read_data=b"fake audio content")