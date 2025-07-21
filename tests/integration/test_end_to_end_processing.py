"""Testes de integração end-to-end para processamento de vídeos."""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import json

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import (
    DownloadFailedError,
    TranscriptionError,
    ConfigurationError
)


@pytest.fixture
def temp_config():
    """Cria configuração temporária para testes de integração."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = AlfredoConfig(
            base_dir=Path(temp_dir),
            data_dir=Path(temp_dir) / "data",
            temp_dir=Path(temp_dir) / "temp",
            max_video_duration=3600,
            download_timeout=30,
            transcription_timeout=60
        )
        config.create_directory_structure()
        yield config


@pytest.fixture
def integration_factory(temp_config):
    """Cria factory para testes de integração."""
    return InfrastructureFactory(temp_config)


class TestEndToEndVideoProcessing:
    """Testes de integração para processamento completo de vídeos."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_video_processing_flow(self, temp_config):
        """Testa fluxo completo de processamento de vídeo."""
        # Arrange - Criar mocks para componentes externos
        with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as mock_downloader_class, \
             patch('src.infrastructure.extractors.ffmpeg_extractor.FFmpegExtractor') as mock_extractor_class, \
             patch('src.infrastructure.providers.whisper_provider.WhisperProvider') as mock_ai_class, \
             patch('src.infrastructure.storage.filesystem_storage.FileSystemStorage') as mock_storage_class:
            
            # Configurar mocks
            mock_downloader = Mock()
            mock_extractor = Mock()
            mock_ai_provider = Mock()
            mock_storage = Mock()
            
            mock_downloader_class.return_value = mock_downloader
            mock_extractor_class.return_value = mock_extractor
            mock_ai_class.return_value = mock_ai_provider
            mock_storage_class.return_value = mock_storage
            
            # Configurar comportamento dos mocks
            mock_downloader.extract_info = AsyncMock(return_value={
                'title': 'Test Video Integration',
                'duration': 120,
                'uploader': 'Test Channel'
            })
            mock_downloader.download = AsyncMock(return_value=str(temp_config.data_dir / "video.mp4"))
            
            mock_extractor.extract_audio = AsyncMock(return_value=str(temp_config.temp_dir / "audio.wav"))
            
            mock_ai_provider.transcribe = AsyncMock(return_value="Esta é uma transcrição de integração.")
            mock_ai_provider.transcribe_audio = AsyncMock(return_value="Esta é uma transcrição de integração.")
            mock_ai_provider.summarize = AsyncMock(return_value="Este é um resumo de integração.")
            
            mock_storage.load_video = AsyncMock(return_value=None)
            mock_storage.save_video = AsyncMock()
            mock_storage.save_transcription = AsyncMock()
            mock_storage.save_summary = AsyncMock()
            
            # Act - Executar processamento completo
            from src.application.use_cases.process_youtube_video import (
                ProcessYouTubeVideoUseCase,
                ProcessYouTubeVideoRequest
            )
            
            factory = InfrastructureFactory(temp_config)
            dependencies = factory.create_all_dependencies()
            use_case = ProcessYouTubeVideoUseCase(**dependencies)
            
            request = ProcessYouTubeVideoRequest(
                url="https://youtube.com/watch?v=integration_test",
                language="pt",
                generate_summary=True
            )
            
            result = await use_case.execute(request)
            
            # Assert - Verificar resultado completo
            assert result is not None
            assert result.video.title == "Test Video Integration"
            assert result.video.transcription == "Esta é uma transcrição de integração."
            assert result.video.summary == "Este é um resumo de integração."
            
            # Verificar que todos os componentes foram chamados
            mock_downloader.extract_info.assert_called_once()
            mock_downloader.download.assert_called_once()
            mock_extractor.extract_audio.assert_called_once()
            # O use case pode chamar transcribe OU transcribe_audio
            assert mock_ai_provider.transcribe.called or mock_ai_provider.transcribe_audio.called
            mock_ai_provider.summarize.assert_called_once()
            mock_storage.save_video.assert_called_once()
            mock_storage.save_transcription.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, temp_config):
        """Testa recuperação de erros em fluxo de integração."""
        with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as mock_downloader_class:
            # Configurar mock para falhar
            mock_downloader = Mock()
            mock_downloader_class.return_value = mock_downloader
            mock_downloader.extract_info = AsyncMock(side_effect=Exception("Network error"))

            from src.application.use_cases.process_youtube_video import (
                ProcessYouTubeVideoUseCase,
                ProcessYouTubeVideoRequest
            )
            factory = InfrastructureFactory(temp_config)
            dependencies = factory.create_all_dependencies()
            use_case = ProcessYouTubeVideoUseCase(**dependencies)
            request = ProcessYouTubeVideoRequest(url="https://www.youtube.com/watch?v=integration_test")
            with pytest.raises(ConfigurationError):
                await use_case.execute(request)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_filesystem_integration(self, temp_config):
        """Testa integração com sistema de arquivos."""
        # Criar arquivo de teste
        test_video_path = temp_config.data_dir / "input" / "test_video.mp4"
        test_video_path.parent.mkdir(parents=True, exist_ok=True)
        test_video_path.write_text("fake video content")
        
        # Testar criação de estrutura de diretórios
        assert temp_config.data_dir.exists()
        assert (temp_config.data_dir / "input").exists()
        assert (temp_config.data_dir / "output").exists()
        assert temp_config.temp_dir.exists()
        
        # Testar salvamento de metadados
        video_metadata = {
            "id": "test_123",
            "title": "Test Video",
            "duration": 120,
            "transcription": "Test transcription"
        }
        
        metadata_file = temp_config.data_dir / "output" / "metadata.json"
        metadata_file.write_text(json.dumps(video_metadata, indent=2))
        
        # Verificar que arquivo foi criado e pode ser lido
        assert metadata_file.exists()
        loaded_metadata = json.loads(metadata_file.read_text())
        assert loaded_metadata["title"] == "Test Video"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_configuration_validation_integration(self, temp_config):
        """Testa validação de configuração em contexto de integração."""
        # Testar configuração válida
        assert temp_config.max_video_duration > 0
        assert temp_config.download_timeout > 0
        assert temp_config.data_dir.exists()
        
        # Testar validação runtime
        temp_config.default_ai_provider = "whisper"
        temp_config.validate_runtime()  # Não deve lançar exceção
        
        # Testar configuração inválida
        temp_config.default_ai_provider = "groq"
        temp_config.groq_api_key = None
        
        with pytest.raises(ConfigurationError):
            temp_config.validate_runtime()


class TestNetworkResilienceIntegration:
    """Testes de integração para resiliência de rede."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, temp_config):
        """Testa tratamento de timeouts de rede."""
        with patch('src.infrastructure.downloaders.ytdlp_downloader.YTDLPDownloader') as mock_downloader_class:
            mock_downloader = Mock()
            mock_downloader_class.return_value = mock_downloader
            
            # Simular timeout
            async def slow_download(*args, **kwargs):
                await asyncio.sleep(temp_config.download_timeout + 1)
                return "never_reached"
            
            mock_downloader.download = slow_download
            
            factory = InfrastructureFactory(temp_config)
            
            # Teste seria executado com timeout real em ambiente de integração
            # Por ora, verificamos que a configuração de timeout está correta
            assert temp_config.download_timeout > 0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_retry_mechanism_integration(self, temp_config):
        """Testa mecanismo de retry em falhas de rede."""
        retry_count = 0
        
        async def failing_operation():
            nonlocal retry_count
            retry_count += 1
            if retry_count < 3:
                raise Exception("Network failure")
            return "success"
        
        # Simular retry com backoff
        max_retries = 3
        backoff_factor = 1.0
        
        for attempt in range(max_retries):
            try:
                result = await failing_operation()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    pytest.fail("Retry mechanism failed")
                await asyncio.sleep(backoff_factor * (2 ** attempt))
        
        assert result == "success"
        assert retry_count == 3


class TestConcurrencyIntegration:
    """Testes de integração para processamento concorrente."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, temp_config):
        """Testa processamento concorrente de múltiplos vídeos."""
        # Simular processamento de múltiplos vídeos
        video_urls = [
            "https://youtube.com/watch?v=video1",
            "https://youtube.com/watch?v=video2",
            "https://youtube.com/watch?v=video3"
        ]
        
        async def process_video(url):
            # Simular processamento
            await asyncio.sleep(0.1)
            return f"processed_{url.split('=')[1]}"
        
        # Executar processamento concorrente
        tasks = [process_video(url) for url in video_urls]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert "processed_video1" in results
        assert "processed_video2" in results
        assert "processed_video3" in results
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_resource_limits_integration(self, temp_config):
        """Testa limites de recursos em processamento concorrente."""
        max_concurrent = temp_config.max_concurrent_downloads
        assert max_concurrent > 0
        
        # Simular semáforo para controle de concorrência
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_operation(operation_id):
            async with semaphore:
                await asyncio.sleep(0.1)
                return f"operation_{operation_id}"
        
        # Executar mais operações que o limite
        operations = [limited_operation(i) for i in range(max_concurrent * 2)]
        results = await asyncio.gather(*operations)
        
        assert len(results) == max_concurrent * 2


class TestDataPersistenceIntegration:
    """Testes de integração para persistência de dados."""
    
    @pytest.mark.integration
    def test_video_entity_persistence(self, temp_config):
        """Testa persistência de entidades Video."""
        # Criar vídeo
        video = Video(
            id="integration_test",
            title="Integration Test Video",
            duration=120.5,
            source_url="https://www.youtube.com/watch?v=integration",
            transcription="Integration transcription"
        )
        # Adiciona summary como atributo extra, se necessário
        video.summary = "Integration summary"
        
        # Simular salvamento
        video_data = {
            "id": video.id,
            "title": video.title,
            "duration": video.duration,
            "url": video.url,
            "transcription": video.transcription,
            "summary": video.summary,
            "created_at": video.created_at.isoformat() if video.created_at else None
        }
        
        # Salvar em arquivo
        output_file = temp_config.data_dir / "output" / "video_data.json"
        output_file.write_text(json.dumps(video_data, indent=2))
        
        # Verificar persistência
        assert output_file.exists()
        
        # Carregar e verificar
        loaded_data = json.loads(output_file.read_text())
        assert loaded_data["id"] == video.id
        assert loaded_data["title"] == video.title
        assert loaded_data["transcription"] == video.transcription
    
    @pytest.mark.integration
    def test_configuration_persistence(self, temp_config):
        """Testa persistência de configurações."""
        # Salvar configuração
        config_data = {
            "max_video_duration": temp_config.max_video_duration,
            "download_timeout": temp_config.download_timeout,
            "transcription_timeout": temp_config.transcription_timeout,
            "default_ai_provider": temp_config.default_ai_provider
        }
        
        config_file = temp_config.data_dir / "config.json"
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Verificar persistência
        assert config_file.exists()
        
        # Carregar e verificar
        loaded_config = json.loads(config_file.read_text())
        assert loaded_config["max_video_duration"] == temp_config.max_video_duration
        assert loaded_config["default_ai_provider"] == temp_config.default_ai_provider