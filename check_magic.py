#!/usr/bin/env python3
"""Verificação rápida de magic values."""

import ast
import os
from pathlib import Path

def check_magic_values():
    """Verifica magic values no projeto."""
    print("🚀 Verificando magic values...")
    
    # Encontrar arquivos Python
    root_dir = Path.cwd()
    python_files = []
    
    for dir_name in ['src']:  # Focar apenas em src por enquanto
        dir_path = root_dir / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                if '__pycache__' not in str(py_file):
                    python_files.append(py_file)
    
    print(f"🔍 Analisando {len(python_files)} arquivos Python...")
    
    total_magic_values = 0
    files_with_issues = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            magic_values = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)) and node.value not in {0, 1, -1, 2, 10, 100}:
                        magic_values.append(f"🔢 Linha {node.lineno}: {node.value}")
                    elif isinstance(node.value, str) and len(node.value) > 3 and not node.value.startswith('_'):
                        # Filtrar strings muito comuns
                        if node.value not in {'utf-8', 'ascii', '__main__', 'GET', 'POST'}:
                            magic_values.append(f"📝 Linha {node.lineno}: {repr(node.value)[:50]}...")
            
            if magic_values:
                files_with_issues += 1
                total_magic_values += len(magic_values)
                
                rel_path = os.path.relpath(file_path)
                print(f"\n📄 {rel_path} ({len(magic_values)} problemas)")
                
                for mv in magic_values[:5]:  # Mostrar apenas os primeiros 5
                    print(f"  {mv}")
                
                if len(magic_values) > 5:
                    print(f"  ... e mais {len(magic_values) - 5} magic values")
        
        except Exception as e:
            print(f"⚠️  Erro ao analisar {file_path}: {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"  • Total de arquivos analisados: {len(python_files)}")
    print(f"  • Arquivos com problemas: {files_with_issues}")
    print(f"  • Total de magic values: {total_magic_values}")
    
    if total_magic_values > 0:
        print(f"\n💡 RECOMENDAÇÕES:")
        print(f"  • Criar módulo src/config/constants.py para strings constantes")
        print(f"  • Mover configurações para AlfredoConfig")
        print(f"  • Usar enums para valores relacionados")
    
    return total_magic_values

if __name__ == "__main__":
    result = check_magic_values()
    if result > 0:
        print(f"\n❌ Encontrados {result} magic values que precisam ser corrigidos.")
    else:
        print("\n✅ Nenhum magic value encontrado!")