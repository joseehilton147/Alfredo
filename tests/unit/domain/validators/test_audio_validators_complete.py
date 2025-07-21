"""
Testes completos para validadores de áudio para aumentar cobertura.

Testa todas as funções de validação de áudio cobrindo todos os cenários
possíveis e branches de código.
"""

import pytest
import tempfile
from pathlib import Path

from src.domain.validators.audio_validators import (
    validate_audio_file_path,
    validate_audio_duration,
    validate_audio_format,
    validate_audio_file_format,
    validate_audio_sample_rate,
    validate_audio_channels
)
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestValidateAudioFilePathComplete:
    """Testes completos para validate_audio_file_path."""
    
    def test_valid_audio_file_with_temp_file(self):
        """Testa validação com arquivo temporário real."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
            temp_path = temp_file.name
            # Deve passar sem erro
            validate_audio_file_path(temp_path)
    
    def test_empty_path_validation(self):
        """Testa validação de caminho vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_path("")
        
        error = exc_info.value
        assert error.field == "audio_file_path"
        assert "vazio" in error.constraint
    
    def test_whitespace_only_path(self):
        """Testa validação de caminho apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_path("   ")
        
        error = exc_info.value
        assert error.field == "audio_file_path"
        assert "vazio" in error.constraint
    
    def test_nonexistent_file_path(self):
        """Testa validação de arquivo inexistente."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_path("/path/to/nonexistent/file.wav")
        
        error = exc_info.value
        assert error.field == "audio_file_path"
        assert "existir" in error.constraint
        assert error.details["file_exists"] is False
    
    def test_directory_instead_of_file(self):
        """Testa validação quando path é diretório."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_audio_file_path(temp_dir)
            
            error = exc_info.value
            assert error.field == "audio_file_path"
            assert "arquivo válido" in error.constraint


class TestValidateAudioDurationComplete:
    """Testes completos para validate_audio_duration."""
    
    def test_valid_durations_range(self):
        """Testa durações válidas em diferentes faixas."""
        valid_durations = [0.1, 1.0, 30.0, 60.0, 3600.0, 7200.0]
        for duration in valid_durations:
            # Deve passar sem erro
            validate_audio_duration(duration)
    
    def test_negative_duration(self):
        """Testa duração negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_duration(-1.0)
        
        error = exc_info.value
        assert error.field == "audio_duration"
        assert "positiva" in error.constraint
    
    def test_zero_duration(self):
        """Testa duração zero."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_duration(0.0)
        
        error = exc_info.value
        assert error.field == "audio_duration"
        assert "positiva" in error.constraint
    
    def test_too_long_duration(self):
        """Testa duração muito longa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_duration(7201.0)  # Mais de 2 horas
        
        error = exc_info.value
        assert error.field == "audio_duration"
        assert "máximo" in error.constraint
    
    def test_edge_case_maximum_duration(self):
        """Testa duração no limite máximo."""
        # Deve passar sem erro
        validate_audio_duration(7200.0)  # Exatamente 2 horas


class TestValidateAudioFormatComplete:
    """Testes completos para validate_audio_format."""
    
    def test_supported_formats_comprehensive(self):
        """Testa todos os formatos suportados."""
        supported_formats = [
            "mp3", "wav", "ogg", "flac", "m4a", "aac", "wma",
            "MP3", "WAV", "OGG", "FLAC", "M4A", "AAC", "WMA"
        ]
        
        for format_name in supported_formats:
            # Deve passar sem erro
            validate_audio_format(format_name)
    
    def test_unsupported_formats(self):
        """Testa formatos não suportados."""
        unsupported_formats = ["mp4", "avi", "mkv", "mov", "txt", "pdf"]
        
        for format_name in unsupported_formats:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_audio_format(format_name)
            
            error = exc_info.value
            assert error.field == "audio_format"
            assert "suportado" in error.constraint
    
    def test_empty_format(self):
        """Testa formato vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_format("")
        
        error = exc_info.value
        assert error.field == "audio_format"
        assert "vazio" in error.constraint
    
    def test_format_with_whitespace(self):
        """Testa formato com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_format("  mp3  ")
        
        error = exc_info.value
        assert error.field == "audio_format"


class TestValidateAudioFileFormatComplete:
    """Testes completos para validate_audio_file_format."""
    
    def test_supported_extensions_comprehensive(self):
        """Testa todas as extensões suportadas."""
        supported_paths = [
            "audio.mp3", "audio.wav", "audio.ogg", "audio.flac",
            "audio.m4a", "audio.aac", "audio.wma",
            "AUDIO.MP3", "AUDIO.WAV", "AUDIO.OGG"
        ]
        
        for file_path in supported_paths:
            # Deve passar sem erro
            validate_audio_file_format(file_path)
    
    def test_unsupported_extensions(self):
        """Testa extensões não suportadas."""
        unsupported_paths = [
            "video.mp4", "video.avi", "document.txt", "image.jpg"
        ]
        
        for file_path in unsupported_paths:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_audio_file_format(file_path)
            
            error = exc_info.value
            assert error.field == "audio_file_format"
            assert "suportada" in error.constraint
    
    def test_no_extension(self):
        """Testa arquivo sem extensão."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_format("audiofile")
        
        error = exc_info.value
        assert error.field == "audio_file_format"
        assert "extensão" in error.constraint
    
    def test_multiple_dots_in_filename(self):
        """Testa nome de arquivo com múltiplos pontos."""
        # Deve passar sem erro
        validate_audio_file_format("my.audio.file.mp3")


class TestValidateAudioSampleRateComplete:
    """Testes completos para validate_audio_sample_rate."""
    
    def test_valid_sample_rates_comprehensive(self):
        """Testa todas as taxas de amostragem válidas."""
        valid_rates = [8000, 16000, 22050, 44100, 48000, 96000, 192000]
        
        for rate in valid_rates:
            # Deve passar sem erro
            validate_audio_sample_rate(rate)
    
    def test_none_sample_rate(self):
        """Testa taxa de amostragem None."""
        # Deve passar sem erro (permitido)
        validate_audio_sample_rate(None)
    
    def test_zero_sample_rate(self):
        """Testa taxa de amostragem zero."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_sample_rate(0)
        
        error = exc_info.value
        assert error.field == "audio_sample_rate"
        assert "positiva" in error.constraint
    
    def test_negative_sample_rate(self):
        """Testa taxa de amostragem negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_sample_rate(-1000)
        
        error = exc_info.value
        assert error.field == "audio_sample_rate"
        assert "positiva" in error.constraint
    
    def test_uncommon_sample_rate_warning(self):
        """Testa taxa de amostragem incomum."""
        uncommon_rates = [7999, 13000, 100000]
        
        for rate in uncommon_rates:
            # Deve passar mas com warning (dependendo da implementação)
            validate_audio_sample_rate(rate)


class TestValidateAudioChannelsComplete:
    """Testes completos para validate_audio_channels."""
    
    def test_valid_channels_comprehensive(self):
        """Testa todos os números de canais válidos."""
        valid_channels = [1, 2, 6, 8]  # Mono, stereo, 5.1, 7.1
        
        for channels in valid_channels:
            # Deve passar sem erro
            validate_audio_channels(channels)
    
    def test_none_channels(self):
        """Testa número de canais None."""
        # Deve passar sem erro (permitido)
        validate_audio_channels(None)
    
    def test_zero_channels(self):
        """Testa zero canais."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_channels(0)
        
        error = exc_info.value
        assert error.field == "audio_channels"
        assert "positivo" in error.constraint
    
    def test_negative_channels(self):
        """Testa número de canais negativo."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_channels(-1)
        
        error = exc_info.value
        assert error.field == "audio_channels"
        assert "positivo" in error.constraint
    
    def test_too_many_channels(self):
        """Testa número excessivo de canais."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_channels(17)  # Mais que 16 canais
        
        error = exc_info.value
        assert error.field == "audio_channels"
        assert "máximo" in error.constraint
    
    def test_edge_case_maximum_channels(self):
        """Testa número máximo de canais."""
        # Deve passar sem erro
        validate_audio_channels(16)  # Máximo permitido
