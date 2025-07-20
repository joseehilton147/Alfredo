"""
Testes para Strategy Pattern - Comportamento Polimórfico dos AI Providers.

Valida que diferentes implementações de AIStrategy são intercambiáveis
e que o padrão facilita extensibilidade.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.application.interfaces.ai_strategy import AIStrategy
from src.infrastructure.providers.mock_provider_strategy import MockProviderStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError


class TestStrategyPattern:
    """Testes para validar o Strategy Pattern."""

    @pytest.fixture
    def config(self):
        """Fixture para configuração de teste."""
        return Mock(spec=AlfredoConfig)

    @pytest.fixture
    def mock_provider(self, config):
        """Fixture para MockProvider."""
        return MockProviderStrategy(config)

    def test_strategy_interface_compliance(self, mock_provider):
        """Testa se MockProvider implementa corretamente a interface."""
        # Verificar que implementa todos os métodos abstratos
        assert hasattr(mock_provider, 'transcribe')
        assert hasattr(mock_provider, 'summarize')
        assert hasattr(mock_provider, 'get_supported_languages')
        assert hasattr(mock_provider, 'get_strategy_name')
        assert hasattr(mock_provider, 'get_configuration')
        assert hasattr(mock_provider, 'is_available')

        # Verificar que é instância da interface
        assert isinstance(mock_provider, AIStrategy)

    def test_strategy_name_consistency(self, mock_provider):
        """Testa consistência do nome da estratégia."""
        name = mock_provider.get_strategy_name()

        assert name == "mock"
        assert isinstance(name, str)
        assert len(name) > 0

    def test_strategy_availability(self, mock_provider):
        """Testa verificação de disponibilidade."""
        is_available = mock_provider.is_available()

        assert isinstance(is_available, bool)
        # MockProvider deve estar sempre disponível
        assert is_available is True

    def test_supported_languages_format(self, mock_provider):
        """Testa formato da lista de idiomas suportados."""
        languages = mock_provider.get_supported_languages()

        assert isinstance(languages, list)
        assert len(languages) > 0
        assert all(isinstance(lang, str) for lang in languages)
        assert "pt" in languages  # Português deve estar presente
        assert "en" in languages  # Inglês deve estar presente

    def test_configuration_structure(self, mock_provider):
        """Testa estrutura da configuração."""
        config = mock_provider.get_configuration()

        assert isinstance(config, dict)

        # Campos obrigatórios
        required_fields = [
            "supports_transcription",
            "supports_summarization",
            "model"
        ]

        for field in required_fields:
            assert field in config, (
                f"Campo obrigatório '{field}' não encontrado"
            )

        # Tipos corretos
        assert isinstance(config["supports_transcription"], bool)
        assert isinstance(config["supports_summarization"], bool)
        assert isinstance(config["model"], str)

    @pytest.mark.asyncio
    async def test_transcribe_basic_functionality(self, mock_provider):
        """Testa funcionalidade básica de transcrição."""
        result = await mock_provider.transcribe("test_audio.wav", "pt")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "MockProvider" in result  # Deve identificar o provider

    @pytest.mark.asyncio
    async def test_transcribe_with_language(self, mock_provider):
        """Testa transcrição com idioma específico."""
        result = await mock_provider.transcribe("test_audio.wav", "en")

        assert isinstance(result, str)
        assert "em en" in result  # Deve mencionar o idioma

    @pytest.mark.asyncio
    async def test_transcribe_without_language(self, mock_provider):
        """Testa transcrição sem especificar idioma."""
        result = await mock_provider.transcribe("test_audio.wav")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_summarize_basic_functionality(self, mock_provider):
        """Testa funcionalidade básica de sumarização."""
        text = "Este é um texto de teste para sumarização."
        result = await mock_provider.summarize(text)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "RESUMO SIMULADO" in result

    @pytest.mark.asyncio
    async def test_summarize_with_context(self, mock_provider):
        """Testa sumarização com contexto."""
        text = "Texto de teste"
        context = "Vídeo educativo"
        result = await mock_provider.summarize(text, context)

        assert isinstance(result, str)
        assert context in result  # Contexto deve aparecer no resumo

    @pytest.mark.asyncio
    async def test_error_handling_transcription(self, mock_provider):
        """Testa tratamento de erros na transcrição."""
        # Configurar para falhar
        mock_provider.set_fail_rate(1.0)

        with pytest.raises(TranscriptionError) as exc_info:
            await mock_provider.transcribe("test.wav")

        error = exc_info.value
        assert error.provider == "mock"
        assert "simulada" in str(error)

        # Restaurar funcionamento normal
        mock_provider.set_fail_rate(0.0)

    @pytest.mark.asyncio
    async def test_error_handling_summarization(self, mock_provider):
        """Testa tratamento de erros na sumarização."""
        # Configurar para falhar
        mock_provider.set_fail_rate(1.0)

        with pytest.raises(TranscriptionError) as exc_info:
            await mock_provider.summarize("texto teste")

        error = exc_info.value
        assert error.provider == "mock"
        assert "simulada" in str(error)

        # Restaurar funcionamento normal
        mock_provider.set_fail_rate(0.0)

    def test_configuration_methods(self, mock_provider):
        """Testa métodos de configuração específicos do MockProvider."""
        # Testar set_fail_rate
        mock_provider.set_fail_rate(0.5)
        assert mock_provider.fail_rate == 0.5

        # Testar limites
        mock_provider.set_fail_rate(-0.1)
        assert mock_provider.fail_rate == 0.0

        mock_provider.set_fail_rate(1.5)
        assert mock_provider.fail_rate == 1.0

        # Testar set_delay
        mock_provider.set_delay(2.0)
        assert mock_provider.delay_seconds == 2.0
        assert mock_provider.simulate_delay is True

        mock_provider.set_delay(0.0)
        assert mock_provider.delay_seconds == 0.0
        assert mock_provider.simulate_delay is False

    @pytest.mark.asyncio
    async def test_health_check(self, mock_provider):
        """Testa verificação de saúde do provider."""
        health = await mock_provider.health_check()

        assert isinstance(health, dict)
        assert "status" in health
        assert "model" in health
        assert "available" in health
        assert "configuration" in health
        assert "timestamp" in health

        assert health["status"] == "healthy"
        assert health["available"] is True

    def test_polymorphic_behavior_multiple_strategies(self, config):
        """Testa comportamento polimórfico com múltiplas estratégias."""
        # Criar diferentes estratégias mock
        strategies = []

        for name in ["strategy1", "strategy2", "strategy3"]:
            strategy = Mock(spec=AIStrategy)
            strategy.get_strategy_name.return_value = name
            strategy.is_available.return_value = True
            strategy.get_supported_languages.return_value = ["pt", "en"]
            strategy.get_configuration.return_value = {
                "model": f"model-{name}",
                "supports_transcription": True,
                "supports_summarization": True
            }
            strategy.transcribe = AsyncMock(
                return_value=f"Transcrição {name}"
            )
            strategy.summarize = AsyncMock(return_value=f"Resumo {name}")

            strategies.append(strategy)

        # Todas devem implementar a mesma interface
        for strategy in strategies:
            assert isinstance(strategy, AIStrategy)
            assert hasattr(strategy, 'transcribe')
            assert hasattr(strategy, 'summarize')
            assert hasattr(strategy, 'get_strategy_name')
            assert hasattr(strategy, 'is_available')
            assert hasattr(strategy, 'get_supported_languages')
            assert hasattr(strategy, 'get_configuration')

    @pytest.mark.asyncio
    async def test_strategy_interchangeability(self, config):
        """Testa que estratégias são intercambiáveis."""
        # Criar duas estratégias diferentes
        strategy1 = Mock(spec=AIStrategy)
        strategy1.transcribe = AsyncMock(return_value="Resultado 1")
        strategy1.summarize = AsyncMock(return_value="Resumo 1")

        strategy2 = Mock(spec=AIStrategy)
        strategy2.transcribe = AsyncMock(return_value="Resultado 2")
        strategy2.summarize = AsyncMock(return_value="Resumo 2")

        # Função que usa qualquer estratégia
        async def process_with_strategy(strategy: AIStrategy, audio_path: str,
                                        text: str):
            transcription = await strategy.transcribe(audio_path)
            summary = await strategy.summarize(text)
            return transcription, summary

        # Testar com primeira estratégia
        result1 = await process_with_strategy(strategy1, "audio.wav", "texto")
        assert result1 == ("Resultado 1", "Resumo 1")

        # Testar com segunda estratégia (intercambiável)
        result2 = await process_with_strategy(strategy2, "audio.wav", "texto")
        assert result2 == ("Resultado 2", "Resumo 2")

    def test_extensibility_new_strategy_implementation(self, config):
        """Testa facilidade de criar nova implementação de estratégia."""
        # Criar nova estratégia seguindo o padrão
        class NovaEstrategiaTest(AIStrategy):

            def __init__(self, config):
                self.config = config
                self.name = "nova_estrategia"

            async def transcribe(self, audio_path: str, language=None) -> str:
                return f"Nova transcrição de {audio_path}"

            async def summarize(self, text: str, context=None) -> str:
                return f"Novo resumo de {len(text)} caracteres"

            def get_supported_languages(self) -> list[str]:
                return ["pt", "en", "es"]

            def get_strategy_name(self) -> str:
                return self.name

            def get_configuration(self) -> dict:
                return {
                    "model": "nova-model-v1",
                    "supports_transcription": True,
                    "supports_summarization": True
                }

            def is_available(self) -> bool:
                return True

        # Criar instância
        nova_estrategia = NovaEstrategiaTest(config)

        # Verificar que implementa a interface corretamente
        assert isinstance(nova_estrategia, AIStrategy)
        assert nova_estrategia.get_strategy_name() == "nova_estrategia"
        assert nova_estrategia.is_available() is True

        # Verificar funcionalidades
        config_info = nova_estrategia.get_configuration()
        assert config_info["supports_transcription"] is True
        assert config_info["supports_summarization"] is True

    @pytest.mark.asyncio
    async def test_strategy_performance_characteristics(self, mock_provider):
        """Testa características de performance das estratégias."""
        import time

        # Configurar delay para testar timing
        mock_provider.set_delay(0.1)  # 100ms delay

        start_time = time.time()
        await mock_provider.transcribe("test.wav")
        elapsed = time.time() - start_time

        # Deve ter respeitado o delay configurado
        assert elapsed >= 0.1
        assert elapsed < 0.2  # Margem para overhead

        # Testar sem delay
        mock_provider.set_delay(0.0)

        start_time = time.time()
        await mock_provider.transcribe("test.wav")
        elapsed = time.time() - start_time

        # Deve ser muito rápido sem delay
        assert elapsed < 0.05

    def test_strategy_configuration_validation(self, config):
        """Testa validação de configurações das estratégias."""
        # Estratégia com configuração inválida
        class InvalidStrategy(AIStrategy):
            def get_configuration(self) -> dict:
                return {}  # Configuração vazia (inválida)

            # Outros métodos omitidos para brevidade
            async def transcribe(self, audio_path: str, language=None) -> str:
                return ""

            async def summarize(self, text: str, context=None) -> str:
                return ""

            def get_supported_languages(self) -> list[str]:
                return []

            def get_strategy_name(self) -> str:
                return "invalid"

            def is_available(self) -> bool:
                return False

        invalid_strategy = InvalidStrategy()
        config_info = invalid_strategy.get_configuration()

        # Verificar que configuração está incompleta
        assert "supports_transcription" not in config_info
        assert "supports_summarization" not in config_info
        assert "model" not in config_info

        # Estratégia deve reportar como não disponível
        assert invalid_strategy.is_available() is False

    @pytest.mark.asyncio
    async def test_concurrent_strategy_usage(self, mock_provider):
        """Testa uso concurrent de estratégias."""
        import asyncio

        # Executar múltiplas operações concorrentemente
        tasks = [
            mock_provider.transcribe(f"audio_{i}.wav")
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # Verificar que todas as operações foram bem-sucedidas
        assert len(results) == 5
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0
            assert "MockProvider" in result