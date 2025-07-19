"""Base screen class for the interactive CLI."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from ..interactive_cli import InteractiveCLI


class Screen(ABC):
    """Abstract base class for all CLI screens."""

    def __init__(self, cli: 'InteractiveCLI'):
        """Initialize the screen.

        Args:
            cli: Reference to the main CLI controller
        """
        self.cli = cli
        self.theme = cli.theme
        self.state = cli.state

    @abstractmethod
    async def render(self) -> None:
        """Render the screen content."""
        pass

    @abstractmethod
    async def handle_input(self, key: str) -> None:
        """Handle user input.

        Args:
            key: The key pressed by the user
        """
        pass

    async def on_enter(self) -> None:
        """Called when the screen is displayed."""
        pass

    async def on_exit(self) -> None:
        """Called when the screen is closed."""
        pass

    def create_panel(self, content, title: str = "Alfredo AI", border_style: str = "blue") -> Panel:
        """Create a styled panel for screen content.

        Args:
            content: The content to display in the panel
            title: Panel title
            border_style: Border color/style

        Returns:
            Styled Rich panel
        """
        return Panel(
            content,
            title=title,
            border_style=border_style,
            padding=(1, 2)
        )

    def create_help_text(self, help_items: list) -> Text:
        """Create formatted help text for screen navigation.

        Args:
            help_items: List of (key, description) tuples

        Returns:
            Formatted help text
        """
        help_text = Text()

        for i, (key, description) in enumerate(help_items):
            if i > 0:
                help_text.append(" | ")

            help_text.append(f"{key}", style="bold cyan")
            help_text.append(f": {description}")

        return help_text

    def get_navigation_help(self) -> Text:
        """Get standard navigation help text.

        Returns:
            Navigation help text
        """
        help_items = [
            ("ESC", "Voltar"),
            ("F1", "Ajuda"),
        ]

        # Add back navigation info if there are previous screens
        if self.cli.get_screen_stack_depth() > 0:
            previous_screen = self.cli.peek_previous_screen()
            if previous_screen:
                screen_name = previous_screen.__class__.__name__.replace("Screen", "")
                help_items.insert(0, ("ESC", f"Voltar para {screen_name}"))
        else:
            help_items[0] = ("ESC", "Sair")

        return self.create_help_text(help_items)

    async def handle_common_keys(self, key: str) -> bool:
        """Handle common keys that are shared across screens.

        Args:
            key: The key that was pressed

        Returns:
            True if the key was handled
        """
        # ESC key is handled globally by InteractiveCLI
        # F1 key is handled globally by InteractiveCLI

        # Handle other common keys here if needed
        return False

    def update_display(self, content) -> None:
        """Update the live display with new content.

        Args:
            content: Rich renderable content to display
        """
        self.cli.update_live_display(content)
