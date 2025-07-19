"""Utilities for consistent theme application across the CLI."""

from typing import Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from .base_theme import Theme
from .default_theme import DefaultTheme


class ThemeManager:
    """Manages theme application across the CLI."""

    def __init__(self, theme: Optional[Theme] = None):
        """Initialize with a theme (defaults to DefaultTheme)."""
        self.theme = theme or DefaultTheme()
        self.console = Console()

    def get_theme(self) -> Theme:
        """Get the current theme."""
        return self.theme

    def set_theme(self, theme: Theme) -> None:
        """Set a new theme."""
        self.theme = theme

    def create_styled_text(
        self,
        text: str,
        style_name: str,
        state: str = "normal"
    ) -> Text:
        """Create styled text using the current theme."""
        style = self.theme.get_style(style_name, state)
        return Text(text, style=style)

    def create_panel(
        self,
        content: Union[str, Text],
        title: Optional[str] = None,
        border_style: Optional[str] = None
    ) -> Panel:
        """Create a themed panel."""
        border_style = border_style or self.theme.border_style

        panel = Panel(
            content,
            title=title,
            border_style=border_style,
            title_align="left"
        )

        # Apply theme colors to the panel
        if hasattr(panel, 'border_style'):
            panel.border_style = self.theme.get_style("panel_border")

        return panel

    def create_menu_table(self, title: str, options: list) -> Table:
        """Create a themed table for menu display."""
        table = Table(
            title=title,
            show_header=False,
            show_lines=False,
            padding=(0, 1),
            border_style=self.theme.border_color
        )

        table.add_column("Icon", width=3, style=self.theme.get_style("menu_option"))
        table.add_column("Option", style=self.theme.get_style("menu_option"))
        table.add_column("Shortcut", width=8, style=self.theme.get_style("text_secondary"))

        return table

    def create_progress_bar(
        self,
        description: str = "Processing..."
    ) -> Progress:
        """Create a themed progress bar."""
        return Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(
                complete_style=self.theme.success_color,
                finished_style=self.theme.success_color
            ),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        )

    def print_status(
        self,
        message: str,
        status_type: str = "info",
        prefix: str = None
    ) -> None:
        """Print a status message with appropriate styling."""
        style_name = f"status_{status_type}"
        styled_text = self.create_styled_text(message, style_name)

        if prefix:
            prefix_style = self.theme.get_style("text_highlight")
            prefix_text = Text(f"[{prefix}] ", style=prefix_style)
            styled_text = prefix_text + styled_text

        self.console.print(styled_text)

    def print_error(self, message: str, prefix: str = "ERROR") -> None:
        """Print an error message."""
        self.print_status(message, "error", prefix)

    def print_success(self, message: str, prefix: str = "SUCCESS") -> None:
        """Print a success message."""
        self.print_status(message, "success", prefix)

    def print_warning(self, message: str, prefix: str = "WARNING") -> None:
        """Print a warning message."""
        self.print_status(message, "warning", prefix)

    def print_info(self, message: str, prefix: str = "INFO") -> None:
        """Print an info message."""
        self.print_status(message, "info", prefix)


class StyleHelper:
    """Helper functions for creating consistent styles."""

    @staticmethod
    def create_menu_option_style(
        theme: Theme,
        selected: bool = False,
        disabled: bool = False
    ) -> Style:
        """Create style for menu options."""
        if disabled:
            return theme.get_style("menu_option", "disabled")
        elif selected:
            return theme.get_style("menu_option", "selected")
        else:
            return theme.get_style("menu_option", "normal")

    @staticmethod
    def create_file_style(
        theme: Theme,
        is_directory: bool = False,
        selected: bool = False
    ) -> Style:
        """Create style for file browser items."""
        if selected:
            return theme.get_style("file", "selected")
        elif is_directory:
            return theme.get_style("file_directory")
        else:
            return theme.get_style("file_regular")

    @staticmethod
    def create_input_style(
        theme: Theme,
        focused: bool = False,
        error: bool = False
    ) -> Style:
        """Create style for input fields."""
        if error:
            return theme.get_style("input", "error")
        elif focused:
            return theme.get_style("input", "focused")
        else:
            return theme.get_style("input", "normal")


class ThemePresets:
    """Predefined theme configurations."""

    @staticmethod
    def get_default_theme() -> DefaultTheme:
        """Get the default Claude Code-inspired theme."""
        return DefaultTheme()

    @staticmethod
    def get_high_contrast_theme() -> DefaultTheme:
        """Get a high contrast version of the default theme."""
        theme = DefaultTheme()
        # Enhance contrast for accessibility
        theme.text_color = "#ffffff"
        theme.background_color = "#000000"
        theme.selected_color = "#00ff00"
        theme.error_color = "#ff0000"
        theme.success_color = "#00ff00"
        theme.warning_color = "#ffff00"
        return theme

    @staticmethod
    def get_minimal_theme() -> DefaultTheme:
        """Get a minimal monochrome theme."""
        theme = DefaultTheme()
        # Use minimal colors
        theme.primary_color = "#ffffff"
        theme.secondary_color = "#cccccc"
        theme.accent_color = "#888888"
        theme.selected_color = "#ffffff"
        return theme
