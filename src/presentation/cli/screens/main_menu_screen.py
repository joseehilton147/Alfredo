"""Main menu screen for the interactive CLI."""

from typing import List

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from ..components.menu import InteractiveMenu, MenuOption
from .base_screen import Screen


class MainMenuScreen(Screen):
    """Main menu screen with all primary application options."""

    def __init__(self, cli):
        """Initialize the main menu screen.

        Args:
            cli: Reference to the main CLI controller
        """
        super().__init__(cli)
        self.menu = self._create_menu()

    def _create_menu(self) -> InteractiveMenu:
        """Create the main menu with all options.

        Returns:
            Configured InteractiveMenu instance
        """
        options = [
            MenuOption(
                key="local",
                label="Processar Vídeo Local",
                description="Transcrever arquivos de vídeo do seu computador",
                icon="📁",
                action=self._handle_local_video,
                shortcut="L",
            ),
            MenuOption(
                key="youtube",
                label="Processar Vídeo do YouTube",
                description="Baixar e transcrever vídeos do YouTube",
                icon="🎬",
                action=self._handle_youtube_video,
                shortcut="Y",
            ),
            MenuOption(
                key="batch",
                label="Processamento em Lote",
                description="Processar múltiplos vídeos simultaneamente",
                icon="📦",
                action=self._handle_batch_processing,
                shortcut="B",
            ),
            MenuOption(
                key="settings",
                label="Configurações",
                description="Ajustar idioma, modelo e outras preferências",
                icon="⚙️",
                action=self._handle_settings,
                shortcut="S",
            ),
            MenuOption(
                key="results",
                label="Ver Resultados",
                description="Visualizar e gerenciar transcrições anteriores",
                icon="📄",
                action=self._handle_results,
                shortcut="R",
            ),
            MenuOption(
                key="help",
                label="Ajuda",
                description="Guia de uso e documentação",
                icon="❓",
                action=self._handle_help,
                shortcut="H",
            ),
        ]

        return InteractiveMenu(
            title="Alfredo AI - Menu Principal", options=options, theme=self.theme
        )

    async def render(self) -> None:
        """Render the main menu screen."""
        try:
            # Create welcome text
            welcome_text = Text()
            welcome_text.append(
                "Bem-vindo ao ", style=self.theme.get_style("text_primary")
            )
            welcome_text.append(
                "Alfredo AI", style=self.theme.get_style("text_highlight")
            )
            welcome_text.append("! 🤖\n", style=self.theme.get_style("text_primary"))
            welcome_text.append(
                "Sua ferramenta de transcrição de vídeos com IA",
                style=self.theme.get_style("text_secondary"),
            )

            # Render menu
            menu_content = self.menu.render()

            # Update display with menu
            self.update_display(menu_content)

        except Exception as e:
            # Handle rendering errors gracefully
            error_panel = Panel(
                f"[red]Erro ao renderizar menu: {e}[/red]",
                title="Erro",
                border_style="red",
            )
            self.update_display(error_panel)

    def _create_help_text(self) -> Text:
        """Create help text for navigation.

        Returns:
            Formatted help text
        """
        help_items = [
            ("↑↓", "Navegar"),
            ("Enter", "Selecionar"),
            ("L/Y/B/S/R/H", "Atalhos"),
            ("ESC", "Sair"),
        ]

        return self.create_help_text(help_items)

    async def handle_input(self, key: str) -> None:
        """Handle user input for the main menu.

        Args:
            key: The key pressed by the user
        """
        # Handle common keys first
        if await self.handle_common_keys(key):
            return

        # Convert arrow keys to menu navigation
        if key == self.cli.keyboard.ARROW_UP:
            key = "up"
        elif key == self.cli.keyboard.ARROW_DOWN:
            key = "down"
        elif key == self.cli.keyboard.ENTER or key == "\r" or key == "\n":
            key = "enter"

        # Handle menu input
        selected_option = self.menu.handle_key(key)
        if selected_option:
            # Execute the selected action
            await selected_option.action()

        # Re-render after input
        await self.render()

    async def on_enter(self) -> None:
        """Called when entering the main menu screen."""
        # Reset menu selection to first option
        self.menu.set_selected_index(0)

        # Update state
        self.state.current_screen = "main_menu"

    async def on_exit(self) -> None:
        """Called when leaving the main menu screen."""
        pass

    # Action handlers for menu options
    async def _handle_local_video(self) -> None:
        """Handle local video processing option."""
        from .local_video_screen import LocalVideoScreen

        local_screen = LocalVideoScreen(self.cli)
        await self.cli.navigate_to(local_screen)

    async def _handle_youtube_video(self) -> None:
        """Handle YouTube video processing option."""
        from .youtube_screen import YouTubeScreen

        youtube_screen = YouTubeScreen(self.cli)
        await self.cli.navigate_to(youtube_screen)

    async def _handle_batch_processing(self) -> None:
        """Handle batch processing option."""
        from .batch_screen import BatchScreen

        batch_screen = BatchScreen(self.cli)
        await self.cli.navigate_to(batch_screen)

    async def _handle_settings(self) -> None:
        """Handle settings option."""
        from .settings_screen import SettingsScreen

        settings_screen = SettingsScreen(self.cli)
        await self.cli.navigate_to(settings_screen)

    async def _handle_results(self) -> None:
        """Handle results viewing option."""
        from .results_screen import ResultsScreen

        results_screen = ResultsScreen(self.cli)
        await self.cli.navigate_to(results_screen)

    async def _handle_help(self) -> None:
        """Handle help option."""
        # TODO: Navigate to help screen (will be implemented in task 13)
        self._show_placeholder_message("Sistema de Ajuda")

    def _show_placeholder_message(self, feature_name: str) -> None:
        """Show a placeholder message for unimplemented features.

        Args:
            feature_name: Name of the feature
        """
        placeholder_text = Text()
        placeholder_text.append(
            f"🚧 {feature_name}\n\n", style=self.theme.get_style("text_highlight")
        )
        placeholder_text.append(
            "Esta funcionalidade será implementada em breve.\n",
            style=self.theme.get_style("text_primary"),
        )
        placeholder_text.append(
            "Pressione qualquer tecla para voltar ao menu principal.",
            style=self.theme.get_style("text_secondary"),
        )

        placeholder_panel = Panel(
            Align.center(placeholder_text),
            title=f"🔧 {feature_name}",
            border_style="yellow",
            title_align="center",
        )

        self.update_display(placeholder_panel)
