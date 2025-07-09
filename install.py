#!/usr/bin/env python3
"""
Instalador Automático do Alfredo AI
Seu assistente pessoal de análise de vídeos
"""
import sys
import subprocess
import requests
import os

def install_dependencies():
    """Instala dependências Python para o Alfredo"""
    print("📦 Instalando componentes do Alfredo...")
    
    deps = [
        "requests>=2.31.0",
        "tqdm>=4.66.0", 
        "scenedetect[opencv]>=0.6.0"
    ]
    
    for dep in deps:
        try:
            print(f"   Instalando {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"   ✅ {dep}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Falha em {dep}: {e}")
            return False
    
    return True

def check_ollama():
    """Verifica e configura o cérebro do Alfredo (Ollama)"""
    print("\n� Verificando cérebro do Alfredo (Ollama)...")
    
    try:
        response = requests.get("http://127.0.0.1:11434", timeout=5)
        print("   ✅ Ollama está rodando")
        
        # Verificar modelos
        models_response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        available = [m['name'] for m in models_response.json()['models']]
        
        required = ["llava:13b", "llama3:8b"]
        missing = [m for m in required if m not in available]
        
        if missing:
            print(f"   📥 Baixando modelos para o Alfredo: {', '.join(missing)}")
            for model in missing:
                print(f"      Baixando {model}...")
                subprocess.run(["ollama", "pull", model], check=True)
                print(f"      ✅ {model}")
        else:
            print("   ✅ Todos os modelos do Alfredo estão disponíveis")
            
        return True
        
    except requests.exceptions.RequestException:
        print("   ❌ Ollama não está rodando")
        print("   💡 Execute: ollama serve")
        return False
    except subprocess.CalledProcessError:
        print("   ❌ Erro ao baixar modelos")
        return False

def create_alias():
    """Cria comando global 'Alfredo' para Windows"""
    print("\n🔗 Configurando comando global 'Alfredo'...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bat_content = f'''@echo off
REM Alfredo AI - Assistente Pessoal Inteligente
REM Executa mantendo diretório de trabalho original
set "WORK_DIR=%CD%"
cd /d "{script_dir}"
py Alfredo.py %*
'''
    
    try:
        # Criar arquivo .bat na pasta do sistema
        system_path = os.environ.get('USERPROFILE', '') + '\\AppData\\Local\\Microsoft\\WindowsApps'
        if os.path.exists(system_path):
            bat_path = os.path.join(system_path, 'Alfredo.bat')
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            print(f"   ✅ Comando 'Alfredo' criado")
            print(f"   📁 Localização: {bat_path}")
            return True
        else:
            print("   ⚠️ Pasta do sistema não encontrada")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao criar comando: {e}")
        return False

def main():
    """Instalação automática do Alfredo"""
    print("🤖 INSTALADOR DO ALFREDO AI")
    print("=" * 40)
    print("Configurando seu assistente pessoal de análise de vídeos...")
    
    success = True
    
    # 1. Dependências Python
    if not install_dependencies():
        success = False
    
    # 2. Ollama e modelos
    if not check_ollama():
        success = False
    
    # 3. Comando global
    if not create_alias():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("🎉 ALFREDO ESTÁ PRONTO!")
        print("\n🤖 Como usar seu assistente:")
        print("   py Alfredo.py")
        print("   py Alfredo.py --test")
        print("   Alfredo  (comando global)")
        print("\n🧪 Execute o diagnóstico:")
        print("   py Alfredo.py --test")
        print("\n💡 Alfredo: Digite 'Alfredo' em qualquer lugar para começar!")
    else:
        print("❌ PROBLEMAS NA INSTALAÇÃO")
        print("   Resolva os erros acima e tente novamente")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
