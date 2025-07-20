# Guia de Instalação - Alfredo AI

Este guia fornece instruções detalhadas para instalar o Alfredo AI em diferentes sistemas operacionais.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação no Windows](#instalação-no-windows)
- [Instalação no macOS](#instalação-no-macos)
- [Instalação no Linux](#instalação-no-linux)
- [Instalação com Docker](#instalação-com-docker)
- [Configuração de API](#configuração-de-api)
- [Verificação da Instalação](#verificação-da-instalação)
- [Solução de Problemas](#solução-de-problemas)

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, Debian 10+, CentOS 8+)

### Software Necessário
- Python 3.8 ou superior
- FFmpeg (para processamento de vídeo)
- Git (para clonar o repositório)

### Hardware Recomendado
- RAM: 4GB ou mais
- Espaço em disco: 2GB livres
- Conexão com internet (para download de vídeos e APIs)

## 🪟 Instalação no Windows

### 1. Instalar Python
1. Acesse [python.org](https://www.python.org/downloads/windows/)
2. Baixe a versão mais recente do Python 3.x
3. Durante a instalação, marque **"Add Python to PATH"**
4. Verifique a instalação:
   ```cmd
   python --version
   ```

### 2. Instalar FFmpeg
**Opção 1 - Chocolatey (recomendado):**
```cmd
# Instale o Chocolatey (se ainda não tiver)
# Abra o PowerShell como administrador
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Instale o FFmpeg
choco install ffmpeg
```

**Opção 2 - Manual:**
1. Acesse [ffmpeg.org](https://ffmpeg.org/download.html)
2. Baixe a versão Windows
3. Extraia para `C:\ffmpeg`
4. Adicione `C:\ffmpeg\bin` ao PATH do sistema

### 3. Instalar Alfredo AI
```cmd
# Clone o repositório
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai

# Crie ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
```

## 🍎 Instalação no macOS

### 1. Instalar Homebrew (se ainda não tiver)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Instalar Python e FFmpeg
```bash
# Instale Python
brew install python@3.11

# Instale FFmpeg
brew install ffmpeg

# Verifique instalações
python3 --version
ffmpeg -version
```

### 3. Instalar Alfredo AI
```bash
# Clone o repositório
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

## 🐧 Instalação no Linux (Ubuntu/Debian)

### 1. Atualizar sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Python e FFmpeg
```bash
# Instale Python e pip
sudo apt install python3 python3-pip python3-venv -y

# Instale FFmpeg
sudo apt install ffmpeg -y

# Verifique instalações
python3 --version
ffmpeg -version
```

### 3. Instalar Alfredo AI
```bash
# Clone o repositório
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

## 🐳 Instalação com Docker

### 1. Instalar Docker
- **Windows/macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux:** [Docker Engine](https://docs.docker.com/engine/install/)

### 2. Usar com Docker
```bash
# Clone o repositório
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai

# Build da imagem
docker build -t alfredo-ai .

# Executar
docker run -v $(pwd)/data:/app/data alfredo-ai
```

### 3. Usar com Docker Compose
```bash
# Executar com Docker Compose
docker-compose up

# Ou em background
docker-compose up -d
```

## 🔑 Configuração de API

### 1. Obter chave Groq API
1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta ou faça login
3. Vá para "API Keys"
4. Crie uma nova chave
5. Copie a chave gerada

### 2. Configurar variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env
nano .env  # ou use seu editor preferido
```

### 3. Adicionar chave ao .env
```bash
# No arquivo .env, adicione:
GROQ_API_KEY=sua_chave_aqui
```

## ✅ Verificação da Instalação

Execute o script de verificação:
```bash
# Verificar estrutura e dependências
python test_basic.py

# Ou use make
make check
```

Se tudo estiver correto, você verá:
```
✅ Estrutura completa!
✅ Todos os módulos principais importados com sucesso!
✅ Todas as dependências principais instaladas!
🎉 Tudo pronto! Alfredo AI está configurado corretamente.
```

## 🧪 Teste Rápido

```bash
# Testar com um vídeo de exemplo
python -m src.main -i examples/sample_video.mp4

# Ou testar transcrição
python -m src.main -i examples/sample_video.mp4 --test-transcription
```

## 🔧 Solução de Problemas

### Problema: "ffmpeg não encontrado"
```bash
# Verifique se está no PATH
which ffmpeg  # Linux/macOS
where ffmpeg  # Windows

# Se não encontrar, adicione ao PATH ou reinstale
```

### Problema: "ModuleNotFoundError"
```bash
# Reinstale dependências
pip install -r requirements.txt --force-reinstall

# Verifique se está no ambiente virtual correto
which python  # Deve apontar para o venv
```

### Problema: "Permission denied" no macOS/Linux
```bash
# Dê permissão de execução
chmod +x src/main.py
```

### Problema: Erro de API
```bash
# Verifique a chave API
echo $GROQ_API_KEY  # Linux/macOS
echo %GROQ_API_KEY%  # Windows

# Teste a conexão
curl -H "Authorization: Bearer sua_chave" https://api.groq.com/openai/v1/models
```

### Problema: Docker não encontra arquivos
```bash
# Verifique os volumes
docker run -v $(pwd)/data:/app/data --rm alfredo-ai ls /app/data
```

## 🛠️ Comandos de Desenvolvimento

Após a instalação, você pode usar os seguintes comandos para desenvolvimento:

### Configuração e Instalação
```bash
make help               # Ver todos os comandos disponíveis
make setup              # Configuração completa do projeto (recomendado)
make install            # Instalar apenas dependências
make install-dev        # Instalar dependências de desenvolvimento
```

### Testes
```bash
make test               # Executar todos os testes
make test-unit          # Apenas testes unitários
make test-integration   # Apenas testes de integração
make test-bdd          # Apenas testes BDD
make test-coverage     # Testes com cobertura detalhada
```

### Qualidade de Código
```bash
make quality-check      # Pipeline completo de qualidade
make quality-report     # Relatório abrangente de qualidade
make format            # Formatar código automaticamente
make lint              # Verificar estilo e qualidade do código
make complexity        # Análise de complexidade
make security          # Análise de segurança
make solid-check       # Verificação de princípios SOLID
```

### Análise de Cobertura
```bash
make coverage-analysis      # Análise detalhada de cobertura
make coverage-analysis-quick # Análise rápida (dados existentes)
make coverage-regression    # Verificação de regressão
make quality-dashboard      # Dashboard local de qualidade
```

### Docker
```bash
make docker-build      # Build da imagem Docker
make docker-run        # Executar com Docker
make docker-up         # Iniciar com docker-compose
```

### Limpeza
```bash
make clean             # Limpeza básica
make clean-all         # Limpeza completa
make clean-quality     # Limpar artefatos de qualidade
```

## 📞 Suporte

Se continuar com problemas:
1. Verifique os [issues](https://github.com/joseehilton147/alfredo-ai/issues)
2. Crie um novo issue com:
   - Sistema operacional
   - Versão do Python
   - Mensagem de erro completa
   - Comandos executados
