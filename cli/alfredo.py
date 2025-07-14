#!/usr/bin/env python3
"""
🤖 ALFREDO AI - CLI Interface
=============================
Main CLI interface for Alfredo AI commands
"""

import os
import sys
import argparse
import asyncio
import inspect
from pathlib import Path

# Add project root to path (go up one level from cli/)
project_dir = Path(__file__).parent.parent.absolute()
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
    
    # Import i18n for localization
    from config.i18n import t
    
    # Enterprise commands mapping to new CLI structure
    enterprise_commands = {
        'resumir-video-local': 'cli.video_local',
        'resumir-audio-local': 'cli.audio_analyzer',
        'resumir-yt': 'cli.youtube_ai',
        'baixar-yt': 'cli.youtube_downloader',
        'limpar-cache': 'cli.clean',
        'limpar': 'cli.clean',
        'groq-status': 'cli.groq_status',
        'info-pc': 'cli.pc_info',
        'configurar-modelos': 'cli.model_config',
        'testes': 'cli.test_runner'
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
    """Show available enterprise commands with localization"""
    from config.i18n import t
    
    print("🤖 " + "=" * 50)
    print(f"   {t('cli.welcome')}")
    print("   Sistema de Vídeo Inteligente")
    print("=" * 52)
    print()
    print("📋 COMANDOS CLI INDEPENDENTES:")
    print("--" * 25)
    print(f"  resumir-audio-local <arquivo>   {t('cli.commands.audio_analyzer')}")
    print(f"  resumir-video-local <arquivo>   {t('cli.commands.video_local')}")
    print(f"  resumir-yt <url>                {t('cli.commands.youtube_ai')}")
    print(f"  baixar-yt <url>                 {t('cli.commands.youtube_downloader')}")
    print(f"  limpar-cache [1-5]              {t('cli.commands.clean')}")
    print(f"  groq-status                     {t('cli.commands.groq_status')}")
    print(f"  info-pc                         {t('cli.commands.pc_info')}")
    print(f"  configurar-modelos              {t('cli.commands.model_config')}")
    print(f"  testes                          {t('cli.commands.test_runner')}")
    print()
    print("💡 EXEMPLOS:")
    print("  alfredo resumir-audio-local meu_video.mp4    # RÁPIDO: só áudio")
    print("  alfredo resumir-video-local meu_video.mp4    # COMPLETO: visual")
    print("  alfredo resumir-yt https://youtube.com/watch?v=...")
    print("  alfredo baixar-yt https://youtube.com/watch?v=...")
    print("  alfredo limpar-cache 3")
    print()

if __name__ == "__main__":
    main()
