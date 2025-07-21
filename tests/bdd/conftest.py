from pytest_bdd import then, when, parsers
import asyncio

# Steps When assertivos e reais para BDD
@when("executo o processamento do vídeo")
async def executar_processamento_video(bdd_context, mock_infrastructure_factory):
    """Executa processamento de vídeo com caso de uso real."""
    from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
    from src.application.dtos.process_youtube_video import ProcessYouTubeVideoRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        # Criar request
        request = ProcessYouTubeVideoRequest(
            url=bdd_context.get("input_url", "https://youtube.com/watch?v=test"),
            language="pt",
            generate_summary=False
        )
        
        # Executar caso de uso real
        import time
        start_time = time.time()
        result = await use_case.execute(request)
        end_time = time.time()
        
        bdd_context["last_result"] = result
        bdd_context["execution_time"] = end_time - start_time
        bdd_context["last_error"] = None
        
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["last_result"] = None

@when("executo o processamento do vídeo com força de reprocessamento")
async def executar_processamento_forcado(bdd_context, mock_infrastructure_factory):
    """Executa processamento forçando reprocessamento."""
    from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
    from src.application.dtos.process_youtube_video import ProcessYouTubeVideoRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        # Criar request com força de reprocessamento
        request = ProcessYouTubeVideoRequest(
            url=bdd_context.get("input_url", "https://youtube.com/watch?v=test"),
            language="pt",
            generate_summary=True,
            force_reprocess=True
        )
        
        # Executar caso de uso real
        import time
        start_time = time.time()
        result = await use_case.execute(request)
        end_time = time.time()
        
        bdd_context["last_result"] = result
        bdd_context["execution_time"] = end_time - start_time
        bdd_context["last_error"] = None
        
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["last_result"] = None

# Steps Then adicionais para cobertura total dos cenários BDD
@then("se todas as tentativas falharem, deve retornar erro específico")
def validar_erro_apos_tentativas(bdd_context):
    assert bdd_context["last_error"] is not None
    assert "DownloadFailedError" in str(type(bdd_context["last_error"]))

@then("todos os vídeos válidos devem ser processados")
def validar_videos_processados(bdd_context):
    assert bdd_context["last_error"] is None
    assert bdd_context["last_result"] is not None
    result = bdd_context["last_result"]
    assert hasattr(result, 'processed_count')
    assert result.processed_count > 0

@then("devo receber o resultado do cache")
def validar_resultado_cache(bdd_context):
    assert bdd_context["last_error"] is None
    assert bdd_context["last_result"] is not None
    result = bdd_context["last_result"]
    assert hasattr(result, 'was_cached')
    assert result.was_cached is True

@then("o vídeo deve ser baixado novamente")
def validar_download_novamente(bdd_context, mock_video_downloader):
    mock_video_downloader.download.assert_called_once()
# Steps Then/When assertivos e reais para BDD
from pytest_bdd import then, parsers

@then("devo receber uma transcrição válida")
def validar_transcricao_valida(bdd_context):
    assert bdd_context["last_error"] is None, f"Erro inesperado: {bdd_context['last_error']}"
    assert bdd_context["last_result"] is not None
    result = bdd_context["last_result"]
    if hasattr(result, 'video'):
        assert result.video.transcription is not None
        assert len(result.video.transcription) > 0
    elif hasattr(result, 'transcription'):
        assert result.transcription is not None
        assert len(result.transcription) > 0

@then(parsers.parse('devo receber um erro de "{error_type}"'))
def validar_tipo_erro(bdd_context, error_type):
    error_mapping = {
        "formato inválido": "InvalidVideoFormatError",
        "download": "DownloadFailedError",
        "transcrição": "TranscriptionError",
        "configuração": "ConfigurationError",
        "provider indisponível": "ProviderUnavailableError"
    }
    expected_error_class = error_mapping.get(error_type, error_type)
    actual_error_class = bdd_context["last_error"].__class__.__name__ if bdd_context["last_error"] is not None else None
    assert actual_error_class == expected_error_class, \
        f"Esperado {expected_error_class}, mas recebeu {actual_error_class}"

@then(parsers.parse("o sistema deve tentar novamente até {max_retries:d} vezes"))
def validar_tentativas_retry(bdd_context, max_retries, mock_video_downloader):
    assert mock_video_downloader.download.call_count <= max_retries

from pytest_bdd import then, parsers
from pytest_bdd import then, parsers
"""Configuração específica para testes BDD."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


# Importar fixtures compartilhadas do conftest principal
from tests.conftest import *

# Importar explicitamente todos os arquivos de step definitions necessários para registro dos steps
from tests.bdd.step_defs import common_steps
from tests.bdd.step_defs import youtube_processing_steps

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
    mock = Mock()
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
    mock = Mock()
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
    mock = Mock()
    mock.transcribe_audio = AsyncMock(return_value="Esta é uma transcrição mock do áudio.")
    mock.generate_summary = AsyncMock(return_value="Este é um resumo mock do vídeo.")
    mock.name = "mock_provider"
    return mock


@pytest.fixture
def mock_storage():
    """Mock do StorageGateway para testes BDD."""
    mock = Mock()
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
    factory = Mock()
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