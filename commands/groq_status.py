"""
Comando para verificar status da API Groq
"""

import sys
import argparse
from pathlib import Path

from integrations.groq.monitor import groq_monitor

def main():
    """Mostra status atual da API Groq"""
    parser = argparse.ArgumentParser(description='Verificar status da API Groq')
    parser.add_argument('--reset', action='store_true', help='Reset contadores de uso')
    parser.add_argument('--diagnose', action='store_true', help='Diagnóstico detalhado')
    args = parser.parse_args()
    
    if args.reset:
        # Reset dos dados de uso
        groq_monitor.reset_usage_data()
        return
    
    if args.diagnose:
        # Diagnóstico detalhado
        print(groq_monitor.diagnose_rate_limits())
        return
    
    # Mostrar status atual
    print(groq_monitor.get_usage_summary())
    
    # Verificar se pode fazer requisições
    limits = groq_monitor.check_rate_limits()
    
    if limits['can_make_request']:
        print("✅ \033[1;32mPronto para fazer requisições!\033[0m")
    else:
        wait_time = groq_monitor.wait_for_rate_limit('request')
        print(f"⏳ \033[1;33mAguarde {wait_time:.0f}s antes da próxima requisição\033[0m")
    
    print("\n💡 \033[1;36mDicas:\033[0m")
    print("  • Use arquivos de áudio menores para economizar rate limits")
    print("  • FLAC é preferível ao MP3 para melhor compressão")
    print("  • Considere usar Ollama local para arquivos grandes")
    print("  • Execute com --reset para limpar contadores de uso")
    print("  • Execute com --diagnose para análise detalhada")

if __name__ == "__main__":
    main()
