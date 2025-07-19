"""Default theme for the interactive CLI."""

from dataclasses import dataclass
from typing import Dict

from rich.style import Style

from .base_theme import Theme
from .colors import ColorPalette, ColorUtils


@dataclass
class DefaultTheme(Theme):
    """Default visual theme inspired by Claude Code."""

    # Core colors (using Claude-inspired palette)
    primary_color: str = ColorPalette.CLAUDE_BLUE
    secondary_color: str = ColorPalette.CLAUDE_GREEN
    accent_color: str = ColorPalette.CLAUDE_PURPLE

    # Status colors
    success_color: str = ColorPalette.CLAUDE_GREEN
    error_color: str = ColorPalette.CLAUDE_RED
    warning_color: str = ColorPalette.CLAUDE_ORANGE
    info_color: str = ColorPalette.CLAUDE_BLUE

    # Text colors
    text_color: str = ColorPalette.PRIMARY_TEXT
    muted_color: str = ColorPalette.MUTED_TEXT
    highlight_color: str = ColorPalette.PRIMARY_TEXT

    # Background colors
    background_color: str = ColorPalette.DARK_BG
    surface_color: str = ColorPalette.MEDIUM_BG

    # Interactive states
    selected_color: str = ColorPalette.CLAUDE_GREEN
    hover_color: str = ColorPalette.HOVER
    disabled_color: str = ColorPalette.DISABLED

    # Border and layout
    border_style: str = "rounded"
    border_color: str = ColorPalette.CLAUDE_PURPLE

    def _get_style_map(self) -> Dict[str, Style]:
        """Get the complete style mapping for the default theme."""
        return {
            # Menu styles
            "menu_title": ColorUtils.create_style(
                color=self.primary_color,
                bold=True
            ),
            "menu_option": ColorUtils.create_style(
                color=self.text_color
            ),
            "menu_option_selected": ColorUtils.create_style(
                color=self.selected_color,
                bold=True
            ),
            "menu_option_disabled": ColorUtils.create_style(
                color=self.disabled_color,
                dim=True
            ),
            "menu_border": ColorUtils.create_style(
                color=self.border_color
            ),

            # Progress bar styles
            "progress_complete": ColorUtils.create_style(
                color=self.success_color
            ),
            "progress_incomplete": ColorUtils.create_style(
                color=self.muted_color
            ),
            "progress_text": ColorUtils.create_style(
                color=self.text_color
            ),
            "progress_percentage": ColorUtils.create_style(
                color=self.primary_color,
                bold=True
            ),

            # Status message styles
            "status_success": ColorUtils.create_style(
                color=self.success_color,
                bold=True
            ),
            "status_error": ColorUtils.create_style(
                color=self.error_color,
                bold=True
            ),
            "status_warning": ColorUtils.create_style(
                color=self.warning_color,
                bold=True
            ),
            "status_info": ColorUtils.create_style(
                color=self.info_color
            ),
            "status_muted": ColorUtils.create_style(
                color=self.muted_color,
                dim=True
            ),

            # File browser styles
            "file_directory": ColorUtils.create_style(
                color=self.primary_color,
                bold=True
            ),
            "file_regular": ColorUtils.create_style(
                color=self.text_color
            ),
            "file_selected": ColorUtils.create_style(
                color=self.selected_color,
                bold=True
            ),
            "file_extension": ColorUtils.create_style(
                color=self.accent_color
            ),
            "file_size": ColorUtils.create_style(
                color=self.muted_color
            ),

            # Input field styles
            "input_normal": ColorUtils.create_style(
                color=self.text_color
            ),
            "input_focused": ColorUtils.create_style(
                color=self.primary_color,
                bold=True
            ),
            "input_error": ColorUtils.create_style(
                color=self.error_color
            ),
            "input_placeholder": ColorUtils.create_style(
                color=self.muted_color,
                italic=True
            ),

            # General text styles
            "text_primary": ColorUtils.create_style(
                color=self.text_color
            ),
            "text_secondary": ColorUtils.create_style(
                color=self.muted_color
            ),
            "text_highlight": ColorUtils.create_style(
                color=self.highlight_color,
                bold=True
            ),
            "text_link": ColorUtils.create_style(
                color=self.primary_color,
                underline=True
            ),

            # Panel and container styles
            "panel_title": ColorUtils.create_style(
                color=self.primary_color,
                bold=True
            ),
            "panel_border": ColorUtils.create_style(
                color=self.border_color
            ),
            "panel_content": ColorUtils.create_style(
                color=self.text_color
            )
        }
