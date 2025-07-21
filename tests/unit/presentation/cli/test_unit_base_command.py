"""
Testes unitários para a classe base Command.

Testa funcionalidades comuns de todos os comandos CLI,
incluindo tratamento de erros, logging, validação e parsing de argumentos.
"""

import sys
import pytest
import argparse
from unittest.mock import Mock, patch
import logging

from src.presentation.cli.base_command import Command, CommandMetadata, CommandFlag
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


class TestableCommand(Command):
    """Comando de teste para testar a classe base."""
    
    def _initialize_metadata(self):
        """Inicializa metadados do comando de teste."""
        self._metadata = CommandMetadata(
            name="test-command",
            description="Comando de teste para validação",
            usage="test-command [options]",
            examples=["test-command --input file.mp4", "test-command --help"],
            supported_formats=["mp4", "avi", "mkv"],
            category="test",
            aliases=["tc", "test"]
        )
        
        # Adicionar flags de teste
        self.add_flag(CommandFlag(
            name="input",
            short_name="i",
            description="Arquivo de entrada",
            type=str,
            required=True
        ))
        
        self.add_flag(CommandFlag(
            name="output",
            short_name="o",
            description="Arquivo de saída",
            type=str,
            default="output.txt"
        ))

    async def execute_from_parsed_args(self, args):
        """Executa comando com argumentos parseados."""
        return {
            "input": args.input,
            "output": args.output,
            "executed": True
        }

    async def execute(self, input_file="test.mp4", output_file="output.txt"):
        """Executa o comando de teste."""
        if not self.validate_args(input_file, output_file):
            raise InvalidVideoFormatError("input_file", input_file, "não pode estar vazio")
        return {"input": input_file, "output": output_file, "executed": True}

    def validate_args(self, input_file="", output_file=""):
        """Valida argumentos do comando de teste."""
        return bool(input_file and input_file.strip())


class TestableCommandWithError(Command):
    """Comando de teste que sempre gera erro."""
    
    def _initialize_metadata(self):
        """Inicializa metadados do comando de erro."""
        self._metadata = CommandMetadata(
            name="error-command",
            description="Comando que sempre falha"
        )

    async def execute_from_parsed_args(self, args):
        """Executa comando que sempre falha."""
        raise TranscriptionError("test_audio", "test.mp4", "Erro simulado para teste")

    async def execute(self):
        """Executa comando que sempre falha."""
        raise TranscriptionError("test_audio", "test.mp4", "Erro simulado para teste")

    def validate_args(self):
        """Sempre retorna False para teste."""
        return False


@pytest.fixture
def mock_config():
    """Fixture para configuração mockada."""
    config = Mock(spec=AlfredoConfig)
    config.default_provider = "groq"
    config.groq_model = "llama-3.3-70b-versatile"
    config.max_retries = 3
    config.timeout = 300
    return config


@pytest.fixture
def mock_factory():
    """Fixture para factory mockada."""
    factory = Mock(spec=InfrastructureFactory)
    factory.create_ai_provider.return_value = Mock()
    factory.create_video_downloader.return_value = Mock()
    factory.create_audio_extractor.return_value = Mock()
    factory.create_storage.return_value = Mock()
    return factory


@pytest.fixture
def testable_command(mock_config, mock_factory):
    """Fixture para comando testável."""
    return TestableCommand(mock_config, mock_factory)


@pytest.fixture
def error_command(mock_config, mock_factory):
    """Fixture para comando que gera erro."""
    return TestableCommandWithError(mock_config, mock_factory)


class TestCommandInitialization:
    """Testes de inicialização da classe Command."""

    def test_command_initialization_success(self, testable_command):
        """Testa inicialização bem-sucedida do comando."""
        assert testable_command.config is not None
        assert testable_command.factory is not None
        assert testable_command.logger is not None
        assert testable_command.error_formatter is not None
        assert testable_command._metadata is not None
        assert testable_command._parser is not None

    def test_command_metadata_initialization(self, testable_command):
        """Testa inicialização dos metadados."""
        metadata = testable_command.get_metadata()
        assert metadata.name == "test-command"
        assert metadata.description == "Comando de teste para validação"
        assert metadata.usage == "test-command [options]"
        assert len(metadata.examples) == 2
        assert len(metadata.supported_formats) == 3
        assert metadata.category == "test"

    def test_command_flags_initialization(self, testable_command):
        """Testa inicialização das flags."""
        assert len(testable_command._flags) == 2
        
        input_flag = next(f for f in testable_command._flags if f.name == "input")
        assert input_flag.short_name == "i"
        assert input_flag.required is True
        assert input_flag.type == str

    def test_command_parser_initialization(self, testable_command):
        """Testa inicialização do parser de argumentos."""
        assert testable_command._parser is not None
        assert testable_command._parser.prog == "test-command"


class TestCommandMetadata:
    """Testes de funcionalidades de metadados."""

    def test_get_metadata_success(self, testable_command):
        """Testa obtenção de metadados."""
        metadata = testable_command.get_metadata()
        assert isinstance(metadata, CommandMetadata)
        assert metadata.name == "test-command"

    def test_get_metadata_not_initialized(self, mock_config, mock_factory):
        """Testa erro quando metadados não são inicializados."""
        class UnInitializedCommand(Command):
            def _initialize_metadata(self):
                pass  # Não inicializa metadados
                
            async def execute_from_parsed_args(self, args):
                pass
                
            async def execute(self):
                pass
                
            def validate_args(self):
                pass

        command = UnInitializedCommand(mock_config, mock_factory)
        
        with pytest.raises(ConfigurationError) as exc_info:
            command.get_metadata()
        assert "não foram inicializados" in str(exc_info.value)

    def test_get_help_text_complete(self, testable_command):
        """Testa geração de texto de ajuda completo."""
        help_text = testable_command.get_help_text()
        
        assert "TEST-COMMAND" in help_text
        assert "Comando de teste para validação" in help_text
        assert "test-command [options]" in help_text
        assert "--input" in help_text
        assert "--output" in help_text
        assert "Flags disponíveis:" in help_text
        assert "Exemplos:" in help_text
        assert "Formatos suportados:" in help_text

    def test_get_command_info(self, testable_command):
        """Testa obtenção de informações do comando."""
        info = testable_command.get_command_info()
        
        assert info["name"] == "test-command"
        assert info["description"] == "Comando de teste para validação"
        assert info["category"] == "test"
        assert len(info["examples"]) == 2
        assert len(info["supported_formats"]) == 3
        assert "input" in info["flags"]
        assert "output" in info["flags"]


class TestArgumentParsing:
    """Testes de parsing de argumentos."""

    def test_parse_arguments_success(self, testable_command):
        """Testa parsing bem-sucedido de argumentos."""
        args = ["--input", "test.mp4", "--output", "result.json"]
        parsed = testable_command.parse_arguments(args)
        
        assert parsed.input == "test.mp4"
        assert parsed.output == "result.json"

    def test_parse_arguments_with_short_flags(self, testable_command):
        """Testa parsing com flags curtas."""
        args = ["-i", "test.mp4", "-o", "result.json"]
        parsed = testable_command.parse_arguments(args)
        
        assert parsed.input == "test.mp4"
        assert parsed.output == "result.json"

    def test_parse_arguments_with_defaults(self, testable_command):
        """Testa parsing com valores padrão."""
        args = ["--input", "test.mp4"]
        parsed = testable_command.parse_arguments(args)
        
        assert parsed.input == "test.mp4"
        assert parsed.output == "output.txt"  # Valor padrão

    def test_parse_arguments_missing_required(self, testable_command):
        """Testa erro com flag obrigatória ausente."""
        args = ["--output", "result.json"]
        
        with pytest.raises(SystemExit):
            testable_command.parse_arguments(args)

    def test_parse_arguments_no_parser(self, mock_config, mock_factory):
        """Testa erro quando parser não está configurado."""
        class NoParserCommand(Command):
            def _initialize_metadata(self):
                pass  # Não configura parser
                
            async def execute_from_parsed_args(self, args):
                pass
                
            async def execute(self):
                pass
                
            def validate_args(self):
                pass

        command = NoParserCommand(mock_config, mock_factory)
        
        with pytest.raises(ConfigurationError) as exc_info:
            command.parse_arguments(["--test"])
        assert "não foi configurado" in str(exc_info.value)


class TestCommandExecution:
    """Testes de execução de comandos."""

    @pytest.mark.asyncio
    async def test_execute_from_parsed_args_success(self, testable_command):
        """Testa execução com argumentos parseados."""
        args = argparse.Namespace(
            input="test.mp4",
            output="result.json"
        )
        
        result = await testable_command.execute_from_parsed_args(args)
        
        assert result["input"] == "test.mp4"
        assert result["output"] == "result.json"
        assert result["executed"] is True

    @pytest.mark.asyncio
    async def test_execute_with_args_success(self, testable_command):
        """Testa execução com argumentos da linha de comando."""
        args = ["--input", "test.mp4", "--output", "result.json"]
        
        result = await testable_command.execute_with_args(args)
        
        assert result["input"] == "test.mp4"
        assert result["output"] == "result.json"
        assert result["executed"] is True

    @pytest.mark.asyncio
    async def test_execute_with_args_invalid(self, testable_command):
        """Testa execução com argumentos inválidos."""
        args = ["--invalid-flag", "value"]
        
        result = await testable_command.execute_with_args(args)
        
        assert result is None  # SystemExit capturado

    @pytest.mark.asyncio
    async def test_execute_direct_success(self, testable_command):
        """Testa execução direta do comando."""
        result = await testable_command.execute(
            input_file="test.mp4",
            output_file="result.json"
        )
        
        assert result["input"] == "test.mp4"
        assert result["output"] == "result.json"
        assert result["executed"] is True

    @pytest.mark.asyncio
    async def test_execute_with_validation_failure(self, testable_command):
        """Testa execução com falha na validação."""
        with pytest.raises(InvalidVideoFormatError):
            await testable_command.execute(input_file="")  # Entrada inválida

    @pytest.mark.asyncio
    async def test_execute_with_error_handling(self, error_command):
        """Testa tratamento de erro durante execução."""
        args = []
        
        result = await error_command.execute_with_args(args)
        
        assert result is None  # Erro foi tratado


class TestArgumentValidation:
    """Testes de validação de argumentos."""

    def test_validate_args_success(self, testable_command):
        """Testa validação bem-sucedida."""
        result = testable_command.validate_args("test.mp4", "output.json")
        assert result is True

    def test_validate_args_empty_input(self, testable_command):
        """Testa validação com entrada vazia."""
        result = testable_command.validate_args("", "output.json")
        assert result is False

    def test_validate_parsed_args_default(self, testable_command):
        """Testa validação padrão de argumentos parseados."""
        args = argparse.Namespace(input="test.mp4", output="result.json")
        result = testable_command.validate_parsed_args(args)
        assert result is True  # Implementação padrão sempre retorna True


class TestErrorHandling:
    """Testes de tratamento de erros."""

    @patch('src.presentation.cli.base_command.ErrorDisplayFormatter')
    def test_handle_error_with_context(self, mock_formatter_class, testable_command):
        """Testa tratamento de erro com contexto."""
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        testable_command.error_formatter = mock_formatter
        
        error = TranscriptionError("test_audio", "test.mp4", "Erro de teste")
        context = {"operation": "test", "file": "test.mp4"}
        
        testable_command.handle_error(error, context)
        
        mock_formatter.display_error.assert_called_once_with(error, context)


class TestLogging:
    """Testes de funcionalidades de logging."""

    def test_log_execution_start(self, testable_command):
        """Testa log de início de execução."""
        from unittest.mock import ANY
        with patch.object(testable_command.logger, 'info') as mock_info:
            testable_command.log_execution_start("processamento", file="test.mp4")
            args, kwargs = mock_info.call_args
            assert args[0] == "🚀 Iniciando processamento"
            assert "extra" in kwargs
            assert kwargs["extra"]["file"] == "test.mp4"
            # Permite campos extras dinâmicos

    def test_log_execution_success(self, testable_command):
        """Testa log de sucesso de execução."""
        from unittest.mock import ANY
        with patch.object(testable_command.logger, 'info') as mock_info:
            testable_command.log_execution_success("transcrição", duration=120)
            args, kwargs = mock_info.call_args
            assert args[0] == "✅ transcrição concluído com sucesso"
            assert "extra" in kwargs
            assert kwargs["extra"]["duration"] == 120
            # Permite campos extras dinâmicos

    def test_log_execution_error(self, testable_command):
        """Testa log de erro de execução."""
        from unittest.mock import ANY
        with patch.object(testable_command.logger, 'error') as mock_error:
            error = TranscriptionError("test_audio", "test.mp4", "Erro de teste")
            testable_command.log_execution_error("transcrição", error, file="test.mp4")
            args, kwargs = mock_error.call_args
            assert args[0].startswith("❌ Erro em transcrição")
            assert "extra" in kwargs
            assert kwargs["extra"]["file"] == "test.mp4"
            assert kwargs["exc_info"] is True
            # Permite campos extras dinâmicos


class TestProgressAndDisplay:
    """Testes de exibição de progresso e resultados."""

    @patch('builtins.print')
    def test_display_progress_with_values(self, mock_print, testable_command):
        """Testa exibição de progresso com valores."""
        testable_command.display_progress("Processando", 50, 100)
        
        mock_print.assert_called_once_with("⏳ Processando (50/100 - 50.0%)")

    @patch('builtins.print')
    def test_display_progress_without_values(self, mock_print, testable_command):
        """Testa exibição de progresso sem valores."""
        testable_command.display_progress("Processando")
        
        mock_print.assert_called_once_with("⏳ Processando")

    @patch('builtins.print')
    def test_display_result_with_transcription(self, mock_print, testable_command):
        """Testa exibição de resultado com transcrição."""
        result = Mock()
        result.transcription = "Esta é uma transcrição de teste"
        result.summary = "Este é um resumo de teste"
        result.file_path = "/path/to/result.json"

        testable_command.display_result(result, "processamento")

        trans_count = len(result.transcription)
        summary_count = len(result.summary)
        expected_calls = [
            (("✅ processamento concluído com sucesso",),),
            ((f"📝 Transcrição: {trans_count} caracteres",),),
            ((f"📋 Resumo: {summary_count} caracteres",),),
            (("💾 Salvo em: /path/to/result.json",),)
        ]

        assert mock_print.call_count == 4
        for i, expected_call in enumerate(expected_calls):
            assert mock_print.call_args_list[i] == expected_call

    @patch('builtins.print')
    def test_display_result_simple(self, mock_print, testable_command):
        """Testa exibição de resultado simples."""
        result = {"status": "success"}
        
        testable_command.display_result(result, "operação")
        
        mock_print.assert_called_once_with("✅ operação concluído com sucesso")


class TestCommandFlags:
    """Testes de funcionalidades de flags."""

    def test_add_flag_success(self, testable_command):
        """Testa adição de flag com sucesso."""
        initial_count = len(testable_command._flags)
        
        new_flag = CommandFlag(
            name="verbose",
            short_name="v",
            description="Modo verboso",
            type=bool,
            default=False
        )
        
        testable_command.add_flag(new_flag)
        
        assert len(testable_command._flags) == initial_count + 1
        assert any(f.name == "verbose" for f in testable_command._flags)

    def test_required_flag(self, testable_command):
        """Testa flag obrigatória."""
        input_flag = next(f for f in testable_command._flags if f.name == "input")
        assert input_flag.required is True
if __name__ == "__main__":
    pytest.main([__file__, "-v"])