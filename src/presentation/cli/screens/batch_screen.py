"""Batch processing screen for the interactive CLI."""

import asyncio
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..components.file_browser import FileExplorer
from ..components.menu import InteractiveMenu, MenuOption
from ..components.progress import MultiProgressDisplay, ProgressDisplay
from .base_screen import Screen


@dataclass
class BatchProcessingResult:
    """Result of batch processing operation."""

    file_path: Path
    success: bool
    transcription: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0


class BatchScreen(Screen):
    """Screen for batch processing multiple video files."""

    # Supported languages with their display names
    SUPPORTED_LANGUAGES = {
        "pt": "Português",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "ja": "日本語",
        "ko": "한국어",
        "zh": "中文",
        "ru": "Русский",
        "ar": "العربية",
        "hi": "हिन्दी",
        "tr": "Türkçe",
        "pl": "Polski",
        "nl": "Nederlands",
    }

    def __init__(self, cli):
        """Initialize the batch processing screen.

        Args:
            cli: Reference to the main CLI controller
        """
        super().__init__(cli)

        # Screen state
        self.current_mode = "selection_type"  # selection_type, file_selection, folder_selection, language_select, confirm, processing, results
        self.selection_type = "files"  # files or folder
        self.selected_files: Set[Path] = set()
        self.selected_folder: Optional[Path] = None
        self.selected_language = "pt"  # Default to Portuguese

        # Components
        self.file_explorer = FileExplorer(theme=self.theme)
        self.type_menu: Optional[InteractiveMenu] = None
        self.language_menu: Optional[InteractiveMenu] = None
        self.multi_progress: Optional[MultiProgressDisplay] = None

        # Processing state
        self.is_processing = False
        self.processing_results: List[BatchProcessingResult] = []
        self.current_processing_index = 0

    async def render(self) -> None:
        """Render the batch processing screen based on current mode."""
        try:
            if self.current_mode == "selection_type":
                await self._render_selection_type()
            elif self.current_mode == "file_selection":
                await self._render_file_selection()
            elif self.current_mode == "folder_selection":
                await self._render_folder_selection()
            elif self.current_mode == "language_select":
                await self._render_language_selection()
            elif self.current_mode == "confirm":
                await self._render_confirmation()
            elif self.current_mode == "processing":
                await self._render_processing()
            elif self.current_mode == "results":
                await self._render_results()
        except Exception as e:
            error_panel = Panel(
                f"[red]Erro ao renderizar tela: {e}[/red]",
                title="Erro",
                border_style="red",
            )
            self.update_display(error_panel)

    async def _render_selection_type(self) -> None:
        """Render the selection type interface."""
        if not self.type_menu:
            self._create_type_menu()

        # Create header
        header_text = Text()
        header_text.append(
            "📦 Processamento em Lote\n\n", style=self.theme.get_style("text_highlight")
        )
        header_text.append(
            "Escolha como deseja selecionar os vídeos para processar:\n\n",
            style=self.theme.get_style("text_secondary"),
        )

        # Render type menu
        menu_panel = self.type_menu.render()

        # Combine content
        content = Group(header_text, menu_panel.renderable)

        # Create main panel
        main_panel = Panel(
            content,
            title="📦 Seleção de Tipo",
            border_style=self.theme.border_style,
            title_align="left",
        )

        self.update_display(main_panel)

    async def _render_file_selection(self) -> None:
        """Render the file selection interface."""
        # Get file browser content
        browser_panel = self.file_explorer.render()

        # Create header with instructions and selection info
        header_text = Text()
        header_text.append(
            "📁 Seleção Múltipla de Arquivos\n\n",
            style=self.theme.get_style("text_highlight"),
        )

        # Show selection count
        selected_count = len(self.selected_files)
        if selected_count > 0:
            header_text.append(
                f"✅ {selected_count} arquivo(s) selecionado(s)\n",
                style=self.theme.get_style("status_success"),
            )
        else:
            header_text.append(
                "Nenhum arquivo selecionado ainda\n",
                style=self.theme.get_style("text_secondary"),
            )

        # Check if current directory has video files
        if not self.file_explorer.has_video_files():
            header_text.append(
                "⚠️  Nenhum arquivo de vídeo encontrado nesta pasta.\n",
                style=self.theme.get_style("status_warning"),
            )
            header_text.append(
                "Navegue para uma pasta que contenha vídeos.\n",
                style=self.theme.get_style("text_secondary"),
            )

        header_text.append("\n")

        # Create help text
        help_text = Text()
        help_text.append("↑↓ Navegar  ", style=self.theme.get_style("text_secondary"))
        help_text.append(
            "Space Selecionar/Desselecionar  ",
            style=self.theme.get_style("text_secondary"),
        )
        help_text.append(
            "Enter Entrar/Continuar  ", style=self.theme.get_style("text_secondary")
        )
        help_text.append(
            "A Selecionar Todos  ", style=self.theme.get_style("text_secondary")
        )
        help_text.append(
            "C Limpar Seleção  ", style=self.theme.get_style("text_secondary")
        )
        help_text.append("ESC Voltar\n", style=self.theme.get_style("text_secondary"))

        # Show selected files if any
        if self.selected_files:
            help_text.append(
                "\n📋 Arquivos Selecionados:\n",
                style=self.theme.get_style("text_highlight"),
            )
            for i, file_path in enumerate(sorted(self.selected_files)):
                if i < 5:  # Show only first 5 files
                    help_text.append(
                        f"  • {file_path.name}\n",
                        style=self.theme.get_style("text_primary"),
                    )
                elif i == 5:
                    help_text.append(
                        f"  ... e mais {len(self.selected_files) - 5} arquivo(s)\n",
                        style=self.theme.get_style("text_secondary"),
                    )
                    break

        # Combine content
        content = Group(header_text, browser_panel.renderable, help_text)

        # Create main panel
        main_panel = Panel(
            content,
            title="📁 Seleção de Arquivos",
            border_style=self.theme.border_style,
            title_align="left",
        )

        self.update_display(main_panel)

    async def _render_folder_selection(self) -> None:
        """Render the folder selection interface."""
        # Get file browser content
        browser_panel = self.file_explorer.render()

        # Create header with instructions
        header_text = Text()
        header_text.append(
            "📂 Seleção de Pasta Completa\n\n",
            style=self.theme.get_style("text_highlight"),
        )

        # Show current folder info
        video_files = self.file_explorer.get_video_files_in_current_dir()
        video_count = len(video_files)

        if video_count > 0:
            header_text.append(
                f"📊 {video_count} vídeo(s) encontrado(s) nesta pasta\n",
                style=self.theme.get_style("status_success"),
            )

            # Show some file names as preview
            header_text.append(
                "Arquivos encontrados:\n", style=self.theme.get_style("text_secondary")
            )
            for i, video_file in enumerate(video_files[:3]):  # Show first 3 files
                header_text.append(
                    f"  • {video_file.name}\n",
                    style=self.theme.get_style("text_primary"),
                )
            if video_count > 3:
                header_text.append(
                    f"  ... e mais {video_count - 3} arquivo(s)\n",
                    style=self.theme.get_style("text_secondary"),
                )
        else:
            header_text.append(
                "⚠️  Nenhum arquivo de vídeo encontrado nesta pasta.\n",
                style=self.theme.get_style("status_warning"),
            )
            header_text.append(
                "Navegue para uma pasta que contenha vídeos.\n",
                style=self.theme.get_style("text_secondary"),
            )

        header_text.append("\n")

        # Create help text
        help_text = Text()
        help_text.append("↑↓ Navegar  ", style=self.theme.get_style("text_secondary"))
        help_text.append(
            "Enter Selecionar Pasta/Entrar  ",
            style=self.theme.get_style("text_secondary"),
        )
        help_text.append(
            "S Selecionar Esta Pasta  ", style=self.theme.get_style("text_secondary")
        )
        help_text.append("ESC Voltar", style=self.theme.get_style("text_secondary"))

        # Combine content
        content = Group(header_text, browser_panel.renderable, help_text)

        # Create main panel
        main_panel = Panel(
            content,
            title="📂 Seleção de Pasta",
            border_style=self.theme.border_style,
            title_align="left",
        )

        self.update_display(main_panel)

    async def _render_language_selection(self) -> None:
        """Render the language selection interface."""
        if not self.language_menu:
            self._create_language_menu()

        # Create header
        header_text = Text()
        header_text.append(
            "🌐 Selecione o idioma dos vídeos\n\n",
            style=self.theme.get_style("text_highlight"),
        )

        # Show selection summary
        if self.selection_type == "files":
            file_count = len(self.selected_files)
            header_text.append(
                f"Arquivos selecionados: {file_count}\n",
                style=self.theme.get_style("text_primary"),
            )
        else:
            video_files = (
                self.file_explorer.get_video_files_in_current_dir()
                if self.selected_folder
                else []
            )
            header_text.append(
                f"Pasta: {self.selected_folder}\n",
                style=self.theme.get_style("text_primary"),
            )
            header_text.append(
                f"Vídeos encontrados: {len(video_files)}\n",
                style=self.theme.get_style("text_primary"),
            )

        header_text.append("\n")

        # Render language menu
        menu_panel = self.language_menu.render()

        # Combine content
        content = Group(header_text, menu_panel.renderable)

        # Create main panel
        main_panel = Panel(
            content,
            title="🌐 Seleção de Idioma",
            border_style=self.theme.border_style,
            title_align="left",
        )

        self.update_display(main_panel)

    async def _render_confirmation(self) -> None:
        """Render the confirmation interface."""
        # Create confirmation content
        content_text = Text()
        content_text.append(
            "✅ Confirmar Processamento em Lote\n\n",
            style=self.theme.get_style("text_highlight"),
        )

        # Show processing summary
        files_to_process = self._get_files_to_process()
        content_text.append(
            f"Total de arquivos: {len(files_to_process)}\n",
            style=self.theme.get_style("text_primary"),
        )

        language_name = self.SUPPORTED_LANGUAGES.get(
            self.selected_language, self.selected_language
        )
        content_text.append(
            f"Idioma: {language_name} ({self.selected_language})\n",
            style=self.theme.get_style("text_primary"),
        )

        if self.selection_type == "folder" and self.selected_folder:
            content_text.append(
                f"Pasta: {self.selected_folder}\n",
                style=self.theme.get_style("text_primary"),
            )

        content_text.append("\n")

        # Show file list preview
        content_text.append(
            "📋 Arquivos a processar:\n", style=self.theme.get_style("text_highlight")
        )
        for i, file_path in enumerate(files_to_process[:5]):  # Show first 5 files
            content_text.append(
                f"  {i+1}. {file_path.name}\n",
                style=self.theme.get_style("text_primary"),
            )

        if len(files_to_process) > 5:
            content_text.append(
                f"  ... e mais {len(files_to_process) - 5} arquivo(s)\n",
                style=self.theme.get_style("text_secondary"),
            )

        content_text.append("\n")
        content_text.append(
            "🚀 Pressione Enter para iniciar o processamento\n",
            style=self.theme.get_style("status_success"),
        )
        content_text.append(
            "⬅️  Pressione Backspace para voltar à seleção de idioma\n",
            style=self.theme.get_style("text_secondary"),
        )
        content_text.append(
            "❌ Pressione ESC para cancelar",
            style=self.theme.get_style("text_secondary"),
        )

        # Create panel
        confirmation_panel = Panel(
            Align.center(content_text),
            title="✅ Confirmação",
            border_style="green",
            title_align="center",
        )

        self.update_display(confirmation_panel)

    async def _render_processing(self) -> None:
        """Render the processing interface."""
        if not self.multi_progress:
            self.multi_progress = MultiProgressDisplay(theme=self.theme)

        # Create processing content
        content_text = Text()
        content_text.append(
            "🔄 Processamento em Lote em Andamento\n\n",
            style=self.theme.get_style("text_highlight"),
        )

        files_to_process = self._get_files_to_process()
        completed = len(
            [r for r in self.processing_results if r.success or r.error_message]
        )

        content_text.append(
            f"Progresso geral: {completed}/{len(files_to_process)} arquivos\n",
            style=self.theme.get_style("text_primary"),
        )

        if self.current_processing_index < len(files_to_process):
            current_file = files_to_process[self.current_processing_index]
            content_text.append(
                f"Processando: {current_file.name}\n",
                style=self.theme.get_style("text_highlight"),
            )

        content_text.append("\n")

        # Show recent results
        if self.processing_results:
            content_text.append(
                "📊 Resultados recentes:\n",
                style=self.theme.get_style("text_highlight"),
            )
            for result in self.processing_results[-3:]:  # Show last 3 results
                if result.success:
                    content_text.append(
                        f"  ✅ {result.file_path.name}\n",
                        style=self.theme.get_style("status_success"),
                    )
                else:
                    content_text.append(
                        f"  ❌ {result.file_path.name}: {result.error_message}\n",
                        style=self.theme.get_style("status_error"),
                    )

        content_text.append(
            "\n⏳ Por favor, aguarde enquanto os vídeos são processados...\n",
            style=self.theme.get_style("text_secondary"),
        )
        content_text.append(
            "⚠️  Este processo pode levar vários minutos dependendo do número e tamanho dos arquivos.",
            style=self.theme.get_style("status_warning"),
        )

        # Get multi-progress panel
        progress_panel = self.multi_progress.render_all()

        # Combine content
        content = Group(content_text, "", progress_panel.renderable)  # Empty line

        # Create main panel
        main_panel = Panel(
            content, title="🔄 Processando", border_style="yellow", title_align="left"
        )

        self.update_display(main_panel)

    async def _render_results(self) -> None:
        """Render the results interface."""
        # Create results content
        content_text = Text()

        successful = [r for r in self.processing_results if r.success]
        failed = [r for r in self.processing_results if not r.success]

        if len(successful) > 0 and len(failed) == 0:
            content_text.append(
                "🎉 Processamento Concluído com Sucesso!\n\n",
                style=self.theme.get_style("status_success"),
            )
        elif len(successful) > 0 and len(failed) > 0:
            content_text.append(
                "⚠️  Processamento Concluído com Alguns Erros\n\n",
                style=self.theme.get_style("status_warning"),
            )
        else:
            content_text.append(
                "❌ Processamento Falhou\n\n",
                style=self.theme.get_style("status_error"),
            )

        # Summary statistics
        total_files = len(self.processing_results)
        content_text.append(
            f"📊 Resumo:\n", style=self.theme.get_style("text_highlight")
        )
        content_text.append(
            f"  Total de arquivos: {total_files}\n",
            style=self.theme.get_style("text_primary"),
        )
        content_text.append(
            f"  ✅ Sucessos: {len(successful)}\n",
            style=self.theme.get_style("status_success"),
        )
        content_text.append(
            f"  ❌ Falhas: {len(failed)}\n", style=self.theme.get_style("status_error")
        )

        # Calculate total processing time
        total_time = sum(r.processing_time for r in self.processing_results)
        content_text.append(
            f"  ⏱️  Tempo total: {total_time:.1f}s\n\n",
            style=self.theme.get_style("text_primary"),
        )

        # Show detailed results
        if successful:
            content_text.append(
                "✅ Arquivos processados com sucesso:\n",
                style=self.theme.get_style("status_success"),
            )
            for result in successful:
                content_text.append(
                    f"  • {result.file_path.name}\n",
                    style=self.theme.get_style("text_primary"),
                )
            content_text.append("\n")

        if failed:
            content_text.append(
                "❌ Arquivos com falha:\n", style=self.theme.get_style("status_error")
            )
            for result in failed:
                content_text.append(
                    f"  • {result.file_path.name}: {result.error_message}\n",
                    style=self.theme.get_style("text_primary"),
                )
            content_text.append("\n")

        content_text.append(
            "💾 Resultados salvos em: data/output/\n",
            style=self.theme.get_style("status_info"),
        )
        content_text.append(
            "Pressione qualquer tecla para voltar ao menu principal...",
            style=self.theme.get_style("text_secondary"),
        )

        # Create results panel
        results_panel = Panel(
            Align.center(content_text),
            title="📊 Resultados do Processamento",
            border_style="green" if len(failed) == 0 else "yellow",
            title_align="center",
        )

        self.update_display(results_panel)

    def _create_type_menu(self) -> None:
        """Create the selection type menu."""
        options = [
            MenuOption(
                key="files",
                label="Selecionar Arquivos Individuais",
                description="Escolher arquivos específicos de vídeo para processar",
                icon="📄",
                action=lambda: self._select_type("files"),
                shortcut="F",
            ),
            MenuOption(
                key="folder",
                label="Selecionar Pasta Completa",
                description="Processar todos os vídeos de uma pasta",
                icon="📂",
                action=lambda: self._select_type("folder"),
                shortcut="P",
            ),
        ]

        self.type_menu = InteractiveMenu(
            title="Tipo de Seleção", options=options, theme=self.theme
        )

    def _create_language_menu(self) -> None:
        """Create the language selection menu."""
        options = []

        for code, name in self.SUPPORTED_LANGUAGES.items():
            # Mark current selection
            icon = "🌐" if code != self.selected_language else "✅"

            options.append(
                MenuOption(
                    key=code,
                    label=f"{name} ({code})",
                    description=f"Transcrever em {name}",
                    icon=icon,
                    action=lambda c=code: self._select_language(c),
                    shortcut=code.upper(),
                )
            )

        self.language_menu = InteractiveMenu(
            title="Selecione o Idioma", options=options, theme=self.theme
        )

        # Set initial selection to current language
        for i, option in enumerate(options):
            if option.key == self.selected_language:
                self.language_menu.set_selected_index(i)
                break

    def _select_type(self, selection_type: str) -> None:
        """Select the type of batch processing.

        Args:
            selection_type: Either 'files' or 'folder'
        """
        self.selection_type = selection_type
        if selection_type == "files":
            self.current_mode = "file_selection"
        else:
            self.current_mode = "folder_selection"

    def _select_language(self, language_code: str) -> None:
        """Select a language and proceed to confirmation.

        Args:
            language_code: The selected language code
        """
        self.selected_language = language_code
        self.current_mode = "confirm"

    def _get_files_to_process(self) -> List[Path]:
        """Get the list of files to process based on current selection.

        Returns:
            List of video file paths to process
        """
        if self.selection_type == "files":
            return sorted(list(self.selected_files))
        elif self.selection_type == "folder" and self.selected_folder:
            # Get all video files in the selected folder
            video_files = []
            try:
                for file_path in self.selected_folder.iterdir():
                    if file_path.is_file() and self.file_explorer._is_supported_video(
                        file_path
                    ):
                        video_files.append(file_path)
            except (PermissionError, OSError):
                pass
            return sorted(video_files)
        else:
            return []

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
        if self.current_mode == "selection_type":
            await self._handle_selection_type_input(key)
        elif self.current_mode == "file_selection":
            await self._handle_file_selection_input(key)
        elif self.current_mode == "folder_selection":
            await self._handle_folder_selection_input(key)
        elif self.current_mode == "language_select":
            await self._handle_language_selection_input(key)
        elif self.current_mode == "confirm":
            await self._handle_confirmation_input(key)
        elif self.current_mode == "processing":
            await self._handle_processing_input(key)
        elif self.current_mode == "results":
            await self._handle_results_input(key)

        # Re-render after input
        await self.render()

    async def _handle_selection_type_input(self, key: str) -> None:
        """Handle input in selection type mode.

        Args:
            key: The key pressed
        """
        if self.type_menu:
            selected_option = self.type_menu.handle_key(key)
            if selected_option:
                await selected_option.action()

    async def _handle_file_selection_input(self, key: str) -> None:
        """Handle input in file selection mode.

        Args:
            key: The key pressed
        """
        if key == "backspace" or key == "\x7f":
            # Go back to selection type
            self.current_mode = "selection_type"
            return

        # Handle file browser navigation
        if key in ["up", "down", "left", "right", "h", "j", "k", "l"]:
            self.file_explorer.handle_key(key)
        elif key == "enter":
            # Enter directory or continue if files selected
            selected_entry = self.file_explorer.get_selected_entry()
            if selected_entry:
                path, is_dir = selected_entry
                if is_dir:
                    # Navigate to directory
                    self.file_explorer.navigate_to(path)
                elif self.selected_files:
                    # Continue to language selection if files are selected
                    self.current_mode = "language_select"
        elif key == " ":
            # Toggle file selection
            selected_entry = self.file_explorer.get_selected_entry()
            if selected_entry:
                path, is_dir = selected_entry
                if not is_dir:  # Only select files, not directories
                    if path in self.selected_files:
                        self.selected_files.remove(path)
                    else:
                        self.selected_files.add(path)
        elif key.lower() == "a":
            # Select all video files in current directory
            video_files = self.file_explorer.get_video_files_in_current_dir()
            self.selected_files.update(video_files)
        elif key.lower() == "c":
            # Clear selection
            self.selected_files.clear()

    async def _handle_folder_selection_input(self, key: str) -> None:
        """Handle input in folder selection mode.

        Args:
            key: The key pressed
        """
        if key == "backspace" or key == "\x7f":
            # Go back to selection type
            self.current_mode = "selection_type"
            return

        # Handle file browser navigation
        if key in ["up", "down", "left", "right", "h", "j", "k", "l"]:
            self.file_explorer.handle_key(key)
        elif key == "enter":
            # Enter directory
            selected_entry = self.file_explorer.get_selected_entry()
            if selected_entry:
                path, is_dir = selected_entry
                if is_dir:
                    self.file_explorer.navigate_to(path)
        elif key.lower() == "s":
            # Select current folder
            current_path = self.file_explorer.get_current_path()
            video_files = self.file_explorer.get_video_files_in_current_dir()
            if video_files:
                self.selected_folder = current_path
                self.current_mode = "language_select"

    async def _handle_language_selection_input(self, key: str) -> None:
        """Handle input in language selection mode.

        Args:
            key: The key pressed
        """
        if key == "backspace" or key == "\x7f":
            # Go back to file/folder selection
            if self.selection_type == "files":
                self.current_mode = "file_selection"
            else:
                self.current_mode = "folder_selection"
            return

        if self.language_menu:
            selected_option = self.language_menu.handle_key(key)
            if selected_option:
                await selected_option.action()

    async def _handle_confirmation_input(self, key: str) -> None:
        """Handle input in confirmation mode.

        Args:
            key: The key pressed
        """
        if key == "enter":
            # Start processing
            await self._start_batch_processing()
        elif key == "backspace" or key == "\x7f":
            # Go back to language selection
            self.current_mode = "language_select"

    async def _handle_processing_input(self, key: str) -> None:
        """Handle input in processing mode.

        Args:
            key: The key pressed
        """
        # During processing, only ESC is allowed to cancel
        if key == self.cli.keyboard.ESC:
            if self.is_processing:
                # TODO: Implement cancellation logic
                pass

    async def _handle_results_input(self, key: str) -> None:
        """Handle input in results mode.

        Args:
            key: The key pressed
        """
        # Any key returns to main menu
        await self.cli.go_back()

    async def _start_batch_processing(self) -> None:
        """Start the batch processing operation."""
        files_to_process = self._get_files_to_process()
        if not files_to_process:
            return

        self.current_mode = "processing"
        self.is_processing = True
        self.processing_results = []
        self.current_processing_index = 0

        try:
            # Initialize multi-progress display
            self.multi_progress = MultiProgressDisplay(theme=self.theme)

            # Create overall progress
            overall_progress = self.multi_progress.add_progress(
                "overall", "Progresso Geral", len(files_to_process)
            )
            overall_progress.start()

            # Process each file
            for i, file_path in enumerate(files_to_process):
                if not self.is_processing:  # Check for cancellation
                    break

                self.current_processing_index = i

                # Create individual progress for this file
                file_progress = self.multi_progress.add_progress(
                    f"file_{i}", f"Processando: {file_path.name}", 100
                )
                file_progress.start()

                try:
                    # Process the file
                    result = await self._process_single_file(file_path, file_progress)
                    self.processing_results.append(result)

                    # Update overall progress
                    overall_progress.update(i + 1, f"Concluído: {file_path.name}")

                except Exception as e:
                    # Handle individual file error
                    error_result = BatchProcessingResult(
                        file_path=file_path, success=False, error_message=str(e)
                    )
                    self.processing_results.append(error_result)

                    # Update overall progress
                    overall_progress.update(i + 1, f"Erro: {file_path.name}")

                finally:
                    # Remove individual progress
                    self.multi_progress.remove_progress(f"file_{i}")

                # Update display
                await self.render()
                await asyncio.sleep(0.1)  # Allow UI to update

            # Complete overall progress
            overall_progress.complete("Processamento concluído!")
            await self.render()
            await asyncio.sleep(1)  # Show completion briefly

            # Move to results
            self.current_mode = "results"

        except Exception as e:
            # Handle general error
            await self._show_error_message(str(e))
        finally:
            self.is_processing = False

    async def _process_single_file(
        self, file_path: Path, progress: ProgressDisplay
    ) -> BatchProcessingResult:
        """Process a single video file.

        Args:
            file_path: Path to the video file
            progress: Progress display for this file

        Returns:
            BatchProcessingResult with processing outcome
        """
        import time

        start_time = time.time()

        try:
            # Update progress
            progress.update(10, "Preparando processamento...")
            await asyncio.sleep(0.1)

            # Get application context and use case
            if not self.cli.app_context:
                raise RuntimeError("Contexto da aplicação não disponível")

            # Create video entity
            video_id = str(uuid.uuid4())
            from src.domain.entities.video import Video

            video = Video(
                id=video_id,
                title=file_path.stem,
                file_path=str(file_path),
                metadata={"source": "batch", "original_name": file_path.name},
            )

            # Save video to repository
            await self.cli.app_context.video_repository.save(video)

            # Update progress
            progress.update(20, "Iniciando transcrição...")
            await asyncio.sleep(0.1)

            # Create transcription request
            from src.application.use_cases.transcribe_audio import (
                TranscribeAudioRequest,
            )

            request = TranscribeAudioRequest(
                video_id=video_id,
                audio_path=str(file_path),
                language=self.selected_language,
            )

            # Update progress
            progress.update(40, "Carregando modelo de IA...")
            await asyncio.sleep(0.1)

            # Execute transcription
            response = await self.cli.app_context.transcribe_use_case.execute(request)

            # Update progress
            progress.update(80, "Salvando resultado...")
            await asyncio.sleep(0.1)

            # Save transcription result
            await self._save_transcription_result(
                response.video, response.transcription
            )

            # Complete
            progress.complete("Concluído!")
            processing_time = time.time() - start_time

            return BatchProcessingResult(
                file_path=file_path,
                success=True,
                transcription=response.transcription,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return BatchProcessingResult(
                file_path=file_path,
                success=False,
                error_message=str(e),
                processing_time=processing_time,
            )

    async def _save_transcription_result(self, video, transcription: str) -> None:
        """Save the transcription result to file.

        Args:
            video: Video entity
            transcription: Transcription text
        """
        try:
            # Create output directory
            output_dir = Path("data/output") / video.id
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save transcription as text file
            transcription_file = output_dir / "transcription.txt"
            with open(transcription_file, "w", encoding="utf-8") as f:
                f.write(transcription)

            # Save as JSON with metadata
            import json
            from datetime import datetime

            result_data = {
                "video_id": video.id,
                "title": video.title,
                "file_path": video.file_path,
                "language": self.selected_language,
                "transcription": transcription,
                "created_at": datetime.now().isoformat(),
                "metadata": video.metadata,
            }

            json_file = output_dir / "result.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise RuntimeError(f"Erro ao salvar resultado: {e}")

    async def _show_error_message(self, error_message: str) -> None:
        """Show error message.

        Args:
            error_message: The error message to display
        """
        # Create error content
        content_text = Text()
        content_text.append(
            "❌ Erro no Processamento em Lote\n\n",
            style=self.theme.get_style("status_error"),
        )

        content_text.append(
            "Detalhes do erro:\n", style=self.theme.get_style("text_secondary")
        )
        content_text.append(
            f"{error_message}\n\n", style=self.theme.get_style("text_primary")
        )

        content_text.append(
            "💡 Sugestões:\n", style=self.theme.get_style("text_highlight")
        )
        content_text.append(
            "• Verifique se os arquivos não estão corrompidos\n",
            style=self.theme.get_style("text_secondary"),
        )
        content_text.append(
            "• Certifique-se de que há espaço suficiente em disco\n",
            style=self.theme.get_style("text_secondary"),
        )
        content_text.append(
            "• Tente com menos arquivos para testar\n\n",
            style=self.theme.get_style("text_secondary"),
        )

        content_text.append(
            "Pressione qualquer tecla para tentar novamente...",
            style=self.theme.get_style("text_secondary"),
        )

        # Create error panel
        error_panel = Panel(
            Align.center(content_text),
            title="❌ Erro",
            border_style="red",
            title_align="center",
        )

        self.update_display(error_panel)

        # Wait for user input
        await self._wait_for_any_key()

        # Reset to selection type
        self._reset_screen()

    async def _wait_for_any_key(self) -> None:
        """Wait for any key press."""
        # This is a simple implementation - in a real scenario you might want
        # to handle this differently
        await asyncio.sleep(0.1)

    def _reset_screen(self) -> None:
        """Reset screen to initial state."""
        self.current_mode = "selection_type"
        self.selection_type = "files"
        self.selected_files.clear()
        self.selected_folder = None
        self.selected_language = "pt"
        self.type_menu = None
        self.language_menu = None
        self.multi_progress = None
        self.is_processing = False
        self.processing_results = []
        self.current_processing_index = 0

    async def on_enter(self) -> None:
        """Called when entering the batch processing screen."""
        # Reset screen state
        self._reset_screen()

        # Update CLI state
        self.state.current_screen = "batch_processing"

    async def on_exit(self) -> None:
        """Called when leaving the batch processing screen."""
        # Clean up any ongoing operations
        if self.is_processing:
            # TODO: Cancel processing if needed
            pass

        # Stop progress displays if active
        if self.multi_progress:
            # Stop all progress displays
            for key in list(self.multi_progress.progress_displays.keys()):
                self.multi_progress.remove_progress(key)
