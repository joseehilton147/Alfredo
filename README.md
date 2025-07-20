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
│   ├── application/              # Casos de uso e gateways
│   │   ├── use_cases/            # Lógica de aplicação
│   │   └── gateways/             # Interfaces abstratas
│   ├── domain/                   # Entidades de negócio
│   │   ├── entities/             # Entidades principais
│   │   ├── exceptions/           # Exceções customizadas
│   │   └── validators/           # Validadores de domínio
│   ├── infrastructure/           # Implementações concretas
│   │   ├── providers/            # Provedores de IA
│   │   ├── repositories/         # Persistência de dados
│   │   └── factories/            # Criação de dependências
│   ├── presentation/             # Interface com usuário
│   │   └── cli/                  # Comandos CLI
│   └── config/                   # Configurações tipadas
├── tests/                        # Testes (cobertura 80%+)
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

### Configuração do Ambiente
```bash
# Setup completo (recomendado)
make setup

# Ou instalação manual
pip install -r requirements-dev.txt
make install-dev
```

### Testes
```bash
# Executar todos os testes
make test

# Testes específicos
make test-unit           # Apenas testes unitários
make test-integration    # Apenas testes de integração
make test-bdd           # Apenas testes BDD
make test-performance   # Testes de performance

# Testes com cobertura detalhada
make test-coverage

# Executar testes específicos (ex: Strategy Pattern)
pytest tests/infrastructure/providers/test_strategy_pattern.py -v
```

### Qualidade de Código
```bash
# Pipeline completo de qualidade (recomendado)
make quality-check

# Verificações individuais
make format             # Formatar código (black, isort)
make format-check       # Verificar formatação
make lint               # Análise estática (flake8, pylint)
make type-check         # Verificação de tipos (mypy)
make complexity         # Análise de complexidade
make duplication        # Detecção de duplicação
make security           # Análise de segurança
make solid-check        # Verificação de princípios SOLID

# Relatório completo de qualidade
make quality-report
```

### Análise de Cobertura
```bash
# Análise detalhada de cobertura
make coverage-analysis

# Análise rápida (sem executar testes)
make coverage-analysis-quick

# Verificar regressão de cobertura
make coverage-regression

# Dashboard de cobertura local
make quality-dashboard
```

### Docker
```bash
# Build e execução
make docker-build
make docker-run
make docker-up          # Com docker-compose

# Desenvolvimento com Docker
make docker-run-dev     # Com volumes montados
```

### Limpeza
```bash
make clean              # Limpeza básica
make clean-all          # Limpeza completa (incluindo caches)
make clean-quality      # Limpar artefatos de qualidade
```

## 🏗️ Arquitetura

O Alfredo AI segue os princípios da **Clean Architecture**:

- **Domain Layer**: Entidades de negócio, validadores e regras fundamentais
- **Application Layer**: Casos de uso e interfaces (gateways)
- **Infrastructure Layer**: Implementações concretas e provedores externos
- **Presentation Layer**: Interface CLI, comandos e interação com usuário

### Principais Gateways
- `VideoDownloaderGateway`: Interface para download de vídeos
- `AudioExtractorGateway`: Interface para extração de áudio
- `StorageGateway`: Interface para persistência de dados
- `AIStrategy`: Interface para provedores de IA (Strategy Pattern)

### Configuração e Constantes
- `AlfredoConfig`: Configuração tipada centralizada
- `src/config/constants.py`: Constantes centralizadas (365+ constantes)
- Eliminação de magic numbers e strings
- Enums para valores relacionados

### Padrões de Design Implementados
- **Strategy Pattern**: Para provedores de IA intercambiáveis
- **Command Pattern**: Para comandos CLI extensíveis
- **Factory Pattern**: Para criação de dependências
- **Dependency Injection**: Para baixo acoplamento
- **Gateway Pattern**: Para abstração de infraestrutura

### Validadores de Domínio
- `validate_video_id()`: Validação de IDs de vídeo
- `validate_video_title()`: Validação de títulos
- `validate_video_duration()`: Validação de duração
- `validate_video_sources()`: Validação de fontes (arquivo/URL)
- `validate_url_format()`: Validação de formato de URLs
- `is_youtube_url()`: Detecção de URLs do YouTube
- `is_supported_video_url()`: Verificação de plataformas suportadas

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

## 📚 Documentação Adicional

- [🏗️ Arquitetura](docs/ARCHITECTURE.md) - Detalhes da Clean Architecture
- [🔧 Ferramentas de Qualidade](docs/QUALITY_TOOLS.md) - Análise de cobertura e qualidade
- [🎯 Padrões de Design](docs/DESIGN_PATTERNS.md) - Padrões implementados
- [🚪 Gateways](docs/GATEWAYS.md) - Interfaces e implementações
- [✅ Validadores](docs/VALIDATORS.md) - Validação de domínio

### Exemplos Práticos

- [📋 Uso Básico](examples/basic_usage.py) - Exemplo básico de uso dos gateways
- [🎯 Constantes](examples/constants_demo.py) - Demonstração das constantes centralizadas
- [✅ Validadores](examples/validators_demo.py) - Uso dos validadores de domínio
- [🎨 Temas](examples/theme_demo.py) - Personalização de temas CLI
- [🎯 Padrões de Design](examples/design_patterns_demo.py) - Strategy e Command patterns

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

## 🛠️ Comandos Disponíveis

### Principais Comandos
```bash
make help               # Ver todos os comandos disponíveis
make setup              # Configuração completa do projeto
make quality-check      # Pipeline completo de qualidade
make quality-report     # Relatório abrangente de qualidade
make test               # Executar todos os testes
make coverage-analysis  # Análise detalhada de cobertura
```

### Análise de Cobertura Avançada

O projeto inclui ferramentas avançadas de análise de cobertura:

```bash
# Análise completa com relatório detalhado
make coverage-analysis

# Análise rápida usando dados existentes
make coverage-analysis-quick

# Verificação de regressão de cobertura
make coverage-regression

# Relatório de qualidade completo
make quality-report
```

**Recursos dos Relatórios:**
- 📊 Cobertura detalhada por módulo
- 🔍 Identificação de módulos com baixa cobertura
- 💡 Sugestões específicas de melhoria
- 📈 Detecção automática de regressão
- 📄 Relatórios salvos em `data/output/reports/`

### Pipeline de Qualidade

O Alfredo AI implementa um pipeline completo de qualidade:

- ✅ **Formatação**: black, isort
- 🔍 **Análise Estática**: flake8, pylint, mypy
- 📊 **Complexidade**: Análise ciclomática
- 🔄 **Duplicação**: Detecção de código duplicado
- 🔒 **Segurança**: bandit, safety
- 🏗️ **SOLID**: Verificação de princípios
- 🧪 **Testes**: Cobertura 80%+

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
