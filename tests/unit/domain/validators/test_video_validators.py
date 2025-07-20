"""
Testes unitários para validadores de vídeo.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
import os

from src.domain.validators.video_validators import (
    validate_video_id,
    validate_video_title,
    validate_video_duration,
    validate_video_sources,
    validate_video_file_format,
)
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestValidateVideoId:
    """Testes para validação de ID de vídeo."""
    
    def test_valid_ids(self):
        """Testa IDs válidos."""
        valid_ids = [
            "video123",
            "VIDEO_123",
            "video-test",
            "123",
            "a",
            "test_video-123",
            "A" * 255,  # Máximo permitido
        ]
        
        for video_id in valid_ids:
            # Não deve lançar exceção
            validate_video_id(video_id)
    
    def test_empty_id(self):
        """Testa ID vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_id("")
        
        assert exc_info.value.field == "id"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_id(self):
        """Testa ID apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_id("   ")
        
        assert exc_info.value.field == "id"
        assert "vazio" in exc_info.value.constraint
    
    def test_none_id(self):
        """Testa ID None."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_id(None)
        
        assert exc_info.value.field == "id"
    
    def test_too_long_id(self):
        """Testa ID muito longo."""
        long_id = "a" * 256  # Acima do limite de 255
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_id(long_id)
        
        assert exc_info.value.field == "id"
        assert "255 caracteres" in exc_info.value.constraint
        assert exc_info.value.details["current_length"] == 256
    
    def test_invalid_characters(self):
        """Testa caracteres inválidos no ID."""
        invalid_ids = [
            "video@123",
            "video 123",  # espaço
            "video#123",
            "video.123",
            "video/123",
            "video\\123",
            "video+123",
            "video=123",
            "vídeo123",  # caractere acentuado
        ]
        
        for video_id in invalid_ids:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_video_id(video_id)
            
            assert exc_info.value.field == "id"
            assert "apenas letras, números" in exc_info.value.constraint


class TestValidateVideoTitle:
    """Testes para validação de título de vídeo."""
    
    def test_valid_titles(self):
        """Testa títulos válidos."""
        valid_titles = [
            "Título do Vídeo",
            "Video Title with Special Characters: !@#$%^&*()",
            "Título com acentos: ção, ã, é, ü",
            "A" * 500,  # Máximo permitido
            "123",
            "Emoji test 🎥📹",
        ]
        
        for title in valid_titles:
            # Não deve lançar exceção
            validate_video_title(title)
    
    def test_empty_title(self):
        """Testa título vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_title("")
        
        assert exc_info.value.field == "title"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_title(self):
        """Testa título apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_title("   ")
        
        assert exc_info.value.field == "title"
        assert "vazio" in exc_info.value.constraint
    
    def test_none_title(self):
        """Testa título None."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_title(None)
        
        assert exc_info.value.field == "title"
    
    def test_too_long_title(self):
        """Testa título muito longo."""
        long_title = "a" * 501  # Acima do limite de 500
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_title(long_title)
        
        assert exc_info.value.field == "title"
        assert "500 caracteres" in exc_info.value.constraint
        assert exc_info.value.details["current_length"] == 501


class TestValidateVideoDuration:
    """Testes para validação de duração de vídeo."""
    
    def test_valid_durations(self):
        """Testa durações válidas."""
        valid_durations = [
            0.0,      # Zero permitido
            1.0,      # 1 segundo
            60.0,     # 1 minuto
            3600.0,   # 1 hora
            86400.0,  # 24 horas (máximo)
        ]
        
        for duration in valid_durations:
            # Não deve lançar exceção
            validate_video_duration(duration)
    
    def test_negative_duration(self):
        """Testa duração negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_duration(-1.0)
        
        assert exc_info.value.field == "duration"
        assert "negativa" in exc_info.value.constraint
    
    def test_too_long_duration(self):
        """Testa duração muito longa."""
        too_long = 86401.0  # Mais de 24 horas
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_duration(too_long)
        
        assert exc_info.value.field == "duration"
        assert "86400 segundos" in exc_info.value.constraint
        assert exc_info.value.details["max_duration_seconds"] == 86400


class TestValidateVideoSources:
    """Testes para validação de fontes de vídeo."""
    
    def test_valid_file_path(self):
        """Testa com arquivo válido."""
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Não deve lançar exceção
            validate_video_sources(temp_path, None)
        finally:
            os.unlink(temp_path)
    
    def test_valid_url(self):
        """Testa com URL válida."""
        # Não deve lançar exceção
        validate_video_sources(None, "https://youtube.com/watch?v=test123")
    
    def test_both_valid(self):
        """Testa com arquivo e URL válidos."""
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Não deve lançar exceção
            validate_video_sources(temp_path, "https://youtube.com/watch?v=test123")
        finally:
            os.unlink(temp_path)
    
    def test_no_sources(self):
        """Testa sem nenhuma fonte."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_sources(None, None)
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint
    
    def test_invalid_file_path(self):
        """Testa com arquivo inexistente."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_sources("/path/that/does/not/exist.mp4", None)
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint
        assert exc_info.value.details["file_exists"] is False
    
    def test_invalid_url_format(self):
        """Testa com URL inválida."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_sources(None, "not-a-url")
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint


class TestValidateVideoFileFormat:
    """Testes para validação de formato de arquivo."""
    
    def test_supported_formats(self):
        """Testa formatos suportados."""
        supported_files = [
            "/path/to/video.mp4",
            "/path/to/video.avi",
            "/path/to/video.mkv",
            "/path/to/video.mov",
            "/path/to/video.wmv",
            "/path/to/video.flv",
            "/path/to/video.webm",
            "/path/to/video.m4v",
            "/path/to/video.3gp",
            "/path/to/video.ogv",
            "/path/to/VIDEO.MP4",  # Case insensitive
        ]
        
        for file_path in supported_files:
            # Não deve lançar exceção
            validate_video_file_format(file_path)
    
    def test_unsupported_formats(self):
        """Testa formatos não suportados."""
        unsupported_files = [
            "/path/to/file.txt",
            "/path/to/file.pdf",
            "/path/to/file.jpg",
            "/path/to/file.mp3",
            "/path/to/file.wav",
            "/path/to/file.zip",
            "/path/to/file",  # Sem extensão
        ]
        
        for file_path in unsupported_files:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_video_file_format(file_path)
            
            assert exc_info.value.field == "file_format"
            assert "formato não suportado" in exc_info.value.constraint
            assert "supported_extensions" in exc_info.value.details