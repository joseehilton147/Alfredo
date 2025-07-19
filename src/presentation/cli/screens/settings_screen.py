"""Settings screen for configuring Alfredo AI preferences."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..components.file_browser import FileExplorer
from ..components.input_field import InputField
from ..components.menu import InteractiveMenu, MenuOption
from .base_screen import Screen


class SettingsScreen(Screen):
    """Interactive settings configuration screen."""

    def __init__(self, cli):
        """Initialize the settings screen.

        Args:
            cli: Reference to the main CLI controller
        """
        super().__init__(cli)
        self.current_mode = "main"  # main, language, model, directories
        self.language_menu = None
        self.model_menu = None
        self.directory_browser = None
        self.current_directory_setting = None
        self.settings_changed = False
        self.main_menu = self._create_main_menu()

    def _create_main_menu(self) -> InteractiveMenu:
        """Create the main settings menu.

        Returns:
            Configured InteractiveMenu instance
        """
        options = [
            MenuOption(
                key="language",
                label="Idioma de Transcrição",
                description=f"Atual: {self._get_current_language_display()}",
                icon="🌐",
                action=self._handle_language_settings,
                shortcut="L",
            ),
            MenuOption(
                key="model",
                label="Modelo Whisper",
                description=f"Atual: {self._get_current_model_display()}",
                icon="🧠",
                action=self._handle_model_settings,
                shortcut="M",
            ),
            MenuOption(
                key="output_dir",
                label="Pasta de Saída",
                description=f"Atual: {self._get_current_output_dir()}",
                icon="📁",
                action=self._handle_output_directory,
                shortcut="O",
            ),
            MenuOption(
                key="input_dir",
                label="Pasta de Entrada",
                description=f"Atual: {self._get_current_input_dir()}",
                icon="📂",
                action=self._handle_input_directory,
                shortcut="I",
            ),
            MenuOption(
                key="save",
                label="Salvar Configurações",
                description="Aplicar e salvar todas as alterações",
                icon="💾",
                action=self._handle_save_settings,
                shortcut="S",
                enabled=self.settings_changed,
            ),
            MenuOption(
                key="reset",
                label="Restaurar Padrões",
                description="Voltar às configurações padrão",
                icon="🔄",
                action=self._handle_reset_settings,
                shortcut="R",
            ),
        ]

        return InteractiveMenu(
            title="⚙️ Configurações do Alfredo AI", options=options, theme=self.theme
        )

    def _get_current_language_display(self) -> str:
        """Get display name for current language setting."""
        current_lang = self.cli.app_context.get_setting("DEFAULT_LANGUAGE", "pt")
        languages = self.cli.app_context.get_supported_languages()
        return languages.get(current_lang, current_lang.upper())

    def _get_current_model_display(self) -> str:
        """Get display name for current Whisper model."""
        current_model = self.cli.app_context.get_setting("WHISPER_MODEL", "base")
        models = self.cli.app_context.get_whisper_models()
        model_info = models.get(current_model, current_model)
        return model_info.split(" - ")[0] if " - " in model_info else current_model

    def _get_current_output_dir(self) -> str:
        """Get current output directory path."""
        output_dir = self.cli.app_context.get_setting("OUTPUT_DIR", "data/output")
        return str(Path(output_dir).resolve())

    def _get_current_input_dir(self) -> str:
        """Get current input directory path."""
        input_dir = self.cli.app_context.get_setting("INPUT_DIR", "data/input")
        return str(Path(input_dir).resolve())

    def _create_language_menu(self) -> InteractiveMenu:
        """Create language selection menu.

        Returns:
            Configured InteractiveMenu for language selection
        """
        languages = self.cli.app_context.get_supported_languages()
        current_lang = self.cli.app_context.get_setting("DEFAULT_LANGUAGE", "pt")

        options = []
        for code, name in languages.items():
            is_current = code == current_lang
            description = "✓ Selecionado" if is_current else ""

            options.append(
                MenuOption(
                    key=code,
                    label=name,
                    description=description,
                    icon="🌐",
                    action=lambda c=code: self._select_language(c),
                    shortcut=code.upper()[:1],
                )
            )

        return InteractiveMenu(
            title="🌐 Selecionar Idioma de Transcrição",
            options=options,
            theme=self.theme,
        )

    def _create_model_menu(self) -> InteractiveMenu:
        """Create Whisper model selection menu.

        Returns:
            Configured InteractiveMenu for model selection
        """
        models = self.cli.app_context.get_whisper_models()
        current_model = self.cli.app_context.get_setting("WHISPER_MODEL", "base")

        options = []
        for model_name, description in models.items():
            is_current = model_name == current_model
            status = "✓ Selecionado" if is_current else ""

            options.append(
                MenuOption(
                    key=model_name,
                    label=model_name.title(),
                    description=f"{description} {status}".strip(),
                    icon="🧠",
                    action=lambda m=model_name: self._select_model(m),
                    shortcut=model_name[0].upper(),
                )
            )

        return InteractiveMenu(
            title="🧠 Selecionar Modelo Whisper", options=options, theme=self.theme
        )

    async def render(self) -> None:
        """Render the settings screen based on current mode."""
        try:
            if self.current_mode == "main":
                await self._render_main_settings()
            elif self.current_mode == "language":
                await self._render_language_selection()
            elif self.current_mode == "model":
                await self._render_model_selection()
            elif self.current_mode == "directories":
                await self._render_directory_browser()
            else:
                # Fallback to main menu
                self.current_mode = "main"
                await self._render_main_settings()

        except Exception as e:
            error_panel = Panel(
                f"[red]Erro ao renderizar configurações: {e}[/red]",
                title="Erro",
                border_style="red",
            )
            self.update_display(error_panel)

    async def _render_main_settings(self) -> None:
        """Render the main settings menu."""
        # Update menu descriptions with current values
        self._update_main_menu_descriptions()

        # Create settings overview
        overview = self._create_settings_overview()

        # Render main menu
        menu_content = self.main_menu.render()

        # Combine overview and menu
        content = Group(overview, "", menu_content)  # Empty line

        panel = Panel(
            content,
            title="⚙️ Configurações",
            border_style=self.theme.border_style,
            title_align="center",
        )

        self.update_display(panel)

    def _create_settings_overview(self) -> Table:
        """Create a table showing current settings overview.

        Returns:
            Rich Table with current settings
        """
        table = Table(show_header=True, header_style="bold")
        table.add_column("Configuração", style="cyan", width=20)
        table.add_column("Valor Atual", style="white", width=40)
        table.add_column("Status", width=10)

        # Add current settings
        settings_info = [
            ("Idioma", self._get_current_language_display(), "✓"),
            ("Modelo Whisper", self._get_current_model_display(), "✓"),
            (
                "Pasta de Saída",
                self._truncate_path(self._get_current_output_dir()),
                "✓",
            ),
            (
                "Pasta de Entrada",
                self._truncate_path(self._get_current_input_dir()),
                "✓",
            ),
        ]

        for setting, value, status in settings_info:
            table.add_row(setting, value, status)

        return table

    def _truncate_path(self, path: str, max_length: int = 35) -> str:
        """Truncate a path for display.

        Args:
            path: Path to truncate
            max_length: Maximum length

        Returns:
            Truncated path
        """
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length - 3) :]

    def _update_main_menu_descriptions(self) -> None:
        """Update main menu option descriptions with current values."""
        descriptions = [
            f"Atual: {self._get_current_language_display()}",
            f"Atual: {self._get_current_model_display()}",
            f"Atual: {self._truncate_path(self._get_current_output_dir())}",
            f"Atual: {self._truncate_path(self._get_current_input_dir())}",
            "Aplicar e salvar todas as alterações",
            "Voltar às configurações padrão",
        ]

        for i, description in enumerate(descriptions):
            if i < len(self.main_menu.options):
                self.main_menu.options[i].description = description

        # Update save button enabled state
        if len(self.main_menu.options) > 4:
            self.main_menu.options[4].enabled = self.settings_changed

    async def _render_language_selection(self) -> None:
        """Render the language selection menu."""
        if not self.language_menu:
            self.language_menu = self._create_language_menu()

        content = self.language_menu.render()
        self.update_display(content)

    async def _render_model_selection(self) -> None:
        """Render the model selection menu."""
        if not self.model_menu:
            self.model_menu = self._create_model_menu()

        content = self.model_menu.render()
        self.update_display(content)

    async def _render_directory_browser(self) -> None:
        """Render the directory browser."""
        if not self.directory_browser:
            # Initialize with current directory
            current_dir = Path.cwd()
            self.directory_browser = FileExplorer(current_dir, self.theme)

        # Create custom content for directory selection
        browser_content = self.directory_browser.render()

        # Add instructions
        instructions = Text()
        instructions.append("Navegue até a pasta desejada e pressione ", style="dim")
        instructions.append("Enter", style="bold cyan")
        instructions.append(" para selecionar.\n", style="dim")
        instructions.append("Configurando: ", style="dim")
        instructions.append(self.current_directory_setting or "Pasta", style="bold")

        content = Group(Panel(instructions, border_style="yellow"), "", browser_content)

        panel = Panel(
            content,
            title=f"📁 Selecionar {self.current_directory_setting}",
            border_style=self.theme.border_style,
            title_align="center",
        )

        self.update_display(panel)

    async def handle_input(self, key: str) -> None:
        """Handle user input based on current mode.

        Args:
            key: The key pressed by the user
        """
        # Handle common keys first
        if await self.handle_common_keys(key):
            return

        # Convert arrow keys
        if key == self.cli.keyboard.ARROW_UP:
            key = "up"
        elif key == self.cli.keyboard.ARROW_DOWN:
            key = "down"
        elif key == self.cli.keyboard.ENTER or key == "\r" or key == "\n":
            key = "enter"

        # Handle input based on current mode
        if self.current_mode == "main":
            await self._handle_main_input(key)
        elif self.current_mode == "language":
            await self._handle_language_input(key)
        elif self.current_mode == "model":
            await self._handle_model_input(key)
        elif self.current_mode == "directories":
            await self._handle_directory_input(key)

        # Re-render after input
        await self.render()

    async def _handle_main_input(self, key: str) -> None:
        """Handle input for main settings menu."""
        selected_option = self.main_menu.handle_key(key)
        if selected_option:
            await selected_option.action()

    async def _handle_language_input(self, key: str) -> None:
        """Handle input for language selection menu."""
        if key == self.cli.keyboard.ESC or key == "escape":
            self.current_mode = "main"
            return

        if self.language_menu:
            selected_option = self.language_menu.handle_key(key)
            if selected_option:
                await selected_option.action()

    async def _handle_model_input(self, key: str) -> None:
        """Handle input for model selection menu."""
        if key == self.cli.keyboard.ESC or key == "escape":
            self.current_mode = "main"
            return

        if self.model_menu:
            selected_option = self.model_menu.handle_key(key)
            if selected_option:
                await selected_option.action()

    async def _handle_directory_input(self, key: str) -> None:
        """Handle input for directory browser."""
        if key == self.cli.keyboard.ESC or key == "escape":
            self.current_mode = "main"
            self.directory_browser = None
            self.current_directory_setting = None
            return

        if self.directory_browser:
            # Handle directory selection
            if key == "enter":
                selected_entry = self.directory_browser.get_selected_entry()
                if selected_entry:
                    path, is_dir = selected_entry
                    if is_dir:
                        # Navigate to directory
                        self.directory_browser.navigate_to(path)
                    else:
                        # Select current directory
                        await self._select_directory(
                            self.directory_browser.get_current_path()
                        )
            else:
                # Pass other keys to file browser
                self.directory_browser.handle_key(key)

    # Action handlers
    async def _handle_language_settings(self) -> None:
        """Handle language settings selection."""
        self.current_mode = "language"
        self.language_menu = self._create_language_menu()

    async def _handle_model_settings(self) -> None:
        """Handle model settings selection."""
        self.current_mode = "model"
        self.model_menu = self._create_model_menu()

    async def _handle_output_directory(self) -> None:
        """Handle output directory configuration."""
        self.current_mode = "directories"
        self.current_directory_setting = "Pasta de Saída"
        current_output = self.cli.app_context.get_setting("OUTPUT_DIR", "data/output")
        self.directory_browser = FileExplorer(Path(current_output).parent, self.theme)

    async def _handle_input_directory(self) -> None:
        """Handle input directory configuration."""
        self.current_mode = "directories"
        self.current_directory_setting = "Pasta de Entrada"
        current_input = self.cli.app_context.get_setting("INPUT_DIR", "data/input")
        self.directory_browser = FileExplorer(Path(current_input).parent, self.theme)

    async def _handle_save_settings(self) -> None:
        """Handle saving settings to .env file."""
        if not self.settings_changed:
            return

        try:
            # Save settings to .env file
            self.cli.app_context.save_settings_to_env()

            # Create directories if they don't exist
            self.cli.app_context.create_directories()

            # Reset changed flag
            self.settings_changed = False

            # Show success message
            await self._show_message(
                "✅ Configurações Salvas",
                "Todas as configurações foram salvas com sucesso!",
                "success",
            )

        except Exception as e:
            await self._show_message(
                "❌ Erro ao Salvar", f"Erro ao salvar configurações: {e}", "error"
            )

    async def _handle_reset_settings(self) -> None:
        """Handle resetting settings to defaults."""
        # Reset to default values
        defaults = {
            "WHISPER_MODEL": "base",
            "DEFAULT_LANGUAGE": "pt",
            "OUTPUT_DIR": "data/output",
            "INPUT_DIR": "data/input",
        }

        for key, value in defaults.items():
            self.cli.app_context.update_setting(key, value)

        self.settings_changed = True

        await self._show_message(
            "🔄 Configurações Restauradas",
            "Configurações restauradas para os valores padrão.\nLembre-se de salvar as alterações.",
            "info",
        )

    async def _select_language(self, language_code: str) -> None:
        """Select a language for transcription.

        Args:
            language_code: Language code to select
        """
        current_lang = self.cli.app_context.get_setting("DEFAULT_LANGUAGE", "pt")
        if language_code != current_lang:
            self.cli.app_context.update_setting("DEFAULT_LANGUAGE", language_code)
            self.settings_changed = True

        self.current_mode = "main"
        self.language_menu = None

    async def _select_model(self, model_name: str) -> None:
        """Select a Whisper model.

        Args:
            model_name: Model name to select
        """
        current_model = self.cli.app_context.get_setting("WHISPER_MODEL", "base")
        if model_name != current_model:
            self.cli.app_context.update_setting("WHISPER_MODEL", model_name)
            self.settings_changed = True

        self.current_mode = "main"
        self.model_menu = None

    async def _select_directory(self, directory_path: Path) -> None:
        """Select a directory for input or output.

        Args:
            directory_path: Directory path to select
        """
        try:
            # Ensure directory exists
            directory_path.mkdir(parents=True, exist_ok=True)

            # Update appropriate setting
            if self.current_directory_setting == "Pasta de Saída":
                current_dir = self.cli.app_context.get_setting(
                    "OUTPUT_DIR", "data/output"
                )
                if str(directory_path) != current_dir:
                    self.cli.app_context.update_setting(
                        "OUTPUT_DIR", str(directory_path)
                    )
                    self.settings_changed = True
            elif self.current_directory_setting == "Pasta de Entrada":
                current_dir = self.cli.app_context.get_setting(
                    "INPUT_DIR", "data/input"
                )
                if str(directory_path) != current_dir:
                    self.cli.app_context.update_setting(
                        "INPUT_DIR", str(directory_path)
                    )
                    self.settings_changed = True

            # Return to main menu
            self.current_mode = "main"
            self.directory_browser = None
            self.current_directory_setting = None

        except Exception as e:
            await self._show_message(
                "❌ Erro", f"Erro ao selecionar diretório: {e}", "error"
            )

    async def _show_message(
        self, title: str, message: str, message_type: str = "info"
    ) -> None:
        """Show a message to the user.

        Args:
            title: Message title
            message: Message content
            message_type: Type of message (info, success, error, warning)
        """
        # Color based on message type
        colors = {
            "info": "blue",
            "success": "green",
            "error": "red",
            "warning": "yellow",
        }

        color = colors.get(message_type, "blue")

        # Create message content
        content = Text()
        content.append(message, style=f"{color}")
        content.append("\n\n")
        content.append("Pressione qualquer tecla para continuar...", style="dim")

        panel = Panel(
            Align.center(content), title=title, border_style=color, title_align="center"
        )

        self.update_display(panel)

        # Wait for any key press
        await self._wait_for_key()

    async def _wait_for_key(self) -> None:
        """Wait for any key press."""
        # This is a simplified implementation
        # In a real implementation, you might want to handle this differently
        pass

    async def on_enter(self) -> None:
        """Called when entering the settings screen."""
        self.current_mode = "main"
        self.settings_changed = False
        self.state.current_screen = "settings"

    async def on_exit(self) -> None:
        """Called when leaving the settings screen."""
        # Clean up any resources
        self.language_menu = None
        self.model_menu = None
        self.directory_browser = None
        self.current_directory_setting = None
