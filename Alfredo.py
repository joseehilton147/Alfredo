#!/usr/bin/env python3
"""
🤖 ALFREDO AI - Assistente Pessoal
==================================
Sistema principal do assistente Alfredo
Ponto de entrada para todos os comandos
"""

import os
import sys
import argparse
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_dir))

def main():
    """Ponto de entrada principal do Alfredo"""
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description="🤖 Alfredo AI - Seu Assistente Pessoal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
COMANDOS ENTERPRISE:
  videol <arquivo>    # Resumir vídeo (análise visual)
  audioa <arquivo>    # Resumir áudio (muito mais rápido!)
  videoy <url>        # Resumir vídeo do YouTube  
  youtube <url>       # Baixar vídeo do YouTube
  yt+ia <url>         # YouTube + IA (download + resumo)
  limpar [nivel]      # Limpeza inteligente (1-5)

EXEMPLOS:
  Alfredo                    # Sistema interativo completo
  Alfredo audioa video.mp4   # Análise rápida de áudio
  Alfredo videol video.mp4   # Análise visual completa
  Alfredo videoy <url>       # Resumir YouTube
  Alfredo yt+ia <url>        # YouTube completo
  Alfredo limpar 3          # Limpeza moderada
  Alfredo --list            # Listar comandos
        """
    )
    
    parser.add_argument('command', nargs='?', help='Comando a executar')
    parser.add_argument('args', nargs='*', help='Argumentos do comando')
    parser.add_argument('--list', '-l', action='store_true', help='Listar comandos disponíveis')
    parser.add_argument('--test', '-t', action='store_true', help='Executar diagnóstico')
    parser.add_argument('--version', '-v', action='store_true', help='Mostrar versão')
    
    args = parser.parse_args()
    
    # Comandos enterprise diretos
    enterprise_commands = {
        'videol': 'commands.video.local_video',
        'audioa': 'commands.video.audio_analyzer',
        'videoy': 'commands.video.youtube_ai', 
        'youtube': 'commands.video.youtube_downloader',
        'yt+ia': 'commands.video.youtube_ai',
        'limpar': 'commands.clean_command'
    }
    
    try:
        if args.version:
            print("🤖 Alfredo AI v1.0.0 - Enterprise Edition")
            return
            
        elif args.test:
            from core.alfredo_core import AlfredoCore
            alfredo = AlfredoCore()
            alfredo.run_diagnostics()
            return
            
        elif args.list:
            show_enterprise_commands()
            return
            
        elif args.command:
            cmd = args.command.lower()
            
            if cmd in ['help', 'ajuda', 'h']:
                show_enterprise_commands()
                return
                
            elif cmd in enterprise_commands:
                # Executa comando enterprise
                module_path = enterprise_commands[cmd]
                original_argv = sys.argv.copy()  # Salva antes de tentar importar
                try:
                    import importlib
                    module = importlib.import_module(module_path)
                    
                    # Adiciona argumentos aos sys.argv para o comando processar
                    sys.argv = ['Alfredo.py'] + args.args
                    
                    # Executa comando
                    if hasattr(module, 'main'):
                        result = module.main()
                        sys.exit(0 if result != False else 1)
                    else:
                        print(f"❌ Comando {cmd} não possui função main()")
                        sys.exit(1)
                        
                except ImportError as e:
                    print(f"❌ Erro ao carregar comando {cmd}: {e}")
                    sys.exit(1)
                finally:
                    sys.argv = original_argv
            else:
                print(f"❌ Comando '{cmd}' não reconhecido")
                print("💡 Use 'Alfredo --list' para ver comandos disponíveis")
                sys.exit(1)
        else:
            # Sistema interativo completo
            from core.alfredo_core import AlfredoCore
            alfredo = AlfredoCore()
            if sys.stdin.isatty():
                alfredo.show_interactive_menu()
            else:
                show_enterprise_commands()
                
    except KeyboardInterrupt:
        print("\n🤖 Alfredo: Até logo! 👋")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

def show_enterprise_commands():
    """Mostra comandos enterprise disponíveis"""
    print("🤖 " + "=" * 50)
    print("   ALFREDO AI - Enterprise Commands")
    print("   Sistema de Vídeo Inteligente")
    print("=" * 52)
    print()
    print("📋 COMANDOS ENTERPRISE:")
    print("--" * 25)
    print("  audioa <arquivo>     � Análise rápida de áudio")
    print("  videol <arquivo>     🎬 Análise visual completa")
    print("  videoy <url>         📹 Resumir vídeo YouTube")
    print("  youtube <url>        ⬇️ Baixar vídeo YouTube")
    print("  yt+ia <url>          🚀 YouTube + IA completo")
    print("  limpar [1-5]         🧹 Limpeza inteligente")
    print()
    print("💡 EXEMPLOS:")
    print("  Alfredo audioa meu_video.mp4    # RÁPIDO: só áudio")
    print("  Alfredo videol meu_video.mp4    # COMPLETO: visual")
    print("  Alfredo videoy https://youtube.com/watch?v=...")
    print("  Alfredo yt+ia https://youtube.com/watch?v=...")
    print("  Alfredo limpar 3")
    print()

if __name__ == "__main__":
    main()
