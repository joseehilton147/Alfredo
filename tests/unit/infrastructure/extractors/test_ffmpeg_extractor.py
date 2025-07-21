"""Testes unitários para FFmpegExtractor."""

import pytest
import asyncio
import subprocess
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from src.infrastructure.extractors.ffmpeg_extractor import FFmpegExtractor
from src.application.gateways.audio_extractor_gateway import AudioFormat
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


@pytest.fixture
def mock_config():
    """Configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.transcription_timeout = 600
    config.data_dir = Path("/mock/data")
    return config


@pytest.fixture
def temp_video_file():
    """Arquivo de vídeo temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        f.write(b"fake video content")
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


class TestFFmpegExtractorInitialization:
    """Testes para inicialização do FFmpegExtractor."""
    
    @patch('subprocess.run')
    def test_initialization_success(self, mock_subprocess, mock_config):
        """Testa inicialização bem-sucedida."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Act
        extractor = FFmpegExtractor(mock_config)
        
        # Assert
        assert extractor.config == mock_config
        assert extractor.logger is not None
        mock_subprocess.assert_called_once()
    
    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_initialization_ffmpeg_not_found(self, mock_subprocess, mock_config):
        """Testa inicialização com FFmpeg não encontrado."""
        with pytest.raises(ConfigurationError) as exc_info:
            FFmpegExtractor(mock_config)
        
        assert "ffmpeg_dependency" in str(exc_info.value)
        assert "FFmpeg não está instalado" in str(exc_info.value)
    
    @patch('subprocess.run')
    def test_initialization_ffmpeg_not_working(self, mock_subprocess, mock_config):
        """Testa inicialização com FFmpeg não funcionando."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "FFmpeg error"
        mock_subprocess.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            FFmpegExtractor(mock_config)
        
        assert "ffmpeg_availability" in str(exc_info.value)
        assert "FFmpeg não está funcionando" in str(exc_info.value)
    
    @patch('subprocess.run', side_effect=subprocess.TimeoutExpired("ffmpeg", 10))
    def test_initialization_ffmpeg_timeout(self, mock_subprocess, mock_config):
        """Testa inicialização com timeout do FFmpeg."""
        with pytest.raises(ConfigurationError) as exc_info:
            FFmpegExtractor(mock_config)
        
        assert "ffmpeg_timeout" in str(exc_info.value)
        assert "FFmpeg não respondeu" in str(exc_info.value)


class TestFFmpegExtractorExtractAudio:
    """Testes para método extract_audio."""
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_success(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração de áudio bem-sucedida."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "output_audio.wav"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.mkdir'):
                # Act
                result = asyncio.run(extractor.extract_audio(
                    temp_video_file,
                    output_path,
                    AudioFormat.WAV
                ))
        
        # Assert
        assert result == str(output_path)
        mock_subprocess.assert_called_once()
        
        # Verificar comando FFmpeg
        call_args = mock_subprocess.call_args[0][0]
        assert "ffmpeg" in call_args
        assert "-i" in call_args
        assert str(temp_video_file) in call_args
        assert "-vn" in call_args  # Sem vídeo
        assert "-acodec" in call_args
        assert "pcm_s16le" in call_args  # Codec WAV
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_video_not_found(self, mock_check, mock_subprocess, mock_config):
        """Testa extração com arquivo de vídeo não encontrado."""
        # Arrange
        extractor = FFmpegExtractor(mock_config)
        non_existent_file = Path("/non/existent/video.mp4")
        output_path = Path("/tmp/output.wav")
        
        # Act & Assert
        with pytest.raises(TranscriptionError) as exc_info:
            asyncio.run(extractor.extract_audio(
                non_existent_file,
                output_path
            ))
        
        assert "Arquivo de vídeo não encontrado" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_ffmpeg_failure(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração com falha do FFmpeg."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "FFmpeg extraction error"
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "output_audio.wav"
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                asyncio.run(extractor.extract_audio(
                    temp_video_file,
                    output_path
                ))
            
            assert "FFmpeg falhou" in str(exc_info.value)
            assert "FFmpeg extraction error" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_output_not_created(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração quando arquivo de saída não é criado."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "output_audio.wav"
        
        def fake_exists(self):
            if self == temp_video_file:
                return True
            if self == output_path:
                return False
            return False
        with patch('pathlib.Path.exists', new=fake_exists):
            with patch('pathlib.Path.mkdir'):
                # Act & Assert
                with pytest.raises(TranscriptionError) as exc_info:
                    asyncio.run(extractor.extract_audio(
                        temp_video_file,
                        output_path
                    ))
                
                # A mensagem de erro inclui o caminho do arquivo e o motivo
                assert "Arquivo de áudio não foi criado" in str(exc_info.value)
    
    @patch('subprocess.run', side_effect=subprocess.TimeoutExpired("ffmpeg", 600))
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_timeout(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração com timeout."""
        # Arrange
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "output_audio.wav"
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                asyncio.run(extractor.extract_audio(
                    temp_video_file,
                    output_path
                ))
            
            assert "Timeout na extração de áudio" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_different_formats(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração com diferentes formatos de áudio."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        formats_to_test = [
            (AudioFormat.WAV, "pcm_s16le"),
            (AudioFormat.MP3, "libmp3lame"),
            (AudioFormat.AAC, "aac"),
            (AudioFormat.FLAC, "flac"),
            (AudioFormat.OGG, "libvorbis")
        ]
        
        for audio_format, expected_codec in formats_to_test:
            output_path = temp_video_file.parent / f"output.{audio_format.value}"
            
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.mkdir'):
                    # Act
                    result = asyncio.run(extractor.extract_audio(
                        temp_video_file,
                        output_path,
                        audio_format
                    ))
            
            # Assert
            assert result == str(output_path)
            
            # Verificar codec correto foi usado
            call_args = mock_subprocess.call_args[0][0]
            assert expected_codec in call_args


class TestFFmpegExtractorGetAudioInfo:
    """Testes para método get_audio_info."""
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_audio_info_success(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa obtenção de informações de áudio bem-sucedida."""
        # Arrange
        audio_info = {
            "streams": [{
                "duration": "120.5",
                "sample_rate": "44100",
                "channels": "2",
                "codec_name": "aac",
                "bit_rate": "128000"
            }]
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(audio_info)
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        # Act
        result = asyncio.run(extractor.get_audio_info(temp_video_file))
        
        # Assert
        assert result["has_audio"] is True
        assert result["duration"] == 120.5
        assert result["sample_rate"] == 44100
        assert result["channels"] == 2
        assert result["codec"] == "aac"
        assert result["bitrate"] == 128000
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_audio_info_no_audio(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa obtenção de informações quando não há áudio."""
        # Arrange
        audio_info = {"streams": []}
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(audio_info)
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        # Act
        result = asyncio.run(extractor.get_audio_info(temp_video_file))
        
        # Assert
        assert result["has_audio"] is False
        assert result["duration"] == 0.0
        assert result["sample_rate"] == 0
        assert result["channels"] == 0
        assert result["codec"] == "none"
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_audio_info_file_not_found(self, mock_check, mock_subprocess, mock_config):
        """Testa obtenção de informações com arquivo não encontrado."""
        # Arrange
        extractor = FFmpegExtractor(mock_config)
        non_existent_file = Path("/non/existent/video.mp4")
        
        # Act & Assert
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(extractor.get_audio_info(non_existent_file))
        
        assert "Arquivo não encontrado" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_audio_info_ffprobe_failure(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa obtenção de informações com falha do FFprobe."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "FFprobe error"
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        # Act & Assert
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(extractor.get_audio_info(temp_video_file))
        
        assert "FFprobe falhou" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_audio_info_invalid_json(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa obtenção de informações com JSON inválido."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        # Act & Assert
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(extractor.get_audio_info(temp_video_file))
        
        assert "Erro ao analisar resposta do FFprobe" in str(exc_info.value)


class TestFFmpegExtractorUtilities:
    """Testes para métodos utilitários."""
    
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_audio_codec(self, mock_check, mock_config):
        """Testa mapeamento de formatos para codecs."""
        extractor = FFmpegExtractor(mock_config)
        
        assert extractor._get_audio_codec(AudioFormat.WAV) == "pcm_s16le"
        assert extractor._get_audio_codec(AudioFormat.MP3) == "libmp3lame"
        assert extractor._get_audio_codec(AudioFormat.AAC) == "aac"
        assert extractor._get_audio_codec(AudioFormat.FLAC) == "flac"
        assert extractor._get_audio_codec(AudioFormat.OGG) == "libvorbis"
    
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_is_format_supported(self, mock_check, mock_config):
        """Testa verificação de formatos suportados."""
        extractor = FFmpegExtractor(mock_config)
        
        # Act & Assert
        for format in AudioFormat:
            result = asyncio.run(extractor.is_format_supported(format))
            assert result is True
    
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_get_supported_formats(self, mock_check, mock_config):
        """Testa obtenção de formatos suportados."""
        extractor = FFmpegExtractor(mock_config)
        
        # Act
        result = asyncio.run(extractor.get_supported_formats())
        
        # Assert
        expected_formats = [
            AudioFormat.WAV,
            AudioFormat.MP3,
            AudioFormat.AAC,
            AudioFormat.FLAC,
            AudioFormat.OGG
        ]
        assert result == expected_formats
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_validate_video_file_valid(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa validação de arquivo de vídeo válido."""
        # Arrange
        audio_info = {
            "streams": [{
                "duration": "120.5",
                "codec_name": "aac"
            }]
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(audio_info)
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        # Act
        result = asyncio.run(extractor.validate_video_file(temp_video_file))
        
        # Assert
        assert result is True
    
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_validate_video_file_not_found(self, mock_check, mock_config):
        """Testa validação de arquivo não encontrado."""
        extractor = FFmpegExtractor(mock_config)
        non_existent_file = Path("/non/existent/video.mp4")
        
        # Act
        result = asyncio.run(extractor.validate_video_file(non_existent_file))
        
        # Assert
        assert result is False
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_estimate_extraction_time(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa estimativa de tempo de extração."""
        # Arrange
        audio_info = {
            "streams": [{
                "duration": "120.0",
                "codec_name": "aac"
            }]
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(audio_info)
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        
        # Act
        result = asyncio.run(extractor.estimate_extraction_time(temp_video_file, AudioFormat.WAV))
        
        # Assert
        assert isinstance(result, float)
        assert result >= 1.0  # Mínimo de 1 segundo
        assert result <= 60.0  # Máximo de 50% da duração (120 * 0.5)


class TestFFmpegExtractorExtractSegment:
    """Testes para método extract_audio_segment."""
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_segment_success(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração de segmento de áudio bem-sucedida."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "segment.wav"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.mkdir'):
                # Act
                result = asyncio.run(extractor.extract_audio_segment(
                    temp_video_file,
                    output_path,
                    start_time=10.0,
                    end_time=30.0
                ))
        
        # Assert
        assert result == str(output_path)
        
        # Verificar comando FFmpeg
        call_args = mock_subprocess.call_args[0][0]
        assert "-ss" in call_args
        assert "10.0" in call_args
        assert "-t" in call_args
        assert "20.0" in call_args  # duração = end_time - start_time
    
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_segment_invalid_times(self, mock_check, mock_config, temp_video_file):
        """Testa extração de segmento com tempos inválidos."""
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "segment.wav"
        
        # Teste com start_time negativo
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(extractor.extract_audio_segment(
                temp_video_file,
                output_path,
                start_time=-5.0,
                end_time=30.0
            ))
        assert "Tempos inválidos" in str(exc_info.value)
        
        # Teste com end_time <= start_time
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(extractor.extract_audio_segment(
                temp_video_file,
                output_path,
                start_time=30.0,
                end_time=20.0
            ))
        assert "Tempos inválidos" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_extract_audio_segment_ffmpeg_failure(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa extração de segmento com falha do FFmpeg."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Segment extraction error"
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "segment.wav"
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                asyncio.run(extractor.extract_audio_segment(
                    temp_video_file,
                    output_path,
                    start_time=10.0,
                    end_time=30.0
                ))
            
            assert "FFmpeg falhou na extração do segmento" in str(exc_info.value)


class TestFFmpegExtractorIntegration:
    """Testes de integração para FFmpegExtractor."""
    
    @patch('subprocess.run')
    @patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor._check_ffmpeg_availability')
    def test_full_extraction_workflow(self, mock_check, mock_subprocess, mock_config, temp_video_file):
        """Testa fluxo completo de extração."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        extractor = FFmpegExtractor(mock_config)
        output_path = temp_video_file.parent / "extracted_audio.wav"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                # Act
                result = asyncio.run(extractor.extract_audio(
                    temp_video_file,
                    output_path,
                    format=AudioFormat.WAV,
                    sample_rate=16000,
                    channels=1
                ))
        
        # Assert
        assert result == str(output_path)
        mock_mkdir.assert_called_once()
        
        # Verificar parâmetros do comando
        call_args = mock_subprocess.call_args[0][0]
        assert "ffmpeg" in call_args
        assert "-ar" in call_args
        assert "16000" in call_args
        assert "-ac" in call_args
        assert "1" in call_args