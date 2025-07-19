"""Configurações do Alfredo AI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class Config:
    """Configurações principais do Alfredo AI."""

    # Diretórios
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    INPUT_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"
    LOGS_DIR = DATA_DIR / "logs"
    TEMP_DIR = DATA_DIR / "temp"

    # Configurações de modelo
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Configurações de processamento
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pt")
    SCENE_THRESHOLD = float(os.getenv("SCENE_THRESHOLD", "30"))
    MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE", "500MB")

    # Configurações de saída
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "json")

    # Configurações de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "alfredo.log"

    @classmethod
    def validate(cls) -> None:
        """Valida as configurações necessárias."""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY não configurada. "
                "Defina a variável de ambiente GROQ_API_KEY."
            )

    @classmethod
    def create_directories(cls) -> None:
        """Cria diretórios necessários."""
        directories = [
            cls.INPUT_DIR / "local",
            cls.INPUT_DIR / "youtube",
            cls.OUTPUT_DIR,
            cls.LOGS_DIR,
            cls.TEMP_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Configurações de desenvolvimento
class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


# Configurações de produção
class ProductionConfig(Config):
    """Configurações para ambiente de produção."""

    DEBUG = False
    LOG_LEVEL = "INFO"


# Configuração ativa
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

# Obter configuração baseada na variável de ambiente
ACTIVE_CONFIG = config.get(os.getenv("ENVIRONMENT", "default"))
