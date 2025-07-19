"""Tests for ProcessYouTubeVideoUseCase."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoRequest,
    ProcessYouTubeVideoResponse,
    ProcessYouTubeVideoUseCase,
)
from src.domain.entities.video import Video


class TestProcessYouTubeVideoUseCase:
    """Test cases for ProcessYouTubeVideoUseCase."""

    @pytest.fixture
    def mock_video_repository(self):
        """Mock video repository."""
        repository = AsyncMock()
        repository.save = AsyncMock()
        return repository

    @pytest.fixture
    def mock_ai_provider(self):
        """Mock AI provider."""
        provider = AsyncMock()
        provider.transcribe_audio = AsyncMock(return_value="Test transcription")
        return provider

    @pytest.fixture
    def use_case(self, mock_video_repository, mock_ai_provider):
        """Create use case instance."""
        return ProcessYouTubeVideoUseCase(mock_video_repository, mock_ai_provider)

    @pytest.fixture
    def sample_request(self):
        """Sample processing request."""
        return ProcessYouTubeVideoRequest(
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",  # Valid YouTube video ID format
            language="pt",
            output_dir="test_output",
        )

    @pytest.mark.asyncio
    async def test_execute_success(
        self, use_case, sample_request, mock_video_repository, mock_ai_provider
    ):
        """Test successful video processing."""
        # Mock the download and info extraction
        with patch.object(use_case, "_download_video") as mock_download, patch.object(
            use_case, "_extract_video_info"
        ) as mock_extract:

            mock_download.return_value = "/path/to/downloaded/video.mp4"
            mock_extract.return_value = {
                "id": "test123",
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 120,
            }

            # Execute
            response = await use_case.execute(sample_request)

            # Verify response
            assert isinstance(response, ProcessYouTubeVideoResponse)
            assert response.video.id == "youtube_test123"
            assert response.video.title == "Test Video"
            assert response.video.source_url == sample_request.url
            assert response.transcription == "Test transcription"
            assert response.downloaded_file == "/path/to/downloaded/video.mp4"

            # Verify repository calls
            assert (
                mock_video_repository.save.call_count == 2
            )  # Once for video, once for transcription

    @pytest.mark.asyncio
    async def test_execute_with_progress_callback(self, use_case, sample_request):
        """Test execution with progress callback."""
        progress_updates = []

        def progress_callback(progress, status):
            progress_updates.append((progress, status))

        sample_request.progress_callback = progress_callback

        with patch.object(use_case, "_download_video") as mock_download, patch.object(
            use_case, "_extract_video_info"
        ) as mock_extract:

            mock_download.return_value = "/path/to/video.mp4"
            mock_extract.return_value = {
                "id": "test123",
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 120,
            }

            await use_case.execute(sample_request)

            # Verify progress updates were called
            assert len(progress_updates) > 0
            assert any("Baixando" in status for _, status in progress_updates)
            assert any("Transcrevendo" in status for _, status in progress_updates)
            assert any("Concluído" in status for _, status in progress_updates)

    @pytest.mark.asyncio
    async def test_execute_cancellation(self, use_case, sample_request):
        """Test processing cancellation."""
        # Cancel immediately
        await use_case.cancel_processing()

        # The cancellation check happens at the beginning of execute()
        # Since we cancelled before calling execute, it should raise immediately
        with pytest.raises(Exception, match="Processamento cancelado"):
            await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_download_video_success(self, use_case):
        """Test successful video download."""
        with patch("builtins.__import__") as mock_import:
            # Mock yt-dlp import
            mock_yt_dlp = MagicMock()
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"title": "Test Video"}
            mock_ydl.prepare_filename.return_value = "/path/to/video.mp4"
            mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl

            def import_side_effect(name, *args, **kwargs):
                if name == "yt_dlp":
                    return mock_yt_dlp
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            # Mock file existence
            with patch("pathlib.Path.exists", return_value=True):
                result = await use_case._download_video(
                    "https://youtube.com/watch?v=test123", "test_output"
                )

            assert result == "/path/to/video.mp4"

    @pytest.mark.asyncio
    async def test_download_video_missing_yt_dlp(self, use_case):
        """Test download when yt-dlp is not installed."""
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "yt_dlp":
                    raise ImportError("No module named 'yt_dlp'")
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            with pytest.raises(ImportError, match="yt-dlp não está instalado"):
                await use_case._download_video(
                    "https://youtube.com/watch?v=test123", "test_output"
                )

    @pytest.mark.asyncio
    async def test_download_video_with_progress(self, use_case):
        """Test video download with progress callback."""
        progress_updates = []

        def progress_callback(progress, status):
            progress_updates.append((progress, status))

        with patch("builtins.__import__") as mock_import:
            # Mock yt-dlp import
            mock_yt_dlp = MagicMock()
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {"title": "Test Video"}
            mock_ydl.prepare_filename.return_value = "/path/to/video.mp4"
            mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl

            def import_side_effect(name, *args, **kwargs):
                if name == "yt_dlp":
                    return mock_yt_dlp
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            # Mock file existence
            with patch("pathlib.Path.exists", return_value=True):
                await use_case._download_video(
                    "https://youtube.com/watch?v=test123",
                    "test_output",
                    progress_callback,
                )

            # Verify progress updates
            assert len(progress_updates) >= 2  # At least connecting and completed
            assert any("Conectando" in status for _, status in progress_updates)
            assert any("concluído" in status for _, status in progress_updates)

    @pytest.mark.asyncio
    async def test_extract_video_info_success(self, use_case):
        """Test successful video info extraction."""
        with patch("builtins.__import__") as mock_import:
            # Mock yt-dlp import
            mock_yt_dlp = MagicMock()
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = {
                "id": "test123",
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 120,
            }
            mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl

            def import_side_effect(name, *args, **kwargs):
                if name == "yt_dlp":
                    return mock_yt_dlp
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            result = await use_case._extract_video_info(
                "https://youtube.com/watch?v=test123"
            )

            assert result["id"] == "test123"
            assert result["title"] == "Test Video"
            assert result["uploader"] == "Test Channel"
            assert result["duration"] == 120

    @pytest.mark.asyncio
    async def test_extract_video_info_fallback(self, use_case):
        """Test video info extraction fallback when yt-dlp is not available."""
        # Mock the import to raise ImportError only for yt_dlp
        original_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "yt_dlp":
                raise ImportError("No module named 'yt_dlp'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = await use_case._extract_video_info(
                "https://youtube.com/watch?v=dQw4w9WgXcQ"  # Use valid YouTube ID format
            )

            assert result["id"] == "dQw4w9WgXcQ"
            assert "YouTube Video" in result["title"]
            assert result["uploader"] == "Unknown"
            assert result["duration"] == 0

    @pytest.mark.asyncio
    async def test_execute_download_failure(self, use_case, sample_request):
        """Test handling of download failure."""
        with patch.object(
            use_case, "_download_video", side_effect=Exception("Download failed")
        ):
            with pytest.raises(Exception, match="Download failed"):
                await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_execute_transcription_failure(
        self, use_case, sample_request, mock_ai_provider
    ):
        """Test handling of transcription failure."""
        mock_ai_provider.transcribe_audio.side_effect = Exception(
            "Transcription failed"
        )

        with patch.object(use_case, "_download_video") as mock_download, patch.object(
            use_case, "_extract_video_info"
        ) as mock_extract:

            mock_download.return_value = "/path/to/video.mp4"
            mock_extract.return_value = {
                "id": "test123",
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 120,
            }

            with pytest.raises(Exception, match="Transcription failed"):
                await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_cancel_processing(self, use_case):
        """Test cancellation functionality."""
        assert not use_case._cancelled

        await use_case.cancel_processing()

        assert use_case._cancelled

    @pytest.mark.asyncio
    async def test_execute_cancellation_during_processing(
        self, use_case, sample_request
    ):
        """Test cancellation during different processing steps."""
        with patch.object(use_case, "_download_video") as mock_download:
            # Cancel during download
            async def cancel_during_download(*args, **kwargs):
                await use_case.cancel_processing()
                return "/path/to/video.mp4"

            mock_download.side_effect = cancel_during_download

            with pytest.raises(Exception, match="Processamento cancelado"):
                await use_case.execute(sample_request)
