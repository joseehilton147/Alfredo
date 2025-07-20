"""
Utilitários para tratamento padronizado de erros na camada de apresentação.

Fornece funções e classes para exibir erros de forma amigável ao usuário,
mantendo detalhes técnicos nos logs.
"""

import logging
from typing import Optional, Dict, Any

from src.domain.exceptions.alfredo_errors import (
    AlfredoError,
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
    ProviderUnavailableError
)


class ErrorDisplayFormatter:
    """
    Formatador para exibição amigável de erros.
    
    Converte exceções técnicas em mensagens compreensíveis para o usuário,
    mantendo informações técnicas nos logs.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa o formatador.
        
        Args:
            logger: Logger para registrar detalhes técnicos (opcional)
        """
        self.logger = logger or logging.getLogger(__name__)

    def format_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        Formata erro para exibição amigável.
        
        Args:
            error: Exceção a ser formatada
            context: Contexto adicional sobre o erro
            
        Returns:
            Mensagem formatada para o usuário
        """
        context = context or {}
        
        # Log detalhes técnicos
        self.logger.error(
            f"Erro capturado: {type(error).__name__}: {str(error)}",
            extra=context,
            exc_info=True
        )

        # Formatar mensagem amigável baseada no tipo de erro
        if isinstance(error, DownloadFailedError):
            return self._format_download_error(error)
        elif isinstance(error, TranscriptionError):
            return self._format_transcription_error(error)
        elif isinstance(error, InvalidVideoFormatError):
            return self._format_validation_error(error)
        elif isinstance(error, ConfigurationError):
            return self._format_configuration_error(error)
        elif isinstance(error, ProviderUnavailableError):
            return self._format_provider_error(error)
        elif isinstance(error, AlfredoError):
            return self._format_alfredo_error(error)
        else:
            return self._format_generic_error(error)

    def _format_download_error(self, error: DownloadFailedError) -> str:
        """Formata erro de download."""
        message = f"❌ Falha no download: {error.message}"
        
        if hasattr(error, 'url'):
            message += f"\n   🔗 URL: {error.url}"
        
        if hasattr(error, 'http_code') and error.http_code:
            message += f"\n   📡 Código HTTP: {error.http_code}"
            
            # Adicionar explicação para códigos comuns
            if error.http_code == 404:
                message += " (Vídeo não encontrado)"
            elif error.http_code == 403:
                message += " (Acesso negado)"
            elif error.http_code >= 500:
                message += " (Erro do servidor)"
        
        if hasattr(error, 'reason'):
            message += f"\n   💬 Motivo: {error.reason}"
        
        message += "\n\n💡 Dicas:"
        message += "\n   • Verifique se a URL está correta"
        message += "\n   • Tente novamente em alguns minutos"
        message += "\n   • Verifique sua conexão com a internet"
        
        return message

    def _format_transcription_error(self, error: TranscriptionError) -> str:
        """Formata erro de transcrição."""
        message = f"❌ Falha na transcrição: {error.message}"
        
        if hasattr(error, 'audio_path'):
            from pathlib import Path
            audio_file = Path(error.audio_path).name
            message += f"\n   🎵 Arquivo: {audio_file}"
        
        if hasattr(error, 'provider'):
            message += f"\n   🤖 Provedor: {error.provider}"
        
        message += "\n\n💡 Dicas:"
        message += "\n   • Verifique se o arquivo de áudio não está corrompido"
        message += "\n   • Tente com um arquivo menor"
        message += "\n   • Verifique se há espaço em disco suficiente"
        
        return message

    def _format_validation_error(self, error: InvalidVideoFormatError) -> str:
        """Formata erro de validação."""
        message = f"❌ Formato inválido: {error.message}"
        
        if hasattr(error, 'field'):
            message += f"\n   📋 Campo: {error.field}"
        
        if hasattr(error, 'value'):
            message += f"\n   📄 Valor: {error.value}"
        
        if hasattr(error, 'constraint'):
            message += f"\n   ⚠️  Restrição: {error.constraint}"
        
        message += "\n\n💡 Dicas:"
        message += "\n   • Verifique se o arquivo existe e não está corrompido"
        message += "\n   • Confirme se o formato é suportado"
        message += "\n   • Verifique as permissões do arquivo"
        
        return message

    def _format_configuration_error(self, error: ConfigurationError) -> str:
        """Formata erro de configuração."""
        message = f"❌ Erro de configuração: {error.message}"
        
        if hasattr(error, 'config_key'):
            message += f"\n   🔧 Configuração: {error.config_key}"
        
        if hasattr(error, 'expected') and error.expected:
            message += f"\n   ✅ Esperado: {error.expected}"
        
        message += "\n\n💡 Dicas:"
        message += "\n   • Verifique as variáveis de ambiente"
        message += "\n   • Confirme se todas as dependências estão instaladas"
        message += "\n   • Verifique as permissões de diretórios"
        
        return message

    def _format_provider_error(self, error: ProviderUnavailableError) -> str:
        """Formata erro de provedor."""
        message = f"❌ Provedor indisponível: {error.message}"
        
        if hasattr(error, 'provider_name'):
            message += f"\n   🤖 Provedor: {error.provider_name}"
        
        if hasattr(error, 'reason'):
            message += f"\n   💬 Motivo: {error.reason}"
        
        message += "\n\n💡 Dicas:"
        message += "\n   • Verifique sua conexão com a internet"
        message += "\n   • Confirme se as API keys estão configuradas"
        message += "\n   • Tente novamente em alguns minutos"
        
        return message

    def _format_alfredo_error(self, error: AlfredoError) -> str:
        """Formata erro genérico do Alfredo."""
        message = f"❌ Erro do Alfredo: {error.message}"
        
        if hasattr(error, 'details') and error.details:
            # Exibir apenas detalhes relevantes para o usuário
            user_details = {k: v for k, v in error.details.items() 
                          if k in ['file_path', 'url', 'language', 'provider']}
            
            if user_details:
                message += "\n   📋 Detalhes:"
                for key, value in user_details.items():
                    message += f"\n     • {key}: {value}"
        
        return message

    def _format_generic_error(self, error: Exception) -> str:
        """Formata erro genérico."""
        message = f"❌ Erro inesperado: {type(error).__name__}"
        
        # Não exibir stack trace completo, apenas mensagem
        error_msg = str(error)
        if error_msg and len(error_msg) < 200:  # Evitar mensagens muito longas
            message += f"\n   💬 {error_msg}"
        
        message += "\n\n💡 Dicas:"
        message += "\n   • Tente executar novamente"
        message += "\n   • Verifique os logs para mais detalhes"
        message += "\n   • Use --verbose para mais informações"
        
        return message

    def display_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """
        Exibe erro formatado no console.
        
        Args:
            error: Exceção a ser exibida
            context: Contexto adicional sobre o erro
        """
        formatted_message = self.format_error(error, context)
        print(formatted_message)

    def display_warning(self, message: str, details: Dict[str, Any] = None) -> None:
        """
        Exibe aviso formatado no console.
        
        Args:
            message: Mensagem de aviso
            details: Detalhes adicionais (opcional)
        """
        warning_msg = f"⚠️  {message}"
        
        if details:
            warning_msg += "\n   📋 Detalhes:"
            for key, value in details.items():
                warning_msg += f"\n     • {key}: {value}"
        
        print(warning_msg)

    def display_success(self, message: str, details: Dict[str, Any] = None) -> None:
        """
        Exibe mensagem de sucesso formatada.
        
        Args:
            message: Mensagem de sucesso
            details: Detalhes adicionais (opcional)
        """
        success_msg = f"✅ {message}"
        
        if details:
            success_msg += "\n   📋 Detalhes:"
            for key, value in details.items():
                success_msg += f"\n     • {key}: {value}"
        
        print(success_msg)