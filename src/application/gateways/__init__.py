"""
Gateways da camada de aplicação.

Este módulo exporta todas as interfaces de gateway que definem contratos
para a infraestrutura implementar.
"""

from .video_downloader_gateway import VideoDownloaderGateway
from .audio_extractor_gateway import AudioExtractorGateway, AudioFormat
from .storage_gateway import StorageGateway

__all__ = [
    "VideoDownloaderGateway",
    "AudioExtractorGateway", 
    "AudioFormat",
    "StorageGateway"
]