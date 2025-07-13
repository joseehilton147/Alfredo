import os
from dotenv import load_dotenv
from services.ai_provider import AIProvider
from services.groq_provider import GroqProvider
from services.ollama_provider import OllamaProvider

def safe_print(text, end="\n", flush=False):
    """Função para imprimir texto sem problemas de encoding no Windows"""
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais, mantém apenas ASCII
        import re
        text = re.sub(r'[^\x20-\x7E]+', '', text)
        print(text, end=end, flush=flush)

def get_ai_provider(provider_override: str = None) -> AIProvider:
    load_dotenv()
    provider = provider_override or os.getenv('AI_PROVIDER') or 'ollama'
    provider = provider.lower()
    if provider == 'groq':
        safe_print('🤖 Usando o provedor de IA: Groq')
        return GroqProvider()
    elif provider == 'ollama':
        safe_print('🤖 Usando o provedor de IA: Ollama')
        return OllamaProvider()
    else:
        raise ValueError(f'Provedor de IA desconhecido: {provider}')
