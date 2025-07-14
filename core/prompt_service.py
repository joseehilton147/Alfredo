#!/usr/bin/env python3
"""
📝 ALFREDO AI - SERVIÇO DE PROMPTS
=================================
Serviço responsável por gerar os prompts para os modelos de IA.
Centraliza toda a lógica de geração de prompts seguindo padrões enterprise.
"""

from pathlib import Path
from typing import Optional
import re

from config.paths import paths

NOTA_TRANSPARENCIA = '*Nota de Transparência: O conteúdo acima foi gerado por IA com base na transcrição. As referências são sugestões baseadas nos tópicos do vídeo e devem ser verificadas de forma independente.*'


def _normalize(text: str) -> str:
    """
    Normaliza texto removendo espaços extras e convertendo para minúsculas.
    
    Args:
        text (str): Texto a ser normalizado
        
    Returns:
        str: Texto normalizado
    """
    return re.sub(r'\s+', '', text).lower()


def get_summary_prompt(transcription: str, video_title: str) -> str:
    """
    Gera o prompt de resumo a partir do template Markdown.
    
    Sempre inclui a Nota de Transparência ao final do prompt gerado.
    Utiliza o sistema centralizado de paths para localizar o template.
    
    Args:
        transcription (str): Transcrição do vídeo/áudio
        video_title (str): Título do vídeo
        
    Returns:
        str: Prompt formatado pronto para ser enviado ao modelo de IA
        
    Raises:
        FileNotFoundError: Quando o template não é encontrado
        UnicodeDecodeError: Quando há problemas de encoding no template
    """
    template_path = paths.PROMPTS_DIR / 'summary_template.md'
    
    if not template_path.exists():
        raise FileNotFoundError(f'Template não encontrado: {template_path}')
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f'Erro de encoding no template {template_path}: {e}')
    
    # Formatar o prompt com os dados fornecidos
    prompt = template.format(transcription=transcription, video_title=video_title)
    
    # Adicionar nota de transparência
    return f'{prompt}\n\n{NOTA_TRANSPARENCIA}'


def validate_template_format(template_path: Path) -> bool:
    """
    Valida se o template possui os placeholders necessários.
    
    Args:
        template_path (Path): Caminho para o arquivo de template
        
    Returns:
        bool: True se o template é válido, False caso contrário
    """
    if not template_path.exists():
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se contém os placeholders obrigatórios
        required_placeholders = ['{transcription}', '{video_title}']
        return all(placeholder in content for placeholder in required_placeholders)
    
    except Exception:
        return False
