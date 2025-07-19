"""Keyboard input handling utilities for the CLI."""

import sys
from typing import Optional

# Platform-specific imports
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    # Windows doesn't have termios
    HAS_TERMIOS = False

# Windows-specific imports
if sys.platform == 'win32':
    try:
        import msvcrt
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False
else:
    HAS_MSVCRT = False


class KeyboardHandler:
    """Handles keyboard input for the interactive CLI."""

    # Special key codes
    ESC = '\x1b'
    ENTER = '\r'
    BACKSPACE = '\x7f'
    TAB = '\t'
    SPACE = ' '

    # Arrow keys (escape sequences)
    ARROW_UP = '\x1b[A'
    ARROW_DOWN = '\x1b[B'
    ARROW_RIGHT = '\x1b[C'
    ARROW_LEFT = '\x1b[D'

    # Function keys
    F1 = '\x1bOP'
    F2 = '\x1bOQ'
    F3 = '\x1bOR'
    F4 = '\x1bOS'

    def __init__(self):
        """Initialize the keyboard handler."""
        self._original_settings = None

    def setup_terminal(self) -> None:
        """Setup terminal for raw input mode."""
        if not sys.stdin.isatty():
            return

        if HAS_TERMIOS:
            # Unix/Linux/macOS
            self._original_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        elif HAS_MSVCRT:
            # Windows - no setup needed for msvcrt
            pass

    def restore_terminal(self) -> None:
        """Restore terminal to original settings."""
        if not sys.stdin.isatty():
            return

        if HAS_TERMIOS and self._original_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._original_settings)
        elif HAS_MSVCRT:
            # Windows - no restore needed for msvcrt
            pass

    def read_key(self) -> str:
        """Read a single key from stdin.

        Returns:
            The key that was pressed
        """
        if not sys.stdin.isatty():
            # For testing or non-interactive environments
            return input()

        if HAS_MSVCRT:
            # Windows implementation using msvcrt
            return self._read_key_windows()
        elif HAS_TERMIOS:
            # Unix/Linux/macOS implementation
            return self._read_key_unix()
        else:
            # Fallback for unsupported platforms
            return input()

    def _read_key_windows(self) -> str:
        """Read key on Windows using msvcrt."""
        import msvcrt

        key = msvcrt.getch()

        # Handle special keys on Windows
        if key == b'\x00' or key == b'\xe0':  # Special key prefix
            key2 = msvcrt.getch()
            # Map Windows special keys to our constants
            if key2 == b'H':  # Up arrow
                return self.ARROW_UP
            elif key2 == b'P':  # Down arrow
                return self.ARROW_DOWN
            elif key2 == b'K':  # Left arrow
                return self.ARROW_LEFT
            elif key2 == b'M':  # Right arrow
                return self.ARROW_RIGHT
            elif key2 == b';':  # F1
                return self.F1
            elif key2 == b'<':  # F2
                return self.F2
            elif key2 == b'=':  # F3
                return self.F3
            elif key2 == b'>':  # F4
                return self.F4
            else:
                # Unknown special key
                return key.decode('utf-8', errors='ignore')

        # Regular key
        return key.decode('utf-8', errors='ignore')

    def _read_key_unix(self) -> str:
        """Read key on Unix/Linux/macOS."""
        key = sys.stdin.read(1)

        # Handle escape sequences (arrow keys, function keys, etc.)
        if key == self.ESC:
            # Read the next characters to determine the full sequence
            try:
                next_char = sys.stdin.read(1)
                if next_char == '[':
                    # Arrow keys and other sequences
                    third_char = sys.stdin.read(1)
                    return self.ESC + next_char + third_char
                elif next_char == 'O':
                    # Function keys
                    third_char = sys.stdin.read(1)
                    return self.ESC + next_char + third_char
                else:
                    # Just ESC followed by another character
                    return key
            except:
                # If we can't read more characters, just return ESC
                return key

        return key

    def is_arrow_key(self, key: str) -> bool:
        """Check if the key is an arrow key.

        Args:
            key: The key to check

        Returns:
            True if it's an arrow key
        """
        return key in [self.ARROW_UP, self.ARROW_DOWN, self.ARROW_LEFT, self.ARROW_RIGHT]

    def is_function_key(self, key: str) -> bool:
        """Check if the key is a function key.

        Args:
            key: The key to check

        Returns:
            True if it's a function key
        """
        return key in [self.F1, self.F2, self.F3, self.F4]

    def get_key_name(self, key: str) -> str:
        """Get a human-readable name for a key.

        Args:
            key: The key code

        Returns:
            Human-readable key name
        """
        key_names = {
            self.ESC: 'ESC',
            self.ENTER: 'ENTER',
            self.BACKSPACE: 'BACKSPACE',
            self.TAB: 'TAB',
            self.SPACE: 'SPACE',
            self.ARROW_UP: 'UP',
            self.ARROW_DOWN: 'DOWN',
            self.ARROW_LEFT: 'LEFT',
            self.ARROW_RIGHT: 'RIGHT',
            self.F1: 'F1',
            self.F2: 'F2',
            self.F3: 'F3',
            self.F4: 'F4',
        }

        return key_names.get(key, key if len(key) == 1 else f'UNKNOWN({repr(key)})')


class MockKeyboardHandler(KeyboardHandler):
    """Mock keyboard handler for testing."""

    def __init__(self, key_sequence: Optional[list] = None):
        """Initialize mock handler with predefined key sequence.

        Args:
            key_sequence: List of keys to simulate
        """
        super().__init__()
        self.key_sequence = key_sequence or []
        self.key_index = 0

    def setup_terminal(self) -> None:
        """Mock setup - does nothing."""
        pass

    def restore_terminal(self) -> None:
        """Mock restore - does nothing."""
        pass

    def read_key(self) -> str:
        """Read next key from the predefined sequence.

        Returns:
            Next key in sequence or ESC if sequence is exhausted
        """
        if self.key_index < len(self.key_sequence):
            key = self.key_sequence[self.key_index]
            self.key_index += 1
            return key
        return self.ESC  # Default to ESC when sequence is exhausted

    def add_keys(self, keys: list) -> None:
        """Add more keys to the sequence.

        Args:
            keys: List of keys to add
        """
        self.key_sequence.extend(keys)
