"""Tests for theme utilities."""

from unittest.mock import Mock, patch

import pytest
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from src.presentation.cli.themes.default_theme import DefaultTheme
from src.presentation.cli.themes.theme_utils import (
    StyleHelper,
    ThemeManager,
    ThemePresets,
)


class TestThemeManager:
    """Test the ThemeManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.theme = DefaultTheme()
        self.manager = ThemeManager(self.theme)

    def test_initialization_with_theme(self):
        """Test ThemeManager initialization with provided theme."""
        manager = ThemeManager(self.theme)
        assert manager.get_theme() == self.theme

    def test_initialization_without_theme(self):
        """Test ThemeManager initialization with default theme."""
        manager = ThemeManager()
        assert isinstance(manager.get_theme(), DefaultTheme)

    def test_set_theme(self):
        """Test setting a new theme."""
        new_theme = DefaultTheme()
        self.manager.set_theme(new_theme)
        assert self.manager.get_theme() == new_theme

    def test_create_styled_text(self):
        """Test creating styled text."""
        text = self.manager.create_styled_text("Hello", "menu_title")
        assert isinstance(text, Text)
        assert str(text) == "Hello"

    def test_create_styled_text_with_state(self):
        """Test creating styled text with specific state."""
        text = self.manager.create_styled_text("Selected", "menu_option", "selected")
        assert isinstance(text, Text)
        assert str(text) == "Selected"

    def test_create_panel(self):
        """Test creating a themed panel."""
        panel = self.manager.create_panel("Content", "Title")
        assert isinstance(panel, Panel)

    def test_create_panel_without_title(self):
        """Test creating a panel without title."""
        panel = self.manager.create_panel("Content")
        assert isinstance(panel, Panel)

    def test_create_menu_table(self):
        """Test creating a menu table."""
        options = ["Option 1", "Option 2"]
        table = self.manager.create_menu_table("Menu", options)
        assert isinstance(table, Table)

    def test_create_progress_bar(self):
        """Test creating a progress bar."""
        progress = self.manager.create_progress_bar("Processing")
        assert isinstance(progress, Progress)

    def test_create_progress_bar_default_description(self):
        """Test creating progress bar with default description."""
        progress = self.manager.create_progress_bar()
        assert isinstance(progress, Progress)

    @patch('src.presentation.cli.themes.theme_utils.Console')
    def test_print_status_methods(self, mock_console_class):
        """Test status printing methods."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        manager = ThemeManager(self.theme)

        # Test different status types
        manager.print_status("Test message", "info")
        manager.print_error("Error message")
        manager.print_success("Success message")
        manager.print_warning("Warning message")
        manager.print_info("Info message")

        # Verify console.print was called
        assert mock_console.print.call_count == 5

    @patch('src.presentation.cli.themes.theme_utils.Console')
    def test_print_status_with_prefix(self, mock_console_class):
        """Test status printing with custom prefix."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        manager = ThemeManager(self.theme)
        manager.print_status("Test message", "info", "CUSTOM")

        mock_console.print.assert_called_once()


class TestStyleHelper:
    """Test the StyleHelper class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.theme = DefaultTheme()

    def test_create_menu_option_style_normal(self):
        """Test creating normal menu option style."""
        style = StyleHelper.create_menu_option_style(self.theme)
        assert style is not None

    def test_create_menu_option_style_selected(self):
        """Test creating selected menu option style."""
        style = StyleHelper.create_menu_option_style(self.theme, selected=True)
        assert style is not None

    def test_create_menu_option_style_disabled(self):
        """Test creating disabled menu option style."""
        style = StyleHelper.create_menu_option_style(self.theme, disabled=True)
        assert style is not None

    def test_create_file_style_regular(self):
        """Test creating regular file style."""
        style = StyleHelper.create_file_style(self.theme)
        assert style is not None

    def test_create_file_style_directory(self):
        """Test creating directory style."""
        style = StyleHelper.create_file_style(self.theme, is_directory=True)
        assert style is not None

    def test_create_file_style_selected(self):
        """Test creating selected file style."""
        style = StyleHelper.create_file_style(self.theme, selected=True)
        assert style is not None

    def test_create_input_style_normal(self):
        """Test creating normal input style."""
        style = StyleHelper.create_input_style(self.theme)
        assert style is not None

    def test_create_input_style_focused(self):
        """Test creating focused input style."""
        style = StyleHelper.create_input_style(self.theme, focused=True)
        assert style is not None

    def test_create_input_style_error(self):
        """Test creating error input style."""
        style = StyleHelper.create_input_style(self.theme, error=True)
        assert style is not None


class TestThemePresets:
    """Test the ThemePresets class."""

    def test_get_default_theme(self):
        """Test getting default theme."""
        theme = ThemePresets.get_default_theme()
        assert isinstance(theme, DefaultTheme)

    def test_get_high_contrast_theme(self):
        """Test getting high contrast theme."""
        theme = ThemePresets.get_high_contrast_theme()
        assert isinstance(theme, DefaultTheme)

        # Verify high contrast colors
        assert theme.text_color == "#ffffff"
        assert theme.background_color == "#000000"
        assert theme.selected_color == "#00ff00"
        assert theme.error_color == "#ff0000"
        assert theme.success_color == "#00ff00"
        assert theme.warning_color == "#ffff00"

    def test_get_minimal_theme(self):
        """Test getting minimal theme."""
        theme = ThemePresets.get_minimal_theme()
        assert isinstance(theme, DefaultTheme)

        # Verify minimal colors
        assert theme.primary_color == "#ffffff"
        assert theme.secondary_color == "#cccccc"
        assert theme.accent_color == "#888888"
        assert theme.selected_color == "#ffffff"

    def test_all_presets_are_different(self):
        """Test that all theme presets are different."""
        default = ThemePresets.get_default_theme()
        high_contrast = ThemePresets.get_high_contrast_theme()
        minimal = ThemePresets.get_minimal_theme()

        # They should have different color schemes
        default_scheme = default.get_color_scheme()
        high_contrast_scheme = high_contrast.get_color_scheme()
        minimal_scheme = minimal.get_color_scheme()

        assert default_scheme != high_contrast_scheme
        assert default_scheme != minimal_scheme
        assert high_contrast_scheme != minimal_scheme

    def test_presets_maintain_theme_interface(self):
        """Test that all presets maintain the Theme interface."""
        presets = [
            ThemePresets.get_default_theme(),
            ThemePresets.get_high_contrast_theme(),
            ThemePresets.get_minimal_theme()
        ]

        for theme in presets:
            # Test that they have all required attributes
            assert hasattr(theme, 'primary_color')
            assert hasattr(theme, 'secondary_color')
            assert hasattr(theme, 'accent_color')
            assert hasattr(theme, 'success_color')
            assert hasattr(theme, 'error_color')
            assert hasattr(theme, 'warning_color')
            assert hasattr(theme, 'info_color')
            assert hasattr(theme, 'text_color')
            assert hasattr(theme, 'muted_color')
            assert hasattr(theme, 'highlight_color')
            assert hasattr(theme, 'background_color')
            assert hasattr(theme, 'surface_color')
            assert hasattr(theme, 'selected_color')
            assert hasattr(theme, 'hover_color')
            assert hasattr(theme, 'disabled_color')
            assert hasattr(theme, 'border_style')
            assert hasattr(theme, 'border_color')

            # Test that they can get styles
            style = theme.get_style("menu_title")
            assert style is not None

            # Test that they can get color scheme
            scheme = theme.get_color_scheme()
            assert isinstance(scheme, dict)
            assert len(scheme) > 0
