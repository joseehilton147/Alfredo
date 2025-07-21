"""
Testes E2E para fluxo completo de processamento de vídeo local.
"""
import pytest
import tempfile
import asyncio
import os
import webbrowser

from pathlib import Path
from unittest.mock import patch, Mock

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.application.use_cases.process_local_video import (
    ProcessLocalVideoUseCase,
    ProcessLocalVideoRequest
)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_local_flow_generates_and_opens_html(tmp_path, monkeypatch):
    # Preparar configuração temporária
    base = tmp_path
    config = AlfredoConfig(
        base_dir=base,
        data_dir=base / "data",
        temp_dir=base / "temp",
        max_video_duration=3600
    )
    config.create_directory_structure()

    # Criar arquivo de vídeo dummy
    input_dir = config.data_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    video_file = input_dir / "dummy.mp4"
    video_file.write_text("fake content")

    # Mockar abertura de navegador
    with patch('webbrowser.open', new_callable=Mock) as mock_open:
        # Executar use case real
        factory = InfrastructureFactory(config)
        deps = factory.create_all_dependencies()
        use_case = ProcessLocalVideoUseCase(**deps)

        request = ProcessLocalVideoRequest(
            file_path=str(video_file),
            language="pt",
            force_reprocess=False
        )
        result = await use_case.execute(request)

    # Verificar HTML gerado
    html_path = config.data_dir / "output" / f"{result.video.id}.html"
    assert html_path.exists(), "HTML não foi gerado para vídeo local"
    content = html_path.read_text(encoding='utf-8')
    assert result.video.title in content
    assert result.video.transcription in content

    # Verificar que webbrowser.open foi chamado
    mock_open.assert_called_once()

    # Verificar limpeza de arquivos temporários
    assert not any((config.temp_dir).rglob('*')), "Arquivos temporários não foram removidos"
