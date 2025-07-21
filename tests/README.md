# Testes do Alfredo AI

Este diretório contém todos os testes do projeto Alfredo AI, organizados seguindo a Clean Architecture.

## Estrutura Organizada por Camadas

### Testes Unitários (`unit/`)

Testes isolados para cada componente, organizados por camada:

- `unit/domain/` - Testes para entidades, validadores e exceções
  - `entities/` - Testes para entidades de domínio (Video, etc.)
  - `validators/` - Testes para validadores de domínio
  - `exceptions/` - Testes para exceções customizadas
- `unit/application/` - Testes para casos de uso e gateways
  - `use_cases/` - Testes para casos de uso isolados
  - `gateways/` - Testes para interfaces de gateway
- `unit/infrastructure/` - Testes para implementações de infraestrutura
  - `providers/` - Testes para provedores de IA
  - `downloaders/` - Testes para downloaders
  - `extractors/` - Testes para extractors de áudio
  - `storage/` - Testes para storage
  - `repositories/` - Testes para repositórios
  - `factories/` - Testes para factories
- `unit/config/` - Testes para configurações
- `unit/presentation/` - Testes para camada de apresentação
  - `cli/` - Testes para interface CLI

### Testes de Integração (`integration/`)

Testes que verificam integração entre componentes:

- `integration/use_cases/` - Testes de casos de uso com dependências reais
- `integration/gateways/` - Testes de contratos de gateways
- `integration/end_to_end/` - Testes de fluxos completos controlados

### Testes End-to-End (`e2e/`)

Testes de fluxos completos do usuário:

- `e2e/youtube_flow/` - Testes completos do fluxo YouTube
- `e2e/local_video_flow/` - Testes completos do fluxo de vídeo local
- `e2e/error_scenarios/` - Testes de cenários de erro

### Outros Tipos de Teste

- `bdd/` - Testes BDD (Behavior-Driven Development)
- `performance/` - Testes de performance e benchmarks
- `security/` - Testes de segurança e validação de entrada

### Fixtures e Utilitários

- `fixtures/` - Fixtures reutilizáveis e dados de teste
  - `base_fixtures.py` - Fixtures base para todos os testes
  - `mock_dependencies.py` - Mocks para dependências externas
  - `test_config.py` - Configurações específicas para testes
- `shared/` - Utilitários compartilhados entre testes
  - `test_utils.py` - Helpers e utilitários para testes

## Executando os Testes

### Comandos Básicos

```bash
# Todos os testes
pytest

# Testes por tipo
pytest tests/unit/           # Testes unitários
pytest tests/integration/    # Testes de integração
pytest tests/e2e/           # Testes end-to-end

# Testes por camada
pytest tests/unit/domain/           # Testes de domínio
pytest tests/unit/application/      # Testes de aplicação
pytest tests/unit/infrastructure/   # Testes de infraestrutura

# Com cobertura
pytest --cov=src --cov-report=html
pytest --cov=src --cov-report=term-missing
```

### Comandos por Marker

```bash
pytest -m unit          # Apenas testes unitários
pytest -m integration   # Apenas testes de integração
pytest -m e2e          # Apenas testes end-to-end
pytest -m performance  # Apenas testes de performance
pytest -m security     # Apenas testes de segurança
pytest -m slow         # Apenas testes lentos
```

### Comandos Avançados

```bash
# Executar em paralelo (se pytest-xdist instalado)
pytest -n auto

# Executar com timeout
pytest --timeout=300

# Executar apenas testes que falharam na última execução
pytest --lf

# Executar com verbose
pytest -v

# Executar com debug
pytest -s --pdb
```

## Configuração de Testes

### Configuração Principal

- `conftest.py` - Configuração global e fixtures principais
- `pytest.ini` - Configuração do pytest
- `pyproject.toml` - Configuração de cobertura e ferramentas

### Fixtures Disponíveis

#### Fixtures Base

- `temp_dir` - Diretório temporário para testes
- `mock_config` - Configuração mock
- `sample_video` - Vídeo de exemplo
- `sample_youtube_video` - Vídeo do YouTube de exemplo

#### Mocks de Dependências

- `mock_video_downloader` - Mock para downloader
- `mock_audio_extractor` - Mock para extractor
- `mock_ai_provider` - Mock para provedor de IA
- `mock_storage` - Mock para storage
- `mock_infrastructure_factory` - Factory mock completa

#### Configurações de Teste

- `unit_test_config` - Configuração para testes unitários
- `integration_test_config` - Configuração para testes de integração
- `e2e_test_config` - Configuração para testes E2E

## Boas Práticas

### Organização de Testes

1. **Espelhar estrutura do código**: Testes devem seguir a mesma estrutura do código fonte
2. **Um arquivo de teste por módulo**: `test_video.py` para `video.py`
3. **Classes de teste por funcionalidade**: Agrupar testes relacionados
4. **Nomes descritivos**: `test_create_video_with_valid_data`

### Escrita de Testes

1. **Arrange-Act-Assert**: Organizar testes em três seções claras
2. **Testes isolados**: Cada teste deve ser independente
3. **Mocks apropriados**: Usar mocks para dependências externas
4. **Assertions específicas**: Verificar comportamentos específicos

### Performance

1. **Testes rápidos**: Testes unitários devem ser muito rápidos (< 1s)
2. **Fixtures reutilizáveis**: Evitar duplicação de setup
3. **Cleanup automático**: Limpar recursos após testes
4. **Paralelização**: Usar pytest-xdist para testes paralelos

## Métricas de Qualidade

### Cobertura de Código

- **Meta**: >= 80% de cobertura geral
- **Domínio**: >= 95% de cobertura (lógica crítica)
- **Aplicação**: >= 90% de cobertura (casos de uso)
- **Infraestrutura**: >= 70% de cobertura (integrações)

### Tipos de Teste

- **70% Unitários**: Testes rápidos e isolados
- **20% Integração**: Testes de contratos e fluxos
- **10% E2E**: Testes de fluxos completos

### Qualidade

- **Zero falhas**: Todos os testes devem passar
- **Zero warnings**: Resolver todos os warnings
- **Tempo limite**: Suite completa < 5 minutos
- **Estabilidade**: Testes não devem ser flaky

## Ferramentas e Dependências

### Principais Dependências

- `pytest` - Framework de testes
- `pytest-asyncio` - Suporte a testes assíncronos
- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocking
- `pytest-bdd` - Testes BDD

### Ferramentas de Qualidade

- `black` - Formatação de código
- `flake8` - Análise estática
- `mypy` - Verificação de tipos
- `bandit` - Análise de segurança

## Contribuindo

Ao adicionar novos testes:

1. Siga a estrutura de diretórios existente
2. Use fixtures apropriadas
3. Adicione marcadores relevantes
4. Mantenha testes isolados e rápidos
5. Documente cenários complexos
6. Valide tanto casos positivos quanto negativos
7. Mantenha cobertura >= 80%
8. Execute todos os testes antes de commit