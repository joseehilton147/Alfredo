"""Configuração dos testes."""
import sys
from pathlib import Path

# Adicionar o diretório src ao PYTHONPATH
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
