#!/usr/bin/env python3
"""Executa o magic values check diretamente."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from magic_values_check import main

if __name__ == "__main__":
    print("Executando magic values check...")
    result = main()
    print(f"Resultado: {result}")