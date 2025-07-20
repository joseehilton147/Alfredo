#!/usr/bin/env python3
"""Teste simples do magic values check."""

import ast
from pathlib import Path

def test_magic_check():
    print("🚀 Teste do magic values check")
    
    # Verificar se conseguimos encontrar arquivos
    root_dir = Path.cwd()
    print(f"📁 Diretório atual: {root_dir}")
    
    src_dir = root_dir / 'src'
    print(f"📂 Diretório src existe: {src_dir.exists()}")
    
    if src_dir.exists():
        py_files = list(src_dir.rglob('*.py'))
        print(f"🔍 Arquivos Python em src: {len(py_files)}")
        
        for py_file in py_files[:3]:
            print(f"  • {py_file}")
            
            # Tentar analisar um arquivo
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
                print(f"    ✅ Análise AST bem-sucedida")
            except Exception as e:
                print(f"    ❌ Erro na análise: {e}")

if __name__ == "__main__":
    test_magic_check()