import pytest
from unittest.mock import AsyncMock, Mock
from pathlib import Path
import tempfile
import os

from src.application.use_cases.transcribe_audio import (
    TranscribeAudioUseCase,
    TranscribeAudioRequest,
    TranscribeAudioResponse
)
from src.domain.entities.video import Video
from tests.fixtures.mock_infrastructure_factory import MockInfrastructureFactory

class TestTranscribeAudioUseCase:

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
        return TranscribeAudioUseCase(
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
        )

    @pytest.fixture
    def temp_audio_file(self):
        """Create a temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'fake audio data')
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_execute_success(self, use_case, mock_factory, temp_audio_file):
        """Test successful audio transcription using factory."""
        # Setup video in storage
        video = Video(id="test-123", title="Test Video")
        storage = mock_factory.create_storage()
        storage.videos["test-123"] = video

        request = TranscribeAudioRequest(
            video_id="test-123",
            audio_path=temp_audio_file
        )

        response = await use_case.execute(request)

        assert isinstance(response, TranscribeAudioResponse)
        assert response.video.id == "test-123"
        assert response.video.title == "Test Video"
        assert "Mock transcription" in response.transcription
        assert not response.was_cached

        # Verify factory dependencies were called
        ai_provider = mock_factory.create_ai_provider()
        assert len(ai_provider.transcribe_calls) == 1
        assert len(storage.save_transcription_calls) == 1

    @pytest.mark.asyncio
    async def test_execute_video_not_found(self, use_case, temp_audio_file):
        """Test transcription when video is not found."""
        request = TranscribeAudioRequest(
            video_id="nonexistent",
            audio_path=temp_audio_file
        )

        from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError
        with pytest.raises(InvalidVideoFormatError, match="Vídeo não encontrado"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_execute_audio_file_not_found(self, use_case, mock_factory):
        """Test transcription when audio file does not exist."""
        # Setup video in storage
        video = Video(id="test-123", title="Test Video")
        storage = mock_factory.create_storage()
        storage.videos["test-123"] = video

        request = TranscribeAudioRequest(
            video_id="test-123",
            audio_path="/nonexistent/audio.wav"
        )

        from src.domain.exceptions.alfredo_errors import TranscriptionError
        with pytest.raises(TranscriptionError, match="Arquivo de áudio não encontrado"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_execute_cached_transcription(self, use_case, mock_factory, temp_audio_file):
        """Test using cached transcription."""
        # Setup video and cached transcription in storage
        video = Video(id="test-123", title="Test Video")
        storage = mock_factory.create_storage()
        storage.videos["test-123"] = video
        storage.transcriptions["test-123"] = {
            "transcription": "Cached transcription",
            "metadata": {}
        }

        request = TranscribeAudioRequest(
            video_id="test-123",
            audio_path=temp_audio_file
        )

        response = await use_case.execute(request)

        assert isinstance(response, TranscribeAudioResponse)
        assert response.transcription == "Cached transcription"
        assert response.was_cached

        # Verify AI provider was not called (used cache)
        ai_provider = mock_factory.create_ai_provider()
        assert len(ai_provider.transcribe_calls) == 0

    @pytest.mark.asyncio
    async def test_execute_transcription_failure(self, failing_mock_factory, temp_audio_file):
        """Test handling of transcription failure using factory."""
        # Setup video in storage (but AI provider will fail)
        video = Video(id="test-123", title="Test Video")
        storage = failing_mock_factory.create_storage()
        storage.should_fail = False  # Storage should work, only AI should fail
        storage.videos["test-123"] = video

        dependencies = failing_mock_factory.create_all_dependencies()
        dependencies['storage'] = storage  # Use non-failing storage
        
        use_case = TranscribeAudioUseCase(
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
        )

        request = TranscribeAudioRequest(
            video_id="test-123",
            audio_path=temp_audio_file
        )

        from src.domain.exceptions.alfredo_errors import TranscriptionError
        with pytest.raises(TranscriptionError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_factory_creates_correct_dependencies_for_transcription(self, mock_factory):
        """Test that factory creates correct dependencies for transcription use case."""
        dependencies = mock_factory.create_all_dependencies()
        
        # Create use case with factory dependencies
        use_case = TranscribeAudioUseCase(
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
        )
        
        # Verify dependencies are properly injected
        assert use_case.ai_provider is not None
        assert use_case.storage is not None
        assert use_case.config is not None
        
        # Verify types
        from src.application.interfaces.ai_provider import AIProviderInterface
        from src.application.gateways.storage_gateway import StorageGateway
        
        assert isinstance(use_case.ai_provider, AIProviderInterface)
        assert isinstance(use_case.storage, StorageGateway)

    @pytest.mark.asyncio
    async def test_use_case_does_not_instantiate_infrastructure_directly(self):
        """Test that Use Case does not instantiate infrastructure classes directly."""
        from tests.fixtures.mock_infrastructure_factory import (
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
        use_case = TranscribeAudioUseCase(
            ai_provider=MockAIProvider(),
            storage=MockStorageGateway(),
            config=config
        )
        
        # Verify that use case accepts the interfaces
        assert use_case.ai_provider is not None
        assert use_case.storage is not None
        assert use_case.config is not None
