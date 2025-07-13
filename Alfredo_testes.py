#!/usr/bin/env python3
"""
Comando para rodar todos os testes automatizados do projeto Alfredo.
Uso: python Alfredo_testes.py
"""
import sys
import subprocess

def main():
    try:
        print("Executando testes automatizados com pytest...\n")
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests', '--maxfail=1', '--disable-warnings', '-v'
        ])
        if result.returncode == 0:
            print("\nTodos os testes passaram com sucesso! ✅")
        else:
            print(f"\nAlguns testes falharam. Código de saída: {result.returncode}")
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("pytest não encontrado. Instale com: pip install pytest")
        sys.exit(1)

if __name__ == "__main__":
    main()
