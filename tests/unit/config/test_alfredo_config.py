"""Testes unitários para AlfredoConfig."""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import ConfigurationError


class TestAlfredoConfigCreation:
    """Testes para criação de AlfredoConfig."""
    
    def test_default_configuration(self):
        """Testa criação com configurações padrão."""
        config = AlfredoConfig()
        
        assert config.groq_model == "llama-3.3-70b-versatile"
        assert config.ollama_model == "llama3:8b"
        assert config.whisper_model == "base"
        assert config.default_ai_provider == "whisper"
        assert config.max_video_duration == 86400
        assert config.download_timeout == 300
        assert config.transcription_timeout == 600
        assert config.max_file_size_mb == 500
        assert config.max_concurrent_downloads == 3
        assert config.default_language == "pt"
        assert config.scene_threshold == 0.3
        assert config.audio_sample_rate == 16000
        assert config.video_quality == "best"
        assert config.log_level == "INFO"
    
    def test_custom_configuration(self):
        """Testa criação com configurações customizadas."""
        config = AlfredoConfig(
            groq_model="custom-model",
            max_video_duration=7200,
            download_timeout=600,
            default_language="en"
        )
        
        assert config.groq_model == "custom-model"
        assert config.max_video_duration == 7200
        assert config.download_timeout == 600
        assert config.default_language == "en"
    
    def test_directory_configuration(self):
        """Testa configuração de diretórios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            config = AlfredoConfig(base_dir=base_dir)
            
            assert config.base_dir == base_dir
            assert config.data_dir == base_dir / "data"
            assert config.temp_dir == config.data_dir / "temp"
    
    def test_custom_data_directory(self):
        """Testa configuração de diretório de dados customizado."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "custom_data"
            config = AlfredoConfig(data_dir=data_dir)
            
            assert config.data_dir == data_dir
            assert config.temp_dir == data_dir / "temp"
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
    def test_api_key_from_environment(self):
        """Testa carregamento de API key do ambiente."""
        config = AlfredoConfig()
        assert config.groq_api_key == "test_key"
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "openai_key"})
    def test_openai_api_key_from_environment(self):
        """Testa carregamento de OpenAI API key do ambiente."""
        config = AlfredoConfig()
        assert config.openai_api_key == "openai_key"


class TestAlfredoConfigValidation:
    """Testes para validação de AlfredoConfig."""
    
    def test_invalid_timeout_negative(self):
        """Testa validação de timeout negativo."""
        with pytest.raises(ConfigurationError) as exc_info:
            AlfredoConfig(download_timeout=-10)
        
        assert "download_timeout" in str(exc_info.value)
        assert "deve ser positivo" in str(exc_info.value)
    
    def test_invalid_timeout_zero(self):
        """Testa validação de timeout zero."""
        with pytest.raises(ConfigurationError) as exc_info:
            AlfredoConfig(max_video_duration=0)
        
        assert "max_video_duration" in str(exc_info.value)
        assert "deve ser positivo" in str(exc_info.value)
    
    def test_invalid_scene_threshold_negative(self):
        """Testa validação de scene_threshold negativo."""
        with pytest.raises(ConfigurationError) as exc_info:
            AlfredoConfig(scene_threshold=-1.0)
        
        assert "scene_threshold" in str(exc_info.value)
        assert "deve ser não-negativo" in str(exc_info.value)
    
    def test_invalid_max_file_size_negative(self):
        """Testa validação de max_file_size_mb negativo."""
        with pytest.raises(ConfigurationError) as exc_info:
            AlfredoConfig(max_file_size_mb=-100)
        
        assert "max_file_size_mb" in str(exc_info.value)
        assert "deve ser positivo" in str(exc_info.value)
    
    def test_invalid_max_concurrent_downloads_zero(self):
        """Testa validação de max_concurrent_downloads zero."""
        with pytest.raises(ConfigurationError) as exc_info:
            AlfredoConfig(max_concurrent_downloads=0)
        
        assert "max_concurrent_downloads" in str(exc_info.value)
        assert "deve ser positivo" in str(exc_info.value)
    
    def test_valid_edge_values(self):
        """Testa valores limítrofes válidos."""
        config = AlfredoConfig(
            max_video_duration=1,
            download_timeout=1,
            transcription_timeout=1,
            scene_threshold=0.0,
            max_file_size_mb=1,
            max_concurrent_downloads=1
        )
        
        assert config.max_video_duration == 1
        assert config.scene_threshold == 0.0


class TestAlfredoConfigRuntimeValidation:
    """Testes para validação runtime de AlfredoConfig."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_groq_provider_without_api_key(self):
        """Testa validação de provider Groq sem API key."""
        config = AlfredoConfig(default_ai_provider="groq", groq_api_key=None)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate_runtime()
        
        assert "groq_api_key" in str(exc_info.value)
        assert "obrigatória para provider groq" in str(exc_info.value)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_openai_provider_without_api_key(self):
        """Testa validação de provider OpenAI sem API key."""
        config = AlfredoConfig(default_ai_provider="openai", openai_api_key=None)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate_runtime()
        
        assert "openai_api_key" in str(exc_info.value)
        assert "obrigatória para provider openai" in str(exc_info.value)
    
    def test_whisper_provider_no_api_key_required(self):
        """Testa que provider Whisper não requer API key."""
        config = AlfredoConfig(default_ai_provider="whisper")
        
        # Não deve lançar exceção
        config.validate_runtime()
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "valid_key"})
    def test_groq_provider_with_api_key(self):
        """Testa validação de provider Groq com API key válida."""
        config = AlfredoConfig(default_ai_provider="groq")
        
        # Não deve lançar exceção
        config.validate_runtime()


class TestAlfredoConfigDirectoryManagement:
    """Testes para gerenciamento de diretórios."""
    
    def test_create_directory_structure(self):
        """Testa criação da estrutura de diretórios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            config = AlfredoConfig(base_dir=base_dir)
            
            config.create_directory_structure()
            
            # Verificar se todos os diretórios foram criados
            expected_dirs = [
                config.data_dir / "input" / "local",
                config.data_dir / "input" / "youtube",
                config.data_dir / "output" / "transcriptions",
                config.data_dir / "output" / "summaries",
                config.data_dir / "logs",
                config.temp_dir,
                config.data_dir / "cache"
            ]
            
            for directory in expected_dirs:
                assert directory.exists()
                assert directory.is_dir()
    
    def test_directory_creation_permission_error(self):
        """Testa tratamento de erro de permissão na criação de diretórios."""
        # Simular erro de permissão
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigurationError) as exc_info:
                config = AlfredoConfig()
            
            assert "directories" in str(exc_info.value)
            assert "sem permissão para criar" in str(exc_info.value)


class TestAlfredoConfigProviderConfig:
    """Testes para configuração específica de providers."""
    
    def test_get_whisper_provider_config(self):
        """Testa configuração do provider Whisper."""
        config = AlfredoConfig(
            whisper_model="large",
            transcription_timeout=900
        )
        
        provider_config = config.get_provider_config("whisper")
        
        assert provider_config["model"] == "large"
        assert provider_config["timeout"] == 900
    
    def test_get_groq_provider_config(self):
        """Testa configuração do provider Groq."""
        config = AlfredoConfig(
            groq_model="custom-model",
            groq_api_key="test_key",
            transcription_timeout=1200
        )
        
        provider_config = config.get_provider_config("groq")
        
        assert provider_config["model"] == "custom-model"
        assert provider_config["api_key"] == "test_key"
        assert provider_config["timeout"] == 1200
    
    def test_get_ollama_provider_config(self):
        """Testa configuração do provider Ollama."""
        config = AlfredoConfig(
            ollama_model="custom-ollama",
            transcription_timeout=600
        )
        
        provider_config = config.get_provider_config("ollama")
        
        assert provider_config["model"] == "custom-ollama"
        assert provider_config["timeout"] == 600
    
    def test_get_unknown_provider_config(self):
        """Testa configuração de provider desconhecido."""
        config = AlfredoConfig()
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.get_provider_config("unknown_provider")
        
        assert "provider_name" in str(exc_info.value)
        assert "não configurado" in str(exc_info.value)


class TestAlfredoConfigEdgeCases:
    """Testes para casos extremos de AlfredoConfig."""
    
    def test_very_large_timeout_values(self):
        """Testa valores muito grandes para timeouts."""
        config = AlfredoConfig(
            max_video_duration=86400 * 7,  # 1 semana
            download_timeout=3600,         # 1 hora
            transcription_timeout=7200     # 2 horas
        )
        
        assert config.max_video_duration == 86400 * 7
        assert config.download_timeout == 3600
        assert config.transcription_timeout == 7200
    
    def test_minimum_valid_values(self):
        """Testa valores mínimos válidos."""
        config = AlfredoConfig(
            max_video_duration=1,
            download_timeout=1,
            transcription_timeout=1,
            max_file_size_mb=1,
            max_concurrent_downloads=1,
            scene_threshold=0.0
        )
        
        assert config.max_video_duration == 1
        assert config.scene_threshold == 0.0
    
    def test_unicode_in_paths(self):
        """Testa caminhos com caracteres Unicode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            unicode_path = Path(temp_dir) / "测试_ação_тест"
            config = AlfredoConfig(base_dir=unicode_path)
            
            # Deve funcionar sem erros
            assert config.base_dir == unicode_path