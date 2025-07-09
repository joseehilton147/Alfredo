#!/usr/bin/env python3
"""
🧠 COMANDO: CONFIGURAR-MODELOS
==============================
Comando para descobrir e configurar automaticamente os melhores modelos de IA
"""

import requests
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "configurar-modelos",
    "description": "🧠 Configurar melhores modelos de IA",
    "function": "main",
    "help": "Descobre e configura automaticamente os melhores modelos VLM e LLM disponíveis",
    "version": "0.0.1",
    "author": "Alfredo AI",
    "category": "config"
}

# Configurações de modelos recomendados (ordenados por prioridade)
RECOMMENDED_VLM_MODELS = [
    ("llava:13b", "Modelo visual de 13B - Excelente para análise de imagens"),
    ("llava:7b", "Modelo visual de 7B - Boa performance, menor uso de memória"),
    ("llava:34b", "Modelo visual de 34B - Máxima qualidade, requer mais recursos"),
    ("bakllava", "Modelo visual alternativo - Boa compatibilidade")
]

RECOMMENDED_LLM_MODELS = [
    ("llama3:8b", "Llama 3 8B - Excelente para texto, rápido"),
    ("llama3:70b", "Llama 3 70B - Máxima qualidade, requer mais recursos"), 
    ("mistral", "Mistral 7B - Boa performance geral"),
    ("codellama", "Code Llama - Especializado em código"),
    ("gemma:7b", "Gemma 7B - Modelo do Google, boa performance")
]

def check_ollama_connection() -> bool:
    """Verifica se Ollama está rodando"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_models() -> List[str]:
    """Lista modelos disponíveis no Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        return []

def test_model_performance(model_name: str, model_type: str) -> Tuple[bool, float]:
    """Testa performance de um modelo"""
    print(f"🧪 Testando {model_name}...")
    
    if model_type == "vlm":
        # Teste simples para VLM (sem imagem, apenas capacidade)
        payload = {
            "model": model_name,
            "prompt": "Describe what you see in this image.",
            "stream": False
        }
    else:
        # Teste simples para LLM
        payload = {
            "model": model_name,
            "prompt": "Responda apenas 'OK' para confirmar funcionamento.",
            "stream": False
        }
    
    try:
        import time
        start_time = time.time()
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=30)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ {model_name}: OK ({response_time:.1f}s)")
            return True, response_time
        else:
            print(f"❌ {model_name}: Falha")
            return False, 999.0
            
    except Exception as e:
        print(f"❌ {model_name}: Erro - {e}")
        return False, 999.0

def pull_model(model_name: str) -> bool:
    """Baixa um modelo no Ollama"""
    print(f"📦 Baixando {model_name}...")
    
    try:
        payload = {"name": model_name}
        response = requests.post("http://localhost:11434/api/pull", 
                               json=payload, timeout=300)
        
        if response.status_code == 200:
            print(f"✅ {model_name}: Download concluído")
            return True
        else:
            print(f"❌ {model_name}: Falha no download")
            return False
            
    except Exception as e:
        print(f"❌ {model_name}: Erro no download - {e}")
        return False

def find_best_models() -> Tuple[str, str]:
    """Encontra os melhores modelos disponíveis"""
    print("🔍 Alfredo: Analisando modelos disponíveis...")
    
    available_models = get_available_models()
    print(f"📋 Modelos instalados: {len(available_models)}")
    
    best_vlm = None
    best_llm = None
    
    # Busca melhor VLM disponível
    for model_name, description in RECOMMENDED_VLM_MODELS:
        if any(model_name in available for available in available_models):
            working, response_time = test_model_performance(model_name, "vlm")
            if working:
                best_vlm = model_name
                print(f"🎯 Melhor VLM encontrado: {model_name}")
                break
    
    # Busca melhor LLM disponível
    for model_name, description in RECOMMENDED_LLM_MODELS:
        if any(model_name in available for available in available_models):
            working, response_time = test_model_performance(model_name, "llm")
            if working:
                best_llm = model_name
                print(f"🎯 Melhor LLM encontrado: {model_name}")
                break
    
    return best_vlm, best_llm

def install_recommended_models() -> Tuple[str, str]:
    """Instala modelos recomendados se não existirem"""
    print("🤖 Alfredo: Instalando modelos recomendados...")
    
    # Instala VLM padrão se necessário
    vlm_installed = None
    for model_name, description in RECOMMENDED_VLM_MODELS[:2]:  # Tenta os 2 primeiros
        if pull_model(model_name):
            vlm_installed = model_name
            break
    
    # Instala LLM padrão se necessário
    llm_installed = None
    for model_name, description in RECOMMENDED_LLM_MODELS[:2]:  # Tenta os 2 primeiros
        if pull_model(model_name):
            llm_installed = model_name
            break
    
    return vlm_installed, llm_installed

def update_env_file(vlm_model: str, llm_model: str):
    """Atualiza arquivo .env com os modelos descobertos"""
    env_path = Path(".env")
    
    # Le .env existente ou cria novo
    env_content = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
    
    # Atualiza modelos
    env_content['VLM_MODEL'] = vlm_model
    env_content['LLM_MODEL'] = llm_model
    env_content['OLLAMA_HOST'] = env_content.get('OLLAMA_HOST', 'http://localhost:11434')
    
    # Escreve .env atualizado
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# Configuração Alfredo AI - Modelos Otimizados\n")
        f.write("# Configurado automaticamente pelo comando 'configurar-modelos'\n\n")
        f.write(f"VLM_MODEL={env_content['VLM_MODEL']}\n")
        f.write(f"LLM_MODEL={env_content['LLM_MODEL']}\n")
        f.write(f"OLLAMA_HOST={env_content['OLLAMA_HOST']}\n")
        f.write("\n# Configurações opcionais\n")
        f.write("# FRAMES_PER_SCENE=3\n")
        f.write("# MAX_RETRIES=3\n")
    
    print(f"✅ Arquivo .env atualizado com os modelos otimizados")

def main():
    """Configura automaticamente os melhores modelos"""
    print("🤖" + "=" * 60 + "🤖")
    print("║" + " " * 19 + "ALFREDO AI - CONFIGURADOR" + " " * 15 + "║")
    print("║" + " " * 14 + "Descoberta Automática dos Melhores Modelos" + " " * 5 + "║")
    print("║" + " " * 17 + "\"Otimização inteligente para você!\"" + " " * 8 + "║")
    print("🤖" + "=" * 60 + "🤖")
    
    print("🤖 Alfredo: Vou encontrar e configurar os melhores modelos de IA!")
    
    # Verifica conexão com Ollama
    if not check_ollama_connection():
        print("❌ Alfredo: Ollama não está rodando!")
        print("💡 Dica: Inicie o Ollama e execute este comando novamente")
        return
    
    print("✅ Alfredo: Ollama conectado com sucesso!")
    
    # Busca modelos existentes
    best_vlm, best_llm = find_best_models()
    
    # Se não encontrou, instala recomendados
    if not best_vlm or not best_llm:
        print("\n📦 Alfredo: Instalando modelos recomendados...")
        
        if not best_vlm:
            print("🧠 Instalando modelo VLM (análise visual)...")
            vlm_installed, _ = install_recommended_models()
            if vlm_installed:
                best_vlm = vlm_installed
        
        if not best_llm:
            print("📝 Instalando modelo LLM (geração de texto)...")
            _, llm_installed = install_recommended_models()
            if llm_installed:
                best_llm = llm_installed
    
    # Valida resultados finais
    if best_vlm and best_llm:
        update_env_file(best_vlm, best_llm)
        
        print(f"\n🎉 ALFREDO: CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 50)
        print(f"🧠 Modelo VLM (Visual): {best_vlm}")
        print(f"📝 Modelo LLM (Texto): {best_llm}")
        print("📁 Configuração salva em: .env")
        print("🤖 Alfredo: Modelos otimizados e prontos para uso!")
        
        # Executa teste final
        print("\n🧪 Alfredo: Executando teste final...")
        from commands.test_runner import main as run_tests
        run_tests()
        
    else:
        print("\n❌ ALFREDO: FALHA NA CONFIGURAÇÃO")
        print("🤖 Alfredo: Não consegui configurar todos os modelos necessários")
        print("💡 Dica: Verifique sua conexão e espaço em disco")

if __name__ == "__main__":
    main()
