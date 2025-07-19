"""Input field component for elegant text entry."""

import re
from typing import Any, Callable, Optional

from rich.align import Align
from rich.panel import Panel
from rich.text import Text


class InputField:
    """Elegant input field component for text entry."""

    def __init__(
        self,
        title: str,
        placeholder: str = "",
        validator=None,
        theme=None,
        max_length: int = 500,
    ):
        """Initialize the input field."""
        self.title = title
        self.placeholder = placeholder
        self.validator = validator
        self.theme = theme
        self.max_length = max_length

        self.value = ""
        self.cursor_position = 0
        self.is_focused = True
        self.validation_message = ""
        self.is_valid = True

    def render(self):
        """Render the input field as a Rich Panel."""
        content = Text()

        # Add title
        title_style = (
            self.theme.get_style("input_focused")
            if self.is_focused
            else self.theme.get_style("text_primary")
        )
        title_text = Text(self.title, style=title_style)
        content.append(title_text)
        content.append("\n\n")

        # Create input line
        input_line = Text()

        # Add input box border
        if self.is_focused:
            border_char = "▶ "
            style = self.theme.get_style("input_focused")
        else:
            border_char = "  "
            style = self.theme.get_style("input_normal")

        input_line.append(border_char, style=style)

        # Add input content
        if self.value:
            # Show actual value with cursor
            for i, char in enumerate(self.value):
                if i == self.cursor_position and self.is_focused:
                    input_line.append(char, style=self.theme.get_style("input_focused"))
                else:
                    input_line.append(char, style=style)

            # Add cursor at end if needed
            if self.cursor_position >= len(self.value) and self.is_focused:
                input_line.append("█", style=self.theme.get_style("input_focused"))
        else:
            # Show placeholder
            if self.placeholder:
                input_line.append(
                    self.placeholder, style=self.theme.get_style("input_placeholder")
                )

            # Add cursor for empty field
            if self.is_focused:
                input_line.append("█", style=self.theme.get_style("input_focused"))

        content.append(input_line)
        content.append("\n")

        # Add validation message
        if self.validation_message:
            if self.is_valid:
                validation_style = self.theme.get_style("status_success")
                icon = "✓ "
            else:
                validation_style = self.theme.get_style("status_error")
                icon = "✗ "

            validation_text = Text()
            validation_text.append(icon, style=validation_style)
            validation_text.append(self.validation_message, style=validation_style)
            content.append(validation_text)
            content.append("\n")

        # Add help text
        help_text = Text()
        help_text.append(
            "Enter: Confirmar  ", style=self.theme.get_style("text_secondary")
        )
        help_text.append(
            "ESC: Cancelar  ", style=self.theme.get_style("text_secondary")
        )
        help_text.append(
            "Ctrl+A: Selecionar tudo", style=self.theme.get_style("text_secondary")
        )
        content.append(help_text)

        # Determine border style based on validation
        if not self.is_valid and self.validation_message:
            border_style = self.theme.error_color
        elif self.is_valid and self.validation_message:
            border_style = self.theme.success_color
        else:
            border_style = (
                self.theme.border_color if self.is_focused else self.theme.muted_color
            )

        return Panel(
            Align.left(content),
            border_style=border_style,
            style=self.theme.get_style("panel_border"),
            title_align="left",
            padding=(1, 2),
        )

    def handle_key(self, key: str):
        """Handle keyboard input."""
        if key == "enter":
            if self.is_valid:
                return self.value
            return None
        elif key == "escape":
            return ""
        elif key == "backspace":
            if self.cursor_position > 0:
                self.value = (
                    self.value[: self.cursor_position - 1]
                    + self.value[self.cursor_position :]
                )
                self.cursor_position -= 1
                self._validate()
        elif key == "delete":
            if self.cursor_position < len(self.value):
                self.value = (
                    self.value[: self.cursor_position]
                    + self.value[self.cursor_position + 1 :]
                )
                self._validate()
        elif key == "left":
            if self.cursor_position > 0:
                self.cursor_position -= 1
        elif key == "right":
            if self.cursor_position < len(self.value):
                self.cursor_position += 1
        elif key == "home":
            self.cursor_position = 0
        elif key == "end":
            self.cursor_position = len(self.value)
        elif key == "ctrl+a":
            self.cursor_position = len(self.value)
        elif len(key) == 1 and key.isprintable():
            if len(self.value) < self.max_length:
                self.value = (
                    self.value[: self.cursor_position]
                    + key
                    + self.value[self.cursor_position :]
                )
                self.cursor_position += 1
                self._validate()

        return None

    def _validate(self):
        """Validate the current input value."""
        if self.validator:
            self.is_valid, self.validation_message = self.validator(self.value)
        else:
            self.is_valid = True
            self.validation_message = ""

    def set_value(self, value: str):
        """Set the input value programmatically."""
        self.value = value[: self.max_length]
        self.cursor_position = len(self.value)
        self._validate()

    def get_value(self):
        """Get the current input value."""
        return self.value

    def clear(self):
        """Clear the input field."""
        self.value = ""
        self.cursor_position = 0
        self.validation_message = ""
        self.is_valid = True

    def focus(self):
        """Focus the input field."""
        self.is_focused = True

    def blur(self):
        """Remove focus from the input field."""
        self.is_focused = False

    def is_empty(self):
        """Check if the input field is empty."""
        return len(self.value.strip()) == 0


class YouTubeURLValidator:
    """Validator for YouTube URLs."""

    YOUTUBE_PATTERNS = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:&.*)?$",
        r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})(?:\?.*)?$",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:\?.*)?$",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})(?:\?.*)?$",
    ]

    @classmethod
    def validate(cls, url: str):
        """Validate a YouTube URL."""
        if not url.strip():
            return True, ""

        for pattern in cls.YOUTUBE_PATTERNS:
            if re.match(pattern, url.strip(), re.IGNORECASE):
                return True, "URL válida do YouTube"

        return False, "URL inválida. Use formato: youtube.com/watch?v=ID ou youtu.be/ID"

    @classmethod
    def extract_video_id(cls, url: str):
        """Extract video ID from YouTube URL."""
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.match(pattern, url.strip(), re.IGNORECASE)
            if match:
                return match.group(1)
        return None
