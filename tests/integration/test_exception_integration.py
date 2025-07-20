"""
Testes de integração para verificar o uso correto das exceções específicas
em todo o sistema refatorado.

Este módulo testa se as exceções específicas são lançadas corretamente
pelos componentes refatorados.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.domain.exceptions import (
    AlfredoError,
    ProviderUnavailableError,
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
)

# Mock whisper module before importing WhisperProvider
with patch.dict('sys.modules', {'whisper': MagicMock()}):
    from src.infrastructure.providers.whisper_provider import WhisperProvider

from src.infrastructure.repositories.json_video_repository import JsonVideoRepository
from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
from src.domain.entities.video import Video


class TestWhisperProviderExceptions:
    """Testa se WhisperProvider lança exceções específicas."""
    
    def test_transcribe_audio_file_not_found(self):
        """Testa se TranscriptionError é lançada para arquivo não encontrado."""
        provider = WhisperProvider()
        
        with pytest.raises(TranscriptionError) as exc_info:
            # Use asyncio.run since the method is async
            import asyncio
            asyncio.run(provider.transcribe_audio("/path/that/does/not/exist.wav"))
        
        error = exc_info.value
        assert error.audio_path == "/path/that/does/not/exist.wav"
        assert "não encontrado" in error.reason.lower()
        assert error.provider == "whisper"
        assert "model" in error.details
    
    @patch('whisper.load_model')
    def test_transcribe_audio_model_loading_error(self, mock_load_model):
        """Testa se ProviderUnavailableError é lançada para erro de modelo."""
        mock_load_model.side_effect = Exception("Model loading failed")
        
        provider = WhisperProvider()
        
        with pytest.raises(ProviderUnavailableError) as exc_info:
            import asyncio
            # Create a temporary file to avoid FileNotFoundError
            with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                asyncio.run(provider.transcribe_audio(temp_file.name))
        
        error = exc_info.value
        assert error.provider_name == "whisper"
        assert "modelo" in error.reason.lower()
        assert "model" in error.details
    
    @patch('whisper.load_model')
    def test_transcribe_audio_transcription_error(self, mock_load_model):
        """Testa se TranscriptionError é lançada para erro de transcrição."""
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        mock_load_model.return_value = mock_model
        
        provider = WhisperProvider()
        
        with pytest.raises(TranscriptionError) as exc_info:
            import asyncio
            # Create a temporary file to avoid FileNotFoundError
            with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                asyncio.run(provider.transcribe_audio(temp_file.name))
        
        error = exc_info.value
        assert error.provider == "whisper"
        assert "transcrição" in error.reason.lower()
        assert "model" in error.details


class TestJsonVideoRepositoryExceptions:
    """Testa se JsonVideoRepository lança exceções específicas."""
    
    @pytest.fixture
    def temp_repo_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.mark.asyncio
    async def test_find_by_id_corrupted_json(self, temp_repo_dir):
        """Testa se InvalidVideoFormatError é lançada para JSON corrompido."""
        repo = JsonVideoRepository(temp_repo_dir)
        
        # Criar arquivo JSON corrompido
        video_dir = Path(temp_repo_dir) / "test_video"
        video_dir.mkdir()
        metadata_file = video_dir / "metadata.json"
        metadata_file.write_text("{ invalid json", encoding="utf-8")
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            await repo.find_by_id("test_video")
        
        error = exc_info.value
        assert error.field == "metadata"
        assert "corrompido" in error.constraint.lower()
        assert "test_video" in error.details["video_id"]
    
    @pytest.mark.asyncio
    async def test_save_permission_error(self, temp_repo_dir):
        """Testa se ConfigurationError é lançada para erro de permissão."""
        repo = JsonVideoRepository(temp_repo_dir)
        
        video = Video(
            id="test_video",
            title="Test Video",
            file_path="/test/path.mp4"
        )
        
        # Mock permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigurationError) as exc_info:
                await repo.save(video)
        
        error = exc_info.value
        assert error.config_key == "file_permissions"
        assert "permissão" in error.reason.lower()
        assert error.expected == "permissões de escrita"
        assert "test_video" in error.details["video_id"]
    
    @pytest.mark.asyncio
    async def test_save_disk_space_error(self, temp_repo_dir):
        """Testa se ConfigurationError é lançada para erro de espaço em disco."""
        repo = JsonVideoRepository(temp_repo_dir)
        
        video = Video(
            id="test_video",
            title="Test Video",
            file_path="/test/path.mp4"
        )
        
        # Mock OSError (disk space)
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with pytest.raises(ConfigurationError) as exc_info:
                await repo.save(video)
        
        error = exc_info.value
        assert error.config_key == "storage_space"
        assert "sistema" in error.reason.lower()
        assert error.expected == "espaço em disco suficiente"
        assert "test_video" in error.details["video_id"]


class TestProcessYouTubeVideoUseCaseExceptions:
    """Testa se ProcessYouTubeVideoUseCase lança exceções específicas."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Cria mocks das dependências."""
        video_repo = Mock()
        ai_provider = Mock()
        return video_repo, ai_provider
    
    @pytest.mark.asyncio
    async def test_missing_yt_dlp_dependency(self, mock_dependencies):
        """Testa se ConfigurationError é lançada quando yt-dlp não está disponível."""
        video_repo, ai_provider = mock_dependencies
        use_case = ProcessYouTubeVideoUseCase(video_repo, ai_provider)
        
        from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoRequest
        request = ProcessYouTubeVideoRequest(url="https://youtube.com/watch?v=test")
        
        # Mock ImportError for yt-dlp
        with patch('src.application.use_cases.process_youtube_video.yt_dlp', None):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'yt_dlp'")):
                with pytest.raises(ConfigurationError) as exc_info:
                    await use_case._download_video(request.url, request.output_dir)
        
        error = exc_info.value
        assert error.config_key == "yt_dlp_dependency"
        assert "yt-dlp" in error.reason.lower()
        assert error.expected == "pip install yt-dlp"
    
    @pytest.mark.asyncio
    async def test_download_private_video_error(self, mock_dependencies):
        """Testa se DownloadFailedError é lançada para vídeo privado."""
        video_repo, ai_provider = mock_dependencies
        use_case = ProcessYouTubeVideoUseCase(video_repo, ai_provider)
        
        # Mock yt-dlp DownloadError
        mock_yt_dlp = MagicMock()
        mock_yt_dlp.DownloadError = Exception  # Use Exception as base for the mock
        
        def mock_extract_info(*args, **kwargs):
            raise Exception("This video is private")
        
        mock_ydl = MagicMock()
        mock_ydl.extract_info = mock_extract_info
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        
        with patch('src.application.use_cases.process_youtube_video.yt_dlp', mock_yt_dlp):
            with pytest.raises(DownloadFailedError) as exc_info:
                await use_case._download_video("https://youtube.com/watch?v=private", "output")
        
        error = exc_info.value
        assert "private" in error.url
        assert "privado" in error.reason.lower() or "private" in error.reason.lower()
    
    @pytest.mark.asyncio
    async def test_cancellation_during_download(self, mock_dependencies):
        """Testa se DownloadFailedError é lançada para cancelamento."""
        video_repo, ai_provider = mock_dependencies
        use_case = ProcessYouTubeVideoUseCase(video_repo, ai_provider)
        
        from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoRequest
        request = ProcessYouTubeVideoRequest(url="https://youtube.com/watch?v=test")
        
        # Simular cancelamento
        use_case._cancelled = True
        
        with pytest.raises(DownloadFailedError) as exc_info:
            await use_case.execute(request)
        
        error = exc_info.value
        assert "cancelado" in error.reason.lower()
        assert error.url == request.url


class TestExceptionSerialization:
    """Testa serialização de exceções para logging e debugging."""
    
    def test_all_exceptions_serialize_correctly(self):
        """Verifica que todas as exceções podem ser serializadas."""
        exceptions = [
            AlfredoError("Test error", {"key": "value"}),
            ProviderUnavailableError("whisper", "Test reason"),
            DownloadFailedError("http://test.com", "Test reason", 404),
            TranscriptionError("/test/path.wav", "Test reason", "whisper"),
            InvalidVideoFormatError("field", "value", "constraint"),
            ConfigurationError("key", "reason", "expected"),
        ]
        
        for exception in exceptions:
            result = exception.to_dict()
            
            # Verificar campos obrigatórios
            assert "error_type" in result
            assert "message" in result
            assert "details" in result
            assert "timestamp" in result
            
            # Verificar que pode ser serializado como JSON
            json_str = json.dumps(result, default=str)
            assert json_str is not None
            
            # Verificar que pode ser deserializado
            parsed = json.loads(json_str)
            assert parsed["error_type"] == exception.__class__.__name__
            assert parsed["message"] == exception.message
    
    def test_exception_chaining_preservation(self):
        """Verifica que o encadeamento de exceções é preservado."""
        original_error = ValueError("Original error")
        
        alfredo_error = AlfredoError("Wrapped error", cause=original_error)
        result = alfredo_error.to_dict()
        
        assert result["cause"] == "Original error"
        assert result["cause_type"] == "ValueError"
    
    def test_exception_details_preservation(self):
        """Verifica que detalhes específicos são preservados."""
        error = DownloadFailedError(
            "https://test.com/video", 
            "Network timeout",
            http_code=408,
            details={"retry_count": 3, "timeout": 30}
        )
        
        result = error.to_dict()
        
        assert result["details"]["url"] == "https://test.com/video"
        assert result["details"]["reason"] == "Network timeout"
        assert result["details"]["http_code"] == 408
        assert result["details"]["retry_count"] == 3
        assert result["details"]["timeout"] == 30


class TestExceptionHandlingInMain:
    """Testa tratamento de exceções no módulo principal."""
    
    def test_exception_hierarchy_is_correct(self):
        """Verifica que a hierarquia de exceções está correta."""
        # Todas as exceções específicas devem herdar de AlfredoError
        specific_exceptions = [
            ProviderUnavailableError,
            DownloadFailedError,
            TranscriptionError,
            InvalidVideoFormatError,
            ConfigurationError,
        ]
        
        for exception_class in specific_exceptions:
            assert issubclass(exception_class, AlfredoError)
            assert issubclass(exception_class, Exception)
        
        # AlfredoError deve herdar de Exception
        assert issubclass(AlfredoError, Exception)
    
    def test_exception_imports_work_correctly(self):
        """Verifica que as exceções podem ser importadas corretamente."""
        # Teste direto das importações do módulo de exceções
        from src.domain.exceptions import (
            AlfredoError,
            DownloadFailedError,
            TranscriptionError,
            InvalidVideoFormatError,
            ConfigurationError,
            ProviderUnavailableError
        )
        
        # Verificar que são as classes corretas
        assert issubclass(DownloadFailedError, AlfredoError)
        assert issubclass(TranscriptionError, AlfredoError)
        assert issubclass(InvalidVideoFormatError, AlfredoError)
        assert issubclass(ConfigurationError, AlfredoError)
        assert issubclass(ProviderUnavailableError, AlfredoError)