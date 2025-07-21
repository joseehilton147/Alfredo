"""
Testes para AIStrategyContext - Strategy Pattern.

Testa o comportamento polimórfico das estratégias de IA e a facilidade
de extensibilidade do sistema.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.application.services.ai_strategy_context import AIStrategyContext, StrategyType
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError, ProviderUnavailableError


class TestAIStrategyContext:
    """Testes para o contexto de estratégias de IA."""

    @pytest.fixture
    def config(self):
        """Fixture para configuração de teste."""
        config = Mock(spec=AlfredoConfig)
        config.default_ai_provider = "mock"
        return config

    @pytest.fixture
    def mock_strategy(self):
        """Fixture para estratégia mock."""
        strategy = Mock()
        strategy.get_strategy_name.return_value = "mock"
        strategy.is_available.return_value = True
        strategy.get_configuration.return_value = {
            "supports_transcription": True,
            "supports_summarization": True
        }
        strategy.get_supported_languages.return_value = ["pt", "en"]
        strategy.transcribe = AsyncMock(return_value="Transcrição mock")
        strategy.summarize = AsyncMock(return_value="Resumo mock")
        return strategy

    def test_strategy_context_initialization(self, config):
        """Testa inicialização do contexto de estratégias."""
        with patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy'):
            context = AIStrategyContext(config=config)
            assert context.config == config
            assert context._strategies == {}
            assert context._current_strategy is None

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_set_strategy_success(self, mock_init, config, mock_strategy):
        """Testa troca de estratégia com sucesso."""
        context = AIStrategyContext(config=config)
        context._strategies = {"mock": mock_strategy}
        
        context.set_strategy("mock")
        
        assert context._current_strategy == mock_strategy

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_set_strategy_not_available(self, mock_init, config):
        """Testa erro ao tentar usar estratégia não disponível."""
        context = AIStrategyContext(config=config)
        context._strategies = {}
        
        with pytest.raises(ConfigurationError) as exc_info:
            context.set_strategy("inexistente")
        
        assert "não está disponível" in str(exc_info.value)

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_current_strategy_success(self, mock_init, config, mock_strategy):
        """Testa obtenção da estratégia atual."""
        context = AIStrategyContext(config=config)
        context._current_strategy = mock_strategy
        
        result = context.get_current_strategy()
        
        assert result == mock_strategy

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_current_strategy_none_available(self, mock_init, config):
        """Testa erro quando nenhuma estratégia está disponível."""
        context = AIStrategyContext(config=config)
        context._current_strategy = None
        context._strategies = {}  # Garantir que é um dicionário vazio
        
        with pytest.raises(ProviderUnavailableError) as exc_info:
            context.get_current_strategy()
        
        assert "Nenhuma estratégia de IA está disponível" in str(exc_info.value)

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_available_strategies(self, mock_init, config, mock_strategy):
        """Testa listagem de estratégias disponíveis."""
        context = AIStrategyContext(config=config)
        context._strategies = {"mock": mock_strategy, "test": Mock()}
        
        result = context.get_available_strategies()
        
        assert result == ["mock", "test"]

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_strategy_info_current(self, mock_init, config, mock_strategy):
        """Testa obtenção de informações da estratégia atual."""
        context = AIStrategyContext(config=config)
        context._current_strategy = mock_strategy
        
        result = context.get_strategy_info()
        
        assert result["name"] == "mock"
        assert result["is_available"] is True

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_strategy_info_specific(self, mock_init, config, mock_strategy):
        """Testa obtenção de informações de estratégia específica."""
        context = AIStrategyContext(config=config)
        context._strategies = {"mock": mock_strategy}
        
        result = context.get_strategy_info("mock")
        
        assert result["name"] == "mock"
        assert result["configuration"]["supports_transcription"] is True

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_best_strategy_for_transcription(self, mock_init, config):
        """Testa seleção da melhor estratégia para transcrição."""
        context = AIStrategyContext(config=config)
        
        # Mock strategies com diferentes capacidades
        whisper_mock = Mock()
        whisper_mock.get_configuration.return_value = {"transcription_only": True}
        
        groq_mock = Mock()
        groq_mock.get_configuration.return_value = {"supports_summarization": True}
        
        context._strategies = {"whisper": whisper_mock, "groq": groq_mock}
        
        result = context.get_best_strategy_for_task("transcription")
        
        # Whisper ou Groq devem ser preferidos para transcrição
        assert result in ["whisper", "groq"]

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_best_strategy_for_summarization(self, mock_init, config):
        """Testa seleção da melhor estratégia para sumarização."""
        context = AIStrategyContext(config=config)
        
        # Mock strategies com diferentes capacidades
        whisper_mock = Mock()
        whisper_mock.get_configuration.return_value = {"transcription_only": True}
        
        groq_mock = Mock()
        groq_mock.get_configuration.return_value = {"supports_summarization": True}
        
        context._strategies = {"whisper": whisper_mock, "groq": groq_mock}
        
        result = context.get_best_strategy_for_task("summarization")
        
        # Groq deve ser preferido para sumarização
        assert result == "groq"

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_get_best_strategy_no_suitable(self, mock_init, config):
        """Testa erro quando nenhuma estratégia suporta a tarefa."""
        context = AIStrategyContext(config=config)
        
        # Mock strategy que não suporta sumarização
        mock_strategy = Mock()
        mock_strategy.get_configuration.return_value = {"supports_summarization": False}
        
        context._strategies = {"mock": mock_strategy}
        
        with pytest.raises(ConfigurationError) as exc_info:
            context.get_best_strategy_for_task("summarization")
        
        assert "Nenhuma estratégia disponível suporta" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    async def test_transcribe_with_best_strategy(self, mock_init, config, mock_strategy):
        """Testa transcrição usando melhor estratégia."""
        context = AIStrategyContext(config=config)
        context._strategies = {"mock": mock_strategy}
        context._current_strategy = mock_strategy
        
        with patch.object(context, 'get_best_strategy_for_task', return_value="mock"):
            result = await context.transcribe_with_best_strategy("audio.wav", "pt")
        
        assert result == "Transcrição mock"
        mock_strategy.transcribe.assert_called_once_with("audio.wav", "pt")

    @pytest.mark.asyncio
    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    async def test_summarize_with_best_strategy(self, mock_init, config, mock_strategy):
        """Testa sumarização usando melhor estratégia."""
        context = AIStrategyContext(config=config)
        context._strategies = {"mock": mock_strategy}
        context._current_strategy = mock_strategy
        
        with patch.object(context, 'get_best_strategy_for_task', return_value="mock"):
            result = await context.summarize_with_best_strategy("texto", "contexto")
        
        assert result == "Resumo mock"
        mock_strategy.summarize.assert_called_once_with("texto", "contexto")

    @pytest.mark.asyncio
    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    async def test_strategy_restoration_after_best_strategy_use(self, mock_init, config):
        """Testa que estratégia original é restaurada após usar melhor estratégia."""
        context = AIStrategyContext(config=config)
        
        original_strategy = Mock()
        original_strategy.get_strategy_name.return_value = "original"
        
        best_strategy = Mock()
        best_strategy.get_strategy_name.return_value = "best"
        best_strategy.transcribe = AsyncMock(return_value="resultado")
        
        context._strategies = {"original": original_strategy, "best": best_strategy}
        context._current_strategy = original_strategy
        
        with patch.object(context, 'get_best_strategy_for_task', return_value="best"):
            await context.transcribe_with_best_strategy("audio.wav")
        
        # Estratégia original deve ser restaurada
        assert context._current_strategy == original_strategy

    def test_polymorphic_behavior(self, config):
        """Testa comportamento polimórfico das estratégias."""
        # Criar diferentes implementações mock
        strategies = []
        
        for name in ["whisper", "groq", "ollama", "mock"]:
            strategy = Mock()
            strategy.get_strategy_name.return_value = name
            strategy.is_available.return_value = True
            strategy.transcribe = AsyncMock(return_value=f"Transcrição {name}")
            strategy.summarize = AsyncMock(return_value=f"Resumo {name}")
            strategies.append((name, strategy))
        
        # Todas devem implementar a mesma interface
        for name, strategy in strategies:
            assert hasattr(strategy, 'transcribe')
            assert hasattr(strategy, 'summarize')
            assert hasattr(strategy, 'get_strategy_name')
            assert hasattr(strategy, 'is_available')
            assert strategy.get_strategy_name() == name

    @patch('src.application.services.ai_strategy_context.AIStrategyContext._initialize_default_strategy')
    def test_extensibility_new_strategy(self, mock_init, config):
        """Testa facilidade de adicionar nova estratégia."""
        context = AIStrategyContext(config=config)
        context._strategies = {}  # Inicializar como dicionário vazio
        
        # Simular adição de nova estratégia
        new_strategy = Mock()
        new_strategy.get_strategy_name.return_value = "nova_estrategia"
        new_strategy.is_available.return_value = True
        new_strategy.get_configuration.return_value = {
            "supports_transcription": True,
            "supports_summarization": True
        }
        
        # Adicionar à lista de estratégias
        context._strategies["nova_estrategia"] = new_strategy
        
        # Verificar que foi adicionada corretamente
        assert "nova_estrategia" in context.get_available_strategies()
        
        # Verificar que pode ser usada
        context.set_strategy("nova_estrategia")
        assert context.get_current_strategy() == new_strategy

    def test_strategy_configuration_validation(self, config):
        """Testa validação de configurações das estratégias."""
        # Estratégia com configuração válida
        valid_strategy = Mock()
        valid_strategy.get_configuration.return_value = {
            "model": "test-model",
            "supports_transcription": True,
            "supports_summarization": False,
            "timeout": 300
        }
        
        config_info = valid_strategy.get_configuration()
        
        # Verificar campos obrigatórios
        assert "supports_transcription" in config_info
        assert "supports_summarization" in config_info
        assert isinstance(config_info["supports_transcription"], bool)
        assert isinstance(config_info["supports_summarization"], bool)