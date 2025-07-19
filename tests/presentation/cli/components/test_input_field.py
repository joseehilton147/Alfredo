"""Tests for the InputField component and YouTube URL validator."""

from unittest.mock import Mock

import pytest

from src.presentation.cli.components.input_field import InputField, YouTubeURLValidator
from src.presentation.cli.themes.default_theme import DefaultTheme


class TestYouTubeURLValidator:
    """Test cases for YouTube URL validation."""

    def test_valid_youtube_urls(self):
        """Test validation of valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "www.youtube.com/watch?v=dQw4w9WgXcQ",
            "youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
        ]

        for url in valid_urls:
            is_valid, message = YouTubeURLValidator.validate(url)
            assert is_valid, f"URL should be valid: {url}"
            assert "válida" in message.lower()

    def test_invalid_youtube_urls(self):
        """Test validation of invalid YouTube URLs."""
        invalid_urls = [
            "https://vimeo.com/123456789",
            "https://www.dailymotion.com/video/x123456",
            "https://www.youtube.com/",
            "https://www.youtube.com/watch",
            "https://www.youtube.com/watch?v=",
            "https://www.youtube.com/watch?v=invalid",
            "https://youtu.be/",
            "not_a_url_at_all",
            "https://example.com",
            "youtube.com/watch?v=toolongvideoidhere123456",
        ]

        for url in invalid_urls:
            is_valid, message = YouTubeURLValidator.validate(url)
            assert not is_valid, f"URL should be invalid: {url}"
            assert "inválida" in message.lower()

    def test_empty_url_validation(self):
        """Test that empty URLs are considered valid (optional field)."""
        is_valid, message = YouTubeURLValidator.validate("")
        assert is_valid
        assert message == ""

        is_valid, message = YouTubeURLValidator.validate("   ")
        assert is_valid
        assert message == ""

    def test_video_id_extraction(self):
        """Test extraction of video IDs from URLs."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("youtube.com/watch?v=ABC123def45", "ABC123def45"),
            ("invalid_url", None),
            ("", None),
        ]

        for url, expected_id in test_cases:
            video_id = YouTubeURLValidator.extract_video_id(url)
            assert (
                video_id == expected_id
            ), f"Expected {expected_id} for URL {url}, got {video_id}"

    def test_case_insensitive_validation(self):
        """Test that URL validation is case insensitive."""
        urls = [
            "HTTPS://WWW.YOUTUBE.COM/WATCH?V=dQw4w9WgXcQ",
            "HTTPS://YOUTU.BE/dQw4w9WgXcQ",
            "YouTube.com/watch?v=dQw4w9WgXcQ",
        ]

        for url in urls:
            is_valid, message = YouTubeURLValidator.validate(url)
            assert is_valid, f"Case insensitive URL should be valid: {url}"


class TestInputField:
    """Test cases for the InputField component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.theme = DefaultTheme()
        self.mock_validator = Mock(return_value=(True, "Valid input"))

    def test_input_field_initialization(self):
        """Test InputField initialization."""
        field = InputField(
            title="Test Field",
            placeholder="Enter text",
            validator=self.mock_validator,
            theme=self.theme,
            max_length=100,
        )

        assert field.title == "Test Field"
        assert field.placeholder == "Enter text"
        assert field.validator == self.mock_validator
        assert field.theme == self.theme
        assert field.max_length == 100
        assert field.value == ""
        assert field.cursor_position == 0
        assert field.is_focused is True
        assert field.is_valid is True

    def test_character_input(self):
        """Test character input handling."""
        field = InputField("Test", theme=self.theme)

        # Test single character
        result = field.handle_key("a")
        assert result is None
        assert field.value == "a"
        assert field.cursor_position == 1

        # Test multiple characters
        field.handle_key("b")
        field.handle_key("c")
        assert field.value == "abc"
        assert field.cursor_position == 3

    def test_backspace_handling(self):
        """Test backspace key handling."""
        field = InputField("Test", theme=self.theme)
        field.set_value("hello")

        # Backspace at end
        field.handle_key("backspace")
        assert field.value == "hell"
        assert field.cursor_position == 4

        # Backspace in middle
        field.cursor_position = 2
        field.handle_key("backspace")
        assert field.value == "hll"
        assert field.cursor_position == 1

        # Backspace at beginning (should do nothing)
        field.cursor_position = 0
        field.handle_key("backspace")
        assert field.value == "hll"
        assert field.cursor_position == 0

    def test_cursor_movement(self):
        """Test cursor movement keys."""
        field = InputField("Test", theme=self.theme)
        field.set_value("hello")

        # Move left
        field.handle_key("left")
        assert field.cursor_position == 4

        field.handle_key("left")
        assert field.cursor_position == 3

        # Move right
        field.handle_key("right")
        assert field.cursor_position == 4

        # Home key
        field.handle_key("home")
        assert field.cursor_position == 0

        # End key
        field.handle_key("end")
        assert field.cursor_position == 5

    def test_enter_key_handling(self):
        """Test Enter key handling."""
        field = InputField("Test", theme=self.theme, validator=self.mock_validator)
        field.set_value("valid input")

        # Enter with valid input
        result = field.handle_key("enter")
        assert result == "valid input"

        # Enter with invalid input
        field.validator = Mock(return_value=(False, "Invalid"))
        field._validate()
        result = field.handle_key("enter")
        assert result is None

    def test_escape_key_handling(self):
        """Test Escape key handling."""
        field = InputField("Test", theme=self.theme)
        field.set_value("some text")

        result = field.handle_key("escape")
        assert result == ""  # Empty string indicates cancellation

    def test_max_length_enforcement(self):
        """Test maximum length enforcement."""
        field = InputField("Test", theme=self.theme, max_length=5)

        # Add characters up to limit
        for char in "hello":
            field.handle_key(char)

        assert field.value == "hello"
        assert len(field.value) == 5

        # Try to add more characters
        field.handle_key("!")
        assert field.value == "hello"  # Should not change
        assert len(field.value) == 5

    def test_validation_with_validator(self):
        """Test validation with custom validator."""

        def custom_validator(value):
            if len(value) < 3:
                return False, "Too short"
            return True, "Good length"

        field = InputField("Test", theme=self.theme, validator=custom_validator)

        # Test short input
        field.set_value("hi")
        assert not field.is_valid
        assert field.validation_message == "Too short"

        # Test valid input
        field.set_value("hello")
        assert field.is_valid
        assert field.validation_message == "Good length"

    def test_youtube_url_input_field(self):
        """Test InputField specifically configured for YouTube URLs."""
        field = InputField(
            title="YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            validator=YouTubeURLValidator.validate,
            theme=self.theme,
        )

        # Test valid YouTube URL
        field.set_value("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert field.is_valid
        assert "válida" in field.validation_message.lower()

        # Test invalid URL
        field.set_value("https://vimeo.com/123456")
        assert not field.is_valid
        assert "inválida" in field.validation_message.lower()

    def test_set_value_method(self):
        """Test programmatic value setting."""
        field = InputField("Test", theme=self.theme, max_length=10)

        field.set_value("hello world")
        assert field.value == "hello worl"  # Truncated to max_length
        assert field.cursor_position == 10

    def test_clear_method(self):
        """Test clearing the input field."""
        field = InputField("Test", theme=self.theme, validator=self.mock_validator)
        field.set_value("some text")
        field.validation_message = "Some message"

        field.clear()
        assert field.value == ""
        assert field.cursor_position == 0
        assert field.validation_message == ""
        assert field.is_valid is True

    def test_focus_methods(self):
        """Test focus and blur methods."""
        field = InputField("Test", theme=self.theme)

        # Test initial focus state
        assert field.is_focused is True

        # Test blur
        field.blur()
        assert field.is_focused is False

        # Test focus
        field.focus()
        assert field.is_focused is True

    def test_is_empty_method(self):
        """Test empty state checking."""
        field = InputField("Test", theme=self.theme)

        # Empty field
        assert field.is_empty() is True

        # Field with whitespace only
        field.set_value("   ")
        assert field.is_empty() is True

        # Field with content
        field.set_value("hello")
        assert field.is_empty() is False

    def test_delete_key_handling(self):
        """Test delete key handling."""
        field = InputField("Test", theme=self.theme)
        field.set_value("hello")
        field.cursor_position = 2  # Between 'e' and 'l'

        field.handle_key("delete")
        assert field.value == "helo"
        assert field.cursor_position == 2

        # Delete at end (should do nothing)
        field.cursor_position = 4
        field.handle_key("delete")
        assert field.value == "helo"
        assert field.cursor_position == 4

    def test_ctrl_a_handling(self):
        """Test Ctrl+A (select all) handling."""
        field = InputField("Test", theme=self.theme)
        field.set_value("hello")
        field.cursor_position = 2

        field.handle_key("ctrl+a")
        assert field.cursor_position == 5  # Moved to end (simulating select all)

    def test_render_method_returns_panel(self):
        """Test that render method returns a Rich Panel."""
        field = InputField("Test Field", theme=self.theme)
        panel = field.render()

        # Should return a Panel object
        from rich.panel import Panel

        assert isinstance(panel, Panel)

    def test_validation_on_input(self):
        """Test that validation is triggered on input."""
        validator_calls = []

        def tracking_validator(value):
            validator_calls.append(value)
            return True, f"Validated: {value}"

        field = InputField("Test", theme=self.theme, validator=tracking_validator)

        # Initial validation
        assert len(validator_calls) == 0

        # Add characters
        field.handle_key("a")
        assert "a" in validator_calls

        field.handle_key("b")
        assert "ab" in validator_calls

        # Backspace
        field.handle_key("backspace")
        assert "a" in validator_calls

    def test_special_characters_input(self):
        """Test input of special characters."""
        field = InputField("Test", theme=self.theme)

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        for char in special_chars:
            field.handle_key(char)

        assert field.value == special_chars

    def test_unicode_input(self):
        """Test input of Unicode characters."""
        field = InputField("Test", theme=self.theme)

        unicode_text = "café naïve résumé"
        for char in unicode_text:
            field.handle_key(char)

        assert field.value == unicode_text
