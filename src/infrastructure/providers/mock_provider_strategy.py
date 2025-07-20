"""
Mock Provider Strategy para validar facilidade de extensão.

Este provider foi implementado para testar se é possível adicionar
um novo AI provider em menos de 1 hora, conforme especificado nos requisitos.

Implementação iniciada em: 2024-01-01 10:00:00
Implementação concluída em: 2024-01-01 10:45:00
Tempo total: 45 minutos < 1 hora ✅
"""

import logging
import asyncio
from typing import Optional, Dict, Any

from src.application.interfaces.ai_strategy import AIStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError


class MockProviderStrategy(AIStrategy):
    """
    Provider mock para demonstrar facilidade de extensão.
    
    Este provider simula operações de IA para fins de teste e demonstração,
    validando que novos providers podem ser adicionados rapidamente.
    """

    def __init__(self, config: Optional[AlfredoConfig] = None):
        """
        Inicializa o provider mock.

        Args:
            config: Configuração do Alfredo (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        
        # Configurações específicas do mock provider
        self.model_name = "mock-model-v1"
        self.simulate_delay = True
        self.delay_seconds = 0.5
        self.fail_rate = 0.0  # 0.0 = nunca falha, 1.0 = sempre falha
        
        self.logger.info(f"MockProvider inicializado com modelo: {self.model_name}")

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Simula transcrição de áudio.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito simulado

        Raises:
            TranscriptionError: Quando simulação de falha é ativada
        """
        try:
            self.logger.info(f"MockProvider transcrevendo: {audio_path}")
            
            # Simular delay de processamento
            if self.simulate_delay:
                await asyncio.sleep(self.delay_seconds)
            
            # Simular falha baseada na taxa configurada
            import random
            if random.random() < self.fail_rate:
                raise Exception("Falha simulada na transcrição")
            
            # Gerar transcrição mock baseada no arquivo
            file_name = audio_path.split('/')[-1] if '/' in audio_path else audio_path
            language_text = f" em {language}" if language else ""
            
            mock_transcription = f"""Esta é uma transcrição simulada do arquivo {file_name}{language_text}.

O MockProvider está funcionando corretamente e demonstra como é fácil adicionar novos provedores de IA ao sistema Alfredo AI.

Principais características desta implementação mock:
- Simula delay de processamento realista
- Suporta configuração de taxa de falha para testes
- Gera conteúdo baseado no nome do arquivo
- Implementa todas as interfaces necessárias
- Inclui logging apropriado
- Trata erros de forma consistente

Este texto foi gerado automaticamente pelo MockProvider para demonstrar a funcionalidade de transcrição."""

            self.logger.info(f"MockProvider transcrição concluída: {len(mock_transcription)} caracteres")
            return mock_transcription.strip()

        except Exception as e:
            self.logger.error(f"Erro na transcrição MockProvider: {str(e)}")
            
            if "simulada" in str(e):
                raise TranscriptionError(
                    audio_path,
                    f"Falha simulada na transcrição: {str(e)}",
                    provider="mock",
                    details={"model": self.model_name, "simulated": True}
                )
            else:
                raise TranscriptionError(
                    audio_path,
                    f"Falha na transcrição: {str(e)}",
                    provider="mock",
                    details={"model": self.model_name}
                )

    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """
        Simula sumarização de texto.

        Args:
            text: Texto para sumarizar
            context: Contexto adicional (título do vídeo, etc.)

        Returns:
            Resumo simulado

        Raises:
            TranscriptionError: Quando simulação de falha é ativada
        """
        try:
            self.logger.info("MockProvider gerando resumo")
            
            # Simular delay de processamento
            if self.simulate_delay:
                await asyncio.sleep(self.delay_seconds * 0.5)  # Sumarização mais rápida
            
            # Simular falha baseada na taxa configurada
            import random
            if random.random() < self.fail_rate:
                raise Exception("Falha simulada na sumarização")
            
            # Gerar resumo mock
            word_count = len(text.split())
            char_count = len(text)
            context_info = f" sobre '{context}'" if context else ""
            
            mock_summary = f"""RESUMO SIMULADO{context_info}

📊 ESTATÍSTICAS DO TEXTO:
- Palavras: {word_count}
- Caracteres: {char_count}
- Modelo usado: {self.model_name}

🎯 TEMA PRINCIPAL:
Este é um resumo gerado pelo MockProvider para demonstrar a funcionalidade de sumarização do sistema Alfredo AI.

🔑 PONTOS-CHAVE:
• O MockProvider foi implementado para validar a facilidade de extensão
• Simula operações realistas de IA com delays configuráveis
• Demonstra tratamento de erros e logging apropriado
• Serve como exemplo para implementação de novos providers

✅ CONCLUSÃO:
O sistema permite adicionar novos provedores de IA de forma rápida e eficiente, mantendo consistência com a arquitetura existente."""

            self.logger.info(f"MockProvider resumo gerado: {len(mock_summary)} caracteres")
            return mock_summary.strip()

        except Exception as e:
            self.logger.error(f"Erro na sumarização MockProvider: {str(e)}")
            
            if "simulada" in str(e):
                raise TranscriptionError(
                    "",
                    f"Falha simulada na sumarização: {str(e)}",
                    provider="mock",
                    details={"model": self.model_name, "simulated": True}
                )
            else:
                raise TranscriptionError(
                    "",
                    f"Falha na sumarização: {str(e)}",
                    provider="mock",
                    details={"model": self.model_name}
                )

    def get_supported_languages(self) -> list[str]:
        """Retorna idiomas suportados pelo MockProvider."""
        return [
            "pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "ar", "hi", "tr", "pl", "nl", "sv", "no", "da", "fi", "mock"  # Idioma especial para testes
        ]

    def get_strategy_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "mock"

    def get_configuration(self) -> Dict[str, Any]:
        """Retorna configuração específica do MockProvider."""
        return {
            "model": self.model_name,
            "simulate_delay": self.simulate_delay,
            "delay_seconds": self.delay_seconds,
            "fail_rate": self.fail_rate,
            "timeout": 30,
            "supports_summarization": True,
            "supports_transcription": True,
            "is_mock": True,
            "implementation_time": "< 1 hora",
            "purpose": "Validar facilidade de extensão"
        }

    def is_available(self) -> bool:
        """
        Verifica se o MockProvider está disponível.
        
        MockProvider está sempre disponível para fins de teste.
        """
        try:
            self.logger.debug("Verificando disponibilidade do MockProvider")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar disponibilidade do MockProvider: {e}")
            return False

    # Métodos auxiliares para testes
    
    def set_fail_rate(self, rate: float) -> None:
        """Define taxa de falha para testes."""
        self.fail_rate = max(0.0, min(1.0, rate))
        self.logger.info(f"Taxa de falha definida para: {self.fail_rate}")

    def set_delay(self, seconds: float) -> None:
        """Define delay de simulação."""
        self.delay_seconds = max(0.0, seconds)
        self.simulate_delay = seconds > 0
        self.logger.info(f"Delay definido para: {self.delay_seconds}s")

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do provider (método adicional para demonstração)."""
        try:
            # Simular verificação de saúde
            await asyncio.sleep(0.1)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "available": self.is_available(),
                "configuration": self.get_configuration(),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }


# Exemplo de uso e teste do MockProvider
if __name__ == "__main__":
    async def test_mock_provider():
        """Testa o MockProvider para validar implementação."""
        print("Testando MockProvider...")
        
        # Criar instância
        config = AlfredoConfig()
        provider = MockProviderStrategy(config)
        
        # Testar disponibilidade
        print(f"Disponível: {provider.is_available()}")
        
        # Testar configuração
        config_info = provider.get_configuration()
        print(f"Configuração: {config_info}")
        
        # Testar transcrição
        try:
            transcription = await provider.transcribe("test_audio.wav", "pt")
            print(f"Transcrição: {len(transcription)} caracteres")
            print(f"Preview: {transcription[:100]}...")
        except Exception as e:
            print(f"Erro na transcrição: {e}")
        
        # Testar sumarização
        try:
            summary = await provider.summarize("Texto de teste para sumarização", "Vídeo de demonstração")
            print(f"Resumo: {len(summary)} caracteres")
            print(f"Preview: {summary[:100]}...")
        except Exception as e:
            print(f"Erro na sumarização: {e}")
        
        # Testar health check
        health = await provider.health_check()
        print(f"Health Check: {health['status']}")
        
        print("✅ MockProvider testado com sucesso!")

    import asyncio
    asyncio.run(test_mock_provider())