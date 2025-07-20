#!/usr/bin/env python3
"""
Script para verificar eliminação de magic numbers e strings no projeto Alfredo AI.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict


class MagicValueFinder(ast.NodeVisitor):
    """Encontra magic values no código."""
    
    def __init__(self):
        self.magic_values = []
        self.allowed_numbers = {0, 1, -1, 2, 10, 100, 1000}
        self.allowed_strings = {
            "", " ", "\n", "\t", "utf-8", "ascii", 
            "GET", "POST", "PUT", "DELETE",
            "http", "https", "__main__", "__init__"
        }
    
    def visit_Constant(self, node):
        """Visita constantes no código."""
        if isinstance(node.value, (int, float)):
            if node.value not in self.allowed_numbers:
                self.magic_values.append({
                    'type': 'number',
                    'value': node.value,
                    'line': node.lineno,
                    'col': node.col_offset
                })
        
        elif isinstance(node.value, str):
            if (node.value not in self.allowed_strings and 
                len(node.value) > 1 and 
                not node.value.startswith('_')):
                self.magic_values.append({
                    'type': 'string',
                    'value': repr(node.value),
                    'line': node.lineno,
                    'col': node.col_offset
                })
        
        self.generic_visit(node)


def analyze_file(file_path: Path) -> List[Dict]:
    """Analisa um arquivo procurando magic values."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        finder = MagicValueFinder()
        finder.visit(tree)
        
        return finder.magic_values
    except Exception as e:
        print(f"⚠️  Erro ao analisar {file_path}: {e}")
        return []


def main() -> int:
    """Função principal."""
    print("🚀 Iniciando verificação de magic values...", flush=True)
    
    # Encontrar arquivos Python
    root_dir = Path.cwd()
    python_files = []
    
    for dir_name in ['src', 'tests', 'scripts']:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                if '__pycache__' not in str(py_file):
                    python_files.append(py_file)
    
    print(f"🔍 Analisando {len(python_files)} arquivos Python...", flush=True)
    
    total_magic_values = 0
    files_with_issues = 0
    
    for file_path in python_files:
        magic_values = analyze_file(file_path)
        
        if magic_values:
            files_with_issues += 1
            total_magic_values += len(magic_values)
            
            rel_path = os.path.relpath(file_path)
            print(f"\n📄 {rel_path} ({len(magic_values)} problemas)", flush=True)
            
            for mv in magic_values[:10]:  # Limitar a 10 por arquivo para não sobrecarregar
                icon = "🔢" if mv['type'] == 'number' else "📝"
                print(f"  {icon} Linha {mv['line']}: {mv['value']}", flush=True)
            
            if len(magic_values) > 10:
                print(f"  ... e mais {len(magic_values) - 10} magic values", flush=True)
    
    print(f"\n📊 RESUMO:", flush=True)
    print(f"  • Total de arquivos analisados: {len(python_files)}", flush=True)
    print(f"  • Arquivos com problemas: {files_with_issues}", flush=True)
    print(f"  • Total de magic values: {total_magic_values}", flush=True)
    
    if total_magic_values == 0:
        print("✅ Nenhum magic value encontrado!", flush=True)
        return 0
    else:
        print(f"❌ Encontrados {total_magic_values} magic values que precisam ser corrigidos.", flush=True)
        print("\n💡 SUGESTÕES:", flush=True)
        print("  • Mover strings constantes para um módulo de constantes", flush=True)
        print("  • Criar enums para valores relacionados", flush=True)
        print("  • Centralizar configurações em AlfredoConfig", flush=True)
        return 1


if __name__ == "__main__":
    exit(main())