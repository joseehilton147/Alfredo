"""Testes unitários para WhisperProvider."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile

from src.infrastructure.providers.whisper_provider import WhisperProvider
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    ProviderUnavailableError
)


@pytest.fixture
def mock_config():
    """Configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.whisper_model = "base"
    return config


@pytest.fixture
def mock_whisper_model():
    """Mock para modelo Whisper."""
    mock_model = Mock()
    mock_model.transcribe.return_value = {
        "text": "Transcrição de teste do Whisper",
        "language": "pt",
        "segments": [
            {"start": 0.0, "end": 5.0, "text": "Primeira parte"},
            {"start": 5.0, "end": 10.0, "text": "Segunda parte"}
        ]
    }
    return mock_model


@pytest.fixture
def temp_audio_file():
    """Arquivo de áudio temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(b"fake audio content")
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestWhisperProviderInitialization:
    """Testes para inicialização do WhisperProvider."""
    
    def test_initialization_success(self, mock_config):
        """Testa inicialização bem-sucedida."""
        provider = WhisperProvider(mock_config)
        
        assert provider.config == mock_config
        assert provider.model_name == "base"
        assert provider.model is None  # Modelo carregado sob demanda
        assert provider.logger is not None
    
    def test_initialization_without_config(self):
        """Testa inicialização sem configuração."""
        with patch('src.infrastructure.providers.whisper_provider.AlfredoConfig') as mock_config_class:
            mock_config_instance = Mock()
            mock_config_instance.whisper_model = "small"
            mock_config_class.return_value = mock_config_instance
            
            provider = WhisperProvider()
            
            assert provider.config == mock_config_instance
            assert provider.model_name == "small"
    
    def test_initialization_custom_model(self):
        """Testa inicialização com modelo customizado."""
        mock_config = Mock()
        mock_config.whisper_model = "large"
        
        provider = WhisperProvider(mock_config)
        
        assert provider.model_name == "large"


class TestWhisperProviderTranscribe:
    """Testes para método transcribe_audio."""
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_success(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa transcrição bem-sucedida."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Transcrição de teste do Whisper"
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act
        result = asyncio.run(provider.transcribe_audio(temp_audio_file, "pt"))
        
        # Assert
        assert result == "Transcrição de teste do Whisper"
        mock_whisper_module.load_model.assert_called_once_with("base")
        mock_model.transcribe.assert_called_once_with(temp_audio_file, language="pt", verbose=False)
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_without_language(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa transcrição sem especificar idioma."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Transcrição sem idioma especificado"
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act
        result = asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        # Assert
        assert result == "Transcrição sem idioma especificado"
        
        # Verificar que language=None foi passado
        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert call_kwargs.get("language") is None
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_model_reuse(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa reutilização do modelo carregado."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Transcrição reutilizando modelo"
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act - Primeira transcrição
        result1 = asyncio.run(provider.transcribe_audio(temp_audio_file, "pt"))
        
        # Act - Segunda transcrição
        result2 = asyncio.run(provider.transcribe_audio(temp_audio_file, "en"))
        
        # Assert
        assert result1 == "Transcrição reutilizando modelo"
        assert result2 == "Transcrição reutilizando modelo"
        
        # Modelo deve ser carregado apenas uma vez
        mock_whisper_module.load_model.assert_called_once_with("base")
        
        # Transcrição deve ser chamada duas vezes
        assert mock_model.transcribe.call_count == 2
    
    def test_transcribe_audio_file_not_found(self, mock_config):
        """Testa transcrição com arquivo não encontrado."""
        provider = WhisperProvider(mock_config)
        non_existent_file = "/non/existent/audio.wav"
        
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(provider.transcribe_audio(non_existent_file))
        
        assert "Arquivo não encontrado" in str(exc_info.value)
        assert exc_info.value.provider == "whisper"
        assert exc_info.value.details["model"] == "base"
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_model_loading_error(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa transcrição com erro no carregamento do modelo."""
        # Arrange
        mock_whisper_module.load_model.side_effect = Exception("Model loading failed")
        
        provider = WhisperProvider(mock_config)
        
        # Act & Assert
        with pytest.raises(ProviderUnavailableError) as exc_info:
            asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        assert "whisper" in str(exc_info.value)
        assert "Erro ao carregar modelo base" in str(exc_info.value)
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_transcription_error(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa transcrição com erro na transcrição."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        assert "Falha na transcrição" in str(exc_info.value)
        assert exc_info.value.provider == "whisper"
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_empty_result(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa transcrição com resultado vazio."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "   "  # Texto apenas com espaços
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act
        result = asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        # Assert
        assert result == ""  # Deve retornar string vazia após strip()
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_transcribe_audio_with_segments(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa transcrição com segmentos detalhados."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Transcrição completa com segmentos",
            "language": "pt",
            "segments": [
                {
                    "start": 0.0,
                    "end": 3.0,
                    "text": "Transcrição completa"
                },
                {
                    "start": 3.0,
                    "end": 6.0,
                    "text": "com segmentos"
                }
            ]
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act
        result = asyncio.run(provider.transcribe_audio(temp_audio_file, "pt"))
        
        # Assert
        assert result == "Transcrição completa com segmentos"
        
        # Verificar que verbose=False foi usado (não queremos logs detalhados)
        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert call_kwargs["verbose"] is False


class TestWhisperProviderUtilities:
    """Testes para métodos utilitários."""
    
    def test_get_supported_languages(self, mock_config):
        """Testa obtenção de idiomas suportados."""
        provider = WhisperProvider(mock_config)
        
        languages = provider.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "pt" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "de" in languages
        assert "it" in languages
        assert "ja" in languages
        assert "ko" in languages
        assert "zh" in languages
        assert "ru" in languages
        assert "ar" in languages
        assert "hi" in languages
        assert "tr" in languages
        assert "pl" in languages
        assert "nl" in languages
        assert "sv" in languages
        assert "no" in languages
        assert "da" in languages
        assert "fi" in languages
        
        # Verificar que tem pelo menos os idiomas esperados
        assert len(languages) >= 19


class TestWhisperProviderDifferentModels:
    """Testes para diferentes modelos Whisper."""
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_different_model_sizes(self, mock_whisper_module, temp_audio_file):
        """Testa diferentes tamanhos de modelo."""
        models_to_test = ["tiny", "base", "small", "medium", "large"]
        
        for model_name in models_to_test:
            # Arrange
            mock_config = Mock()
            mock_config.whisper_model = model_name
            
            mock_model = Mock()
            mock_model.transcribe.return_value = {
                "text": f"Transcrição com modelo {model_name}"
            }
            mock_whisper_module.load_model.return_value = mock_model
            
            provider = WhisperProvider(mock_config)
            
            # Act
            result = asyncio.run(provider.transcribe_audio(temp_audio_file))
            
            # Assert
            assert result == f"Transcrição com modelo {model_name}"
            mock_whisper_module.load_model.assert_called_with(model_name)
            
            # Reset mock para próxima iteração
            mock_whisper_module.reset_mock()
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_model_loading_performance(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa que modelo é carregado apenas uma vez para múltiplas transcrições."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Transcrição de performance"
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act - Múltiplas transcrições
        for i in range(5):
            result = asyncio.run(provider.transcribe_audio(temp_audio_file))
            assert result == "Transcrição de performance"
        
        # Assert - Modelo carregado apenas uma vez
        mock_whisper_module.load_model.assert_called_once_with("base")
        
        # Transcrição chamada 5 vezes
        assert mock_model.transcribe.call_count == 5


class TestWhisperProviderErrorHandling:
    """Testes para tratamento de erros específicos."""
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_memory_error_handling(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa tratamento de erro de memória."""
        # Arrange
        mock_whisper_module.load_model.side_effect = MemoryError("Not enough memory")
        
        provider = WhisperProvider(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        assert "Falha na transcrição" in str(exc_info.value)
        assert exc_info.value.provider == "whisper"
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_cuda_error_handling(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa tratamento de erro CUDA."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.side_effect = RuntimeError("CUDA out of memory")
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        assert "Falha na transcrição" in str(exc_info.value)
        assert "CUDA out of memory" in str(exc_info.value)
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_audio_format_error(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa tratamento de erro de formato de áudio."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Unsupported audio format")
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(provider.transcribe_audio(temp_audio_file))
        
        assert "Falha na transcrição" in str(exc_info.value)
        assert "Unsupported audio format" in str(exc_info.value)


class TestWhisperProviderIntegration:
    """Testes de integração para WhisperProvider."""
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_full_transcription_workflow(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa fluxo completo de transcrição."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Esta é uma transcrição completa de teste para verificar o fluxo completo do Whisper provider.",
            "language": "pt",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "Esta é uma transcrição"},
                {"start": 2.0, "end": 4.0, "text": "completa de teste"},
                {"start": 4.0, "end": 6.0, "text": "para verificar o fluxo"},
                {"start": 6.0, "end": 8.0, "text": "completo do Whisper provider."}
            ]
        }
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act
        result = asyncio.run(provider.transcribe_audio(temp_audio_file, "pt"))
        
        # Assert
        expected_text = "Esta é uma transcrição completa de teste para verificar o fluxo completo do Whisper provider."
        assert result == expected_text
        
        # Verificar que modelo foi carregado corretamente
        mock_whisper_module.load_model.assert_called_once_with("base")
        
        # Verificar parâmetros da transcrição
        call_args = mock_model.transcribe.call_args
        assert call_args[0][0] == temp_audio_file
        assert call_args[1]["language"] == "pt"
        assert call_args[1]["verbose"] is False
    
    @patch('src.infrastructure.providers.whisper_provider.whisper')
    def test_multiple_languages_workflow(self, mock_whisper_module, mock_config, temp_audio_file):
        """Testa fluxo com múltiplos idiomas."""
        # Arrange
        mock_model = Mock()
        
        # Diferentes respostas para diferentes idiomas
        def transcribe_side_effect(audio_path, language=None, verbose=False):
            language_responses = {
                "pt": {"text": "Transcrição em português"},
                "en": {"text": "Transcription in English"},
                "es": {"text": "Transcripción en español"},
                None: {"text": "Auto-detected transcription"}
            }
            return language_responses.get(language, {"text": "Unknown language"})
        
        mock_model.transcribe.side_effect = transcribe_side_effect
        mock_whisper_module.load_model.return_value = mock_model
        
        provider = WhisperProvider(mock_config)
        
        # Act & Assert
        languages_to_test = ["pt", "en", "es", None]
        expected_results = [
            "Transcrição em português",
            "Transcription in English", 
            "Transcripción en español",
            "Auto-detected transcription"
        ]
        
        for language, expected in zip(languages_to_test, expected_results):
            result = asyncio.run(provider.transcribe_audio(temp_audio_file, language))
            assert result == expected
        
        # Verificar que modelo foi carregado apenas uma vez
        mock_whisper_module.load_model.assert_called_once_with("base")
        
        # Verificar que transcrição foi chamada para cada idioma
        assert mock_model.transcribe.call_count == 4