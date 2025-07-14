"""
Core interfaces for Alfredo AI system.
This module provides Protocol-based interfaces for dependency injection
and architectural decoupling.
"""

from typing import Protocol, runtime_checkable, Dict, List, Any, Optional
from abc import abstractmethod


@runtime_checkable
class ICoreOperations(Protocol):
    """Interface para operações centrais do sistema.
    
    Esta interface define o contrato para o sistema core do Alfredo,
    permitindo injeção de dependência e desacoplamento arquitetural.
    """
    
    @abstractmethod
    def handle_error(self, error: Exception) -> None:
        """Trata exceções de acordo com políticas definidas.
        
        Args:
            error: Exceção a ser tratada
        """
        ...
    
    @abstractmethod
    def get_provider(self, provider_name: str) -> 'AIProvider':
        """Obtém instância de provedor de IA configurado.
        
        Args:
            provider_name: Nome do provedor ('groq', 'ollama', etc.)
            
        Returns:
            Instância do provedor de IA
            
        Raises:
            ProviderNotFoundError: Se o provedor não estiver registrado
        """
        ...
    
    @abstractmethod
    def list_commands(self) -> Dict[str, Dict[str, str]]:
        """Lista todos os comandos disponíveis.
        
        Returns:
            Dicionário com comandos e suas informações
        """
        ...
    
    @abstractmethod
    def execute_command(self, command: str, args: List[str]) -> Any:
        """Executa um comando com argumentos fornecidos.
        
        Args:
            command: Nome do comando
            args: Lista de argumentos
            
        Returns:
            Resultado da execução do comando
        """
        ...


@runtime_checkable
class ICLIHandler(Protocol):
    """Interface para manipulação da CLI.
    
    Define o contrato para processamento de argumentos de linha de comando
    e execução de comandos através da interface CLI.
    """
    
    @abstractmethod
    def parse_arguments(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analisa argumentos da linha de comando.
        
        Args:
            args: Lista de argumentos (opcional, usa sys.argv se None)
            
        Returns:
            Dicionário com argumentos parseados
        """
        ...
    
    @abstractmethod
    def execute_command(self, command: str, args: List[str] = None) -> Any:
        """Executa comando via CLI.
        
        Args:
            command: Nome do comando
            args: Argumentos do comando
            
        Returns:
            Resultado da execução
        """
        ...
    
    @abstractmethod
    def show_help(self) -> None:
        """Exibe ajuda da CLI."""
        ...


@runtime_checkable
class IProviderFactory(Protocol):
    """Interface para factory de provedores de IA."""
    
    @abstractmethod
    def register(self, name: str, provider_class: type) -> None:
        """Registra um provedor no factory.
        
        Args:
            name: Nome do provedor
            provider_class: Classe do provedor
        """
        ...
    
    @abstractmethod
    def create(self, name: str) -> 'AIProvider':
        """Cria instância de um provedor.
        
        Args:
            name: Nome do provedor
            
        Returns:
            Instância do provedor
            
        Raises:
            ValueError: Se o provedor não estiver registrado
        """
        ...
    
    @abstractmethod
    def list_providers(self) -> List[str]:
        """Lista provedores registrados.
        
        Returns:
            Lista com nomes dos provedores
        """
        ...


@runtime_checkable
class IAIProvider(Protocol):
    """Interface para provedores de IA.
    
    Define o contrato que todos os provedores de IA devem implementar.
    """
    
    @abstractmethod
    async def transcribe(self, audio_path: str) -> str:
        """Transcreve áudio para texto.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Texto transcrito
        """
        ...
    
    @abstractmethod
    async def summarize(self, transcription: str, video_title: str) -> str:
        """Gera resumo a partir da transcrição.
        
        Args:
            transcription: Texto transcrito
            video_title: Título do vídeo
            
        Returns:
            Resumo gerado
        """
        ...


class ProviderNotFoundError(Exception):
    """Exceção lançada quando um provedor não é encontrado."""
    pass


class CommandNotFoundError(Exception):
    """Exceção lançada quando um comando não é encontrado."""
    pass
