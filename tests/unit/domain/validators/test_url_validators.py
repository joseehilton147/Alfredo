"""
Testes unitários para validadores de URL.
"""

import pytest

from src.domain.validators.url_validators import (
    validate_url_format,
    is_youtube_url,
    is_supported_video_url,
    extract_youtube_video_id,
    validate_youtube_url,
)
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestValidateUrlFormat:
    """Testes para validação de formato de URL."""
    
    def test_valid_urls(self):
        """Testa URLs válidas."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=test123",
            "https://example.com/path/to/video",
            "http://localhost:8080/video",
            "https://sub.domain.com/video.mp4",
            "https://192.168.1.1/video",
        ]
        
        for url in valid_urls:
            # Não deve lançar exceção
            validate_url_format(url)
    
    def test_empty_url(self):
        """Testa URL vazia."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_url_format("")
        
        assert exc_info.value.field == "url"
        assert "vazia" in exc_info.value.constraint
    
    def test_whitespace_only_url(self):
        """Testa URL apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_url_format("   ")
        
        assert exc_info.value.field == "url"
        assert "vazia" in exc_info.value.constraint
    
    def test_none_url(self):
        """Testa URL None."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_url_format(None)
        
        assert exc_info.value.field == "url"
    
    def test_no_protocol(self):
        """Testa URL sem protocolo."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_url_format("www.youtube.com/watch?v=test")
        
        assert exc_info.value.field == "url"
        assert "http://" in exc_info.value.constraint
    
    def test_invalid_protocol(self):
        """Testa protocolo inválido."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_url_format("ftp://example.com/video")
        
        assert exc_info.value.field == "url"
        assert "http://" in exc_info.value.constraint
    
    def test_no_domain(self):
        """Testa URL sem domínio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_url_format("https://")
        
        assert exc_info.value.field == "url"
        assert "domínio válido" in exc_info.value.constraint
    
    def test_invalid_domain_format(self):
        """Testa formato de domínio inválido."""
        invalid_urls = [
            "https://.com/video",
            "https://-.com/video",
            "https://domain-.com/video",
        ]
        
        for url in invalid_urls:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_url_format(url)
            
            assert exc_info.value.field == "url"


class TestIsYoutubeUrl:
    """Testes para detecção de URLs do YouTube."""
    
    def test_youtube_urls(self):
        """Testa URLs válidas do YouTube."""
        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=test123",
            "https://youtube.com/watch?v=abc123",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/test123",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
            "www.youtube.com/watch?v=test123",  # Sem protocolo
            "youtube.com/watch?v=test123",
        ]
        
        for url in youtube_urls:
            assert is_youtube_url(url) is True
    
    def test_non_youtube_urls(self):
        """Testa URLs que não são do YouTube."""
        non_youtube_urls = [
            "https://vimeo.com/123456789",
            "https://dailymotion.com/video/test",
            "https://example.com/video.mp4",
            "https://facebook.com/video/123",
            "",
            None,
            "not-a-url",
        ]
        
        for url in non_youtube_urls:
            assert is_youtube_url(url) is False


class TestIsSupportedVideoUrl:
    """Testes para detecção de URLs de plataformas suportadas."""
    
    def test_supported_urls(self):
        """Testa URLs de plataformas suportadas."""
        supported_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/test123",
            "youtube.com/watch?v=abc123",
        ]
        
        for url in supported_urls:
            assert is_supported_video_url(url) is True
    
    def test_unsupported_urls(self):
        """Testa URLs de plataformas não suportadas."""
        unsupported_urls = [
            "https://vimeo.com/123456789",
            "https://dailymotion.com/video/test",
            "https://example.com/video.mp4",
            "",
            None,
            "not-a-url",
        ]
        
        for url in unsupported_urls:
            assert is_supported_video_url(url) is False


class TestExtractYoutubeVideoId:
    """Testes para extração de ID de vídeo do YouTube."""
    
    def test_extract_from_watch_url(self):
        """Testa extração de URL watch."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://youtube.com/watch?v=test123", "test123"),
            ("https://youtube.com/watch?v=abc-123_def", "abc-123_def"),
        ]
        
        for url, expected_id in test_cases:
            assert extract_youtube_video_id(url) == expected_id
    
    def test_extract_from_short_url(self):
        """Testa extração de URL curta (youtu.be)."""
        test_cases = [
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://youtu.be/test123", "test123"),
            ("youtu.be/abc-123_def", "abc-123_def"),
        ]
        
        for url, expected_id in test_cases:
            assert extract_youtube_video_id(url) == expected_id
    
    def test_extract_from_embed_url(self):
        """Testa extração de URL embed."""
        test_cases = [
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://youtube.com/embed/test123", "test123"),
        ]
        
        for url, expected_id in test_cases:
            assert extract_youtube_video_id(url) == expected_id
    
    def test_extract_from_v_url(self):
        """Testa extração de URL /v/."""
        test_cases = [
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://youtube.com/v/test123", "test123"),
        ]
        
        for url, expected_id in test_cases:
            assert extract_youtube_video_id(url) == expected_id
    
    def test_extract_from_invalid_url(self):
        """Testa extração de URLs inválidas."""
        invalid_urls = [
            "https://vimeo.com/123456789",
            "https://example.com/video",
            "not-a-url",
            "",
            None,
        ]
        
        for url in invalid_urls:
            assert extract_youtube_video_id(url) is None


class TestValidateYoutubeUrl:
    """Testes para validação específica de URLs do YouTube."""
    
    def test_valid_youtube_urls(self):
        """Testa URLs válidas do YouTube."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/test123",
            "http://youtube.com/watch?v=abc123",
        ]
        
        for url in valid_urls:
            # Não deve lançar exceção
            validate_youtube_url(url)
    
    def test_invalid_format(self):
        """Testa URLs com formato inválido."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_youtube_url("not-a-url")
        
        assert exc_info.value.field == "url"
    
    def test_non_youtube_url(self):
        """Testa URL válida mas não do YouTube."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_youtube_url("https://vimeo.com/123456789")
        
        assert exc_info.value.field == "url"
        assert "YouTube" in exc_info.value.constraint
    
    def test_youtube_url_without_video_id(self):
        """Testa URL do YouTube sem ID de vídeo válido."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_youtube_url("https://youtube.com/watch?v=")
        
        assert exc_info.value.field == "url"
        assert "extrair ID" in exc_info.value.constraint