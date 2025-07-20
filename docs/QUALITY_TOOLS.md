# Ferramentas de Qualidade - Alfredo AI

Este documento detalha todas as ferramentas de qualidade e análise disponíveis no projeto Alfredo AI.

## Visão Geral

O Alfredo AI implementa um pipeline completo de qualidade com ferramentas automatizadas para:
- Análise de cobertura de testes
- Verificação de qualidade de código
- Detecção de regressão
- Relatórios detalhados
- Monitoramento contínuo

## Análise de Cobertura

### Comandos Principais

#### `make coverage-analysis`
Executa análise completa de cobertura com relatório detalhado.

```bash
make coverage-analysis
```

**Funcionalidades:**
- Executa todos os testes com cobertura
- Gera relatório detalhado por módulo
- Identifica módulos com baixa cobertura
- Fornece sugestões específicas de melhoria
- Salva relatório em `data/output/reports/coverage_detailed.txt`

**Exemplo de Saída:**
```
📊 RELATÓRIO DETALHADO DE COBERTURA DE TESTES
===============================================
Gerado em: 2024-01-15T10:30:00
Cobertura total: 85.2%
Linhas totais: 1,234
Linhas cobertas: 1,051
Linhas não cobertas: 183

✅ COBERTURA ADEQUADA - Meta atingida!

🔴 MÓDULOS COM BAIXA COBERTURA:
--------------------------------
  src.infrastructure.providers.ollama_provider
    Cobertura: 65.4%
    Linhas não cobertas: 23
    Linhas específicas: 45, 67, 89, 123, 145

💡 SUGESTÕES DE MELHORIA:
------------------------
1. Priorize testes para módulos com cobertura < 80%
2. Foque em reduzir linhas não cobertas (atual: 183)
3. Considere implementar testes de integração
4. Adicione testes de edge cases e tratamento de erros
```

#### `make coverage-analysis-quick`
Análise rápida usando dados de cobertura existentes.

```bash
make coverage-analysis-quick
```

**Características:**
- Não executa testes novamente
- Usa arquivo `coverage.json` existente
- Ideal para verificações rápidas durante desenvolvimento
- Gera relatório em `data/output/reports/coverage_quick.txt`

#### `make coverage-regression`
Verificação automática de regressão de cobertura.

```bash
make coverage-regression
```

**Funcionalidades:**
- Compara cobertura atual com baseline
- Detecta diminuição na cobertura (tolerância: 1%)
- Atualiza baseline automaticamente se melhorou
- Mantém histórico em `data/output/reports/coverage_baseline.json`

**Exemplo de Detecção de Regressão:**
```
❌ REGRESSÃO DETECTADA!
   Baseline: 85.2%
   Atual: 82.1%
   Diferença: -3.1%
```

### Script de Análise Detalhada

O script `scripts/coverage_analysis.py` oferece funcionalidades avançadas:

```bash
# Análise com cobertura mínima personalizada
python scripts/coverage_analysis.py --min-coverage 85

# Análise sem executar testes
python scripts/coverage_analysis.py --no-run

# Verificação de regressão com baseline customizado
python scripts/coverage_analysis.py --baseline custom_baseline.json

# Saída personalizada
python scripts/coverage_analysis.py --output custom_report.txt
```

**Parâmetros Disponíveis:**
- `--min-coverage`: Cobertura mínima esperada (padrão: 80%)
- `--output`: Arquivo de saída do relatório
- `--baseline`: Arquivo de baseline para regressão
- `--no-run`: Não executar testes, usar dados existentes

## Pipeline de Qualidade

### Verificação Completa

#### `make quality-check`
Executa todas as verificações de qualidade em sequência.

```bash
make quality-check
```

**Verificações Incluídas:**
1. **Formatação de Código** (black, isort)
2. **Análise Estática** (flake8, pylint)
3. **Verificação de Tipos** (mypy)
4. **Análise de Complexidade**
5. **Detecção de Duplicação**
6. **Análise de Segurança** (bandit, safety)
7. **Cobertura de Testes**

#### `make quality-report`
Gera relatório abrangente de qualidade.

```bash
make quality-report
```

**Características:**
- Executa todas as verificações
- Gera relatório consolidado com timestamp
- Salva em `data/output/reports/quality_report_YYYYMMDD_HHMMSS.txt`
- Inclui métricas detalhadas de cada ferramenta

#### `make quality-check-parallel`
Execução paralela para CI/CD (mais rápida).

```bash
make quality-check-parallel
```

**Otimizações:**
- Executa verificações em paralelo quando possível
- Versões "silent" para saída limpa
- Ideal para pipelines de CI/CD
- Falha rápida em caso de problemas

### Verificações Individuais

#### Formatação de Código
```bash
make format-check        # Verificar formatação
make format              # Aplicar formatação
```

#### Análise Estática
```bash
make lint                # Linting básico
make lint-full           # Linting abrangente com múltiplas ferramentas
```

#### Complexidade
```bash
make complexity          # Análise de complexidade ciclomática
make metrics             # Métricas detalhadas de código
```

#### Duplicação
```bash
make duplication         # Detecção de código duplicado
```

#### Segurança
```bash
make security            # Análise básica de segurança
make security-full       # Análise completa com relatórios
```

## Estrutura de Relatórios

### Diretórios de Saída

```
data/output/
├── coverage/                    # Relatórios HTML de cobertura
│   ├── index.html              # Dashboard principal
│   └── htmlcov/                # Arquivos detalhados
├── reports/                    # Relatórios de texto
│   ├── coverage_detailed.txt   # Análise detalhada
│   ├── coverage_quick.txt      # Análise rápida
│   ├── coverage_baseline.json  # Baseline para regressão
│   └── quality_report_*.txt    # Relatórios de qualidade
├── metrics/                    # Métricas de código
│   ├── complexity.json         # Complexidade ciclomática
│   ├── maintainability.json    # Índice de manutenibilidade
│   └── raw_metrics.json        # Métricas brutas
└── security/                   # Relatórios de segurança
    ├── bandit_report.json      # Análise Bandit
    └── safety_report.json      # Vulnerabilidades
```

### Formatos de Relatório

#### Relatório de Cobertura Detalhado
- **Formato**: Texto estruturado
- **Conteúdo**: Métricas por módulo, sugestões, linhas específicas
- **Localização**: `data/output/reports/coverage_detailed.txt`

#### Relatório HTML de Cobertura
- **Formato**: HTML interativo
- **Conteúdo**: Dashboard visual, navegação por arquivos
- **Localização**: `data/output/coverage/index.html`

#### Baseline de Regressão
- **Formato**: JSON
- **Conteúdo**: Cobertura histórica, timestamps
- **Localização**: `data/output/reports/coverage_baseline.json`

## Integração com CI/CD

### Pipeline Básico

```yaml
# .github/workflows/quality.yml
name: Quality Check
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: make install-dev
      
      - name: Quality Gate
        run: make quality-gate
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: data/output/coverage.xml
```

### Comandos para CI/CD

```bash
make ci-quality         # Pipeline completo para CI
make quality-gate       # Gate rigoroso para deployment
make quality-dashboard  # Dashboard local para desenvolvimento
```

## Configuração e Personalização

### Limites de Qualidade

Os limites podem ser configurados nos arquivos:

- **Cobertura**: `scripts/coverage_analysis.py` (padrão: 80%)
- **Complexidade**: `.flake8` (máximo: 10)
- **Duplicação**: `scripts/duplication_check.py` (máximo: 3%)

### Exclusões

Arquivos e diretórios podem ser excluídos via:

- **Coverage**: `.coveragerc`
- **Linting**: `.flake8`, `pyproject.toml`
- **Security**: `bandit.yml`

### Exemplo de Configuração

```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Monitoramento Contínuo

### Modo Watch

```bash
make quality-watch      # Monitoramento contínuo
```

Executa verificações a cada 60 segundos, ideal para desenvolvimento ativo.

### Dashboard Local

```bash
make quality-dashboard  # Abre dashboard local
```

Inicia servidor HTTP local com relatórios de cobertura em `http://localhost:8080`.

## Troubleshooting

### Problemas Comuns

#### Coverage.json não encontrado
```bash
# Solução: Execute testes primeiro
make test-coverage
make coverage-analysis-quick
```

#### Baseline não existe
```bash
# Solução: Crie baseline inicial
make coverage-regression  # Cria baseline automaticamente
```

#### Dependências faltando
```bash
# Solução: Instale dependências de desenvolvimento
make install-dev
```

### Logs e Debug

Para debug detalhado:

```bash
# Executar com verbose
python scripts/coverage_analysis.py --verbose

# Verificar logs de qualidade
cat data/output/reports/quality_report_*.txt
```

## Melhores Práticas

### Durante Desenvolvimento

1. **Execute verificações localmente**:
   ```bash
   make quality-check
   ```

2. **Monitore cobertura continuamente**:
   ```bash
   make coverage-analysis-quick
   ```

3. **Verifique regressão antes de commit**:
   ```bash
   make coverage-regression
   ```

### Para CI/CD

1. **Use pipeline paralelo**:
   ```bash
   make quality-check-parallel
   ```

2. **Configure quality gate**:
   ```bash
   make quality-gate
   ```

3. **Mantenha artefatos**:
   - Salve relatórios como artefatos
   - Configure notificações para regressão

### Para Equipes

1. **Estabeleça limites claros**:
   - Cobertura mínima: 80%
   - Complexidade máxima: 10
   - Zero duplicação crítica

2. **Revise relatórios regularmente**:
   - Análise semanal de qualidade
   - Identificação de tendências
   - Planos de melhoria

3. **Automatize verificações**:
   - Pre-commit hooks
   - CI/CD obrigatório
   - Notificações automáticas

Este sistema de qualidade garante que o Alfredo AI mantenha altos padrões de código e cobertura de testes, facilitando manutenção e evolução contínua do projeto.