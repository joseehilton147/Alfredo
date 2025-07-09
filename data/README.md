# 📁 Estrutura de Dados - Alfredo AI

Esta pasta contém toda a estrutura de dados do sistema, organizada seguindo padrões enterprise.

## 📂 Estrutura

```
data/
├── input/           # 📥 Dados de entrada
│   ├── local/       # 🎬 Vídeos locais para processamento
│   └── youtube/     # 📹 Vídeos baixados do YouTube
├── output/          # 📤 Dados de saída
│   └── summaries/   # 📄 Resumos gerados
│       ├── local/   # 📝 Resumos de vídeos locais
│       └── youtube/ # 📝 Resumos de vídeos do YouTube
└── cache/           # 🗂️ Dados temporários
    ├── frames/      # 🖼️ Frames extraídos (temporário)
    └── downloads/   # ⬇️ Downloads em progresso
```

## 🔄 Fluxo de Dados

1. **Input**: Vídeos são colocados em `input/local/` ou baixados para `input/youtube/`
2. **Processing**: Frames são extraídos para `cache/frames/`
3. **Output**: Resumos são salvos em `output/summaries/`
4. **Cleanup**: Cache pode ser limpo periodicamente

## 🧹 Gestão de Cache

- `cache/frames/`: Limpo automaticamente após processamento
- `cache/downloads/`: Limpo conforme necessário
- Use `Alfredo limpar` para gestão avançada

## 📋 Convenções

- **Vídeos locais**: Coloque em `input/local/`
- **Resumos**: Gerados automaticamente em `output/summaries/`
- **Nomes**: Mantêm nome original do vídeo (sem extensão para resumos)
