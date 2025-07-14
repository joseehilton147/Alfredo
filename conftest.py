#!/usr/bin/env python3
"""
Configuração global do pytest para o projeto Alfredo AI
"""

import pytest
from pathlib import Path

@pytest.fixture
def project_root():
    """Retorna o diretório raiz do projeto"""
    return Path(__file__).parent
