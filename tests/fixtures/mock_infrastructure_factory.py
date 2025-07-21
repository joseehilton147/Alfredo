"""Mock Infrastructure Factory para testes."""

from typing import Dict, Any
from unittest.mock import AsyncMock, Mock

from src.config.alfredo_config import AlfredoConfig
from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.domain.exceptions.alfredo_errors import ConfigurationError


class MockVideoDownloaderGateway(VideoDownloaderGateway):
    """Mock implementation of VideoDownloaderGateway."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.download_calls = []
        self.extract_info_calls = []
        self.get_formats_calls = []
    
    async def download(self, url: str, output_dir: str, quality: str = "best") -> str:
        """Mock download method."""
        self.download_calls.append((url, output_dir, quality))
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import DownloadFailedError
            raise DownloadFailedError(url, "Mock download failure", http_code=404)
        
        return f"/mock/path/{url.split('/')[-1]}.mp4"
    
    async def extract_info(self, url: str) -> dict:
        """Mock extract_info method."""
        self.extract_info_calls.append(url)
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import DownloadFailedError
            raise DownloadFailedError(url, "Mock info extraction failure")
        
        return {
            "id": "mock_video_123",
            "title": "Mock Video Title",
            "duration": 120,
            "uploader": "Mock Channel",
            "description": "Mock video description"
        }
    
    async def get_available_formats(self, url: str) -> list:
        """Mock get_available_formats method."""
        self.get_formats_calls.append(url)
        
        return [
            {"format_id": "best", "ext": "mp4", "quality": "720p"},
            {"format_id": "worst", "ext": "mp4", "quality": "360p"}
        ]

    async def get_video_id(self, url: str) -> str:
        """Mock get_video_id method."""
        return "mock_video_id"

    async def is_url_supported(self, url: str) -> bool:
        """Mock is_url_supported method."""
        return True


class MockAudioExtractorGateway(AudioExtractorGateway):
    """Mock implementation of AudioExtractorGateway."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.extract_calls = []
        self.get_info_calls = []
    
    async def extract_audio(self, video_path: str, output_path: str, 
                          format: str = "wav", sample_rate: int = 16000) -> str:
        """Mock extract_audio method."""
        self.extract_calls.append((video_path, output_path, format, sample_rate))
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import TranscriptionError
            raise TranscriptionError(video_path, "Mock audio extraction failure")
        
        return output_path
    
    async def get_audio_info(self, video_path: str) -> dict:
        """Mock get_audio_info method."""
        self.get_info_calls.append(video_path)
        
        return {
            "duration": 120.5,
            "sample_rate": 44100,
            "channels": 2,
            "format": "mp4"
        }

    async def estimate_extraction_time(self, video_path: str, format: str = "wav") -> float:
        return 10.0

    async def extract_audio_segment(self, video_path: str, output_path: str, start_time: float, end_time: float, format: str = "wav", sample_rate: int = 16000) -> str:
        return output_path

    async def get_supported_formats(self) -> list:
        return ["wav", "mp3"]

    async def is_format_supported(self, format: str) -> bool:
        return True

    async def validate_video_file(self, video_path: str) -> bool:
        return True


class MockStorageGateway(StorageGateway):
    """Mock implementation of StorageGateway."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.videos = {}
        self.transcriptions = {}
        self.summaries = {}
        self.save_video_calls = []
        self.load_video_calls = []
        self.save_transcription_calls = []
        self.load_transcription_calls = []
        self.list_videos_calls = []
    
    async def save_video(self, video) -> None:
        """Mock save_video method."""
        self.save_video_calls.append(video)
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import ConfigurationError
            raise ConfigurationError("storage", "Mock save failure")
        
        self.videos[video.id] = video
    
    async def load_video(self, video_id: str):
        """Mock load_video method."""
        self.load_video_calls.append(video_id)
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import ConfigurationError
            raise ConfigurationError("storage", "Mock load failure")
        
        return self.videos.get(video_id)
    
    async def save_transcription(self, video_id: str, transcription: str, 
                               metadata: dict = None) -> None:
        """Mock save_transcription method."""
        self.save_transcription_calls.append((video_id, transcription, metadata))
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import ConfigurationError
            raise ConfigurationError("storage", "Mock transcription save failure")
        
        self.transcriptions[video_id] = {
            "transcription": transcription,
            "metadata": metadata or {}
        }
    
    async def load_transcription(self, video_id: str) -> str:
        """Mock load_transcription method."""
        self.load_transcription_calls.append(video_id)
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import ConfigurationError
            raise ConfigurationError("storage", "Mock transcription load failure")
        
        data = self.transcriptions.get(video_id)
        return data["transcription"] if data else None
    
    async def list_videos(self, limit: int = 100, offset: int = 0) -> list:
        """Mock list_videos method."""
        self.list_videos_calls.append((limit, offset))
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import ConfigurationError
            raise ConfigurationError("storage", "Mock list failure")
        
        videos = list(self.videos.values())
        return videos[offset:offset + limit]

    async def backup_data(self, backup_path: str) -> bool:
        return not self.should_fail

    async def cleanup_orphaned_data(self) -> int:
        return 0

    async def delete_video(self, video_id: str) -> bool:
        if video_id in self.videos:
            del self.videos[video_id]
            return True
        return False

    async def get_storage_stats(self) -> dict:
        return {}

    async def load_summary(self, video_id: str) -> str:
        return self.summaries.get(video_id)

    async def restore_data(self, backup_path: str) -> bool:
        return not self.should_fail

    async def save_summary(self, video_id: str, summary: str, metadata: dict = None) -> None:
        self.summaries[video_id] = summary

    async def video_exists(self, video_id: str) -> bool:
        return video_id in self.videos


class MockAIProvider(AIProviderInterface):
    """Mock implementation of AIProviderInterface."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.transcribe_calls = []
        self.get_supported_languages_calls = []
    
    async def transcribe_audio(self, audio_path: str, language: str = "pt") -> str:
        """Mock transcribe_audio method."""
        self.transcribe_calls.append((audio_path, language))
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import TranscriptionError
            raise TranscriptionError(audio_path, "Mock transcription failure")
        
        return f"Mock transcription for {audio_path} in {language}"
    
    def get_supported_languages(self) -> list[str]:
        """Mock get_supported_languages method."""
        self.get_supported_languages_calls.append(True)
        
        if self.should_fail:
            from src.domain.exceptions.alfredo_errors import ConfigurationError
            raise ConfigurationError("languages", "Mock languages failure")
        
        return ["pt", "en", "es", "fr"]


class MockInfrastructureFactory:
    """
    Mock Infrastructure Factory para testes.
    
    Esta factory cria mocks das dependências de infraestrutura para
    permitir testes isolados dos Use Cases sem dependências externas.
    """
    
    def __init__(self, config: AlfredoConfig = None, should_fail: bool = False):
        """
        Inicializa a mock factory.
        
        Args:
            config: Configuração (pode ser None para testes)
            should_fail: Se True, os mocks falharão nas operações
        """
        self.config = config or self._create_mock_config()
        self.should_fail = should_fail
        self._instances: Dict[str, Any] = {}
    
    def _create_mock_config(self) -> AlfredoConfig:
        """Cria uma configuração mock para testes."""
        # Usar valores que não causem validação de diretórios
        import tempfile
        from pathlib import Path
        temp_dir = Path(tempfile.mkdtemp())
        
        config = Mock(spec=AlfredoConfig)
        config.default_ai_provider = "whisper"
        config.whisper_model = "base"
        config.groq_model = "llama-3.3-70b-versatile"
        config.ollama_model = "llama3:8b"
        config.audio_sample_rate = 16000
        config.temp_dir = temp_dir
        config.data_dir = temp_dir
        config.max_video_duration = 3600
        config.download_timeout = 300
        config.transcription_timeout = 600
        
        return config
    
    def create_video_downloader(self) -> VideoDownloaderGateway:
        """Cria mock de VideoDownloaderGateway."""
        cache_key = 'video_downloader'
        
        if cache_key not in self._instances:
            self._instances[cache_key] = MockVideoDownloaderGateway(self.should_fail)
        
        return self._instances[cache_key]
    
    def create_audio_extractor(self) -> AudioExtractorGateway:
        """Cria mock de AudioExtractorGateway."""
        cache_key = 'audio_extractor'
        
        if cache_key not in self._instances:
            self._instances[cache_key] = MockAudioExtractorGateway(self.should_fail)
        
        return self._instances[cache_key]
    
    def create_ai_provider(self, provider_type: str = None) -> AIProviderInterface:
        """Cria mock de AIProviderInterface."""
        provider_type = provider_type or self.config.default_ai_provider
        cache_key = f'ai_provider_{provider_type}'
        
        if cache_key not in self._instances:
            # Validar provider_type
            if provider_type not in ["whisper", "groq", "ollama"]:
                raise ConfigurationError(
                    "ai_provider_type", 
                    f"Provider '{provider_type}' não suportado",
                    expected="whisper, groq, ollama"
                )
            
            self._instances[cache_key] = MockAIProvider(self.should_fail)
        
        return self._instances[cache_key]
    
    def create_storage(self, storage_type: str = "filesystem") -> StorageGateway:
        """Cria mock de StorageGateway."""
        cache_key = f'storage_{storage_type}'
        
        if cache_key not in self._instances:
            # Validar storage_type
            if storage_type not in ["filesystem", "json"]:
                raise ConfigurationError(
                    "storage_type",
                    f"Storage '{storage_type}' não suportado",
                    expected="filesystem, json"
                )
            
            self._instances[cache_key] = MockStorageGateway(self.should_fail)
        
        return self._instances[cache_key]
    
    def create_all_dependencies(self, provider_type: str = None, 
                               storage_type: str = "filesystem") -> Dict[str, Any]:
        """Cria todas as dependências mock."""
        return {
            'video_repository': self.create_storage(storage_type),
            'downloader': self.create_video_downloader(),
            'extractor': self.create_audio_extractor(),
            'ai_provider': self.create_ai_provider(provider_type),
            'storage': self.create_storage(storage_type),
            'config': self.config
        }
    
    def clear_cache(self) -> None:
        """Limpa o cache de instâncias."""
        self._instances.clear()
    
    def get_cached_instances(self) -> Dict[str, Any]:
        """Retorna cópia do cache de instâncias."""
        return self._instances.copy()
    
    def set_failure_mode(self, should_fail: bool) -> None:
        """Define se os mocks devem falhar."""
        self.should_fail = should_fail
        # Atualizar mocks existentes
        for instance in self._instances.values():
            if hasattr(instance, 'should_fail'):
                instance.should_fail = should_fail