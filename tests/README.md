# 🧪 Testes - Alfredo AI

Estrutura de testes organizada por categoria e tipo.

## 📂 Estrutura

```
tests/
├── fixtures/        # 📦 Dados para testes
│   └── videos/      # 🎬 Vídeos de amostra
├── unit/           # 🔬 Testes unitários
└── integration/    # 🔗 Testes de integração
```

## 🎬 Vídeos de Teste

### Local
- Coloque vídeos de teste em `fixtures/videos/`
- Nome recomendado: `video-sample.mp4`
- Formatos suportados: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

### YouTube
- **Download**: `https://www.youtube.com/watch?v=oUPaJxk6TZ0`
- **IA + Transcrição**: `https://www.youtube.com/watch?v=Tn6-PIqc4UM`

## 🔬 Tipos de Teste

### Unit (Unitários)
- Testes de funções individuais
- Mocks e stubs
- Execução rápida

### Integration (Integração)
- Testes de fluxos completos
- Dependências reais (Ollama, yt-dlp)
- Validação end-to-end

## ▶️ Execução

```bash
# Todos os testes
Alfredo testes

# Testes específicos (futuro)
python -m pytest tests/unit/
python -m pytest tests/integration/
```
