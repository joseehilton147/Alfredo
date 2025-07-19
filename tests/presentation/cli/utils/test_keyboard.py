"""Tests for keyboard input handling utilities."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from src.presentation.cli.utils.keyboard import KeyboardHandler, MockKeyboardHandler


class TestKeyboardHandler:
    """Test cases for KeyboardHandler."""

    def setup_method(self):
        """Setup test fixtures."""
        self.handler = KeyboardHandler()

    def test_initialization(self):
        """Test KeyboardHandler initialization."""
        assert self.handler._original_settings is None

    def test_key_constants(self):
        """Test that key constants are defined correctly."""
        assert KeyboardHandler.ESC == '\x1b'
        assert KeyboardHandler.ENTER == '\r'
        assert KeyboardHandler.BACKSPACE == '\x7f'
        assert KeyboardHandler.TAB == '\t'
        assert KeyboardHandler.SPACE == ' '
        assert KeyboardHandler.ARROW_UP == '\x1b[A'
        assert KeyboardHandler.ARROW_DOWN == '\x1b[B'
        assert KeyboardHandler.ARROW_RIGHT == '\x1b[C'
        assert KeyboardHandler.ARROW_LEFT == '\x1b[D'
        assert KeyboardHandler.F1 == '\x1bOP'
        assert KeyboardHandler.F2 == '\x1bOQ'
        assert KeyboardHandler.F3 == '\x1bOR'
        assert KeyboardHandler.F4 == '\x1bOS'

    def test_is_arrow_key(self):
        """Test arrow key detection."""
        assert self.handler.is_arrow_key(KeyboardHandler.ARROW_UP)
        assert self.handler.is_arrow_key(KeyboardHandler.ARROW_DOWN)
        assert self.handler.is_arrow_key(KeyboardHandler.ARROW_LEFT)
        assert self.handler.is_arrow_key(KeyboardHandler.ARROW_RIGHT)

        assert not self.handler.is_arrow_key('a')
        assert not self.handler.is_arrow_key(KeyboardHandler.ESC)
        assert not self.handler.is_arrow_key(KeyboardHandler.F1)

    def test_is_function_key(self):
        """Test function key detection."""
        assert self.handler.is_function_key(KeyboardHandler.F1)
        assert self.handler.is_function_key(KeyboardHandler.F2)
        assert self.handler.is_function_key(KeyboardHandler.F3)
        assert self.handler.is_function_key(KeyboardHandler.F4)

        assert not self.handler.is_function_key('a')
        assert not self.handler.is_function_key(KeyboardHandler.ESC)
        assert not self.handler.is_function_key(KeyboardHandler.ARROW_UP)

    def test_get_key_name(self):
        """Test getting human-readable key names."""
        assert self.handler.get_key_name(KeyboardHandler.ESC) == 'ESC'
        assert self.handler.get_key_name(KeyboardHandler.ENTER) == 'ENTER'
        assert self.handler.get_key_name(KeyboardHandler.BACKSPACE) == 'BACKSPACE'
        assert self.handler.get_key_name(KeyboardHandler.TAB) == 'TAB'
        assert self.handler.get_key_name(KeyboardHandler.SPACE) == 'SPACE'
        assert self.handler.get_key_name(KeyboardHandler.ARROW_UP) == 'UP'
        assert self.handler.get_key_name(KeyboardHandler.ARROW_DOWN) == 'DOWN'
        assert self.handler.get_key_name(KeyboardHandler.ARROW_LEFT) == 'LEFT'
        assert self.handler.get_key_name(KeyboardHandler.ARROW_RIGHT) == 'RIGHT'
        assert self.handler.get_key_name(KeyboardHandler.F1) == 'F1'
        assert self.handler.get_key_name(KeyboardHandler.F2) == 'F2'
        assert self.handler.get_key_name(KeyboardHandler.F3) == 'F3'
        assert self.handler.get_key_name(KeyboardHandler.F4) == 'F4'

        # Regular characters
        assert self.handler.get_key_name('a') == 'a'
        assert self.handler.get_key_name('1') == '1'

        # Unknown sequences
        unknown_key = '\x1b[Z'
        result = self.handler.get_key_name(unknown_key)
        assert 'UNKNOWN' in result

    @patch('sys.stdin.isatty')
    def test_setup_terminal_non_tty(self, mock_isatty):
        """Test terminal setup when not a TTY."""
        mock_isatty.return_value = False

        # Should not raise an error
        self.handler.setup_terminal()
        assert self.handler._original_settings is None

    @patch('sys.stdin.isatty')
    def test_restore_terminal_non_tty(self, mock_isatty):
        """Test terminal restore when not a TTY."""
        mock_isatty.return_value = False

        # Should not raise an error
        self.handler.restore_terminal()

    @patch('sys.stdin.isatty')
    @patch('sys.stdin.read')
    def test_read_key_non_tty(self, mock_read, mock_isatty):
        """Test reading key when not a TTY."""
        mock_isatty.return_value = False

        with patch('builtins.input', return_value='test_input'):
            result = self.handler.read_key()
            assert result == 'test_input'

    @patch('sys.stdin.isatty')
    def test_read_key_simple_character(self, mock_isatty):
        """Test reading a simple character."""
        mock_isatty.return_value = True

        # Mock the appropriate method based on platform
        if sys.platform == 'win32':
            with patch('msvcrt.getch', return_value=b'a'):
                result = self.handler.read_key()
                assert result == 'a'
        else:
            with patch('sys.stdin.read', return_value='a'):
                result = self.handler.read_key()
                assert result == 'a'

    @patch('sys.stdin.isatty')
    def test_read_key_escape_sequence(self, mock_isatty):
        """Test reading escape sequences."""
        mock_isatty.return_value = True

        # Mock the appropriate method based on platform
        if sys.platform == 'win32':
            # On Windows, arrow up is represented differently
            with patch('msvcrt.getch', side_effect=[b'\xe0', b'H']):
                result = self.handler.read_key()
                assert result == KeyboardHandler.ARROW_UP
        else:
            # Unix/Linux/macOS
            with patch('sys.stdin.read', side_effect=['\x1b', '[', 'A']):
                result = self.handler.read_key()
                assert result == '\x1b[A'  # ARROW_UP

    @patch('sys.stdin.isatty')
    def test_read_key_function_key_sequence(self, mock_isatty):
        """Test reading function key sequences."""
        mock_isatty.return_value = True

        # Mock the appropriate method based on platform
        if sys.platform == 'win32':
            # On Windows, F1 is represented differently
            with patch('msvcrt.getch', side_effect=[b'\x00', b';']):
                result = self.handler.read_key()
                assert result == KeyboardHandler.F1
        else:
            # Unix/Linux/macOS
            with patch('sys.stdin.read', side_effect=['\x1b', 'O', 'P']):
                result = self.handler.read_key()
                assert result == '\x1bOP'  # F1

    @patch('sys.stdin.isatty')
    def test_read_key_escape_only(self, mock_isatty):
        """Test reading just ESC key."""
        mock_isatty.return_value = True

        # Mock the appropriate method based on platform
        if sys.platform == 'win32':
            # On Windows, ESC is just the escape character
            with patch('msvcrt.getch', return_value=b'\x1b'):
                result = self.handler.read_key()
                assert result == '\x1b'  # Just ESC
        else:
            # Unix/Linux/macOS - Mock reading ESC followed by exception (timeout)
            with patch('sys.stdin.read', side_effect=['\x1b', Exception("Timeout")]):
                result = self.handler.read_key()
                assert result == '\x1b'  # Just ESC


class TestMockKeyboardHandler:
    """Test cases for MockKeyboardHandler."""

    def test_initialization_empty(self):
        """Test MockKeyboardHandler initialization without key sequence."""
        handler = MockKeyboardHandler()

        assert handler.key_sequence == []
        assert handler.key_index == 0

    def test_initialization_with_sequence(self):
        """Test MockKeyboardHandler initialization with key sequence."""
        keys = ['a', 'b', KeyboardHandler.ESC]
        handler = MockKeyboardHandler(keys)

        assert handler.key_sequence == keys
        assert handler.key_index == 0

    def test_setup_and_restore_terminal(self):
        """Test mock setup and restore methods."""
        handler = MockKeyboardHandler()

        # Should not raise errors
        handler.setup_terminal()
        handler.restore_terminal()

    def test_read_key_from_sequence(self):
        """Test reading keys from predefined sequence."""
        keys = ['a', 'b', 'c']
        handler = MockKeyboardHandler(keys)

        assert handler.read_key() == 'a'
        assert handler.read_key() == 'b'
        assert handler.read_key() == 'c'

        # After sequence is exhausted, should return ESC
        assert handler.read_key() == KeyboardHandler.ESC
        assert handler.read_key() == KeyboardHandler.ESC

    def test_add_keys(self):
        """Test adding keys to the sequence."""
        handler = MockKeyboardHandler(['a'])

        assert handler.read_key() == 'a'
        assert handler.read_key() == KeyboardHandler.ESC  # Exhausted

        # Add more keys
        handler.add_keys(['b', 'c'])

        # Should continue from where it left off
        assert handler.read_key() == 'b'
        assert handler.read_key() == 'c'
        assert handler.read_key() == KeyboardHandler.ESC  # Exhausted again

    def test_key_index_tracking(self):
        """Test that key index is tracked correctly."""
        keys = ['x', 'y', 'z']
        handler = MockKeyboardHandler(keys)

        assert handler.key_index == 0

        handler.read_key()
        assert handler.key_index == 1

        handler.read_key()
        assert handler.key_index == 2

        handler.read_key()
        assert handler.key_index == 3

        # Index should not increment beyond sequence length
        handler.read_key()
        assert handler.key_index == 3

    def test_inheritance(self):
        """Test that MockKeyboardHandler inherits from KeyboardHandler."""
        handler = MockKeyboardHandler()

        assert isinstance(handler, KeyboardHandler)

        # Should have access to parent methods
        assert handler.is_arrow_key(KeyboardHandler.ARROW_UP)
        assert handler.get_key_name('a') == 'a'

    def test_mixed_key_types(self):
        """Test handling different types of keys."""
        keys = [
            'a',  # Regular character
            KeyboardHandler.ESC,  # Special key
            KeyboardHandler.ARROW_UP,  # Arrow key
            KeyboardHandler.F1,  # Function key
            '1',  # Number
            KeyboardHandler.ENTER  # Enter key
        ]
        handler = MockKeyboardHandler(keys)

        for expected_key in keys:
            assert handler.read_key() == expected_key

        # After sequence, should return ESC
        assert handler.read_key() == KeyboardHandler.ESC
