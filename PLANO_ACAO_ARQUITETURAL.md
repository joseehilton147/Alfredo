# Plano de Ação Arquitetural Detalhado - Alfredo AI

## 📋 CHECKLIST GERAL DE CONFORMIDADE

### Status Atual das Diretrizes Mandatórias

| Diretriz | Status | Prioridade | Esforço |
|----------|--------|------------|---------|
| ✅ Clean Architecture (Estrutura) | CONFORME | - | - |
| ❌ Hierarquia de Exceções | NÃO CONFORME | ALTA | 2 dias |
| ❌ Factory Pattern + DI | NÃO CONFORME | ALTA | 3 dias |
| ❌ Gateways de Infraestrutura | NÃO CONFORME | ALTA | 4 dias |
| ⚠️ Configuração Tipada | PARCIAL | MÉDIA | 1 dia |
| ⚠️ Validação de Domínio | PARCIAL | MÉDIA | 2 dias |
| ⚠️ Camada de Apresentação | PARCIAL | MÉDIA | 2 dias |
| ✅ Testes Unitários (Base) | CONFORME | - | - |
| ❌ Testes BDD/Gherkin | NÃO CONFORME | BAIXA | 3 dias |
| ❌ Métricas de Qualidade | NÃO CONFORME | BAIXA | 1 dia |

---

## 🎯 FASE 1: FUNDAÇÕES CRÍTICAS (Semana 1-2)

### 📝 **AÇÃO 1.1: Hierarquia de Exceções Customizadas**

#### Objetivo
Implementar sistema robusto de tratamento de erros conforme diretrizes mandatórias.

#### Tarefas Detalhadas

**1.1.1 Criar Estrutura de Exceções**
```bash
# Criar arquivo de exceções
touch src/domain/exceptions/__init__.py
touch src/domain/exceptions/alfredo_errors.py
```

**Implementação Requerida:**
```python
# src/domain/exceptions/alfredo_errors.py
class AlfredoError(Exception):
    """Exceção base do Alfredo AI"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

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

class ConfigurationError(AlfredoError):
    """Erro de configuração"""
    pass
```

**1.1.2 Refatorar Código Existente**
- [ ] Substituir `RuntimeError` em `WhisperProvider.transcribe_audio()`
- [ ] Substituir `Exception` genéricas em `ProcessYouTubeVideoUseCase`
- [ ] Atualizar `JsonVideoRepository` para usar exceções específicas
- [ ] Refatorar `main.py` para capturar exceções específicas

**1.1.3 Atualizar Testes**
- [ ] Modificar testes para verificar exceções específicas
- [ ] Adicionar testes para cada tipo de exceção
- [ ] Verificar que detalhes das exceções são preservados

**Critério de Aceitação**: 
- Zero ocorrências de `except Exception:` genérico
- Todas as exceções herdam de `AlfredoError`
- Testes verificam tipos específicos de exceção

---

### 🏭 **AÇÃO 1.2: Factory Pattern e Injeção de Dependência**

#### Objetivo
Implementar sistema de injeção de dependência conforme padrão definido nas diretrizes.

#### Tarefas Detalhadas

**1.2.1 Criar Infrastructure Factory**
```bash
mkdir -p src/infrastructure/factories
touch src/infrastructure/factories/__init__.py
touch src/infrastructure/factories/infrastructure_factory.py
```

**Implementação Requerida:**
```python
# src/infrastructure/factories/infrastructure_factory.py
from src.application.gateways.video_downloader import VideoDownloaderGateway
from src.application.gateways.audio_extractor import AudioExtractorGateway
from src.application.gateways.storage_gateway import StorageGateway
from src.application.interfaces.ai_provider import AIProviderInterface

class InfrastructureFactory:
    @staticmethod
    def create_video_downloader() -> VideoDownloaderGateway:
        from src.infrastructure.downloaders.ytdlp_downloader import YTDLPDownloader
        return YTDLPDownloader()
    
    @staticmethod
    def create_audio_extractor() -> AudioExtractorGateway:
        from src.infrastructure.extractors.ffmpeg_extractor import FFmpegExtractor
        return FFmpegExtractor()
    
    @staticmethod
    def create_ai_provider(provider_type: str = "whisper") -> AIProviderInterface:
        if provider_type == "whisper":
            from src.infrastructure.providers.whisper_provider import WhisperProvider
            return WhisperProvider()
        raise ConfigurationError(f"Provider não suportado: {provider_type}")
    
    @staticmethod
    def create_storage(storage_type: str = "filesystem") -> StorageGateway:
        if storage_type == "filesystem":
            from src.infrastructure.storage.filesystem_storage import FileSystemStorage
            return FileSystemStorage()
        raise ConfigurationError(f"Storage não suportado: {storage_type}")
```

**1.2.2 Refatorar Use Cases**
- [ ] Modificar construtores para receber todas as dependências
- [ ] Remover instanciação direta de classes de infraestrutura
- [ ] Atualizar testes para usar mocks das interfaces

**1.2.3 Atualizar Camada de Apresentação**
- [ ] Modificar `main.py` para usar factory
- [ ] Atualizar CLI para injetar dependências via factory

**Critério de Aceitação**:
- Use Cases não instanciam classes de infraestrutura diretamente
- Factory centraliza criação de todas as dependências
- Testes usam mocks das interfaces, não implementações

---

### 🔌 **AÇÃO 1.3: Implementar Gateways de Infraestrutura**

#### Objetivo
Completar abstração de dependências externas conforme Clean Architecture.

#### Tarefas Detalhadas

**1.3.1 Criar Interfaces de Gateway**
```bash
mkdir -p src/application/gateways
touch src/application/gateways/__init__.py
touch src/application/gateways/video_downloader.py
touch src/application/gateways/audio_extractor.py
touch src/application/gateways/storage_gateway.py
```

**Implementações Requeridas:**

```python
# src/application/gateways/video_downloader_gateway.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pathlib import Path

class VideoDownloaderGateway(ABC):
    @abstractmethod
    async def download(self, url: str, output_dir: str | Path, quality: str = "best") -> str:
        """
        Baixa um vídeo da URL especificada.
        
        Args:
            url: URL válida do vídeo a ser baixado
            output_dir: Diretório onde o vídeo será salvo
            quality: Qualidade do vídeo ("best", "worst", "720p", etc.)
            
        Returns:
            str: Caminho completo do arquivo de vídeo baixado
            
        Raises:
            DownloadFailedError: Quando o download falha por qualquer motivo
            InvalidVideoFormatError: Quando a URL não é válida ou suportada
            ConfigurationError: Quando há problemas de configuração
        """
        pass
    
    @abstractmethod
    async def extract_info(self, url: str) -> Dict:
        """
        Extrai metadados do vídeo sem fazer o download.
        
        Returns:
            Dict: Dicionário com metadados completos do vídeo incluindo
                  title, duration, uploader, upload_date, view_count, etc.
        """
        pass
    
    @abstractmethod
    async def get_available_formats(self, url: str) -> List[Dict]:
        """Lista todos os formatos disponíveis para download."""
        pass
    
    @abstractmethod
    async def is_url_supported(self, url: str) -> bool:
        """Verifica se a URL é suportada pelo downloader."""
        pass
    
    @abstractmethod
    async def get_video_id(self, url: str) -> Optional[str]:
        """Extrai o ID único do vídeo da URL."""
        pass
```

```python
# src/application/gateways/audio_extractor.py
from abc import ABC, abstractmethod

class AudioExtractorGateway(ABC):
    @abstractmethod
    async def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extrai áudio do vídeo"""
        pass
```

```python
# src/application/gateways/storage_gateway.py
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.video import Video

class StorageGateway(ABC):
    @abstractmethod
    async def save_video(self, video: Video) -> None:
        pass
    
    @abstractmethod
    async def load_video(self, video_id: str) -> Optional[Video]:
        pass
    
    @abstractmethod
    async def save_transcription(self, video_id: str, transcription: str) -> None:
        pass
```

**1.3.2 Criar Implementações Concretas**
```bash
mkdir -p src/infrastructure/downloaders
mkdir -p src/infrastructure/extractors
mkdir -p src/infrastructure/storage
```

**1.3.3 Refatorar Use Cases**
- [ ] Modificar `ProcessYouTubeVideoUseCase` para usar gateways
- [ ] Extrair lógica de download para gateway específico
- [ ] Separar responsabilidades de storage

**Critério de Aceitação**:
- Use Cases dependem apenas de interfaces de gateway
- Implementações concretas isoladas na camada de infraestrutura
- Fácil substituição de implementações via factory

---

## 🎯 FASE 2: CONFIGURAÇÃO E VALIDAÇÃO (Semana 3)

### ⚙️ **AÇÃO 2.1: Refatorar Sistema de Configuração**

#### Objetivo
Implementar configuração tipada conforme padrão `AlfredoConfig` das diretrizes.

#### Tarefas Detalhadas

**2.1.1 Criar Nova Estrutura de Configuração**
```python
# src/config/alfredo_config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class AlfredoConfig:
    # Modelos de IA
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_model: str = "llama3:8b"
    whisper_model: str = "base"
    
    # Timeouts e Limites
    max_video_duration: int = 86400  # 24 horas
    download_timeout: int = 300      # 5 minutos
    transcription_timeout: int = 600  # 10 minutos
    max_file_size: str = "500MB"
    
    # Diretórios
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Optional[Path] = None
    
    # API Keys
    groq_api_key: Optional[str] = None
    
    # Configurações de Processamento
    default_language: str = "pt"
    scene_threshold: float = 30.0
    
    def __post_init__(self):
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        
        # Validações
        if self.max_video_duration <= 0:
            raise ConfigurationError("max_video_duration deve ser positivo")
        
        if self.scene_threshold < 0:
            raise ConfigurationError("scene_threshold deve ser não-negativo")
    
    def validate(self) -> None:
        """Valida configurações obrigatórias"""
        if not self.groq_api_key:
            raise ConfigurationError("GROQ_API_KEY é obrigatória")
    
    def create_directories(self) -> None:
        """Cria diretórios necessários"""
        directories = [
            self.data_dir / "input" / "local",
            self.data_dir / "input" / "youtube", 
            self.data_dir / "output",
            self.data_dir / "logs",
            self.data_dir / "temp",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
```

**2.1.2 Migrar Configurações Existentes**
- [ ] Substituir `Config` class por `AlfredoConfig`
- [ ] Migrar todas as variáveis de ambiente
- [ ] Atualizar todos os pontos de uso

**2.1.3 Atualizar Factory para Usar Nova Configuração**
- [ ] Injetar `AlfredoConfig` na factory
- [ ] Usar configurações tipadas em todas as implementações

**Critério de Aceitação**:
- Todas as configurações tipadas e validadas
- Zero "magic strings" ou números no código
- Configuração centralizada e injetada via DI

---

### 🛡️ **AÇÃO 2.2: Fortalecer Validação de Domínio**

#### Objetivo
Implementar validações robustas nas entidades conforme diretrizes.

#### Tarefas Detalhadas

**2.2.1 Expandir Validações na Entidade Video**
```python
# Adicionar ao src/domain/entities/video.py
def __post_init__(self) -> None:
    if self.created_at is None:
        self.created_at = datetime.now()
    if self.metadata is None:
        self.metadata = {}
    
    # Validações robustas
    self._validate_id()
    self._validate_title()
    self._validate_sources()
    self._validate_duration()

def _validate_id(self) -> None:
    if not self.id or not self.id.strip():
        raise InvalidVideoFormatError("ID do vídeo não pode ser vazio")
    
    if len(self.id) > 255:
        raise InvalidVideoFormatError("ID do vídeo muito longo")

def _validate_title(self) -> None:
    if not self.title or not self.title.strip():
        raise InvalidVideoFormatError("Título do vídeo não pode ser vazio")

def _validate_sources(self) -> None:
    has_file = self.file_path and Path(self.file_path).exists()
    has_url = self.url and self._is_valid_url(self.url)
    
    if not has_file and not has_url:
        raise InvalidVideoFormatError("Vídeo deve ter file_path válido ou URL válida")

def _validate_duration(self) -> None:
    if self.duration < 0:
        raise InvalidVideoFormatError("Duração não pode ser negativa")

def _is_valid_url(self, url: str) -> bool:
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None
```

**2.2.2 Criar Validadores Específicos**
```bash
mkdir -p src/domain/validators
touch src/domain/validators/__init__.py
touch src/domain/validators/video_validators.py
touch src/domain/validators/url_validators.py
```

**2.2.3 Adicionar Testes de Validação**
- [ ] Testar todos os cenários de validação
- [ ] Verificar mensagens de erro específicas
- [ ] Testar edge cases e boundary conditions

**Critério de Aceitação**:
- Impossível criar entidades em estado inválido
- Mensagens de erro específicas e úteis
- 100% de cobertura nos testes de validação

---

## 🎯 FASE 3: APRESENTAÇÃO E INTEGRAÇÃO (Semana 4)

### 🖥️ **AÇÃO 3.1: Refatorar Camada de Apresentação**

#### Objetivo
Limpar lógica procedural e implementar padrão de apresentação limpa.

#### Tarefas Detalhadas

**3.1.1 Criar Comandos Específicos**
```bash
mkdir -p src/presentation/cli/commands
touch src/presentation/cli/commands/__init__.py
touch src/presentation/cli/commands/youtube_command.py
touch src/presentation/cli/commands/local_video_command.py
touch src/presentation/cli/commands/batch_command.py
```

**Implementação Exemplo:**
```python
# src/presentation/cli/commands/youtube_command.py
from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.config.alfredo_config import AlfredoConfig

class YouTubeCommand:
    def __init__(self, config: AlfredoConfig):
        self.config = config
        factory = InfrastructureFactory()
        self.use_case = ProcessYouTubeVideoUseCase(
            video_repository=factory.create_storage(),
            ai_provider=factory.create_ai_provider(),
            downloader=factory.create_video_downloader(),
            extractor=factory.create_audio_extractor()
        )
    
    async def execute(self, url: str, language: str = "pt") -> None:
        try:
            request = ProcessYouTubeVideoRequest(url=url, language=language)
            response = await self.use_case.execute(request)
            print(f"✅ Vídeo processado: {response.video.title}")
        except DownloadFailedError as e:
            print(f"❌ Erro no download: {e}")
        except TranscriptionError as e:
            print(f"❌ Erro na transcrição: {e}")
```

**3.1.2 Refatorar main.py**
```python
# Novo src/main.py (versão limpa)
async def main():
    config = AlfredoConfig()
    config.validate()
    config.create_directories()
    
    args = parse_arguments()
    
    if args.url:
        command = YouTubeCommand(config)
        await command.execute(args.url, args.language)
    elif args.batch:
        command = BatchCommand(config)
        await command.execute(args.batch, args.language)
    elif args.input:
        command = LocalVideoCommand(config)
        await command.execute(args.input, args.language)
    else:
        show_help()
```

**Critério de Aceitação**:
- `main.py` com menos de 50 linhas
- Lógica de negócio completamente separada
- Comandos testáveis independentemente

---

### 🎨 **AÇÃO 3.2: Implementar Padrões de Design Faltantes**

#### Objetivo
Aplicar Strategy, Command e outros padrões conforme diretrizes.

#### Tarefas Detalhadas

**3.2.1 Implementar Strategy Pattern para AI Providers**
```python
# src/application/strategies/ai_strategy.py
from abc import ABC, abstractmethod

class AIStrategy(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str, language: str) -> str:
        pass
    
    @abstractmethod
    async def summarize(self, text: str, context: str) -> str:
        pass

class WhisperStrategy(AIStrategy):
    # Implementação específica
    pass

class GroqStrategy(AIStrategy):
    # Implementação específica
    pass
```

**3.2.2 Implementar Command Pattern para CLI**
```python
# src/presentation/cli/commands/base_command.py
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs) -> None:
        pass
    
    @abstractmethod
    def validate_args(self, *args, **kwargs) -> bool:
        pass
```

**3.2.3 Documentar Padrões Utilizados**
- [ ] Criar documentação de arquitetura
- [ ] Justificar escolha de cada padrão
- [ ] Exemplos de uso e extensão

**Critério de Aceitação**:
- Padrões implementados e documentados
- Facilidade para adicionar novos providers
- Código extensível e manutenível

---

## 🎯 FASE 4: QUALIDADE E ROBUSTEZ (Semana 5)

### 🧪 **AÇÃO 4.1: Expandir Cobertura de Testes**

#### Objetivo
Atingir 80%+ de cobertura e implementar testes BDD.

#### Tarefas Detalhadas

**4.1.1 Implementar Testes BDD**
```bash
mkdir -p tests/bdd
touch tests/bdd/__init__.py
touch tests/bdd/test_youtube_processing.py
```

**Exemplo de Teste BDD:**
```python
# tests/bdd/test_youtube_processing.py
import pytest
from pytest_bdd import scenarios, given, when, then

scenarios('features/youtube_processing.feature')

@given('que tenho uma URL válida do YouTube')
def valid_youtube_url(context):
    context.url = "https://youtube.com/watch?v=dQw4w9WgXcQ"

@when('executo o processamento do vídeo')
async def process_video(context):
    # Implementação do teste
    pass

@then('devo receber uma transcrição válida')
def verify_transcription(context):
    assert context.result.transcription
    assert len(context.result.transcription) > 0
```

**4.1.2 Criar Arquivos Feature**
```gherkin
# tests/bdd/features/youtube_processing.feature
Feature: Processamento de vídeos do YouTube
  
  Scenario: Análise de vídeo válido
    Given que tenho uma URL válida do YouTube
    When executo o processamento do vídeo
    Then devo receber uma transcrição válida
    And devo receber metadados do vídeo
    And o resultado deve ser salvo no repositório
```

**4.1.3 Adicionar Testes de Integração**
- [ ] Testes end-to-end para fluxos completos
- [ ] Testes de performance para operações longas
- [ ] Testes de resiliência para falhas de rede

**Critério de Aceitação**:
- Cobertura de testes ≥ 80%
- Cenários BDD implementados
- Testes servem como documentação viva

---

### 📊 **AÇÃO 4.2: Implementar Métricas de Qualidade**

#### Objetivo
Garantir qualidade contínua conforme diretrizes.

#### Tarefas Detalhadas

**4.2.1 Configurar Ferramentas de Análise**
```bash
# requirements-dev.txt
pylint>=2.15.0
flake8>=5.0.0
black>=22.0.0
isort>=5.10.0
bandit>=1.7.0
coverage>=6.0.0
pytest-cov>=4.0.0
```

**4.2.2 Criar Configurações de Qualidade**
```ini
# .pylintrc
[MASTER]
load-plugins=pylint.extensions.docparams

[MESSAGES CONTROL]
disable=missing-docstring,too-few-public-methods

[FORMAT]
max-line-length=88

[DESIGN]
max-complexity=10
max-args=7
max-locals=15
```

**4.2.3 Implementar Pipeline de Qualidade**
```bash
# Makefile
quality-check:
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	pylint src/
	bandit -r src/
	pytest --cov=src --cov-report=html --cov-fail-under=80
```

**Critério de Aceitação**:
- Todas as métricas dentro dos limites
- Pipeline automatizado funcionando
- Relatórios de qualidade gerados

---

## 📈 MÉTRICAS DE SUCESSO

### Métricas Quantitativas
- [ ] **Cobertura de Testes**: ≥ 80%
- [ ] **Complexidade Ciclomática**: ≤ 10 por função
- [ ] **Linhas por Função**: ≤ 20
- [ ] **Linhas por Classe**: ≤ 200
- [ ] **Duplicação de Código**: ≤ 3%

### Métricas Qualitativas
- [ ] **Zero Violações SOLID**: Verificado por análise estática
- [ ] **Zero Magic Numbers**: Todas as constantes nomeadas
- [ ] **100% Exceções Tipadas**: Nenhuma `Exception` genérica
- [ ] **Injeção de Dependência**: 100% das dependências injetadas
- [ ] **Documentação Atualizada**: Arquitetura e padrões documentados

### Métricas de Manutenibilidade
- [ ] **Facilidade de Extensão**: Novos providers em < 1 hora
- [ ] **Facilidade de Teste**: Novos testes em < 30 minutos
- [ ] **Tempo de Build**: < 2 minutos para todos os checks
- [ ] **Onboarding**: Novo desenvolvedor produtivo em < 1 dia

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

### Esta Semana
1. **Implementar hierarquia de exceções** (Ação 1.1)
2. **Criar factory pattern básico** (Ação 1.2)
3. **Definir interfaces de gateway** (Ação 1.3)

### Próxima Semana
1. **Completar implementações de gateway**
2. **Refatorar configurações**
3. **Fortalecer validações de domínio**

### Validação Contínua
- Executar testes após cada mudança
- Verificar métricas de qualidade diariamente
- Revisar conformidade com diretrizes semanalmente

---

**🎯 Meta Final**: Projeto Alfredo AI 100% conforme às diretrizes arquiteturais mandatórias, servindo como referência de excelência em Clean Architecture para projetos Python.