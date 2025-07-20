"""Implementação de armazenamento usando sistema de arquivos."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from src.application.gateways.storage_gateway import StorageGateway
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    ConfigurationError,
    InvalidVideoFormatError
)


class FileSystemStorage(StorageGateway):
    """Implementação de StorageGateway usando sistema de arquivos."""
    
    def __init__(self, config: AlfredoConfig):
        """
        Inicializa o storage.
        
        Args:
            config: Configuração do Alfredo
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_path = config.data_dir / "output"
        
        # Garantir que diretórios existem
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Garante que todos os diretórios necessários existem."""
        directories = [
            self.base_path,
            self.base_path / "videos",
            self.base_path / "transcriptions",
            self.base_path / "summaries",
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise ConfigurationError(
                    "directory_creation",
                    f"Sem permissão para criar {directory}: {e}",
                    expected="permissões de escrita",
                    details={"directory": str(directory)}
                )
    
    async def save_video(self, video: Video) -> None:
        """
        Salva metadados do vídeo.
        
        Args:
            video: Entidade de vídeo para salvar
            
        Raises:
            ConfigurationError: Quando há erro de configuração
        """
        try:
            video_dir = self.base_path / "videos" / video.id
            video_dir.mkdir(parents=True, exist_ok=True)
            
            # Preparar dados para serialização
            data = {
                "id": video.id,
                "title": video.title,
                "url": getattr(video, 'url', None) or getattr(video, 'source_url', None),
                "file_path": video.file_path,
                "duration": video.duration,
                "created_at": (
                    video.created_at.isoformat() if video.created_at else None
                ),
                "metadata": getattr(video, 'metadata', {}),
                "transcription": getattr(video, 'transcription', None),
                "summary": getattr(video, 'summary', None),
            }
            
            # Salvar metadados
            metadata_file = video_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Vídeo salvo: {video.id}")
            
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
            raise ConfigurationError(
                "video_save_error",
                f"Erro inesperado ao salvar: {str(e)}",
                expected="salvamento bem-sucedido",
                details={"video_id": video.id, "error": str(e)}
            )
    
    async def load_video(self, video_id: str) -> Optional[Video]:
        """
        Carrega vídeo por ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Vídeo encontrado ou None
            
        Raises:
            ConfigurationError: Quando há erro de acesso
        """
        try:
            video_dir = self.base_path / "videos" / video_id
            metadata_file = video_dir / "metadata.json"
            
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Converter string ISO para datetime
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            
            # Mapear campos para compatibilidade
            if data.get("url") and not data.get("source_url"):
                data["source_url"] = data["url"]
            
            return Video(**data)
            
        except FileNotFoundError:
            # File not found é comportamento esperado, não erro
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
    
    async def save_transcription(self, video_id: str, transcription: str,
                                metadata: Optional[Dict] = None) -> None:
        """
        Salva transcrição com metadados opcionais.
        
        Args:
            video_id: ID do vídeo
            transcription: Texto da transcrição
            metadata: Metadados opcionais da transcrição
            
        Raises:
            ConfigurationError: Quando há erro de configuração
        """
        try:
            transcription_dir = self.base_path / "transcriptions" / video_id
            transcription_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar transcrição
            transcription_file = transcription_dir / "transcription.txt"
            with open(transcription_file, "w", encoding="utf-8") as f:
                f.write(transcription)
            
            # Salvar metadados se fornecidos
            if metadata:
                metadata_file = transcription_dir / "metadata.json"
                metadata_with_timestamp = {
                    **metadata,
                    "created_at": datetime.now().isoformat(),
                    "video_id": video_id,
                    "transcription_length": len(transcription)
                }
                
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata_with_timestamp, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Transcrição salva para vídeo: {video_id}")
            
        except PermissionError as e:
            self.logger.error(f"Sem permissão para salvar transcrição {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para escrever transcrição",
                expected="permissões de escrita",
                details={"video_id": video_id, "directory": str(transcription_dir)}
            )
        except Exception as e:
            self.logger.error(f"Erro ao salvar transcrição {video_id}: {str(e)}")
            raise ConfigurationError(
                "transcription_save_error",
                f"Erro ao salvar transcrição: {str(e)}",
                expected="salvamento bem-sucedido",
                details={"video_id": video_id, "error": str(e)}
            )
    
    async def load_transcription(self, video_id: str) -> Optional[str]:
        """
        Carrega transcrição por video ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Transcrição encontrada ou None
        """
        try:
            transcription_file = self.base_path / "transcriptions" / video_id / "transcription.txt"
            
            if not transcription_file.exists():
                return None
            
            with open(transcription_file, "r", encoding="utf-8") as f:
                return f.read()
                
        except FileNotFoundError:
            return None
        except PermissionError as e:
            self.logger.error(f"Sem permissão para acessar transcrição {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para acessar transcrição",
                expected="permissões de leitura",
                details={"video_id": video_id, "file_path": str(transcription_file)}
            )
        except Exception as e:
            self.logger.error(f"Erro ao carregar transcrição {video_id}: {str(e)}")
            return None
    

    
    async def save_summary(
        self,
        video_id: str,
        summary: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Salva resumo de um vídeo com metadados opcionais.
        
        Args:
            video_id: ID do vídeo associado ao resumo
            summary: Texto do resumo
            metadata: Metadados adicionais opcionais
            
        Raises:
            ConfigurationError: Quando há erro de configuração
        """
        try:
            summary_dir = self.base_path / "summaries" / video_id
            summary_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar resumo
            summary_file = summary_dir / "summary.txt"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            
            # Salvar metadados se fornecidos
            if metadata:
                metadata_file = summary_dir / "metadata.json"
                metadata_with_timestamp = {
                    **metadata,
                    "created_at": datetime.now().isoformat(),
                    "video_id": video_id,
                    "summary_length": len(summary)
                }
                
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata_with_timestamp, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Resumo salvo para vídeo: {video_id}")
            
        except PermissionError as e:
            self.logger.error(f"Sem permissão para salvar resumo {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para escrever resumo",
                expected="permissões de escrita",
                details={"video_id": video_id, "directory": str(summary_dir)}
            )
        except Exception as e:
            self.logger.error(f"Erro ao salvar resumo {video_id}: {str(e)}")
            raise ConfigurationError(
                "summary_save_error",
                f"Erro ao salvar resumo: {str(e)}",
                expected="salvamento bem-sucedido",
                details={"video_id": video_id, "error": str(e)}
            )
    
    async def load_summary(self, video_id: str) -> Optional[str]:
        """
        Carrega resumo de um vídeo pelo ID.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Texto do resumo ou None se não encontrado
        """
        try:
            summary_file = self.base_path / "summaries" / video_id / "summary.txt"
            
            if not summary_file.exists():
                return None
            
            with open(summary_file, "r", encoding="utf-8") as f:
                return f.read()
                
        except FileNotFoundError:
            return None
        except PermissionError as e:
            self.logger.error(f"Sem permissão para acessar resumo {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para acessar resumo",
                expected="permissões de leitura",
                details={"video_id": video_id, "file_path": str(summary_file)}
            )
        except Exception as e:
            self.logger.error(f"Erro ao carregar resumo {video_id}: {str(e)}")
            return None
    
    async def list_videos(
        self, 
        limit: int = 100, 
        offset: int = 0,
        filter_by: Optional[Dict] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Video]:
        """
        Lista vídeos com suporte a paginação e filtros.
        
        Args:
            limit: Número máximo de vídeos a retornar
            offset: Número de vídeos a pular (para paginação)
            filter_by: Filtros opcionais
            sort_by: Campo para ordenação
            sort_order: Ordem de classificação
            
        Returns:
            Lista de vídeos que atendem aos critérios
        """
        try:
            videos = []
            videos_dir = self.base_path / "videos"
            
            if not videos_dir.exists():
                return videos
            
            # Listar diretórios de vídeos
            video_dirs = [d for d in videos_dir.iterdir() if d.is_dir()]
            
            # Carregar todos os vídeos primeiro
            all_videos = []
            for video_dir in video_dirs:
                video = await self.load_video(video_dir.name)
                if video:
                    all_videos.append(video)
            
            # Aplicar filtros se fornecidos
            if filter_by:
                all_videos = self._apply_filters(all_videos, filter_by)
            
            # Aplicar ordenação
            all_videos = self._apply_sorting(all_videos, sort_by, sort_order)
            
            # Aplicar paginação
            paginated_videos = all_videos[offset:offset + limit]
            
            return paginated_videos
            
        except PermissionError as e:
            self.logger.error(f"Sem permissão para listar vídeos: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para acessar diretório {videos_dir}",
                expected="permissões de leitura",
                details={"directory": str(videos_dir)}
            )
        except Exception as e:
            self.logger.error(f"Erro inesperado ao listar vídeos: {str(e)}")
            return []
    
    def _apply_filters(self, videos: List[Video], filter_by: Dict) -> List[Video]:
        """Aplica filtros à lista de vídeos."""
        filtered_videos = videos
        
        if filter_by.get("has_transcription") is not None:
            has_transcription = filter_by["has_transcription"]
            filtered_videos = [
                v for v in filtered_videos 
                if bool(getattr(v, 'transcription', None)) == has_transcription
            ]
        
        if filter_by.get("has_summary") is not None:
            has_summary = filter_by["has_summary"]
            filtered_videos = [
                v for v in filtered_videos 
                if bool(getattr(v, 'summary', None)) == has_summary
            ]
        
        if filter_by.get("source_type"):
            source_type = filter_by["source_type"]
            if source_type == "local":
                filtered_videos = [v for v in filtered_videos if v.is_local()]
            elif source_type == "remote":
                filtered_videos = [v for v in filtered_videos if v.is_remote()]
        
        if filter_by.get("date_from"):
            date_from = filter_by["date_from"]
            filtered_videos = [
                v for v in filtered_videos 
                if v.created_at and v.created_at >= date_from
            ]
        
        if filter_by.get("date_to"):
            date_to = filter_by["date_to"]
            filtered_videos = [
                v for v in filtered_videos 
                if v.created_at and v.created_at <= date_to
            ]
        
        return filtered_videos
    
    def _apply_sorting(self, videos: List[Video], sort_by: str, sort_order: str) -> List[Video]:
        """Aplica ordenação à lista de vídeos."""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "created_at":
            return sorted(
                videos, 
                key=lambda v: v.created_at or datetime.min, 
                reverse=reverse
            )
        elif sort_by == "title":
            return sorted(videos, key=lambda v: v.title.lower(), reverse=reverse)
        elif sort_by == "duration":
            return sorted(videos, key=lambda v: v.duration, reverse=reverse)
        else:
            # Fallback para created_at
            return sorted(
                videos, 
                key=lambda v: v.created_at or datetime.min, 
                reverse=reverse
            )
    
    async def delete_video(self, video_id: str) -> bool:
        """
        Remove um vídeo e todos os dados associados.
        
        Args:
            video_id: ID do vídeo a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
        """
        try:
            import shutil
            
            removed_any = False
            
            # Remover diretório do vídeo
            video_dir = self.base_path / "videos" / video_id
            if video_dir.exists():
                shutil.rmtree(video_dir)
                removed_any = True
                self.logger.info(f"Diretório do vídeo removido: {video_dir}")
            
            # Remover transcrição
            transcription_dir = self.base_path / "transcriptions" / video_id
            if transcription_dir.exists():
                shutil.rmtree(transcription_dir)
                removed_any = True
                self.logger.info(f"Transcrição removida: {transcription_dir}")
            
            # Remover resumo
            summary_dir = self.base_path / "summaries" / video_id
            if summary_dir.exists():
                shutil.rmtree(summary_dir)
                removed_any = True
                self.logger.info(f"Resumo removido: {summary_dir}")
            
            if removed_any:
                self.logger.info(f"Vídeo {video_id} removido completamente")
            
            return removed_any
            
        except PermissionError as e:
            self.logger.error(f"Sem permissão para remover vídeo {video_id}: {str(e)}")
            raise ConfigurationError(
                "file_permissions",
                f"Sem permissão para remover dados do vídeo",
                expected="permissões de escrita",
                details={"video_id": video_id}
            )
        except Exception as e:
            self.logger.error(f"Erro ao remover vídeo {video_id}: {str(e)}")
            raise ConfigurationError(
                "video_delete_error",
                f"Erro ao remover vídeo: {str(e)}",
                expected="remoção bem-sucedida",
                details={"video_id": video_id, "error": str(e)}
            )
    
    async def video_exists(self, video_id: str) -> bool:
        """
        Verifica se um vídeo existe no storage.
        
        Args:
            video_id: ID do vídeo a ser verificado
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            video_dir = self.base_path / "videos" / video_id
            metadata_file = video_dir / "metadata.json"
            return metadata_file.exists()
        except Exception:
            return False
    
    async def get_storage_stats(self) -> Dict:
        """
        Obtém estatísticas do storage.
        
        Returns:
            Dict: Estatísticas do storage
        """
        try:
            stats = {
                "total_videos": 0,
                "videos_with_transcription": 0,
                "videos_with_summary": 0,
                "total_storage_size": 0,
                "oldest_video": None,
                "newest_video": None
            }
            
            videos_dir = self.base_path / "videos"
            if not videos_dir.exists():
                return stats
            
            video_dirs = [d for d in videos_dir.iterdir() if d.is_dir()]
            stats["total_videos"] = len(video_dirs)
            
            dates = []
            for video_dir in video_dirs:
                # Verificar transcrição
                transcription_dir = self.base_path / "transcriptions" / video_dir.name
                if transcription_dir.exists():
                    stats["videos_with_transcription"] += 1
                
                # Verificar resumo
                summary_dir = self.base_path / "summaries" / video_dir.name
                if summary_dir.exists():
                    stats["videos_with_summary"] += 1
                
                # Coletar datas
                try:
                    video = await self.load_video(video_dir.name)
                    if video and video.created_at:
                        dates.append(video.created_at)
                except Exception:
                    pass
            
            # Calcular tamanho total
            def get_dir_size(path: Path) -> int:
                total = 0
                try:
                    for item in path.rglob("*"):
                        if item.is_file():
                            total += item.stat().st_size
                except Exception:
                    pass
                return total
            
            stats["total_storage_size"] = get_dir_size(self.base_path)
            
            # Datas mais antiga e mais recente
            if dates:
                stats["oldest_video"] = min(dates)
                stats["newest_video"] = max(dates)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                "total_videos": 0,
                "videos_with_transcription": 0,
                "videos_with_summary": 0,
                "total_storage_size": 0,
                "oldest_video": None,
                "newest_video": None,
                "error": str(e)
            }
    
    async def cleanup_orphaned_data(self) -> int:
        """
        Remove dados órfãos (transcrições/resumos sem vídeo associado).
        
        Returns:
            int: Número de registros órfãos removidos
        """
        try:
            import shutil
            
            removed_count = 0
            
            # Obter lista de vídeos existentes
            videos_dir = self.base_path / "videos"
            existing_video_ids = set()
            
            if videos_dir.exists():
                existing_video_ids = {
                    d.name for d in videos_dir.iterdir() 
                    if d.is_dir() and (d / "metadata.json").exists()
                }
            
            # Verificar transcrições órfãs
            transcriptions_dir = self.base_path / "transcriptions"
            if transcriptions_dir.exists():
                for transcription_dir in transcriptions_dir.iterdir():
                    if transcription_dir.is_dir() and transcription_dir.name not in existing_video_ids:
                        shutil.rmtree(transcription_dir)
                        removed_count += 1
                        self.logger.info(f"Transcrição órfã removida: {transcription_dir.name}")
            
            # Verificar resumos órfãos
            summaries_dir = self.base_path / "summaries"
            if summaries_dir.exists():
                for summary_dir in summaries_dir.iterdir():
                    if summary_dir.is_dir() and summary_dir.name not in existing_video_ids:
                        shutil.rmtree(summary_dir)
                        removed_count += 1
                        self.logger.info(f"Resumo órfão removido: {summary_dir.name}")
            
            self.logger.info(f"Limpeza concluída: {removed_count} itens órfãos removidos")
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de dados órfãos: {str(e)}")
            raise ConfigurationError(
                "cleanup_error",
                f"Erro na limpeza: {str(e)}",
                expected="limpeza bem-sucedida",
                details={"error": str(e)}
            )
    
    async def backup_data(self, backup_path: str) -> bool:
        """
        Cria backup de todos os dados.
        
        Args:
            backup_path: Caminho onde o backup será salvo
            
        Returns:
            bool: True se backup criado com sucesso
        """
        try:
            import shutil
            import tarfile
            from pathlib import Path
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Criar arquivo tar.gz com todos os dados
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(self.base_path, arcname="alfredo_data")
            
            self.logger.info(f"Backup criado: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {str(e)}")
            raise ConfigurationError(
                "backup_error",
                f"Erro ao criar backup: {str(e)}",
                expected="backup bem-sucedido",
                details={"backup_path": backup_path, "error": str(e)}
            )
    
    async def restore_data(self, backup_path: str) -> bool:
        """
        Restaura dados de um backup.
        
        Args:
            backup_path: Caminho do arquivo de backup
            
        Returns:
            bool: True se restaurado com sucesso
        """
        try:
            import tarfile
            from pathlib import Path
            
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                raise InvalidVideoFormatError(
                    "backup_path",
                    str(backup_path),
                    "Arquivo de backup não encontrado"
                )
            
            # Criar backup dos dados atuais antes de restaurar
            current_backup = self.base_path.parent / f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            await self.backup_data(str(current_backup))
            
            # Extrair backup
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(self.base_path.parent)
            
            self.logger.info(f"Dados restaurados de: {backup_path}")
            self.logger.info(f"Backup dos dados anteriores salvo em: {current_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {str(e)}")
            raise ConfigurationError(
                "restore_error",
                f"Erro ao restaurar backup: {str(e)}",
                expected="restauração bem-sucedida",
                details={"backup_path": backup_path, "error": str(e)}
            )