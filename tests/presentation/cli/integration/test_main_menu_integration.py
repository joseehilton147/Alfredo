"""Integration tests for MainMenuScreen with InteractiveCLI."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.presentation.cli.interactive_cli import InteractiveCLI
from src.presentation.cli.screens.main_menu_screen import MainMenuScreen
from src.presentation.cli.utils.keyboard import MockKeyboardHandler


class TestMainMenuIntegration:
    """Integration tests for MainMenuScreen with InteractiveCLI."""

    @pytest.fixture
    def mock_app_context(self):
        """Create a mock application context."""
        return Mock()

    @pytest.fixture
    def cli_with_mock_keyboard(self, mock_app_context):
        """Create CLI with mock keyboard for testing."""
        cli = InteractiveCLI(mock_app_context)
        cli.keyboard = MockKeyboardHandler()
        return cli

    @pytest.mark.asyncio
    async def test_cli_initializes_with_main_menu(self, cli_with_mock_keyboard):
        """Test that CLI initializes with MainMenuScreen."""
        cli = cli_with_mock_keyboard

        # Mock the main loop to prevent infinite execution
        with patch.object(cli, '_main_loop', new_callable=AsyncMock):
            await cli.run()

        # Should have navigated to MainMenuScreen
        assert cli.current_screen is not None
        assert isinstance(cli.current_screen, MainMenuScreen)

    @pytest.mark.asyncio
    async def test_main_menu_navigation_integration(self, cli_with_mock_keyboard):
        """Test navigation integration between CLI and MainMenuScreen."""
        cli = cli_with_mock_keyboard

        # Create and navigate to main menu
        main_menu = MainMenuScreen(cli)
        await cli.navigate_to(main_menu)

        # Verify navigation state
        assert cli.current_screen == main_menu
        assert cli.state.current_screen == "main_menu"
        assert len(cli.screen_stack) == 0  # First screen, no previous screens

    @pytest.mark.asyncio
    async def test_main_menu_keyboard_integration(self, cli_with_mock_keyboard):
        """Test keyboard handling integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)
        await cli.navigate_to(main_menu)

        # Set up keyboard sequence for testing
        cli.keyboard.key_sequence = [cli.keyboard.ARROW_DOWN, cli.keyboard.ESC]

        # Mock the render method to prevent actual rendering
        main_menu.render = AsyncMock()

        # Test arrow key handling
        await main_menu.handle_input(cli.keyboard.ARROW_DOWN)

        # Should have called render
        main_menu.render.assert_called()

    @pytest.mark.asyncio
    async def test_main_menu_esc_key_behavior(self, cli_with_mock_keyboard):
        """Test ESC key behavior in main menu."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)
        await cli.navigate_to(main_menu)

        # Mock shutdown to prevent actual exit
        cli._shutdown = AsyncMock()

        # Simulate ESC key press (should trigger go_back, which should shutdown)
        await cli._handle_global_keys(cli.keyboard.ESC)

        # Should have called shutdown since there's no previous screen
        cli._shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_menu_option_selection_integration(self, cli_with_mock_keyboard):
        """Test option selection integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)
        await cli.navigate_to(main_menu)

        # Mock the placeholder message method
        main_menu._show_placeholder_message = Mock()

        # Test selecting the first option (Local Video)
        first_option = main_menu.menu.options[0]
        await first_option.action()

        # Should have shown placeholder message
        main_menu._show_placeholder_message.assert_called_once_with("Processamento de Vídeo Local")

    @pytest.mark.asyncio
    async def test_main_menu_shortcut_integration(self, cli_with_mock_keyboard):
        """Test keyboard shortcuts integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)
        await cli.navigate_to(main_menu)

        # Mock render to prevent actual rendering
        main_menu.render = AsyncMock()

        # Mock the placeholder message method to verify action was called
        main_menu._show_placeholder_message = Mock()

        # Test 'Y' shortcut for YouTube
        await main_menu.handle_input('Y')

        # Should have shown placeholder message for YouTube
        main_menu._show_placeholder_message.assert_called_once_with("Processamento de Vídeo do YouTube")

    @pytest.mark.asyncio
    async def test_main_menu_theme_integration(self, cli_with_mock_keyboard):
        """Test theme integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)

        # Should use the same theme as CLI
        assert main_menu.theme == cli.theme
        assert main_menu.menu.theme == cli.theme

    @pytest.mark.asyncio
    async def test_main_menu_state_integration(self, cli_with_mock_keyboard):
        """Test state integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)

        # Should use the same state as CLI
        assert main_menu.state == cli.state

        # Test on_enter updates state
        await main_menu.on_enter()
        assert main_menu.state.current_screen == "main_menu"

    @pytest.mark.asyncio
    async def test_main_menu_display_update_integration(self, cli_with_mock_keyboard):
        """Test display update integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)

        # Mock the CLI's update_live_display method
        cli.update_live_display = Mock()

        # Test that main menu can update display
        test_content = "Test content"
        main_menu.update_display(test_content)

        # Should have called CLI's update method
        cli.update_live_display.assert_called_once_with(test_content)

    @pytest.mark.asyncio
    async def test_main_menu_lifecycle_integration(self, cli_with_mock_keyboard):
        """Test screen lifecycle integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)

        # Test on_enter
        await main_menu.on_enter()
        assert main_menu.menu.get_selected_index() == 0

        # Test on_exit (should not raise exceptions)
        await main_menu.on_exit()

    def test_main_menu_help_text_integration(self, cli_with_mock_keyboard):
        """Test help text integration with CLI state."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)

        # Mock CLI methods for help text
        cli.get_screen_stack_depth = Mock(return_value=0)
        cli.peek_previous_screen = Mock(return_value=None)

        # Get navigation help
        help_text = main_menu.get_navigation_help()

        # Should return Rich Text object
        assert hasattr(help_text, 'append')

    @pytest.mark.asyncio
    async def test_main_menu_error_handling_integration(self, cli_with_mock_keyboard):
        """Test error handling integration."""
        cli = cli_with_mock_keyboard
        main_menu = MainMenuScreen(cli)

        # Test that exceptions in render don't crash the system
        with patch.object(main_menu, 'menu') as mock_menu:
            mock_menu.render.side_effect = Exception("Test error")

            # Should not raise exception
            try:
                await main_menu.render()
            except Exception:
                pytest.fail("MainMenuScreen.render should handle exceptions gracefully")

    @pytest.mark.asyncio
    async def test_full_menu_workflow_integration(self, cli_with_mock_keyboard):
        """Test a complete menu workflow."""
        cli = cli_with_mock_keyboard

        # Start with main menu
        with patch.object(cli, '_main_loop', new_callable=AsyncMock):
            await cli.run()

        # Should be at main menu
        assert isinstance(cli.current_screen, MainMenuScreen)

        # Test navigation through menu options
        main_menu = cli.current_screen
        main_menu.render = AsyncMock()

        # Test down navigation
        await main_menu.handle_input(cli.keyboard.ARROW_DOWN)
        assert main_menu.menu.get_selected_index() > 0

        # Test up navigation
        await main_menu.handle_input(cli.keyboard.ARROW_UP)

        # Test shortcut selection
        main_menu._show_placeholder_message = Mock()
        await main_menu.handle_input('S')
        main_menu._show_placeholder_message.assert_called_once_with("Configurações")
