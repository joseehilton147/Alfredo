from pathlib import Path
import re

NOTA_TRANSPARENCIA = '*Nota de Transparência: O conteúdo acima foi gerado por IA com base na transcrição. As referências são sugestões baseadas nos tópicos do vídeo e devem ser verificadas de forma independente.*'

# Função utilitária para normalizar texto
def _normalize(text):
    return re.sub(r'\s+', '', text).lower()

def get_summary_prompt(transcription: str, video_title: str) -> str:
    """Gera o prompt de resumo a partir do template Markdown, sempre incluindo a Nota de Transparência ao final."""
    template_path = Path(__file__).parent.parent / 'config' / 'prompts' / 'summary_template.md'
    if not template_path.exists():
        raise FileNotFoundError(f'Template não encontrado: {template_path}')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    prompt = template.format(transcription=transcription, video_title=video_title)
    prompt = f'{prompt}\n\n{NOTA_TRANSPARENCIA}'
    return prompt
