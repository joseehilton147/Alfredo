"""
Gateway para download de vídeos.

Este módulo define a interface abstrata para download de vídeos de diferentes fontes,
seguindo os princípios da Clean Architecture onde a camada de aplicação define
contratos que a infraestrutura deve implementar.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pathlib import Path


class VideoDownloaderGateway(ABC):
    """
    Interface abstrata para download de vídeos.
    
    Esta interface define os contratos que implementações concretas de download
    de vídeo devem seguir, permitindo isolamento da infraestrutura e facilitando
    testes através de mocks.
    """

    @abstractmethod
    async def download(
        self,
        url: str,
        output_dir: str | Path,
        quality: str = "best"
    ) -> str:
        """
        Baixa um vídeo da URL especificada.
        
        Args:
            url: URL válida do vídeo a ser baixado
            output_dir: Diretório onde o vídeo será salvo
            quality: Qualidade do vídeo ("best", "worst", "720p", etc.)
            
        Returns:
            str: Caminho completo do arquivo de vídeo baixado
            
        Raises:
            DownloadFailedError: Quando o download falha por qualquer motivo
            InvalidVideoFormatError: Quando a URL não é válida ou suportada
            ConfigurationError: Quando há problemas de configuração
        """
        pass

    @abstractmethod
    async def extract_info(self, url: str) -> Dict:
        """
        Extrai metadados do vídeo sem fazer o download.
        
        Esta operação é útil para validar URLs, obter informações sobre
        duração, título e formatos disponíveis antes de decidir baixar.
        
        Args:
            url: URL do vídeo para extrair informações
            
        Returns:
            Dict: Dicionário com metadados do vídeo contendo:
                - title: Título do vídeo
                - duration: Duração em segundos
                - uploader: Nome do canal/uploader
                - upload_date: Data de upload (formato YYYYMMDD)
                - view_count: Número de visualizações
                - description: Descrição do vídeo
                - thumbnail: URL da thumbnail
                - formats: Lista de formatos disponíveis
                
        Raises:
            DownloadFailedError: Quando não é possível acessar a URL
            InvalidVideoFormatError: Quando a URL não é válida
        """
        pass

    @abstractmethod
    async def get_available_formats(self, url: str) -> List[Dict]:
        """
        Lista todos os formatos disponíveis para download.
        
        Útil para permitir que o usuário escolha entre diferentes
        qualidades e formatos antes de fazer o download.
        
        Args:
            url: URL do vídeo para listar formatos
            
        Returns:
            List[Dict]: Lista de dicionários, cada um representando um formato:
                - format_id: ID único do formato
                - ext: Extensão do arquivo (mp4, webm, etc.)
                - quality: Descrição da qualidade
                - filesize: Tamanho estimado em bytes (pode ser None)
                - vcodec: Codec de vídeo
                - acodec: Codec de áudio
                - fps: Frames por segundo
                - resolution: Resolução (ex: "1920x1080")
                
        Raises:
            DownloadFailedError: Quando não é possível acessar a URL
            InvalidVideoFormatError: Quando a URL não é válida
        """
        pass

    @abstractmethod
    async def is_url_supported(self, url: str) -> bool:
        """
        Verifica se a URL é suportada pelo downloader.
        
        Args:
            url: URL a ser verificada
            
        Returns:
            bool: True se a URL é suportada, False caso contrário
        """
        pass

    @abstractmethod
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
        pass