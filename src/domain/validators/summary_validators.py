"""
Validadores específicos para entidades de resumo.

Este módulo contém funções de validação reutilizáveis para diferentes
aspectos das entidades de resumo, seguindo regras de negócio específicas.
"""

from typing import Optional

from ..exceptions.alfredo_errors import InvalidVideoFormatError


def validate_summary_text(text: str) -> None:
    """
    Valida o texto do resumo segundo regras de negócio.
    
    Regras:
    - Não pode ser vazio ou apenas espaços
    - Máximo de 100.000 caracteres
    - Deve ter encoding válido (UTF-8)
    
    Args:
        text: Texto do resumo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o texto não atender aos critérios
    """
    if not text or not text.strip():
        raise InvalidVideoFormatError(
            field="summary_text",
            value=text,
            constraint="não pode ser vazio ou apenas espaços"
        )
    
    max_length = 100_000  # 100 mil caracteres
    if len(text) > max_length:
        raise InvalidVideoFormatError(
            field="summary_text",
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
            field="summary_text",
            value=text,
            constraint="deve ter encoding UTF-8 válido",
            details={"encoding_error": str(e)}
        )


def validate_summary_type(summary_type: str) -> None:
    """
    Valida o tipo do resumo.
    
    Regras:
    - Não pode ser vazio
    - Deve estar na lista de tipos suportados
    
    Args:
        summary_type: Tipo do resumo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o tipo não atender aos critérios
    """
    if not summary_type or not summary_type.strip():
        raise InvalidVideoFormatError(
            field="summary_type",
            value=summary_type,
            constraint="não pode ser vazio"
        )
    
    # Tipos de resumo suportados
    supported_types = {
        'general',          # Resumo geral
        'bullet_points',    # Pontos principais
        'structured',       # Resumo estruturado em seções
        'executive',        # Resumo executivo
        'detailed',         # Resumo detalhado
        'key_insights',     # Insights principais
        'timeline',         # Resumo cronológico
        'topics',           # Resumo por tópicos
    }
    
    type_lower = summary_type.lower().strip()
    
    if type_lower not in supported_types:
        raise InvalidVideoFormatError(
            field="summary_type",
            value=summary_type,
            constraint=f"tipo não suportado. Tipos aceitos: {', '.join(sorted(supported_types))}",
            details={
                "detected_type": summary_type,
                "supported_types": list(supported_types)
            }
        )


def validate_summary_language(language: str) -> None:
    """
    Valida o código de idioma do resumo.
    
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
            field="summary_language",
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
            field="summary_language",
            value=language,
            constraint=f"idioma não suportado. Idiomas aceitos: {', '.join(sorted(supported_languages))}",
            details={
                "detected_language": language,
                "supported_languages": list(supported_languages)
            }
        )


def validate_summary_provider(provider: Optional[str]) -> None:
    """
    Valida o provedor de resumo.
    
    Args:
        provider: Nome do provedor a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o provedor não for válido
    """
    if provider is None:
        return
    
    if not provider or not provider.strip():
        raise InvalidVideoFormatError(
            field="summary_provider",
            value=provider,
            constraint="não pode ser vazio se fornecido"
        )
    
    # Provedores conhecidos
    known_providers = {
        'groq', 'ollama', 'openai', 'azure', 'google', 'aws', 'anthropic'
    }
    
    provider_lower = provider.lower().strip()
    
    # Não é erro se não estiver na lista, mas registra como desconhecido
    if provider_lower not in known_providers:
        # Log ou warning poderia ser adicionado aqui
        pass


def validate_summary_model(model: Optional[str]) -> None:
    """
    Valida o modelo usado para geração do resumo.
    
    Args:
        model: Nome do modelo a ser validado
        
    Raises:
        InvalidVideoFormatError: Se o modelo não for válido
    """
    if model is None:
        return
    
    if not model or not model.strip():
        raise InvalidVideoFormatError(
            field="summary_model",
            value=model,
            constraint="não pode ser vazio se fornecido"
        )
    
    # Modelos conhecidos
    known_models = {
        # Groq
        'llama-3.3-70b-versatile', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768',
        # Ollama
        'llama3:8b', 'llama3:70b', 'mistral:7b', 'codellama:7b',
        # OpenAI
        'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo',
    }
    
    model_lower = model.lower().strip()
    
    # Não é erro se não estiver na lista, mas registra como desconhecido
    if model_lower not in known_models:
        # Log ou warning poderia ser adicionado aqui
        pass


def validate_summary_confidence(confidence: Optional[float]) -> None:
    """
    Valida o nível de confiança do resumo.
    
    Args:
        confidence: Nível de confiança a ser validado
        
    Raises:
        InvalidVideoFormatError: Se a confiança não atender aos critérios
    """
    if confidence is None:
        return
    
    if confidence < 0.0:
        raise InvalidVideoFormatError(
            field="summary_confidence",
            value=confidence,
            constraint="deve ser maior ou igual a 0.0"
        )
    
    if confidence > 1.0:
        raise InvalidVideoFormatError(
            field="summary_confidence",
            value=confidence,
            constraint="deve ser menor ou igual a 1.0"
        )


def validate_processing_time(processing_time: Optional[float]) -> None:
    """
    Valida o tempo de processamento do resumo.
    
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
    
    # Tempo máximo razoável: 1 hora
    max_time = 3600  # 1 hora em segundos
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