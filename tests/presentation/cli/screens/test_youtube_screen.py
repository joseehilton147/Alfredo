"""Tests for YouTubeScreen."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoResponse
from src.domain.entities.video import Video
from src.presentation.cli.screens.youtube_screen import YouTubeScreen


class TestYouTubeScreen:
    """Test cases for YouTubeScreen."""

    @pytest.fixture
    def mock_cli(self):
        """Mock CLI controller."""
        cli = MagicMock()
        cli.app_context = MagicMock()
        cli.app_context.video_repository = AsyncMock()
        cli.app_context.whisper_provider = AsyncMock()
        cli.app_context.get_setting = MagicMock(return_value="pt")
        cli.go_back = AsyncMock()
        cli.navigate_to = AsyncMock()
        return cli

    @pytest.fixture
    def youtube_screen(self, mock_cli):
        """Create YouTube screen instance."""
        return YouTubeScreen(mock_cli)

    @pytest.mark.asyncio
    async def test_initial_state(self, youtube_screen):
        """Test initial screen state."""
        assert youtube_screen.current_step == "input"
        assert youtube_screen.video_info is None
        assert youtube_screen.processing_progress is None
        assert youtube_screen.error_message == ""
        assert youtube_screen.success_message == ""
        assert youtube_screen.current_use_case is None

    @pytest.mark.asyncio
    async def test_handle_input_escape_in_input_step(self, youtube_screen, mock_cli):
        """Test ESC key handling in input step."""
        youtube_screen.current_step = "input"

        await youtube_screen.handle_input("escape")

        mock_cli.go_back.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_input_valid_url(self, youtube_screen):
        """Test handling valid URL input."""
        youtube_screen.current_step = "input"
        youtube_screen.url_input.is_valid = True

        with patch.object(youtube_screen, "_load_video_info") as mock_load:
            with patch.object(
                youtube_screen.url_input,
                "handle_key",
                return_value="https://youtube.com/watch?v=test123",
            ):
                await youtube_screen.handle_input("enter")

                mock_load.assert_called_once_with("https://youtube.com/watch?v=test123")

    @pytest.mark.asyncio
    async def test_load_video_info_success(self, youtube_screen):
        """Test successful video info loading."""
        with patch.object(youtube_screen, "_fetch_video_info") as mock_fetch:
            mock_fetch.return_value = None  # Successful fetch

            await youtube_screen._load_video_info("https://youtube.com/watch?v=test123")

            assert youtube_screen.current_step == "preview"
            assert youtube_screen.error_message == ""
            mock_fetch.assert_called_once_with("https://youtube.com/watch?v=test123")

    @pytest.mark.asyncio
    async def test_load_video_info_invalid_url(self, youtube_screen):
        """Test loading info for invalid URL."""
        with patch(
            "src.presentation.cli.components.input_field.YouTubeURLValidator.extract_video_id",
            return_value=None,
        ):
            await youtube_screen._load_video_info("invalid_url")

            assert youtube_screen.current_step == "input"
            assert (
                "Não foi possível extrair ID do vídeo" in youtube_screen.error_message
            )

    @pytest.mark.asyncio
    async def test_fetch_video_info_with_yt_dlp(self, youtube_screen):
        """Test fetching video info with yt-dlp available."""
        with patch("src.presentation.cli.screens.youtube_screen.yt_dlp") as mock_yt_dlp:
            # Mock yt-dlp
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 120,
                "height": 720,
                "id": "test123",
            }
            mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl

            await youtube_screen._fetch_video_info(
                "https://youtube.com/watch?v=test123"
            )

            assert youtube_screen.video_info["title"] == "Test Video"
            assert youtube_screen.video_info["uploader"] == "Test Channel"
            assert youtube_screen.video_info["duration"] == 120
            assert youtube_screen.video_info["height"] == 720
            assert youtube_screen.video_info["id"] == "test123"

    @pytest.mark.asyncio
    async def test_fetch_video_info_without_yt_dlp(self, youtube_screen):
        """Test fetching video info without yt-dlp."""
        with patch(
            "src.presentation.cli.screens.youtube_screen.yt_dlp",
            side_effect=ImportError,
        ):
            with patch(
                "src.presentation.cli.components.input_field.YouTubeURLValidator.extract_video_id",
                return_value="test123",
            ):
                await youtube_screen._fetch_video_info(
                    "https://youtube.com/watch?v=test123"
                )

                assert "test123" in youtube_screen.video_info["title"]
                assert "yt-dlp não instalado" in youtube_screen.video_info["uploader"]
                assert youtube_screen.video_info["duration"] == 0
                assert youtube_screen.video_info["id"] == "test123"

    @pytest.mark.asyncio
    async def test_handle_preview_step_enter(self, youtube_screen):
        """Test Enter key in preview step."""
        youtube_screen.current_step = "preview"
        youtube_screen.video_info = {
            "url": "https://youtube.com/watch?v=test123",
            "title": "Test",
        }

        with patch.object(youtube_screen, "_start_processing") as mock_start:
            await youtube_screen.handle_input("enter")

            mock_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_preview_step_escape(self, youtube_screen):
        """Test ESC key in preview step."""
        youtube_screen.current_step = "preview"

        with patch.object(youtube_screen, "render") as mock_render:
            await youtube_screen.handle_input("escape")

            assert youtube_screen.current_step == "input"
            assert youtube_screen.error_message == ""
            mock_render.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_preview_step_quit(self, youtube_screen, mock_cli):
        """Test Q key in preview step."""
        youtube_screen.current_step = "preview"

        await youtube_screen.handle_input("q")

        mock_cli.go_back.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_processing_success(self, youtube_screen, mock_cli):
        """Test successful video processing."""
        youtube_screen.video_info = {
            "url": "https://youtube.com/watch?v=test123",
            "title": "Test Video",
        }

        # Mock successful response
        mock_video = Video(
            id="youtube_test123", title="Test Video", file_path="/path/to/video.mp4"
        )
        mock_response = ProcessYouTubeVideoResponse(
            video=mock_video,
            transcription="Test transcription",
            downloaded_file="/path/to/video.mp4",
        )

        with patch(
            "src.presentation.cli.screens.youtube_screen.ProcessYouTubeVideoUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_response
            mock_use_case_class.return_value = mock_use_case

            with patch.object(youtube_screen, "render") as mock_render:
                await youtube_screen._start_processing()

                assert youtube_screen.current_step == "complete"
                assert "processado com sucesso" in youtube_screen.success_message
                assert youtube_screen.current_use_case == mock_use_case

    @pytest.mark.asyncio
    async def test_start_processing_import_error(self, youtube_screen, mock_cli):
        """Test processing with missing yt-dlp dependency."""
        youtube_screen.video_info = {
            "url": "https://youtube.com/watch?v=test123",
            "title": "Test Video",
        }

        with patch(
            "src.presentation.cli.screens.youtube_screen.ProcessYouTubeVideoUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ImportError("yt-dlp não está instalado")
            mock_use_case_class.return_value = mock_use_case

            with patch.object(youtube_screen, "render") as mock_render:
                await youtube_screen._start_processing()

                assert youtube_screen.current_step == "complete"
                assert "Dependência não encontrada" in youtube_screen.error_message

    @pytest.mark.asyncio
    async def test_start_processing_general_error(self, youtube_screen, mock_cli):
        """Test processing with general error."""
        youtube_screen.video_info = {
            "url": "https://youtube.com/watch?v=test123",
            "title": "Test Video",
        }

        with patch(
            "src.presentation.cli.screens.youtube_screen.ProcessYouTubeVideoUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = Exception("Processing failed")
            mock_use_case_class.return_value = mock_use_case

            with patch.object(youtube_screen, "render") as mock_render:
                await youtube_screen._start_processing()

                assert youtube_screen.current_step == "complete"
                assert "Erro durante o processamento" in youtube_screen.error_message

    @pytest.mark.asyncio
    async def test_handle_processing_step_escape(self, youtube_screen):
        """Test ESC key during processing (cancellation)."""
        youtube_screen.current_step = "processing"
        youtube_screen.current_use_case = AsyncMock()

        with patch.object(youtube_screen, "render") as mock_render:
            await youtube_screen.handle_input("escape")

            youtube_screen.current_use_case.cancel_processing.assert_called_once()
            assert youtube_screen.current_step == "complete"
            assert "cancelado pelo usuário" in youtube_screen.error_message

    @pytest.mark.asyncio
    async def test_handle_complete_step_enter(self, youtube_screen):
        """Test Enter key in complete step (process another video)."""
        youtube_screen.current_step = "complete"
        youtube_screen.success_message = "Previous success"

        with patch.object(youtube_screen, "render") as mock_render:
            await youtube_screen.handle_input("enter")

            assert youtube_screen.current_step == "input"
            assert youtube_screen.success_message == ""
            assert youtube_screen.video_info is None

    @pytest.mark.asyncio
    async def test_handle_complete_step_escape(self, youtube_screen, mock_cli):
        """Test ESC key in complete step (go back)."""
        youtube_screen.current_step = "complete"

        await youtube_screen.handle_input("escape")

        mock_cli.go_back.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_state(self, youtube_screen):
        """Test state reset functionality."""
        # Set some state
        youtube_screen.current_step = "complete"
        youtube_screen.video_info = {"title": "Test"}
        youtube_screen.error_message = "Some error"
        youtube_screen.success_message = "Some success"

        youtube_screen._reset_state()

        assert youtube_screen.current_step == "input"
        assert youtube_screen.video_info is None
        assert youtube_screen.processing_progress is None
        assert youtube_screen.error_message == ""
        assert youtube_screen.success_message == ""

    @pytest.mark.asyncio
    async def test_on_enter(self, youtube_screen):
        """Test screen enter event."""
        youtube_screen.current_step = "complete"  # Set non-initial state

        with patch.object(youtube_screen, "render") as mock_render:
            await youtube_screen.on_enter()

            assert youtube_screen.current_step == "input"  # Should be reset
            mock_render.assert_called_once()

    @pytest.mark.asyncio
    async def test_progress_callback_integration(self, youtube_screen, mock_cli):
        """Test progress callback integration during processing."""
        youtube_screen.video_info = {
            "url": "https://youtube.com/watch?v=test123",
            "title": "Test Video",
        }

        progress_updates = []

        def mock_progress_callback(progress, status):
            progress_updates.append((progress, status))

        with patch(
            "src.presentation.cli.screens.youtube_screen.ProcessYouTubeVideoUseCase"
        ) as mock_use_case_class:
            mock_use_case = AsyncMock()

            # Simulate progress callback calls
            async def mock_execute(request):
                if request.progress_callback:
                    request.progress_callback(10, "Baixando...")
                    request.progress_callback(50, "Transcrevendo...")
                    request.progress_callback(100, "Concluído!")

                mock_video = Video(id="test", title="Test", file_path="/path")
                return ProcessYouTubeVideoResponse(
                    video=mock_video, transcription="Test", downloaded_file="/path"
                )

            mock_use_case.execute = mock_execute
            mock_use_case_class.return_value = mock_use_case

            with patch.object(youtube_screen, "render") as mock_render:
                await youtube_screen._start_processing()

                # Verify progress updates were processed
                assert mock_render.call_count >= 3  # Initial + progress updates

    @pytest.mark.asyncio
    async def test_fetch_video_info_error_handling(self, youtube_screen):
        """Test error handling in video info fetching."""
        with patch("src.presentation.cli.screens.youtube_screen.yt_dlp") as mock_yt_dlp:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = Exception("Network error")
            mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl

            with pytest.raises(Exception, match="Erro ao acessar vídeo"):
                await youtube_screen._fetch_video_info(
                    "https://youtube.com/watch?v=test123"
                )
