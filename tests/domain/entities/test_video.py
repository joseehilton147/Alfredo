import pytest
from datetime import datetime
from src.domain.entities.video import Video

class TestVideo:
    
    def test_video_creation_with_url(self):
        video = Video(
            id="test-123",
            title="Test Video",
            url="https://example.com/video.mp4"
        )
        assert video.title == "Test Video"
        assert video.is_remote() is True
        assert video.is_local() is False
        assert video.get_source() == "https://example.com/video.mp4"
    
    def test_video_creation_with_file_path(self):
        video = Video(
            id="test-456",
            title="Local Video",
            file_path="/path/to/video.mp4"
        )
        assert video.is_local() is True
        assert video.is_remote() is False
        assert video.get_source() == "/path/to/video.mp4"
    
    def test_video_post_init(self):
        video = Video(id="test-789", title="Test")
        assert video.created_at is not None
        assert isinstance(video.metadata, dict)
