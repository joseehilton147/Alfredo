"""Configuração específica para testes BDD."""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Importar fixtures compartilhadas do conftest principal
from tests.conftest import *

# Fixtures específicas para BDD
@pytest.fixture
def mock_config():
    """Configuração mock para testes BDD."""
    from src.config.alfredo_config import AlfredoConfig
    
    config = AlfredoConfig()
    config.data_dir = Path("/tmp/alfredo_test")
    config.temp_dir = Path("/tmp/alfredo_test/temp")
    config.max_video_duration = 3600
    config.download_timeout = 300
    config.transcription_timeout = 600
    return config

@pytest.fixture
def mock_video_downloader():
    """Mock do VideoDownloaderGateway para testes BDD."""
    from src.application.gateways.video_downloader import VideoDownloaderGateway
    
    mock = Mock(spec=VideoDownloaderGateway)
    mock.download = AsyncMock(return_value="/mock/path/video.mp4")
    mock.extract_info = AsyncMock(return_value={
        "title": "Mock Video Title",
        "duration": 120,
        "uploader": "Mock Channel",
        "upload_date": "20240101"
    })
    mock.get_available_formats = AsyncMock(return_value=[
        {"format_id": "best", "ext": "mp4", "quality": "720p"}
    ])
    return mock

@pytest.fixture
def mock_audio_extractor():
    """Mock do AudioExtractorGateway para testes BDD."""
    from src.application.gateways.audio_extractor import AudioExtractorGateway
    
    mock = Mock(spec=AudioExtractorGateway)
    mock.extract_audio = AsyncMock(return_value="/mock/path/audio.wav")
    mock.get_audio_info = AsyncMock(return_value={
        "duration": 120,
        "sample_rate": 16000,
        "channels": 1
    })
    return mock

@pytest.fixture
def mock_ai_provider():
    """Mock do AIProvider para testes BDD."""
    from src.infrastructure.providers.ai_provider_interface import AIProviderInterface
    
    mock = Mock(spec=AIProviderInterface)
    mock.transcribe_audio = AsyncMock(return_value="Esta é uma transcrição mock do áudio.")
    mock.generate_summary = AsyncMock(return_value="Este é um resumo mock do vídeo.")
    mock.name = "mock_provider"
    return mock

@pytest.fixture
def mock_storage():
    """Mock do StorageGateway para testes BDD."""
    from src.application.gateways.storage_gateway import StorageGateway
    from src.domain.entities.video import Video
    
    mock = Mock(spec=StorageGateway)
    mock.save_video = AsyncMock()
    mock.load_video = AsyncMock(return_value=None)
    mock.save_transcription = AsyncMock()
    mock.load_transcription = AsyncMock(return_value=None)
    mock.list_videos = AsyncMock(return_value=[])
    return mock

@pytest.fixture
def mock_infrastructure_factory(mock_video_downloader, mock_audio_extractor, 
                               mock_ai_provider, mock_storage, mock_config):
    """Factory mock completa para testes BDD."""
    from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
    
    factory = Mock(spec=InfrastructureFactory)
    factory.create_video_downloader.return_value = mock_video_downloader
    factory.create_audio_extractor.return_value = mock_audio_extractor
    factory.create_ai_provider.return_value = mock_ai_provider
    factory.create_storage.return_value = mock_storage
    factory.create_all_dependencies.return_value = {
        'downloader': mock_video_downloader,
        'extractor': mock_audio_extractor,
        'ai_provider': mock_ai_provider,
        'storage': mock_storage,
        'config': mock_config
    }
    return factory

@pytest.fixture
def sample_video_data():
    """Dados de exemplo para testes BDD."""
    return {
        "valid_youtube_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "invalid_url": "not-a-url",
        "valid_local_path": "/path/to/video.mp4",
        "invalid_local_path": "/path/to/nonexistent.mp4",
        "expected_transcription": "Esta é uma transcrição de exemplo.",
        "expected_summary": "Este é um resumo de exemplo."
    }

@pytest.fixture
def bdd_context():
    """Contexto compartilhado entre steps BDD."""
    return {
        "last_result": None,
        "last_error": None,
        "execution_time": None,
        "temp_files": []
    }

# Configuração para relatórios BDD
def pytest_configure(config):
    """Configuração adicional para pytest-bdd."""
    config.addinivalue_line(
        "markers", "bdd: marca testes BDD"
    )

# Hook para limpeza após testes BDD
@pytest.fixture(autouse=True)
def cleanup_bdd_test(bdd_context):
    """Limpeza automática após cada teste BDD."""
    yield
    
    # Limpar arquivos temporários criados durante o teste
    for temp_file in bdd_context.get("temp_files", []):
        try:
            Path(temp_file).unlink(missing_ok=True)
        except Exception:
            pass
    
    # Resetar contexto
    bdd_context.clear()