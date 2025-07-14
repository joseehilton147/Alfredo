import sys
import requests
import subprocess
import whisper
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integrations.ai_provider import AIProvider
from legacy.services_old.prompt_service import get_summary_prompt

class OllamaProvider(AIProvider):
    async def transcribe(self, audio_path: str) -> str:
        try:
            # Verifica se Whisper está instalado
            try:
                _ = whisper.load_model
            except Exception:
                raise ImportError('O pacote whisper não está instalado.')
            model = whisper.load_model('base')
            result = model.transcribe(audio_path)
            return result['text']
        except Exception as e:
            raise RuntimeError(f'Erro na transcrição com Whisper local: {e}')

    async def summarize(self, transcription: str, video_title: str) -> str:
        url = 'http://127.0.0.1:11434/api/generate'
        final_prompt = get_summary_prompt(transcription, video_title)
        payload = {
            'model': 'llama3:8b',
            'prompt': final_prompt,
            'stream': False
        }
        try:
            # Verifica se Ollama está acessível
            try:
                response = requests.get('http://127.0.0.1:11434')
                if response.status_code != 200:
                    raise ConnectionError('Ollama não está acessível na porta 11434.')
            except Exception:
                raise ConnectionError('Ollama não está acessível na porta 11434.')
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get('response', '')
        except Exception as e:
            raise RuntimeError(f'Erro na sumarização com Ollama local: {e}')
