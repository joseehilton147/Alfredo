#!/usr/bin/env python3
"""
Demonstração dos padrões de design implementados no Alfredo AI.

Este arquivo mostra como usar e estender os padrões implementados:
- Strategy Pattern para AI providers
- Command Pattern para CLI
- Factory Pattern para dependências
- Dependency Injection

Execute: python examples/design_patterns_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path para importações
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.alfredo_config import AlfredoConfig
from src.infrastructure.factories.infrastructure_factory import InfrastructureFactory
from src.application.services.ai_strategy_context import AIStrategyContext, StrategyType
from src.presentation.cli.command_registry import CommandRegistry
from src.presentation.cli.youtube_command import YouTubeCommand


async def demo_strategy_pattern():
    """Demonstra o uso do Strategy Pattern para AI providers."""
    print("=" * 60)
    print("DEMONSTRAÇÃO: STRATEGY PATTERN - AI PROVIDERS")
    print("=" * 60)
    
    # Configurar contexto
    config = AlfredoConfig()
    context = AIStrategyContext(config)
    
    print(f"Estratégias disponíveis: {context.get_available_strategies()}")
    print()
    
    # Demonstrar seleção automática da melhor estratégia
    print("1. Seleção automática da melhor estratégia:")
    try:
        best_for_transcription = context.get_best_strategy_for_task("transcription")
        print(f"   Melhor para transcrição: {best_for_transcription}")
        
        best_for_summarization = context.get_best_strategy_for_task("summarization")
        print(f"   Melhor para sumarização: {best_for_summarization}")
    except Exception as e:
        print(f"   Erro: {e}")
    print()
    
    # Demonstrar testabilidade e intercambiabilidade
    print("4. Testabilidade e Intercambiabilidade:")
    print("   O Strategy Pattern permite:")
    print("   - ✅ Testes unitários isolados para cada estratégia")
    print("   - ✅ Comportamento polimórfico validado")
    print("   - ✅ Extensibilidade testada com mock providers")
    print("   - ✅ Performance e concorrência validadas")
    print("   - ✅ Configuração e validação automáticas")
    print("   Veja: tests/infrastructure/providers/test_strategy_pattern.py")
    print()
    
    # Demonstrar informações das estratégias
    print("2. Informações das estratégias:")
    for strategy_name in context.get_available_strategies():
        try:
            info = context.get_strategy_info(strategy_name)
            print(f"   {strategy_name}:")
            print(f"     - Suporta transcrição: {info['configuration'].get('supports_transcription', True)}")
            print(f"     - Suporta sumarização: {info['configuration'].get('supports_summarization', False)}")
            print(f"     - Disponível: {info['is_available']}")
        except Exception as e:
            print(f"     Erro ao obter info: {e}")
    print()
    
    # Demonstrar troca dinâmica de estratégia
    print("3. Troca dinâmica de estratégia:")
    try:
        current = context.get_current_strategy()
        print(f"   Estratégia atual: {current.get_strategy_name()}")
        
        # Tentar trocar para outra estratégia
        available = context.get_available_strategies()
        if len(available) > 1:
            new_strategy = available[1] if available[0] == current.get_strategy_name() else available[0]
            context.set_strategy(new_strategy)
            print(f"   Nova estratégia: {context.get_current_strategy().get_strategy_name()}")
        else:
            print("   Apenas uma estratégia disponível")
    except Exception as e:
        print(f"   Erro: {e}")
    print()


def demo_command_pattern():
    """Demonstra o uso do Command Pattern para CLI."""
    print("=" * 60)
    print("DEMONSTRAÇÃO: COMMAND PATTERN - CLI")
    print("=" * 60)
    
    # Configurar registry
    config = AlfredoConfig()
    factory = InfrastructureFactory(config)
    registry = CommandRegistry(config, factory)
    
    print("1. Comandos disponíveis:")
    commands = registry.get_available_commands()
    for name, description in commands.items():
        print(f"   {name}: {description}")
    print()
    
    print("2. Aliases disponíveis:")
    aliases = registry.get_aliases()
    if aliases:
        for alias, command in aliases.items():
            print(f"   {alias} -> {command}")
    else:
        print("   Nenhum alias configurado")
    print()
    
    print("3. Comandos por categoria:")
    categories = registry.get_all_categories()
    for category in categories:
        commands_in_category = registry.get_commands_by_category(category)
        print(f"   {category}: {', '.join(commands_in_category)}")
    print()
    
    print("4. Help automático do comando YouTube:")
    try:
        youtube_command = registry.get_command("youtube")
        help_text = youtube_command.get_help_text()
        print(help_text)
    except Exception as e:
        print(f"   Erro: {e}")
    print()
    
    print("5. Busca por padrão:")
    matches = registry.find_command_by_pattern("you")
    print(f"   Comandos que contêm 'you': {matches}")
    print()


def demo_factory_pattern():
    """Demonstra o uso do Factory Pattern."""
    print("=" * 60)
    print("DEMONSTRAÇÃO: FACTORY PATTERN")
    print("=" * 60)
    
    config = AlfredoConfig()
    factory = InfrastructureFactory(config)
    
    print("1. Criação de dependências individuais:")
    try:
        downloader = factory.create_video_downloader()
        print(f"   Video Downloader: {type(downloader).__name__}")
        
        extractor = factory.create_audio_extractor()
        print(f"   Audio Extractor: {type(extractor).__name__}")
        
        storage = factory.create_storage()
        print(f"   Storage: {type(storage).__name__}")
        
        ai_provider = factory.create_ai_provider()
        print(f"   AI Provider: {type(ai_provider).__name__}")
    except Exception as e:
        print(f"   Erro: {e}")
    print()
    
    print("2. Criação de todas as dependências:")
    try:
        all_deps = factory.create_all_dependencies()
        print("   Dependências criadas:")
        for name, instance in all_deps.items():
            print(f"     {name}: {type(instance).__name__}")
    except Exception as e:
        print(f"   Erro: {e}")
    print()
    
    print("3. Cache de instâncias (singleton):")
    try:
        # Criar mesma dependência duas vezes
        provider1 = factory.create_ai_provider("whisper")
        provider2 = factory.create_ai_provider("whisper")
        
        print(f"   Primeira instância: {id(provider1)}")
        print(f"   Segunda instância: {id(provider2)}")
        print(f"   São a mesma instância: {provider1 is provider2}")
    except Exception as e:
        print(f"   Erro: {e}")
    print()


def demo_dependency_injection():
    """Demonstra injeção de dependência."""
    print("=" * 60)
    print("DEMONSTRAÇÃO: DEPENDENCY INJECTION")
    print("=" * 60)
    
    config = AlfredoConfig()
    factory = InfrastructureFactory(config)
    
    print("1. Use Case com dependências injetadas:")
    try:
        from src.application.use_cases.process_youtube_video import ProcessYouTubeVideoUseCase
        
        # Criar dependências
        dependencies = factory.create_all_dependencies()
        
        # Injetar no Use Case
        use_case = ProcessYouTubeVideoUseCase(**dependencies)
        
        print("   Use Case criado com dependências:")
        print(f"     Config: {type(use_case._config).__name__}")
        print(f"     Downloader: {type(use_case._downloader).__name__}")
        print(f"     Extractor: {type(use_case._extractor).__name__}")
        print(f"     AI Provider: {type(use_case._ai_provider).__name__}")
        print(f"     Storage: {type(use_case._storage).__name__}")
        
    except Exception as e:
        print(f"   Erro: {e}")
    print()
    
    print("2. Command com dependências injetadas:")
    try:
        youtube_command = YouTubeCommand(config, factory)
        
        print("   Command criado com dependências:")
        print(f"     Config: {type(youtube_command.config).__name__}")
        print(f"     Factory: {type(youtube_command.factory).__name__}")
        
        # Mostrar metadados
        metadata = youtube_command.get_metadata()
        print(f"     Nome: {metadata.name}")
        print(f"     Categoria: {metadata.category}")
        print(f"     Aliases: {metadata.aliases}")
        
    except Exception as e:
        print(f"   Erro: {e}")
    print()


def demo_extensibility():
    """Demonstra como estender o sistema com novos componentes."""
    print("=" * 60)
    print("DEMONSTRAÇÃO: EXTENSIBILIDADE")
    print("=" * 60)
    
    print("1. Como adicionar um novo AI Provider:")
    print("""
   # Passo 1: Implementar a interface AIStrategy
   class NovoProviderStrategy(AIStrategy):
       async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
           # Implementação específica
           pass
       
       async def summarize(self, text: str, context: Optional[str] = None) -> str:
           # Implementação específica
           pass
       
       def get_strategy_name(self) -> str:
           return "novo_provider"
   
   # Passo 2: Registrar na factory
   def create_ai_provider(self, provider_type: str = None) -> AIStrategy:
       # ... código existente ...
       elif provider_type == "novo_provider":
           self._instances[cache_key] = NovoProviderStrategy(self._config)
   
   # Passo 3: Adicionar configuração
   @dataclass
   class AlfredoConfig:
       # ... configurações existentes ...
       novo_provider_api_key: Optional[str] = None
   
   # Tempo estimado: < 1 hora
   """)
    
    print("2. Como adicionar um novo Command:")
    print("""
   # Passo 1: Criar classe que herda de Command
   class NovoCommand(Command):
       def _initialize_metadata(self) -> None:
           self._metadata = CommandMetadata(
               name="novo",
               description="Novo comando de exemplo",
               category="exemplo"
           )
       
       async def execute_from_parsed_args(self, args: argparse.Namespace) -> Any:
           # Implementação específica
           pass
   
   # Passo 2: Salvar como novo_command.py no diretório CLI
   # O comando será descoberto automaticamente pelo CommandRegistry
   
   # Tempo estimado: < 30 minutos
   """)
    
    print("3. Como adicionar um novo Gateway:")
    print("""
   # Passo 1: Definir interface na camada Application
   class NovoGateway(ABC):
       @abstractmethod
       async def nova_operacao(self, parametro: str) -> str:
           pass
   
   # Passo 2: Implementar na camada Infrastructure
   class NovaImplementacao(NovoGateway):
       async def nova_operacao(self, parametro: str) -> str:
           # Implementação específica
           pass
   
   # Passo 3: Adicionar à factory
   def create_novo_gateway(self) -> NovoGateway:
       return NovaImplementacao(self._config)
   
   # Tempo estimado: < 45 minutos
   """)


async def main():
    """Executa todas as demonstrações."""
    print("DEMONSTRAÇÃO DOS PADRÕES DE DESIGN - ALFREDO AI")
    print("=" * 60)
    print()
    
    try:
        await demo_strategy_pattern()
        demo_command_pattern()
        demo_factory_pattern()
        demo_dependency_injection()
        demo_extensibility()
        
        print("=" * 60)
        print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("Para mais informações, consulte:")
        print("- docs/DESIGN_PATTERNS.md")
        print("- docs/ARCHITECTURE.md")
        print("- docs/VALIDATORS.md")
        
    except Exception as e:
        print(f"Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())