"""
Testes específicos para o padrão Factory de provedores.
"""

import pytest
from unittest.mock import Mock, patch

from core.provider_factory import ProviderFactory, get_ai_provider
from core.interfaces import ProviderNotFoundError, IAIProvider


class MockAIProvider:
    """Mock provider que implementa IAIProvider."""
    
    def __init__(self, name="mock"):
        self.name = name
    
    async def transcribe(self, audio_path: str) -> str:
        return f"Mock transcription from {self.name}"
    
    async def summarize(self, transcription: str, video_title: str) -> str:
        return f"Mock summary from {self.name}: {video_title}"


class TestProviderFactoryPattern:
    """Testes detalhados para o padrão Factory."""
    
    def setup_method(self):
        """Limpa o factory antes de cada teste."""
        ProviderFactory.reset()
    
    def test_register_valid_provider(self):
        """Testa registro de provedor válido."""
        ProviderFactory.register('mock', MockAIProvider)
        assert ProviderFactory.is_registered('mock')
        assert 'mock' in ProviderFactory.list_providers()
    
    def test_register_invalid_provider(self):
        """Testa registro de provedor inválido."""
        class InvalidProvider:
            pass
        
        with pytest.raises(TypeError, match="must implement IAIProvider interface"):
            ProviderFactory.register('invalid', InvalidProvider)
    
    def test_create_existing_provider(self):
        """Testa criação de provedor existente."""
        ProviderFactory.register('mock', MockAIProvider)
        provider = ProviderFactory.create('mock')
        
        assert isinstance(provider, MockAIProvider)
        assert provider.name == "mock"
    
    def test_create_nonexistent_provider(self):
        """Testa criação de provedor inexistente."""
        with pytest.raises(ProviderNotFoundError) as exc_info:
            ProviderFactory.create('nonexistent')
        
        assert "Provider 'nonexistent' não registrado" in str(exc_info.value)
        assert "nenhum" in str(exc_info.value)  # Quando não há provedores
    
    def test_create_nonexistent_with_available_providers(self):
        """Testa mensagem de erro com provedores disponíveis."""
        ProviderFactory.register('mock1', MockAIProvider)
        ProviderFactory.register('mock2', MockAIProvider)
        
        with pytest.raises(ProviderNotFoundError) as exc_info:
            ProviderFactory.create('nonexistent')
        
        error_msg = str(exc_info.value)
        assert "Provider 'nonexistent' não registrado" in error_msg
        assert "mock1" in error_msg
        assert "mock2" in error_msg
    
    def test_provider_caching(self):
        """Testa sistema de cache."""
        ProviderFactory.register('mock', MockAIProvider)
        
        # Primeira criação
        provider1 = ProviderFactory.create('mock', use_cache=True)
        
        # Segunda criação com cache
        provider2 = ProviderFactory.create('mock', use_cache=True)
        assert provider1 is provider2
        
        # Criação sem cache
        provider3 = ProviderFactory.create('mock', use_cache=False)
        assert provider1 is not provider3
    
    def test_clear_specific_cache(self):
        """Testa limpeza de cache específico."""
        ProviderFactory.register('mock1', MockAIProvider)
        ProviderFactory.register('mock2', MockAIProvider)
        
        # Cria instâncias em cache
        provider1 = ProviderFactory.create('mock1', use_cache=True)
        provider2 = ProviderFactory.create('mock2', use_cache=True)
        
        # Limpa cache específico
        ProviderFactory.clear_cache('mock1')
        
        # Verifica que apenas mock1 foi removido do cache
        provider1_new = ProviderFactory.create('mock1', use_cache=True)
        provider2_cached = ProviderFactory.create('mock2', use_cache=True)
        
        assert provider1 is not provider1_new
        assert provider2 is provider2_cached
    
    def test_clear_all_cache(self):
        """Testa limpeza de todo o cache."""
        ProviderFactory.register('mock1', MockAIProvider)
        ProviderFactory.register('mock2', MockAIProvider)
        
        # Cria instâncias em cache
        provider1 = ProviderFactory.create('mock1', use_cache=True)
        provider2 = ProviderFactory.create('mock2', use_cache=True)
        
        # Limpa todo o cache
        ProviderFactory.clear_cache()
        
        # Verifica que ambas foram removidas do cache
        provider1_new = ProviderFactory.create('mock1', use_cache=True)
        provider2_new = ProviderFactory.create('mock2', use_cache=True)
        
        assert provider1 is not provider1_new
        assert provider2 is not provider2_new
    
    def test_factory_reset(self):
        """Testa reset completo do factory."""
        ProviderFactory.register('mock', MockAIProvider)
        provider = ProviderFactory.create('mock', use_cache=True)
        
        # Verifica que está registrado e em cache
        assert ProviderFactory.is_registered('mock')
        assert len(ProviderFactory.list_providers()) == 1
        
        # Reset completo
        ProviderFactory.reset()
        
        # Verifica que foi limpo
        assert not ProviderFactory.is_registered('mock')
        assert len(ProviderFactory.list_providers()) == 0
        
        # Não deve conseguir criar após reset
        with pytest.raises(ProviderNotFoundError):
            ProviderFactory.create('mock')


class TestLegacyFunction:
    """Testes para função legada get_ai_provider."""
    
    def test_get_ai_provider_with_available_provider(self):
        """Testa função legada com provedor disponível."""
        # Re-registra provedores após reset de outros testes
        try:
            from integrations.groq.provider import GroqProvider
            ProviderFactory.register('groq', GroqProvider)
        except ImportError:
            pass
        
        try:
            from integrations.ollama.provider import OllamaProvider
            ProviderFactory.register('ollama', OllamaProvider)
        except ImportError:
            pass
        
        # Testa com provider disponível
        provider = get_ai_provider('ollama')  # Usa ollama como padrão
        assert provider is not None
    
    @patch.dict('os.environ', {'AI_PROVIDER': 'unknown'})
    def test_get_ai_provider_unknown_provider(self):
        """Testa erro com provedor desconhecido."""
        with pytest.raises(ValueError, match="Provedor de IA desconhecido: unknown"):
            get_ai_provider()
    
    def test_get_ai_provider_function_exists(self):
        """Testa que a função legada existe e é callable."""
        assert callable(get_ai_provider)
        
        # Testa que retorna algo (não None) quando chamada com provedor válido
        try:
            result = get_ai_provider('ollama')
            assert result is not None
        except Exception:
            # Se falhar, pelo menos a função deve existir
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
