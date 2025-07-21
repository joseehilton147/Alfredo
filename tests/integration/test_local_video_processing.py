import pytest
import os
from pathlib import Path

from src.application.use_cases.process_local_video import ProcessLocalVideoUseCase, ProcessLocalVideoRequest
from src.infrastructure.extractors.ffmpeg_extractor import FFmpegExtractor
from src.infrastructure.providers.mock_provider_strategy import MockProviderStrategy
from src.infrastructure.storage.filesystem_storage import FileSystemStorage
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError, TranscriptionError

@pytest.fixture
def config():
    # Configuração para testes, usando diretórios temporários
    test_config = AlfredoConfig()
    test_config.data_dir = Path("data/temp/test_local_video_processing")
    test_config.output_dir = test_config.data_dir / "output"
    test_config.temp_dir = test_config.data_dir / "temp"
    test_config.cache_dir = test_config.data_dir / "cache"

    # Garante que os diretórios existam e estejam limpos antes de cada teste
    for d in [test_config.data_dir, test_config.output_dir, test_config.temp_dir, test_config.cache_dir]:
        if d.exists():
            import shutil
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    
    yield test_config

    # Limpa os diretórios após o teste
    for d in [test_config.data_dir, test_config.output_dir, test_config.temp_dir, test_config.cache_dir]:
        if d.exists():
            import shutil
            shutil.rmtree(d)

@pytest.fixture
def local_video_processing_use_case(config):
    extractor = FFmpegExtractor(config)
    ai_provider = MockProviderStrategy() # Usando mock para AI para evitar chamadas externas
    storage = FileSystemStorage(config)
    return ProcessLocalVideoUseCase(extractor, ai_provider, storage, config)

@pytest.mark.asyncio
async def test_process_local_video_invalid_file(local_video_processing_use_case, config):
    # Cria um arquivo de vídeo vazio para simular um arquivo inválido
    invalid_video_path = config.temp_dir / "invalid_video.mp4"
    invalid_video_path.touch() # Cria um arquivo vazio

    request = ProcessLocalVideoRequest(file_path=str(invalid_video_path), language="en")
    
    with pytest.raises(InvalidVideoFormatError):
        await local_video_processing_use_case.execute(request)

    # Garante que nenhum arquivo foi salvo ou que foram limpos
    assert not any((config.output_dir / "videos").iterdir())
    assert not any((config.output_dir / "transcriptions").iterdir())
    assert not any((config.output_dir / "summaries").iterdir())
    assert not any(config.temp_dir.iterdir())

@pytest.mark.asyncio
async def test_process_local_video_cancellation(local_video_processing_use_case, config):
    # Cria um arquivo de vídeo vazio para simular um arquivo
    test_video_path = config.temp_dir / "test_video_cancellation.mp4"
    test_video_path.touch()

    request = ProcessLocalVideoRequest(file_path=str(test_video_path), language="en")

    # Simula o cancelamento durante o processo
    local_video_processing_use_case._cancelled = True 

    with pytest.raises(TranscriptionError, match="Processamento cancelado pelo usuário"):
        await local_video_processing_use_case.execute(request)
    
    # Garante que nenhum arquivo foi salvo ou que foram limpos
    assert not any((config.output_dir / "videos").iterdir())
    assert not any((config.output_dir / "transcriptions").iterdir())
    assert not any((config.output_dir / "summaries").iterdir())
    assert not any(config.temp_dir.iterdir())