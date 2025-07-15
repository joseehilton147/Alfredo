import pytest
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.transcribe_audio import (
    TranscribeAudioUseCase,
    TranscribeAudioRequest,
    TranscribeAudioResponse
)
from src.domain.entities.video import Video

class TestTranscribeAudioUseCase:
    
    @pytest.fixture
    def video_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def ai_provider(self):
        return AsyncMock()
    
    @pytest.fixture
    def use_case(self, video_repository, ai_provider):
        return TranscribeAudioUseCase(video_repository, ai_provider)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, use_case, video_repository, ai_provider):
        video = Video(id="test-123", title="Test Video")
        video_repository.find_by_id.return_value = video
        ai_provider.transcribe_audio.return_value = "Transcribed text"
        
        request = TranscribeAudioRequest(
            video_id="test-123",
            audio_path="/path/to/audio.wav"
        )
        
        response = await use_case.execute(request)
        
        assert isinstance(response, TranscribeAudioResponse)
        assert response.video == video
        assert response.transcription == "Transcribed text"
        video_repository.find_by_id.assert_called_once_with("test-123")
        ai_provider.transcribe_audio.assert_called_once_with("/path/to/audio.wav", "pt")
    
    @pytest.mark.asyncio
    async def test_execute_video_not_found(self, use_case, video_repository, ai_provider):
        video_repository.find_by_id.return_value = None
        
        request = TranscribeAudioRequest(
            video_id="nonexistent",
            audio_path="/path/to/audio.wav"
        )
        
        with pytest.raises(ValueError, match="Vídeo nonexistent não encontrado"):
            await use_case.execute(request)
