"""
Hierarquia de exceções customizadas do Alfredo AI.

Este módulo define todas as exceções específicas do domínio, permitindo
tratamento de erros mais preciso e informativo em toda a aplicação.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class AlfredoError(Exception):
    """
    Exceção base do Alfredo AI com suporte a detalhes estruturados.
    
    Esta classe serve como base para todas as exceções específicas do domínio,
    fornecendo funcionalidades comuns como armazenamento de detalhes estruturados,
    causa raiz e serialização para logging/debugging.
    
    Attributes:
        message: Mensagem descritiva do erro
        details: Dicionário com detalhes estruturados do erro
        cause: Exceção original que causou este erro (se aplicável)
        timestamp: Momento em que o erro ocorreu
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 cause: Optional[Exception] = None):
        """
        Inicializa uma nova instância de AlfredoError.
        
        Args:
            message: Mensagem descritiva do erro
            details: Dicionário opcional com detalhes estruturados
            cause: Exceção original que causou este erro
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa a exceção para um dicionário estruturado.
        
        Útil para logging, debugging e transmissão de informações de erro
        de forma estruturada.
        
        Returns:
            Dict contendo todas as informações da exceção
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
            "cause_type": self.cause.__class__.__name__ if self.cause else None,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def __str__(self) -> str:
        """Representação string da exceção."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message
    
    def __repr__(self) -> str:
        """Representação técnica da exceção."""
        return (f"{self.__class__.__name__}("
                f"message='{self.message}', "
                f"details={self.details}, "
                f"cause={self.cause})")


class ProviderUnavailableError(AlfredoError):
    """
    Exceção lançada quando um provedor de IA está indisponível ou com falha.
    
    Esta exceção é usada quando não é possível conectar ou usar um provedor
    específico de IA (Whisper, Groq, Ollama, etc.).
    """
    
    def __init__(self, provider_name: str, reason: str, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Inicializa erro de provedor indisponível.
        
        Args:
            provider_name: Nome do provedor que falhou
            reason: Motivo da indisponibilidade
            details: Detalhes adicionais opcionais
        """
        message = f"Provider {provider_name} indisponível: {reason}"
        error_details = {
            "provider_name": provider_name,
            "reason": reason,
            **(details or {})
        }
        super().__init__(message, error_details)
        self.provider_name = provider_name
        self.reason = reason


class DownloadFailedError(AlfredoError):
    """
    Exceção lançada quando falha o download de um vídeo.
    
    Esta exceção é usada quando não é possível baixar um vídeo do YouTube
    ou de outra fonte externa.
    """
    
    def __init__(self, url: str, reason: str, http_code: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Inicializa erro de download.
        
        Args:
            url: URL que falhou no download
            reason: Motivo da falha
            http_code: Código HTTP da resposta (se aplicável)
            details: Detalhes adicionais opcionais
        """
        message = f"Falha no download de {url}: {reason}"
        error_details = {
            "url": url,
            "reason": reason,
            "http_code": http_code,
            **(details or {})
        }
        super().__init__(message, error_details)
        self.url = url
        self.reason = reason
        self.http_code = http_code


class TranscriptionError(AlfredoError):
    """
    Exceção lançada quando ocorre erro na transcrição de áudio.
    
    Esta exceção é usada quando falha o processo de transcrição de áudio
    usando qualquer provedor de IA.
    """
    
    def __init__(self, audio_path: str, reason: str, provider: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Inicializa erro de transcrição.
        
        Args:
            audio_path: Caminho do arquivo de áudio que falhou
            reason: Motivo da falha na transcrição
            provider: Nome do provedor usado (se conhecido)
            details: Detalhes adicionais opcionais
        """
        message = f"Erro na transcrição de {audio_path}: {reason}"
        error_details = {
            "audio_path": audio_path,
            "reason": reason,
            "provider": provider,
            **(details or {})
        }
        super().__init__(message, error_details)
        self.audio_path = audio_path
        self.reason = reason
        self.provider = provider


class InvalidVideoFormatError(AlfredoError):
    """
    Exceção lançada quando um vídeo tem formato inválido ou dados inconsistentes.
    
    Esta exceção é usada durante validação de entidades de domínio quando
    os dados não atendem aos critérios de negócio.
    """
    
    def __init__(self, field: str, value: Any, constraint: str,
                 details: Optional[Dict[str, Any]] = None):
        """
        Inicializa erro de formato inválido.
        
        Args:
            field: Nome do campo que falhou na validação
            value: Valor que causou a falha
            constraint: Descrição da restrição violada
            details: Detalhes adicionais opcionais
        """
        message = f"Campo {field} inválido: {constraint}"
        error_details = {
            "field": field,
            "value": value,
            "constraint": constraint,
            **(details or {})
        }
        super().__init__(message, error_details)
        self.field = field
        self.value = value
        self.constraint = constraint


class ConfigurationError(AlfredoError):
    """
    Exceção lançada quando há erro de configuração do sistema.
    
    Esta exceção é usada quando configurações obrigatórias estão ausentes,
    inválidas ou inconsistentes.
    """
    
    def __init__(self, config_key: str, reason: str, expected: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        Inicializa erro de configuração.
        
        Args:
            config_key: Chave de configuração que causou o erro
            reason: Motivo do erro de configuração
            expected: Valor ou formato esperado (se aplicável)
            details: Detalhes adicionais opcionais
        """
        message = f"Configuração {config_key} inválida: {reason}"
        error_details = {
            "config_key": config_key,
            "reason": reason,
            "expected": expected,
            **(details or {})
        }
        super().__init__(message, error_details)
        self.config_key = config_key
        self.reason = reason
        self.expected = expected