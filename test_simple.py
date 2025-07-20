print("Teste simples")
import ast
from pathlib import Path

root_dir = Path.cwd()
src_dir = root_dir / 'src'
print(f"Src dir exists: {src_dir.exists()}")

if src_dir.exists():
    py_files = list(src_dir.rglob('*.py'))
    print(f"Found {len(py_files)} Python files")
    
    if py_files:
        first_file = py_files[0]
        print(f"Analyzing: {first_file}")
        
        try:
            with open(first_file, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            print("AST parsing successful")
            
            # Procurar por constantes
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)) and node.value not in {0, 1, -1, 2}:
                        print(f"Magic number found: {node.value} at line {node.lineno}")
                    elif isinstance(node.value, str) and len(node.value) > 1:
                        print(f"Magic string found: {repr(node.value)} at line {node.lineno}")
                        
        except Exception as e:
            print(f"Error: {e}")