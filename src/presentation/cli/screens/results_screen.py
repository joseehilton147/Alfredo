"""Results screen for viewing and managing transcription results."""

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.align import Align
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .base_screen import Screen


class TranscriptionResult:
    """Represents a transcription result."""

    def __init__(self, result_dir: Path):
        """Initialize from result directory.

        Args:
            result_dir: Directory containing the result files
        """
        self.result_dir = result_dir
        self.video_id = result_dir.name

        # Load metadata from result.json
        self.metadata = self._load_metadata()

        # Load transcription text
        self.transcription_text = self._load_transcription()

    def _load_metadata(self) -> Dict:
        """Load metadata from result.json."""
        try:
            json_file = self.result_dir / "result.json"
            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _load_transcription(self) -> str:
        """Load transcription text from transcription.txt."""
        try:
            txt_file = self.result_dir / "transcription.txt"
            if txt_file.exists():
                with open(txt_file, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            pass
        return ""

    @property
    def title(self) -> str:
        """Get the video title."""
        return self.metadata.get("title", "Sem título")

    @property
    def created_at(self) -> datetime:
        """Get creation date."""
        try:
            date_str = self.metadata.get("created_at", "")
            if date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            pass
        return datetime.fromtimestamp(self.result_dir.stat().st_mtime)

    @property
    def file_path(self) -> str:
        """Get the original file path."""
        return self.metadata.get("file_path", "")

    @property
    def language(self) -> str:
        """Get the transcription language."""
        return self.metadata.get("language", "pt")

    @property
    def duration(self) -> float:
        """Get video duration."""
        return self.metadata.get("duration", 0.0)

    @property
    def character_count(self) -> int:
        """Get transcription character count."""
        return len(self.transcription_text)

    @property
    def word_count(self) -> int:
        """Get transcription word count."""
        return len(self.transcription_text.split()) if self.transcription_text else 0

    def get_preview(self, max_chars: int = 200) -> str:
        """Get a preview of the transcription.

        Args:
            max_chars: Maximum characters to include

        Returns:
            Preview text
        """
        if not self.transcription_text:
            return "Sem transcrição disponível"

        if len(self.transcription_text) <= max_chars:
            return self.transcription_text

        return self.transcription_text[:max_chars] + "..."


class ResultsScreen(Screen):
    """Screen for viewing and managing transcription results."""

    def __init__(self, cli):
        """Initialize the results screen."""
        super().__init__(cli)
        self.results: List[TranscriptionResult] = []
        self.selected_index = 0
        self.view_mode = "list"  # "list", "preview", "full_view", "message"
        self.current_result: Optional[TranscriptionResult] = None
        self.scroll_offset = 0
        self.preview_scroll = 0
        self.show_confirmation = False
        self.confirmation_action = None
        self.confirmation_message = ""
        self.message_panel: Optional[Panel] = None

    async def on_enter(self) -> None:
        """Called when entering the screen."""
        await self._load_results()

    async def render(self) -> None:
        """Render the results screen."""
        if self.view_mode == "message":
            if self.message_panel:
                self.update_display(self.message_panel)
            return

        if self.show_confirmation:
            await self._render_confirmation()
        elif self.view_mode == "list":
            await self._render_list_view()
        elif self.view_mode == "preview":
            await self._render_preview_view()
        elif self.view_mode == "full_view":
            await self._render_full_view()

    async def _render_list_view(self) -> None:
        """Render the list view of results."""
        if not self.results:
            content = self._create_empty_state()
        else:
            content = self._create_results_list()

        help_text = self._get_list_help_text()

        main_content = Group(content, "", help_text)
        panel = self.create_panel(main_content, "📋 Resultados das Transcrições")
        self.update_display(panel)

    async def _render_preview_view(self) -> None:
        """Render the preview view of a selected result."""
        if not self.current_result:
            await self._render_list_view()
            return

        content = self._create_preview_content()
        help_text = self._get_preview_help_text()

        main_content = Group(content, "", help_text)
        panel = self.create_panel(
            main_content, f"👁️ Preview: {self.current_result.title}"
        )
        self.update_display(panel)

    async def _render_full_view(self) -> None:
        """Render the full view of a transcription."""
        if not self.current_result:
            await self._render_list_view()
            return

        content = self._create_full_view_content()
        help_text = self._get_full_view_help_text()

        main_content = Group(content, "", help_text)
        panel = self.create_panel(
            main_content, f"📄 Transcrição: {self.current_result.title}"
        )
        self.update_display(panel)

    async def _render_confirmation(self) -> None:
        """Render confirmation dialog."""
        content = self._create_confirmation_content()
        panel = self.create_panel(content, "⚠️ Confirmação", border_style="red")
        self.update_display(panel)

    def _create_empty_state(self) -> Text:
        """Create empty state content."""
        content = Text()
        content.append("📭 Nenhuma transcrição encontrada\n\n", style="bold yellow")
        content.append("Para criar transcrições:\n", style="dim")
        content.append("• Use 'Processar Vídeo Local' no menu principal\n", style="dim")
        content.append(
            "• Use 'Processar Vídeo do YouTube' no menu principal\n", style="dim"
        )
        content.append(
            "• Use 'Processamento em Lote' para múltiplos arquivos\n", style="dim"
        )
        return content

    def _create_results_list(self) -> Table:
        """Create the results list table."""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("📅 Data", style="cyan", width=12)
        table.add_column("📹 Título", style="white", min_width=30)
        table.add_column("🌐 Idioma", style="green", width=8)
        table.add_column("📊 Estatísticas", style="yellow", width=15)
        table.add_column("📁 Origem", style="dim", width=20)

        # Sort results by date (newest first)
        sorted_results = sorted(self.results, key=lambda r: r.created_at, reverse=True)

        # Calculate visible range
        visible_start = self.scroll_offset
        visible_end = min(
            visible_start + 10, len(sorted_results)
        )  # Show 10 items at a time

        for i, result in enumerate(
            sorted_results[visible_start:visible_end], visible_start
        ):
            # Highlight selected row
            style = "bold reverse" if i == self.selected_index else ""

            # Format date
            date_str = result.created_at.strftime("%d/%m/%Y")

            # Format statistics
            stats = f"{result.word_count:,} palavras"
            if result.duration > 0:
                duration_str = f"{result.duration/60:.1f}min"
                stats += f"\n{duration_str}"

            # Format origin (file path or URL)
            origin = Path(result.file_path).name if result.file_path else "Desconhecido"
            if len(origin) > 18:
                origin = origin[:15] + "..."

            table.add_row(
                date_str,
                result.title,
                result.language.upper(),
                stats,
                origin,
                style=style,
            )

        # Add scroll indicators
        if len(sorted_results) > 10:
            scroll_info = (
                f"Mostrando {visible_start + 1}-{visible_end} de {len(sorted_results)}"
            )
            if visible_start > 0:
                scroll_info += " ↑"
            if visible_end < len(sorted_results):
                scroll_info += " ↓"

            table.caption = scroll_info

        return table

    def _create_preview_content(self) -> Group:
        """Create preview content for selected result."""
        result = self.current_result

        # Header with metadata
        header = Text()
        header.append(f"📹 {result.title}\n", style="bold white")
        header.append(
            f"📅 {result.created_at.strftime('%d/%m/%Y às %H:%M')}\n", style="cyan"
        )
        header.append(f"🌐 Idioma: {result.language.upper()}\n", style="green")
        header.append(
            f"📊 {result.word_count:,} palavras, {result.character_count:,} caracteres\n",
            style="yellow",
        )

        if result.duration > 0:
            header.append(
                f"⏱️ Duração: {result.duration/60:.1f} minutos\n", style="magenta"
            )

        if result.file_path:
            header.append(f"📁 Origem: {result.file_path}\n", style="dim")

        header.append("\n")

        # Preview text
        preview_text = Text()
        preview_text.append("📝 Preview da Transcrição:\n\n", style="bold blue")

        # Get scrollable preview
        lines = (
            result.transcription_text.split("\n")
            if result.transcription_text
            else ["Sem transcrição disponível"]
        )
        visible_lines = lines[
            self.preview_scroll : self.preview_scroll + 15
        ]  # Show 15 lines

        for line in visible_lines:
            preview_text.append(line + "\n", style="white")

        # Add scroll indicator
        if len(lines) > 15:
            scroll_info = f"\nLinhas {self.preview_scroll + 1}-{min(self.preview_scroll + 15, len(lines))} de {len(lines)}"
            if self.preview_scroll > 0:
                scroll_info += " ↑"
            if self.preview_scroll + 15 < len(lines):
                scroll_info += " ↓"
            preview_text.append(scroll_info, style="dim")

        return Group(header, preview_text)

    def _create_full_view_content(self) -> Group:
        """Create full view content for selected result."""
        result = self.current_result

        # Header
        header = Text()
        header.append(f"📹 {result.title}\n", style="bold white")
        header.append(
            f"📅 {result.created_at.strftime('%d/%m/%Y às %H:%M')}\n\n", style="cyan"
        )

        # Full transcription text
        full_text = Text()
        full_text.append("📄 Transcrição Completa:\n\n", style="bold blue")

        if result.transcription_text:
            # Get scrollable text
            lines = result.transcription_text.split("\n")
            visible_lines = lines[
                self.preview_scroll : self.preview_scroll + 20
            ]  # Show 20 lines

            for line in visible_lines:
                full_text.append(line + "\n", style="white")

            # Add scroll indicator
            if len(lines) > 20:
                scroll_info = f"\nLinhas {self.preview_scroll + 1}-{min(self.preview_scroll + 20, len(lines))} de {len(lines)}"
                if self.preview_scroll > 0:
                    scroll_info += " ↑"
                if self.preview_scroll + 20 < len(lines):
                    scroll_info += " ↓"
                full_text.append(scroll_info, style="dim")
        else:
            full_text.append("Sem transcrição disponível", style="dim")

        return Group(header, full_text)

    def _create_confirmation_content(self) -> Text:
        """Create confirmation dialog content."""
        content = Text()
        content.append(self.confirmation_message + "\n\n", style="bold white")
        content.append("Esta ação não pode ser desfeita.\n\n", style="red")
        content.append("Pressione ", style="white")
        content.append("Y", style="bold green")
        content.append(" para confirmar ou ", style="white")
        content.append("N", style="bold red")
        content.append(" para cancelar.", style="white")
        return content

    def _get_list_help_text(self) -> Text:
        """Get help text for list view."""
        help_items = [
            ("↑↓", "Navegar"),
            ("Enter", "Preview"),
            ("V", "Ver completo"),
            ("E", "Exportar"),
            ("Del", "Deletar"),
        ]

        if len(self.results) > 10:
            help_items.insert(1, ("PgUp/PgDn", "Rolar"))

        help_items.extend([("ESC", "Voltar"), ("F1", "Ajuda")])
        return self.create_help_text(help_items)

    def _get_preview_help_text(self) -> Text:
        """Get help text for preview view."""
        help_items = [
            ("↑↓", "Rolar"),
            ("V", "Ver completo"),
            ("E", "Exportar"),
            ("Del", "Deletar"),
            ("ESC", "Voltar à lista"),
        ]
        return self.create_help_text(help_items)

    def _get_full_view_help_text(self) -> Text:
        """Get help text for full view."""
        help_items = [
            ("↑↓", "Rolar"),
            ("E", "Exportar"),
            ("Del", "Deletar"),
            ("ESC", "Voltar"),
        ]
        return self.create_help_text(help_items)

    async def handle_input(self, key: str) -> None:
        """Handle user input."""
        if self.view_mode == "message":
            self.view_mode = "list"
            self.message_panel = None
            return

        if await self.handle_common_keys(key):
            return

        if self.show_confirmation:
            await self._handle_confirmation_input(key)
        elif self.view_mode == "list":
            await self._handle_list_input(key)
        elif self.view_mode == "preview":
            await self._handle_preview_input(key)
        elif self.view_mode == "full_view":
            await self._handle_full_view_input(key)

    async def _handle_list_input(self, key: str) -> None:
        """Handle input in list view."""
        if key == "up" and self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = max(0, self.scroll_offset - 1)

        elif key == "down" and self.selected_index < len(self.results) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + 10:
                self.scroll_offset = min(len(self.results) - 10, self.scroll_offset + 1)

        elif key == "pageup":
            self.selected_index = max(0, self.selected_index - 10)
            self.scroll_offset = max(0, self.scroll_offset - 10)

        elif key == "pagedown":
            self.selected_index = min(len(self.results) - 1, self.selected_index + 10)
            self.scroll_offset = min(len(self.results) - 10, self.scroll_offset + 10)

        elif key == "enter" and self.results:
            # Enter preview mode
            sorted_results = sorted(
                self.results, key=lambda r: r.created_at, reverse=True
            )
            self.current_result = sorted_results[self.selected_index]
            self.view_mode = "preview"
            self.preview_scroll = 0

        elif key.lower() == "v" and self.results:
            # Enter full view mode
            sorted_results = sorted(
                self.results, key=lambda r: r.created_at, reverse=True
            )
            self.current_result = sorted_results[self.selected_index]
            self.view_mode = "full_view"
            self.preview_scroll = 0

        elif key.lower() == "e" and self.results:
            # Export selected result
            sorted_results = sorted(
                self.results, key=lambda r: r.created_at, reverse=True
            )
            await self._export_result(sorted_results[self.selected_index])

        elif key == "delete" and self.results:
            # Delete selected result
            sorted_results = sorted(
                self.results, key=lambda r: r.created_at, reverse=True
            )
            await self._confirm_delete(sorted_results[self.selected_index])

    async def _handle_preview_input(self, key: str) -> None:
        """Handle input in preview view."""
        if key == "escape":
            self.view_mode = "list"
            self.current_result = None
            self.preview_scroll = 0

        elif key == "up" and self.preview_scroll > 0:
            self.preview_scroll -= 1

        elif key == "down":
            lines = (
                self.current_result.transcription_text.split("\n")
                if self.current_result.transcription_text
                else []
            )
            if self.preview_scroll + 15 < len(lines):
                self.preview_scroll += 1

        elif key.lower() == "v":
            # Switch to full view
            self.view_mode = "full_view"
            self.preview_scroll = 0

        elif key.lower() == "e":
            # Export current result
            await self._export_result(self.current_result)

        elif key == "delete":
            # Delete current result
            await self._confirm_delete(self.current_result)

    async def _handle_full_view_input(self, key: str) -> None:
        """Handle input in full view."""
        if key == "escape":
            self.view_mode = "list"
            self.current_result = None
            self.preview_scroll = 0

        elif key == "up" and self.preview_scroll > 0:
            self.preview_scroll -= 1

        elif key == "down":
            lines = (
                self.current_result.transcription_text.split("\n")
                if self.current_result.transcription_text
                else []
            )
            if self.preview_scroll + 20 < len(lines):
                self.preview_scroll += 1

        elif key.lower() == "e":
            # Export current result
            await self._export_result(self.current_result)

        elif key == "delete":
            # Delete current result
            await self._confirm_delete(self.current_result)

    async def _handle_confirmation_input(self, key: str) -> None:
        """Handle input in confirmation dialog."""
        if key.lower() == "y":
            # Confirm action
            if self.confirmation_action:
                await self.confirmation_action()
            self.show_confirmation = False
            self.confirmation_action = None

        elif key.lower() == "n" or key == "escape":
            # Cancel action
            self.show_confirmation = False
            self.confirmation_action = None

    async def _load_results(self) -> None:
        """Load transcription results from the output directory."""
        self.results = []

        try:
            output_dir = Path("data/output")
            if not output_dir.exists():
                return

            for item in output_dir.iterdir():
                if item.is_dir() and item.name != "summaries":
                    # Check if this directory contains transcription results
                    if (item / "result.json").exists() or (
                        item / "transcription.txt"
                    ).exists():
                        result = TranscriptionResult(item)
                        self.results.append(result)

        except Exception as e:
            # Handle error silently for now
            pass

    async def _export_result(self, result: TranscriptionResult) -> None:
        """Export a transcription result to multiple formats."""
        try:
            # Create exports directory
            exports_dir = Path("data/output") / "exports"
            exports_dir.mkdir(exist_ok=True)

            # Generate base filename
            timestamp = result.created_at.strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(
                c for c in result.title if c.isalnum() or c in (" ", "-", "_")
            ).strip()
            safe_title = safe_title[:50]  # Limit length
            base_name = f"{timestamp}_{safe_title}" if safe_title else timestamp

            # Export to TXT
            txt_file = exports_dir / f"{base_name}.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(f"Título: {result.title}\n")
                f.write(f"Data: {result.created_at.strftime('%d/%m/%Y às %H:%M')}\n")
                f.write(f"Idioma: {result.language}\n")
                if result.file_path:
                    f.write(f"Arquivo: {result.file_path}\n")
                f.write(
                    f"Duração: {result.duration/60:.1f} minutos\n"
                    if result.duration > 0
                    else ""
                )
                f.write("\n" + "=" * 50 + "\n\n")
                f.write(result.transcription_text)

            # Export to JSON
            json_file = exports_dir / f"{base_name}.json"
            export_data = {
                "title": result.title,
                "created_at": result.created_at.isoformat(),
                "language": result.language,
                "file_path": result.file_path,
                "duration": result.duration,
                "transcription": result.transcription_text,
                "statistics": {
                    "word_count": result.word_count,
                    "character_count": result.character_count,
                },
                "metadata": result.metadata,
            }

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            # Export to SRT (subtitle format)
            srt_file = exports_dir / f"{base_name}.srt"
            await self._export_to_srt(result, srt_file)

            # Show success message
            await self._show_export_success(exports_dir, base_name)

        except Exception as e:
            await self._show_error(f"Erro ao exportar: {str(e)}")

    async def _export_to_srt(self, result: TranscriptionResult, srt_file: Path) -> None:
        """Export transcription to SRT subtitle format."""
        try:
            with open(srt_file, "w", encoding="utf-8") as f:
                # Simple SRT generation - split text into chunks
                text = result.transcription_text
                if not text:
                    f.write(
                        "1\n00:00:00,000 --> 00:00:05,000\nSem transcrição disponível\n\n"
                    )
                    return

                # Split into sentences or chunks
                sentences = text.replace(". ", ".\n").split("\n")
                sentences = [s.strip() for s in sentences if s.strip()]

                duration_per_sentence = (
                    max(3.0, result.duration / len(sentences))
                    if result.duration > 0 and sentences
                    else 5.0
                )

                for i, sentence in enumerate(sentences, 1):
                    start_time = (i - 1) * duration_per_sentence
                    end_time = i * duration_per_sentence

                    start_srt = self._seconds_to_srt_time(start_time)
                    end_srt = self._seconds_to_srt_time(end_time)

                    f.write(f"{i}\n")
                    f.write(f"{start_srt} --> {end_srt}\n")
                    f.write(f"{sentence}\n\n")

        except Exception:
            # If SRT export fails, create a simple fallback
            with open(srt_file, "w", encoding="utf-8") as f:
                f.write("1\n00:00:00,000 --> 00:05:00,000\n")
                f.write(
                    result.transcription_text[:100] + "..."
                    if len(result.transcription_text) > 100
                    else result.transcription_text
                )
                f.write("\n\n")

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    async def _show_export_success(self, exports_dir: Path, base_name: str) -> None:
        """Show export success message."""
        content = Text()
        content.append("✅ Exportação concluída com sucesso!\n\n", style="bold green")
        content.append("Arquivos criados:\n", style="white")
        content.append(f"📄 {base_name}.txt\n", style="cyan")
        content.append(f"📋 {base_name}.json\n", style="cyan")
        content.append(f"🎬 {base_name}.srt\n", style="cyan")
        content.append(f"\nLocal: {exports_dir}\n\n", style="dim")
        content.append("Pressione qualquer tecla para continuar...", style="yellow")

        self.message_panel = self.create_panel(content, "📤 Exportação", border_style="green")
        self.view_mode = "message"


    async def _confirm_delete(self, result: TranscriptionResult) -> None:
        """Show delete confirmation dialog."""
        self.confirmation_message = f"Deseja deletar a transcrição '{result.title}'?"
        self.confirmation_action = lambda: self._delete_result(result)
        self.show_confirmation = True

    async def _delete_result(self, result: TranscriptionResult) -> None:
        """Delete a transcription result."""
        try:
            # Remove the entire result directory
            shutil.rmtree(result.result_dir)

            # Reload results
            await self._load_results()

            # Adjust selection if needed
            if self.selected_index >= len(self.results):
                self.selected_index = max(0, len(self.results) - 1)

            # Return to list view
            self.view_mode = "list"
            self.current_result = None

            # Show success message
            await self._show_delete_success(result.title)

        except Exception as e:
            await self._show_error(f"Erro ao deletar: {str(e)}")

    async def _show_delete_success(self, title: str) -> None:
        """Show delete success message."""
        content = Text()
        content.append("🗑️ Transcrição deletada com sucesso!\n\n", style="bold green")
        content.append(f"'{title}' foi removida permanentemente.\n\n", style="white")
        content.append("Pressione qualquer tecla para continuar...", style="yellow")

        self.message_panel = self.create_panel(content, "✅ Deletado", border_style="green")
        self.view_mode = "message"


    async def _show_error(self, message: str) -> None:
        """Show error message."""
        content = Text()
        content.append("❌ Erro\n\n", style="bold red")
        content.append(f"{message}\n\n", style="white")
        content.append("Pressione qualquer tecla para continuar...", style="yellow")

        self.message_panel = self.create_panel(content, "❌ Erro", border_style="red")
        self.view_mode = "message"
