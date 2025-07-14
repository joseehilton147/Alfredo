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
from typing import Dict, Any, List, Optional

from core.interfaces import ICoreOperations, ICLIHandler
from core.alfredo_core import AlfredoCore


class AlfredoCLI(ICLIHandler):
    """Handler da CLI do Alfredo com injeção de dependência."""
    
    def __init__(self, core: ICoreOperations = None):
        self.core = core or AlfredoCore()
        self.enterprise_commands = {
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
    
    def parse_arguments(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analisa argumentos da linha de comando.
        
        Args:
            args: Lista de argumentos (opcional, usa sys.argv se None)
            
        Returns:
            Dicionário com argumentos parseados
        """
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
        parser.add_argument('--provider', help='Especifica o provedor de IA a ser usado (apenas groq suportado)', default=None)
        
        parsed_args = parser.parse_args(args)
        return vars(parsed_args)
    
    def execute_command(self, command: str, args: List[str] = None) -> Any:
        """Executa comando via CLI.
        
        Args:
            command: Nome do comando
            args: Argumentos do comando
            
        Returns:
            Resultado da execução
        """
        cmd = command.lower()
        args = args or []
        
        if cmd in self.enterprise_commands:
            return self._execute_enterprise_command(cmd, args)
        else:
            # Tenta executar através do core
            return self.core.execute_command(cmd, args)
    
    def _execute_enterprise_command(self, cmd: str, args: List[str]) -> Any:
        """Executa comando enterprise."""
        module_path = self.enterprise_commands[cmd]
        original_argv = sys.argv.copy()
        
        try:
            import importlib
            module = importlib.import_module(module_path)
            
            # Configura sys.argv para o comando processar os argumentos
            sys.argv = ['Alfredo.py'] + args
            
            # Verifica se a função main existe
            if hasattr(module, 'main'):
                main_func = getattr(module, 'main')
                
                # Verifica se a função main é assíncrona
                if inspect.iscoroutinefunction(main_func):
                    result = asyncio.run(main_func())
                else:
                    result = main_func()
                
                return result
            else:
                raise AttributeError(f"Comando {cmd} não possui função main()")
                
        except ImportError as e:
            raise ImportError(f"Erro ao carregar comando {cmd}: {e}")
        finally:
            sys.argv = original_argv
    
    def show_help(self) -> None:
        """Exibe ajuda da CLI."""
        show_enterprise_commands()


def main(core: ICoreOperations = None):
    """Ponto de entrada principal do Alfredo com injeção de dependência.
    
    Args:
        core: Instância do core (opcional, usa AlfredoCore() por padrão)
    """
    cli = AlfredoCLI(core)
    
    try:
        parsed_args = cli.parse_arguments()
        
        # Import i18n for localization
        from config.i18n import t
        
        if parsed_args.get('version'):
            print("🤖 Alfredo AI v1.0.0 - Enterprise Edition")
            return
            
        elif parsed_args.get('test'):
            # Executa diagnóstico através do core
            if hasattr(cli.core, 'run_diagnostics'):
                cli.core.run_diagnostics()
            else:
                print("❌ Função de diagnóstico não disponível")
            return
            
        elif parsed_args.get('list'):
            cli.show_help()
            return
            
        elif parsed_args.get('command'):
            cmd = parsed_args['command']
            args = parsed_args.get('args', [])
            
            if cmd in ['help', 'ajuda', 'h']:
                cli.show_help()
                return
            
            # Configura provedor se especificado
            if parsed_args.get('provider'):
                os.environ['AI_PROVIDER'] = parsed_args['provider']
            
            # Executa comando
            result = cli.execute_command(cmd, args)
            sys.exit(0 if result is not False else 1)
        else:
            # Sistema interativo completo
            if sys.stdin.isatty():
                if hasattr(cli.core, 'show_interactive_menu'):
                    cli.core.show_interactive_menu()
                else:
                    cli.show_help()
            else:
                cli.show_help()
                
    except KeyboardInterrupt:
        print("\n🤖 Alfredo: Até logo! 👋")
    except Exception as e:
        cli.core.handle_error(e)
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
