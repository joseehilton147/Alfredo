"""Factory para criação centralizada de dependências de infraestrutura."""

from typing import Dict, Any

from src.config.alfredo_config import AlfredoConfig
from src.application.interfaces.ai_provider import AIProviderInterface
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.domain.exceptions.alfredo_errors import ConfigurationError


class InfrastructureFactory:
    """
    Factory centralizada para criação de dependências de infraestrutura.
    
    Esta classe implementa o padrão Factory para centralizar a criação de
    todas as dependências de infraestrutura, incluindo cache de instâncias
    singleton para otimização de performance.
    """
    
    def __init__(self, config: AlfredoConfig):
        """
        Inicializa a factory com configuração.
        
        Args:
            config: Configuração tipada do Alfredo
        """
        self._config = config
        self._instances: Dict[str, Any] = {}  # Cache de instâncias singleton
    
    def create_video_downloader(self) -> VideoDownloaderGateway:
        """
        Cria implementação de VideoDownloaderGateway.
        
        Returns:
            Instância de VideoDownloaderGateway
            
        Raises:
            ConfigurationError: Se não conseguir criar a instância
        """
        cache_key = 'video_downloader'
        
        if cache_key not in self._instances:
            try:
                # Import dinâmico para evitar dependências circulares
                from src.infrastructure.downloaders.ytdlp_downloader import YTDLPDownloader
                self._instances[cache_key] = YTDLPDownloader(self._config)
            except ImportError as e:
                raise ConfigurationError(
                    "video_downloader_dependency",
                    f"Não foi possível importar YTDLPDownloader: {e}",
                    expected="yt-dlp instalado",
                    details={"error": str(e)}
                )
        
        return self._instances[cache_key]
    
    def create_audio_extractor(self) -> AudioExtractorGateway:
        """
        Cria implementação de AudioExtractorGateway.
        
        Returns:
            Instância de AudioExtractorGateway
            
        Raises:
            ConfigurationError: Se não conseguir criar a instância
        """
        cache_key = 'audio_extractor'
        
        if cache_key not in self._instances:
            try:
                # Import dinâmico para evitar dependências circulares
                from src.infrastructure.extractors.ffmpeg_extractor import FFmpegExtractor
                self._instances[cache_key] = FFmpegExtractor(self._config)
            except ImportError as e:
                raise ConfigurationError(
                    "audio_extractor_dependency",
                    f"Não foi possível importar FFmpegExtractor: {e}",
                    expected="ffmpeg-python instalado",
                    details={"error": str(e)}
                )
        
        return self._instances[cache_key]
    
    def create_ai_provider(self, provider_type: str = None) -> AIProviderInterface:
        """
        Cria implementação de AIProviderInterface.
        
        Args:
            provider_type: Tipo do provider (whisper, groq, ollama)
                          Se None, usa o padrão da configuração
        
        Returns:
            Instância de AIProviderInterface
            
        Raises:
            ConfigurationError: Se provider não é suportado
        """
        provider_type = provider_type or self._config.default_ai_provider
        cache_key = f'ai_provider_{provider_type}'
        
        if cache_key not in self._instances:
            if provider_type == "whisper":
                try:
                    from src.infrastructure.providers.whisper_provider import WhisperProvider
                    self._instances[cache_key] = WhisperProvider(self._config)
                except ImportError as e:
                    raise ConfigurationError(
                        "whisper_dependency",
                        f"Não foi possível importar WhisperProvider: {e}",
                        expected="openai-whisper instalado",
                        details={"provider": provider_type, "error": str(e)}
                    )
            elif provider_type == "groq":
                try:
                    from src.infrastructure.providers.groq_provider import GroqProvider
                    self._instances[cache_key] = GroqProvider(self._config)
                except ImportError as e:
                    raise ConfigurationError(
                        "groq_dependency",
                        f"Não foi possível importar GroqProvider: {e}",
                        expected="groq instalado",
                        details={"provider": provider_type, "error": str(e)}
                    )
            elif provider_type == "ollama":
                try:
                    from src.infrastructure.providers.ollama_provider import OllamaProvider
                    self._instances[cache_key] = OllamaProvider(self._config)
                except ImportError as e:
                    raise ConfigurationError(
                        "ollama_dependency",
                        f"Não foi possível importar OllamaProvider: {e}",
                        expected="ollama instalado",
                        details={"provider": provider_type, "error": str(e)}
                    )
            elif provider_type == "mock":
                try:
                    from src.infrastructure.providers.mock_provider_strategy import MockProviderStrategy
                    self._instances[cache_key] = MockProviderStrategy(self._config)
                except ImportError as e:
                    raise ConfigurationError(
                        "mock_dependency",
                        f"Não foi possível importar MockProviderStrategy: {e}",
                        expected="MockProvider disponível",
                        details={"provider": provider_type, "error": str(e)}
                    )
            else:
                raise ConfigurationError(
                    "ai_provider_type", 
                    f"Provider '{provider_type}' não suportado",
                    expected="whisper, groq, ollama, mock",
                    details={
                        "requested_provider": provider_type,
                        "available_providers": ["whisper", "groq", "ollama", "mock"]
                    }
                )
        
        return self._instances[cache_key]
    
    def create_storage(self, storage_type: str = "filesystem") -> StorageGateway:
        """
        Cria implementação de StorageGateway.
        
        Args:
            storage_type: Tipo de storage (filesystem, json)
        
        Returns:
            Instância de StorageGateway
            
        Raises:
            ConfigurationError: Se storage não é suportado
        """
        cache_key = f'storage_{storage_type}'
        
        if cache_key not in self._instances:
            if storage_type == "filesystem":
                try:
                    from src.infrastructure.storage.filesystem_storage import FileSystemStorage
                    self._instances[cache_key] = FileSystemStorage(self._config)
                except ImportError as e:
                    raise ConfigurationError(
                        "filesystem_storage_dependency",
                        f"Não foi possível importar FileSystemStorage: {e}",
                        expected="módulo filesystem_storage disponível",
                        details={"storage_type": storage_type, "error": str(e)}
                    )
            elif storage_type == "json":
                try:
                    from src.infrastructure.repositories.json_video_repository import JsonVideoRepository
                    # Adapter para compatibilidade com StorageGateway
                    from src.infrastructure.storage.json_storage_adapter import JsonStorageAdapter
                    repository = JsonVideoRepository(str(self._config.data_dir / "output"))
                    self._instances[cache_key] = JsonStorageAdapter(repository)
                except ImportError as e:
                    raise ConfigurationError(
                        "json_storage_dependency",
                        f"Não foi possível importar JsonStorage: {e}",
                        expected="módulo json_storage disponível",
                        details={"storage_type": storage_type, "error": str(e)}
                    )
            else:
                raise ConfigurationError(
                    "storage_type",
                    f"Storage '{storage_type}' não suportado",
                    expected="filesystem, json",
                    details={
                        "requested_storage": storage_type,
                        "available_storages": ["filesystem", "json"]
                    }
                )
        
        return self._instances[cache_key]
    
    def create_all_dependencies(self, provider_type: str = None, 
                               storage_type: str = "filesystem") -> Dict[str, Any]:
        """
        Cria todas as dependências de uma vez para injeção em Use Cases.
        
        Args:
            provider_type: Tipo do AI provider (whisper, groq, ollama)
            storage_type: Tipo de storage (filesystem, json)
        
        Returns:
            Dicionário com todas as dependências criadas
            
        Raises:
            ConfigurationError: Se alguma dependência não pode ser criada
        """
        # Validar provider_type antes de criar
        if provider_type:
            self._validate_provider_type(provider_type)
        
        # Validar storage_type antes de criar
        self._validate_storage_type(storage_type)
        
        try:
            # Preparar dicionário de dependências para injeção em UseCases
            dependencies = {
                'downloader': self.create_video_downloader(),
                'extractor': self.create_audio_extractor(),
                'ai_provider': self.create_ai_provider(provider_type),
                'storage': self.create_storage(storage_type),
                'config': self._config
            }
            
            # Validar que todas as dependências foram criadas
            for key, value in dependencies.items():
                if value is None:
                    raise ConfigurationError(
                        f"dependency_{key}",
                        f"Falha ao criar dependência {key}",
                        expected="instância válida",
                        details={"dependency": key, "provider_type": provider_type, "storage_type": storage_type}
                    )
            
            return dependencies
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            else:
                raise ConfigurationError(
                    "dependency_creation",
                    f"Erro inesperado ao criar dependências: {str(e)}",
                    expected="criação bem-sucedida de todas as dependências",
                    details={"provider_type": provider_type, "storage_type": storage_type, "error": str(e)}
                )
    
    def _validate_provider_type(self, provider_type: str) -> None:
        """
        Valida se o tipo de provider é suportado.
        
        Args:
            provider_type: Tipo do provider para validar
            
        Raises:
            ConfigurationError: Se provider não é suportado
        """
        supported_providers = ["whisper", "groq", "ollama"]
        
        if provider_type not in supported_providers:
            raise ConfigurationError(
                "ai_provider_validation",
                f"Provider '{provider_type}' não é suportado",
                expected=f"um dos: {', '.join(supported_providers)}",
                details={
                    "requested_provider": provider_type,
                    "supported_providers": supported_providers
                }
            )
    
    def _validate_storage_type(self, storage_type: str) -> None:
        """
        Valida se o tipo de storage é suportado.
        
        Args:
            storage_type: Tipo do storage para validar
            
        Raises:
            ConfigurationError: Se storage não é suportado
        """
        supported_storages = ["filesystem", "json"]
        
        if storage_type not in supported_storages:
            raise ConfigurationError(
                "storage_type_validation",
                f"Storage '{storage_type}' não é suportado",
                expected=f"um dos: {', '.join(supported_storages)}",
                details={
                    "requested_storage": storage_type,
                    "supported_storages": supported_storages
                }
            )
    
    def clear_cache(self) -> None:
        """Limpa o cache de instâncias (útil para testes)."""
        self._instances.clear()
    
    def get_cached_instances(self) -> Dict[str, Any]:
        """
        Retorna cópia do cache de instâncias (útil para debugging).
        
        Returns:
            Dicionário com instâncias em cache
        """
        return self._instances.copy()