"""
Testes para edge cases e boundary conditions dos validadores.
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
from src.domain.validators.url_validators import (
    validate_url_format,
    is_youtube_url,
    extract_youtube_video_id,
    validate_youtube_url,
)
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestBoundaryConditions:
    """Testes para condições de fronteira."""
    
    def test_id_exactly_255_characters(self):
        """Testa ID com exatamente 255 caracteres (limite)."""
        id_255 = "a" * 255
        # Não deve lançar exceção
        validate_video_id(id_255)
    
    def test_id_256_characters(self):
        """Testa ID com 256 caracteres (acima do limite)."""
        id_256 = "a" * 256
        with pytest.raises(InvalidVideoFormatError):
            validate_video_id(id_256)
    
    def test_title_exactly_500_characters(self):
        """Testa título com exatamente 500 caracteres (limite)."""
        title_500 = "a" * 500
        # Não deve lançar exceção
        validate_video_title(title_500)
    
    def test_title_501_characters(self):
        """Testa título com 501 caracteres (acima do limite)."""
        title_501 = "a" * 501
        with pytest.raises(InvalidVideoFormatError):
            validate_video_title(title_501)
    
    def test_duration_exactly_zero(self):
        """Testa duração exatamente zero (permitida)."""
        # Não deve lançar exceção
        validate_video_duration(0.0)
    
    def test_duration_exactly_24_hours(self):
        """Testa duração exatamente 24 horas (limite)."""
        # Não deve lançar exceção
        validate_video_duration(86400.0)
    
    def test_duration_just_over_24_hours(self):
        """Testa duração ligeiramente acima de 24 horas."""
        with pytest.raises(InvalidVideoFormatError):
            validate_video_duration(86400.1)
    
    def test_duration_negative_small(self):
        """Testa duração ligeiramente negativa."""
        with pytest.raises(InvalidVideoFormatError):
            validate_video_duration(-0.1)


class TestSpecialCharacters:
    """Testes para caracteres especiais."""
    
    def test_id_with_underscores_and_hyphens(self):
        """Testa ID com underscores e hífens (permitidos)."""
        valid_ids = [
            "video_123",
            "video-456",
            "video_test-123",
            "_video_",
            "-video-",
            "123_456-789",
        ]
        
        for video_id in valid_ids:
            # Não deve lançar exceção
            validate_video_id(video_id)
    
    def test_title_with_special_characters(self):
        """Testa título com caracteres especiais permitidos."""
        special_titles = [
            "Vídeo: Teste & Análise",
            "Tutorial #1 - Como fazer?",
            "Preço: R$ 100,00 (50% off!)",
            "Email: test@example.com",
            "Matemática: 2 + 2 = 4",
            "Programação: if (x > 0) { return true; }",
            "Unicode: 🎥 📹 🎬 ⭐",
            "Acentos: ção, ã, é, ü, ñ",
        ]
        
        for title in special_titles:
            # Não deve lançar exceção
            validate_video_title(title)
    
    def test_id_with_forbidden_characters(self):
        """Testa ID com caracteres proibidos."""
        forbidden_ids = [
            "video@123",
            "video 123",  # espaço
            "video#123",
            "video.123",
            "video/123",
            "video\\123",
            "video+123",
            "video=123",
            "video%123",
            "video&123",
            "video*123",
            "video(123)",
            "video[123]",
            "video{123}",
            "video|123",
            "video:123",
            "video;123",
            "video'123",
            'video"123',
            "video<123>",
            "video?123",
            "video!123",
            "vídeo123",  # acentuado
        ]
        
        for video_id in forbidden_ids:
            with pytest.raises(InvalidVideoFormatError):
                validate_video_id(video_id)


class TestUrlEdgeCases:
    """Testes para edge cases de URLs."""
    
    def test_url_with_port(self):
        """Testa URL com porta."""
        urls_with_port = [
            "https://localhost:8080/video",
            "http://example.com:3000/watch?v=123",
            "https://youtube.com:443/watch?v=test",
        ]
        
        for url in urls_with_port:
            # Não deve lançar exceção
            validate_url_format(url)
    
    def test_url_with_ip_address(self):
        """Testa URL com endereço IP."""
        ip_urls = [
            "https://192.168.1.1/video",
            "http://10.0.0.1:8080/watch",
            "https://127.0.0.1/test",
        ]
        
        for url in ip_urls:
            # Não deve lançar exceção
            validate_url_format(url)
    
    def test_youtube_url_variations(self):
        """Testa variações de URLs do YouTube."""
        youtube_variations = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=test123",
            "https://youtube.com/watch?v=abc123",
            "www.youtube.com/watch?v=def456",
            "youtube.com/watch?v=ghi789",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/test123",
            "youtu.be/abc123",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://youtube.com/embed/test123",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
            "https://youtube.com/v/test123",
        ]
        
        for url in youtube_variations:
            assert is_youtube_url(url) is True
            video_id = extract_youtube_video_id(url)
            assert video_id is not None
            assert len(video_id) > 0
    
    def test_youtube_video_id_formats(self):
        """Testa diferentes formatos de ID de vídeo do YouTube."""
        test_cases = [
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=abc123", "abc123"),
            ("https://youtube.com/watch?v=test_video-123", "test_video-123"),
            ("https://youtu.be/short_id", "short_id"),
            ("https://youtu.be/very-long-video-id-123", "very-long-video-id-123"),
        ]
        
        for url, expected_id in test_cases:
            extracted_id = extract_youtube_video_id(url)
            assert extracted_id == expected_id


class TestFilePathEdgeCases:
    """Testes para edge cases de caminhos de arquivo."""
    
    def test_file_path_with_spaces(self):
        """Testa caminho de arquivo com espaços."""
        with NamedTemporaryFile(delete=False, suffix='.mp4', prefix='video with spaces ') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Não deve lançar exceção
            validate_video_sources(temp_path, None)
        finally:
            os.unlink(temp_path)
    
    def test_file_path_with_unicode(self):
        """Testa caminho de arquivo com caracteres Unicode."""
        with NamedTemporaryFile(delete=False, suffix='.mp4', prefix='vídeo_测试_') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Não deve lançar exceção
            validate_video_sources(temp_path, None)
        finally:
            os.unlink(temp_path)
    
    def test_file_extensions_case_insensitive(self):
        """Testa extensões de arquivo case-insensitive."""
        extensions = [
            '.MP4', '.AVI', '.MKV', '.MOV', '.WMV',
            '.FLV', '.WEBM', '.M4V', '.3GP', '.OGV',
            '.Mp4', '.Avi', '.mKv', '.MoV', '.wMv',
        ]
        
        for ext in extensions:
            file_path = f"/path/to/video{ext}"
            # Não deve lançar exceção
            validate_video_file_format(file_path)


class TestErrorMessageQuality:
    """Testes para qualidade das mensagens de erro."""
    
    def test_id_error_includes_current_length(self):
        """Testa se erro de ID inclui comprimento atual."""
        long_id = "a" * 300
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_id(long_id)
        
        assert exc_info.value.field == "id"
        assert "255 caracteres" in exc_info.value.constraint
        assert exc_info.value.details["current_length"] == 300
    
    def test_title_error_includes_current_length(self):
        """Testa se erro de título inclui comprimento atual."""
        long_title = "a" * 600
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_title(long_title)
        
        assert exc_info.value.field == "title"
        assert "500 caracteres" in exc_info.value.constraint
        assert exc_info.value.details["current_length"] == 600
    
    def test_duration_error_includes_limits(self):
        """Testa se erro de duração inclui limites."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_duration(100000.0)
        
        assert exc_info.value.field == "duration"
        assert "86400 segundos" in exc_info.value.constraint
        assert exc_info.value.details["max_duration_seconds"] == 86400
        assert exc_info.value.details["max_duration_hours"] == 24.0
    
    def test_sources_error_includes_details(self):
        """Testa se erro de sources inclui detalhes específicos."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_sources("/nonexistent/file.mp4", "invalid-url")
        
        assert exc_info.value.field == "sources"
        assert "pelo menos um" in exc_info.value.constraint
        assert "file_path" in exc_info.value.details
        assert "url" in exc_info.value.details
        assert exc_info.value.details["file_exists"] is False
    
    def test_file_format_error_includes_supported_formats(self):
        """Testa se erro de formato inclui formatos suportados."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_video_file_format("/path/to/file.txt")
        
        assert exc_info.value.field == "file_format"
        assert "formato não suportado" in exc_info.value.constraint
        assert "supported_extensions" in exc_info.value.details
        assert ".mp4" in exc_info.value.details["supported_extensions"]
        assert ".txt" not in exc_info.value.details["supported_extensions"]


class TestValidationConsistency:
    """Testes para consistência entre validadores."""
    
    def test_video_entity_uses_same_validation(self):
        """Testa se entidade Video usa as mesmas validações."""
        from src.domain.entities.video import Video
        
        # Teste com ID inválido - deve falhar da mesma forma
        with pytest.raises(InvalidVideoFormatError) as exc_info_direct:
            validate_video_id("invalid@id")
        
        with pytest.raises(InvalidVideoFormatError) as exc_info_entity:
            Video(
                id="invalid@id",
                title="Título Válido",
                url="https://youtube.com/watch?v=test123"
            )
        
        # Ambos devem ter o mesmo tipo de erro
        assert exc_info_direct.value.field == exc_info_entity.value.field
        assert exc_info_direct.value.constraint == exc_info_entity.value.constraint
    
    def test_url_validation_consistency(self):
        """Testa consistência entre validações de URL."""
        invalid_url = "not-a-url"
        
        # Validação direta deve falhar
        with pytest.raises(InvalidVideoFormatError):
            validate_url_format(invalid_url)
        
        # Validação através de sources também deve falhar
        with pytest.raises(InvalidVideoFormatError):
            validate_video_sources(None, invalid_url)
    
    def test_youtube_url_validation_consistency(self):
        """Testa consistência entre validações de URL do YouTube."""
        youtube_url = "https://youtube.com/watch?v=test123"
        
        # Todas as funções devem ser consistentes
        assert is_youtube_url(youtube_url) is True
        assert extract_youtube_video_id(youtube_url) == "test123"
        
        # Validação específica não deve falhar
        validate_youtube_url(youtube_url)