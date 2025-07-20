"""Application context for dependency injection in the CLI."""

import os
from pathlib import Path
from typing import Optional

from src.application.use_cases.transcribe_audio import TranscribeAudioUseCase
from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory


class ApplicationContext:
    """Application context for dependency injection."""

    def __init__(self):
        """Initialize the application context with all dependencies."""
        # Load settings from environment and create config
        self.settings = self._load_settings()
        self.config = self._create_config()
        
        # Initialize factory
        self.factory = InfrastructureFactory(self.config)
        
        # Initialize use cases using factory
        dependencies = self.factory.create_all_dependencies()
        
        self.transcribe_use_case = TranscribeAudioUseCase(
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
        )
        
        self.process_youtube_use_case = ProcessYouTubeVideoUseCase(
            downloader=dependencies['downloader'],
            extractor=dependencies['extractor'],
            ai_provider=dependencies['ai_provider'],
            storage=dependencies['storage'],
            config=dependencies['config']
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
    
    def _create_config(self) -> AlfredoConfig:
        """Create AlfredoConfig from loaded settings.
        
        Returns:
            Configured AlfredoConfig instance
        """
        # Create config with settings from environment
        config = AlfredoConfig()
        
        # Override with loaded settings
        if "WHISPER_MODEL" in self.settings:
            config.whisper_model = self.settings["WHISPER_MODEL"]
        if "DEFAULT_LANGUAGE" in self.settings:
            config.default_language = self.settings["DEFAULT_LANGUAGE"]
        if "OUTPUT_DIR" in self.settings:
            config.data_dir = Path(self.settings["OUTPUT_DIR"]).parent
        
        # Ensure directories are created
        config.create_directory_structure()
        
        return config

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
        """Get supported languages from the AI provider.

        Returns:
            Dictionary mapping language codes to display names
        """
        # Get AI provider from factory
        ai_provider = self.factory.create_ai_provider()
        supported_codes = ai_provider.get_supported_languages()

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
