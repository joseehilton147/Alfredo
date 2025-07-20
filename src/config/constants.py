"""
Constantes centralizadas do Alfredo AI.

Este módulo centraliza todas as strings constantes, números mágicos e valores
de configuração que são usados em múltiplos lugares no código.
"""

from enum import Enum


# ============================================================================
# CONSTANTES DE APLICAÇÃO
# ============================================================================

APP_NAME = "Alfredo AI"
APP_DESCRIPTION = "Sistema de transcrição e análise de vídeos usando IA"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Alfredo AI Team"

# ============================================================================
# CONSTANTES DE ARQUIVOS E DIRETÓRIOS
# ============================================================================

# Extensões de arquivo
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
AUDIO_EXTENSIONS = ['.wav', '.mp3', '.flac', '.aac', '.ogg']

# Nomes de arquivos padrão
DEFAULT_LOG_FILE = 'alfredo.log'
RESULT_METADATA_FILE = 'result.json'
TRANSCRIPTION_FILE = 'transcription.txt'
SUMMARY_FILE = 'summary.txt'

# Diretórios padrão
DEFAULT_INPUT_DIR = 'data/input'
DEFAULT_OUTPUT_DIR = 'data/output'
DEFAULT_TEMP_DIR = 'data/temp'
DEFAULT_LOGS_DIR = 'logs'
DEFAULT_CACHE_DIR = 'data/cache'

# Subdiretórios específicos
YOUTUBE_INPUT_DIR = 'data/input/youtube'
LOCAL_INPUT_DIR = 'data/input/local'
YOUTUBE_OUTPUT_DIR = 'data/output/youtube'
LOCAL_OUTPUT_DIR = 'data/output/local'

# ============================================================================
# CONSTANTES DE COMANDOS CLI
# ============================================================================

# Comandos principais
COMMAND_YOUTUBE = 'youtube'
COMMAND_LOCAL = 'local'
COMMAND_BATCH = 'batch'

# Argumentos comuns
ARG_URL = 'url'
ARG_FILE_PATH = 'file_path'
ARG_DIRECTORY = 'directory'
ARG_LANGUAGE = '--language'
ARG_LANGUAGE_SHORT = '-l'
ARG_QUALITY = '--quality'
ARG_FORCE = '--force'
ARG_RECURSIVE = '--recursive'
ARG_RECURSIVE_SHORT = '-r'
ARG_MAX_WORKERS = '--max-workers'
ARG_VERBOSE = '--verbose'
ARG_VERBOSE_SHORT = '-v'

# Valores padrão de argumentos
DEFAULT_LANGUAGE = 'pt'
DEFAULT_QUALITY = 'best'
DEFAULT_MAX_WORKERS = 3

# ============================================================================
# CONSTANTES DE MODELOS DE IA
# ============================================================================

# Modelos padrão
DEFAULT_GROQ_MODEL = 'llama-3.3-70b-versatile'
DEFAULT_OLLAMA_MODEL = 'llama3:8b'
DEFAULT_WHISPER_MODEL = 'base'
DEFAULT_MOCK_MODEL = 'mock-model-v1'

# URLs de API
DEFAULT_OLLAMA_URL = 'http://localhost:11434'

# ============================================================================
# CONSTANTES DE REDE E TIMEOUTS
# ============================================================================

# Timeouts (em segundos)
DEFAULT_DOWNLOAD_TIMEOUT = 300  # 5 minutos
DEFAULT_TRANSCRIPTION_TIMEOUT = 600  # 10 minutos
DEFAULT_API_TIMEOUT = 30
DEFAULT_RETRY_DELAY = 1.0

# Limites
MAX_RETRIES = 3
MAX_FILE_SIZE_MB = 500
MAX_VIDEO_DURATION_HOURS = 24
MAX_VIDEO_DURATION_SECONDS = MAX_VIDEO_DURATION_HOURS * 3600  # 86400

# Taxa de amostragem de áudio
DEFAULT_SAMPLE_RATE = 16000

# ============================================================================
# CONSTANTES DE VALIDAÇÃO
# ============================================================================

# Limites de texto
MAX_VIDEO_ID_LENGTH = 255
MAX_VIDEO_TITLE_LENGTH = 500
MIN_TEXT_LENGTH = 1

# Padrões de validação
VALID_ID_PATTERN = r'^[a-zA-Z0-9_-]+$'
URL_PATTERN = r'^https?://[^\s/$.?#].[^\s]*$'
YOUTUBE_URL_PATTERN = r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'

# ============================================================================
# CONSTANTES DE INTERFACE
# ============================================================================

# Estados da aplicação
STATE_MAIN_MENU = 'main_menu'
STATE_INPUT = 'input'
STATE_PROCESSING = 'processing'
STATE_RESULTS = 'results'

# Status de tarefas
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_RUNNING = 'running'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_FAILED = 'failed'

# Idiomas suportados
SUPPORTED_LANGUAGES = {
    'pt': 'Português',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano'
}

# ============================================================================
# CONSTANTES DE MENSAGENS
# ============================================================================

# Mensagens de erro
ERROR_PREFIX = '❌ '
ERROR_ALFREDO_PREFIX = '❌ Erro do Alfredo: '
ERROR_UNEXPECTED = '❌ Ocorreu um erro inesperado durante a execução'
ERROR_INTERRUPTED = '\n⚠️  Processamento interrompido pelo usuário'

# Mensagens de sucesso
SUCCESS_PREFIX = '✅ '

# Mensagens informativas
INFO_PREFIX = '💡 '
WARNING_PREFIX = '⚠️  '

# Mensagens de help
HELP_MESSAGE = """
Comandos disponíveis:
  youtube <url>     - Processa vídeos do YouTube
  local <arquivo>   - Processa arquivos de vídeo locais  
  batch <diretório> - Processa múltiplos arquivos em lote

Exemplos:
  alfredo youtube https://youtube.com/watch?v=VIDEO_ID
  alfredo local /path/to/video.mp4 --language en
  alfredo batch /path/to/videos/ --recursive
"""

HELP_SUGGESTION = "\nUse 'alfredo --help' para ver comandos disponíveis"

# ============================================================================
# CONSTANTES DE LOGGING
# ============================================================================

# Níveis de log
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'

# Formatos de log
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# CONSTANTES DE CORES E TEMAS
# ============================================================================

# Cores do tema padrão (Claude Code inspired)
COLOR_PRIMARY = '#2563eb'
COLOR_SUCCESS = '#059669'
COLOR_WARNING = '#ea580c'
COLOR_ERROR = '#dc2626'
COLOR_INFO = '#0891b2'
COLOR_MUTED = '#6b7280'
COLOR_BACKGROUND = '#f8fafc'
COLOR_SURFACE = '#ffffff'
COLOR_BORDER = '#e2e8f0'

# ============================================================================
# ENUMS
# ============================================================================

class CommandCategory(Enum):
    """Categorias de comandos CLI."""
    GENERAL = 'general'
    VIDEO = 'video'
    AUDIO = 'audio'
    BATCH = 'batch'
    SETTINGS = 'settings'


class ProcessingStatus(Enum):
    """Status de processamento."""
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    EXTRACTING = 'extracting'
    TRANSCRIBING = 'transcribing'
    SUMMARIZING = 'summarizing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class AIProvider(Enum):
    """Provedores de IA disponíveis."""
    WHISPER = 'whisper'
    GROQ = 'groq'
    OLLAMA = 'ollama'
    MOCK = 'mock'


class AudioFormat(Enum):
    """Formatos de áudio suportados."""
    WAV = 'wav'
    MP3 = 'mp3'
    FLAC = 'flac'
    AAC = 'aac'
    OGG = 'ogg'


class VideoQuality(Enum):
    """Qualidades de vídeo para download."""
    BEST = 'best'
    WORST = 'worst'
    HD720 = '720p'
    HD1080 = '1080p'
    HD1440 = '1440p'
    HD2160 = '2160p'


# ============================================================================
# CONSTANTES DE CONFIGURAÇÃO ESPECÍFICAS
# ============================================================================

# Configurações de desenvolvimento
DEV_CONFIG_KEY = 'DEBUG'
DEV_LOG_LEVEL = LOG_LEVEL_DEBUG

# Configurações de produção
PROD_LOG_LEVEL = LOG_LEVEL_INFO

# Configurações de API
API_KEY_ENV_GROQ = 'GROQ_API_KEY'
API_KEY_ENV_OPENAI = 'OPENAI_API_KEY'

# Configurações de processamento
DEFAULT_SCENE_THRESHOLD = 0.3
DEFAULT_PROGRESS_UPDATE_INTERVAL = 0.5

# ============================================================================
# CONSTANTES DE VALIDAÇÃO DE ENTRADA
# ============================================================================

# Caracteres permitidos em IDs
ALLOWED_ID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'

# Protocolos suportados
SUPPORTED_PROTOCOLS = ['http', 'https', 'ftp', 'file']

# Plataformas de vídeo suportadas
SUPPORTED_VIDEO_PLATFORMS = [
    'youtube.com',
    'youtu.be',
    'vimeo.com',
    'dailymotion.com'
]

# ============================================================================
# CONSTANTES DE SISTEMA
# ============================================================================

# Encoding padrão
DEFAULT_ENCODING = 'utf-8'
FALLBACK_ENCODING = 'ascii'

# Separadores de sistema
UNIX_PATH_SEPARATOR = '/'
WINDOWS_PATH_SEPARATOR = '\\'

# Plataformas
PLATFORM_WINDOWS = 'win32'
PLATFORM_LINUX = 'linux'
PLATFORM_MACOS = 'darwin'

# ============================================================================
# CONSTANTES DE INTERFACE DE USUÁRIO
# ============================================================================

# Símbolos e ícones
ICON_SUCCESS = '✅'
ICON_ERROR = '❌'
ICON_WARNING = '⚠️'
ICON_INFO = '💡'
ICON_PROCESSING = '🔄'
ICON_DOWNLOAD = '⬇️'
ICON_UPLOAD = '⬆️'
ICON_FILE = '📄'
ICON_FOLDER = '📁'
ICON_VIDEO = '🎥'
ICON_AUDIO = '🎧'
ICON_MUSIC = '🎵'
ICON_MICROPHONE = '🎤'

# Estilos de borda
BORDER_STYLE_ROUNDED = 'rounded'
BORDER_STYLE_SOLID = 'solid'
BORDER_STYLE_DOUBLE = 'double'

# ============================================================================
# CONSTANTES DE METADADOS
# ============================================================================

# Campos de metadados
METADATA_TITLE = 'title'
METADATA_DURATION = 'duration'
METADATA_FORMAT = 'format'
METADATA_SIZE = 'size'
METADATA_CREATED_AT = 'created_at'
METADATA_UPDATED_AT = 'updated_at'
METADATA_LANGUAGE = 'language'
METADATA_PROVIDER = 'provider'
METADATA_MODEL = 'model'

# ============================================================================
# CONSTANTES DE CACHE
# ============================================================================

# TTL do cache (em segundos)
CACHE_TTL_SHORT = 300    # 5 minutos
CACHE_TTL_MEDIUM = 3600  # 1 hora
CACHE_TTL_LONG = 86400   # 24 horas

# Tamanhos de cache
CACHE_SIZE_SMALL = 100
CACHE_SIZE_MEDIUM = 500
CACHE_SIZE_LARGE = 1000