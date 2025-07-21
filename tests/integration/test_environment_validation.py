"""
Testes de validação de ambiente e configuração do Alfredo AI.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

import src.config.validators as validators
from src.config.alfredo_config import AlfredoConfig


def test_validate_ffmpeg_ok(monkeypatch):
    # Simula ffmpeg presente e versão adequada
    monkeypatch.setattr(validators, "shutil", shutil)
    monkeypatch.setattr(validators, "subprocess", __import__("subprocess"))
    assert validators.validate_ffmpeg() is None

def test_validate_ffmpeg_missing(monkeypatch):
    monkeypatch.setattr(validators.shutil, "which", lambda _: None)
    with pytest.raises(validators.ValidationError):
        validators.validate_ffmpeg()

def test_validate_data_directories(tmp_path):
    # Remove diretórios se existirem
    base = tmp_path / "data"
    if base.exists():
        shutil.rmtree(base)
    validators.validate_data_directories(base)
    assert (base / "input" / "local").exists()
    assert (base / "input" / "youtube").exists()
    assert (base / "output").exists()
    assert (base / "logs").exists()
    assert (base / "temp").exists()
    assert (base / "cache").exists()

def test_validate_ai_providers_ok():
    class DummyConfig:
        groq_api_key = "abc"
        ollama_host = "localhost"
    validators.validate_ai_providers(DummyConfig())

def test_validate_ai_providers_missing():
    class DummyConfig:
        groq_api_key = ""
        ollama_host = ""
    with pytest.raises(validators.ValidationError):
        validators.validate_ai_providers(DummyConfig())
