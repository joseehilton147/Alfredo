"""Tests for the InteractiveMenu component."""

from unittest.mock import MagicMock, Mock

import pytest

from src.presentation.cli.components.menu import InteractiveMenu, MenuOption
from src.presentation.cli.themes.default_theme import DefaultTheme


class TestMenuOption:
    """Tests for MenuOption dataclass."""

    def test_menu_option_creation(self):
        """Test creating a MenuOption."""
        action = Mock()
        option = MenuOption(
            key="test",
            label="Test Option",
            description="A test option",
            icon="🔧",
            action=action,
            enabled=True,
            shortcut="t"
        )

        assert option.key == "test"
        assert option.label == "Test Option"
        assert option.description == "A test option"
        assert option.icon == "🔧"
        assert option.action == action
        assert option.enabled is True
        assert option.shortcut == "t"

    def test_menu_option_defaults(self):
        """Test MenuOption with default values."""
        action = Mock()
        option = MenuOption(
            key="test",
            label="Test Option",
            description="A test option",
            icon="🔧",
            action=action
        )

        assert option.enabled is True
        assert option.shortcut is None


class TestInteractiveMenu:
    """Tests for InteractiveMenu component."""

    @pytest.fixture
    def theme(self):
        """Create a theme for testing."""
        return DefaultTheme()

    @pytest.fixture
    def sample_options(self):
        """Create sample menu options for testing."""
        return [
            MenuOption(
                key="option1",
                label="First Option",
                description="The first option",
                icon="1️⃣",
                action=Mock(),
                shortcut="1"
            ),
            MenuOption(
                key="option2",
                label="Second Option",
                description="The second option",
                icon="2️⃣",
                action=Mock(),
                shortcut="2"
            ),
            MenuOption(
                key="option3",
                label="Third Option",
                description="The third option",
                icon="3️⃣",
                action=Mock(),
                enabled=False,
                shortcut="3"
            )
        ]

    @pytest.fixture
    def menu(self, theme, sample_options):
        """Create a menu for testing."""
        return InteractiveMenu("Test Menu", sample_options, theme)

    def test_menu_initialization(self, menu, sample_options):
        """Test menu initialization."""
        assert menu.title == "Test Menu"
        assert menu.options == sample_options
        assert menu.selected_index == 0

    def test_render_returns_panel(self, menu):
        """Test that render returns a Rich Panel."""
        panel = menu.render()
        assert hasattr(panel, 'renderable')  # Rich Panel has renderable attribute

    def test_handle_key_down_navigation(self, menu):
        """Test down arrow key navigation."""
        initial_index = menu.selected_index
        result = menu.handle_key("down")

        assert result is None  # Navigation doesn't return option
        assert menu.selected_index != initial_index  # Index should change

    def test_handle_key_up_navigation(self, menu):
        """Test up arrow key navigation."""
        menu.selected_index = 1  # Start at second option
        result = menu.handle_key("up")

        assert result is None
        assert menu.selected_index == 0

    def test_handle_key_enter_selection(self, menu):
        """Test Enter key selection."""
        menu.selected_index = 0  # Select first option
        result = menu.handle_key("enter")

        assert result is not None
        assert result == menu.options[0]

    def test_handle_key_space_selection(self, menu):
        """Test Space key selection."""
        menu.selected_index = 1  # Select second option
        result = menu.handle_key(" ")

        assert result is not None
        assert result == menu.options[1]

    def test_handle_key_numeric_shortcut(self, menu):
        """Test numeric shortcut selection."""
        result = menu.handle_key("2")

        assert result is not None
        assert result == menu.options[1]  # Second option (index 1)
        assert menu.selected_index == 1

    def test_handle_key_letter_shortcut(self, menu):
        """Test letter shortcut selection."""
        # Add option with letter shortcut
        letter_option = MenuOption(
            key="letter",
            label="Letter Option",
            description="Option with letter shortcut",
            icon="📝",
            action=Mock(),
            shortcut="l"
        )
        menu.options.append(letter_option)

        result = menu.handle_key("l")

        assert result is not None
        assert result == letter_option

    def test_handle_key_disabled_option(self, menu):
        """Test that disabled options cannot be selected."""
        # Try to select disabled option (index 2)
        result = menu.handle_key("3")

        assert result is None  # Should not return disabled option

    def test_handle_key_vim_navigation(self, menu):
        """Test vim-style navigation keys."""
        # Test 'j' for down
        initial_index = menu.selected_index
        menu.handle_key("j")
        assert menu.selected_index != initial_index

        # Test 'k' for up
        menu.handle_key("k")
        assert menu.selected_index == initial_index

    def test_move_selection_skips_disabled(self, menu):
        """Test that navigation skips disabled options."""
        menu.selected_index = 1  # Start at enabled option

        # Move down - should skip disabled option at index 2
        menu._move_selection(1)

        # Should wrap around to first option since third is disabled
        assert menu.selected_index == 0

    def test_get_selected_option_enabled(self, menu):
        """Test getting selected option when enabled."""
        menu.selected_index = 0
        option = menu._get_selected_option()

        assert option is not None
        assert option == menu.options[0]

    def test_get_selected_option_disabled(self, menu):
        """Test getting selected option when disabled."""
        menu.selected_index = 2  # Disabled option
        option = menu._get_selected_option()

        assert option is None

    def test_get_selected_index(self, menu):
        """Test getting selected index."""
        menu.selected_index = 1
        assert menu.get_selected_index() == 1

    def test_set_selected_index(self, menu):
        """Test setting selected index."""
        menu.set_selected_index(1)
        assert menu.selected_index == 1

    def test_set_selected_index_invalid(self, menu):
        """Test setting invalid selected index."""
        original_index = menu.selected_index
        menu.set_selected_index(-1)
        assert menu.selected_index == original_index

        menu.set_selected_index(999)
        assert menu.selected_index == original_index

    def test_enable_option(self, menu):
        """Test enabling a disabled option."""
        menu.enable_option(2)  # Enable third option
        assert menu.options[2].enabled is True

    def test_disable_option(self, menu):
        """Test disabling an enabled option."""
        menu.disable_option(0)  # Disable first option
        assert menu.options[0].enabled is False

    def test_enable_disable_invalid_index(self, menu):
        """Test enable/disable with invalid indices."""
        # Should not raise exceptions
        menu.enable_option(-1)
        menu.enable_option(999)
        menu.disable_option(-1)
        menu.disable_option(999)

    def test_navigation_with_all_disabled(self):
        """Test navigation when all options are disabled."""
        theme = DefaultTheme()
        disabled_options = [
            MenuOption("1", "Option 1", "Desc 1", "🔧", Mock(), enabled=False),
            MenuOption("2", "Option 2", "Desc 2", "🔧", Mock(), enabled=False)
        ]
        menu = InteractiveMenu("Test", disabled_options, theme)

        original_index = menu.selected_index
        menu._move_selection(1)

        # Should not change when all options are disabled
        assert menu.selected_index == original_index

    def test_empty_options_list(self):
        """Test menu with empty options list."""
        theme = DefaultTheme()
        menu = InteractiveMenu("Empty Menu", [], theme)

        # Should not crash
        panel = menu.render()
        assert panel is not None

        # Navigation should not crash
        menu.handle_key("down")
        menu.handle_key("up")

        # Selection should return None
        result = menu.handle_key("enter")
        assert result is None
