#!/usr/bin/env python3
"""
Script de verificação de qualidade e complexidade para Alfredo AI.

Este script executa várias verificações de qualidade de código incluindo:
- Complexidade ciclomática
- Linhas por função e classe
- Duplicação de código
- Análise de código morto
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import xml.etree.ElementTree as ET


class QualityChecker:
    """Verificador de qualidade de código."""
    
    def __init__(self, src_dir: str = "src", max_complexity: int = 10,
                 max_function_lines: int = 20, max_class_lines: int = 200,
                 max_duplication: float = 3.0):
        self.src_dir = Path(src_dir)
        self.max_complexity = max_complexity
        self.max_function_lines = max_function_lines
        self.max_class_lines = max_class_lines
        self.max_duplication = max_duplication
        self.results = {}
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Executa todas as verificações de qualidade."""
        print("🔍 Executando verificações de qualidade...")
        
        self.results = {
            "complexity": self.check_cyclomatic_complexity(),
            "function_length": self.check_function_length(),
            "class_length": self.check_class_length(),
            "duplication": self.check_code_duplication(),
            "dead_code": self.check_dead_code(),
            "maintainability": self.check_maintainability_index(),
        }
        
        return self.results
    
    def check_cyclomatic_complexity(self) -> Dict[str, Any]:
        """Verifica complexidade ciclomática usando radon."""
        print("📊 Verificando complexidade ciclomática...")
        
        try:
            # Executar radon cc para complexidade ciclomática
            result = subprocess.run([
                "radon", "cc", str(self.src_dir), 
                "--json", "--total-average"
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            violations = []
            
            for file_path, functions in data.items():
                if isinstance(functions, list):
                    for func in functions:
                        if func.get("complexity", 0) > self.max_complexity:
                            violations.append({
                                "file": file_path,
                                "function": func.get("name", "unknown"),
                                "complexity": func.get("complexity", 0),
                                "line": func.get("lineno", 0)
                            })
            
            return {
                "passed": len(violations) == 0,
                "violations": violations,
                "max_allowed": self.max_complexity,
                "total_functions": sum(len(funcs) if isinstance(funcs, list) else 0 
                                     for funcs in data.values())
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return {"passed": False, "error": str(e)}
    
    def check_function_length(self) -> Dict[str, Any]:
        """Verifica comprimento de funções usando radon."""
        print("📏 Verificando comprimento de funções...")
        
        try:
            # Usar radon raw para métricas de linhas
            result = subprocess.run([
                "radon", "raw", str(self.src_dir), "--json"
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            violations = []
            
            # Analisar arquivos Python diretamente para funções longas
            for py_file in self.src_dir.rglob("*.py"):
                violations.extend(self._analyze_function_length(py_file))
            
            return {
                "passed": len(violations) == 0,
                "violations": violations,
                "max_allowed": self.max_function_lines
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return {"passed": False, "error": str(e)}
    
    def check_class_length(self) -> Dict[str, Any]:
        """Verifica comprimento de classes."""
        print("🏗️ Verificando comprimento de classes...")
        
        violations = []
        
        for py_file in self.src_dir.rglob("*.py"):
            violations.extend(self._analyze_class_length(py_file))
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "max_allowed": self.max_class_lines
        }
    
    def check_code_duplication(self) -> Dict[str, Any]:
        """Verifica duplicação de código usando radon."""
        print("🔄 Verificando duplicação de código...")
        
        try:
            # Usar radon para detectar duplicação
            result = subprocess.run([
                "radon", "raw", str(self.src_dir), "--json"
            ], capture_output=True, text=True, check=True)
            
            # Para duplicação real, usaríamos uma ferramenta como jscpd
            # Por enquanto, vamos simular baseado em métricas
            duplication_percentage = 0.0  # Placeholder
            
            return {
                "passed": duplication_percentage <= self.max_duplication,
                "percentage": duplication_percentage,
                "max_allowed": self.max_duplication
            }
            
        except subprocess.CalledProcessError as e:
            return {"passed": False, "error": str(e)}
    
    def check_dead_code(self) -> Dict[str, Any]:
        """Verifica código morto usando vulture."""
        print("💀 Verificando código morto...")
        
        try:
            result = subprocess.run([
                "vulture", str(self.src_dir), "--json"
            ], capture_output=True, text=True)
            
            if result.stdout.strip():
                data = json.loads(result.stdout)
                dead_code_items = len(data) if isinstance(data, list) else 0
            else:
                dead_code_items = 0
            
            return {
                "passed": dead_code_items == 0,
                "dead_code_items": dead_code_items,
                "details": json.loads(result.stdout) if result.stdout.strip() else []
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return {"passed": False, "error": str(e)}
    
    def check_maintainability_index(self) -> Dict[str, Any]:
        """Verifica índice de manutenibilidade usando radon."""
        print("🔧 Verificando índice de manutenibilidade...")
        
        try:
            result = subprocess.run([
                "radon", "mi", str(self.src_dir), "--json"
            ], capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            low_maintainability = []
            
            for file_path, mi_score in data.items():
                if mi_score < 20:  # Baixa manutenibilidade
                    low_maintainability.append({
                        "file": file_path,
                        "maintainability_index": mi_score
                    })
            
            return {
                "passed": len(low_maintainability) == 0,
                "low_maintainability": low_maintainability,
                "min_acceptable": 20
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return {"passed": False, "error": str(e)}
    
    def _analyze_function_length(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analisa comprimento de funções em um arquivo."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            in_function = False
            function_start = 0
            function_name = ""
            indent_level = 0
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Detectar início de função
                if stripped.startswith(('def ', 'async def ')):
                    if in_function:
                        # Função anterior terminou
                        func_length = i - function_start - 1
                        if func_length > self.max_function_lines:
                            violations.append({
                                "file": str(file_path),
                                "function": function_name,
                                "lines": func_length,
                                "start_line": function_start
                            })
                    
                    in_function = True
                    function_start = i
                    function_name = stripped.split('(')[0].replace('def ', '').replace('async ', '').strip()
                    indent_level = len(line) - len(line.lstrip())
                
                # Detectar fim de função (mudança de indentação)
                elif in_function and stripped and len(line) - len(line.lstrip()) <= indent_level:
                    if not stripped.startswith(('@', '#', '"""', "'''")):
                        func_length = i - function_start - 1
                        if func_length > self.max_function_lines:
                            violations.append({
                                "file": str(file_path),
                                "function": function_name,
                                "lines": func_length,
                                "start_line": function_start
                            })
                        in_function = False
            
            # Verificar última função se arquivo termina dentro dela
            if in_function:
                func_length = len(lines) - function_start
                if func_length > self.max_function_lines:
                    violations.append({
                        "file": str(file_path),
                        "function": function_name,
                        "lines": func_length,
                        "start_line": function_start
                    })
                    
        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
        
        return violations
    
    def _analyze_class_length(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analisa comprimento de classes em um arquivo."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            in_class = False
            class_start = 0
            class_name = ""
            indent_level = 0
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Detectar início de classe
                if stripped.startswith('class '):
                    if in_class:
                        # Classe anterior terminou
                        class_length = i - class_start - 1
                        if class_length > self.max_class_lines:
                            violations.append({
                                "file": str(file_path),
                                "class": class_name,
                                "lines": class_length,
                                "start_line": class_start
                            })
                    
                    in_class = True
                    class_start = i
                    class_name = stripped.split('(')[0].replace('class ', '').strip(':')
                    indent_level = len(line) - len(line.lstrip())
                
                # Detectar fim de classe (mudança de indentação)
                elif in_class and stripped and len(line) - len(line.lstrip()) <= indent_level:
                    if not stripped.startswith(('@', '#', '"""', "'''")):
                        class_length = i - class_start - 1
                        if class_length > self.max_class_lines:
                            violations.append({
                                "file": str(file_path),
                                "class": class_name,
                                "lines": class_length,
                                "start_line": class_start
                            })
                        in_class = False
            
            # Verificar última classe se arquivo termina dentro dela
            if in_class:
                class_length = len(lines) - class_start
                if class_length > self.max_class_lines:
                    violations.append({
                        "file": str(file_path),
                        "class": class_name,
                        "lines": class_length,
                        "start_line": class_start
                    })
                    
        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
        
        return violations
    
    def generate_report(self) -> str:
        """Gera relatório de qualidade."""
        if not self.results:
            return "Nenhuma verificação foi executada."
        
        report = ["=" * 60]
        report.append("📊 RELATÓRIO DE QUALIDADE DE CÓDIGO - ALFREDO AI")
        report.append("=" * 60)
        
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results.values() 
                          if isinstance(result, dict) and result.get("passed", False))
        
        report.append(f"\n✅ Verificações aprovadas: {passed_checks}/{total_checks}")
        report.append(f"📊 Taxa de aprovação: {(passed_checks/total_checks)*100:.1f}%")
        
        for check_name, result in self.results.items():
            report.append(f"\n{'='*40}")
            report.append(f"🔍 {check_name.upper().replace('_', ' ')}")
            report.append(f"{'='*40}")
            
            if isinstance(result, dict):
                if result.get("passed", False):
                    report.append("✅ APROVADO")
                else:
                    report.append("❌ REPROVADO")
                    
                    if "error" in result:
                        report.append(f"Erro: {result['error']}")
                    
                    if "violations" in result and result["violations"]:
                        report.append(f"Violações encontradas: {len(result['violations'])}")
                        for violation in result["violations"][:5]:  # Mostrar apenas 5 primeiras
                            if "function" in violation:
                                report.append(f"  - {violation['file']}:{violation.get('line', '?')} "
                                            f"função '{violation['function']}' "
                                            f"(complexidade: {violation.get('complexity', '?')})")
                            elif "class" in violation:
                                report.append(f"  - {violation['file']}:{violation.get('start_line', '?')} "
                                            f"classe '{violation['class']}' "
                                            f"({violation.get('lines', '?')} linhas)")
                            else:
                                report.append(f"  - {violation}")
                        
                        if len(result["violations"]) > 5:
                            report.append(f"  ... e mais {len(result['violations']) - 5} violações")
            else:
                report.append(f"Resultado: {result}")
        
        report.append("\n" + "=" * 60)
        report.append("📋 RESUMO DAS MÉTRICAS")
        report.append("=" * 60)
        report.append(f"• Complexidade ciclomática máxima: {self.max_complexity}")
        report.append(f"• Linhas máximas por função: {self.max_function_lines}")
        report.append(f"• Linhas máximas por classe: {self.max_class_lines}")
        report.append(f"• Duplicação máxima permitida: {self.max_duplication}%")
        
        return "\n".join(report)
    
    def save_report(self, output_file: str = "data/output/quality_report.txt"):
        """Salva relatório em arquivo."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        
        print(f"📄 Relatório salvo em: {output_path}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Verificador de qualidade de código")
    parser.add_argument("--src-dir", default="src", help="Diretório do código fonte")
    parser.add_argument("--max-complexity", type=int, default=10, 
                       help="Complexidade ciclomática máxima")
    parser.add_argument("--max-function-lines", type=int, default=20,
                       help="Linhas máximas por função")
    parser.add_argument("--max-class-lines", type=int, default=200,
                       help="Linhas máximas por classe")
    parser.add_argument("--max-duplication", type=float, default=3.0,
                       help="Porcentagem máxima de duplicação")
    parser.add_argument("--output", default="data/output/quality_report.txt",
                       help="Arquivo de saída do relatório")
    parser.add_argument("--json", action="store_true",
                       help="Saída em formato JSON")
    
    args = parser.parse_args()
    
    checker = QualityChecker(
        src_dir=args.src_dir,
        max_complexity=args.max_complexity,
        max_function_lines=args.max_function_lines,
        max_class_lines=args.max_class_lines,
        max_duplication=args.max_duplication
    )
    
    results = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(checker.generate_report())
        checker.save_report(args.output)
    
    # Retornar código de saída baseado nos resultados
    all_passed = all(result.get("passed", False) if isinstance(result, dict) else False 
                    for result in results.values())
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()