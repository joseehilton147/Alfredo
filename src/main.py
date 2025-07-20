#!/usr/bin/env python3
"""
Alfredo AI - Ponto de entrada principal
Assistente de análise de vídeo com transcrição automática
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.alfredo_config import AlfredoConfig
from src.config.constants import (
    APP_NAME, APP_DESCRIPTION, DEFAULT_LOG_FILE, DEFAULT_LOGS_DIR,
    COMMAND_YOUTUBE, COMMAND_LOCAL, COMMAND_BATCH,
    ARG_URL, ARG_FILE_PATH, ARG_DIRECTORY, ARG_LANGUAGE, ARG_LANGUAGE_SHORT,
    ARG_QUALITY, ARG_FORCE, ARG_RECURSIVE, ARG_RECURSIVE_SHORT,
    ARG_MAX_WORKERS, ARG_VERBOSE, ARG_VERBOSE_SHORT,
    DEFAULT_LANGUAGE, DEFAULT_QUALITY, DEFAULT_MAX_WORKERS,
    ERROR_PREFIX, ERROR_ALFREDO_PREFIX, ERROR_UNEXPECTED, ERROR_INTERRUPTED,
    INFO_PREFIX, HELP_MESSAGE, HELP_SUGGESTION
)
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.presentation.cli.command_registry import CommandRegistry
from src.domain.exceptions.alfredo_errors import AlfredoError


def setup_logging(config: AlfredoConfig, verbose: bool = False) -> None:
    """Configura o sistema de logging."""
    level = logging.DEBUG if verbose else getattr(logging, config.log_level.upper())
    
    # Garantir que o diretório de logs existe
    log_file = config.data_dir / DEFAULT_LOGS_DIR / DEFAULT_LOG_FILE
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format=config.log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )


async def main():
    """Função principal - apenas parsing e delegação."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - {APP_DESCRIPTION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_MESSAGE
    )

    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # YouTube command
    youtube_parser = subparsers.add_parser(COMMAND_YOUTUBE, help='Processar vídeo do YouTube')
    youtube_parser.add_argument(ARG_URL, help='URL do vídeo do YouTube')
    youtube_parser.add_argument(ARG_LANGUAGE, ARG_LANGUAGE_SHORT, default=DEFAULT_LANGUAGE, help=f'Idioma (padrão: {DEFAULT_LANGUAGE})')
    youtube_parser.add_argument(ARG_QUALITY, default=DEFAULT_QUALITY, help='Qualidade do vídeo')
    youtube_parser.add_argument(ARG_FORCE, action='store_true', help='Forçar reprocessamento')

    # Local video command
    local_parser = subparsers.add_parser(COMMAND_LOCAL, help='Processar arquivo de vídeo local')
    local_parser.add_argument(ARG_FILE_PATH, help='Caminho do arquivo de vídeo')
    local_parser.add_argument(ARG_LANGUAGE, ARG_LANGUAGE_SHORT, default=DEFAULT_LANGUAGE, help=f'Idioma (padrão: {DEFAULT_LANGUAGE})')
    local_parser.add_argument(ARG_FORCE, action='store_true', help='Forçar reprocessamento')

    # Batch command
    batch_parser = subparsers.add_parser(COMMAND_BATCH, help='Processar múltiplos arquivos')
    batch_parser.add_argument(ARG_DIRECTORY, help='Diretório com arquivos de vídeo')
    batch_parser.add_argument(ARG_LANGUAGE, ARG_LANGUAGE_SHORT, default=DEFAULT_LANGUAGE, help=f'Idioma (padrão: {DEFAULT_LANGUAGE})')
    batch_parser.add_argument(ARG_RECURSIVE, ARG_RECURSIVE_SHORT, action='store_true', help='Busca recursiva')
    batch_parser.add_argument(ARG_MAX_WORKERS, type=int, default=DEFAULT_MAX_WORKERS, help='Workers paralelos')
    batch_parser.add_argument(ARG_FORCE, action='store_true', help='Forçar reprocessamento')

    # Argumentos globais
    parser.add_argument(ARG_VERBOSE, ARG_VERBOSE_SHORT, action='store_true', help='Modo verbose')

    args = parser.parse_args()

    # Configurar sistema
    config = AlfredoConfig()
    config.validate_runtime()
    config.create_directory_structure()
    setup_logging(config, args.verbose)

    # Criar factory e registry
    factory = InfrastructureFactory(config)
    registry = CommandRegistry(config, factory)

    try:
        if not args.command:
            parser.print_help()
            return

        # Obter e executar comando
        command = registry.get_command(args.command)

        if args.command == COMMAND_YOUTUBE:
            await command.execute(
                url=args.url,
                language=args.language,
                quality=args.quality,
                force_reprocess=args.force
            )
        elif args.command == COMMAND_LOCAL:
            await command.execute(
                file_path=args.file_path,
                language=args.language,
                force_reprocess=args.force
            )
        elif args.command == COMMAND_BATCH:
            await command.execute(
                directory=args.directory,
                language=args.language,
                recursive=args.recursive,
                max_workers=args.max_workers,
                force_reprocess=args.force
            )

    except KeyboardInterrupt:
        print(ERROR_INTERRUPTED)
    except ValueError as e:
        # Erro de comando não encontrado
        print(f"{ERROR_PREFIX}{e}")
        print(HELP_SUGGESTION)
        sys.exit(1)
    except AlfredoError as e:
        # Erros específicos do domínio já são tratados pelos comandos
        # mas podem escapar em casos raros
        print(f"{ERROR_ALFREDO_PREFIX}{e.message}")
        if hasattr(e, 'details') and e.details:
            logging.getLogger(__name__).debug(f"Detalhes do erro: {e.details}")
        sys.exit(1)
    except Exception as e:
        # Erros inesperados - logar detalhes técnicos mas exibir mensagem amigável
        logger = logging.getLogger(__name__)
        logger.error(f"Erro inesperado no main: {e}", exc_info=True)
        
        print(ERROR_UNEXPECTED)
        print(f"{INFO_PREFIX}Verifique os logs para mais detalhes técnicos")
        print(f"   Log: {config.data_dir / DEFAULT_LOGS_DIR / DEFAULT_LOG_FILE}")
        
        if args.verbose:
            print(f"\nDetalhes técnicos: {e}")
        
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
