"""Configuração específica para pytest-bdd."""
import pytest
from pytest_bdd import given, when, then, scenarios
from pathlib import Path

# Configuração base para features
FEATURES_BASE_DIR = Path(__file__).parent / "features"

def load_scenarios_from_feature(feature_name: str):
    """Carrega cenários de um arquivo feature específico."""
    feature_path = FEATURES_BASE_DIR / f"{feature_name}.feature"
    if feature_path.exists():
        return scenarios(str(feature_path))
    else:
        raise FileNotFoundError(f"Feature file not found: {feature_path}")

# Configuração de relatórios
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Hook para capturar erros em steps BDD."""
    print(f"BDD Step Error in {feature.filename}:")
    print(f"  Scenario: {scenario.name}")
    print(f"  Step: {step.name}")
    print(f"  Error: {exception}")

def pytest_bdd_before_scenario(request, feature, scenario):
    """Hook executado antes de cada cenário."""
    print(f"\n🎬 Executando cenário: {scenario.name}")

def pytest_bdd_after_scenario(request, feature, scenario):
    """Hook executado após cada cenário."""
    print(f"✅ Cenário concluído: {scenario.name}")

# Utilitários para steps
class BDDStepHelpers:
    """Helpers para steps BDD."""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Valida se uma URL é válida."""
        import re
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """Valida se um caminho de arquivo é válido."""
        try:
            return Path(path).exists()
        except Exception:
            return False
    
    @staticmethod
    def measure_execution_time(func):
        """Decorator para medir tempo de execução."""
        import time
        import functools
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            return result, execution_time
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            return result, execution_time
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper