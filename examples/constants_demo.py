#!/usr/bin/env python3
"""
Demonstração do uso das constantes centralizadas do Alfredo AI.

Este exemplo mostra como usar as constantes definidas em src/config/constants.py
para evitar magic numbers e strings no código.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.constants import (
    # Constantes de aplicação
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    
    # Constantes de modelos IA
    DEFAULT_GROQ_MODEL,
    DEFAULT_WHISPER_MODEL,
    DEFAULT_OLLAMA_MODEL,
    
    # Constantes de timeouts
    DEFAULT_DOWNLOAD_TIMEOUT,
    DEFAULT_TRANSCRIPTION_TIMEOUT,
    MAX_VIDEO_DURATION_HOURS,
    
    # Extensões de arquivo
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS,
    
    # Enums
    AIProvider,
    ProcessingStatus,
    VideoQuality,
    AudioFormat,
    
    # Constantes de interface
    ICON_SUCCESS,
    ICON_ERROR,
    ICON_VIDEO,
    ICON_AUDIO,
    
    # Mensagens padronizadas
    ERROR_PREFIX,
    SUCCESS_PREFIX,
    HELP_MESSAGE,
    
    # Padrões de validação
    VALID_ID_PATTERN,
    URL_PATTERN,
    YOUTUBE_URL_PATTERN,
)


def demonstrar_constantes_aplicacao():
    """Demonstra uso das constantes de aplicação."""
    print(f"🤖 {APP_NAME} v{APP_VERSION}")
    print(f"📝 {APP_DESCRIPTION}")
    print()


def demonstrar_constantes_modelos():
    """Demonstra uso das constantes de modelos de IA."""
    print("🧠 Modelos de IA Disponíveis:")
    print(f"  • Groq: {DEFAULT_GROQ_MODEL}")
    print(f"  • Whisper: {DEFAULT_WHISPER_MODEL}")
    print(f"  • Ollama: {DEFAULT_OLLAMA_MODEL}")
    print()


def demonstrar_enums():
    """Demonstra uso dos enums definidos."""
    print("📊 Enums Disponíveis:")
    
    print("  • Provedores de IA:")
    for provider in AIProvider:
        print(f"    - {provider.value}")
    
    print("  • Status de Processamento:")
    for status in ProcessingStatus:
        print(f"    - {status.value}")
    
    print("  • Qualidades de Vídeo:")
    for quality in VideoQuality:
        print(f"    - {quality.value}")
    
    print("  • Formatos de Áudio:")
    for format in AudioFormat:
        print(f"    - {format.value}")
    print()


def demonstrar_timeouts_limites():
    """Demonstra uso das constantes de timeouts e limites."""
    print("⏱️ Timeouts e Limites:")
    print(f"  • Download: {DEFAULT_DOWNLOAD_TIMEOUT}s")
    print(f"  • Transcrição: {DEFAULT_TRANSCRIPTION_TIMEOUT}s")
    print(f"  • Duração máxima: {MAX_VIDEO_DURATION_HOURS}h")
    print()


def demonstrar_extensoes_arquivo():
    """Demonstra uso das constantes de extensões de arquivo."""
    print("📁 Extensões Suportadas:")
    print(f"  • Vídeo: {', '.join(VIDEO_EXTENSIONS)}")
    print(f"  • Áudio: {', '.join(AUDIO_EXTENSIONS)}")
    print()


def demonstrar_icones_mensagens():
    """Demonstra uso dos ícones e mensagens padronizadas."""
    print("🎨 Ícones e Mensagens:")
    print(f"  {ICON_SUCCESS} Sucesso")
    print(f"  {ICON_ERROR} Erro")
    print(f"  {ICON_VIDEO} Vídeo")
    print(f"  {ICON_AUDIO} Áudio")
    print()
    
    print("💬 Mensagens Padronizadas:")
    print(f"  {SUCCESS_PREFIX}Operação concluída com sucesso!")
    print(f"  {ERROR_PREFIX}Ocorreu um erro durante a operação")
    print()


def demonstrar_validacao_url():
    """Demonstra uso dos padrões de validação."""
    import re
    
    print("🔍 Validação de URLs:")
    
    urls_teste = [
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://example.com/video.mp4",
        "invalid-url"
    ]
    
    for url in urls_teste:
        # Validar formato geral de URL
        url_valida = bool(re.match(URL_PATTERN, url))
        
        # Verificar se é YouTube
        youtube_match = re.search(YOUTUBE_URL_PATTERN, url)
        eh_youtube = bool(youtube_match)
        
        status = ICON_SUCCESS if url_valida else ICON_ERROR
        print(f"  {status} {url}")
        print(f"    • URL válida: {url_valida}")
        print(f"    • YouTube: {eh_youtube}")
        
        if eh_youtube and youtube_match:
            video_id = youtube_match.group(1)
            print(f"    • ID do vídeo: {video_id}")
        print()


def demonstrar_uso_pratico():
    """Demonstra uso prático das constantes em código."""
    print("💻 Exemplo de Uso Prático:")
    
    # Simulação de processamento de vídeo
    def processar_video(arquivo: str, provider: AIProvider = AIProvider.WHISPER):
        """Exemplo de função que usa constantes."""
        extensao = Path(arquivo).suffix.lower()
        
        if extensao not in VIDEO_EXTENSIONS:
            return f"{ERROR_PREFIX}Formato não suportado: {extensao}"
        
        print(f"  {ICON_VIDEO} Processando: {arquivo}")
        print(f"  🧠 Provider: {provider.value}")
        print(f"  ⏱️ Timeout: {DEFAULT_TRANSCRIPTION_TIMEOUT}s")
        
        # Simular processamento
        status = ProcessingStatus.TRANSCRIBING
        print(f"  📊 Status: {status.value}")
        
        return f"{SUCCESS_PREFIX}Vídeo processado com sucesso!"
    
    # Testar com diferentes arquivos
    arquivos_teste = [
        "video.mp4",
        "audio.wav",
        "documento.txt"
    ]
    
    for arquivo in arquivos_teste:
        resultado = processar_video(arquivo, AIProvider.GROQ)
        print(f"  {resultado}")
        print()


def main():
    """Executa todas as demonstrações."""
    print("🎯 Demonstração das Constantes Centralizadas do Alfredo AI\n")
    
    demonstrar_constantes_aplicacao()
    demonstrar_constantes_modelos()
    demonstrar_enums()
    demonstrar_timeouts_limites()
    demonstrar_extensoes_arquivo()
    demonstrar_icones_mensagens()
    demonstrar_validacao_url()
    demonstrar_uso_pratico()
    
    print("✨ Benefícios das Constantes Centralizadas:")
    print("  • Eliminação de magic numbers e strings")
    print("  • Facilita manutenção e alterações")
    print("  • Reduz erros de digitação")
    print("  • Melhora legibilidade do código")
    print("  • Permite validação centralizada")
    print("  • Facilita internacionalização")
    print()
    
    print(f"{SUCCESS_PREFIX}Demonstração concluída!")


if __name__ == "__main__":
    main()