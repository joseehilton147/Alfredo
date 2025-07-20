# Gateways - Alfredo AI

Este documento descreve os gateways (interfaces) utilizados no Alfredo AI para abstrair dependências externas, seguindo os princípios da Clean Architecture.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [VideoDownloaderGateway](#videodownloadergateway)
- [AudioExtractorGateway](#audioextractorgateway)
- [StorageGateway](#storagegateway)
- [AIProviderInterface](#aiproviderinterface)
- [Implementações](#implementações)
- [Testes](#testes)

## 🎯 Visão Geral

Os gateways são interfaces abstratas que definem contratos para interação com sistemas externos. Eles permitem:

- **Isolamento da infraestrutura**: Use Cases não conhecem implementações concretas
- **Facilidade de testes**: Mocks podem ser facilmente criados
- **Flexibilidade**: Implementações podem ser trocadas sem afetar a lógica de negócio
- **Conformidade com Clean Architecture**: Dependências apontam para dentro

## 📥 VideoDownloaderGateway

Interface para download de vídeos de diferentes fontes (YouTube, Vimeo, etc.).

### Métodos

#### `download(url, output_dir, quality="best") -> str`
Baixa um vídeo da URL especificada.

**Parâmetros:**
- `url: str` - URL válida do vídeo a ser baixado
- `output_dir: str | Path` - Diretório onde o vídeo será salvo
- `quality: str` - Qualidade do vídeo ("best", "worst", "720p", etc.)

**Retorna:**
- `str` - Caminho completo do arquivo de vídeo baixado

**Exceções:**
- `DownloadFailedError` - Quando o download falha por qualquer motivo
- `InvalidVideoFormatError` - Quando a URL não é válida ou suportada
- `ConfigurationError` - Quando há problemas de configuração

#### `extract_info(url) -> Dict`
Extrai metadados do vídeo sem fazer o download.

**Parâmetros:**
- `url: str` - URL do vídeo para extrair informações

**Retorna:**
- `Dict` - Dicionário com metadados do vídeo:
  - `title`: Título do vídeo
  - `duration`: Duração em segundos
  - `uploader`: Nome do canal/uploader
  - `upload_date`: Data de upload (formato YYYYMMDD)
  - `view_count`: Número de visualizações
  - `description`: Descrição do vídeo
  - `thumbnail`: URL da thumbnail
  - `formats`: Lista de formatos disponíveis

#### `get_available_formats(url) -> List[Dict]`
Lista todos os formatos disponíveis para download.

**Retorna:**
- `List[Dict]` - Lista de formatos, cada um contendo:
  - `format_id`: ID único do formato
  - `ext`: Extensão do arquivo (mp4, webm, etc.)
  - `quality`: Descrição da qualidade
  - `filesize`: Tamanho estimado em bytes
  - `vcodec`: Codec de vídeo
  - `acodec`: Codec de áudio
  - `fps`: Frames por segundo
  - `resolution`: Resolução (ex: "1920x1080")

#### `is_url_supported(url) -> bool`
Verifica se a URL é suportada pelo downloader.

**Parâmetros:**
- `url: str` - URL a ser verificada

**Retorna:**
- `bool` - True se a URL é suportada, False caso contrário

#### `get_video_id(url) -> Optional[str]`
Extrai o ID único do vídeo da URL.

**Parâmetros:**
- `url: str` - URL do vídeo

**Retorna:**
- `Optional[str]` - ID do vídeo ou None se não puder ser extraído

### Exemplo de Uso

```python
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway

async def processar_video_youtube(downloader: VideoDownloaderGateway, url: str):
    # Verificar se URL é suportada
    if not await downloader.is_url_supported(url):
        raise InvalidVideoFormatError(f"URL não suportada: {url}")
    
    # Extrair informações básicas
    info = await downloader.extract_info(url)
    print(f"Título: {info['title']}")
    print(f"Duração: {info['duration']}s")
    
    # Listar formatos disponíveis
    formats = await downloader.get_available_formats(url)
    for fmt in formats:
        print(f"Formato: {fmt['quality']} ({fmt['ext']})")
    
    # Fazer download
    video_path = await downloader.download(url, "data/input/youtube", "720p")
    print(f"Vídeo baixado: {video_path}")
```

## 🎵 AudioExtractorGateway

Interface para extração de áudio de arquivos de vídeo.

### Métodos

#### `extract_audio(video_path, output_path, format="wav") -> str`
Extrai áudio de um arquivo de vídeo.

**Parâmetros:**
- `video_path: str` - Caminho do arquivo de vídeo
- `output_path: str` - Caminho de saída para o arquivo de áudio
- `format: str` - Formato de saída ("wav", "mp3", "flac")

**Retorna:**
- `str` - Caminho do arquivo de áudio extraído

#### `get_audio_info(video_path) -> Dict`
Obtém informações sobre o áudio sem extrair.

**Retorna:**
- `Dict` - Informações do áudio (sample_rate, channels, duration, etc.)

## 💾 StorageGateway

Interface para persistência de dados (vídeos, transcrições, metadados).

### Métodos

#### `save_video(video) -> None`
Salva metadados de um vídeo.

#### `load_video(video_id) -> Optional[Video]`
Carrega metadados de um vídeo pelo ID.

#### `save_transcription(video_id, transcription, metadata) -> None`
Salva transcrição de um vídeo.

#### `load_transcription(video_id) -> Optional[str]`
Carrega transcrição de um vídeo.

#### `list_videos(limit, offset) -> List[Video]`
Lista vídeos com paginação.

## 🤖 AIProviderInterface

Interface para provedores de IA (Whisper, Groq, Ollama).

### Métodos

#### `transcribe(audio_path, language) -> str`
Transcreve áudio para texto.

#### `summarize(text, context) -> str`
Gera resumo de um texto.

#### `is_available() -> bool`
Verifica se o provedor está disponível.

## 🏗️ Implementações

### Implementações Atuais
- `YTDLPDownloader` - Implementa `VideoDownloaderGateway` usando yt-dlp
- `FFmpegExtractor` - Implementa `AudioExtractorGateway` usando ffmpeg
- `FileSystemStorage` - Implementa `StorageGateway` usando sistema de arquivos
- `WhisperProvider` - Implementa `AIProviderInterface` usando OpenAI Whisper
- `GroqProvider` - Implementa `AIProviderInterface` usando Groq API

### Criação via Factory

```python
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory

factory = InfrastructureFactory()

# Criar implementações
downloader = factory.create_video_downloader()
extractor = factory.create_audio_extractor()
storage = factory.create_storage("filesystem")
ai_provider = factory.create_ai_provider("whisper")
```

## 🧪 Testes

### Testando com Mocks

```python
import pytest
from unittest.mock import Mock
from src.application.gateways.video_downloader_gateway import VideoDownloaderGateway

@pytest.mark.asyncio
async def test_download_video():
    # Criar mock do gateway
    mock_downloader = Mock(spec=VideoDownloaderGateway)
    mock_downloader.download.return_value = "/path/to/video.mp4"
    mock_downloader.is_url_supported.return_value = True
    
    # Usar no teste
    assert await mock_downloader.is_url_supported("https://youtube.com/watch?v=123")
    video_path = await mock_downloader.download("https://youtube.com/watch?v=123", "/output")
    assert video_path == "/path/to/video.mp4"
```

### Testes de Integração

```python
@pytest.mark.integration
async def test_real_downloader():
    from src.infrastructure.downloaders.ytdlp_downloader import YTDLPDownloader
    
    downloader = YTDLPDownloader()
    
    # Testar com URL real (usar URL de teste)
    info = await downloader.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert "title" in info
    assert info["duration"] > 0
```

## 📚 Boas Práticas

### Para Implementadores

1. **Sempre implementar todas as interfaces**: Não deixe métodos vazios
2. **Tratar erros adequadamente**: Use exceções específicas do domínio
3. **Documentar comportamentos específicos**: Cada implementação pode ter peculiaridades
4. **Validar entradas**: Verificar parâmetros antes de processar
5. **Ser idempotente quando possível**: Mesma entrada deve gerar mesma saída

### Para Consumidores

1. **Depender apenas da interface**: Nunca importe implementações concretas
2. **Tratar exceções específicas**: Capture exceções do domínio, não genéricas
3. **Usar factory pattern**: Deixe a factory criar as implementações
4. **Testar com mocks**: Use mocks para testes unitários rápidos
5. **Validar contratos**: Verifique se implementações seguem a interface

## 🔄 Extensibilidade

### Adicionando Novo Gateway

1. Criar interface em `src/application/gateways/`
2. Implementar em `src/infrastructure/`
3. Adicionar à factory
4. Criar testes
5. Atualizar documentação

### Exemplo: Novo Gateway

```python
# src/application/gateways/subtitle_gateway.py
from abc import ABC, abstractmethod

class SubtitleGateway(ABC):
    @abstractmethod
    async def extract_subtitles(self, video_path: str) -> List[str]:
        """Extrai legendas de um vídeo."""
        pass
```

```python
# src/infrastructure/subtitle/whisper_subtitle_extractor.py
class WhisperSubtitleExtractor(SubtitleGateway):
    async def extract_subtitles(self, video_path: str) -> List[str]:
        # Implementação usando Whisper
        pass
```

---

**📝 Nota**: Esta documentação deve ser atualizada sempre que novos gateways forem adicionados ou interfaces existentes forem modificadas.