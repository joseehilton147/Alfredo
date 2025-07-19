"""Tests for the DefaultTheme class."""

import pytest
from rich.style import Style

from src.presentation.cli.themes.colors import ColorPalette
from src.presentation.cli.themes.default_theme import DefaultTheme


class TestDefaultTheme:
    """Test the DefaultTheme class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.theme = DefaultTheme()

    def test_default_theme_initialization(self):
        """Test that DefaultTheme initializes with Claude-inspired colors."""
        assert self.theme.primary_color == ColorPalette.CLAUDE_BLUE
        assert self.theme.secondary_color == ColorPalette.CLAUDE_GREEN
        assert self.theme.accent_color == ColorPalette.CLAUDE_PURPLE
        assert self.theme.success_color == ColorPalette.CLAUDE_GREEN
        assert self.theme.error_color == ColorPalette.CLAUDE_RED
        assert self.theme.warning_color == ColorPalette.CLAUDE_ORANGE
        assert self.theme.info_color == ColorPalette.CLAUDE_BLUE
        assert self.theme.text_color == ColorPalette.PRIMARY_TEXT
        assert self.theme.muted_color == ColorPalette.MUTED_TEXT
        assert self.theme.highlight_color == ColorPalette.PRIMARY_TEXT
        assert self.theme.background_color == ColorPalette.DARK_BG
        assert self.theme.surface_color == ColorPalette.MEDIUM_BG
        assert self.theme.selected_color == ColorPalette.CLAUDE_GREEN
        assert self.theme.hover_color == ColorPalette.HOVER
        assert self.theme.disabled_color == ColorPalette.DISABLED
        assert self.theme.border_style == "rounded"
        assert self.theme.border_color == ColorPalette.CLAUDE_PURPLE

    def test_style_map_completeness(self):
        """Test that style map contains all expected styles."""
        style_map = self.theme._get_style_map()
        assert isinstance(style_map, dict)

        # Menu styles
        menu_styles = [
            "menu_title", "menu_option", "menu_option_selected",
            "menu_option_disabled", "menu_border"
        ]
        for style in menu_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

        # Progress styles
        progress_styles = [
            "progress_complete", "progress_incomplete",
            "progress_text", "progress_percentage"
        ]
        for style in progress_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

        # Status styles
        status_styles = [
            "status_success", "status_error", "status_warning",
            "status_info", "status_muted"
        ]
        for style in status_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

        # File browser styles
        file_styles = [
            "file_directory", "file_regular", "file_selected",
            "file_extension", "file_size"
        ]
        for style in file_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

        # Input field styles
        input_styles = [
            "input_normal", "input_focused", "input_error", "input_placeholder"
        ]
        for style in input_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

        # Text styles
        text_styles = [
            "text_primary", "text_secondary", "text_highlight", "text_link"
        ]
        for style in text_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

        # Panel styles
        panel_styles = ["panel_title", "panel_border", "panel_content"]
        for style in panel_styles:
            assert style in style_map
            assert isinstance(style_map[style], Style)

    def test_menu_styles(self):
        """Test menu-specific styles."""
        # Menu title should be bold and primary color
        title_style = self.theme.get_style("menu_title")
        assert title_style.bold is True

        # Selected option should be bold and selected color
        selected_style = self.theme.get_style("menu_option", "selected")
        assert selected_style.bold is True

        # Disabled option should be dimmed
        disabled_style = self.theme.get_style("menu_option", "disabled")
        assert disabled_style.dim is True

    def test_status_styles(self):
        """Test status message styles."""
        # Success should be bold
        success_style = self.theme.get_style("status_success")
        assert success_style.bold is True

        # Error should be bold
        error_style = self.theme.get_style("status_error")
        assert error_style.bold is True

        # Warning should be bold
        warning_style = self.theme.get_style("status_warning")
        assert warning_style.bold is True

        # Muted should be dimmed
        muted_style = self.theme.get_style("status_muted")
        assert muted_style.dim is True

    def test_file_browser_styles(self):
        """Test file browser styles."""
        # Directory should be bold
        dir_style = self.theme.get_style("file_directory")
        assert dir_style.bold is True

        # Selected file should be bold
        selected_style = self.theme.get_style("file", "selected")
        assert selected_style.bold is True

    def test_input_field_styles(self):
        """Test input field styles."""
        # Focused input should be bold
        focused_style = self.theme.get_style("input", "focused")
        assert focused_style.bold is True

        # Placeholder should be italic
        placeholder_style = self.theme.get_style("input_placeholder")
        assert placeholder_style.italic is True

    def test_text_styles(self):
        """Test general text styles."""
        # Highlight should be bold
        highlight_style = self.theme.get_style("text_highlight")
        assert highlight_style.bold is True

        # Link should be underlined
        link_style = self.theme.get_style("text_link")
        assert link_style.underline is True

    def test_panel_styles(self):
        """Test panel styles."""
        # Panel title should be bold
        title_style = self.theme.get_style("panel_title")
        assert title_style.bold is True

    def test_get_color_scheme_contains_claude_colors(self):
        """Test that color scheme contains Claude-inspired colors."""
        scheme = self.theme.get_color_scheme()

        assert scheme["primary"] == ColorPalette.CLAUDE_BLUE
        assert scheme["secondary"] == ColorPalette.CLAUDE_GREEN
        assert scheme["accent"] == ColorPalette.CLAUDE_PURPLE
        assert scheme["success"] == ColorPalette.CLAUDE_GREEN
        assert scheme["error"] == ColorPalette.CLAUDE_RED
        assert scheme["warning"] == ColorPalette.CLAUDE_ORANGE

    def test_theme_inheritance(self):
        """Test that DefaultTheme properly inherits from Theme."""
        from src.presentation.cli.themes.base_theme import Theme
        assert isinstance(self.theme, Theme)

    def test_style_consistency(self):
        """Test that styles are consistent across similar elements."""
        # All bold styles should actually be bold
        bold_styles = [
            "menu_title", "menu_option_selected", "status_success",
            "status_error", "status_warning", "file_directory",
            "input_focused", "text_highlight", "panel_title"
        ]

        for style_name in bold_styles:
            style = self.theme.get_style(style_name)
            assert style.bold is True, f"Style {style_name} should be bold"

        # All dim styles should actually be dim
        dim_styles = ["menu_option_disabled", "status_muted"]

        for style_name in dim_styles:
            style = self.theme.get_style(style_name)
            assert style.dim is True, f"Style {style_name} should be dim"
