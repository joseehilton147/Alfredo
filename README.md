# Alfredo AI 🤖

AI-powered video transcription and analysis tool using OpenAI Whisper

## 🎯 O que é o Alfredo AI?

O Alfredo AI é uma ferramenta que utiliza OpenAI Whisper para:

- ✅ Transcrever áudio de vídeos automaticamente
- ✅ Processar vídeos locais
- ✅ Baixar e processar vídeos do YouTube
- ✅ Salvar transcrições em formato JSON
- ✅ Suporte a múltiplos idiomas (padrão: Português)

## 🚀 Instalação Rápida

### 1. Clone e Instale

```bash
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai
pip install -r requirements.txt
pip install -e .
```

### 2. Configure (Opcional)

```bash
cp .env.example .env
# Edite .env conforme necessário
```

### 3. Execute

```bash
# Processar vídeo local
python -m src.main --input caminho/para/video.mp4

# Baixar e processar do YouTube
python -m src.main --url "https://youtube.com/watch?v=VIDEO_ID"

# Processar vários vídeos
python -m src.main --batch pasta/com/videos/

# Ver todas as opções
python -m src.main --help
```

## 🐳 Docker

```bash
# Build
docker build -t alfredo-ai .

# Run
docker run -v $(pwd)/data:/app/data alfredo-ai python -m src.main --help
```

## 📋 Pré-requisitos

- Python 3.8+
- FFmpeg (para processamento de áudio/vídeo)
- ~2GB de espaço livre (para modelos Whisper)

### Instalação do FFmpeg

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Windows:**

Baixe em: <https://ffmpeg.org/download.html>

## 📁 Estrutura do Projeto

```text
alfredo-ai/
├── src/                          # Código fonte
│   ├── main.py                   # Ponto de entrada
│   ├── application/              # Casos de uso
│   ├── domain/                   # Entidades de negócio
│   ├── infrastructure/           # Provedores externos
│   └── config/                   # Configurações
├── tests/                        # Testes (98% cobertura)
├── data/                         # Dados processados
│   ├── input/                    # Vídeos de entrada
│   │   ├── local/                # Vídeos locais
│   │   └── youtube/              # Vídeos do YouTube
│   ├── output/                   # Resultados
│   ├── logs/                     # Logs da aplicação
│   └── temp/                     # Arquivos temporários
├── requirements.txt              # Dependências mínimas
├── requirements-dev.txt          # Dependências de desenvolvimento
└── README.md                     # Este arquivo
```

## ⚡ Exemplos de Uso

```bash
# Básico
python -m src.main --input video.mp4

# Com idioma específico
python -m src.main --input video.mp4 --language en

# Modo verbose
python -m src.main --input video.mp4 --verbose

# YouTube
python -m src.main --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Processamento em lote
python -m src.main --batch /pasta/com/videos/
```

## 🧪 Desenvolvimento

### Configuração do ambiente de desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
make test

# Executar testes com cobertura
pytest --cov=src --cov-report=html

# Formatar código
make format

# Verificar tipos e linting
make lint

# Setup completo
make setup
```

### Comandos disponíveis

```bash
make help  # Ver todos os comandos disponíveis
```

## 🧪 Testes

O projeto possui 98% de cobertura de testes com 64 testes automatizados.

```bash
# Executar todos os testes
make test

# Testes com relatório HTML
pytest --cov=src --cov-report=html

# Teste específico
pytest tests/test_main.py
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- [OpenAI Whisper](https://github.com/openai/whisper) pelo modelo de transcrição
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) para download de vídeos do YouTube
- Comunidade open source pelas ferramentas utilizadas

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!** ⭐
