"""Adapter para compatibilizar JsonVideoRepository com StorageGateway."""

from typing import List, Optional, Dict

from src.application.gateways.storage_gateway import StorageGateway
from src.domain.entities.video import Video
from src.domain.repositories.video_repository import VideoRepository


class JsonStorageAdapter(StorageGateway):
    """
    Adapter que permite usar VideoRepository como StorageGateway.
    
    Este adapter permite reutilizar a implementação existente do
    JsonVideoRepository através da interface StorageGateway.
    """
    
    def __init__(self, video_repository: VideoRepository):
        """
        Inicializa o adapter.
        
        Args:
            video_repository: Repositório de vídeos existente
        """
        self.video_repository = video_repository
        self._transcriptions: Dict[str, str] = {}  # Cache simples para transcrições
    
    async def save_video(self, video: Video) -> None:
        """
        Salva metadados do vídeo.
        
        Args:
            video: Entidade de vídeo para salvar
        """
        await self.video_repository.save(video)
    
    async def load_video(self, video_id: str) -> Optional[Video]:
        """
        Carrega vídeo por ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Vídeo encontrado ou None
        """
        return await self.video_repository.find_by_id(video_id)
    
    async def save_transcription(self, video_id: str, transcription: str,
                                metadata: Optional[Dict] = None) -> None:
        """
        Salva transcrição com metadados opcionais.
        
        Args:
            video_id: ID do vídeo
            transcription: Texto da transcrição
            metadata: Metadados opcionais da transcrição
        """
        # Armazenar transcrição no cache
        self._transcriptions[video_id] = transcription
        
        # Atualizar vídeo com transcrição
        video = await self.load_video(video_id)
        if video:
            video.transcription = transcription
            if metadata:
                if not hasattr(video, 'metadata') or video.metadata is None:
                    video.metadata = {}
                video.metadata.update(metadata)
            await self.save_video(video)
    
    async def load_transcription(self, video_id: str) -> Optional[str]:
        """
        Carrega transcrição por video ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Transcrição encontrada ou None
        """
        # Primeiro tentar do cache
        if video_id in self._transcriptions:
            return self._transcriptions[video_id]
        
        # Depois tentar do vídeo
        video = await self.load_video(video_id)
        if video and hasattr(video, 'transcription') and video.transcription:
            self._transcriptions[video_id] = video.transcription
            return video.transcription
        
        return None
    
    async def list_videos(self, limit: int = 100, 
                         offset: int = 0) -> List[Video]:
        """
        Lista vídeos com paginação.
        
        Args:
            limit: Número máximo de vídeos
            offset: Número de vídeos para pular
            
        Returns:
            Lista de vídeos
        """
        # O JsonVideoRepository não suporta paginação nativamente
        # então vamos implementar uma versão simples
        all_videos = await self.video_repository.list_all()
        
        # Aplicar paginação manualmente
        return all_videos[offset:offset + limit]