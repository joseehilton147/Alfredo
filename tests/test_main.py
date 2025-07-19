import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from src.main import (
    setup_logging,
    create_directories,
    process_single_video,
    process_batch,
    download_youtube_video,
    main
)


class TestSetupLogging:
    def test_setup_logging_verbose_false(self):
        """Testa configuração de logging sem verbose."""
        with patch('src.main.logging') as mock_logging:
            setup_logging(verbose=False)
            mock_logging.basicConfig.assert_called_once()

    def test_setup_logging_verbose_true(self):
        """Testa configuração de logging com verbose."""
        with patch('src.main.logging') as mock_logging:
            setup_logging(verbose=True)
            mock_logging.basicConfig.assert_called_once()


class TestCreateDirectories:
    def test_create_directories_success(self):
        """Testa criação de diretórios."""
        with patch('src.main.Path') as mock_path:
            mock_path.return_value.mkdir = MagicMock()
            create_directories()
            assert mock_path.call_count >= 5


class TestProcessSingleVideo:
    @pytest.mark.asyncio
    async def test_process_single_video_success(self):
        """Testa processamento de vídeo único com sucesso."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'dummy video content')
            tmp_path = tmp.name

        try:
            with patch('src.main.Video') as mock_video, \
                 patch('src.main.JsonVideoRepository') as mock_repo, \
                 patch('src.main.WhisperProvider') as mock_provider, \
                 patch('src.main.TranscribeAudioUseCase') as mock_use_case, \
                 patch('src.main.logging') as mock_logging:

                mock_video_instance = MagicMock()
                mock_video_instance.id = "test_video"
                mock_video.return_value = mock_video_instance

                mock_repo_instance = AsyncMock()
                mock_repo.return_value = mock_repo_instance

                mock_use_case_instance = AsyncMock()
                mock_use_case_instance.execute.return_value = MagicMock(
                    transcription="Test transcription"
                )
                mock_use_case.return_value = mock_use_case_instance

                await process_single_video(tmp_path, "pt")

                mock_video.assert_called_once()
                mock_repo_instance.save.assert_called_once()
                mock_use_case_instance.execute.assert_called_once()

        finally:
            os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_process_single_video_error(self):
        """Testa tratamento de erro no processamento de vídeo."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'dummy video content')
            tmp_path = tmp.name

        try:
            with patch('src.main.Video') as mock_video, \
                 patch('src.main.logging') as mock_logging:

                mock_video.side_effect = Exception("Test error")

                with pytest.raises(Exception):
                    await process_single_video(tmp_path, "pt")

        finally:
            os.unlink(tmp_path)


class TestProcessBatch:
    @pytest.mark.asyncio
    async def test_process_batch_empty_directory(self):
        """Testa processamento de diretório vazio."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('src.main.logging') as mock_logging:
                await process_batch(tmp_dir, "pt")

    @pytest.mark.asyncio
    async def test_process_batch_nonexistent_directory(self):
        """Testa processamento de diretório inexistente."""
        with patch('src.main.logging') as mock_logging:
            await process_batch("/nonexistent/path", "pt")

    @pytest.mark.asyncio
    async def test_process_batch_with_videos(self):
        """Testa processamento de diretório com vídeos."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_files = ["video1.mp4", "video2.avi", "test.txt"]
            for filename in video_files:
                Path(tmp_dir, filename).touch()

            with patch('src.main.process_single_video') as mock_process, \
                 patch('src.main.logging') as mock_logging:

                mock_process.return_value = None
                await process_batch(tmp_dir, "pt")
                assert mock_process.call_count == 2


class TestDownloadYoutubeVideo:
    @pytest.mark.asyncio
    async def test_download_youtube_video_success(self):
        """Testa download de vídeo do YouTube com sucesso."""
class TestDownloadYoutubeVideo:
    @pytest.mark.asyncio
    async def test_download_youtube_video_success(self):
        """Testa download de vídeo do YouTube com sucesso."""
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {"title": "test_video"}
            mock_ydl_instance.prepare_filename.return_value = "/path/to/video.mp4"
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            result = await download_youtube_video("https://youtube.com/watch?v=test")
            assert result == "/path/to/video.mp4"

    @pytest.mark.asyncio
    async def test_download_youtube_video_import_error(self):
        """Testa erro quando yt-dlp não está instalado."""
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'yt_dlp':
                raise ImportError("No module named 'yt_dlp'")
            return real_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ImportError) as exc_info:
                await download_youtube_video("https://youtube.com/watch?v=test")
            assert "yt-dlp não está instalado" in str(exc_info.value)


class TestMain:
    @pytest.mark.asyncio
    async def test_main_no_arguments(self):
        """Testa execução sem argumentos."""
        test_args = ["main.py"]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging') as mock_setup, \
             patch('src.main.create_directories') as mock_create, \
             patch('src.main.logging') as mock_logging:

            await main()
            mock_setup.assert_called_once()
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_with_input_file(self):
        """Testa execução com arquivo de entrada."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'dummy video content')
            tmp_path = tmp.name

        try:
            test_args = ["main.py", "--input", tmp_path, "--verbose"]

            with patch('sys.argv', test_args), \
                 patch('src.main.setup_logging') as mock_setup, \
                 patch('src.main.create_directories') as mock_create, \
                 patch('src.main.process_single_video') as mock_process, \
                 patch('src.main.logging') as mock_logging:

                await main()
                mock_setup.assert_called_once_with(True)
                mock_create.assert_called_once()
                mock_process.assert_called_once_with(tmp_path, "pt")

        finally:
            os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_main_with_url(self):
        """Testa execução com URL do YouTube."""
        test_args = ["main.py", "--url", "https://youtube.com/watch?v=test"]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging') as mock_setup, \
             patch('src.main.create_directories') as mock_create, \
             patch('src.main.download_youtube_video') as mock_download, \
             patch('src.main.process_single_video') as mock_process, \
             patch('src.main.logging') as mock_logging:

            mock_download.return_value = "/path/to/downloaded.mp4"

            await main()
            mock_setup.assert_called_once_with(False)
            mock_create.assert_called_once()
            mock_download.assert_called_once_with("https://youtube.com/watch?v=test")
            mock_process.assert_called_once_with("/path/to/downloaded.mp4", "pt")

    @pytest.mark.asyncio
    async def test_main_with_batch(self):
        """Testa execução com processamento em lote."""
        test_args = ["main.py", "--batch", "/test/dir", "--language", "en"]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging') as mock_setup, \
             patch('src.main.create_directories') as mock_create, \
             patch('src.main.process_batch') as mock_batch, \
             patch('src.main.logging') as mock_logging:

            await main()
            mock_setup.assert_called_once_with(False)
            mock_create.assert_called_once()
            mock_batch.assert_called_once_with("/test/dir", "en")

    @pytest.mark.asyncio
    async def test_main_keyboard_interrupt(self):
        """Testa interrupção por teclado."""
        test_args = ["main.py", "--input", "/test/path.mp4"]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging'), \
             patch('src.main.create_directories'), \
             patch('src.main.process_single_video') as mock_process, \
             patch('src.main.logging') as mock_logging:

            mock_process.side_effect = KeyboardInterrupt()

            await main()

    @pytest.mark.asyncio
    async def test_main_general_exception(self):
        """Testa tratamento de exceção geral."""
        test_args = ["main.py", "--input", "/test/path.mp4"]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging'), \
             patch('src.main.create_directories'), \
             patch('src.main.process_single_video') as mock_process, \
             patch('src.main.logging') as mock_logging, \
             patch('sys.exit') as mock_exit:

            mock_process.side_effect = Exception("Test error")

            await main()
            mock_exit.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_main_with_all_options(self):
        """Testa execução com todas as opções."""
        test_args = [
            "main.py",
            "--input", "/test/path.mp4",
            "--language", "en",
            "--output", "/custom/output",
            "--detect-scenes",
            "--verbose"
        ]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging') as mock_setup, \
             patch('src.main.create_directories') as mock_create, \
             patch('src.main.process_single_video') as mock_process, \
             patch('src.main.logging') as mock_logging:

            await main()
            mock_setup.assert_called_once_with(True)
            mock_create.assert_called_once()
            mock_process.assert_called_once_with("/test/path.mp4", "en")


class TestDownloadYoutubeVideoExtended:
    @pytest.mark.asyncio
    async def test_download_youtube_video_with_custom_output(self):
        """Testa download com diretório customizado."""
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = {"title": "test_video"}
            mock_ydl_instance.prepare_filename.return_value = "/custom/path/test_video.mp4"
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            result = await download_youtube_video(
                "https://youtube.com/watch?v=test",
                output_dir="/custom/path"
            )
            assert result == "/custom/path/test_video.mp4"


class TestProcessBatchExtended:
    @pytest.mark.asyncio
    async def test_process_batch_with_error_in_single_video(self):
        """Testa processamento em lote com erro em um vídeo."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_files = ["video1.mp4", "video2.avi"]
            for filename in video_files:
                Path(tmp_dir, filename).touch()

            with patch('src.main.process_single_video') as mock_process, \
                 patch('src.main.logging') as mock_logging:

                mock_process.side_effect = [Exception("Error processing video1"), None]
                await process_batch(tmp_dir, "pt")
                assert mock_process.call_count == 2


# Teste para argumentos de linha de comando
class TestArgumentParsing:
    @pytest.mark.asyncio
    async def test_argument_parser_help(self):
        """Testa se o parser mostra ajuda quando não há argumentos."""
        test_args = ["main.py"]

        with patch('sys.argv', test_args), \
             patch('src.main.setup_logging'), \
             patch('src.main.create_directories'), \
             patch('src.main.argparse.ArgumentParser.print_help') as mock_help, \
             patch('src.main.logging') as mock_logging:

            await main()
            mock_help.assert_called_once()
