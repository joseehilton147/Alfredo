# Contribuindo para o Alfredo AI 🤝

Obrigado por seu interesse em contribuir para o Alfredo AI! Este documento fornece diretrizes e instruções para contribuidores.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Reportando Bugs](#reportando-bugs)
- [Solicitando Features](#solicitando-features)
- [Enviando Pull Requests](#enviando-pull-requests)
- [Padrões de Código](#padrões-de-código)
- [Configuração do Ambiente de Desenvolvimento](#configuração-do-ambiente-de-desenvolvimento)
- [Testes](#testes)
- [Documentação](#documentação)

## 📜 Código de Conduta

### Nosso Compromisso
Nos comprometemos a criar um ambiente acolhedor e inclusivo para todos os contribuidores, independentemente de idade, tamanho corporal, deficiência, etnia, identidade e expressão de gênero, nível de experiência, nacionalidade, aparência pessoal, raça, religião ou identidade e orientação sexual.

### Nossos Padrões
- Use linguagem acolhedora e inclusiva
- Seja respeitoso com diferentes pontos de vista e experiências
- Aceite críticas construtivas com graça
- Foque no que é melhor para a comunidade

## 🚀 Como Contribuir

### Primeiros Passos
1. Fork o repositório
2. Clone seu fork localmente
3. Crie uma branch para sua contribuição
4. Faça suas alterações
5. Teste suas alterações
6. Envie um Pull Request

### Tipos de Contribuição
- 🐛 **Bug fixes**: Correções de bugs
- ✨ **Features**: Novas funcionalidades
- 📚 **Documentação**: Melhorias na documentação
- 🧪 **Testes**: Adição ou melhoria de testes
- 🔧 **Refatoração**: Melhorias de código sem mudança de funcionalidade
- ⚡ **Performance**: Otimizações de performance

## 🐛 Reportando Bugs

### Antes de Reportar
1. Verifique se o bug já foi reportado nos [issues](https://github.com/joseehilton147/alfredo-ai/issues)
2. Teste com a versão mais recente do código

### Como Reportar
Use o template de bug report:
```markdown
**Descrição do Bug**
Uma descrição clara e concisa do bug.

**Para Reproduzir**
Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '....'
3. Role até '....'
4. Veja o erro

**Comportamento Esperado**
Uma descrição clara do que você esperava que acontecesse.

**Screenshots**
Se aplicável, adicione screenshots para ajudar a explicar o problema.

**Ambiente:**
 - OS: [e.g. iOS]
 - Python: [e.g. 3.8]
 - Versão do Alfredo AI: [e.g. 1.0.0]

**Contexto Adicional**
Adicione qualquer outro contexto sobre o problema aqui.
```

## 💡 Solicitando Features

### Antes de Solicitar
1. Verifique se a feature já foi solicitada nos [issues](https://github.com/joseehilton147/alfredo-ai/issues)
2. Considere se a feature se alinha com os objetivos do projeto

### Como Solicitar
Use o template de feature request:
```markdown
**Sua Feature Request está relacionada a um problema?**
Uma descrição clara e concisa do problema. Ex. Sempre fico frustrado quando [...]

**Descreva a solução que você gostaria**
Uma descrição clara e concisa do que você quer que aconteça.

**Descreva alternativas que você considerou**
Uma descrição clara e concisa de quaisquer soluções ou features alternativas que você considerou.

**Contexto Adicional**
Adicione qualquer outro contexto ou screenshots sobre a feature request aqui.
```

## 🔀 Enviando Pull Requests

### Processo
1. **Fork e Clone**
   ```bash
   git clone https://github.com/seu-usuario/alfredo-ai.git
   cd alfredo-ai
   ```

2. **Crie uma Branch**
   ```bash
   git checkout -b feature/nova-funcionalidade
   # ou
   git checkout -b fix/correcao-bug
   ```

3. **Faça suas Alterações**
   - Siga os padrões de código
   - Adicione testes para novas funcionalidades
   - Atualize documentação conforme necessário

4. **Teste suas Alterações**
   ```bash
   make test
   make lint
   make type-check
   ```

5. **Commit suas Alterações**
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade"
   ```

6. **Push e Pull Request**
   ```bash
   git push origin feature/nova-funcionalidade
   ```

### Padrões de Commit
Usamos [Conventional Commits](https://www.conventionalcommits.org/):
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Mudanças de formatação
- `refactor`: Refatoração de código
- `test`: Adição ou modificação de testes
- `chore`: Tarefas de manutenção

Exemplos:
```
feat: adiciona suporte para vídeos 4K
fix: corrige erro de transcrição em vídeos longos
docs: atualiza README com novos exemplos
```

## 📝 Padrões de Código

### Estilo de Código
- **Python**: Seguimos PEP 8 com algumas adaptações
- **Black**: Formatação automática com linha de 88 caracteres
- **isort**: Ordenação de imports
- **mypy**: Type checking estático

### Estrutura de Diretórios
```
src/
├── application/     # Casos de uso e lógica de aplicação
├── domain/         # Entidades e regras de negócio
└── infrastructure/ # Implementações concretas
```

### Convenções de Nomenclatura
- **Classes**: PascalCase (ex: `VideoProcessor`)
- **Funções/Métodos**: snake_case (ex: `process_video`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_FILE_SIZE`)
- **Variáveis**: snake_case (ex: `video_path`)

### Docstrings
Use Google style docstrings:
```python
def process_video(video_path: str, language: str = "pt") -> dict:
    """Processa um vídeo e retorna transcrição e resumo.
    
    Args:
        video_path: Caminho para o arquivo de vídeo
        language: Idioma do vídeo (padrão: pt)
        
    Returns:
        dict: Contendo transcrição, resumo e metadados
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
        ValueError: Se o formato não for suportado
    """
```

## ⚙️ Configuração do Ambiente de Desenvolvimento

### Instalação Rápida
```bash
# Clone e configure
git clone https://github.com/joseehilton147/alfredo-ai.git
cd alfredo-ai

# Configure ambiente
make setup-dev

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### Ferramentas de Desenvolvimento
```bash
# Instalar pre-commit hooks
pre-commit install

# Executar verificações
make lint
make test
make type-check
```

## 🧪 Testes

### Executando Testes
```bash
# Todos os testes
make test

# Com cobertura
make test-cov

# Testes específicos
pytest tests/test_video_entity.py -v
```

### Escrevendo Testes
- Use pytest para testes
- Nomeie testes com prefixo `test_`
- Use fixtures para setup complexo
- Mock dependências externas

Exemplo:
```python
def test_video_transcription():
    """Testa transcrição de vídeo."""
    video_path = "tests/fixtures/sample.mp4"
    result = process_video(video_path)
    assert "transcription" in result
    assert len(result["transcription"]) > 0
```

## 📚 Documentação

### Onde Documentar
- **Código**: Docstrings em todas as funções públicas
- **README.md**: Visão geral e instruções rápidas
- **INSTALL.md**: Instruções detalhadas de instalação
- **docs/**: Documentação técnica detalhada

### Padrões de Documentação
- Use Markdown para documentação
- Inclua exemplos de uso
- Mantenha documentação atualizada
- Use screenshots quando apro
