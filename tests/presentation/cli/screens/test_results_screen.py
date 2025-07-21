"""Tests for the results screen of the interactive CLI."""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add src to path to allow imports
from src.presentation.cli.screens.results_screen import (
    ResultsScreen,
    TranscriptionResult,
)


@pytest.fixture
def mock_cli():
    """Fixture for a mocked CLI application."""
    cli = MagicMock()
    cli.keyboard.read_key = AsyncMock()
    cli.update_live_display = MagicMock()
    return cli


@pytest.fixture
def mock_transcription_result(tmp_path):
    """Fixture for a mocked transcription result."""
    result_dir = tmp_path / "result1"
    result_dir.mkdir()
    (result_dir / "result.json").write_text(json.dumps({
        "title": "Test Video",
        "created_at": "2023-10-27T10:00:00Z",
        "language": "en",
        "file_path": "/path/to/video.mp4",
        "duration": 60.0
    }))
    (result_dir / "transcription.txt").write_text("This is a test transcription.")
    return TranscriptionResult(result_dir)


@pytest.mark.asyncio
async def test_results_screen_empty_state(mock_cli):
    """Test that the results screen shows an empty state message."""
    with patch("pathlib.Path.iterdir", return_value=[]):
        screen = ResultsScreen(mock_cli)
        await screen.on_enter()
        await screen.render()
        
        # Check that the empty state message is displayed
        mock_cli.update_live_display.assert_called_once()
        renderable = mock_cli.update_live_display.call_args[0][0]
        assert "Nenhuma transcrição encontrada" in str(renderable.renderable.renderables[0].text)


@pytest.mark.asyncio
async def test_results_screen_list_results(mock_cli, mock_transcription_result):
    """Test that the results screen lists transcription results."""
    with patch("pathlib.Path.iterdir", return_value=[mock_transcription_result.result_dir]):
        screen = ResultsScreen(mock_cli)
        await screen.on_enter()
        await screen.render()
        
        # Check that the result is listed in the table
        mock_cli.update_live_display.assert_called_once()
        renderable = mock_cli.update_live_display.call_args[0][0]
        assert "Test Video" in str(renderable.renderable.renderables[0])


@pytest.mark.asyncio
async def test_results_screen_navigation(mock_cli, mock_transcription_result):
    """Test navigation in the results screen."""
    results = [mock_transcription_result, mock_transcription_result]
    with patch("pathlib.Path.iterdir", return_value=[r.result_dir for r in results]):
        screen = ResultsScreen(mock_cli)
        await screen.on_enter()
        
        # Test navigation down
        await screen.handle_input("down")
        assert screen.selected_index == 1
        
        # Test navigation up
        await screen.handle_input("up")
        assert screen.selected_index == 0


@pytest.mark.asyncio
async def test_results_screen_preview(mock_cli, mock_transcription_result):
    """Test the preview mode of the results screen."""
    with patch("pathlib.Path.iterdir", return_value=[mock_transcription_result.result_dir]):
        screen = ResultsScreen(mock_cli)
        await screen.on_enter()
        
        # Enter preview mode
        await screen.handle_input("enter")
        assert screen.view_mode == "preview"
        
        # Check that the preview is rendered
        await screen.render()
        mock_cli.update_live_display.assert_called()
        renderable = mock_cli.update_live_display.call_args[0][0]
        assert "Preview da Transcrição" in str(renderable.renderable.renderables[0])


@pytest.mark.asyncio
async def test_results_screen_full_view(mock_cli, mock_transcription_result):
    """Test the full view mode of the results screen."""
    with patch("pathlib.Path.iterdir", return_value=[mock_transcription_result.result_dir]):
        screen = ResultsScreen(mock_cli)
        await screen.on_enter()
        
        # Enter full view mode
        await screen.handle_input("v")
        assert screen.view_mode == "full_view"
        
        # Check that the full view is rendered
        await screen.render()
        mock_cli.update_live_display.assert_called()
        renderable = mock_cli.update_live_display.call_args[0][0]
        assert "Transcrição Completa" in str(renderable.renderable.renderables[0])


@pytest.mark.asyncio
async def test_results_screen_export(mock_cli, mock_transcription_result, tmp_path):
    """Test exporting a transcription result."""
    with patch("pathlib.Path.iterdir", return_value=[mock_transcription_result.result_dir]):
        screen = ResultsScreen(mock_cli)
        await screen.on_enter()
        
        # Export the result
        with patch("presentation.cli.screens.results_screen.Path.mkdir") as mock_mkdir:
            await screen.handle_input("e")
            # Check that the export directory is created
            mock_mkdir.assert_called_with(exist_ok=True)


@pytest.mark.asyncio
async def test_results_screen_delete(mock_cli, mock_transcription_result):
    """Test deleting a transcription result."""
    with patch("pathlib.Path.iterdir", return_value=[mock_transcription_result.result_dir]):
        with patch("shutil.rmtree") as mock_rmtree:
            screen = ResultsScreen(mock_cli)
            await screen.on_enter()
            
            # Delete the result
            await screen.handle_input("delete")
            await screen.handle_input("y")
            
            # Check that the result directory is removed
            mock_rmtree.assert_called_with(mock_transcription_result.result_dir)
