#!/usr/bin/env python3
"""
Script para validar regras de dependência da Clean Architecture.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import sys


class CleanArchitectureDependencyChecker:
    """Verificador das regras de dependência da Clean Architecture."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.violations: List[str] = []
        self.warnings: List[str] = []
        
        # Definir camadas e suas dependências permitidas
        self.layer_dependencies = {
            "domain": [],  # Domain não pode depender de nada
            "application": ["domain"],  # Application pode depender apenas de Domain
            "infrastructure": ["domain", "application"],  # Infrastructure pode depender de Domain e Application
            "presentation": ["domain", "application"],  # Presentation pode depender de Domain e Application
            "config": []  # Config é independente
        }
        
    def check_dependency_rules(self) -> bool:
        """Executa verificação das regras de dependência."""
        print("🔍 Verificando regras de dependência da Clean Architecture...")
        
        self._check_domain_independence()
        self._check_application_dependencies()
        self._check_infrastructure_dependencies()
        self._check_presentation_dependencies()
        self._check_forbidden_circular_dependencies()
        
        self._print_report()
        
        return len(self.violations) == 0
    
    def _check_domain_independence(self):
        """Verifica que Domain não depende de camadas externas."""
        print("📋 Verificando independência da camada Domain...")
        
        domain_files = self._get_python_files(self.src_path / "domain")
        
        forbidden_imports = [
            "from src.application",
            "from src.infrastructure", 
            "from src.presentation",
            "from src.config",
            "import requests",
            "import yt_dlp",
            "import ffmpeg",
            "import groq",
            "import openai",
            "import whisper"
        ]
        
        for file_path in domain_files:
            content = self._read_file_safe(file_path)
            if not content:
                continue
                
            for forbidden in forbidden_imports:
                if forbidden in content:
                    self.violations.append(
                        f"❌ DOMAIN: {file_path.relative_to(self.project_root)} "
                        f"tem dependência proibida: {forbidden}"
                    )
        
        # Verificar imports relativos proibidos
        for file_path in domain_files:
            content = self._read_file_safe(file_path)
            if not content:
                continue
                
            # Procurar por imports que saem da camada domain
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('from ') and 'src.' in line:
                    # Extrair o módulo importado
                    match = re.match(r'from\s+(src\.[^\s]+)', line)
                    if match:
                        imported_module = match.group(1)
                        if not imported_module.startswith('src.domain'):
                            self.violations.append(
                                f"❌ DOMAIN: {file_path.relative_to(self.project_root)}:{i} "
                                f"importa de fora da camada domain: {imported_module}"
                            )
    
    def _check_application_dependencies(self):
        """Verifica que Application depende apenas de Domain."""
        print("📋 Verificando dependências da camada Application...")
        
        app_files = self._get_python_files(self.src_path / "application")
        
        forbidden_imports = [
            "from src.infrastructure",
            "from src.presentation"
        ]
        
        for file_path in app_files:
            content = self._read_file_safe(file_path)
            if not content:
                continue
                
            for forbidden in forbidden_imports:
                if forbidden in content:
                    self.violations.append(
                        f"❌ APPLICATION: {file_path.relative_to(self.project_root)} "
                        f"tem dependência proibida: {forbidden}"
                    )
        
        # Verificar se Application usa interfaces, não implementações
        for file_path in app_files:
            content = self._read_file_safe(file_path)
            if not content:
                continue
                
            # Procurar por instanciação direta de classes de infraestrutura
            forbidden_instantiations = [
                "WhisperProvider(",
                "GroqProvider(",
                "OllamaProvider(",
                "YTDLPDownloader(",
                "FFmpegExtractor(",
                "FileSystemStorage(",
                "JsonVideoRepository("
            ]
            
            for forbidden in forbidden_instantiations:
                if forbidden in content:
                    self.violations.append(
                        f"❌ APPLICATION: {file_path.relative_to(self.project_root)} "
                        f"instancia implementação concreta: {forbidden}"
                    )
    
    def _check_infrastructure_dependencies(self):
        """Verifica que Infrastructure implementa interfaces de Application."""
        print("📋 Verificando dependências da camada Infrastructure...")
        
        infra_files = self._get_python_files(self.src_path / "infrastructure")
        
        # Verificar se implementações de infraestrutura implementam interfaces
        gateway_implementations = 0
        
        for file_path in infra_files:
            content = self._read_file_safe(file_path)
            if not content:
                continue
                
            # Procurar por implementações de gateways
            if "Gateway" in content and "class " in content:
                # Verificar se herda de uma interface
                if "from src.application.gateways" in content or "from src.application.interfaces" in content:
                    gateway_implementations += 1
                else:
                    self.warnings.append(
                        f"⚠️  INFRASTRUCTURE: {file_path.relative_to(self.project_root)} "
                        "parece implementar gateway mas não importa interface"
                    )
        
        if gateway_implementations < 3:
            self.warnings.append(
                f"⚠️  INFRASTRUCTURE: Poucas implementações de gateway encontradas ({gateway_implementations})"
            )
    
    def _check_presentation_dependencies(self):
        """Verifica que Presentation usa apenas Application."""
        print("📋 Verificando dependências da camada Presentation...")
        
        presentation_files = self._get_python_files(self.src_path / "presentation")
        
        # Verificar se Presentation não acessa Infrastructure diretamente
        for file_path in presentation_files:
            content = self._read_file_safe(file_path)
            if not content:
                continue
                
            # Procurar por imports diretos de infrastructure
            if "from src.infrastructure" in content:
                # Exceção para factory - é permitido
                if "from src.infrastructure.factories" not in content:
                    self.violations.append(
                        f"❌ PRESENTATION: {file_path.relative_to(self.project_root)} "
                        "importa diretamente de Infrastructure (use Factory)"
                    )
            
            # Verificar se usa Use Cases ao invés de lógica de negócio
            business_logic_indicators = [
                "yt_dlp.YoutubeDL",
                "whisper.load_model",
                "ffmpeg.input",
                "groq.Groq"
            ]
            
            for indicator in business_logic_indicators:
                if indicator in content:
                    self.violations.append(
                        f"❌ PRESENTATION: {file_path.relative_to(self.project_root)} "
                        f"contém lógica de negócio: {indicator}"
                    )
    
    def _check_forbidden_circular_dependencies(self):
        """Verifica se há dependências circulares."""
        print("📋 Verificando dependências circulares...")
        
        # Mapear todas as dependências
        dependencies = {}
        
        for layer in ["domain", "application", "infrastructure", "presentation"]:
            layer_path = self.src_path / layer
            if not layer_path.exists():
                continue
                
            dependencies[layer] = set()
            layer_files = self._get_python_files(layer_path)
            
            for file_path in layer_files:
                content = self._read_file_safe(file_path)
                if not content:
                    continue
                    
                # Encontrar imports de outras camadas
                for other_layer in ["domain", "application", "infrastructure", "presentation"]:
                    if other_layer != layer:
                        if f"from src.{other_layer}" in content:
                            dependencies[layer].add(other_layer)
        
        # Verificar dependências circulares
        for layer, deps in dependencies.items():
            for dep in deps:
                if dep in dependencies and layer in dependencies[dep]:
                    self.violations.append(
                        f"❌ CIRCULAR: Dependência circular entre {layer} e {dep}"
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
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Lê arquivo de forma segura."""
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return ""
    
    def _print_report(self):
        """Imprime relatório de conformidade."""
        print("\n" + "="*70)
        print("📋 RELATÓRIO DE CONFORMIDADE - CLEAN ARCHITECTURE")
        print("="*70)
        
        if self.violations:
            print(f"\n❌ VIOLAÇÕES CRÍTICAS ({len(self.violations)}):")
            for violation in self.violations:
                print(f"  {violation}")
        
        if self.warnings:
            print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.violations and not self.warnings:
            print("\n✅ CLEAN ARCHITECTURE TOTALMENTE CONFORME!")
        elif not self.violations:
            print(f"\n✅ CLEAN ARCHITECTURE CONFORME com {len(self.warnings)} avisos menores")
        else:
            print(f"\n❌ VIOLAÇÕES DE CLEAN ARCHITECTURE: {len(self.violations)} críticas")
        
        print("="*70)


def main():
    """Função principal."""
    project_root = Path(__file__).parent.parent
    checker = CleanArchitectureDependencyChecker(project_root)
    
    success = checker.check_dependency_rules()
    
    if success:
        print("\n🎉 Verificação Clean Architecture APROVADA!")
        sys.exit(0)
    else:
        print("\n💥 Verificação Clean Architecture REPROVADA!")
        sys.exit(1)


if __name__ == "__main__":
    main()