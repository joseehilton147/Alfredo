# Guia de Extensão - Alfredo AI

Este documento fornece instruções detalhadas para estender o sistema Alfredo AI com novos componentes.

## Índice

1. [Adicionando um Novo AI Provider](#adicionando-um-novo-ai-provider)
2. [Adicionando um Novo Comando CLI](#adicionando-um-novo-comando-cli)
3. [Adicionando um Novo Gateway](#adicionando-um-novo-gateway)
4. [Adicionando Validadores Customizados](#adicionando-validadores-customizados)
5. [Testando Extensões](#testando-extensões)

---

## Adicionando um Novo AI Provider

**Tempo estimado: < 1 hora**

### Passo 1: Implementar a Interface AIStrategy

Crie um novo arquivo em `src/infrastructure/providers/seu_provider_strategy.py`:

```python
from src.application.interfaces.ai_strategy import AIStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError

class SeuProviderStrategy(AIStrategy):
    def __init__(self, config: Optional[AlfredoConfig] = None):
        self.config = config or AlfredoConfig()
        self._strategy_config = self.config.get_provider_config("seu_provider")
        # Configurações específicas do provider
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        # Implementar lógica de transcrição
        pass
    
    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        # Implementar lógica de sumarização
        pass
    
    def get_supported_languages(self) -> list[str]:
        return ["pt", "en", "es"]  # Idiomas suportados
    
    def get_strategy_name(self) -> str:
        return "seu_provider"
    
    def get_configuration(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "supports_transcription": True,
            "supports_summarization": True,
            "api_key_required": True
        }
    
    def is_available(self) -> bool:
        # Verificar se provider está disponível
        return bool(self.api_key)
```

### Passo 2: Adicionar Configurações

Em `src/config/alfredo_config.py`, adicione:

```python
@dataclass
class AlfredoConfig:
    # ... configurações existentes ...
    
    # Configurações do novo provider
    seu_provider_model: str = "modelo-padrao"
    seu_provider_api_key: Optional[str] = field(default_factory=lambda: os.getenv("SEU_PROVIDER_API_KEY"))
    seu_provider_timeout: int = 600

    def get_provider_config(self, provider_name: str) -> dict:
        configs = {
            # ... configurações existentes ...
            "seu_provider": {
                "model": self.seu_provider_model,
                "api_key": self.seu_provider_api_key,
                "timeout": self.seu_provider_timeout
            }
        }
        return configs.get(provider_name, {})
```

### Passo 3: Registrar na Factory

Em `src/infrastructure/factories/infrastructure_factory.py`:

```python
def create_ai_provider(self, provider_type: str = None) -> AIStrategy:
    # ... código existente ...
    elif provider_type == "seu_provider":
        self._instances[cache_key] = SeuProviderStrategy(self._config)
    # ... resto do código ...
```

### Passo 4: Atualizar Imports

Em `src/infrastructure/providers/__init__.py`:

```python
from src.infrastructure.providers.seu_provider_strategy import SeuProviderStrategy

__all__ = [
    # ... providers existentes ...
    "SeuProviderStrategy"
]
```

### Passo 5: Criar Testes

Crie `tests/infrastructure/providers/test_seu_provider_strategy.py`:

```python
import pytest
from unittest.mock import Mock, patch
from src.infrastructure.providers.seu_provider_strategy import SeuProviderStrategy

@pytest.mark.asyncio
async def test_transcribe_success():
    config = Mock()
    config.get_provider_config.return_value = {"api_key": "test_key"}
    
    strategy = SeuProviderStrategy(config)
    
    with patch.object(strategy, '_make_api_request') as mock_request:
        mock_request.return_value = {"text": "Texto transcrito"}
        
        result = await strategy.transcribe("test.wav", "pt")
        
        assert result == "Texto transcrito"

@pytest.mark.asyncio
async def test_summarize_success():
    # Teste similar para sumarização
    pass
```

### Passo 6: Testar Integração

```python
# Teste manual
from src.config.alfredo_config import AlfredoConfig
from src.application.services.ai_strategy_context import AIStrategyContext

config = AlfredoConfig()
config.seu_provider_api_key = "sua_api_key"

context = AIStrategyContext(config)
context.set_strategy("seu_provider")

# Testar transcrição
result = await context.transcribe("audio.wav")
print(f"Transcrição: {result}")
```

---

## Adicionando um Novo Comando CLI

**Tempo estimado: < 30 minutos**

### Passo 1: Criar Classe do Comando

Crie `src/presentation/cli/seu_comando_command.py`:

```python
import argparse
from src.presentation.cli.base_command import Command, CommandMetadata, CommandFlag

class SeuComandoCommand(Command):
    def _initialize_metadata(self) -> None:
        self._metadata = CommandMetadata(
            name="seu_comando",
            description="Descrição do seu comando",
            usage="alfredo seu_comando [opções]",
            examples=[
                "seu_comando --opcao valor",
                "seu_comando --help"
            ],
            category="categoria",
            aliases=["sc", "comando"]
        )
        
        # Definir flags
        self._flags = [
            CommandFlag(
                name="opcao",
                short_name="o",
                description="Descrição da opção",
                type=str,
                required=True
            )
        ]
    
    async def execute_from_parsed_args(self, args: argparse.Namespace) -> Any:
        # Implementar lógica do comando
        print(f"Executando comando com opção: {args.opcao}")
        return {"status": "success", "opcao": args.opcao}
    
    def validate_parsed_args(self, args: argparse.Namespace) -> bool:
        # Validações específicas
        if not args.opcao:
            print("❌ Opção é obrigatória")
            return False
        return True
```

### Passo 2: Descoberta Automática

O comando será descoberto automaticamente pelo `CommandRegistry` se:
- O arquivo termina com `_command.py`
- A classe herda de `Command`
- A classe termina com `Command`

### Passo 3: Testar o Comando

```python
# Teste manual
from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.presentation.cli.command_registry import CommandRegistry

config = AlfredoConfig()
factory = InfrastructureFactory(config)
registry = CommandRegistry(config, factory)

# Verificar se comando foi descoberto
print(registry.get_available_commands())

# Executar comando
command = registry.get_command("seu_comando")
result = await command.execute_with_args(["--opcao", "valor_teste"])
```

---

## Adicionando um Novo Gateway

**Tempo estimado: < 45 minutos**

### Passo 1: Definir Interface

Crie `src/application/gateways/seu_gateway.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class SeuGateway(ABC):
    @abstractmethod
    async def operacao_principal(self, parametro: str) -> str:
        """Operação principal do gateway."""
        pass
    
    @abstractmethod
    async def operacao_secundaria(self, dados: dict) -> List[str]:
        """Operação secundária do gateway."""
        pass
```

### Passo 2: Implementar na Infraestrutura

Crie `src/infrastructure/gateways/sua_implementacao.py`:

```python
from src.application.gateways.seu_gateway import SeuGateway
from src.config.alfredo_config import AlfredoConfig

class SuaImplementacao(SeuGateway):
    def __init__(self, config: AlfredoConfig):
        self.config = config
    
    async def operacao_principal(self, parametro: str) -> str:
        # Implementação específica
        return f"Resultado para {parametro}"
    
    async def operacao_secundaria(self, dados: dict) -> List[str]:
        # Implementação específica
        return [f"Item {k}: {v}" for k, v in dados.items()]
```

### Passo 3: Adicionar à Factory

Em `src/infrastructure/factories/infrastructure_factory.py`:

```python
def create_seu_gateway(self) -> SeuGateway:
    if 'seu_gateway' not in self._instances:
        self._instances['seu_gateway'] = SuaImplementacao(self._config)
    return self._instances['seu_gateway']

def create_all_dependencies(self) -> dict:
    return {
        # ... dependências existentes ...
        'seu_gateway': self.create_seu_gateway()
    }
```

### Passo 4: Usar em Use Cases

```python
class SeuUseCase:
    def __init__(self, seu_gateway: SeuGateway, config: AlfredoConfig):
        self._seu_gateway = seu_gateway
        self._config = config
    
    async def execute(self, request):
        resultado = await self._seu_gateway.operacao_principal(request.parametro)
        return {"resultado": resultado}
```

---

## Adicionando Validadores Customizados

**Tempo estimado: < 20 minutos**

### Passo 1: Criar Validador

Crie `src/domain/validators/seus_validadores.py`:

```python
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError

def validar_formato_customizado(valor: str) -> None:
    """Valida formato customizado."""
    if not valor or len(valor) < 3:
        raise InvalidVideoFormatError(
            "formato_customizado", 
            valor, 
            "deve ter pelo menos 3 caracteres"
        )

def validar_range_numerico(numero: int, min_val: int, max_val: int) -> None:
    """Valida se número está no range especificado."""
    if not min_val <= numero <= max_val:
        raise InvalidVideoFormatError(
            "range_numerico",
            numero,
            f"deve estar entre {min_val} e {max_val}"
        )
```

### Passo 2: Usar em Entidades

```python
from src.domain.validators.seus_validadores import validar_formato_customizado

@dataclass
class SuaEntidade:
    campo_customizado: str
    
    def __post_init__(self):
        validar_formato_customizado(self.campo_customizado)
```

### Passo 3: Atualizar __init__.py

Em `src/domain/validators/__init__.py`:

```python
from src.domain.validators.seus_validadores import (
    validar_formato_customizado,
    validar_range_numerico
)

__all__ = [
    # ... validadores existentes ...
    "validar_formato_customizado",
    "validar_range_numerico"
]
```

---

## Testando Extensões

### Testes Unitários

```python
# tests/test_sua_extensao.py
import pytest
from unittest.mock import Mock

def test_seu_provider_disponivel():
    """Testa se novo provider está disponível."""
    from src.application.services.ai_strategy_context import AIStrategyContext
    
    config = Mock()
    context = AIStrategyContext(config)
    
    assert "seu_provider" in context.get_available_strategies()

def test_seu_comando_descoberto():
    """Testa se novo comando foi descoberto."""
    from src.presentation.cli.command_registry import CommandRegistry
    
    config = Mock()
    factory = Mock()
    registry = CommandRegistry(config, factory)
    
    assert "seu_comando" in registry.get_available_commands()
```

### Testes de Integração

```python
# tests/integration/test_extensoes_integration.py
import pytest

@pytest.mark.asyncio
async def test_fluxo_completo_com_novo_provider():
    """Testa fluxo completo usando novo provider."""
    # Configurar ambiente de teste
    # Executar fluxo completo
    # Verificar resultados
    pass
```

### Validação Manual

```python
# scripts/validar_extensoes.py
async def validar_novo_provider():
    """Valida que novo provider funciona corretamente."""
    try:
        context = AIStrategyContext()
        context.set_strategy("seu_provider")
        
        # Testar transcrição
        result = await context.transcribe("test_audio.wav")
        print(f"✅ Transcrição: {len(result)} caracteres")
        
        # Testar sumarização
        summary = await context.summarize("Texto de teste")
        print(f"✅ Sumarização: {len(summary)} caracteres")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(validar_novo_provider())
    print(f"Validação: {'✅ SUCESSO' if success else '❌ FALHA'}")
```

---

## Checklist de Extensão

### Para Novo AI Provider:
- [ ] Implementar interface `AIStrategy`
- [ ] Adicionar configurações em `AlfredoConfig`
- [ ] Registrar na `InfrastructureFactory`
- [ ] Atualizar imports em `__init__.py`
- [ ] Criar testes unitários
- [ ] Testar integração com `AIStrategyContext`
- [ ] Validar tempo de implementação < 1 hora

### Para Novo Comando CLI:
- [ ] Herdar de `Command`
- [ ] Implementar `_initialize_metadata()`
- [ ] Implementar `execute_from_parsed_args()`
- [ ] Salvar como `*_command.py`
- [ ] Testar descoberta automática
- [ ] Validar help automático
- [ ] Validar tempo de implementação < 30 minutos

### Para Novo Gateway:
- [ ] Definir interface abstrata
- [ ] Implementar classe concreta
- [ ] Adicionar à factory
- [ ] Usar em Use Cases
- [ ] Criar testes com mocks
- [ ] Validar tempo de implementação < 45 minutos

---

## Exemplos Práticos

### Exemplo 1: Provider OpenAI

```python
# Implementação real de um provider OpenAI
class OpenAIStrategy(AIStrategy):
    def __init__(self, config: AlfredoConfig):
        self.client = openai.OpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return transcript.text
    
    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em resumos."},
                {"role": "user", "content": f"Resuma este texto: {text}"}
            ]
        )
        return response.choices[0].message.content
```

### Exemplo 2: Comando de Análise de Sentimento

```python
class SentimentCommand(Command):
    def _initialize_metadata(self) -> None:
        self._metadata = CommandMetadata(
            name="sentiment",
            description="Analisa sentimento de transcrições",
            usage="alfredo sentiment <video_id>",
            category="analysis"
        )
    
    async def execute_from_parsed_args(self, args: argparse.Namespace) -> Any:
        # Carregar transcrição
        storage = self.factory.create_storage()
        transcription = await storage.load_transcription(args.video_id)
        
        # Analisar sentimento
        ai_provider = self.factory.create_ai_provider()
        sentiment = await ai_provider.analyze_sentiment(transcription)
        
        print(f"Sentimento: {sentiment}")
        return {"video_id": args.video_id, "sentiment": sentiment}
```

---

## Conclusão

O sistema Alfredo AI foi projetado para ser altamente extensível. Seguindo estes guias, você pode:

- **Adicionar novos AI providers em < 1 hora**
- **Criar novos comandos CLI em < 30 minutos**
- **Implementar novos gateways em < 45 minutos**
- **Adicionar validadores customizados em < 20 minutos**

A arquitetura baseada em padrões de design (Strategy, Command, Factory) e princípios SOLID garante que extensões sejam:

- **Isoladas**: Não afetam código existente
- **Testáveis**: Podem ser testadas independentemente
- **Configuráveis**: Integram-se ao sistema de configuração
- **Descobríveis**: São encontradas automaticamente pelo sistema

Para mais informações, consulte:
- `docs/DESIGN_PATTERNS.md` - Detalhes dos padrões implementados
- `docs/ARCHITECTURE.md` - Visão geral da arquitetura
- `examples/new_provider_template.py` - Template para novos providers
- `examples/design_patterns_demo.py` - Demonstrações práticas