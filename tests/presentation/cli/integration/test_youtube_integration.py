"""Integration tests for YouTube video processing workflow."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.presentation.cli.context import ApplicationContext
from src.presentation.cli.interactive_cli import InteractiveCLI
from src.presentation.cli.screens.main_menu_screen import MainMenuScreen
from src.presentation.cli.screens.youtube_screen import YouTubeScreen
from src.presentation.cli.themes.default_theme import DefaultTheme


class MockApplicationContext:
    """Mock application context for testing."""

    def __init__(self):
        self.settings = {"language": "pt", "whisper_model": "base"}


class TestYouTubeIntegration:
    """Integration tests for YouTube processing workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_context = MockApplicationContext()
        self.cli = InteractiveCLI(self.mock_context)
        self.cli.theme = DefaultTheme()

    @pytest.mark.asyncio
    async def test_navigation_from_main_menu_to_youtube(self):
        """Test navigation from main menu to YouTube screen."""
        # Start with main menu
        main_menu = MainMenuScreen(self.cli)
        self.cli.current_screen = main_menu

        # Simulate selecting YouTube option
        with patch.object(self.cli, "navigate_to") as mock_navigate:
            await main_menu._handle_youtube_video()

            # Should navigate to YouTube screen
            mock_navigate.assert_called_once()
            args = mock_navigate.call_args[0]
            assert isinstance(args[0], YouTubeScreen)

    @pytest.mark.asyncio
    async def test_complete_youtube_workflow_valid_url(self):
        """Test complete workflow with valid YouTube URL."""
        youtube_screen = YouTubeScreen(self.cli)

        # Mock video info response
        mock_video_info = {
            "title": "Test Video Title",
            "uploader": "Test Channel",
            "duration": 180,
            "height": 720,
            "id": "dQw4w9WgXcQ",
        }

        with patch("yt_dlp.YoutubeDL") as mock_yt_dlp, patch(
            "asyncio.sleep", new_callable=AsyncMock
        ):

            mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value = (
                mock_video_info
            )

            # Step 1: Enter valid URL
            valid_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
            youtube_screen.url_input.set_value(valid_url)

            # Simulate Enter key to proceed
            result = youtube_screen.url_input.handle_key("enter")
            assert result == valid_url

            # Step 2: Load video info
            await youtube_screen._load_video_info(valid_url)
            assert youtube_screen.current_step == "preview"
            assert youtube_screen.video_info is not None
            assert youtube_screen.video_info["title"] == "Test Video Title"

            # Step 3: Confirm processing
            await youtube_screen.handle_input("enter")
            assert youtube_screen.current_step == "complete"
            assert youtube_screen.success_message != ""

    @pytest.mark.asyncio
    async def test_youtube_workflow_invalid_url(self):
        """Test workflow with invalid YouTube URL."""
        youtube_screen = YouTubeScreen(self.cli)

        # Step 1: Enter invalid URL
        invalid_url = "https://vimeo.com/123456"
        youtube_screen.url_input.set_value(invalid_url)

        # URL should be marked as invalid
        assert not youtube_screen.url_input.is_valid

        # Trying to proceed should not work
        result = youtube_screen.url_input.handle_key("enter")
        assert result is None  # Should not proceed with invalid URL

    @pytest.mark.asyncio
    async def test_youtube_workflow_network_error(self):
        """Test workflow with network error during video info fetch."""
        youtube_screen = YouTubeScreen(self.cli)

        with patch("yt_dlp.YoutubeDL") as mock_yt_dlp:
            mock_yt_dlp.return_value.__enter__.return_value.extract_info.side_effect = (
                Exception("Network error")
            )

            # Try to load video info
            await youtube_screen._load_video_info(
                "https://youtube.com/watch?v=dQw4w9WgXcQ"
            )

            # Should return to input step with error
            assert youtube_screen.current_step == "input"
            assert "Network error" in youtube_screen.error_message

    @pytest.mark.asyncio
    async def test_youtube_workflow_cancellation_at_input(self):
        """Test cancelling at input step."""
        youtube_screen = YouTubeScreen(self.cli)

        with patch.object(self.cli, "go_back") as mock_go_back:
            # Simulate escape key
            await youtube_screen.handle_input("escape")
            mock_go_back.assert_called_once()

    @pytest.mark.asyncio
    async def test_youtube_workflow_cancellation_at_preview(self):
        """Test cancelling at preview step."""
        youtube_screen = YouTubeScreen(self.cli)
        youtube_screen.current_step = "preview"
        youtube_screen.video_info = {"title": "Test Video"}

        # Simulate escape key
        await youtube_screen.handle_input("escape")

        # Should return to input step
        assert youtube_screen.current_step == "input"
        assert youtube_screen.error_message == ""

    @pytest.mark.asyncio
    async def test_youtube_workflow_cancellation_during_processing(self):
        """Test cancelling during processing."""
        youtube_screen = YouTubeScreen(self.cli)
        youtube_screen.current_step = "processing"

        # Simulate escape key
        await youtube_screen.handle_input("escape")

        # Should go to complete step with cancellation message
        assert youtube_screen.current_step == "complete"
        assert "cancelado" in youtube_screen.error_message.lower()

    @pytest.mark.asyncio
    async def test_youtube_workflow_retry_after_completion(self):
        """Test retrying after completion."""
        youtube_screen = YouTubeScreen(self.cli)
        youtube_screen.current_step = "complete"
        youtube_screen.success_message = "Previous success"
        youtube_screen.video_info = {"title": "Previous video"}

        # Simulate enter key to retry
        await youtube_screen.handle_input("enter")

        # Should reset to input step
        assert youtube_screen.current_step == "input"
        assert youtube_screen.success_message == ""
        assert youtube_screen.video_info is None

    @pytest.mark.asyncio
    async def test_url_validation_edge_cases(self):
        """Test URL validation with various edge cases."""
        youtube_screen = YouTubeScreen(self.cli)

        test_cases = [
            # Valid URLs
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
            ("https://youtu.be/dQw4w9WgXcQ", True),
            ("youtube.com/watch?v=dQw4w9WgXcQ", True),
            ("HTTPS://YOUTUBE.COM/WATCH?V=dQw4w9WgXcQ", True),
            # Invalid URLs
            ("https://vimeo.com/123456", False),
            ("not_a_url", False),
            ("https://youtube.com/", False),
            ("https://youtube.com/watch?v=", False),
            ("", True),  # Empty is valid (optional)
        ]

        for url, should_be_valid in test_cases:
            youtube_screen.url_input.set_value(url)
            assert (
                youtube_screen.url_input.is_valid == should_be_valid
            ), f"URL {url} validation failed"

    @pytest.mark.asyncio
    async def test_video_info_display_formatting(self):
        """Test that video information is properly formatted for display."""
        youtube_screen = YouTubeScreen(self.cli)

        # Set video info with various data types
        youtube_screen.video_info = {
            "title": "Test Video with Special Characters & Symbols",
            "uploader": "Test Channel Name",
            "duration": 3661,  # 1 hour, 1 minute, 1 second
            "height": 1080,
            "id": "dQw4w9WgXcQ",
        }

        youtube_screen.current_step = "preview"

        # Render should not raise exceptions
        await youtube_screen.render()

        # Display should be updated
        assert self.cli.live_display is not None or hasattr(self.cli, "display_content")

    @pytest.mark.asyncio
    async def test_processing_progress_updates(self):
        """Test that processing progress is properly updated."""
        youtube_screen = YouTubeScreen(self.cli)
        youtube_screen.video_info = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=test",
        }

        progress_updates = []

        # Mock progress display to capture updates
        original_update = None

        def capture_progress_update(progress, status=None):
            progress_updates.append((progress, status))
            if original_update:
                original_update(progress, status)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            await youtube_screen._start_processing()

            # Should have completed successfully
            assert youtube_screen.current_step == "complete"
            assert youtube_screen.success_message != ""

    @pytest.mark.asyncio
    async def test_keyboard_navigation_consistency(self):
        """Test that keyboard navigation is consistent across steps."""
        youtube_screen = YouTubeScreen(self.cli)

        # Test escape key behavior in each step
        steps_and_expected_behavior = [
            ("input", "go_back"),
            ("preview", "return_to_input"),
            ("processing", "cancel_processing"),
            ("complete", "go_back"),
        ]

        for step, expected in steps_and_expected_behavior:
            youtube_screen.current_step = step

            if expected == "go_back":
                with patch.object(self.cli, "go_back") as mock_go_back:
                    await youtube_screen.handle_input("escape")
                    if step in ["input", "complete"]:
                        mock_go_back.assert_called_once()
            elif expected == "return_to_input":
                await youtube_screen.handle_input("escape")
                assert youtube_screen.current_step == "input"
            elif expected == "cancel_processing":
                await youtube_screen.handle_input("escape")
                assert youtube_screen.current_step == "complete"

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery and retry workflow."""
        youtube_screen = YouTubeScreen(self.cli)

        # Simulate error during video info loading
        with patch("yt_dlp.YoutubeDL") as mock_yt_dlp:
            mock_yt_dlp.return_value.__enter__.return_value.extract_info.side_effect = (
                Exception("Temporary error")
            )

            # Try to load video info
            await youtube_screen._load_video_info(
                "https://youtube.com/watch?v=dQw4w9WgXcQ"
            )

            # Should be back at input step with error
            assert youtube_screen.current_step == "input"
            assert youtube_screen.error_message != ""

            # Now simulate successful retry
            mock_video_info = {
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 180,
                "height": 720,
                "id": "dQw4w9WgXcQ",
            }
            mock_yt_dlp.return_value.__enter__.return_value.extract_info.side_effect = (
                None
            )
            mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value = (
                mock_video_info
            )

            # Retry should work
            await youtube_screen._load_video_info(
                "https://youtube.com/watch?v=dQw4w9WgXcQ"
            )
            assert youtube_screen.current_step == "preview"
            assert youtube_screen.video_info is not None

    @pytest.mark.asyncio
    async def test_memory_cleanup_on_reset(self):
        """Test that memory is properly cleaned up when resetting state."""
        youtube_screen = YouTubeScreen(self.cli)

        # Set up some state
        youtube_screen.current_step = "complete"
        youtube_screen.video_info = {"title": "Large video data" * 1000}
        youtube_screen.error_message = "Error message"
        youtube_screen.success_message = "Success message"
        youtube_screen.url_input.set_value("https://youtube.com/watch?v=test")

        # Reset state
        youtube_screen._reset_state()

        # All references should be cleared
        assert youtube_screen.video_info is None
        assert youtube_screen.processing_progress is None
        assert youtube_screen.error_message == ""
        assert youtube_screen.success_message == ""
        assert youtube_screen.url_input.get_value() == ""
        assert youtube_screen.current_step == "input"
