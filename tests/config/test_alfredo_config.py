import pytest
import shutil
import subprocess
from pathlib import Path
tempfile = pytest.importorskip('tempfile')

from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError

# Dummy result for subprocess.run
class DummyCompleted:
    def __init__(self, returncode, stderr=b''):
        self.returncode = returncode
        self.stderr = stderr


def test_validate_ffmpeg_success(monkeypatch):
    """FFmpeg presente e executa corretamente."""
    monkeypatch.setattr(shutil, 'which', lambda cmd: '/usr/bin/ffmpeg')
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: DummyCompleted(0))
    config = AlfredoConfig()
    # Deve passar sem exceção
    config.validate_ffmpeg()


def test_validate_ffmpeg_missing(monkeypatch):
    """FFmpeg não está no PATH."""
    monkeypatch.setattr(shutil, 'which', lambda cmd: None)
    config = AlfredoConfig()
    with pytest.raises(ConfigurationError) as exc:
        config.validate_ffmpeg()
    assert exc.value.config_key == 'ffmpeg'


def test_validate_ffmpeg_error(monkeypatch):
    """FFmpeg retorna erro de execução."""
    monkeypatch.setattr(shutil, 'which', lambda cmd: '/usr/bin/ffmpeg')
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: DummyCompleted(1, stderr=b'fail'))
    config = AlfredoConfig()
    with pytest.raises(ConfigurationError) as exc:
        config.validate_ffmpeg()
    assert 'erro ao executar ffmpeg' in exc.value.reason


def test_directory_structure(tmp_path):
    """create_directory_structure cria todas as pastas esperadas."""
    data_dir = tmp_path / 'data'
    temp_dir = tmp_path / 'temp'
    config = AlfredoConfig(base_dir=tmp_path, data_dir=data_dir, temp_dir=temp_dir)
    # Remover se existir
    shutil.rmtree(data_dir, ignore_errors=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    config.create_directory_structure()
    expected = [
        data_dir / 'input' / 'local',
        data_dir / 'input' / 'youtube',
        data_dir / 'output' / 'transcriptions',
        data_dir / 'output' / 'summaries',
        data_dir / 'logs',
        temp_dir,
        data_dir / 'cache'
    ]
    for path in expected:
        assert path.exists(), f"Diretório {path} não foi criado"


def test_default_ai_provider_requires_key(monkeypatch):
    """Validação de provider exige API key adequada."""
    config = AlfredoConfig()
    # Simula provider Groq sem chave
    config.default_ai_provider = 'groq'
    config.groq_api_key = None
    with pytest.raises(ConfigurationError) as exc:
        config.validate_runtime()
    assert 'groq_api_key' in exc.value.config_key


def test_invalid_timeouts():
    """Timeouts não positivos devem levantar erro."""
    with pytest.raises(ConfigurationError):
        AlfredoConfig(download_timeout=0)
    with pytest.raises(ConfigurationError):
        AlfredoConfig(transcription_timeout=-1)


def test_video_quality_setting():
    """Configuração de qualidade de vídeo é armazenada corretamente."""
    config = AlfredoConfig(video_quality='hd')
    assert config.video_quality == 'hd'
    
def test_get_provider_config_whisper_and_custom_models():
    """Testa get_provider_config para diferentes providers e custom models."""
    cfg = AlfredoConfig()
    # customizar modelos
    cfg.whisper_model = 'custom_whisper'
    cfg.groq_model = 'custom_groq'
    cfg.ollama_model = 'custom_ollama'
    # whisper
    wcfg = cfg.get_provider_config('whisper')
    assert wcfg['model'] == 'custom_whisper'
    assert wcfg['timeout'] == cfg.transcription_timeout
    # groq exige api_key
    cfg.groq_api_key = 'key123'
    gcfg = cfg.get_provider_config('groq')
    assert gcfg['model'] == 'custom_groq'
    assert gcfg['api_key'] == 'key123'
    # ollama
    ocfg = cfg.get_provider_config('ollama')
    assert ocfg['model'] == 'custom_ollama'
    assert ocfg['timeout'] == cfg.transcription_timeout

def test_get_provider_config_invalid_provider():
    """Provider inválido deve gerar ConfigurationError."""
    cfg = AlfredoConfig()
    with pytest.raises(ConfigurationError):
        cfg.get_provider_config('unknown')

def test_custom_timeouts_persist():
    """Testa customização de timeouts de download e transcription."""
    cfg = AlfredoConfig(download_timeout=123, transcription_timeout=456)
    assert cfg.download_timeout == 123
    assert cfg.transcription_timeout == 456

def test_default_language_and_scene_threshold():
    """Testa configuração de default_language e scene_threshold."""
    cfg = AlfredoConfig(default_language='en', scene_threshold=0.5)
    assert cfg.default_language == 'en'
    assert cfg.scene_threshold == 0.5
