"""Implementação do provedor de transcrição usando OpenAI Whisper."""

import logging
from typing import Optional

import whisper

from src.application.interfaces.ai_provider import AIProviderInterface
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import TranscriptionError, ProviderUnavailableError


class WhisperProvider(AIProviderInterface):
    """Provedor de transcrição usando OpenAI Whisper."""

    def __init__(self, config: Optional[AlfredoConfig] = None):
        """Inicializa o provedor Whisper.

        Args:
            config: Configuração do Alfredo (opcional, usa padrão se não fornecida)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AlfredoConfig()
        self.model_name = self.config.whisper_model
        self.model = None

    async def transcribe_audio(
        self, audio_path: str, language: Optional[str] = None
    ) -> str:
        """Transcreve áudio usando Whisper.

        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (opcional)

        Returns:
            Texto transcrito
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

    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados."""
        return [
            "en",
            "pt",
            "es",
            "fr",
            "de",
            "it",
            "ja",
            "ko",
            "zh",
            "ru",
            "ar",
            "hi",
            "tr",
            "pl",
            "nl",
            "sv",
            "no",
            "da",
            "fi",
        ]
