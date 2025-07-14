#!/usr/bin/env python3
"""
🤖 ALFREDO AI - New Architecture Entry Point
============================================
Modern entry point using the new modular architecture
"""

import sys
from pathlib import Path

def main() -> None:
    """Main entry point da nova arquitetura
    
    Responsabilidades:
    1. Inicializar configurações básicas
    2. Garantir estrutura de diretórios
    3. Disparar a interface de linha de comando
    
    Raises:
        SystemExit: Em caso de erro crítico na inicialização
    """
    try:
        from config.settings import config
        from cli.alfredo import main as cli_main
        
        config.ensure_directories()
        cli_main()
    except Exception as e:
        from core.alfredo_core import handle_startup_error
        handle_startup_error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
