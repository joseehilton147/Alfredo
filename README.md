# Alfredo AI 🤖

**AI-powered video transcription and analysis tool**

## 🎯 O que é o Alfredo AI?

O Alfredo AI é uma ferramenta simples que utiliza OpenAI Whisper para:
- ✅ Transcrever áudio de vídeos automaticamente
- ✅ Processar vídeos locais
- ✅ Baixar e processar vídeos do YouTube
- ✅ Salvar transcrições em formato JSON

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

## 📁 Estrutura do Projeto

```
alfredo-ai/
├── src/                          # Código fonte
│   ├── main.py                   # Ponto de entrada
│   ├── application/              # Casos de uso
│   ├── domain/                   # Entidades de negócio
│   ├── infrastructure/           # Provedores externos
│   └── config/                   # Configurações
├── tests/                        # Testes (100% cobertura)
├── data/                         # Dados processados
│   ├── input/                    # Vídeos de entrada
│   ├── output/                   # Resultados
│   └── logs/                     # Logs da aplicação
├── requirements.txt              # Dependências mínimas
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
```

## 🧪 Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
pytest

# Executar testes com cobertura
pytest --cov=src

# Formatar código
black src/ tests/
isort src/ tests/

# Verificar tipos
mypy src/
```

## 📋 Requisitos

- Python 3.8+
- FFmpeg (para processamento de áudio)
- ~2GB de espaço livre (para modelos Whisper)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🙋‍♂️ Suporte

- 📧 Email: joseehilton147@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/joseehilton147/alfredo-ai/issues)

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!** ⭐

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API
```

### Método 2: Docker

```bash
# Build da imagem
docker build -t alfredo-ai .

# Execução
docker run -v $(pwd)/data:/app/data alfredo-ai

# Ou com Docker Compose
docker-compose up
```

## 📋 Pré-requisitos

- Python 3.8+
- FFmpeg (para processamento de vídeo)
- Chave de API Groq (para transcrição)

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
Baixe em: https://ffmpeg.org/download.html

## 🔧 Configuração

1. Copie o arquivo `.env.example` para `.env`
2. Adicione sua chave de API Groq:
   ```
   GROQ_API_KEY=sua_chave_aqui
   ```

## 🎮 Uso

### Processar vídeo local:
```bash
python -m src.main -i data/input/local/meu_video.mp4
```

### Processar vídeo do YouTube:
```bash
python -m src.main -y https://youtube.com/watch?v=VIDEO_ID
```

### Opções adicionais:
```bash
# Modo verbose
python -m src.main -i video.mp4 -v

# Especificar idioma
python -m src.main -i video.mp4 -l pt

# Salvar transcrição em arquivo
python -m src.main -i video.mp4 -o data/output/transcricao.txt
```

## 📁 Estrutura de Diretórios

```
alfredo-ai/
├── src/                    # Código fonte
│   ├── application/        # Casos de uso
│   ├── domain/            # Entidades e regras de negócio
│   └── infrastructure/    # Implementações concretas
├── data/                  # Dados do projeto
│   ├── input/local/       # Vídeos locais
│   ├── input/youtube/     # Vídeos do YouTube
│   ├── output/            # Arquivos processados
│   └── logs/              # Logs de execução
├── tests/                 # Testes
├── examples/              # Exemplos de uso
├── Dockerfile            # Container Docker
└── docker-compose.yml    # Configuração Docker Compose
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Teste específico
pytest tests/test_video_entity.py
```

## 🛠️ Desenvolvimento

### Configuração do ambiente de desenvolvimento:
```bash
# Instalar pre-commit hooks
pre-commit install

# Formatar código
make format

# Verificar estilo
make lint

# Executar testes
make test
```

### Comandos disponíveis:
```bash
make help  # Ver todos os comandos disponíveis
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os [issues](https://github.com/joseehilton147/alfredo-ai/issues)
2. Crie um novo issue com descrição detalhada
3. Inclua logs e exemplos quando possível

## 🙏 Agradecimentos

- [Groq](https://groq.com/) pela API de transcrição
- [Whisper](https://github.com/openai/whisper) pelo modelo de transcrição
- Comunidade open source pelas ferramentas utilizadas
