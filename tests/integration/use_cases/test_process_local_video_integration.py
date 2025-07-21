"""Integration tests for the ProcessLocalVideoUseCase."""

import asyncio
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.application.use_cases.process_local_video import (
    ProcessLocalVideoRequest,
    ProcessLocalVideoUseCase,
)
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_video_file(temp_dir):
    """Create a dummy video file for testing."""
    video_path = temp_dir / "test_video.mp4"
    video_path.touch()
    return video_path


@pytest.fixture
def config(temp_dir):
    """Create a test configuration."""
    return AlfredoConfig(
        temp_dir=temp_dir,
        storage_dir=temp_dir,
        audio_sample_rate=16000,
    )


@pytest.fixture
def storage_gateway(config):
    """Create a StorageGateway instance with a temporary database."""
    return StorageGateway(config)


@pytest.fixture
def audio_extractor_gateway():
    """Create an AudioExtractorGateway instance."""
    return AudioExtractorGateway()


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider."""
    provider = AsyncMock()
    provider.transcribe_audio = AsyncMock(return_value="Test transcription")
    return provider


@pytest.fixture
def use_case(
    audio_extractor_gateway, mock_ai_provider, storage_gateway, config
):
    """Create use case instance."""
    return ProcessLocalVideoUseCase(
        extractor=audio_extractor_gateway,
        ai_provider=mock_ai_provider,
        storage=storage_gateway,
        config=config,
    )


@pytest.mark.asyncio
async def test_process_local_video_success(
    use_case: ProcessLocalVideoUseCase, test_video_file: Path, temp_dir: Path
):
    """Test successful processing of a local video."""
    # Arrange
    request = ProcessLocalVideoRequest(file_path=str(test_video_file))

    # Act
    response = await use_case.execute(request)

    # Assert
    assert response.transcription == "Test transcription"
    assert response.was_cached is False
    assert response.video.title == test_video_file.name

    # Check if the temporary audio file is deleted
    temp_audio_file = temp_dir / f"{response.video.id}.wav"
    assert not temp_audio_file.exists()

    # Check if the video and transcription are saved in the database
    saved_video = await use_case.storage.load_video(response.video.id)
    saved_transcription = await use_case.storage.load_transcription(
        response.video.id
    )
    assert saved_video is not None
    assert saved_transcription == "Test transcription"


@pytest.mark.asyncio
async def test_process_local_video_caching(
    use_case: ProcessLocalVideoUseCase, test_video_file: Path
):
    """Test that a processed video is retrieved from cache."""
    # Arrange
    request = ProcessLocalVideoRequest(file_path=str(test_video_file))
    await use_case.execute(request)  # First execution

    # Act
    response = await use_case.execute(request)  # Second execution

    # Assert
    assert response.was_cached is True
    assert response.transcription == "Test transcription"


@pytest.mark.asyncio
async def test_process_local_video_invalid_path(use_case: ProcessLocalVideoUseCase):
    """Test processing with an invalid file path."""
    # Arrange
    request = ProcessLocalVideoRequest(file_path="/invalid/path/to/video.mp4")

    # Act & Assert
    with pytest.raises(InvalidVideoFormatError):
        await use_case.execute(request)


@pytest.mark.asyncio
async def test_process_local_video_unsupported_format(
    use_case: ProcessLocalVideoUseCase, temp_dir: Path
):
    """Test processing with an unsupported video format."""
    # Arrange
    unsupported_file = temp_dir / "video.txt"
    unsupported_file.touch()
    request = ProcessLocalVideoRequest(file_path=str(unsupported_file))

    # Act & Assert
    with pytest.raises(InvalidVideoFormatError):
        await use_case.execute(request)
