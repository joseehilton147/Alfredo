"""Main interactive CLI controller for Alfredo AI."""

import asyncio
import os
from typing import List, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .context import ApplicationContext
from .screens.base_screen import Screen
from .screens.main_menu_screen import MainMenuScreen
from .state import CLIState
from .themes.default_theme import DefaultTheme
from .utils.keyboard import KeyboardHandler


class InteractiveCLI:
    """Main controller for the interactive CLI interface."""

    def __init__(self, app_context=None):
        """Initialize the interactive CLI.

        Args:
            app_context: Application context for dependency injection
        """
        self.app_context = app_context or ApplicationContext()
        self.theme = DefaultTheme()
        self.state = CLIState()
        self.console = Console()
        self.keyboard = KeyboardHandler()

        # Navigation state
        self.current_screen: Optional[Screen] = None
        self.screen_stack: List[Screen] = []

        # Runtime state
        self.running = False
        self.live_display: Optional[Live] = None

    async def run(self) -> None:
        """Execute the interactive CLI main loop."""
        self.running = True

        try:
            # Setup terminal for raw input
            self.keyboard.setup_terminal()

            # Clear screen and hide cursor
            self.console.clear()
            os.system('cls' if os.name == 'nt' else 'clear')

            # Initialize with main menu screen
            main_menu = MainMenuScreen(self)
            await self.navigate_to(main_menu)

            # Start the main loop
            await self._main_loop()

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            await self._shutdown()
        except Exception as e:
            # Handle unexpected errors
            self.console.print(f"[red]Erro inesperado: {e}[/red]")
            await self._shutdown()
        finally:
            # Always restore terminal
            self.keyboard.restore_terminal()
            self.console.show_cursor()

    async def _main_loop(self) -> None:
        """Main event loop for the CLI."""
        while self.running and self.current_screen:
            try:
                # Render current screen
                await self._render_current_screen()

                # Handle user input
                await self._handle_input()

                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.01)

            except Exception as e:
                self.console.print(f"[red]Erro no loop principal: {e}[/red]")
                break

    async def _render_current_screen(self) -> None:
        """Render the current screen."""
        if not self.current_screen:
            return

        try:
            # Create a live display for smooth updates
            if not self.live_display:
                self.live_display = Live(
                    self._create_loading_panel(),
                    console=self.console,
                    refresh_per_second=10,
                    auto_refresh=True
                )
                self.live_display.start()

            # Render the screen content
            await self.current_screen.render()

        except Exception as e:
            error_panel = Panel(
                f"[red]Erro ao renderizar tela: {e}[/red]",
                title="Erro",
                border_style="red"
            )
            if self.live_display:
                self.live_display.update(error_panel)

    def _create_loading_panel(self) -> Panel:
        """Create a loading panel."""
        return Panel(
            Text("Carregando...", style="cyan"),
            title="Alfredo AI",
            border_style="blue"
        )

    async def _handle_input(self) -> None:
        """Handle user input."""
        try:
            # Read key with timeout to keep the loop responsive
            key = await asyncio.get_event_loop().run_in_executor(
                None, self.keyboard.read_key
            )

            # Handle global keys first
            if await self._handle_global_keys(key):
                return

            # Pass key to current screen
            if self.current_screen:
                await self.current_screen.handle_input(key)

        except Exception as e:
            self.console.print(f"[red]Erro ao processar entrada: {e}[/red]")

    async def _handle_global_keys(self, key: str) -> bool:
        """Handle global keyboard shortcuts.

        Args:
            key: The key that was pressed

        Returns:
            True if the key was handled globally
        """
        # ESC key - go back or exit
        if key == self.keyboard.ESC:
            await self.go_back()
            return True

        # F1 key - show help (will be implemented in later tasks)
        if key == self.keyboard.F1:
            # TODO: Show contextual help
            return True

        # Ctrl+C - exit
        if key == '\x03':  # Ctrl+C
            await self._shutdown()
            return True

        return False

    async def navigate_to(self, screen: Screen) -> None:
        """Navigate to a new screen.

        Args:
            screen: The screen to navigate to
        """
        # Call on_exit for current screen
        if self.current_screen:
            await self.current_screen.on_exit()
            self.screen_stack.append(self.current_screen)

        # Set new screen
        self.current_screen = screen

        # Call on_enter for new screen
        if self.current_screen:
            await self.current_screen.on_enter()

    async def go_back(self) -> None:
        """Return to the previous screen."""
        if self.screen_stack:
            # Call on_exit for current screen
            if self.current_screen:
                await self.current_screen.on_exit()

            # Pop previous screen
            self.current_screen = self.screen_stack.pop()

            # Call on_enter for restored screen
            if self.current_screen:
                await self.current_screen.on_enter()

            # Update state
            self.state.current_screen = self.current_screen.__class__.__name__ if self.current_screen else "none"
        else:
            # No previous screen - exit application
            await self._shutdown()

    async def _shutdown(self) -> None:
        """Shutdown the CLI gracefully."""
        self.running = False

        # Call on_exit for current screen
        if self.current_screen:
            await self.current_screen.on_exit()

        # Stop live display
        if self.live_display:
            self.live_display.stop()

        # Clear screen and show goodbye message
        self.console.clear()
        goodbye_panel = Panel(
            Text("Obrigado por usar o Alfredo AI!", style="green bold"),
            title="Até logo!",
            border_style="green"
        )
        self.console.print(goodbye_panel)

    def update_live_display(self, content) -> None:
        """Update the live display content.

        Args:
            content: Rich renderable content to display
        """
        if self.live_display:
            self.live_display.update(content)

    def get_screen_stack_depth(self) -> int:
        """Get the current depth of the screen stack.

        Returns:
            Number of screens in the stack
        """
        return len(self.screen_stack)

    def clear_screen_stack(self) -> None:
        """Clear the entire screen stack."""
        self.screen_stack.clear()

    def peek_previous_screen(self) -> Optional[Screen]:
        """Peek at the previous screen without popping it.

        Returns:
            The previous screen or None if stack is empty
        """
        return self.screen_stack[-1] if self.screen_stack else None
