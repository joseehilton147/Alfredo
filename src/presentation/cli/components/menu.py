"""Interactive menu component for the CLI."""

from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


@dataclass
class MenuOption:
    """Represents a menu option."""
    key: str
    label: str
    description: str
    icon: str
    action: Callable[[], Any]
    enabled: bool = True
    shortcut: Optional[str] = None


class InteractiveMenu:
    """Interactive menu component with keyboard navigation."""

    def __init__(self, title: str, options: List[MenuOption], theme: Any):
        """Initialize the interactive menu.

        Args:
            title: Menu title
            options: List of menu options
            theme: Theme instance for styling
        """
        self.title = title
        self.options = options
        self.theme = theme
        self.selected_index = 0
        self.console = Console()

    def render(self) -> Panel:
        """Render the menu as a Rich Panel.

        Returns:
            Rich Panel containing the rendered menu
        """
        # Create menu content
        menu_content = Text()

        # Add title
        title_text = Text(self.title, style=self.theme.get_style("menu_title"))
        menu_content.append(title_text)
        menu_content.append("\n\n")

        # Add options
        for i, option in enumerate(self.options):
            # Determine style based on selection and enabled state
            if not option.enabled:
                style = self.theme.get_style("menu_option_disabled")
                prefix = "  "
            elif i == self.selected_index:
                style = self.theme.get_style("menu_option_selected")
                prefix = "▶ "
            else:
                style = self.theme.get_style("menu_option")
                prefix = "  "

            # Create option line
            option_line = Text()
            option_line.append(prefix, style=style)
            option_line.append(option.icon + " ", style=style)
            option_line.append(option.label, style=style)

            # Add shortcut if available
            if option.shortcut:
                option_line.append(f" ({option.shortcut})",
                                 style=self.theme.get_style("text_secondary"))

            menu_content.append(option_line)
            menu_content.append("\n")

            # Add description for selected item
            if i == self.selected_index and option.description:
                desc_text = Text(f"    {option.description}",
                               style=self.theme.get_style("text_secondary"))
                menu_content.append(desc_text)
                menu_content.append("\n")

        # Add navigation help
        help_text = Text("\n")
        help_text.append("↑↓ Navegar  ", style=self.theme.get_style("text_secondary"))
        help_text.append("Enter Selecionar  ", style=self.theme.get_style("text_secondary"))
        help_text.append("ESC Voltar", style=self.theme.get_style("text_secondary"))
        menu_content.append(help_text)

        # Create panel
        return Panel(
            Align.center(menu_content),
            border_style=self.theme.border_style,
            style=self.theme.get_style("panel_border"),
            title_align="center"
        )

    def handle_key(self, key: str) -> Optional[MenuOption]:
        """Handle keyboard input and return selected option if any.

        Args:
            key: The pressed key

        Returns:
            Selected MenuOption if Enter was pressed, None otherwise
        """
        if key == "up" or key == "k":
            self._move_selection(-1)
        elif key == "down" or key == "j":
            self._move_selection(1)
        elif key == "enter" or key == " ":
            return self._get_selected_option()
        elif key.isdigit():
            # Handle numeric shortcuts
            index = int(key) - 1
            if 0 <= index < len(self.options) and self.options[index].enabled:
                self.selected_index = index
                return self.options[index]
        else:
            # Handle letter shortcuts
            for i, option in enumerate(self.options):
                if option.shortcut and option.shortcut.lower() == key.lower() and option.enabled:
                    self.selected_index = i
                    return option

        return None

    def _move_selection(self, direction: int) -> None:
        """Move selection up or down.

        Args:
            direction: -1 for up, 1 for down
        """
        enabled_indices = [i for i, opt in enumerate(self.options) if opt.enabled]
        if not enabled_indices:
            return

        current_pos = enabled_indices.index(self.selected_index) if self.selected_index in enabled_indices else 0
        new_pos = (current_pos + direction) % len(enabled_indices)
        self.selected_index = enabled_indices[new_pos]

    def _get_selected_option(self) -> Optional[MenuOption]:
        """Get the currently selected option if it's enabled.

        Returns:
            Selected MenuOption if enabled, None otherwise
        """
        if 0 <= self.selected_index < len(self.options):
            option = self.options[self.selected_index]
            if option.enabled:
                return option
        return None

    def get_selected_index(self) -> int:
        """Get the currently selected index.

        Returns:
            Currently selected index
        """
        return self.selected_index

    def set_selected_index(self, index: int) -> None:
        """Set the selected index.

        Args:
            index: Index to select
        """
        if 0 <= index < len(self.options):
            self.selected_index = index

    def enable_option(self, index: int) -> None:
        """Enable a menu option.

        Args:
            index: Index of option to enable
        """
        if 0 <= index < len(self.options):
            self.options[index].enabled = True

    def disable_option(self, index: int) -> None:
        """Disable a menu option.

        Args:
            index: Index of option to disable
        """
        if 0 <= index < len(self.options):
            self.options[index].enabled = False
