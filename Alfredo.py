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
import asyncio
import inspect
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
  resumir-video-local <arquivo>   # Resumir vídeo local (análise visual)
  resumir-audio-local <arquivo>   # Resumir áudio local (rápido)
  resumir-yt <url>                # Resumir vídeo do YouTube (download + IA)
  baixar-yt <url>                 # Baixar vídeo do YouTube
  limpar-cache [nível]            # Limpeza inteligente de cache (1-5)

EXEMPLOS:
  Alfredo                        # Sistema interativo completo
  Alfredo resumir-audio-local video.mp4   # Resumo rápido de áudio
  Alfredo resumir-video-local video.mp4   # Resumo visual completo
  Alfredo resumir-yt <url>                # Resumir YouTube
  Alfredo baixar-yt <url>                 # Baixar YouTube
  Alfredo limpar-cache 3                  # Limpeza moderada
  Alfredo --list                         # Listar comandos
        """
    )
    
    parser.add_argument('command', nargs='?', help='Comando a executar')
    parser.add_argument('args', nargs='*', help='Argumentos do comando')
    parser.add_argument('--list', '-l', action='store_true', help='Listar comandos disponíveis')
    parser.add_argument('--test', '-t', action='store_true', help='Executar diagnóstico')
    parser.add_argument('--version', '-v', action='store_true', help='Mostrar versão')
    parser.add_argument('--provider', help='Especifica o provedor de IA a ser usado (groq ou ollama)', default=None)
    
    args = parser.parse_args()
    
    # Comandos enterprise diretos
    enterprise_commands = {
        'resumir-video-local': 'commands.video.local_video',
        'resumir-audio-local': 'commands.video.audio_analyzer',
        'resumir-yt': 'commands.video.youtube_ai',
        'baixar-yt': 'commands.video.youtube_downloader',
        'limpar-cache': 'commands.clean_command'
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

                    # Configura sys.argv para o comando processar os argumentos
                    sys.argv = ['Alfredo.py'] + args.args
                    if args.provider:
                        sys.argv.extend(['--provider', args.provider])

                    # Verifica se a função main existe
                    if hasattr(module, 'main'):
                        main_func = getattr(module, 'main')

                        # Verifica se a função main é assíncrona
                        if inspect.iscoroutinefunction(main_func):
                            result = asyncio.run(main_func())
                        else:
                            result = main_func()

                        sys.exit(0 if result is not False else 1)
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
    print("  resumir-audio-local <arquivo>   🎧 Resumir áudio local (rápido)")
    print("  resumir-video-local <arquivo>   🎬 Resumir vídeo local (visual)")
    print("  resumir-yt <url>                📹 Resumir vídeo do YouTube (download + IA)")
    print("  baixar-yt <url>                 ⬇️  Baixar vídeo do YouTube")
    print("  limpar-cache [1-5]              🧹 Limpeza inteligente de cache")
    print()
    print("💡 EXEMPLOS:")
    print("  Alfredo resumir-audio-local meu_video.mp4    # RÁPIDO: só áudio")
    print("  Alfredo resumir-video-local meu_video.mp4    # COMPLETO: visual")
    print("  Alfredo resumir-yt https://youtube.com/watch?v=...")
    print("  Alfredo baixar-yt https://youtube.com/watch?v=...")
    print("  Alfredo limpar-cache 3")
    print()

if __name__ == "__main__":
    main()
