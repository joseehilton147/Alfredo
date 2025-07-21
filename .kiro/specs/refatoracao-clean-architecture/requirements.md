# Requirements Document

## Introduction

Esta especificação define os requisitos para a refatoração arquitetural completa do projeto Alfredo AI, transformando-o de uma implementação parcialmente conforme com Clean Architecture para uma implementação que atende 100% das diretrizes mandatórias definidas no steering. O objetivo é criar um sistema robusto, manutenível e escalável que sirva como referência de excelência em Clean Architecture para projetos Python.

A refatoração aborda lacunas críticas identificadas na análise arquitetural, incluindo hierarquia de exceções customizadas, factory pattern com injeção de dependência, gateways de infraestrutura, configuração tipada centralizada, validação de domínio robusta e cobertura de testes BDD/TDD.

## Requirements

### Requirement 1: Sistema de Exceções Customizadas

**User Story:** Como desenvolvedor do sistema, quero um sistema robusto de tratamento de erros com exceções específicas, para que eu possa identificar e tratar diferentes tipos de falhas de forma precisa e informativa.

#### Acceptance Criteria

1. WHEN o sistema encontra qualquer tipo de erro THEN SHALL lançar uma exceção específica derivada de AlfredoError
2. WHEN uma exceção é lançada THEN SHALL incluir mensagem descritiva e detalhes opcionais em formato dict
3. WHEN o código captura exceções THEN SHALL capturar tipos específicos, não Exception genérica
4. WHEN ProviderUnavailableError é lançada THEN SHALL indicar qual provedor de IA está indisponível
5. WHEN DownloadFailedError é lançada THEN SHALL incluir URL e motivo da falha
6. WHEN TranscriptionError é lançada THEN SHALL incluir caminho do arquivo e detalhes do erro
7. WHEN InvalidVideoFormatError é lançada THEN SHALL especificar qual validação falhou
8. WHEN ConfigurationError é lançada THEN SHALL indicar qual configuração está inválida

### Requirement 2: Factory Pattern e Injeção de Dependência

**User Story:** Como desenvolvedor do sistema, quero um sistema centralizado de criação de dependências com injeção automática, para que eu possa facilmente testar, substituir e gerenciar implementações de infraestrutura.

#### Acceptance Criteria

1. WHEN um Use Case é instanciado THEN SHALL receber todas as dependências via construtor
2. WHEN InfrastructureFactory é chamada THEN SHALL retornar implementações concretas das interfaces
3. WHEN um teste é executado THEN SHALL poder usar mocks das interfaces sem modificar Use Cases
4. WHEN create_video_downloader() é chamado THEN SHALL retornar implementação de VideoDownloaderGateway
5. WHEN create_audio_extractor() é chamado THEN SHALL retornar implementação de AudioExtractorGateway
6. WHEN create_ai_provider() é chamado com tipo específico THEN SHALL retornar provider correspondente
7. WHEN create_storage() é chamado THEN SHALL retornar implementação de StorageGateway
8. WHEN provider_type inválido é fornecido THEN SHALL lançar ConfigurationError

### Requirement 3: Gateways de Infraestrutura

**User Story:** Como arquiteto do sistema, quero interfaces abstratas para todas as dependências externas, para que o sistema siga rigorosamente os princípios de Clean Architecture e seja facilmente extensível.

#### Acceptance Criteria

1. WHEN VideoDownloaderGateway é definida THEN SHALL ter métodos download() e extract_info()
2. WHEN AudioExtractorGateway é definida THEN SHALL ter método extract_audio()
3. WHEN StorageGateway é definida THEN SHALL ter métodos save_video(), load_video() e save_transcription()
4. WHEN Use Cases são implementados THEN SHALL depender apenas das interfaces de gateway
5. WHEN implementações concretas são criadas THEN SHALL estar isoladas na camada de infraestrutura
6. WHEN YTDLPDownloader é implementado THEN SHALL implementar VideoDownloaderGateway
7. WHEN FFmpegExtractor é implementado THEN SHALL implementar AudioExtractorGateway
8. WHEN FileSystemStorage é implementado THEN SHALL implementar StorageGateway

### Requirement 4: Configuração Tipada Centralizada

**User Story:** Como desenvolvedor do sistema, quero todas as configurações centralizadas em uma classe tipada com validação automática, para que eu possa evitar magic strings/numbers e garantir configurações válidas.

#### Acceptance Criteria

1. WHEN AlfredoConfig é instanciada THEN SHALL validar todas as configurações obrigatórias
2. WHEN configuração inválida é fornecida THEN SHALL lançar ConfigurationError específica
3. WHEN validate() é chamado THEN SHALL verificar se GROQ_API_KEY está presente
4. WHEN create_directories() é chamado THEN SHALL criar toda a estrutura de diretórios necessária
5. WHEN max_video_duration <= 0 THEN SHALL lançar ConfigurationError
6. WHEN scene_threshold < 0 THEN SHALL lançar ConfigurationError
7. WHEN data_dir é None THEN SHALL definir como base_dir/data automaticamente
8. WHEN configurações são acessadas THEN SHALL ser tipadas e não magic strings

### Requirement 5: Validação de Domínio Robusta

**User Story:** Como desenvolvedor do sistema, quero validações robustas nas entidades de domínio, para que seja impossível criar objetos em estado inválido e todos os erros sejam detectados precocemente.

#### Acceptance Criteria

1. WHEN Video é instanciada THEN SHALL validar ID, título, sources e duração
2. WHEN ID é vazio ou None THEN SHALL lançar InvalidVideoFormatError
3. WHEN ID tem mais de 255 caracteres THEN SHALL lançar InvalidVideoFormatError
4. WHEN título é vazio ou None THEN SHALL lançar InvalidVideoFormatError
5. WHEN não há file_path válido nem URL válida THEN SHALL lançar InvalidVideoFormatError
6. WHEN duração é negativa THEN SHALL lançar InvalidVideoFormatError
7. WHEN URL é fornecida THEN SHALL validar formato usando regex apropriado
8. WHEN validação falha THEN SHALL incluir mensagem específica sobre qual validação falhou

### Requirement 6: Camada de Apresentação Refatorada

**User Story:** Como desenvolvedor do sistema, quero uma camada de apresentação limpa separada da lógica de negócio, para que o main.py seja apenas um ponto de entrada que delega para comandos específicos.

#### Acceptance Criteria

1. WHEN main.py é executado THEN SHALL ter menos de 50 linhas de código
2. WHEN argumentos são processados THEN SHALL delegar para comando específico apropriado
3. WHEN YouTubeCommand é executado THEN SHALL processar URLs do YouTube
4. WHEN LocalVideoCommand é executado THEN SHALL processar arquivos locais
5. WHEN BatchCommand é executado THEN SHALL processar múltiplos arquivos
6. WHEN comando é executado THEN SHALL capturar exceções específicas e exibir mensagens amigáveis
7. WHEN erro ocorre THEN SHALL exibir mensagem específica do tipo de erro
8. WHEN comando é bem-sucedido THEN SHALL exibir confirmação com detalhes relevantes

### Requirement 7: Padrões de Design Implementados

**User Story:** Como arquiteto do sistema, quero padrões de design bem implementados e documentados, para que o código seja extensível, manutenível e siga as melhores práticas da indústria.

#### Acceptance Criteria

1. WHEN Strategy Pattern é implementado THEN SHALL permitir diferentes estratégias de AI
2. WHEN Command Pattern é implementado THEN SHALL encapsular operações CLI
3. WHEN novo AI provider é adicionado THEN SHALL ser possível em menos de 1 hora
4. WHEN padrão é implementado THEN SHALL ser documentado com justificativa
5. WHEN AIStrategy é definida THEN SHALL ter métodos transcribe() e summarize()
6. WHEN Command é definida THEN SHALL ter métodos execute() e validate_args()
7. WHEN padrão é usado THEN SHALL ter testes específicos validando comportamento
8. WHEN documentação é criada THEN SHALL incluir exemplos de uso e extensão

### Requirement 8: Cobertura de Testes BDD/TDD

**User Story:** Como desenvolvedor do sistema, quero cobertura de testes abrangente com cenários BDD, para que o sistema seja confiável e os testes sirvam como documentação viva.

#### Acceptance Criteria

1. WHEN testes são executados THEN SHALL atingir cobertura mínima de 80%
2. WHEN cenários BDD são definidos THEN SHALL usar formato Gherkin
3. WHEN teste BDD é executado THEN SHALL validar comportamento end-to-end
4. WHEN Use Case é testado THEN SHALL usar mocks para todas as dependências
5. WHEN exceção específica é testada THEN SHALL verificar tipo e mensagem
6. WHEN validação de domínio é testada THEN SHALL cobrir todos os cenários de erro
7. WHEN teste de integração é executado THEN SHALL validar fluxo completo
8. WHEN testes são executados THEN SHALL servir como documentação do comportamento esperado

### Requirement 9: Métricas de Qualidade

**User Story:** Como desenvolvedor do sistema, quero métricas de qualidade automatizadas e configuradas, para que o código mantenha padrões altos de qualidade continuamente.

#### Acceptance Criteria

1. WHEN análise estática é executada THEN SHALL usar pylint, flake8, black e isort
2. WHEN complexidade ciclomática é medida THEN SHALL ser ≤ 10 por função
3. WHEN linhas por função são contadas THEN SHALL ser ≤ 20
4. WHEN linhas por classe são contadas THEN SHALL ser ≤ 200
5. WHEN duplicação de código é medida THEN SHALL ser ≤ 3%
6. WHEN análise de segurança é executada THEN SHALL usar bandit
7. WHEN pipeline de qualidade é executado THEN SHALL completar em < 2 minutos
8. WHEN métricas falham THEN SHALL impedir merge/deploy

### Requirement 10: Conformidade com Diretrizes Mandatórias

**User Story:** Como arquiteto do sistema, quero 100% de conformidade com as diretrizes mandatórias definidas no steering, para que o projeto sirva como referência de excelência em Clean Architecture.

#### Acceptance Criteria

1. WHEN estrutura de diretórios é verificada THEN SHALL seguir exatamente o padrão definido
2. WHEN princípios SOLID são verificados THEN SHALL ter zero violações
3. WHEN regra de dependência é verificada THEN SHALL ser respeitada em todas as camadas
4. WHEN nomenclatura é verificada THEN SHALL seguir convenções definidas
5. WHEN magic numbers/strings são verificados THEN SHALL ter zero ocorrências
6. WHEN injeção de dependência é verificada THEN SHALL ser 100% implementada
7. WHEN documentação é verificada THEN SHALL estar atualizada e completa
8. WHEN checklist de conformidade é executado THEN SHALL ter 100% de aprovação