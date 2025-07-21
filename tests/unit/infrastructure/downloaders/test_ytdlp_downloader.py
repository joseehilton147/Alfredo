"""Testes unitários para YTDLPDownloader."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
from pathlib import Path
import tempfile

from src.infrastructure.downloaders.ytdlp_downloader import YTDLPDownloader
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError,
    InvalidVideoFormatError,
    ConfigurationError
)


@pytest.fixture
def mock_config():
    """Configuração mock para testes."""
    config = Mock(spec=AlfredoConfig)
    config.download_timeout = 300
    config.data_dir = Path("/mock/data")
    return config


@pytest.fixture
def mock_yt_dlp():
    """Mock para yt-dlp."""
    mock_yt_dlp = Mock()
    mock_youtube_dl = Mock()
    mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
    mock_yt_dlp.YoutubeDL.return_value.__exit__.return_value = None
    mock_yt_dlp.DownloadError = Exception
    return mock_yt_dlp, mock_youtube_dl


    """Testes para inicialização do YTDLPDownloader."""

    def test_initialization_success(self, mock_config):
        """Testa inicialização bem-sucedida."""
        fake_yt_dlp = Mock()
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            assert downloader.config == mock_config
            assert downloader.yt_dlp == fake_yt_dlp
            assert downloader.logger is not None

    def test_initialization_missing_dependency(self, mock_config):
        """Testa inicialização com dependência ausente."""
        if "yt_dlp" in sys.modules:
            del sys.modules["yt_dlp"]
        with patch.dict(sys.modules, {}):
            with pytest.raises(ConfigurationError) as exc_info:
                YTDLPDownloader(mock_config)
            assert "yt_dlp_dependency" in str(exc_info.value)
            assert "yt-dlp não está instalado" in str(exc_info.value)


    """Testes para método download."""

    def test_download_success(self, mock_config):
        """Testa download bem-sucedido."""
        fake_yt_dlp = Mock()
        mock_youtube_dl = Mock()
        fake_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        fake_yt_dlp.YoutubeDL.return_value.__exit__.return_value = None
        fake_yt_dlp.DownloadError = Exception

        video_info = {
            'id': 'test_video_id',
            'title': 'Test Video',
            'duration': 120,
            'ext': 'mp4'
        }
        mock_youtube_dl.extract_info.return_value = video_info
        mock_youtube_dl.prepare_filename.return_value = "/tmp/test_video.mp4"

        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.mkdir'):
                    result = asyncio.run(downloader.download(
                        "https://youtube.com/watch?v=test",
                        "/tmp/output"
                    ))
            assert result == "/tmp/test_video.mp4"
            mock_youtube_dl.extract_info.assert_called_once()
            mock_youtube_dl.prepare_filename.assert_called_once()

    def test_download_file_not_created(self, mock_config):
        """Testa download quando arquivo não é criado."""
        fake_yt_dlp = Mock()
        mock_youtube_dl = Mock()
        fake_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        fake_yt_dlp.YoutubeDL.return_value.__exit__.return_value = None
        fake_yt_dlp.DownloadError = Exception

        video_info = {'id': 'test', 'title': 'Test'}
        mock_youtube_dl.extract_info.return_value = video_info
        mock_youtube_dl.prepare_filename.return_value = "/tmp/test_video.mp4"

        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            with patch('pathlib.Path.exists', return_value=False):
                with patch('pathlib.Path.mkdir'):
                    with pytest.raises(DownloadFailedError):
                        asyncio.run(downloader.download(
                            "https://youtube.com/watch?v=test",
                            "/tmp/output"
                        ))
    # Repita o padrão acima para todos os outros métodos de teste nesta classe, removendo o uso de @patch e _setup_yt_dlp_mock, criando o mock do módulo yt_dlp diretamente e usando patch.dict.
        mock_youtube_dl.prepare_filename.return_value = "/tmp/test_video.mp4"
        
        downloader = YTDLPDownloader(mock_config)
        
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.mkdir'):
                # Act & Assert
                with pytest.raises(DownloadFailedError) as exc_info:
                    asyncio.run(downloader.download(
                        "https://youtube.com/watch?v=test",
                        "/tmp/output"
                    ))
                
                assert "Arquivo não foi criado após download" in str(exc_info.value)
    
    @patch('src.infrastructure.downloaders.ytdlp_downloader.yt_dlp')
    def test_download_private_video(self, mock_yt_dlp_module, mock_config):
        """Testa download de vídeo privado."""
        # Arrange
        mock_yt_dlp, mock_youtube_dl = self._setup_yt_dlp_mock(mock_yt_dlp_module)
        
        mock_youtube_dl.extract_info.side_effect = Exception("Video is private")
        
        downloader = YTDLPDownloader(mock_config)
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(DownloadFailedError) as exc_info:
                asyncio.run(downloader.download(
                    "https://youtube.com/watch?v=private",
                    "/tmp/output"
                ))
            
            assert "Vídeo privado ou restrito" in str(exc_info.value)
    
    @patch('src.infrastructure.downloaders.ytdlp_downloader.yt_dlp')
    def test_download_not_available(self, mock_yt_dlp_module, mock_config):
        """Testa download de vídeo não disponível."""
        # Arrange
        mock_yt_dlp, mock_youtube_dl = self._setup_yt_dlp_mock(mock_yt_dlp_module)
        
        mock_youtube_dl.extract_info.side_effect = Exception("Video not available")
        
        downloader = YTDLPDownloader(mock_config)
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(DownloadFailedError) as exc_info:
                asyncio.run(downloader.download(
                    "https://youtube.com/watch?v=unavailable",
                    "/tmp/output"
                ))
            
            assert "Vídeo não disponível" in str(exc_info.value)
    
    @patch('src.infrastructure.downloaders.ytdlp_downloader.yt_dlp')
    def test_download_copyright_blocked(self, mock_yt_dlp_module, mock_config):
        """Testa download de vídeo bloqueado por copyright."""
        # Arrange
        mock_yt_dlp, mock_youtube_dl = self._setup_yt_dlp_mock(mock_yt_dlp_module)
        
        mock_youtube_dl.extract_info.side_effect = Exception("Copyright blocked")
        
        downloader = YTDLPDownloader(mock_config)
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(DownloadFailedError) as exc_info:
                asyncio.run(downloader.download(
                    "https://youtube.com/watch?v=blocked",
                    "/tmp/output"
                ))
            
            assert "Vídeo bloqueado por direitos autorais" in str(exc_info.value)
    
    @patch('src.infrastructure.downloaders.ytdlp_downloader.yt_dlp')
    def test_download_generic_error(self, mock_yt_dlp_module, mock_config):
        """Testa download com erro genérico."""
        # Arrange
        mock_yt_dlp, mock_youtube_dl = self._setup_yt_dlp_mock(mock_yt_dlp_module)
        
        mock_youtube_dl.extract_info.side_effect = Exception("Generic error")
        
        downloader = YTDLPDownloader(mock_config)
        
        with patch('pathlib.Path.mkdir'):
            # Act & Assert
            with pytest.raises(DownloadFailedError) as exc_info:
                asyncio.run(downloader.download(
                    "https://youtube.com/watch?v=error",
                    "/tmp/output"
                ))
            
            assert "Erro no download: Generic error" in str(exc_info.value)
    
    def _setup_yt_dlp_mock(self, mock_yt_dlp_module):
        """Configura mock do yt-dlp."""
        mock_youtube_dl = Mock()
        mock_yt_dlp_module.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        mock_yt_dlp_module.YoutubeDL.return_value.__exit__.return_value = None
        mock_yt_dlp_module.DownloadError = Exception
        return mock_yt_dlp_module, mock_youtube_dl


class TestYTDLPDownloaderExtractInfo:
    """Testes para método extract_info."""
    
    def test_extract_info_success(self, mock_config):
        """Testa extração de informações bem-sucedida."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        video_info = {
            'id': 'test_video_id',
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'duration': 120,
            'description': 'Test description',
            'upload_date': '20240101',
            'view_count': 1000,
            'webpage_url': 'https://youtube.com/watch?v=test'
        }
        mock_youtube_dl.extract_info.return_value = video_info
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            result = asyncio.run(downloader.extract_info("https://youtube.com/watch?v=test"))
            assert result['id'] == 'test_video_id'
            assert result['title'] == 'Test Video'
            assert result['uploader'] == 'Test Channel'
            assert result['duration'] == 120
            assert result['description'] == 'Test description'
            assert result['upload_date'] == '20240101'
            assert result['view_count'] == 1000
            assert result['webpage_url'] == 'https://youtube.com/watch?v=test'
    
    def test_extract_info_missing_fields(self, mock_config):
        """Testa extração com campos ausentes."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        video_info = {'id': 'test_video_id'}
        mock_youtube_dl.extract_info.return_value = video_info
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            result = asyncio.run(downloader.extract_info("https://youtube.com/watch?v=test"))
            assert result['id'] == 'test_video_id'
            assert result['title'] == 'Unknown Title'
            assert result['uploader'] == 'Unknown'
            assert result['duration'] == 0
            assert result['description'] == ''
            assert result['upload_date'] == ''
            assert result['view_count'] == 0
    
    def test_extract_info_private_video(self, mock_config):
        """Testa extração de vídeo privado."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        mock_youtube_dl.extract_info.side_effect = Exception("Video is private")
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                asyncio.run(downloader.extract_info("https://youtube.com/watch?v=private"))
            assert "Vídeo privado ou restrito" in str(exc_info.value)
    
    def test_extract_info_not_available(self, mock_config):
        """Testa extração de vídeo não disponível."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        mock_youtube_dl.extract_info.side_effect = Exception("Video not available")
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                asyncio.run(downloader.extract_info("https://youtube.com/watch?v=unavailable"))
            assert "Vídeo não disponível" in str(exc_info.value)
    
    def test_extract_info_generic_error(self, mock_config):
        """Testa extração com erro genérico."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        mock_youtube_dl.extract_info.side_effect = Exception("Generic error")
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                asyncio.run(downloader.extract_info("https://youtube.com/watch?v=error"))
            assert "URL inválida: Generic error" in str(exc_info.value)
    
    def _setup_yt_dlp_mock(self, mock_yt_dlp_module):
        """Configura mock do yt-dlp."""
        mock_youtube_dl = Mock()
        mock_yt_dlp_module.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        mock_yt_dlp_module.YoutubeDL.return_value.__exit__.return_value = None
        mock_yt_dlp_module.DownloadError = Exception
        return mock_yt_dlp_module, mock_youtube_dl


class TestYTDLPDownloaderFormats:
    """Testes para métodos relacionados a formatos."""
    
    def test_get_available_formats(self, mock_config):
        """Testa obtenção de formatos disponíveis."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        video_info = {
            'formats': [
                {
                    'format_id': 'best',
                    'ext': 'mp4',
                    'quality': 'high',
                    'filesize': 1000000,
                    'vcodec': 'h264',
                    'acodec': 'aac',
                    'format_note': 'best quality'
                },
                {
                    'format_id': 'worst',
                    'ext': 'webm',
                    'quality': 'low',
                    'filesize': 500000,
                    'vcodec': 'vp9',
                    'acodec': 'opus',
                    'format_note': 'worst quality'
                }
            ]
        }
        # O método get_available_formats chama extract_info, que por sua vez chama mock_youtube_dl.extract_info
        # Precisamos garantir que o mock de extract_info retorne o dicionário correto
        mock_youtube_dl.extract_info.return_value = video_info
        # Também precisamos garantir que o método extract_info do downloader retorne o dicionário correto
        # Para isso, vamos mockar o método extract_info da instância do downloader
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            # Mockar o método extract_info do downloader para retornar o dicionário com 'formats'
            from unittest.mock import AsyncMock
            downloader.extract_info = AsyncMock(return_value=video_info)
            result = asyncio.run(downloader.get_available_formats("https://youtube.com/watch?v=test"))
            assert len(result) == 2
            assert result[0]['format_id'] == 'best'
            assert result[0]['ext'] == 'mp4'
            assert result[1]['format_id'] == 'worst'
            assert result[1]['ext'] == 'webm'
    
    def test_get_format_selector(self, mock_config):
        """Testa seletor de formato."""
        fake_yt_dlp = Mock()
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            assert downloader._get_format_selector("best") == "best[ext=mp4]/best"
            assert downloader._get_format_selector("worst") == "worst[ext=mp4]/worst"
            assert downloader._get_format_selector("720p") == "best[height<=720][ext=mp4]/best[height<=720]"
            assert downloader._get_format_selector("480p") == "best[height<=480][ext=mp4]/best[height<=480]"
            assert downloader._get_format_selector("360p") == "best[height<=360][ext=mp4]/best[height<=360]"
            assert downloader._get_format_selector("unknown") == "best[ext=mp4]/best"
    
    def _setup_yt_dlp_mock(self, mock_yt_dlp_module):
        """Configura mock do yt-dlp."""
        mock_youtube_dl = Mock()
        mock_yt_dlp_module.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        mock_yt_dlp_module.YoutubeDL.return_value.__exit__.return_value = None
        mock_yt_dlp_module.DownloadError = Exception
        return mock_yt_dlp_module, mock_youtube_dl


class TestYTDLPDownloaderUtilities:
    """Testes para métodos utilitários."""
    
    def test_is_url_supported_true(self, mock_config):
        """Testa URL suportada."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        video_info = {'id': 'test', 'title': 'Test'}
        mock_youtube_dl.extract_info.return_value = video_info
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            result = asyncio.run(downloader.is_url_supported("https://youtube.com/watch?v=test"))
            assert result is True
    
    def test_is_url_supported_false(self, mock_config):
        """Testa URL não suportada."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        mock_youtube_dl.extract_info.side_effect = Exception("Not supported")
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            result = asyncio.run(downloader.is_url_supported("https://unsupported.com/video"))
            assert result is False
    
    def test_get_video_id_success(self, mock_config):
        """Testa extração de ID do vídeo."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        video_info = {'id': 'test_video_123'}
        mock_youtube_dl.extract_info.return_value = video_info
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            result = asyncio.run(downloader.get_video_id("https://youtube.com/watch?v=test"))
            assert result == 'test_video_123'
    
    def test_get_video_id_error(self, mock_config):
        """Testa extração de ID com erro."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        mock_youtube_dl.extract_info.side_effect = Exception("Error extracting ID")
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
        with pytest.raises(InvalidVideoFormatError) as exc_info:
            asyncio.run(downloader.get_video_id("https://youtube.com/watch?v=error"))
        # A mensagem de erro personalizada inclui prefixos, então basta garantir que o erro original está presente
        assert "Error extracting ID" in str(exc_info.value)
    
    def _setup_yt_dlp_mock(self, mock_yt_dlp_module):
        """Configura mock do yt-dlp."""
        mock_youtube_dl = Mock()
        mock_yt_dlp_module.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        mock_yt_dlp_module.YoutubeDL.return_value.__exit__.return_value = None
        mock_yt_dlp_module.DownloadError = Exception
        return mock_yt_dlp_module, mock_youtube_dl


class TestYTDLPDownloaderIntegration:
    """Testes de integração para YTDLPDownloader."""
    
    def test_full_download_workflow(self, mock_config):
        """Testa fluxo completo de download."""
        from unittest.mock import MagicMock, Mock
        fake_yt_dlp = Mock()
        mock_youtube_dl = MagicMock()
        fake_yt_dlp.YoutubeDL.return_value = MagicMock(__enter__=MagicMock(return_value=mock_youtube_dl), __exit__=MagicMock(return_value=None))
        fake_yt_dlp.DownloadError = Exception
        video_info = {
            'id': 'test_video_id',
            'title': 'Test Video',
            'duration': 120,
            'ext': 'mp4'
        }
        mock_youtube_dl.extract_info.return_value = video_info
        mock_youtube_dl.prepare_filename.return_value = "/tmp/test_video.mp4"
        with patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}):
            downloader = YTDLPDownloader(mock_config)
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.mkdir') as mock_mkdir:
                    result = asyncio.run(downloader.download(
                        "https://youtube.com/watch?v=test",
                        "/tmp/output",
                        quality="720p"
                    ))
            assert result == "/tmp/test_video.mp4"
            mock_mkdir.assert_called_once()
            mock_youtube_dl.extract_info.assert_called_once()
    
    def _setup_yt_dlp_mock(self, mock_yt_dlp_module):
        """Configura mock do yt-dlp."""
        mock_youtube_dl = Mock()
        mock_yt_dlp_module.YoutubeDL.return_value.__enter__.return_value = mock_youtube_dl
        mock_yt_dlp_module.YoutubeDL.return_value.__exit__.return_value = None
        mock_yt_dlp_module.DownloadError = Exception
        return mock_yt_dlp_module, mock_youtube_dl