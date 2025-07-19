"""Tests for the base Screen class."""

from abc import ABC
from unittest.mock import AsyncMock, Mock

import pytest

from src.presentation.cli.screens.base_screen import Screen


class ConcreteScreen(Screen):
    """Concrete implementation of Screen for testing."""

    def __init__(self, cli):
        super().__init__(cli)
        self.render_called = False
        self.handle_input_called = False
        self.on_enter_called = False
        self.on_exit_called = False
        self.last_key = None

    async def render(self) -> None:
        """Test implementation of render."""
        self.render_called = True

    async def handle_input(self, key: str) -> None:
        """Test implementation of handle_input."""
        self.handle_input_called = True
        self.last_key = key

    async def on_enter(self) -> None:
        """Test implementation of on_enter."""
        self.on_enter_called = True

    async def on_exit(self) -> None:
        """Test implementation of on_exit."""
        self.on_exit_called = True


class TestScreen:
    """Tests for the base Screen class."""

    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI for testing."""
        cli = Mock()
        cli.theme = Mock()
        return cli

    @pytest.fixture
    def screen(self, mock_cli):
        """Create a concrete screen for testing."""
        return ConcreteScreen(mock_cli)

    def test_screen_is_abstract(self):
        """Test that Screen is an abstract base class."""
        assert issubclass(Screen, ABC)

        # Should not be able to instantiate Screen directly
        with pytest.raises(TypeError):
            Screen(Mock())

    def test_screen_initialization(self, screen, mock_cli):
        """Test screen initialization."""
        assert screen.cli == mock_cli
        assert screen.theme == mock_cli.theme

    @pytest.mark.asyncio
    async def test_render_method(self, screen):
        """Test the render method."""
        await screen.render()
        assert screen.render_called is True

    @pytest.mark.asyncio
    async def test_handle_input_method(self, screen):
        """Test the handle_input method."""
        test_key = "enter"
        await screen.handle_input(test_key)

        assert screen.handle_input_called is True
        assert screen.last_key == test_key

    @pytest.mark.asyncio
    async def test_on_enter_method(self, screen):
        """Test the on_enter method."""
        await screen.on_enter()
        assert screen.on_enter_called is True

    @pytest.mark.asyncio
    async def test_on_exit_method(self, screen):
        """Test the on_exit method."""
        await screen.on_exit()
        assert screen.on_exit_called is True

    @pytest.mark.asyncio
    async def test_lifecycle_methods_default_implementation(self, mock_cli):
        """Test that lifecycle methods have default implementations."""

        class MinimalScreen(Screen):
            """Minimal screen implementation."""

            async def render(self) -> None:
                pass

            async def handle_input(self, key: str) -> None:
                pass

        screen = MinimalScreen(mock_cli)

        # These should not raise exceptions
        await screen.on_enter()
        await screen.on_exit()

    def test_screen_attributes_access(self, screen, mock_cli):
        """Test accessing screen attributes."""
        # Should be able to access cli and theme
        assert hasattr(screen, 'cli')
        assert hasattr(screen, 'theme')

        # Should reference the same objects
        assert screen.cli is mock_cli
        assert screen.theme is mock_cli.theme

    @pytest.mark.asyncio
    async def test_multiple_method_calls(self, screen):
        """Test calling methods multiple times."""
        # Call render multiple times
        await screen.render()
        await screen.render()
        assert screen.render_called is True

        # Call handle_input with different keys
        await screen.handle_input("up")
        assert screen.last_key == "up"

        await screen.handle_input("down")
        assert screen.last_key == "down"

        # Call lifecycle methods
        await screen.on_enter()
        await screen.on_exit()
        assert screen.on_enter_called is True
        assert screen.on_exit_called is True
