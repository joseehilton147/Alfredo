"""
Módulo de exceções customizadas do Alfredo AI.

Este módulo contém a hierarquia completa de exceções específicas do domínio,
permitindo tratamento de erros mais preciso e informativo.
"""

from .alfredo_errors import (
    AlfredoError,
    ProviderUnavailableError,
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
)

__all__ = [
    "AlfredoError",
    "ProviderUnavailableError", 
    "DownloadFailedError",
    "TranscriptionError",
    "InvalidVideoFormatError",
    "ConfigurationError",
]