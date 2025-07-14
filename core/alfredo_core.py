#!/usr/bin/env python3
"""
🤖 ALFREDO AI - CORE SYSTEM
============================
Sistema central do assistente pessoal Alfredo
Gerencia comandos e módulos de forma modular
"""

import os
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.interfaces import ICoreOperations, IAIProvider, ProviderNotFoundError, CommandNotFoundError
from core.provider_factory import ProviderFactory


class AlfredoCore(ICoreOperations):
    """Sistema central do Alfredo - Gerenciador de comandos.
    
    Implementa ICoreOperations para fornecer operações centrais
    do sistema com injeção de dependência e desacoplamento.
    """
    
    def __init__(self, provider_factory: Optional[ProviderFactory] = None):
        self.work_dir = os.getcwd()
        self.project_dir = Path(__file__).parent.parent
        self.commands = {}
        self.provider_factory = provider_factory or ProviderFactory
        self.load_commands()
    
    def handle_error(self, error: Exception) -> None:
        """Trata exceções de acordo com políticas definidas.
        
        Args:
            error: Exceção a ser tratada
        """
        if isinstance(error, ProviderNotFoundError):
            print(f"❌ Erro de Provedor: {error}")
            available = self.provider_factory.list_providers()
            if available:
                print(f"💡 Provedores disponíveis: {', '.join(available)}")
            else:
                print("💡 Nenhum provedor de IA configurado")
        elif isinstance(error, CommandNotFoundError):
            print(f"❌ Comando não encontrado: {error}")
            self.show_available_commands()
        else:
            print(f"❌ Erro inesperado: {error}")
            if hasattr(error, '__traceback__'):
                import traceback
                traceback.print_exc()
    
    def get_provider(self, provider_name: str) -> IAIProvider:
        """Obtém instância de provedor de IA configurado.
        
        Args:
            provider_name: Nome do provedor (ex: 'groq')
            
        Returns:
            Instância do provedor de IA
            
        Raises:
            ProviderNotFoundError: Se o provedor não estiver registrado
        """
        try:
            return self.provider_factory.create(provider_name)
        except ProviderNotFoundError as e:
            self.handle_error(e)
            raise
    
    def list_commands(self) -> Dict[str, Dict[str, str]]:
        """Lista todos os comandos disponíveis.
        
        Returns:
            Dicionário com comandos e suas informações
        """
        return self.commands.copy()
    
    def execute_command(self, command: str, args: List[str] = None) -> Any:
        """Executa um comando com argumentos fornecidos.
        
        Args:
            command: Nome do comando
            args: Lista de argumentos
            
        Returns:
            Resultado da execução do comando
            
        Raises:
            CommandNotFoundError: Se o comando não existir
        """
        if command not in self.commands:
            error = CommandNotFoundError(f"Comando '{command}' não encontrado")
            self.handle_error(error)
            raise error
        
        cmd_info = self.commands[command]
        args = args or []
        
        try:
            # Executa comando através do módulo
            if "module" in cmd_info:
                module = importlib.import_module(cmd_info["module"])
                if "function" in cmd_info:
                    func = getattr(module, cmd_info["function"])
                    return func(*args)
                elif hasattr(module, 'main'):
                    return module.main(*args)
                else:
                    raise AttributeError(f"Módulo {cmd_info['module']} não possui função 'main'")
            else:
                raise ValueError(f"Comando {command} mal configurado")
                
        except Exception as e:
            self.handle_error(e)
            raise
    
    def show_available_commands(self) -> None:
        """Exibe comandos disponíveis."""
        print("📋 Comandos disponíveis:")
        for cmd, info in self.commands.items():
            desc = info.get('description', 'Sem descrição')
            print(f"  {cmd}: {desc}")

    def show_banner(self):
        """Exibe banner do Alfredo"""
        print("🤖 " + "=" * 50)
        print("   ALFREDO AI - Assistente Pessoal")
        print("   Olá! Como posso ajudá-lo hoje?")
        print("=" * 52)
    
    def load_commands(self):
        """Carrega todos os comandos disponíveis"""
        # Comandos built-in
        self.commands = {
            "resumir-video": {
                "description": "📹 Analisar e resumir vídeos locais",
                "module": "commands.video.local_video",
                "help": "Extrai frames-chave de vídeos e gera resumos usando IA"
            },
            "limpar": {
                "description": "🧹 Limpar arquivos e pastas",
                "module": "commands.clean_command",
                "help": "Sistema de limpeza com diferentes níveis"
            },
            "groq-status": {
                "description": "🔍 Verificar status da API Groq",
                "module": "commands.groq_status",
                "help": "Mostra status atual da API Groq e rate limits"
            },
            "info-pc": {
                "description": "💻 Exibir informações do PC",
                "module": "commands.pc_info",
                "help": "Exibe informações detalhadas do sistema"
            },
            "configurar-modelos": {
                "description": "🧠 Configurar modelos de IA",
                "module": "commands.model_config_command",
                "help": "Descobre e configura automaticamente os melhores modelos"
            },
            "testes": {
                "description": "🧪 Executar testes do sistema",
                "module": "commands.test_runner",
                "help": "Executa bateria completa de testes"
            },
            "test": {
                "description": "🧪 Executar diagnóstico do sistema",
                "module": "core.alfredo_core",
                "function": "run_diagnostics",
                "help": "Verifica se todas as dependências estão funcionando"
            }
        }
        
        # Carrega comandos externos da pasta commands/
        self._load_external_commands()
    
    def _load_external_commands(self):
        """Carrega comandos de módulos externos"""
        commands_dir = self.project_dir / "commands"
        
        if not commands_dir.exists():
            return
        
        # Carrega comandos do diretório principal commands/
        for file_path in commands_dir.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "__init__.py":
                continue
                
            module_name = file_path.stem
            try:
                # Usa importlib para carregar o módulo sem modificar sys.path
                spec = importlib.util.spec_from_file_location(f"commands.{module_name}", file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'COMMAND_INFO'):
                        command_info = module.COMMAND_INFO
                        self.commands[command_info['name']] = {
                            "description": command_info['description'],
                            "module": f"commands.{module_name}",
                        "function": command_info.get('function', 'main'),
                        "help": command_info.get('help', 'Sem descrição disponível'),
                        "category": command_info.get('category', 'geral')
                    }
            except Exception as e:
                print(f"⚠️ Erro ao carregar comando {module_name}: {e}")
        
        # Carrega comandos de subdiretórios (como commands/video/)
        for sub_dir in commands_dir.iterdir():
            if sub_dir.is_dir() and not sub_dir.name.startswith('_'):
                for file_path in sub_dir.glob("*.py"):
                    if file_path.name.startswith("_") or file_path.name == "__init__.py":
                        continue
                        
                    module_name = file_path.stem
                    try:
                        # Importa usando caminho completo para evitar conflitos
                        spec = importlib.util.spec_from_file_location(
                            f"{sub_dir.name}.{module_name}", file_path
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'COMMAND_INFO'):
                            command_info = module.COMMAND_INFO
                            self.commands[command_info['name']] = {
                                "description": command_info['description'],
                                "module": module,
                                "function": command_info.get('function', 'main'),
                                "help": command_info.get('help', 'Sem descrição disponível'),
                                "category": command_info.get('category', sub_dir.name)
                            }
                    except Exception as e:
                        print(f"⚠️ Erro ao carregar {sub_dir.name}/{module_name}: {e}")
    
    def show_commands_list(self):
        """Mostra lista de comandos disponíveis de forma não-interativa"""
        self.show_banner()
        print("\n📋 COMANDOS DISPONÍVEIS:")
        print("-" * 50)
        
        for i, (cmd, info) in enumerate(self.commands.items(), 1):
            if cmd == 'test':
                continue
            print(f"  {cmd}")
            print(f"    {info['description']}")
            print(f"    💡 {info['help']}")
            print()
        
        print("📖 COMANDOS ESPECIAIS:")
        print("  test      - 🧪 Executar diagnóstico do sistema")
        print("  --help    - ❓ Mostrar esta ajuda")
        print("  --version - 📋 Mostrar versão")
        print()
        print("💡 USO: Alfredo <comando>")
        print("   Exemplo: Alfredo resumir-video")
    
    def show_interactive_menu(self):
        """Exibe menu interativo apenas em terminais apropriados"""
        self.show_banner()
        print("\n📋 COMANDOS DISPONÍVEIS:")
        print("-" * 40)
        
        commands_list = [cmd for cmd in self.commands.keys() if cmd != 'test']
        
        for i, cmd in enumerate(commands_list, 1):
            info = self.commands[cmd]
            print(f"  [{i}] {cmd}")
            print(f"      {info['description']}")
            print()
        
        print("📖 COMANDOS ESPECIAIS:")
        print("  [t] test    - 🧪 Executar diagnóstico")
        print("  [h] help    - ❓ Mostrar ajuda")
        print("  [q] quit    - 🚪 Sair")
        print()
        
        while True:
            try:
                choice = input("🤖 Alfredo: O que deseja fazer? ").strip().lower()
                
                if choice in ['q', 'quit', 'sair', 'exit']:
                    print("🤖 Alfredo: Até logo! 👋")
                    break
                elif choice in ['h', 'help', 'ajuda']:
                    self.show_commands_list()
                elif choice in ['t', 'test', 'teste']:
                    self.run_diagnostics()
                elif choice.isdigit():
                    # Seleção por número
                    idx = int(choice) - 1
                    if 0 <= idx < len(commands_list):
                        selected_cmd = commands_list[idx]
                        print(f"\n🚀 Executando: {selected_cmd}")
                        self.execute_command(selected_cmd)
                        break  # Sai após executar comando
                    else:
                        print("❌ Número inválido!")
                elif choice in self.commands:
                    print(f"\n🚀 Executando: {choice}")
                    self.execute_command(choice)
                    break  # Sai após executar comando
                else:
                    print("❌ Comando não reconhecido. Digite 'h' para ajuda.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n🤖 Alfredo: Até logo! 👋")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                break
    
    def run_diagnostics(self):
        """Executa diagnóstico completo do sistema"""
        print("\n🔍 ALFREDO AI - DIAGNÓSTICO DO SISTEMA")
        print("=" * 45)
        print("🤖 Verificando se todos os meus componentes estão funcionando...")
        
        all_ok = True
        
        # Testa Python
        import sys
        print(f"🐍 Python: {sys.version.split()[0]} ✅")
        
        # Testa dependências básicas
        dependencies = ['requests', 'tqdm', 'scenedetect']
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"📦 {dep}: ✅")
            except ImportError:
                print(f"📦 {dep}: ❌")
                all_ok = False
        
        # Testa PySceneDetect
        try:
            import scenedetect
            print("🎬 PySceneDetect: ✅")
        except ImportError:
            print("🎬 PySceneDetect: ❌")
            all_ok = False
        
        # Testa Groq API
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                print("🤖 Groq API: ✅")
            else:
                print("🤖 Groq API: ❌ (Chave não configurada)")
                all_ok = False
        except Exception:
            print("� Groq API: ❌")
            all_ok = False
        
        print("=" * 45)
        if all_ok:
            print("✅ PERFEITO! Todos os meus sistemas estão operacionais!")
            print("🤖 Alfredo: Estou pronto para analisar seus vídeos!")
        else:
            print("⚠️ ATENÇÃO: Alguns componentes precisam de ajustes")
            print("💡 Execute 'py install.py' para corrigir problemas")
        
        return all_ok
