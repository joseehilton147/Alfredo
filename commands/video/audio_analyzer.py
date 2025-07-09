#!/usr/bin/env python3
"""
🎧 COMANDO: ANÁLISE DE ÁUDIO
=============================
Sistema de transcrição e análise de áudio usando Whisper
Muito mais rápido e preciso que análise visual!
"""

import os
import sys
import subprocess
import requests
import json
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

# Suprimir warnings específicos do Whisper
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Importa configuração de caminhos
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.paths import paths

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "audioa",
    "description": "🎧 Analisar áudio de vídeos",
    "function": "main",
    "help": "Transcreve e analisa áudio usando Whisper + IA - muito mais rápido que análise visual",
    "version": "1.0.0",
    "author": "Alfredo AI",
    "category": "audio"
}

# Configurações
OLLAMA_HOST = "http://127.0.0.1:11434"
LLM_MODEL = "llama3:8b"
AUDIO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".m4a", ".flac"]

def extract_audio(video_path: Path) -> Optional[Path]:
    """Extrai áudio do vídeo usando ffmpeg"""
    print(f"🎵 Alfredo: Extraindo áudio de '{video_path.name}'...")
    
    # Criar pasta de cache para áudio
    audio_cache_dir = paths.CACHE_ROOT / "audio"
    audio_cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo de áudio
    audio_path = audio_cache_dir / f"{video_path.stem}.wav"
    
    if audio_path.exists():
        print(f"♻️ Alfredo: Ótimo! Já extraí este áudio antes!")
        return audio_path
    
    try:
        # Comando ffmpeg para extrair áudio
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-acodec", "pcm_s16le",  # 16-bit PCM
            "-ar", "16000",          # 16kHz (padrão Whisper)
            "-ac", "1",              # Mono
            "-y",                    # Sobrescrever
            str(audio_path)
        ]
        
        print("🔄 Alfredo: Processando o áudio...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and audio_path.exists():
            size_mb = audio_path.stat().st_size / (1024 * 1024)
            print(f"✅ Alfredo: Áudio extraído com sucesso! ({size_mb:.1f} MB)")
            return audio_path
        else:
            print(f"😕 Alfredo: Ops, tive um problema na extração: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("⏰ Alfredo: A extração demorou demais - seu vídeo deve ser bem longo!")
        return None
    except FileNotFoundError:
        print("❌ Alfredo: Não encontrei o ffmpeg no seu sistema!")
        print("💡 Dica: Baixe em https://ffmpeg.org/download.html")
        return None
    except Exception as e:
        print(f"😅 Alfredo: Algo inesperado aconteceu: {e}")
        return None

def transcribe_audio(audio_path: Path) -> Optional[str]:
    """Transcreve áudio usando Whisper local ou online"""
    print(f"🗣️ Alfredo: Transcrevendo o áudio...")
    
    # Tentar Whisper local primeiro
    transcription = transcribe_with_whisper_local(audio_path)
    
    if not transcription:
        print("🤔 Alfredo: Whisper não está disponível, vou usar método básico...")
        transcription = transcribe_with_basic_method(audio_path)
    
    return transcription

def transcribe_with_whisper_local(audio_path: Path) -> Optional[str]:
    """Usa Whisper Python library diretamente"""
    try:
        # Importar Whisper
        import whisper
        
        print("🎙️ Alfredo: Usando Whisper para transcrição...")
        print("⏳ Carregando modelo (pode demorar um pouco na primeira vez)...")
        
        # Carregar modelo base (rápido e eficiente)
        model = whisper.load_model("base")
        
        print("🔄 Alfredo: Transcrevendo... (tenha paciência, vale a pena!)")
        
        # Transcrever áudio
        result = model.transcribe(str(audio_path), language="pt")
        
        if result and "text" in result:
            transcription = result["text"].strip()
            print(f"✅ Alfredo: Transcrição finalizada! ({len(transcription)} caracteres)")
            return transcription
        else:
            print("🤔 Alfredo: Whisper não conseguiu extrair texto")
            return None
            
    except ImportError:
        print("💡 Alfredo: Whisper não está instalado ainda")
        return None
    except Exception as e:
        print(f"😅 Alfredo: Problema com o Whisper: {e}")
        return None

def transcribe_with_basic_method(audio_path: Path) -> str:
    """Método básico quando Whisper não está disponível"""
    print("📝 Alfredo: Fazendo análise básica do arquivo...")
    
    # Informações básicas do arquivo
    size_mb = audio_path.stat().st_size / (1024 * 1024)
    duration_info = get_audio_duration(audio_path)
    
    return f"""[ANÁLISE BÁSICA DE ARQUIVO]
Arquivo: {audio_path.name}
Tamanho: {size_mb:.1f} MB
{duration_info}

Nota: Para transcrição completa, instale o Whisper com:
pip install openai-whisper

Depois execute novamente para uma análise completa do conteúdo de áudio! 🎧"""

def get_audio_duration(audio_path: Path) -> str:
    """Obtém duração do áudio usando ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"Duração: {minutes}:{seconds:02d}"
        
    except Exception:
        pass
    
    return "Duração: Não determinada"

def analyze_transcription(transcription: str, source_name: str) -> str:
    """Analisa a transcrição usando Alfredo"""
    if "[TRANSCRIÇÃO BÁSICA]" in transcription:
        return generate_basic_summary(transcription, source_name)
    
    print("� Alfredo: Analisando o conteúdo da transcrição...")
    
    prompt = f"""Você é o Alfredo, um assistente especializado em análise de conteúdo educativo e técnico.

Analise esta transcrição de áudio e crie um resumo estruturado focado nos conceitos principais:

TRANSCRIÇÃO:
{transcription}

Crie uma análise completa no formato Markdown seguindo EXATAMENTE esta estrutura:

# {source_name}

> 🤖 **Resumo criado por Alfredo** - Análise completa de áudio

## 📋 Resumo Executivo
[Uma síntese clara e objetiva do conteúdo principal em 2-3 frases, focando no tema central]

## 🎯 Conceitos Principais
- **[Nome do Conceito 1]**: [Explicação clara e direta]
- **[Nome do Conceito 2]**: [Explicação clara e direta] 
- **[Nome do Conceito 3]**: [Explicação clara e direta]

## 📚 Desenvolvimento do Conteúdo
[Análise detalhada dos temas abordados, mantendo o foco nos conceitos técnicos ou educativos apresentados]

## 💡 Insights e Aprendizados
- [Ponto importante ou insight revelador]
- [Observação relevante sobre o tema]
- [Conclusão ou aplicação prática]

## � Pontos de Destaque
- **Tema Principal**: [Qual o foco central do conteúdo]
- **Público-Alvo**: [Para quem esse conteúdo é direcionado]
- **Nível**: [Básico/Intermediário/Avançado]

## � Notas para Revisão
- [ ] [Conceito chave para revisar]
- [ ] [Tópico para aprofundar]
- [ ] [Prática recomendada]

---
*📅 Análise criada em {datetime.now().strftime("%d/%m/%Y às %H:%M")}*  
*🎧 Fonte: {source_name}*  
*🤖 "Extraindo o melhor do seu conteúdo!"*

**Nota**: Este resumo foca nos conceitos e aprendizados principais. A transcrição completa está disponível para consulta detalhada."""

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/generate", 
                               json=payload, timeout=240)  # Aumentado para 4 minutos
        response.raise_for_status()
        return response.json()['response'].strip()
    except requests.exceptions.Timeout:
        print("⏰ Alfredo: A análise demorou demais, vou criar um resumo próprio...")
        return generate_smart_summary(transcription, source_name)
    except Exception as e:
        print(f"😅 Alfredo: Tive um problema técnico, mas não se preocupe: {e}")
        return generate_smart_summary(transcription, source_name)

def generate_smart_summary(transcription: str, source_name: str) -> str:
    """Gera resumo inteligente quando Ollama não responder"""
    word_count = len(transcription.split())
    char_count = len(transcription)
    
    # Análise básica da transcrição
    words = transcription.lower().split()
    
    # Detectar temas técnicos comuns
    programming_terms = sum(1 for word in words if word in ['array', 'javascript', 'python', 'código', 'função', 'variável', 'algoritmo', 'programação'])
    tech_terms = sum(1 for word in words if word in ['sistema', 'dados', 'estrutura', 'memória', 'processo', 'aplicação'])
    
    # Determinar categoria
    if programming_terms > 5:
        category = "Programação"
        emoji = "💻"
    elif tech_terms > 5:
        category = "Tecnologia"
        emoji = "🔧"
    else:
        category = "Educativo"
        emoji = "📚"
    
    # Extrair algumas frases-chave (primeiras frases significativas)
    sentences = transcription.replace('.', '.|').replace('?', '?|').replace('!', '!|').split('|')
    key_sentences = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
    
    return f"""# {source_name}

> 🤖 **Resumo criado por Alfredo** - Análise de áudio com processamento inteligente

## 📋 Resumo Executivo
Este conteúdo de {category.lower()} foi analisado automaticamente. Com {word_count:,} palavras, apresenta conceitos técnicos e educativos relevantes para o tema abordado.

## {emoji} Análise de Conteúdo
**Categoria Detectada**: {category}  
**Extensão**: {word_count:,} palavras ({char_count:,} caracteres)  
**Processamento**: {datetime.now().strftime("%d/%m/%Y às %H:%M")}

## 🔍 Primeiras Impressões
{chr(10).join(f"• {sentence}" for sentence in key_sentences[:3])}

## 📝 Transcrição Completa
```
{transcription}
```

## 💡 Para Análise Completa
Quando o Ollama estiver disponível, execute novamente para obter:
- Resumo detalhado dos conceitos
- Estruturação temática
- Insights e pontos principais
- Checklist de aprendizado

### Como Resolver
1. Verifique se o Ollama está rodando: `ollama serve`
2. Confirme o modelo: `ollama pull llama3:8b`
3. Execute novamente: `python Alfredo.py audioa`

---
*📅 Processado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}*  
*🎧 Fonte: {source_name}*  
*🤖 "Sempre encontro uma forma de ajudar!"*"""

def generate_basic_summary(transcription: str, source_name: str) -> str:
    """Gera resumo básico quando Whisper não está disponível"""
    word_count = len(transcription.split())
    char_count = len(transcription)
    
    return f"""# {source_name}

> 🤖 **Resumo criado por Alfredo** - Análise básica de áudio

## 📊 Estatísticas do Arquivo
- Caracteres: {char_count:,}
- Palavras estimadas: {word_count:,}
- Processado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}

## 📝 Conteúdo Extraído
{transcription}

## � Quer Mais?
Para uma análise completa e inteligente, você precisa do Whisper instalado!

### Como Instalar
```bash
pip install openai-whisper
```

Depois é só executar novamente e eu farei uma análise muito mais detalhada! 😊

## 💡 Dica do Alfredo
Também certifique-se de que o Ollama está funcionando:
- Execute: `ollama serve`
- Instale o modelo: `ollama pull llama3:8b`

---
*🎧 Análise básica por Alfredo*  
*🤖 "Sempre melhorando para você!"*"""

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

def find_audio_files(search_dir: Optional[Path] = None) -> list[Path]:
    """Encontra arquivos de áudio/vídeo"""
    if search_dir is None:
        search_dirs = [paths.INPUT_LOCAL, Path.cwd()]
    else:
        search_dirs = [search_dir]
    
    files = []
    
    for search_path in search_dirs:
        print(f"🔍 Alfredo: Procurando arquivos em {search_path}")
        
        for ext in AUDIO_EXTENSIONS:
            files.extend(search_path.glob(f"*{ext}"))
            files.extend(search_path.glob(f"*{ext.upper()}"))
            files.extend(search_path.glob(f"*/*{ext}"))
            files.extend(search_path.glob(f"*/*{ext.upper()}"))
        
        if files:
            break
    
    return sorted(set(files))

def select_audio_file() -> Optional[Path]:
    """Seleciona arquivo de áudio interativamente"""
    files = find_audio_files()
    
    if not files:
        print("� Alfredo: Não encontrei arquivos de áudio/vídeo!")
        print(f"   📋 Formatos que eu entendo: {', '.join(AUDIO_EXTENSIONS)}")
        print("💡 Coloque alguns arquivos aqui e me chame novamente!")
        return None
    
    print(f"\n🎵 Alfredo: Achei {len(files)} arquivo(s) interessante(s):")
    
    if len(files) == 1:
        file = files[0]
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"🎯 Arquivo: {file.name} ({size_mb:.1f} MB)")
        
        confirm = input("🤖 Posso analisar este arquivo? (s/N): ").strip().lower()
        return file if confirm in ['s', 'sim', 'y', 'yes'] else None
    
    # Múltiplos arquivos - mostrar menu
    for i, file in enumerate(files[:10], 1):  # Máximo 10
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  [{i}] {file.name} ({size_mb:.1f} MB)")
    
    if len(files) > 10:
        print(f"  ... e mais {len(files) - 10} arquivo(s)")
    
    try:
        choice = input("\n🤖 Escolha um arquivo (1-10): ").strip()
        index = int(choice) - 1
        
        if 0 <= index < min(len(files), 10):
            return files[index]
        else:
            print("😅 Número inválido!")
            return None
            
    except ValueError:
        print("😊 Por favor, digite um número!")
        return None

def main():
    """Função principal - análise de áudio"""
    print("🤖" + "=" * 58 + "🤖")
    print("║" + " " * 22 + "ALFREDO - ÁUDIO" + " " * 22 + "║")
    print("║" + " " * 15 + "Sistema de Análise de Áudio" + " " * 16 + "║")
    print("║" + " " * 18 + "\"Muito mais rápido!\"" + " " * 19 + "║")
    print("🤖" + "=" * 58 + "🤖")
    
    print("🤖 Alfredo: Oi! Vou analisar o áudio do seu arquivo!")
    print("⚡ Esta análise é muito mais rápida que análise visual")
    
    # Verificar se arquivo foi passado como argumento
    import sys
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            print(f"😕 Alfredo: Não encontrei o arquivo {file_path}")
            return False
        print(f"🎵 Alfredo: Vou analisar: {file_path.name}")
    else:
        file_path = select_audio_file()
        if not file_path:
            print("👋 Alfredo: Até logo! Qualquer coisa me chama de novo!")
            return False
    
    start_time = time.time()
    
    # 1. Extrair áudio (se for vídeo)
    if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        audio_path = extract_audio(file_path)
        if not audio_path:
            return False
    else:
        audio_path = file_path
        print(f"🎵 Alfredo: Arquivo de áudio detectado: {audio_path.name}")
    
    # 2. Transcrever áudio
    transcription = transcribe_audio(audio_path)
    if not transcription:
        print("😕 Alfredo: Não consegui transcrever o áudio")
        return False
    
    # 3. Analisar com inteligência
    summary = analyze_transcription(transcription, file_path.stem)
    
    # 4. Salvar resultado com versionamento automático
    base_summary_path = paths.get_output_summary_path(file_path.stem, "audio")
    base_summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Obter caminho com versionamento se necessário
    summary_path = get_versioned_output_path(base_summary_path)
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        total_time = time.time() - start_time
        
        # Verificar se é uma nova versão
        if summary_path != base_summary_path:
            version_info = f" (versão {summary_path.stem.split('-v')[-1]})"
            print(f"\n🎉 ALFREDO: NOVA VERSÃO CRIADA!")
            print(f"📝 Arquivo já existia, criando{version_info}")
        else:
            print(f"\n🎉 ALFREDO: ANÁLISE CONCLUÍDA!")
        
        print(f"⏱️ Tempo total: {total_time:.1f}s ({total_time/60:.1f} min)")
        print(f"📄 Resumo salvo em: {summary_path}")
        print("🚀 Análise de áudio é realmente mais rápida!")
        
        return True
        
    except Exception as e:
        print(f"😅 Alfredo: Problema ao salvar: {e}")
        return False

if __name__ == "__main__":
    main()
