"""
Testes para a classe base Command.

Testa funcionalidades comuns de todos os comandos CLI,
incluindo tratamento de erros, logging e validação.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import logging

from src.presentation.cli.base_command import Command
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
    ProviderUnavailableError,
    AlfredoError
)


class TestCommand(Command):
    """Comando de teste para testar a classe base."""
    
    def _initialize_metadata(self) -> None:
        """Inicializa metadados do comando de teste."""
        from src.presentation.cli.base_command import CommandMetadata
        self._metadata = CommandMetadata(
            name="test",
            description="Test command",
            usage="test [options]",
            category="test"
        )
    
    async def execute(self, *args, **kwargs):
        """Implementação de teste."""
        return "test_result"
    
    def validate_args(self, *args, **kwargs):
        """Validação de teste."""
        return kwargs.get('valid', True)


class TestBaseCommand:
    """Testes para a classe base Command."""

    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        config = Mock(spec=AlfredoConfig)
        config.log_level = "INFO"
        config.log_format = "%(message)s"
        config.data_dir = Mock()
        config.data_dir.__truediv__ = Mock(return_value=Mock())
        return config

    @pytest.fixture
    def mock_factory(self):
        """Mock da factory."""
        return Mock(spec=InfrastructureFactory)

    @pytest.fixture
    def command(self, mock_config, mock_factory):
        """Instância de comando para testes."""
        return TestCommand(mock_config, mock_factory)

    def test_command_initialization(self, mock_config, mock_factory):
        """Testa inicialização do comando."""
        command = TestCommand(mock_config, mock_factory)
        
        assert command.config == mock_config
        assert command.factory == mock_factory
        assert isinstance(command.logger, logging.LoggerAdapter)
        assert hasattr(command, 'error_formatter')

    def test_validate_args_success(self, command):
        """Testa validação de argumentos bem-sucedida."""
        result = command.validate_args(valid=True)
        assert result is True

    def test_validate_args_failure(self, command):
        """Testa validação de argumentos com falha."""
        result = command.validate_args(valid=False)
        assert result is False

    @pytest.mark.asyncio
    async def test_execute_success(self, command):
        """Testa execução bem-sucedida."""
        result = await command.execute()
        assert result == "test_result"

    @patch('builtins.print')
    def test_handle_download_error(self, mock_print, command):
        """Testa tratamento de erro de download."""
        error = DownloadFailedError(
            url="https://test.com",
            reason="Test error",
            http_code=404
        )
        error.url = "https://test.com"
        error.reason = "Test error"
        error.http_code = 404
        
        command.handle_error(error)
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_handle_transcription_error(self, mock_print, command):
        """Testa tratamento de erro de transcrição."""
        error = TranscriptionError(
            audio_path="/test/audio.wav",
            reason="Test error",
            provider="TestProvider"
        )
        error.audio_path = "/test/audio.wav"
        error.provider = "TestProvider"
        
        command.handle_error(error)
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_handle_configuration_error(self, mock_print, command):
        """Testa tratamento de erro de configuração."""
        error = ConfigurationError(
            config_key="test_key",
            reason="Test error",
            expected="test_value"
        )
        error.config_key = "test_key"
        error.expected = "test_value"
        
        command.handle_error(error)
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_handle_validation_error(self, mock_print, command):
        """Testa tratamento de erro de validação."""
        error = InvalidVideoFormatError(
            field="test_field",
            value="test_value",
            constraint="test_constraint"
        )
        error.field = "test_field"
        error.value = "test_value"
        error.constraint = "test_constraint"
        
        command.handle_error(error)
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_handle_provider_error(self, mock_print, command):
        """Testa tratamento de erro de provedor."""
        error = ProviderUnavailableError(
            provider_name="TestProvider",
            reason="Test error"
        )
        error.provider_name = "TestProvider"
        error.reason = "Test error"
        
        command.handle_error(error)
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_handle_generic_alfredo_error(self, mock_print, command):
        """Testa tratamento de erro genérico do Alfredo."""
        error = AlfredoError("Test error", details={"key": "value"})
        
        command.handle_error(error)
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_handle_unexpected_error(self, mock_print, command):
        """Testa tratamento de erro inesperado."""
        error = ValueError("Unexpected error")
        
        command.handle_error(error)
        mock_print.assert_called_once()

    def test_log_execution_start(self, command):
        """Testa logging de início de execução."""
        with patch.object(command.logger, 'info') as mock_log:
            command.log_execution_start("test operation", key="value")
            mock_log.assert_called_once()

    def test_log_execution_success(self, command):
        """Testa logging de sucesso."""
        with patch.object(command.logger, 'info') as mock_log:
            command.log_execution_success("test operation", key="value")
            mock_log.assert_called_once()

    def test_log_execution_error(self, command):
        """Testa logging de erro."""
        with patch.object(command.logger, 'error') as mock_log:
            error = Exception("Test error")
            command.log_execution_error("test operation", error, key="value")
            mock_log.assert_called_once()

    @patch('builtins.print')
    def test_display_progress(self, mock_print, command):
        """Testa exibição de progresso."""
        command.display_progress("Test message", 50, 100)
        mock_print.assert_called_with("⏳ Test message (50/100 - 50.0%)")

    @patch('builtins.print')
    def test_display_progress_without_numbers(self, mock_print, command):
        """Testa exibição de progresso sem números."""
        command.display_progress("Test message")
        mock_print.assert_called_with("⏳ Test message")

    @patch('builtins.print')
    def test_display_result(self, mock_print, command):
        """Testa exibição de resultado."""
        result = Mock()
        result.transcription = "Test transcription"
        result.summary = "Test summary"
        result.file_path = "/test/path"
        
        command.display_result(result, "test operation")
        
        # Verificar se print foi chamado múltiplas vezes
        assert mock_print.call_count >= 1

    def test_get_command_info(self, command):
        """Testa obtenção de informações do comando."""
        info = command.get_command_info()
        
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'description' in info
        assert 'class' in info
        assert info['class'] == 'TestCommand'