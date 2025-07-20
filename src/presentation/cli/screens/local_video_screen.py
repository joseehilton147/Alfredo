"""Local video processing screen for the interactive CLI."""

import asyncio
import uuid
from pathlib import Path
from typing import Optional

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from ..components.file_browser import FileExplorer
from ..components.menu import InteractiveMenu, MenuOption
from ..components.progress import ProgressDisplay
from .base_screen import Screen


class LocalVideoScreen(Screen):
    """Screen for processing local video files."""

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
        "nl": "Nederlands"
    }

    def __init__(self, cli):
        """Initialize the local video screen.

        Args:
            cli: Reference to the main CLI controller
        """
        super().__init__(cli)

        # Screen state
        self.current_mode = "file_browser"  # file_browser, language_select, confirm, processing
        self.selected_file: Optional[Path] = None
        self.selected_language = "pt"  # Default to Portuguese

        # Components
        self.file_explorer = FileExplorer(theme=self.theme)
        self.language_menu: Optional[InteractiveMenu] = None
        self.progress_display: Optional[ProgressDisplay] = None

        # Processing state
        self.is_processing = False

    async def render(self) -> None:
        """Render the local video screen based on current mode."""
        try:
            if self.current_mode == "file_browser":
                await self._render_file_browser()
            elif self.current_mode == "language_select":
                await self._render_language_selection()
            elif self.current_mode == "confirm":
                await self._render_confirmation()
            elif self.current_mode == "processing":
                await self._render_processing()
        except Exception as e:
            error_panel = Panel(
                f"[red]Erro ao renderizar tela: {e}[/red]",
                title="Erro",
                border_style="red"
            )
            self.update_display(error_panel)

    async def _render_file_browser(self) -> None:
        """Render the file browser interface."""
        # Get file browser content
        browser_panel = self.file_explorer.render()

        # Create header with instructions
        header_text = Text()
        header_text.append("📁 Selecione um arquivo de vídeo para transcrever\n\n",
                          style=self.theme.get_style("text_highlight"))

        # Check if current directory has video files
        if not self.file_explorer.has_video_files():
            header_text.append("⚠️  Nenhum arquivo de vídeo encontrado nesta pasta.\n",
                             style=self.theme.get_style("status_warning"))
            header_text.append("Navegue para uma pasta que contenha vídeos.\n",
                             style=self.theme.get_style("text_secondary"))

        # Create help text
        help_text = Text("\n")
        help_text.append("↑↓ Navegar  ", style=self.theme.get_style("text_secondary"))
        help_text.append("Enter Selecionar  ", style=self.theme.get_style("text_secondary"))
        help_text.append("ESC Voltar", style=self.theme.get_style("text_secondary"))

        # Combine content
        content = Group(
            header_text,
            browser_panel.renderable,
            help_text
        )

        # Create main panel
        main_panel = Panel(
            content,
            title="🎬 Processar Vídeo Local",
            border_style=self.theme.border_style,
            title_align="left"
        )

        self.update_display(main_panel)

    async def _render_language_selection(self) -> None:
        """Render the language selection interface."""
        if not self.language_menu:
            self._create_language_menu()

        # Create header
        header_text = Text()
        header_text.append("🌐 Selecione o idioma do vídeo\n\n",
                          style=self.theme.get_style("text_highlight"))

        if self.selected_file:
            header_text.append(f"Arquivo: ", style=self.theme.get_style("text_secondary"))
            header_text.append(f"{self.selected_file.name}\n",
                             style=self.theme.get_style("text_primary"))
            header_text.append(f"Tamanho: ", style=self.theme.get_style("text_secondary"))

            # Get file size
            try:
                size_bytes = self.selected_file.stat().st_size
                size_str = self._format_file_size(size_bytes)
                header_text.append(f"{size_str}\n\n", style=self.theme.get_style("text_primary"))
            except:
                header_text.append("Desconhecido\n\n", style=self.theme.get_style("text_primary"))

        # Render language menu
        menu_panel = self.language_menu.render()

        # Combine content
        content = Group(
            header_text,
            menu_panel.renderable
        )

        # Create main panel
        main_panel = Panel(
            content,
            title="🌐 Seleção de Idioma",
            border_style=self.theme.border_style,
            title_align="left"
        )

        self.update_display(main_panel)

    async def _render_confirmation(self) -> None:
        """Render the confirmation interface."""
        # Create confirmation content
        content_text = Text()
        content_text.append("✅ Confirmar Processamento\n\n",
                           style=self.theme.get_style("text_highlight"))

        if self.selected_file:
            content_text.append("Arquivo: ", style=self.theme.get_style("text_secondary"))
            content_text.append(f"{self.selected_file.name}\n",
                               style=self.theme.get_style("text_primary"))

            content_text.append("Caminho: ", style=self.theme.get_style("text_secondary"))
            content_text.append(f"{self.selected_file}\n",
                               style=self.theme.get_style("text_primary"))

            content_text.append("Idioma: ", style=self.theme.get_style("text_secondary"))
            language_name = self.SUPPORTED_LANGUAGES.get(self.selected_language, self.selected_language)
            content_text.append(f"{language_name} ({self.selected_language})\n\n",
                               style=self.theme.get_style("text_primary"))

        content_text.append("🚀 Pressione Enter para iniciar o processamento\n",
                           style=self.theme.get_style("status_success"))
        content_text.append("⬅️  Pressione Backspace para voltar à seleção de idioma\n",
                           style=self.theme.get_style("text_secondary"))
        content_text.append("❌ Pressione ESC para cancelar",
                           style=self.theme.get_style("text_secondary"))

        # Create panel
        confirmation_panel = Panel(
            Align.center(content_text),
            title="✅ Confirmação",
            border_style="green",
            title_align="center"
        )

        self.update_display(confirmation_panel)

    async def _render_processing(self) -> None:
        """Render the processing interface."""
        if not self.progress_display:
            self.progress_display = ProgressDisplay(
                title="Transcrevendo vídeo",
                theme=self.theme
            )
            self.progress_display.set_indeterminate(True)

        # Create processing content
        content_text = Text()
        content_text.append("🔄 Processando Vídeo\n\n",
                           style=self.theme.get_style("text_highlight"))

        if self.selected_file:
            content_text.append("Arquivo: ", style=self.theme.get_style("text_secondary"))
            content_text.append(f"{self.selected_file.name}\n",
                               style=self.theme.get_style("text_primary"))

            language_name = self.SUPPORTED_LANGUAGES.get(self.selected_language, self.selected_language)
            content_text.append("Idioma: ", style=self.theme.get_style("text_secondary"))
            content_text.append(f"{language_name}\n\n",
                               style=self.theme.get_style("text_primary"))

        content_text.append("⏳ Por favor, aguarde enquanto o vídeo é processado...\n",
                           style=self.theme.get_style("text_secondary"))
        content_text.append("⚠️  Este processo pode levar alguns minutos dependendo do tamanho do arquivo.",
                           style=self.theme.get_style("status_warning"))

        # Get progress panel
        progress_panel = self.progress_display.render()

        # Combine content
        content = Group(
            content_text,
            "",  # Empty line
            progress_panel.renderable
        )

        # Create main panel
        main_panel = Panel(
            content,
            title="🔄 Processando",
            border_style="yellow",
            title_align="left"
        )

        self.update_display(main_panel)

    def _create_language_menu(self) -> None:
        """Create the language selection menu."""
        options = []

        for code, name in self.SUPPORTED_LANGUAGES.items():
            # Mark current selection
            icon = "🌐" if code != self.selected_language else "✅"

            options.append(MenuOption(
                key=code,
                label=f"{name} ({code})",
                description=f"Transcrever em {name}",
                icon=icon,
                action=lambda c=code: self._select_language(c),
                shortcut=code.upper()
            ))

        self.language_menu = InteractiveMenu(
            title="Selecione o Idioma",
            options=options,
            theme=self.theme
        )

        # Set initial selection to current language
        for i, option in enumerate(options):
            if option.key == self.selected_language:
                self.language_menu.set_selected_index(i)
                break

    def _select_language(self, language_code: str) -> None:
        """Select a language and proceed to confirmation.

        Args:
            language_code: The selected language code
        """
        self.selected_language = language_code
        self.current_mode = "confirm"

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
        elif key == self.cli.keyboard.ENTER or key == '\r' or key == '\n':
            key = "enter"

        # Handle input based on current mode
        if self.current_mode == "file_browser":
            await self._handle_file_browser_input(key)
        elif self.current_mode == "language_select":
            await self._handle_language_selection_input(key)
        elif self.current_mode == "confirm":
            await self._handle_confirmation_input(key)
        elif self.current_mode == "processing":
            await self._handle_processing_input(key)

        # Re-render after input
        await self.render()

    async def _handle_file_browser_input(self, key: str) -> None:
        """Handle input in file browser mode.

        Args:
            key: The key pressed
        """
        # Pass key to file explorer
        selected_file = self.file_explorer.handle_key(key)

        if selected_file:
            # File was selected
            self.selected_file = selected_file
            self.current_mode = "language_select"

    async def _handle_language_selection_input(self, key: str) -> None:
        """Handle input in language selection mode.

        Args:
            key: The key pressed
        """
        if key == "backspace" or key == '\x7f':
            # Go back to file browser
            self.current_mode = "file_browser"
            return

        if self.language_menu:
            selected_option = self.language_menu.handle_key(key)
            if selected_option:
                # Language was selected
                await selected_option.action()

    async def _handle_confirmation_input(self, key: str) -> None:
        """Handle input in confirmation mode.

        Args:
            key: The key pressed
        """
        if key == "enter":
            # Start processing
            await self._start_processing()
        elif key == "backspace" or key == '\x7f':
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

    async def _start_processing(self) -> None:
        """Start the video processing."""
        if not self.selected_file or not self.selected_file.exists():
            return

        self.current_mode = "processing"
        self.is_processing = True

        try:
            # Create progress display
            self.progress_display = ProgressDisplay(
                title="Transcrevendo vídeo",
                theme=self.theme
            )
            self.progress_display.set_indeterminate(True)

            # Update status
            self.progress_display.update(0, "Preparando processamento...")
            await self.render()

            # Get application context and use case
            if not self.cli.app_context:
                from src.domain.exceptions import ConfigurationError
                raise ConfigurationError(
                    "app_context", 
                    "Contexto da aplicação não disponível",
                    expected="aplicação inicializada corretamente"
                )

            # Create video entity
            video_id = str(uuid.uuid4())
            from src.domain.entities.video import Video

            video = Video(
                id=video_id,
                title=self.selected_file.stem,
                file_path=str(self.selected_file),
                metadata={"source": "local", "original_name": self.selected_file.name}
            )

            # Save video to repository
            await self.cli.app_context.video_repository.save(video)

            # Update progress
            self.progress_display.update(10, "Iniciando transcrição...")
            await self.render()
            await asyncio.sleep(0.1)  # Allow UI to update

            # Create transcription request
            from src.application.use_cases.transcribe_audio import (
                TranscribeAudioRequest,
            )

            request = TranscribeAudioRequest(
                video_id=video_id,
                audio_path=str(self.selected_file),
                language=self.selected_language
            )

            # Update progress
            self.progress_display.update(20, "Carregando modelo de IA...")
            await self.render()
            await asyncio.sleep(0.1)

            # Execute transcription
            response = await self.cli.app_context.transcribe_use_case.execute(request)

            # Update progress
            self.progress_display.update(90, "Salvando resultado...")
            await self.render()
            await asyncio.sleep(0.1)

            # Save transcription result
            await self._save_transcription_result(response.video, response.transcription)

            # Complete
            self.progress_display.complete("Transcrição concluída!")
            await self.render()

            # Add to recent files
            self.state.add_recent_file(self.selected_file)

            # Show success message
            await self._show_success_message(response.transcription)

        except Exception as e:
            # Handle error
            await self._show_error_message(str(e))
        finally:
            self.is_processing = False

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
                "metadata": video.metadata
            }

            json_file = output_dir / "result.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

        except PermissionError as e:
            from src.domain.exceptions import ConfigurationError
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para salvar em {output_dir}",
                expected="permissões de escrita",
                details={"output_dir": str(output_dir), "error": str(e)}
            )
        except OSError as e:
            from src.domain.exceptions import ConfigurationError
            raise ConfigurationError(
                "storage_space",
                f"Erro de sistema ao salvar resultado: {e}",
                expected="espaço em disco suficiente",
                details={"output_dir": str(output_dir), "error": str(e)}
            )
        except Exception as e:
            from src.domain.exceptions import AlfredoError
            raise AlfredoError(f"Erro ao salvar resultado: {e}", cause=e)

    async def _show_success_message(self, transcription: str) -> None:
        """Show success message with transcription preview.

        Args:
            transcription: The transcription text
        """
        # Create success content
        content_text = Text()
        content_text.append("🎉 Transcrição Concluída com Sucesso!\n\n",
                           style=self.theme.get_style("status_success"))

        if self.selected_file:
            content_text.append("Arquivo: ", style=self.theme.get_style("text_secondary"))
            content_text.append(f"{self.selected_file.name}\n",
                               style=self.theme.get_style("text_primary"))

        content_text.append("Caracteres: ", style=self.theme.get_style("text_secondary"))
        content_text.append(f"{len(transcription)}\n\n",
                           style=self.theme.get_style("text_primary"))

        # Show preview of transcription (first 200 characters)
        preview = transcription[:200] + "..." if len(transcription) > 200 else transcription
        content_text.append("📝 Preview:\n", style=self.theme.get_style("text_highlight"))
        content_text.append(f'"{preview}"\n\n', style=self.theme.get_style("text_primary"))

        content_text.append("💾 Resultado salvo em: data/output/\n",
                           style=self.theme.get_style("status_info"))
        content_text.append("Pressione qualquer tecla para continuar...",
                           style=self.theme.get_style("text_secondary"))

        # Create success panel
        success_panel = Panel(
            Align.center(content_text),
            title="🎉 Sucesso",
            border_style="green",
            title_align="center"
        )

        self.update_display(success_panel)

        # Wait for user input
        await self._wait_for_any_key()

        # Reset to file browser
        self._reset_screen()

    async def _show_error_message(self, error_message: str) -> None:
        """Show error message.

        Args:
            error_message: The error message to display
        """
        # Create error content
        content_text = Text()
        content_text.append("❌ Erro no Processamento\n\n",
                           style=self.theme.get_style("status_error"))

        content_text.append("Detalhes do erro:\n", style=self.theme.get_style("text_secondary"))
        content_text.append(f"{error_message}\n\n", style=self.theme.get_style("text_primary"))

        content_text.append("💡 Sugestões:\n", style=self.theme.get_style("text_highlight"))
        content_text.append("• Verifique se o arquivo não está corrompido\n",
                           style=self.theme.get_style("text_secondary"))
        content_text.append("• Certifique-se de que há espaço suficiente em disco\n",
                           style=self.theme.get_style("text_secondary"))
        content_text.append("• Tente com um arquivo menor para testar\n\n",
                           style=self.theme.get_style("text_secondary"))

        content_text.append("Pressione qualquer tecla para tentar novamente...",
                           style=self.theme.get_style("text_secondary"))

        # Create error panel
        error_panel = Panel(
            Align.center(content_text),
            title="❌ Erro",
            border_style="red",
            title_align="center"
        )

        self.update_display(error_panel)

        # Wait for user input
        await self._wait_for_any_key()

        # Reset to file browser
        self._reset_screen()

    async def _wait_for_any_key(self) -> None:
        """Wait for any key press."""
        # This is a simple implementation - in a real scenario you might want
        # to handle this differently
        await asyncio.sleep(0.1)

    def _reset_screen(self) -> None:
        """Reset screen to initial state."""
        self.current_mode = "file_browser"
        self.selected_file = None
        self.selected_language = "pt"
        self.language_menu = None
        self.progress_display = None
        self.is_processing = False

    async def on_enter(self) -> None:
        """Called when entering the local video screen."""
        # Reset screen state
        self._reset_screen()

        # Update CLI state
        self.state.current_screen = "local_video"

    async def on_exit(self) -> None:
        """Called when leaving the local video screen."""
        # Clean up any ongoing operations
        if self.is_processing:
            # TODO: Cancel processing if needed
            pass

        # Stop progress display if active
        if self.progress_display:
            self.progress_display.stop()
