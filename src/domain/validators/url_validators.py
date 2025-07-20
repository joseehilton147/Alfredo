"""
Validadores específicos para URLs e fontes externas.

Este módulo contém funções de validação para URLs de vídeo,
incluindo validação de formato e detecção de plataformas suportadas.
"""

import re
from typing import Optional
from urllib.parse import urlparse

from ..exceptions.alfredo_errors import InvalidVideoFormatError


def validate_url_format(url: str) -> None:
    """
    Valida o formato básico de uma URL.
    
    Regras:
    - Deve começar com http:// ou https://
    - Deve ter domínio válido
    - Deve ter estrutura de URL válida
    
    Args:
        url: URL a ser validada
        
    Raises:
        InvalidVideoFormatError: Se a URL não tiver formato válido
    """
    if not url or not url.strip():
        raise InvalidVideoFormatError(
            field="url",
            value=url,
            constraint="não pode ser vazia"
        )
    
    # Verificar se começa com protocolo válido
    if not url.startswith(('http://', 'https://')):
        raise InvalidVideoFormatError(
            field="url",
            value=url,
            constraint="deve começar com http:// ou https://"
        )
    
    # Usar urlparse para validação mais robusta
    try:
        parsed = urlparse(url)
        
        # Verificar se tem domínio
        if not parsed.netloc:
            raise InvalidVideoFormatError(
                field="url",
                value=url,
                constraint="deve ter domínio válido"
            )
        
        # Verificar formato do domínio usando regex
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        
        if not domain_pattern.match(parsed.netloc.split(':')[0]):  # Remove porta se houver
            raise InvalidVideoFormatError(
                field="url",
                value=url,
                constraint="domínio tem formato inválido",
                details={"domain": parsed.netloc}
            )
            
    except Exception as e:
        if isinstance(e, InvalidVideoFormatError):
            raise
        
        raise InvalidVideoFormatError(
            field="url",
            value=url,
            constraint="formato de URL inválido",
            details={"parse_error": str(e)}
        )


def is_youtube_url(url: str) -> bool:
    """
    Verifica se uma URL é do YouTube.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for URL do YouTube, False caso contrário
    """
    if not url:
        return False
    
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch',
        r'(?:https?://)?(?:www\.)?youtu\.be/',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/',
        r'(?:https?://)?(?:www\.)?youtube\.com/?$',  # Homepage do YouTube
    ]
    
    for pattern in youtube_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    return False


def is_supported_video_url(url: str) -> bool:
    """
    Verifica se uma URL é de uma plataforma de vídeo suportada.
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for de plataforma suportada, False caso contrário
    """
    if not url:
        return False
    
    # Por enquanto, apenas YouTube é suportado
    # Pode ser expandido para outras plataformas no futuro
    supported_platforms = [
        r'(?:https?://)?(?:www\.)?youtube\.com/',
        r'(?:https?://)?(?:www\.)?youtu\.be/',
        # Adicionar outras plataformas conforme necessário:
        # r'(?:https?://)?(?:www\.)?vimeo\.com/',
        # r'(?:https?://)?(?:www\.)?dailymotion\.com/',
    ]
    
    for pattern in supported_platforms:
        if re.match(pattern, url, re.IGNORECASE):
            return True
    
    return False


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    Extrai o ID do vídeo de uma URL do YouTube.
    
    Args:
        url: URL do YouTube
        
    Returns:
        ID do vídeo se encontrado, None caso contrário
    """
    if not is_youtube_url(url):
        return None
    
    # Padrões para extrair ID do vídeo
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([\w-]+)',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def validate_youtube_url(url: str) -> None:
    """
    Valida especificamente uma URL do YouTube.
    
    Args:
        url: URL do YouTube a ser validada
        
    Raises:
        InvalidVideoFormatError: Se não for uma URL válida do YouTube
    """
    # Primeiro validar formato básico
    validate_url_format(url)
    
    # Verificar se consegue extrair ID do vídeo (isso já verifica se é YouTube)
    video_id = extract_youtube_video_id(url)
    if not video_id:
        # Se não conseguiu extrair ID, verificar se pelo menos é do YouTube
        if is_youtube_url(url):
            raise InvalidVideoFormatError(
                field="url",
                value=url,
                constraint="não foi possível extrair ID do vídeo da URL do YouTube"
            )
        else:
            raise InvalidVideoFormatError(
                field="url",
                value=url,
                constraint="deve ser uma URL válida do YouTube"
            )