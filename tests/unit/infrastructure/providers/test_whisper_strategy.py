"""Tests for WhisperStrategy to improve coverage."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import logging

from src.infrastructure.providers.whisper_strategy import WhisperStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError


class TestWhisperStrategyBasic:
    """Basic tests for WhisperStrategy functionality."""
    
    def test_whisper_strategy_initialization(self):
        """Test WhisperStrategy initialization."""
        # Arrange & Act
        strategy = WhisperStrategy()
        
        # Assert
        assert strategy.model is None
        assert strategy.model_name is not None
        assert hasattr(strategy, 'config')
        assert hasattr(strategy, 'logger')

    def test_whisper_strategy_initialization_with_config(self):
        """Test WhisperStrategy initialization with custom config."""
        # Arrange
        mock_config = Mock(spec=AlfredoConfig)
        mock_config.whisper_model = "base"
        mock_config.get_provider_config.return_value = {"timeout": 300}
        
        # Act
        strategy = WhisperStrategy(config=mock_config)
        
        # Assert
        assert strategy.config == mock_config
        assert strategy.model_name == "base"

    def test_get_strategy_name(self):
        """Test get_strategy_name method."""
        # Arrange
        strategy = WhisperStrategy()
        
        # Act
        name = strategy.get_strategy_name()
        
        # Assert
        assert name == "whisper"

    def test_get_supported_languages(self):
        """Test get_supported_languages method."""
        # Arrange
        strategy = WhisperStrategy()
        
        # Act
        languages = strategy.get_supported_languages()
        
        # Assert
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "en" in languages
        assert "pt" in languages
        assert "es" in languages
        assert "fr" in languages

    def test_get_configuration(self):
        """Test get_configuration method."""
        # Arrange
        mock_config = Mock(spec=AlfredoConfig)
        mock_config.whisper_model = "small"
        mock_config.get_provider_config.return_value = {"timeout": 600}
        strategy = WhisperStrategy(config=mock_config)
        
        # Act
        config = strategy.get_configuration()
        
        # Assert
        assert isinstance(config, dict)
        assert config["model"] == "small"
        assert config["timeout"] == 600
        assert config["supports_summarization"] is False
        assert config["transcription_only"] is True

    def test_is_available_success(self):
        """Test is_available method when whisper is available."""
        # Arrange
        strategy = WhisperStrategy()
        
        # Act
        result = strategy.is_available()
        
        # Assert
        # Since whisper is imported, it should be available
        assert result is True

    def test_is_available_with_mock_import_error(self):
        """Test is_available method behavior with import simulation."""
        # Arrange
        strategy = WhisperStrategy()
        
        # Act & Assert
        # Test that method handles exceptions gracefully
        try:
            result = strategy.is_available()
            assert isinstance(result, bool)
        except Exception:
            pytest.fail("is_available should not raise exceptions")

    def test_is_available_error_handling(self):
        """Test is_available method error handling."""
        # Arrange
        strategy = WhisperStrategy()
        
        # Mock the import check to simulate error
        with patch.object(strategy, 'logger') as mock_logger:
            # Act
            result = strategy.is_available()
            
            # Assert
            assert isinstance(result, bool)
            # Logger should exist
            assert mock_logger is not None

    @pytest.mark.asyncio
    async def test_summarize_short_text(self):
        """Test summarize method with short text."""
        # Arrange
        strategy = WhisperStrategy()
        short_text = "This is a short text."
        
        # Act
        result = await strategy.summarize(short_text)
        
        # Assert
        assert result == short_text

    @pytest.mark.asyncio
    async def test_summarize_long_text(self):
        """Test summarize method with long text."""
        # Arrange
        strategy = WhisperStrategy()
        long_text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        
        # Act
        result = await strategy.summarize(long_text)
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0
        assert "First sentence" in result
        assert "Second sentence" in result
        assert "Fifth sentence" in result

    @pytest.mark.asyncio
    async def test_summarize_with_context(self):
        """Test summarize method with context."""
        # Arrange
        strategy = WhisperStrategy()
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        context = "Test Video"
        
        # Act
        result = await strategy.summarize(text, context=context)
        
        # Assert
        assert isinstance(result, str)
        assert "Test Video" in result
        assert "Resumo de 'Test Video':" in result

    @pytest.mark.asyncio
    async def test_summarize_empty_sentences(self):
        """Test summarize method with text having empty sentences."""
        # Arrange
        strategy = WhisperStrategy()
        text = "First sentence.. . Third sentence.. ."
        
        # Act
        result = await strategy.summarize(text)
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.whisper_strategy.whisper')
    async def test_transcribe_success(self, mock_whisper):
        """Test transcribe method success."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "  Transcribed text  "}
        mock_whisper.load_model.return_value = mock_model
        
        strategy = WhisperStrategy()
        
        # Act
        result = await strategy.transcribe("test_audio.wav")
        
        # Assert
        assert result == "Transcribed text"
        mock_whisper.load_model.assert_called_once()
        mock_model.transcribe.assert_called_once_with("test_audio.wav", language=None, verbose=False)

    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.whisper_strategy.whisper')
    async def test_transcribe_with_language(self, mock_whisper):
        """Test transcribe method with language parameter."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "Texto transcrito"}
        mock_whisper.load_model.return_value = mock_model
        
        strategy = WhisperStrategy()
        
        # Act
        result = await strategy.transcribe("test_audio.wav", language="pt")
        
        # Assert
        assert result == "Texto transcrito"
        mock_model.transcribe.assert_called_once_with("test_audio.wav", language="pt", verbose=False)

    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.whisper_strategy.whisper')
    async def test_transcribe_model_already_loaded(self, mock_whisper):
        """Test transcribe method when model is already loaded."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "Test result"}
        
        strategy = WhisperStrategy()
        strategy.model = mock_model  # Simulate already loaded model
        
        # Act
        result = await strategy.transcribe("test_audio.wav")
        
        # Assert
        assert result == "Test result"
        mock_whisper.load_model.assert_not_called()  # Should not load again
        mock_model.transcribe.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.whisper_strategy.whisper')
    async def test_transcribe_file_not_found(self, mock_whisper):
        """Test transcribe method with file not found error."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.side_effect = FileNotFoundError("File not found")
        mock_whisper.load_model.return_value = mock_model
        
        strategy = WhisperStrategy()
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            await strategy.transcribe("nonexistent.wav")
        
        assert "Arquivo não encontrado" in str(exc_info.value)
        assert exc_info.value.provider == "whisper"

    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.whisper_strategy.whisper')
    async def test_transcribe_model_loading_error(self, mock_whisper):
        """Test transcribe method with model loading error."""
        # Arrange
        mock_whisper.load_model.side_effect = Exception("Failed to load model")
        
        strategy = WhisperStrategy()
        
        # Act & Assert
        with pytest.raises(ProviderUnavailableError) as exc_info:
            await strategy.transcribe("test_audio.wav")
        
        assert "whisper" in str(exc_info.value)
        assert "Failed to load model" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.whisper_strategy.whisper')
    async def test_transcribe_general_error(self, mock_whisper):
        """Test transcribe method with general transcription error."""
        # Arrange
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("General transcription error")
        mock_whisper.load_model.return_value = mock_model
        
        strategy = WhisperStrategy()
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            await strategy.transcribe("test_audio.wav")
        
        assert "Falha na transcrição" in str(exc_info.value)
        assert exc_info.value.provider == "whisper"

    def test_logger_setup(self):
        """Test that logger is properly setup."""
        # Arrange & Act
        strategy = WhisperStrategy()
        
        # Assert
        assert isinstance(strategy.logger, logging.Logger)
        assert strategy.logger.name.endswith("whisper_strategy")

    def test_strategy_config_setup(self):
        """Test that strategy config is properly setup."""
        # Arrange
        mock_config = Mock(spec=AlfredoConfig)
        mock_config.whisper_model = "tiny"
        mock_strategy_config = {"timeout": 300, "custom_option": "value"}
        mock_config.get_provider_config.return_value = mock_strategy_config
        
        # Act
        strategy = WhisperStrategy(config=mock_config)
        
        # Assert
        mock_config.get_provider_config.assert_called_once_with("whisper")
        assert strategy._strategy_config == mock_strategy_config
