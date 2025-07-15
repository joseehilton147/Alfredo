"""Testes para configurações."""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.settings import Config, DevelopmentConfig, ProductionConfig, ACTIVE_CONFIG


class TestConfig:
    """Testes para a classe Config."""

    def test_base_config_paths(self):
        """Testa configuração dos caminhos base."""
        # Testar que os caminhos são Path objects
        assert isinstance(Config.BASE_DIR, Path)
        assert isinstance(Config.DATA_DIR, Path)
        assert isinstance(Config.INPUT_DIR, Path)
        assert isinstance(Config.OUTPUT_DIR, Path)
        assert isinstance(Config.LOGS_DIR, Path)
        assert isinstance(Config.TEMP_DIR, Path)
        
        # Testar estrutura dos caminhos
        assert Config.DATA_DIR == Config.BASE_DIR / "data"
        assert Config.INPUT_DIR == Config.DATA_DIR / "input"
        assert Config.OUTPUT_DIR == Config.DATA_DIR / "output"

    def test_default_config_values(self):
        """Testa valores padrão da configuração."""
        with patch.dict(os.environ, {}, clear=True):
            # Recarregar módulo para pegar valores padrão
            from importlib import reload
            from src.config import settings
            reload(settings)
            
            assert settings.Config.WHISPER_MODEL == "base"
            assert settings.Config.GROQ_MODEL == "llama3-70b-8192"
            assert settings.Config.DEFAULT_LANGUAGE == "pt"
            assert settings.Config.SCENE_THRESHOLD == 30.0
            assert settings.Config.OUTPUT_FORMAT == "json"
            assert settings.Config.LOG_LEVEL == "INFO"

    def test_environment_variables_override(self):
        """Testa que variáveis de ambiente sobrescrevem valores padrão."""
        env_vars = {
            "WHISPER_MODEL": "large",
            "GROQ_MODEL": "custom-model",
            "DEFAULT_LANGUAGE": "en",
            "SCENE_THRESHOLD": "45.5",
            "OUTPUT_FORMAT": "txt",
            "LOG_LEVEL": "DEBUG",
            "GROQ_API_KEY": "test-api-key"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            from importlib import reload
            from src.config import settings
            reload(settings)
            
            assert settings.Config.WHISPER_MODEL == "large"
            assert settings.Config.GROQ_MODEL == "custom-model"
            assert settings.Config.DEFAULT_LANGUAGE == "en"
            assert settings.Config.SCENE_THRESHOLD == 45.5
            assert settings.Config.OUTPUT_FORMAT == "txt"
            assert settings.Config.LOG_LEVEL == "DEBUG"
            assert settings.Config.GROQ_API_KEY == "test-api-key"

    def test_validate_with_api_key(self):
        """Testa validação com API key configurada."""
        with patch.object(Config, 'GROQ_API_KEY', 'valid-key'):
            # Não deve lançar exceção
            Config.validate()

    def test_validate_without_api_key(self):
        """Testa validação sem API key."""
        with patch.object(Config, 'GROQ_API_KEY', None):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            
            assert "GROQ_API_KEY não configurada" in str(exc_info.value)

    def test_validate_with_empty_api_key(self):
        """Testa validação com API key vazia."""
        with patch.object(Config, 'GROQ_API_KEY', ''):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            
            assert "GROQ_API_KEY não configurada" in str(exc_info.value)

    def test_create_directories(self):
        """Testa criação de diretórios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(Config, 'BASE_DIR', Path(temp_dir)):
                with patch.object(Config, 'DATA_DIR', Path(temp_dir) / "data"):
                    with patch.object(Config, 'INPUT_DIR', Path(temp_dir) / "data" / "input"):
                        with patch.object(Config, 'OUTPUT_DIR', Path(temp_dir) / "data" / "output"):
                            with patch.object(Config, 'LOGS_DIR', Path(temp_dir) / "data" / "logs"):
                                with patch.object(Config, 'TEMP_DIR', Path(temp_dir) / "data" / "temp"):
                                    
                                    Config.create_directories()
                                    
                                    # Verificar que diretórios foram criados
                                    assert (Path(temp_dir) / "data" / "input" / "local").exists()
                                    assert (Path(temp_dir) / "data" / "input" / "youtube").exists()
                                    assert (Path(temp_dir) / "data" / "output").exists()
                                    assert (Path(temp_dir) / "data" / "logs").exists()
                                    assert (Path(temp_dir) / "data" / "temp").exists()


class TestDevelopmentConfig:
    """Testes para configuração de desenvolvimento."""

    def test_development_config_inheritance(self):
        """Testa herança da configuração de desenvolvimento."""
        assert issubclass(DevelopmentConfig, Config)
        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.LOG_LEVEL == "DEBUG"


class TestProductionConfig:
    """Testes para configuração de produção."""

    def test_production_config_inheritance(self):
        """Testa herança da configuração de produção."""
        assert issubclass(ProductionConfig, Config)
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.LOG_LEVEL == "INFO"


class TestActiveConfig:
    """Testes para configuração ativa."""

    def test_default_environment(self):
        """Testa configuração padrão."""
        with patch.dict(os.environ, {}, clear=True):
            from importlib import reload
            from src.config import settings
            reload(settings)
            
            assert settings.ACTIVE_CONFIG == settings.DevelopmentConfig

    def test_development_environment(self):
        """Testa ambiente de desenvolvimento."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            from importlib import reload
            from src.config import settings
            reload(settings)
            
            assert settings.ACTIVE_CONFIG == settings.DevelopmentConfig

    def test_production_environment(self):
        """Testa ambiente de produção."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            from importlib import reload
            from src.config import settings
            reload(settings)
            
            assert settings.ACTIVE_CONFIG == settings.ProductionConfig

    def test_unknown_environment(self):
        """Testa ambiente desconhecido."""
        with patch.dict(os.environ, {"ENVIRONMENT": "unknown"}):
            from importlib import reload
            from src.config import settings
            reload(settings)
            
            # Para ambiente desconhecido, retorna None
            assert settings.ACTIVE_CONFIG is None
