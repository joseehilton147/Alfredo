"""
Testes arquiteturais para validar padrões e estruturas.
Verifica dependências circulares, interfaces e factory pattern.
"""

import pytest
import sys
import importlib
from typing import Type, Protocol
from unittest.mock import Mock, patch

from core.interfaces import (
    ICoreOperations, 
    ICLIHandler, 
    IProviderFactory, 
    IAIProvider,
    ProviderNotFoundError,
    CommandNotFoundError
)
from core.provider_factory import ProviderFactory
from core.alfredo_core import AlfredoCore
from cli.alfredo import AlfredoCLI


class TestInterfaces:
    """Testes para validar interfaces e contratos."""
    
    def test_core_operations_interface(self):
        """Verifica se AlfredoCore implementa ICoreOperations."""
        core = AlfredoCore()
        assert isinstance(core, ICoreOperations)
        
        # Verifica métodos obrigatórios
        assert hasattr(core, 'handle_error')
        assert hasattr(core, 'get_provider')
        assert hasattr(core, 'list_commands')
        assert hasattr(core, 'execute_command')
    
    def test_cli_handler_interface(self):
        """Verifica se AlfredoCLI implementa ICLIHandler."""
        cli = AlfredoCLI()
        assert isinstance(cli, ICLIHandler)
        
        # Verifica métodos obrigatórios
        assert hasattr(cli, 'parse_arguments')
        assert hasattr(cli, 'execute_command')
        assert hasattr(cli, 'show_help')
    
    def test_provider_factory_interface(self):
        """Verifica se ProviderFactory implementa IProviderFactory."""
        factory = ProviderFactory()
        assert isinstance(factory, IProviderFactory)
        
        # Verifica métodos obrigatórios
        assert hasattr(factory, 'register')
        assert hasattr(factory, 'create')
        assert hasattr(factory, 'list_providers')


class MockProvider:
    """Mock provider para testes."""
    
    async def transcribe(self, audio_path: str) -> str:
        return "Mock transcription"
    
    async def summarize(self, transcription: str, video_title: str) -> str:
        return "Mock summary"


class TestProviderFactory:
    """Testes para o padrão Factory."""
    
    def setup_method(self):
        """Limpa o factory antes de cada teste."""
        ProviderFactory.reset()
    
    def test_provider_registration(self):
        """Testa registro de provedores."""
        ProviderFactory.register('mock', MockProvider)
        assert 'mock' in ProviderFactory.list_providers()
        assert ProviderFactory.is_registered('mock')
    
    def test_provider_creation(self):
        """Testa criação de provedores."""
        ProviderFactory.register('mock', MockProvider)
        provider = ProviderFactory.create('mock')
        assert isinstance(provider, MockProvider)
    
    def test_provider_not_found_error(self):
        """Testa erro quando provedor não existe."""
        with pytest.raises(ProviderNotFoundError):
            ProviderFactory.create('nonexistent')
    
    def test_provider_cache(self):
        """Testa cache de instâncias."""
        ProviderFactory.register('mock', MockProvider)
        
        # Primeira criação
        provider1 = ProviderFactory.create('mock', use_cache=True)
        
        # Segunda criação deve retornar a mesma instância
        provider2 = ProviderFactory.create('mock', use_cache=True)
        assert provider1 is provider2
        
        # Criação sem cache deve retornar nova instância
        provider3 = ProviderFactory.create('mock', use_cache=False)
        assert provider1 is not provider3
    
    def test_clear_cache(self):
        """Testa limpeza de cache."""
        ProviderFactory.register('mock', MockProvider)
        
        # Cria instância em cache
        provider1 = ProviderFactory.create('mock', use_cache=True)
        
        # Limpa cache
        ProviderFactory.clear_cache('mock')
        
        # Nova criação deve retornar instância diferente
        provider2 = ProviderFactory.create('mock', use_cache=True)
        assert provider1 is not provider2


class TestDependencyInjection:
    """Testes para injeção de dependência."""
    
    def test_core_dependency_injection(self):
        """Testa injeção de dependência no core."""
        mock_factory = Mock()
        mock_factory.list_providers.return_value = ['mock']
        mock_factory.create.return_value = MockProvider()
        
        core = AlfredoCore(provider_factory=mock_factory)
        provider = core.get_provider('mock')
        
        mock_factory.create.assert_called_once_with('mock')
        assert provider is not None
    
    def test_cli_dependency_injection(self):
        """Testa injeção de dependência na CLI."""
        mock_core = Mock(spec=ICoreOperations)
        mock_core.list_commands.return_value = {'test': {'description': 'Test command'}}
        
        cli = AlfredoCLI(core=mock_core)
        commands = cli.core.list_commands()
        
        mock_core.list_commands.assert_called_once()
        assert 'test' in commands


class TestCircularDependencies:
    """Testes para verificar ausência de dependências circulares."""
    
    def test_no_circular_imports_core_cli(self):
        """Verifica que não há imports circulares entre core e cli."""
        # Remove módulos do cache se existirem
        modules_to_remove = [
            'core.alfredo_core',
            'cli.alfredo',
            'core.interfaces',
            'core.provider_factory'
        ]
        
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
        
        # Importa core primeiro
        core_module = importlib.import_module('core.alfredo_core')
        assert core_module is not None
        
        # Importa CLI depois
        cli_module = importlib.import_module('cli.alfredo')
        assert cli_module is not None
        
        # Verifica que ambos funcionam
        core = core_module.AlfredoCore()
        cli = cli_module.AlfredoCLI(core)
        
        assert core is not None
        assert cli is not None
    
    def test_interfaces_import_independence(self):
        """Verifica que interfaces podem ser importadas independentemente."""
        # Remove interfaces do cache
        if 'core.interfaces' in sys.modules:
            del sys.modules['core.interfaces']
        
        # Importa apenas interfaces
        interfaces_module = importlib.import_module('core.interfaces')
        
        # Verifica que todas as interfaces estão disponíveis
        assert hasattr(interfaces_module, 'ICoreOperations')
        assert hasattr(interfaces_module, 'ICLIHandler')
        assert hasattr(interfaces_module, 'IProviderFactory')
        assert hasattr(interfaces_module, 'IAIProvider')


class TestErrorHandling:
    """Testes para tratamento de erros."""
    
    def test_core_error_handling(self):
        """Testa tratamento de erros no core."""
        core = AlfredoCore()
        
        # Testa erro de provedor não encontrado
        with patch('builtins.print') as mock_print:
            error = ProviderNotFoundError("Provider not found")
            core.handle_error(error)
            mock_print.assert_called()
    
    def test_command_not_found_error(self):
        """Testa erro de comando não encontrado."""
        core = AlfredoCore()
        
        with pytest.raises(CommandNotFoundError):
            core.execute_command('nonexistent_command')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
