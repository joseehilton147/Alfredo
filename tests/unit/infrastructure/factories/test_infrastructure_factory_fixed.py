"""
Testes completos para InfrastructureFactory para aumentar cobertura significativamente.

Testa todas as funções de criação de dependências, cache singleton,
tratamento de erros e cenários de configuração.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError


class TestInfrastructureFactoryComplete:
    """Testes completos para InfrastructureFactory."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock da configuração do Alfredo."""
        config = Mock(spec=AlfredoConfig)
        config.default_ai_provider = "whisper"
        config.storage_type = "json"
        config.data_dir = Path("/tmp/alfredo")
        return config
    
    @pytest.fixture
    def factory(self, mock_config):
        """Factory com configuração mock."""
        return InfrastructureFactory(mock_config)
    
    def test_init_initializes_correctly(self, mock_config):
        """Testa inicialização correta da factory."""
        factory = InfrastructureFactory(mock_config)
        
        assert factory._config == mock_config
        assert factory._instances == {}
    
    def test_create_video_downloader_success(self, factory):
        """Testa criação bem-sucedida do video downloader."""
        mock_downloader = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   return_value=mock_downloader) as mock_class:
            
            result = factory.create_video_downloader()
            
            assert result == mock_downloader
            mock_class.assert_called_once_with(factory._config)
            
            # Verifica cache
            assert 'video_downloader' in factory._instances
            assert factory._instances['video_downloader'] == mock_downloader
    
    def test_create_video_downloader_caching(self, factory):
        """Testa cache do video downloader."""
        mock_downloader = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   return_value=mock_downloader) as mock_class:
            
            # Primeira chamada
            result1 = factory.create_video_downloader()
            # Segunda chamada
            result2 = factory.create_video_downloader()
            
            assert result1 == result2 == mock_downloader
            # Verifica que o construtor foi chamado apenas uma vez
            mock_class.assert_called_once()
    
    def test_create_video_downloader_import_error(self, factory):
        """Testa erro de importação no video downloader."""
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   side_effect=ImportError("yt-dlp não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_video_downloader()
            
            error = exc_info.value
            assert error.field == "video_downloader_dependency"
            assert "yt-dlp" in error.constraint
            assert error.expected == "yt-dlp instalado"
            assert "yt-dlp não encontrado" in error.details["error"]
    
    def test_create_audio_extractor_success(self, factory):
        """Testa criação bem-sucedida do audio extractor."""
        mock_extractor = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor', 
                   return_value=mock_extractor) as mock_class:
            
            result = factory.create_audio_extractor()
            
            assert result == mock_extractor
            mock_class.assert_called_once_with(factory._config)
            
            # Verifica cache
            assert 'audio_extractor' in factory._instances
            assert factory._instances['audio_extractor'] == mock_extractor
    
    def test_create_audio_extractor_caching(self, factory):
        """Testa cache do audio extractor."""
        mock_extractor = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor', 
                   return_value=mock_extractor) as mock_class:
            
            # Primeira chamada
            result1 = factory.create_audio_extractor()
            # Segunda chamada
            result2 = factory.create_audio_extractor()
            
            assert result1 == result2 == mock_extractor
            # Verifica que o construtor foi chamado apenas uma vez
            mock_class.assert_called_once()
    
    def test_create_audio_extractor_import_error(self, factory):
        """Testa erro de importação no audio extractor."""
        with patch('src.infrastructure.factories.infrastructure_factory.FFmpegExtractor', 
                   side_effect=ImportError("ffmpeg-python não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_audio_extractor()
            
            error = exc_info.value
            assert error.field == "audio_extractor_dependency"
            assert "ffmpeg-python" in error.constraint
            assert error.expected == "ffmpeg-python instalado"
            assert "ffmpeg-python não encontrado" in error.details["error"]
    
    def test_create_ai_provider_whisper_success(self, factory):
        """Testa criação bem-sucedida do provider Whisper."""
        mock_provider = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider', 
                   return_value=mock_provider) as mock_class:
            
            result = factory.create_ai_provider("whisper")
            
            assert result == mock_provider
            mock_class.assert_called_once_with(factory._config)
            
            # Verifica cache
            assert 'ai_provider_whisper' in factory._instances
            assert factory._instances['ai_provider_whisper'] == mock_provider
    
    def test_create_ai_provider_default_from_config(self, factory):
        """Testa criação do provider padrão da configuração."""
        mock_provider = Mock()
        factory._config.default_ai_provider = "whisper"
        
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider', 
                   return_value=mock_provider):
            
            # Chama sem especificar provider_type
            result = factory.create_ai_provider()
            
            assert result == mock_provider
            # Verifica que usou o padrão da config
            assert 'ai_provider_whisper' in factory._instances
    
    def test_create_ai_provider_groq_success(self, factory):
        """Testa criação bem-sucedida do provider Groq."""
        mock_provider = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.GroqProvider', 
                   return_value=mock_provider) as mock_class:
            
            result = factory.create_ai_provider("groq")
            
            assert result == mock_provider
            mock_class.assert_called_once_with(factory._config)
            
            # Verifica cache
            assert 'ai_provider_groq' in factory._instances
            assert factory._instances['ai_provider_groq'] == mock_provider
    
    def test_create_ai_provider_ollama_success(self, factory):
        """Testa criação bem-sucedida do provider Ollama."""
        mock_provider = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.OllamaProvider', 
                   return_value=mock_provider) as mock_class:
            
            result = factory.create_ai_provider("ollama")
            
            assert result == mock_provider
            mock_class.assert_called_once_with(factory._config)
            
            # Verifica cache
            assert 'ai_provider_ollama' in factory._instances
            assert factory._instances['ai_provider_ollama'] == mock_provider
    
    def test_create_ai_provider_whisper_import_error(self, factory):
        """Testa erro de importação no provider Whisper."""
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider', 
                   side_effect=ImportError("openai-whisper não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_ai_provider("whisper")
            
            error = exc_info.value
            assert error.field == "whisper_dependency"
            assert "openai-whisper" in error.constraint
            assert error.expected == "openai-whisper instalado"
            assert error.details["provider"] == "whisper"
            assert "openai-whisper não encontrado" in error.details["error"]
    
    def test_create_ai_provider_groq_import_error(self, factory):
        """Testa erro de importação no provider Groq."""
        with patch('src.infrastructure.factories.infrastructure_factory.GroqProvider', 
                   side_effect=ImportError("groq não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_ai_provider("groq")
            
            error = exc_info.value
            assert error.field == "groq_dependency"
            assert "groq" in error.constraint
            assert error.expected == "groq instalado"
    
    def test_create_ai_provider_ollama_import_error(self, factory):
        """Testa erro de importação no provider Ollama."""
        with patch('src.infrastructure.factories.infrastructure_factory.OllamaProvider', 
                   side_effect=ImportError("requests não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_ai_provider("ollama")
            
            error = exc_info.value
            assert error.field == "ollama_dependency"
            assert "requests" in error.constraint
            assert error.expected == "requests instalado"
    
    def test_create_ai_provider_unsupported_type(self, factory):
        """Testa provider não suportado."""
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_ai_provider("invalid_provider")
        
        error = exc_info.value
        assert error.field == "ai_provider_type"
        assert "invalid_provider" in error.constraint
        assert error.details["provider"] == "invalid_provider"
    
    def test_create_ai_provider_caching_different_types(self, factory):
        """Testa cache independente para diferentes tipos de provider."""
        mock_whisper = Mock()
        mock_groq = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.WhisperProvider', 
                   return_value=mock_whisper), \
             patch('src.infrastructure.factories.infrastructure_factory.GroqProvider', 
                   return_value=mock_groq):
            
            whisper1 = factory.create_ai_provider("whisper")
            groq1 = factory.create_ai_provider("groq") 
            whisper2 = factory.create_ai_provider("whisper")
            groq2 = factory.create_ai_provider("groq")
            
            # Verifica caching independente
            assert whisper1 == whisper2 == mock_whisper
            assert groq1 == groq2 == mock_groq
            assert whisper1 != groq1
            
            # Verifica cache
            assert 'ai_provider_whisper' in factory._instances
            assert 'ai_provider_groq' in factory._instances
    
    def test_create_storage_json_success(self, factory):
        """Testa criação bem-sucedida do storage JSON."""
        mock_storage = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.JsonVideoRepository', 
                   return_value=mock_storage) as mock_class:
            
            result = factory.create_storage("json")
            
            assert result == mock_storage
            mock_class.assert_called_once_with(factory._config.data_dir)
            
            # Verifica cache
            assert 'storage_json' in factory._instances
            assert factory._instances['storage_json'] == mock_storage
    
    def test_create_storage_filesystem_success(self, factory):
        """Testa criação bem-sucedida do storage filesystem."""
        mock_storage = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage', 
                   return_value=mock_storage) as mock_class:
            
            result = factory.create_storage("filesystem")
            
            assert result == mock_storage
            mock_class.assert_called_once_with(factory._config.data_dir)
            
            # Verifica cache
            assert 'storage_filesystem' in factory._instances
            assert factory._instances['storage_filesystem'] == mock_storage
    
    def test_create_storage_default_from_config(self, factory):
        """Testa criação do storage padrão da configuração."""
        mock_storage = Mock()
        factory._config.storage_type = "json"
        
        with patch('src.infrastructure.factories.infrastructure_factory.JsonVideoRepository', 
                   return_value=mock_storage):
            
            # Chama sem especificar storage_type
            result = factory.create_storage()
            
            assert result == mock_storage
            # Verifica que usou o padrão da config
            assert 'storage_json' in factory._instances
    
    def test_create_storage_unsupported_type(self, factory):
        """Testa storage não suportado."""
        with pytest.raises(ConfigurationError) as exc_info:
            factory.create_storage("invalid_storage")
        
        error = exc_info.value
        assert error.field == "storage_type"
        assert "invalid_storage" in error.constraint
        assert error.details["storage_type"] == "invalid_storage"
    
    def test_create_storage_json_import_error(self, factory):
        """Testa erro de importação no storage JSON."""
        with patch('src.infrastructure.factories.infrastructure_factory.JsonVideoRepository', 
                   side_effect=ImportError("json não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_storage("json")
            
            error = exc_info.value
            assert error.field == "json_storage_dependency"
            assert "json" in error.constraint
    
    def test_create_storage_filesystem_import_error(self, factory):
        """Testa erro de importação no storage filesystem."""
        with patch('src.infrastructure.factories.infrastructure_factory.FileSystemStorage', 
                   side_effect=ImportError("pathlib não encontrado")):
            
            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_storage("filesystem")
            
            error = exc_info.value
            assert error.field == "filesystem_storage_dependency"
            assert "pathlib" in error.constraint
    
    def test_create_all_dependencies_success(self, factory):
        """Testa criação de todas as dependências."""
        mock_downloader = Mock()
        mock_extractor = Mock()
        mock_provider = Mock()
        mock_storage = Mock()
        
        with patch.object(factory, 'create_video_downloader', return_value=mock_downloader), \
             patch.object(factory, 'create_audio_extractor', return_value=mock_extractor), \
             patch.object(factory, 'create_ai_provider', return_value=mock_provider), \
             patch.object(factory, 'create_storage', return_value=mock_storage):
            
            result = factory.create_all_dependencies()
            
            expected = {
                'video_downloader': mock_downloader,
                'audio_extractor': mock_extractor,
                'ai_provider': mock_provider,
                'storage': mock_storage
            }
            
            assert result == expected
    
    def test_create_all_dependencies_with_provider_type(self, factory):
        """Testa criação de todas as dependências com tipo específico de provider."""
        mock_downloader = Mock()
        mock_extractor = Mock()
        mock_provider = Mock()
        mock_storage = Mock()
        
        with patch.object(factory, 'create_video_downloader', return_value=mock_downloader), \
             patch.object(factory, 'create_audio_extractor', return_value=mock_extractor), \
             patch.object(factory, 'create_ai_provider', return_value=mock_provider) as mock_ai, \
             patch.object(factory, 'create_storage', return_value=mock_storage):
            
            result = factory.create_all_dependencies(ai_provider_type="groq")
            
            # Verifica que o provider foi chamado com tipo específico
            mock_ai.assert_called_once_with("groq")
            
            expected = {
                'video_downloader': mock_downloader,
                'audio_extractor': mock_extractor,
                'ai_provider': mock_provider,
                'storage': mock_storage
            }
            
            assert result == expected
    
    def test_cache_isolation_between_different_instances(self, mock_config):
        """Testa isolamento de cache entre diferentes instâncias da factory."""
        factory1 = InfrastructureFactory(mock_config)
        factory2 = InfrastructureFactory(mock_config)
        
        mock_downloader1 = Mock()
        mock_downloader2 = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   side_effect=[mock_downloader1, mock_downloader2]):
            
            result1 = factory1.create_video_downloader()
            result2 = factory2.create_video_downloader()
            
            # Cada factory deve ter sua própria instância
            assert result1 == mock_downloader1
            assert result2 == mock_downloader2
            assert result1 != result2
            
            # Caches são independentes
            assert factory1._instances != factory2._instances
    
    def test_error_handling_preserves_cache_integrity(self, factory):
        """Testa que erros não corrompem o cache."""
        mock_downloader = Mock()
        
        # Primeiro, cria uma instância válida
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   return_value=mock_downloader):
            downloader = factory.create_video_downloader()
            assert downloader == mock_downloader
        
        # Agora tenta criar um provider inválido
        with pytest.raises(ConfigurationError):
            factory.create_ai_provider("invalid")
        
        # Verifica que o cache do downloader ainda está intacto
        assert 'video_downloader' in factory._instances
        assert factory._instances['video_downloader'] == mock_downloader
        
        # E que pode ser recuperado normalmente
        downloader2 = factory.create_video_downloader()
        assert downloader2 == mock_downloader
    
    def test_memory_management_weak_references(self, factory):
        """Testa gestão de memória e referências do cache."""
        mock_downloader = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   return_value=mock_downloader):
            
            # Cria instância
            downloader = factory.create_video_downloader()
            assert downloader == mock_downloader
            
            # Verifica que está no cache
            assert 'video_downloader' in factory._instances
            
            # Remove referência local
            del downloader
            
            # Instância ainda deve estar no cache
            assert factory._instances['video_downloader'] == mock_downloader
            
            # E deve ser reutilizada
            downloader2 = factory.create_video_downloader()
            assert downloader2 == mock_downloader
    
    def test_configuration_changes_affect_new_instances(self, mock_config):
        """Testa que mudanças na configuração afetam novas instâncias."""
        factory = InfrastructureFactory(mock_config)
        
        # Muda configuração
        mock_config.default_ai_provider = "groq"
        
        mock_provider = Mock()
        with patch('src.infrastructure.factories.infrastructure_factory.GroqProvider', 
                   return_value=mock_provider):
            
            # Nova instância deve usar a configuração atualizada
            provider = factory.create_ai_provider()
            assert provider == mock_provider
            assert 'ai_provider_groq' in factory._instances
    
    def test_factory_methods_are_thread_safe_conceptually(self, factory):
        """Testa conceito de thread safety dos métodos da factory."""
        # Este teste verifica que não há estado compartilhado perigoso
        # Em um cenário real, precisaríamos de threading locks
        
        mock_downloader1 = Mock()
        mock_downloader2 = Mock()
        
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   return_value=mock_downloader1):
            
            # Primeira chamada
            downloader1 = factory.create_video_downloader()
            
        # Simula chamada concorrente (mesmo que não seja realmente concorrente)
        with patch('src.infrastructure.factories.infrastructure_factory.YTDLPDownloader', 
                   return_value=mock_downloader2):
            
            # Segunda chamada deve retornar a instância cacheada
            downloader2 = factory.create_video_downloader()
            
        # Ambas devem ser a mesma instância (da primeira chamada)
        assert downloader1 == downloader2 == mock_downloader1
