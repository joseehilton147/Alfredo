"""Testes para a entidade Video."""
import pytest
from datetime import datetime

from src.domain.entities.video import Video


class TestVideoEntity:
    """Testes para a entidade Video."""

    def test_create_video(self):
        """Testa a criação de um vídeo local."""
        video = Video(
            id="test_123",
            title="Vídeo de Teste",
            file_path="/tmp/test.mp4"
        )

        assert video.id == "test_123"
        assert video.title == "Vídeo de Teste"
        assert video.file_path == "/tmp/test.mp4"
        assert video.url is None
        assert video.duration == 0.0
        assert video.created_at is not None
        assert isinstance(video.created_at, datetime)
        assert video.metadata == {}

    def test_create_video_with_url(self):
        """Testa criação de vídeo remoto."""
        video = Video(
            id="test_456",
            title="Vídeo Online",
            url="https://example.com/video.mp4"
        )

        assert video.id == "test_456"
        assert video.title == "Vídeo Online"
        assert video.url == "https://example.com/video.mp4"
        assert video.file_path is None

    def test_video_is_local(self):
        """Testa verificação se vídeo é local."""
        video_local = Video(
            id="test_1",
            title="Local",
            file_path="/tmp/video.mp4"
        )
        video_remote = Video(
            id="test_2",
            title="Remoto",
            url="https://example.com/video.mp4"
        )

        assert video_local.is_local() is True
        assert video_local.is_remote() is False
        assert video_remote.is_local() is False
        assert video_remote.is_remote() is True

    def test_video_get_source(self):
        """Testa obtenção da fonte do vídeo."""
        video_local = Video(
            id="test_1",
            title="Local",
            file_path="/tmp/video.mp4"
        )
        video_remote = Video(
            id="test_2",
            title="Remoto",
            url="https://example.com/video.mp4"
        )
        video_no_source = Video(
            id="test_3",
            title="Sem Fonte"
        )

        assert video_local.get_source() == "/tmp/video.mp4"
        assert video_remote.get_source() == "https://example.com/video.mp4"
        assert video_no_source.get_source() == ""

    def test_video_with_metadata(self):
        """Testa vídeo com metadados."""
        metadata = {"resolution": "1080p", "codec": "h264"}
        video = Video(
            id="test_meta",
            title="Com Metadados",
            file_path="/tmp/meta.mp4",
            metadata=metadata
        )

        assert video.metadata == metadata
        assert video.metadata["resolution"] == "1080p"

    def test_video_post_init(self):
        """Testa inicialização automática de campos."""
        video = Video(
            id="test_init",
            title="Test Init"
        )

        assert video.created_at is not None
        assert isinstance(video.created_at, datetime)
        assert video.metadata == {}
        assert video.duration == 0.0

    def test_video_str_representation(self):
        """Testa representação string do vídeo."""
        video = Video(
            id="test_001",
            title="Meu Vídeo",
            file_path="/videos/meu_video.mp4"
        )

        str_repr = str(video)
        assert "test_001" in str_repr
        assert "Meu Vídeo" in str_repr
