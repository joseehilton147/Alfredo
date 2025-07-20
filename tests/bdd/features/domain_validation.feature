Feature: Validação de entidades de domínio
  Como desenvolvedor do sistema
  Quero que as entidades de domínio sejam validadas corretamente
  Para garantir que dados inválidos não sejam aceitos

  Background:
    Given que o sistema de validação está ativo

  Scenario: Criação de vídeo com dados válidos
    Given que tenho dados válidos para um vídeo
    When crio uma entidade Video
    Then a entidade deve ser criada com sucesso
    And todos os campos devem estar preenchidos corretamente

  Scenario: Validação de ID de vídeo vazio
    Given que tenho um ID de vídeo vazio
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "ID não pode ser vazio"

  Scenario: Validação de ID de vídeo muito longo
    Given que tenho um ID de vídeo com mais de 255 caracteres
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "máximo 255 caracteres"

  Scenario: Validação de caracteres inválidos no ID
    Given que tenho um ID de vídeo com caracteres especiais inválidos
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "apenas letras, números, _ e -" 
 Scenario: Validação de título vazio
    Given que tenho um título de vídeo vazio
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "título não pode ser vazio"

  Scenario: Validação de título muito longo
    Given que tenho um título de vídeo com mais de 500 caracteres
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "máximo 500 caracteres"

  Scenario: Validação de sources inválidas
    Given que não tenho nem file_path válido nem URL válida
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "deve ter file_path válido ou URL válida"

  Scenario: Validação de duração negativa
    Given que tenho uma duração negativa para o vídeo
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "não pode ser negativa"

  Scenario: Validação de duração muito longa
    Given que tenho uma duração maior que 24 horas
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "máximo 24 horas"

  Scenario: Validação de URL inválida
    Given que tenho uma URL com formato inválido
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "URL inválida"

  Scenario: Validação de file_path inexistente
    Given que tenho um file_path que não existe
    When tento criar uma entidade Video
    Then devo receber um erro de "InvalidVideoFormatError"
    And a mensagem deve indicar "arquivo não encontrado"

  Scenario: Validação bem-sucedida com file_path válido
    Given que tenho um file_path válido
    When crio uma entidade Video
    Then a entidade deve ser criada com sucesso
    And o file_path deve estar definido

  Scenario: Validação bem-sucedida com URL válida
    Given que tenho uma URL válida
    When crio uma entidade Video
    Then a entidade deve ser criada com sucesso
    And a URL deve estar definida

  Scenario: Validação de configuração inválida
    Given que tenho uma configuração com timeout negativo
    When tento criar AlfredoConfig
    Then devo receber um erro de "ConfigurationError"
    And a mensagem deve indicar "deve ser positivo"

  Scenario: Validação de API key obrigatória
    Given que configuro provider Groq sem API key
    When tento validar a configuração
    Then devo receber um erro de "ConfigurationError"
    And a mensagem deve indicar "obrigatória para provider groq"