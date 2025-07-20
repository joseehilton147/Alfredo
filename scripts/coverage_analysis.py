#!/usr/bin/env python3
"""
Script de análise detalhada de cobertura de testes para Alfredo AI.

Gera relatórios detalhados de cobertura por módulo, identifica áreas
com baixa cobertura e sugere melhorias.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CoverageReport:
    """Relatório de cobertura para um módulo."""

    module: str
    coverage_percent: float
    lines_total: int
    lines_covered: int
    lines_missing: int
    missing_lines: List[str]
    branch_coverage: Optional[float] = None


@dataclass
class QualityMetrics:
    """Métricas de qualidade do projeto."""

    total_coverage: float
    module_reports: List[CoverageReport]
    low_coverage_modules: List[str]
    uncovered_lines: int
    total_lines: int
    timestamp: str


class CoverageAnalyzer:
    """Analisador de cobertura de testes."""

    def __init__(self, project_root: Path, min_coverage: float = 80.0):
        self.project_root = project_root
        self.min_coverage = min_coverage
        self.src_dir = project_root / "src"
        self.tests_dir = project_root / "tests"

    def run_coverage(self) -> bool:
        """Executa análise de cobertura usando pytest-cov."""
        try:
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "--cov=src",
                "--cov-report=json:coverage.json",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-branch",
                "tests/",
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"❌ Erro ao executar testes: {result.stderr}")
                return False

            return True

        except Exception as e:
            print(f"❌ Erro ao executar cobertura: {e}")
            return False

    def parse_coverage_json(self) -> Optional[QualityMetrics]:
        """Parse do arquivo JSON de cobertura."""
        coverage_file = self.project_root / "coverage.json"

        if not coverage_file.exists():
            print("❌ Arquivo coverage.json não encontrado")
            return None

        try:
            with open(coverage_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            module_reports = []
            low_coverage_modules = []

            for filename, file_data in data["files"].items():
                # Converter path absoluto para módulo relativo
                rel_path = Path(filename).relative_to(self.project_root)
                module = (
                    str(rel_path)
                    .replace("/", ".")
                    .replace("\\", ".")
                    .replace(".py", "")
                )

                # Calcular métricas
                executed_lines = file_data["summary"]["covered_lines"]
                total_lines = file_data["summary"]["num_statements"]
                missing_lines = file_data["summary"]["missing_lines"]

                coverage_percent = (
                    (executed_lines / total_lines * 100) if total_lines > 0 else 100
                )

                # Obter linhas não cobertas
                missing_line_numbers = [
                    str(line) for line in file_data.get("missing_lines", [])
                ]

                report = CoverageReport(
                    module=module,
                    coverage_percent=coverage_percent,
                    lines_total=total_lines,
                    lines_covered=executed_lines,
                    lines_missing=missing_lines,
                    missing_lines=missing_line_numbers,
                    branch_coverage=file_data["summary"].get("covered_branches", 0)
                    / max(file_data["summary"].get("num_branches", 1), 1)
                    * 100,
                )

                module_reports.append(report)

                if coverage_percent < self.min_coverage:
                    low_coverage_modules.append(module)

            # Métricas totais
            total_coverage = data["totals"]["percent_covered"]
            total_lines = data["totals"]["num_statements"]
            covered_lines = data["totals"]["covered_lines"]
            uncovered_lines = total_lines - covered_lines

            return QualityMetrics(
                total_coverage=total_coverage,
                module_reports=module_reports,
                low_coverage_modules=low_coverage_modules,
                uncovered_lines=uncovered_lines,
                total_lines=total_lines,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            print(f"❌ Erro ao processar coverage.json: {e}")
            return None

    def generate_detailed_report(self, metrics: QualityMetrics) -> str:
        """Gera relatório detalhado de cobertura."""
        report = []

        # Cabeçalho
        report.append("=" * 80)
        report.append("📊 RELATÓRIO DETALHADO DE COBERTURA DE TESTES")
        report.append("=" * 80)
        report.append(f"Gerado em: {metrics.timestamp}")
        report.append(f"Cobertura total: {metrics.total_coverage:.1f}%")
        report.append(f"Linhas totais: {metrics.total_lines}")
        report.append(
            f"Linhas cobertas: {metrics.total_lines - metrics.uncovered_lines}"
        )
        report.append(f"Linhas não cobertas: {metrics.uncovered_lines}")
        report.append("")

        # Status geral
        if metrics.total_coverage >= self.min_coverage:
            report.append("✅ COBERTURA ADEQUADA - Meta atingida!")
        else:
            report.append(f"❌ COBERTURA INSUFICIENTE - Meta: {self.min_coverage}%")

        report.append("")

        # Módulos com baixa cobertura
        if metrics.low_coverage_modules:
            report.append("🔴 MÓDULOS COM BAIXA COBERTURA:")
            report.append("-" * 50)

            low_modules = [
                r
                for r in metrics.module_reports
                if r.module in metrics.low_coverage_modules
            ]
            low_modules.sort(key=lambda x: x.coverage_percent)

            for module_report in low_modules:
                report.append(f"  {module_report.module}")
                report.append(f"    Cobertura: {module_report.coverage_percent:.1f}%")
                report.append(f"    Linhas não cobertas: {module_report.lines_missing}")
                if module_report.missing_lines:
                    lines_preview = ", ".join(module_report.missing_lines[:10])
                    if len(module_report.missing_lines) > 10:
                        lines_preview += (
                            f" ... (+{len(module_report.missing_lines) - 10} mais)"
                        )
                    report.append(f"    Linhas específicas: {lines_preview}")
                report.append("")

        # Top módulos com boa cobertura
        good_modules = [
            r for r in metrics.module_reports if r.coverage_percent >= self.min_coverage
        ]
        if good_modules:
            report.append("✅ MÓDULOS COM BOA COBERTURA:")
            report.append("-" * 50)

            good_modules.sort(key=lambda x: x.coverage_percent, reverse=True)

            for module_report in good_modules[:10]:  # Top 10
                report.append(
                    f"  {module_report.module}: {module_report.coverage_percent:.1f}%"
                )

        report.append("")

        # Sugestões de melhoria
        report.append("💡 SUGESTÕES DE MELHORIA:")
        report.append("-" * 50)

        if metrics.low_coverage_modules:
            report.append("1. Priorize testes para módulos com cobertura < 80%:")
            for module in metrics.low_coverage_modules[:5]:
                report.append(f"   - {module}")

        if metrics.uncovered_lines > 100:
            report.append(
                f"2. Foque em reduzir linhas não cobertas (atual: {metrics.uncovered_lines})"
            )

        report.append(
            "3. Considere implementar testes de integração para fluxos completos"
        )
        report.append("4. Adicione testes de edge cases e tratamento de erros")

        return "\n".join(report)

    def generate_html_summary(self, metrics: QualityMetrics) -> str:
        """Gera sumário HTML para dashboard."""
        html = f"""
        <div class="coverage-summary">
            <h2>📊 Cobertura de Testes</h2>
            <div class="metrics">
                <div class="metric">
                    <span class="value">{metrics.total_coverage:.1f}%</span>
                    <span class="label">Cobertura Total</span>
                </div>
                <div class="metric">
                    <span class="value">{len(metrics.low_coverage_modules)}</span>
                    <span class="label">Módulos Baixa Cobertura</span>
                </div>
                <div class="metric">
                    <span class="value">{metrics.uncovered_lines}</span>
                    <span class="label">Linhas Não Cobertas</span>
                </div>
            </div>
            <div class="status {'success' if metrics.total_coverage >= self.min_coverage else 'warning'}">
                {'✅ Meta Atingida' if metrics.total_coverage >= self.min_coverage else '❌ Abaixo da Meta'}
            </div>
        </div>
        """
        return html

    def save_report(self, metrics: QualityMetrics, output_file: Path) -> None:
        """Salva relatório detalhado em arquivo."""
        report_content = self.generate_detailed_report(metrics)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"✅ Relatório salvo em: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")

    def check_coverage_regression(
        self, metrics: QualityMetrics, baseline_file: Path
    ) -> bool:
        """Verifica se houve regressão na cobertura."""
        if not baseline_file.exists():
            # Salva baseline atual
            baseline_data = {
                "total_coverage": metrics.total_coverage,
                "timestamp": metrics.timestamp,
            }

            with open(baseline_file, "w", encoding="utf-8") as f:
                json.dump(baseline_data, f, indent=2)

            print(f"📝 Baseline de cobertura criado: {metrics.total_coverage:.1f}%")
            return True

        try:
            with open(baseline_file, "r", encoding="utf-8") as f:
                baseline = json.load(f)

            baseline_coverage = baseline["total_coverage"]
            current_coverage = metrics.total_coverage

            if current_coverage < baseline_coverage - 1.0:  # Tolerância de 1%
                print("❌ REGRESSÃO DETECTADA!")
                print(f"   Baseline: {baseline_coverage:.1f}%")
                print(f"   Atual: {current_coverage:.1f}%")
                print(f"   Diferença: {current_coverage - baseline_coverage:.1f}%")
                return False
            else:
                print("✅ Cobertura mantida ou melhorada")
                print(f"   Baseline: {baseline_coverage:.1f}%")
                print(f"   Atual: {current_coverage:.1f}%")

                # Atualiza baseline se melhorou
                if current_coverage > baseline_coverage:
                    baseline["total_coverage"] = current_coverage
                    baseline["timestamp"] = metrics.timestamp

                    with open(baseline_file, "w", encoding="utf-8") as f:
                        json.dump(baseline, f, indent=2)

                return True

        except Exception as e:
            print(f"❌ Erro ao verificar baseline: {e}")
            return False


def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Análise detalhada de cobertura de testes"
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=80.0,
        help="Cobertura mínima esperada (padrão: 80%%)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/coverage_report.txt"),
        help="Arquivo de saída do relatório",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("reports/coverage_baseline.json"),
        help="Arquivo de baseline para detecção de regressão",
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Não executar testes, apenas analisar coverage.json existente",
    )

    args = parser.parse_args()

    # Configurar diretórios
    project_root = Path(__file__).parent.parent
    analyzer = CoverageAnalyzer(project_root, args.min_coverage)

    # Criar diretório de relatórios
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.baseline.parent.mkdir(parents=True, exist_ok=True)

    print("🔍 Iniciando análise de cobertura...")

    # Executar testes se necessário
    if not args.no_run:
        print("⚡ Executando testes com cobertura...")
        if not analyzer.run_coverage():
            sys.exit(1)

    # Analisar resultados
    print("📊 Analisando resultados...")
    metrics = analyzer.parse_coverage_json()

    if not metrics:
        print("❌ Falha ao analisar cobertura")
        sys.exit(1)

    # Gerar relatório
    print("📝 Gerando relatório...")
    analyzer.save_report(metrics, args.output)

    # Verificar regressão
    print("🔍 Verificando regressão...")
    no_regression = analyzer.check_coverage_regression(metrics, args.baseline)

    # Sumário final
    print("\n" + "=" * 60)
    print("📊 SUMÁRIO FINAL")
    print("=" * 60)
    print(f"Cobertura total: {metrics.total_coverage:.1f}%")
    print(f"Meta: {args.min_coverage}%")
    print(
        f"Status: {'✅ APROVADO' if metrics.total_coverage >= args.min_coverage else '❌ REPROVADO'}"
    )
    print(f"Módulos com baixa cobertura: {len(metrics.low_coverage_modules)}")
    print(f"Regressão: {'❌ DETECTADA' if not no_regression else '✅ NÃO DETECTADA'}")

    # Exit code baseado nos critérios
    if metrics.total_coverage < args.min_coverage or not no_regression:
        sys.exit(1)

    print("\n✅ Análise de cobertura concluída com sucesso!")


if __name__ == "__main__":
    main()
