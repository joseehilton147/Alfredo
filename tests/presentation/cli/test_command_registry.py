"""
Testes para CommandRegistry - Command Pattern.

Testa o registro automático de comandos, descoberta e funcionalidades
expandidas do sistema de comandos CLI.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.presentation.cli.command_registry import CommandRegistry
from src.presentation.cli.base_command import Command, CommandMetadata
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory


class MockCommand(Command):
    """Comando mock para testes."""
    
    def _initialize_metadata(self):
        self._metadata = CommandMetadata(
            name="mock",
            description="Comando mock para testes",
            category="test",
            aliases=["m", "test"]
        )
    
    async def execute_from_parsed_args(self, args):
        return {"status": "success", "command": "mock"}
    
    def validate_parsed_args(self, args):
        return True


class TestCommandRegistry:
    """Testes para o registry de comandos."""

    @pytest.fixture
    def config(self):
        """Fixture para configuração de teste."""
        return Mock(spec=AlfredoConfig)

    @pytest.fixture
    def factory(self):
        """Fixture para factory de teste."""
        return Mock(spec=InfrastructureFactory)

    @pytest.fixture
    def registry(self, config, factory):
        """Fixture para registry de teste."""
        with patch.object(CommandRegistry, '_register_default_commands'), \
             patch.object(CommandRegistry, '_auto_discover_commands'):
            return CommandRegistry(config, factory, auto_discover=False)

    def test_registry_initialization(self, config, factory):
        """Testa inicialização do registry."""
        with patch.object(CommandRegistry, '_register_default_commands') as mock_default, \
             patch.object(CommandRegistry, '_auto_discover_commands') as mock_discover:
            
            registry = CommandRegistry(config, factory, auto_discover=True)
            
            assert registry.config == config
            assert registry.factory == factory
            mock_default.assert_called_once()
            mock_discover.assert_called_once()

    def test_registry_initialization_no_auto_discover(self, config, factory):
        """Testa inicialização sem descoberta automática."""
        with patch.object(CommandRegistry, '_register_default_commands') as mock_default, \
             patch.object(CommandRegistry, '_auto_discover_commands') as mock_discover:
            
            registry = CommandRegistry(config, factory, auto_discover=False)
            
            mock_default.assert_called_once()
            mock_discover.assert_not_called()

    def test_register_command_success(self, registry):
        """Testa registro de comando com sucesso."""
        registry.register_command("mock", MockCommand)
        
        assert "mock" in registry._commands
        assert registry._commands["mock"] == MockCommand

    def test_register_command_invalid_class(self, registry):
        """Testa erro ao registrar classe que não herda de Command."""
        class InvalidCommand:
            pass
        
        with pytest.raises(ValueError) as exc_info:
            registry.register_command("invalid", InvalidCommand)
        
        assert "deve herdar de Command" in str(exc_info.value)

    def test_register_command_with_metadata(self, registry, config, factory):
        """Testa registro de comando com metadados."""
        # Mock para evitar criação real do comando
        with patch.object(MockCommand, '__init__', return_value=None):
            mock_instance = MockCommand.__new__(MockCommand)
            mock_instance._metadata = CommandMetadata(
                name="mock",
                description="Comando mock",
                category="test",
                aliases=["m"]
            )
            
            with patch.object(MockCommand, '__call__', return_value=mock_instance):
                registry.register_command("mock", MockCommand)
        
        # Verificar que aliases foram registrados
        assert "m" in registry._aliases
        assert registry._aliases["m"] == "mock"
        
        # Verificar categoria
        assert "test" in registry._categories
        assert "mock" in registry._categories["test"]

    def test_get_command_success(self, registry, config, factory):
        """Testa obtenção de comando com sucesso."""
        registry._commands["mock"] = MockCommand
        
        command = registry.get_command("mock")
        
        assert isinstance(command, MockCommand)

    def test_get_command_via_alias(self, registry, config, factory):
        """Testa obtenção de comando via alias."""
        registry._commands["mock"] = MockCommand
        registry._aliases["m"] = "mock"
        
        command = registry.get_command("m")
        
        assert isinstance(command, MockCommand)

    def test_get_command_not_found(self, registry):
        """Testa erro quando comando não é encontrado."""
        with pytest.raises(ValueError) as exc_info:
            registry.get_command("inexistente")
        
        assert "não encontrado" in str(exc_info.value)

    def test_get_available_commands(self, registry, config, factory):
        """Testa listagem de comandos disponíveis."""
        registry._commands["mock"] = MockCommand
        
        # Mock para evitar criação real do comando
        with patch.object(MockCommand, '__init__', return_value=None):
            mock_instance = MockCommand.__new__(MockCommand)
            mock_instance.get_command_info = Mock(return_value={"description": "Comando mock"})
            
            with patch.object(MockCommand, '__call__', return_value=mock_instance):
                commands = registry.get_available_commands()
        
        assert "mock" in commands
        assert commands["mock"] == "Comando mock"

    def test_register_alias(self, registry):
        """Testa registro de alias."""
        registry._commands["mock"] = MockCommand
        
        registry.register_alias("test", "mock")
        
        assert registry._aliases["test"] == "mock"

    def test_register_alias_command_not_exists(self, registry):
        """Testa erro ao registrar alias para comando inexistente."""
        with pytest.raises(ValueError) as exc_info:
            registry.register_alias("test", "inexistente")
        
        assert "não existe" in str(exc_info.value)

    def test_get_commands_by_category(self, registry):
        """Testa obtenção de comandos por categoria."""
        registry._categories["test"] = ["mock1", "mock2"]
        
        commands = registry.get_commands_by_category("test")
        
        assert commands == ["mock1", "mock2"]

    def test_get_commands_by_category_not_found(self, registry):
        """Testa obtenção de comandos de categoria inexistente."""
        commands = registry.get_commands_by_category("inexistente")
        
        assert commands == []

    def test_get_all_categories(self, registry):
        """Testa obtenção de todas as categorias."""
        registry._categories = {"test": ["mock"], "video": ["youtube"]}
        
        categories = registry.get_all_categories()
        
        assert set(categories) == {"test", "video"}

    def test_get_aliases(self, registry):
        """Testa obtenção de todos os aliases."""
        registry._aliases = {"m": "mock", "t": "test"}
        
        aliases = registry.get_aliases()
        
        assert aliases == {"m": "mock", "t": "test"}

    def test_find_command_by_pattern(self, registry):
        """Testa busca de comandos por padrão."""
        registry._commands = {"youtube": MockCommand, "local": MockCommand, "batch": MockCommand}
        registry._aliases = {"yt": "youtube"}
        
        matches = registry.find_command_by_pattern("you")
        
        assert "youtube" in matches

    def test_find_command_by_pattern_in_aliases(self, registry):
        """Testa busca de comandos por padrão em aliases."""
        registry._commands = {"youtube": MockCommand}
        registry._aliases = {"yt": "youtube", "tube": "youtube"}
        
        matches = registry.find_command_by_pattern("yt")
        
        assert "youtube" in matches

    def test_get_command_help_specific(self, registry, config, factory):
        """Testa obtenção de help para comando específico."""
        registry._commands["mock"] = MockCommand
        
        # Mock para evitar criação real do comando
        with patch.object(MockCommand, '__init__', return_value=None):
            mock_instance = MockCommand.__new__(MockCommand)
            mock_instance.get_help_text = Mock(return_value="Help do comando mock")
            
            with patch.object(MockCommand, '__call__', return_value=mock_instance):
                help_text = registry.get_command_help("mock")
        
        assert help_text == "Help do comando mock"

    def test_get_command_help_not_found(self, registry):
        """Testa help para comando não encontrado."""
        help_text = registry.get_command_help("inexistente")
        
        assert "não encontrado" in help_text

    def test_get_command_help_with_suggestions(self, registry):
        """Testa help com sugestões de comandos similares."""
        registry._commands = {"youtube": MockCommand}
        
        with patch.object(registry, 'find_command_by_pattern', return_value=["youtube"]):
            help_text = registry.get_command_help("you")
        
        assert "Comandos similares" in help_text
        assert "youtube" in help_text

    def test_get_command_help_by_category(self, registry, config, factory):
        """Testa help por categoria."""
        registry._categories = {"test": ["mock"]}
        registry._commands = {"mock": MockCommand}
        
        # Mock para evitar criação real do comando
        with patch.object(MockCommand, '__init__', return_value=None):
            mock_instance = MockCommand.__new__(MockCommand)
            mock_instance.get_command_info = Mock(return_value={"description": "Comando mock"})
            
            with patch.object(MockCommand, '__call__', return_value=mock_instance):
                help_text = registry.get_command_help(category="test")
        
        assert "CATEGORIA: TEST" in help_text
        assert "mock" in help_text

    def test_get_command_help_category_not_found(self, registry):
        """Testa help para categoria não encontrada."""
        help_text = registry.get_command_help(category="inexistente")
        
        assert "não encontrada" in help_text

    def test_get_command_help_general(self, registry, config, factory):
        """Testa help geral."""
        registry._categories = {"test": ["mock"]}
        registry._commands = {"mock": MockCommand}
        registry._aliases = {"m": "mock"}
        
        # Mock para evitar criação real do comando
        with patch.object(MockCommand, '__init__', return_value=None):
            mock_instance = MockCommand.__new__(MockCommand)
            mock_instance.get_command_info = Mock(return_value={"description": "Comando mock"})
            
            with patch.object(MockCommand, '__call__', return_value=mock_instance):
                help_text = registry.get_command_help()
        
        assert "ALFREDO AI" in help_text
        assert "TEST:" in help_text
        assert "ALIASES:" in help_text
        assert "EXEMPLOS:" in help_text

    def test_list_commands(self, registry):
        """Testa listagem de nomes de comandos."""
        registry._commands = {"mock": MockCommand, "test": MockCommand}
        
        commands = registry.list_commands()
        
        assert set(commands) == {"mock", "test"}

    @patch('importlib.import_module')
    @patch('inspect.getmembers')
    @patch('pathlib.Path.glob')
    def test_auto_discover_commands(self, mock_glob, mock_getmembers, mock_import, registry):
        """Testa descoberta automática de comandos."""
        # Mock arquivos encontrados
        mock_file = Mock()
        mock_file.name = "test_command.py"
        mock_file.stem = "test_command"
        mock_glob.return_value = [mock_file]
        
        # Mock módulo importado
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        # Mock classes encontradas
        mock_getmembers.return_value = [("TestCommand", MockCommand)]
        
        # Mock para verificar se é subclasse
        with patch('inspect.isclass', return_value=True), \
             patch('builtins.issubclass', return_value=True):
            
            registry._auto_discover_commands()
        
        # Verificar que comando foi registrado
        mock_import.assert_called_once()

    def test_command_polymorphism(self, config, factory):
        """Testa comportamento polimórfico dos comandos."""
        # Criar diferentes comandos mock
        commands = []
        
        for name in ["youtube", "local", "batch"]:
            command_class = type(f"{name.title()}Command", (Command,), {
                "_initialize_metadata": lambda self: setattr(self, '_metadata', CommandMetadata(
                    name=name,
                    description=f"Comando {name}",
                    category="video"
                )),
                "execute_from_parsed_args": lambda self, args: {"command": name},
                "validate_parsed_args": lambda self, args: True
            })
            commands.append((name, command_class))
        
        # Todos devem implementar a mesma interface
        for name, command_class in commands:
            # Verificar que herdam de Command
            assert issubclass(command_class, Command)
            
            # Verificar que têm métodos obrigatórios
            instance = command_class.__new__(command_class)
            assert hasattr(instance, 'execute_from_parsed_args')
            assert hasattr(instance, 'validate_parsed_args')
            assert hasattr(instance, '_initialize_metadata')

    def test_extensibility_new_command(self, registry, config, factory):
        """Testa facilidade de adicionar novo comando."""
        # Criar novo comando
        class NovoCommand(Command):
            def _initialize_metadata(self):
                self._metadata = CommandMetadata(
                    name="novo",
                    description="Novo comando",
                    category="extensao"
                )
            
            async def execute_from_parsed_args(self, args):
                return {"status": "novo comando executado"}
            
            def validate_parsed_args(self, args):
                return True
        
        # Registrar novo comando
        registry.register_command("novo", NovoCommand)
        
        # Verificar que foi adicionado
        assert "novo" in registry.list_commands()
        
        # Verificar que pode ser obtido
        command = registry.get_command("novo")
        assert isinstance(command, NovoCommand)
        
        # Verificar categoria
        assert "extensao" in registry.get_all_categories()
        assert "novo" in registry.get_commands_by_category("extensao")

    def test_command_metadata_validation(self, config, factory):
        """Testa validação de metadados dos comandos."""
        # Comando com metadados válidos
        class ValidCommand(Command):
            def _initialize_metadata(self):
                self._metadata = CommandMetadata(
                    name="valid",
                    description="Comando válido",
                    usage="alfredo valid [opções]",
                    examples=["valid --help", "valid --option value"],
                    category="test",
                    aliases=["v"]
                )
            
            async def execute_from_parsed_args(self, args):
                return {"status": "success"}
            
            def validate_parsed_args(self, args):
                return True
        
        # Criar instância e verificar metadados
        command = ValidCommand.__new__(ValidCommand)
        command._initialize_metadata()
        
        metadata = command._metadata
        assert metadata.name == "valid"
        assert metadata.description == "Comando válido"
        assert metadata.category == "test"
        assert "v" in metadata.aliases
        assert len(metadata.examples) == 2