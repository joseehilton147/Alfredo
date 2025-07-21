"""
Testa fallback de abertura automática do HTML (quando webbrowser.open falha).
"""
import pytest
from unittest.mock import patch
from pathlib import Path
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase, ProcessYouTubeVideoRequest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_html_open_fallback(monkeypatch, tmp_path, capsys):
    config = AlfredoConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        temp_dir=tmp_path / "temp"
    )
    config.create_directory_structure()
    dummy_title = "Fallback Test Video"
    dummy_transcription = "Transcrição fallback test."
    dummy_summary = "Resumo fallback test."
    with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as dl_cls, \
         patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor') as ex_cls, \
         patch('src.infrastructure.providers.whisper_provider.WhisperProvider') as ai_cls, \
         patch('webbrowser.open', side_effect=Exception("Browser error")) as mock_open:
        mock_dl = dl_cls.return_value
        mock_ex = ex_cls.return_value
        mock_ai = ai_cls.return_value
        mock_dl.extract_info = lambda url: {'title': dummy_title, 'duration': 100, 'uploader': 'Channel'}
        mock_dl.download = lambda url, out, q: str(config.data_dir / "video.mp4")
        mock_ex.extract_audio = lambda v, a, **k: str(config.temp_dir / "audio.wav")
        mock_ai.transcribe = lambda a, l: dummy_transcription
        mock_ai.summarize = lambda t: dummy_summary
        factory = InfrastructureFactory(config)
        deps = factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**deps)
        request = ProcessYouTubeVideoRequest(url="https://youtube.com/watch?v=fallback_test", language="pt", generate_summary=True)
        await use_case.execute(request)
    captured = capsys.readouterr()
    assert "Não foi possível abrir automaticamente" in captured.out
    assert "HTML gerado em:" in captured.out
