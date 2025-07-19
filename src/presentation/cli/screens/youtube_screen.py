"""YouTube video processing screen."""

import asyncio
from typing import Any, Dict, Optional

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoRequest,
    ProcessYouTubeVideoUseCase,
)

from ..components.input_field import InputField, YouTubeURLValidator
from ..components.progress import ProgressDisplay
from .base_screen import Screen


class YouTubeScreen(Screen):
    """Screen for processing YouTube videos."""

    def __init__(self, cli: Any):
        """Initialize the YouTube screen.

        Args:
            cli: Reference to the main CLI controller
        """
        super().__init__(cli)
        self.console = Console()

        # Initialize input field
        self.url_input = InputField(
            title="🎬 URL do Vídeo do YouTube",
            placeholder="https://youtube.com/watch?v=... ou https://youtu.be/...",
            validator=YouTubeURLValidator.validate,
            theme=self.theme,
            max_length=500,
        )

        # State management
        self.current_step = "input"  # input, preview, processing, complete
        self.video_info: Optional[Dict[str, Any]] = None
        self.processing_progress: Optional[ProgressDisplay] = None
        self.error_message = ""
        self.success_message = ""
        self.current_use_case: Optional[ProcessYouTubeVideoUseCase] = None

    async def render(self) -> None:
        """Render the YouTube screen."""
        if self.current_step == "input":
            await self._render_input_step()
        elif self.current_step == "preview":
            await self._render_preview_step()
        elif self.current_step == "processing":
            await self._render_processing_step()
        elif self.current_step == "complete":
            await self._render_complete_step()

    async def _render_input_step(self) -> None:
        """Render the URL input step."""
        content = Text()

        # Add header
        header = Text(
            "🎬 Processar Vídeo do YouTube", style=self.theme.get_style("panel_title")
        )
        content.append(header)
        content.append("\n\n")

        # Add description
        description = Text(
            "Digite a URL do vídeo do YouTube que deseja transcrever.\n"
            "Formatos aceitos: youtube.com/watch?v=ID ou youtu.be/ID",
            style=self.theme.get_style("text_secondary"),
        )
        content.append(description)
        content.append("\n\n")

        # Show error message if any
        if self.error_message:
            error_text = Text()
            error_text.append("❌ ", style=self.theme.get_style("status_error"))
            error_text.append(
                self.error_message, style=self.theme.get_style("status_error")
            )
            content.append(error_text)
            content.append("\n\n")

        # Create main panel
        main_panel = Panel(
            Align.center(content),
            border_style=self.theme.border_style,
            style=self.theme.get_style("panel_border"),
            title="Alfredo AI",
            title_align="center",
            padding=(1, 2),
        )

        # Create input panel
        input_panel = self.url_input.render()

        # Create navigation help
        help_text = self.get_navigation_help()
        help_panel = Panel(
            Align.center(help_text),
            border_style=self.theme.muted_color,
            style=self.theme.get_style("text_secondary"),
            height=3,
        )

        # Update display with all panels
        from rich.columns import Columns
        from rich.layout import Layout

        layout = Layout()
        layout.split_column(
            Layout(main_panel, size=8),
            Layout(input_panel, size=8),
            Layout(help_panel, size=3),
        )

        self.update_display(layout)

    async def _render_preview_step(self) -> None:
        """Render the video preview step."""
        content = Text()

        # Add header
        header = Text(
            "📋 Informações do Vídeo", style=self.theme.get_style("panel_title")
        )
        content.append(header)
        content.append("\n\n")

        if self.video_info:
            # Show video information
            info_text = Text()
            info_text.append(
                "📺 Título: ", style=self.theme.get_style("text_highlight")
            )
            info_text.append(
                f"{self.video_info.get('title', 'N/A')}\n",
                style=self.theme.get_style("text_primary"),
            )

            info_text.append("👤 Canal: ", style=self.theme.get_style("text_highlight"))
            info_text.append(
                f"{self.video_info.get('uploader', 'N/A')}\n",
                style=self.theme.get_style("text_primary"),
            )

            info_text.append(
                "⏱️  Duração: ", style=self.theme.get_style("text_highlight")
            )
            duration = self.video_info.get("duration", 0)
            duration_str = (
                f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
            )
            info_text.append(
                f"{duration_str}\n", style=self.theme.get_style("text_primary")
            )

            info_text.append(
                "📊 Qualidade: ", style=self.theme.get_style("text_highlight")
            )
            info_text.append(
                f"{self.video_info.get('height', 'N/A')}p\n",
                style=self.theme.get_style("text_primary"),
            )

            content.append(info_text)
        else:
            content.append(
                "Carregando informações do vídeo...",
                style=self.theme.get_style("text_secondary"),
            )

        content.append("\n")

        # Add confirmation prompt
        confirm_text = Text()
        confirm_text.append(
            "Deseja processar este vídeo?\n\n",
            style=self.theme.get_style("text_primary"),
        )
        confirm_text.append(
            "Enter: Processar  ", style=self.theme.get_style("status_success")
        )
        confirm_text.append(
            "ESC: Voltar  ", style=self.theme.get_style("text_secondary")
        )
        confirm_text.append("Q: Cancelar", style=self.theme.get_style("status_error"))
        content.append(confirm_text)

        # Create panel
        panel = Panel(
            Align.center(content),
            border_style=self.theme.border_style,
            style=self.theme.get_style("panel_border"),
            title="Alfredo AI - Preview",
            title_align="center",
            padding=(2, 4),
        )

        self.update_display(panel)

    async def _render_processing_step(self) -> None:
        """Render the processing step."""
        content = Text()

        # Add header
        header = Text("⚙️ Processando Vídeo", style=self.theme.get_style("panel_title"))
        content.append(header)
        content.append("\n\n")

        # Add video title if available
        if self.video_info:
            title_text = Text()
            title_text.append(
                "Processando: ", style=self.theme.get_style("text_secondary")
            )
            title_text.append(
                self.video_info.get("title", "Vídeo do YouTube"),
                style=self.theme.get_style("text_primary"),
            )
            content.append(title_text)
            content.append("\n\n")

        # Show progress if available
        if self.processing_progress:
            progress_panel = self.processing_progress.render()
            content.append(progress_panel)
        else:
            content.append(
                "Iniciando processamento...",
                style=self.theme.get_style("text_secondary"),
            )

        content.append("\n\n")

        # Add cancel option
        cancel_text = Text(
            "ESC: Cancelar processamento", style=self.theme.get_style("status_error")
        )
        content.append(cancel_text)

        # Create panel
        panel = Panel(
            Align.center(content),
            border_style=self.theme.border_style,
            style=self.theme.get_style("panel_border"),
            title="Alfredo AI - Processando",
            title_align="center",
            padding=(2, 4),
        )

        self.update_display(panel)

    async def _render_complete_step(self) -> None:
        """Render the completion step."""
        content = Text()

        if self.success_message:
            # Success
            header = Text(
                "✅ Processamento Concluído",
                style=self.theme.get_style("status_success"),
            )
            content.append(header)
            content.append("\n\n")

            success_text = Text(
                self.success_message, style=self.theme.get_style("text_primary")
            )
            content.append(success_text)
        else:
            # Error
            header = Text(
                "❌ Erro no Processamento", style=self.theme.get_style("status_error")
            )
            content.append(header)
            content.append("\n\n")

            error_text = Text(
                self.error_message, style=self.theme.get_style("status_error")
            )
            content.append(error_text)

        content.append("\n\n")

        # Add navigation options
        nav_text = Text()
        nav_text.append(
            "Enter: Processar outro vídeo  ",
            style=self.theme.get_style("status_success"),
        )
        nav_text.append(
            "ESC: Voltar ao menu", style=self.theme.get_style("text_secondary")
        )
        content.append(nav_text)

        # Create panel
        panel = Panel(
            Align.center(content),
            border_style=self.theme.border_style,
            style=self.theme.get_style("panel_border"),
            title="Alfredo AI - Resultado",
            title_align="center",
            padding=(2, 4),
        )

        self.update_display(panel)

    async def handle_input(self, key: str) -> None:
        """Handle user input based on current step.

        Args:
            key: The key pressed by the user
        """
        if self.current_step == "input":
            await self._handle_input_step(key)
        elif self.current_step == "preview":
            await self._handle_preview_step(key)
        elif self.current_step == "processing":
            await self._handle_processing_step(key)
        elif self.current_step == "complete":
            await self._handle_complete_step(key)

    async def _handle_input_step(self, key: str) -> None:
        """Handle input in the URL input step."""
        if key == "escape":
            self.cli.go_back()
            return

        # Handle input field
        result = self.url_input.handle_key(key)

        if result is not None:
            if result == "":  # Cancelled
                self.cli.go_back()
            elif result and self.url_input.is_valid:
                # Valid URL entered, proceed to preview
                await self._load_video_info(result)
            # If invalid, stay on input step

        # Re-render to show updated input
        await self.render()

    async def _handle_preview_step(self, key: str) -> None:
        """Handle input in the preview step."""
        if key == "escape":
            self.current_step = "input"
            self.error_message = ""
            await self.render()
        elif key == "enter":
            # Start processing
            await self._start_processing()
        elif key.lower() == "q":
            self.cli.go_back()

    async def _handle_processing_step(self, key: str) -> None:
        """Handle input in the processing step."""
        if key == "escape":
            # Cancel processing
            if self.current_use_case:
                await self.current_use_case.cancel_processing()

            self.current_step = "complete"
            self.error_message = "Processamento cancelado pelo usuário"
            await self.render()

    async def _handle_complete_step(self, key: str) -> None:
        """Handle input in the complete step."""
        if key == "enter":
            # Process another video
            self._reset_state()
            await self.render()
        elif key == "escape":
            self.cli.go_back()

    async def _load_video_info(self, url: str) -> None:
        """Load video information from YouTube URL.

        Args:
            url: YouTube URL
        """
        self.current_step = "preview"
        self.error_message = ""

        try:
            # Extract video ID
            video_id = YouTubeURLValidator.extract_video_id(url)
            if not video_id:
                self.error_message = "Não foi possível extrair ID do vídeo da URL"
                self.current_step = "input"
                return

            # Try to get video info using yt-dlp
            await self._fetch_video_info(url)

        except Exception as e:
            self.error_message = f"Erro ao carregar informações do vídeo: {str(e)}"
            self.current_step = "input"

        await self.render()

    async def _fetch_video_info(self, url: str) -> None:
        """Fetch video information using yt-dlp.

        Args:
            url: YouTube URL
        """
        try:
            import yt_dlp

            # Configure yt-dlp to only extract info
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }

            # Run in thread to avoid blocking
            def extract_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)

            # Execute in thread pool
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, extract_info)

            # Extract relevant information
            self.video_info = {
                "title": info.get("title", "Título não disponível"),
                "uploader": info.get("uploader", "Canal não disponível"),
                "duration": info.get("duration", 0),
                "height": info.get("height", "N/A"),
                "url": url,
                "id": info.get("id", ""),
            }

        except ImportError:
            # yt-dlp not available, create mock info
            video_id = YouTubeURLValidator.extract_video_id(url)
            self.video_info = {
                "title": f"Vídeo do YouTube (ID: {video_id})",
                "uploader": "Canal não disponível (yt-dlp não instalado)",
                "duration": 0,
                "height": "N/A",
                "url": url,
                "id": video_id,
            }
        except Exception as e:
            raise Exception(f"Erro ao acessar vídeo: {str(e)}")

    async def _start_processing(self) -> None:
        """Start video processing."""
        self.current_step = "processing"
        self.processing_progress = ProgressDisplay(
            title="Processando vídeo do YouTube", theme=self.theme
        )

        await self.render()

        try:
            # Get application context from CLI
            app_context = self.cli.app_context

            # Create use case
            use_case = ProcessYouTubeVideoUseCase(
                video_repository=app_context.video_repository,
                ai_provider=app_context.whisper_provider,
            )

            # Store reference for cancellation
            self.current_use_case = use_case

            # Create request with progress callback
            def progress_callback(progress: int, status: str):
                self.processing_progress.update(progress, status)
                # Schedule render in the event loop
                asyncio.create_task(self.render())

            request = ProcessYouTubeVideoRequest(
                url=self.video_info["url"],
                language=app_context.get_setting("DEFAULT_LANGUAGE", "pt"),
                progress_callback=progress_callback,
            )

            # Execute processing
            response = await use_case.execute(request)

            # Complete successfully
            self.current_step = "complete"
            self.success_message = (
                f"Vídeo '{response.video.title}' processado com sucesso!\n"
                f"Arquivo baixado: {response.downloaded_file}\n"
                f"Transcrição salva no repositório"
            )

        except ImportError as e:
            self.current_step = "complete"
            self.error_message = f"Dependência não encontrada: {str(e)}"
        except Exception as e:
            self.current_step = "complete"
            self.error_message = f"Erro durante o processamento: {str(e)}"

        await self.render()

    def _reset_state(self) -> None:
        """Reset screen state for new input."""
        self.current_step = "input"
        self.video_info = None
        self.processing_progress = None
        self.error_message = ""
        self.success_message = ""
        self.url_input.clear()

    async def on_enter(self) -> None:
        """Called when the screen is displayed."""
        self._reset_state()
        await self.render()

    async def on_exit(self) -> None:
        """Called when the screen is closed."""
        pass
        pass
