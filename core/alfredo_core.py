#!/usr/bin/env python3
"""
🤖 ALFREDO AI - CORE SYSTEM
============================
Sistema central do assistente pessoal Alfredo
Gerencia comandos e módulos de forma modular
"""

import os
import sys
import importlib
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Callable, Any

class AlfredoCore:
    """Sistema central do Alfredo - Gerenciador de comandos"""
    
    def __init__(self):
        self.work_dir = os.getcwd()
        self.project_dir = Path(__file__).parent.parent
        self.commands = {}
        self.load_commands()
    
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
            
        # Adiciona pasta commands ao path
        sys.path.insert(0, str(commands_dir))
        
        # Carrega comandos do diretório principal commands/
        for file_path in commands_dir.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "__init__.py":
                continue
                
            module_name = file_path.stem
            try:
                module = importlib.import_module(module_name)
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
    
    def execute_command(self, command_name: str):
        """Executa um comando específico"""
        if command_name not in self.commands:
            print(f"❌ Comando '{command_name}' não encontrado!")
            print("💡 Use 'Alfredo --list' para ver comandos disponíveis")
            return False
        
        cmd_info = self.commands[command_name]
        
        try:
            if command_name == 'test':
                self.run_diagnostics()
                return True
            else:
                # Verifica se é módulo carregado ou string
                if isinstance(cmd_info.get('module'), str):
                    # Módulo como string - usa método antigo
                    return self._execute_external_command(cmd_info)
                else:
                    # Módulo já carregado - executa diretamente
                    module = cmd_info['module']
                    function_name = cmd_info.get('function', 'main')
                    
                    if hasattr(module, function_name):
                        func = getattr(module, function_name)
                        func()
                        return True
                    else:
                        print(f"❌ Função '{function_name}' não encontrada no módulo")
                        return False
                
        except Exception as e:
            print(f"❌ Erro ao executar comando '{command_name}': {e}")
            return False
    
    def _execute_external_command(self, cmd_info: Dict[str, str]) -> bool:
        """Executa comando de módulo externo"""
        module_name = cmd_info['module']
        function_name = cmd_info.get('function', 'main')
        
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                func()
                return True
            else:
                print(f"❌ Função '{function_name}' não encontrada no módulo {module_name}")
                return False
        except ImportError as e:
            print(f"❌ Módulo '{module_name}' não encontrado: {e}")
            return False
    
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
        
        # Testa Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("🧠 Ollama (meu cérebro): ✅")
                
                models = response.json()
                model_names = [model['name'] for model in models.get('models', [])]
                
                for model in ['llava:13b', 'llama3:8b']:
                    if model in model_names:
                        print(f"🎯 {model}: ✅")
                    else:
                        print(f"🎯 {model}: ❌")
                        all_ok = False
            else:
                print("🧠 Ollama: ❌")
                all_ok = False
        except Exception:
            print("🧠 Ollama: ❌")
            all_ok = False
        
        print("=" * 45)
        if all_ok:
            print("✅ PERFEITO! Todos os meus sistemas estão operacionais!")
            print("🤖 Alfredo: Estou pronto para analisar seus vídeos!")
        else:
            print("⚠️ ATENÇÃO: Alguns componentes precisam de ajustes")
            print("💡 Execute 'py install.py' para corrigir problemas")
        
        return all_ok
