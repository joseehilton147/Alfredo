#!/usr/bin/env python3
"""Exemplo básico de uso do Alfredo AI."""
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
from src.domain.entities.video import Video
from src.infrastructure.providers.whisper_provider import WhisperProvider
from src.infrastructure.repositories.json_video_repository import JsonVideoRepository


async def main():
    """Exemplo de uso básico."""
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar instâncias
    video_repo = JsonVideoRepository()
    whisper = WhisperProvider(model_name="base")
    use_case = TranscribeAudioUseCase(video_repo, whisper)
    
    # Criar vídeo de exemplo
    video = Video(
        id="example_video",
        title="Vídeo de Exemplo",
        file_path="data/input/local/exemplo.mp4"
    )
    
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
        print(f"Texto: {response.transcription}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    asyncio.run(main())
