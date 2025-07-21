"""Configuração tipada centralizada do Alfredo AI."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.config.constants import (
    DEFAULT_GROQ_MODEL, DEFAULT_OLLAMA_MODEL, DEFAULT_WHISPER_MODEL,
    DEFAULT_LANGUAGE, DEFAULT_DOWNLOAD_TIMEOUT, DEFAULT_TRANSCRIPTION_TIMEOUT,
    MAX_FILE_SIZE_MB, MAX_VIDEO_DURATION_SECONDS, DEFAULT_MAX_WORKERS,
    DEFAULT_SCENE_THRESHOLD, API_KEY_ENV_GROQ, API_KEY_ENV_OPENAI,
    AIProvider
)
from src.domain.exceptions.alfredo_errors import ConfigurationError


@dataclass
class AlfredoConfig:
    """
    Configuração tipada centralizada do Alfredo AI.
    
    Esta classe centraliza todas as configurações do sistema com validação
    automática e valores padrão apropriados.
    """
    
    # Modelos de IA
    groq_model: str = DEFAULT_GROQ_MODEL
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    whisper_model: str = DEFAULT_WHISPER_MODEL
    default_ai_provider: str = AIProvider.WHISPER.value
    
    # Timeouts e Limites
    max_video_duration: int = MAX_VIDEO_DURATION_SECONDS
    download_timeout: int = DEFAULT_DOWNLOAD_TIMEOUT
    transcription_timeout: int = DEFAULT_TRANSCRIPTION_TIMEOUT
    max_file_size_mb: int = MAX_FILE_SIZE_MB
    max_concurrent_downloads: int = DEFAULT_MAX_WORKERS
    
    # Diretórios
    base_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.parent
    )
    data_dir: Optional[Path] = None
    temp_dir: Optional[Path] = None
    
    # API Keys e Credenciais
    groq_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv(API_KEY_ENV_GROQ)
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv(API_KEY_ENV_OPENAI)
    )
    
    # Configurações de Processamento
    default_language: str = DEFAULT_LANGUAGE
    scene_threshold: float = DEFAULT_SCENE_THRESHOLD
    audio_sample_rate: int = 16000
    video_quality: str = "best"
    
    # Configurações de Log
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Validações e configurações automáticas após inicialização."""
        # Configurar diretórios padrão
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.temp_dir is None:
            self.temp_dir = self.data_dir / "temp"
        
        # Validações críticas
        self._validate_timeouts()
        self._validate_limits()
        self._validate_directories()
    
    def _validate_timeouts(self) -> None:
        """Valida configurações de timeout."""
        if self.max_video_duration <= 0:
            raise ConfigurationError(
                "max_video_duration", 
                "deve ser positivo", 
                expected="> 0"
            )
        
        if self.download_timeout <= 0:
            raise ConfigurationError(
                "download_timeout", 
                "deve ser positivo", 
                expected="> 0"
            )
        
        if self.transcription_timeout <= 0:
            raise ConfigurationError(
                "transcription_timeout", 
                "deve ser positivo", 
                expected="> 0"
            )
    
    def _validate_limits(self) -> None:
        """Valida limites e thresholds."""
        if self.scene_threshold < 0:
            raise ConfigurationError(
                "scene_threshold", 
                "deve ser não-negativo", 
                expected=">= 0"
            )
        
        if self.max_file_size_mb <= 0:
            raise ConfigurationError(
                "max_file_size_mb", 
                "deve ser positivo", 
                expected="> 0"
            )
        
        if self.max_concurrent_downloads <= 0:
            raise ConfigurationError(
                "max_concurrent_downloads", 
                "deve ser positivo", 
                expected="> 0"
            )
    
    def _validate_directories(self) -> None:
        """Valida e cria diretórios necessários."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise ConfigurationError(
                "directories", 
                f"sem permissão para criar: {e}",
                details={"data_dir": str(self.data_dir), "temp_dir": str(self.temp_dir)}
            )
    
    def validate_runtime(self) -> None:
        """Validações que dependem de recursos externos."""
        if self.default_ai_provider == "groq" and not self.groq_api_key:
            raise ConfigurationError(
                "groq_api_key", 
                "obrigatória para provider groq",
                expected="GROQ_API_KEY environment variable"
            )
        
        if self.default_ai_provider == "openai" and not self.openai_api_key:
            raise ConfigurationError(
                "openai_api_key", 
                "obrigatória para provider openai",
                expected="OPENAI_API_KEY environment variable"
            )
        # Verifica presença de FFmpeg
        self.validate_ffmpeg()
    
    def create_directory_structure(self) -> None:
        """Cria toda a estrutura de diretórios necessária."""
        directories = [
            self.data_dir / "input" / "local",
            self.data_dir / "input" / "youtube",
            self.data_dir / "output" / "transcriptions",
            self.data_dir / "output" / "summaries",
            self.data_dir / "logs",
            self.temp_dir,
            self.data_dir / "cache"
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise ConfigurationError(
                    "directory_creation",
                    f"sem permissão para criar {directory}: {e}",
                    expected="permissões de escrita",
                    details={"directory": str(directory)}
                )
    
    def validate_ffmpeg(self) -> None:
        """Verifica se o FFmpeg está instalado e acessível."""
        import shutil, subprocess

        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise ConfigurationError(
                "ffmpeg", 
                "não encontrado no PATH", 
                expected="ffmpeg instalado e acessível"
            )
        # Verificar versão
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            raise ConfigurationError(
                "ffmpeg", 
                "erro ao executar ffmpeg", 
                expected="ffmpeg retornar versão", 
                details={"stderr": result.stderr.decode(errors='ignore')}
            )
    def get_provider_config(self, provider_name: str) -> dict:
        """
        Retorna configuração específica do provider.
        
        Args:
            provider_name: Nome do provider (whisper, groq, ollama)
            
        Returns:
            Dicionário com configurações específicas
            
        Raises:
            ConfigurationError: Se provider não é suportado
        """
        configs = {
            "whisper": {
                "model": self.whisper_model,
                "timeout": self.transcription_timeout
            },
            "groq": {
                "model": self.groq_model,
                "api_key": self.groq_api_key,
                "timeout": self.transcription_timeout
            },
            "ollama": {
                "model": self.ollama_model,
                "timeout": self.transcription_timeout
            }
        }
        
        if provider_name not in configs:
            raise ConfigurationError(
                "provider_name", 
                f"Provider '{provider_name}' não configurado",
                expected="whisper, groq, ollama",
                details={"requested_provider": provider_name, "available": list(configs.keys())}
            )
        
        return configs[provider_name]