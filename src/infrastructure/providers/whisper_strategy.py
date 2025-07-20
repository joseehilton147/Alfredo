"""Implementação da estratégia Whisper para transcrição de áudio."""

import logging
from typing import Optional, Dict, Any

import whisper

from src.application.interfaces.ai_strategy import AIStrategy
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError


class WhisperStrategy(AIStrategy):
    """Estratégia de IA usando OpenAI Whisper para transcrição."""

    def __init__(self, config: Optional[AlfredoConfig] = None):
        """Inicializa a estratégia Whisper.

        Args:
            config: Configuração do Alfredo (opcional, usa padrão se não fornecida)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        self.model_name = self.config.whisper_model
        self.model = None
        self._strategy_config = self.config.get_provider_config("whisper")

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcreve áudio usando Whisper.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito

        Raises:
            TranscriptionError: Quando falha a transcrição
            ProviderUnavailableError: Quando o modelo não pode ser carregado
        """
        try:
            if self.model is None:
                self.logger.info(f"Carregando modelo Whisper: {self.model_name}")
                self.model = whisper.load_model(self.model_name)

            self.logger.info(f"Transcrevendo áudio: {audio_path}")

            # Transcrever áudio
            result = self.model.transcribe(audio_path, language=language, verbose=False)

            transcription = result["text"].strip()
            self.logger.info(f"Transcrição concluída: {len(transcription)} caracteres")

            return transcription

        except FileNotFoundError as e:
            self.logger.error(f"Arquivo de áudio não encontrado: {str(e)}")
            raise TranscriptionError(
                audio_path, 
                f"Arquivo não encontrado: {str(e)}", 
                provider="whisper",
                details={"model": self.model_name}
            )
        except Exception as e:
            self.logger.error(f"Erro na transcrição: {str(e)}")
            # Check if it's a model loading error
            if "model" in str(e).lower() or "load" in str(e).lower():
                raise ProviderUnavailableError(
                    "whisper",
                    f"Erro ao carregar modelo {self.model_name}: {str(e)}",
                    details={"model": self.model_name, "audio_path": audio_path}
                )
            else:
                raise TranscriptionError(
                    audio_path, 
                    f"Falha na transcrição: {str(e)}", 
                    provider="whisper",
                    details={"model": self.model_name}
                )

    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """Gera resumo do texto fornecido.
        
        Nota: Whisper é especializado em transcrição, não sumarização.
        Esta implementação retorna um resumo básico baseado em heurísticas.

        Args:
            text: Texto para sumarizar
            context: Contexto adicional (título do vídeo, etc.)

        Returns:
            Resumo básico do texto
        """
        self.logger.info("Gerando resumo básico com Whisper (heurístico)")
        
        # Resumo básico: primeiras e últimas frases
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return text
        
        # Pega as primeiras 2 e última frase
        summary_sentences = sentences[:2] + [sentences[-1]]
        summary = '. '.join(summary_sentences) + '.'
        
        if context:
            summary = f"Resumo de '{context}': {summary}"
        
        return summary

    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados pelo Whisper."""
        return [
            "en", "pt", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "ar", "hi", "tr", "pl", "nl", "sv", "no", "da", "fi"
        ]

    def get_strategy_name(self) -> str:
        """Retorna o nome da estratégia."""
        return "whisper"

    def get_configuration(self) -> Dict[str, Any]:
        """Retorna configuração específica da estratégia Whisper."""
        return {
            "model": self.model_name,
            "timeout": self._strategy_config.get("timeout", 600),
            "supports_summarization": False,  # Whisper não é otimizado para sumarização
            "transcription_only": True
        }

    def is_available(self) -> bool:
        """Verifica se a estratégia Whisper está disponível."""
        try:
            # Tenta importar whisper para verificar disponibilidade
            import whisper
            return True
        except ImportError:
            self.logger.warning("Whisper não está instalado")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar disponibilidade do Whisper: {e}")
            return False