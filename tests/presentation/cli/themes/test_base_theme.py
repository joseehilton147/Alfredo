"""Tests for the base Theme class."""

import pytest
from rich.style import Style

from src.presentation.cli.themes.base_theme import Theme


class MockTheme(Theme):
    """Mock theme implementation for testing."""

    def __init__(self):
        super().__init__(
            primary_color="#2563eb",
            secondary_color="#059669",
            accent_color="#7c3aed",
            success_color="#059669",
            error_color="#dc2626",
            warning_color="#ea580c",
            info_color="#2563eb",
            text_color="#f8fafc",
            muted_color="#64748b",
            highlight_color="#f8fafc",
            background_color="#0f172a",
            surface_color="#1e293b",
            selected_color="#059669",
            hover_color="#3b82f6",
            disabled_color="#475569",
            border_style="rounded",
            border_color="#7c3aed"
        )

    def _get_style_map(self):
        """Mock style map for testing."""
        return {
            "test_element": Style(color="red"),
            "test_element_selected": Style(color="green", bold=True),
            "another_element": Style(color="blue")
        }


class TestTheme:
    """Test the base Theme class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.theme = MockTheme()

    def test_theme_initialization(self):
        """Test that theme initializes with correct values."""
        assert self.theme.primary_color == "#2563eb"
        assert self.theme.secondary_color == "#059669"
        assert self.theme.accent_color == "#7c3aed"
        assert self.theme.success_color == "#059669"
        assert self.theme.error_color == "#dc2626"
        assert self.theme.warning_color == "#ea580c"
        assert self.theme.info_color == "#2563eb"
        assert self.theme.text_color == "#f8fafc"
        assert self.theme.muted_color == "#64748b"
        assert self.theme.highlight_color == "#f8fafc"
        assert self.theme.background_color == "#0f172a"
        assert self.theme.surface_color == "#1e293b"
        assert self.theme.selected_color == "#059669"
        assert self.theme.hover_color == "#3b82f6"
        assert self.theme.disabled_color == "#475569"
        assert self.theme.border_style == "rounded"
        assert self.theme.border_color == "#7c3aed"

    def test_get_style_with_element_and_state(self):
        """Test getting style with specific element and state."""
        style = self.theme.get_style("test_element", "selected")
        assert isinstance(style, Style)
        assert style.color.name == "green"
        assert style.bold is True

    def test_get_style_with_element_only(self):
        """Test getting style with element only (default state)."""
        style = self.theme.get_style("test_element")
        assert isinstance(style, Style)
        assert style.color.name == "red"

    def test_get_style_unknown_element(self):
        """Test getting style for unknown element returns empty style."""
        style = self.theme.get_style("unknown_element")
        assert isinstance(style, Style)
        # Empty style should have no specific properties set

    def test_get_style_unknown_state(self):
        """Test getting style with unknown state falls back to element style."""
        style = self.theme.get_style("test_element", "unknown_state")
        assert isinstance(style, Style)
        assert style.color.name == "red"  # Falls back to base element style

    def test_get_color_scheme(self):
        """Test getting complete color scheme."""
        scheme = self.theme.get_color_scheme()
        assert isinstance(scheme, dict)

        expected_keys = [
            "primary", "secondary", "accent", "success", "error", "warning",
            "info", "text", "muted", "highlight", "background", "surface",
            "selected", "hover", "disabled", "border"
        ]

        for key in expected_keys:
            assert key in scheme
            assert isinstance(scheme[key], str)

    def test_create_custom_style_with_defaults(self):
        """Test creating custom style with default values."""
        style = self.theme.create_custom_style()
        assert isinstance(style, Style)
        # Should use theme's default text color

    def test_create_custom_style_with_parameters(self):
        """Test creating custom style with specific parameters."""
        style = self.theme.create_custom_style(
            color="red",
            bgcolor="blue",
            bold=True,
            italic=True,
            underline=True,
            dim=True
        )
        assert isinstance(style, Style)
        assert style.color.name == "red"
        assert style.bgcolor.name == "blue"
        assert style.bold is True
        assert style.italic is True
        assert style.underline is True
        assert style.dim is True

    def test_create_custom_style_partial_parameters(self):
        """Test creating custom style with some parameters."""
        style = self.theme.create_custom_style(color="green", bold=True)
        assert isinstance(style, Style)
        assert style.color.name == "green"
        assert style.bold is True
        assert style.italic is False  # Default value
        assert style.underline is False  # Default value
