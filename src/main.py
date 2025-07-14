#!/usr/bin/env python3
"""
Alfredo AI - Script principal de execução
Ponto de entrada para processamento de vídeos com transcrição e análise
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.application.use_cases.transcribe_audio import (
    TranscribeAudioUseCase,
    TranscribeAudioRequest,
)
from src.domain.entities.video import Video
from src.infrastructure.providers.whisper_provider import WhisperProvider
from src.infrastructure.repositories.json_video_repository import JsonVideoRepository


def setup_logging(verbose: bool = False) -> None:
    """Configura o sistema de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("data/logs/alfredo.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def create_directories() -> None:
    """Cria diretórios necessários se não existirem."""
    directories = [
        "data/input/local",
        "data/input/youtube",
        "data/output",
        "data/logs",
        "data/temp",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


async def process_single_video(
    video_path: str, language: str = "pt"
) -> None:
    """Processa um único vídeo."""
    logger = logging.getLogger(__name__)
    
    try:
        # Criar entidade de vídeo
        video = Video(
            id=f"video_{Path(video_path).stem}",
            title=Path(video_path).name,
            file_path=video_path,
        )
        
        # Configurar repositório e provedor
        video_repo = JsonVideoRepository()
        whisper = WhisperProvider()
        use_case = TranscribeAudioUseCase(video_repo, whisper)
        
        # Salvar vídeo no repositório
        await video_repo.save(video)
        
        # Executar transcrição
        request = TranscribeAudioRequest(
            video_id=video.id,
            audio_path=video_path,
            language=language,
        )
        
        response = await use_case.execute(request)
        
        logger.info(f"Transcrição concluída: {response.transcription[:100]}...")
        
    except Exception as e:
        logger.error(f"Erro ao processar vídeo {video_path}: {str(e)}")
        raise


async def process_batch(directory: str, language: str = "pt") -> None:
    """Processa múltiplos vídeos em lote."""
    logger = logging.getLogger(__name__)
    
    video_dir = Path(directory)
    if not video_dir.exists():
        logger.error(f"Diretório não encontrado: {directory}")
        return
    
    # Extensões de vídeo suportadas
    video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"}
    
    videos = [
        str(f) for f in video_dir.iterdir()
        if f.suffix.lower() in video_extensions
    ]
    
    if not videos:
        logger.warning("Nenhum vídeo encontrado no diretório")
        return
    
    logger.info(f"Encontrados {len(videos)} vídeos para processar")
    
    for video_path in videos:
        try:
            await process_single_video(video_path, language)
        except Exception as e:
            logger.error(f"Erro ao processar {video_path}: {str(e)}")
            continue


async def download_youtube_video(url: str, output_dir: str = "data/input/youtube") -> str:
    """Baixa vídeo do YouTube."""
    try:
        import yt_dlp
        
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
            "quiet": True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
            
    except ImportError:
        raise ImportError(
            "yt-dlp não está instalado. Instale com: pip install yt-dlp"
        )


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Alfredo AI - Assistente de análise de vídeo"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Caminho para o arquivo de vídeo local"
    )
    
    parser.add_argument(
        "--url", "-u",
        type=str,
        help="URL do YouTube para download e processamento"
    )
    
    parser.add_argument(
        "--batch", "-b",
        type=str,
        help="Diretório com vídeos para processamento em lote"
    )
    
    parser.add_argument(
        "--language", "-l",
        type=str,
        default="pt",
        help="Idioma do vídeo (padrão: pt)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="data/output",
        help="Diretório de saída para os resultados"
    )
    
    parser.add_argument(
        "--detect-scenes",
        action="store_true",
        help="Ativar detecção de cenas"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Ativar modo verbose"
    )
    
    args = parser.parse_args()
    
    # Configurar
    setup_logging(args.verbose)
    create_directories()
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando Alfredo AI...")
    
    try:
        if args.url:
            logger.info(f"📥 Baixando vídeo do YouTube: {args.url}")
            video_path = await download_youtube_video(args.url)
            await process_single_video(video_path, args.language)
            
        elif args.batch:
            logger.info(f"📁 Processando vídeos em lote: {args.batch}")
            await process_batch(args.batch, args.language)
            
        elif args.input:
            logger.info(f"🎬 Processando vídeo: {args.input}")
            await process_single_video(args.input, args.language)
            
        else:
            parser.print_help()
            logger.error("Nenhuma opção de entrada fornecida")
            
    except KeyboardInterrupt:
        logger.info("Processamento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante o processamento: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
