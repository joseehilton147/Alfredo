"""Implementação da estratégia Ollama para transcrição e sumarização."""

import logging
import json
from typing import Optional, Dict, Any
import aiohttp
import asyncio

from src.application.interfaces.ai_strategy import AIStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError


class OllamaStrategy(AIStrategy):
    """Estratégia de IA usando Ollama para transcrição e sumarização."""

    def __init__(self, config: Optional[AlfredoConfig] = None):
        """Inicializa a estratégia Ollama.

        Args:
            config: Configuração do Alfredo (opcional, usa padrão se não fornecida)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        self._strategy_config = self.config.get_provider_config("ollama")
        self.model_name = self._strategy_config.get("model", "llama3:8b")
        self.base_url = "http://localhost:11434"  # URL padrão do Ollama
        self.timeout = self._strategy_config.get("timeout", 600)

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcreve áudio usando Ollama.
        
        Nota: Ollama não tem capacidade nativa de transcrição de áudio.
        Esta implementação usa uma abordagem alternativa ou retorna erro.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito

        Raises:
            ProviderUnavailableError: Ollama não suporta transcrição direta de áudio
        """
        self.logger.warning("Ollama não suporta transcrição direta de áudio")
        raise ProviderUnavailableError(
            "ollama",
            "Ollama não possui capacidade nativa de transcrição de áudio. Use Whisper ou Groq para transcrição.",
            details={
                "audio_path": audio_path,
                "suggestion": "Use WhisperStrategy ou GroqStrategy para transcrição"
            }
        )

    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """Gera resumo do texto usando Ollama.

        Args:
            text: Texto para sumarizar
            context: Contexto adicional (título do vídeo, etc.)

        Returns:
            Resumo gerado

        Raises:
            TranscriptionError: Quando falha a sumarização
            ProviderUnavailableError: Quando o serviço está indisponível
        """
        try:
            self.logger.info(f"Gerando resumo com Ollama (modelo: {self.model_name})")
            
            # Prompt para sumarização
            prompt = f"""Analise o seguinte texto transcrito e crie um resumo estruturado em português brasileiro.

{f"Contexto: {context}" if context else ""}

Texto para resumir:
{text}

Crie um resumo que inclua:
1. Tema principal
2. Pontos-chave abordados  
3. Conclusões importantes

Mantenha o resumo conciso mas informativo."""

            # Payload para API do Ollama
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            }

            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ProviderUnavailableError(
                            "ollama",
                            f"Erro HTTP {response.status}: {error_text}",
                            details={"model": self.model_name}
                        )
                    
                    result = await response.json()
                    summary = result.get("response", "").strip()
                    
                    if not summary:
                        raise TranscriptionError(
                            "",
                            "Resposta vazia do Ollama",
                            provider="ollama",
                            details={"model": self.model_name}
                        )
                    
                    self.logger.info(f"Resumo Ollama gerado: {len(summary)} caracteres")
                    return summary

        except aiohttp.ClientError as e:
            self.logger.error(f"Erro de conexão com Ollama: {str(e)}")
            raise ProviderUnavailableError(
                "ollama",
                f"Não foi possível conectar ao Ollama: {str(e)}. Verifique se o serviço está rodando.",
                details={"base_url": self.base_url, "model": self.model_name}
            )
        except asyncio.TimeoutError:
            self.logger.error("Timeout na requisição para Ollama")
            raise ProviderUnavailableError(
                "ollama",
                f"Timeout após {self.timeout}s. O modelo pode estar sendo baixado.",
                details={"timeout": self.timeout, "model": self.model_name}
            )
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar resposta JSON do Ollama: {str(e)}")
            raise TranscriptionError(
                "",
                f"Resposta inválida do Ollama: {str(e)}",
                provider="ollama",
                details={"model": self.model_name}
            )
        except Exception as e:
            self.logger.error(f"Erro na sumarização Ollama: {str(e)}")
            raise TranscriptionError(
                "",
                f"Falha na sumarização: {str(e)}",
                provider="ollama",
                details={"model": self.model_name}
            )

    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados pelo Ollama."""
        # Ollama suporta múltiplos idiomas dependendo do modelo
        return [
            "en", "pt", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "ar", "hi", "tr", "pl", "nl", "sv", "no", "da", "fi"
        ]

    def get_strategy_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "ollama"

    def get_configuration(self) -> Dict[str, Any]:
        """Retorna configuração específica da estratégia Ollama."""
        return {
            "model": self.model_name,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "supports_summarization": True,
            "supports_transcription": False,  # Ollama não suporta transcrição direta
            "requires_local_service": True
        }

    def is_available(self) -> bool:
        """Verifica se a estratégia Ollama está disponível."""
        try:
            # Verifica se consegue fazer uma requisição simples para o Ollama
            import asyncio
            import aiohttp
            
            async def check_ollama():
                try:
                    timeout = aiohttp.ClientTimeout(total=5)  # Timeout curto para verificação
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(f"{self.base_url}/api/tags") as response:
                            return response.status == 200
                except:
                    return False
            
            # Executa verificação assíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(check_ollama())
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar disponibilidade do Ollama: {e}")
            return False