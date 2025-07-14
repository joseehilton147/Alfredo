"""
Provider Factory for AI providers.
Implements the Factory pattern for creating AI provider instances.
"""

import os
from typing import Dict, Type, List
from dotenv import load_dotenv
from core.interfaces import IProviderFactory, IAIProvider, ProviderNotFoundError


class ProviderFactory(IProviderFactory):
    """Factory para criação de provedores de IA.
    
    Implementa o padrão Factory para gerenciar instâncias de provedores
    de IA de forma centralizada e desacoplada.
    
    Attributes:
        _providers: Registro interno de classes de provedores disponíveis.
        _instances: Cache de instâncias criadas para reutilização.
        
    Example:
        >>> ProviderFactory.register('groq', GroqProvider)
        >>> provider = ProviderFactory.create('groq')
        >>> providers = ProviderFactory.list_providers()
    """
    
    _providers: Dict[str, Type[IAIProvider]] = {}
    _instances: Dict[str, IAIProvider] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[IAIProvider]) -> None:
        """Registra um provedor no factory.
        
        Args:
            name: Nome único do provedor
            provider_class: Classe que implementa IAIProvider
            
        Raises:
            TypeError: Se provider_class não implementa IAIProvider
        """
        if not hasattr(provider_class, 'transcribe') or not hasattr(provider_class, 'summarize'):
            raise TypeError(f"Provider class {provider_class.__name__} must implement IAIProvider interface")
        
        cls._providers[name] = provider_class
        # Limpa cache de instância se existir
        if name in cls._instances:
            del cls._instances[name]
    
    @classmethod
    def create(cls, name: str, use_cache: bool = True) -> IAIProvider:
        """Cria instância de um provedor.
        
        Args:
            name: Nome do provedor registrado
            use_cache: Se deve usar cache de instâncias (padrão: True)
            
        Returns:
            Instância do provedor de IA
            
        Raises:
            ProviderNotFoundError: Se o provedor não estiver registrado
        """
        if name not in cls._providers:
            available = ', '.join(cls._providers.keys()) if cls._providers else 'nenhum'
            raise ProviderNotFoundError(
                f"Provider '{name}' não registrado. Disponíveis: {available}"
            )
        
        # Verifica cache se solicitado
        if use_cache and name in cls._instances:
            return cls._instances[name]
        
        # Cria nova instância
        provider_class = cls._providers[name]
        instance = provider_class()
        
        # Armazena em cache se solicitado
        if use_cache:
            cls._instances[name] = instance
        
        return instance
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """Lista provedores registrados.
        
        Returns:
            Lista com nomes dos provedores registrados
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Verifica se um provedor está registrado.
        
        Args:
            name: Nome do provedor
            
        Returns:
            True se o provedor estiver registrado
        """
        return name in cls._providers
    
    @classmethod
    def clear_cache(cls, name: str = None) -> None:
        """Limpa cache de instâncias.
        
        Args:
            name: Nome específico do provedor (opcional)
                  Se None, limpa todo o cache
        """
        if name is None:
            cls._instances.clear()
        elif name in cls._instances:
            del cls._instances[name]
    
    @classmethod
    def reset(cls) -> None:
        """Reseta completamente o factory (útil para testes)."""
        cls._providers.clear()
        cls._instances.clear()


def safe_print(text, end="\n", flush=False):
    """Função para imprimir texto sem problemas de encoding no Windows"""
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais, mantém apenas ASCII
        import re
        text = re.sub(r'[^\x20-\x7E]+', '', text)
        print(text, end=end, flush=flush)


def get_ai_provider(provider_override: str = None) -> IAIProvider:
    """Legacy function - mantida para compatibilidade retroativa.
    
    Recomenda-se usar ProviderFactory.create() diretamente.
    """
    load_dotenv()
    provider = provider_override or os.getenv('AI_PROVIDER') or 'groq'
    provider = provider.lower()
    
    # Tenta usar o factory primeiro
    try:
        return ProviderFactory.create(provider)
    except ProviderNotFoundError:
        # Fallback para lógica legada - apenas Groq suportado
        if provider == 'groq':
            safe_print('🤖 Usando o provedor de IA: Groq')
            try:
                from integrations.groq.provider import GroqProvider
                return GroqProvider()
            except ImportError:
                from services.groq_provider import GroqProvider
                return GroqProvider()
        else:
            raise ValueError(f'Provedor de IA desconhecido: {provider}. Apenas "groq" é suportado.')


# Auto-registrar provedores conhecidos
def _auto_register_providers():
    """Registra automaticamente provedores conhecidos."""
    try:
        from integrations.groq.provider import GroqProvider
        ProviderFactory.register('groq', GroqProvider)
    except ImportError:
        try:
            from services.groq_provider import GroqProvider
            ProviderFactory.register('groq', GroqProvider)
        except ImportError:
            pass  # Groq provider não disponível


# Executa auto-registro na importação do módulo
_auto_register_providers()
