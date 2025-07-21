"""Tests for JsonStorageAdapter to improve coverage."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List

from src.infrastructure.storage.json_storage_adapter import JsonStorageAdapter
from src.domain.entities.video import Video
from src.domain.repositories.video_repository import VideoRepository


class TestJsonStorageAdapterBasic:
    """Basic tests for JsonStorageAdapter functionality."""
    
    def test_json_storage_adapter_initialization(self):
        """Test JsonStorageAdapter initialization."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        
        # Act
        adapter = JsonStorageAdapter(mock_repository)
        
        # Assert
        assert adapter.video_repository == mock_repository
        assert isinstance(adapter._transcriptions, dict)
        assert len(adapter._transcriptions) == 0

    @pytest.mark.asyncio
    async def test_save_video(self):
        """Test save_video method."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_repository.save = AsyncMock()
        adapter = JsonStorageAdapter(mock_repository)
        
        mock_video = Mock(spec=Video)
        
        # Act
        await adapter.save_video(mock_video)
        
        # Assert
        mock_repository.save.assert_called_once_with(mock_video)

    @pytest.mark.asyncio
    async def test_load_video_found(self):
        """Test load_video method when video exists."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_video = Mock(spec=Video)
        mock_repository.find_by_id = AsyncMock(return_value=mock_video)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.load_video("test_id")
        
        # Assert
        assert result == mock_video
        mock_repository.find_by_id.assert_called_once_with("test_id")

    @pytest.mark.asyncio
    async def test_load_video_not_found(self):
        """Test load_video method when video doesn't exist."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_repository.find_by_id = AsyncMock(return_value=None)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.load_video("nonexistent_id")
        
        # Assert
        assert result is None
        mock_repository.find_by_id.assert_called_once_with("nonexistent_id")

    @pytest.mark.asyncio
    async def test_save_transcription_new_video(self):
        """Test save_transcription method with new video."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_repository.find_by_id = AsyncMock(return_value=None)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        await adapter.save_transcription("test_id", "Test transcription")
        
        # Assert
        assert adapter._transcriptions["test_id"] == "Test transcription"
        mock_repository.find_by_id.assert_called_once_with("test_id")

    @pytest.mark.asyncio
    async def test_save_transcription_existing_video(self):
        """Test save_transcription method with existing video."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_video = Mock(spec=Video)
        mock_video.transcription = None
        mock_video.metadata = None
        mock_repository.find_by_id = AsyncMock(return_value=mock_video)
        mock_repository.save = AsyncMock()
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        await adapter.save_transcription("test_id", "Test transcription")
        
        # Assert
        assert adapter._transcriptions["test_id"] == "Test transcription"
        assert mock_video.transcription == "Test transcription"
        mock_repository.save.assert_called_once_with(mock_video)

    @pytest.mark.asyncio
    async def test_save_transcription_with_metadata(self):
        """Test save_transcription method with metadata."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_video = Mock(spec=Video)
        mock_video.transcription = None
        mock_video.metadata = {"existing": "data"}
        mock_repository.find_by_id = AsyncMock(return_value=mock_video)
        mock_repository.save = AsyncMock()
        adapter = JsonStorageAdapter(mock_repository)
        
        metadata = {"language": "pt", "provider": "whisper"}
        
        # Act
        await adapter.save_transcription("test_id", "Test transcription", metadata)
        
        # Assert
        assert adapter._transcriptions["test_id"] == "Test transcription"
        assert mock_video.transcription == "Test transcription"
        assert mock_video.metadata["language"] == "pt"
        assert mock_video.metadata["provider"] == "whisper"
        assert mock_video.metadata["existing"] == "data"  # Should preserve existing metadata

    @pytest.mark.asyncio
    async def test_save_transcription_with_metadata_no_existing_metadata(self):
        """Test save_transcription method with metadata when video has no metadata."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_video = Mock(spec=Video)
        mock_video.transcription = None
        # Simulate video without metadata attribute
        if hasattr(mock_video, 'metadata'):
            delattr(mock_video, 'metadata')
        mock_repository.find_by_id = AsyncMock(return_value=mock_video)
        mock_repository.save = AsyncMock()
        adapter = JsonStorageAdapter(mock_repository)
        
        metadata = {"language": "en"}
        
        # Act
        await adapter.save_transcription("test_id", "Test transcription", metadata)
        
        # Assert
        assert adapter._transcriptions["test_id"] == "Test transcription"
        assert mock_video.transcription == "Test transcription"
        assert mock_video.metadata == {"language": "en"}

    @pytest.mark.asyncio
    async def test_load_transcription_from_cache(self):
        """Test load_transcription method from cache."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        adapter = JsonStorageAdapter(mock_repository)
        adapter._transcriptions["test_id"] = "Cached transcription"
        
        # Act
        result = await adapter.load_transcription("test_id")
        
        # Assert
        assert result == "Cached transcription"
        # Should not call repository since it's cached
        mock_repository.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_load_transcription_from_video(self):
        """Test load_transcription method from video."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_video = Mock(spec=Video)
        mock_video.transcription = "Video transcription"
        mock_repository.find_by_id = AsyncMock(return_value=mock_video)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.load_transcription("test_id")
        
        # Assert
        assert result == "Video transcription"
        assert adapter._transcriptions["test_id"] == "Video transcription"  # Should cache it
        mock_repository.find_by_id.assert_called_once_with("test_id")

    @pytest.mark.asyncio
    async def test_load_transcription_video_without_transcription(self):
        """Test load_transcription method with video that has no transcription."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_video = Mock(spec=Video)
        mock_video.transcription = None
        mock_repository.find_by_id = AsyncMock(return_value=mock_video)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.load_transcription("test_id")
        
        # Assert
        assert result is None
        mock_repository.find_by_id.assert_called_once_with("test_id")

    @pytest.mark.asyncio
    async def test_load_transcription_video_not_found(self):
        """Test load_transcription method when video doesn't exist."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_repository.find_by_id = AsyncMock(return_value=None)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.load_transcription("nonexistent_id")
        
        # Assert
        assert result is None
        mock_repository.find_by_id.assert_called_once_with("nonexistent_id")

    @pytest.mark.asyncio
    async def test_list_videos_no_pagination(self):
        """Test list_videos method without pagination."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_videos = [Mock(spec=Video) for _ in range(5)]
        mock_repository.list_all = AsyncMock(return_value=mock_videos)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.list_videos()
        
        # Assert
        assert result == mock_videos
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_videos_with_limit(self):
        """Test list_videos method with limit."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_videos = [Mock(spec=Video) for _ in range(10)]
        mock_repository.list_all = AsyncMock(return_value=mock_videos)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.list_videos(limit=3)
        
        # Assert
        assert len(result) == 3
        assert result == mock_videos[:3]
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_videos_with_offset(self):
        """Test list_videos method with offset."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_videos = [Mock(spec=Video) for _ in range(10)]
        mock_repository.list_all = AsyncMock(return_value=mock_videos)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.list_videos(offset=5)
        
        # Assert
        assert len(result) == 5  # remaining videos after offset
        assert result == mock_videos[5:]
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_videos_with_limit_and_offset(self):
        """Test list_videos method with both limit and offset."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_videos = [Mock(spec=Video) for _ in range(20)]
        mock_repository.list_all = AsyncMock(return_value=mock_videos)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.list_videos(limit=5, offset=10)
        
        # Assert
        assert len(result) == 5
        assert result == mock_videos[10:15]
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_videos_offset_beyond_list(self):
        """Test list_videos method with offset beyond list length."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_videos = [Mock(spec=Video) for _ in range(5)]
        mock_repository.list_all = AsyncMock(return_value=mock_videos)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.list_videos(offset=10)
        
        # Assert
        assert len(result) == 0
        assert result == []
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_videos_empty_repository(self):
        """Test list_videos method with empty repository."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        mock_repository.list_all = AsyncMock(return_value=[])
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act
        result = await adapter.list_videos()
        
        # Assert
        assert len(result) == 0
        assert result == []
        mock_repository.list_all.assert_called_once()

    def test_transcription_cache_management(self):
        """Test transcription cache management."""
        # Arrange
        mock_repository = Mock(spec=VideoRepository)
        adapter = JsonStorageAdapter(mock_repository)
        
        # Act & Assert
        # Initially empty
        assert len(adapter._transcriptions) == 0
        
        # Add transcription
        adapter._transcriptions["id1"] = "transcription1"
        adapter._transcriptions["id2"] = "transcription2"
        
        assert len(adapter._transcriptions) == 2
        assert adapter._transcriptions["id1"] == "transcription1"
        assert adapter._transcriptions["id2"] == "transcription2"
