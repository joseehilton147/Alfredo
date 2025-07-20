#!/usr/bin/env python3
"""
Script para validar conformidade da estrutura de diretórios com Clean Architecture.
"""

import os
from pathlib import Path
from typing import Dict, List, Set
import sys

class DirectoryStructureValidator:
    """Validador da estrutura de diretórios conforme Clean Architecture."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.tests_path = project_root / "tests"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> bool:
        """Executa todas as validações de estrutura."""
        print("🔍 Validando estrutura de diretórios...")
        
        # Validações principais
        self._validate_clean_architecture_layers()
        self._validate_layer_separation()
        self._validate_naming_conventions()
        self._validate_test_structure()
        self._validate_required_files()
        
        # Relatório final
        self._print_report()
        
        return len(self.errors) == 0
    
    def _validate_clean_architecture_layers(self):
        """Valida que as camadas da Clean Architecture estão presentes."""
        required_layers = {
            "domain": ["entities", "exceptions", "validators", "repositories"],
            "application": ["use_cases", "gateways", "interfaces"],
            "infrastructure": ["providers", "repositories", "factories", "storage", "downloaders", "extractors"],
            "presentation": ["cli"],
            "config": []
        }
        
        for layer, subdirs in required_layers.items():
            layer_path = self.src_path / layer
            
            if not layer_path.exists():
                self.errors.append(f"❌ Camada obrigatória ausente: src/{layer}")
                continue
                
            if not layer_path.is_dir():
                self.errors.append(f"❌ {layer} deve ser um diretório")
                continue
                
            # Verificar subdiretórios obrigatórios
            for subdir in subdirs:
                subdir_path = layer_path / subdir
                if not subdir_path.exists():
                    self.errors.append(f"❌ Subdiretório obrigatório ausente: src/{layer}/{subdir}")
                elif not subdir_path.is_dir():
                    self.errors.append(f"❌ src/{layer}/{subdir} deve ser um diretório")
    
    def _validate_layer_separation(self):
        """Valida que as camadas estão corretamente separadas."""
        # Verificar que domain não tem dependências externas
        domain_files = self._get_python_files(self.src_path / "domain")
        for file_path in domain_files:
            content = self._read_file_safe(file_path)
            if content:
                # Verificar imports proibidos no domain
                forbidden_imports = [
                    "from src.application",
                    "from src.infrastructure", 
                    "from src.presentation",
                    "import requests",
                    "import yt_dlp",
                    "import ffmpeg"
                ]
                
                for forbidden in forbidden_imports:
                    if forbidden in content:
                        self.errors.append(f"❌ Domain layer com dependência proibida em {file_path.relative_to(self.project_root)}: {forbidden}")
        
        # Verificar que application não depende de infrastructure
        app_files = self._get_python_files(self.src_path / "application")
        for file_path in app_files:
            content = self._read_file_safe(file_path)
            if content:
                if "from src.infrastructure" in content:
                    self.errors.append(f"❌ Application layer com dependência proibida de Infrastructure em {file_path.relative_to(self.project_root)}")
    
    def _validate_naming_conventions(self):
        """Valida convenções de nomenclatura."""
        # Verificar snake_case para arquivos Python
        python_files = self._get_python_files(self.src_path)
        for file_path in python_files:
            filename = file_path.stem
            if filename != "__init__" and not self._is_snake_case(filename):
                self.warnings.append(f"⚠️  Arquivo não segue snake_case: {file_path.relative_to(self.project_root)}")
        
        # Verificar que diretórios seguem snake_case
        for root, dirs, files in os.walk(self.src_path):
            for dir_name in dirs:
                if dir_name != "__pycache__" and not self._is_snake_case(dir_name):
                    self.warnings.append(f"⚠️  Diretório não segue snake_case: {Path(root).relative_to(self.project_root)}/{dir_name}")
    
    def _validate_test_structure(self):
        """Valida que estrutura de testes espelha src/."""
        # Verificar que principais diretórios de src/ têm correspondentes em tests/
        src_dirs = {d.name for d in self.src_path.iterdir() if d.is_dir() and d.name != "__pycache__"}
        test_dirs = {d.name for d in self.tests_path.iterdir() if d.is_dir() and d.name != "__pycache__"}
        
        # Diretórios específicos de teste são permitidos
        test_specific_dirs = {"bdd", "integration", "performance", "security", "shared", "unit", "fixtures"}
        
        missing_test_dirs = src_dirs - test_dirs - test_specific_dirs
        for missing_dir in missing_test_dirs:
            self.warnings.append(f"⚠️  Diretório de teste ausente para: tests/{missing_dir}")
        
        # Verificar estrutura unit/ espelha src/
        unit_path = self.tests_path / "unit"
        if unit_path.exists():
            unit_dirs = {d.name for d in unit_path.iterdir() if d.is_dir() and d.name != "__pycache__"}
            missing_unit_dirs = src_dirs - unit_dirs
            for missing_dir in missing_unit_dirs:
                self.warnings.append(f"⚠️  Diretório de teste unitário ausente: tests/unit/{missing_dir}")
    
    def _validate_required_files(self):
        """Valida presença de arquivos obrigatórios."""
        required_files = [
            "src/__init__.py",
            "src/main.py",
            "src/domain/__init__.py",
            "src/application/__init__.py", 
            "src/infrastructure/__init__.py",
            "src/presentation/__init__.py",
            "src/config/__init__.py",
            "tests/conftest.py",
            "requirements.txt",
            "requirements-dev.txt"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                if file_path.startswith("src/") and file_path.endswith("__init__.py"):
                    self.warnings.append(f"⚠️  Arquivo __init__.py ausente: {file_path}")
                else:
                    self.errors.append(f"❌ Arquivo obrigatório ausente: {file_path}")
    
    def _get_python_files(self, directory: Path) -> List[Path]:
        """Obtém todos os arquivos Python em um diretório."""
        if not directory.exists():
            return []
        
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Ignorar __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Lê arquivo de forma segura."""
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return ""
    
    def _is_snake_case(self, name: str) -> bool:
        """Verifica se nome segue snake_case."""
        if not name:
            return False
        
        # Permitir números e underscores
        return name.islower() and "_" not in name or all(
            c.islower() or c.isdigit() or c == "_" for c in name
        ) and not name.startswith("_") and not name.endswith("_")
    
    def _print_report(self):
        """Imprime relatório de validação."""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE VALIDAÇÃO DA ESTRUTURA DE DIRETÓRIOS")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERROS CRÍTICOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ ESTRUTURA DE DIRETÓRIOS TOTALMENTE CONFORME!")
        elif not self.errors:
            print(f"\n✅ ESTRUTURA VÁLIDA com {len(self.warnings)} avisos menores")
        else:
            print(f"\n❌ ESTRUTURA INVÁLIDA: {len(self.errors)} erros críticos")
        
        print("="*60)


def main():
    """Função principal."""
    project_root = Path(__file__).parent.parent
    validator = DirectoryStructureValidator(project_root)
    
    success = validator.validate_all()
    
    if success:
        print("\n🎉 Validação da estrutura de diretórios APROVADA!")
        sys.exit(0)
    else:
        print("\n💥 Validação da estrutura de diretórios REPROVADA!")
        sys.exit(1)


if __name__ == "__main__":
    main()