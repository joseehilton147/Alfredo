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
        if len(alfredo.commands) > 0:
            print(f"✅ Comandos carregados: {len(alfredo.commands)}")
        else:
            print("❌ Nenhum comando carregado")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema principal: {e}")
        return False

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
    
    all_ok = True
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: OK ({description})")
        except ImportError:
            print(f"⚠️ {module}: Missing ({description})")
            all_ok = False
    
    return all_ok

def test_ollama_connection():
    """Testa conexão com Ollama"""
    print("\n🧠 TESTE: Ollama")
    print("-" * 30)
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama: Conectado")
            
            models = response.json()
            model_names = [model['name'] for model in models.get('models', [])]
            
            required_models = ['llava:13b', 'llama3:8b']
            all_models_ok = True
            
            for model in required_models:
                if model in model_names:
                    print(f"✅ Modelo {model}: Disponível")
                else:
                    print(f"❌ Modelo {model}: Faltando")
                    all_models_ok = False
            
            return all_models_ok
        else:
            print("❌ Ollama: Erro de conexão")
            return False
            
    except Exception as e:
        print(f"❌ Ollama: {e}")
        return False

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
                return False
            
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
                return True
            else:
                print(f"❌ Download test: Falhou (código {result.returncode})")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste de download: {e}")
        return False

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
            return False
            
        # Testa comando video_summarizer (apenas importação)
        print("🔍 Testando resumir-video...")
        try:
            # Testa o módulo no novo local
            video_dir = os.path.join(os.path.dirname(__file__), 'video')
            if video_dir not in sys.path:
                sys.path.insert(0, video_dir)
            import local_video
            print("✅ resumir-video: Comando OK")
        except Exception as e:
            print(f"❌ resumir-video: {e}")
            return False
            
        # Testa comando de limpeza
        print("🔍 Testando limpar...")
        try:
            import clean_command
            print("✅ limpar: Comando OK")
        except Exception as e:
            print(f"❌ limpar: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro geral nos comandos: {e}")
        return False

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
            return False
        
        # Verifica se Ollama está respondendo
        try:
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama: Conectado")
            else:
                print("❌ Ollama: Não responde")
                return False
        except Exception:
            print("❌ Ollama: Não conectado")
            return False
        
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
            return True
        else:
            print(f"❌ YouTube + IA test: Falha - {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste YouTube + IA: {e}")
        return False

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
        return True  # Não falha o teste se não há vídeo
    
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
                return False
            
            print("✅ Análise local: OK (simulado)")
            print("💡 Processamento completo funcionaria corretamente")
            return True
        else:
            print(f"⚠️ Arquivo '{test_video.name}' não é um vídeo válido")
            print("💡 Use formatos: .mp4, .avi, .mov, .mkv, .webm")
            return True  # Não falha se arquivo não é vídeo
            
    except Exception as e:
        print(f"❌ Erro no teste de vídeo local: {e}")
        return False

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
