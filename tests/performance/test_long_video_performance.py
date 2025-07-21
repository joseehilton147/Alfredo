import time
import pytest
import psutil
from memory_profiler import memory_usage
import asyncio
from pathlib import Path
import os
import subprocess
from src.application.use_cases.process_local_video import (
    ProcessLocalVideoUseCase,
    ProcessLocalVideoRequest
)
from src.config.alfredo_config import AlfredoConfig

class DummyExtractor:
    async def get_audio_info(self, video_path):
        return {'duration': 3600}

    async def extract_audio(self, video_path, audio_path, **kwargs):
        # simula processamento de 2 segundos
        time.sleep(2)
        return

class DummyAIProvider:
    async def transcribe_audio(self, path, lang):
        time.sleep(1)
        return "transcription"

class DummyStorage:
    async def load_video(self, id): return None
    async def load_transcription(self, id): return None
    async def save_video(self, video): pass
    async def save_transcription(self, id, transcription, metadata=None):
        # Armazena transcrição com metadata opcional
        pass

@pytest.mark.performance
def test_long_video_performance_time_and_memory(tmp_path):
    config = AlfredoConfig()
    # threshold de 20% sobre duração máxima configurada
    time_threshold = config.max_video_duration * 1.2
    mem_threshold = 500 * 1024 * 1024  # 500MB

    # gera arquivo dummy
    video_file = tmp_path / "video.mp4"
    video_file.write_text("")

    use_case = ProcessLocalVideoUseCase(
        downloader=None,
        extractor=DummyExtractor(),
        ai_provider=DummyAIProvider(),
        storage=DummyStorage(),
        config=config
    )

    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss

    def run_use_case():
        import asyncio
        # Criar um novo loop para evitar conflito com loop em execução
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                use_case.execute(ProcessLocalVideoRequest(str(video_file)))
            )
        finally:
            loop.close()

    # medir tempo e memória
    start = time.perf_counter()
    mem_usage = memory_usage((run_use_case,), interval=0.1)
    duration = time.perf_counter() - start

    # memory_usage retorna MiB
    peak_mem = max(mem_usage) * 1024 * 1024
    assert duration <= time_threshold, f"Tempo {duration}s excede threshold {time_threshold}s"
    assert (peak_mem - start_mem) <= mem_threshold, (
        f"Pico de memória {peak_mem} ultrapassa threshold {mem_threshold}"
    )

@pytest.mark.performance
@pytest.mark.asyncio
async def test_timeout_raised_on_extract_audio(monkeypatch, tmp_path):
    from subprocess import TimeoutExpired
    config = AlfredoConfig()
    config.transcription_timeout = 1

    # substitui extractor para demorar 2s
    extractor = DummyExtractor()
    async def slow_extract(video_path, audio_path, **kwargs):
        # simula atraso usando asyncio para respeitar timeout
        await asyncio.sleep(2)
    monkeypatch.setattr(extractor, 'extract_audio', slow_extract)

    use_case = ProcessLocalVideoUseCase(
        downloader=None,
        extractor=extractor,
        ai_provider=DummyAIProvider(),
        storage=DummyStorage(),
        config=config
    )

    video_file = tmp_path / "video.mp4"
    video_file.write_text("")

    with pytest.raises(TimeoutExpired):
        await use_case.execute(ProcessLocalVideoRequest(str(video_file)))
