"""
Testes para o YouTubeCommand.

Testa funcionalidades específicas do comando de processamento
de vídeos do YouTube, incluindo validação de URLs e integração
com use cases.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from src.presentation.cli.youtube_command import YouTubeCommand
from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoRequest,
    ProcessYouTubeVideoResponse
)
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


class TestYouTubeCommand:
    """Testes para o comando YouTube."""

    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        config = Mock(spec=AlfredoConfig)
        config.log_level = "INFO"
        config.log_format = "%(message)s"
        config.data_dir = Path("/test/data")
        config.temp_dir = Path("/test/temp")
        return config

    @pytest.fixture
    def mock_factory(self):
        """Mock da factory."""
        factory = Mock(spec=InfrastructureFactory)
        factory.create_video_downloader.return_value = Mock()
        factory.create_audio_extractor.return_value = Mock()
        factory.create_ai_provider.return_value = Mock()
        factory.create_storage.return_value = Mock()
        return factory

    @pytest.fixture
    def youtube_command(self, mock_config, mock_factory):
        """Instância do comando YouTube para testes."""
        return YouTubeCommand(mock_config, mock_factory)

    def test_validate_args_valid_youtube_url(self, youtube_command):
        """Testa validação com URL válida do YouTube."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            assert youtube_command.validate_args(url) is True

    @patch('builtins.print')
    def test_validate_args_empty_url(self, mock_print, youtube_command):
        """Testa validação com URL vazia."""
        result = youtube_command.validate_args("")
        assert result is False
        mock_print.assert_called()

    @patch('builtins.print')
    def test_validate_args_invalid_protocol(self, mock_print, youtube_command):
        """Testa validação com protocolo inválido."""
        result = youtube_command.validate_args("ftp://youtube.com/watch?v=test")
        assert result is False
        mock_print.assert_called()

    @patch('builtins.print')
    def test_validate_args_non_youtube_url(self, mock_print, youtube_command):
        """Testa validação com URL que não é do YouTube."""
        result = youtube_command.validate_args("https://vimeo.com/123456")
        assert result is False
        mock_print.assert_called()

    @patch('builtins.print')
    def test_validate_args_invalid_language(self, mock_print, youtube_command):
        """Testa validação com idioma inválido."""
        result = youtube_command.validate_args(
            "https://youtube.com/watch?v=test", 
            language="invalid"
        )
        assert result is False
        mock_print.assert_called()

    def test_validate_args_valid_language(self, youtube_command):
        """Testa validação com idioma válido."""
        valid_languages = ['pt', 'en', 'es', 'fr', 'de']
        
        for lang in valid_languages:
            result = youtube_command.validate_args(
                "https://youtube.com/watch?v=test",
                language=lang
            )
            assert result is True

    @pytest.mark.asyncio
    @patch('src.presentation.cli.youtube_command.tqdm')
    async def test_execute_success(self, mock_tqdm, youtube_command, mock_factory):
        """Testa execução bem-sucedida."""
        # Mock do use case
        mock_use_case = AsyncMock()
        mock_video = Video(
            id="test_id",
            title="Test Video",
            source_url="https://youtube.com/watch?v=test"
        )
        mock_response = ProcessYouTubeVideoResponse(
            video=mock_video,
            transcription="Test transcription",
            downloaded_file="/test/video.mp4"
        )
        mock_use_case.execute.return_value = mock_response
        
        # Mock da progress bar
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        with patch('src.presentation.cli.youtube_command.ProcessYouTubeVideoUseCase') as mock_use_case_class:
            mock_use_case_class.return_value = mock_use_case
            
            result = await youtube_command.execute(
                url="https://youtube.com/watch?v=test",
                language="pt"
            )
            
            assert result == mock_response
            mock_use_case.execute.assert_called_once()
            mock_progress.close.assert_called()

    @pytest.mark.asyncio
    async def test_execute_invalid_args(self, youtube_command):
        """Testa execução com argumentos inválidos."""
        with pytest.raises(InvalidVideoFormatError):
            await youtube_command.execute(url="invalid_url")

    @pytest.mark.asyncio
    @patch('src.presentation.cli.youtube_command.tqdm')
    async def test_execute_keyboard_interrupt(self, mock_tqdm, youtube_command):
        """Testa execução interrompida pelo usuário."""
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = KeyboardInterrupt()
        mock_use_case.cancel_processing = AsyncMock()
        
        with patch('src.presentation.cli.youtube_command.ProcessYouTubeVideoUseCase') as mock_use_case_class:
            mock_use_case_class.return_value = mock_use_case
            
            with pytest.raises(DownloadFailedError):
                await youtube_command.execute(
                    url="https://youtube.com/watch?v=test"
                )
            
            mock_use_case.cancel_processing.assert_called_once()
            mock_progress.close.assert_called()

    @pytest.mark.asyncio
    @patch('src.presentation.cli.youtube_command.tqdm')
    async def test_execute_download_error(self, mock_tqdm, youtube_command):
        """Testa execução com erro de download."""
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        mock_use_case = AsyncMock()
        download_error = DownloadFailedError("https://test.com", "Test error")
        mock_use_case.execute.side_effect = download_error
        
        with patch('src.presentation.cli.youtube_command.ProcessYouTubeVideoUseCase') as mock_use_case_class:
            mock_use_case_class.return_value = mock_use_case
            
            with pytest.raises(DownloadFailedError):
                await youtube_command.execute(
                    url="https://youtube.com/watch?v=test"
                )
            
            mock_progress.close.assert_called()

    @pytest.mark.asyncio
    @patch('src.presentation.cli.youtube_command.tqdm')
    async def test_execute_unexpected_error(self, mock_tqdm, youtube_command):
        """Testa execução com erro inesperado."""
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = ValueError("Unexpected error")
        
        with patch('src.presentation.cli.youtube_command.ProcessYouTubeVideoUseCase') as mock_use_case_class:
            mock_use_case_class.return_value = mock_use_case
            
            with pytest.raises(ConfigurationError):
                await youtube_command.execute(
                    url="https://youtube.com/watch?v=test"
                )
            
            mock_progress.close.assert_called()

    def test_update_progress(self, youtube_command):
        """Testa atualização de progresso."""
        mock_progress = Mock()
        youtube_command._progress_bar = mock_progress
        
        youtube_command._update_progress(50, "Test message")
        
        assert mock_progress.n == 50
        mock_progress.set_description.assert_called_with("🎬 Test message")
        mock_progress.refresh.assert_called_once()

    def test_update_progress_no_bar(self, youtube_command):
        """Testa atualização de progresso sem barra."""
        youtube_command._progress_bar = None
        
        # Não deve gerar erro
        youtube_command._update_progress(50, "Test message")

    @patch('builtins.print')
    def test_display_youtube_result(self, mock_print, youtube_command):
        """Testa exibição de resultado do YouTube."""
        mock_video = Video(
            id="test_id",
            title="Test Video",
            source_url="https://youtube.com/watch?v=test",
            duration=120,
            metadata={
                'uploader': 'Test Channel',
                'view_count': 1000
            }
        )
        mock_response = ProcessYouTubeVideoResponse(
            video=mock_video,
            transcription="Test transcription",
            downloaded_file="/test/video.mp4"
        )
        
        youtube_command._display_youtube_result(mock_response)
        
        # Verificar se print foi chamado múltiplas vezes
        assert mock_print.call_count >= 5

    def test_get_command_info(self, youtube_command):
        """Testa obtenção de informações do comando."""
        info = youtube_command.get_command_info()
        
        assert info['name'] == 'youtube'
        assert 'description' in info
        assert 'usage' in info
        assert 'examples' in info
        assert isinstance(info['examples'], list)
        assert len(info['examples']) > 0