"""
Testes unitários para a entidade AudioTrack.
"""

import pytest
from datetime import datetime
from tempfile import NamedTemporaryFile
import os

from src.domain.entities.audio_track import AudioTrack
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


class TestAudioTrackCreation:
    """Testes para criação da entidade AudioTrack."""
    
    def test_create_valid_audio_track(self):
        """Testa criação de AudioTrack válido."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(
                file_path=temp_path,
                duration=120.5,
                sample_rate=44100,
                channels=2,
                format="wav",
                size_bytes=1024000
            )
            
            assert audio.file_path == temp_path
            assert audio.duration == 120.5
            assert audio.sample_rate == 44100
            assert audio.channels == 2
            assert audio.format == "wav"
            assert audio.size_bytes == 1024000
            assert isinstance(audio.created_at, datetime)
            assert audio.metadata == {}
        finally:
            os.unlink(temp_path)
    
    def test_create_audio_track_minimal(self):
        """Testa criação de AudioTrack com campos mínimos."""
        with NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(file_path=temp_path)
            
            assert audio.file_path == temp_path
            assert audio.duration == 0.0
            assert audio.sample_rate is None
            assert audio.channels is None
            assert audio.format is None
            assert audio.size_bytes is None
            assert isinstance(audio.created_at, datetime)
        finally:
            os.unlink(temp_path)
    
    def test_create_audio_track_with_metadata(self):
        """Testa criação de AudioTrack com metadados."""
        with NamedTemporaryFile(delete=False, suffix='.flac') as temp_file:
            temp_path = temp_file.name
        
        try:
            metadata = {"encoder": "ffmpeg", "bitrate": "320kbps"}
            audio = AudioTrack(
                file_path=temp_path,
                duration=180.0,
                metadata=metadata,
                source_video_id="video_123"
            )
            
            assert audio.metadata == metadata
            assert audio.source_video_id == "video_123"
        finally:
            os.unlink(temp_path)


class TestAudioTrackValidation:
    """Testes para validação da entidade AudioTrack."""
    
    def test_invalid_file_path_empty(self):
        """Testa caminho de arquivo vazio."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            AudioTrack(file_path="")
        
        assert exc_info.value.field == "audio_file_path"
        assert "vazio" in exc_info.value.constraint
    
    def test_invalid_file_path_nonexistent(self):
        """Testa arquivo inexistente."""
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            AudioTrack(file_path="/path/that/does/not/exist.wav")
        
        assert exc_info.value.field == "audio_file_path"
        assert "deve existir" in exc_info.value.constraint
    
    def test_invalid_duration_negative(self):
        """Testa duração negativa."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                AudioTrack(file_path=temp_path, duration=-10.0)
            
            assert exc_info.value.field == "audio_duration"
            assert "negativa" in exc_info.value.constraint
        finally:
            os.unlink(temp_path)
    
    def test_invalid_duration_too_long(self):
        """Testa duração muito longa."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                AudioTrack(file_path=temp_path, duration=86401.0)  # Mais de 24h
            
            assert exc_info.value.field == "audio_duration"
            assert "86400 segundos" in exc_info.value.constraint
        finally:
            os.unlink(temp_path)
    
    def test_invalid_format_unsupported(self):
        """Testa formato não suportado."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                AudioTrack(file_path=temp_path, format="xyz")
            
            assert exc_info.value.field == "audio_format"
            assert "não suportado" in exc_info.value.constraint
        finally:
            os.unlink(temp_path)
    
    def test_invalid_file_extension(self):
        """Testa extensão de arquivo não suportada."""
        with NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_path = temp_file.name
        
        try:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                AudioTrack(file_path=temp_path)
            
            assert exc_info.value.field == "audio_file_format"
            assert "não suportado" in exc_info.value.constraint
        finally:
            os.unlink(temp_path)


class TestAudioTrackMethods:
    """Testes para métodos da entidade AudioTrack."""
    
    def test_get_file_size_mb(self):
        """Testa cálculo do tamanho em MB."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            # 2MB = 2 * 1024 * 1024 bytes = 2097152 bytes
            audio = AudioTrack(file_path=temp_path, size_bytes=2097152)  # Exatamente 2MB
            assert audio.get_file_size_mb() == 2.0
            
            audio_no_size = AudioTrack(file_path=temp_path)
            assert audio_no_size.get_file_size_mb() == 0.0
        finally:
            os.unlink(temp_path)
    
    def test_get_duration_formatted(self):
        """Testa formatação da duração."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(file_path=temp_path, duration=125.0)  # 2:05
            assert audio.get_duration_formatted() == "02:05"
            
            audio_short = AudioTrack(file_path=temp_path, duration=45.0)  # 0:45
            assert audio_short.get_duration_formatted() == "00:45"
        finally:
            os.unlink(temp_path)
    
    def test_is_stereo(self):
        """Testa verificação de áudio estéreo."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio_stereo = AudioTrack(file_path=temp_path, channels=2)
            assert audio_stereo.is_stereo() is True
            
            audio_mono = AudioTrack(file_path=temp_path, channels=1)
            assert audio_mono.is_stereo() is False
            
            audio_no_channels = AudioTrack(file_path=temp_path)
            assert audio_no_channels.is_stereo() is False
        finally:
            os.unlink(temp_path)
    
    def test_is_mono(self):
        """Testa verificação de áudio mono."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio_mono = AudioTrack(file_path=temp_path, channels=1)
            assert audio_mono.is_mono() is True
            
            audio_stereo = AudioTrack(file_path=temp_path, channels=2)
            assert audio_stereo.is_mono() is False
            
            audio_no_channels = AudioTrack(file_path=temp_path)
            assert audio_no_channels.is_mono() is False
        finally:
            os.unlink(temp_path)
    
    def test_get_quality_info(self):
        """Testa informações de qualidade."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Áudio de alta qualidade
            audio_hq = AudioTrack(file_path=temp_path, sample_rate=44100, channels=2)
            quality = audio_hq.get_quality_info()
            assert quality["sample_rate_quality"] == "Alta"
            assert quality["channel_type"] == "Estéreo"
            
            # Áudio de qualidade média
            audio_mq = AudioTrack(file_path=temp_path, sample_rate=22050, channels=1)
            quality = audio_mq.get_quality_info()
            assert quality["sample_rate_quality"] == "Média"
            assert quality["channel_type"] == "Mono"
            
            # Áudio de baixa qualidade
            audio_lq = AudioTrack(file_path=temp_path, sample_rate=8000)
            quality = audio_lq.get_quality_info()
            assert quality["sample_rate_quality"] == "Baixa"
        finally:
            os.unlink(temp_path)


class TestAudioTrackEdgeCases:
    """Testes para casos extremos da entidade AudioTrack."""
    
    def test_zero_duration(self):
        """Testa duração zero (permitida)."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(file_path=temp_path, duration=0.0)
            assert audio.duration == 0.0
        finally:
            os.unlink(temp_path)
    
    def test_maximum_duration(self):
        """Testa duração máxima permitida (24 horas)."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(file_path=temp_path, duration=86400.0)  # Exatamente 24h
            assert audio.duration == 86400.0
        finally:
            os.unlink(temp_path)
    
    def test_supported_formats(self):
        """Testa todos os formatos suportados."""
        supported_extensions = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
        
        for ext in supported_extensions:
            with NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Não deve lançar exceção
                audio = AudioTrack(file_path=temp_path)
                assert audio.file_path == temp_path
            finally:
                os.unlink(temp_path)
    
    def test_high_sample_rates(self):
        """Testa taxas de amostragem altas."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(file_path=temp_path, sample_rate=192000)
            quality = audio.get_quality_info()
            assert quality["sample_rate_quality"] == "Alta"
        finally:
            os.unlink(temp_path)
    
    def test_multichannel_audio(self):
        """Testa áudio multicanal."""
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        try:
            audio = AudioTrack(file_path=temp_path, channels=6)  # 5.1 surround
            assert audio.channels == 6
            assert not audio.is_mono()
            assert not audio.is_stereo()
        finally:
            os.unlink(temp_path)