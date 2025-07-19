"""Tests for color definitions and utilities."""

import pytest
from rich.color import Color
from rich.style import Style

from src.presentation.cli.themes.colors import ColorPalette, ColorUtils, ThemeColors


class TestColorPalette:
    """Test the ColorPalette class."""

    def test_color_palette_has_required_colors(self):
        """Test that ColorPalette has all required color definitions."""
        # Primary colors
        assert hasattr(ColorPalette, 'CLAUDE_BLUE')
        assert hasattr(ColorPalette, 'CLAUDE_GREEN')
        assert hasattr(ColorPalette, 'CLAUDE_ORANGE')
        assert hasattr(ColorPalette, 'CLAUDE_RED')
        assert hasattr(ColorPalette, 'CLAUDE_PURPLE')

        # Neutral colors
        assert hasattr(ColorPalette, 'DARK_BG')
        assert hasattr(ColorPalette, 'MEDIUM_BG')
        assert hasattr(ColorPalette, 'LIGHT_BG')

        # Text colors
        assert hasattr(ColorPalette, 'PRIMARY_TEXT')
        assert hasattr(ColorPalette, 'SECONDARY_TEXT')
        assert hasattr(ColorPalette, 'MUTED_TEXT')

        # Interactive states
        assert hasattr(ColorPalette, 'HOVER')
        assert hasattr(ColorPalette, 'SELECTED')
        assert hasattr(ColorPalette, 'DISABLED')

    def test_color_values_are_valid_hex(self):
        """Test that all color values are valid hex colors."""
        colors = [
            ColorPalette.CLAUDE_BLUE,
            ColorPalette.CLAUDE_GREEN,
            ColorPalette.CLAUDE_ORANGE,
            ColorPalette.CLAUDE_RED,
            ColorPalette.CLAUDE_PURPLE,
            ColorPalette.DARK_BG,
            ColorPalette.MEDIUM_BG,
            ColorPalette.LIGHT_BG,
            ColorPalette.PRIMARY_TEXT,
            ColorPalette.SECONDARY_TEXT,
            ColorPalette.MUTED_TEXT,
            ColorPalette.HOVER,
            ColorPalette.SELECTED,
            ColorPalette.DISABLED
        ]

        for color in colors:
            assert color.startswith('#'), f"Color {color} should start with #"
            assert len(color) == 7, f"Color {color} should be 7 characters long"
            # Test that it's valid hex
            int(color[1:], 16)  # This will raise ValueError if not valid hex


class TestColorUtils:
    """Test the ColorUtils class."""

    def test_hex_to_rich_color(self):
        """Test hex to Rich Color conversion."""
        hex_color = "#2563eb"
        rich_color = ColorUtils.hex_to_rich_color(hex_color)
        assert isinstance(rich_color, Color)

    def test_create_style_basic(self):
        """Test basic style creation."""
        style = ColorUtils.create_style(color="red", bold=True)
        assert isinstance(style, Style)
        assert style.color.name == "red"
        assert style.bold is True

    def test_create_style_with_all_options(self):
        """Test style creation with all options."""
        style = ColorUtils.create_style(
            color="blue",
            bgcolor="white",
            bold=True,
            italic=True,
            underline=True,
            dim=True
        )
        assert isinstance(style, Style)
        assert style.color.name == "blue"
        assert style.bgcolor.name == "white"
        assert style.bold is True
        assert style.italic is True
        assert style.underline is True
        assert style.dim is True

    def test_create_style_defaults(self):
        """Test style creation with default values."""
        style = ColorUtils.create_style()
        assert isinstance(style, Style)

    def test_get_gradient_colors(self):
        """Test gradient color generation."""
        start_color = "#ff0000"
        end_color = "#0000ff"
        colors = ColorUtils.get_gradient_colors(start_color, end_color, 5)
        assert isinstance(colors, list)
        assert len(colors) >= 2
        assert start_color in colors
        assert end_color in colors


class TestThemeColors:
    """Test the ThemeColors class."""

    def test_get_menu_colors(self):
        """Test menu color retrieval."""
        colors = ThemeColors.get_menu_colors()
        assert isinstance(colors, dict)

        required_keys = ["title", "option", "selected", "disabled", "border"]
        for key in required_keys:
            assert key in colors
            assert isinstance(colors[key], str)

    def test_get_progress_colors(self):
        """Test progress bar color retrieval."""
        colors = ThemeColors.get_progress_colors()
        assert isinstance(colors, dict)

        required_keys = ["complete", "incomplete", "text", "percentage"]
        for key in required_keys:
            assert key in colors
            assert isinstance(colors[key], str)

    def test_get_status_colors(self):
        """Test status message color retrieval."""
        colors = ThemeColors.get_status_colors()
        assert isinstance(colors, dict)

        required_keys = ["success", "error", "warning", "info", "muted"]
        for key in required_keys:
            assert key in colors
            assert isinstance(colors[key], str)

    def test_get_file_browser_colors(self):
        """Test file browser color retrieval."""
        colors = ThemeColors.get_file_browser_colors()
        assert isinstance(colors, dict)

        required_keys = ["directory", "file", "selected", "extension", "size"]
        for key in required_keys:
            assert key in colors
            assert isinstance(colors[key], str)

    def test_all_color_methods_return_valid_colors(self):
        """Test that all color methods return valid color values."""
        color_methods = [
            ThemeColors.get_menu_colors,
            ThemeColors.get_progress_colors,
            ThemeColors.get_status_colors,
            ThemeColors.get_file_browser_colors
        ]

        for method in color_methods:
            colors = method()
            for color_value in colors.values():
                # Should be either a hex color or a named color
                if color_value.startswith('#'):
                    assert len(color_value) == 7
                    int(color_value[1:], 16)  # Valid hex
                else:
                    # Named color - just check it's a string
                    assert isinstance(color_value, str)
                    assert len(color_value) > 0
