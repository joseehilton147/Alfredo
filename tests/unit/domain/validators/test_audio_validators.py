"""
Testes unitários para validadores de áudio.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
import os

from src.domain.validators.audio_validators import (
    validate_audio_file_path,
    validate_audio_duration,
    validate_audio_format,
    validate_audio_file_format,
    validate_audio_sample_rate,
    validate_audio_channels,
)
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestValidateAudioFilePath:
    """Testes para validação de caminho de arquivo de áudio."""
    
    def test_valid_file_paths(self):
        """Testa caminhos de arquivo válidos."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Não deve lançar exceção
            validate_audio_file_path(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_file_path(self):
        """Testa caminho vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_path("")
        
        assert exc_info.value.field == "audio_file_path"
        assert "vazio" in exc_info.value.constraint
    
    def test_whitespace_only_path(self):
        """Testa caminho apenas com espaços."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_path("   ")
        
        assert exc_info.value.field == "audio_file_path"
        assert "vazio" in exc_info.value.constraint
    
    def test_nonexistent_file(self):
        """Testa arquivo inexistente."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_path("/path/that/does/not/exist.wav")
        
        assert exc_info.value.field == "audio_file_path"
        assert "deve existir" in exc_info.value.constraint
        assert exc_info.value.details["file_exists"] is False
    
    def test_directory_instead_of_file(self):
        """Testa diretório em vez de arquivo."""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_audio_file_path(temp_dir)
            
            assert exc_info.value.field == "audio_file_path"
            assert "arquivo válido" in exc_info.value.constraint
    
    def test_unsupported_file_extension(self):
        """Testa extensão não suportada."""
        with NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_audio_file_path(temp_path)
            
            assert exc_info.value.field == "audio_file_format"
            assert "não suportado" in exc_info.value.constraint
        finally:
            os.unlink(temp_path)


class TestValidateAudioDuration:
    """Testes para validação de duração de áudio."""
    
    def test_valid_durations(self):
        """Testa durações válidas."""
        valid_durations = [0.0, 1.0, 60.0, 3600.0, 86400.0]  # 0s a 24h
        
        for duration in valid_durations:
            # Não deve lançar exceção
            validate_audio_duration(duration)
    
    def test_negative_duration(self):
        """Testa duração negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_duration(-1.0)
        
        assert exc_info.value.field == "audio_duration"
        assert "negativa" in exc_info.value.constraint
    
    def test_too_long_duration(self):
        """Testa duração muito longa."""
        too_long = 86401.0  # Mais de 24 horas
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_duration(too_long)
        
        assert exc_info.value.field == "audio_duration"
        assert "86400 segundos" in exc_info.value.constraint
        assert exc_info.value.details["max_duration_seconds"] == 86400


class TestValidateAudioFormat:
    """Testes para validação de formato de áudio."""
    
    def test_supported_formats(self):
        """Testa formatos suportados."""
        supported_formats = ['wav', 'mp3', 'flac', 'aac', 'ogg', 'm4a', 'wma']
        
        for format_name in supported_formats:
            # Não deve lançar exceção
            validate_audio_format(format_name)
            
            # Testa case insensitive
            validate_audio_format(format_name.upper())
    
    def test_unsupported_format(self):
        """Testa formato não suportado."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_format("xyz")
        
        assert exc_info.value.field == "audio_format"
        assert "não suportado" in exc_info.value.constraint
        assert "xyz" in str(exc_info.value.details["detected_format"])
    
    def test_format_with_whitespace(self):
        """Testa formato com espaços."""
        # Deve funcionar (espaços são removidos)
        validate_audio_format("  wav  ")


class TestValidateAudioFileFormat:
    """Testes para validação de formato de arquivo de áudio."""
    
    def test_supported_extensions(self):
        """Testa extensões suportadas."""
        supported_extensions = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        
        for ext in supported_extensions:
            test_path = f"/path/to/audio{ext}"
            # Não deve lançar exceção
            validate_audio_file_format(test_path)
            
            # Testa case insensitive
            test_path_upper = f"/path/to/audio{ext.upper()}"
            validate_audio_file_format(test_path_upper)
    
    def test_unsupported_extension(self):
        """Testa extensão não suportada."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_format("/path/to/file.txt")
        
        assert exc_info.value.field == "audio_file_format"
        assert "não suportado" in exc_info.value.constraint
        assert ".txt" in str(exc_info.value.details["detected_extension"])
    
    def test_no_extension(self):
        """Testa arquivo sem extensão."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_file_format("/path/to/file")
        
        assert exc_info.value.field == "audio_file_format"
        assert "não suportado" in exc_info.value.constraint


class TestValidateAudioSampleRate:
    """Testes para validação de taxa de amostragem."""
    
    def test_valid_sample_rates(self):
        """Testa taxas de amostragem válidas."""
        valid_rates = [8000, 16000, 22050, 44100, 48000, 96000, 192000]
        
        for rate in valid_rates:
            # Não deve lançar exceção
            validate_audio_sample_rate(rate)
    
    def test_none_sample_rate(self):
        """Testa taxa None (permitida)."""
        # Não deve lançar exceção
        validate_audio_sample_rate(None)
    
    def test_zero_sample_rate(self):
        """Testa taxa zero."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_sample_rate(0)
        
        assert exc_info.value.field == "audio_sample_rate"
        assert "positiva" in exc_info.value.constraint
    
    def test_negative_sample_rate(self):
        """Testa taxa negativa."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_sample_rate(-1000)
        
        assert exc_info.value.field == "audio_sample_rate"
        assert "positiva" in exc_info.value.constraint
    
    def test_uncommon_sample_rate(self):
        """Testa taxa não comum (mas válida)."""
        # Não deve lançar exceção, apenas não é comum
        validate_audio_sample_rate(11025)


class TestValidateAudioChannels:
    """Testes para validação de número de canais."""
    
    def test_valid_channels(self):
        """Testa números de canais válidos."""
        valid_channels = [1, 2, 4, 6, 8]  # Mono, estéreo, quadri, 5.1, 7.1
        
        for channels in valid_channels:
            # Não deve lançar exceção
            validate_audio_channels(channels)
    
    def test_none_channels(self):
        """Testa canais None (permitido)."""
        # Não deve lançar exceção
        validate_audio_channels(None)
    
    def test_zero_channels(self):
        """Testa zero canais."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_channels(0)
        
        assert exc_info.value.field == "audio_channels"
        assert "positivo" in exc_info.value.constraint
    
    def test_negative_channels(self):
        """Testa número negativo de canais."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_channels(-1)
        
        assert exc_info.value.field == "audio_channels"
        assert "positivo" in exc_info.value.constraint
    
    def test_too_many_channels(self):
        """Testa muitos canais."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            validate_audio_channels(16)  # Mais que 8
        
        assert exc_info.value.field == "audio_channels"
        assert "8 canais" in exc_info.value.constraint
        assert exc_info.value.details["max_channels"] == 8


class TestAudioValidatorsEdgeCases:
    """Testes para casos extremos dos validadores de áudio."""
    
    def test_boundary_duration_values(self):
        """Testa valores limítrofes de duração."""
        # Valores exatos nos limites
        validate_audio_duration(0.0)      # Mínimo
        validate_audio_duration(86400.0)  # Máximo (24h)
        
        # Valores logo fora dos limites
        with pytest.raises(InvalidVideoFormatError):
            validate_audio_duration(-0.1)   # Abaixo do mínimo
        
        with pytest.raises(InvalidVideoFormatError):
            validate_audio_duration(86400.1) # Acima do máximo
    
    def test_format_case_sensitivity(self):
        """Testa sensibilidade a maiúsculas/minúsculas."""
        test_cases = ['wav', 'WAV', 'Wav', 'wAv']
        
        for format_case in test_cases:
            # Todos devem ser aceitos
            validate_audio_format(format_case)
    
    def test_file_path_with_spaces(self):
        """Testa caminho com espaços."""
        with NamedTemporaryFile(delete=False, suffix='.wav', 
                               prefix='audio with spaces ') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Não deve lançar exceção
            validate_audio_file_path(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_unicode_file_path(self):
        """Testa caminho com caracteres Unicode."""
        # Criar arquivo temporário com nome Unicode
        import tempfile
        temp_dir = tempfile.gettempdir()
        unicode_path = os.path.join(temp_dir, "áudio_teste_🎵.wav")
        
        # Criar arquivo temporário
        with open(unicode_path, 'w') as f:
            f.write("")
        
        try:
            # Não deve lançar exceção
            validate_audio_file_path(unicode_path)
        finally:
            if os.path.exists(unicode_path):
                os.unlink(unicode_path)