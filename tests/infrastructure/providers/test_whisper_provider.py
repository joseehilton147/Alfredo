"""Testes para WhisperProvider."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.providers.whisper_provider import WhisperProvider
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError


class TestWhisperProvider:
    """Testes para o provedor Whisper."""

    def test_init_default_model(self):
        """Testa inicialização com modelo padrão."""
        provider = WhisperProvider()
        assert provider.model_name == "base"
        assert provider.model is None

    def test_init_custom_model(self):
        """Testa inicialização com modelo customizado."""
        from src.config.alfredo_config import AlfredoConfig
        config = AlfredoConfig()
        config.whisper_model = "large"
        provider = WhisperProvider(config)
        assert provider.model_name == "large"
        assert provider.model is None

    @pytest.mark.asyncio
    async def test_transcribe_audio_success_first_time(self):
        """Testa transcrição de áudio com sucesso na primeira vez."""
        from src.config.alfredo_config import AlfredoConfig
        config = AlfredoConfig()
        config.whisper_model = "small"
        provider = WhisperProvider(config)

        with patch('whisper.load_model') as mock_load_model:
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {"text": "  Hello world  "}
            mock_load_model.return_value = mock_model

            result = await provider.transcribe_audio("/path/to/audio.wav", "en")

            assert result == "Hello world"
            mock_load_model.assert_called_once_with("small")
            mock_model.transcribe.assert_called_once_with(
                "/path/to/audio.wav",
                language="en",
                verbose=False
            )

    @pytest.mark.asyncio
    async def test_transcribe_audio_success_model_already_loaded(self):
        """Testa transcrição com modelo já carregado."""
        provider = WhisperProvider()

        # Simular modelo já carregado
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Test transcription"}
        provider.model = mock_model

        result = await provider.transcribe_audio("/path/to/audio.wav")

        assert result == "Test transcription"
        mock_model.transcribe.assert_called_once_with(
            "/path/to/audio.wav",
            language=None,
            verbose=False
        )

    @pytest.mark.asyncio
    async def test_transcribe_audio_error(self):
        """Testa erro na transcrição."""
        provider = WhisperProvider()

        with patch('whisper.load_model') as mock_load_model:
            mock_model = MagicMock()
            mock_model.transcribe.side_effect = Exception("Transcription error")
            mock_load_model.return_value = mock_model

            with pytest.raises(TranscriptionError) as exc_info:
                await provider.transcribe_audio("/path/to/audio.wav")

            assert "Falha na transcrição" in str(exc_info.value)
            assert "Transcription error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_audio_load_model_error(self):
        """Testa erro ao carregar modelo."""
        provider = WhisperProvider()

        with patch('whisper.load_model') as mock_load_model:
            mock_load_model.side_effect = Exception("Model load error")

            with pytest.raises(ProviderUnavailableError) as exc_info:
                await provider.transcribe_audio("/path/to/audio.wav")

            assert "Erro ao carregar modelo" in str(exc_info.value)
            assert "Model load error" in str(exc_info.value)

    def test_get_supported_languages(self):
        """Testa obtenção de idiomas suportados."""
        provider = WhisperProvider()
        languages = provider.get_supported_languages()

        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "pt" in languages
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "de" in languages
