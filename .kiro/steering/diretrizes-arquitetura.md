# Diretrizes Mandatórias para Evolução e Refatoração do Agente de IA "Alfredo"

Este documento estabelece as diretrizes obrigatórias para refatorar a base de código procedural existente do Alfredo AI para uma arquitetura em camadas (Clean Architecture), resultando em um sistema mais testável, manutenível e robusto.

## 1. Arquitetura e Estrutura em Camadas (Clean Architecture)

A estrutura do projeto deve ser rigorosamente dividida nas seguintes camadas. A **Regra de Dependência é absoluta**: o código em uma camada interna não pode, em hipótese alguma, saber sobre o código em uma camada externa.

### Camada de Domínio (Entities)
**Objetivo**: Representar os conceitos centrais do negócio.

**Ação**: Crie classes Python simples (dataclasses são ideais) para representar as entidades fundamentais:
- `Video`: Representa um arquivo de vídeo com URL ou caminho válido
- `AudioTrack`: Representa uma faixa de áudio extraída
- `Transcription`: Representa o texto transcrito do áudio
- `FrameAnalysis`: Representa análise visual de frames
- `Summary`: Representa o resumo gerado pela IA

```python
@dataclass
class Video:
    source: str  # URL ou caminho do arquivo
    duration: Optional[float] = None
    format: Optional[str] = None
    
    def __post_init__(self):
        if not self.source or not self._is_valid_source():
            raise ValueError("Video deve ter uma URL ou caminho válido")
```

Essas classes devem conter apenas dados e lógica de validação intrínseca. Elas não devem depender de NADA externo.

### Camada de Aplicação (Use Cases)
**Objetivo**: Orquestrar o fluxo de cada funcionalidade (casos de uso).

**Ação**: Refatore a lógica atualmente dispersa nos scripts de `commands/` para classes de Casos de Uso:

```python
class SummarizeYoutubeVideoUseCase:
    def __init__(self, 
                 downloader: VideoDownloaderGateway,
                 audio_extractor: AudioExtractorGateway,
                 ai_provider: AIProvider,
                 storage: StorageGateway):
        self._downloader = downloader
        self._audio_extractor = audio_extractor
        self._ai_provider = ai_provider
        self._storage = storage
    
    async def execute(self, url: str) -> Summary:
        # Orquestra: download → extração → transcrição → sumarização
        video = await self._downloader.download(url)
        audio = await self._audio_extractor.extract(video)
        transcription = await self._ai_provider.transcribe(audio)
        summary = await self._ai_provider.summarize(transcription, video.title)
        await self._storage.save_summary(summary)
        return summary
```

- `SummarizeYoutubeVideoUseCase`: URL → download → análise → resumo
- `SummarizeLocalVideoUseCase`: arquivo local → análise → resumo
- `SummarizeAudioOnlyUseCase`: análise rápida apenas de áudio

### Camada de Adaptadores de Interface (Gateways / Providers)
**Objetivo**: Abstrair e adaptar tecnologias externas.

**Ação**: Defina interfaces (ABCs) para todas as dependências externas:

```python
class VideoDownloaderGateway(ABC):
    @abstractmethod
    async def download(self, url: str) -> Video:
        pass

class AudioExtractorGateway(ABC):
    @abstractmethod
    async def extract(self, video: Video) -> AudioTrack:
        pass

class StorageGateway(ABC):
    @abstractmethod
    async def save_summary(self, summary: Summary) -> None:
        pass
    
    @abstractmethod
    async def load_summary(self, video_id: str) -> Optional[Summary]:
        pass
```

### Camada de Infraestrutura (Frameworks & Drivers)
**Objetivo**: Implementar as interfaces da camada de adaptadores.

**Ação**: Crie implementações concretas:

```python
class YTDLPDownloader(VideoDownloaderGateway):
    async def download(self, url: str) -> Video:
        # Implementação usando yt-dlp
        pass

class FFmpegAudioExtractor(AudioExtractorGateway):
    async def extract(self, video: Video) -> AudioTrack:
        # Implementação usando ffmpeg
        pass

class FileSystemStorage(StorageGateway):
    def __init__(self, base_path: Path):
        self._base_path = base_path
    
    async def save_summary(self, summary: Summary) -> None:
        # Salva no sistema de arquivos
        pass
```

### Camada de Apresentação (UI)
**Objetivo**: Interagir com o usuário.

**Ação**: Os scripts em `commands/` se tornam a camada de Apresentação:

```python
# commands/video/youtube_ai.py
async def main():
    # 1. Analisar argumentos da linha de comando
    args = parse_arguments()
    
    # 2. Instanciar dependências (Injeção de Dependência)
    downloader = YTDLPDownloader()
    extractor = FFmpegAudioExtractor()
    ai_provider = get_ai_provider()
    storage = FileSystemStorage(paths.OUTPUT_SUMMARIES_YOUTUBE)
    
    # 3. Instanciar e executar Use Case
    use_case = SummarizeYoutubeVideoUseCase(downloader, extractor, ai_provider, storage)
    
    try:
        summary = await use_case.execute(args.url)
        print(f"✅ Resumo salvo: {summary.file_path}")
    except DownloadFailedError as e:
        print(f"❌ Erro no download: {e}")
    except TranscriptionError as e:
        print(f"❌ Erro na transcrição: {e}")
```

Responsabilidades da camada de apresentação:
- Analisar argumentos da linha de comando
- Instanciar Use Cases e dependências
- Chamar execução do Use Case
- Exibir resultados para o usuário
- **NÃO** conter lógica de negócio

### Domain-Driven Design (DDD)
- Utilizar Linguagem Ubíqua derivada do domínio (análise de vídeo/áudio)
- Modelar usando: Entidades, Objetos de Valor, Agregados, Serviços de Domínio
- Delimitar contextos com Bounded Contexts:
  - **Contexto de Análise de Mídia**: Video, AudioTrack, Transcription, Summary
  - **Contexto de Provedores de IA**: AIProvider, GroqProvider, OllamaProvider
  - **Contexto de Armazenamento**: StorageGateway, FileSystemStorage

## 2. Metodologia de Desenvolvimento e Design

### Behavior-Driven Development (BDD)
- Definir comportamento esperado através de cenários Gherkin (Given-When-Then)
- Exemplo para Alfredo:
  ```gherkin
  Cenário: Análise de áudio local
    Dado que tenho um arquivo de áudio válido
    Quando executo a análise de áudio
    Então devo receber uma transcrição
    E devo receber um resumo estruturado
  ```

### Test-Driven Development (TDD)
- Seguir ciclo Red-Green-Refactor obrigatoriamente
- Casos de Uso e lógica de domínio devem ter testes de unidade dedicados
- Testes não devem depender de serviços externos (use mocks/stubs para interfaces de infraestrutura)
- O arquivo `commands/test_runner.py` deve ser expandido para executar testes de unidade reais, não apenas diagnósticos
- Testes devem estar em `tests/` seguindo estrutura do projeto
- Usar `pytest` como framework padrão

```python
# tests/use_cases/test_summarize_youtube_video.py
@pytest.mark.asyncio
async def test_summarize_youtube_video_success():
    # Given
    mock_downloader = Mock(spec=VideoDownloaderGateway)
    mock_extractor = Mock(spec=AudioExtractorGateway)
    mock_ai_provider = Mock(spec=AIProvider)
    mock_storage = Mock(spec=StorageGateway)
    
    use_case = SummarizeYoutubeVideoUseCase(
        mock_downloader, mock_extractor, mock_ai_provider, mock_storage
    )
    
    # When
    result = await use_case.execute("https://youtube.com/watch?v=test")
    
    # Then
    assert result is not None
    mock_downloader.download.assert_called_once()
    mock_ai_provider.transcribe.assert_called_once()
```

### Design Patterns (GoF)
- **Factory Pattern**: Expandir `provider_factory.py` para criar gateways de infraestrutura
- **Strategy Pattern**: AI providers já implementam, manter e expandir
- **Command Pattern**: Use Cases são comandos que encapsulam operações
- **Dependency Injection**: Injetar implementações de infraestrutura nos Use Cases
- Justificar escolha do padrão quando relevante
- Documentar padrões utilizados no código

```python
# Exemplo de Factory expandido
class InfrastructureFactory:
    @staticmethod
    def create_video_downloader() -> VideoDownloaderGateway:
        return YTDLPDownloader()
    
    @staticmethod
    def create_audio_extractor() -> AudioExtractorGateway:
        return FFmpegAudioExtractor()
    
    @staticmethod
    def create_storage(storage_type: str) -> StorageGateway:
        if storage_type == "filesystem":
            return FileSystemStorage(paths.OUTPUT_SUMMARIES)
        raise ValueError(f"Storage type not supported: {storage_type}")
```

## 3. Princípios de Codificação e Qualidade

### SOLID

#### Single Responsibility Principle (SRP)
- Cada classe/módulo tem uma única razão para mudar
- Exemplo: `GroqProvider` só gerencia comunicação com Groq
- `AudioAnalyzer` só processa análise de áudio

#### Open/Closed Principle (OCP)
- Aberto para extensão, fechado para modificação
- Novos provedores de IA via interface `AIProvider`
- Novos comandos via padrão de registro `COMMAND_INFO`

#### Liskov Substitution Principle (LSP)
- Subtipos substituíveis por tipos base
- `GroqProvider` e `OllamaProvider` intercambiáveis via `AIProvider`

#### Interface Segregation Principle (ISP)
- Interfaces específicas para cada cliente
- Separar `transcribe()` e `summarize()` se necessário

#### Dependency Inversion Principle (DIP)
- Depender de abstrações, não implementações
- Usar `AIProvider` interface, não implementações concretas

### Clean Code
- Código legível e autoexplicativo
- Evitar métodos longos (máximo 20 linhas)
- Evitar classes grandes (máximo 200 linhas)
- Usar nomes descritivos: `transcribe_audio()` não `process()`
- Comentários apenas quando necessário

### DRY (Don't Repeat Yourself)
- Centralizar lógica comum em `services/`
- Reutilizar utilitários em `config/` e `services/`
- Refatorar lógica duplicada de seleção de arquivos e exibição de menus
- Evitar duplicação de código entre comandos

### KISS (Keep It Simple, Stupid)
- Preferir solução mais simples que funcione
- Evitar over-engineering
- Exemplo: usar `requests` simples antes de implementar cliente HTTP complexo

### YAGNI (You Ain't Gonna Need It)
- Implementar apenas funcionalidades necessárias
- Não antecipar requisitos futuros sem justificativa

### Gerenciamento de Configuração
- Centralizar todas as configurações (nomes de modelos de IA, timeouts, caminhos) em um único local
- Injetar configurações nas classes que precisam delas
- Evitar "magic strings" e números mágicos no código
- Usar dataclasses ou classes de configuração tipadas:

```python
@dataclass
class AlfredoConfig:
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_model: str = "llama3:8b"
    whisper_model: str = "base"
    max_video_duration: int = 3600  # 1 hora
    download_timeout: int = 300     # 5 minutos
    transcription_timeout: int = 600 # 10 minutos
```

## 4. Segurança e Operações

### Princípio do Menor Privilégio (PoLP)
- Cada componente acessa apenas recursos necessários
- API keys isoladas por provedor
- Permissões mínimas para arquivos temporários

### Segurança por Design e Robustez
- Validar todas as entradas externas na camada de domínio
- Sanitizar URLs do YouTube antes de processar
- Validar formatos de arquivo antes de processar
- Rate limiting para APIs externas (já implementado no Groq)

### Error Handling Robusto
- Substituir exceções genéricas (`except Exception`) por exceções customizadas e específicas
- Criar hierarquia de exceções do domínio:

```python
class AlfredoError(Exception):
    """Exceção base do Alfredo"""
    pass

class ProviderUnavailableError(AlfredoError):
    """Provedor de IA indisponível"""
    pass

class DownloadFailedError(AlfredoError):
    """Falha no download de vídeo"""
    pass

class TranscriptionError(AlfredoError):
    """Erro na transcrição de áudio"""
    pass

class InvalidVideoFormatError(AlfredoError):
    """Formato de vídeo inválido"""
    pass
```

- A camada de apresentação deve capturar essas exceções e apresentar mensagens amigáveis ao usuário
- Não expor informações sensíveis (stack traces, paths internos) para o usuário final

### Práticas de Banco de Dados
- Não aplicável diretamente (projeto usa arquivos)
- Para metadados: usar estruturas normalizadas
- Indexar por nome de arquivo para busca rápida
- Evitar consultas N+1 em listagens de arquivos

## 5. Plano de Refatoração do Projeto Alfredo

### Estrutura de Diretórios Refatorada
```
Alfredo/
├── domain/                    # Camada de Domínio
│   ├── entities/
│   │   ├── video.py          # Video, AudioTrack
│   │   ├── analysis.py       # Transcription, Summary, FrameAnalysis
│   │   └── __init__.py
│   ├── exceptions/
│   │   ├── alfredo_errors.py # Hierarquia de exceções customizadas
│   │   └── __init__.py
│   └── __init__.py
│
├── application/               # Camada de Aplicação (Use Cases)
│   ├── use_cases/
│   │   ├── summarize_youtube_video.py
│   │   ├── summarize_local_video.py
│   │   ├── summarize_audio_only.py
│   │   └── __init__.py
│   ├── gateways/             # Interfaces (ABCs)
│   │   ├── video_downloader.py
│   │   ├── audio_extractor.py
│   │   ├── storage_gateway.py
│   │   └── __init__.py
│   └── __init__.py
│
├── infrastructure/           # Camada de Infraestrutura
│   ├── providers/           # Implementações de AI
│   │   ├── groq_provider.py
│   │   ├── ollama_provider.py
│   │   └── __init__.py
│   ├── downloaders/
│   │   ├── ytdlp_downloader.py
│   │   └── __init__.py
│   ├── extractors/
│   │   ├── ffmpeg_extractor.py
│   │   └── __init__.py
│   ├── storage/
│   │   ├── filesystem_storage.py
│   │   └── __init__.py
│   ├── factories/
│   │   ├── infrastructure_factory.py
│   │   └── __init__.py
│   └── __init__.py
│
├── presentation/            # Camada de Apresentação (UI)
│   ├── cli/
│   │   ├── youtube_command.py
│   │   ├── local_video_command.py
│   │   ├── audio_command.py
│   │   └── __init__.py
│   └── __init__.py
│
├── config/                  # Configurações
│   ├── alfredo_config.py    # Classe de configuração centralizada
│   ├── paths.py            # Mantém gerenciamento de caminhos
│   └── __init__.py
│
├── tests/                   # Testes organizados por camada
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   └── fixtures/
│
├── Alfredo.py              # Entry point - instancia apresentação
└── requirements.txt
```

### Exemplo de Refatoração: YouTube Command

**Antes (Procedural):**
```python
# commands/video/youtube_ai.py - Estado atual
def main():
    # Lógica misturada: parsing, download, IA, storage
    url = sys.argv[1]
    # ... código procedural misturado
```

**Depois (Clean Architecture):**
```python
# presentation/cli/youtube_command.py
async def main():
    args = parse_arguments()
    
    # Injeção de dependências
    factory = InfrastructureFactory()
    use_case = SummarizeYoutubeVideoUseCase(
        downloader=factory.create_video_downloader(),
        extractor=factory.create_audio_extractor(),
        ai_provider=factory.create_ai_provider(args.provider),
        storage=factory.create_storage("filesystem"),
        config=AlfredoConfig()
    )
    
    try:
        with tqdm(desc="Processando vídeo") as progress:
            summary = await use_case.execute(args.url, progress_callback=progress.update)
            print(f"✅ Resumo salvo: {summary.file_path}")
    except DownloadFailedError as e:
        print(f"❌ Erro no download: {e}")
    except TranscriptionError as e:
        print(f"❌ Erro na transcrição: {e}")
```

### Migração Gradual
1. **Fase 1**: Criar estrutura de domínio (entities, exceptions)
2. **Fase 2**: Extrair Use Cases da lógica atual
3. **Fase 3**: Criar gateways e implementações de infraestrutura
4. **Fase 4**: Refatorar comandos para camada de apresentação
5. **Fase 5**: Adicionar testes abrangentes
6. **Fase 6**: Remover código legado

### Checklist de Refatoração
- [ ] Criar entidades de domínio (Video, AudioTrack, Transcription, Summary)
- [ ] Definir exceções customizadas (AlfredoError e subclasses)
- [ ] Extrair Use Cases da lógica procedural atual
- [ ] Criar interfaces (gateways) para dependências externas
- [ ] Implementar gateways de infraestrutura
- [ ] Refatorar comandos para camada de apresentação
- [ ] Centralizar configurações em classe tipada
- [ ] Escrever testes de unidade para Use Cases
- [ ] Aplicar injeção de dependência
- [ ] Seguir princípios SOLID rigorosamente
- [ ] Validar entradas na camada de domínio
- [ ] Implementar tratamento robusto de erros
- [ ] Documentar arquitetura e padrões utilizados

## 6. Ferramentas e Validação

### Ferramentas Recomendadas
- `pylint` ou `flake8` para análise estática
- `black` para formatação automática
- `pytest` para testes
- `coverage.py` para cobertura de testes
- `bandit` para análise de segurança

### Métricas de Qualidade
- Cobertura de testes: mínimo 80%
- Complexidade ciclomática: máximo 10 por função
- Linhas por função: máximo 20
- Linhas por classe: máximo 200