"""Testes para a entidade Video."""
import pytest
from src.domain.entities.video import Video


class TestVideoEntity:
    """Testes para a entidade Video."""
    
    def test_create_video(self):
        """Testa a criação de um vídeo."""
        video = Video(
            id="test_123",
            title="Vídeo de Teste",
            file_path="/tmp/test.mp4"
        )
        
        assert video.id == "test_123"
        assert video.title == "Vídeo de Teste"
        assert video.file_path == "/tmp/test.mp4"
        assert video.transcription is None
        assert video.scene_timestamps == []
    
    def test_video_with_transcription(self):
        """Testa vídeo com transcrição."""
        video = Video(
            id="test_456",
            title="Vídeo com Transcrição",
            file_path="/tmp/test2.mp4",
            transcription="Este é um vídeo de teste"
        )
        
        assert video.transcription == "Este é um vídeo de teste"
    
    def test_video_with_scenes(self):
        """Testa vídeo com timestamps de cenas."""
        scenes = [10.5, 25.3, 45.7]
        video = Video(
            id="test_789",
            title="Vídeo com Cenas",
            file_path="/tmp/test3.mp4",
            scene_timestamps=scenes
        )
        
        assert video.scene_timestamps == scenes
    
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
        assert "/videos/meu_video.mp4" in str_repr
