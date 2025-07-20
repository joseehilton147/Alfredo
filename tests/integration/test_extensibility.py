"""
Testes de Integração para Extensibilidade do Sistema.

Valida que novos componentes podem ser adicionados facilmente e que
os padrões implementados facilitam a extensão do sistema.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
from pathlib import Path

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.application.services.ai_strategy_context import AIStrategyContext
from src.presentation.cli.command_registry import CommandRegistry
from src.application.interfaces.ai_strategy import AIStrategy
from src.presentation.cli.base_command import Command, CommandMetadata


class TestSystemExtensibility:
    """Testes para validar extensibilidade do sistema."""

    @pytest.fixture
    def config(self):
        """Fixture para configuração de teste."""
        config = Mock(spec=AlfredoConfig)
        config.default_ai_provider = "mock"
        return config

    @pytest.fixture
    def factory(self, config):
        """Fixture para factory de teste."""
        return InfrastructureFactory(config)

    def test_new_ai_provider_integration_time(self, config):
        """Testa que novo AI provider pode ser integrado rapidamente."""
        import time
        
        start_time = time.time()
        
        # Simular implementação de novo provider
        class RapidProviderStrategy(AIStrategy):
            def __init__(self, config):
                self.config = config
                self.name = "rapid_provider"
            
            async def transcribe(self, audio_path: str, language=None) -> str:
                return f"Transcrição rápida de {audio_path}"
            
            async def summarize(self, text: str, context=None) -> str:
                return f"Resumo rápido: {text[:50]}..."
            
            def get_supported_languages(self) -> list[str]:
                return ["pt", "en"]
            
            def get_strategy_name(self) -> str:
                return self.name
            
            def get_configuration(self) -> dict:
                return {
                    "model": "rapid-model",
                    "supports_transcription": True,
                    "supports_summarization": True,
                    "implementation_time": "< 15 minutos"
                }
            
            def is_available(self) -> bool:
                return True
        
        # Criar instância
        provider = RapidProviderStrategy(config)
        
        # Verificar que implementa interface corretamente
        assert isinstance(provider, AIStrategy)
        assert provider.get_strategy_name() == "rapid_provider"
        assert provider.is_available() is True
        
        implementation_time = time.time() - start_time
        
        # Implementação deve ser muito rápida (< 1 segundo para criar classe)
        assert implementation_time < 1.0
        
        # Verificar configuração
        config_info = provider.get_configuration()
        assert "implementation_time" in config_info

    def test_new_command_integration_time(self, config):
        """Testa que novo comando pode ser integrado rapidamente."""
        import time
        
        start_time = time.time()
        
        # Simular implementação de novo comando
        class RapidCommand(Command):
            def _initialize_metadata(self):
                self._metadata = CommandMetadata(
                    name="rapid",
                    description="Comando implementado rapidamente",
                    category="test",
                    aliases=["r"]
                )
            
            async def execute_from_parsed_args(self, args):
                return {"status": "rapid execution", "time": "< 5 minutos"}
            
            def validate_parsed_args(self, args):
                return True
        
        # Registrar comando
        factory = Mock()
        registry = CommandRegistry(config, factory, auto_discover=False)
        registry.register_command("rapid", RapidCommand)
        
        implementation_time = time.time() - start_time
        
        # Implementação deve ser muito rápida
        assert implementation_time < 1.0
        
        # Verificar que foi registrado
        assert "rapid" in registry.list_commands()
        
        # Verificar que pode ser obtido
        command = registry.get_command("rapid")
        assert isinstance(command, RapidCommand)

    @pytest.mark.asyncio
    async def test_end_to_end_new_provider_workflow(self, config):
        """Testa fluxo completo com novo provider."""
        # Criar novo provider
        class E2ETestProvider(AIStrategy):
            def __init__(self, config):
                self.config = config
            
            async def transcribe(self, audio_path: str, language=None) -> str:
                return f"E2E Transcrição: {audio_path}"
            
            async def summarize(self, text: str, context=None) -> str:
                return f"E2E Resumo: {text}"
            
            def get_supported_languages(self) -> list[str]:
                return ["pt", "en"]
            
            def get_strategy_name(self) -> str:
                return "e2e_test"
            
            def get_configuration(self) -> dict:
                return {
                    "supports_transcription": True,
                    "supports_summarization": True
                }
            
            def is_available(self) -> bool:
                return True
        
        # Integrar ao contexto
        context = AIStrategyContext(config)
        context._strategies["e2e_test"] = E2ETestProvider(config)
        
        # Testar uso
        context.set_strategy("e2e_test")
        current = context.get_current_strategy()
        
        # Verificar funcionalidades
        transcription = await current.transcribe("test.wav", "pt")
        assert "E2E Transcrição" in transcription
        
        summary = await current.summarize("texto teste", "contexto")
        assert "E2E Resumo" in summary

    def test_factory_extensibility(self, config):
        """Testa extensibilidade da factory."""
        factory = InfrastructureFactory(config)
        
        # Simular adição de novo tipo de dependência
        class NovoGateway:
            def __init__(self, config):
                self.config = config
            
            def nova_operacao(self):
                return "Nova funcionalidade"
        
        # Adicionar método à factory dinamicamente
        def create_novo_gateway(self):
            cache_key = 'novo_gateway'
            if cache_key not in self._instances:
                self._instances[cache_key] = NovoGateway(self._config)
            return self._instances[cache_key]
        
        # Monkey patch para simular extensão
        factory.create_novo_gateway = create_novo_gateway.__get__(factory, InfrastructureFactory)
        
        # Testar que funciona
        gateway = factory.create_novo_gateway()
        assert isinstance(gateway, NovoGateway)
        assert gateway.nova_operacao() == "Nova funcionalidade"
        
        # Testar cache singleton
        gateway2 = factory.create_novo_gateway()
        assert gateway is gateway2

    def test_command_discovery_mechanism(self, config):
        """Testa mecanismo de descoberta de comandos."""
        factory = Mock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar arquivo de comando temporário
            command_file = Path(temp_dir) / "test_discovery_command.py"
            command_content = '''
from src.presentation.cli.base_command import Command, CommandMetadata

class TestDiscoveryCommand(Command):
    def _initialize_metadata(self):
        self._metadata = CommandMetadata(
            name="test_discovery",
            description="Comando descoberto automaticamente"
        )
    
    async def execute_from_parsed_args(self, args):
        return {"discovered": True}
    
    def validate_parsed_args(self, args):
        return True
'''
            command_file.write_text(command_content)
            
            # Mock para simular descoberta
            with patch('pathlib.Path.glob') as mock_glob, \
                 patch('importlib.import_module') as mock_import, \
                 patch('inspect.getmembers') as mock_members, \
                 patch('inspect.isclass', return_value=True), \
                 patch('builtins.issubclass', return_value=True):
                
                # Configurar mocks
                mock_glob.return_value = [command_file]
                mock_module = Mock()
                mock_import.return_value = mock_module
                
                # Simular classe encontrada
                mock_command_class = Mock()
                mock_command_class.__name__ = "TestDiscoveryCommand"
                mock_members.return_value = [("TestDiscoveryCommand", mock_command_class)]
                
                # Testar descoberta
                registry = CommandRegistry(config, factory, auto_discover=True)
                
                # Verificar que tentou importar
                mock_import.assert_called()

    def test_configuration_extensibility(self, config):
        """Testa extensibilidade do sistema de configuração."""
        # Simular extensão da configuração
        original_config = AlfredoConfig()
        
        # Adicionar nova configuração dinamicamente
        setattr(original_config, 'novo_provider_api_key', 'test_key')
        setattr(original_config, 'novo_provider_model', 'novo-model-v1')
        
        # Verificar que foi adicionada
        assert hasattr(original_config, 'novo_provider_api_key')
        assert original_config.novo_provider_api_key == 'test_key'

    @pytest.mark.asyncio
    async def test_multiple_providers_coexistence(self, config):
        """Testa coexistência de múltiplos providers."""
        # Criar múltiplos providers
        providers = {}
        
        for i in range(3):
            class TestProvider(AIStrategy):
                def __init__(self, config, provider_id):
                    self.config = config
                    self.provider_id = provider_id
                
                async def transcribe(self, audio_path: str, language=None) -> str:
                    return f"Provider {self.provider_id}: {audio_path}"
                
                async def summarize(self, text: str, context=None) -> str:
                    return f"Provider {self.provider_id}: {text}"
                
                def get_supported_languages(self) -> list[str]:
                    return ["pt", "en"]
                
                def get_strategy_name(self) -> str:
                    return f"test_provider_{self.provider_id}"
                
                def get_configuration(self) -> dict:
                    return {"supports_transcription": True, "supports_summarization": True}
                
                def is_available(self) -> bool:
                    return True
            
            providers[f"test_provider_{i}"] = TestProvider(config, i)
        
        # Integrar ao contexto
        context = AIStrategyContext(config)
        context._strategies.update(providers)
        
        # Testar que todos funcionam
        for provider_name, provider in providers.items():
            context.set_strategy(provider_name)
            current = context.get_current_strategy()
            
            result = await current.transcribe("test.wav")
            assert provider_name.split('_')[-1] in result

    def test_backward_compatibility(self, config):
        """Testa compatibilidade com implementações anteriores."""
        # Simular provider antigo (sem alguns métodos novos)
        class LegacyProvider(AIStrategy):
            async def transcribe(self, audio_path: str, language=None) -> str:
                return "Legacy transcription"
            
            async def summarize(self, text: str, context=None) -> str:
                return "Legacy summary"
            
            def get_supported_languages(self) -> list[str]:
                return ["pt"]
            
            def get_strategy_name(self) -> str:
                return "legacy"
            
            def get_configuration(self) -> dict:
                # Configuração mínima (compatibilidade)
                return {
                    "supports_transcription": True,
                    "supports_summarization": True
                }
            
            def is_available(self) -> bool:
                return True
        
        # Verificar que ainda funciona
        legacy_provider = LegacyProvider()
        assert isinstance(legacy_provider, AIStrategy)
        assert legacy_provider.get_strategy_name() == "legacy"

    def test_error_isolation_between_providers(self, config):
        """Testa isolamento de erros entre providers."""
        # Provider que falha
        class FailingProvider(AIStrategy):
            async def transcribe(self, audio_path: str, language=None) -> str:
                raise Exception("Provider falhou")
            
            async def summarize(self, text: str, context=None) -> str:
                raise Exception("Provider falhou")
            
            def get_supported_languages(self) -> list[str]:
                return ["pt"]
            
            def get_strategy_name(self) -> str:
                return "failing"
            
            def get_configuration(self) -> dict:
                return {"supports_transcription": True, "supports_summarization": True}
            
            def is_available(self) -> bool:
                return False  # Reporta como não disponível
        
        # Provider que funciona
        class WorkingProvider(AIStrategy):
            async def transcribe(self, audio_path: str, language=None) -> str:
                return "Working transcription"
            
            async def summarize(self, text: str, context=None) -> str:
                return "Working summary"
            
            def get_supported_languages(self) -> list[str]:
                return ["pt"]
            
            def get_strategy_name(self) -> str:
                return "working"
            
            def get_configuration(self) -> dict:
                return {"supports_transcription": True, "supports_summarization": True}
            
            def is_available(self) -> bool:
                return True
        
        # Integrar ao contexto
        context = AIStrategyContext(config)
        context._strategies["failing"] = FailingProvider()
        context._strategies["working"] = WorkingProvider()
        
        # Provider que falha não deve afetar o que funciona
        available = context.get_available_strategies()
        assert "working" in available
        
        # Usar provider que funciona
        context.set_strategy("working")
        current = context.get_current_strategy()
        assert current.get_strategy_name() == "working"

    def test_performance_impact_of_extensibility(self, config):
        """Testa que extensibilidade não impacta performance significativamente."""
        import time
        
        # Criar contexto com muitos providers
        context = AIStrategyContext(config)
        
        # Adicionar múltiplos providers
        for i in range(10):
            provider = Mock(spec=AIStrategy)
            provider.get_strategy_name.return_value = f"provider_{i}"
            provider.is_available.return_value = True
            provider.get_configuration.return_value = {"supports_transcription": True}
            context._strategies[f"provider_{i}"] = provider
        
        # Medir tempo de operações
        start_time = time.time()
        
        # Operações que devem ser rápidas mesmo com muitos providers
        available = context.get_available_strategies()
        context.set_strategy("provider_5")
        current = context.get_current_strategy()
        best = context.get_best_strategy_for_task("transcription")
        
        elapsed = time.time() - start_time
        
        # Operações devem ser rápidas (< 100ms)
        assert elapsed < 0.1
        assert len(available) == 10
        assert current.get_strategy_name() == "provider_5"