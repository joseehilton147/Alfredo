# Step mínimo para isolar problema de reconhecimento
from pytest_bdd import given, then

@given("dummy step")
def dummy_step():
    print("[DEBUG] Dummy step executado")

@then("dummy result")
def dummy_result():
    print("[DEBUG] Dummy result executado")
"""Steps para validação de entidades de domínio."""
import pytest
from pytest_bdd import given, when, then, parsers
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import os

# Steps para configuração

@given("que o sistema de validação está ativo")
def sistema_validacao_ativo():
    """Confirma que o sistema de validação está funcionando."""
    print("[DEBUG] Step 'que o sistema de validação está ativo' registrado e executado")

# Steps para dados de entrada

@given("que tenho dados válidos para um vídeo")
def dados_video_validos(bdd_context):
    """Define dados válidos para criação de vídeo."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho um ID de vídeo vazio")
def id_video_vazio(bdd_context):
    """Define ID de vídeo vazio."""
    bdd_context["video_data"] = {
        "id": "",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho um ID de vídeo com mais de 255 caracteres")
def id_video_muito_longo(bdd_context):
    """Define ID de vídeo muito longo."""
    long_id = "a" * 256  # 256 caracteres
    bdd_context["video_data"] = {
        "id": long_id,
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho um ID de vídeo com caracteres especiais inválidos")
def id_video_caracteres_invalidos(bdd_context):
    """Define ID de vídeo com caracteres inválidos."""
    bdd_context["video_data"] = {
        "id": "video@#$%",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho um título de vídeo vazio")
def titulo_video_vazio(bdd_context):
    """Define título de vídeo vazio."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "",
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho um título de vídeo com mais de 500 caracteres")
def titulo_video_muito_longo(bdd_context):
    """Define título de vídeo muito longo."""
    long_title = "a" * 501  # 501 caracteres
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": long_title,
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que não tenho nem file_path válido nem URL válida")
def sem_sources_validas(bdd_context):
    """Define vídeo sem sources válidas."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "file_path": "/path/inexistente.mp4",
        "url": "url-invalida"
    }

@given("que tenho uma duração negativa para o vídeo")
def duracao_negativa(bdd_context):
    """Define duração negativa."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": -10.0,
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho uma duração maior que 24 horas")
def duracao_muito_longa(bdd_context):
    """Define duração maior que 24 horas."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 86401.0,  # 24 horas + 1 segundo
        "url": "https://youtube.com/watch?v=test123"
    }

@given("que tenho uma URL com formato inválido")
def url_formato_invalido(bdd_context):
    """Define URL com formato inválido."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "url": "not-a-valid-url"
    }

@given("que tenho um file_path que não existe")
def file_path_inexistente(bdd_context):
    """Define file_path que não existe."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "file_path": "/path/que/nao/existe.mp4"
    }

@given("que tenho um file_path válido")
def file_path_valido(bdd_context):
    """Define file_path válido (cria arquivo temporário)."""
    # Criar arquivo temporário para teste
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_file.close()
    
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "file_path": temp_file.name
    }
    
    # Adicionar à lista de arquivos temporários para limpeza
    bdd_context.setdefault("temp_files", []).append(temp_file.name)

@given("que tenho uma URL válida")
def url_valida(bdd_context):
    """Define URL válida."""
    bdd_context["video_data"] = {
        "id": "video_123",
        "title": "Vídeo de Teste",
        "duration": 120.5,
        "url": "https://youtube.com/watch?v=valid123"
    }

@given("que tenho uma configuração com timeout negativo")
def config_timeout_negativo(bdd_context):
    """Define configuração com timeout negativo."""
    bdd_context["config_data"] = {
        "download_timeout": -10
    }

@given("que configuro provider Groq sem API key")
def config_groq_sem_api_key(bdd_context):
    """Define configuração Groq sem API key."""
    bdd_context["config_data"] = {
        "default_ai_provider": "groq",
        "groq_api_key": None
    }

# Steps para ações

@when("crio uma entidade Video")
def criar_entidade_video(bdd_context):
    """Cria uma entidade Video com os dados fornecidos."""
    from src.domain.entities.video import Video
    
    try:
        video_data = bdd_context["video_data"]
        video = Video(**video_data)
        bdd_context["created_entity"] = video
        bdd_context["last_error"] = None
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["created_entity"] = None

@when("tento criar uma entidade Video")
def tentar_criar_entidade_video(bdd_context):
    """Tenta criar uma entidade Video (esperando erro)."""
    criar_entidade_video(bdd_context)

@when("tento criar AlfredoConfig")
def tentar_criar_alfredo_config(bdd_context):
    """Tenta criar AlfredoConfig com dados fornecidos."""
    from src.config.alfredo_config import AlfredoConfig
    
    try:
        config_data = bdd_context.get("config_data", {})
        
        # Criar config com dados específicos
        if "download_timeout" in config_data:
            config = AlfredoConfig(download_timeout=config_data["download_timeout"])
        else:
            config = AlfredoConfig()
        
        bdd_context["created_config"] = config
        bdd_context["last_error"] = None
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["created_config"] = None

@when("tento validar a configuração")
def tentar_validar_configuracao(bdd_context):
    """Tenta validar configuração runtime."""
    from src.config.alfredo_config import AlfredoConfig
    
    try:
        config_data = bdd_context.get("config_data", {})
        
        # Simular configuração sem API key
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=False):
            config = AlfredoConfig(
                default_ai_provider=config_data.get("default_ai_provider", "whisper"),
                groq_api_key=config_data.get("groq_api_key")
            )
            config.validate_runtime()
        
        bdd_context["created_config"] = config
        bdd_context["last_error"] = None
    except Exception as e:
        bdd_context["last_error"] = e
        bdd_context["created_config"] = None

# Steps para validação de resultados

@then("a entidade deve ser criada com sucesso")
def validar_entidade_criada_sucesso(bdd_context):
    """Valida que a entidade foi criada com sucesso."""
    assert bdd_context["last_error"] is None, f"Erro inesperado: {bdd_context['last_error']}"
    assert bdd_context["created_entity"] is not None

@then("todos os campos devem estar preenchidos corretamente")
def validar_campos_preenchidos(bdd_context):
    """Valida que todos os campos estão preenchidos corretamente."""
    entity = bdd_context["created_entity"]
    video_data = bdd_context["video_data"]
    
    assert entity.id == video_data["id"]
    assert entity.title == video_data["title"]
    assert entity.duration == video_data["duration"]
    
    if "url" in video_data:
        assert entity.url == video_data["url"]
    if "file_path" in video_data:
        assert entity.file_path == video_data["file_path"]

@then(parsers.parse('devo receber um erro de "{error_type}"'))
def validar_tipo_erro_dominio(bdd_context, error_type):
    """Valida que o tipo de erro esperado foi lançado."""
    assert bdd_context["last_error"] is not None, "Nenhum erro foi lançado"
    
    error_class_name = bdd_context["last_error"].__class__.__name__
    assert error_type in error_class_name, \
        f"Esperado erro contendo '{error_type}', mas recebeu {error_class_name}"

@then(parsers.parse('a mensagem deve indicar "{expected_message}"'))
def validar_mensagem_erro(bdd_context, expected_message):
    """Valida que a mensagem de erro contém o texto esperado."""
    assert bdd_context["last_error"] is not None
    
    error_message = str(bdd_context["last_error"])
    assert expected_message.lower() in error_message.lower(), \
        f"Mensagem '{expected_message}' não encontrada em '{error_message}'"

@then("o file_path deve estar definido")
def validar_file_path_definido(bdd_context):
    """Valida que o file_path está definido."""
    entity = bdd_context["created_entity"]
    assert entity.file_path is not None
    assert len(entity.file_path) > 0

@then("a URL deve estar definida")
def validar_url_definida(bdd_context):
    """Valida que a URL está definida."""
    entity = bdd_context["created_entity"]
    assert entity.url is not None
    assert len(entity.url) > 0