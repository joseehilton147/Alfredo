"""Módulo de provedores de IA com implementação do Strategy Pattern."""

# Imports condicionais para evitar falhas por dependências faltando
_available_providers = []

try:
    from src.infrastructure.providers.whisper_strategy import WhisperStrategy
    _available_providers.append("WhisperStrategy")
except ImportError:
    WhisperStrategy = None

try:
    from src.infrastructure.providers.groq_strategy import GroqStrategy
    _available_providers.append("GroqStrategy")
except ImportError:
    GroqStrategy = None

try:
    from src.infrastructure.providers.ollama_strategy import OllamaStrategy
    _available_providers.append("OllamaStrategy")
except ImportError:
    OllamaStrategy = None

try:
    from src.infrastructure.providers.mock_provider_strategy import MockProviderStrategy
    _available_providers.append("MockProviderStrategy")
except ImportError:
    MockProviderStrategy = None

# Mantém compatibilidade com implementação anterior
try:
    from src.infrastructure.providers.whisper_provider import WhisperProvider
    _available_providers.append("WhisperProvider")
except ImportError:
    WhisperProvider = None

__all__ = _available_providers