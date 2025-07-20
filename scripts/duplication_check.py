#!/usr/bin/env python3
"""
Script para verificação de duplicação de código no projeto Alfredo AI.

Utiliza análise de hash de blocos de código para detectar duplicação.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import re


class DuplicationChecker:
    """Verificador de duplicação de código."""
    
    def __init__(self, src_dir: str = "src", min_lines: int = 6, 
                 max_duplication: float = 3.0):
        self.src_dir = Path(src_dir)
        self.min_lines = min_lines
        self.max_duplication = max_duplication
        self.duplicates = []
        
    def check_duplication(self) -> Dict[str, any]:
        """Verifica duplicação de código."""
        print(f"🔍 Verificando duplicação de código (mínimo {self.min_lines} linhas)...")
        
        # Coletar todos os arquivos Python
        python_files = list(self.src_dir.rglob("*.py"))
        
        if not python_files:
            return {
                "passed": True,
                "percentage": 0.0,
                "duplicates": [],
                "total_lines": 0,
                "duplicate_lines": 0
            }
        
        # Analisar cada arquivo
        all_blocks = {}
        total_lines = 0
        
        for py_file in python_files:
            blocks, file_lines = self._extract_code_blocks(py_file)
            total_lines += file_lines
            
            for block_hash, block_info in blocks.items():
                if block_hash not in all_blocks:
                    all_blocks[block_hash] = []
                all_blocks[block_hash].append(block_info)
        
        # Encontrar duplicatas
        duplicate_lines = 0
        duplicates = []
        
        for block_hash, occurrences in all_blocks.items():
            if len(occurrences) > 1:
                # Temos duplicação
                duplicate_lines += (len(occurrences) - 1) * occurrences[0]["lines"]
                duplicates.append({
                    "hash": block_hash,
                    "lines": occurrences[0]["lines"],
                    "occurrences": len(occurrences),
                    "locations": [
                        {
                            "file": occ["file"],
                            "start_line": occ["start_line"],
                            "end_line": occ["end_line"]
                        }
                        for occ in occurrences
                    ],
                    "code_sample": occurrences[0]["code"][:200] + "..." if len(occurrences[0]["code"]) > 200 else occurrences[0]["code"]
                })
        
        duplication_percentage = (duplicate_lines / total_lines * 100) if total_lines > 0 else 0
        
        return {
            "passed": duplication_percentage <= self.max_duplication,
            "percentage": round(duplication_percentage, 2),
            "duplicates": duplicates,
            "total_lines": total_lines,
            "duplicate_lines": duplicate_lines,
            "max_allowed": self.max_duplication
        }
    
    def _extract_code_blocks(self, file_path: Path) -> Tuple[Dict[str, Dict], int]:
        """Extrai blocos de código de um arquivo."""
        blocks = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Processar blocos de código
            for i in range(len(lines) - self.min_lines + 1):
                block_lines = lines[i:i + self.min_lines]
                
                # Normalizar o bloco (remover espaços em branco e comentários)
                normalized_block = self._normalize_code_block(block_lines)
                
                if normalized_block.strip():
                    block_hash = hashlib.md5(normalized_block.encode()).hexdigest()
                    
                    blocks[block_hash] = {
                        "file": str(file_path),
                        "start_line": i + 1,
                        "end_line": i + self.min_lines,
                        "lines": self.min_lines,
                        "code": normalized_block
                    }
            
            return blocks, total_lines
            
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            return {}, 0
    
    def _normalize_code_block(self, lines: List[str]) -> str:
        """Normaliza um bloco de código para comparação."""
        normalized_lines = []
        
        for line in lines:
            # Remover comentários
            line = re.sub(r'#.*$', '', line)
            
            # Remover strings (para evitar falsos positivos)
            line = re.sub(r'["\'].*?["\']', '""', line)
            
            # Normalizar espaços em branco
            line = re.sub(r'\s+', ' ', line.strip())
            
            if line:  # Ignorar linhas vazias
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Gera relatório de duplicação."""
        report = ["=" * 60]
        report.append("🔄 RELATÓRIO DE DUPLICAÇÃO DE CÓDIGO")
        report.append("=" * 60)
        
        if results["passed"]:
            report.append("✅ APROVADO - Duplicação dentro do limite aceitável")
        else:
            report.append("❌ REPROVADO - Duplicação acima do limite")
        
        report.append(f"\n📊 Estatísticas:")
        report.append(f"• Total de linhas: {results['total_lines']}")
        report.append(f"• Linhas duplicadas: {results['duplicate_lines']}")
        report.append(f"• Porcentagem de duplicação: {results['percentage']}%")
        report.append(f"• Limite máximo: {results['max_allowed']}%")
        report.append(f"• Blocos duplicados encontrados: {len(results['duplicates'])}")
        
        if results["duplicates"]:
            report.append(f"\n🔍 Duplicações encontradas:")
            
            for i, dup in enumerate(results["duplicates"][:10], 1):  # Mostrar apenas 10 primeiras
                report.append(f"\n{i}. Bloco duplicado ({dup['lines']} linhas, {dup['occurrences']} ocorrências):")
                
                for loc in dup["locations"]:
                    report.append(f"   📁 {loc['file']}:{loc['start_line']}-{loc['end_line']}")
                
                report.append(f"   📝 Código:")
                for line in dup["code_sample"].split('\n')[:3]:
                    if line.strip():
                        report.append(f"      {line}")
                
                if len(dup["code_sample"].split('\n')) > 3:
                    report.append("      ...")
            
            if len(results["duplicates"]) > 10:
                report.append(f"\n... e mais {len(results['duplicates']) - 10} duplicações")
        
        return "\n".join(report)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Verificador de duplicação de código")
    parser.add_argument("--src-dir", default="src", help="Diretório do código fonte")
    parser.add_argument("--min-lines", type=int, default=6,
                       help="Número mínimo de linhas para considerar duplicação")
    parser.add_argument("--max-duplication", type=float, default=3.0,
                       help="Porcentagem máxima de duplicação permitida")
    parser.add_argument("--output", default="data/output/duplication_report.txt",
                       help="Arquivo de saída do relatório")
    parser.add_argument("--json", action="store_true",
                       help="Saída em formato JSON")
    
    args = parser.parse_args()
    
    checker = DuplicationChecker(
        src_dir=args.src_dir,
        min_lines=args.min_lines,
        max_duplication=args.max_duplication
    )
    
    results = checker.check_duplication()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report = checker.generate_report(results)
        print(report)
        
        # Salvar relatório
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Relatório salvo em: {output_path}")
    
    # Retornar código de saída baseado no resultado
    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()