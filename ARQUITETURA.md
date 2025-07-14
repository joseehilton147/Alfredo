# 🏗️ Arquitetura do Alfredo AI

## Visão Geral

O Alfredo AI foi projetado com uma **arquitetura modular e escalável** que separa claramente as responsabilidades e permite fácil manutenção e extensão do sistema.

## 🎯 Princípios de Design

### 1. **Modularidade**
- Cada módulo tem uma responsabilidade específica
- Baixo acoplamento entre componentes
- Alto grau de coesão interna

### 2. **Extensibilidade**
- Novos provedores de IA podem ser adicionados facilmente
- Comandos podem ser criados dinamicamente
- Sistema de plugins para funcionalidades futuras

### 3. **Testabilidade**
- Cobertura de testes por domínio
- Testes unitários, de integração e end-to-end
- Mocks e fixtures para isolamento

### 4. **Internacionalização**
- Suporte nativo para múltiplos idiomas
- Mensagens externalizadas em arquivos JSON
- Fácil adição de novos idiomas

## 📋 Componentes Principais

### 🎯 CLI Layer (`cli/`)
**Responsabilidade**: Interface de linha de comando para o usuário final

```
cli/
├── alfredo.py              # Interface principal consolidada
├── audio_analyzer.py       # CLI para análise de áudio
├── video_local.py          # CLI para análise de vídeo local
├── youtube_ai.py           # CLI para YouTube + IA
├── clean.py                # CLI para limpeza de cache
└── groq_status.py          # CLI para status da API Groq
```

**Características**:
- Entry points configurados no `pyproject.toml`
- Não modificam `sys.path` (usa imports nativos)
- Interface amigável com feedback em tempo real

### 🧠 Core Layer (`core/`)
**Responsabilidade**: Lógica de negócio central e orquestração

```
core/
├── alfredo_core.py         # Sistema central de gerenciamento
├── prompt_service.py       # Gerenciamento de prompts de IA
└── provider_factory.py     # Factory para provedores de IA
```

**Características**:
- Carregamento dinâmico de comandos
- Gerenciamento do ciclo de vida dos componentes
- Abstração dos provedores de IA

### 🔌 Integrations Layer (`integrations/`)
**Responsabilidade**: Integração com serviços externos

```
integrations/
├── ai_provider.py          # Interface abstrata para provedores
├── groq/
│   ├── provider.py         # Implementação Groq
│   └── monitor.py          # Monitoramento de rate limits
└── ollama/
    ├── provider.py         # Implementação Ollama
    └── client.py           # Cliente Ollama
```

**Características**:
- Pattern Strategy para diferentes provedores
- Configuração flexível por provedor
- Monitoramento de rate limits e quotas

### ⚙️ Config Layer (`config/`)
**Responsabilidade**: Configurações e internacionalização

```
config/
├── settings.py             # Configurações globais
├── paths.py                # Gerenciamento de caminhos
├── i18n.py                 # Sistema de internacionalização
└── locales/
    ├── pt/                 # Português
    └── en/                 # Inglês
```

**Características**:
- Configuração centralizada
- Suporte a variáveis de ambiente
- Sistema de i18n com fallback automático

### 🎬 Commands Layer (`commands/`)
**Responsabilidade**: Implementação de comandos específicos

```
commands/
├── clean_command.py        # Comando de limpeza
├── pc_info.py              # Informações do sistema
├── groq_status.py          # Status da API Groq
└── video/
    ├── audio_analyzer.py   # Análise de áudio
    ├── local_video.py      # Análise de vídeo local
    ├── youtube_ai.py       # YouTube + IA
    └── youtube_downloader.py # Download YouTube
```

**Características**:
- Comandos auto-registráveis
- Metadata declarativa (`COMMAND_INFO`)
- Isolamento de responsabilidades

### 🧪 Tests Layer (`tests/`)
**Responsabilidade**: Garantia de qualidade

```
tests/
├── unit/                   # Testes unitários
│   ├── test_core.py        # Testes do core
│   └── test_commands.py    # Testes de comandos
├── integration/            # Testes de integração
│   └── test_ai_providers.py # Testes de provedores
└── e2e/                    # Testes end-to-end
    └── test_video_workflow.py # Workflow completo
```

**Características**:
- Fixtures compartilhadas (`conftest.py`)
- Mocks para dependências externas
- Testes de performance e stress

## 🔄 Fluxo de Dados

### 1. **Comando CLI → Core**
```
Usuário → CLI Command → Core System → Provider Factory → AI Provider
```

### 2. **Processamento de Vídeo**
```
Input → Pre-processing → Frame Extraction → AI Analysis → Post-processing → Output
```

### 3. **Gerenciamento de Cache**
```
Request → Cache Check → Processing (if miss) → Cache Store → Response
```

## 🚀 Patterns Utilizados

### 1. **Command Pattern**
- Encapsula comandos como objetos
- Permite undo/redo futuro
- Facilita logging e auditoria

### 2. **Strategy Pattern**
- Diferentes algoritmos de análise
- Provedores de IA intercambiáveis
- Configuração runtime

### 3. **Factory Pattern**
- Criação de provedores de IA
- Instanciação de comandos
- Configuração baseada em contexto

### 4. **Observer Pattern**
- Sistema de eventos
- Notificações de progresso
- Logging distribuído

## 📦 Dependências e Instalação

### **Instalação via PyProject.toml**
```bash
pip install -e .
```

### **Entry Points Configurados**
```toml
[project.scripts]
alfredo = "cli.alfredo:main"
alfredo-groq-status = "cli.groq_status:main"
alfredo-clean = "cli.clean:main"
```

### **Principais Dependências**
- **Processamento**: `scenedetect`, `opencv-python`, `pillow`
- **IA**: `openai-whisper`, `requests`
- **Utilitários**: `tqdm`, `psutil`, `yt-dlp`
- **Testes**: `pytest`, `pytest-asyncio`

## 🔍 Debugging e Monitoramento

### **Logs Estruturados**
- Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR)
- Contexto preservado entre componentes
- Rotação automática de logs

### **Métricas**
- Tempo de processamento por comando
- Taxa de sucesso/falha
- Uso de recursos (CPU, memória, disk)

### **Health Checks**
- Status dos provedores de IA
- Conectividade com serviços externos
- Integridade do cache

## 🔮 Roadmap de Arquitetura

### **Versão 2.0**
- [ ] API REST para integração web
- [ ] Sistema de plugins dinâmicos
- [ ] Cache distribuído (Redis)
- [ ] Processamento paralelo avançado

### **Versão 3.0**
- [ ] Microservices com Docker
- [ ] Message Queue (RabbitMQ/Kafka)
- [ ] Observabilidade completa (Prometheus/Grafana)
- [ ] Multi-tenancy

## 📚 Referências

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Python Packaging Guide](https://packaging.python.org/)
- [Design Patterns](https://refactoring.guru/design-patterns)

---

**Mantido por**: Alfredo AI Team  
**Última atualização**: Julho 2025
