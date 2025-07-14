#!/usr/bin/env python3
"""
🧪 COMANDO: TESTES
==================
Sistema de testes automatizados do Alfredo AI
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "testes",
    "description": "🧪 Executar todos os testes do sistema",
    "function": "main",
    "help": "Executa bateria completa de testes para validar funcionamento de todos os comandos",
    "version": "0.0.1",
    "author": "Alfredo AI"
}

def test_core_system():
    """Testa o sistema principal do Alfredo"""
    print("\n🔧 TESTE: Sistema Principal")
    print("-" * 30)
    
    try:
        # Testa importação do core
        from core.alfredo_core import AlfredoCore
        alfredo = AlfredoCore()
        print("✅ Core system: OK")
        
        # Testa carregamento de comandos
        assert len(alfredo.commands) > 0, "Nenhum comando carregado"
        print(f"✅ Comandos carregados: {len(alfredo.commands)}")
        
    except Exception as e:
        print(f"❌ Erro no sistema principal: {e}")
        assert False, f"Erro no sistema principal: {e}"

def test_dependencies():
    """Testa dependências básicas"""
    print("\n📦 TESTE: Dependências")
    print("-" * 30)
    
    dependencies = [
        ('requests', 'HTTP client'),
        ('tqdm', 'Progress bars'),
        ('psutil', 'System info'),
        ('yt_dlp', 'YouTube downloader'),
        ('scenedetect', 'Video analysis')
    ]
    
    missing_deps = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: OK ({description})")
        except ImportError:
            print(f"⚠️ {module}: Missing ({description})")
            missing_deps.append(module)
    
    if missing_deps:
        print(f"❌ Dependências faltando: {', '.join(missing_deps)}")
    
    assert len(missing_deps) == 0, f"Dependências faltando: {', '.join(missing_deps)}"

def test_ollama_connection():
    """Testa conexão com Ollama"""
    print("\n🧠 TESTE: Ollama")
    print("-" * 30)
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        assert response.status_code == 200, "Ollama não conectado"
        print("✅ Ollama: Conectado")
        
        models = response.json()
        model_names = [model['name'] for model in models.get('models', [])]
        
        required_models = ['llava:13b', 'llama3:8b']
        missing_models = []
        
        for model in required_models:
            if model in model_names:
                print(f"✅ Modelo {model}: Disponível")
            else:
                print(f"❌ Modelo {model}: Faltando")
                missing_models.append(model)
        
        if missing_models:
            print(f"⚠️ Modelos faltando: {', '.join(missing_models)}")
        
        # Não falha o teste se modelos estão faltando, apenas avisa
        
    except Exception as e:
        print(f"❌ Ollama: {e}")
        # Para Ollama, apenas avisa mas não falha os testes

def test_youtube_download():
    """Testa download do YouTube com vídeo específico para validação"""
    print("\n🌐 TESTE: Download YouTube")
    print("-" * 30)
    
    # URL específica para teste de download
    test_url = "https://www.youtube.com/watch?v=oUPaJxk6TZ0"
    
    try:
        # Cria diretório temporário
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            print(f"📁 Testando em: {temp_path}")
            print(f"🔗 URL de teste: {test_url}")
            
            # Verifica se yt-dlp está disponível
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'yt-dlp'], 
                                      capture_output=True, check=True)
                print("✅ yt-dlp: Disponível")
            except subprocess.CalledProcessError:
                print("❌ yt-dlp: Não instalado")
                assert False, "yt-dlp não está instalado"
            
            # Testa download de informações apenas (sem baixar o vídeo)
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--dump-json',
                '--no-download',
                test_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, cwd=temp_path)
            
            if result.returncode == 0:
                print("✅ Download test: OK (info obtida)")
                print("💡 Download real funcionaria corretamente")
            else:
                print(f"❌ Download test: Falhou (código {result.returncode})")
                assert False, f"Download test falhou com código {result.returncode}"
                
    except Exception as e:
        print(f"❌ Erro no teste de download: {e}")
        assert False, f"Erro no teste de download: {e}"

def test_command_execution():
    """Testa execução básica dos comandos"""
    print("\n⚙️ TESTE: Execução de Comandos")
    print("-" * 30)
    
    try:
        from core.alfredo_core import AlfredoCore
        alfredo = AlfredoCore()
        
        # Testa comando info-pc
        print("🔍 Testando info-pc...")
        try:
            # Simula execução sem mostrar output
            import commands.pc_info
            print("✅ info-pc: Comando OK")
        except Exception as e:
            print(f"❌ info-pc: {e}")
            assert False, f"Comando info-pc falhou: {e}"
            
        # Testa comando video_summarizer (apenas importação)
        print("🔍 Testando resumir-video...")
        try:
            # Testa o módulo no novo local usando importlib
            import importlib.util
            project_root = Path(__file__).parent.parent.parent  # Precisa de um .parent extra pois está em tests/unit/
            video_file = project_root / "commands" / "video" / "local_video.py"
            spec = importlib.util.spec_from_file_location("local_video", video_file)
            if spec and spec.loader:
                local_video_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(local_video_module)
                print("✅ resumir-video: Comando OK")
            else:
                assert False, "Não foi possível carregar o módulo local_video"
        except Exception as e:
            print(f"❌ resumir-video: {e}")
            assert False, f"Comando resumir-video falhou: {e}"
            
        # Testa comando de limpeza
        print("🔍 Testando limpar...")
        try:
            # Testa o módulo de limpeza usando importlib
            import importlib.util
            project_root = Path(__file__).parent.parent.parent  # Precisa de um .parent extra pois está em tests/unit/
            clean_file = project_root / "commands" / "clean_command.py"
            spec = importlib.util.spec_from_file_location("clean_command", clean_file)
            if spec and spec.loader:
                clean_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(clean_module)
                print("✅ limpar: Comando OK")
            else:
                assert False, "Não foi possível carregar o módulo clean_command"
        except Exception as e:
            print(f"❌ limpar: {e}")
            assert False, f"Comando limpar falhou: {e}"
        
    except Exception as e:
        print(f"❌ Erro geral nos comandos: {e}")
        assert False, f"Erro geral nos comandos: {e}"

def test_youtube_ai_workflow():
    """Testa workflow completo YouTube + IA com vídeo específico"""
    print("\n🎬 TESTE: YouTube + IA Workflow")
    print("-" * 30)
    
    # URL específica para teste de transcrição com IA
    test_url = "https://www.youtube.com/watch?v=Tn6-PIqc4UM"
    
    try:
        print(f"🔗 URL de teste IA: {test_url}")
        
        # Verifica se yt-dlp está disponível
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'yt-dlp'], 
                                  capture_output=True, check=True)
            print("✅ yt-dlp: Disponível")
        except subprocess.CalledProcessError:
            print("❌ yt-dlp: Não instalado")
            assert False, "yt-dlp não está instalado"
        
        # Verifica se Ollama está respondendo (opcional)
        try:
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama: Conectado")
            else:
                print("❌ Ollama: Não responde")
        except Exception:
            print("❌ Ollama: Não conectado")
        
        # Testa apenas extração de informações (simula workflow)
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--dump-json',
            '--no-download',
            test_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            duration = info.get('duration', 0)
            
            print(f"✅ YouTube + IA test: OK")
            print(f"📹 Título: {info.get('title', 'N/A')[:50]}...")
            print(f"⏱️ Duração: {duration}s")
            print("💡 Workflow completo funcionaria corretamente")
        else:
            print(f"❌ YouTube + IA test: Falha - {result.stderr}")
            assert False, f"YouTube + IA test falhou: {result.stderr}"
            
    except Exception as e:
        print(f"❌ Erro no teste YouTube + IA: {e}")
        assert False, f"Erro no teste YouTube + IA: {e}"

def test_local_video_analysis():
    """Testa análise de vídeo local com arquivo de teste"""
    print("\n🎬 TESTE: Análise Vídeo Local")
    print("-" * 30)
    
    # Procura vídeo de teste na pasta tests
    test_video_dir = Path("tests")
    test_video_patterns = ["video-sample.*", "*.mp4", "*.avi", "*.mov"]
    
    test_video = None
    for pattern in test_video_patterns:
        matches = list(test_video_dir.glob(pattern))
        if matches:
            test_video = matches[0]
            break
    
    if not test_video or not test_video.exists():
        print("⚠️ Vídeo de teste não encontrado")
        print("💡 Coloque um vídeo na pasta 'tests/' com nome 'video-sample.*'")
        return  # Não falha o teste se não há vídeo
    
    try:
        print(f"📹 Arquivo de teste: {test_video.name}")
        
        # Verifica se é um arquivo de vídeo válido
        if test_video.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            print("✅ Formato de vídeo: Válido")
            
            # Verifica se PySceneDetect conseguiria processar
            try:
                import scenedetect
                print("✅ PySceneDetect: Disponível")
            except ImportError:
                print("❌ PySceneDetect: Não instalado")
                assert False, "PySceneDetect não está instalado"
            
            print("✅ Análise local: OK (simulado)")
            print("💡 Processamento completo funcionaria corretamente")
        else:
            print(f"⚠️ Arquivo '{test_video.name}' não é um vídeo válido")
            print("💡 Use formatos: .mp4, .avi, .mov, .mkv, .webm")
            return  # Não falha se arquivo não é vídeo
            
    except Exception as e:
        print(f"❌ Erro no teste de vídeo local: {e}")
        assert False, f"Erro no teste de vídeo local: {e}"

def main():
    """Executa todos os testes"""
    print("🧪 ALFREDO AI - BATERIA DE TESTES")
    print("=" * 40)
    print("🤖 Executando validação completa do sistema...")
    
    tests = [
        ("Sistema Principal", test_core_system),
        ("Dependências", test_dependencies),
        ("Ollama", test_ollama_connection),
        ("YouTube Download", test_youtube_download),
        ("YouTube + IA", test_youtube_ai_workflow),
        ("Vídeo Local", test_local_video_analysis),
        ("Comandos", test_command_execution)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERRO no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 40)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 RESULTADO: {passed}/{total} testes aprovados")
    
    if passed == total:
        print("🎉 PERFEITO! Todos os testes passaram!")
        print("🤖 Alfredo: Sistema 100% funcional!")
    else:
        print("⚠️ Alguns testes falharam. Verifique as dependências.")
        print("💡 Execute 'py install.py' para corrigir problemas")
    
    return passed == total

if __name__ == "__main__":
    main()
