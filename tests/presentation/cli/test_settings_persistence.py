"""Tests for settings persistence functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.presentation.cli.context import ApplicationContext


class TestSettingsPersistence:
    """Test cases for settings persistence to .env file."""

    def test_load_settings_from_env_file(self):
        """Test loading settings from .env file."""
        env_content = """
# Test .env file
WHISPER_MODEL=small
DEFAULT_LANGUAGE=en
OUTPUT_DIR=/custom/output
INPUT_DIR=/custom/input
LOG_LEVEL=DEBUG
"""

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=env_content)):
                with patch.dict(
                    os.environ, {}, clear=True
                ):  # Clear env vars to test file loading
                    context = ApplicationContext()

                    assert context.get_setting("WHISPER_MODEL") == "small"
                    assert context.get_setting("DEFAULT_LANGUAGE") == "en"
                    assert context.get_setting("OUTPUT_DIR") == "/custom/output"
                    assert context.get_setting("INPUT_DIR") == "/custom/input"
                    assert context.get_setting("LOG_LEVEL") == "DEBUG"

    def test_load_settings_with_comments_and_empty_lines(self):
        """Test loading settings with comments and empty lines."""
        env_content = """
# Alfredo AI Configuration
# This is a comment

WHISPER_MODEL=base
# Another comment
DEFAULT_LANGUAGE=pt

# Empty line above
OUTPUT_DIR=data/output
"""

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=env_content)):
                context = ApplicationContext()

                assert context.get_setting("WHISPER_MODEL") == "base"
                assert context.get_setting("DEFAULT_LANGUAGE") == "pt"
                assert context.get_setting("OUTPUT_DIR") == "data/output"

    def test_load_settings_with_quoted_values(self):
        """Test loading settings with quoted values."""
        env_content = """
WHISPER_MODEL="base"
DEFAULT_LANGUAGE='pt'
OUTPUT_DIR="/path/with spaces/output"
"""

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=env_content)):
                context = ApplicationContext()

                assert context.get_setting("WHISPER_MODEL") == "base"
                assert context.get_setting("DEFAULT_LANGUAGE") == "pt"
                assert context.get_setting("OUTPUT_DIR") == "/path/with spaces/output"

    def test_environment_variables_override_env_file(self):
        """Test that environment variables override .env file values."""
        env_content = """
WHISPER_MODEL=base
DEFAULT_LANGUAGE=pt
"""

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=env_content)):
                with patch.dict(
                    os.environ, {"WHISPER_MODEL": "large", "DEFAULT_LANGUAGE": "en"}
                ):
                    context = ApplicationContext()

                    # Environment variables should override .env file
                    assert context.get_setting("WHISPER_MODEL") == "large"
                    assert context.get_setting("DEFAULT_LANGUAGE") == "en"

    def test_default_values_when_no_env_file(self):
        """Test default values when no .env file exists."""
        with patch("pathlib.Path.exists", return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                context = ApplicationContext()

                # Should use default values
                assert context.get_setting("WHISPER_MODEL") == "base"
                assert context.get_setting("DEFAULT_LANGUAGE") == "pt"
                assert context.get_setting("OUTPUT_DIR") == "data/output"
                assert context.get_setting("INPUT_DIR") == "data/input"
                assert context.get_setting("LOG_LEVEL") == "INFO"

    def test_save_settings_to_new_env_file(self):
        """Test saving settings to a new .env file."""
        context = ApplicationContext()
        context.update_setting("WHISPER_MODEL", "small")
        context.update_setting("DEFAULT_LANGUAGE", "en")
        context.update_setting("OUTPUT_DIR", "/new/output")

        mock_file = mock_open()
        with patch("pathlib.Path.exists", return_value=False):
            with patch("builtins.open", mock_file):
                context.save_settings_to_env()

                # Verify file was written
                mock_file.assert_called_once_with(Path(".env"), "w", encoding="utf-8")

                # Get written content from writelines call
                written_lines = mock_file().writelines.call_args[0][0]
                written_content = "".join(written_lines)

                # Verify settings were written
                assert "WHISPER_MODEL=small" in written_content
                assert "DEFAULT_LANGUAGE=en" in written_content
                assert "OUTPUT_DIR=/new/output" in written_content

    def test_save_settings_update_existing_env_file(self):
        """Test updating existing .env file while preserving comments."""
        existing_content = """# Alfredo AI Configuration
WHISPER_MODEL=base
# Language setting
DEFAULT_LANGUAGE=pt
OUTPUT_DIR=data/output

# End of file
"""

        context = ApplicationContext()
        context.update_setting("WHISPER_MODEL", "large")
        context.update_setting("DEFAULT_LANGUAGE", "en")
        context.update_setting("NEW_SETTING", "new_value")

        mock_file = mock_open(read_data=existing_content)
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_file):
                context.save_settings_to_env()

                # Get written content
                written_lines = mock_file().writelines.call_args[0][0]
                written_content = "".join(written_lines)

                # Verify comments were preserved
                assert "# Alfredo AI Configuration" in written_content
                assert "# Language setting" in written_content
                assert "# End of file" in written_content

                # Verify settings were updated
                assert "WHISPER_MODEL=large" in written_content
                assert "DEFAULT_LANGUAGE=en" in written_content
                assert "NEW_SETTING=new_value" in written_content

                # Verify old values were replaced
                assert "WHISPER_MODEL=base" not in written_content
                assert "DEFAULT_LANGUAGE=pt" not in written_content

    def test_save_settings_error_handling(self):
        """Test error handling when saving settings fails."""
        context = ApplicationContext()
        context.update_setting("WHISPER_MODEL", "small")

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(RuntimeError, match="Erro ao salvar configurações"):
                context.save_settings_to_env()

    def test_create_directories(self):
        """Test directory creation functionality."""
        context = ApplicationContext()
        context.update_setting("OUTPUT_DIR", "/test/output")
        context.update_setting("INPUT_DIR", "/test/input")

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            context.create_directories()

            # Verify directories were created
            assert mock_mkdir.call_count >= 2

            # Check that mkdir was called with parents=True, exist_ok=True
            for call in mock_mkdir.call_args_list:
                assert call.kwargs.get("parents") is True
                assert call.kwargs.get("exist_ok") is True

    def test_get_supported_languages(self):
        """Test getting supported languages from whisper provider."""
        context = ApplicationContext()

        # Mock whisper provider
        context.whisper_provider.get_supported_languages = lambda: [
            "en",
            "pt",
            "es",
            "fr",
        ]

        languages = context.get_supported_languages()

        assert isinstance(languages, dict)
        assert "en" in languages
        assert "pt" in languages
        assert languages["en"] == "English"
        assert languages["pt"] == "Português"

    def test_get_whisper_models(self):
        """Test getting available Whisper models."""
        context = ApplicationContext()

        models = context.get_whisper_models()

        assert isinstance(models, dict)
        assert "tiny" in models
        assert "base" in models
        assert "small" in models
        assert "medium" in models
        assert "large" in models

        # Verify descriptions
        assert "39 MB" in models["tiny"]
        assert "74 MB" in models["base"]

    def test_validate_configuration_valid(self):
        """Test configuration validation with valid settings."""
        context = ApplicationContext()

        with patch("pathlib.Path.mkdir"):
            with patch("pathlib.Path.write_text"):
                with patch("pathlib.Path.unlink"):
                    errors = context.validate_configuration()

                    assert errors == []

    def test_validate_configuration_invalid_output_dir(self):
        """Test configuration validation with invalid output directory."""
        context = ApplicationContext()
        context.update_setting("OUTPUT_DIR", "/invalid/readonly/path")

        with patch(
            "pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            errors = context.validate_configuration()

            assert len(errors) > 0
            assert any("não é gravável" in error for error in errors)

    def test_validate_configuration_invalid_model(self):
        """Test configuration validation with invalid Whisper model."""
        context = ApplicationContext()
        context.update_setting("WHISPER_MODEL", "invalid_model")

        with patch("pathlib.Path.mkdir"):
            with patch("pathlib.Path.write_text"):
                with patch("pathlib.Path.unlink"):
                    errors = context.validate_configuration()

                    assert len(errors) > 0
                    assert any("Modelo Whisper inválido" in error for error in errors)

    def test_validate_configuration_invalid_language(self):
        """Test configuration validation with invalid language."""
        context = ApplicationContext()
        context.update_setting("DEFAULT_LANGUAGE", "invalid_lang")

        # Mock supported languages
        context.get_supported_languages = lambda: {"en": "English", "pt": "Português"}

        with patch("pathlib.Path.mkdir"):
            with patch("pathlib.Path.write_text"):
                with patch("pathlib.Path.unlink"):
                    errors = context.validate_configuration()

                    assert len(errors) > 0
                    assert any("Idioma padrão inválido" in error for error in errors)


class TestSettingsIntegration:
    """Integration tests for settings with real file system."""

    def test_real_env_file_operations(self):
        """Test real .env file operations with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"

            # Create initial .env file
            initial_content = """# Test configuration
WHISPER_MODEL=base
DEFAULT_LANGUAGE=pt
"""
            env_file.write_text(initial_content)

            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Load settings
                context = ApplicationContext()
                assert context.get_setting("WHISPER_MODEL") == "base"
                assert context.get_setting("DEFAULT_LANGUAGE") == "pt"

                # Update settings
                context.update_setting("WHISPER_MODEL", "small")
                context.update_setting("DEFAULT_LANGUAGE", "en")
                context.update_setting("NEW_SETTING", "test_value")

                # Save settings
                context.save_settings_to_env()

                # Verify file was updated
                updated_content = env_file.read_text()
                assert "WHISPER_MODEL=small" in updated_content
                assert "DEFAULT_LANGUAGE=en" in updated_content
                assert "NEW_SETTING=test_value" in updated_content
                assert "# Test configuration" in updated_content  # Comment preserved

            finally:
                os.chdir(original_cwd)

    def test_directory_creation_integration(self):
        """Test directory creation with real file system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory so relative paths work correctly
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                context = ApplicationContext()

                # Set custom directories
                output_dir = Path(temp_dir) / "custom_output"
                input_dir = Path(temp_dir) / "custom_input"

                context.update_setting("OUTPUT_DIR", str(output_dir))
                context.update_setting("INPUT_DIR", str(input_dir))

                # Create directories
                context.create_directories()

                # Verify directories were created
                assert output_dir.exists()
                assert input_dir.exists()
                assert (Path(temp_dir) / "data" / "logs").exists()
                assert (Path(temp_dir) / "data" / "temp").exists()
                assert (Path(temp_dir) / "data" / "cache").exists()

            finally:
                os.chdir(original_cwd)
