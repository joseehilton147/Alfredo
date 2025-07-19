"""Use case for processing YouTube videos."""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from src.application.interfaces.ai_provider import AIProviderInterface
from src.domain.entities.video import Video
from src.domain.repositories.video_repository import VideoRepository


@dataclass
class ProcessYouTubeVideoRequest:
    """Request for processing YouTube video."""

    url: str
    language: str = "pt"
    output_dir: str = "data/input/youtube"
    progress_callback: Optional[Callable[[int, str], None]] = None


@dataclass
class ProcessYouTubeVideoResponse:
    """Response for YouTube video processing."""

    video: Video
    transcription: str
    downloaded_file: str


class ProcessYouTubeVideoUseCase:
    """Use case for downloading and processing YouTube videos."""

    def __init__(
        self, video_repository: VideoRepository, ai_provider: AIProviderInterface
    ):
        """Initialize the use case.

        Args:
            video_repository: Repository for video entities
            ai_provider: AI provider for transcription
        """
        self.video_repository = video_repository
        self.ai_provider = ai_provider
        self.logger = logging.getLogger(__name__)
        self._cancelled = False

    async def execute(
        self, request: ProcessYouTubeVideoRequest
    ) -> ProcessYouTubeVideoResponse:
        """Execute YouTube video processing.

        Args:
            request: Processing request

        Returns:
            Processing response with video and transcription

        Raises:
            ImportError: If yt-dlp is not installed
            ValueError: If URL is invalid or video cannot be processed
            Exception: For other processing errors
        """
        try:
            # Step 1: Download video
            if self._cancelled:
                raise Exception("Processamento cancelado")

            if request.progress_callback:
                request.progress_callback(10, "Baixando vídeo...")

            downloaded_file = await self._download_video(
                request.url, request.output_dir, request.progress_callback
            )

            # Step 2: Extract video info and create entity
            if self._cancelled:
                raise Exception("Processamento cancelado")

            if request.progress_callback:
                request.progress_callback(30, "Processando informações do vídeo...")

            video_info = await self._extract_video_info(request.url)
            video = Video(
                id=f"youtube_{video_info['id']}",
                title=video_info["title"],
                file_path=downloaded_file,
                source_url=request.url,
            )

            # Step 3: Save video to repository
            if self._cancelled:
                raise Exception("Processamento cancelado")

            await self.video_repository.save(video)

            # Step 4: Transcribe audio
            if self._cancelled:
                raise Exception("Processamento cancelado")

            if request.progress_callback:
                request.progress_callback(60, "Transcrevendo áudio...")

            transcription = await self.ai_provider.transcribe_audio(
                downloaded_file, request.language
            )

            # Step 5: Update video with transcription
            if self._cancelled:
                raise Exception("Processamento cancelado")

            if request.progress_callback:
                request.progress_callback(90, "Salvando resultados...")

            video.transcription = transcription
            await self.video_repository.save(video)

            if request.progress_callback:
                request.progress_callback(100, "Concluído!")

            self.logger.info(f"YouTube video processed successfully: {video.title}")

            return ProcessYouTubeVideoResponse(
                video=video,
                transcription=transcription,
                downloaded_file=downloaded_file,
            )

        except Exception as e:
            self.logger.error(f"Error processing YouTube video {request.url}: {str(e)}")
            raise

    async def _download_video(
        self,
        url: str,
        output_dir: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Download video from YouTube.

        Args:
            url: YouTube URL
            output_dir: Output directory for downloaded video

        Returns:
            Path to downloaded video file

        Raises:
            ImportError: If yt-dlp is not installed
            Exception: If download fails
        """
        try:
            import yt_dlp
        except ImportError:
            raise ImportError(
                "yt-dlp não está instalado. Instale com: pip install yt-dlp"
            )

        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Progress hook for yt-dlp
        def progress_hook(d):
            if progress_callback and d["status"] == "downloading":
                if "total_bytes" in d and d["total_bytes"]:
                    percent = int(
                        (d["downloaded_bytes"] / d["total_bytes"]) * 30
                    )  # 30% of total progress
                    progress_callback(10 + percent, f"Baixando: {percent + 10}%")
                elif "_percent_str" in d:
                    # Fallback to yt-dlp's percent string
                    percent_str = d["_percent_str"].strip()
                    progress_callback(20, f"Baixando: {percent_str}")

        # Configure yt-dlp options
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress_hook] if progress_callback else [],
        }

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return filename

        # Run download in thread to avoid blocking
        loop = asyncio.get_event_loop()

        if progress_callback:
            progress_callback(12, "Conectando ao YouTube...")

        filename = await loop.run_in_executor(None, download)

        if progress_callback:
            progress_callback(40, "Download concluído")

        if not Path(filename).exists():
            raise Exception("Falha no download do vídeo")

        return filename

    async def _extract_video_info(self, url: str) -> dict:
        """Extract video information from YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            Dictionary with video information
        """
        try:
            import yt_dlp
        except ImportError:
            # Fallback to basic info extraction
            from src.presentation.cli.components.input_field import YouTubeURLValidator

            video_id = YouTubeURLValidator.extract_video_id(url)
            return {
                "id": video_id or "unknown",
                "title": f"YouTube Video {video_id}",
                "uploader": "Unknown",
                "duration": 0,
            }

        # Configure yt-dlp to only extract info
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        def extract_info():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        # Run in thread to avoid blocking
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, extract_info)

        return {
            "id": info.get("id", "unknown"),
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown"),
            "duration": info.get("duration", 0),
        }

    async def cancel_processing(self) -> None:
        """Cancel ongoing processing operation."""
        self.logger.info("Processing cancellation requested")
        self._cancelled = True
