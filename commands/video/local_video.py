#!/usr/bin/env python3
"""
🎬 COMANDO: RESUMIR-VIDEO LOCAL
===============================
Sistema de análise e resumo de vídeos locais com IA usando nova arquitetura
"""

import sys
import subprocess
import base64
import requests
import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from typing import List, Optional

# Importa configuração de caminhos
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.paths import paths

# Informações do comando para o Alfredo
COMMAND_INFO = {
    "name": "resumir-video",
    "description": "🎬 Resumir vídeos locais com IA",
    "function": "main",
    "help": "Analisa frames de vídeos locais e gera resumos estruturados em Markdown usando IA local",
    "version": "0.0.1",
    "author": "Alfredo AI",
    "category": "video"
}

# Configurações
OLLAMA_HOST = "http://127.0.0.1:11434"
VLM_MODEL = "llava:13b"
LLM_MODEL = "llama3:8b"
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
FRAMES_PER_SCENE = 3
MAX_RETRIES = 3

def get_versioned_output_path(base_path: Path) -> Path:
    """Gera caminho com versionamento automático se arquivo já existir"""
    if not base_path.exists():
        return base_path
    
    # Extrair nome base e extensão
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    
    # Procurar próxima versão disponível
    version = 2
    while True:
        versioned_name = f"{stem}-v{version}{suffix}"
        versioned_path = parent / versioned_name
        
        if not versioned_path.exists():
            return versioned_path
        
        version += 1
        
        # Proteção contra loop infinito (máximo 100 versões)
        if version > 100:
            print("⚠️ Alfredo: Muitas versões! Sobrescrevendo a última...")
            return versioned_path

def test_ai_vision() -> bool:
    """Testa se a IA visual está funcionando"""
    try:
        # Teste rápido com imagem mínima
        test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x12IDATx\x9cc```\x00\x02\x00\x00\x05\x00\x01\x0d\n-\xdb\x00\x00\x00\x00IEND\xaeB\x60\x82'
        b64_image = base64.b64encode(test_image).decode('utf-8')
        
        payload = {
            "model": "llava:7b",
            "prompt": "Test",
            "images": [b64_image],
            "stream": False
        }
        
        response = requests.post(f"{OLLAMA_HOST}/api/generate", 
                               json=payload, timeout=10)
        
        return response.status_code == 200 and 'response' in response.json()
        
    except Exception:
        return False

def extract_frames(video_path: Path) -> List[Path]:
    """Extrai keyframes do vídeo usando nova estrutura"""
    # Criar estrutura organizada: data/cache/frames/nome_do_video/
    temp_dir = paths.get_cache_frames_path(video_path.stem)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎬 Alfredo: Analisando cenas de '{video_path.name}'...")
    print("🤖 Extraindo frames-chave com minha visão avançada...")
    
    cmd = [
        sys.executable, "-m", "scenedetect",
        "--input", str(video_path),
        "--output", str(temp_dir),
        "detect-adaptive",
        "save-images",
        "--num-images", str(FRAMES_PER_SCENE)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ Alfredo: Encontrei um problema na extração: {result.stderr}")
            return []
        
        # Buscar imagens geradas
        frames = list(temp_dir.glob("*.jpg"))
        print(f"📸 Alfredo: Consegui extrair {len(frames)} frames importantes!")
        return sorted(frames)
        
    except subprocess.TimeoutExpired:
        print("❌ Alfredo: O vídeo está muito longo, demorou mais que o esperado.")
        return []
    except Exception as e:
        print(f"❌ Alfredo: Erro inesperado na extração: {e}")
        return []

def analyze_frame(frame_path: Path, frame_number: int, total_frames: int) -> Optional[str]:
    """Analisa um frame com IA usando fallback para modelos"""
    start_time = time.time()
    
    try:
        with open(frame_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode("utf-8")
        
        prompt = """Analise esta imagem de vídeo brevemente em 2-3 frases:
- O que está sendo mostrado?
- Que informações ou conceitos são visíveis?

Seja direto e conciso."""
        
        # Lista de modelos para testar (do mais rápido ao mais completo)
        models_to_try = ["llava:7b", "llava:13b"]
        
        for model_idx, model in enumerate(models_to_try):
            payload = {
                "model": model,
                "prompt": prompt,
                "images": [b64_image],
                "stream": False
            }
            
            for attempt in range(2):  # Apenas 2 tentativas por modelo
                try:
                    # Timeout mais agressivo para não travar
                    response = requests.post(f"{OLLAMA_HOST}/api/generate", 
                                           json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'response' in result and result['response'].strip():
                            elapsed = time.time() - start_time
                            return result['response'].strip()
                        else:
                            print(f"⚠️ Frame {frame_number}/{total_frames}: Modelo {model} retornou resposta vazia")
                            break  # Tenta próximo modelo
                    else:
                        error_msg = response.json().get('error', 'Erro desconhecido')
                        print(f"⚠️ Frame {frame_number}/{total_frames}: {model} erro {response.status_code}")
                        break  # Tenta próximo modelo
                        
                except requests.exceptions.Timeout:
                    elapsed = time.time() - start_time
                    if attempt == 1:  # Última tentativa
                        print(f"⏱️ Frame {frame_number}/{total_frames}: {model} timeout após {elapsed:.1f}s")
                        break
                    print(f"⚠️ Frame {frame_number}/{total_frames}: {model} timeout, tentativa {attempt + 2}...")
                    
                except Exception as e:
                    if attempt == 1:
                        print(f"❌ Frame {frame_number}/{total_frames}: {model} erro: {str(e)[:50]}...")
                        break
                    print(f"⚠️ Frame {frame_number}/{total_frames}: {model} tentativa {attempt + 2}...")
        
        # Se todos os modelos falharam, usa análise básica
        elapsed = time.time() - start_time
        print(f"📝 Frame {frame_number}/{total_frames}: Usando análise básica após {elapsed:.1f}s")
        return f"Frame {frame_number}: {frame_path.name} - conteúdo visual detectado (análise IA indisponível)"
                
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Frame {frame_number}/{total_frames}: Erro após {elapsed:.1f}s - {str(e)[:50]}...")
        return f"Frame {frame_number}: {frame_path.name} - erro na análise"

def generate_summary(descriptions: List[str], video_name: str) -> str:
    """Gera um resumo inteligente e estruturado"""
    if not descriptions:
        return "❌ Alfredo: Não consegui obter descrições para criar o resumo."
    
    print("🧠 Alfredo: Processando informações e criando seu resumo personalizado...")
    
    content = "\n".join([f"Frame {i+1}: {desc}" for i, desc in enumerate(descriptions)])
    
    prompt = f"""Sou Alfredo, assistente de IA especializado em análise educacional, similar ao JARVIS do Tony Stark.

Baseado nas análises dos frames do vídeo "{video_name}", criarei um resumo estruturado e profissional.

ANÁLISES DOS FRAMES:
{content}

Crie uma nota de estudo completa no formato Markdown:

# {video_name}

> 🤖 **Resumo criado por Alfredo AI** - Seu assistente pessoal para análise de vídeos educativos

## 📋 Resumo Executivo
[Síntese clara e objetiva do conteúdo principal em 2-3 frases]

## 🎯 Conceitos Fundamentais
- **Conceito Principal 1**: [Explicação detalhada]
- **Conceito Principal 2**: [Explicação detalhada]
- **Conceito Principal 3**: [Explicação detalhada]

## 📚 Desenvolvimento Detalhado
[Análise aprofundada dos tópicos, conectando os conceitos observados nos frames]

## 💡 Insights e Observações
- [Ponto importante ou insight relevante]
- [Observação técnica ou prática]
- [Conexão com outros conceitos]

## 📌 Checklist de Revisão
- [ ] [Tópico para revisar e praticar]
- [ ] [Conceito para aprofundar]
- [ ] [Exercício ou aplicação prática]

## 🔗 Próximos Passos
- [Sugestão de estudo complementar]
- [Tópico relacionado para explorar]

---
*📅 Análise concluída por Alfredo AI em {datetime.now().strftime("%d/%m/%Y às %H:%M")}*  
*🎬 Vídeo: {video_name}*  
*🤖 "Sempre aqui para maximizar seu aprendizado!"*"""

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/generate", 
                               json=payload, timeout=120)
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        print(f"❌ Alfredo: Encontrei um problema ao gerar o resumo: {e}")
        return f"""# {video_name}

> 🤖 **Nota do Alfredo**: Houve um problema técnico na geração do resumo.

## ❌ Erro Técnico
Não foi possível gerar o resumo completo devido a: {e}

## 📋 Dados Coletados
{chr(10).join([f"- Frame {i+1}: {desc}" for i, desc in enumerate(descriptions)])}

---
*Alfredo AI - {datetime.now().strftime("%d/%m/%Y às %H:%M")}*"""

def find_videos(search_dir: Optional[Path] = None) -> List[Path]:
    """Busca vídeos no diretório usando nova estrutura"""
    if search_dir is None:
        # Prioriza pasta de input local, depois pasta atual
        search_dirs = [paths.INPUT_LOCAL, Path.cwd()]
    else:
        search_dirs = [search_dir]
    
    videos = []
    
    for search_path in search_dirs:
        print(f"🔍 Alfredo: Varrendo diretório {search_path}")
        print("🤖 Buscando vídeos na pasta e subpastas...")
        
        for ext in VIDEO_EXTENSIONS:
            # Buscar na pasta atual
            videos.extend(search_path.glob(f"*{ext}"))
            videos.extend(search_path.glob(f"*{ext.upper()}"))
            
            # Buscar em subpastas (1 nível)
            videos.extend(search_path.glob(f"*/*{ext}"))
            videos.extend(search_path.glob(f"*/*{ext.upper()}"))
        
        # Se encontrou vídeos, para de procurar
        if videos:
            break
    
    return sorted(set(videos))  # Remove duplicatas e ordena

def select_video(search_dir: Optional[Path] = None) -> Optional[Path]:
    """Apresenta opções de vídeos"""
    videos = find_videos(search_dir)
    
    if not videos:
        search_path = search_dir or Path.cwd()
        print(f"🤖 Alfredo: Não encontrei vídeos com os formatos que conheço:")
        print(f"   📋 Formatos: {', '.join(VIDEO_EXTENSIONS)}")
        print(f"   📁 Local pesquisado: {search_path}")
        print(f"   🔍 Incluí subpastas (1 nível)")
        print("💡 Alfredo: Coloque alguns vídeos aqui e me execute novamente!")
        return None
    
    print(f"\n🎬 Alfredo: Encontrei {len(videos)} vídeo(s) para analisar:")
    
    if len(videos) == 1:
        video = videos[0]
        size_mb = video.stat().st_size / (1024 * 1024)
        print(f"🎯 Único vídeo disponível: {video.name} ({size_mb:.1f} MB)")
        
        confirm = input("🤖 Alfredo: Posso processar este vídeo para você? (s/N): ").strip().lower()
        if confirm in ['s', 'sim', 'y', 'yes']:
            return video
        else:
            print("👋 Alfredo: Entendido! Quando precisar, estarei aqui.")
            return None
    
    # Múltiplos vídeos - lista organizada
    print("📋 Alfredo: Aqui estão suas opções:")
    for i, video in enumerate(videos, 1):
        size_mb = video.stat().st_size / (1024 * 1024)
        # Mostrar caminho relativo se estiver em subpasta
        rel_path = video.relative_to(search_dir or Path.cwd())
        print(f"  [{i:2d}] {rel_path} ({size_mb:.1f} MB)")
    
    while True:
        try:
            choice = input(f"\n🤖 Alfredo: Qual vídeo devo analisar? (1-{len(videos)}) ou 'q' para sair: ").strip()
            if choice.lower() in ['q', 'quit', 'sair', 'cancelar']:
                print("👋 Alfredo: Sem problemas! Estarei aqui quando precisar.")
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(videos):
                selected_video = videos[idx]
                print(f"✅ Alfredo: Perfeita escolha! Vou analisar '{selected_video.name}'")
                return selected_video
            else:
                print(f"❌ Alfredo: Digite um número entre 1 e {len(videos)}, por favor.")
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Alfredo: Entendi, cancelando operação.")
            return None

def process_video(video_path: Path, work_dir: Optional[Path] = None) -> bool:
    """Processa um vídeo com análise completa"""
    if work_dir is None:
        work_dir = Path.cwd()
        
    print(f"\n🚀 ALFREDO EM AÇÃO")
    print("=" * 50)
    print(f"🎬 Vídeo selecionado: {video_path.name}")
    print("🤖 Alfredo: Iniciando análise completa...")
    
    # 1. Extrair frames
    frames = extract_frames(video_path)
    if not frames:
        print("❌ Alfredo: Não consegui extrair frames. Verificando arquivo...")
        return False
    
    # 2. Analisar frames com feedback melhorado
    descriptions = []
    failed_frames = 0
    start_time = time.time()
    
    print(f"\n🧠 Alfredo: Analisando {len(frames)} frames com minha visão AI...")
    print("💡 Dica: Cada frame demora 5-30s dependendo da complexidade")
    
    # Barra de progresso mais informativa
    with tqdm(
        total=len(frames), 
        desc="🔍 Análise IA", 
        unit="frame",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    ) as pbar:
        
        for i, frame in enumerate(frames, 1):
            frame_start = time.time()
            
            # Atualiza informações da barra
            pbar.set_postfix_str(f"📸 {frame.name}")
            
            description = analyze_frame(frame, i, len(frames))
            
            frame_elapsed = time.time() - frame_start
            total_elapsed = time.time() - start_time
            
            if description:
                descriptions.append(description)
                pbar.set_description(f"✅ Frame {i}")
            else:
                failed_frames += 1
                pbar.set_description(f"⚠️ Frame {i}")
            
            # Atualiza progresso
            pbar.update(1)
            
            # Estimativa de tempo restante
            if i > 0:
                avg_time_per_frame = total_elapsed / i
                remaining_frames = len(frames) - i
                eta_seconds = avg_time_per_frame * remaining_frames
                eta_minutes = eta_seconds / 60
                
                if eta_minutes > 1:
                    pbar.set_postfix_str(f"📸 {frame.name} | ETA: {eta_minutes:.1f}min")
                else:
                    pbar.set_postfix_str(f"📸 {frame.name} | ETA: {eta_seconds:.0f}s")
    
    # Verifica se conseguiu analisar pelo menos alguns frames
    success_rate = (len(descriptions) / len(frames)) * 100 if frames else 0
    total_time = time.time() - start_time
    
    print(f"\n⏱️ Tempo total de análise: {total_time:.1f}s ({total_time/60:.1f} min)")
    
    if not descriptions:
        print("❌ Alfredo: Não consegui analisar nenhum frame com sucesso.")
        print("💡 Sugestões:")
        print("   - Verifique se o Ollama está rodando: ollama serve")
        print("   - Teste um modelo simples: ollama run llava:7b")
        print("   - Verifique a conexão: curl http://127.0.0.1:11434/api/tags")
        return False
    elif failed_frames > 0:
        print(f"⚠️ Alfredo: Analisei {len(descriptions)}/{len(frames)} frames ({success_rate:.1f}% de sucesso)")
        if success_rate < 50:
            print("💡 Alfredo: Taxa de sucesso baixa, mas vou continuar com o que consegui analisar!")
    else:
        print(f"✅ Alfredo: Analisei todos os {len(descriptions)} frames com sucesso!")
    
    # 3. Gerar resumo
    summary = generate_summary(descriptions, video_path.stem)
    
    # 4. Criar pasta output e salvar resultado com versionamento
    base_summary_path = paths.get_output_summary_path(video_path.stem, "local")
    base_summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Obter caminho com versionamento se necessário
    summary_path = get_versioned_output_path(base_summary_path)
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # Verificar se é uma nova versão
        if summary_path != base_summary_path:
            version_info = f" (versão {summary_path.stem.split('-v')[-1]})"
            print(f"\n🎉 ALFREDO: NOVA VERSÃO CRIADA!")
            print(f"📝 Arquivo já existia, criando{version_info}")
        else:
            print(f"\n🎉 ALFREDO: MISSÃO CUMPRIDA!")
        
        print(f"📄 Resumo salvo em: {summary_path}")
        print("🤖 Alfredo: Seu resumo está pronto e organizado!")
        
        # Limpeza automática com opção
        print(f"\n🧹 Alfredo: Posso limpar os arquivos temporários agora?")
        clean_choice = input("🤖 Limpar frames temporários? (S/n): ").strip().lower()
        if clean_choice in ['', 's', 'sim', 'y', 'yes']:
            cleanup_temp(video_path.stem)
        else:
            frames_path = paths.get_cache_frames_path(video_path.stem)
            print(f"🗂️ Alfredo: Frames mantidos em: {frames_path}")
            print("💡 Use 'Alfredo limpar' quando quiser organizar")
        
        return True
        
    except Exception as e:
        print(f"❌ Alfredo: Problema ao salvar o arquivo: {e}")
        return False

def cleanup_temp(video_stem: str):
    """Limpa os arquivos temporários usando nova estrutura"""
    temp_dir = paths.get_cache_frames_path(video_stem)
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"🧹 Alfredo: Limpeza concluída - removidos arquivos temporários de '{video_stem}'")

def main():
    """Executa o resumo de vídeo"""
    print("🤖" + "=" * 58 + "🤖")
    print("║" + " " * 23 + "ALFREDO AI" + " " * 25 + "║")
    print("║" + " " * 16 + "Assistente de Análise de Vídeos" + " " * 11 + "║")
    print("║" + " " * 19 + "\"Sempre aqui para ajudar!\"" + " " * 13 + "║")
    print("🤖" + "=" * 58 + "🤖")
    
    print("🤖 Alfredo: Olá! Estou aqui para analisar seus vídeos educativos.")
    
    # Verificar se arquivo foi passado como argumento
    import sys
    if len(sys.argv) > 1:
        video_path = Path(sys.argv[1])
        if not video_path.exists():
            print(f"❌ Alfredo: Não encontrei o arquivo {video_path}")
            return False
        print(f"📹 Alfredo: Vou analisar o arquivo: {video_path.name}")
    else:
        # Usar diretório atual
        current_work_dir = Path.cwd()
        print(f"📁 Alfredo: Trabalhando no diretório: {current_work_dir}")
        
        # Buscar e selecionar vídeo
        video_path = select_video(current_work_dir)
        if not video_path:
            print("👋 Alfredo: Até a próxima! Estarei aqui quando precisar.")
            return False
    
    # Verificar se pode usar IA visual
    print("\n🧠 Alfredo: Verificando disponibilidade da IA visual...")
    ai_available = test_ai_vision()
    
    if not ai_available:
        print("⚠️ Alfredo: IA visual indisponível, usando modo básico...")
        print("💡 Dica: Execute 'ollama serve' e 'ollama pull llava:7b' para IA completa")
        
        # Oferecer modo básico
        choice = input("🤖 Continuar com análise básica (extração de frames)? (s/N): ").strip().lower()
        if choice not in ['s', 'sim', 'y', 'yes']:
            print("👋 Alfredo: Entendido! Configure a IA visual e me chame novamente.")
            return False
    
    # Processar o vídeo
    success = process_video(video_path)
    
    if success:
        print("\n🎊 ALFREDO: ANÁLISE CONCLUÍDA COM SUCESSO!")
        print(f"📁 Resultado disponível no sistema de arquivos organizado")
        print("🤖 Alfredo: Foi um prazer ajudar! Até a próxima análise!")
    else:
        print("\n❌ ALFREDO: ENCONTREI UM PROBLEMA")
        print("🤖 Alfredo: Desculpe, algo deu errado. Execute testes para diagnóstico.")

if __name__ == "__main__":
    main()
