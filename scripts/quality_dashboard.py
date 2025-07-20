#!/usr/bin/env python3
"""
Dashboard de qualidade consolidado para Alfredo AI.

Gera relatórios HTML interativos com todas as métricas de qualidade:
- Cobertura de testes
- Conformidade SOLID
- Análise estática (linting)
- Complexidade de código
- Métricas de performance
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess
import sys


class QualityDashboard:
    """Gerador de dashboard de qualidade."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "data" / "output" / "reports"
        self.dashboard_dir = project_root / "data" / "output" / "dashboard"
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Executa todas as verificações de qualidade."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'coverage': self._run_coverage_check(),
            'solid': self._run_solid_check(),
            'linting': self._run_linting_check(),
            'complexity': self._run_complexity_check(),
            'tests': self._run_test_summary()
        }
        
        return results
    
    def _run_coverage_check(self) -> Dict[str, Any]:
        """Executa verificação de cobertura."""
        try:
            # Executar testes com cobertura
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/unit/",
                "--cov=src",
                "--cov-report=json:coverage.json",
                "--cov-report=html:data/output/coverage",
                "--quiet"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            # Ler dados de cobertura
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    'status': 'success',
                    'total_coverage': data['totals']['percent_covered'],
                    'lines_total': data['totals']['num_statements'],
                    'lines_covered': data['totals']['covered_lines'],
                    'lines_missing': data['totals']['num_statements'] - data['totals']['covered_lines']
                }
            else:
                return {'status': 'error', 'message': 'Coverage file not found'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _run_solid_check(self) -> Dict[str, Any]:
        """Executa verificação SOLID."""
        try:
            result = subprocess.run([
                sys.executable, "scripts/solid_compliance_check.py",
                "--json", "data/output/reports/solid_compliance.json"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            solid_file = self.reports_dir / "solid_compliance.json"
            if solid_file.exists():
                with open(solid_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    'status': 'success',
                    'compliance_score': data['compliance_score'],
                    'total_violations': data['total_violations'],
                    'violations_by_principle': data['violations_by_principle']
                }
            else:
                return {'status': 'error', 'message': 'SOLID report not found'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _run_linting_check(self) -> Dict[str, Any]:
        """Executa verificação de linting."""
        try:
            # Executar flake8
            result = subprocess.run([
                sys.executable, "-m", "flake8", "src/", "--count", "--statistics"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            error_count = 0
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip().isdigit():
                        error_count = int(line.strip())
                        break
            
            return {
                'status': 'success',
                'error_count': error_count,
                'output': result.stdout,
                'passed': error_count == 0
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _run_complexity_check(self) -> Dict[str, Any]:
        """Executa verificação de complexidade."""
        try:
            # Usar radon para análise de complexidade
            result = subprocess.run([
                sys.executable, "-m", "radon", "cc", "src/", "--json"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                
                # Calcular métricas agregadas
                total_functions = 0
                high_complexity = 0
                
                for file_path, functions in data.items():
                    for func in functions:
                        total_functions += 1
                        if func['complexity'] > 10:
                            high_complexity += 1
                
                return {
                    'status': 'success',
                    'total_functions': total_functions,
                    'high_complexity_count': high_complexity,
                    'complexity_ratio': (high_complexity / max(total_functions, 1)) * 100
                }
            else:
                return {'status': 'error', 'message': 'Radon not available'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _run_test_summary(self) -> Dict[str, Any]:
        """Executa sumário de testes."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/unit/",
                "--tb=no",
                "-q"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            # Parse da saída do pytest
            output = result.stdout
            passed = failed = 0
            
            if "passed" in output:
                parts = output.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        passed = int(parts[i-1])
                    elif part == "failed":
                        failed = int(parts[i-1])
            
            return {
                'status': 'success',
                'passed': passed,
                'failed': failed,
                'total': passed + failed,
                'success_rate': (passed / max(passed + failed, 1)) * 100
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_html_dashboard(self, results: Dict[str, Any]) -> str:
        """Gera dashboard HTML."""
        
        # Calcular score geral de qualidade
        scores = []
        
        if results['coverage']['status'] == 'success':
            scores.append(min(results['coverage']['total_coverage'], 100))
        
        if results['solid']['status'] == 'success':
            scores.append(results['solid']['compliance_score'])
        
        if results['linting']['status'] == 'success':
            linting_score = 100 if results['linting']['passed'] else max(0, 100 - results['linting']['error_count'])
            scores.append(linting_score)
        
        if results['tests']['status'] == 'success':
            scores.append(results['tests']['success_rate'])
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Qualidade - Alfredo AI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.8;
            font-size: 1.1em;
        }}
        
        .overall-score {{
            background: {'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)' if overall_score >= 80 else 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)' if overall_score >= 60 else 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)'};
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid #3498db;
        }}
        
        .metric-card.success {{
            border-left-color: #27ae60;
        }}
        
        .metric-card.warning {{
            border-left-color: #f39c12;
        }}
        
        .metric-card.error {{
            border-left-color: #e74c3c;
        }}
        
        .metric-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .metric-details {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .status-success {{
            background: #d5f4e6;
            color: #27ae60;
        }}
        
        .status-warning {{
            background: #fef9e7;
            color: #f39c12;
        }}
        
        .status-error {{
            background: #fadbd8;
            color: #e74c3c;
        }}
        
        .footer {{
            background: #ecf0f1;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #ecf0f1;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Dashboard de Qualidade</h1>
            <p>Alfredo AI - Sistema de Análise de Vídeo</p>
            <p>Gerado em: {datetime.fromisoformat(results['timestamp']).strftime('%d/%m/%Y às %H:%M:%S')}</p>
        </div>
        
        <div class="overall-score">
            <div class="score-circle">
                {overall_score:.0f}%
            </div>
            <h2>Score Geral de Qualidade</h2>
            <p>{'🎉 Excelente qualidade!' if overall_score >= 80 else '⚠️ Qualidade moderada' if overall_score >= 60 else '❌ Necessita melhorias'}</p>
        </div>
        
        <div class="metrics-grid">
            <!-- Cobertura de Testes -->
            <div class="metric-card {'success' if results['coverage']['status'] == 'success' and results['coverage'].get('total_coverage', 0) >= 80 else 'warning' if results['coverage']['status'] == 'success' else 'error'}">
                <div class="metric-title">📊 Cobertura de Testes</div>
                {f'''
                <div class="metric-value">{results['coverage']['total_coverage']:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {results['coverage']['total_coverage']}%"></div>
                </div>
                <div class="metric-details">
                    Linhas cobertas: {results['coverage']['lines_covered']:,}<br>
                    Linhas totais: {results['coverage']['lines_total']:,}<br>
                    Linhas não cobertas: {results['coverage']['lines_missing']:,}
                </div>
                ''' if results['coverage']['status'] == 'success' else f'''
                <div class="metric-value">❌ Erro</div>
                <div class="metric-details">{results['coverage']['message']}</div>
                '''}
                <span class="status-badge status-{'success' if results['coverage']['status'] == 'success' and results['coverage'].get('total_coverage', 0) >= 80 else 'warning' if results['coverage']['status'] == 'success' else 'error'}">
                    {'Adequada' if results['coverage']['status'] == 'success' and results['coverage'].get('total_coverage', 0) >= 80 else 'Baixa' if results['coverage']['status'] == 'success' else 'Erro'}
                </span>
            </div>
            
            <!-- Conformidade SOLID -->
            <div class="metric-card {'success' if results['solid']['status'] == 'success' and results['solid'].get('compliance_score', 0) >= 80 else 'warning' if results['solid']['status'] == 'success' else 'error'}">
                <div class="metric-title">🏗️ Conformidade SOLID</div>
                {f'''
                <div class="metric-value">{results['solid']['compliance_score']:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {results['solid']['compliance_score']}%"></div>
                </div>
                <div class="metric-details">
                    Total de violações: {results['solid']['total_violations']}<br>
                    Principais: {', '.join([f"{k}: {v}" for k, v in results['solid']['violations_by_principle'].items()])}
                </div>
                ''' if results['solid']['status'] == 'success' else f'''
                <div class="metric-value">❌ Erro</div>
                <div class="metric-details">{results['solid']['message']}</div>
                '''}
                <span class="status-badge status-{'success' if results['solid']['status'] == 'success' and results['solid'].get('compliance_score', 0) >= 80 else 'warning' if results['solid']['status'] == 'success' else 'error'}">
                    {'Excelente' if results['solid']['status'] == 'success' and results['solid'].get('compliance_score', 0) >= 80 else 'Boa' if results['solid']['status'] == 'success' else 'Erro'}
                </span>
            </div>
            
            <!-- Análise Estática -->
            <div class="metric-card {'success' if results['linting']['status'] == 'success' and results['linting'].get('passed', False) else 'warning' if results['linting']['status'] == 'success' else 'error'}">
                <div class="metric-title">🔍 Análise Estática</div>
                {f'''
                <div class="metric-value">{'✅ OK' if results['linting']['passed'] else f"{results['linting']['error_count']} erros"}</div>
                <div class="metric-details">
                    Status: {'Sem problemas detectados' if results['linting']['passed'] else f'{results['linting']['error_count']} problemas encontrados'}<br>
                    Ferramenta: flake8
                </div>
                ''' if results['linting']['status'] == 'success' else f'''
                <div class="metric-value">❌ Erro</div>
                <div class="metric-details">{results['linting']['message']}</div>
                '''}
                <span class="status-badge status-{'success' if results['linting']['status'] == 'success' and results['linting'].get('passed', False) else 'warning' if results['linting']['status'] == 'success' else 'error'}">
                    {'Limpo' if results['linting']['status'] == 'success' and results['linting'].get('passed', False) else 'Problemas' if results['linting']['status'] == 'success' else 'Erro'}
                </span>
            </div>
            
            <!-- Testes -->
            <div class="metric-card {'success' if results['tests']['status'] == 'success' and results['tests'].get('success_rate', 0) >= 90 else 'warning' if results['tests']['status'] == 'success' else 'error'}">
                <div class="metric-title">🧪 Execução de Testes</div>
                {f'''
                <div class="metric-value">{results['tests']['success_rate']:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {results['tests']['success_rate']}%"></div>
                </div>
                <div class="metric-details">
                    Testes passando: {results['tests']['passed']}<br>
                    Testes falhando: {results['tests']['failed']}<br>
                    Total: {results['tests']['total']}
                </div>
                ''' if results['tests']['status'] == 'success' else f'''
                <div class="metric-value">❌ Erro</div>
                <div class="metric-details">{results['tests']['message']}</div>
                '''}
                <span class="status-badge status-{'success' if results['tests']['status'] == 'success' and results['tests'].get('success_rate', 0) >= 90 else 'warning' if results['tests']['status'] == 'success' else 'error'}">
                    {'Estável' if results['tests']['status'] == 'success' and results['tests'].get('success_rate', 0) >= 90 else 'Instável' if results['tests']['status'] == 'success' else 'Erro'}
                </span>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Alfredo AI - Dashboard gerado automaticamente</p>
            <p>Para mais detalhes, consulte os relatórios individuais em data/output/reports/</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def save_dashboard(self, results: Dict[str, Any], output_file: Path):
        """Salva dashboard HTML."""
        html_content = self.generate_html_dashboard(results)
        
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Dashboard salvo em: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar dashboard: {e}")
    
    def save_json_summary(self, results: Dict[str, Any], output_file: Path):
        """Salva sumário JSON."""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ Sumário JSON salvo em: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar JSON: {e}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Dashboard de qualidade consolidado")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/dashboard/quality_dashboard.html"),
        help="Arquivo HTML de saída"
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("data/output/dashboard/quality_summary.json"),
        help="Arquivo JSON de sumário"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Pular execução de verificações (usar dados existentes)"
    )
    
    args = parser.parse_args()
    
    # Configurar
    project_root = Path(__file__).parent.parent
    dashboard = QualityDashboard(project_root)
    
    print("📊 Gerando dashboard de qualidade...")
    
    # Executar verificações
    if not args.skip_checks:
        print("🔍 Executando verificações de qualidade...")
        results = dashboard.run_all_checks()
    else:
        print("⏭️  Pulando verificações, usando dados existentes...")
        # Aqui você poderia carregar dados existentes se necessário
        results = dashboard.run_all_checks()  # Por enquanto, sempre executa
    
    # Gerar dashboard
    dashboard.save_dashboard(results, args.output)
    dashboard.save_json_summary(results, args.json)
    
    # Sumário
    print("\n" + "=" * 60)
    print("📊 DASHBOARD DE QUALIDADE GERADO")
    print("=" * 60)
    print(f"📄 Dashboard HTML: {args.output}")
    print(f"📋 Sumário JSON: {args.json}")
    
    # Calcular score geral
    scores = []
    if results['coverage']['status'] == 'success':
        scores.append(results['coverage']['total_coverage'])
    if results['solid']['status'] == 'success':
        scores.append(results['solid']['compliance_score'])
    if results['tests']['status'] == 'success':
        scores.append(results['tests']['success_rate'])
    
    if scores:
        overall_score = sum(scores) / len(scores)
        print(f"🎯 Score Geral: {overall_score:.1f}%")
        print(f"📊 Status: {'✅ Excelente' if overall_score >= 80 else '⚠️ Moderado' if overall_score >= 60 else '❌ Necessita melhorias'}")
    
    print("\n✅ Dashboard de qualidade concluído!")


if __name__ == "__main__":
    main()