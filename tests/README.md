# Testes do Alfredo AI

Este diretório contém a suíte completa de testes para o projeto Alfredo AI, implementando uma estratégia abrangente de testes BDD/TDD.

## Estrutura de Testes

### 📁 tests/bdd/
Testes comportamentais (Behavior-Driven Development) usando pytest-bdd:
- **features/**: Arquivos .feature em formato Gherkin
- **step_defs/**: Definições de steps para os cenários BDD
- **conftest.py**: Configurações e fixtures específicas para BDD

#### Cenários Implementados:
- `youtube_processing.feature`: Processamento de vídeos do YouTube
- `domain_validation.feature`: Validação de entidades de domínio

### 📁 tests/unit/
Testes unitários organizados por camada da arquitetura:
- **domain/**: Testes para entidades, validadores e exceções
- **application/**: Testes para use cases e interfaces
- **config/**: Testes para configurações
- **infrastructure/**: Testes para factories e implementações

### 📁 tests/integration/
Testes de integração end-to-end:
- Fluxos completos de processamento
- Integração entre camadas
- Testes de resiliência de rede
- Processamento concorrente

### 📁 tests/performance/
Testes de performance e benchmarks:
- Validação de performance
- Testes de concorrência
- Monitoramento de memória
- Benchmarks de escalabilidade

### 📁 tests/security/
Testes de segurança básicos:
- Validação de inputs maliciosos
- Proteção contra SQL injection, XSS, path traversal
- Segurança de URLs e sistema de arquivos
- Proteção de dados sensíveis em logs

## Executando os Testes

### Todos os Testes
```bash
python -m pytest
```

### Por Categoria
```bash
# Testes unitários
python -m pytest tests/unit/ -v

# Testes BDD
python -m pytest tests/bdd/ -v

# Testes de integração
python -m pytest tests/integration/ -v -m integration

# Testes de performance
python -m pytest tests/performance/ -v -m performance

# Testes de segurança
python -m pytest tests/security/ -v -m security
```

### Com Cobertura
```bash
python -m pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Marcadores (Markers)

Os testes são organizados com marcadores para execução seletiva:
- `@pytest.mark.bdd`: Testes BDD
- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.performance`: Testes de performance
- `@pytest.mark.security`: Testes de segurança

## Fixtures Principais

### BDD Fixtures
- `mock_config`: Configuração mock para testes
- `mock_infrastructure_factory`: Factory mock completa
- `bdd_context`: Contexto compartilhado entre steps
- `sample_video_data`: Dados de exemplo para testes

### Performance Fixtures
- `performance_config`: Configuração otimizada para performance
- `PerformanceTimer`: Medição de tempo de execução
- `MemoryProfiler`: Monitoramento de uso de memória

### Security Fixtures
- Configurações temporárias isoladas
- Mocks para componentes externos
- Captura de logs para análise de segurança

## Estratégia de Testes

### 1. Test-Driven Development (TDD)
- Testes escritos antes da implementação
- Ciclo Red-Green-Refactor
- Cobertura mínima de 80%

### 2. Behavior-Driven Development (BDD)
- Cenários em linguagem natural (Gherkin)
- Testes como documentação viva
- Validação de comportamento end-to-end

### 3. Testes de Integração
- Validação de fluxos completos
- Integração entre camadas
- Testes de resiliência

### 4. Testes de Performance
- Benchmarks de operações críticas
- Monitoramento de recursos
- Testes de escalabilidade

### 5. Testes de Segurança
- Validação contra ataques comuns
- Proteção de dados sensíveis
- Sanitização de inputs

## Configuração do pytest

O arquivo `pytest.ini` contém as configurações:
- Diretórios de teste
- Marcadores personalizados
- Configurações de cobertura
- Configurações BDD

## Dependências de Teste

Principais dependências para execução dos testes:
- `pytest`: Framework de testes
- `pytest-asyncio`: Suporte a testes assíncronos
- `pytest-cov`: Cobertura de código
- `pytest-mock`: Mocking
- `pytest-bdd`: Testes BDD
- `psutil`: Monitoramento de sistema (performance)

## Relatórios

### Cobertura de Código
- Relatório HTML: `htmlcov/index.html`
- Relatório terminal: Exibido após execução com `--cov`

### Relatórios BDD
- Cenários executados e resultados
- Steps com falha detalhados

### Benchmarks de Performance
- Tempos de execução por operação
- Uso de memória e recursos
- Comparações de performance

## Melhores Práticas

1. **Isolamento**: Cada teste é independente
2. **Mocking**: Dependências externas são mockadas
3. **Fixtures**: Reutilização de configurações comuns
4. **Marcadores**: Organização por categoria
5. **Documentação**: Testes servem como documentação
6. **Performance**: Testes executam rapidamente
7. **Segurança**: Validação de inputs maliciosos
8. **Cobertura**: Meta de 80% de cobertura mínima

## Contribuindo

Ao adicionar novos testes:
1. Siga a estrutura de diretórios existente
2. Use fixtures apropriadas
3. Adicione marcadores relevantes
4. Mantenha testes isolados e rápidos
5. Documente cenários complexos
6. Valide tanto casos positivos quanto negativos