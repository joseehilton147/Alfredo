"""Implementação da estratégia Groq para transcrição e sumarização."""

import logging
import os
from typing import Optional, Dict, Any

from src.application.interfaces.ai_strategy import AIStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError, ConfigurationError


class GroqStrategy(AIStrategy):
    """Estratégia de IA usando Groq para transcrição e sumarização."""

    def __init__(self, config: Optional[AlfredoConfig] = None):
        """Inicializa a estratégia Groq.

        Args:
            config: Configuração do Alfredo (opcional, usa padrão se não fornecida)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        self._strategy_config = self.config.get_provider_config("groq")
        self.model_name = self._strategy_config.get("model", "llama-3.3-70b-versatile")
        self.api_key = self._strategy_config.get("api_key")
        
        if not self.api_key:
            raise ConfigurationError(
                "groq_api_key",
                "API key do Groq é obrigatória",
                "Defina GROQ_API_KEY no ambiente ou configuração"
            )

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcreve áudio usando Groq.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito

        Raises:
            TranscriptionError: Quando falha a transcrição
            ProviderUnavailableError: Quando o serviço está indisponível
        """
        try:
            # Importação dinâmica para evitar dependência obrigatória
            from groq import Groq
            
            client = Groq(api_key=self.api_key)
            
            self.logger.info(f"Transcrevendo áudio com Groq: {audio_path}")
            
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",  # Modelo de transcrição do Groq
                    language=language,
                    response_format="text"
                )
            
            result = transcription.strip()
            self.logger.info(f"Transcrição Groq concluída: {len(result)} caracteres")
            
            return result

        except FileNotFoundError as e:
            self.logger.error(f"Arquivo de áudio não encontrado: {str(e)}")
            raise TranscriptionError(
                audio_path,
                f"Arquivo não encontrado: {str(e)}",
                provider="groq",
                details={"model": "whisper-large-v3"}
            )
        except ImportError:
            self.logger.error("Biblioteca groq não está instalada")
            raise ProviderUnavailableError(
                "groq",
                "Biblioteca groq não está instalada. Execute: pip install groq",
                details={"audio_path": audio_path}
            )
        except Exception as e:
            self.logger.error(f"Erro na transcrição Groq: {str(e)}")
            if "api" in str(e).lower() or "key" in str(e).lower():
                raise ProviderUnavailableError(
                    "groq",
                    f"Erro de API: {str(e)}",
                    details={"audio_path": audio_path}
                )
            else:
                raise TranscriptionError(
                    audio_path,
                    f"Falha na transcrição: {str(e)}",
                    provider="groq",
                    details={"model": "whisper-large-v3"}
                )

    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """Gera resumo do texto usando Groq.

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
            from groq import Groq
            
            client = Groq(api_key=self.api_key)
            
            self.logger.info("Gerando resumo com Groq")
            
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

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em criar resumos claros e estruturados."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content.strip()
            self.logger.info(f"Resumo Groq gerado: {len(summary)} caracteres")
            
            return summary

        except ImportError:
            self.logger.error("Biblioteca groq não está instalada")
            raise ProviderUnavailableError(
                "groq",
                "Biblioteca groq não está instalada. Execute: pip install groq"
            )
        except Exception as e:
            self.logger.error(f"Erro na sumarização Groq: {str(e)}")
            if "api" in str(e).lower() or "key" in str(e).lower():
                raise ProviderUnavailableError(
                    "groq",
                    f"Erro de API: {str(e)}"
                )
            else:
                raise TranscriptionError(
                    "",
                    f"Falha na sumarização: {str(e)}",
                    provider="groq",
                    details={"model": self.model_name}
                )

    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados pelo Groq."""
        return [
            "en", "pt", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "ar", "hi", "tr", "pl", "nl", "sv", "no", "da", "fi"
        ]

    def get_strategy_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "groq"

    def get_configuration(self) -> Dict[str, Any]:
        """Retorna configuração específica da estratégia Groq."""
        return {
            "model": self.model_name,
            "transcription_model": "whisper-large-v3",
            "timeout": self._strategy_config.get("timeout", 600),
            "supports_summarization": True,
            "api_key_required": True,
            "has_api_key": bool(self.api_key)
        }

    def is_available(self) -> bool:
        """Verifica se a estratégia Groq está disponível."""
        try:
            # Verifica se tem API key
            if not self.api_key:
                self.logger.warning("API key do Groq não configurada")
                return False
            
            # Tenta importar groq
            import groq
            return True
            
        except ImportError:
            self.logger.warning("Biblioteca groq não está instalada")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar disponibilidade do Groq: {e}")
            return False