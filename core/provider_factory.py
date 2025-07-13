import os
from dotenv import load_dotenv
from services.ai_provider import AIProvider
from services.groq_provider import GroqProvider
from services.ollama_provider import OllamaProvider

def get_ai_provider(provider_override: str = None) -> AIProvider:
    load_dotenv()
    provider = provider_override or os.getenv('AI_PROVIDER') or 'ollama'
    provider = provider.lower()
    if provider == 'groq':
        print('🤖 Usando o provedor de IA: Groq')
        return GroqProvider()
    elif provider == 'ollama':
        print('🤖 Usando o provedor de IA: Ollama')
        return OllamaProvider()
    else:
        raise ValueError(f'Provedor de IA desconhecido: {provider}')
