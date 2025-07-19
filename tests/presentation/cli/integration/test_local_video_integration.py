"""Integration tests for LocalVideoScreen."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities.video import Video
from src.presentation.cli.screens.local_video_screen import LocalVideoScreen
from src.presentation.cli.state import CLIState
from src.presentation.cli.themes.default_theme import DefaultTheme


class MockKeyboardHandler:
    """Mock keyboard handler for testing."""

    def __init__(self):
        self.ESC = '\x1b'
        self.F1 = '\x1b[OP'
        self.ARROW_UP = '\x1b[A'
        self.ARROW_DOWN = '\x1b[B'
        self.ENTER = '\r'

    def setup_terminal(self):
        pass

    def restore_terminal(self):
        pass

    def read_key(self):
        return ''


class MockApplicationContext:
    """Mock application context for testing."""

    def __init__(self):
        self.video_repository = AsyncMock()
        self.whisper_provider = AsyncMock()
        self.transcribe_use_case = AsyncMock()
        self.settings = {
            'DEFAULT_LANGUAGE': 'pt',
            'WHISPER_MODEL': 'base',
            'OUTPUT_DIR': 'data/output'
        }

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)


@pytest.fixture
def mock_app_context():
    """Create a mock application context."""
    return MockApplicationContext()


@pytest.fixture
def mock_cli(mock_app_context):
    """Create a mock CLI instance."""
    cli = MagicMock()
    cli.app_context = mock_app_context
    cli.theme = DefaultTheme()
    cli.state = CLIState()
    cli.keyboard = MockKeyboardHandler()
    cli.update_live_display = MagicMock()
    cli.get_screen_stack_depth = MagicMock(return_value=1)
    cli.peek_previous_screen = MagicMock(return_value=None)
    return cli


@pytest.fixture
def local_video_screen(mock_cli):
    """Create a LocalVideoScreen instance for testing."""
    return LocalVideoScreen(mock_cli)


@pytest.fixture
def sample_video_file():
    """Create a temporary video file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        f.write(b'fake video content')
        video_path = Path(f.name)

    yield video_path

    # Cleanup
    if video_path.exists():
        video_path.unlink()


class TestLocalVideoScreenInitialization:
    """Test LocalVideoScreen initialization."""

    def test_initialization(self, local_video_screen):
        """Test that LocalVideoScreen initializes correctly."""
        assert local_video_screen.current_mode == "file_browser"
        assert local_video_screen.selected_file is None
        assert local_video_screen.selected_language == "pt"
        assert local_video_screen.file_explorer is not None
        assert not local_video_screen.is_processing

    def test_supported_languages(self, local_video_screen):
        """Test that supported languages are properly defined."""
        languages = local_video_screen.SUPPORTED_LANGUAGES
        assert "pt" in languages
        assert "en" in languages
        assert "es" in languages
        assert languages["pt"] == "Português"
        assert languages["en"] == "English"


class TestLocalVideoScreenNavigation:
    """Test navigation between different modes."""

    @pytest.mark.asyncio
    async def test_file_browser_mode_rendering(self, local_video_screen):
        """Test rendering in file browser mode."""
        local_video_screen.current_mode = "file_browser"

        # Mock file explorer to avoid file system dependencies
        local_video_screen.file_explorer.has_video_files = MagicMock(return_value=True)
        local_video_screen.file_explorer.render = MagicMock(return_value=MagicMock(renderable="mock_content"))

        await local_video_screen.render()

        # Verify that update_display was called
        local_video_screen.cli.update_live_display.assert_called_once()

    @pytest.mark.asyncio
    async def test_language_selection_mode(self, local_video_screen, sample_video_file):
        """Test language selection mode."""
        local_video_screen.selected_file = sample_video_file
        local_video_screen.current_mode = "language_select"

        await local_video_screen.render()

        # Verify language menu was created
        assert local_video_screen.language_menu is not None

        # Verify display was updated
        local_video_screen.cli.update_live_display.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirmation_mode(self, local_video_screen, sample_video_file):
        """Test confirmation mode rendering."""
        local_video_screen.selected_file = sample_video_file
        local_video_screen.selected_language = "en"
        local_video_screen.current_mode = "confirm"

        await local_video_screen.render()

        # Verify display was updated
        local_video_screen.cli.update_live_display.assert_called_once()

    @pytest.mark.asyncio
    async def test_processing_mode(self, local_video_screen, sample_video_file):
        """Test processing mode rendering."""
        local_video_screen.selected_file = sample_video_file
        local_video_screen.selected_language = "pt"
        local_video_screen.current_mode = "processing"

        await local_video_screen.render()

        # Verify display was updated
        local_video_screen.cli.update_live_display.assert_called_once()


class TestLocalVideoScreenInput:
    """Test input handling in different modes."""

    @pytest.mark.asyncio
    async def test_file_browser_input_navigation(self, local_video_screen):
        """Test navigation input in file browser mode."""
        local_video_screen.current_mode = "file_browser"
        local_video_screen.file_explorer.handle_key = MagicMock(return_value=None)

        # Test arrow key navigation
        await local_video_screen.handle_input("up")
        local_video_screen.file_explorer.handle_key.assert_called_with("up")

        await local_video_screen.handle_input("down")
        local_video_screen.file_explorer.handle_key.assert_called_with("down")

    @pytest.mark.asyncio
    async def test_file_browser_file_selection(self, local_video_screen, sample_video_file):
        """Test file selection in file browser mode."""
        local_video_screen.current_mode = "file_browser"
        local_video_screen.file_explorer.handle_key = MagicMock(return_value=sample_video_file)

        await local_video_screen.handle_input("enter")

        # Verify file was selected and mode changed
        assert local_video_screen.selected_file == sample_video_file
        assert local_video_screen.current_mode == "language_select"

    @pytest.mark.asyncio
    async def test_language_selection_input(self, local_video_screen, sample_video_file):
        """Test input handling in language selection mode."""
        local_video_screen.selected_file = sample_video_file
        local_video_screen.current_mode = "language_select"
        local_video_screen._create_language_menu()

        # Test backspace to go back
        await local_video_screen.handle_input("backspace")
        assert local_video_screen.current_mode == "file_browser"

    @pytest.mark.asyncio
    async def test_confirmation_input(self, local_video_screen, sample_video_file):
        """Test input handling in confirmation mode."""
        local_video_screen.selected_file = sample_video_file
        local_video_screen.current_mode = "confirm"

        # Test backspace to go back
        await local_video_screen.handle_input("backspace")
        assert local_video_screen.current_mode == "language_select"


class TestLocalVideoScreenProcessing:
    """Test video processing functionality."""

    @pytest.mark.asyncio
    async def test_start_processing_success(self, local_video_screen, sample_video_file):
        """Test successful video processing."""
        # Setup
        local_video_screen.selected_file = sample_video_file
        local_video_screen.selected_language = "pt"

        # Mock the use case response
        mock_video = Video(
            id="test-id",
            title="Test Video",
            file_path=str(sample_video_file)
        )

        mock_response = MagicMock()
        mock_response.video = mock_video
        mock_response.transcription = "This is a test transcription."

        local_video_screen.cli.app_context.transcribe_use_case.execute = AsyncMock(return_value=mock_response)
        local_video_screen.cli.app_context.video_repository.save = AsyncMock()

        # Mock file operations
        with patch('builtins.open', create=True):
            with patch('json.dump'):
                with patch('pathlib.Path.mkdir'):
                    with patch.object(local_video_screen, '_wait_for_any_key', new_callable=AsyncMock):
                        await local_video_screen._start_processing()

        # Verify use case was called
        local_video_screen.cli.app_context.transcribe_use_case.execute.assert_called_once()

        # Verify video was saved
        local_video_screen.cli.app_context.video_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_processing_error(self, local_video_screen, sample_video_file):
        """Test error handling during processing."""
        # Setup
        local_video_screen.selected_file = sample_video_file
        local_video_screen.selected_language = "pt"

        # Mock the use case to raise an error
        local_video_screen.cli.app_context.transcribe_use_case.execute = AsyncMock(
            side_effect=Exception("Test error")
        )
        local_video_screen.cli.app_context.video_repository.save = AsyncMock()

        # Mock _wait_for_any_key to avoid blocking
        with patch.object(local_video_screen, '_wait_for_any_key', new_callable=AsyncMock):
            await local_video_screen._start_processing()

        # Verify error handling
        assert not local_video_screen.is_processing

    @pytest.mark.asyncio
    async def test_processing_without_file(self, local_video_screen):
        """Test processing when no file is selected."""
        local_video_screen.selected_file = None

        await local_video_screen._start_processing()

        # Should return early without processing
        assert not local_video_screen.is_processing

    @pytest.mark.asyncio
    async def test_processing_with_nonexistent_file(self, local_video_screen):
        """Test processing with a file that doesn't exist."""
        local_video_screen.selected_file = Path("/nonexistent/file.mp4")

        await local_video_screen._start_processing()

        # Should return early without processing
        assert not local_video_screen.is_processing


class TestLocalVideoScreenUtilities:
    """Test utility methods."""

    def test_format_file_size(self, local_video_screen):
        """Test file size formatting."""
        assert local_video_screen._format_file_size(500) == "500 B"
        assert local_video_screen._format_file_size(1536) == "1.5 KB"
        assert local_video_screen._format_file_size(1048576) == "1.0 MB"
        assert local_video_screen._format_file_size(1073741824) == "1.0 GB"

    def test_select_language(self, local_video_screen):
        """Test language selection."""
        local_video_screen._select_language("en")

        assert local_video_screen.selected_language == "en"
        assert local_video_screen.current_mode == "confirm"

    def test_reset_screen(self, local_video_screen):
        """Test screen reset functionality."""
        # Set some state
        local_video_screen.current_mode = "processing"
        local_video_screen.selected_file = Path("test.mp4")
        local_video_screen.selected_language = "en"
        local_video_screen.is_processing = True

        # Reset
        local_video_screen._reset_screen()

        # Verify reset
        assert local_video_screen.current_mode == "file_browser"
        assert local_video_screen.selected_file is None
        assert local_video_screen.selected_language == "pt"
        assert not local_video_screen.is_processing


class TestLocalVideoScreenLifecycle:
    """Test screen lifecycle methods."""

    @pytest.mark.asyncio
    async def test_on_enter(self, local_video_screen):
        """Test on_enter lifecycle method."""
        # Set some state first
        local_video_screen.current_mode = "processing"
        local_video_screen.selected_file = Path("test.mp4")

        await local_video_screen.on_enter()

        # Verify screen was reset
        assert local_video_screen.current_mode == "file_browser"
        assert local_video_screen.selected_file is None
        assert local_video_screen.state.current_screen == "local_video"

    @pytest.mark.asyncio
    async def test_on_exit(self, local_video_screen):
        """Test on_exit lifecycle method."""
        # Set processing state
        local_video_screen.is_processing = True
        local_video_screen.progress_display = MagicMock()
        local_video_screen.progress_display.stop = MagicMock()

        await local_video_screen.on_exit()

        # Verify cleanup
        local_video_screen.progress_display.stop.assert_called_once()


class TestLocalVideoScreenIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_workflow_success(self, local_video_screen, sample_video_file):
        """Test complete workflow from file selection to processing."""
        # Mock dependencies
        local_video_screen.file_explorer.handle_key = MagicMock(return_value=sample_video_file)

        mock_video = Video(
            id="test-id",
            title="Test Video",
            file_path=str(sample_video_file)
        )

        mock_response = MagicMock()
        mock_response.video = mock_video
        mock_response.transcription = "Test transcription"

        local_video_screen.cli.app_context.transcribe_use_case.execute = AsyncMock(return_value=mock_response)
        local_video_screen.cli.app_context.video_repository.save = AsyncMock()

        # Step 1: File selection
        await local_video_screen.handle_input("enter")
        assert local_video_screen.current_mode == "language_select"
        assert local_video_screen.selected_file == sample_video_file

        # Step 2: Language selection (use default)
        local_video_screen._select_language("pt")
        assert local_video_screen.current_mode == "confirm"
        assert local_video_screen.selected_language == "pt"

        # Step 3: Confirmation and processing
        with patch('builtins.open', create=True):
            with patch('json.dump'):
                with patch('pathlib.Path.mkdir'):
                    with patch.object(local_video_screen, '_wait_for_any_key', new_callable=AsyncMock):
                        await local_video_screen.handle_input("enter")

        # Verify final state
        assert local_video_screen.current_mode == "file_browser"  # Reset after success
        local_video_screen.cli.app_context.transcribe_use_case.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_with_navigation_back(self, local_video_screen, sample_video_file):
        """Test workflow with navigation back through modes."""
        # Start in language selection
        local_video_screen.selected_file = sample_video_file
        local_video_screen.current_mode = "language_select"

        # Go back to file browser
        await local_video_screen.handle_input("backspace")
        assert local_video_screen.current_mode == "file_browser"

        # Go to confirmation mode
        local_video_screen.current_mode = "confirm"

        # Go back to language selection
        await local_video_screen.handle_input("backspace")
        assert local_video_screen.current_mode == "language_select"

    @pytest.mark.asyncio
    async def test_error_recovery(self, local_video_screen, sample_video_file):
        """Test error recovery and screen reset."""
        # Setup for processing
        local_video_screen.selected_file = sample_video_file
        local_video_screen.selected_language = "pt"

        # Mock error in processing
        local_video_screen.cli.app_context.transcribe_use_case.execute = AsyncMock(
            side_effect=Exception("Processing failed")
        )
        local_video_screen.cli.app_context.video_repository.save = AsyncMock()

        with patch.object(local_video_screen, '_wait_for_any_key', new_callable=AsyncMock):
            await local_video_screen._start_processing()

        # Verify error recovery
        assert not local_video_screen.is_processing
        assert local_video_screen.current_mode == "file_browser"  # Should reset


if __name__ == "__main__":
    pytest.main([__file__])
