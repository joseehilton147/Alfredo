"""
Módulo de validação de ambiente e dependências para o Alfredo AI.
"""
import os
import shutil
import subprocess
from pathlib import Path

from src.config.alfredo_config import AlfredoConfig

class ValidationError(Exception):
    """Exceção para erros de validação de ambiente/configuração."""
    pass

def validate_ffmpeg(min_version: str = "4.0"):
    """Verifica se o FFmpeg está instalado e se a versão atende ao mínimo."""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise ValidationError("FFmpeg não encontrado. Instale o FFmpeg e adicione ao PATH.")
    try:
        result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, check=True)
        version_line = result.stdout.splitlines()[0]
        # Exemplo: 'ffmpeg version 6.1.1-2025-07-17-git-bc8d06d541-full_build-www'
        # ou 'ffmpeg version 2025-07-17-git-bc8d06d541-full_build-www.gyan.dev ...'
        import re
        match = re.search(r"ffmpeg version (\d+\.\d+(?:\.\d+)?)", version_line)
        if not match:
            # Tenta capturar qualquer número de versão na linha
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", version_line)
        if not match:
            # Se não encontrar, provavelmente é build customizada sem número
            # Apenas avisa e não valida versão
            print(f"Aviso: não foi possível extrair a versão do FFmpeg. Build customizada detectada: '{version_line}'")
            return
        version = match.group(1)
        if tuple(map(int, version.split("."))) < tuple(map(int, min_version.split("."))):
            raise ValidationError(f"FFmpeg versão {version} encontrada, mas a mínima requerida é {min_version}.")
    except Exception as e:
        raise ValidationError(f"Erro ao verificar versão do FFmpeg: {e}")

def validate_ai_providers(config: AlfredoConfig):
    """Valida configurações dos providers de IA (ex: Whisper, Groq, Ollama)."""
    # Exemplo: Whisper não requer chave, mas Groq/Ollama sim
    if hasattr(config, "groq_api_key") and not config.groq_api_key:
        raise ValidationError("Chave da API Groq não configurada.")
    if hasattr(config, "ollama_host") and not config.ollama_host:
        raise ValidationError("Host do Ollama não configurado.")
    # Adicione outras validações conforme necessário

def validate_data_directories(base_path: Path = Path("data")):
    """Garante que os diretórios de dados necessários existem ou os cria."""
    required_dirs = [
        base_path / "input" / "local",
        base_path / "input" / "youtube",
        base_path / "output",
        base_path / "logs",
        base_path / "temp",
        base_path / "cache",
    ]
    for d in required_dirs:
        d.mkdir(parents=True, exist_ok=True)
