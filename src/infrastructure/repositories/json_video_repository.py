"""Implementação do repositório de vídeos usando JSON."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.domain.entities.video import Video
from src.domain.repositories.video_repository import VideoRepository


class JsonVideoRepository(VideoRepository):
    """Repositório de vídeos usando arquivos JSON."""

    def __init__(self, base_path: str = "data/output"):
        """Inicializa o repositório.

        Args:
            base_path: Diretório base para armazenar os dados
        """
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def find_by_id(self, video_id: str) -> Optional[Video]:
        """Busca um vídeo pelo ID.

        Args:
            video_id: ID do vídeo

        Returns:
            Vídeo encontrado ou None
        """
        try:
            video_dir = self.base_path / video_id
            metadata_file = video_dir / "metadata.json"

            if not metadata_file.exists():
                return None

            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Converter string ISO para datetime
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])

            return Video(**data)

        except Exception as e:
            self.logger.error(f"Erro ao buscar vídeo {video_id}: {str(e)}")
            return None

    async def save(self, video: Video) -> None:
        """Salva um vídeo no repositório.

        Args:
            video: Vídeo a ser salvo
        """
        try:
            video_dir = self.base_path / video.id
            video_dir.mkdir(parents=True, exist_ok=True)

            # Preparar dados para serialização
            data = {
                "id": video.id,
                "title": video.title,
                "url": video.url,
                "file_path": video.file_path,
                "duration": video.duration,
                "created_at": (
                    video.created_at.isoformat() if video.created_at else None
                ),
                "metadata": video.metadata,
            }

            # Salvar metadados
            metadata_file = video_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Vídeo salvo: {video.id}")

        except Exception as e:
            self.logger.error(f"Erro ao salvar vídeo {video.id}: {str(e)}")
            raise

    async def delete(self, video_id: str) -> bool:
        """Remove um vídeo do repositório.

        Args:
            video_id: ID do vídeo

        Returns:
            True se removido com sucesso
        """
        try:
            video_dir = self.base_path / video_id
            if video_dir.exists():
                import shutil

                shutil.rmtree(video_dir)
                self.logger.info(f"Vídeo removido: {video_id}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Erro ao remover vídeo {video_id}: {str(e)}")
            return False

    async def list_all(self) -> list[Video]:
        """Lista todos os vídeos no repositório.

        Returns:
            Lista de vídeos
        """
        try:
            videos = []

            for item in self.base_path.iterdir():
                if item.is_dir():
                    video = await self.find_by_id(item.name)
                    if video:
                        videos.append(video)

            return videos

        except Exception as e:
            self.logger.error(f"Erro ao listar vídeos: {str(e)}")
            return []
