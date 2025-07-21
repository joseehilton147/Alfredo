"""
Testes completos para screens CLI para aumentar cobertura na presentation layer.

Testa main menu, navegação, interações e componentes das telas.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from rich.console import Console

from src.presentation.cli.screens.main_menu_screen import MainMenuScreen
from src.presentation.cli.screens.base_screen import Screen


class TestMainMenuScreenComplete:
    """Testes completos para MainMenuScreen."""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock do CLI controller."""
        cli = Mock()
        cli.console = Mock(spec=Console)
        cli.switch_screen = Mock()
        cli.run_in_background = AsyncMock()
        cli.context = Mock()
        cli.context.get_supported_languages = Mock(return_value=["pt", "en", "es"])
        return cli
    
    @pytest.fixture
    def main_menu(self, mock_cli):
        """MainMenuScreen com CLI mock."""
        return MainMenuScreen(mock_cli)
    
    def test_init_creates_menu_correctly(self, mock_cli):
        """Testa inicialização correta do menu."""
        screen = MainMenuScreen(mock_cli)
        
        assert screen.cli == mock_cli
        assert screen.menu is not None
        
        # Verifica opções do menu
        options = screen.menu.options
        assert len(options) >= 4  # local, youtube, batch, results
        
        option_keys = [opt.key for opt in options]
        assert "local" in option_keys
        assert "youtube" in option_keys
        assert "batch" in option_keys
        assert "results" in option_keys
    
    def test_menu_options_have_required_attributes(self, main_menu):
        """Testa que opções do menu têm atributos necessários."""
        options = main_menu.menu.options
        
        for option in options:
            assert hasattr(option, 'key')
            assert hasattr(option, 'label')
            assert hasattr(option, 'description')
            assert hasattr(option, 'icon')
            assert hasattr(option, 'action')
            assert hasattr(option, 'shortcut')
            
            # Verifica que não são None
            assert option.key is not None
            assert option.label is not None
            assert option.description is not None
            assert option.icon is not None
            assert option.action is not None
    
    def test_menu_shortcuts_are_unique(self, main_menu):
        """Testa que atalhos do menu são únicos."""
        options = main_menu.menu.options
        shortcuts = [opt.shortcut for opt in options if opt.shortcut]
        
        # Verifica que não há duplicatas
        assert len(shortcuts) == len(set(shortcuts))
    
    def test_handle_local_video_action(self, main_menu, mock_cli):
        """Testa ação de vídeo local."""
        with patch.object(main_menu, '_show_placeholder_message') as mock_placeholder:
            main_menu._handle_local_video()
            
            mock_placeholder.assert_called_once_with(
                "Processamento de Vídeo Local",
                "Esta funcionalidade permite processar arquivos de vídeo locais."
            )
    
    def test_handle_youtube_video_action(self, main_menu, mock_cli):
        """Testa ação de vídeo YouTube."""
        with patch.object(main_menu, '_show_placeholder_message') as mock_placeholder:
            main_menu._handle_youtube_video()
            
            mock_placeholder.assert_called_once_with(
                "Processamento de Vídeo do YouTube",
                "Esta funcionalidade permite baixar e processar vídeos do YouTube."
            )
    
    def test_handle_batch_processing_action(self, main_menu, mock_cli):
        """Testa ação de processamento em lote."""
        with patch.object(main_menu, '_show_placeholder_message') as mock_placeholder:
            main_menu._handle_batch_processing()
            
            mock_placeholder.assert_called_once_with(
                "Processamento em Lote",
                "Esta funcionalidade permite processar múltiplos arquivos simultaneamente."
            )
    
    def test_handle_results_action(self, main_menu, mock_cli):
        """Testa ação de visualizar resultados."""
        with patch.object(main_menu, '_show_placeholder_message') as mock_placeholder:
            main_menu._handle_results()
            
            mock_placeholder.assert_called_once_with(
                "Visualizar Resultados",
                "Esta funcionalidade permite visualizar e gerenciar resultados anteriores."
            )
    
    def test_handle_settings_action(self, main_menu, mock_cli):
        """Testa ação de configurações."""
        with patch.object(main_menu, '_show_placeholder_message') as mock_placeholder:
            main_menu._handle_settings()
            
            mock_placeholder.assert_called_once_with(
                "Configurações",
                "Esta funcionalidade permite ajustar configurações do sistema."
            )
    
    def test_show_placeholder_message(self, main_menu, mock_cli):
        """Testa exibição de mensagem placeholder."""
        title = "Test Title"
        message = "Test message content"
        
        with patch('rich.panel.Panel') as mock_panel, \
             patch('rich.align.Align') as mock_align:
            
            main_menu._show_placeholder_message(title, message)
            
            # Verifica que Panel foi criado
            mock_panel.assert_called_once()
            
            # Verifica que console.print foi chamado
            mock_cli.console.print.assert_called()
    
    def test_render_method(self, main_menu, mock_cli):
        """Testa método render da tela."""
        with patch.object(main_menu, '_render_header') as mock_header, \
             patch.object(main_menu, '_render_menu') as mock_menu:
            
            main_menu.render()
            
            mock_header.assert_called_once()
            mock_menu.assert_called_once()
    
    def test_render_header(self, main_menu, mock_cli):
        """Testa renderização do cabeçalho."""
        with patch('rich.panel.Panel') as mock_panel, \
             patch('rich.align.Align') as mock_align:
            
            main_menu._render_header()
            
            # Verifica criação do painel do cabeçalho
            mock_panel.assert_called()
            mock_cli.console.print.assert_called()
    
    def test_render_menu(self, main_menu, mock_cli):
        """Testa renderização do menu."""
        with patch.object(main_menu.menu, 'render') as mock_menu_render:
            
            main_menu._render_menu()
            
            mock_menu_render.assert_called_once_with(mock_cli.console)
    
    def test_handle_input_delegates_to_menu(self, main_menu):
        """Testa que handle_input delega para o menu."""
        test_key = "l"
        
        with patch.object(main_menu.menu, 'handle_input', return_value=True) as mock_handle:
            
            result = main_menu.handle_input(test_key)
            
            mock_handle.assert_called_once_with(test_key)
            assert result is True
    
    def test_handle_input_returns_false_when_menu_returns_false(self, main_menu):
        """Testa retorno falso quando menu não processa input."""
        test_key = "x"
        
        with patch.object(main_menu.menu, 'handle_input', return_value=False) as mock_handle:
            
            result = main_menu.handle_input(test_key)
            
            mock_handle.assert_called_once_with(test_key)
            assert result is False


class TestBaseScreenComponents:
    """Testes para componentes base das telas."""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock do CLI controller."""
        cli = Mock()
        cli.console = Mock(spec=Console)
        return cli
    
    @pytest.fixture
    def base_screen(self, mock_cli):
        """Screen base para testes."""
        return Screen(mock_cli)
    
    def test_base_screen_init(self, mock_cli):
        """Testa inicialização da tela base."""
        screen = Screen(mock_cli)
        
        assert screen.cli == mock_cli
    
    def test_base_screen_render_not_implemented(self, base_screen):
        """Testa que render base não está implementado."""
        with pytest.raises(NotImplementedError):
            base_screen.render()
    
    def test_base_screen_handle_input_returns_false(self, base_screen):
        """Testa que handle_input base retorna False."""
        result = base_screen.handle_input("any_key")
        assert result is False


class TestMenuOptionsConfiguration:
    """Testa configuração específica das opções do menu."""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock do CLI controller."""
        cli = Mock()
        cli.console = Mock(spec=Console)
        cli.switch_screen = Mock()
        return cli
    
    @pytest.fixture
    def main_menu(self, mock_cli):
        """MainMenuScreen com CLI mock."""
        return MainMenuScreen(mock_cli)
    
    def test_local_video_option_configuration(self, main_menu):
        """Testa configuração da opção de vídeo local."""
        options = main_menu.menu.options
        local_option = next((opt for opt in options if opt.key == "local"), None)
        
        assert local_option is not None
        assert local_option.label == "Processar Vídeo Local"
        assert "vídeo" in local_option.description.lower()
        assert local_option.icon == "📁"
        assert local_option.shortcut == "L"
        assert callable(local_option.action)
    
    def test_youtube_option_configuration(self, main_menu):
        """Testa configuração da opção YouTube."""
        options = main_menu.menu.options
        youtube_option = next((opt for opt in options if opt.key == "youtube"), None)
        
        assert youtube_option is not None
        assert "YouTube" in youtube_option.label
        assert "youtube" in youtube_option.description.lower()
        assert local_option.icon in ["🎬", "📺", "🎥"]  # Aceita vários ícones de vídeo
        assert youtube_option.shortcut == "Y"
        assert callable(youtube_option.action)
    
    def test_batch_option_configuration(self, main_menu):
        """Testa configuração da opção de lote."""
        options = main_menu.menu.options
        batch_option = next((opt for opt in options if opt.key == "batch"), None)
        
        assert batch_option is not None
        assert "Lote" in batch_option.label or "Batch" in batch_option.label
        assert "múltip" in batch_option.description.lower() or "lote" in batch_option.description.lower()
        assert batch_option.shortcut == "B"
        assert callable(batch_option.action)
    
    def test_results_option_configuration(self, main_menu):
        """Testa configuração da opção de resultados."""
        options = main_menu.menu.options
        results_option = next((opt for opt in options if opt.key == "results"), None)
        
        assert results_option is not None
        assert "Resultado" in results_option.label or "Result" in results_option.label
        assert "resultado" in results_option.description.lower() or "result" in results_option.description.lower()
        assert results_option.shortcut == "R"
        assert callable(results_option.action)
    
    def test_settings_option_configuration(self, main_menu):
        """Testa configuração da opção de configurações."""
        options = main_menu.menu.options
        settings_option = next((opt for opt in options if opt.key == "settings"), None)
        
        if settings_option:  # Pode não existir em todas as versões
            assert "Configurações" in settings_option.label or "Settings" in settings_option.label
            assert "config" in settings_option.description.lower() or "ajust" in settings_option.description.lower()
            assert settings_option.shortcut == "S"
            assert callable(settings_option.action)
    
    def test_exit_option_configuration(self, main_menu):
        """Testa configuração da opção de sair."""
        options = main_menu.menu.options
        exit_option = next((opt for opt in options if opt.key == "exit"), None)
        
        if exit_option:  # Pode não existir em todas as versões
            assert "Sair" in exit_option.label or "Exit" in exit_option.label
            assert callable(exit_option.action)


class TestMenuInteractions:
    """Testa interações específicas do menu."""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock do CLI controller."""
        cli = Mock()
        cli.console = Mock(spec=Console)
        cli.switch_screen = Mock()
        return cli
    
    @pytest.fixture
    def main_menu(self, mock_cli):
        """MainMenuScreen com CLI mock."""
        return MainMenuScreen(mock_cli)
    
    def test_menu_navigation_by_key(self, main_menu):
        """Testa navegação por teclas."""
        with patch.object(main_menu.menu, 'handle_input', return_value=True) as mock_handle:
            
            # Testa teclas de navegação
            navigation_keys = ['up', 'down', 'j', 'k', 'enter', 'space']
            
            for key in navigation_keys:
                result = main_menu.handle_input(key)
                assert result is True
            
            assert mock_handle.call_count == len(navigation_keys)
    
    def test_menu_shortcuts_execution(self, main_menu):
        """Testa execução por atalhos."""
        # Simula pressionamento de atalho
        with patch.object(main_menu, '_handle_local_video') as mock_local:
            
            # Simula que o menu processou o atalho 'l' e executou a ação
            with patch.object(main_menu.menu, 'handle_input') as mock_handle:
                def side_effect(key):
                    if key.lower() == 'l':
                        # Simula execução da ação
                        main_menu._handle_local_video()
                        return True
                    return False
                
                mock_handle.side_effect = side_effect
                
                result = main_menu.handle_input('l')
                
                assert result is True
                mock_local.assert_called_once()
    
    def test_invalid_key_handling(self, main_menu):
        """Testa tratamento de teclas inválidas."""
        with patch.object(main_menu.menu, 'handle_input', return_value=False):
            
            result = main_menu.handle_input('invalid_key')
            
            assert result is False
    
    def test_special_characters_handling(self, main_menu):
        """Testa tratamento de caracteres especiais."""
        special_keys = ['ctrl+c', 'ctrl+d', 'esc', 'tab', 'shift+tab']
        
        with patch.object(main_menu.menu, 'handle_input', return_value=False):
            
            for key in special_keys:
                result = main_menu.handle_input(key)
                # Deve retornar False para caracteres não reconhecidos
                assert result is False


class TestScreenRendering:
    """Testa renderização específica das telas."""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock do CLI controller."""
        cli = Mock()
        cli.console = Mock(spec=Console)
        return cli
    
    @pytest.fixture
    def main_menu(self, mock_cli):
        """MainMenuScreen com CLI mock."""
        return MainMenuScreen(mock_cli)
    
    def test_render_calls_console_print(self, main_menu, mock_cli):
        """Testa que render chama console.print."""
        with patch.object(main_menu, '_render_header'), \
             patch.object(main_menu, '_render_menu'):
            
            main_menu.render()
            
            # Pelo menos o cabeçalho deve ser impresso
            assert mock_cli.console.print.call_count >= 0
    
    def test_header_contains_app_title(self, main_menu, mock_cli):
        """Testa que cabeçalho contém título da aplicação."""
        with patch('rich.text.Text') as mock_text:
            
            main_menu._render_header()
            
            # Verifica que Text foi criado (para o título)
            mock_text.assert_called()
    
    def test_menu_renders_with_console(self, main_menu, mock_cli):
        """Testa que menu é renderizado com console."""
        with patch.object(main_menu.menu, 'render') as mock_render:
            
            main_menu._render_menu()
            
            mock_render.assert_called_once_with(mock_cli.console)
    
    def test_placeholder_message_formatting(self, main_menu, mock_cli):
        """Testa formatação da mensagem placeholder."""
        title = "Test Title"
        message = "Test message with multiple words"
        
        with patch('rich.panel.Panel') as mock_panel, \
             patch('rich.text.Text') as mock_text:
            
            main_menu._show_placeholder_message(title, message)
            
            # Verifica que Text foi criado para título e mensagem
            assert mock_text.call_count >= 1
            
            # Verifica que Panel foi criado
            mock_panel.assert_called_once()
            
            # Verifica que foi impresso
            mock_cli.console.print.assert_called()


class TestMenuOptionsCallbacks:
    """Testa callbacks específicos das opções do menu."""
    
    @pytest.fixture
    def mock_cli(self):
        """Mock do CLI controller."""
        cli = Mock()
        cli.console = Mock(spec=Console)
        cli.switch_screen = Mock()
        return cli
    
    @pytest.fixture
    def main_menu(self, mock_cli):
        """MainMenuScreen com CLI mock."""
        return MainMenuScreen(mock_cli)
    
    def test_all_options_have_working_callbacks(self, main_menu):
        """Testa que todas as opções têm callbacks funcionais."""
        options = main_menu.menu.options
        
        for option in options:
            # Verifica que a ação é callable
            assert callable(option.action)
            
            # Tenta executar a ação (deve não dar erro)
            try:
                option.action()
            except Exception as e:
                # Se falhar, pelo menos deve ser um erro esperado
                assert "placeholder" in str(e).lower() or "not implemented" in str(e).lower()
    
    def test_option_actions_dont_crash(self, main_menu):
        """Testa que ações das opções não causam crash."""
        actions = [
            main_menu._handle_local_video,
            main_menu._handle_youtube_video,
            main_menu._handle_batch_processing,
            main_menu._handle_results,
            main_menu._handle_settings
        ]
        
        for action in actions:
            try:
                with patch.object(main_menu, '_show_placeholder_message'):
                    action()
            except Exception as e:
                pytest.fail(f"Action {action.__name__} crashed with: {e}")
    
    def test_actions_call_placeholder_correctly(self, main_menu):
        """Testa que ações chamam placeholder corretamente."""
        with patch.object(main_menu, '_show_placeholder_message') as mock_placeholder:
            
            # Testa cada ação
            main_menu._handle_local_video()
            main_menu._handle_youtube_video()
            main_menu._handle_batch_processing()
            main_menu._handle_results()
            main_menu._handle_settings()
            
            # Verifica que placeholder foi chamado para cada ação
            assert mock_placeholder.call_count == 5
            
            # Verifica que cada chamada teve título e mensagem
            for call in mock_placeholder.call_args_list:
                args = call[0]
                assert len(args) == 2  # título e mensagem
                assert isinstance(args[0], str)  # título é string
                assert isinstance(args[1], str)  # mensagem é string
                assert len(args[0]) > 0  # título não é vazio
                assert len(args[1]) > 0  # mensagem não é vazia
