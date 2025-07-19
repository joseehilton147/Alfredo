"""Application context for dependency injection in the CLI."""

import os
from pathlib import Path
from typing import Optional

from src.application.use_cases.transcribe_audio import TranscribeAudioUseCase
from src.infrastructure.providers.whisper_provider import WhisperProvider
from src.infrastructure.repositories.json_video_repository import JsonVideoRepository


class ApplicationContext:
    """Application context for dependency injection."""

    def __init__(self):
        """Initialize the application context with all dependencies."""
        # Load settings from environment
        self.settings = self._load_settings()

        # Initialize repositories
        self.video_repository = JsonVideoRepository(
            base_path=self.settings.get("OUTPUT_DIR", "data/output")
        )

        # Initialize providers
        self.whisper_provider = WhisperProvider(
            model_name=self.settings.get("WHISPER_MODEL", "base")
        )

        # Initialize use cases
        self.transcribe_use_case = TranscribeAudioUseCase(
            video_repository=self.video_repository,
            ai_provider=self.whisper_provider
        )

    def _load_settings(self) -> dict:
        """Load settings from environment variables and .env file.

        Returns:
            Dictionary with application settings
        """
        settings = {}

        # Try to load from .env file
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            settings[key.strip()] = value.strip().strip('"\'')
            except Exception:
                pass  # Ignore errors loading .env file

        # Override with environment variables
        settings.update({
            "WHISPER_MODEL": os.getenv("WHISPER_MODEL", settings.get("WHISPER_MODEL", "base")),
            "DEFAULT_LANGUAGE": os.getenv("DEFAULT_LANGUAGE", settings.get("DEFAULT_LANGUAGE", "pt")),
            "OUTPUT_DIR": os.getenv("OUTPUT_DIR", settings.get("OUTPUT_DIR", "data/output")),
            "INPUT_DIR": os.getenv("INPUT_DIR", settings.get("INPUT_DIR", "data/input")),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", settings.get("LOG_LEVEL", "INFO")),
        })

        return settings

    def get_setting(self, key: str, default=None):
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def update_setting(self, key: str, value: str) -> None:
        """Update a setting value.

        Args:
            key: Setting key
            value: New value
        """
        self.settings[key] = value

    def save_settings_to_env(self) -> None:
        """Save current settings to .env file."""
        try:
            env_file = Path(".env")

            # Read existing content to preserve comments and structure
            existing_lines = []
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    existing_lines = f.readlines()

            # Update or add settings
            updated_lines = []
            updated_keys = set()

            for line in existing_lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    key = stripped.split("=", 1)[0].strip()
                    if key in self.settings:
                        # Update existing setting
                        updated_lines.append(f"{key}={self.settings[key]}\n")
                        updated_keys.add(key)
                    else:
                        # Keep existing line
                        updated_lines.append(line)
                else:
                    # Keep comments and empty lines
                    updated_lines.append(line)

            # Add new settings that weren't in the file
            for key, value in self.settings.items():
                if key not in updated_keys:
                    updated_lines.append(f"{key}={value}\n")

            # Write back to file
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(updated_lines)

        except Exception as e:
            raise RuntimeError(f"Erro ao salvar configurações: {e}")

    def create_directories(self) -> None:
        """Create necessary directories for the application."""
        directories = [
            self.settings.get("OUTPUT_DIR", "data/output"),
            self.settings.get("INPUT_DIR", "data/input"),
            "data/logs",
            "data/temp",
            "data/cache"
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def get_supported_languages(self) -> dict:
        """Get supported languages from the whisper provider.

        Returns:
            Dictionary mapping language codes to display names
        """
        # Get supported languages from whisper provider
        supported_codes = self.whisper_provider.get_supported_languages()

        # Map to display names
        language_names = {
            "en": "English",
            "pt": "Português",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "ja": "日本語",
            "ko": "한국어",
            "zh": "中文",
            "ru": "Русский",
            "ar": "العربية",
            "hi": "हिन्दी",
            "tr": "Türkçe",
            "pl": "Polski",
            "nl": "Nederlands",
            "sv": "Svenska",
            "no": "Norsk",
            "da": "Dansk",
            "fi": "Suomi"
        }

        # Return only supported languages
        return {
            code: language_names.get(code, code.upper())
            for code in supported_codes
            if code in language_names
        }

    def get_whisper_models(self) -> dict:
        """Get available Whisper models.

        Returns:
            Dictionary mapping model names to descriptions
        """
        return {
            "tiny": "Tiny (39 MB) - Mais rápido, menor precisão",
            "base": "Base (74 MB) - Equilibrio entre velocidade e precisão",
            "small": "Small (244 MB) - Boa precisão, velocidade moderada",
            "medium": "Medium (769 MB) - Alta precisão, mais lento",
            "large": "Large (1550 MB) - Máxima precisão, mais lento"
        }

    def validate_configuration(self) -> list:
        """Validate the current configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if output directory is writable
        output_dir = Path(self.settings.get("OUTPUT_DIR", "data/output"))
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            test_file = output_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
        except Exception:
            errors.append(f"Diretório de saída não é gravável: {output_dir}")

        # Check Whisper model
        model = self.settings.get("WHISPER_MODEL", "base")
        valid_models = list(self.get_whisper_models().keys())
        if model not in valid_models:
            errors.append(f"Modelo Whisper inválido: {model}. Válidos: {', '.join(valid_models)}")

        # Check language
        language = self.settings.get("DEFAULT_LANGUAGE", "pt")
        valid_languages = list(self.get_supported_languages().keys())
        if language not in valid_languages:
            errors.append(f"Idioma padrão inválido: {language}. Válidos: {', '.join(valid_languages)}")

        return errors
