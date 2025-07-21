import pytest
import os
from pathlib import Path

from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase, ProcessYouTubeVideoRequest
from src.infrastructure.downloaders.ytdlp_downloader import YTDLPDownloader
from src.infrastructure.extractors.ffmpeg_extractor import FFmpegExtractor
from src.infrastructure.providers.mock_provider_strategy import MockProviderStrategy
from src.infrastructure.storage.filesystem_storage import FileSystemStorage
from src.infrastructure.storage.json_storage_adapter import JsonStorageAdapter
from src.infrastructure.repositories.json_video_repository import JsonVideoRepository
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import DownloadFailedError, TranscriptionError, InvalidVideoFormatError

@pytest.fixture
def config():
    # Configuração para testes, usando diretórios temporários
    test_config = AlfredoConfig()
    test_config.data_dir = Path("data/temp/test_youtube_processing")
    test_config.output_dir = test_config.data_dir / "output"
    test_config.temp_dir = test_config.data_dir / "temp"
    test_config.cache_dir = test_config.data_dir / "cache"

    # Garante que os diretórios existam e estejam limpos antes de cada teste
    for d in [test_config.temp_dir, test_config.output_dir, test_config.cache_dir]:
        if d.exists():
            import shutil
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    
    yield test_config

    # Limpa os diretórios após o teste
    for d in [test_config.temp_dir, test_config.output_dir, test_config.cache_dir]:
        if d.exists():
            import shutil
            shutil.rmtree(d)

@pytest.fixture
def youtube_processing_use_case(config):
    downloader = YTDLPDownloader(config)
    extractor = FFmpegExtractor(config)
    ai_provider = MockProviderStrategy() # Usando mock para AI para evitar chamadas externas
    storage = FileSystemStorage(config)
    return ProcessYouTubeVideoUseCase(downloader, extractor, ai_provider, storage, config)

@pytest.mark.asyncio
async def test_process_youtube_video_success(youtube_processing_use_case, config):
    # URL de um vídeo curto para teste (ex: um vídeo de teste sem direitos autorais)
    # ATENÇÃO: Substitua por uma URL de vídeo real e curta para testes de integração
    # Exemplo: "https://www.youtube.com/watch?v=dQw4w9WgXcQ" (Rick Astley - Never Gonna Give You Up)
    # Ou um vídeo de teste mais curto e sem música para evitar problemas de direitos autorais
    # Sugestão: um vídeo de teste de 10 segundos sem áudio ou com áudio genérico
    test_url = "https://www.youtube.com/watch?v=LXb3EKWsInQ" # Exemplo de vídeo curto sem áudio complexo

    request = ProcessYouTubeVideoRequest(url=test_url, language="en", output_dir=str(config.output_dir))
    response = await youtube_processing_use_case.execute(request)

    assert response.video is not None
    assert "Esta é uma transcrição simulada" in response.transcription
    
    
    # Verifica se o vídeo e a transcrição foram salvos pelo storage
    video_id = f"youtube_{response.video.metadata['id']}"
    assert (config.output_dir / "videos" / video_id / "metadata.json").exists()
    assert (config.output_dir / "transcriptions" / video_id / "transcription.txt").exists()

    # Limpeza adicional (já coberta pelo fixture, mas bom ter certeza)
    if os.path.exists(response.downloaded_file):
        os.remove(response.downloaded_file)
    
    # Verifica se o arquivo de áudio temporário foi limpo
    temp_audio_path = config.temp_dir / f"{video_id}.wav"
    assert not temp_audio_path.exists()

@pytest.mark.asyncio
async def test_process_youtube_video_invalid_url(youtube_processing_use_case):
    invalid_url = "https://www.youtube.com/watch?v=INVALID_ID"
    request = ProcessYouTubeVideoRequest(url=invalid_url, language="en")
    
    with pytest.raises(InvalidVideoFormatError):
        await youtube_processing_use_case.execute(request)

@pytest.mark.asyncio
async def test_process_youtube_video_cancellation(youtube_processing_use_case, config):
    test_url = "https://www.youtube.com/watch?v=LXb3EKWsInQ" # Vídeo curto
    request = ProcessYouTubeVideoRequest(url=test_url, language="en")

    # Simula o cancelamento durante o processo
    youtube_processing_use_case._cancelled = True 

    with pytest.raises(DownloadFailedError, match="Processamento cancelado pelo usuário"):
        await youtube_processing_use_case.execute(request)
    
    # Garante que nenhum arquivo foi salvo ou que foram limpos
    assert not any((config.output_dir / "videos").iterdir())
    assert not any((config.output_dir / "transcriptions").iterdir())
    assert not any((config.output_dir / "summaries").iterdir())
    assert not any(config.temp_dir.iterdir())