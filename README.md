# Alfredo AI 🤖

Assistente inteligente para análise e processamento de vídeos com IA.

## 🎯 O que é o Alfredo AI?

O Alfredo AI é uma ferramenta que utiliza inteligência artificial para:
- Transcrever áudio de vídeos automaticamente
- Identificar e marcar cenas importantes
- Gerar resumos e insights dos vídeos
- Processar vídeos locais ou do YouTube

## 🚀 Instalação

### Método 1: Instalação Local

```bash
# Clone o repositório
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento

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
