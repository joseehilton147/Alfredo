"""Configuração global de testes para pytest."""

import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock

# Adicionar o diretório src ao PYTHONPATH
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar fixtures base para disponibilizar mocks e dependências para todos os testes
from tests.fixtures.base_fixtures import *
# from tests.fixtures.mock_dependencies import *
# from tests.fixtures.test_config import *

# Configuração do loop de eventos para testes assíncronos
@pytest.fixture(scope="session")
def event_loop():
    """Cria um loop de eventos para toda a sessão de testes."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Fixtures para diretórios de teste
@pytest.fixture
def test_data_dir():
    """Diretório com dados de teste."""
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Diretório temporário para saídas de teste."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


# Fixtures específicas para diferentes tipos de teste
@pytest.fixture
def unit_test_setup(mock_config):
    """Setup para testes unitários."""
    return {
        'config': mock_config,
        'mock_external_deps': True,
        'timeout': 5.0
    }


@pytest.fixture
def integration_test_setup(mock_config):
    """Setup para testes de integração."""
    return {
        'config': mock_config,
        'mock_external_deps': False,
        'timeout': 30.0
    }


@pytest.fixture
def e2e_test_setup(mock_config):
    """Setup para testes end-to-end."""
    return {
        'config': mock_config,
        'mock_external_deps': False,
        'use_real_network': True,
        'timeout': 300.0
    }


# Fixtures para cenários de teste comuns
@pytest.fixture
def youtube_test_url():
    """URL de teste do YouTube."""
    return "https://www.youtube.com/watch?v=FZ42HMWG6xg"


@pytest.fixture
def sample_video_urls():
    """URLs de vídeo de exemplo para testes."""
    return [
        "https://www.youtube.com/watch?v=test1",
        "https://www.youtube.com/watch?v=test2",
        "https://youtu.be/test3"
    ]


# Fixtures para validação de dados
@pytest.fixture
def valid_video_inputs():
    """Entradas válidas para criação de vídeo."""
    return [
        {
            'id': 'valid_1',
            'title': 'Vídeo Válido 1',
            'duration': 120.0,
            'file_path': '/path/to/video1.mp4'
        },
        {
            'id': 'valid_2', 
            'title': 'Vídeo Válido 2',
            'duration': 300.0,
            'url': 'https://youtube.com/watch?v=valid2'
        }
    ]


@pytest.fixture
def invalid_video_inputs():
    """Entradas inválidas para testes de validação."""
    return [
        {'id': '', 'title': 'Título válido'},  # ID vazio
        {'id': 'a' * 300, 'title': 'Título válido'},  # ID muito longo
        {'id': 'valid_id', 'title': ''},  # Título vazio
        {'id': 'valid_id', 'title': 'Título válido', 'duration': -10},  # Duração negativa
        {'id': 'valid_id', 'title': 'Título válido'}  # Sem fontes
    ]


# Fixtures para testes de performance
@pytest.fixture
def performance_test_videos():
    """Dados de vídeo para testes de performance."""
    return {
        'small': {'duration': 30, 'size_mb': 10},
        'medium': {'duration': 300, 'size_mb': 100},
        'large': {'duration': 1800, 'size_mb': 500}
    }


# Fixtures para testes de segurança
@pytest.fixture
def malicious_inputs():
    """Inputs maliciosos para testes de segurança."""
    return {
        'sql_injection': [
            "'; DROP TABLE videos; --",
            "1' OR '1'='1",
            "admin'/*"
        ],
        'xss': [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src="x" onerror="alert(1)">'
        ],
        'path_traversal': [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam'
        ]
    }


# Configuração de cleanup automático
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup automático de arquivos de teste."""
    yield
    # Cleanup será executado após cada teste
    # Implementar limpeza se necessário


# Configuração de markers para pytest
def pytest_configure(config):
    """Configuração de markers personalizados."""
    config.addinivalue_line(
        "markers", "slow: marca testes como lentos"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "bdd: marca testes BDD"
    )
    config.addinivalue_line(
        "markers", "security: marca testes de segurança"
    )
    config.addinivalue_line(
        "markers", "performance: marca testes de performance"
    )


# Hooks do pytest para configuração adicional
def pytest_sessionstart(session):
    """Executado no início da sessão de testes."""
    sys.stdout.reconfigure(encoding='utf-8')
    print("\n🧪 Iniciando sessão de testes do Alfredo AI")


def pytest_sessionfinish(session, exitstatus):
    """Executado no final da sessão de testes."""
    print(f"\n✅ Sessão de testes finalizada com status: {exitstatus}")
    
    # Cleanup de configurações de teste
    # test_config_manager.cleanup_all_configs()  # Comentado temporariamente


# Configuração para testes paralelos (se usando pytest-xdist)
@pytest.fixture(scope="session", autouse=True)
def configure_parallel_tests():
    """Configuração para execução paralela de testes."""
    # Configurações específicas para testes paralelos
    pass
