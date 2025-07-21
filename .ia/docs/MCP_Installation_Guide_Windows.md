# Guia de Instalação MCP para Windows - Kiro IDE

Este guia fornece instruções detalhadas para instalar e configurar os servidores MCP (Model Context Protocol) no Windows, especificamente para Context7 e Playwright, evitando problemas comuns de dependências.

## Pré-requisitos

### 1. Node.js e npm
```powershell
# Verificar se Node.js está instalado
node --version
npm --version
```

Se não estiver instalado, baixe do [site oficial do Node.js](https://nodejs.org/).

### 2. Python e uv (para alguns MCPs)
```powershell
# Instalar uv (gerenciador de pacotes Python)
# Opção 1: Via pip
pip install uv

# Opção 2: Via PowerShell (recomendado)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Problemas Comuns e Soluções

### Problema: "Cannot find module 'inherits'"

Este é um problema comum com npx no Windows. Soluções:

```powershell
# 1. Limpar cache do npm
npm cache clean --force

# 2. Instalar dependência globalmente
npm install -g inherits

# 3. Limpar cache do npx (se necessário)
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\npm-cache\_npx" -ErrorAction SilentlyContinue
```

## Instalação dos MCPs

### 1. Context7 MCP

O Context7 fornece acesso a documentação de bibliotecas em tempo real.

#### Instalação:
```powershell
# Instalar globalmente para evitar problemas de cache
npm install -g @upstash/context7-mcp
```

#### Configuração no mcp.json:
```json
{
  "mcpServers": {
    "Context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": [
        "resolve-library-id",
        "get-library-docs"
      ]
    }
  }
}
```

#### Teste:
```powershell
# Verificar se funciona
npx -y @upstash/context7-mcp --help
```

### 2. Playwright MCP

O Playwright MCP permite automação de navegadores.

#### Instalação:
```powershell
# Instalar globalmente
npm install -g @playwright/mcp@latest

# Instalar navegadores do Playwright (necessário)
npx playwright install
```

#### Configuração no mcp.json:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp@latest"
      ],
      "disabled": false,
      "autoApprove": [
        "browser_navigate",
        "browser_wait_for",
        "browser_click",
        "browser_evaluate",
        "browser_resize",
        "browser_console_messages",
        "browser_press_key",
        "browser_snapshot"
      ]
    }
  }
}
```

#### Teste:
```powershell
# Verificar se funciona
npx -y @playwright/mcp@latest --help
```

### 3. Serper Search MCP

O Serper Search MCP fornece capacidades de busca no Google e scraping de páginas web.

#### Instalação:
```powershell
# Instalar globalmente
npm install -g serper-search-scrape-mcp-server
```

#### Configuração no mcp.json:
```json
{
  "mcpServers": {
    "serper-search": {
      "command": "npx",
      "args": [
        "-y",
        "serper-search-scrape-mcp-server"
      ],
      "env": {
        "SERPER_API_KEY": "sua_api_key_aqui"
      },
      "disabled": false,
      "autoApprove": [
        "google_search",
        "scrape"
      ]
    }
  }
}
```

#### Obtenção da API Key:
1. Acesse [serper.dev](https://serper.dev/)
2. Crie uma conta gratuita
3. Obtenha sua API key no dashboard
4. Substitua `"sua_api_key_aqui"` pela sua chave real

#### Teste:
```powershell
# Definir a variável de ambiente temporariamente para teste
$env:SERPER_API_KEY="sua_api_key_aqui"
npx -y serper-search-scrape-mcp-server --help
```

## Configuração Completa do MCP

### Localização do arquivo de configuração:
- **Usuário (global)**: `%USERPROFILE%\.kiro\settings\mcp.json`
- **Workspace (local)**: `.kiro\settings\mcp.json`

### Exemplo de configuração completa:

```json
{
  "mcpServers": {
    "Context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": [
        "resolve-library-id",
        "get-library-docs"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp@latest"
      ],
      "disabled": false,
      "autoApprove": [
        "browser_navigate",
        "browser_wait_for",
        "browser_click",
        "browser_evaluate",
        "browser_resize",
        "browser_console_messages",
        "browser_press_key",
        "browser_snapshot"
      ]
    },
    "serper-search": {
      "command": "npx",
      "args": [
        "-y",
        "serper-search-scrape-mcp-server"
      ],
      "env": {
        "SERPER_API_KEY": "sua_api_key_aqui"
      },
      "disabled": false,
      "autoApprove": [
        "google_search",
        "scrape"
      ]
    },
    "fetch": {
      "command": "uvx",
      "args": [
        "mcp-server-fetch"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": [
        "fetch"
      ]
    }
  }
}
```

## Script de Instalação Automatizada

Crie um arquivo `install-mcp.ps1`:

```powershell
# Script de instalação automatizada dos MCPs
Write-Host "Instalando MCPs para Kiro..." -ForegroundColor Green

# Limpar caches
Write-Host "Limpando caches..." -ForegroundColor Yellow
npm cache clean --force
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\npm-cache\_npx" -ErrorAction SilentlyContinue

# Instalar dependências globais
Write-Host "Instalando dependências..." -ForegroundColor Yellow
npm install -g inherits
npm install -g @upstash/context7-mcp
npm install -g @playwright/mcp@latest
npm install -g serper-search-scrape-mcp-server

# Instalar navegadores do Playwright
Write-Host "Instalando navegadores do Playwright..." -ForegroundColor Yellow
npx playwright install

# Verificar instalações
Write-Host "Verificando instalações..." -ForegroundColor Yellow
Write-Host "Context7:" -ForegroundColor Cyan
npx -y @upstash/context7-mcp --help | Select-Object -First 3

Write-Host "Playwright:" -ForegroundColor Cyan
npx -y @playwright/mcp@latest --help | Select-Object -First 3

Write-Host "Serper Search:" -ForegroundColor Cyan
Write-Host "Instalado com sucesso. Configure sua API key no mcp.json" -ForegroundColor Yellow

Write-Host "Instalação concluída!" -ForegroundColor Green
Write-Host "Reinicie o Kiro e reconecte os servidores MCP." -ForegroundColor Yellow
Write-Host "Não esqueça de configurar sua API key do Serper no arquivo mcp.json!" -ForegroundColor Red
```

Execute com:
```powershell
PowerShell -ExecutionPolicy Bypass -File install-mcp.ps1
```

## Solução de Problemas

### 1. Timeout de Conexão
Se o MCP server não conectar em 60 segundos:
- Verifique se as dependências estão instaladas
- Teste o comando manualmente no terminal
- Limpe os caches e reinstale

### 2. Módulos não encontrados
```powershell
# Reinstalar globalmente
npm uninstall -g @playwright/mcp @upstash/context7-mcp serper-search-scrape-mcp-server
npm install -g @playwright/mcp@latest @upstash/context7-mcp serper-search-scrape-mcp-server
```

### 3. Problemas de Permissão
Execute o PowerShell como Administrador se necessário.

## Verificação Final

Após a instalação:

1. **Abra o Kiro IDE**
2. **Vá para o painel MCP Server** (feature panel)
3. **Reconecte os servidores** ou use Command Palette > "MCP"
4. **Verifique se os servidores aparecem como conectados**

## Comandos de Teste

### Context7:
```javascript
// No Kiro, teste com:
// Resolver biblioteca: "react"
// Obter documentação de uma biblioteca
```

### Playwright:
```javascript
// No Kiro, teste com:
// Navegar para uma página
// Tirar screenshot
// Interagir com elementos
```

### Serper Search:
```javascript
// No Kiro, teste com:
// Buscar no Google: "Python clean architecture tutorial"
// Fazer scraping de uma página web
// Obter resultados de pesquisa estruturados
```

---

**Nota**: Este guia foi testado no Windows 11 com Node.js v22.17.0. Para outras versões, alguns comandos podem variar ligeiramente.