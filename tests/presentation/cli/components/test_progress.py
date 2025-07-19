"""Tests for the ProgressDisplay component."""

import time
from unittest.mock import Mock, patch

import pytest

from src.presentation.cli.components.progress import (
    MultiProgressDisplay,
    ProgressDisplay,
)
from src.presentation.cli.themes.default_theme import DefaultTheme


class TestProgressDisplay:
    """Tests for ProgressDisplay component."""

    @pytest.fixture
    def theme(self):
        """Create a theme for testing."""
        return DefaultTheme()

    @pytest.fixture
    def progress(self, theme):
        """Create a progress display for testing."""
        return ProgressDisplay("Test Progress", 100, theme)

    def test_progress_initialization(self, progress):
        """Test progress display initialization."""
        assert progress.title == "Test Progress"
        assert progress.total == 100
        assert progress.current == 0
        assert progress.status == "Iniciando..."
        assert progress.is_indeterminate is False

    def test_progress_initialization_defaults(self):
        """Test progress display with default values."""
        progress = ProgressDisplay("Test")

        assert progress.title == "Test"
        assert progress.total == 100
        assert progress.current == 0
        assert progress.theme is None

    def test_update_progress(self, progress):
        """Test updating progress value."""
        progress.update(50, "Meio caminho")

        assert progress.current == 50
        assert progress.status == "Meio caminho"

    def test_update_progress_without_status(self, progress):
        """Test updating progress without changing status."""
        original_status = progress.status
        progress.update(25)

        assert progress.current == 25
        assert progress.status == original_status

    def test_render_returns_panel(self, progress):
        """Test that render returns a Rich Panel."""
        panel = progress.render()
        assert hasattr(panel, 'renderable')  # Rich Panel has renderable attribute

    def test_render_with_progress(self, progress):
        """Test rendering with some progress."""
        progress.update(75, "Quase lá")
        panel = progress.render()

        assert panel is not None
        # Panel should contain progress information

    def test_render_indeterminate(self, progress):
        """Test rendering in indeterminate mode."""
        progress.set_indeterminate(True)
        panel = progress.render()

        assert panel is not None
        assert progress.is_indeterminate is True

    def test_set_indeterminate(self, progress):
        """Test setting indeterminate mode."""
        progress.set_indeterminate(True)
        assert progress.is_indeterminate is True

        progress.set_indeterminate(False)
        assert progress.is_indeterminate is False

    def test_complete_progress(self, progress):
        """Test completing progress."""
        progress.complete("Finalizado!")

        assert progress.current == progress.total
        assert progress.status == "Finalizado!"

    def test_complete_indeterminate_progress(self, progress):
        """Test completing indeterminate progress."""
        progress.set_indeterminate(True)
        original_current = progress.current

        progress.complete("Finalizado!")

        # Current should not change for indeterminate
        assert progress.current == original_current
        assert progress.status == "Finalizado!"

    def test_get_percentage(self, progress):
        """Test getting progress percentage."""
        progress.update(25)
        assert progress.get_percentage() == 25.0

        progress.update(50)
        assert progress.get_percentage() == 50.0

        progress.update(100)
        assert progress.get_percentage() == 100.0

    def test_get_percentage_zero_total(self):
        """Test getting percentage with zero total."""
        progress = ProgressDisplay("Test", 0)
        assert progress.get_percentage() == 0.0

    def test_get_percentage_indeterminate(self, progress):
        """Test getting percentage in indeterminate mode."""
        progress.set_indeterminate(True)
        assert progress.get_percentage() == 0.0

    def test_get_elapsed_time(self, progress):
        """Test getting elapsed time."""
        start_time = time.time()
        elapsed = progress.get_elapsed_time()

        # Should be close to 0 since just created
        assert elapsed >= 0
        assert elapsed < 1  # Should be less than 1 second

    def test_reset_progress(self, progress):
        """Test resetting progress."""
        progress.update(50, "Meio caminho")
        original_start_time = progress.start_time

        # Wait a tiny bit to ensure time difference
        time.sleep(0.01)

        progress.reset()

        assert progress.current == 0
        assert progress.status == "Iniciando..."
        assert progress.start_time > original_start_time

    @patch('src.presentation.cli.components.progress.time.time')
    def test_render_with_mocked_time(self, mock_time, progress):
        """Test render with mocked time for consistent testing."""
        mock_time.return_value = 1000.0
        progress.start_time = 995.0  # 5 seconds ago

        panel = progress.render()
        assert panel is not None

    def test_start_and_stop(self, progress):
        """Test starting and stopping progress."""
        # These methods interact with Rich Progress
        # We mainly test they don't crash
        progress.start()
        assert progress.task_id is not None

        progress.stop()
        # Should not crash

    def test_progress_with_no_theme(self):
        """Test progress display without theme."""
        progress = ProgressDisplay("Test", 100, None)

        # Should not crash
        panel = progress.render()
        assert panel is not None

        progress.update(50, "Test status")
        panel = progress.render()
        assert panel is not None


class TestMultiProgressDisplay:
    """Tests for MultiProgressDisplay component."""

    @pytest.fixture
    def theme(self):
        """Create a theme for testing."""
        return DefaultTheme()

    @pytest.fixture
    def multi_progress(self, theme):
        """Create a multi-progress display for testing."""
        return MultiProgressDisplay(theme)

    def test_multi_progress_initialization(self, multi_progress):
        """Test multi-progress display initialization."""
        assert len(multi_progress.progress_displays) == 0

    def test_add_progress(self, multi_progress):
        """Test adding a progress display."""
        progress = multi_progress.add_progress("test1", "Test Progress 1", 100)

        assert isinstance(progress, ProgressDisplay)
        assert "test1" in multi_progress.progress_displays
        assert multi_progress.progress_displays["test1"] == progress

    def test_get_progress(self, multi_progress):
        """Test getting a progress display."""
        added_progress = multi_progress.add_progress("test1", "Test Progress 1", 100)
        retrieved_progress = multi_progress.get_progress("test1")

        assert retrieved_progress == added_progress

    def test_get_nonexistent_progress(self, multi_progress):
        """Test getting a non-existent progress display."""
        result = multi_progress.get_progress("nonexistent")
        assert result is None

    def test_remove_progress(self, multi_progress):
        """Test removing a progress display."""
        multi_progress.add_progress("test1", "Test Progress 1", 100)
        assert "test1" in multi_progress.progress_displays

        multi_progress.remove_progress("test1")
        assert "test1" not in multi_progress.progress_displays

    def test_remove_nonexistent_progress(self, multi_progress):
        """Test removing a non-existent progress display."""
        # Should not crash
        multi_progress.remove_progress("nonexistent")

    def test_render_all_empty(self, multi_progress):
        """Test rendering when no progress displays exist."""
        panel = multi_progress.render_all()
        assert panel is not None

    def test_render_all_with_progress(self, multi_progress):
        """Test rendering with multiple progress displays."""
        progress1 = multi_progress.add_progress("test1", "Progress 1", 100)
        progress2 = multi_progress.add_progress("test2", "Progress 2", 50)

        progress1.update(25, "First quarter")
        progress2.update(10, "Getting started")

        panel = multi_progress.render_all()
        assert panel is not None

    def test_multi_progress_without_theme(self):
        """Test multi-progress display without theme."""
        multi_progress = MultiProgressDisplay(None)

        # Should not crash
        progress = multi_progress.add_progress("test", "Test", 100)
        assert progress is not None

        panel = multi_progress.render_all()
        assert panel is not None

    def test_multiple_operations(self, multi_progress):
        """Test multiple operations on multi-progress display."""
        # Add multiple progress displays
        progress1 = multi_progress.add_progress("download", "Download", 100)
        progress2 = multi_progress.add_progress("process", "Process", 200)
        progress3 = multi_progress.add_progress("upload", "Upload", 150)

        # Update them
        progress1.update(50, "Downloading...")
        progress2.update(75, "Processing...")
        progress3.update(100, "Uploading...")

        # Render
        panel = multi_progress.render_all()
        assert panel is not None

        # Remove one
        multi_progress.remove_progress("process")
        assert len(multi_progress.progress_displays) == 2

        # Render again
        panel = multi_progress.render_all()
        assert panel is not None
        # Render again
        panel = multi_progress.render_all()
        assert panel is not None
