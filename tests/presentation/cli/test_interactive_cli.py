"""Tests for the InteractiveCLI navigation and state management."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.presentation.cli.interactive_cli import InteractiveCLI
from src.presentation.cli.screens.base_screen import Screen
from src.presentation.cli.state import CLIState, ProcessingTask
from src.presentation.cli.utils.keyboard import MockKeyboardHandler


class MockScreen(Screen):
    """Mock screen for testing."""

    def __init__(self, cli, name="MockScreen"):
        super().__init__(cli)
        self.name = name
        self.render_called = False
        self.handle_input_called = False
        self.on_enter_called = False
        self.on_exit_called = False
        self.last_key = None

    async def render(self):
        """Mock render method."""
        self.render_called = True

    async def handle_input(self, key: str):
        """Mock input handler."""
        self.handle_input_called = True
        self.last_key = key

    async def on_enter(self):
        """Mock on_enter method."""
        self.on_enter_called = True
        self.state.current_screen = self.name

    async def on_exit(self):
        """Mock on_exit method."""
        self.on_exit_called = True


class TestInteractiveCLI:
    """Test cases for InteractiveCLI."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app_context = MagicMock()
        self.cli = InteractiveCLI(self.app_context)

        # Replace keyboard handler with mock
        self.mock_keyboard = MockKeyboardHandler()
        self.cli.keyboard = self.mock_keyboard

    def test_initialization(self):
        """Test CLI initialization."""
        assert self.cli.app_context == self.app_context
        assert isinstance(self.cli.state, CLIState)
        assert self.cli.current_screen is None
        assert len(self.cli.screen_stack) == 0
        assert not self.cli.running

    @pytest.mark.asyncio
    async def test_navigate_to_screen(self):
        """Test navigation to a new screen."""
        screen1 = MockScreen(self.cli, "Screen1")
        screen2 = MockScreen(self.cli, "Screen2")

        # Navigate to first screen
        await self.cli.navigate_to(screen1)

        assert self.cli.current_screen == screen1
        assert len(self.cli.screen_stack) == 0
        assert screen1.on_enter_called
        assert self.cli.state.current_screen == "Screen1"

        # Navigate to second screen
        await self.cli.navigate_to(screen2)

        assert self.cli.current_screen == screen2
        assert len(self.cli.screen_stack) == 1
        assert self.cli.screen_stack[0] == screen1
        assert screen1.on_exit_called
        assert screen2.on_enter_called

    @pytest.mark.asyncio
    async def test_go_back_navigation(self):
        """Test going back to previous screen."""
        screen1 = MockScreen(self.cli, "Screen1")
        screen2 = MockScreen(self.cli, "Screen2")

        # Navigate to screens
        await self.cli.navigate_to(screen1)
        await self.cli.navigate_to(screen2)

        # Reset mock flags
        screen1.on_enter_called = False
        screen1.on_exit_called = False
        screen2.on_enter_called = False
        screen2.on_exit_called = False

        # Go back
        await self.cli.go_back()

        assert self.cli.current_screen == screen1
        assert len(self.cli.screen_stack) == 0
        assert screen2.on_exit_called
        assert screen1.on_enter_called

    @pytest.mark.asyncio
    async def test_go_back_from_root_screen(self):
        """Test going back when no previous screen exists."""
        screen1 = MockScreen(self.cli, "Screen1")

        await self.cli.navigate_to(screen1)

        # Go back from root screen should shutdown
        await self.cli.go_back()

        assert not self.cli.running
        assert screen1.on_exit_called

    @pytest.mark.asyncio
    async def test_esc_key_navigation(self):
        """Test ESC key triggers go_back."""
        screen1 = MockScreen(self.cli, "Screen1")
        screen2 = MockScreen(self.cli, "Screen2")

        await self.cli.navigate_to(screen1)
        await self.cli.navigate_to(screen2)

        # Simulate ESC key press
        handled = await self.cli._handle_global_keys(self.mock_keyboard.ESC)

        assert handled
        assert self.cli.current_screen == screen1
        assert len(self.cli.screen_stack) == 0

    @pytest.mark.asyncio
    async def test_f1_key_handling(self):
        """Test F1 key is handled globally."""
        handled = await self.cli._handle_global_keys(self.mock_keyboard.F1)
        assert handled

    @pytest.mark.asyncio
    async def test_ctrl_c_handling(self):
        """Test Ctrl+C triggers shutdown."""
        self.cli.running = True

        handled = await self.cli._handle_global_keys('\x03')  # Ctrl+C

        assert handled
        assert not self.cli.running

    def test_screen_stack_utilities(self):
        """Test screen stack utility methods."""
        screen1 = MockScreen(self.cli, "Screen1")
        screen2 = MockScreen(self.cli, "Screen2")

        # Test empty stack
        assert self.cli.get_screen_stack_depth() == 0
        assert self.cli.peek_previous_screen() is None

        # Add screens to stack
        self.cli.screen_stack.append(screen1)
        self.cli.screen_stack.append(screen2)

        assert self.cli.get_screen_stack_depth() == 2
        assert self.cli.peek_previous_screen() == screen2

        # Clear stack
        self.cli.clear_screen_stack()
        assert self.cli.get_screen_stack_depth() == 0

    @pytest.mark.asyncio
    async def test_shutdown_process(self):
        """Test graceful shutdown process."""
        screen1 = MockScreen(self.cli, "Screen1")
        self.cli.current_screen = screen1
        self.cli.running = True

        # Mock live display
        self.cli.live_display = MagicMock()

        await self.cli._shutdown()

        assert not self.cli.running
        assert screen1.on_exit_called
        assert self.cli.live_display.stop.called

    def test_update_live_display(self):
        """Test live display update."""
        mock_content = "test content"
        self.cli.live_display = MagicMock()

        self.cli.update_live_display(mock_content)

        self.cli.live_display.update.assert_called_once_with(mock_content)

    def test_update_live_display_no_display(self):
        """Test live display update when no display exists."""
        # Should not raise an error
        self.cli.update_live_display("test content")


class TestCLIState:
    """Test cases for CLIState."""

    def setup_method(self):
        """Setup test fixtures."""
        self.state = CLIState()

    def test_initialization(self):
        """Test state initialization."""
        assert self.state.current_screen == "main_menu"
        assert len(self.state.previous_screens) == 0
        assert len(self.state.recent_files) == 0
        assert len(self.state.processing_queue) == 0
        assert len(self.state.last_results) == 0
        assert self.state.selected_language == "pt"
        assert self.state.selected_whisper_model == "base"
        assert not self.state.is_processing

    def test_add_recent_file(self):
        """Test adding recent files."""
        from pathlib import Path

        file1 = Path("test1.mp4")
        file2 = Path("test2.mp4")

        self.state.add_recent_file(file1)
        assert len(self.state.recent_files) == 1
        assert self.state.recent_files[0] == file1

        self.state.add_recent_file(file2)
        assert len(self.state.recent_files) == 2
        assert self.state.recent_files[0] == file2  # Most recent first

        # Add same file again - should move to front
        self.state.add_recent_file(file1)
        assert len(self.state.recent_files) == 2
        assert self.state.recent_files[0] == file1

    def test_recent_files_limit(self):
        """Test recent files list is limited to 10 items."""
        from pathlib import Path

        # Add 15 files
        for i in range(15):
            self.state.add_recent_file(Path(f"test{i}.mp4"))

        # Should only keep the last 10
        assert len(self.state.recent_files) == 10
        assert self.state.recent_files[0] == Path("test14.mp4")  # Most recent
        assert self.state.recent_files[-1] == Path("test5.mp4")  # Oldest kept

    def test_processing_task_management(self):
        """Test processing task management."""
        from pathlib import Path

        file_path = Path("test.mp4")
        language = "en"

        # Add task
        task = self.state.add_processing_task(file_path, language)

        assert task.file_path == file_path
        assert task.language == language
        assert task.status == "pending"
        assert task.progress == 0
        assert len(self.state.processing_queue) == 1

        # Update progress
        self.state.update_task_progress(task, 50, "processing")
        assert task.progress == 50
        assert task.status == "processing"

        # Complete task
        self.state.complete_task(task)
        assert task.status == "completed"
        assert task.progress == 100

        # Fail task
        task2 = self.state.add_processing_task(Path("test2.mp4"), "pt")
        self.state.fail_task(task2, "Test error")
        assert task2.status == "failed"
        assert task2.error_message == "Test error"

    def test_task_filtering(self):
        """Test task filtering methods."""
        from pathlib import Path

        # Create tasks with different statuses
        task1 = self.state.add_processing_task(Path("test1.mp4"), "en")
        task2 = self.state.add_processing_task(Path("test2.mp4"), "pt")
        task3 = self.state.add_processing_task(Path("test3.mp4"), "es")

        self.state.complete_task(task1)
        self.state.fail_task(task2, "Error")
        # task3 remains pending

        pending_tasks = self.state.get_pending_tasks()
        completed_tasks = self.state.get_completed_tasks()
        failed_tasks = self.state.get_failed_tasks()

        assert len(pending_tasks) == 1
        assert pending_tasks[0] == task3

        assert len(completed_tasks) == 1
        assert completed_tasks[0] == task1

        assert len(failed_tasks) == 1
        assert failed_tasks[0] == task2

    def test_clear_completed_tasks(self):
        """Test clearing completed tasks."""
        from pathlib import Path

        task1 = self.state.add_processing_task(Path("test1.mp4"), "en")
        task2 = self.state.add_processing_task(Path("test2.mp4"), "pt")

        self.state.complete_task(task1)
        # task2 remains pending

        assert len(self.state.processing_queue) == 2

        self.state.clear_completed_tasks()

        assert len(self.state.processing_queue) == 1
        assert self.state.processing_queue[0] == task2

    def test_settings_management(self):
        """Test settings management."""
        # Test setting and getting values
        self.state.update_setting("test_key", "test_value")
        assert self.state.get_setting("test_key") == "test_value"

        # Test default value
        assert self.state.get_setting("nonexistent_key", "default") == "default"
        assert self.state.get_setting("nonexistent_key") is None


class TestProcessingTask:
    """Test cases for ProcessingTask."""

    def test_initialization(self):
        """Test task initialization."""
        from pathlib import Path

        file_path = Path("test.mp4")
        language = "en"

        task = ProcessingTask(file_path, language)

        assert task.file_path == file_path
        assert task.language == language
        assert task.status == "pending"
        assert task.progress == 0
        assert task.error_message is None


class TestNavigationIntegration:
    """Integration tests for navigation system."""

    def setup_method(self):
        """Setup test fixtures."""
        self.app_context = MagicMock()
        self.cli = InteractiveCLI(self.app_context)
        self.mock_keyboard = MockKeyboardHandler()
        self.cli.keyboard = self.mock_keyboard

    @pytest.mark.asyncio
    async def test_complex_navigation_flow(self):
        """Test complex navigation scenarios."""
        screen1 = MockScreen(self.cli, "MainMenu")
        screen2 = MockScreen(self.cli, "Settings")
        screen3 = MockScreen(self.cli, "LanguageSettings")

        # Navigate through multiple screens
        await self.cli.navigate_to(screen1)
        await self.cli.navigate_to(screen2)
        await self.cli.navigate_to(screen3)

        assert self.cli.get_screen_stack_depth() == 2
        assert self.cli.current_screen == screen3

        # Go back twice
        await self.cli.go_back()
        assert self.cli.current_screen == screen2
        assert self.cli.get_screen_stack_depth() == 1

        await self.cli.go_back()
        assert self.cli.current_screen == screen1
        assert self.cli.get_screen_stack_depth() == 0

        # Go back from root should shutdown
        await self.cli.go_back()
        assert not self.cli.running

    @pytest.mark.asyncio
    async def test_state_persistence_during_navigation(self):
        """Test that state persists during navigation."""
        from pathlib import Path

        screen1 = MockScreen(self.cli, "Screen1")
        screen2 = MockScreen(self.cli, "Screen2")

        # Add some state data
        self.cli.state.add_recent_file(Path("test.mp4"))
        self.cli.state.update_setting("test_setting", "test_value")

        # Navigate between screens
        await self.cli.navigate_to(screen1)
        await self.cli.navigate_to(screen2)
        await self.cli.go_back()

        # State should persist
        assert len(self.cli.state.recent_files) == 1
        assert self.cli.state.get_setting("test_setting") == "test_value"

    @pytest.mark.asyncio
    async def test_screen_lifecycle_during_navigation(self):
        """Test screen lifecycle methods are called correctly."""
        screen1 = MockScreen(self.cli, "Screen1")
        screen2 = MockScreen(self.cli, "Screen2")

        # Navigate to first screen
        await self.cli.navigate_to(screen1)
        assert screen1.on_enter_called
        assert not screen1.on_exit_called

        # Navigate to second screen
        screen1.on_enter_called = False
        screen1.on_exit_called = False

        await self.cli.navigate_to(screen2)
        assert screen1.on_exit_called
        assert screen2.on_enter_called
        assert not screen2.on_exit_called

        # Go back
        screen1.on_enter_called = False
        screen2.on_exit_called = False

        await self.cli.go_back()
        assert screen2.on_exit_called
        assert screen1.on_enter_called
