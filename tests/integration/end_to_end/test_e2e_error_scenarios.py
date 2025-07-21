"""
Testes E2E para cenários de erro nos fluxos de YouTube e vídeo local.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoUseCase,
    ProcessYouTubeVideoRequest
)
from src.application.use_cases.process_local_video import (
    ProcessLocalVideoUseCase,
    ProcessLocalVideoRequest
)
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError,
    ConfigurationError,
    InvalidVideoFormatError,
)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_youtube_invalid_url(tmp_path):
    # Configuração mínima
    config = AlfredoConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        temp_dir=tmp_path / "temp",
        max_video_duration=3600,
        download_timeout=5,
        transcription_timeout=5
    )
    config.create_directory_structure()

    # Mock downloader.extract_info para URL inválida
    with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as dl_cls:
        mock_dl = dl_cls.return_value
        mock_dl.extract_info = AsyncMock(side_effect=DownloadFailedError(
            "invalid_url", "URL inválida"))

        factory = InfrastructureFactory(config)
        deps = factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**deps)

        request = ProcessYouTubeVideoRequest(
            url="invalid_url",
            language="pt",
            generate_summary=False
        )
        with pytest.raises(DownloadFailedError) as exc:
            await use_case.execute(request)
        assert "invalid_url" in str(exc.value)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_youtube_network_timeout(tmp_path):
    # Configuração mínima
    config = AlfredoConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        temp_dir=tmp_path / "temp",
        max_video_duration=3600,
        download_timeout=1,
        transcription_timeout=1
    )
    config.create_directory_structure()

    # Mock extract_info ok, download retrona TimeoutError
    with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as dl_cls:
        mock_dl = dl_cls.return_value
        mock_dl.extract_info = AsyncMock(return_value={
            'id': '123', 'title': 'Test', 'duration': 10
        })
        mock_dl.download = AsyncMock(side_effect=TimeoutError("Timeout"))

        factory = InfrastructureFactory(config)
        deps = factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**deps)

        request = ProcessYouTubeVideoRequest(
            url="https://youtube.com/watch?v=timeout",
        )
        with pytest.raises(ConfigurationError) as exc:
            await use_case.execute(request)
        # Deve ser convertido em ConfigurationError inesperado
        assert exc.value.details.get('url') == request.url

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_local_missing_file(tmp_path):
    # Configuração mínima
    config = AlfredoConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        temp_dir=tmp_path / "temp",
        max_video_duration=3600
    )
    config.create_directory_structure()

    factory = InfrastructureFactory(config)
    deps = factory.create_all_dependencies()
    use_case = ProcessLocalVideoUseCase(**deps)

    # Solicitar processamento de arquivo inexistente
    missing = tmp_path / "nonexistent.mp4"
    request = ProcessLocalVideoRequest(
        file_path=str(missing),
    )
    with pytest.raises(InvalidVideoFormatError) as exc:
        await use_case.execute(request)
    assert "não encontrado" in exc.value.message.lower()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_local_invalid_format(tmp_path):
    # Configuração mínima
    config = AlfredoConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        temp_dir=tmp_path / "temp",
        max_video_duration=3600
    )
    config.create_directory_structure()

    # Criar arquivo com extensão inválida
    input_dir = config.data_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    bad_file = input_dir / "file.txt"
    bad_file.write_text("conteudo")

    factory = InfrastructureFactory(config)
    deps = factory.create_all_dependencies()
    use_case = ProcessLocalVideoUseCase(**deps)

    request = ProcessLocalVideoRequest(
        file_path=str(bad_file),
    )
    with pytest.raises(InvalidVideoFormatError) as exc:
        await use_case.execute(request)
    assert "formato" in exc.value.message.lower()
