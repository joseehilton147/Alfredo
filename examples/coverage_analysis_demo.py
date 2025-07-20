#!/usr/bin/env python3
"""
Demonstração das funcionalidades de análise de cobertura do Alfredo AI.

Este exemplo mostra como usar as ferramentas de análise de cobertura
para monitorar e melhorar a qualidade dos testes.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Executa um comando e exibe o resultado."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    print(f"Executando: {command}")
    print()
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - Concluído com sucesso")
            return True
        else:
            print(f"❌ {description} - Falhou (código: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False


def demonstrate_coverage_analysis():
    """Demonstra as funcionalidades de análise de cobertura."""
    
    print("🤖 Demonstração - Análise de Cobertura do Alfredo AI")
    print("="*60)
    print()
    print("Esta demonstração mostra como usar as ferramentas de análise")
    print("de cobertura para monitorar e melhorar a qualidade dos testes.")
    print()
    
    # 1. Análise completa de cobertura
    success1 = run_command(
        "make coverage-analysis",
        "Análise Completa de Cobertura"
    )
    
    if success1:
        print("\n📊 Relatório detalhado salvo em: data/output/reports/coverage_detailed.txt")
        print("   - Cobertura por módulo")
        print("   - Módulos com baixa cobertura")
        print("   - Sugestões de melhoria")
        print("   - Linhas específicas não cobertas")
    
    # 2. Análise rápida (sem executar testes)
    success2 = run_command(
        "make coverage-analysis-quick",
        "Análise Rápida de Cobertura (usando dados existentes)"
    )
    
    if success2:
        print("\n⚡ Análise rápida concluída usando coverage.json existente")
        print("   - Útil para verificações rápidas durante desenvolvimento")
        print("   - Não executa testes novamente")
    
    # 3. Verificação de regressão
    success3 = run_command(
        "make coverage-regression",
        "Verificação de Regressão de Cobertura"
    )
    
    if success3:
        print("\n🔍 Verificação de regressão concluída")
        print("   - Compara com baseline anterior")
        print("   - Detecta diminuição na cobertura")
        print("   - Atualiza baseline automaticamente se melhorou")
    
    # 4. Relatório de qualidade completo
    success4 = run_command(
        "make quality-report",
        "Relatório de Qualidade Completo"
    )
    
    if success4:
        print("\n📋 Relatório de qualidade completo gerado")
        print("   - Inclui todas as métricas de qualidade")
        print("   - Análise de cobertura integrada")
        print("   - Salvo com timestamp único")
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DA DEMONSTRAÇÃO")
    print("="*60)
    
    total_success = sum([success1, success2, success3, success4])
    print(f"✅ Comandos executados com sucesso: {total_success}/4")
    
    if total_success == 4:
        print("\n🎉 Todas as funcionalidades de análise de cobertura funcionaram!")
        print("\n📁 Arquivos gerados:")
        print("   - data/output/reports/coverage_detailed.txt")
        print("   - data/output/reports/coverage_quick.txt")
        print("   - data/output/reports/coverage_baseline.json")
        print("   - data/output/reports/quality_report_*.txt")
        
        print("\n💡 Próximos passos:")
        print("   1. Revise os relatórios gerados")
        print("   2. Identifique módulos com baixa cobertura")
        print("   3. Adicione testes para melhorar cobertura")
        print("   4. Execute novamente para verificar melhorias")
        
    else:
        print("\n⚠️  Algumas funcionalidades falharam.")
        print("   Verifique se o projeto está configurado corretamente:")
        print("   - make setup")
        print("   - make install-dev")
        print("   - Certifique-se que pytest-cov está instalado")


def show_coverage_commands():
    """Mostra todos os comandos de cobertura disponíveis."""
    
    print("\n" + "="*60)
    print("📋 COMANDOS DE COBERTURA DISPONÍVEIS")
    print("="*60)
    
    commands = [
        ("make test-coverage", "Executa testes com análise de cobertura"),
        ("make coverage-analysis", "Análise detalhada com relatório completo"),
        ("make coverage-analysis-quick", "Análise rápida usando dados existentes"),
        ("make coverage-regression", "Verificação de regressão automática"),
        ("make quality-check", "Verificações de qualidade incluindo cobertura"),
        ("make quality-report", "Relatório abrangente de qualidade"),
        ("make quality-check-parallel", "Verificações paralelas para CI/CD"),
    ]
    
    for command, description in commands:
        print(f"  {command:<30} - {description}")
    
    print("\n📊 Arquivos de Saída:")
    print("  data/output/coverage/          - Relatórios HTML de cobertura")
    print("  data/output/reports/           - Relatórios de texto detalhados")
    print("  coverage.json                  - Dados de cobertura em JSON")
    print("  .coverage                      - Arquivo de cobertura do pytest")


def main():
    """Função principal da demonstração."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--commands-only":
        show_coverage_commands()
        return
    
    try:
        demonstrate_coverage_analysis()
        show_coverage_commands()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()