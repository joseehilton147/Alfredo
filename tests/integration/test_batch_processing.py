"""Integration tests for batch processing functionality."""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.presentation.cli.screens.batch_screen import BatchScreen


class TestBatchProcessingIntegration:
    """Integration tests for batch processing workflow."""

    @pytest.fixture
    def temp_video_files(self):
        """Create temporary video files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock video files
            video_files = []
            for i in range(3):
                video_file = temp_path / f"test_video_{i}.mp4"
                video_file.write_text(f"Mock video content {i}")
                video_files.append(video_file)

            yield temp_path, video_files

    @pytest.fixture
    def mock_cli_with_context(self):
        """Create a mock CLI with application context."""
        cli = MagicMock()
        cli.theme = MagicMock()
        cli.theme.get_style.return_value = "white"
        cli.theme.border_style = "blue"
        cli.state = MagicMock()
        cli.keyboard = MagicMock()
        cli.keyboard.ARROW_UP = "up"
        cli.keyboard.ARROW_DOWN = "down"
        cli.keyboard.ENTER = "enter"
        cli.keyboard.ESC = "esc"
        cli.update_live_display = MagicMock()

        # Mock application context
        cli.app_context = MagicMock()
        cli.app_context.video_repository = AsyncMock()
        cli.app_context.transcribe_use_case = AsyncMock()

        return cli

    @pytest.fixture
    def batch_screen_with_context(self, mock_cli_with_context):
        """Create a BatchScreen with mocked context."""
        return BatchScreen(mock_cli_with_context)

    @pytest.mark.asyncio
    async def test_complete_file_selection_workflow(
        self, batch_screen_with_context, temp_video_files
    ):
        """Test complete workflow for file selection mode."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Start in selection type mode
        assert screen.current_mode == "selection_type"

        # Select files mode
        screen._select_type("files")
        assert screen.current_mode == "file_selection"
        assert screen.selection_type == "files"

        # Navigate to temp directory
        screen.file_explorer.navigate_to(temp_path)

        # Select files
        for video_file in video_files:
            screen.selected_files.add(video_file)

        assert len(screen.selected_files) == 3

        # Move to language selection
        screen.current_mode = "language_select"

        # Select language
        screen._select_language("en")
        assert screen.current_mode == "confirm"
        assert screen.selected_language == "en"

        # Get files to process
        files_to_process = screen._get_files_to_process()
        assert len(files_to_process) == 3
        assert all(f in files_to_process for f in video_files)

    @pytest.mark.asyncio
    async def test_complete_folder_selection_workflow(
        self, batch_screen_with_context, temp_video_files
    ):
        """Test complete workflow for folder selection mode."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Start in selection type mode
        assert screen.current_mode == "selection_type"

        # Select folder mode
        screen._select_type("folder")
        assert screen.current_mode == "folder_selection"
        assert screen.selection_type == "folder"

        # Navigate to temp directory
        screen.file_explorer.navigate_to(temp_path)

        # Select current folder
        screen.selected_folder = temp_path

        # Move to language selection
        screen.current_mode = "language_select"

        # Select language
        screen._select_language("pt")
        assert screen.current_mode == "confirm"
        assert screen.selected_language == "pt"

    @pytest.mark.asyncio
    async def test_batch_processing_execution(
        self, batch_screen_with_context, temp_video_files
    ):
        """Test actual batch processing execution."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Setup for processing
        screen.selection_type = "files"
        screen.selected_files = set(video_files)
        screen.selected_language = "en"

        # Mock transcription responses
        mock_responses = []
        for i, video_file in enumerate(video_files):
            mock_response = MagicMock()
            mock_response.video = MagicMock()
            mock_response.video.id = f"video_{i}"
            mock_response.video.title = f"Test Video {i}"
            mock_response.video.file_path = str(video_file)
            mock_response.video.metadata = {"source": "batch"}
            mock_response.transcription = f"Transcription for video {i}"
            mock_responses.append(mock_response)

        screen.cli.app_context.transcribe_use_case.execute.side_effect = mock_responses

        # Mock save method to avoid file I/O
        screen._save_transcription_result = AsyncMock()

        # Start processing
        await screen._start_batch_processing()

        # Verify processing completed
        assert screen.current_mode == "results"
        assert len(screen.processing_results) == 3

        # Check all results are successful
        successful_results = [r for r in screen.processing_results if r.success]
        assert len(successful_results) == 3

        # Verify transcription use case was called for each file
        assert screen.cli.app_context.transcribe_use_case.execute.call_count == 3

        # Verify save was called for each successful transcription
        assert screen._save_transcription_result.call_count == 3

    @pytest.mark.asyncio
    async def test_batch_processing_with_errors(
        self, batch_screen_with_context, temp_video_files
    ):
        """Test batch processing with some files failing."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Setup for processing
        screen.selection_type = "files"
        screen.selected_files = set(video_files)
        screen.selected_language = "en"

        # Mock transcription responses - some succeed, some fail
        def mock_transcribe_side_effect(request):
            if "test_video_1" in request.audio_path:
                raise Exception("Transcription failed for video 1")

            mock_response = MagicMock()
            mock_response.video = MagicMock()
            mock_response.video.id = "video_success"
            mock_response.video.title = "Successful Video"
            mock_response.video.file_path = request.audio_path
            mock_response.video.metadata = {"source": "batch"}
            mock_response.transcription = "Successful transcription"
            return mock_response

        screen.cli.app_context.transcribe_use_case.execute.side_effect = (
            mock_transcribe_side_effect
        )

        # Mock save method
        screen._save_transcription_result = AsyncMock()

        # Start processing
        await screen._start_batch_processing()

        # Verify processing completed
        assert screen.current_mode == "results"
        assert len(screen.processing_results) == 3

        # Check results - should have both successes and failures
        successful_results = [r for r in screen.processing_results if r.success]
        failed_results = [r for r in screen.processing_results if not r.success]

        assert len(successful_results) == 2  # 2 successful
        assert len(failed_results) == 1  # 1 failed

        # Check failed result has error message
        failed_result = failed_results[0]
        assert "Transcription failed for video 1" in failed_result.error_message

    @pytest.mark.asyncio
    async def test_transcription_result_saving(self, batch_screen_with_context):
        """Test saving of transcription results."""
        screen = batch_screen_with_context

        # Create mock video and transcription
        mock_video = MagicMock()
        mock_video.id = "test_video_id"
        mock_video.title = "Test Video"
        mock_video.file_path = "/path/to/video.mp4"
        mock_video.metadata = {"source": "batch", "original_name": "video.mp4"}

        transcription = "This is a test transcription with multiple sentences. It should be saved properly."

        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock Path.mkdir and file operations
            with patch("pathlib.Path.mkdir") as mock_mkdir, patch(
                "builtins.open", create=True
            ) as mock_open, patch("json.dump") as mock_json_dump:

                # Mock file handles
                mock_text_file = MagicMock()
                mock_json_file = MagicMock()
                mock_open.side_effect = [mock_text_file, mock_json_file]

                await screen._save_transcription_result(mock_video, transcription)

                # Verify directory creation
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

                # Verify text file writing
                mock_text_file.__enter__.return_value.write.assert_called_once_with(
                    transcription
                )

                # Verify JSON file writing
                mock_json_dump.assert_called_once()

                # Check JSON data structure
                json_call_args = mock_json_dump.call_args[0]
                json_data = json_call_args[0]

                assert json_data["video_id"] == "test_video_id"
                assert json_data["title"] == "Test Video"
                assert json_data["transcription"] == transcription
                assert json_data["language"] == screen.selected_language
                assert "created_at" in json_data

    @pytest.mark.asyncio
    async def test_error_handling_during_processing(
        self, batch_screen_with_context, temp_video_files
    ):
        """Test error handling during batch processing."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Setup for processing
        screen.selection_type = "files"
        screen.selected_files = set(video_files[:1])  # Just one file
        screen.selected_language = "en"

        # Mock application context to be None (will cause error)
        screen.cli.app_context = None

        # Start processing
        await screen._start_batch_processing()

        # Should handle error gracefully and move to results
        assert screen.current_mode == "results"
        assert len(screen.processing_results) == 1
        assert not screen.processing_results[0].success
        assert (
            "Contexto da aplicação não disponível"
            in screen.processing_results[0].error_message
        )

    @pytest.mark.asyncio
    async def test_navigation_between_modes(self, batch_screen_with_context):
        """Test navigation between different modes."""
        screen = batch_screen_with_context

        # Start in selection type
        assert screen.current_mode == "selection_type"

        # Navigate to file selection
        await screen._handle_selection_type_input("f")  # Assuming 'f' selects files

        # Navigate back with backspace
        await screen._handle_file_selection_input("backspace")
        assert screen.current_mode == "selection_type"

        # Navigate to folder selection
        screen._select_type("folder")
        assert screen.current_mode == "folder_selection"

        # Navigate back
        await screen._handle_folder_selection_input("backspace")
        assert screen.current_mode == "selection_type"

    @pytest.mark.asyncio
    async def test_file_selection_operations(
        self, batch_screen_with_context, temp_video_files
    ):
        """Test file selection operations."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Setup file selection mode
        screen.current_mode = "file_selection"
        screen.file_explorer.navigate_to(temp_path)

        # Mock file explorer methods
        screen.file_explorer.get_selected_entry = MagicMock()
        screen.file_explorer.get_video_files_in_current_dir = MagicMock(
            return_value=video_files
        )

        # Test selecting individual files
        for video_file in video_files:
            screen.file_explorer.get_selected_entry.return_value = (video_file, False)
            await screen._handle_file_selection_input(" ")  # Space to select

        assert len(screen.selected_files) == 3

        # Test select all
        screen.selected_files.clear()
        await screen._handle_file_selection_input("a")
        assert len(screen.selected_files) == 3

        # Test clear selection
        await screen._handle_file_selection_input("c")
        assert len(screen.selected_files) == 0

    @pytest.mark.asyncio
    async def test_progress_tracking(self, batch_screen_with_context, temp_video_files):
        """Test progress tracking during batch processing."""
        temp_path, video_files = temp_video_files
        screen = batch_screen_with_context

        # Setup for processing
        screen.selection_type = "files"
        screen.selected_files = set(video_files)
        screen.selected_language = "en"

        # Mock transcription to track progress calls
        progress_updates = []

        async def mock_process_file(file_path, progress):
            # Simulate progress updates
            progress.update(10, "Starting...")
            progress_updates.append((file_path, 10, "Starting..."))

            progress.update(50, "Processing...")
            progress_updates.append((file_path, 50, "Processing..."))

            progress.complete("Done!")
            progress_updates.append((file_path, 100, "Done!"))

            # Return successful result
            from src.presentation.cli.screens.batch_screen import BatchProcessingResult

            return BatchProcessingResult(
                file_path=file_path,
                success=True,
                transcription="Test transcription",
                processing_time=1.0,
            )

        screen._process_single_file = mock_process_file

        # Start processing
        await screen._start_batch_processing()

        # Verify progress was tracked for each file
        assert len(progress_updates) == 9  # 3 files × 3 updates each

        # Verify processing completed
        assert screen.current_mode == "results"
        assert len(screen.processing_results) == 3

        # Check that all results are successful
        successful_count = sum(1 for r in screen.processing_results if r.success)
        failed_count = sum(1 for r in screen.processing_results if not r.success)

        # Debug information
        if failed_count > 0:
            for i, result in enumerate(screen.processing_results):
                print(
                    f"Result {i}: success={result.success}, error={result.error_message}"
                )

        assert (
            successful_count == 3
        ), f"Expected 3 successful results, got {successful_count} successful and {failed_count} failed"

    def test_language_menu_creation(self, batch_screen_with_context):
        """Test language menu creation and selection."""
        screen = batch_screen_with_context

        # Create language menu
        screen._create_language_menu()

        assert screen.language_menu is not None
        assert len(screen.language_menu.options) == len(screen.SUPPORTED_LANGUAGES)

        # Check that current language is marked as selected
        selected_option = None
        for option in screen.language_menu.options:
            if option.key == screen.selected_language:
                selected_option = option
                break

        assert selected_option is not None
        assert selected_option.icon == "✅"

    def test_type_menu_creation(self, batch_screen_with_context):
        """Test type selection menu creation."""
        screen = batch_screen_with_context

        # Create type menu
        screen._create_type_menu()

        assert screen.type_menu is not None
        assert len(screen.type_menu.options) == 2  # files and folder options

        # Check options
        option_keys = [opt.key for opt in screen.type_menu.options]
        assert "files" in option_keys
        assert "folder" in option_keys
