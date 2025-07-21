"""Simple tests for JsonStorageAdapter to improve coverage."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List

from src.infrastructure.storage.json_storage_adapter import JsonStorageAdapter
from src.domain.entities.video import Video


class TestJsonStorageAdapterSimple:
    """Simple tests for JsonStorageAdapter functionality."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock video repository with all necessary methods."""
        mock_repo = Mock()
        mock_repo.save = AsyncMock()
        mock_repo.find_by_id = AsyncMock()
        mock_repo.list_all = AsyncMock()
        return mock_repo
    
    @pytest.fixture
    def adapter(self, mock_repository):
        """Create a JsonStorageAdapter instance."""
        return JsonStorageAdapter(mock_repository)
    
    def test_json_storage_adapter_initialization(self, mock_repository):
        """Test JsonStorageAdapter initialization."""
        # Act
        adapter = JsonStorageAdapter(mock_repository)
        
        # Assert
        assert adapter.video_repository == mock_repository
        assert isinstance(adapter._transcriptions, dict)
        assert len(adapter._transcriptions) == 0

    @pytest.mark.asyncio
    async def test_save_video_success(self, adapter, mock_repository):
        """Test save_video method success."""
        # Arrange
        video = Video(
            id="test_id",
            title="Test Video",
            duration_seconds=120,
            file_path="/path/to/video.mp4"
        )
        
        # Act
        await adapter.save_video(video)
        
        # Assert
        mock_repository.save.assert_called_once_with(video)

    @pytest.mark.asyncio
    async def test_load_video_found(self, adapter, mock_repository):
        """Test load_video when video is found."""
        # Arrange
        video_id = "test_id"
        expected_video = Video(
            id=video_id,
            title="Test Video",
            duration_seconds=120,
            file_path="/path/to/video.mp4"
        )
        mock_repository.find_by_id.return_value = expected_video
        
        # Act
        result = await adapter.load_video(video_id)
        
        # Assert
        assert result == expected_video
        mock_repository.find_by_id.assert_called_once_with(video_id)

    @pytest.mark.asyncio
    async def test_load_video_not_found(self, adapter, mock_repository):
        """Test load_video when video is not found."""
        # Arrange
        video_id = "nonexistent_id"
        mock_repository.find_by_id.return_value = None
        
        # Act
        result = await adapter.load_video(video_id)
        
        # Assert
        assert result is None
        mock_repository.find_by_id.assert_called_once_with(video_id)

    @pytest.mark.asyncio
    async def test_save_transcription_basic(self, adapter):
        """Test save_transcription method."""
        # Arrange
        video_id = "test_id"
        transcription = "This is a test transcription"
        
        # Act
        await adapter.save_transcription(video_id, transcription)
        
        # Assert
        assert adapter._transcriptions[video_id] == transcription

    @pytest.mark.asyncio
    async def test_save_transcription_with_metadata(self, adapter):
        """Test save_transcription with metadata."""
        # Arrange
        video_id = "test_id"
        transcription = "This is a test transcription"
        metadata = {"language": "pt", "confidence": 0.95}
        
        # Act
        await adapter.save_transcription(video_id, transcription, metadata)
        
        # Assert
        assert adapter._transcriptions[video_id] == transcription

    @pytest.mark.asyncio
    async def test_load_transcription_from_cache(self, adapter):
        """Test load_transcription from cache."""
        # Arrange
        video_id = "test_id"
        expected_transcription = "Cached transcription"
        adapter._transcriptions[video_id] = expected_transcription
        
        # Act
        result = await adapter.load_transcription(video_id)
        
        # Assert
        assert result == expected_transcription

    @pytest.mark.asyncio
    async def test_load_transcription_not_found(self, adapter, mock_repository):
        """Test load_transcription when not found."""
        # Arrange
        video_id = "nonexistent_id"
        mock_repository.find_by_id.return_value = None
        
        # Act
        result = await adapter.load_transcription(video_id)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_videos_basic(self, adapter, mock_repository):
        """Test list_videos basic functionality."""
        # Arrange
        videos = [
            Video(id="1", title="Video 1", duration_seconds=60, file_path="/path/1.mp4"),
            Video(id="2", title="Video 2", duration_seconds=90, file_path="/path/2.mp4")
        ]
        mock_repository.list_all.return_value = videos
        
        # Act
        result = await adapter.list_videos()
        
        # Assert
        assert result == videos
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_videos_with_limit(self, adapter, mock_repository):
        """Test list_videos with limit."""
        # Arrange
        videos = [
            Video(id="1", title="Video 1", duration_seconds=60, file_path="/path/1.mp4"),
            Video(id="2", title="Video 2", duration_seconds=90, file_path="/path/2.mp4"),
            Video(id="3", title="Video 3", duration_seconds=120, file_path="/path/3.mp4")
        ]
        mock_repository.find_all.return_value = videos
        
        # Act
        result = await adapter.list_videos(limit=2)
        
        # Assert
        assert len(result) == 2
        assert result == videos[:2]

    @pytest.mark.asyncio
    async def test_list_videos_with_offset(self, adapter, mock_repository):
        """Test list_videos with offset."""
        # Arrange
        videos = [
            Video(id="1", title="Video 1", duration_seconds=60, file_path="/path/1.mp4"),
            Video(id="2", title="Video 2", duration_seconds=90, file_path="/path/2.mp4"),
            Video(id="3", title="Video 3", duration_seconds=120, file_path="/path/3.mp4")
        ]
        mock_repository.find_all.return_value = videos
        
        # Act
        result = await adapter.list_videos(offset=1)
        
        # Assert
        assert len(result) == 2
        assert result == videos[1:]

    @pytest.mark.asyncio
    async def test_list_videos_with_limit_and_offset(self, adapter, mock_repository):
        """Test list_videos with both limit and offset."""
        # Arrange
        videos = [
            Video(id="1", title="Video 1", duration_seconds=60, file_path="/path/1.mp4"),
            Video(id="2", title="Video 2", duration_seconds=90, file_path="/path/2.mp4"),
            Video(id="3", title="Video 3", duration_seconds=120, file_path="/path/3.mp4"),
            Video(id="4", title="Video 4", duration_seconds=150, file_path="/path/4.mp4")
        ]
        mock_repository.find_all.return_value = videos
        
        # Act
        result = await adapter.list_videos(limit=2, offset=1)
        
        # Assert
        assert len(result) == 2
        assert result == videos[1:3]

    @pytest.mark.asyncio
    async def test_list_videos_empty_result(self, adapter, mock_repository):
        """Test list_videos with empty repository."""
        # Arrange
        mock_repository.find_all.return_value = []
        
        # Act
        result = await adapter.list_videos()
        
        # Assert
        assert result == []

    def test_transcription_cache_management(self, adapter):
        """Test transcription cache management."""
        # Arrange
        video_id_1 = "video_1"
        video_id_2 = "video_2"
        transcription_1 = "First transcription"
        transcription_2 = "Second transcription"
        
        # Act
        adapter._transcriptions[video_id_1] = transcription_1
        adapter._transcriptions[video_id_2] = transcription_2
        
        # Assert
        assert len(adapter._transcriptions) == 2
        assert adapter._transcriptions[video_id_1] == transcription_1
        assert adapter._transcriptions[video_id_2] == transcription_2

    def test_cache_overwrite(self, adapter):
        """Test transcription cache overwrite."""
        # Arrange
        video_id = "test_video"
        first_transcription = "First transcription"
        second_transcription = "Updated transcription"
        
        # Act
        adapter._transcriptions[video_id] = first_transcription
        adapter._transcriptions[video_id] = second_transcription
        
        # Assert
        assert adapter._transcriptions[video_id] == second_transcription
        assert len(adapter._transcriptions) == 1

    def test_cache_contains_video(self, adapter):
        """Test checking if cache contains video transcription."""
        # Arrange
        video_id = "test_video"
        transcription = "Test transcription"
        adapter._transcriptions[video_id] = transcription
        
        # Act & Assert
        assert video_id in adapter._transcriptions
        assert "nonexistent_id" not in adapter._transcriptions

    def test_adapter_properties_access(self, adapter, mock_repository):
        """Test accessing adapter properties."""
        # Act & Assert
        assert adapter.video_repository is mock_repository
        assert isinstance(adapter._transcriptions, dict)
