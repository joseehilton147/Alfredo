# 🤖 Video Summarizer - Alfredo AI

> **Sistema de análise inteligente de vídeos e áudios usando IA open-source**

Um assistente pessoal para transformar conteúdo audiovisual em resumos estruturados e insights educativos. O Alfredo utiliza tecnologias como Whisper (OpenAI) e Ollama para processar e analisar conteúdo de forma rápida e eficiente.

## 🏗️ **Nova Arquitetura Modular**

O Alfredo foi refatorado para uma **arquitetura modular e escalável**:

```
/alfredo/
├── cli/                  # Comandos CLI independentes 
├── api/                  # Futuras APIs REST/web
├── core/                 # Lógica de negócio central
├── integrations/         # Integrações externas (Groq, Ollama)
├── config/              # Configurações e i18n
├── data/                # Dados (entrada, saída, cache)
├── tests/               # Testes (unit, integration, e2e)
├── scripts/             # Scripts utilitários
└── legacy/              # Código para migração
```

### 🎯 **Benefícios da Nova Estrutura**

- **🔧 Comandos CLI Independentes**: Cada comando pode ser executado isoladamente
- **🌍 Internacionalização**: Suporte nativo a múltiplos idiomas (PT/EN)
- **🔌 Integrações Modulares**: Provedores de IA separados e intercambiáveis  
- **🧪 Testes Robustos**: Cobertura de testes por domínio e integração
- **📈 Escalabilidade**: Estrutura preparada para APIs web futuras

## ⚠️ **Aviso Importante**

Este projeto **NÃO compete** com LLMs frontier como GPT-4, Claude ou Gemini. É uma solução experimental usando ferramentas **totalmente open-source** e está em **fase inicial de desenvolvimento**. O objetivo é aprender e explorar as possibilidades das ferramentas abertas disponíveis.

## 🌟 **Características Principais**

- **🎧 Análise de Áudio**: Transcrição automática usando Whisper (3-5 min vs 10+ min visual)
- **🎬 Análise Visual**: Extração de frames e análise com IA (processo mais lento)
- **📹 YouTube**: Download e análise automática de vídeos do YouTube
- **🧹 Limpeza Inteligente**: Sistema de limpeza de arquivos temporários
- **🤖 Interface Amigável**: Comunicação natural e feedback em tempo real
- **📊 Múltiplos Formatos**: Suporte a MP4, AVI, MOV, MKV, WebM, MP3, WAV, etc.

## 🚀 **Comandos Disponíveis**

### 📋 **Comandos Principais**

```bash
# ANÁLISE RÁPIDA (Recomendado)
alfredo resumir-audio-local <arquivo>     # Análise de áudio (3-5 min)

# ANÁLISE COMPLETA
alfredo resumir-video-local <arquivo>     # Análise visual (10+ min)

# YOUTUBE
alfredo baixar-yt <url>                   # Baixar vídeo do YouTube
alfredo resumir-yt <url>                  # Baixar + analisar YouTube

# UTILIDADES
alfredo limpar-cache [1-5]                # Limpeza inteligente
alfredo --help                            # Ajuda
alfredo --list                            # Listar comandos
```

### 🎯 **Comandos Mais Usados**

| Comando | Tempo | Descrição | Recomendação |
|---------|--------|-----------|--------------|
| `resumir-audio-local` | 3-5 min | Análise só do áudio | ⭐ **Mais rápido** |
| `resumir-video-local` | 10+ min | Análise visual completa | Para conteúdo visual específico |
| `resumir-yt` | 5-15 min | YouTube + análise | Para vídeos online |

## 📦 **Instalação Completa**

### **Pré-requisitos**

1. **Python 3.8+** (recomendado 3.10+)
2. **Git** para clonagem
3. **ffmpeg** para processamento de vídeo/áudio

### **Passo 1: Clonar o Repositório**

```bash
git clone https://github.com/joseehilton147/Alfredo.git
cd Alfredo
```

### **Passo 2: Instalar o Projeto**

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar o projeto em modo desenvolvimento
pip install -e .

# Isso instalará todas as dependências e criará os comandos CLI
```

### **Passo 3: Instalar ffmpeg**

#### **Windows:**
1. Baixe em: https://ffmpeg.org/download.html
2. Extraia e adicione ao PATH do sistema
3. Teste: `ffmpeg -version`

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### **macOS:**
```bash
# Com Homebrew
brew install ffmpeg
```

### **Passo 4: Configurar Ollama (Para Análise Avançada)**

```bash
# Instalar Ollama
# Windows/Linux/Mac: https://ollama.ai/download

# Instalar modelo recomendado
ollama pull llama3:8b

# Iniciar servidor (manter rodando)
ollama serve
```

### **Passo 5: Testar Instalação**

```bash
# Verificar se tudo está funcionando
alfredo --test

# Listar comandos disponíveis
alfredo --list

# Testar com arquivo de exemplo
alfredo resumir-audio-local exemplo.mp4
```

## 📁 **Estrutura do Projeto**

```
alfredo/
├── 📦 pyproject.toml          # Configuração do projeto
├── 📋 requirements.txt        # Dependências Python (legacy)
├── 📖 README.md              # Este arquivo
├── 🎯 cli/                   # Comandos CLI independentes
│   ├── alfredo.py            # Interface principal
│   ├── audio_analyzer.py     # Análise de áudio
│   ├── video_local.py        # Análise visual local
│   ├── youtube_ai.py         # YouTube + IA
│   └── clean.py              # Limpeza de cache
├── 🧠 core/                  # Lógica de negócio central
│   ├── alfredo_core.py       # Sistema central
│   └── prompt_service.py     # Gerenciamento de prompts
├── 🔌 integrations/          # Integrações externas
│   ├── groq/                 # Provedor Groq
│   └── ollama/               # Provedor Ollama
├── ⚙️ config/                # Configurações e i18n
│   ├── settings.py           # Configurações
│   ├── i18n.py               # Internacionalização
│   └── locales/              # Traduções (PT/EN)
├── 🎬 commands/              # Comandos backend
│   └── video/
│       ├── audio_analyzer.py  # Análise de áudio
│       ├── local_video.py     # Análise visual
│       └── youtube_ai.py      # Análise YouTube
├── 📂 data/                  # Dados e cache
│   ├── input/local/          # Vídeos de entrada
│   ├── output/summaries/     # Resumos gerados
│   └── cache/                # Arquivos temporários
├── 🧪 tests/                 # Testes automatizados
│   ├── unit/                 # Testes unitários
│   ├── integration/          # Testes de integração
│   └── e2e/                  # Testes end-to-end
└── 🗂️ legacy/                # Código legado (migração)
└── 🗑️ _temp/                 # Cache antigo (será migrado)
```

## 🎯 **Como Usar**

### **1. Análise Rápida de Áudio (Recomendado)**

```bash
# Coloque seu vídeo em data/input/local/
cp meu_video.mp4 data/input/local/

# Execute análise de áudio (mais rápida)
alfredo resumir-audio-local meu_video.mp4

# O resumo será salvo em:
# data/output/summaries/audio/meu_video.md
```

### **2. Análise Visual Completa**

```bash
# Para análise visual detalhada
alfredo resumir-video-local meu_video.mp4

# Resultado em:
# data/output/summaries/visual/meu_video.md
```

### **3. YouTube**

```bash
# Analisar vídeo do YouTube
alfredo resumir-yt "https://youtube.com/watch?v=..."

# Apenas baixar vídeo
alfredo baixar-yt "https://youtube.com/watch?v=..."
```

### **4. Limpeza**

```bash
# Limpeza leve (nível 1)
alfredo limpar-cache 1

# Limpeza pesada (nível 5)
alfredo limpar-cache 5
```

## ⚙️ **Configuração**

### **Formatos Suportados**

- **Vídeo**: MP4, AVI, MOV, MKV, WebM
- **Áudio**: MP3, WAV, M4A, FLAC
- **YouTube**: Qualquer URL válida

### **Personalização**

Edite `config/paths.py` para alterar diretórios:

```python
# Exemplo de personalização
INPUT_LOCAL = Path("meus_videos")  # Pasta de entrada
OUTPUT_ROOT = Path("resultados")   # Pasta de saída
```

## 🐛 **Solução de Problemas**

### **Problemas Comuns**

| Problema | Solução |
|----------|---------|
| `ffmpeg não encontrado` | Instale ffmpeg e adicione ao PATH |
| `Whisper muito lento` | Use `audioa` em vez de `videol` |
| `Ollama timeout` | Verifique se `ollama serve` está rodando |
| `Módulo não encontrado` | Execute `pip install -r requirements.txt` |

### **Logs e Debug**

```bash
# Verificar status dos serviços
alfredo --test

# Ver informações detalhadas do sistema
alfredo info-pc

# Verificar status da API Groq
alfredo groq-status
```

## 📊 **Performance**

| Tipo de Análise | Tempo Médio | Qualidade | Recomendação |
|------------------|-------------|-----------|--------------|
| **Áudio** (resumir-audio-local) | 3-5 min | ⭐⭐⭐⭐ | Uso geral |
| **Visual** (resumir-video-local) | 10-15 min | ⭐⭐⭐⭐⭐ | Conteúdo visual específico |
| **YouTube** (resumir-yt) | 5-10 min | ⭐⭐⭐⭐ | Vídeos online |

## 🤝 **Contribuição**

Este projeto está em **desenvolvimento inicial**. Contribuições são bem-vindas:

1. Fork o projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit: `git commit -m "Adiciona nova feature"`
4. Push: `git push origin minha-feature`
5. Abra um Pull Request

## 📄 **Licença**

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🙏 **Agradecimentos**

- **OpenAI Whisper** - Transcrição de áudio
- **Ollama** - Modelos de linguagem locais
- **ffmpeg** - Processamento de mídia
- **yt-dlp** - Download do YouTube

## 📞 **Contato**

- 📧 Linkedin: [Jose Hilton](https://www.linkedin.com/in/jose-hilton/)
- 🐙 GitHub: [joseehilton147](https://github.com/joseehilton147)
- 💬 Issues: [Reportar problemas](https://github.com/joseehilton147/Alfredo/issues)

---

> 🤖 **"Transformando vídeos em conhecimento, um frame de cada vez!"** - Alfredo AI

**Feito com ❤️ e muita ☕ para a comunidade open-source**
