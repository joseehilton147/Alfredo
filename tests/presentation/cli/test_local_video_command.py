"""
Testes para o LocalVideoCommand.

Testa funcionalidades específicas do comando de processamento
de arquivos de vídeo locais, incluindo validação de arquivos
e diferentes formatos.
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock, mock_open
from pathlib import Path

from src.presentation.cli.local_video_command import LocalVideoCommand
from src.application.use_cases.process_local_video import (
    ProcessLocalVideoRequest,
    ProcessLocalVideoResponse
)
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


class TestLocalVideoCommand:
    """Testes para o comando de vídeo local."""

    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        config = Mock(spec=AlfredoConfig)
        config.log_level = "INFO"
        config.log_format = "%(message)s"
        config.data_dir = Path("/test/data")
        config.temp_dir = Path("/test/temp")
        config.max_file_size_mb = 500
        return config

    @pytest.fixture
    def mock_factory(self):
        """Mock da factory."""
        factory = Mock(spec=InfrastructureFactory)
        factory.create_audio_extractor.return_value = Mock()
        factory.create_ai_provider.return_value = Mock()
        factory.create_storage.return_value = Mock()
        return factory

    @pytest.fixture
    def local_command(self, mock_config, mock_factory):
        """Instância do comando de vídeo local para testes."""
        return LocalVideoCommand(mock_config, mock_factory)

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    @patch('os.access')
    def test_validate_args_valid_file(self, mock_access, mock_stat, mock_is_file, 
                                     mock_exists, local_command):
        """Testa validação com arquivo válido."""
        # Setup mocks
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value.st_size = 100 * 1024 * 1024  # 100MB
        mock_access.return_value = True
        
        result = local_command.validate_args("/test/video.mp4")
        assert result is True

    @patch('builtins.print')
    def test_validate_args_empty_path(self, mock_print, local_command):
        """Testa validação com caminho vazio."""
        result = local_command.validate_args("")
        assert result is False
        mock_print.assert_called()

    @patch('pathlib.Path.exists')
    @patch('builtins.print')
    def test_validate_args_file_not_found(self, mock_print, mock_exists, local_command):
        """Testa validação com arquivo não encontrado."""
        mock_exists.return_value = False
        
        result = local_command.validate_args("/test/nonexistent.mp4")
        assert result is False
        mock_print.assert_called()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('builtins.print')
    def test_validate_args_is_directory(self, mock_print, mock_is_file, 
                                       mock_exists, local_command):
        """Testa validação com diretório em vez de arquivo."""
        mock_exists.return_value = True
        mock_is_file.return_value = False
        
        result = local_command.validate_args("/test/directory")
        assert result is False
        mock_print.assert_called()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('builtins.print')
    def test_validate_args_unsupported_format(self, mock_print, mock_is_file, 
                                             mock_exists, local_command):
        """Testa validação com formato não suportado."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        result = local_command.validate_args("/test/document.txt")
        assert result is False
        mock_print.assert_called()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    @patch('builtins.print')
    def test_validate_args_file_too_large(self, mock_print, mock_stat, mock_is_file, 
                                         mock_exists, local_command):
        """Testa validação com arquivo muito grande."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value.st_size = 600 * 1024 * 1024  # 600MB (> 500MB limit)
        
        result = local_command.validate_args("/test/large_video.mp4")
        assert result is False
        mock_print.assert_called()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    @patch('os.access')
    @patch('builtins.print')
    def test_validate_args_no_read_permission(self, mock_print, mock_access, mock_stat, 
                                             mock_is_file, mock_exists, local_command):
        """Testa validação sem permissão de leitura."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value.st_size = 100 * 1024 * 1024
        mock_access.return_value = False
        
        result = local_command.validate_args("/test/no_permission.mp4")
        assert result is False
        mock_print.assert_called()

    def test_validate_args_supported_formats(self, local_command):
        """Testa validação com todos os formatos suportados."""
        supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', 
                           '.flv', '.webm', '.m4v', '.3gp', '.ogv']
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('os.access', return_value=True):
            
            mock_stat.return_value.st_size = 100 * 1024 * 1024
            
            for fmt in supported_formats:
                result = local_command.validate_args(f"/test/video{fmt}")
                assert result is True, f"Format {fmt} should be supported"

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.stat')
    @patch('os.access')
    @patch('builtins.print')
    def test_validate_args_invalid_language(self, mock_print, mock_access, mock_stat, 
                                           mock_is_file, mock_exists, local_command):
        """Testa validação com idioma inválido."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_stat.return_value.st_size = 100 * 1024 * 1024
        mock_access.return_value = True
        
        result = local_command.validate_args("/test/video.mp4", language="invalid")
        assert result is False
        mock_print.assert_called()

    @pytest.mark.asyncio
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    @patch('pathlib.Path.stat')
    @patch('os.access', return_value=True)
    @patch('src.presentation.cli.local_video_command.tqdm')
    async def test_execute_success(self, mock_tqdm, mock_access, mock_stat, 
                                  mock_is_file, mock_exists, local_command):
        """Testa execução bem-sucedida."""
        # Setup mocks
        mock_stat.return_value.st_size = 100 * 1024 * 1024
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        # Mock do use case
        mock_use_case = AsyncMock()
        mock_video = Video(
            id="test_id",
            title="test_video.mp4",
            file_path="/test/video.mp4"
        )
        mock_response = ProcessLocalVideoResponse(
            video=mock_video,
            transcription="Test transcription",
            was_cached=False
        )
        mock_use_case.execute.return_value = mock_response
        
        with patch('src.presentation.cli.local_video_command.ProcessLocalVideoUseCase') as mock_use_case_class:
            mock_use_case_class.return_value = mock_use_case
            
            result = await local_command.execute(file_path="/test/video.mp4")
            
            assert result == mock_response
            mock_use_case.execute.assert_called_once()
            mock_progress.close.assert_called()

    @pytest.mark.asyncio
    async def test_execute_invalid_args(self, local_command):
        """Testa execução com argumentos inválidos."""
        with pytest.raises(InvalidVideoFormatError):
            await local_command.execute(file_path="")

    @pytest.mark.asyncio
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    @patch('pathlib.Path.stat')
    @patch('os.access', return_value=True)
    @patch('src.presentation.cli.local_video_command.tqdm')
    async def test_execute_keyboard_interrupt(self, mock_tqdm, mock_access, mock_stat, 
                                             mock_is_file, mock_exists, local_command):
        """Testa execução interrompida pelo usuário."""
        mock_stat.return_value.st_size = 100 * 1024 * 1024
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = KeyboardInterrupt()
        mock_use_case.cancel_processing = AsyncMock()
        
        with patch('src.presentation.cli.local_video_command.ProcessLocalVideoUseCase') as mock_use_case_class:
            mock_use_case_class.return_value = mock_use_case
            
            with pytest.raises(TranscriptionError):
                await local_command.execute(file_path="/test/video.mp4")
            
            mock_use_case.cancel_processing.assert_called_once()
            mock_progress.close.assert_called()

    def test_update_progress(self, local_command):
        """Testa atualização de progresso."""
        mock_progress = Mock()
        local_command._progress_bar = mock_progress
        
        local_command._update_progress(75, "Test message")
        
        assert mock_progress.n == 75
        mock_progress.set_description.assert_called_with("🎬 Test message")
        mock_progress.refresh.assert_called_once()

    @patch('builtins.print')
    def test_display_local_video_result(self, mock_print, local_command):
        """Testa exibição de resultado de vídeo local."""
        mock_video = Video(
            id="test_id",
            title="test_video.mp4",
            file_path="/test/video.mp4",
            duration=180,
            metadata={
                'file_size': 100 * 1024 * 1024,
                'file_extension': '.mp4'
            }
        )
        mock_response = ProcessLocalVideoResponse(
            video=mock_video,
            transcription="Test transcription",
            was_cached=False
        )
        
        local_command._display_local_video_result(mock_response)
        
        # Verificar se print foi chamado múltiplas vezes
        assert mock_print.call_count >= 5

    @patch('builtins.print')
    def test_display_local_video_result_cached(self, mock_print, local_command):
        """Testa exibição de resultado em cache."""
        mock_video = Video(
            id="test_id",
            title="test_video.mp4",
            file_path="/test/video.mp4"
        )
        mock_response = ProcessLocalVideoResponse(
            video=mock_video,
            transcription="Test transcription",
            was_cached=True
        )
        
        local_command._display_local_video_result(mock_response)
        
        # Verificar se menciona cache
        calls = [str(call) for call in mock_print.call_args_list]
        cache_mentioned = any("cache" in call.lower() for call in calls)
        assert cache_mentioned

    def test_get_supported_formats(self, local_command):
        """Testa obtenção de formatos suportados."""
        formats = local_command.get_supported_formats()
        
        assert isinstance(formats, dict)
        assert '.mp4' in formats
        assert '.avi' in formats
        assert len(formats) > 5

    def test_get_command_info(self, local_command):
        """Testa obtenção de informações do comando."""
        info = local_command.get_command_info()
        
        assert info['name'] == 'local'
        assert 'description' in info
        assert 'usage' in info
        assert 'supported_formats' in info
        assert 'examples' in info
        assert isinstance(info['examples'], list)
        assert len(info['examples']) > 0