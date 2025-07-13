import os
import asyncio
import groq
from services.ai_provider import AIProvider
from services.prompt_service import get_summary_prompt

class GroqProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError('GROQ_API_KEY não encontrada nas variáveis de ambiente')
        self.client = groq.AsyncGroq(api_key=api_key)

    async def transcribe(self, audio_path: str) -> str:
        try:
            with open(audio_path, 'rb') as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model='whisper-large-v3',
                    file=audio_file
                )
            return response.text
        except Exception as e:
            raise RuntimeError(f'Erro na transcrição Groq: {e}')

    async def summarize(self, transcription: str, video_title: str) -> str:
        final_prompt = get_summary_prompt(transcription, video_title)
        try:
            response = await self.client.chat.completions.create(
                model='llama3-8b-8192',
                messages=[
                    {'role': 'user', 'content': final_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f'Erro na sumarização Groq: {e}')
