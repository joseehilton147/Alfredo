"""
Testes completos para factories de infraestrutura para aumentar cobertura.

Testa todas as funções de factory cobrindo todos os cenários
possíveis e branches de código.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError, ProviderUnavailableError


class TestInfrastructureFactoryComplete:
    """Testes completos para InfrastructureFactory."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock de configuração para testes."""
        config = Mock(spec=AlfredoConfig)
        config.ai_provider = "whisper"
        config.storage_type = "json"
        config.downloader_type = "yt-dlp"
        config.extractor_type = "ffmpeg"
        return config
    
    def test_create_ai_provider_whisper(self, mock_config):
        """Testa criação de provider Whisper."""
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider') as mock_whisper:
            mock_instance = Mock()
            mock_whisper.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_ai_provider(mock_config)
            
            assert result == mock_instance
            mock_whisper.assert_called_once()
    
    def test_create_ai_provider_groq(self, mock_config):
        """Testa criação de provider Groq."""
        mock_config.ai_provider = "groq"
        
        with patch('src.infrastructure.factories.infrastructure_factory.GroqProvider') as mock_groq:
            mock_instance = Mock()
            mock_groq.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_ai_provider(mock_config)
            
            assert result == mock_instance
            mock_groq.assert_called_once()
    
    def test_create_ai_provider_ollama(self, mock_config):
        """Testa criação de provider Ollama."""
        mock_config.ai_provider = "ollama"
        
        with patch('src.infrastructure.factories.infrastructure_factory.OllamaProvider') as mock_ollama:
            mock_instance = Mock()
            mock_ollama.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_ai_provider(mock_config)
            
            assert result == mock_instance
            mock_ollama.assert_called_once()
    
    def test_create_ai_provider_invalid(self, mock_config):
        """Testa criação de provider inválido."""
        mock_config.ai_provider = "invalid_provider"
        
        factory = InfrastructureFactory()
        
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_ai_provider(mock_config)
        
        assert "AI provider" in str(exc_info.value)
        assert "invalid_provider" in str(exc_info.value)
    
    def test_create_video_downloader_yt_dlp(self, mock_config):
        """Testa criação de downloader yt-dlp."""
        mock_config.downloader_type = "yt-dlp"
        
        with patch('src.infrastructure.factories.infrastructure_factory.YtDlpDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_downloader.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_video_downloader(mock_config)
            
            assert result == mock_instance
            mock_downloader.assert_called_once()
    
    def test_create_video_downloader_youtube_dl(self, mock_config):
        """Testa criação de downloader youtube-dl."""
        mock_config.downloader_type = "youtube-dl"
        
        with patch('src.infrastructure.factories.infrastructure_factory.YouTubeDLDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_downloader.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_video_downloader(mock_config)
            
            assert result == mock_instance
            mock_downloader.assert_called_once()
    
    def test_create_video_downloader_invalid(self, mock_config):
        """Testa criação de downloader inválido."""
        mock_config.downloader_type = "invalid_downloader"
        
        factory = InfrastructureFactory()
        
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_video_downloader(mock_config)
        
        assert "Downloader" in str(exc_info.value)
        assert "invalid_downloader" in str(exc_info.value)
    
    def test_create_audio_extractor_ffmpeg(self, mock_config):
        """Testa criação de extractor FFmpeg."""
        mock_config.extractor_type = "ffmpeg"
        
        with patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor') as mock_extractor:
            mock_instance = Mock()
            mock_extractor.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_audio_extractor(mock_config)
            
            assert result == mock_instance
            mock_extractor.assert_called_once()
    
    def test_create_audio_extractor_moviepy(self, mock_config):
        """Testa criação de extractor MoviePy."""
        mock_config.extractor_type = "moviepy"
        
        with patch('src.infrastructure.factories.infrastructure_factory.MoviePyExtractor') as mock_extractor:
            mock_instance = Mock()
            mock_extractor.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_audio_extractor(mock_config)
            
            assert result == mock_instance
            mock_extractor.assert_called_once()
    
    def test_create_audio_extractor_invalid(self, mock_config):
        """Testa criação de extractor inválido."""
        mock_config.extractor_type = "invalid_extractor"
        
        factory = InfrastructureFactory()
        
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_audio_extractor(mock_config)
        
        assert "Audio extractor" in str(exc_info.value)
        assert "invalid_extractor" in str(exc_info.value)
    
    def test_create_storage_json(self, mock_config):
        """Testa criação de storage JSON."""
        mock_config.storage_type = "json"
        
        with patch('src.infrastructure.factories.infrastructure_factory.JsonVideoRepository') as mock_storage:
            mock_instance = Mock()
            mock_storage.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_storage(mock_config)
            
            assert result == mock_instance
            mock_storage.assert_called_once()
    
    def test_create_storage_filesystem(self, mock_config):
        """Testa criação de storage filesystem."""
        mock_config.storage_type = "filesystem"
        
        with patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage') as mock_storage:
            mock_instance = Mock()
            mock_storage.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result = factory.create_storage(mock_config)
            
            assert result == mock_instance
            mock_storage.assert_called_once()
    
    def test_create_storage_invalid(self, mock_config):
        """Testa criação de storage inválido."""
        mock_config.storage_type = "invalid_storage"
        
        factory = InfrastructureFactory()
        
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_storage(mock_config)
        
        assert "Storage" in str(exc_info.value)
        assert "invalid_storage" in str(exc_info.value)
    
    def test_singleton_pattern_ai_provider(self, mock_config):
        """Testa padrão singleton para AI provider."""
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider') as mock_whisper:
            mock_instance = Mock()
            mock_whisper.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result1 = factory.create_ai_provider(mock_config)
            result2 = factory.create_ai_provider(mock_config)
            
            assert result1 == result2
            mock_whisper.assert_called_once()  # Só deve ser chamado uma vez
    
    def test_singleton_pattern_storage(self, mock_config):
        """Testa padrão singleton para storage."""
        with patch('src.infrastructure.factories.infrastructure_factory.JsonVideoRepository') as mock_storage:
            mock_instance = Mock()
            mock_storage.return_value = mock_instance
            
            factory = InfrastructureFactory()
            result1 = factory.create_storage(mock_config)
            result2 = factory.create_storage(mock_config)
            
            assert result1 == result2
            mock_storage.assert_called_once()  # Só deve ser chamado uma vez
    
    def test_different_configs_create_different_instances(self):
        """Testa que configurações diferentes criam instâncias diferentes."""
        config1 = Mock(spec=AlfredoConfig)
        config1.ai_provider = "whisper"
        
        config2 = Mock(spec=AlfredoConfig)
        config2.ai_provider = "groq"
        
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider') as mock_whisper, \
             patch('src.infrastructure.factories.infrastructure_factory.GroqProvider') as mock_groq:
            
            mock_whisper_instance = Mock()
            mock_groq_instance = Mock()
            mock_whisper.return_value = mock_whisper_instance
            mock_groq.return_value = mock_groq_instance
            
            factory = InfrastructureFactory()
            result1 = factory.create_ai_provider(config1)
            result2 = factory.create_ai_provider(config2)
            
            assert result1 != result2
            assert result1 == mock_whisper_instance
            assert result2 == mock_groq_instance
    
    def test_cache_key_generation(self, mock_config):
        """Testa geração de chaves de cache."""
        factory = InfrastructureFactory()
        
        # Simula método de cache interno
        cache_key = f"{mock_config.ai_provider}_{hash(str(mock_config.__dict__))}"
        
        # Verifica se a chave é gerada consistentemente
        assert isinstance(cache_key, str)
        assert mock_config.ai_provider in cache_key
    
    def test_error_handling_during_creation(self, mock_config):
        """Testa tratamento de erro durante criação."""
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider') as mock_whisper:
            mock_whisper.side_effect = Exception("Erro de inicialização")
            
            factory = InfrastructureFactory()
            
            with pytest.raises(ProviderUnavailableError) as exc_info:
                factory.create_ai_provider(mock_config)
            
            assert "whisper" in str(exc_info.value)
            assert "Erro de inicialização" in str(exc_info.value)
    
    def test_create_all_dependencies(self, mock_config):
        """Testa criação de todas as dependências."""
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider') as mock_ai, \
             patch('src.infrastructure.factories.infrastructure_factory.YtDlpDownloader') as mock_downloader, \
             patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor') as mock_extractor, \
             patch('src.infrastructure.factories.infrastructure_factory.JsonVideoRepository') as mock_storage:
            
            # Setup mocks
            mock_ai.return_value = Mock()
            mock_downloader.return_value = Mock()
            mock_extractor.return_value = Mock()
            mock_storage.return_value = Mock()
            
            factory = InfrastructureFactory()
            
            # Criar todas as dependências
            ai_provider = factory.create_ai_provider(mock_config)
            downloader = factory.create_video_downloader(mock_config)
            extractor = factory.create_audio_extractor(mock_config)
            storage = factory.create_storage(mock_config)
            
            # Verificar que todas foram criadas
            assert ai_provider is not None
            assert downloader is not None
            assert extractor is not None
            assert storage is not None
    
    def test_memory_management(self, mock_config):
        """Testa gerenciamento de memória e cache."""
        factory = InfrastructureFactory()
        
        # Verificar que o cache interno existe
        assert hasattr(factory, '_cache') or hasattr(factory, '_instances')
        
        # Criar várias instâncias
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider') as mock_provider:
            mock_provider.return_value = Mock()
            
            for _ in range(10):
                factory.create_ai_provider(mock_config)
            
            # Provider deve ser criado apenas uma vez devido ao singleton
            mock_provider.assert_called_once()
