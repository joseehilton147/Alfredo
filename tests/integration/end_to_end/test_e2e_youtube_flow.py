"""
Testes E2E para fluxo completo de processamento de vídeo YouTube.
"""
import pytest
import tempfile
import asyncio
import json
import os
import webbrowser

from pathlib import Path
from unittest.mock import patch, AsyncMock, Mock

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoUseCase,
    ProcessYouTubeVideoRequest
)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_youtube_flow_generates_and_opens_html(tmp_path, monkeypatch):
    # Preparar configuração temporária
    base = tmp_path
    config = AlfredoConfig(
        base_dir=base,
        data_dir=base / "data",
        temp_dir=base / "temp",
        max_video_duration=3600,
        download_timeout=30,
        transcription_timeout=60
    )
    config.create_directory_structure()

    # Mockar componentes externos (downloader, extractor, AI provider)
    dummy_title = "E2E Test Video"
    dummy_duration = 120
    dummy_transcription = "Transcrição E2E test."
    dummy_summary = "Resumo E2E test."

    with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as dl_cls, \
         patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor') as ex_cls, \
         patch('src.infrastructure.providers.whisper_provider.WhisperProvider') as ai_cls, \
         patch('webbrowser.open', new_callable=Mock) as mock_open:

        # Instâncias mock
        mock_dl = dl_cls.return_value
        mock_ex = ex_cls.return_value
        mock_ai = ai_cls.return_value

        mock_dl.extract_info = AsyncMock(return_value={'title': dummy_title, 'duration': dummy_duration, 'uploader':'Channel'})
        # Criar um arquivo de vídeo dummy
        video_file = config.data_dir / "video.mp4"
        video_file.write_text("fake")
        mock_dl.download = AsyncMock(return_value=str(video_file))

        mock_ex.extract_audio = AsyncMock(return_value=str(config.temp_dir / "audio.wav"))

        mock_ai.transcribe = AsyncMock(return_value=dummy_transcription)
        mock_ai.summarize = AsyncMock(return_value=dummy_summary)

        # Executar use case real
        factory = InfrastructureFactory(config)
        deps = factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**deps)

        request = ProcessYouTubeVideoRequest(
            url="https://youtube.com/watch?v=e2e_test",
            language="pt",
            generate_summary=True
        )
        result = await use_case.execute(request)

    # Verificar HTML gerado
    html_path = config.data_dir / "output" / f"{result.video.id}.html"
    assert html_path.exists(), "HTML não foi gerado"
    content = html_path.read_text(encoding='utf-8')
    assert dummy_title in content
    assert dummy_transcription in content
    assert dummy_summary in content

    # Verificar que webbrowser.open foi chamado
    mock_open.assert_called_once()

    # Verificar limpeza de arquivos temporários
    # temp_dir deve estar vazio
    assert not any((config.temp_dir).rglob('*')), "Arquivos temporários não foram removidos"
