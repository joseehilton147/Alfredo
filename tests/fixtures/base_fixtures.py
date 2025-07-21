"""Fixtures base reutilizáveis para todos os testes."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Optional

from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import AlfredoError


@pytest.fixture
def temp_dir():
    """Cria diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config(temp_dir):
    """Cria configuração mock para testes."""
    return AlfredoConfig(
        base_dir=temp_dir,
        data_dir=temp_dir / "data",
        temp_dir=temp_dir / "temp",
        groq_api_key="test_groq_key",
        openai_api_key="test_openai_key",
        default_ai_provider="whisper",
        max_video_duration=3600,
        download_timeout=300,
        transcription_timeout=600
    )


@pytest.fixture
def sample_video():
    """Cria vídeo de exemplo para testes."""
    return Video(
        id="test_video_123",
        title="Vídeo de Teste",
        duration=120.5,
        file_path="/path/to/test_video.mp4",
        url="https://youtube.com/watch?v=test123"
    )


@pytest.fixture
def sample_local_video(temp_dir):
    """Cria vídeo local de exemplo para testes."""
    video_file = temp_dir / "test_video.mp4"
    video_file.write_text("fake video content")
    
    return Video(
        id="local_video_123",
        title="Vídeo Local de Teste",
        duration=90.0,
        file_path=str(video_file)
    )


@pytest.fixture
def sample_youtube_video():
    """Cria vídeo do YouTube de exemplo para testes."""
    return Video(
        id="youtube_video_123",
        title="Vídeo YouTube de Teste",
        duration=180.0,
        url="https://www.youtube.com/watch?v=FZ42HMWG6xg"
    )


@pytest.fixture
def mock_video_downloader():
    """Mock para VideoDownloaderGateway."""
    mock = AsyncMock()
    mock.download.return_value = Video(
        id="downloaded_video",
        title="Downloaded Video",
        duration=120.0,
        file_path="/tmp/downloaded_video.mp4",
        url="https://youtube.com/watch?v=test"
    )
    return mock


@pytest.fixture
def mock_audio_extractor():
    """Mock para AudioExtractorGateway."""
    mock = AsyncMock()
    mock.extract.return_value = "/tmp/extracted_audio.wav"
    return mock


@pytest.fixture
def mock_ai_provider():
    """Mock para AIProviderInterface."""
    mock = AsyncMock()
    mock.transcribe.return_value = "Esta é uma transcrição de teste."
    mock.summarize.return_value = "Este é um resumo de teste."
    return mock


@pytest.fixture
def mock_storage():
    """Mock para StorageGateway."""
    mock = AsyncMock()
    mock.save_transcription.return_value = "/tmp/transcription.json"
    mock.save_summary.return_value = "/tmp/summary.html"
    mock.load_video.return_value = None
    return mock


@pytest.fixture
def mock_infrastructure_factory(
    mock_video_downloader,
    mock_audio_extractor, 
    mock_ai_provider,
    mock_storage,
    mock_config
):
    """Factory mock com todas as dependências."""
    factory = Mock()
    factory.create_video_downloader.return_value = mock_video_downloader
    factory.create_audio_extractor.return_value = mock_audio_extractor
    factory.create_ai_provider.return_value = mock_ai_provider
    factory.create_storage.return_value = mock_storage
    factory._config = mock_config
    
    factory.create_all_dependencies.return_value = {
        'downloader': mock_video_downloader,
        'extractor': mock_audio_extractor,
        'ai_provider': mock_ai_provider,
        'storage': mock_storage,
        'config': mock_config
    }
    
    return factory


@pytest.fixture
def sample_transcription_result():
    """Resultado de transcrição de exemplo."""
    return {
        "text": "Esta é uma transcrição de exemplo para testes.",
        "language": "pt",
        "confidence": 0.95,
        "duration": 120.5,
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "text": "Esta é uma transcrição"
            },
            {
                "start": 5.0,
                "end": 10.0,
                "text": "de exemplo para testes."
            }
        ]
    }


@pytest.fixture
def sample_summary_result():
    """Resultado de resumo de exemplo."""
    return {
        "title": "Resumo do Vídeo de Teste",
        "summary": "Este vídeo aborda conceitos importantes sobre testes automatizados.",
        "key_points": [
            "Importância dos testes unitários",
            "Configuração de fixtures",
            "Mocks e stubs"
        ],
        "duration": 120.5,
        "language": "pt"
    }


@pytest.fixture
def sample_error_scenarios():
    """Cenários de erro comuns para testes."""
    return {
        'download_error': Exception("Erro no download do vídeo"),
        'transcription_error': AlfredoError("Erro na transcrição"),
        'network_error': ConnectionError("Erro de conexão"),
        'timeout_error': TimeoutError("Timeout na operação"),
        'file_not_found': FileNotFoundError("Arquivo não encontrado")
    }


@pytest.fixture
def mock_progress_callback():
    """Mock para callback de progresso."""
    return Mock()


@pytest.fixture
def sample_video_metadata():
    """Metadados de vídeo de exemplo."""
    return {
        "format": "mp4",
        "codec": "h264",
        "resolution": "1920x1080",
        "fps": 30,
        "bitrate": 2000,
        "size_mb": 50.5,
        "created_at": "2024-01-01T12:00:00Z"
    }


@pytest.fixture
def sample_processing_context():
    """Contexto de processamento de exemplo."""
    return {
        "session_id": "test_session_123",
        "user_id": "test_user",
        "processing_start": "2024-01-01T12:00:00Z",
        "settings": {
            "language": "pt",
            "quality": "high",
            "format": "mp4"
        }
    }


class MockAsyncContextManager:
    """Context manager mock para operações assíncronas."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_async_context():
    """Mock para context managers assíncronos."""
    return MockAsyncContextManager


# Fixtures para diferentes tipos de teste

@pytest.fixture
def unit_test_config():
    """Configuração específica para testes unitários."""
    return {
        'mock_external_dependencies': True,
        'use_real_files': False,
        'timeout': 5.0
    }


@pytest.fixture
def integration_test_config():
    """Configuração específica para testes de integração."""
    return {
        'mock_external_dependencies': False,
        'use_real_files': True,
        'timeout': 30.0
    }


@pytest.fixture
def e2e_test_config():
    """Configuração específica para testes end-to-end."""
    return {
        'mock_external_dependencies': False,
        'use_real_files': True,
        'use_real_network': True,
        'timeout': 300.0
    }


# Fixtures para validação de dados

@pytest.fixture
def valid_video_data():
    """Dados válidos para criação de vídeo."""
    return {
        'id': 'valid_video_123',
        'title': 'Vídeo Válido para Teste',
        'duration': 120.0,
        'file_path': '/path/to/valid_video.mp4'
    }


@pytest.fixture
def invalid_video_data():
    """Dados inválidos para testes de validação."""
    return {
        'empty_id': {'id': '', 'title': 'Test'},
        'long_id': {'id': 'a' * 300, 'title': 'Test'},
        'empty_title': {'id': 'test', 'title': ''},
        'negative_duration': {'id': 'test', 'title': 'Test', 'duration': -10},
        'no_sources': {'id': 'test', 'title': 'Test'}
    }


# Fixtures para performance testing

@pytest.fixture
def performance_test_data():
    """Dados para testes de performance."""
    return {
        'small_video': {'duration': 30, 'size_mb': 10},
        'medium_video': {'duration': 300, 'size_mb': 100},
        'large_video': {'duration': 3600, 'size_mb': 1000}
    }


# Fixtures para testes de segurança

@pytest.fixture
def security_test_data():
    """Dados para testes de segurança."""
    return {
        'malicious_urls': [
            'javascript:alert("xss")',
            'file:///etc/passwd',
            'http://malicious-site.com/payload'
        ],
        'path_traversal': [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '/etc/passwd'
        ],
        'sql_injection': [
            "'; DROP TABLE videos; --",
            "1' OR '1'='1",
            "admin'/*"
        ]
    }