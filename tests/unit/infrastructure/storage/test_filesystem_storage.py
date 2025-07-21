"""Testes unitários para FileSystemStorage."""

import pytest
import asyncio
import json
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.infrastructure.storage.filesystem_storage import FileSystemStorage
from src.config.alfredo_config import AlfredoConfig
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    ConfigurationError,
    InvalidVideoFormatError
)


@pytest.fixture
def temp_dir():
    """Diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config(temp_dir):
    """Configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.data_dir = temp_dir
    return config


@pytest.fixture
def sample_video():
    """Vídeo de exemplo para testes."""
    return Video(
        id="test_video_123",
        title="Vídeo de Teste",
        duration=120.5,
        file_path="/path/to/test_video.mp4",
        url="https://youtube.com/watch?v=test123",
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )


@pytest.fixture
def sample_local_video(temp_dir):
    """Vídeo local de exemplo para testes."""
    video_file = temp_dir / "test_video.mp4"
    video_file.write_text("fake video content")
    
    return Video(
        id="local_video_123",
        title="Vídeo Local de Teste",
        duration=90.0,
        file_path=str(video_file),
        created_at=datetime(2024, 1, 2, 14, 30, 0)
    )


class TestFileSystemStorageInitialization:
    """Testes para inicialização do FileSystemStorage."""
    
    def test_initialization_success(self, mock_config, temp_dir):
        """Testa inicialização bem-sucedida."""
        storage = FileSystemStorage(mock_config)
        
        assert storage.config == mock_config
        assert storage.base_path == temp_dir / "output"
        assert storage.logger is not None
        
        # Verificar que diretórios foram criados
        assert (temp_dir / "output").exists()
        assert (temp_dir / "output" / "videos").exists()
        assert (temp_dir / "output" / "transcriptions").exists()
        assert (temp_dir / "output" / "summaries").exists()
    
    def test_initialization_creates_directories(self, mock_config, temp_dir):
        """Testa que inicialização cria diretórios necessários."""
        # Garantir que diretórios não existem
        output_dir = temp_dir / "output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        storage = FileSystemStorage(mock_config)
        
        # Verificar que todos os diretórios foram criados
        assert output_dir.exists()
        assert (output_dir / "videos").exists()
        assert (output_dir / "transcriptions").exists()
        assert (output_dir / "summaries").exists()
    
    @patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied"))
    def test_initialization_permission_error(self, mock_mkdir, mock_config):
        """Testa inicialização com erro de permissão."""
        with pytest.raises(ConfigurationError) as exc_info:
            FileSystemStorage(mock_config)
        
        assert "directory_creation" in str(exc_info.value)
        assert "Sem permissão para criar" in str(exc_info.value)


class TestFileSystemStorageVideoOperations:
    """Testes para operações com vídeos."""
    
    def test_save_video_success(self, mock_config, sample_video):
        """Testa salvamento de vídeo bem-sucedido."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        asyncio.run(storage.save_video(sample_video))
        
        # Assert
        video_dir = storage.base_path / "videos" / sample_video.id
        metadata_file = video_dir / "metadata.json"
        
        assert video_dir.exists()
        assert metadata_file.exists()
        
        # Verificar conteúdo do arquivo
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["id"] == sample_video.id
        assert data["title"] == sample_video.title
        assert data["duration"] == sample_video.duration
        assert data["file_path"] == sample_video.file_path
        assert data["url"] == sample_video.url
        assert data["created_at"] == "2024-01-01T12:00:00"
    
    def test_save_video_with_metadata(self, mock_config, temp_dir):
        """Testa salvamento de vídeo com metadados."""
        # Criar arquivo temporário para o teste
        video_file = temp_dir / "video_with_metadata.mp4"
        video_file.write_text("fake video content")
        
        video = Video(
            id="video_with_metadata",
            title="Vídeo com Metadados",
            duration=180.0,
            file_path=str(video_file),
            metadata={"format": "mp4", "resolution": "1920x1080"}
        )
        
        storage = FileSystemStorage(mock_config)
        
        # Act
        asyncio.run(storage.save_video(video))
        
        # Assert
        metadata_file = storage.base_path / "videos" / video.id / "metadata.json"
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["metadata"]["format"] == "mp4"
        assert data["metadata"]["resolution"] == "1920x1080"
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_video_permission_error(self, mock_open, mock_config, sample_video):
        """Testa salvamento com erro de permissão."""
        storage = FileSystemStorage(mock_config)
        
        with pytest.raises(ConfigurationError) as exc_info:
            asyncio.run(storage.save_video(sample_video))
        
        assert "file_permissions" in str(exc_info.value)
        assert "Sem permissão para escrever" in str(exc_info.value)
    
    def test_load_video_success(self, mock_config, sample_video):
        """Testa carregamento de vídeo bem-sucedido."""
        storage = FileSystemStorage(mock_config)
        
        # Primeiro salvar o vídeo
        asyncio.run(storage.save_video(sample_video))
        
        # Act
        loaded_video = asyncio.run(storage.load_video(sample_video.id))
        
        # Assert
        assert loaded_video is not None
        assert loaded_video.id == sample_video.id
        assert loaded_video.title == sample_video.title
        assert loaded_video.duration == sample_video.duration
        assert loaded_video.file_path == sample_video.file_path
        assert loaded_video.created_at == sample_video.created_at
    
    def test_load_video_not_found(self, mock_config):
        """Testa carregamento de vídeo não encontrado."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        loaded_video = asyncio.run(storage.load_video("non_existent_video"))
        
        # Assert
        assert loaded_video is None
    
    def test_load_video_corrupted_metadata(self, mock_config, sample_video):
        """Testa carregamento com metadados corrompidos."""
        storage = FileSystemStorage(mock_config)
        
        # Criar arquivo com JSON inválido
        video_dir = storage.base_path / "videos" / sample_video.id
        video_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = video_dir / "metadata.json"
        
        with open(metadata_file, 'w') as f:
            f.write("invalid json content")
        
        # Act & Assert
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(storage.load_video(sample_video.id))
        
        assert "Arquivo de metadados corrompido" in str(exc_info.value)
    
    def test_video_exists_true(self, mock_config, sample_video):
        """Testa verificação de existência de vídeo (verdadeiro)."""
        storage = FileSystemStorage(mock_config)
        
        # Salvar vídeo primeiro
        asyncio.run(storage.save_video(sample_video))
        
        # Act
        exists = asyncio.run(storage.video_exists(sample_video.id))
        
        # Assert
        assert exists is True
    
    def test_video_exists_false(self, mock_config):
        """Testa verificação de existência de vídeo (falso)."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        exists = asyncio.run(storage.video_exists("non_existent_video"))
        
        # Assert
        assert exists is False
    
    def test_delete_video_success(self, mock_config, sample_video):
        """Testa remoção de vídeo bem-sucedida."""
        storage = FileSystemStorage(mock_config)
        
        # Salvar vídeo, transcrição e resumo
        asyncio.run(storage.save_video(sample_video))
        asyncio.run(storage.save_transcription(sample_video.id, "Transcrição de teste"))
        asyncio.run(storage.save_summary(sample_video.id, "Resumo de teste"))
        
        # Verificar que existem
        assert asyncio.run(storage.video_exists(sample_video.id))
        
        # Act
        result = asyncio.run(storage.delete_video(sample_video.id))
        
        # Assert
        assert result is True
        assert not asyncio.run(storage.video_exists(sample_video.id))
        
        # Verificar que todos os diretórios foram removidos
        video_dir = storage.base_path / "videos" / sample_video.id
        transcription_dir = storage.base_path / "transcriptions" / sample_video.id
        summary_dir = storage.base_path / "summaries" / sample_video.id
        
        assert not video_dir.exists()
        assert not transcription_dir.exists()
        assert not summary_dir.exists()
    
    def test_delete_video_not_found(self, mock_config):
        """Testa remoção de vídeo não encontrado."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        result = asyncio.run(storage.delete_video("non_existent_video"))
        
        # Assert
        assert result is False


class TestFileSystemStorageTranscriptionOperations:
    """Testes para operações com transcrições."""
    
    def test_save_transcription_success(self, mock_config):
        """Testa salvamento de transcrição bem-sucedido."""
        storage = FileSystemStorage(mock_config)
        video_id = "test_video_123"
        transcription = "Esta é uma transcrição de teste."
        metadata = {"provider": "whisper", "language": "pt"}
        
        # Act
        asyncio.run(storage.save_transcription(video_id, transcription, metadata))
        
        # Assert
        transcription_dir = storage.base_path / "transcriptions" / video_id
        transcription_file = transcription_dir / "transcription.txt"
        metadata_file = transcription_dir / "metadata.json"
        
        assert transcription_dir.exists()
        assert transcription_file.exists()
        assert metadata_file.exists()
        
        # Verificar conteúdo
        with open(transcription_file, 'r', encoding='utf-8') as f:
            saved_transcription = f.read()
        assert saved_transcription == transcription
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            saved_metadata = json.load(f)
        assert saved_metadata["provider"] == "whisper"
        assert saved_metadata["language"] == "pt"
        assert saved_metadata["video_id"] == video_id
        assert saved_metadata["transcription_length"] == len(transcription)
        assert "created_at" in saved_metadata
    
    def test_save_transcription_without_metadata(self, mock_config):
        """Testa salvamento de transcrição sem metadados."""
        storage = FileSystemStorage(mock_config)
        video_id = "test_video_456"
        transcription = "Transcrição sem metadados."
        
        # Act
        asyncio.run(storage.save_transcription(video_id, transcription))
        
        # Assert
        transcription_file = storage.base_path / "transcriptions" / video_id / "transcription.txt"
        metadata_file = storage.base_path / "transcriptions" / video_id / "metadata.json"
        
        assert transcription_file.exists()
        assert not metadata_file.exists()  # Não deve criar arquivo de metadados
    
    def test_load_transcription_success(self, mock_config):
        """Testa carregamento de transcrição bem-sucedido."""
        storage = FileSystemStorage(mock_config)
        video_id = "test_video_789"
        transcription = "Transcrição para carregamento."
        
        # Salvar primeiro
        asyncio.run(storage.save_transcription(video_id, transcription))
        
        # Act
        loaded_transcription = asyncio.run(storage.load_transcription(video_id))
        
        # Assert
        assert loaded_transcription == transcription
    
    def test_load_transcription_not_found(self, mock_config):
        """Testa carregamento de transcrição não encontrada."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        loaded_transcription = asyncio.run(storage.load_transcription("non_existent_video"))
        
        # Assert
        assert loaded_transcription is None
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_transcription_permission_error(self, mock_open, mock_config):
        """Testa salvamento de transcrição com erro de permissão."""
        storage = FileSystemStorage(mock_config)
        
        with pytest.raises(ConfigurationError) as exc_info:
            asyncio.run(storage.save_transcription("test_video", "transcription"))
        
        assert "file_permissions" in str(exc_info.value)


class TestFileSystemStorageSummaryOperations:
    """Testes para operações com resumos."""
    
    def test_save_summary_success(self, mock_config):
        """Testa salvamento de resumo bem-sucedido."""
        storage = FileSystemStorage(mock_config)
        video_id = "test_video_summary"
        summary = "Este é um resumo de teste."
        metadata = {"provider": "groq", "model": "llama-3.3-70b"}
        
        # Act
        asyncio.run(storage.save_summary(video_id, summary, metadata))
        
        # Assert
        summary_dir = storage.base_path / "summaries" / video_id
        summary_file = summary_dir / "summary.txt"
        metadata_file = summary_dir / "metadata.json"
        
        assert summary_dir.exists()
        assert summary_file.exists()
        assert metadata_file.exists()
        
        # Verificar conteúdo
        with open(summary_file, 'r', encoding='utf-8') as f:
            saved_summary = f.read()
        assert saved_summary == summary
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            saved_metadata = json.load(f)
        assert saved_metadata["provider"] == "groq"
        assert saved_metadata["model"] == "llama-3.3-70b"
        assert saved_metadata["video_id"] == video_id
        assert saved_metadata["summary_length"] == len(summary)
    
    def test_load_summary_success(self, mock_config):
        """Testa carregamento de resumo bem-sucedido."""
        storage = FileSystemStorage(mock_config)
        video_id = "test_video_load_summary"
        summary = "Resumo para carregamento."
        
        # Salvar primeiro
        asyncio.run(storage.save_summary(video_id, summary))
        
        # Act
        loaded_summary = asyncio.run(storage.load_summary(video_id))
        
        # Assert
        assert loaded_summary == summary
    
    def test_load_summary_not_found(self, mock_config):
        """Testa carregamento de resumo não encontrado."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        loaded_summary = asyncio.run(storage.load_summary("non_existent_video"))
        
        # Assert
        assert loaded_summary is None


class TestFileSystemStorageListOperations:
    """Testes para operações de listagem."""
    
    def test_list_videos_empty(self, mock_config):
        """Testa listagem de vídeos vazia."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        videos = asyncio.run(storage.list_videos())
        
        # Assert
        assert videos == []
    
    def test_list_videos_with_data(self, mock_config, sample_video, sample_local_video):
        """Testa listagem de vídeos com dados."""
        storage = FileSystemStorage(mock_config)
        
        # Salvar vídeos
        asyncio.run(storage.save_video(sample_video))
        asyncio.run(storage.save_video(sample_local_video))
        
        # Act
        videos = asyncio.run(storage.list_videos())
        
        # Assert
        assert len(videos) == 2
        video_ids = [v.id for v in videos]
        assert sample_video.id in video_ids
        assert sample_local_video.id in video_ids
    
    def test_list_videos_with_limit(self, mock_config):
        """Testa listagem de vídeos com limite."""
        storage = FileSystemStorage(mock_config)
        
        # Criar múltiplos vídeos
        for i in range(5):
            video = Video(
                id=f"video_{i}",
                title=f"Vídeo {i}",
                duration=60.0,
                file_path=f"/path/to/video_{i}.mp4"
            )
            asyncio.run(storage.save_video(video))
        
        # Act
        videos = asyncio.run(storage.list_videos(limit=3))
        
        # Assert
        assert len(videos) == 3
    
    def test_list_videos_with_offset(self, mock_config):
        """Testa listagem de vídeos com offset."""
        storage = FileSystemStorage(mock_config)
        
        # Criar múltiplos vídeos
        for i in range(5):
            video = Video(
                id=f"video_{i}",
                title=f"Vídeo {i}",
                duration=60.0,
                file_path=f"/path/to/video_{i}.mp4"
            )
            asyncio.run(storage.save_video(video))
        
        # Act
        videos = asyncio.run(storage.list_videos(limit=2, offset=2))
        
        # Assert
        assert len(videos) == 2
    
    def test_list_videos_with_filters(self, mock_config):
        """Testa listagem de vídeos com filtros."""
        storage = FileSystemStorage(mock_config)
        
        # Criar vídeos com diferentes características
        video1 = Video(id="v1", title="Video 1", duration=60.0, file_path="/local/video1.mp4")
        video2 = Video(id="v2", title="Video 2", duration=120.0, url="https://youtube.com/watch?v=test")
        
        asyncio.run(storage.save_video(video1))
        asyncio.run(storage.save_video(video2))
        
        # Adicionar transcrição apenas ao primeiro
        asyncio.run(storage.save_transcription("v1", "Transcrição do vídeo 1"))
        
        # Act - Filtrar por vídeos com transcrição
        videos_with_transcription = asyncio.run(storage.list_videos(
            filter_by={"has_transcription": True}
        ))
        
        # Assert
        assert len(videos_with_transcription) == 0  # Nenhum vídeo tem transcrição no objeto Video
    
    def test_list_videos_sorting(self, mock_config):
        """Testa listagem de vídeos com ordenação."""
        storage = FileSystemStorage(mock_config)
        
        # Criar vídeos com diferentes durações
        video1 = Video(id="v1", title="Video A", duration=30.0, file_path="/path/v1.mp4")
        video2 = Video(id="v2", title="Video B", duration=60.0, file_path="/path/v2.mp4")
        video3 = Video(id="v3", title="Video C", duration=45.0, file_path="/path/v3.mp4")
        
        for video in [video1, video2, video3]:
            asyncio.run(storage.save_video(video))
        
        # Act - Ordenar por duração (crescente)
        videos_asc = asyncio.run(storage.list_videos(sort_by="duration", sort_order="asc"))
        
        # Assert
        durations = [v.duration for v in videos_asc]
        assert durations == [30.0, 45.0, 60.0]
        
        # Act - Ordenar por título (decrescente)
        videos_desc = asyncio.run(storage.list_videos(sort_by="title", sort_order="desc"))
        
        # Assert
        titles = [v.title for v in videos_desc]
        assert titles == ["Video C", "Video B", "Video A"]


class TestFileSystemStorageStatistics:
    """Testes para estatísticas do storage."""
    
    def test_get_storage_stats_empty(self, mock_config):
        """Testa estatísticas com storage vazio."""
        storage = FileSystemStorage(mock_config)
        
        # Act
        stats = asyncio.run(storage.get_storage_stats())
        
        # Assert
        assert stats["total_videos"] == 0
        assert stats["videos_with_transcription"] == 0
        assert stats["videos_with_summary"] == 0
        assert stats["total_storage_size"] >= 0
        assert stats["oldest_video"] is None
        assert stats["newest_video"] is None
    
    def test_get_storage_stats_with_data(self, mock_config, sample_video):
        """Testa estatísticas com dados."""
        storage = FileSystemStorage(mock_config)
        
        # Adicionar dados
        asyncio.run(storage.save_video(sample_video))
        asyncio.run(storage.save_transcription(sample_video.id, "Transcrição"))
        asyncio.run(storage.save_summary(sample_video.id, "Resumo"))
        
        # Act
        stats = asyncio.run(storage.get_storage_stats())
        
        # Assert
        assert stats["total_videos"] == 1
        assert stats["videos_with_transcription"] == 1
        assert stats["videos_with_summary"] == 1
        assert stats["total_storage_size"] > 0
        assert stats["oldest_video"] == sample_video.created_at
        assert stats["newest_video"] == sample_video.created_at


class TestFileSystemStorageCleanup:
    """Testes para operações de limpeza."""
    
    def test_cleanup_orphaned_data(self, mock_config, sample_video):
        """Testa limpeza de dados órfãos."""
        storage = FileSystemStorage(mock_config)
        
        # Criar dados órfãos (transcrição e resumo sem vídeo)
        orphan_id = "orphan_video"
        asyncio.run(storage.save_transcription(orphan_id, "Transcrição órfã"))
        asyncio.run(storage.save_summary(orphan_id, "Resumo órfão"))
        
        # Criar vídeo válido com dados
        asyncio.run(storage.save_video(sample_video))
        asyncio.run(storage.save_transcription(sample_video.id, "Transcrição válida"))
        
        # Act
        removed_count = asyncio.run(storage.cleanup_orphaned_data())
        
        # Assert
        assert removed_count == 2  # Transcrição e resumo órfãos
        
        # Verificar que dados órfãos foram removidos
        orphan_transcription_dir = storage.base_path / "transcriptions" / orphan_id
        orphan_summary_dir = storage.base_path / "summaries" / orphan_id
        assert not orphan_transcription_dir.exists()
        assert not orphan_summary_dir.exists()
        
        # Verificar que dados válidos permanecem
        valid_transcription_dir = storage.base_path / "transcriptions" / sample_video.id
        assert valid_transcription_dir.exists()
    
    def test_backup_data(self, mock_config, sample_video, temp_dir):
        """Testa criação de backup."""
        storage = FileSystemStorage(mock_config)
        
        # Adicionar alguns dados
        asyncio.run(storage.save_video(sample_video))
        asyncio.run(storage.save_transcription(sample_video.id, "Transcrição para backup"))
        
        backup_path = temp_dir / "backup.tar.gz"
        
        # Act
        result = asyncio.run(storage.backup_data(str(backup_path)))
        
        # Assert
        assert result is True
        assert backup_path.exists()
        assert backup_path.stat().st_size > 0
    
    def test_restore_data(self, mock_config, sample_video, temp_dir):
        """Testa restauração de backup."""
        storage = FileSystemStorage(mock_config)
        
        # Criar dados e backup
        asyncio.run(storage.save_video(sample_video))
        backup_path = temp_dir / "backup.tar.gz"
        asyncio.run(storage.backup_data(str(backup_path)))
        
        # Limpar dados atuais
        shutil.rmtree(storage.base_path)
        storage._ensure_directories()
        
        # Act
        result = asyncio.run(storage.restore_data(str(backup_path)))
        
        # Assert
        assert result is True
        
        # Verificar que dados foram restaurados
        restored_video = asyncio.run(storage.load_video(sample_video.id))
        assert restored_video is not None
        assert restored_video.id == sample_video.id


class TestFileSystemStorageErrorHandling:
    """Testes para tratamento de erros."""
    
    @patch('pathlib.Path.mkdir', side_effect=OSError("Disk full"))
    def test_save_video_disk_full(self, mock_mkdir, mock_config, sample_video):
        """Testa salvamento com disco cheio."""
        storage = FileSystemStorage(mock_config)
        
        with pytest.raises(ConfigurationError) as exc_info:
            asyncio.run(storage.save_video(sample_video))
        
        assert "storage_space" in str(exc_info.value)
    
    def test_backup_invalid_path(self, mock_config):
        """Testa backup com caminho inválido."""
        storage = FileSystemStorage(mock_config)
        invalid_path = "/invalid/path/backup.tar.gz"
        
        with pytest.raises(ConfigurationError) as exc_info:
            asyncio.run(storage.backup_data(invalid_path))
        
        assert "backup_error" in str(exc_info.value)
    
    def test_restore_backup_not_found(self, mock_config):
        """Testa restauração com backup não encontrado."""
        storage = FileSystemStorage(mock_config)
        non_existent_backup = "/non/existent/backup.tar.gz"
        
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(storage.restore_data(non_existent_backup))
        
        assert "Arquivo de backup não encontrado" in str(exc_info.value)