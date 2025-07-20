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
from tests.fixtures.mock_infrastructure_factory import MockInfrastructureFactory


class TestProcessYouTubeVideoUseCase:
    """Test cases for ProcessYouTubeVideoUseCase."""

    @pytest.fixture
    def mock_factory(self):
        """Mock infrastructure factory."""
        return MockInfrastructureFactory()

    @pytest.fixture
    def failing_mock_factory(self):
        """Mock infrastructure factory that fails operations."""
        return MockInfrastructureFactory(should_fail=True)

    @pytest.fixture
    def use_case(self, mock_factory):
        """Create use case instance using factory."""
        dependencies = mock_factory.create_all_dependencies()
        return ProcessYouTubeVideoUseCase(
            downloader=dependencies['downloader'],
            extractor=dependencies['extractor'],
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
        )

    @pytest.fixture
    def sample_request(self):
        """Sample processing request."""
        return ProcessYouTubeVideoRequest(
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",  # Valid YouTube video ID format
            language="pt",
            output_dir="test_output",
        )

    @pytest.mark.asyncio
    async def test_execute_success(self, use_case, sample_request, mock_factory):
        """Test successful video processing."""
        # Execute
        response = await use_case.execute(sample_request)

        # Verify response
        assert isinstance(response, ProcessYouTubeVideoResponse)
        assert response.video.id == "youtube_mock_video_123"
        assert response.video.title == "Mock Video Title"
        assert response.video.source_url == sample_request.url
        assert "Mock transcription" in response.transcription
        assert "/mock/path/" in response.downloaded_file

        # Verify that factory dependencies were called
        downloader = mock_factory.create_video_downloader()
        extractor = mock_factory.create_audio_extractor()
        ai_provider = mock_factory.create_ai_provider()
        storage = mock_factory.create_storage()

        # Verify calls were made
        assert len(downloader.extract_info_calls) == 1
        assert len(downloader.download_calls) == 1
        assert len(extractor.extract_calls) == 1
        assert len(ai_provider.transcribe_calls) == 1
        assert len(storage.save_video_calls) == 1
        assert len(storage.save_transcription_calls) == 1

    @pytest.mark.asyncio
    async def test_execute_with_progress_callback(self, use_case, sample_request):
        """Test execution with progress callback."""
        progress_updates = []

        def progress_callback(progress, status):
            progress_updates.append((progress, status))

        sample_request.progress_callback = progress_callback

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
        from src.domain.exceptions.alfredo_errors import DownloadFailedError
        with pytest.raises(DownloadFailedError, match="Processamento cancelado"):
            await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_execute_download_failure(self, failing_mock_factory, sample_request):
        """Test handling of download failure using factory."""
        dependencies = failing_mock_factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(
            downloader=dependencies['downloader'],
            extractor=dependencies['extractor'],
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
        )

        from src.domain.exceptions.alfredo_errors import DownloadFailedError
        with pytest.raises(DownloadFailedError):
            await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_execute_transcription_failure(self, mock_factory, sample_request):
        """Test handling of transcription failure using factory."""
        # Create factory with failing AI provider
        dependencies = mock_factory.create_all_dependencies()
        ai_provider = dependencies['ai_provider']
        ai_provider.should_fail = True
        
        use_case = ProcessYouTubeVideoUseCase(
            downloader=dependencies['downloader'],
            extractor=dependencies['extractor'],
            ai_provider=ai_provider,
            storage=dependencies['storage'],
            config=dependencies['config']
        )

        from src.domain.exceptions.alfredo_errors import TranscriptionError
        with pytest.raises(TranscriptionError):
            await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_factory_creates_correct_dependencies(self, mock_factory):
        """Test that factory creates all required dependencies."""
        dependencies = mock_factory.create_all_dependencies()
        
        # Verify all dependencies are present
        required_keys = ['downloader', 'extractor', 'ai_provider', 'storage', 'config']
        for key in required_keys:
            assert key in dependencies
            assert dependencies[key] is not None
        
        # Verify types
        from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
        from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
        from src.application.interfaces.ai_provider import AIProviderInterface
        from src.application.gateways.storage_gateway import StorageGateway
        
        assert isinstance(dependencies['downloader'], VideoDownloaderGateway)
        assert isinstance(dependencies['extractor'], AudioExtractorGateway)
        assert isinstance(dependencies['ai_provider'], AIProviderInterface)
        assert isinstance(dependencies['storage'], StorageGateway)

    @pytest.mark.asyncio
    async def test_factory_caching_behavior(self, mock_factory):
        """Test that factory properly caches instances."""
        # Create same dependency twice
        downloader1 = mock_factory.create_video_downloader()
        downloader2 = mock_factory.create_video_downloader()
        
        # Should be the same instance (cached)
        assert downloader1 is downloader2
        
        # Clear cache and create again
        mock_factory.clear_cache()
        downloader3 = mock_factory.create_video_downloader()
        
        # Should be different instance after cache clear
        assert downloader1 is not downloader3

    @pytest.mark.asyncio
    async def test_cancel_processing(self, use_case):
        """Test cancellation functionality."""
        assert not use_case._cancelled

        await use_case.cancel_processing()

        assert use_case._cancelled

    @pytest.mark.asyncio
    async def test_execute_cancellation_during_processing(self, use_case, sample_request):
        """Test cancellation during different processing steps."""
        # Cancel during processing
        await use_case.cancel_processing()

        from src.domain.exceptions.alfredo_errors import DownloadFailedError
        with pytest.raises(DownloadFailedError, match="Processamento cancelado"):
            await use_case.execute(sample_request)

    @pytest.mark.asyncio
    async def test_use_case_does_not_instantiate_infrastructure_directly(self):
        """Test that Use Case does not instantiate infrastructure classes directly."""
        # This test verifies that the Use Case constructor only accepts interfaces
        # and does not create concrete implementations internally
        
        from tests.fixtures.mock_infrastructure_factory import (
            MockVideoDownloaderGateway,
            MockAudioExtractorGateway,
            MockAIProvider,
            MockStorageGateway
        )
        from src.config.alfredo_config import AlfredoConfig
        import tempfile
        
        # Create mock config
        temp_dir = tempfile.mkdtemp()
        config = AlfredoConfig()
        config.data_dir = Path(temp_dir)
        config.temp_dir = Path(temp_dir)
        
        # Create use case with mock dependencies
        use_case = ProcessYouTubeVideoUseCase(
            downloader=MockVideoDownloaderGateway(),
            extractor=MockAudioExtractorGateway(),
            ai_provider=MockAIProvider(),
            storage=MockStorageGateway(),
            config=config
        )
        
        # Verify that use case accepts the interfaces
        assert use_case.downloader is not None
        assert use_case.extractor is not None
        assert use_case.ai_provider is not None
        assert use_case.storage is not None
        assert use_case.config is not None
