"""Use case for processing YouTube videos."""

import logging
import time
import psutil
from dataclasses import dataclass
from typing import Callable, Optional
import webbrowser

from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError, 
    TranscriptionError, 
    InvalidVideoFormatError,
    ConfigurationError
)


@dataclass
class ProcessYouTubeVideoRequest:
    """Request for processing YouTube video."""

    url: str
    language: str = "pt"
    generate_summary: bool = False
    force_reprocess: bool = False
    quality: str = "best"
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
        self,
        downloader: VideoDownloaderGateway,
        extractor: AudioExtractorGateway,
        ai_provider: AIProviderInterface,
        storage: StorageGateway,
        config: AlfredoConfig
    ):
        """Initialize the use case with injected dependencies."""
        self.downloader = downloader
        self.extractor = extractor
        self.ai_provider = ai_provider
        self.storage = storage
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cancelled = False

    async def execute(
        self,
        request: ProcessYouTubeVideoRequest
    ) -> ProcessYouTubeVideoResponse:
        """Execute YouTube video processing."""
        start_time = time.time()
        mem_start = psutil.Process().memory_info().rss // 1024 // 1024
        try:
            downloaded_file = None
            audio_path = None

            # Step 1: Extract video info
            if self._cancelled:
                raise DownloadFailedError(request.url, "Processamento cancelado pelo usuário")
            if request.progress_callback:
                request.progress_callback(5, "Extraindo informações do vídeo...")
            video_info = await self.downloader.extract_info(request.url)

            # Step 2: Create video entity
            extracted_id = video_info.get('id') or request.url.split('v=')[-1]
            video = Video(
                id=f"youtube_{extracted_id}",
                title=video_info.get("title", ""),
                duration=video_info.get("duration", 0),
                metadata=video_info,
                source_url=request.url  # Garante que sempre há uma fonte válida
            )

            # Step 3: Check if already processed
            existing_video = await self.storage.load_video(video.id)
            if existing_video and not request.force_reprocess:
                self.logger.info(f"Video already processed: {video.title}")
                existing_transcription = await self.storage.load_transcription(video.id)
                return ProcessYouTubeVideoResponse(
                    video=existing_video,
                    transcription=existing_transcription or "",
                    downloaded_file=existing_video.file_path or ""
                )

            # Step 4: Download video
            input_youtube_dir = self.config.data_dir / "input" / "youtube"
            input_youtube_dir.mkdir(parents=True, exist_ok=True)
            if request.progress_callback:
                request.progress_callback(20, "Baixando vídeo...")
            downloaded_file = await self.downloader.download(
                request.url,
                str(input_youtube_dir),
                request.quality
            )
            video.file_path = downloaded_file

            # Step 5: Extract audio
            if self._cancelled:
                raise TranscriptionError(downloaded_file, "Processamento cancelado pelo usuário")
            if request.progress_callback:
                request.progress_callback(40, "Extraindo áudio...")
            audio_path = str(self.config.temp_dir / f"{video.id}.wav")
            await self.extractor.extract_audio(
                downloaded_file,
                audio_path,
                format="wav",
                sample_rate=self.config.audio_sample_rate
            )

            # Step 6: Transcribe audio
            if self._cancelled:
                raise TranscriptionError(audio_path, "Processamento cancelado pelo usuário")
            if request.progress_callback:
                request.progress_callback(70, "Transcrevendo áudio...")
            if hasattr(self.ai_provider, 'transcribe'):
                transcription = await self.ai_provider.transcribe(audio_path, request.language)
            else:
                transcription = await self.ai_provider.transcribe_audio(audio_path, request.language)

            # Step 7: Save results and summary
            if self._cancelled:
                raise TranscriptionError(audio_path, "Processamento cancelado pelo usuário")
            if request.progress_callback:
                request.progress_callback(90, "Salvando resultados...")
            video.transcription = transcription
            await self.storage.save_video(video)
            await self.storage.save_transcription(
                video.id,
                transcription,
                {
                    "language": request.language,
                    "provider": self.ai_provider.__class__.__name__,
                    "audio_sample_rate": self.config.audio_sample_rate
                }
            )
            if request.generate_summary:
                summary = await self.ai_provider.summarize(transcription)
                video.summary = summary
                await self.storage.save_summary(
                    video.id,
                    summary,
                    {
                        "language": request.language,
                        "provider": self.ai_provider.__class__.__name__
                    }
                )

            # Step 8: Generate HTML and open browser
            html_dir = self.config.data_dir / "output"
            html_dir.mkdir(parents=True, exist_ok=True)
            html_path = html_dir / f"{video.id}.html"

            html_content = f"""
<!DOCTYPE html>
<html lang='pt-br'>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>{video.title}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; color: #222; }}
      h1 {{ color: #0057b7; }}
      .summary {{ background: #e3f2fd; padding: 1em; border-radius: 8px; margin-top: 1em; }}
      .transcription {{ margin-top: 2em; white-space: pre-wrap; }}
      @media (max-width: 600px) {{ body {{ font-size: 1.1em; }} }}
    </style>
  </head>
  <body>
    <h1>{video.title}</h1>
    <div class='transcription'><strong>Transcrição:</strong><br>{transcription}</div>
    {f"<div class='summary'><strong>Resumo:</strong><br>{video.summary}</div>" if hasattr(video, 'summary') and video.summary else ''}
    <footer style='margin-top:3em;font-size:0.9em;color:#888;'>
      <p>Arquivo gerado por Alfredo AI - {html_path.name}</p>
    </footer>
  </body>
</html>
"""
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            import sys
            try:
                webbrowser.open(str(html_path))
                print(f"[Alfredo] HTML gerado e aberto: {html_path}")
            except Exception:
                print(f"[Alfredo] HTML gerado em: {html_path}\nNão foi possível abrir automaticamente. Abra manualmente no navegador.")

            if request.progress_callback:
                request.progress_callback(100, "Concluído!")
            self.logger.info(f"YouTube video processed successfully: {video.title}")

            return ProcessYouTubeVideoResponse(
                video=video,
                transcription=transcription,
                downloaded_file=downloaded_file
            )
        except (DownloadFailedError, TranscriptionError, InvalidVideoFormatError, ConfigurationError):
            raise
        except Exception as e:
            self.logger.error(f"Error processing YouTube video {request.url}: {str(e)}")
            raise ConfigurationError(
                "unexpected_error",
                f"Erro inesperado no processamento: {str(e)}",
                expected="processamento bem-sucedido",
                details={"url": request.url, "error": str(e)}
            )
            mem_end = psutil.Process().memory_info().rss // 1024 // 1024
            duration = round(time.time() - start_time, 2)
            self.logger.info(f"YouTube video processed successfully: {video.title}", extra={"duration_sec": duration, "mem_usage_mb": mem_end})
            import os
            if downloaded_file and os.path.exists(downloaded_file):
                try:
                    os.remove(downloaded_file)
                except Exception:
                    pass
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception:
                    pass

    async def cancel_processing(self) -> None:
        """Cancel ongoing processing operation."""
        self.logger.info("Processing cancellation requested")
        self._cancelled = True
