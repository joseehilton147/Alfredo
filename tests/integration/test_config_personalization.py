"""
Testes de configuração e personalização do Alfredo AI.
"""
import pytest
from src.config.alfredo_config import AlfredoConfig


def test_config_model_variants():
    config = AlfredoConfig()
    # Supondo que AlfredoConfig permite alterar o modelo Whisper
    config.whisper_model = "base"
    assert config.whisper_model == "base"
    config.whisper_model = "medium"
    assert config.whisper_model == "medium"
    config.whisper_model = "large"
    assert config.whisper_model == "large"

def test_config_timeout_and_retry():
    config = AlfredoConfig()
    config.transcription_timeout = 600
    config.max_retries = 2
    assert config.transcription_timeout == 600
    assert config.max_retries == 2

def test_config_output_format():
    config = AlfredoConfig()
    config.output_format = "json"
    assert config.output_format == "json"
    config.output_format = "html"
    assert config.output_format == "html"
