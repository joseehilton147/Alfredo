"""CLI state management for the interactive interface."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...domain.entities.video import Video

# Type alias for transcription results (will be replaced with actual entity later)
TranscriptionResult = Any


@dataclass
class ProcessingTask:
    """Represents a processing task in the queue."""

    file_path: Path
    language: str
    status: str = "pending"  # pending, processing, completed, failed
    progress: int = 0
    error_message: Optional[str] = None


@dataclass
class CLIState:
    """Global state management for the CLI application."""

    # Navigation state
    current_screen: str = "main_menu"
    previous_screens: List[str] = field(default_factory=list)

    # Application settings
    settings: Dict[str, Any] = field(default_factory=dict)

    # User data
    recent_files: List[Path] = field(default_factory=list)
    processing_queue: List[ProcessingTask] = field(default_factory=list)
    last_results: List[TranscriptionResult] = field(default_factory=list)

    # UI state
    selected_language: str = "pt"
    selected_whisper_model: str = "base"
    output_directory: Optional[Path] = None

    # Runtime state
    is_processing: bool = False
    current_operation: Optional[str] = None

    def add_recent_file(self, file_path: Path) -> None:
        """Add a file to the recent files list.

        Args:
            file_path: Path to the file to add
        """
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)

        # Keep only the last 10 recent files
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]

    def add_processing_task(self, file_path: Path, language: str) -> ProcessingTask:
        """Add a new processing task to the queue.

        Args:
            file_path: Path to the file to process
            language: Language for transcription

        Returns:
            The created processing task
        """
        task = ProcessingTask(file_path=file_path, language=language)
        self.processing_queue.append(task)
        return task

    def update_task_progress(self, task: ProcessingTask, progress: int, status: str = None) -> None:
        """Update the progress of a processing task.

        Args:
            task: The task to update
            progress: Progress percentage (0-100)
            status: Optional status update
        """
        task.progress = progress
        if status:
            task.status = status

    def complete_task(self, task: ProcessingTask, result: Optional[TranscriptionResult] = None) -> None:
        """Mark a task as completed.

        Args:
            task: The task to complete
            result: Optional transcription result
        """
        task.status = "completed"
        task.progress = 100

        if result:
            self.last_results.insert(0, result)
            # Keep only the last 50 results
            if len(self.last_results) > 50:
                self.last_results = self.last_results[:50]

    def fail_task(self, task: ProcessingTask, error_message: str) -> None:
        """Mark a task as failed.

        Args:
            task: The task that failed
            error_message: Error description
        """
        task.status = "failed"
        task.error_message = error_message

    def get_pending_tasks(self) -> List[ProcessingTask]:
        """Get all pending processing tasks.

        Returns:
            List of pending tasks
        """
        return [task for task in self.processing_queue if task.status == "pending"]

    def get_completed_tasks(self) -> List[ProcessingTask]:
        """Get all completed processing tasks.

        Returns:
            List of completed tasks
        """
        return [task for task in self.processing_queue if task.status == "completed"]

    def get_failed_tasks(self) -> List[ProcessingTask]:
        """Get all failed processing tasks.

        Returns:
            List of failed tasks
        """
        return [task for task in self.processing_queue if task.status == "failed"]

    def clear_completed_tasks(self) -> None:
        """Remove all completed tasks from the queue."""
        self.processing_queue = [
            task for task in self.processing_queue
            if task.status != "completed"
        ]

    def update_setting(self, key: str, value: Any) -> None:
        """Update a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
