"""
Validadores específicos para entidades de vídeo.

Este módulo contém funções de validação reutilizáveis para diferentes
aspectos das entidades de vídeo, seguindo regras de negócio específicas.
"""

import re
from pathlib import Path
from typing import Optional, Any

from ..exceptions.alfredo_errors import InvalidVideoFormatError
from .url_validators import validate_url_format


def validate_video_id(video_id: str) -> None:
    """
    Valida o ID de um vídeo segundo regras de negócio.
    
    Regras:
    - Não pode ser vazio ou apenas espaços
    - Máximo de 255 caracteres
    - Apenas letras, números, underscore e hífen
    
    Args:
        video_id: ID do vídeo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o ID não atender aos critérios
    """
    if not video_id or not video_id.strip():
        raise InvalidVideoFormatError(
            field="id",
            value=video_id,
            constraint="não pode ser vazio ou apenas espaços"
        )
    
    if len(video_id) > 255:
        raise InvalidVideoFormatError(
            field="id",
            value=video_id,
            constraint="máximo 255 caracteres",
            details={"current_length": len(video_id)}
        )
    
    # Validar caracteres permitidos: letras, números, _, -
    if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
        raise InvalidVideoFormatError(
            field="id",
            value=video_id,
            constraint="apenas letras, números, underscore (_) e hífen (-) são permitidos"
        )


def validate_video_title(title: str) -> None:
    """
    Valida o título de um vídeo segundo regras de negócio.
    
    Regras:
    - Não pode ser vazio ou apenas espaços
    - Máximo de 500 caracteres
    - Deve ter encoding válido (UTF-8)
    
    Args:
        title: Título do vídeo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o título não atender aos critérios
    """
    if not title or not title.strip():
        raise InvalidVideoFormatError(
            field="title",
            value=title,
            constraint="não pode ser vazio ou apenas espaços"
        )
    
    if len(title) > 500:
        raise InvalidVideoFormatError(
            field="title",
            value=title,
            constraint="máximo 500 caracteres",
            details={"current_length": len(title)}
        )
    
    # Validar encoding UTF-8
    try:
        title.encode('utf-8')
    except UnicodeEncodeError as e:
        raise InvalidVideoFormatError(
            field="title",
            value=title,
            constraint="deve ter encoding UTF-8 válido",
            details={"encoding_error": str(e)}
        )


def validate_video_duration(duration: float) -> None:
    """
    Valida a duração de um vídeo segundo regras de negócio.
    
    Regras:
    - Não pode ser negativa
    - Máximo de 24 horas (86400 segundos)
    - Zero é permitido para casos especiais
    
    Args:
        duration: Duração em segundos a ser validada
        
    Raises:
        InvalidVideoFormatError: Se a duração não atender aos critérios
    """
    if duration < 0:
        raise InvalidVideoFormatError(
            field="duration",
            value=duration,
            constraint="não pode ser negativa"
        )
    
    # 24 horas = 86400 segundos
    max_duration = 86400
    if duration > max_duration:
        raise InvalidVideoFormatError(
            field="duration",
            value=duration,
            constraint=f"máximo {max_duration} segundos (24 horas)",
            details={
                "max_duration_seconds": max_duration,
                "max_duration_hours": max_duration / 3600
            }
        )


def validate_video_sources(file_path: Optional[str], url: Optional[str]) -> None:
    """
    Valida as fontes de um vídeo (arquivo local ou URL).
    
    Regras:
    - Pelo menos uma fonte válida deve existir
    - Se file_path fornecido, arquivo deve existir
    - Se URL fornecida, deve ter formato válido
    
    Args:
        file_path: Caminho do arquivo local (opcional)
        url: URL do vídeo (opcional)
        
    Raises:
        InvalidVideoFormatError: Se nenhuma fonte válida for encontrada
    """
    has_valid_file = False
    has_valid_url = False
    
    # Verificar arquivo local (apenas se fornecido e existir)
    if file_path:
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists() and file_path_obj.is_file():
                has_valid_file = True
        except TypeError:
            pass # Ignorar se file_path não for um tipo válido para Path
    
    # Verificar URL (apenas se fornecida e válida)
    if url:
        try:
            validate_url_format(url)
            has_valid_url = True
        except InvalidVideoFormatError:
            pass # URL inválida, mas não vamos lançar erro aqui se houver file_path válido
        except TypeError:
            pass # Ignorar se url não for um tipo válido para validação
    
    # Pelo menos uma fonte deve ser válida
    if not has_valid_file and not has_valid_url:
        error_details = {}
        
        if file_path:
            error_details["file_path"] = file_path
            error_details["file_exists"] = Path(file_path).exists() if file_path else False
        
        if url:
            error_details["url"] = url
            error_details["url_format_valid"] = False
        
        raise InvalidVideoFormatError(
            field="sources",
            value={"file_path": file_path, "url": url},
            constraint="deve ter pelo menos um file_path válido ou URL válida",
            details=error_details
        )


def validate_video_file_format(file_path: str) -> None:
    """
    Valida se o formato do arquivo de vídeo é suportado.
    
    Args:
        file_path: Caminho do arquivo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o formato não for suportado
    """
    supported_extensions = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', 
        '.flv', '.webm', '.m4v', '.3gp', '.ogv'
    }
    
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()
    
    if extension not in supported_extensions:
        raise InvalidVideoFormatError(
            field="file_format",
            value=extension,
            constraint=f"formato não suportado. Formatos aceitos: {', '.join(sorted(supported_extensions))}",
            details={
                "file_path": file_path,
                "detected_extension": extension,
                "supported_extensions": list(supported_extensions)
            }
        )