import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import shutil

from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase, ProcessYouTubeVideoRequest
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.entities.audio_track import AudioTrack
from src.domain.entities.transcription import Transcription
from src.domain.entities.summary import Summary
from src.domain.exceptions.alfredo_errors import DownloadFailedError, TranscriptionError

# Define um diretório temporário para os testes
@pytest.fixture(scope="module")
def temp_test_dir():
    temp_dir = Path("data/temp/integration_tests")
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_ai_provider():
    mock = AsyncMock()
    mock.transcribe.return_value = Transcription(text="mocked transcription", language="pt")
    mock.summarize.return_value = Summary(
        text="This is a mocked summary of the video content.",
        key_points=["mock", "test", "video"]
    )
    return mock

@pytest.fixture
def alfredo_config():
    return AlfredoConfig()

@pytest.mark.asyncio
async def test_summarize_youtube_video_integration_success(temp_test_dir, mock_ai_provider, alfredo_config):
    # Given
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (small video)
    
    # Configura o factory para usar o diretório temporário para armazenamento
    alfredo_config.output_summaries_youtube = temp_test_dir
    alfredo_config.temp_dir = temp_test_dir

    factory = InfrastructureFactory(config=alfredo_config)
    
    downloader = factory.create_video_downloader()
    storage = factory.create_storage("filesystem") # Assume filesystem storage
    
    # Mock the audio extractor
    mock_extractor = AsyncMock()
    mock_extractor.extract_audio.return_value = None # Mock the return value if needed

    with patch('src.infrastructure.factories.infrastructure_factory.InfrastructureFactory.create_audio_extractor', return_value=mock_extractor):
        # Injeta o mock_ai_provider
        use_case = ProcessYoutubeVideoUseCase(
            downloader=downloader,
            audio_extractor=mock_extractor, # Use the mocked extractor
            ai_provider=mock_ai_provider,
            storage=storage,
            config=alfredo_config
        )

        # When
        summary = await use_case.execute(ProcessYouTubeVideoRequest(url=youtube_url))

        # Then
        assert summary is not None
        assert isinstance(summary, Summary)
        assert "mocked summary" in summary.summary_text.lower()
        assert "mocked transcription" in mock_ai_provider.transcribe.call_args[0][0].text.lower() # Check if transcription was passed
        
        # Verify if the summary file was created in the temporary directory
        summary_file_path = Path(summary.file_path)
        assert summary_file_path.exists()
        assert summary_file_path.is_file()
        assert summary_file_path.parent == temp_test_dir

        # Clean up downloaded video and audio files
        # These are usually in the temp_dir or data/input/youtube
        # For this integration test, we expect them to be cleaned by the use case or downloader
        # We can check if the temp_test_dir is relatively clean after the test
        remaining_files = list(temp_test_dir.iterdir())
        # Allow for the summary HTML file to remain, but no large video/audio files
        assert len(remaining_files) == 1 # Only the summary HTML file should remain
        assert summary_file_path.name in [f.name for f in remaining_files]

        mock_ai_provider.transcribe.assert_called_once()
        mock_ai_provider.summarize.assert_called_once()

@pytest.mark.asyncio
async def test_summarize_youtube_video_integration_download_failure(temp_test_dir, mock_ai_provider, alfredo_config):
    # Given
    invalid_youtube_url = "https://www.youtube.com/watch?v=invalid_video_id"
    
    alfredo_config.output_summaries_youtube = temp_test_dir
    alfredo_config.temp_dir = temp_test_dir

    factory = InfrastructureFactory(config=alfredo_config)
    
    # Mock the downloader to raise an error
    mock_downloader = AsyncMock()
    mock_downloader.download.side_effect = DownloadFailedError(url=invalid_youtube_url, reason="Failed to download video")

    # Mock the audio extractor
    mock_extractor = AsyncMock()
    mock_extractor.extract_audio.return_value = None # Mock the return value if needed

    with patch('src.infrastructure.factories.infrastructure_factory.InfrastructureFactory.create_audio_extractor', return_value=mock_extractor):
        storage = factory.create_storage("filesystem")
        
        use_case = ProcessYoutubeVideoUseCase(
            downloader=mock_downloader,
            audio_extractor=mock_extractor, # Use the mocked extractor
            ai_provider=mock_ai_provider,
            storage=storage,
            config=alfredo_config
        )

        # When / Then
        with pytest.raises(DownloadFailedError, match="Failed to download video"):
            await use_case.execute(ProcessYouTubeVideoRequest(url=invalid_youtube_url))

        mock_downloader.download.assert_called_once_with(invalid_youtube_url)
        mock_ai_provider.transcribe.assert_not_called()
        mock_ai_provider.summarize.assert_not_called()

@pytest.mark.asyncio
async def test_summarize_youtube_video_integration_transcription_failure(temp_test_dir, mock_ai_provider, alfredo_config):
    # Given
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    alfredo_config.output_summaries_youtube = temp_test_dir
    alfredo_config.temp_dir = temp_test_dir

    factory = InfrastructureFactory(config=alfredo_config)
    
    downloader = factory.create_video_downloader()
    # Mock the audio extractor
    mock_extractor = AsyncMock()
    mock_extractor.extract_audio.return_value = None # Mock the return value if needed

    with patch('src.infrastructure.factories.infrastructure_factory.InfrastructureFactory.create_audio_extractor', return_value=mock_extractor):
        storage = factory.create_storage("filesystem")
        
        # Mock the AI provider to raise a transcription error
        mock_ai_provider.transcribe.side_effect = TranscriptionError(audio_path="mock_audio_path.wav", reason="Transcription service failed")

        use_case = ProcessYoutubeVideoUseCase(
            downloader=downloader,
            audio_extractor=mock_extractor, # Use the mocked extractor
            ai_provider=mock_ai_provider,
            storage=storage,
            config=alfredo_config
        )

        # When / Then
        with pytest.raises(TranscriptionError, match="Transcription service failed"):
            await use_case.execute(ProcessYouTubeVideoRequest(url=youtube_url))

        mock_ai_provider.transcribe.assert_called_once()
        mock_ai_provider.summarize.assert_not_called()
