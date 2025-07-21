"""
Validadores específicos para entidades de transcrição.

Este módulo contém funções de validação reutilizáveis para diferentes
aspectos das entidades de transcrição, seguindo regras de negócio específicas.
"""

from typing import Optional

from ..exceptions.alfredo_errors import InvalidVideoFormatError


def validate_transcription_text(text: str) -> None:
    """
    Valida o texto da transcrição segundo regras de negócio.
    
    Regras:
    - Não pode ser vazio ou apenas espaços
    - Máximo de 1.000.000 caracteres (1MB de texto)
    - Deve ter encoding válido (UTF-8)
    
    Args:
        text: Texto da transcrição a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o texto não atender aos critérios
    """
    if not text or not text.strip():
        raise InvalidVideoFormatError(
            field="transcription_text",
            value=text,
            constraint="não pode ser vazio ou apenas espaços"
        )
    
    max_length = 1_000_000  # 1 milhão de caracteres
    if len(text) > max_length:
        raise InvalidVideoFormatError(
            field="transcription_text",
            value=text,
            constraint=f"máximo {max_length:,} caracteres",
            details={
                "current_length": len(text),
                "max_length": max_length
            }
        )
    
    # Validar encoding UTF-8
    try:
        text.encode('utf-8')
    except UnicodeEncodeError as e:
        raise InvalidVideoFormatError(
            field="transcription_text",
            value=text,
            constraint="deve ter encoding UTF-8 válido",
            details={"encoding_error": str(e)}
        )


def validate_transcription_language(language: str) -> None:
    """
    Valida o código de idioma da transcrição.
    
    Regras:
    - Deve ser código ISO 639-1 (2 letras) ou ISO 639-3 (3 letras)
    - Não pode ser vazio
    - Deve estar na lista de idiomas suportados
    
    Args:
        language: Código do idioma a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o idioma não atender aos critérios
    """
    if not language or not language.strip():
        raise InvalidVideoFormatError(
            field="transcription_language",
            value=language,
            constraint="não pode ser vazio"
        )
    
    language = language.strip().lower()
    
    # Idiomas suportados (ISO 639-1 e alguns ISO 639-3)
    supported_languages = {
        'pt', 'en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh', 'ru',
        'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi',
        'pt-br', 'en-us', 'en-gb', 'es-es', 'es-mx', 'fr-fr', 'de-de'
    }
    
    if language not in supported_languages:
        raise InvalidVideoFormatError(
            field="transcription_language",
            value=language,
            constraint=f"idioma não suportado. Idiomas aceitos: {', '.join(sorted(supported_languages))}",
            details={
                "detected_language": language,
                "supported_languages": list(supported_languages)
            }
        )


def validate_transcription_confidence(confidence: float) -> None:
    """
    Valida o nível de confiança da transcrição.
    
    Regras:
    - Deve estar entre 0.0 e 1.0 (inclusive)
    - Valores negativos não são permitidos
    - Valores acima de 1.0 não são permitidos
    
    Args:
        confidence: Nível de confiança a ser validado
        
    Raises:
        InvalidVideoFormatError: Se a confiança não atender aos critérios
    """
    if confidence < 0.0:
        raise InvalidVideoFormatError(
            field="transcription_confidence",
            value=confidence,
            constraint="deve ser maior ou igual a 0.0"
        )
    
    if confidence > 1.0:
        raise InvalidVideoFormatError(
            field="transcription_confidence",
            value=confidence,
            constraint="deve ser menor ou igual a 1.0"
        )


def validate_transcription_provider(provider: Optional[str]) -> None:
    """
    Valida o provedor de transcrição.
    
    Args:
        provider: Nome do provedor a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o provedor não for válido
    """
    if provider is None:
        return
    
    if not provider or not provider.strip():
        raise InvalidVideoFormatError(
            field="transcription_provider",
            value=provider,
            constraint="não pode ser vazio se fornecido"
        )
    
    # Provedores conhecidos
    known_providers = {
        'whisper', 'groq', 'ollama', 'openai', 'azure', 'google', 'aws'
    }
    
    provider_lower = provider.lower().strip()
    
    # Não é erro se não estiver na lista, mas registra como desconhecido
    if provider_lower not in known_providers:
        # Log ou warning poderia ser adicionado aqui
        pass


def validate_transcription_model(model: Optional[str]) -> None:
    """
    Valida o modelo usado para transcrição.
    
    Args:
        model: Nome do modelo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o modelo não for válido
    """
    if model is None:
        return
    
    if not model or not model.strip():
        raise InvalidVideoFormatError(
            field="transcription_model",
            value=model,
            constraint="não pode ser vazio se fornecido"
        )
    
    # Modelos conhecidos do Whisper
    known_whisper_models = {
        'tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'
    }
    
    model_lower = model.lower().strip()
    
    # Não é erro se não estiver na lista, mas registra como desconhecido
    if model_lower not in known_whisper_models:
        # Log ou warning poderia ser adicionado aqui
        pass


def validate_processing_time(processing_time: Optional[float]) -> None:
    """
    Valida o tempo de processamento da transcrição.
    
    Args:
        processing_time: Tempo de processamento em segundos
        
    Raises:
        InvalidVideoFormatError: Se o tempo não for válido
    """
    if processing_time is None:
        return
    
    if processing_time < 0:
        raise InvalidVideoFormatError(
            field="processing_time",
            value=processing_time,
            constraint="não pode ser negativo"
        )
    
    # Tempo máximo razoável: 24 horas
    max_time = 86400  # 24 horas em segundos
    if processing_time > max_time:
        raise InvalidVideoFormatError(
            field="processing_time",
            value=processing_time,
            constraint=f"tempo de processamento muito alto (máximo {max_time} segundos)",
            details={
                "max_processing_time": max_time,
                "max_processing_hours": max_time / 3600
            }
        )