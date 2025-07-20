"""Testes unitários para InfrastructureFactory."""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError


@pytest.fixture
def mock_config():
    """Cria configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.default_ai_provider = "whisper"
    config.data_dir = Path("/mock/data")
    config.temp_dir = Path("/mock/temp")
    return config


@pytest.fixture
def factory(mock_config):
    """Cria factory com configuração mock."""
    return InfrastructureFactory(mock_config)


class TestInfrastructureFactoryCreation:
    """Testes para criação da InfrastructureFactory."""
    
    def test_factory_initialization(self, mock_config):
        """Testa inicialização da factory."""
        factory = InfrastructureFactory(mock_config)
        
        assert factory._config == mock_config
        assert factory._instances == {}
    
    def test_factory_requires_config(self):
        """Testa que factory requer configuração."""
        with pytest.raises(TypeError):
            InfrastructureFactory()


class TestVideoDownloaderCreation:
    """Testes para criação de VideoDownloader."""
    
    @patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader')
    def test_create_video_downloader(self, mock_ytdlp_class, factory):
        """Testa criação de video downloader."""
        mock_instance = Mock()
        mock_ytdlp_class.return_value = mock_instance
        
        result = factory.create_video_downloader()
        
        assert result == mock_instance
        mock_ytdlp_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader')
    def test_create_video_downloader_singleton(self, mock_ytdlp_class, factory):
        """Testa que video downloader é singleton."""
        mock_instance = Mock()
        mock_ytdlp_class.return_value = mock_instance
        
        result1 = factory.create_video_downloader()
        result2 = factory.create_video_downloader()
        
        assert result1 == result2
        mock_ytdlp_class.assert_called_once()  # Chamado apenas uma vez


class TestAudioExtractorCreation:
    """Testes para criação de AudioExtractor."""
    
    @patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor')
    def test_create_audio_extractor(self, mock_ffmpeg_class, factory):
        """Testa criação de audio extractor."""
        mock_instance = Mock()
        mock_ffmpeg_class.return_value = mock_instance
        
        result = factory.create_audio_extractor()
        
        assert result == mock_instance
        mock_ffmpeg_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor')
    def test_create_audio_extractor_singleton(self, mock_ffmpeg_class, factory):
        """Testa que audio extractor é singleton."""
        mock_instance = Mock()
        mock_ffmpeg_class.return_value = mock_instance
        
        result1 = factory.create_audio_extractor()
        result2 = factory.create_audio_extractor()
        
        assert result1 == result2
        mock_ffmpeg_class.assert_called_once()


class TestAIProviderCreation:
    """Testes para criação de AI Provider."""
    
    @patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider')
    def test_create_ai_provider_whisper(self, mock_whisper_class, factory):
        """Testa criação de provider Whisper."""
        mock_instance = Mock()
        mock_whisper_class.return_value = mock_instance
        
        result = factory.create_ai_provider("whisper")
        
        assert result == mock_instance
        mock_whisper_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.GroqProvider')
    def test_create_ai_provider_groq(self, mock_groq_class, factory):
        """Testa criação de provider Groq."""
        mock_instance = Mock()
        mock_groq_class.return_value = mock_instance
        
        result = factory.create_ai_provider("groq")
        
        assert result == mock_instance
        mock_groq_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.OllamaProvider')
    def test_create_ai_provider_ollama(self, mock_ollama_class, factory):
        """Testa criação de provider Ollama."""
        mock_instance = Mock()
        mock_ollama_class.return_value = mock_instance
        
        result = factory.create_ai_provider("ollama")
        
        assert result == mock_instance
        mock_ollama_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider')
    def test_create_ai_provider_default(self, mock_whisper_class, factory):
        """Testa criação de provider padrão (sem especificar tipo)."""
        mock_instance = Mock()
        mock_whisper_class.return_value = mock_instance
        
        result = factory.create_ai_provider()
        
        assert result == mock_instance
        mock_whisper_class.assert_called_once_with(factory._config)
    
    def test_create_ai_provider_invalid_type(self, factory):
        """Testa criação de provider com tipo inválido."""
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_ai_provider("invalid_provider")
        
        assert "ai_provider" in str(exc_info.value)
        assert "não suportado" in str(exc_info.value)
        assert "whisper, groq, ollama" in str(exc_info.value)
    
    @patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider')
    def test_create_ai_provider_singleton(self, mock_whisper_class, factory):
        """Testa que AI provider é singleton por tipo."""
        mock_instance = Mock()
        mock_whisper_class.return_value = mock_instance
        
        result1 = factory.create_ai_provider("whisper")
        result2 = factory.create_ai_provider("whisper")
        
        assert result1 == result2
        mock_whisper_class.assert_called_once()
    
    @patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider')
    @patch('src.infrastructure.factories.infrastructure_factory.GroqProvider')
    def test_create_different_ai_providers(self, mock_groq_class, mock_whisper_class, factory):
        """Testa criação de diferentes tipos de AI provider."""
        mock_whisper = Mock()
        mock_groq = Mock()
        mock_whisper_class.return_value = mock_whisper
        mock_groq_class.return_value = mock_groq
        
        whisper_result = factory.create_ai_provider("whisper")
        groq_result = factory.create_ai_provider("groq")
        
        assert whisper_result == mock_whisper
        assert groq_result == mock_groq
        assert whisper_result != groq_result


class TestStorageCreation:
    """Testes para criação de Storage."""
    
    @patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage')
    def test_create_storage_filesystem(self, mock_fs_class, factory):
        """Testa criação de storage filesystem."""
        mock_instance = Mock()
        mock_fs_class.return_value = mock_instance
        
        result = factory.create_storage("filesystem")
        
        assert result == mock_instance
        mock_fs_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.JsonStorage')
    def test_create_storage_json(self, mock_json_class, factory):
        """Testa criação de storage JSON."""
        mock_instance = Mock()
        mock_json_class.return_value = mock_instance
        
        result = factory.create_storage("json")
        
        assert result == mock_instance
        mock_json_class.assert_called_once_with(factory._config)
    
    @patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage')
    def test_create_storage_default(self, mock_fs_class, factory):
        """Testa criação de storage padrão."""
        mock_instance = Mock()
        mock_fs_class.return_value = mock_instance
        
        result = factory.create_storage()
        
        assert result == mock_instance
        mock_fs_class.assert_called_once_with(factory._config)
    
    def test_create_storage_invalid_type(self, factory):
        """Testa criação de storage com tipo inválido."""
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_storage("invalid_storage")
        
        assert "storage_type" in str(exc_info.value)
        assert "não suportado" in str(exc_info.value)
        assert "filesystem, json" in str(exc_info.value)
    
    @patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage')
    def test_create_storage_singleton(self, mock_fs_class, factory):
        """Testa que storage é singleton por tipo."""
        mock_instance = Mock()
        mock_fs_class.return_value = mock_instance
        
        result1 = factory.create_storage("filesystem")
        result2 = factory.create_storage("filesystem")
        
        assert result1 == result2
        mock_fs_class.assert_called_once()


class TestCreateAllDependencies:
    """Testes para criação de todas as dependências."""
    
    @patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage')
    @patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider')
    @patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor')
    @patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader')
    def test_create_all_dependencies(self, mock_downloader, mock_extractor, 
                                   mock_ai_provider, mock_storage, factory):
        """Testa criação de todas as dependências."""
        # Arrange
        mock_downloader_instance = Mock()
        mock_extractor_instance = Mock()
        mock_ai_provider_instance = Mock()
        mock_storage_instance = Mock()
        
        mock_downloader.return_value = mock_downloader_instance
        mock_extractor.return_value = mock_extractor_instance
        mock_ai_provider.return_value = mock_ai_provider_instance
        mock_storage.return_value = mock_storage_instance
        
        # Act
        dependencies = factory.create_all_dependencies()
        
        # Assert
        assert 'downloader' in dependencies
        assert 'extractor' in dependencies
        assert 'ai_provider' in dependencies
        assert 'storage' in dependencies
        assert 'config' in dependencies
        
        assert dependencies['downloader'] == mock_downloader_instance
        assert dependencies['extractor'] == mock_extractor_instance
        assert dependencies['ai_provider'] == mock_ai_provider_instance
        assert dependencies['storage'] == mock_storage_instance
        assert dependencies['config'] == factory._config
    
    def test_create_all_dependencies_structure(self, factory):
        """Testa estrutura do dicionário de dependências."""
        with patch.multiple(
            'src.infrastructure.factories.infrastructure_factory',
            YTDLPDownloader=Mock(return_value=Mock()),
            FFmpegExtractor=Mock(return_value=Mock()),
            WhisperProvider=Mock(return_value=Mock()),
            FileSystemStorage=Mock(return_value=Mock())
        ):
            dependencies = factory.create_all_dependencies()
            
            expected_keys = {'downloader', 'extractor', 'ai_provider', 'storage', 'config'}
            assert set(dependencies.keys()) == expected_keys


class TestFactoryCaching:
    """Testes para sistema de cache da factory."""
    
    def test_cache_isolation_between_types(self, factory):
        """Testa que cache é isolado entre diferentes tipos."""
        with patch.multiple(
            'src.infrastructure.factories.infrastructure_factory',
            YTDLPDownloader=Mock(return_value=Mock()),
            WhisperProvider=Mock(return_value=Mock()),
            GroqProvider=Mock(return_value=Mock())
        ):
            downloader = factory.create_video_downloader()
            whisper = factory.create_ai_provider("whisper")
            groq = factory.create_ai_provider("groq")
            
            # Todos devem ser diferentes
            assert downloader != whisper
            assert whisper != groq
            assert downloader != groq
    
    def test_cache_key_generation(self, factory):
        """Testa geração de chaves de cache."""
        with patch.multiple(
            'src.infrastructure.factories.infrastructure_factory',
            WhisperProvider=Mock(return_value=Mock()),
            GroqProvider=Mock(return_value=Mock())
        ):
            whisper1 = factory.create_ai_provider("whisper")
            whisper2 = factory.create_ai_provider("whisper")
            groq = factory.create_ai_provider("groq")
            
            # Mesmo tipo deve retornar mesma instância
            assert whisper1 == whisper2
            # Tipos diferentes devem retornar instâncias diferentes
            assert whisper1 != groq
    
    def test_cache_persistence(self, factory):
        """Testa persistência do cache entre chamadas."""
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # Primeira chamada
            result1 = factory.create_video_downloader()
            
            # Segunda chamada
            result2 = factory.create_video_downloader()
            
            # Terceira chamada
            result3 = factory.create_video_downloader()
            
            # Todas devem retornar a mesma instância
            assert result1 == result2 == result3
            # Classe deve ter sido instanciada apenas uma vez
            mock_class.assert_called_once()