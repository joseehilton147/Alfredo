Feature: Processamento de vídeos do YouTube
  Como usuário do sistema Alfredo AI
  Quero processar vídeos do YouTube
  Para obter transcrições e resumos automaticamente

  Background:
    Given que o sistema está configurado corretamente
    And que tenho conectividade com a internet

  Scenario: Processamento bem-sucedido de vídeo válido
    Given que tenho uma URL válida do YouTube "https://youtube.com/watch?v=dQw4w9WgXcQ"
    When executo o processamento do vídeo
    Then devo receber uma transcrição válida
    And devo receber metadados do vídeo
    And o resultado deve ser salvo no repositório
    And o arquivo temporário deve ser removido
    And o processamento deve completar em menos de 30 segundos

  Scenario: Processamento com geração de resumo
    Given que tenho uma URL válida do YouTube "https://youtube.com/watch?v=educational_video"
    When executo o processamento do vídeo com resumo
    Then devo receber uma transcrição válida
    And devo receber um resumo válido
    And devo receber metadados do vídeo
    And o resultado deve ser salvo no repositório

  Scenario: Tratamento de URL inválida
    Given que tenho uma URL inválida "not-a-url"
    When executo o processamento do vídeo
    Then devo receber um erro de "formato inválido"
    And nenhum arquivo deve ser criado

  Scenario: Tratamento de URL do YouTube inválida
    Given que tenho uma URL inválida "https://youtube.com/watch?v=invalid"
    When executo o processamento do vídeo
    Then devo receber um erro de "download"
    And nenhum arquivo deve ser criado

  Scenario: Recuperação de falha de download com retry
    Given que tenho uma URL que falha no download
    When executo o processamento do vídeo
    Then o sistema deve tentar novamente até 3 vezes
    And se todas as tentativas falharem, deve retornar erro específico

  Scenario: Processamento de vídeo muito longo
    Given que tenho uma URL válida do YouTube "https://youtube.com/watch?v=very_long_video"
    And que o vídeo tem duração maior que o limite configurado
    When executo o processamento do vídeo
    Then devo receber um erro de "formato inválido"
    And nenhum arquivo deve ser criado

  Scenario: Processamento com provider de IA indisponível
    Given que tenho uma URL válida do YouTube "https://youtube.com/watch?v=test_video"
    And que o provider de IA está indisponível
    When executo o processamento do vídeo
    Then devo receber um erro de "provider indisponível"
    And o vídeo deve ser baixado e salvo
    And a transcrição não deve ser gerada

  Scenario: Processamento em lote de múltiplas URLs
    Given que tenho uma lista de URLs válidas do YouTube
    When executo o processamento em lote
    Then todos os vídeos válidos devem ser processados
    And devo receber um relatório de processamento
    And vídeos com erro devem ser reportados separadamente

  Scenario: Cache de vídeo já processado
    Given que tenho uma URL válida do YouTube "https://youtube.com/watch?v=cached_video"
    And que o vídeo já foi processado anteriormente
    When executo o processamento do vídeo
    Then devo receber o resultado do cache
    And nenhum download deve ser realizado
    And o processamento deve completar em menos de 5 segundos

  Scenario: Forçar reprocessamento de vídeo em cache
    Given que tenho uma URL válida do YouTube "https://youtube.com/watch?v=cached_video"
    And que o vídeo já foi processado anteriormente
    When executo o processamento do vídeo com força de reprocessamento
    Then o vídeo deve ser baixado novamente
    And uma nova transcrição deve ser gerada
    And o cache deve ser atualizado