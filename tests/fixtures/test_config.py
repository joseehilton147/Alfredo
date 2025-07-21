"""Configurações específicas para testes."""

import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from src.config.alfredo_config import AlfredoConfig


class TestConfig(AlfredoConfig):
    """Configuração específica para testes."""
    
    def __init__(self, **kwargs):
        # Configurações padrão para testes
        test_defaults = {
            'base_dir': Path(tempfile.mkdtemp()),
            'groq_api_key': 'test_groq_key',
            'openai_api_key': 'test_openai_key',
            'default_ai_provider': 'whisper',
            'max_video_duration': 300,  # 5 minutos para testes
            'download_timeout': 30,     # 30 segundos para testes
            'transcription_timeout': 60, # 1 minuto para testes
            'max_file_size_mb': 50,     # 50MB para testes
            'max_concurrent_downloads': 2,
            'log_level': 'DEBUG'
        }
        
        # Mesclar com kwargs fornecidos
        test_defaults.update(kwargs)
        super().__init__(**test_defaults)
    
    def create_test_directories(self):
        """Cria diretórios específicos para testes."""
        test_dirs = [
            self.data_dir / "test_input",
            self.data_dir / "test_output", 
            self.data_dir / "test_cache",
            self.temp_dir / "test_temp"
        ]
        
        for directory in test_dirs:
            directory.mkdir(parents=True, exist_ok=True)
    
    def cleanup_test_directories(self):
        """Remove diretórios de teste."""
        import shutil
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir, ignore_errors=True)


class TestConfigBuilder:
    """Builder para criar configurações de teste customizadas."""
    
    def __init__(self):
        self._config_data = {}
    
    def with_temp_dir(self, temp_dir: Optional[Path] = None):
        """Define diretório temporário."""
        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp())
        self._config_data['base_dir'] = temp_dir
        return self
    
    def with_ai_provider(self, provider: str, api_key: Optional[str] = None):
        """Define provider de IA."""
        self._config_data['default_ai_provider'] = provider
        if api_key:
            if provider == 'groq':
                self._config_data['groq_api_key'] = api_key
            elif provider == 'openai':
                self._config_data['openai_api_key'] = api_key
        return self
    
    def with_timeouts(self, download: int = 30, transcription: int = 60):
        """Define timeouts."""
        self._config_data['download_timeout'] = download
        self._config_data['transcription_timeout'] = transcription
        return self
    
    def with_limits(self, max_duration: int = 300, max_file_size: int = 50):
        """Define limites."""
        self._config_data['max_video_duration'] = max_duration
        self._config_data['max_file_size_mb'] = max_file_size
        return self
    
    def with_debug_logging(self):
        """Habilita logging de debug."""
        self._config_data['log_level'] = 'DEBUG'
        return self
    
    def build(self) -> TestConfig:
        """Constrói a configuração de teste."""
        return TestConfig(**self._config_data)


# Configurações pré-definidas para diferentes tipos de teste

def get_unit_test_config() -> TestConfig:
    """Configuração para testes unitários."""
    return TestConfigBuilder() \
        .with_ai_provider('whisper') \
        .with_timeouts(download=5, transcription=10) \
        .with_limits(max_duration=60, max_file_size=10) \
        .with_debug_logging() \
        .build()


def get_integration_test_config() -> TestConfig:
    """Configuração para testes de integração."""
    return TestConfigBuilder() \
        .with_ai_provider('whisper') \
        .with_timeouts(download=30, transcription=60) \
        .with_limits(max_duration=300, max_file_size=50) \
        .with_debug_logging() \
        .build()


def get_e2e_test_config() -> TestConfig:
    """Configuração para testes end-to-end."""
    return TestConfigBuilder() \
        .with_ai_provider('whisper') \
        .with_timeouts(download=120, transcription=300) \
        .with_limits(max_duration=1800, max_file_size=200) \
        .build()


def get_performance_test_config() -> TestConfig:
    """Configuração para testes de performance."""
    return TestConfigBuilder() \
        .with_ai_provider('whisper') \
        .with_timeouts(download=300, transcription=600) \
        .with_limits(max_duration=3600, max_file_size=500) \
        .build()


def get_security_test_config() -> TestConfig:
    """Configuração para testes de segurança."""
    return TestConfigBuilder() \
        .with_ai_provider('whisper') \
        .with_timeouts(download=10, transcription=20) \
        .with_limits(max_duration=30, max_file_size=5) \
        .with_debug_logging() \
        .build()


# Configurações específicas por provider

def get_groq_test_config(api_key: str = "test_groq_key") -> TestConfig:
    """Configuração para testes com Groq."""
    return TestConfigBuilder() \
        .with_ai_provider('groq', api_key) \
        .with_timeouts(download=30, transcription=60) \
        .build()


def get_ollama_test_config() -> TestConfig:
    """Configuração para testes com Ollama."""
    return TestConfigBuilder() \
        .with_ai_provider('ollama') \
        .with_timeouts(download=30, transcription=120) \
        .build()


def get_whisper_test_config() -> TestConfig:
    """Configuração para testes com Whisper."""
    return TestConfigBuilder() \
        .with_ai_provider('whisper') \
        .with_timeouts(download=30, transcription=60) \
        .build()


# Configurações para cenários específicos

def get_slow_network_config() -> TestConfig:
    """Configuração para simular rede lenta."""
    return TestConfigBuilder() \
        .with_timeouts(download=300, transcription=60) \
        .with_limits(max_file_size=20) \
        .build()


def get_limited_resources_config() -> TestConfig:
    """Configuração para recursos limitados."""
    return TestConfigBuilder() \
        .with_timeouts(download=60, transcription=120) \
        .with_limits(max_duration=600, max_file_size=100) \
        .build()


def get_high_performance_config() -> TestConfig:
    """Configuração para alta performance."""
    config = TestConfigBuilder() \
        .with_timeouts(download=10, transcription=30) \
        .with_limits(max_duration=7200, max_file_size=1000) \
        .build()
    
    config.max_concurrent_downloads = 5
    return config


# Utilitários para configuração de teste

class TestConfigManager:
    """Gerenciador de configurações de teste."""
    
    def __init__(self):
        self._configs: Dict[str, TestConfig] = {}
        self._current_config: Optional[TestConfig] = None
    
    def register_config(self, name: str, config: TestConfig):
        """Registra uma configuração."""
        self._configs[name] = config
    
    def get_config(self, name: str) -> TestConfig:
        """Obtém configuração por nome."""
        if name not in self._configs:
            raise ValueError(f"Configuração '{name}' não encontrada")
        return self._configs[name]
    
    def set_current_config(self, name: str):
        """Define configuração atual."""
        self._current_config = self.get_config(name)
    
    def get_current_config(self) -> Optional[TestConfig]:
        """Obtém configuração atual."""
        return self._current_config
    
    def list_configs(self) -> list:
        """Lista todas as configurações registradas."""
        return list(self._configs.keys())
    
    def cleanup_all_configs(self):
        """Limpa todas as configurações."""
        for config in self._configs.values():
            config.cleanup_test_directories()
        self._configs.clear()
        self._current_config = None


# Instância global do gerenciador
test_config_manager = TestConfigManager()

# Registrar configurações padrão
test_config_manager.register_config('unit', get_unit_test_config())
test_config_manager.register_config('integration', get_integration_test_config())
test_config_manager.register_config('e2e', get_e2e_test_config())
test_config_manager.register_config('performance', get_performance_test_config())
test_config_manager.register_config('security', get_security_test_config())
test_config_manager.register_config('groq', get_groq_test_config())
test_config_manager.register_config('ollama', get_ollama_test_config())
test_config_manager.register_config('whisper', get_whisper_test_config())


def get_test_config(config_type: str = 'unit') -> TestConfig:
    """Função de conveniência para obter configuração de teste."""
    return test_config_manager.get_config(config_type)