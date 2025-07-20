# Validadores de Domínio - Alfredo AI

Este documento descreve o sistema de validadores do domínio Alfredo AI, que garantem que entidades sejam criadas apenas em estados válidos, seguindo regras de negócio específicas.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Validadores de Vídeo](#validadores-de-vídeo)
- [Validadores de URL](#validadores-de-url)
- [Uso Prático](#uso-prático)
- [Tratamento de Erros](#tratamento-de-erros)
- [Extensibilidade](#extensibilidade)

## 🎯 Visão Geral

Os validadores são funções puras que implementam regras de negócio específicas para validação de dados. Eles:

- **Garantem consistência**: Dados sempre atendem aos critérios de negócio
- **Falham rapidamente**: Erros são detectados na criação das entidades
- **São reutilizáveis**: Podem ser usados em diferentes contextos
- **Fornecem contexto**: Mensagens de erro específicas e detalhadas

## 📹 Validadores de Vídeo

### `validate_video_id(video_id: str)`

Valida o ID de um vídeo segundo regras de negócio.

**Regras:**
- Não pode ser vazio ou apenas espaços
- Máximo de 255 caracteres
- Apenas letras, números, underscore (_) e hífen (-)

**Exemplo:**
```python
from src.domain.validators import validate_video_id

# ✅ Válido
validate_video_id("video_123")
validate_video_id("my-video-2024")

# ❌ Inválido - lança InvalidVideoFormatError
validate_video_id("")  # Vazio
validate_video_id("video with spaces")  # Espaços
validate_video_id("a" * 256)  # Muito longo
```

### `validate_video_title(title: str)`

Valida o título de um vídeo segundo regras de negócio.

**Regras:**
- Não pode ser vazio ou apenas espaços
- Máximo de 500 caracteres
- Deve ter encoding UTF-8 válido

**Exemplo:**
```python
from src.domain.validators import validate_video_title

# ✅ Válido
validate_video_title("Meu Vídeo Incrível")
validate_video_title("Tutorial: Como usar Python 🐍")

# ❌ Inválido
validate_video_title("")  # Vazio
validate_video_title("   ")  # Apenas espaços
validate_video_title("a" * 501)  # Muito longo
```

### `validate_video_duration(duration: float)`

Valida a duração de um vídeo segundo regras de negócio.

**Regras:**
- Não pode ser negativa
- Máximo de 24 horas (86400 segundos)
- Zero é permitido para casos especiais

**Exemplo:**
```python
from src.domain.validators import validate_video_duration

# ✅ Válido
validate_video_duration(0)      # Zero permitido
validate_video_duration(120.5)  # 2 minutos e 30 segundos
validate_video_duration(3600)   # 1 hora

# ❌ Inválido
validate_video_duration(-10)    # Negativa
validate_video_duration(90000)  # Mais de 24 horas
```

### `validate_video_sources(file_path: Optional[str], url: Optional[str])`

Valida as fontes de um vídeo (arquivo local ou URL).

**Regras:**
- Pelo menos uma fonte válida deve existir
- Se file_path fornecido, arquivo deve existir
- Se URL fornecida, deve ter formato válido

**Exemplo:**
```python
from src.domain.validators import validate_video_sources

# ✅ Válido
validate_video_sources("video.mp4", None)  # Arquivo existe
validate_video_sources(None, "https://youtube.com/watch?v=123")  # URL válida
validate_video_sources("video.mp4", "https://youtube.com/watch?v=123")  # Ambos

# ❌ Inválido
validate_video_sources(None, None)  # Nenhuma fonte
validate_video_sources("inexistente.mp4", None)  # Arquivo não existe
validate_video_sources(None, "url-inválida")  # URL inválida
```

### `validate_video_file_format(file_path: str)`

Valida se o formato do arquivo de vídeo é suportado.

**Formatos Suportados:**
- `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`
- `.flv`, `.webm`, `.m4v`, `.3gp`, `.ogv`

**Exemplo:**
```python
from src.domain.validators import validate_video_file_format

# ✅ Válido
validate_video_file_format("video.mp4")
validate_video_file_format("movie.avi")

# ❌ Inválido
validate_video_file_format("audio.mp3")  # Não é vídeo
validate_video_file_format("document.pdf")  # Formato não suportado
```

## 🌐 Validadores de URL

### `validate_url_format(url: str)`

Valida o formato básico de uma URL.

**Regras:**
- Deve começar com http:// ou https://
- Deve ter domínio válido
- Deve ter estrutura de URL válida

**Exemplo:**
```python
from src.domain.validators import validate_url_format

# ✅ Válido
validate_url_format("https://youtube.com/watch?v=123")
validate_url_format("http://example.com/video")

# ❌ Inválido
validate_url_format("youtube.com")  # Sem protocolo
validate_url_format("ftp://example.com")  # Protocolo não suportado
validate_url_format("https://")  # Sem domínio
```

### `is_youtube_url(url: str) -> bool`

Verifica se uma URL é do YouTube.

**Padrões Suportados:**
- `youtube.com/watch?v=`
- `youtu.be/`
- `youtube.com/embed/`
- `youtube.com/v/`

**Exemplo:**
```python
from src.domain.validators import is_youtube_url

# ✅ YouTube URLs
assert is_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ")
assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
assert is_youtube_url("https://youtube.com/embed/dQw4w9WgXcQ")

# ❌ Não YouTube
assert not is_youtube_url("https://vimeo.com/123456")
assert not is_youtube_url("https://example.com")
```

### `is_supported_video_url(url: str) -> bool`

Verifica se uma URL é de uma plataforma de vídeo suportada.

**Plataformas Suportadas:**
- YouTube (youtube.com, youtu.be)
- *Outras plataformas podem ser adicionadas no futuro*

**Exemplo:**
```python
from src.domain.validators import is_supported_video_url

# ✅ Plataformas suportadas
assert is_supported_video_url("https://youtube.com/watch?v=123")
assert is_supported_video_url("https://youtu.be/123")

# ❌ Plataformas não suportadas
assert not is_supported_video_url("https://vimeo.com/123")
assert not is_supported_video_url("https://dailymotion.com/123")
```

### `extract_youtube_video_id(url: str) -> Optional[str]`

Extrai o ID do vídeo de uma URL do YouTube.

**Exemplo:**
```python
from src.domain.validators import extract_youtube_video_id

# ✅ Extração bem-sucedida
video_id = extract_youtube_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ")
assert video_id == "dQw4w9WgXcQ"

video_id = extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ")
assert video_id == "dQw4w9WgXcQ"

# ❌ Não consegue extrair
video_id = extract_youtube_video_id("https://vimeo.com/123")
assert video_id is None
```

### `validate_youtube_url(url: str)`

Valida especificamente uma URL do YouTube.

**Exemplo:**
```python
from src.domain.validators import validate_youtube_url

# ✅ Válido
validate_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ")

# ❌ Inválido
validate_youtube_url("https://vimeo.com/123")  # Não é YouTube
validate_youtube_url("https://youtube.com/invalid")  # YouTube mas sem ID
```

## 💡 Uso Prático

### Em Entidades de Domínio

```python
from dataclasses import dataclass
from typing import Optional
from src.domain.validators import (
    validate_video_id,
    validate_video_title,
    validate_video_duration,
    validate_video_sources
)

@dataclass
class Video:
    id: str
    title: str
    duration: float
    file_path: Optional[str] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        # Validar todos os campos na criação
        validate_video_id(self.id)
        validate_video_title(self.title)
        validate_video_duration(self.duration)
        validate_video_sources(self.file_path, self.url)
```

### Em Use Cases

```python
from src.domain.validators import validate_youtube_url, is_youtube_url

class ProcessYouTubeVideoUseCase:
    async def execute(self, url: str):
        # Validar entrada
        if not is_youtube_url(url):
            raise InvalidVideoFormatError(
                field="url",
                value=url,
                constraint="deve ser uma URL válida do YouTube"
            )
        
        validate_youtube_url(url)
        
        # Continuar processamento...
```

### Em Gateways

```python
from src.domain.validators import validate_url_format, is_supported_video_url

class YTDLPDownloader(VideoDownloaderGateway):
    async def download(self, url: str, output_dir: str, quality: str = "best"):
        # Validar entrada
        validate_url_format(url)
        
        if not is_supported_video_url(url):
            raise InvalidVideoFormatError(
                field="url",
                value=url,
                constraint="plataforma não suportada"
            )
        
        # Continuar download...
```

## 🚨 Tratamento de Erros

Todos os validadores lançam `InvalidVideoFormatError` quando a validação falha:

```python
from src.domain.exceptions import InvalidVideoFormatError

try:
    validate_video_id("invalid id with spaces")
except InvalidVideoFormatError as e:
    print(f"Campo: {e.field}")
    print(f"Valor: {e.value}")
    print(f"Restrição: {e.constraint}")
    print(f"Detalhes: {e.details}")
    
    # Serializar para logging
    error_dict = e.to_dict()
    logger.error("Validation failed", extra=error_dict)
```

### Exemplo de Erro Detalhado

```python
# Erro com contexto rico
try:
    validate_video_duration(-10)
except InvalidVideoFormatError as e:
    # e.field = "duration"
    # e.value = -10
    # e.constraint = "não pode ser negativa"
    # e.details = {}
```

## 🔧 Extensibilidade

### Adicionando Novos Validadores

1. **Criar função de validação:**

```python
# src/domain/validators/custom_validators.py
def validate_video_quality(quality: str) -> None:
    """Valida qualidade de vídeo."""
    valid_qualities = {"144p", "240p", "360p", "480p", "720p", "1080p", "4K"}
    
    if quality not in valid_qualities:
        raise InvalidVideoFormatError(
            field="quality",
            value=quality,
            constraint=f"deve ser uma das opções: {', '.join(valid_qualities)}"
        )
```

2. **Adicionar ao `__init__.py`:**

```python
from .custom_validators import validate_video_quality

__all__ = [
    # ... outros validadores
    "validate_video_quality",
]
```

3. **Criar testes:**

```python
# tests/domain/validators/test_custom_validators.py
def test_validate_video_quality_valid():
    validate_video_quality("1080p")  # Não deve lançar exceção

def test_validate_video_quality_invalid():
    with pytest.raises(InvalidVideoFormatError) as exc_info:
        validate_video_quality("8K")
    
    assert exc_info.value.field == "quality"
    assert exc_info.value.value == "8K"
```

### Validadores Compostos

```python
def validate_complete_video(video_data: dict) -> None:
    """Valida todos os aspectos de um vídeo."""
    validate_video_id(video_data["id"])
    validate_video_title(video_data["title"])
    validate_video_duration(video_data["duration"])
    validate_video_sources(
        video_data.get("file_path"),
        video_data.get("url")
    )
    
    # Validações adicionais específicas
    if video_data.get("quality"):
        validate_video_quality(video_data["quality"])
```

## 📚 Boas Práticas

### Para Desenvolvedores

1. **Validar na criação**: Use validadores em `__post_init__` de dataclasses
2. **Falhar rapidamente**: Validar entradas o mais cedo possível
3. **Mensagens claras**: Fornecer contexto útil nos erros
4. **Ser específico**: Usar validadores específicos em vez de genéricos
5. **Testar exaustivamente**: Cobrir casos válidos e inválidos

### Para Extensões

1. **Seguir padrões**: Usar mesma estrutura de exceções
2. **Documentar regras**: Explicar claramente as regras de validação
3. **Ser consistente**: Manter consistência com validadores existentes
4. **Adicionar testes**: Sempre incluir testes abrangentes
5. **Atualizar documentação**: Manter documentação atualizada

---

**📝 Nota**: Os validadores são parte fundamental da arquitetura limpa, garantindo que o domínio mantenha sua integridade independentemente da fonte dos dados.