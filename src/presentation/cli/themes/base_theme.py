"""Base theme class for the interactive CLI."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

from rich.style import Style

from .colors import ColorUtils


@dataclass
class Theme(ABC):
    """Abstract base class for CLI themes."""

    # Core colors
    primary_color: str
    secondary_color: str
    accent_color: str

    # Status colors
    success_color: str
    error_color: str
    warning_color: str
    info_color: str

    # Text colors
    text_color: str
    muted_color: str
    highlight_color: str

    # Background colors
    background_color: str
    surface_color: str

    # Interactive states
    selected_color: str
    hover_color: str
    disabled_color: str

    # Border and layout
    border_style: str
    border_color: str

    def get_style(self, element_type: str, state: str = "normal") -> Style:
        """Get Rich Style for a specific element type and state."""
        style_map = self._get_style_map()
        key = f"{element_type}_{state}"

        if key in style_map:
            return style_map[key]
        elif element_type in style_map:
            return style_map[element_type]
        else:
            return Style()

    @abstractmethod
    def _get_style_map(self) -> Dict[str, Style]:
        """Get the complete style mapping for this theme."""
        pass

    def get_color_scheme(self) -> Dict[str, str]:
        """Get the complete color scheme as a dictionary."""
        return {
            "primary": self.primary_color,
            "secondary": self.secondary_color,
            "accent": self.accent_color,
            "success": self.success_color,
            "error": self.error_color,
            "warning": self.warning_color,
            "info": self.info_color,
            "text": self.text_color,
            "muted": self.muted_color,
            "highlight": self.highlight_color,
            "background": self.background_color,
            "surface": self.surface_color,
            "selected": self.selected_color,
            "hover": self.hover_color,
            "disabled": self.disabled_color,
            "border": self.border_color
        }

    def create_custom_style(
        self,
        color: str = None,
        bgcolor: str = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        dim: bool = False
    ) -> Style:
        """Create a custom style using theme colors."""
        return ColorUtils.create_style(
            color=color or self.text_color,
            bgcolor=bgcolor,
            bold=bold,
            italic=italic,
            underline=underline,
            dim=dim
        )
