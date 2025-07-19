"""Tests for CLI state management."""

from pathlib import Path

import pytest

from src.presentation.cli.state import CLIState, ProcessingTask


class TestCLIState:
    """Test cases for CLIState class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.state = CLIState()

    def test_initialization_defaults(self):
        """Test that CLIState initializes with correct defaults."""
        assert self.state.current_screen == "main_menu"
        assert self.state.previous_screens == []
        assert self.state.settings == {}
        assert self.state.recent_files == []
        assert self.state.processing_queue == []
        assert self.state.last_results == []
        assert self.state.selected_language == "pt"
        assert self.state.selected_whisper_model == "base"
        assert self.state.output_directory is None
        assert not self.state.is_processing
        assert self.state.current_operation is None

    def test_add_recent_file_new_file(self):
        """Test adding a new file to recent files."""
        file_path = Path("test_video.mp4")

        self.state.add_recent_file(file_path)

        assert len(self.state.recent_files) == 1
        assert self.state.recent_files[0] == file_path

    def test_add_recent_file_duplicate(self):
        """Test adding a duplicate file moves it to front."""
        file1 = Path("video1.mp4")
        file2 = Path("video2.mp4")

        self.state.add_recent_file(file1)
        self.state.add_recent_file(file2)
        self.state.add_recent_file(file1)  # Add duplicate

        assert len(self.state.recent_files) == 2
        assert self.state.recent_files[0] == file1  # Should be first
        assert self.state.recent_files[1] == file2

    def test_recent_files_limit(self):
        """Test that recent files list is limited to 10 items."""
        # Add 15 files
        for i in range(15):
            self.state.add_recent_file(Path(f"video_{i}.mp4"))

        # Should only keep the last 10
        assert len(self.state.recent_files) == 10

        # Most recent should be first
        assert self.state.recent_files[0] == Path("video_14.mp4")
        # Oldest kept should be last
        assert self.state.recent_files[-1] == Path("video_5.mp4")

    def test_add_processing_task(self):
        """Test adding a processing task."""
        file_path = Path("test.mp4")
        language = "en"

        task = self.state.add_processing_task(file_path, language)

        assert isinstance(task, ProcessingTask)
        assert task.file_path == file_path
        assert task.language == language
        assert task.status == "pending"
        assert task.progress == 0
        assert task.error_message is None

        assert len(self.state.processing_queue) == 1
        assert self.state.processing_queue[0] == task

    def test_update_task_progress(self):
        """Test updating task progress."""
        task = self.state.add_processing_task(Path("test.mp4"), "pt")

        self.state.update_task_progress(task, 50)
        assert task.progress == 50
        assert task.status == "pending"  # Status unchanged

        self.state.update_task_progress(task, 75, "processing")
        assert task.progress == 75
        assert task.status == "processing"

    def test_complete_task_without_result(self):
        """Test completing a task without transcription result."""
        task = self.state.add_processing_task(Path("test.mp4"), "pt")

        self.state.complete_task(task)

        assert task.status == "completed"
        assert task.progress == 100
        assert len(self.state.last_results) == 0

    def test_complete_task_with_result(self):
        """Test completing a task with transcription result."""
        from unittest.mock import MagicMock

        task = self.state.add_processing_task(Path("test.mp4"), "pt")
        mock_result = MagicMock()

        self.state.complete_task(task, mock_result)

        assert task.status == "completed"
        assert task.progress == 100
        assert len(self.state.last_results) == 1
        assert self.state.last_results[0] == mock_result

    def test_last_results_limit(self):
        """Test that last results list is limited to 50 items."""
        from unittest.mock import MagicMock

        task = self.state.add_processing_task(Path("test.mp4"), "pt")

        # Add 55 results
        for i in range(55):
            mock_result = MagicMock()
            mock_result.id = i
            self.state.complete_task(task, mock_result)
            # Re-add task for next iteration
            if i < 54:
                task = self.state.add_processing_task(Path(f"test_{i}.mp4"), "pt")

        # Should only keep the last 50
        assert len(self.state.last_results) == 50
        # Most recent should be first
        assert self.state.last_results[0].id == 54
        # Oldest kept should be last
        assert self.state.last_results[-1].id == 5

    def test_fail_task(self):
        """Test failing a task."""
        task = self.state.add_processing_task(Path("test.mp4"), "pt")
        error_message = "Processing failed due to invalid format"

        self.state.fail_task(task, error_message)

        assert task.status == "failed"
        assert task.error_message == error_message

    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        task1 = self.state.add_processing_task(Path("test1.mp4"), "pt")
        task2 = self.state.add_processing_task(Path("test2.mp4"), "en")
        task3 = self.state.add_processing_task(Path("test3.mp4"), "es")

        # Complete one task, fail another
        self.state.complete_task(task1)
        self.state.fail_task(task2, "Error")
        # task3 remains pending

        pending_tasks = self.state.get_pending_tasks()

        assert len(pending_tasks) == 1
        assert pending_tasks[0] == task3
        assert pending_tasks[0].status == "pending"

    def test_get_completed_tasks(self):
        """Test getting completed tasks."""
        task1 = self.state.add_processing_task(Path("test1.mp4"), "pt")
        task2 = self.state.add_processing_task(Path("test2.mp4"), "en")
        task3 = self.state.add_processing_task(Path("test3.mp4"), "es")

        self.state.complete_task(task1)
        self.state.complete_task(task2)
        self.state.fail_task(task3, "Error")

        completed_tasks = self.state.get_completed_tasks()

        assert len(completed_tasks) == 2
        assert task1 in completed_tasks
        assert task2 in completed_tasks
        assert all(task.status == "completed" for task in completed_tasks)

    def test_get_failed_tasks(self):
        """Test getting failed tasks."""
        task1 = self.state.add_processing_task(Path("test1.mp4"), "pt")
        task2 = self.state.add_processing_task(Path("test2.mp4"), "en")
        task3 = self.state.add_processing_task(Path("test3.mp4"), "es")

        self.state.complete_task(task1)
        self.state.fail_task(task2, "Error 1")
        self.state.fail_task(task3, "Error 2")

        failed_tasks = self.state.get_failed_tasks()

        assert len(failed_tasks) == 2
        assert task2 in failed_tasks
        assert task3 in failed_tasks
        assert all(task.status == "failed" for task in failed_tasks)

    def test_clear_completed_tasks(self):
        """Test clearing completed tasks from queue."""
        task1 = self.state.add_processing_task(Path("test1.mp4"), "pt")
        task2 = self.state.add_processing_task(Path("test2.mp4"), "en")
        task3 = self.state.add_processing_task(Path("test3.mp4"), "es")

        self.state.complete_task(task1)
        self.state.complete_task(task2)
        self.state.fail_task(task3, "Error")

        assert len(self.state.processing_queue) == 3

        self.state.clear_completed_tasks()

        # Should only keep non-completed tasks
        assert len(self.state.processing_queue) == 1
        assert self.state.processing_queue[0] == task3
        assert self.state.processing_queue[0].status == "failed"

    def test_update_setting(self):
        """Test updating settings."""
        key = "whisper_model"
        value = "large"

        self.state.update_setting(key, value)

        assert self.state.settings[key] == value

    def test_get_setting_existing(self):
        """Test getting an existing setting."""
        key = "language"
        value = "en"
        self.state.settings[key] = value

        result = self.state.get_setting(key)

        assert result == value

    def test_get_setting_nonexistent_with_default(self):
        """Test getting a nonexistent setting with default."""
        key = "nonexistent_key"
        default = "default_value"

        result = self.state.get_setting(key, default)

        assert result == default

    def test_get_setting_nonexistent_without_default(self):
        """Test getting a nonexistent setting without default."""
        key = "nonexistent_key"

        result = self.state.get_setting(key)

        assert result is None


class TestProcessingTask:
    """Test cases for ProcessingTask class."""

    def test_initialization_with_defaults(self):
        """Test ProcessingTask initialization with default values."""
        file_path = Path("test_video.mp4")
        language = "pt"

        task = ProcessingTask(file_path, language)

        assert task.file_path == file_path
        assert task.language == language
        assert task.status == "pending"
        assert task.progress == 0
        assert task.error_message is None

    def test_initialization_with_custom_values(self):
        """Test ProcessingTask initialization with custom values."""
        file_path = Path("test_video.mp4")
        language = "en"
        status = "processing"
        progress = 50
        error_message = "Custom error"

        task = ProcessingTask(
            file_path=file_path,
            language=language,
            status=status,
            progress=progress,
            error_message=error_message
        )

        assert task.file_path == file_path
        assert task.language == language
        assert task.status == status
        assert task.progress == progress
        assert task.error_message == error_message

    def test_task_equality(self):
        """Test ProcessingTask equality comparison."""
        file_path = Path("test.mp4")
        language = "pt"

        task1 = ProcessingTask(file_path, language)
        task2 = ProcessingTask(file_path, language)

        # Tasks with same parameters should be equal
        assert task1 == task2

    def test_task_string_representation(self):
        """Test ProcessingTask string representation."""
        file_path = Path("test_video.mp4")
        language = "pt"

        task = ProcessingTask(file_path, language)

        str_repr = str(task)
        assert "test_video.mp4" in str_repr
        assert "pt" in str_repr
        assert "pending" in str_repr
