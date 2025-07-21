"""Mocks e stubs para dependências externas."""

import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.application.interfaces.ai_provider import AIProviderInterface
from src.domain.entities.video import Video


class MockVideoDownloader(VideoDownloaderGateway):
    """Mock para VideoDownloaderGateway."""
    
    def __init__(self, config=None):
        self.config = config
        self.download_calls = []
        self.should_fail = False
        self.failure_exception = Exception("Mock download failure")
        self.download_delay = 0.0
        self.downloaded_videos = {}
    
    async def download(self, url: str, output_dir: Optional[Path] = None) -> Video:
        """Mock do método download."""
        self.download_calls.append({'url': url, 'output_dir': output_dir})
        
        if self.download_delay > 0:
            await asyncio.sleep(self.download_delay)
        
        if self.should_fail:
            raise self.failure_exception
        
        # Simular download bem-sucedido
        video_id = f"mock_video_{len(self.download_calls)}"
        file_path = output_dir / f"{video_id}.mp4" if output_dir else f"/tmp/{video_id}.mp4"
        
        video = Video(
            id=video_id,
            title=f"Mock Video from {url}",
            duration=120.0,
            file_path=str(file_path),
            url=url,
            metadata={
                'format': 'mp4',
                'resolution': '1920x1080',
                'downloaded_at': '2024-01-01T12:00:00Z'
            }
        )
        
        self.downloaded_videos[url] = video
        return video
    
    def set_failure(self, should_fail: bool, exception: Optional[Exception] = None):
        """Configura se o mock deve falhar."""
        self.should_fail = should_fail
        if exception:
            self.failure_exception = exception
    
    def set_delay(self, delay: float):
        """Configura delay para simular operação lenta."""
        self.download_delay = delay
    
    def get_download_count(self) -> int:
        """Retorna número de downloads realizados."""
        return len(self.download_calls)
    
    def was_url_downloaded(self, url: str) -> bool:
        """Verifica se URL foi baixada."""
        return any(call['url'] == url for call in self.download_calls)


class MockAudioExtractor(AudioExtractorGateway):
    """Mock para AudioExtractorGateway."""
    
    def __init__(self, config=None):
        self.config = config
        self.extract_calls = []
        self.should_fail = False
        self.failure_exception = Exception("Mock extraction failure")
        self.extract_delay = 0.0
        self.extracted_audios = {}
    
    async def extract(self, video: Video, output_dir: Optional[Path] = None) -> str:
        """Mock do método extract."""
        self.extract_calls.append({'video': video, 'output_dir': output_dir})
        
        if self.extract_delay > 0:
            await asyncio.sleep(self.extract_delay)
        
        if self.should_fail:
            raise self.failure_exception
        
        # Simular extração bem-sucedida
        audio_filename = f"audio_{video.id}.wav"
        audio_path = output_dir / audio_filename if output_dir else f"/tmp/{audio_filename}"
        
        self.extracted_audios[video.id] = str(audio_path)
        return str(audio_path)
    
    def set_failure(self, should_fail: bool, exception: Optional[Exception] = None):
        """Configura se o mock deve falhar."""
        self.should_fail = should_fail
        if exception:
            self.failure_exception = exception
    
    def set_delay(self, delay: float):
        """Configura delay para simular operação lenta."""
        self.extract_delay = delay
    
    def get_extract_count(self) -> int:
        """Retorna número de extrações realizadas."""
        return len(self.extract_calls)
    
    def was_video_extracted(self, video_id: str) -> bool:
        """Verifica se vídeo foi extraído."""
        return any(call['video'].id == video_id for call in self.extract_calls)


class MockAIProvider(AIProviderInterface):
    """Mock para AIProviderInterface."""
    
    def __init__(self, config=None):
        self.config = config
        self.transcribe_calls = []
        self.summarize_calls = []
        self.should_fail_transcribe = False
        self.should_fail_summarize = False
        self.transcribe_exception = Exception("Mock transcription failure")
        self.summarize_exception = Exception("Mock summarization failure")
        self.transcribe_delay = 0.0
        self.summarize_delay = 0.0
        self.transcription_results = {}
        self.summary_results = {}
    
    async def transcribe(self, audio_path: str, language: str = "pt") -> str:
        """Mock do método transcribe."""
        self.transcribe_calls.append({'audio_path': audio_path, 'language': language})
        
        if self.transcribe_delay > 0:
            await asyncio.sleep(self.transcribe_delay)
        
        if self.should_fail_transcribe:
            raise self.transcribe_exception
        
        # Simular transcrição bem-sucedida
        transcription = f"Transcrição mock do áudio {Path(audio_path).name} em {language}"
        self.transcription_results[audio_path] = transcription
        return transcription
    
    async def summarize(self, text: str, title: Optional[str] = None) -> str:
        """Mock do método summarize."""
        self.summarize_calls.append({'text': text, 'title': title})
        
        if self.summarize_delay > 0:
            await asyncio.sleep(self.summarize_delay)
        
        if self.should_fail_summarize:
            raise self.summarize_exception
        
        # Simular resumo bem-sucedido
        summary = f"Resumo mock do texto (primeiras 50 chars): {text[:50]}..."
        if title:
            summary = f"Resumo de '{title}': {summary}"
        
        self.summary_results[text[:100]] = summary
        return summary
    
    def set_transcribe_failure(self, should_fail: bool, exception: Optional[Exception] = None):
        """Configura se transcrição deve falhar."""
        self.should_fail_transcribe = should_fail
        if exception:
            self.transcribe_exception = exception
    
    def set_summarize_failure(self, should_fail: bool, exception: Optional[Exception] = None):
        """Configura se resumo deve falhar."""
        self.should_fail_summarize = should_fail
        if exception:
            self.summarize_exception = exception
    
    def set_transcribe_delay(self, delay: float):
        """Configura delay para transcrição."""
        self.transcribe_delay = delay
    
    def set_summarize_delay(self, delay: float):
        """Configura delay para resumo."""
        self.summarize_delay = delay
    
    def get_transcribe_count(self) -> int:
        """Retorna número de transcrições realizadas."""
        return len(self.transcribe_calls)
    
    def get_summarize_count(self) -> int:
        """Retorna número de resumos realizados."""
        return len(self.summarize_calls)


class MockStorage(StorageGateway):
    """Mock para StorageGateway."""
    
    def __init__(self, config=None):
        self.config = config
        self.save_calls = []
        self.load_calls = []
        self.should_fail_save = False
        self.should_fail_load = False
        self.save_exception = Exception("Mock save failure")
        self.load_exception = Exception("Mock load failure")
        self.stored_data = {}
        self.save_delay = 0.0
        self.load_delay = 0.0
    
    async def save_video(self, video: Video) -> str:
        """Mock do método save_video."""
        self.save_calls.append({'type': 'video', 'data': video})
        
        if self.save_delay > 0:
            await asyncio.sleep(self.save_delay)
        
        if self.should_fail_save:
            raise self.save_exception
        
        file_path = f"/mock/storage/videos/{video.id}.json"
        self.stored_data[f"video_{video.id}"] = video
        return file_path
    
    async def save_transcription(self, video_id: str, transcription: str) -> str:
        """Mock do método save_transcription."""
        self.save_calls.append({'type': 'transcription', 'video_id': video_id, 'data': transcription})
        
        if self.save_delay > 0:
            await asyncio.sleep(self.save_delay)
        
        if self.should_fail_save:
            raise self.save_exception
        
        file_path = f"/mock/storage/transcriptions/{video_id}.txt"
        self.stored_data[f"transcription_{video_id}"] = transcription
        return file_path
    
    async def save_summary(self, video_id: str, summary: str) -> str:
        """Mock do método save_summary."""
        self.save_calls.append({'type': 'summary', 'video_id': video_id, 'data': summary})
        
        if self.save_delay > 0:
            await asyncio.sleep(self.save_delay)
        
        if self.should_fail_save:
            raise self.save_exception
        
        file_path = f"/mock/storage/summaries/{video_id}.html"
        self.stored_data[f"summary_{video_id}"] = summary
        return file_path
    
    async def load_video(self, video_id: str) -> Optional[Video]:
        """Mock do método load_video."""
        self.load_calls.append({'type': 'video', 'video_id': video_id})
        
        if self.load_delay > 0:
            await asyncio.sleep(self.load_delay)
        
        if self.should_fail_load:
            raise self.load_exception
        
        return self.stored_data.get(f"video_{video_id}")
    
    async def load_transcription(self, video_id: str) -> Optional[str]:
        """Mock do método load_transcription."""
        self.load_calls.append({'type': 'transcription', 'video_id': video_id})
        
        if self.load_delay > 0:
            await asyncio.sleep(self.load_delay)
        
        if self.should_fail_load:
            raise self.load_exception
        
        return self.stored_data.get(f"transcription_{video_id}")
    
    async def load_summary(self, video_id: str) -> Optional[str]:
        """Mock do método load_summary."""
        self.load_calls.append({'type': 'summary', 'video_id': video_id})
        
        if self.load_delay > 0:
            await asyncio.sleep(self.load_delay)
        
        if self.should_fail_load:
            raise self.load_exception
        
        return self.stored_data.get(f"summary_{video_id}")
    
    def set_save_failure(self, should_fail: bool, exception: Optional[Exception] = None):
        """Configura se save deve falhar."""
        self.should_fail_save = should_fail
        if exception:
            self.save_exception = exception
    
    def set_load_failure(self, should_fail: bool, exception: Optional[Exception] = None):
        """Configura se load deve falhar."""
        self.should_fail_load = should_fail
        if exception:
            self.load_exception = exception
    
    def set_delays(self, save_delay: float = 0.0, load_delay: float = 0.0):
        """Configura delays para operações."""
        self.save_delay = save_delay
        self.load_delay = load_delay
    
    def get_save_count(self) -> int:
        """Retorna número de saves realizados."""
        return len(self.save_calls)
    
    def get_load_count(self) -> int:
        """Retorna número de loads realizados."""
        return len(self.load_calls)
    
    def clear_storage(self):
        """Limpa dados armazenados."""
        self.stored_data.clear()
        self.save_calls.clear()
        self.load_calls.clear()


class MockInfrastructureFactory:
    """Mock para InfrastructureFactory."""
    
    def __init__(self, config=None):
        self.config = config
        self.video_downloader = MockVideoDownloader(config)
        self.audio_extractor = MockAudioExtractor(config)
        self.ai_provider = MockAIProvider(config)
        self.storage = MockStorage(config)
        self.creation_calls = []
    
    def create_video_downloader(self) -> MockVideoDownloader:
        """Cria mock de video downloader."""
        self.creation_calls.append('video_downloader')
        return self.video_downloader
    
    def create_audio_extractor(self) -> MockAudioExtractor:
        """Cria mock de audio extractor."""
        self.creation_calls.append('audio_extractor')
        return self.audio_extractor
    
    def create_ai_provider(self, provider_type: str = "whisper") -> MockAIProvider:
        """Cria mock de AI provider."""
        self.creation_calls.append(f'ai_provider_{provider_type}')
        return self.ai_provider
    
    def create_storage(self, storage_type: str = "filesystem") -> MockStorage:
        """Cria mock de storage."""
        self.creation_calls.append(f'storage_{storage_type}')
        return self.storage
    
    def create_all_dependencies(self, provider_type: str = None, storage_type: str = "filesystem") -> Dict[str, Any]:
        """Cria todas as dependências mock."""
        self.creation_calls.append('all_dependencies')
        return {
            'downloader': self.video_downloader,
            'extractor': self.audio_extractor,
            'ai_provider': self.ai_provider,
            'storage': self.storage,
            'config': self.config
        }
    
    def reset_mocks(self):
        """Reseta todos os mocks."""
        self.video_downloader = MockVideoDownloader(self.config)
        self.audio_extractor = MockAudioExtractor(self.config)
        self.ai_provider = MockAIProvider(self.config)
        self.storage = MockStorage(self.config)
        self.creation_calls.clear()
    
    def configure_failures(self, 
                          download_fail: bool = False,
                          extract_fail: bool = False,
                          transcribe_fail: bool = False,
                          summarize_fail: bool = False,
                          save_fail: bool = False,
                          load_fail: bool = False):
        """Configura falhas em todos os mocks."""
        self.video_downloader.set_failure(download_fail)
        self.audio_extractor.set_failure(extract_fail)
        self.ai_provider.set_transcribe_failure(transcribe_fail)
        self.ai_provider.set_summarize_failure(summarize_fail)
        self.storage.set_save_failure(save_fail)
        self.storage.set_load_failure(load_fail)
    
    def configure_delays(self,
                        download_delay: float = 0.0,
                        extract_delay: float = 0.0,
                        transcribe_delay: float = 0.0,
                        summarize_delay: float = 0.0,
                        save_delay: float = 0.0,
                        load_delay: float = 0.0):
        """Configura delays em todos os mocks."""
        self.video_downloader.set_delay(download_delay)
        self.audio_extractor.set_delay(extract_delay)
        self.ai_provider.set_transcribe_delay(transcribe_delay)
        self.ai_provider.set_summarize_delay(summarize_delay)
        self.storage.set_delays(save_delay, load_delay)


# Stubs para bibliotecas externas

class MockYTDLP:
    """Mock para yt-dlp."""
    
    def __init__(self):
        self.extract_info_calls = []
        self.download_calls = []
        self.should_fail = False
        self.failure_exception = Exception("Mock yt-dlp failure")
    
    def extract_info(self, url: str, download: bool = False) -> Dict[str, Any]:
        """Mock do extract_info."""
        self.extract_info_calls.append({'url': url, 'download': download})
        
        if self.should_fail:
            raise self.failure_exception
        
        return {
            'id': 'mock_video_id',
            'title': f'Mock Video from {url}',
            'duration': 120.0,
            'url': url,
            'formats': [
                {'format_id': 'best', 'ext': 'mp4', 'url': f'{url}/video.mp4'}
            ]
        }
    
    def download(self, urls: List[str]) -> None:
        """Mock do download."""
        self.download_calls.extend(urls)
        
        if self.should_fail:
            raise self.failure_exception


class MockFFmpeg:
    """Mock para FFmpeg."""
    
    def __init__(self):
        self.input_calls = []
        self.output_calls = []
        self.run_calls = []
        self.should_fail = False
        self.failure_exception = Exception("Mock FFmpeg failure")
    
    def input(self, filename: str, **kwargs):
        """Mock do input."""
        self.input_calls.append({'filename': filename, 'kwargs': kwargs})
        return self
    
    def output(self, filename: str, **kwargs):
        """Mock do output."""
        self.output_calls.append({'filename': filename, 'kwargs': kwargs})
        return self
    
    def run(self, **kwargs):
        """Mock do run."""
        self.run_calls.append(kwargs)
        
        if self.should_fail:
            raise self.failure_exception


class MockWhisper:
    """Mock para OpenAI Whisper."""
    
    def __init__(self):
        self.load_model_calls = []
        self.transcribe_calls = []
        self.should_fail = False
        self.failure_exception = Exception("Mock Whisper failure")
    
    def load_model(self, name: str):
        """Mock do load_model."""
        self.load_model_calls.append(name)
        return self
    
    def transcribe(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Mock do transcribe."""
        self.transcribe_calls.append({'audio_path': audio_path, 'kwargs': kwargs})
        
        if self.should_fail:
            raise self.failure_exception
        
        return {
            'text': f'Transcrição mock do arquivo {Path(audio_path).name}',
            'language': kwargs.get('language', 'pt'),
            'segments': [
                {'start': 0.0, 'end': 5.0, 'text': 'Primeira parte'},
                {'start': 5.0, 'end': 10.0, 'text': 'Segunda parte'}
            ]
        }