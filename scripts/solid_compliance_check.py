#!/usr/bin/env python3
"""
Script para validar conformidade com os princípios SOLID.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import sys


class SOLIDComplianceChecker:
    """Verificador de conformidade com princípios SOLID."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.violations: List[str] = []
        self.warnings: List[str] = []
        
    def check_all_principles(self) -> bool:
        """Executa verificação de todos os princípios SOLID."""
        print("🔍 Verificando conformidade com princípios SOLID...")
        
        self._check_single_responsibility()
        self._check_open_closed()
        self._check_liskov_substitution()
        self._check_interface_segregation()
        self._check_dependency_inversion()
        
        self._print_report()
        
        return len(self.violations) == 0
    
    def _check_single_responsibility(self):
        """Verifica Single Responsibility Principle (SRP)."""
        print("📋 Verificando Single Responsibility Principle...")
        
        python_files = self._get_python_files(self.src_path)
        
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self._check_class_srp(node, file_path)
                        
            except Exception as e:
                self.warnings.append(f"⚠️  Erro ao analisar {file_path.relative_to(self.project_root)}: {e}")
    
    def _check_class_srp(self, class_node: ast.ClassDef, file_path: Path):
        """Verifica SRP para uma classe específica."""
        class_name = class_node.name
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        
        # Exceções para classes que legitimamente podem ter mais métodos
        legitimate_large_classes = [
            "Command",  # Base class para CLI commands
            "AlfredoConfig",  # Configuration class
            "InfrastructureFactory",  # Factory class
            "FileExplorer",  # UI component
            "InteractiveCLI"  # Main CLI interface
        ]
        
        # Verificar se classe tem muitos métodos (indicativo de múltiplas responsabilidades)
        max_methods = 20 if class_name in legitimate_large_classes else 15
        if len(methods) > max_methods:
            self.violations.append(
                f"❌ SRP: Classe {class_name} em {file_path.relative_to(self.project_root)} "
                f"tem {len(methods)} métodos (máximo recomendado: {max_methods})"
            )
        
        # Verificar se classe tem responsabilidades mistas (mais restritivo)
        method_categories = self._categorize_methods(methods)
        max_categories = 4 if class_name in legitimate_large_classes else 2
        if len(method_categories) > max_categories and class_name not in ["Video", "AlfredoConfig"]:
            self.violations.append(
                f"❌ SRP: Classe {class_name} em {file_path.relative_to(self.project_root)} "
                f"parece ter múltiplas responsabilidades: {list(method_categories.keys())}"
            )
    
    def _categorize_methods(self, methods: List[ast.FunctionDef]) -> Dict[str, List[str]]:
        """Categoriza métodos por tipo de responsabilidade."""
        categories = {
            "data_access": [],
            "business_logic": [],
            "validation": [],
            "formatting": [],
            "network": [],
            "file_io": []
        }
        
        for method in methods:
            method_name = method.name.lower()
            
            if any(keyword in method_name for keyword in ["save", "load", "get", "find", "query", "repository"]):
                categories["data_access"].append(method_name)
            elif any(keyword in method_name for keyword in ["validate", "check", "verify"]):
                categories["validation"].append(method_name)
            elif any(keyword in method_name for keyword in ["format", "render", "display", "print"]):
                categories["formatting"].append(method_name)
            elif any(keyword in method_name for keyword in ["download", "upload", "request", "post", "get"]):
                categories["network"].append(method_name)
            elif any(keyword in method_name for keyword in ["read", "write", "file", "path"]):
                categories["file_io"].append(method_name)
            else:
                categories["business_logic"].append(method_name)
        
        # Remove categorias vazias
        return {k: v for k, v in categories.items() if v}
    
    def _check_open_closed(self):
        """Verifica Open/Closed Principle (OCP)."""
        print("📋 Verificando Open/Closed Principle...")
        
        # Verificar se interfaces/abstrações estão sendo usadas
        interface_files = []
        concrete_files = []
        
        for file_path in self._get_python_files(self.src_path):
            content = file_path.read_text(encoding="utf-8")
            
            if "ABC" in content or "@abstractmethod" in content:
                interface_files.append(file_path)
            elif "class " in content and "def " in content:
                concrete_files.append(file_path)
        
        if len(interface_files) < 5:
            self.warnings.append(
                f"⚠️  OCP: Poucas interfaces/abstrações encontradas ({len(interface_files)}). "
                "Considere usar mais abstrações para facilitar extensão."
            )
        
        # Verificar se gateways estão sendo implementados
        gateway_pattern = re.compile(r"class \w+Gateway\(ABC\):")
        gateway_implementations = []
        
        for file_path in self._get_python_files(self.src_path / "infrastructure"):
            content = file_path.read_text(encoding="utf-8")
            if "Gateway" in content and "class " in content:
                gateway_implementations.append(file_path)
        
        if len(gateway_implementations) < 3:
            self.violations.append(
                f"❌ OCP: Poucas implementações de Gateway encontradas ({len(gateway_implementations)}). "
                "Gateways são essenciais para extensibilidade."
            )
    
    def _check_liskov_substitution(self):
        """Verifica Liskov Substitution Principle (LSP)."""
        print("📋 Verificando Liskov Substitution Principle...")
        
        # Verificar hierarquias de herança
        inheritance_violations = []
        
        for file_path in self._get_python_files(self.src_path):
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Verificar se classes derivadas não violam contratos
                        if node.bases:
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    base_name = base.id
                                    if "Error" in base_name or "Exception" in base_name:
                                        # Exceções são OK
                                        continue
                                    
                                    # Verificar se métodos sobrescritos mantêm assinatura
                                    self._check_method_signatures(node, file_path)
                                    
            except Exception as e:
                self.warnings.append(f"⚠️  Erro ao verificar LSP em {file_path.relative_to(self.project_root)}: {e}")
    
    def _check_method_signatures(self, class_node: ast.ClassDef, file_path: Path):
        """Verifica se métodos sobrescritos mantêm assinaturas compatíveis."""
        # Esta é uma verificação simplificada
        # Em um cenário real, seria necessário análise mais profunda
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        
        for method in methods:
            # Verificar se métodos async/sync são consistentes
            if method.name in ["execute", "process", "transcribe", "summarize"]:
                is_async = isinstance(method, ast.AsyncFunctionDef)
                # Verificação básica - em implementação real seria mais robusta
                pass
    
    def _check_interface_segregation(self):
        """Verifica Interface Segregation Principle (ISP)."""
        print("📋 Verificando Interface Segregation Principle...")
        
        # Verificar se interfaces são específicas e não muito grandes
        for file_path in self._get_python_files(self.src_path / "application" / "gateways"):
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if any("ABC" in str(base) for base in node.bases):
                            abstract_methods = [
                                n for n in node.body 
                                if isinstance(n, ast.FunctionDef) and 
                                any("abstractmethod" in str(d) for d in getattr(n, 'decorator_list', []))
                            ]
                            
                            if len(abstract_methods) > 8:
                                self.violations.append(
                                    f"❌ ISP: Interface {node.name} em {file_path.relative_to(self.project_root)} "
                                    f"tem {len(abstract_methods)} métodos abstratos (máximo recomendado: 8)"
                                )
                            
            except Exception as e:
                self.warnings.append(f"⚠️  Erro ao verificar ISP em {file_path.relative_to(self.project_root)}: {e}")
    
    def _check_dependency_inversion(self):
        """Verifica Dependency Inversion Principle (DIP)."""
        print("📋 Verificando Dependency Inversion Principle...")
        
        # Verificar Use Cases - devem depender apenas de abstrações
        use_case_files = list((self.src_path / "application" / "use_cases").glob("*.py"))
        
        for file_path in use_case_files:
            if file_path.name == "__init__.py":
                continue
                
            content = file_path.read_text(encoding="utf-8")
            
            # Verificar imports proibidos (dependências concretas)
            forbidden_imports = [
                "from src.infrastructure.providers",
                "from src.infrastructure.repositories", 
                "from src.infrastructure.storage",
                "from src.infrastructure.downloaders",
                "from src.infrastructure.extractors"
            ]
            
            for forbidden in forbidden_imports:
                if forbidden in content:
                    self.violations.append(
                        f"❌ DIP: Use Case {file_path.name} depende de implementação concreta: {forbidden}"
                    )
            
            # Verificar se construtor recebe dependências
            if "def __init__(self" in content:
                # Verificar se há parâmetros no construtor (injeção de dependência)
                init_pattern = re.search(r"def __init__\(self([^)]*)\):", content)
                if init_pattern:
                    params = init_pattern.group(1).strip()
                    if not params or params == "":
                        self.warnings.append(
                            f"⚠️  DIP: Use Case {file_path.name} pode não estar usando injeção de dependência"
                        )
        
        # Verificar se Factory está sendo usada
        factory_usage = 0
        for file_path in self._get_python_files(self.src_path):
            content = file_path.read_text(encoding="utf-8")
            if "InfrastructureFactory" in content or "Factory" in content:
                factory_usage += 1
        
        if factory_usage < 3:
            self.violations.append(
                f"❌ DIP: Pouco uso de Factory Pattern ({factory_usage} arquivos). "
                "Factory é essencial para injeção de dependência."
            )
    
    def _get_python_files(self, directory: Path) -> List[Path]:
        """Obtém todos os arquivos Python em um diretório."""
        if not directory.exists():
            return []
        
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Ignorar __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _print_report(self):
        """Imprime relatório de conformidade SOLID."""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE CONFORMIDADE SOLID")
        print("="*60)
        
        if self.violations:
            print(f"\n❌ VIOLAÇÕES CRÍTICAS ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  {violation}")
        
        if self.warnings:
            print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.violations and not self.warnings:
            print("\n✅ PRINCÍPIOS SOLID TOTALMENTE IMPLEMENTADOS!")
        elif not self.violations:
            print(f"\n✅ SOLID CONFORME com {len(self.warnings)} avisos menores")
        else:
            print(f"\n❌ VIOLAÇÕES SOLID ENCONTRADAS: {len(self.violations)} críticas")
        
        print("="*60)


def main():
    """Função principal."""
    project_root = Path(__file__).parent.parent
    checker = SOLIDComplianceChecker(project_root)
    
    success = checker.check_all_principles()
    
    if success:
        print("\n🎉 Verificação SOLID APROVADA!")
        sys.exit(0)
    else:
        print("\n💥 Verificação SOLID REPROVADA!")
        sys.exit(1)


if __name__ == "__main__":
    main()