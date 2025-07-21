"""Implementação do repositório de vídeos usando JSON."""

import json
import time
import psutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.repositories.video_repository import VideoRepository
from src.domain.exceptions.alfredo_errors import ConfigurationError, InvalidVideoFormatError


class JsonVideoRepository(VideoRepository):
    """Repositório de vídeos usando arquivos JSON."""

    def __init__(self, config: Optional[AlfredoConfig] = None):
        """Inicializa o repositório.

        Args:
            config: Configuração do Alfredo (opcional, usa padrão se não fornecida)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        self.base_path = self.config.data_dir / "output"
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def find_by_id(self, video_id: str) -> Optional[Video]:
        # imports já estão no topo
        start_time = time.time()
        mem_start = psutil.Process().memory_info().rss // 1024 // 1024
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

            # Mapear 'url' antiga para 'source_url' se 'source_url' não existir
            if "url" in data and "source_url" not in data:
                data["source_url"] = data.pop("url")

            mem_end = psutil.Process().memory_info().rss // 1024 // 1024
            duration = round(time.time() - start_time, 2)
            self.logger.info(f"Video loaded: {video_id}", extra={"duration_sec": duration, "mem_usage_mb": mem_end})
            return Video(**data)

        except FileNotFoundError:
            # File not found is expected behavior, not an error
            return None
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Dados corrompidos para vídeo {video_id}: {str(e)}")
            raise InvalidVideoFormatError(
                "metadata", 
                str(metadata_file), 
                f"Arquivo de metadados corrompido: {str(e)}",
                details={"video_id": video_id, "file_path": str(metadata_file)}
            )
        except PermissionError as e:
            self.logger.error(f"Sem permissão para acessar vídeo {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para acessar {metadata_file}",
                expected="permissões de leitura",
                details={"video_id": video_id, "file_path": str(metadata_file)}
            )
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar vídeo {video_id}: {str(e)}")
            return None

    async def save(self, video: Video) -> None:
        import time, psutil
        start_time = time.time()
        mem_start = psutil.Process().memory_info().rss // 1024 // 1024
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
                "transcription": video.transcription,
                "source_url": video.source_url,
            }

            # Salvar metadados
            metadata_file = video_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            mem_end = psutil.Process().memory_info().rss // 1024 // 1024
            duration = round(time.time() - start_time, 2)
            self.logger.info(f"Vídeo salvo: {video.id}", extra={"duration_sec": duration, "mem_usage_mb": mem_end})

        except PermissionError as e:
            self.logger.error(f"Sem permissão para salvar vídeo {video.id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para escrever em {video_dir}",
                expected="permissões de escrita",
                details={"video_id": video.id, "directory": str(video_dir)}
            )
        except OSError as e:
            self.logger.error(f"Erro de sistema ao salvar vídeo {video.id}: {str(e)}")
            raise ConfigurationError(
                "storage_space",
                f"Erro de sistema ao salvar: {str(e)}",
                expected="espaço em disco suficiente",
                details={"video_id": video.id, "directory": str(video_dir)}
            )
        except Exception as e:
            self.logger.error(f"Erro inesperado ao salvar vídeo {video.id}: {str(e)}")
            raise

    async def delete(self, video_id: str) -> bool:
        import time, psutil
        start_time = time.time()
        mem_start = psutil.Process().memory_info().rss // 1024 // 1024
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
                mem_end = psutil.Process().memory_info().rss // 1024 // 1024
                duration = round(time.time() - start_time, 2)
                self.logger.info(f"Vídeo removido: {video_id}", extra={"duration_sec": duration, "mem_usage_mb": mem_end})
                return True
            return False

        except PermissionError as e:
            self.logger.error(f"Sem permissão para remover vídeo {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para remover {video_dir}",
                expected="permissões de escrita",
                details={"video_id": video_id, "directory": str(video_dir)}
            )
        except Exception as e:
            self.logger.error(f"Erro inesperado ao remover vídeo {video_id}: {str(e)}")
            return False

    async def list_all(self) -> list[Video]:
        import time, psutil
        start_time = time.time()
        mem_start = psutil.Process().memory_info().rss // 1024 // 1024
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

            mem_end = psutil.Process().memory_info().rss // 1024 // 1024
            duration = round(time.time() - start_time, 2)
            self.logger.info(f"Videos listed", extra={"duration_sec": duration, "mem_usage_mb": mem_end, "count": len(videos)})
            return videos

        except PermissionError as e:
            self.logger.error(f"Sem permissão para listar vídeos: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para acessar diretório {self.base_path}",
                expected="permissões de leitura",
                details={"directory": str(self.base_path)}
            )
        except Exception as e:
            self.logger.error(f"Erro inesperado ao listar vídeos: {str(e)}")
            return []
