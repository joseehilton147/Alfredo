"""
Validadores específicos para entidades de áudio.

Este módulo contém funções de validação reutilizáveis para diferentes
aspectos das entidades de áudio, seguindo regras de negócio específicas.
"""

from pathlib import Path
from typing import Optional

from ..exceptions.alfredo_errors import InvalidVideoFormatError


def validate_audio_file_path(file_path: str) -> None:
    """
    Valida o caminho do arquivo de áudio.
    
    Regras:
    - Não pode ser vazio ou apenas espaços
    - Arquivo deve existir
    - Deve ter extensão de áudio válida
    
    Args:
        file_path: Caminho do arquivo de áudio a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o caminho não atender aos critérios
    """
    if not file_path or not file_path.strip():
        raise InvalidVideoFormatError(
            field="audio_file_path",
            value=file_path,
            constraint="não pode ser vazio ou apenas espaços"
        )
    
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise InvalidVideoFormatError(
            field="audio_file_path",
            value=file_path,
            constraint="arquivo deve existir",
            details={"file_exists": False}
        )
    
    if not file_path_obj.is_file():
        raise InvalidVideoFormatError(
            field="audio_file_path",
            value=file_path,
            constraint="deve ser um arquivo válido",
            details={"is_file": False}
        )
    
    # Validar extensão de áudio
    validate_audio_file_format(file_path)


def validate_audio_duration(duration: float) -> None:
    """
    Valida a duração de um áudio segundo regras de negócio.
    
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
            field="audio_duration",
            value=duration,
            constraint="não pode ser negativa"
        )
    
    # 24 horas = 86400 segundos
    max_duration = 86400
    if duration > max_duration:
        raise InvalidVideoFormatError(
            field="audio_duration",
            value=duration,
            constraint=f"máximo {max_duration} segundos (24 horas)",
            details={
                "max_duration_seconds": max_duration,
                "max_duration_hours": max_duration / 3600
            }
        )


def validate_audio_format(format_name: str) -> None:
    """
    Valida se o formato de áudio é suportado.
    
    Args:
        format_name: Nome do formato a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o formato não for suportado
    """
    supported_formats = {
        'wav', 'mp3', 'flac', 'aac', 'ogg', 'm4a', 'wma'
    }
    
    format_lower = format_name.lower().strip()
    
    if format_lower not in supported_formats:
        raise InvalidVideoFormatError(
            field="audio_format",
            value=format_name,
            constraint=f"formato não suportado. Formatos aceitos: {', '.join(sorted(supported_formats))}",
            details={
                "detected_format": format_name,
                "supported_formats": list(supported_formats)
            }
        )


def validate_audio_file_format(file_path: str) -> None:
    """
    Valida se o formato do arquivo de áudio é suportado baseado na extensão.
    
    Args:
        file_path: Caminho do arquivo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o formato não for suportado
    """
    supported_extensions = {
        '.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a', '.wma'
    }
    
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()
    
    if extension not in supported_extensions:
        raise InvalidVideoFormatError(
            field="audio_file_format",
            value=extension,
            constraint=f"formato não suportado. Formatos aceitos: {', '.join(sorted(supported_extensions))}",
            details={
                "file_path": file_path,
                "detected_extension": extension,
                "supported_extensions": list(supported_extensions)
            }
        )


def validate_audio_sample_rate(sample_rate: Optional[int]) -> None:
    """
    Valida a taxa de amostragem do áudio.
    
    Args:
        sample_rate: Taxa de amostragem em Hz
        
    Raises:
        InvalidVideoFormatError: Se a taxa não for válida
    """
    if sample_rate is None:
        return
    
    if sample_rate <= 0:
        raise InvalidVideoFormatError(
            field="audio_sample_rate",
            value=sample_rate,
            constraint="deve ser positiva"
        )
    
    # Taxas comuns: 8000, 16000, 22050, 44100, 48000, 96000, 192000
    common_rates = {8000, 16000, 22050, 44100, 48000, 96000, 192000}
    
    if sample_rate not in common_rates:
        # Não é erro, mas adiciona informação
        pass


def validate_audio_channels(channels: Optional[int]) -> None:
    """
    Valida o número de canais do áudio.
    
    Args:
        channels: Número de canais
        
    Raises:
        InvalidVideoFormatError: Se o número de canais não for válido
    """
    if channels is None:
        return
    
    if channels <= 0:
        raise InvalidVideoFormatError(
            field="audio_channels",
            value=channels,
            constraint="deve ser positivo"
        )
    
    if channels > 8:  # Máximo razoável para áudio comum
        raise InvalidVideoFormatError(
            field="audio_channels",
            value=channels,
            constraint="máximo 8 canais suportados",
            details={"max_channels": 8}
        )