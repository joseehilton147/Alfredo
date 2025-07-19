# Documento de Design - CLI Interativa do Alfredo AI

## Visão Geral

A CLI interativa do Alfredo AI será implementada como uma camada de apresentação elegante e intuitiva que se integra perfeitamente com a arquitetura Clean Architecture existente. O design foca em proporcionar uma experiência visual rica, inspirada no Claude Code, utilizando bibliotecas Python modernas para criar interfaces de terminal sofisticadas.

## Arquitetura

### Estrutura de Camadas

```
src/presentation/
├── cli/
│   ├── __init__.py
│   ├── interactive_cli.py          # Ponto de entrada principal
│   ├── components/                 # Componentes reutilizáveis da UI
│   │   ├── __init__.py
│   │   ├── menu.py                # Menus interativos
│   │   ├── progress.py            # Barras de progresso
│   │   ├── file_browser.py        # Navegador de arquivos
│   │   ├── input_field.py         # Campos de entrada
│   │   └── status_display.py      # Exibição de status
│   ├── screens/                   # Telas da aplicação
│   │   ├── __init__.py
│   │   ├── main_menu.py           # Menu principal
│   │   ├── local_video_screen.py  # Processamento local
│   │   ├── youtube_screen.py      # Processamento YouTube
│   │   ├── batch_screen.py        # Processamento em lote
│   │   ├── settings_screen.py     # Configurações
│   │   ├── results_screen.py      # Visualização de resultados
│   │   └── help_screen.py         # Sistema de ajuda
│   ├── themes/                    # Temas visuais
│   │   ├── __init__.py
│   │   ├── default_theme.py       # Tema padrão
│   │   └── colors.py              # Definições de cores
│   └── utils/                     # Utilitários da CLI
│       ├── __init__.py
│       ├── keyboard.py            # Manipulação de teclado
│       ├── terminal.py            # Utilitários do terminal
│       └── validators.py          # Validadores de entrada
```

### Dependências Externas

**Bibliotecas Principais:**

- **Rich**: Framework para interfaces de terminal ricas e elegantes
- **Textual**: Framework para aplicações TUI (Text User Interface) modernas
- **Click**: Para integração com comandos CLI tradicionais
- **Prompt Toolkit**: Para entrada interativa avançada

**Bibliotecas de Suporte:**

- **Pydantic**: Validação de dados de entrada
- **Asyncio**: Operações assíncronas para responsividade
- **Pathlib**: Manipulação moderna de caminhos

## Componentes e Interfaces

### 1. InteractiveCLI (Classe Principal)

```python
class InteractiveCLI:
    """Controlador principal da CLI interativa."""

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        self.theme = DefaultTheme()
        self.current_screen = None
        self.screen_stack = []

    async def run(self) -> None:
        """Executa a CLI interativa."""

    def navigate_to(self, screen: Screen) -> None:
        """Navega para uma nova tela."""

    def go_back(self) -> None:
        """Retorna à tela anterior."""
```

### 2. Screen (Classe Base Abstrata)

```python
from abc import ABC, abstractmethod

class Screen(ABC):
    """Classe base para todas as telas da CLI."""

    def __init__(self, cli: InteractiveCLI):
        self.cli = cli
        self.theme = cli.theme

    @abstractmethod
    async def render(self) -> None:
        """Renderiza a tela."""

    @abstractmethod
    async def handle_input(self, key: str) -> None:
        """Manipula entrada do usuário."""

    async def on_enter(self) -> None:
        """Chamado quando a tela é exibida."""

    async def on_exit(self) -> None:
        """Chamado quando a tela é fechada."""
```

### 3. Menu Component

```python
class InteractiveMenu:
    """Componente de menu interativo reutilizável."""

    def __init__(self, title: str, options: List[MenuOption], theme: Theme):
        self.title = title
        self.options = options
        self.selected_index = 0
        self.theme = theme

    def render(self) -> Panel:
        """Renderiza o menu usando Rich."""

    def handle_key(self, key: str) -> Optional[MenuOption]:
        """Manipula teclas e retorna opção selecionada."""
```

### 4. FileExplorer Component

```python
class FileExplorer:
    """Navegador de arquivos interativo."""

    def __init__(self, initial_path: Path, file_filter: Callable[[Path], bool]):
        self.current_path = initial_path
        self.file_filter = file_filter
        self.selected_index = 0

    def render(self) -> Panel:
        """Renderiza o explorador de arquivos."""

    def navigate_to(self, path: Path) -> None:
        """Navega para um diretório."""

    def get_selected_file(self) -> Optional[Path]:
        """Retorna o arquivo selecionado."""
```

### 5. ProgressDisplay Component

```python
class ProgressDisplay:
    """Exibição elegante de progresso."""

    def __init__(self, title: str, total: int = 100):
        self.title = title
        self.total = total
        self.current = 0
        self.status = "Iniciando..."

    def update(self, progress: int, status: str = None) -> None:
        """Atualiza o progresso."""

    def render(self) -> Panel:
        """Renderiza a barra de progresso."""
```

## Modelos de Dados

### MenuOption

```python
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class MenuOption:
    """Opção de menu."""
    key: str
    label: str
    description: str
    icon: str
    action: Callable[[], None]
    enabled: bool = True
    shortcut: Optional[str] = None
```

### Theme

```python
@dataclass
class Theme:
    """Configurações visuais da CLI."""
    primary_color: str = "bright_blue"
    secondary_color: str = "bright_green"
    accent_color: str = "bright_yellow"
    error_color: str = "bright_red"
    success_color: str = "bright_green"
    text_color: str = "white"
    background_color: str = "black"
    border_style: str = "rounded"
```

### CLIState

```python
@dataclass
class CLIState:
    """Estado global da CLI."""
    current_screen: str
    settings: Dict[str, Any]
    recent_files: List[Path]
    processing_queue: List[ProcessingTask]
    last_results: List[TranscriptionResult]
```

## Tratamento de Erros

### ErrorHandler

```python
class ErrorHandler:
    """Manipulador centralizado de erros."""

    def __init__(self, theme: Theme):
        self.theme = theme

    def display_error(self, error: Exception, context: str = None) -> None:
        """Exibe erro de forma elegante."""

    def display_warning(self, message: str) -> None:
        """Exibe aviso."""

    def display_success(self, message: str) -> None:
        """Exibe mensagem de sucesso."""
```

### Estratégias de Erro

1. **Erros de Validação**: Feedback imediato com sugestões
2. **Erros de Rede**: Retry automático com indicador visual
3. **Erros de Arquivo**: Navegação alternativa e sugestões
4. **Erros de Processamento**: Logs detalhados e opções de recuperação

## Estratégia de Testes

### Estrutura de Testes

```
tests/presentation/cli/
├── __init__.py
├── test_interactive_cli.py
├── components/
│   ├── test_menu.py
│   ├── test_progress.py
│   ├── test_file_browser.py
│   └── test_input_field.py
├── screens/
│   ├── test_main_menu.py
│   ├── test_local_video_screen.py
│   └── test_youtube_screen.py
├── fixtures/
│   ├── mock_terminal.py
│   ├── sample_videos.py
│   └── test_data.py
└── integration/
    ├── test_full_workflow.py
    └── test_error_scenarios.py
```

### Tipos de Testes

1. **Testes Unitários**: Componentes individuais
2. **Testes de Integração**: Fluxos completos
3. **Testes de Interface**: Simulação de entrada do usuário
4. **Testes de Performance**: Responsividade da interface

### Mocking Strategy

```python
class MockTerminal:
    """Mock do terminal para testes."""

    def __init__(self):
        self.output = []
        self.input_queue = []

    def write(self, text: str) -> None:
        self.output.append(text)

    def read_key(self) -> str:
        return self.input_queue.pop(0) if self.input_queue else ""
```

## Integração com Sistema Existente

### ApplicationContext

```python
class ApplicationContext:
    """Contexto da aplicação para injeção de dependências."""

    def __init__(self):
        self.video_repository = JsonVideoRepository()
        self.whisper_provider = WhisperProvider()
        self.transcribe_use_case = TranscribeAudioUseCase(
            self.video_repository,
            self.whisper_provider
        )
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Carrega configurações do .env."""
```

### Adaptadores

```python
class CLIToUseCaseAdapter:
    """Adapta chamadas da CLI para use cases."""

    def __init__(self, context: ApplicationContext):
        self.context = context

    async def process_local_video(self, file_path: Path, language: str) -> ProcessingResult:
        """Processa vídeo local através do use case."""

    async def process_youtube_video(self, url: str, language: str) -> ProcessingResult:
        """Processa vídeo do YouTube através do use case."""
```

## Performance e Otimização

### Estratégias de Performance

1. **Renderização Assíncrona**: UI responsiva durante processamento
2. **Lazy Loading**: Carregamento sob demanda de dados
3. **Caching**: Cache de resultados e configurações
4. **Throttling**: Limitação de atualizações de UI

### Monitoramento

```python
class PerformanceMonitor:
    """Monitor de performance da CLI."""

    def __init__(self):
        self.render_times = []
        self.response_times = []

    def track_render_time(self, screen: str, duration: float) -> None:
        """Rastreia tempo de renderização."""

    def get_performance_report(self) -> Dict[str, float]:
        """Retorna relatório de performance."""
```

## Configuração e Personalização

### Settings Manager

```python
class SettingsManager:
    """Gerenciador de configurações da CLI."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.settings = self._load_settings()

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém configuração."""

    def set(self, key: str, value: Any) -> None:
        """Define configuração."""

    def save(self) -> None:
        """Salva configurações."""
```

### Configurações Disponíveis

- **Tema**: Cores e estilo visual
- **Idioma**: Idioma padrão para transcrição
- **Modelo Whisper**: Modelo padrão do Whisper
- **Diretórios**: Caminhos padrão para entrada e saída
- **Atalhos**: Personalizações de teclado
- **Comportamento**: Confirmações e avisos

## Acessibilidade

### Recursos de Acessibilidade

1. **Navegação por Teclado**: Suporte completo sem mouse
2. **Alto Contraste**: Temas para visibilidade melhorada
3. **Leitores de Tela**: Compatibilidade com tecnologias assistivas
4. **Atalhos Consistentes**: Padrões de navegação familiares

### Implementação

```python
class AccessibilityHelper:
    """Utilitários de acessibilidade."""

    def __init__(self, theme: Theme):
        self.theme = theme

    def get_high_contrast_theme(self) -> Theme:
        """Retorna tema de alto contraste."""

    def announce_screen_change(self, screen_name: str) -> None:
        """Anuncia mudança de tela para leitores."""
```

## Internacionalização

### Suporte a Idiomas

```python
class I18nManager:
    """Gerenciador de internacionalização."""

    def __init__(self, locale: str = "pt_BR"):
        self.locale = locale
        self.translations = self._load_translations()

    def t(self, key: str, **kwargs) -> str:
        """Traduz texto."""

    def set_locale(self, locale: str) -> None:
        """Define idioma."""
```

### Estrutura de Traduções

```
src/presentation/cli/locales/
├── pt_BR/
│   ├── common.json
│   ├── menus.json
│   └── messages.json
├── en_US/
│   ├── common.json
│   ├── menus.json
│   └── messages.json
└── es_ES/
    ├── common.json
    ├── menus.json
    └── messages.json
```
