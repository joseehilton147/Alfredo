"""Testes para JsonVideoRepository."""
import pytest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.infrastructure.repositories.json_video_repository import JsonVideoRepository
from src.domain.entities.video import Video


class TestJsonVideoRepository:
    """Testes para o repositório JSON de vídeos."""

    @pytest.fixture
    def temp_dir(self):
        """Cria um diretório temporário para testes."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def repository(self, temp_dir):
        """Cria uma instância do repositório para testes."""
        return JsonVideoRepository(temp_dir)

    @pytest.fixture
    def sample_video(self):
        """Cria um vídeo de exemplo para testes."""
        return Video(
            id="test_video_123",
            title="Vídeo de Teste",
            file_path="/path/to/video.mp4",
            duration=120.0,
            metadata={"quality": "HD", "source": "local"}
        )

    def test_init_default_path(self):
        """Testa inicialização com caminho padrão."""
        with patch('pathlib.Path.mkdir'):
            repo = JsonVideoRepository()
            assert repo.base_path == Path("data/output")

    def test_init_custom_path(self, temp_dir):
        """Testa inicialização com caminho customizado."""
        repo = JsonVideoRepository(temp_dir)
        assert repo.base_path == Path(temp_dir)
        assert repo.base_path.exists()

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Testa busca de vídeo inexistente."""
        result = await repository.find_by_id("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_and_find_video(self, repository, sample_video):
        """Testa salvar e buscar vídeo."""
        # Salvar vídeo
        await repository.save(sample_video)
        
        # Verificar se o diretório foi criado
        video_dir = repository.base_path / sample_video.id
        assert video_dir.exists()
        
        # Verificar se o arquivo de metadados foi criado
        metadata_file = video_dir / "metadata.json"
        assert metadata_file.exists()
        
        # Buscar vídeo
        found_video = await repository.find_by_id(sample_video.id)
        assert found_video is not None
        assert found_video.id == sample_video.id
        assert found_video.title == sample_video.title
        assert found_video.file_path == sample_video.file_path
        assert found_video.duration == sample_video.duration
        assert found_video.metadata == sample_video.metadata

    @pytest.mark.asyncio
    async def test_save_video_with_none_created_at(self, repository):
        """Testa salvar vídeo com created_at None."""
        video = Video(
            id="test_none_date",
            title="Test Video",
            created_at=None
        )
        
        await repository.save(video)
        found_video = await repository.find_by_id(video.id)
        assert found_video is not None

    @pytest.mark.asyncio
    async def test_find_by_id_corrupted_json(self, repository, sample_video):
        """Testa busca com arquivo JSON corrompido."""
        # Salvar vídeo primeiro
        await repository.save(sample_video)
        
        # Corromper o arquivo JSON
        metadata_file = repository.base_path / sample_video.id / "metadata.json"
        with open(metadata_file, "w") as f:
            f.write("invalid json content")
        
        # Tentar buscar vídeo
        result = await repository.find_by_id(sample_video.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_save_error_handling(self, repository):
        """Testa tratamento de erro ao salvar."""
        video = Video(id="test", title="Test")
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(OSError):
                await repository.save(video)

    @pytest.mark.asyncio
    async def test_delete_existing_video(self, repository, sample_video):
        """Testa remoção de vídeo existente."""
        # Salvar vídeo primeiro
        await repository.save(sample_video)
        
        # Verificar que existe
        assert (repository.base_path / sample_video.id).exists()
        
        # Remover vídeo
        result = await repository.delete(sample_video.id)
        assert result is True
        
        # Verificar que foi removido
        assert not (repository.base_path / sample_video.id).exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_video(self, repository):
        """Testa remoção de vídeo inexistente."""
        result = await repository.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_error_handling(self, repository, sample_video):
        """Testa tratamento de erro ao remover."""
        # Salvar vídeo primeiro
        await repository.save(sample_video)
        
        with patch('shutil.rmtree', side_effect=OSError("Permission denied")):
            result = await repository.delete(sample_video.id)
            assert result is False

    @pytest.mark.asyncio
    async def test_list_all_empty(self, repository):
        """Testa listagem de repositório vazio."""
        videos = await repository.list_all()
        assert videos == []

    @pytest.mark.asyncio
    async def test_list_all_with_videos(self, repository):
        """Testa listagem com vídeos."""
        # Criar alguns vídeos
        video1 = Video(id="video1", title="Video 1")
        video2 = Video(id="video2", title="Video 2")
        video3 = Video(id="video3", title="Video 3")
        
        await repository.save(video1)
        await repository.save(video2)
        await repository.save(video3)
        
        # Listar todos
        videos = await repository.list_all()
        assert len(videos) == 3
        
        video_ids = [v.id for v in videos]
        assert "video1" in video_ids
        assert "video2" in video_ids
        assert "video3" in video_ids

    @pytest.mark.asyncio
    async def test_list_all_with_non_video_directories(self, repository):
        """Testa listagem ignorando diretórios sem vídeos."""
        # Criar vídeo válido
        video1 = Video(id="valid_video", title="Valid Video")
        await repository.save(video1)
        
        # Criar diretório sem metadata.json
        invalid_dir = repository.base_path / "invalid_dir"
        invalid_dir.mkdir()
        
        # Criar arquivo (não diretório)
        (repository.base_path / "not_a_dir.txt").touch()
        
        videos = await repository.list_all()
        assert len(videos) == 1
        assert videos[0].id == "valid_video"

    @pytest.mark.asyncio
    async def test_list_all_error_handling(self, repository):
        """Testa tratamento de erro ao listar."""
        with patch('pathlib.Path.iterdir', side_effect=OSError("Permission denied")):
            videos = await repository.list_all()
            assert videos == []

    @pytest.mark.asyncio
    async def test_find_by_id_invalid_datetime(self, repository, sample_video):
        """Testa busca com datetime inválido no JSON."""
        # Salvar vídeo primeiro
        await repository.save(sample_video)
        
        # Modificar arquivo para ter datetime inválido
        metadata_file = repository.base_path / sample_video.id / "metadata.json"
        with open(metadata_file, "r") as f:
            data = json.load(f)
        
        data["created_at"] = "invalid-datetime"
        
        with open(metadata_file, "w") as f:
            json.dump(data, f)
        
        # Buscar vídeo - deve retornar None devido ao erro
        result = await repository.find_by_id(sample_video.id)
        assert result is None
