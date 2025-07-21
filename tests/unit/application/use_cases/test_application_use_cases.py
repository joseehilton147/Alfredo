"""Testes unitários simplificados para Use Cases da camada de aplicação."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path

from src.application.use_cases.process_local_video import (
    ProcessLocalVideoUseCase,
    ProcessLocalVideoRequest,
    ProcessLocalVideoResponse
)
from src.application.use_cases.process_youtube_video import (
    ProcessYouTubeVideoUseCase,
    ProcessYouTubeVideoRequest,
    ProcessYouTubeVideoResponse
)
from src.application.use_cases.transcribe_audio import (
    TranscribeAudioUseCase,
    TranscribeAudioRequest,
    TranscribeAudioResponse
)
from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
    DownloadFailedError
)


class TestProcessLocalVideoUseCase:
    """Testes para ProcessLocalVideoUseCase."""

    @pytest.fixture
    def mock_extractor(self):
        """Mock do AudioExtractorGateway."""
        mock = AsyncMock(spec=AudioExtractorGateway)
        mock.get_audio_info.return_value = {'duration': 120.5}
        return mock

    @pytest.fixture
    def mock_ai_provider(self):
        """Mock do AIProviderInterface."""
        mock = AsyncMock(spec=AIProviderInterface)
        mock.transcribe_audio.return_value = "Transcrição de teste."
        mock.__class__.__name__ = "MockAIProvider"
        return mock

    @pytest.fixture
    def mock_storage(self):
        """Mock do StorageGateway."""
        mock = AsyncMock(spec=StorageGateway)
        mock.load_video.return_value = None
        mock.load_transcription.return_value = None
        return mock

    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        config = Mock(spec=AlfredoConfig)
        config.temp_dir = Path("/tmp/alfredo")
        config.audio_sample_rate = 16000
        return config

    @pytest.fixture
    def use_case(self, mock_extractor, mock_ai_provider, mock_storage, mock_config):
        """Instância do Use Case com dependências mockadas."""
        return ProcessLocalVideoUseCase(
            extractor=mock_extractor,
            ai_provider=mock_ai_provider,
            storage=mock_storage,
            config=mock_config
        )

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, use_case):
        """Testa erro quando arquivo não existe."""
        # Arrange
        request = ProcessLocalVideoRequest(
            file_path="/path/to/nonexistent.mp4",
            language="pt"
        )
        
        with patch('pathlib.Path.exists', return_value=False):
            # Act & Assert
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                await use_case.execute(request)
            
            assert "Arquivo não encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_unsupported_format(self, use_case):
        """Testa erro com formato não suportado."""
        # Arrange
        request = ProcessLocalVideoRequest(
            file_path="/path/to/video.xyz",
            language="pt"
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            # Act & Assert
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                await use_case.execute(request)
            
            assert "Formato de vídeo não suportado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cancel_processing(self, use_case):
        """Testa cancelamento do processamento."""
        # Arrange
        request = ProcessLocalVideoRequest(
            file_path="/path/to/video.mp4",
            language="pt"
        )
        
        await use_case.cancel_processing()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            
            mock_stat.return_value.st_size = 1024000
            mock_stat.return_value.st_mtime = 1640995200
            
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                await use_case.execute(request)
            
            assert "Processamento cancelado pelo usuário" in str(exc_info.value)

    def test_is_supported_video_format(self, use_case):
        """Testa validação de formatos suportados."""
        # Arrange & Act & Assert
        assert use_case._is_supported_video_format(Path("video.mp4"))
        assert use_case._is_supported_video_format(Path("video.avi"))
        assert use_case._is_supported_video_format(Path("video.mkv"))
        assert use_case._is_supported_video_format(Path("video.mov"))
        assert use_case._is_supported_video_format(Path("video.wmv"))
        assert use_case._is_supported_video_format(Path("video.flv"))
        assert use_case._is_supported_video_format(Path("video.webm"))
        
        # Formatos não suportados
        assert not use_case._is_supported_video_format(Path("video.xyz"))
        assert not use_case._is_supported_video_format(Path("video.txt"))


class TestProcessYouTubeVideoUseCase:
    """Testes para ProcessYouTubeVideoUseCase."""

    @pytest.fixture
    def mock_downloader(self):
        """Mock do VideoDownloaderGateway."""
        mock = AsyncMock(spec=VideoDownloaderGateway)
        mock.extract_info.return_value = {
            'id': 'test_video_id',
            'title': 'Vídeo de Teste',
            'duration': 180.5
        }
        mock.download.return_value = "/path/to/downloaded_video.mp4"
        return mock

    @pytest.fixture
    def mock_extractor(self):
        """Mock do AudioExtractorGateway."""
        return AsyncMock(spec=AudioExtractorGateway)

    @pytest.fixture
    def mock_ai_provider(self):
        """Mock do AIProviderInterface."""
        mock = AsyncMock(spec=AIProviderInterface)
        mock.transcribe_audio.return_value = "Transcrição do YouTube."
        mock.__class__.__name__ = "MockAIProvider"
        return mock

    @pytest.fixture
    def mock_storage(self):
        """Mock do StorageGateway."""
        mock = AsyncMock(spec=StorageGateway)
        mock.load_video.return_value = None
        mock.load_transcription.return_value = None
        return mock

    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        config = Mock(spec=AlfredoConfig)
        config.temp_dir = Mock()
        config.temp_dir.__truediv__ = Mock(return_value="/tmp/alfredo/youtube_test_video_id.wav")
        config.audio_sample_rate = 16000
        return config

    @pytest.fixture
    def use_case(self, mock_downloader, mock_extractor, mock_ai_provider, mock_storage, mock_config):
        """Instância do Use Case com dependências mockadas."""
        return ProcessYouTubeVideoUseCase(
            downloader=mock_downloader,
            extractor=mock_extractor,
            ai_provider=mock_ai_provider,
            storage=mock_storage,
            config=mock_config
        )

    @pytest.mark.asyncio
    async def test_execute_extract_info_error(self, use_case, mock_downloader):
        """Testa erro na extração de informações do vídeo."""
        # Arrange
        request = ProcessYouTubeVideoRequest(
            url="https://www.youtube.com/watch?v=invalid",
            language="pt"
        )
        
        mock_downloader.extract_info.side_effect = DownloadFailedError(
            request.url, "URL inválida"
        )
        
        # Act & Assert
        with pytest.raises(DownloadFailedError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cancel_processing(self, use_case):
        """Testa cancelamento do processamento."""
        # Arrange
        request = ProcessYouTubeVideoRequest(
            url="https://www.youtube.com/watch?v=test",
            language="pt"
        )
        
        await use_case.cancel_processing()
        
        # Act & Assert
        with pytest.raises(DownloadFailedError) as exc_info:
            await use_case.execute(request)
        
        assert "Processamento cancelado pelo usuário" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, use_case, mock_downloader):
        """Testa tratamento de erro inesperado."""
        # Arrange
        request = ProcessYouTubeVideoRequest(
            url="https://www.youtube.com/watch?v=test",
            language="pt"
        )
        
        mock_downloader.extract_info.side_effect = Exception("Erro inesperado")
        
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            await use_case.execute(request)
        
        assert "Erro inesperado no processamento" in str(exc_info.value)


class TestTranscribeAudioUseCase:
    """Testes para TranscribeAudioUseCase."""

    @pytest.fixture
    def mock_ai_provider(self):
        """Mock do AIProviderInterface."""
        mock = AsyncMock(spec=AIProviderInterface)
        mock.transcribe_audio.return_value = "Transcrição de áudio."
        mock.__class__.__name__ = "MockAIProvider"
        return mock

    @pytest.fixture
    def mock_storage(self):
        """Mock do StorageGateway."""
        mock = AsyncMock(spec=StorageGateway)
        mock.load_transcription.return_value = None
        return mock

    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        return Mock(spec=AlfredoConfig)

    @pytest.fixture
    def use_case(self, mock_ai_provider, mock_storage, mock_config):
        """Instância do Use Case com dependências mockadas."""
        return TranscribeAudioUseCase(
            ai_provider=mock_ai_provider,
            storage=mock_storage,
            config=mock_config
        )

    @pytest.mark.asyncio
    async def test_execute_video_not_found(self, use_case, mock_storage):
        """Testa erro quando vídeo não é encontrado."""
        # Arrange
        request = TranscribeAudioRequest(
            video_id="nonexistent_video",
            audio_path="/path/to/audio.wav",
            language="pt"
        )
        
        mock_storage.load_video.return_value = None
        
        # Act & Assert
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            await use_case.execute(request)
        
        assert "Vídeo não encontrado" in str(exc_info.value)
        assert exc_info.value.field == "video_id"
        assert exc_info.value.value == "nonexistent_video"

    @pytest.mark.asyncio
    async def test_execute_audio_file_not_found(self, use_case, mock_storage):
        """Testa erro quando arquivo de áudio não existe."""
        # Arrange
        # Criar um mock de vídeo válido
        mock_video = Mock()
        mock_video.id = "test_video"
        mock_storage.load_video.return_value = mock_video
        
        request = TranscribeAudioRequest(
            video_id="test_video",
            audio_path="/path/to/nonexistent_audio.wav",
            language="pt"
        )
        
        with patch('os.path.exists', return_value=False):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                await use_case.execute(request)
            
            assert "Arquivo de áudio não encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_transcription_error(self, use_case, mock_storage, mock_ai_provider):
        """Testa erro na transcrição."""
        # Arrange
        mock_video = Mock()
        mock_video.id = "test_video"
        mock_storage.load_video.return_value = mock_video
        
        mock_ai_provider.transcribe_audio.side_effect = TranscriptionError(
            "/path/to/audio.wav", "Erro na transcrição"
        )
        
        request = TranscribeAudioRequest(
            video_id="test_video",
            audio_path="/path/to/audio.wav",
            language="pt"
        )
        
        with patch('os.path.exists', return_value=True):
            # Act & Assert
            with pytest.raises(TranscriptionError):
                await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_execute_empty_transcription(self, use_case, mock_storage, mock_ai_provider):
        """Testa erro quando transcrição retorna vazia."""
        # Arrange
        mock_video = Mock()
        mock_video.id = "test_video"
        mock_storage.load_video.return_value = mock_video
        
        mock_ai_provider.transcribe_audio.return_value = ""
        
        request = TranscribeAudioRequest(
            video_id="test_video",
            audio_path="/path/to/audio.wav",
            language="pt"
        )
        
        with patch('os.path.exists', return_value=True):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                await use_case.execute(request)
            
            assert "Transcrição resultou em texto vazio" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, use_case, mock_storage, mock_ai_provider):
        """Testa tratamento de erro inesperado."""
        # Arrange
        mock_video = Mock()
        mock_video.id = "test_video"
        mock_storage.load_video.return_value = mock_video
        
        mock_ai_provider.transcribe_audio.side_effect = Exception("Erro inesperado")
        
        request = TranscribeAudioRequest(
            video_id="test_video",
            audio_path="/path/to/audio.wav",
            language="pt"
        )
        
        with patch('os.path.exists', return_value=True):
            # Act & Assert
            with pytest.raises(TranscriptionError) as exc_info:
                await use_case.execute(request)
            
            assert "Erro inesperado na transcrição" in str(exc_info.value)