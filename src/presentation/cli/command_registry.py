"""
Registry de comandos CLI do Alfredo AI.

Centraliza o registro e criação de comandos CLI, facilitando a descoberta
automática e a injeção de dependências. Suporte expandido para:
- Descoberta automática de comandos
- Categorização de comandos
- Aliases de comandos
- Help automático baseado em metadados
"""

from typing import Dict, Type, Any, List, Optional
import logging
import importlib
import inspect
import pkgutil
from pathlib import Path

from src.presentation.cli.base_command import Command, CommandMetadata
from src.presentation.cli.youtube_command import YouTubeCommand
from src.presentation.cli.local_video_command import LocalVideoCommand
from src.presentation.cli.batch_command import BatchCommand
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory


class CommandRegistry:
    """
    Registry expandido para comandos CLI.
    
    Responsabilidades:
    - Registrar comandos disponíveis
    - Descoberta automática de comandos
    - Criar instâncias de comandos com dependências injetadas
    - Fornecer informações sobre comandos disponíveis
    - Suporte a aliases e categorização
    - Help automático baseado em metadados
    """

    def __init__(self, config: AlfredoConfig, factory: InfrastructureFactory, auto_discover: bool = True):
        """
        Inicializa o registry com configuração e factory.
        
        Args:
            config: Configuração do Alfredo AI
            factory: Factory para criação de dependências
            auto_discover: Se deve descobrir comandos automaticamente
        """
        self.config = config
        self.factory = factory
        self.logger = logging.getLogger(__name__)
        
        # Registry de comandos disponíveis
        self._commands: Dict[str, Type[Command]] = {}
        
        # Registry de aliases
        self._aliases: Dict[str, str] = {}
        
        # Registry por categoria
        self._categories: Dict[str, List[str]] = {}
        
        # Registrar comandos básicos
        self._register_default_commands()
        
        # Descoberta automática se habilitada
        if auto_discover:
            self._auto_discover_commands()

    def _register_default_commands(self) -> None:
        """Registra comandos padrão do sistema."""
        default_commands = {
            'youtube': YouTubeCommand,
            'local': LocalVideoCommand,
            'batch': BatchCommand,
        }
        
        for name, command_class in default_commands.items():
            self.register_command(name, command_class)

    def _auto_discover_commands(self) -> None:
        """Descobre automaticamente comandos no diretório de comandos."""
        try:
            commands_path = Path(__file__).parent
            
            # Procurar por arquivos Python que terminam com '_command.py'
            for file_path in commands_path.glob("*_command.py"):
                if file_path.name == "base_command.py":
                    continue
                    
                module_name = file_path.stem
                try:
                    # Importar módulo dinamicamente
                    module = importlib.import_module(f"src.presentation.cli.{module_name}")
                    
                    # Procurar por classes que herdam de Command
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, Command) and 
                            obj != Command and 
                            name.endswith("Command")):
                            
                            command_name = name.replace("Command", "").lower()
                            if command_name not in self._commands:
                                self.register_command(command_name, obj)
                                self.logger.info(f"Comando descoberto automaticamente: {command_name}")
                                
                except Exception as e:
                    self.logger.warning(f"Erro ao descobrir comandos em {module_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro na descoberta automática de comandos: {e}")

    def get_command(self, command_name: str) -> Command:
        """
        Cria instância de comando com dependências injetadas.
        
        Args:
            command_name: Nome do comando a ser criado
            
        Returns:
            Instância do comando configurada
            
        Raises:
            ValueError: Se comando não for encontrado
        """
        # Verificar se é um alias
        actual_name = self._aliases.get(command_name, command_name)
        
        if actual_name not in self._commands:
            available = ', '.join(self._commands.keys())
            aliases = ', '.join(self._aliases.keys()) if self._aliases else "nenhum"
            raise ValueError(
                f"Comando '{command_name}' não encontrado. "
                f"Comandos disponíveis: {available}. "
                f"Aliases disponíveis: {aliases}"
            )

        command_class = self._commands[actual_name]
        return command_class(self.config, self.factory)

    def get_available_commands(self) -> Dict[str, str]:
        """
        Retorna comandos disponíveis com suas descrições.
        
        Returns:
            Dicionário com nome e descrição dos comandos
        """
        commands_info = {}
        
        for name, command_class in self._commands.items():
            # Criar instância temporária para obter informações
            try:
                temp_command = command_class(self.config, self.factory)
                info = temp_command.get_command_info()
                commands_info[name] = info.get('description', 'Comando CLI')
            except Exception as e:
                self.logger.warning(f"Erro ao obter info do comando {name}: {e}")
                commands_info[name] = "Comando CLI"

        return commands_info

    def get_command_help(self, command_name: str = None, category: str = None) -> str:
        """
        Retorna texto de ajuda para comando específico, categoria ou todos.
        
        Args:
            command_name: Nome do comando (opcional)
            category: Categoria de comandos (opcional)
            
        Returns:
            Texto de ajuda formatado
        """
        if command_name:
            # Verificar se é alias
            actual_name = self._aliases.get(command_name, command_name)
            
            if actual_name not in self._commands:
                # Sugerir comandos similares
                similar = self.find_command_by_pattern(command_name)
                error_msg = f"Comando '{command_name}' não encontrado."
                if similar:
                    error_msg += f" Comandos similares: {', '.join(similar)}"
                return error_msg
            
            try:
                command = self.get_command(command_name)
                return command.get_help_text()
                
            except Exception as e:
                return f"Erro ao obter ajuda para '{command_name}': {e}"
        
        elif category:
            # Ajuda por categoria
            commands_in_category = self.get_commands_by_category(category)
            if not commands_in_category:
                available_categories = ', '.join(self.get_all_categories())
                return f"Categoria '{category}' não encontrada. Categorias disponíveis: {available_categories}"
            
            help_text = f"\nCOMANDOS DA CATEGORIA: {category.upper()}\n"
            help_text += "=" * 50 + "\n"
            
            for cmd_name in commands_in_category:
                try:
                    command = self.get_command(cmd_name)
                    info = command.get_command_info()
                    help_text += f"  {cmd_name:<15} - {info['description']}\n"
                except Exception:
                    help_text += f"  {cmd_name:<15} - Comando CLI\n"
            
            return help_text
        
        else:
            # Ajuda geral expandida
            help_text = "\nALFREDO AI - Assistente de Análise de Vídeo\n"
            help_text += "=" * 70 + "\n"
            
            # Comandos por categoria
            for category in sorted(self.get_all_categories()):
                commands_in_category = self.get_commands_by_category(category)
                if commands_in_category:
                    help_text += f"\n{category.upper()}:\n"
                    for cmd_name in sorted(commands_in_category):
                        try:
                            command = self.get_command(cmd_name)
                            info = command.get_command_info()
                            help_text += f"  {cmd_name:<15} - {info['description']}\n"
                        except Exception:
                            help_text += f"  {cmd_name:<15} - Comando CLI\n"
            
            # Aliases se existirem
            if self._aliases:
                help_text += "\nALIASES:\n"
                for alias, command in sorted(self._aliases.items()):
                    help_text += f"  {alias:<15} -> {command}\n"
            
            help_text += "\nUSO:\n"
            help_text += "  alfredo <comando> [argumentos]\n"
            help_text += "  alfredo <comando> --help    # Ajuda específica do comando\n"
            help_text += "  alfredo help <categoria>    # Comandos de uma categoria\n"
            
            help_text += "\nEXEMPLOS:\n"
            help_text += "  alfredo youtube https://youtube.com/watch?v=VIDEO_ID\n"
            help_text += "  alfredo local /path/to/video.mp4 --language en\n"
            help_text += "  alfredo batch /path/to/videos/ --parallel 3\n"
            
            return help_text

    def register_command(self, name: str, command_class: Type[Command]) -> None:
        """
        Registra um novo comando no registry.
        
        Args:
            name: Nome do comando
            command_class: Classe do comando
        """
        if not issubclass(command_class, Command):
            raise ValueError(f"Comando deve herdar de Command: {command_class}")
        
        self._commands[name] = command_class
        
        # Tentar obter metadados para aliases e categoria
        try:
            temp_command = command_class(self.config, self.factory)
            metadata = temp_command.get_metadata()
            
            # Registrar aliases
            for alias in metadata.aliases:
                self._aliases[alias] = name
            
            # Registrar categoria
            category = metadata.category
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(name)
            
        except Exception as e:
            self.logger.warning(f"Erro ao obter metadados do comando {name}: {e}")
        
        self.logger.info(f"Comando '{name}' registrado: {command_class.__name__}")

    def register_alias(self, alias: str, command_name: str) -> None:
        """Registra um alias para um comando.
        
        Args:
            alias: Nome do alias
            command_name: Nome do comando real
        """
        if command_name not in self._commands:
            raise ValueError(f"Comando '{command_name}' não existe")
        
        self._aliases[alias] = command_name
        self.logger.info(f"Alias '{alias}' registrado para comando '{command_name}'")

    def get_commands_by_category(self, category: str) -> List[str]:
        """Retorna comandos de uma categoria específica.
        
        Args:
            category: Nome da categoria
            
        Returns:
            Lista de comandos da categoria
        """
        return self._categories.get(category, [])

    def get_all_categories(self) -> List[str]:
        """Retorna todas as categorias disponíveis.
        
        Returns:
            Lista de categorias
        """
        return list(self._categories.keys())

    def get_aliases(self) -> Dict[str, str]:
        """Retorna todos os aliases registrados.
        
        Returns:
            Dicionário de aliases para comandos
        """
        return self._aliases.copy()

    def find_command_by_pattern(self, pattern: str) -> List[str]:
        """Encontra comandos que correspondem a um padrão.
        
        Args:
            pattern: Padrão de busca (substring)
            
        Returns:
            Lista de comandos que correspondem ao padrão
        """
        matches = []
        pattern_lower = pattern.lower()
        
        # Buscar em nomes de comandos
        for name in self._commands.keys():
            if pattern_lower in name.lower():
                matches.append(name)
        
        # Buscar em aliases
        for alias, command in self._aliases.items():
            if pattern_lower in alias.lower() and command not in matches:
                matches.append(command)
        
        return matches

    def list_commands(self) -> list:
        """
        Lista nomes dos comandos disponíveis.
        
        Returns:
            Lista com nomes dos comandos
        """
        return list(self._commands.keys())