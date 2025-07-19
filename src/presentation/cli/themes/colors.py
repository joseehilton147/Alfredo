"""Color definitions and utilities for the CLI themes."""

from typing import Any, Dict

from rich.color import Color
from rich.style import Style


class ColorPalette:
    """Claude Code-inspired color palette."""

    # Primary colors (inspired by Claude's interface)
    CLAUDE_BLUE = "#2563eb"      # Primary blue
    CLAUDE_GREEN = "#059669"     # Success green
    CLAUDE_ORANGE = "#ea580c"    # Warning orange
    CLAUDE_RED = "#dc2626"       # Error red
    CLAUDE_PURPLE = "#7c3aed"    # Accent purple

    # Neutral colors
    DARK_BG = "#0f172a"          # Dark background
    MEDIUM_BG = "#1e293b"        # Medium background
    LIGHT_BG = "#334155"         # Light background

    # Text colors
    PRIMARY_TEXT = "#f8fafc"     # Primary text (white)
    SECONDARY_TEXT = "#cbd5e1"   # Secondary text (light gray)
    MUTED_TEXT = "#64748b"       # Muted text (gray)

    # Interactive states
    HOVER = "#3b82f6"            # Hover state
    SELECTED = "#1d4ed8"         # Selected state
    DISABLED = "#475569"         # Disabled state


class ColorUtils:
    """Utilities for working with colors in the CLI."""

    @staticmethod
    def hex_to_rich_color(hex_color: str) -> Color:
        """Convert hex color to Rich Color object."""
        return Color.parse(hex_color)

    @staticmethod
    def create_style(
        color: str = None,
        bgcolor: str = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        dim: bool = False
    ) -> Style:
        """Create a Rich Style object with the given properties."""
        return Style(
            color=color,
            bgcolor=bgcolor,
            bold=bold,
            italic=italic,
            underline=underline,
            dim=dim
        )

    @staticmethod
    def get_gradient_colors(start_color: str, end_color: str, steps: int) -> list[str]:
        """Generate a gradient between two colors."""
        # For now, return a simple interpolation
        # This could be enhanced with proper color interpolation
        return [start_color, end_color]  # Simplified for now


class ThemeColors:
    """Predefined color combinations for different UI elements."""

    @staticmethod
    def get_menu_colors() -> Dict[str, str]:
        """Get colors for menu elements."""
        return {
            "title": ColorPalette.CLAUDE_BLUE,
            "option": ColorPalette.PRIMARY_TEXT,
            "selected": ColorPalette.CLAUDE_GREEN,
            "disabled": ColorPalette.DISABLED,
            "border": ColorPalette.CLAUDE_PURPLE
        }

    @staticmethod
    def get_progress_colors() -> Dict[str, str]:
        """Get colors for progress bars."""
        return {
            "complete": ColorPalette.CLAUDE_GREEN,
            "incomplete": ColorPalette.LIGHT_BG,
            "text": ColorPalette.PRIMARY_TEXT,
            "percentage": ColorPalette.CLAUDE_BLUE
        }

    @staticmethod
    def get_status_colors() -> Dict[str, str]:
        """Get colors for status messages."""
        return {
            "success": ColorPalette.CLAUDE_GREEN,
            "error": ColorPalette.CLAUDE_RED,
            "warning": ColorPalette.CLAUDE_ORANGE,
            "info": ColorPalette.CLAUDE_BLUE,
            "muted": ColorPalette.MUTED_TEXT
        }

    @staticmethod
    def get_file_browser_colors() -> Dict[str, str]:
        """Get colors for file browser elements."""
        return {
            "directory": ColorPalette.CLAUDE_BLUE,
            "file": ColorPalette.PRIMARY_TEXT,
            "selected": ColorPalette.CLAUDE_GREEN,
            "extension": ColorPalette.CLAUDE_PURPLE,
            "size": ColorPalette.SECONDARY_TEXT
        }
