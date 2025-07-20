#!/usr/bin/env python3
"""
Exemplo básico de uso do Alfredo AI.

Este exemplo demonstra como usar os gateways e casos de uso
seguindo os princípios da Clean Architecture.
"""
import asyncio
import logging
from pathlib import Path

# Adicionar src ao path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.application.use_cases.transcribe_audio import (
    TranscribeAudioUseCase,
    TranscribeAudioRequest,
)
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.domain.entities.video import Video
from src.domain.validators import (
    validate_video_id,
    validate_video_title,
    validate_url_format,
    is_youtube_url,
    extract_youtube_video_id
)
from src.infrastructure.providers.whisper_provider import WhisperProvider
from src.infrastructure.repositories.json_video_repository import JsonVideoRepository


async def exemplo_download_youtube():
    """Exemplo de uso do VideoDownloaderGateway."""
    print("🎬 Exemplo: Download de vídeo do YouTube")
    
    # Simulação de uso do gateway (implementação real seria injetada)
    class MockVideoDownloader(VideoDownloaderGateway):
        async def download(self, url: str, output_dir: str | Path, quality: str = "best") -> str:
            print(f"📥 Baixando: {url}")
            print(f"📁 Destino: {output_dir}")
            print(f"🎯 Qualidade: {quality}")
            return "data/input/youtube/video_baixado.mp4"
        
        async def extract_info(self, url: str) -> dict:
            return {
                "title": "Vídeo de Exemplo",
                "duration": 120,
                "uploader": "Canal Exemplo",
                "view_count": 1000
            }
        
        async def get_available_formats(self, url: str) -> list:
            return [
                {"format_id": "720p", "ext": "mp4", "quality": "720p"},
                {"format_id": "1080p", "ext": "mp4", "quality": "1080p"}
            ]
        
        async def is_url_supported(self, url: str) -> bool:
            return "youtube.com" in url or "youtu.be" in url
        
        async def get_video_id(self, url: str) -> str:
            return "dQw4w9WgXcQ"  # Exemplo
    
    downloader = MockVideoDownloader()
    
    # Verificar se URL é suportada usando validadores
    url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Validar formato da URL
    try:
        validate_url_format(url)
        print("✅ URL tem formato válido")
    except Exception as e:
        print(f"❌ URL inválida: {e}")
        return
    
    # Verificar se é YouTube
    if is_youtube_url(url):
        print("✅ URL do YouTube detectada")
        
        # Extrair ID do vídeo
        video_id = extract_youtube_video_id(url)
        print(f"🆔 ID do vídeo: {video_id}")
    
    if await downloader.is_url_supported(url):
        print("✅ URL suportada pelo downloader")
        
        # Extrair informações
        info = await downloader.extract_info(url)
        print(f"📋 Título: {info['title']}")
        print(f"⏱️ Duração: {info['duration']}s")
        
        # Validar título usando validador de domínio
        try:
            validate_video_title(info['title'])
            print("✅ Título válido")
        except Exception as e:
            print(f"⚠️ Título pode ter problemas: {e}")
        
        # Listar formatos
        formats = await downloader.get_available_formats(url)
        print(f"🎥 Formatos disponíveis: {len(formats)}")
        
        # Fazer download
        video_path = await downloader.download(url, "data/input/youtube")
        print(f"✅ Download concluído: {video_path}")


async def exemplo_transcricao():
    """Exemplo de transcrição de áudio."""
    print("\n🎧 Exemplo: Transcrição de áudio")
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar instâncias (em produção, usar factory pattern)
    video_repo = JsonVideoRepository()
    whisper = WhisperProvider(model_name="base")
    use_case = TranscribeAudioUseCase(video_repo, whisper)
    
    # Criar vídeo de exemplo com validação
    try:
        # Validar dados antes de criar a entidade
        validate_video_id("example_video")
        validate_video_title("Vídeo de Exemplo")
        print("✅ Dados do vídeo validados")
        
        video = Video(
            id="example_video",
            title="Vídeo de Exemplo",
            file_path="data/input/local/exemplo.mp4"
        )
        print("✅ Entidade Video criada com sucesso")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return
    
    # Salvar vídeo
    await video_repo.save(video)
    
    # Executar transcrição
    request = TranscribeAudioRequest(
        video_id=video.id,
        audio_path="data/input/local/exemplo.mp4",
        language="pt"
    )
    
    try:
        response = await use_case.execute(request)
        print("✅ Transcrição concluída!")
        print(f"📝 Texto: {response.transcription}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


async def main():
    """Executa todos os exemplos."""
    print("🤖 Alfredo AI - Exemplos de Uso\n")
    
    await exemplo_download_youtube()
    await exemplo_transcricao()
    
    print("\n🎉 Exemplos concluídos!")


if __name__ == "__main__":
    asyncio.run(main())
