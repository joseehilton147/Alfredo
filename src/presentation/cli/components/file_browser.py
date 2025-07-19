"""Interactive file browser component for the CLI."""

import os
from pathlib import Path
from typing import List, Optional, Set, Tuple

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class FileExplorer:
    """Interactive file browser with video file filtering."""

    # Supported video file extensions
    SUPPORTED_VIDEO_EXTENSIONS = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
        '.MP4', '.AVI', '.MKV', '.MOV', '.WMV', '.FLV', '.WEBM'
    }

    def __init__(self, initial_path: Optional[Path] = None, theme: Optional[object] = None):
        """Initialize the file explorer.

        Args:
            initial_path: Starting directory path
            theme: Theme instance for styling
        """
        self.current_path = Path(initial_path or Path.cwd())
        self.theme = theme
        self.selected_index = 0
        self.console = Console()
        self._entries: List[Tuple[Path, bool, str]] = []  # (path, is_dir, display_name)
        self._refresh_entries()

    def _refresh_entries(self) -> None:
        """Refresh the list of entries in the current directory."""
        self._entries = []

        try:
            # Add parent directory entry if not at root
            if self.current_path.parent != self.current_path:
                self._entries.append((self.current_path.parent, True, ".."))

            # Get all entries in current directory
            entries = []
            for entry in self.current_path.iterdir():
                if entry.is_dir():
                    entries.append((entry, True, entry.name))
                elif self._is_supported_video(entry):
                    entries.append((entry, False, entry.name))

            # Sort: directories first, then files, both alphabetically
            entries.sort(key=lambda x: (not x[1], x[2].lower()))
            self._entries.extend(entries)

        except (PermissionError, OSError) as e:
            # Handle permission errors gracefully
            self._entries = [(self.current_path.parent, True, ".. (Erro de acesso)")]

        # Reset selection if it's out of bounds
        if self.selected_index >= len(self._entries):
            self.selected_index = 0

    def _is_supported_video(self, path: Path) -> bool:
        """Check if a file is a supported video format.

        Args:
            path: Path to check

        Returns:
            True if the file is a supported video format
        """
        return path.suffix in self.SUPPORTED_VIDEO_EXTENSIONS

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _get_file_info(self, path: Path) -> Tuple[str, str]:
        """Get file information (size and type).

        Args:
            path: Path to get info for

        Returns:
            Tuple of (size_str, type_str)
        """
        try:
            if path.is_dir():
                # Count items in directory
                try:
                    item_count = len(list(path.iterdir()))
                    return f"{item_count} itens", "Pasta"
                except (PermissionError, OSError):
                    return "---", "Pasta"
            else:
                # Get file size
                size = path.stat().st_size
                size_str = self._format_file_size(size)
                return size_str, "Vídeo"
        except (PermissionError, OSError):
            return "---", "Arquivo"

    def render(self) -> Panel:
        """Render the file browser as a Rich Panel.

        Returns:
            Rich Panel containing the file browser
        """
        # Create table for file listing
        table = Table(show_header=True, header_style="bold")
        table.add_column("", width=2)  # Selection indicator
        table.add_column("Nome", min_width=30)
        table.add_column("Tamanho", width=10, justify="right")
        table.add_column("Tipo", width=8)

        # Add entries to table
        for i, (path, is_dir, display_name) in enumerate(self._entries):
            # Selection indicator
            indicator = "▶" if i == self.selected_index else " "

            # Style based on selection and type
            if i == self.selected_index:
                if self.theme:
                    name_style = self.theme.get_style("file_selected")
                else:
                    name_style = "bold green"
            elif is_dir:
                if self.theme:
                    name_style = self.theme.get_style("file_directory")
                else:
                    name_style = "bold blue"
            else:
                if self.theme:
                    name_style = self.theme.get_style("file_regular")
                else:
                    name_style = "white"

            # Get file info
            size_str, type_str = self._get_file_info(path)

            # Add icon based on type
            if display_name == "..":
                icon = "📁"
                display_name = ".. (Voltar)"
            elif is_dir:
                icon = "📁"
            else:
                icon = "🎬"

            # Create name with icon
            name_text = Text()
            name_text.append(icon + " ")
            name_text.append(display_name, style=name_style)

            table.add_row(
                indicator,
                name_text,
                size_str,
                type_str
            )

        # Create content with current path header
        path_text = Text()
        path_text.append("📍 Localização: ", style="bold")
        path_text.append(str(self.current_path), style="cyan")

        # Create help text
        help_text = Text()
        help_text.append("↑↓ Navegar  ", style="dim")
        help_text.append("Enter Selecionar/Entrar  ", style="dim")
        help_text.append("ESC Voltar", style="dim")

        # Create a group with all content
        from rich.console import Group
        content = Group(
            path_text,
            "",  # Empty line
            table,
            "",  # Empty line
            help_text
        )

        # Create panel
        title = "🗂️  Navegador de Arquivos"
        return Panel(
            content,
            title=title,
            border_style=self.theme.border_style if self.theme else "rounded",
            title_align="left"
        )

    def handle_key(self, key: str) -> Optional[Path]:
        """Handle keyboard input and return selected path if any.

        Args:
            key: The pressed key

        Returns:
            Selected Path if Enter was pressed on a file, None otherwise
        """
        if key == "up" or key == "k":
            self._move_selection(-1)
        elif key == "down" or key == "j":
            self._move_selection(1)
        elif key == "enter" or key == " ":
            return self._handle_selection()
        elif key == "h" or key == "left":
            # Go to parent directory
            self._navigate_to_parent()

        return None

    def _move_selection(self, direction: int) -> None:
        """Move selection up or down.

        Args:
            direction: -1 for up, 1 for down
        """
        if not self._entries:
            return

        self.selected_index = (self.selected_index + direction) % len(self._entries)

    def _handle_selection(self) -> Optional[Path]:
        """Handle selection of current item.

        Returns:
            Selected file path if it's a video file, None otherwise
        """
        if not self._entries or self.selected_index >= len(self._entries):
            return None

        selected_path, is_dir, display_name = self._entries[self.selected_index]

        if is_dir:
            # Navigate to directory
            self.navigate_to(selected_path)
            return None
        else:
            # Return selected file
            return selected_path

    def _navigate_to_parent(self) -> None:
        """Navigate to parent directory."""
        if self.current_path.parent != self.current_path:
            self.navigate_to(self.current_path.parent)

    def navigate_to(self, path: Path) -> bool:
        """Navigate to a specific directory.

        Args:
            path: Directory path to navigate to

        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            if path.is_dir() and path.exists():
                self.current_path = path.resolve()
                self.selected_index = 0
                self._refresh_entries()
                return True
        except (PermissionError, OSError):
            pass

        return False

    def get_current_path(self) -> Path:
        """Get the current directory path.

        Returns:
            Current directory path
        """
        return self.current_path

    def get_selected_entry(self) -> Optional[Tuple[Path, bool]]:
        """Get the currently selected entry.

        Returns:
            Tuple of (path, is_directory) or None if no selection
        """
        if not self._entries or self.selected_index >= len(self._entries):
            return None

        path, is_dir, _ = self._entries[self.selected_index]
        return (path, is_dir)

    def get_video_files_in_current_dir(self) -> List[Path]:
        """Get all video files in the current directory.

        Returns:
            List of video file paths
        """
        video_files = []
        for path, is_dir, _ in self._entries:
            if not is_dir and self._is_supported_video(path):
                video_files.append(path)
        return video_files

    def has_video_files(self) -> bool:
        """Check if current directory has any video files.

        Returns:
            True if there are video files in current directory
        """
        return len(self.get_video_files_in_current_dir()) > 0

    def get_entry_count(self) -> int:
        """Get the number of entries in current directory.

        Returns:
            Number of entries
        """
        return len(self._entries)

    def set_selected_index(self, index: int) -> None:
        """Set the selected index.

        Args:
            index: Index to select
        """
        if 0 <= index < len(self._entries):
            self.selected_index = index
