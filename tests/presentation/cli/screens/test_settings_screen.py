"""Tests for the settings screen."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.presentation.cli.context import ApplicationContext
from src.presentation.cli.interactive_cli import InteractiveCLI
from src.presentation.cli.screens.settings_screen import SettingsScreen
from src.presentation.cli.themes.default_theme import DefaultTheme


class TestSettingsScreen:
    """Test cases for the SettingsScreen class."""

    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI instance."""
        cli = Mock(spec=InteractiveCLI)
        cli.theme = DefaultTheme()
        cli.app_context = Mock(spec=ApplicationContext)
        cli.state = Mock()
        cli.keyboard = Mock()
        cli.keyboard.ARROW_UP = "\x1b[A"
        cli.keyboard.ARROW_DOWN = "\x1b[B"
        cli.keyboard.ENTER = "\r"
        cli.keyboard.ESC = "\x1b"

        # Mock app context methods
        cli.app_context.get_setting.side_effect = lambda key, default=None: {
            "DEFAULT_LANGUAGE": "pt",
            "WHISPER_MODEL": "base",
            "OUTPUT_DIR": "data/output",
            "INPUT_DIR": "data/input",
        }.get(key, default)

        cli.app_context.get_supported_languages.return_value = {
            "pt": "Português",
            "en": "English",
            "es": "Español",
            "fr": "Français",
        }

        cli.app_context.get_whisper_models.return_value = {
            "tiny": "Tiny (39 MB) - Mais rápido, menor precisão",
            "base": "Base (74 MB) - Equilibrio entre velocidade e precisão",
            "small": "Small (244 MB) - Boa precisão, velocidade moderada",
            "medium": "Medium (769 MB) - Alta precisão, mais lento",
            "large": "Large (1550 MB) - Máxima precisão, mais lento",
        }

        return cli

    @pytest.fixture
    def settings_screen(self, mock_cli):
        """Create a SettingsScreen instance."""
        return SettingsScreen(mock_cli)

    def test_initialization(self, settings_screen, mock_cli):
        """Test settings screen initialization."""
        assert settings_screen.cli == mock_cli
        assert settings_screen.current_mode == "main"
        assert settings_screen.main_menu is not None
        assert settings_screen.settings_changed is False

    def test_get_current_language_display(self, settings_screen):
        """Test getting current language display name."""
        display_name = settings_screen._get_current_language_display()
        assert display_name == "Português"

    def test_get_current_model_display(self, settings_screen):
        """Test getting current model display name."""
        display_name = settings_screen._get_current_model_display()
        assert display_name == "Base (74 MB)"

    def test_get_current_directories(self, settings_screen):
        """Test getting current directory paths."""
        output_dir = settings_screen._get_current_output_dir()
        input_dir = settings_screen._get_current_input_dir()

        assert "data\\output" in output_dir or "data/output" in output_dir
        assert "data\\input" in input_dir or "data/input" in input_dir

    def test_create_main_menu(self, settings_screen):
        """Test main menu creation."""
        menu = settings_screen._create_main_menu()

        assert menu.title == "⚙️ Configurações do Alfredo AI"
        assert len(menu.options) == 6

        # Check menu options
        option_keys = [opt.key for opt in menu.options]
        expected_keys = [
            "language",
            "model",
            "output_dir",
            "input_dir",
            "save",
            "reset",
        ]
        assert option_keys == expected_keys

    def test_create_language_menu(self, settings_screen):
        """Test language menu creation."""
        menu = settings_screen._create_language_menu()

        assert menu.title == "🌐 Selecionar Idioma de Transcrição"
        assert len(menu.options) == 4  # pt, en, es, fr

        # Check that current language is marked as selected
        pt_option = next(opt for opt in menu.options if opt.key == "pt")
        assert "✓ Selecionado" in pt_option.description

    def test_create_model_menu(self, settings_screen):
        """Test model menu creation."""
        menu = settings_screen._create_model_menu()

        assert menu.title == "🧠 Selecionar Modelo Whisper"
        assert len(menu.options) == 5  # tiny, base, small, medium, large

        # Check that current model is marked as selected
        base_option = next(opt for opt in menu.options if opt.key == "base")
        assert "✓ Selecionado" in base_option.description

    @pytest.mark.asyncio
    async def test_select_language(self, settings_screen, mock_cli):
        """Test language selection."""
        # Select a different language
        await settings_screen._select_language("en")

        # Verify setting was updated
        mock_cli.app_context.update_setting.assert_called_with("DEFAULT_LANGUAGE", "en")
        assert settings_screen.settings_changed is True
        assert settings_screen.current_mode == "main"

    @pytest.mark.asyncio
    async def test_select_same_language(self, settings_screen, mock_cli):
        """Test selecting the same language doesn't mark as changed."""
        # Select the same language (pt)
        await settings_screen._select_language("pt")

        # Verify setting was not updated and not marked as changed
        mock_cli.app_context.update_setting.assert_not_called()
        assert settings_screen.settings_changed is False

    @pytest.mark.asyncio
    async def test_select_model(self, settings_screen, mock_cli):
        """Test model selection."""
        # Select a different model
        await settings_screen._select_model("small")

        # Verify setting was updated
        mock_cli.app_context.update_setting.assert_called_with("WHISPER_MODEL", "small")
        assert settings_screen.settings_changed is True
        assert settings_screen.current_mode == "main"

    @pytest.mark.asyncio
    async def test_select_same_model(self, settings_screen, mock_cli):
        """Test selecting the same model doesn't mark as changed."""
        # Select the same model (base)
        await settings_screen._select_model("base")

        # Verify setting was not updated and not marked as changed
        mock_cli.app_context.update_setting.assert_not_called()
        assert settings_screen.settings_changed is False

    @pytest.mark.asyncio
    async def test_select_directory(self, settings_screen, mock_cli):
        """Test directory selection."""
        test_path = Path("/test/output")

        # Mock Path.mkdir to avoid actual directory creation
        with patch.object(Path, "mkdir"):
            # Set up for output directory selection
            settings_screen.current_directory_setting = "Pasta de Saída"

            await settings_screen._select_directory(test_path)

            # Verify setting was updated
            mock_cli.app_context.update_setting.assert_called_with(
                "OUTPUT_DIR", str(test_path)
            )
            assert settings_screen.settings_changed is True
            assert settings_screen.current_mode == "main"

    @pytest.mark.asyncio
    async def test_handle_save_settings_success(self, settings_screen, mock_cli):
        """Test successful settings save."""
        settings_screen.settings_changed = True

        # Mock successful save
        mock_cli.app_context.save_settings_to_env.return_value = None
        mock_cli.app_context.create_directories.return_value = None

        with patch.object(settings_screen, "_show_message") as mock_show:
            await settings_screen._handle_save_settings()

            # Verify save was called
            mock_cli.app_context.save_settings_to_env.assert_called_once()
            mock_cli.app_context.create_directories.assert_called_once()

            # Verify success message was shown
            mock_show.assert_called_once()
            args = mock_show.call_args[0]
            assert "Salvas" in args[0]
            assert args[2] == "success"

            # Verify settings_changed was reset
            assert settings_screen.settings_changed is False

    @pytest.mark.asyncio
    async def test_handle_save_settings_error(self, settings_screen, mock_cli):
        """Test settings save error handling."""
        settings_screen.settings_changed = True

        # Mock save error
        mock_cli.app_context.save_settings_to_env.side_effect = Exception("Save error")

        with patch.object(settings_screen, "_show_message") as mock_show:
            await settings_screen._handle_save_settings()

            # Verify error message was shown
            mock_show.assert_called_once()
            args = mock_show.call_args[0]
            assert "Erro" in args[0]
            assert args[2] == "error"

    @pytest.mark.asyncio
    async def test_handle_reset_settings(self, settings_screen, mock_cli):
        """Test settings reset."""
        with patch.object(settings_screen, "_show_message") as mock_show:
            await settings_screen._handle_reset_settings()

            # Verify default settings were applied
            expected_calls = [
                (("WHISPER_MODEL", "base"),),
                (("DEFAULT_LANGUAGE", "pt"),),
                (("OUTPUT_DIR", "data/output"),),
                (("INPUT_DIR", "data/input"),),
            ]

            actual_calls = mock_cli.app_context.update_setting.call_args_list
            assert len(actual_calls) == 4

            # Verify settings_changed was set
            assert settings_screen.settings_changed is True

            # Verify info message was shown
            mock_show.assert_called_once()
            args = mock_show.call_args[0]
            assert "Restauradas" in args[0]
            assert args[2] == "info"

    @pytest.mark.asyncio
    async def test_handle_main_input(self, settings_screen):
        """Test main menu input handling."""
        # Mock menu selection
        mock_option = Mock()

        # Create a proper async mock
        async def mock_action():
            pass

        mock_option.action = mock_action
        settings_screen.main_menu.handle_key = Mock(return_value=mock_option)

        await settings_screen._handle_main_input("enter")

        # Verify menu handled key
        settings_screen.main_menu.handle_key.assert_called_with("enter")

    @pytest.mark.asyncio
    async def test_handle_language_input_escape(self, settings_screen):
        """Test language menu escape handling."""
        settings_screen.current_mode = "language"

        await settings_screen._handle_language_input("\x1b")

        assert settings_screen.current_mode == "main"

    @pytest.mark.asyncio
    async def test_handle_model_input_escape(self, settings_screen):
        """Test model menu escape handling."""
        settings_screen.current_mode = "model"

        await settings_screen._handle_model_input("\x1b")

        assert settings_screen.current_mode == "main"

    @pytest.mark.asyncio
    async def test_handle_directory_input_escape(self, settings_screen):
        """Test directory browser escape handling."""
        settings_screen.current_mode = "directories"
        settings_screen.directory_browser = Mock()
        settings_screen.current_directory_setting = "Test"

        await settings_screen._handle_directory_input("\x1b")

        assert settings_screen.current_mode == "main"
        assert settings_screen.directory_browser is None
        assert settings_screen.current_directory_setting is None

    def test_truncate_path(self, settings_screen):
        """Test path truncation for display."""
        # Short path should not be truncated
        short_path = "/short/path"
        result = settings_screen._truncate_path(short_path)
        assert result == short_path

        # Long path should be truncated
        long_path = "/very/long/path/that/exceeds/the/maximum/length/for/display"
        result = settings_screen._truncate_path(long_path, max_length=20)
        assert len(result) <= 20
        assert result.startswith("...")

    @pytest.mark.asyncio
    async def test_on_enter(self, settings_screen):
        """Test screen enter event."""
        await settings_screen.on_enter()

        assert settings_screen.current_mode == "main"
        assert settings_screen.settings_changed is False
        assert settings_screen.state.current_screen == "settings"

    @pytest.mark.asyncio
    async def test_on_exit(self, settings_screen):
        """Test screen exit event."""
        # Set up some state
        settings_screen.language_menu = Mock()
        settings_screen.model_menu = Mock()
        settings_screen.directory_browser = Mock()
        settings_screen.current_directory_setting = "Test"

        await settings_screen.on_exit()

        # Verify cleanup
        assert settings_screen.language_menu is None
        assert settings_screen.model_menu is None
        assert settings_screen.directory_browser is None
        assert settings_screen.current_directory_setting is None

    @pytest.mark.asyncio
    async def test_mode_transitions(self, settings_screen):
        """Test mode transitions between different settings screens."""
        # Test language mode
        await settings_screen._handle_language_settings()
        assert settings_screen.current_mode == "language"
        assert settings_screen.language_menu is not None

        # Test model mode
        await settings_screen._handle_model_settings()
        assert settings_screen.current_mode == "model"
        assert settings_screen.model_menu is not None

        # Test directory mode
        await settings_screen._handle_output_directory()
        assert settings_screen.current_mode == "directories"
        assert settings_screen.current_directory_setting == "Pasta de Saída"
        assert settings_screen.directory_browser is not None

    def test_update_main_menu_descriptions(self, settings_screen):
        """Test main menu description updates."""
        # Change a setting
        settings_screen.settings_changed = True

        # Update descriptions
        settings_screen._update_main_menu_descriptions()

        # Verify descriptions contain current values
        language_option = settings_screen.main_menu.options[0]
        assert "Português" in language_option.description

        model_option = settings_screen.main_menu.options[1]
        assert "Base" in model_option.description

        # Verify save button is enabled when settings changed
        save_option = settings_screen.main_menu.options[4]
        assert save_option.enabled is True


class TestSettingsScreenIntegration:
    """Integration tests for settings screen with real components."""

    @pytest.fixture
    def real_app_context(self):
        """Create a real ApplicationContext for integration tests."""
        with patch("src.presentation.cli.context.Path.exists", return_value=False):
            return ApplicationContext()

    @pytest.fixture
    def integration_cli(self, real_app_context):
        """Create CLI with real context for integration tests."""
        cli = Mock(spec=InteractiveCLI)
        cli.theme = DefaultTheme()
        cli.app_context = real_app_context
        cli.state = Mock()
        cli.keyboard = Mock()
        cli.keyboard.ARROW_UP = "\x1b[A"
        cli.keyboard.ARROW_DOWN = "\x1b[B"
        cli.keyboard.ENTER = "\r"
        cli.keyboard.ESC = "\x1b"
        return cli

    @pytest.mark.asyncio
    async def test_full_settings_workflow(self, integration_cli):
        """Test complete settings configuration workflow."""
        settings_screen = SettingsScreen(integration_cli)

        # Initialize screen
        await settings_screen.on_enter()
        assert settings_screen.current_mode == "main"

        # Change language
        await settings_screen._select_language("en")
        assert settings_screen.settings_changed is True

        # Change model
        await settings_screen._select_model("small")
        assert settings_screen.settings_changed is True

        # Verify settings were updated in context
        assert integration_cli.app_context.get_setting("DEFAULT_LANGUAGE") == "en"
        assert integration_cli.app_context.get_setting("WHISPER_MODEL") == "small"

        # Test reset
        await settings_screen._handle_reset_settings()
        assert integration_cli.app_context.get_setting("DEFAULT_LANGUAGE") == "pt"
        assert integration_cli.app_context.get_setting("WHISPER_MODEL") == "base"
