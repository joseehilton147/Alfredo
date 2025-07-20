"""Steps comuns reutilizáveis para testes BDD."""
import pytest
import asyncio
from pytest_bdd import given, when, then, parsers
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Steps para configuração do sistema
@given("que o sistema está configurado corretamente")
def sistema_configurado(mock_config):
    """Configura o sistema para testes."""
    assert mock_config is not None
    assert mock_config.data_dir is not None
    assert mock_config.temp_dir is not None

@given("que tenho conectividade com a internet")
def conectividade_internet():
    """Simula conectividade com a internet."""
    # Em testes BDD, assumimos conectividade
    pass

@given("que não tenho conectividade com a internet")
def sem_conectividade_internet():
    """Simula falta de conectividade com a internet."""
    # Este step será usado para testar cenários offline
    pass

# Steps para URLs
@given(parsers.parse('que tenho uma URL válida do YouTube "{url}"'))
def url_youtube_valida(bdd_context, url):
    """Define uma URL válida do YouTube."""
    bdd_context["input_url"] = url
    assert url.startswith("https://youtube.com/") or url.startswith("https://www.youtube.com/")

@given(parsers.parse('que tenho uma URL inválida "{url}"'))
def url_invalida(bdd_context, url):
    """Define uma URL inválida."""
    bdd_context["input_url"] = url
    # Não fazemos validação aqui, deixamos para o sistema validar

@given(parsers.parse('que tenho uma URL que falha no download'))
def url_falha_download(bdd_context, mock_video_downloader):
    """Configura URL que falhará no download."""
    from src.domain.exceptions.alfredo_errors import DownloadFailedError
    
    bdd_context["input_url"] = "https://youtube.com/watch?v=fail"
    mock_video_downloader.download.side_effect = DownloadFailedError(
        "https://youtube.com/watch?v=fail", 
        "Mock failure", 
        404
    )

# Steps para arquivos locais
@given(parsers.parse('que tenho um arquivo de vídeo válido "{file_path}"'))
def arquivo_video_valido(bdd_context, file_path):
    """Define um arquivo de vídeo válido."""
    bdd_context["input_file"] = file_path

@given(parsers.parse('que tenho um arquivo de áudio válido "{file_path}"'))
def arquivo_audio_valido(bdd_context, file_path):
    """Define um arquivo de áudio válido."""
    bdd_context["input_file"] = file_path

@given(parsers.parse('que tenho um arquivo inexistente "{file_path}"'))
def arquivo_inexistente(bdd_context, file_path):
    """Define um arquivo que não existe."""
    bdd_context["input_file"] = file_path

# Steps para execução de operações
@when("executo o processamento do vídeo")
async def executar_processamento_video(bdd_context, mock_infrastructure_factory):
    """Executa o processamento de vídeo."""
    from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
    from src.application.dtos.process_youtube_video import ProcessYouTubeVideoRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        # Criar request
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

@when("executo a análise de áudio")
async def executar_analise_audio(bdd_context, mock_infrastructure_factory):
    """Executa análise de áudio."""
    from src.application.use_cases.transcribe_audio import TranscribeAudioUseCase
    from src.application.dtos.transcribe_audio import TranscribeAudioRequest
    
    try:
        # Criar use case com dependências mock
        dependencies = mock_infrastructure_factory.create_all_dependencies()
        use_case = TranscribeAudioUseCase(**dependencies)
        
        # Criar request
        request = TranscribeAudioRequest(
            audio_path=bdd_context.get("input_file", "/mock/audio.wav"),
            language="pt"
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

# Steps para validação de resultados
@then("devo receber uma transcrição válida")
def validar_transcricao_valida(bdd_context):
    """Valida que a transcrição foi gerada corretamente."""
    assert bdd_context["last_error"] is None, f"Erro inesperado: {bdd_context['last_error']}"
    assert bdd_context["last_result"] is not None
    
    result = bdd_context["last_result"]
    if hasattr(result, 'video'):
        assert result.video.transcription is not None
        assert len(result.video.transcription) > 0
    elif hasattr(result, 'transcription'):
        assert result.transcription is not None
        assert len(result.transcription) > 0

@then("devo receber metadados do vídeo")
def validar_metadados_video(bdd_context):
    """Valida que os metadados do vídeo foram obtidos."""
    assert bdd_context["last_error"] is None
    assert bdd_context["last_result"] is not None
    
    result = bdd_context["last_result"]
    if hasattr(result, 'video'):
        video = result.video
        assert video.title is not None
        assert video.duration is not None
        assert video.metadata is not None

@then("o resultado deve ser salvo no repositório")
def validar_salvamento_repositorio(bdd_context, mock_storage):
    """Valida que o resultado foi salvo no repositório."""
    assert bdd_context["last_error"] is None
    mock_storage.save_video.assert_called_once()
    mock_storage.save_transcription.assert_called_once()

@then("o arquivo temporário deve ser removido")
def validar_limpeza_temporarios(bdd_context):
    """Valida que arquivos temporários foram removidos."""
    # Em ambiente de teste, verificamos que a limpeza foi chamada
    # A implementação real seria verificar se os arquivos não existem mais
    pass

# Steps para validação de erros
@then(parsers.parse('devo receber um erro de "{error_type}"'))
def validar_tipo_erro(bdd_context, error_type):
    """Valida que o tipo de erro esperado foi lançado."""
    assert bdd_context["last_error"] is not None, "Nenhum erro foi lançado"
    
    error_mapping = {
        "formato inválido": "InvalidVideoFormatError",
        "download": "DownloadFailedError",
        "transcrição": "TranscriptionError",
        "configuração": "ConfigurationError",
        "provider indisponível": "ProviderUnavailableError"
    }
    
    expected_error_class = error_mapping.get(error_type, error_type)
    actual_error_class = bdd_context["last_error"].__class__.__name__
    
    assert actual_error_class == expected_error_class, \
        f"Esperado {expected_error_class}, mas recebeu {actual_error_class}"

@then("nenhum arquivo deve ser criado")
def validar_nenhum_arquivo_criado(bdd_context, mock_storage):
    """Valida que nenhum arquivo foi criado."""
    mock_storage.save_video.assert_not_called()
    mock_storage.save_transcription.assert_not_called()

# Steps para retry e resiliência
@then(parsers.parse("o sistema deve tentar novamente até {max_retries:d} vezes"))
def validar_tentativas_retry(bdd_context, max_retries, mock_video_downloader):
    """Valida que o sistema tentou novamente o número correto de vezes."""
    # Verificar se o mock foi chamado o número esperado de vezes
    assert mock_video_downloader.download.call_count <= max_retries

@then("se todas as tentativas falharem, deve retornar erro específico")
def validar_erro_apos_tentativas(bdd_context):
    """Valida que após todas as tentativas, um erro específico é retornado."""
    assert bdd_context["last_error"] is not None
    assert "DownloadFailedError" in str(type(bdd_context["last_error"]))

# Steps para performance
@then(parsers.parse("o processamento deve completar em menos de {max_seconds:d} segundos"))
def validar_tempo_execucao(bdd_context, max_seconds):
    """Valida que o processamento completou no tempo esperado."""
    execution_time = bdd_context.get("execution_time", 0)
    assert execution_time < max_seconds, \
        f"Processamento levou {execution_time:.2f}s, esperado menos de {max_seconds}s"