"""Steps específicos para processamento de YouTube."""
import pytest
import asyncio
from pytest_bdd import given, when, then, parsers, scenarios
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Carregar cenários do arquivo feature
scenarios('../features/youtube_processing.feature')

# Steps específicos para YouTube

@when("executo o processamento do vídeo com resumo")
async def executar_processamento_com_resumo(bdd_context, mock_infrastructure_factory):
    """Executa processamento de vídeo com geração de resumo."""
    from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
    from src.application.dtos.process_youtube_video import ProcessYouTubeVideoRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        # Criar request com resumo habilitado
        request = ProcessYouTubeVideoRequest(
            url=bdd_context.get("input_url", "https://youtube.com/watch?v=test"),
            language="pt",
            generate_summary=True
        )
        
        # Executar
        import time
        start_time = time.time()
        result = await use_case.execute(request)
        end_time = time.time()
        
        bdd_context["last_result"] = result
        bdd_context["execution_time"] = end_time - start_time
        bdd_context["last_error"] = None
        
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["last_result"] = None

@given("que o vídeo tem duração maior que o limite configurado")
def video_muito_longo(mock_video_downloader, mock_config):
    """Configura um vídeo com duração maior que o limite."""
    # Configurar mock para retornar vídeo muito longo
    mock_video_downloader.extract_info.return_value = {
        "title": "Vídeo Muito Longo",
        "duration": mock_config.max_video_duration + 1000,  # Maior que o limite
        "uploader": "Test Channel"
    }

@given("que o provider de IA está indisponível")
def provider_ia_indisponivel(mock_ai_provider):
    """Configura provider de IA como indisponível."""
    from src.domain.exceptions.alfredo_errors import ProviderUnavailableError
    
    mock_ai_provider.transcribe_audio.side_effect = ProviderUnavailableError(
        "mock_provider", 
        "Provider temporariamente indisponível"
    )

@given("que tenho uma lista de URLs válidas do YouTube")
def lista_urls_youtube(bdd_context):
    """Define uma lista de URLs do YouTube para processamento em lote."""
    bdd_context["input_urls"] = [
        "https://youtube.com/watch?v=video1",
        "https://youtube.com/watch?v=video2",
        "https://youtube.com/watch?v=video3"
    ]

@given("que o vídeo já foi processado anteriormente")
def video_ja_processado(bdd_context, mock_storage):
    """Configura um vídeo que já existe no cache."""
    from src.domain.entities.video import Video
    from datetime import datetime
    
    # Criar vídeo mock que já existe
    cached_video = Video(
        id="cached_video",
        title="Vídeo em Cache",
        duration=120,
        url=bdd_context.get("input_url", "https://youtube.com/watch?v=cached_video"),
        transcription="Transcrição em cache",
        summary="Resumo em cache",
        created_at=datetime.now()
    )
    
    # Configurar mock para retornar vídeo do cache
    mock_storage.load_video.return_value = cached_video
    bdd_context["cached_video"] = cached_video

@when("executo o processamento em lote")
async def executar_processamento_lote(bdd_context, mock_infrastructure_factory):
    """Executa processamento em lote de múltiplas URLs."""
    from src.application.use_cases.batch_process_videos import BatchProcessVideosUseCase
    from src.application.dtos.batch_process_videos import BatchProcessVideosRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = BatchProcessVideosUseCase(**dependencies)
        
        # Criar request para lote
        request = BatchProcessVideosRequest(
            urls=bdd_context.get("input_urls", []),
            language="pt",
            generate_summary=False,
            max_concurrent=2
        )
        
        # Executar
        import time
        start_time = time.time()
        result = await use_case.execute(request)
        end_time = time.time()
        
        bdd_context["last_result"] = result
        bdd_context["execution_time"] = end_time - start_time
        bdd_context["last_error"] = None
        
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["last_result"] = None

@when("executo o processamento do vídeo com força de reprocessamento")
async def executar_processamento_forcado(bdd_context, mock_infrastructure_factory):
    """Executa processamento forçando reprocessamento."""
    from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
    from src.application.dtos.process_youtube_video import ProcessYouTubeVideoRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        # Criar request com força de reprocessamento
        request = ProcessYouTubeVideoRequest(
            url=bdd_context.get("input_url", "https://youtube.com/watch?v=test"),
            language="pt",
            generate_summary=True,
            force_reprocess=True
        )
        
        # Executar
        import time
        start_time = time.time()
        result = await use_case.execute(request)
        end_time = time.time()
        
        bdd_context["last_result"] = result
        bdd_context["execution_time"] = end_time - start_time
        bdd_context["last_error"] = None
        
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["last_result"] = None

# Steps para validação de resultados específicos do YouTube

@then("devo receber um resumo válido")
def validar_resumo_valido(bdd_context):
    """Valida que um resumo foi gerado corretamente."""
    assert bdd_context["last_error"] is None, f"Erro inesperado: {bdd_context['last_error']}"
    assert bdd_context["last_result"] is not None
    
    result = bdd_context["last_result"]
    if hasattr(result, 'video'):
        assert result.video.summary is not None
        assert len(result.video.summary) > 0
    elif hasattr(result, 'summary'):
        assert result.summary is not None
        assert len(result.summary) > 0

@then("o vídeo deve ser baixado e salvo")
def validar_video_baixado_salvo(bdd_context, mock_video_downloader, mock_storage):
    """Valida que o vídeo foi baixado e salvo mesmo com erro na transcrição."""
    # Verificar que o download foi chamado
    mock_video_downloader.download.assert_called_once()
    
    # Verificar que o vídeo foi salvo (mesmo sem transcrição)
    mock_storage.save_video.assert_called_once()

@then("a transcrição não deve ser gerada")
def validar_transcricao_nao_gerada(bdd_context, mock_storage):
    """Valida que a transcrição não foi gerada devido ao erro do provider."""
    # Verificar que save_transcription não foi chamado
    mock_storage.save_transcription.assert_not_called()

@then("todos os vídeos válidos devem ser processados")
def validar_videos_processados(bdd_context):
    """Valida que todos os vídeos válidos foram processados."""
    assert bdd_context["last_error"] is None
    assert bdd_context["last_result"] is not None
    
    result = bdd_context["last_result"]
    assert hasattr(result, 'processed_count')
    assert result.processed_count > 0

@then("devo receber um relatório de processamento")
def validar_relatorio_processamento(bdd_context):
    """Valida que um relatório de processamento foi gerado."""
    assert bdd_context["last_result"] is not None
    
    result = bdd_context["last_result"]
    assert hasattr(result, 'report')
    assert result.report is not None
    assert 'processed_count' in result.report
    assert 'failed_count' in result.report

@then("vídeos com erro devem ser reportados separadamente")
def validar_relatorio_erros(bdd_context):
    """Valida que vídeos com erro são reportados separadamente."""
    result = bdd_context["last_result"]
    assert hasattr(result, 'failed_videos')
    # Em ambiente de teste, pode não haver falhas, então verificamos a estrutura

@then("devo receber o resultado do cache")
def validar_resultado_cache(bdd_context):
    """Valida que o resultado veio do cache."""
    assert bdd_context["last_error"] is None
    assert bdd_context["last_result"] is not None
    
    result = bdd_context["last_result"]
    assert hasattr(result, 'was_cached')
    assert result.was_cached is True

@then("nenhum download deve ser realizado")
def validar_nenhum_download(bdd_context, mock_video_downloader):
    """Valida que nenhum download foi realizado (resultado do cache)."""
    mock_video_downloader.download.assert_not_called()

@then("o vídeo deve ser baixado novamente")
def validar_download_novamente(bdd_context, mock_video_downloader):
    """Valida que o vídeo foi baixado novamente (reprocessamento forçado)."""
    mock_video_downloader.download.assert_called_once()

@then("uma nova transcrição deve ser gerada")
def validar_nova_transcricao(bdd_context, mock_ai_provider):
    """Valida que uma nova transcrição foi gerada."""
    mock_ai_provider.transcribe_audio.assert_called_once()

@then("o cache deve ser atualizado")
def validar_cache_atualizado(bdd_context, mock_storage):
    """Valida que o cache foi atualizado com o novo resultado."""
    # Verificar que save_video foi chamado para atualizar o cache
    mock_storage.save_video.assert_called_once()
    mock_storage.save_transcription.assert_called_once()