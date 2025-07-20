"""
Testes para Comportamento Polimórfico das Interfaces.

Valida que diferentes implementações podem ser usadas de forma intercambiável
através das interfaces definidas.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from abc import ABC, abstractmethod

from src.application.interfaces.ai_strategy import AIStrategy
from src.presentation.cli.base_command import Command, CommandMetadata
from src.application.gateways.storage_gateway import StorageGateway
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway


class TestPolymorphicBehavior:
    """Testes para comportamento polimórfico das interfaces."""

    def test_ai_strategy_polymorphism(self):
        """Testa polimorfismo da interface AIStrategy."""
        # Criar diferentes implementações mock
        implementations = []
        
        for name in ["whisper", "groq", "ollama", "custom"]:
            impl = Mock(spec=AIStrategy)
            impl.get_strategy_name.return_value = name
            impl.is_available.return_value = True
            impl.get_supported_languages.return_value = ["pt", "en"]
            impl.get_configuration.return_value = {
                "model": f"{name}-model",
                "supports_transcription": True,
                "supports_summarization": name != "whisper"  # Whisper só transcrição
            }
            impl.transcribe = AsyncMock(return_value=f"Transcrição {name}")
            impl.summarize = AsyncMock(return_value=f"Resumo {name}")
            
            implementations.append(impl)
        
        # Função que usa qualquer implementação de AIStrategy
        async def process_with_any_strategy(strategy: AIStrategy, audio_path: str, text: str):
            # Deve funcionar com qualquer implementação
            name = strategy.get_strategy_name()
            available = strategy.is_available()
            languages = strategy.get_supported_languages()
            config = strategy.get_configuration()
            
            transcription = await strategy.transcribe(audio_path)
            summary = await strategy.summarize(text)
            
            return {
                "name": name,
                "available": available,
                "languages": languages,
                "config": config,
                "transcription": transcription,
                "summary": summary
            }
        
        # Testar com todas as implementações
        import asyncio
        
        async def test_all():
            results = []
            for impl in implementations:
                result = await process_with_any_strategy(impl, "test.wav", "texto")
                results.append(result)
            return results
        
        results = asyncio.run(test_all())
        
        # Verificar que todas funcionaram
        assert len(results) == 4
        for i, result in enumerate(results):
            expected_name = ["whisper", "groq", "ollama", "custom"][i]
            assert result["name"] == expected_name
            assert result["available"] is True
            assert "pt" in result["languages"]
            assert expected_name in result["transcription"]
            assert expected_name in result["summary"]

    def test_command_polymorphism(self):
        """Testa polimorfismo da interface Command."""
        # Criar diferentes implementações de comando
        commands = []
        
        for name in ["youtube", "local", "batch", "custom"]:
            cmd = Mock(spec=Command)
            cmd.get_metadata.return_value = CommandMetadata(
                name=name,
                description=f"Comando {name}",
                category="video" if name != "custom" else "test"
            )
            cmd.get_command_info.return_value = {
                "name": name,
                "description": f"Comando {name}",
                "category": "video" if name != "custom" else "test"
            }
            cmd.get_help_text.return_value = f"Help do comando {name}"
            cmd.execute_from_parsed_args = AsyncMock(return_value={"command": name, "status": "success"})
            cmd.validate_parsed_args.return_value = True
            
            commands.append(cmd)
        
        # Função que usa qualquer comando
        async def execute_any_command(command: Command, args):
            # Deve funcionar com qualquer implementação
            metadata = command.get_metadata()
            info = command.get_command_info()
            help_text = command.get_help_text()
            
            is_valid = command.validate_parsed_args(args)
            if is_valid:
                result = await command.execute_from_parsed_args(args)
            else:
                result = {"error": "Invalid args"}
            
            return {
                "metadata": metadata,
                "info": info,
                "help": help_text,
                "valid": is_valid,
                "result": result
            }
        
        # Testar com todos os comandos
        import asyncio
        
        async def test_all_commands():
            results = []
            for cmd in commands:
                result = await execute_any_command(cmd, Mock())
                results.append(result)
            return results
        
        results = asyncio.run(test_all_commands())
        
        # Verificar que todos funcionaram
        assert len(results) == 4
        for i, result in enumerate(results):
            expected_name = ["youtube", "local", "batch", "custom"][i]
            assert result["metadata"].name == expected_name
            assert result["info"]["name"] == expected_name
            assert expected_name in result["help"]
            assert result["valid"] is True
            assert result["result"]["command"] == expected_name

    def test_gateway_polymorphism(self):
        """Testa polimorfismo das interfaces Gateway."""
        # Testar StorageGateway
        storage_impls = []
        
        for name in ["filesystem", "database", "cloud"]:
            impl = Mock(spec=StorageGateway)
            impl.save_video = AsyncMock(return_value=f"Saved to {name}")
            impl.load_video = AsyncMock(return_value=f"Loaded from {name}")
            impl.save_transcription = AsyncMock(return_value=f"Transcription saved to {name}")
            impl.load_transcription = AsyncMock(return_value=f"Transcription from {name}")
            
            storage_impls.append((name, impl))
        
        # Função que usa qualquer storage
        async def use_any_storage(storage: StorageGateway, video_data, transcription_data):
            save_result = await storage.save_video(video_data)
            load_result = await storage.load_video("video_id")
            save_trans = await storage.save_transcription("video_id", transcription_data)
            load_trans = await storage.load_transcription("video_id")
            
            return {
                "save_video": save_result,
                "load_video": load_result,
                "save_transcription": save_trans,
                "load_transcription": load_trans
            }
        
        # Testar com todas as implementações
        import asyncio
        
        async def test_all_storages():
            results = []
            for name, impl in storage_impls:
                result = await use_any_storage(impl, "video_data", "transcription_data")
                results.append((name, result))
            return results
        
        results = asyncio.run(test_all_storages())
        
        # Verificar que todas funcionaram
        assert len(results) == 3
        for name, result in results:
            assert name in result["save_video"]
            assert name in result["load_video"]
            assert name in result["save_transcription"]
            assert name in result["load_transcription"]

    def test_interface_contract_enforcement(self):
        """Testa que interfaces enforçam contratos."""
        # Tentar criar implementação incompleta
        class IncompleteStrategy(AIStrategy):
            # Faltam métodos obrigatórios
            pass
        
        # Deve falhar ao tentar instanciar
        with pytest.raises(TypeError):
            IncompleteStrategy()

    def test_liskov_substitution_principle(self):
        """Testa Princípio da Substituição de Liskov."""
        # Criar implementações que devem ser substituíveis
        class BaseStrategy(AIStrategy):
            async def transcribe(self, audio_path: str, language=None) -> str:
                return "Base transcription"
            
            async def summarize(self, text: str, context=None) -> str:
                return "Base summary"
            
            def get_supported_languages(self) -> list[str]:
                return ["pt"]
            
            def get_strategy_name(self) -> str:
                return "base"
            
            def get_configuration(self) -> dict:
                return {"supports_transcription": True, "supports_summarization": True}
            
            def is_available(self) -> bool:
                return True
        
        class EnhancedStrategy(BaseStrategy):
            async def transcribe(self, audio_path: str, language=None) -> str:
                # Comportamento aprimorado mas compatível
                base_result = await super().transcribe(audio_path, language)
                return f"Enhanced: {base_result}"
            
            def get_strategy_name(self) -> str:
                return "enhanced"
        
        # Função que espera BaseStrategy
        async def use_base_strategy(strategy: BaseStrategy):
            return await strategy.transcribe("test.wav")
        
        # Deve funcionar com ambas as implementações
        import asyncio
        
        base = BaseStrategy()
        enhanced = EnhancedStrategy()
        
        base_result = asyncio.run(use_base_strategy(base))
        enhanced_result = asyncio.run(use_base_strategy(enhanced))
        
        assert "Base transcription" in base_result
        assert "Enhanced: Base transcription" in enhanced_result

    def test_interface_segregation_principle(self):
        """Testa Princípio da Segregação de Interface."""
        # Interfaces devem ser específicas para cada necessidade
        
        # Interface específica para transcrição
        class TranscriptionOnlyInterface(ABC):
            @abstractmethod
            async def transcribe(self, audio_path: str, language=None) -> str:
                pass
        
        # Interface específica para sumarização
        class SummarizationOnlyInterface(ABC):
            @abstractmethod
            async def summarize(self, text: str, context=None) -> str:
                pass
        
        # Implementação que só faz transcrição
        class TranscriptionOnlyProvider(TranscriptionOnlyInterface):
            async def transcribe(self, audio_path: str, language=None) -> str:
                return "Transcription only"
        
        # Implementação que só faz sumarização
        class SummarizationOnlyProvider(SummarizationOnlyInterface):
            async def summarize(self, text: str, context=None) -> str:
                return "Summarization only"
        
        # Clientes específicos
        async def transcription_client(provider: TranscriptionOnlyInterface):
            return await provider.transcribe("test.wav")
        
        async def summarization_client(provider: SummarizationOnlyInterface):
            return await provider.summarize("test text")
        
        # Testar que cada cliente usa apenas sua interface
        import asyncio
        
        trans_provider = TranscriptionOnlyProvider()
        summ_provider = SummarizationOnlyProvider()
        
        trans_result = asyncio.run(transcription_client(trans_provider))
        summ_result = asyncio.run(summarization_client(summ_provider))
        
        assert trans_result == "Transcription only"
        assert summ_result == "Summarization only"

    def test_dependency_inversion_principle(self):
        """Testa Princípio da Inversão de Dependência."""
        # Classe de alto nível que depende de abstração
        class VideoProcessor:
            def __init__(self, ai_strategy: AIStrategy, storage: StorageGateway):
                self._ai_strategy = ai_strategy  # Depende da abstração
                self._storage = storage          # Depende da abstração
            
            async def process(self, audio_path: str, video_id: str):
                transcription = await self._ai_strategy.transcribe(audio_path)
                await self._storage.save_transcription(video_id, transcription)
                return transcription
        
        # Implementações concretas
        ai_mock = Mock(spec=AIStrategy)
        ai_mock.transcribe = AsyncMock(return_value="Test transcription")
        
        storage_mock = Mock(spec=StorageGateway)
        storage_mock.save_transcription = AsyncMock()
        
        # Injetar dependências (inversão)
        processor = VideoProcessor(ai_mock, storage_mock)
        
        # Testar que funciona
        import asyncio
        result = asyncio.run(processor.process("test.wav", "video_123"))
        
        assert result == "Test transcription"
        ai_mock.transcribe.assert_called_once_with("test.wav")
        storage_mock.save_transcription.assert_called_once_with("video_123", "Test transcription")

    def test_open_closed_principle(self):
        """Testa Princípio Aberto/Fechado."""
        # Classe base fechada para modificação
        class BaseProcessor:
            def __init__(self, strategy: AIStrategy):
                self._strategy = strategy
            
            async def process(self, audio_path: str):
                return await self._strategy.transcribe(audio_path)
        
        # Extensão sem modificar a classe base
        class EnhancedProcessor(BaseProcessor):
            async def process(self, audio_path: str):
                # Adiciona funcionalidade sem modificar a base
                result = await super().process(audio_path)
                return f"Enhanced: {result}"
        
        # Testar ambas as implementações
        strategy_mock = Mock(spec=AIStrategy)
        strategy_mock.transcribe = AsyncMock(return_value="Base result")
        
        import asyncio
        
        base_processor = BaseProcessor(strategy_mock)
        enhanced_processor = EnhancedProcessor(strategy_mock)
        
        base_result = asyncio.run(base_processor.process("test.wav"))
        enhanced_result = asyncio.run(enhanced_processor.process("test.wav"))
        
        assert base_result == "Base result"
        assert enhanced_result == "Enhanced: Base result"

    def test_runtime_polymorphism(self):
        """Testa polimorfismo em tempo de execução."""
        # Lista de diferentes implementações
        strategies = []
        
        for i in range(3):
            strategy = Mock(spec=AIStrategy)
            strategy.get_strategy_name.return_value = f"strategy_{i}"
            strategy.transcribe = AsyncMock(return_value=f"Result {i}")
            strategies.append(strategy)
        
        # Função que escolhe estratégia em runtime
        def choose_strategy(index: int) -> AIStrategy:
            return strategies[index]
        
        # Usar diferentes estratégias em runtime
        import asyncio
        
        async def test_runtime():
            results = []
            for i in range(3):
                strategy = choose_strategy(i)  # Escolha em runtime
                result = await strategy.transcribe("test.wav")
                results.append(result)
            return results
        
        results = asyncio.run(test_runtime())
        
        assert results == ["Result 0", "Result 1", "Result 2"]

    def test_interface_evolution_compatibility(self):
        """Testa compatibilidade na evolução de interfaces."""
        # Interface original
        class OriginalInterface(ABC):
            @abstractmethod
            async def process(self, data: str) -> str:
                pass
        
        # Interface evoluída (com novos métodos opcionais)
        class EvolvedInterface(OriginalInterface):
            async def advanced_process(self, data: str, options: dict = None) -> str:
                # Método padrão que usa o método original
                return await self.process(data)
        
        # Implementação antiga (só implementa interface original)
        class LegacyImplementation(OriginalInterface):
            async def process(self, data: str) -> str:
                return f"Legacy: {data}"
        
        # Implementação nova (implementa interface evoluída)
        class ModernImplementation(EvolvedInterface):
            async def process(self, data: str) -> str:
                return f"Modern: {data}"
            
            async def advanced_process(self, data: str, options: dict = None) -> str:
                base = await self.process(data)
                if options:
                    return f"{base} with options"
                return base
        
        # Testar compatibilidade
        import asyncio
        
        legacy = LegacyImplementation()
        modern = ModernImplementation()
        
        # Ambas devem funcionar com interface original
        legacy_result = asyncio.run(legacy.process("test"))
        modern_result = asyncio.run(modern.process("test"))
        
        assert legacy_result == "Legacy: test"
        assert modern_result == "Modern: test"
        
        # Implementação moderna deve ter funcionalidade adicional
        advanced_result = asyncio.run(modern.advanced_process("test", {"enhanced": True}))
        assert "with options" in advanced_result