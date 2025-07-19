"""Integration tests for YouTube video processing."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoRequest,
    ProcessYouTubeVideoUseCase,
)
from src.domain.entities.video import Video


class TestYouTubeProcessingIntegration:
    """Integration tests for YouTube video processing."""

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

    @pytest.mark.asyncio
    async def test_youtube_processing_end_to_end(self, use_case):
        """Test complete YouTube video processing workflow."""
        # Mock the download and info extraction methods
        with patch.object(use_case, "_download_video") as mock_download, patch.object(
            use_case, "_extract_video_info"
        ) as mock_extract:

            # Setup mocks
            mock_download.return_value = "/path/to/downloaded/video.mp4"
            mock_extract.return_value = {
                "id": "dQw4w9WgXcQ",
                "title": "Test YouTube Video",
                "uploader": "Test Channel",
                "duration": 120,
            }

            # Track progress updates
            progress_updates = []

            def progress_callback(progress, status):
                progress_updates.append((progress, status))

            # Create request
            request = ProcessYouTubeVideoRequest(
                url="https://youtube.com/watch?v=dQw4w9WgXcQ",
                language="pt",
                progress_callback=progress_callback,
            )

            # Execute processing
            response = await use_case.execute(request)

            # Verify response
            assert response.video.id == "youtube_dQw4w9WgXcQ"
            assert response.video.title == "Test YouTube Video"
            assert response.video.source_url == request.url
            assert response.transcription == "Test transcription"
            assert response.downloaded_file == "/path/to/downloaded/video.mp4"

            # Verify progress updates were made
            assert len(progress_updates) > 0
            assert any("Baixando" in status for _, status in progress_updates)
            assert any(
                "Transcrevendo" in status or "transcrição" in status.lower()
                for _, status in progress_updates
            )
            assert any(
                "Concluído" in status or "concluído" in status.lower()
                for _, status in progress_updates
            )

            # Verify repository was called to save video
            assert (
                use_case.video_repository.save.call_count == 2
            )  # Once for video, once for transcription

    @pytest.mark.asyncio
    async def test_youtube_processing_with_cancellation(self, use_case):
        """Test YouTube processing cancellation."""
        # Cancel the processing
        await use_case.cancel_processing()

        # Create request
        request = ProcessYouTubeVideoRequest(
            url="https://youtube.com/watch?v=dQw4w9WgXcQ", language="pt"
        )

        # Verify cancellation works
        with pytest.raises(Exception, match="Processamento cancelado"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_youtube_processing_error_handling(self, use_case):
        """Test error handling in YouTube processing."""
        # Mock download to fail
        with patch.object(
            use_case, "_download_video", side_effect=Exception("Download failed")
        ):
            request = ProcessYouTubeVideoRequest(
                url="https://youtube.com/watch?v=dQw4w9WgXcQ", language="pt"
            )

            # Verify error is propagated
            with pytest.raises(Exception, match="Download failed"):
                await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_youtube_url_validation(self):
        """Test YouTube URL validation."""
        from src.presentation.cli.components.input_field import YouTubeURLValidator

        # Test valid URLs
        valid_urls = [
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "youtube.com/watch?v=dQw4w9WgXcQ",
            "youtu.be/dQw4w9WgXcQ",
        ]

        for url in valid_urls:
            is_valid, message = YouTubeURLValidator.validate(url)
            assert is_valid, f"URL should be valid: {url}"
            assert "válida" in message.lower()

        # Test invalid URLs
        invalid_urls = [
            "https://example.com/video",
            "not-a-url",
            "https://youtube.com/watch?v=invalid",
            "https://youtube.com/watch?v=",
            "",
        ]

        for url in invalid_urls:
            if url:  # Empty string is considered valid (no input yet)
                is_valid, message = YouTubeURLValidator.validate(url)
                assert not is_valid, f"URL should be invalid: {url}"
                assert "inválida" in message.lower()

    @pytest.mark.asyncio
    async def test_video_id_extraction(self):
        """Test video ID extraction from YouTube URLs."""
        from src.presentation.cli.components.input_field import YouTubeURLValidator

        test_cases = [
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ?t=10", "dQw4w9WgXcQ"),
            ("youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]

        for url, expected_id in test_cases:
            video_id = YouTubeURLValidator.extract_video_id(url)
            assert video_id == expected_id, f"Failed to extract ID from {url}"

        # Test invalid URLs
        invalid_urls = [
            "https://example.com/video",
            "not-a-url",
            "https://youtube.com/watch?v=invalid",
        ]

        for url in invalid_urls:
            video_id = YouTubeURLValidator.extract_video_id(url)
            assert video_id is None, f"Should not extract ID from invalid URL: {url}"
