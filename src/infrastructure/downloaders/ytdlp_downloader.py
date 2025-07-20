"""Implementação de download usando yt-dlp."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError, 
    InvalidVideoFormatError,
    ConfigurationError
)


class YTDLPDownloader(VideoDownloaderGateway):
    """Implementação de VideoDownloaderGateway usando yt-dlp."""
    
    def __init__(self, config: AlfredoConfig):
        """
        Inicializa o downloader.
        
        Args:
            config: Configuração do Alfredo
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Verificar se yt-dlp está disponível
        try:
            import yt_dlp
            self.yt_dlp = yt_dlp
        except ImportError:
            raise ConfigurationError(
                "yt_dlp_dependency",
                "yt-dlp não está instalado",
                expected="pip install yt-dlp",
                details={"required_package": "yt-dlp"}
            )
    
    async def download(self, url: str, output_dir: str, 
                      quality: str = "best") -> str:
        """
        Baixa vídeo e retorna caminho do arquivo baixado.
        
        Args:
            url: URL do vídeo para download
            output_dir: Diretório de destino
            quality: Qualidade desejada do vídeo
            
        Returns:
            Caminho completo do arquivo baixado
            
        Raises:
            DownloadFailedError: Quando falha o download
        """
        try:
            # Garantir que o diretório existe
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Configurar opções do yt-dlp
            ydl_opts = {
                "format": self._get_format_selector(quality),
                "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }
            
            def download_sync():
                with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    return filename
            
            # Executar download em thread separada
            loop = asyncio.get_event_loop()
            filename = await loop.run_in_executor(None, download_sync)
            
            # Verificar se arquivo foi criado
            if not Path(filename).exists():
                raise DownloadFailedError(
                    url,
                    "Arquivo não foi criado após download",
                    details={
                        "expected_file": filename,
                        "output_dir": output_dir,
                        "quality": quality
                    }
                )
            
            self.logger.info(f"Download concluído: {filename}")
            return filename
            
        except self.yt_dlp.DownloadError as e:
            error_msg = str(e)
            if "private" in error_msg.lower():
                raise DownloadFailedError(
                    url, 
                    "Vídeo privado ou restrito",
                    details={"error": error_msg, "quality": quality}
                )
            elif "not available" in error_msg.lower():
                raise DownloadFailedError(
                    url, 
                    "Vídeo não disponível",
                    details={"error": error_msg, "quality": quality}
                )
            elif "copyright" in error_msg.lower():
                raise DownloadFailedError(
                    url, 
                    "Vídeo bloqueado por direitos autorais",
                    details={"error": error_msg, "quality": quality}
                )
            else:
                raise DownloadFailedError(
                    url, 
                    f"Erro no download: {error_msg}",
                    details={"error": error_msg, "quality": quality}
                )
        except Exception as e:
            self.logger.error(f"Erro inesperado no download: {str(e)}")
            raise DownloadFailedError(
                url, 
                f"Erro inesperado: {str(e)}",
                details={"error": str(e), "quality": quality, "output_dir": output_dir}
            )
    
    async def extract_info(self, url: str) -> Dict:
        """
        Extrai metadados do vídeo sem baixar.
        
        Args:
            url: URL do vídeo
            
        Returns:
            Dicionário com informações do vídeo
            
        Raises:
            InvalidVideoFormatError: Quando URL é inválida
        """
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
            }
            
            def extract_sync():
                with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            # Executar extração em thread separada
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, extract_sync)
            
            return {
                "id": info.get("id", "unknown"),
                "title": info.get("title", "Unknown Title"),
                "uploader": info.get("uploader", "Unknown"),
                "duration": info.get("duration", 0),
                "description": info.get("description", ""),
                "upload_date": info.get("upload_date", ""),
                "view_count": info.get("view_count", 0),
                "webpage_url": info.get("webpage_url", url),
            }
            
        except self.yt_dlp.DownloadError as e:
            error_msg = str(e)
            if "private" in error_msg.lower():
                raise InvalidVideoFormatError(
                    "url", 
                    url, 
                    "Vídeo privado ou restrito"
                )
            elif "not available" in error_msg.lower():
                raise InvalidVideoFormatError(
                    "url", 
                    url, 
                    "Vídeo não disponível"
                )
            else:
                raise InvalidVideoFormatError(
                    "url", 
                    url, 
                    f"URL inválida: {error_msg}"
                )
        except Exception as e:
            self.logger.error(f"Erro ao extrair informações: {str(e)}")
            raise InvalidVideoFormatError(
                "url", 
                url, 
                f"Erro ao acessar vídeo: {str(e)}"
            )
    
    async def get_available_formats(self, url: str) -> List[Dict]:
        """
        Lista formatos disponíveis para download.
        
        Args:
            url: URL do vídeo
            
        Returns:
            Lista de formatos disponíveis
            
        Raises:
            InvalidVideoFormatError: Quando URL é inválida
        """
        try:
            info = await self.extract_info(url)
            formats = info.get("formats", [])
            
            # Filtrar e simplificar informações dos formatos
            simplified_formats = []
            for fmt in formats:
                simplified_formats.append({
                    "format_id": fmt.get("format_id", "unknown"),
                    "ext": fmt.get("ext", "unknown"),
                    "quality": fmt.get("quality", "unknown"),
                    "filesize": fmt.get("filesize", 0),
                    "vcodec": fmt.get("vcodec", "unknown"),
                    "acodec": fmt.get("acodec", "unknown"),
                    "format_note": fmt.get("format_note", ""),
                })
            
            return simplified_formats
            
        except (InvalidVideoFormatError, DownloadFailedError):
            # Re-raise exceções específicas
            raise
        except Exception as e:
            self.logger.error(f"Erro ao listar formatos: {str(e)}")
            raise InvalidVideoFormatError(
                "url", 
                url, 
                f"Erro ao listar formatos: {str(e)}"
            )
    
    def _get_format_selector(self, quality: str) -> str:
        """
        Converte qualidade em seletor de formato do yt-dlp.
        
        Args:
            quality: Qualidade desejada (best, worst, 720p, etc.)
            
        Returns:
            String de seleção de formato para yt-dlp
        """
        quality_map = {
            "best": "best[ext=mp4]/best",
            "worst": "worst[ext=mp4]/worst",
            "720p": "best[height<=720][ext=mp4]/best[height<=720]",
            "480p": "best[height<=480][ext=mp4]/best[height<=480]",
            "360p": "best[height<=360][ext=mp4]/best[height<=360]",
        }
        
        return quality_map.get(quality, "best[ext=mp4]/best")
    
    async def is_url_supported(self, url: str) -> bool:
        """
        Verifica se a URL é suportada pelo yt-dlp.
        
        Args:
            url: URL a ser verificada
            
        Returns:
            bool: True se a URL é suportada, False caso contrário
        """
        try:
            # Tentar extrair informações básicas sem download
            await self.extract_info(url)
            return True
        except (InvalidVideoFormatError, DownloadFailedError):
            return False
        except Exception:
            return False
    
    async def get_video_id(self, url: str) -> Optional[str]:
        """
        Extrai o ID único do vídeo da URL.
        
        Args:
            url: URL do vídeo
            
        Returns:
            Optional[str]: ID do vídeo ou None se não puder ser extraído
            
        Raises:
            InvalidVideoFormatError: Quando a URL não é válida
        """
        try:
            info = await self.extract_info(url)
            return info.get("id")
        except (InvalidVideoFormatError, DownloadFailedError):
            # Re-raise exceções específicas
            raise
        except Exception as e:
            self.logger.error(f"Erro ao extrair ID do vídeo: {str(e)}")
            raise InvalidVideoFormatError(
                "url", 
                url, 
                f"Erro ao extrair ID: {str(e)}"
            )