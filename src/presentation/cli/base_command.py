"""
Classe base para comandos CLI do Alfredo AI.

Implementa o padrão Command expandido com funcionalidades avançadas:
- Interface padronizada para comandos
- Tratamento de erros estruturado
- Logging configurado
- Injeção de dependências
- Suporte a sub-comandos e flags
- Help automático baseado em metadados
- Validação avançada de argumentos
"""

import logging
import argparse
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass, field

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.exceptions.alfredo_errors import (
    AlfredoError,
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
    ProviderUnavailableError
)
from src.presentation.cli.error_handler import ErrorDisplayFormatter


@dataclass
class CommandMetadata:
    """Metadados de um comando para geração automática de help."""
    name: str
    description: str
    usage: str = ""
    examples: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=list)
    category: str = "general"
    aliases: List[str] = field(default_factory=list)
    flags: Dict[str, str] = field(default_factory=dict)
    sub_commands: Dict[str, str] = field(default_factory=dict)


@dataclass
class CommandFlag:
    """Definição de uma flag de comando."""
    name: str
    short_name: Optional[str] = None
    description: str = ""
    type: type = str
    default: Any = None
    required: bool = False
    choices: Optional[List[str]] = None


class Command(ABC):
    """
    Classe base para todos os comandos CLI.
    
    Implementa o padrão Command expandido com funcionalidades avançadas:
    - Validação de argumentos
    - Tratamento padronizado de erros
    - Logging estruturado
    - Injeção de dependências via factory
    - Suporte a sub-comandos e flags
    - Help automático baseado em metadados
    """

    def __init__(self, config: AlfredoConfig, factory: InfrastructureFactory):
        """
        Inicializa o comando com configuração e factory.
        
        Args:
            config: Configuração do Alfredo AI
            factory: Factory para criação de dependências de infraestrutura
        """
        self.config = config
        self.factory = factory
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configurar logging específico do comando
        self._setup_command_logging()
        
        # Configurar formatador de erros
        self.error_formatter = ErrorDisplayFormatter(self.logger)
        
        # Metadados do comando (deve ser definido pelas subclasses)
        self._metadata: Optional[CommandMetadata] = None
        
        # Parser de argumentos
        self._parser: Optional[argparse.ArgumentParser] = None
        
        # Sub-comandos registrados
        self._sub_commands: Dict[str, 'Command'] = {}
        
        # Flags definidas
        self._flags: List[CommandFlag] = []
        
        # Inicializar metadados e parser
        self._initialize_metadata()
        self._setup_argument_parser()

    def _setup_command_logging(self) -> None:
        """Configura logging específico para o comando."""
        # Adicionar contexto do comando ao logger
        self.logger = logging.LoggerAdapter(
            self.logger, 
            {'command': self.__class__.__name__}
        )

    @abstractmethod
    def _initialize_metadata(self) -> None:
        """Inicializa metadados do comando. Deve ser implementado pelas subclasses."""
        pass

    def _setup_argument_parser(self) -> None:
        """Configura parser de argumentos baseado nos metadados."""
        if not self._metadata:
            return
            
        self._parser = argparse.ArgumentParser(
            prog=self._metadata.name,
            description=self._metadata.description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Adicionar flags definidas
        for flag in self._flags:
            args = [f"--{flag.name}"]
            if flag.short_name:
                args.append(f"-{flag.short_name}")
                
            kwargs = {
                "help": flag.description,
                "type": flag.type,
                "default": flag.default,
                "required": flag.required
            }
            
            if flag.choices:
                kwargs["choices"] = flag.choices
                
            self._parser.add_argument(*args, **kwargs)
        
        # Configurar sub-comandos se existirem
        if self._metadata.sub_commands:
            subparsers = self._parser.add_subparsers(
                dest="sub_command",
                help="Sub-comandos disponíveis"
            )
            
            for sub_cmd, description in self._metadata.sub_commands.items():
                subparsers.add_parser(sub_cmd, help=description)

    def add_flag(self, flag: CommandFlag) -> None:
        """Adiciona uma flag ao comando.
        
        Args:
            flag: Definição da flag a ser adicionada
        """
        self._flags.append(flag)
        # Reconfigurar parser se já foi inicializado
        if self._parser:
            self._setup_argument_parser()

    def add_sub_command(self, name: str, command: 'Command') -> None:
        """Adiciona um sub-comando.
        
        Args:
            name: Nome do sub-comando
            command: Instância do comando
        """
        self._sub_commands[name] = command
        
        # Atualizar metadados
        if self._metadata:
            self._metadata.sub_commands[name] = command.get_metadata().description

    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Faz parse dos argumentos usando o parser configurado.
        
        Args:
            args: Lista de argumentos da linha de comando
            
        Returns:
            Namespace com argumentos parseados
            
        Raises:
            SystemExit: Se argumentos são inválidos
        """
        if not self._parser:
            raise ConfigurationError(
                "argument_parser",
                "Parser de argumentos não foi configurado"
            )
            
        return self._parser.parse_args(args)

    def get_metadata(self) -> CommandMetadata:
        """Retorna metadados do comando.
        
        Returns:
            Metadados do comando
        """
        if not self._metadata:
            raise ConfigurationError(
                "command_metadata",
                "Metadados do comando não foram inicializados"
            )
        return self._metadata

    def get_help_text(self) -> str:
        """Gera texto de ajuda automático baseado nos metadados.
        
        Returns:
            Texto de ajuda formatado
        """
        if not self._metadata:
            return "Ajuda não disponível"
            
        help_text = f"\n{self._metadata.name.upper()}\n"
        help_text += "=" * 50 + "\n"
        help_text += f"{self._metadata.description}\n\n"
        
        if self._metadata.usage:
            help_text += f"Uso: {self._metadata.usage}\n\n"
        
        if self._flags:
            help_text += "Flags disponíveis:\n"
            for flag in self._flags:
                flag_names = f"--{flag.name}"
                if flag.short_name:
                    flag_names += f", -{flag.short_name}"
                help_text += f"  {flag_names:<20} {flag.description}\n"
            help_text += "\n"
        
        if self._metadata.sub_commands:
            help_text += "Sub-comandos:\n"
            for name, desc in self._metadata.sub_commands.items():
                help_text += f"  {name:<15} {desc}\n"
            help_text += "\n"
        
        if self._metadata.examples:
            help_text += "Exemplos:\n"
            for example in self._metadata.examples:
                help_text += f"  {example}\n"
            help_text += "\n"
        
        if self._metadata.supported_formats:
            help_text += f"Formatos suportados: {', '.join(self._metadata.supported_formats)}\n"
        
        return help_text

    async def execute_with_args(self, args: List[str]) -> Any:
        """Executa comando com argumentos da linha de comando.
        
        Args:
            args: Argumentos da linha de comando
            
        Returns:
            Resultado da execução
        """
        try:
            parsed_args = self.parse_arguments(args)
            
            # Verificar se é um sub-comando
            if hasattr(parsed_args, 'sub_command') and parsed_args.sub_command:
                if parsed_args.sub_command in self._sub_commands:
                    sub_command = self._sub_commands[parsed_args.sub_command]
                    # Remover o nome do sub-comando dos argumentos
                    remaining_args = [arg for arg in args if arg != parsed_args.sub_command]
                    return await sub_command.execute_with_args(remaining_args)
                else:
                    raise ConfigurationError(
                        "sub_command",
                        f"Sub-comando '{parsed_args.sub_command}' não encontrado"
                    )
            
            # Validar argumentos
            if not self.validate_parsed_args(parsed_args):
                return None
            
            # Executar comando principal
            return await self.execute_from_parsed_args(parsed_args)
            
        except SystemExit:
            # argparse chamou sys.exit() (help ou erro)
            return None
        except Exception as e:
            self.handle_error(e)
            return None

    @abstractmethod
    async def execute_from_parsed_args(self, args: argparse.Namespace) -> Any:
        """Executa comando com argumentos parseados.
        
        Args:
            args: Argumentos parseados pelo argparse
            
        Returns:
            Resultado da execução
        """
        pass

    def validate_parsed_args(self, args: argparse.Namespace) -> bool:
        """Valida argumentos parseados.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se válidos, False caso contrário
        """
        # Implementação padrão - pode ser sobrescrita
        return True

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Executa o comando principal.
        
        Args:
            *args: Argumentos posicionais específicos do comando
            **kwargs: Argumentos nomeados específicos do comando
            
        Returns:
            Resultado da execução do comando
            
        Raises:
            AlfredoError: Para erros específicos do domínio
        """
        pass

    @abstractmethod
    def validate_args(self, *args, **kwargs) -> bool:
        """
        Valida argumentos antes da execução.
        
        Args:
            *args: Argumentos posicionais a validar
            **kwargs: Argumentos nomeados a validar
            
        Returns:
            True se argumentos são válidos, False caso contrário
        """
        pass

    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """
        Trata erros de forma padronizada com mensagens amigáveis.
        
        Args:
            error: Exceção a ser tratada
            context: Contexto adicional sobre o erro
        """
        self.error_formatter.display_error(error, context)

    def log_execution_start(self, operation: str, **context) -> None:
        """
        Registra início da execução com contexto.
        
        Args:
            operation: Nome da operação sendo executada
            **context: Contexto adicional para logging
        """
        import time, psutil
        context = dict(context)
        context["start_time"] = time.time()
        context["mem_usage_mb"] = psutil.Process().memory_info().rss // 1024 // 1024
        self.logger.info(f"🚀 Iniciando {operation}", extra=context)

    def log_execution_success(self, operation: str, **context) -> None:
        """
        Registra sucesso da execução com contexto.
        
        Args:
            operation: Nome da operação executada
            **context: Contexto adicional para logging
        """
        import time, psutil
        context = dict(context)
        context["end_time"] = time.time()
        context["mem_usage_mb"] = psutil.Process().memory_info().rss // 1024 // 1024
        if "start_time" in context:
            context["duration_sec"] = round(context["end_time"] - context["start_time"], 2)
        self.logger.info(f"✅ {operation} concluído com sucesso", extra=context)

    def log_execution_error(self, operation: str, error: Exception, **context) -> None:
        """
        Registra erro na execução com contexto.
        
        Args:
            operation: Nome da operação que falhou
            error: Exceção que ocorreu
            **context: Contexto adicional para logging
        """
        import time, psutil
        context = dict(context)
        context["end_time"] = time.time()
        context["mem_usage_mb"] = psutil.Process().memory_info().rss // 1024 // 1024
        if "start_time" in context:
            context["duration_sec"] = round(context["end_time"] - context["start_time"], 2)
        self.logger.error(
            f"❌ Erro em {operation}: {str(error)}", 
            extra=context, 
            exc_info=True
        )

    def display_progress(self, message: str, current: int = None, total: int = None) -> None:
        """
        Exibe progresso da operação.
        
        Args:
            message: Mensagem de progresso
            current: Valor atual (opcional)
            total: Valor total (opcional)
        """
        if current is not None and total is not None:
            percentage = (current / total) * 100
            print(f"⏳ {message} ({current}/{total} - {percentage:.1f}%)")
        else:
            print(f"⏳ {message}")

    def display_result(self, result: Any, operation: str) -> None:
        """
        Exibe resultado da operação de forma padronizada.
        
        Args:
            result: Resultado a ser exibido
            operation: Nome da operação executada
        """
        print(f"✅ {operation} concluído com sucesso")
        
        # Exibir informações específicas baseadas no tipo do resultado
        if hasattr(result, 'transcription') and result.transcription:
            char_count = len(result.transcription)
            print(f"📝 Transcrição: {char_count} caracteres")
            
        if hasattr(result, 'summary') and result.summary:
            char_count = len(result.summary)
            print(f"📋 Resumo: {char_count} caracteres")
            
        if hasattr(result, 'file_path'):
            print(f"💾 Salvo em: {result.file_path}")

    def get_command_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o comando para help e documentação.
        
        Returns:
            Dicionário com informações do comando
        """
        if self._metadata:
            return {
                "name": self._metadata.name,
                "description": self._metadata.description,
                "usage": self._metadata.usage,
                "examples": self._metadata.examples,
                "supported_formats": self._metadata.supported_formats,
                "category": self._metadata.category,
                "aliases": self._metadata.aliases,
                "flags": {flag.name: flag.description for flag in self._flags},
                "sub_commands": self._metadata.sub_commands,
                "class": self.__class__.__name__
            }
        else:
            return {
                "name": self.__class__.__name__.replace("Command", "").lower(),
                "description": self.__doc__.split('\n')[0] if self.__doc__ else "Comando CLI",
                "class": self.__class__.__name__
            }