"""Progress display component for the CLI."""

import time
from typing import Any, Optional

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text


class ProgressDisplay:
    """Elegant progress display component."""

    def __init__(self, title: str, total: int = 100, theme: Any = None):
        """Initialize the progress display.

        Args:
            title: Title for the progress display
            total: Total progress value (default 100 for percentage)
            theme: Theme instance for styling
        """
        self.title = title
        self.total = total
        self.current = 0
        self.status = "Iniciando..."
        self.theme = theme
        self.console = Console()
        self.start_time = time.time()
        self.is_indeterminate = False

        # Create Rich Progress instance
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
            transient=False
        )

        # Add task to progress
        self.task_id = None

    def start(self) -> None:
        """Start the progress display."""
        self.progress.start()
        self.task_id = self.progress.add_task(
            description=self.title,
            total=self.total if not self.is_indeterminate else None
        )

    def stop(self) -> None:
        """Stop the progress display."""
        if self.progress.live.is_started:
            self.progress.stop()

    def update(self, progress: int, status: Optional[str] = None) -> None:
        """Update the progress.

        Args:
            progress: Current progress value
            status: Optional status message
        """
        self.current = progress
        if status:
            self.status = status

        if self.task_id is not None:
            if self.is_indeterminate:
                self.progress.update(self.task_id, description=f"{self.title}: {self.status}")
            else:
                self.progress.update(
                    self.task_id,
                    completed=progress,
                    description=f"{self.title}: {self.status}"
                )

    def set_indeterminate(self, indeterminate: bool = True) -> None:
        """Set progress to indeterminate mode (spinner only).

        Args:
            indeterminate: Whether to use indeterminate mode
        """
        self.is_indeterminate = indeterminate
        if self.task_id is not None:
            # Remove and re-add task with new total
            self.progress.remove_task(self.task_id)
            self.task_id = self.progress.add_task(
                description=f"{self.title}: {self.status}",
                total=None if indeterminate else self.total
            )

    def render(self) -> Panel:
        """Render the progress display as a Rich Panel.

        Returns:
            Rich Panel containing the progress display
        """
        # Create progress content
        content = Text()

        # Add title
        if self.theme:
            title_style = self.theme.get_style("progress_text")
        else:
            title_style = "bold blue"

        content.append(f"{self.title}\n", style=title_style)

        # Add status
        if self.theme:
            status_style = self.theme.get_style("text_secondary")
        else:
            status_style = "dim"

        content.append(f"Status: {self.status}\n", style=status_style)

        # Add progress bar
        if not self.is_indeterminate:
            # Calculate percentage
            percentage = (self.current / self.total * 100) if self.total > 0 else 0

            # Create visual progress bar
            bar_width = 40
            filled_width = int(bar_width * self.current / self.total) if self.total > 0 else 0

            # Progress bar characters
            filled_char = "█"
            empty_char = "░"

            progress_bar = Text()

            # Add filled portion
            if self.theme:
                filled_style = self.theme.get_style("progress_complete")
            else:
                filled_style = "green"
            progress_bar.append(filled_char * filled_width, style=filled_style)

            # Add empty portion
            if self.theme:
                empty_style = self.theme.get_style("progress_incomplete")
            else:
                empty_style = "dim"
            progress_bar.append(empty_char * (bar_width - filled_width), style=empty_style)

            content.append(progress_bar)

            # Add percentage
            if self.theme:
                percentage_style = self.theme.get_style("progress_percentage")
            else:
                percentage_style = "bold"
            content.append(f" {percentage:.1f}%", style=percentage_style)

            # Add progress numbers
            content.append(f" ({self.current}/{self.total})", style=status_style)
        else:
            # Indeterminate progress - just show spinner effect
            spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            spinner_index = int(time.time() * 10) % len(spinner_chars)
            spinner_char = spinner_chars[spinner_index]

            if self.theme:
                spinner_style = self.theme.get_style("progress_complete")
            else:
                spinner_style = "blue"
            content.append(f"{spinner_char} Processando...", style=spinner_style)

        # Add elapsed time
        elapsed = time.time() - self.start_time
        elapsed_text = f"\nTempo decorrido: {elapsed:.1f}s"
        content.append(elapsed_text, style=status_style)

        # Create panel
        border_style = self.theme.border_style if self.theme else "rounded"
        panel_border_style = self.theme.get_style("panel_border") if self.theme else "blue"

        return Panel(
            Align.center(content),
            border_style=border_style,
            style=panel_border_style,
            title="Progresso",
            title_align="center"
        )

    def complete(self, final_status: str = "Concluído!") -> None:
        """Mark progress as complete.

        Args:
            final_status: Final status message
        """
        if not self.is_indeterminate:
            self.current = self.total
        self.status = final_status

        if self.task_id is not None:
            if self.is_indeterminate:
                self.progress.update(self.task_id, description=f"{self.title}: {final_status}")
            else:
                self.progress.update(
                    self.task_id,
                    completed=self.total,
                    description=f"{self.title}: {final_status}"
                )

    def get_percentage(self) -> float:
        """Get current progress percentage.

        Returns:
            Progress percentage (0-100)
        """
        if self.is_indeterminate or self.total == 0:
            return 0.0
        return (self.current / self.total) * 100

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds.

        Returns:
            Elapsed time since creation
        """
        return time.time() - self.start_time

    def reset(self) -> None:
        """Reset the progress display."""
        self.current = 0
        self.status = "Iniciando..."
        self.start_time = time.time()

        if self.task_id is not None:
            self.progress.reset(self.task_id)


class MultiProgressDisplay:
    """Display multiple progress bars simultaneously."""

    def __init__(self, theme: Any = None):
        """Initialize multi-progress display.

        Args:
            theme: Theme instance for styling
        """
        self.theme = theme
        self.progress_displays = {}
        self.console = Console()

    def add_progress(self, key: str, title: str, total: int = 100) -> ProgressDisplay:
        """Add a new progress display.

        Args:
            key: Unique key for this progress
            title: Title for the progress display
            total: Total progress value

        Returns:
            Created ProgressDisplay instance
        """
        progress = ProgressDisplay(title, total, self.theme)
        self.progress_displays[key] = progress
        return progress

    def remove_progress(self, key: str) -> None:
        """Remove a progress display.

        Args:
            key: Key of progress to remove
        """
        if key in self.progress_displays:
            self.progress_displays[key].stop()
            del self.progress_displays[key]

    def get_progress(self, key: str) -> Optional[ProgressDisplay]:
        """Get a progress display by key.

        Args:
            key: Key of progress to get

        Returns:
            ProgressDisplay instance or None if not found
        """
        return self.progress_displays.get(key)

    def render_all(self) -> Panel:
        """Render all progress displays in a single panel.

        Returns:
            Rich Panel containing all progress displays
        """
        if not self.progress_displays:
            return Panel("Nenhum progresso ativo", title="Progresso")

        from rich.console import Group

        content_parts = []

        for i, (key, progress) in enumerate(self.progress_displays.items()):
            if i > 0:
                content_parts.append("─" * 50)

            # Get progress panel content (without the panel wrapper)
            progress_panel = progress.render()
            content_parts.append(progress_panel.renderable)

        border_style = self.theme.border_style if self.theme else "rounded"
        panel_border_style = self.theme.get_style("panel_border") if self.theme else "blue"

        return Panel(
            Group(*content_parts),
            border_style=border_style,
            style=panel_border_style,
            title="Progresso Múltiplo",
            title_align="center"
        )
