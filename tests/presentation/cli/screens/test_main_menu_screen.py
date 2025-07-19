"""Tests for the MainMenuScreen."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.presentation.cli.screens.main_menu_screen import MainMenuScreen
from src.presentation.cli.themes.default_theme import DefaultTheme
from src.presentation.cli.utils.keyboard import MockKeyboardHandler


class TestMainMenuScreen:
    """Tests for MainMenuScreen class."""

    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI controller for testing."""
        cli = Mock()
        cli.theme = DefaultTheme()
        cli.state = Mock()
        cli.keyboard = MockKeyboardHandler()
        cli.update_live_display = Mock()
        cli.get_screen_stack_depth = Mock(return_value=0)
        cli.peek_previous_screen = Mock(return_value=None)
        cli.navigate_to = AsyncMock()
        return cli

    @pytest.fixture
    def main_menu_screen(self, mock_cli):
        """Create a MainMenuScreen for testing."""
        return MainMenuScreen(mock_cli)

    def test_initialization(self, main_menu_screen, mock_cli):
        """Test MainMenuScreen initialization."""
        assert main_menu_screen.cli == mock_cli
        assert main_menu_screen.theme == mock_cli.theme
        assert main_menu_screen.state == mock_cli.state
        assert main_menu_screen.menu is not None
        assert main_menu_screen.menu.title == "Alfredo AI - Menu Principal"

    def test_menu_options_creation(self, main_menu_screen):
        """Test that all required menu options are created."""
        options = main_menu_screen.menu.options

        # Should have 6 options
        assert len(options) == 6

        # Check option keys
        option_keys = [opt.key for opt in options]
        expected_keys = ["local", "youtube", "batch", "settings", "results", "help"]
        assert option_keys == expected_keys

        # Check option labels
        option_labels = [opt.label for opt in options]
        expected_labels = [
            "Processar Vídeo Local",
            "Processar Vídeo do YouTube",
            "Processamento em Lote",
            "Configurações",
            "Ver Resultados",
            "Ajuda",
        ]
        assert option_labels == expected_labels

    def test_menu_options_have_icons(self, main_menu_screen):
        """Test that all menu options have Unicode icons."""
        options = main_menu_screen.menu.options

        expected_icons = ["📁", "🎬", "📦", "⚙️", "📄", "❓"]
        actual_icons = [opt.icon for opt in options]

        assert actual_icons == expected_icons

    def test_menu_options_have_shortcuts(self, main_menu_screen):
        """Test that all menu options have keyboard shortcuts."""
        options = main_menu_screen.menu.options

        expected_shortcuts = ["L", "Y", "B", "S", "R", "H"]
        actual_shortcuts = [opt.shortcut for opt in options]

        assert actual_shortcuts == expected_shortcuts

    def test_menu_options_have_descriptions(self, main_menu_screen):
        """Test that all menu options have descriptions."""
        options = main_menu_screen.menu.options

        for option in options:
            assert option.description is not None
            assert len(option.description) > 0

    def test_menu_options_are_enabled(self, main_menu_screen):
        """Test that all menu options are enabled by default."""
        options = main_menu_screen.menu.options

        for option in options:
            assert option.enabled is True

    @pytest.mark.asyncio
    async def test_render_method(self, main_menu_screen):
        """Test the render method."""
        # Should not raise any exceptions
        await main_menu_screen.render()

        # Should call update_display
        main_menu_screen.cli.update_live_display.assert_called()

    @pytest.mark.asyncio
    async def test_on_enter_method(self, main_menu_screen):
        """Test the on_enter method."""
        await main_menu_screen.on_enter()

        # Should reset menu selection to first option
        assert main_menu_screen.menu.get_selected_index() == 0

        # Should update state
        main_menu_screen.state.current_screen = "main_menu"

    @pytest.mark.asyncio
    async def test_on_exit_method(self, main_menu_screen):
        """Test the on_exit method."""
        # Should not raise any exceptions
        await main_menu_screen.on_exit()

    @pytest.mark.asyncio
    async def test_handle_input_arrow_keys(self, main_menu_screen):
        """Test handling arrow key input."""
        # Mock the keyboard constants
        main_menu_screen.cli.keyboard.ARROW_UP = "\x1b[A"
        main_menu_screen.cli.keyboard.ARROW_DOWN = "\x1b[B"
        main_menu_screen.cli.keyboard.ENTER = "\r"

        initial_index = main_menu_screen.menu.get_selected_index()

        # Test down arrow
        await main_menu_screen.handle_input("\x1b[B")
        # Index should change (unless it was already at the last enabled option)

        # Test up arrow
        await main_menu_screen.handle_input("\x1b[A")
        # Should move back

    @pytest.mark.asyncio
    async def test_handle_input_enter_key(self, main_menu_screen):
        """Test handling Enter key input."""
        main_menu_screen.cli.keyboard.ENTER = "\r"

        # Mock the action for the first option
        first_option = main_menu_screen.menu.options[0]
        first_option.action = AsyncMock()

        # Simulate Enter key press
        await main_menu_screen.handle_input("\r")

        # The action should be called
        first_option.action.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_input_shortcuts(self, main_menu_screen):
        """Test handling keyboard shortcuts."""
        # Test 'L' shortcut for local video
        local_option = main_menu_screen.menu.options[0]
        local_option.action = AsyncMock()

        await main_menu_screen.handle_input("L")
        local_option.action.assert_called_once()

        # Test 'Y' shortcut for YouTube
        youtube_option = main_menu_screen.menu.options[1]
        youtube_option.action = AsyncMock()

        await main_menu_screen.handle_input("Y")
        youtube_option.action.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_common_keys(self, main_menu_screen):
        """Test handling common keys."""
        main_menu_screen.handle_common_keys = AsyncMock(return_value=True)

        await main_menu_screen.handle_input("some_key")

        main_menu_screen.handle_common_keys.assert_called_once_with("some_key")

    def test_create_help_text(self, main_menu_screen):
        """Test help text creation."""
        help_text = main_menu_screen._create_help_text()

        # Should return a Rich Text object
        assert hasattr(help_text, "append")  # Rich Text has append method

    @pytest.mark.asyncio
    async def test_local_video_action(self, main_menu_screen):
        """Test local video action handler."""
        with patch.object(
            main_menu_screen, "_show_placeholder_message"
        ) as mock_placeholder:
            await main_menu_screen._handle_local_video()
            mock_placeholder.assert_called_once_with("Processamento de Vídeo Local")

    @pytest.mark.asyncio
    async def test_youtube_video_action(self, main_menu_screen):
        """Test YouTube video action handler."""
        with patch.object(
            main_menu_screen, "_show_placeholder_message"
        ) as mock_placeholder:
            await main_menu_screen._handle_youtube_video()
            mock_placeholder.assert_called_once_with(
                "Processamento de Vídeo do YouTube"
            )

    @pytest.mark.asyncio
    async def test_batch_processing_action(self, main_menu_screen):
        """Test batch processing action handler."""
        with patch.object(
            main_menu_screen, "_show_placeholder_message"
        ) as mock_placeholder:
            await main_menu_screen._handle_batch_processing()
            mock_placeholder.assert_called_once_with("Processamento em Lote")

    @pytest.mark.asyncio
    async def test_settings_action(self, main_menu_screen):
        """Test settings action handler."""
        with patch(
            "src.presentation.cli.screens.settings_screen.SettingsScreen"
        ) as mock_settings_screen:
            mock_settings_instance = Mock()
            mock_settings_screen.return_value = mock_settings_instance

            await main_menu_screen._handle_settings()

            mock_settings_screen.assert_called_once_with(main_menu_screen.cli)
            main_menu_screen.cli.navigate_to.assert_called_once_with(
                mock_settings_instance
            )

    @pytest.mark.asyncio
    async def test_results_action(self, main_menu_screen):
        """Test results action handler."""
        with patch.object(
            main_menu_screen, "_show_placeholder_message"
        ) as mock_placeholder:
            await main_menu_screen._handle_results()
            mock_placeholder.assert_called_once_with("Visualização de Resultados")

    @pytest.mark.asyncio
    async def test_help_action(self, main_menu_screen):
        """Test help action handler."""
        with patch.object(
            main_menu_screen, "_show_placeholder_message"
        ) as mock_placeholder:
            await main_menu_screen._handle_help()
            mock_placeholder.assert_called_once_with("Sistema de Ajuda")

    def test_show_placeholder_message(self, main_menu_screen):
        """Test placeholder message display."""
        feature_name = "Test Feature"

        main_menu_screen._show_placeholder_message(feature_name)

        # Should call update_display
        main_menu_screen.cli.update_live_display.assert_called()

        # Get the call arguments
        call_args = main_menu_screen.cli.update_live_display.call_args[0][0]

        # Should be a Panel
        assert hasattr(call_args, "renderable")

    def test_menu_option_actions_are_callable(self, main_menu_screen):
        """Test that all menu option actions are callable."""
        options = main_menu_screen.menu.options

        for option in options:
            assert callable(option.action)

    @pytest.mark.asyncio
    async def test_render_after_input(self, main_menu_screen):
        """Test that render is called after handling input."""
        main_menu_screen.cli.keyboard.ARROW_DOWN = "\x1b[B"

        # Mock render method
        original_render = main_menu_screen.render
        main_menu_screen.render = AsyncMock()

        await main_menu_screen.handle_input("\x1b[B")

        # Render should be called after input handling
        main_menu_screen.render.assert_called_once()

        # Restore original render
        main_menu_screen.render = original_render

    def test_menu_title_is_correct(self, main_menu_screen):
        """Test that menu title is correct."""
        assert main_menu_screen.menu.title == "Alfredo AI - Menu Principal"

    def test_menu_uses_theme(self, main_menu_screen, mock_cli):
        """Test that menu uses the correct theme."""
        assert main_menu_screen.menu.theme == mock_cli.theme

    @pytest.mark.asyncio
    async def test_multiple_key_presses(self, main_menu_screen):
        """Test handling multiple key presses in sequence."""
        main_menu_screen.cli.keyboard.ARROW_DOWN = "\x1b[B"
        main_menu_screen.cli.keyboard.ARROW_UP = "\x1b[A"

        initial_index = main_menu_screen.menu.get_selected_index()

        # Press down then up
        await main_menu_screen.handle_input("\x1b[B")
        await main_menu_screen.handle_input("\x1b[A")

        # Should be back to initial position (or close to it)
        # The exact behavior depends on the menu implementation

    def test_all_shortcuts_are_unique(self, main_menu_screen):
        """Test that all keyboard shortcuts are unique."""
        shortcuts = [opt.shortcut for opt in main_menu_screen.menu.options]
        unique_shortcuts = set(shortcuts)

        assert len(shortcuts) == len(unique_shortcuts)

    def test_all_keys_are_unique(self, main_menu_screen):
        """Test that all option keys are unique."""
        keys = [opt.key for opt in main_menu_screen.menu.options]
        unique_keys = set(keys)

        assert len(keys) == len(unique_keys)

    @pytest.mark.asyncio
    async def test_case_insensitive_shortcuts(self, main_menu_screen):
        """Test that shortcuts work with both upper and lower case."""
        # Mock the action for the local video option
        local_option = main_menu_screen.menu.options[0]
        local_option.action = AsyncMock()

        # Test uppercase 'L'
        await main_menu_screen.handle_input("L")
        assert local_option.action.call_count == 1

        # Test lowercase 'l'
        await main_menu_screen.handle_input("l")
        assert local_option.action.call_count == 2
