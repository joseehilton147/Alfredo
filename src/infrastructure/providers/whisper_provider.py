"""Implementação do provedor de transcrição usando OpenAI Whisper."""
import logging
from typing import Optional

import whisper


class WhisperProvider:
    """Provedor de transcrição usando OpenAI Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """Inicializa o provedor Whisper.
        
        Args:
            model_name: Nome do modelo Whisper a usar
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        
    async def transcribe_audio(
        self, 
        audio_path: str, 
        language: Optional[str] = None
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
            result = self.model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )
            
            transcription = result["text"].strip()
            self.logger.info(f"Transcrição concluída: {len(transcription)} caracteres")
            
            return transcription
            
        except Exception as e:
            self.logger.error(f"Erro na transcrição: {str(e)}")
            raise RuntimeError(f"Falha ao transcrever áudio: {str(e)}")
            
    def get_supported_languages(self) -> list[str]:
        """Retorna lista de idiomas suportados."""
        return [
            "en", "pt", "es", "fr", "de", "it", "ja", "ko", "zh", "ru",
            "ar", "hi", "tr", "pl", "nl", "sv", "no", "da", "fi"
        ]
