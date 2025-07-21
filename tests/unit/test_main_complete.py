"""
Testes completos para src.main para aumentar cobertura substancialmente.

Testa todas as funções e cenários do ponto de entrada principal
incluindo parsing de argumentos, configuração e execução de comandos.
"""

import pytest
import asyncio
import argparse
import sys
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path

from src.main import main
from src.domain.exceptions.alfredo_errors import (
    AlfredoError, DownloadFailedError, ConfigurationError
)
from src.config.validators import ValidationError


class TestMainFunctionComplete:
    """Testes completos para função main."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock da configuração."""
        config = Mock()
        config.data_dir = Path("/tmp/alfredo")
        config.validate_runtime = Mock()
        config.create_directory_structure = Mock()
        return config
    
    @pytest.fixture
    def mock_factory(self):
        """Mock da factory."""
        return Mock()
    
    @pytest.fixture
    def mock_registry(self):
        """Mock do registry."""
        registry = Mock()
        command = Mock()
        command.execute = AsyncMock()
        registry.get_command.return_value = command
        return registry, command
    
    @pytest.fixture
    def mock_all_dependencies(self, mock_config, mock_factory, mock_registry):
        """Mock de todas as dependências principais."""
        registry, command = mock_registry
        with patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging'), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=registry):
            yield {
                'config': mock_config,
                'factory': mock_factory, 
                'registry': registry,
                'command': command
            }
    
    @pytest.mark.asyncio
    async def test_main_no_arguments_shows_help(self, mock_all_dependencies):
        """Testa main sem argumentos mostra help."""
        with patch.object(sys, 'argv', ['alfredo']), \
             patch('argparse.ArgumentParser.print_help') as mock_help:
            
            await main()
            
            mock_help.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_youtube_command_success(self, mock_all_dependencies):
        """Testa execução bem-sucedida do comando YouTube."""
        with patch.object(sys, 'argv', [
            'alfredo', 'youtube', 'https://youtube.com/watch?v=test',
            '--language', 'pt', '--quality', 'high', '--force'
        ]):
            await main()
            
            command = mock_all_dependencies['command']
            command.execute.assert_called_once_with(
                url='https://youtube.com/watch?v=test',
                language='pt',
                quality='high',
                force_reprocess=True
            )
    
    @pytest.mark.asyncio
    async def test_main_local_command_success(self, mock_all_dependencies):
        """Testa execução bem-sucedida do comando local."""
        with patch.object(sys, 'argv', [
            'alfredo', 'local', '/path/to/video.mp4',
            '--language', 'en', '--force'
        ]):
            await main()
            
            command = mock_all_dependencies['command']
            command.execute.assert_called_once_with(
                file_path='/path/to/video.mp4',
                language='en',
                force_reprocess=True
            )
    
    @pytest.mark.asyncio
    async def test_main_batch_command_success(self, mock_all_dependencies):
        """Testa execução bem-sucedida do comando batch."""
        with patch.object(sys, 'argv', [
            'alfredo', 'batch', '/path/to/videos',
            '--language', 'pt', '--recursive', '--max-workers', '4', '--force'
        ]):
            await main()
            
            command = mock_all_dependencies['command']
            command.execute.assert_called_once_with(
                directory='/path/to/videos',
                language='pt',
                recursive=True,
                max_workers=4,
                force_reprocess=True
            )
    
    @pytest.mark.asyncio
    async def test_main_with_verbose_flag(self, mock_all_dependencies):
        """Testa execução com flag verbose."""
        with patch.object(sys, 'argv', [
            'alfredo', 'youtube', 'https://youtube.com/test', '--verbose'
        ]), \
             patch('src.main.setup_structured_logging') as mock_logging:
            
            await main()
            
            # Verifica se logging foi configurado com DEBUG
            mock_logging.assert_called_once()
            args, kwargs = mock_logging.call_args
            # Verifica se level foi passado e se é DEBUG (10)
            assert 'level' in kwargs and kwargs['level'] == 10
    
    @pytest.mark.asyncio
    async def test_main_without_verbose_flag(self, mock_all_dependencies):
        """Testa execução sem flag verbose."""
        with patch.object(sys, 'argv', [
            'alfredo', 'youtube', 'https://youtube.com/test'
        ]), \
             patch('src.main.setup_structured_logging') as mock_logging:
            
            await main()
            
            # Verifica se logging foi configurado com INFO
            mock_logging.assert_called_once()
            args, kwargs = mock_logging.call_args
            # Verifica se level foi passado e se é INFO (20)
            assert 'level' in kwargs and kwargs['level'] == 20


class TestMainConfigurationAndValidation:
    """Testes para configuração e validação no main."""
    
    @pytest.mark.asyncio
    async def test_validation_error_during_ffmpeg_check(self):
        """Testa erro de validação do ffmpeg."""
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.AlfredoConfig'), \
             patch('src.main.validate_ffmpeg', side_effect=ValidationError("FFmpeg não encontrado")), \
             patch('builtins.print') as mock_print, \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 2
        mock_print.assert_called_with("❌ Erro de configuração/ambiente: FFmpeg não encontrado")
    
    @pytest.mark.asyncio
    async def test_validation_error_during_ai_providers_check(self):
        """Testa erro de validação dos providers AI."""
        mock_config = Mock()
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers', 
                   side_effect=ValidationError("Providers AI não disponíveis")), \
             patch('builtins.print') as mock_print, \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 2
        mock_print.assert_called_with("❌ Erro de configuração/ambiente: Providers AI não disponíveis")
    
    @pytest.mark.asyncio
    async def test_validation_error_during_data_directories_check(self):
        """Testa erro de validação dos diretórios de dados."""
        mock_config = Mock()
        mock_config.data_dir = Path("/invalid/path")
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories', 
                   side_effect=ValidationError("Diretórios não acessíveis")), \
             patch('builtins.print') as mock_print, \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 2
        mock_print.assert_called_with("❌ Erro de configuração/ambiente: Diretórios não acessíveis")
    
    @pytest.mark.asyncio
    async def test_config_runtime_validation_called(self):
        """Testa se validação de runtime é chamada."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        
        with patch.object(sys, 'argv', ['alfredo']), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging'), \
             patch('argparse.ArgumentParser.print_help'):
            
            await main()
            
            mock_config.validate_runtime.assert_called_once()
            mock_config.create_directory_structure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_logging_configuration_setup(self):
        """Testa configuração do sistema de logging."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        
        with patch.object(sys, 'argv', ['alfredo']), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging') as mock_logging, \
             patch('argparse.ArgumentParser.print_help'):
            
            await main()
            
            # Verifica se o logging foi configurado
            mock_logging.assert_called_once()
            call_args = mock_logging.call_args
            
            # Verifica os parâmetros passados
            expected_log_file = str(mock_config.data_dir / "logs" / "alfredo.log")
            assert expected_log_file in call_args[0]
            assert call_args[1]['to_stdout'] is True


class TestMainErrorHandling:
    """Testes para tratamento de erros no main."""
    
    @pytest.fixture
    def mock_base_setup(self):
        """Setup básico para testes de erro."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        
        with patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging'):
            yield mock_config
    
    @pytest.mark.asyncio
    async def test_keyboard_interrupt_handling(self, mock_base_setup):
        """Testa tratamento de KeyboardInterrupt."""
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock(side_effect=KeyboardInterrupt())
        mock_registry.get_command.return_value = mock_command
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry), \
             patch('builtins.print') as mock_print:
            
            await main()
            
            mock_print.assert_called_with("\n⚠️  Operação interrompida pelo usuário")
    
    @pytest.mark.asyncio
    async def test_value_error_handling(self, mock_base_setup):
        """Testa tratamento de ValueError (comando não encontrado)."""
        mock_factory = Mock()
        mock_registry = Mock()
        mock_registry.get_command.side_effect = ValueError("Comando 'invalid' não encontrado")
        
        with patch.object(sys, 'argv', ['alfredo', 'invalid']), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry), \
             patch('builtins.print') as mock_print, \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 1
        mock_print.assert_any_call("❌ Comando 'invalid' não encontrado")
        mock_print.assert_any_call("\n💡 Use 'alfredo --help' para ver comandos disponíveis")
    
    @pytest.mark.asyncio
    async def test_alfredo_error_handling(self, mock_base_setup):
        """Testa tratamento de AlfredoError."""
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        error = DownloadFailedError("Falha no download", {"url": "https://test.com"})
        mock_command.execute = AsyncMock(side_effect=error)
        mock_registry.get_command.return_value = mock_command
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry), \
             patch('builtins.print') as mock_print, \
             patch('logging.getLogger') as mock_logger, \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 1
        mock_print.assert_called_with("🔥 Falha no download")
    
    @pytest.mark.asyncio
    async def test_alfredo_error_with_details_logging(self, mock_base_setup):
        """Testa AlfredoError com detalhes sendo logados."""
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        error = ConfigurationError("Erro de config", {"config_key": "invalid_value"})
        mock_command.execute = AsyncMock(side_effect=error)
        mock_registry.get_command.return_value = mock_command
        
        mock_logger = Mock()
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry), \
             patch('builtins.print'), \
             patch('logging.getLogger', return_value=mock_logger), \
             pytest.raises(SystemExit):
            
            await main()
        
        # Verifica se os detalhes foram logados
        mock_logger.debug.assert_called_with(
            "Detalhes do erro: {'config_key': 'invalid_value'}"
        )
    
    @pytest.mark.asyncio
    async def test_unexpected_error_handling_without_verbose(self, mock_base_setup):
        """Testa tratamento de erro inesperado sem verbose."""
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock(side_effect=RuntimeError("Erro inesperado"))
        mock_registry.get_command.return_value = mock_command
        
        mock_logger = Mock()
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry), \
             patch('builtins.print') as mock_print, \
             patch('logging.getLogger', return_value=mock_logger), \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 1
        
        # Verifica mensagens de erro amigáveis
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "⚠️  Ops! Algo inesperado aconteceu" in print_calls
        assert "💡 Verifique os logs para mais detalhes técnicos" in print_calls
        
        # Verifica que erro foi logado com detalhes técnicos
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert "Erro inesperado no main: Erro inesperado" in error_call[0][0]
        assert error_call[1]['exc_info'] is True
    
    @pytest.mark.asyncio
    async def test_unexpected_error_handling_with_verbose(self, mock_base_setup):
        """Testa tratamento de erro inesperado com verbose."""
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock(side_effect=RuntimeError("Erro inesperado detalhado"))
        mock_registry.get_command.return_value = mock_command
        
        mock_logger = Mock()
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com', '--verbose']), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry), \
             patch('builtins.print') as mock_print, \
             patch('logging.getLogger', return_value=mock_logger), \
             pytest.raises(SystemExit) as exc_info:
            
            await main()
        
        assert exc_info.value.code == 1
        
        # Verifica que detalhes técnicos foram exibidos
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Detalhes técnicos: Erro inesperado detalhado" in call for call in print_calls)


class TestMainArgumentParsing:
    """Testes específicos para parsing de argumentos."""
    
    @pytest.mark.asyncio
    async def test_youtube_command_with_all_options(self):
        """Testa comando YouTube com todas as opções."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock()
        mock_registry.get_command.return_value = mock_command
        
        with patch.object(sys, 'argv', [
            'alfredo', 'youtube', 'https://youtube.com/watch?v=test',
            '--language', 'es', '--quality', 'medium', '--force', '--verbose'
        ]), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging'), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry):
            
            await main()
            
            mock_command.execute.assert_called_once_with(
                url='https://youtube.com/watch?v=test',
                language='es',
                quality='medium',
                force_reprocess=True
            )
    
    @pytest.mark.asyncio
    async def test_batch_command_with_all_options(self):
        """Testa comando batch com todas as opções."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock()
        mock_registry.get_command.return_value = mock_command
        
        with patch.object(sys, 'argv', [
            'alfredo', 'batch', '/path/to/videos',
            '--language', 'fr', '--recursive', '--max-workers', '8', '--force'
        ]), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging'), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry):
            
            await main()
            
            mock_command.execute.assert_called_once_with(
                directory='/path/to/videos',
                language='fr',
                recursive=True,
                max_workers=8,
                force_reprocess=True
            )
    
    @pytest.mark.asyncio
    async def test_default_values_applied(self):
        """Testa se valores padrão são aplicados corretamente."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock()
        mock_registry.get_command.return_value = mock_command
        
        with patch.object(sys, 'argv', [
            'alfredo', 'youtube', 'https://youtube.com/test'
        ]), \
             patch('src.main.AlfredoConfig', return_value=mock_config), \
             patch('src.main.validate_ffmpeg'), \
             patch('src.main.validate_ai_providers'), \
             patch('src.main.validate_data_directories'), \
             patch('src.main.setup_structured_logging'), \
             patch('src.main.InfrastructureFactory', return_value=mock_factory), \
             patch('src.main.CommandRegistry', return_value=mock_registry):
            
            await main()
            
            # Verifica valores padrão são usados
            mock_command.execute.assert_called_once_with(
                url='https://youtube.com/test',
                language='pt',  # DEFAULT_LANGUAGE
                quality='medium',  # DEFAULT_QUALITY  
                force_reprocess=False  # default para --force
            )


class TestMainIntegrationFlow:
    """Testes para fluxo completo de integração."""
    
    @pytest.mark.asyncio
    async def test_complete_application_startup_flow(self):
        """Testa fluxo completo de startup da aplicação."""
        mock_config = Mock()
        mock_config.data_dir = Path("/tmp/alfredo")
        mock_factory = Mock()
        mock_registry = Mock()
        mock_command = Mock()
        mock_command.execute = AsyncMock()
        mock_registry.get_command.return_value = mock_command
        
        with patch.object(sys, 'argv', ['alfredo', 'youtube', 'https://test.com']), \
             patch('src.main.AlfredoConfig', return_value=mock_config) as mock_config_class, \
             patch('src.main.validate_ffmpeg') as mock_validate_ffmpeg, \
             patch('src.main.validate_ai_providers') as mock_validate_ai, \
             patch('src.main.validate_data_directories') as mock_validate_dirs, \
             patch('src.main.setup_structured_logging') as mock_setup_logging, \
             patch('src.main.InfrastructureFactory', return_value=mock_factory) as mock_factory_class, \
             patch('src.main.CommandRegistry', return_value=mock_registry) as mock_registry_class:
            
            await main()
            
            # Verifica ordem correta de inicialização
            mock_config_class.assert_called_once()
            mock_validate_ffmpeg.assert_called_once()
            mock_validate_ai.assert_called_once_with(mock_config)
            mock_validate_dirs.assert_called_once_with(mock_config.data_dir)
            mock_config.validate_runtime.assert_called_once()
            mock_config.create_directory_structure.assert_called_once()
            mock_setup_logging.assert_called_once()
            mock_factory_class.assert_called_once_with(mock_config)
            mock_registry_class.assert_called_once_with(mock_config, mock_factory)
            mock_registry.get_command.assert_called_once_with('youtube')
            mock_command.execute.assert_called_once()
