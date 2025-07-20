"""
Testes unitários para a entidade Video.
"""

import pytest
from datetime import datetime
from tempfile import NamedTemporaryFile
import os

from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestVideoCreation:
    """Testes para criação da entidade Video."""
    
    def test_create_valid_video_with_file(self):
        """Testa criação de vídeo válido com arquivo local."""
        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        try:
            video = Video(
                id="test_video_123",
                title="Vídeo de Teste",
                file_path=temp_path,
                duration=120.5
            )
            
            assert video.id == "test_video_123"
            assert video.title == "Vídeo de Teste"
            assert video.file_path == temp_path
            assert video.duration == 120.5
            assert video.is_local() is True
            assert video.is_remote() is False
            assert video.get_source() == temp_path
            assert isinstance(video.created_at, datetime)
            assert video.metadata == {}
        finally:
            os.unlink(temp_path)
    
    def test_create_valid_video_with_url(self):
        """Testa criação de vídeo válido com URL."""
        video = Video(
            id="youtube_video_456",
            title="Vídeo do YouTube",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            duration=180.0
        )
        
        assert video.id == "youtube_video_456"
        assert video.title == "Vídeo do YouTube"
        assert video.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert video.duration == 180.0
        assert video.is_local() is False
        assert video.is_remote() is True
        assert video.get_source() == "https://youtube.com/watch?v=dQw4w9WgXcQ"
    
    def test_create_video_with_both_sources(self):
        """Testa criação de vídeo com arquivo e URL."""
        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        try:
            video = Video(
                id="dual_source_789",
                title="Vídeo com Duas Fontes",
                file_path=temp_path,
                url="https://youtube.com/watch?v=test123",
                duration=300.0
            )
            
            assert video.is_local() is True
            assert video.is_remote() is True
            # get_source() prioriza arquivo local
            assert video.get_source() == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_create_video_with_metadata(self):
        """Testa criação de vídeo com metadados."""
        video = Video(
            id="meta_video_001",
            title="Vídeo com Metadados",
            url="https://youtube.com/watch?v=meta123",
            duration=60.0,
            metadata={"uploader": "Test Channel", "views": "1000"}
        )
        
        assert video.metadata["uploader"] == "Test Channel"
        assert video.metadata["views"] == "1000"
    
    def test_create_video_with_transcription(self):
        """Testa criação de vídeo com transcrição."""
        video = Video(
            id="transcribed_video_002",
            title="Vídeo Transcrito",
            url="https://youtube.com/watch?v=trans123",
            duration=90.0,
            transcription="Esta é a transcrição do vídeo."
        )
        
        assert video.transcription == "Esta é a transcrição do vídeo."


class TestVideoValidation:
    """Testes para validação da entidade Video."""
    
    def test_invalid_id_empty(self):
        """Testa ID vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="",
                title="Título Válido",
                url="https://youtube.com/watch?v=test123"
            )
        
        assert exc_info.value.field == "id"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_id_too_long(self):
        """Testa ID muito longo."""
        long_id = "a" * 256  # Acima do limite de 255
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id=long_id,
                title="Título Válido",
                url="https://youtube.com/watch?v=test123"
            )
        
        assert exc_info.value.field == "id"
        assert "255 caracteres" in exc_info.value.constraint
    
    def test_invalid_id_special_characters(self):
        """Testa ID com caracteres especiais."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="video@123",
                title="Título Válido",
                url="https://youtube.com/watch?v=test123"
            )
        
        assert exc_info.value.field == "id"
        assert "apenas letras, números" in exc_info.value.constraint
    
    def test_invalid_title_empty(self):
        """Testa título vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title="",
                url="https://youtube.com/watch?v=test123"
            )
        
        assert exc_info.value.field == "title"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_title_too_long(self):
        """Testa título muito longo."""
        long_title = "a" * 501  # Acima do limite de 500
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title=long_title,
                url="https://youtube.com/watch?v=test123"
            )
        
        assert exc_info.value.field == "title"
        assert "500 caracteres" in exc_info.value.constraint
    
    def test_invalid_duration_negative(self):
        """Testa duração negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title="Título Válido",
                url="https://youtube.com/watch?v=test123",
                duration=-10.0
            )
        
        assert exc_info.value.field == "duration"
        assert "negativa" in exc_info.value.constraint
    
    def test_invalid_duration_too_long(self):
        """Testa duração muito longa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title="Título Válido",
                url="https://youtube.com/watch?v=test123",
                duration=86401.0  # Mais de 24 horas
            )
        
        assert exc_info.value.field == "duration"
        assert "86400 segundos" in exc_info.value.constraint
    
    def test_invalid_sources_none(self):
        """Testa sem nenhuma fonte válida."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title="Título Válido",
                # Sem file_path nem url
            )
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint
    
    def test_invalid_sources_nonexistent_file(self):
        """Testa com arquivo inexistente."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title="Título Válido",
                file_path="/path/that/does/not/exist.mp4"
            )
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint
    
    def test_invalid_sources_invalid_url(self):
        """Testa com URL inválida."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            Video(
                id="valid_id_123",
                title="Título Válido",
                url="not-a-valid-url"
            )
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint


class TestVideoMethods:
    """Testes para métodos da entidade Video."""
    
    def test_is_local_with_file(self):
        """Testa is_local() com arquivo."""
        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        try:
            video = Video(
                id="local_video_123",
                title="Vídeo Local",
                file_path=temp_path
            )
            
            assert video.is_local() is True
        finally:
            os.unlink(temp_path)
    
    def test_is_local_without_file(self):
        """Testa is_local() sem arquivo."""
        video = Video(
            id="remote_video_123",
            title="Vídeo Remoto",
            url="https://youtube.com/watch?v=test123"
        )
        
        assert video.is_local() is False
    
    def test_is_remote_with_url(self):
        """Testa is_remote() com URL."""
        video = Video(
            id="remote_video_123",
            title="Vídeo Remoto",
            url="https://youtube.com/watch?v=test123"
        )
        
        assert video.is_remote() is True
    
    def test_is_remote_without_url(self):
        """Testa is_remote() sem URL."""
        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        try:
            video = Video(
                id="local_video_123",
                title="Vídeo Local",
                file_path=temp_path
            )
            
            assert video.is_remote() is False
        finally:
            os.unlink(temp_path)
    
    def test_get_source_priority(self):
        """Testa prioridade do get_source() (arquivo local tem prioridade)."""
        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        try:
            video = Video(
                id="dual_source_123",
                title="Vídeo com Duas Fontes",
                file_path=temp_path,
                url="https://youtube.com/watch?v=test123"
            )
            
            # Arquivo local tem prioridade
            assert video.get_source() == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_get_source_empty(self):
        """Testa get_source() quando não há fontes válidas."""
        # Este teste não pode ser executado porque a validação impede
        # a criação de vídeo sem fontes válidas
        pass


class TestVideoEdgeCases:
    """Testes para casos extremos da entidade Video."""
    
    def test_zero_duration(self):
        """Testa duração zero (permitida)."""
        video = Video(
            id="zero_duration_123",
            title="Vídeo com Duração Zero",
            url="https://youtube.com/watch?v=test123",
            duration=0.0
        )
        
        assert video.duration == 0.0
    
    def test_maximum_duration(self):
        """Testa duração máxima permitida (24 horas)."""
        video = Video(
            id="max_duration_123",
            title="Vídeo com Duração Máxima",
            url="https://youtube.com/watch?v=test123",
            duration=86400.0  # Exatamente 24 horas
        )
        
        assert video.duration == 86400.0
    
    def test_unicode_title(self):
        """Testa título com caracteres Unicode."""
        video = Video(
            id="unicode_title_123",
            title="Vídeo com Título Especial: 🎥 Ação & Emoção",
            url="https://youtube.com/watch?v=test123"
        )
        
        assert "🎥" in video.title
        assert "Ação" in video.title
    
    def test_maximum_id_length(self):
        """Testa ID com comprimento máximo permitido."""
        max_id = "a" * 255  # Exatamente o máximo
        
        video = Video(
            id=max_id,
            title="Vídeo com ID Máximo",
            url="https://youtube.com/watch?v=test123"
        )
        
        assert len(video.id) == 255
    
    def test_maximum_title_length(self):
        """Testa título com comprimento máximo permitido."""
        max_title = "a" * 500  # Exatamente o máximo
        
        video = Video(
            id="max_title_123",
            title=max_title,
            url="https://youtube.com/watch?v=test123"
        )
        
        assert len(video.title) == 500