#!/usr/bin/env python3
"""
📥 COMANDO: BAIXAR-VIDEO YOUTUBE
================================
Comando para baixar vídeos do YouTube usando nova arquitetura
"""

import subprocess
import sys
import os
from pathlib import Path

# Importa configuração de caminhos
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.paths import paths

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "baixar-video",
    "description": "📥 Baixar vídeos do YouTube",
    "function": "main",
    "help": "Download de vídeos do YouTube na melhor qualidade com áudio usando yt-dlp",
    "version": "0.0.1",
    "author": "Alfredo AI",
    "category": "video"
}

def check_ytdlp():
    """Verifica se yt-dlp está instalado"""
    try:
        # Verifica se yt-dlp está disponível
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'yt-dlp'], 
                              capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ytdlp():
    """Instala yt-dlp"""
    print("📦 Instalando yt-dlp...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], check=True)
        print("✅ yt-dlp instalado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar yt-dlp")
        return False

def extract_video_id(url: str) -> str:
    """Extrai o video_id da URL do YouTube"""
    import re
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("ID do vídeo não encontrado na URL fornecida.")

def download_youtube_video(url: str, output_dir: Path = None, output_filename: str = None) -> Path:
    """
    Baixa video do YouTube na melhor qualidade com audio usando nova estrutura
    Retorna o caminho do arquivo baixado
    """
    if output_dir is None:
        output_dir = paths.INPUT_YOUTUBE
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_filename is None:
        # fallback para título, mas o ideal é sempre passar o video_id
        output_filename = '%(id)s.%(ext)s'
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '--embed-subs',
        '--write-auto-sub',
        '--sub-lang', 'pt,en',
        '--no-playlist',
        '-o', output_filename,
        url
    ]
    # NUNCA imprime nada, suprime todo output
    try:
        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)
        if result.returncode == 0:
            # Busca pelo nome exato
            if '%(id)s' in output_filename or output_filename.endswith('.mp4'):
                # Se output_filename é um nome fixo
                expected_file = output_dir / output_filename.replace('%(id)s', extract_video_id(url)).replace('%(ext)s', 'mp4')
                if expected_file.exists():
                    return expected_file
            # fallback: retorna o arquivo mp4 mais recente
            video_files = list(output_dir.glob('*.mp4'))
            if video_files:
                latest_file = max(video_files, key=lambda f: f.stat().st_mtime)
                return latest_file
            else:
                raise Exception('Arquivo de video nao encontrado apos download')
        else:
            error_msg = result.stderr or result.stdout or 'Erro desconhecido'
            # Remove qualquer caractere Unicode do erro
            import re
            error_msg = re.sub(r'[^\x20-\x7E]+', '', error_msg)
            raise Exception(f'Erro no download: {error_msg}')
    except Exception as e:
        # Remove qualquer caractere Unicode do erro
        import re
        msg = re.sub(r'[^\x20-\x7E]+', '', str(e))
        raise Exception(msg)

def main():
    """Baixa vídeos do YouTube na melhor qualidade"""
    print("🤖" + "=" * 48 + "🤖")
    print("║" + " " * 16 + "ALFREDO AI - DOWNLOADER" + " " * 9 + "║")
    print("║" + " " * 12 + "Download YouTube na Melhor Qualidade" + " " * 1 + "║")
    print("🤖" + "=" * 48 + "🤖")
    
    # Verifica se yt-dlp está instalado
    if not check_ytdlp():
        print("⚠️ Alfredo: yt-dlp não encontrado!")
        install = input("🤖 Alfredo: Posso instalar para você? (s/N): ").lower()
        if install in ['s', 'sim', 'y', 'yes']:
            if not install_ytdlp():
                return
        else:
            print("❌ Alfredo: yt-dlp é necessário para este comando")
            return
    
    # Solicita URL do vídeo
    url = input("\n🔗 Alfredo: URL do vídeo do YouTube: ").strip()
    if not url:
        print("❌ Alfredo: URL não fornecida")
        return
    
    try:
        downloaded_file = download_youtube_video(url)
        print(f"\n🎉 ALFREDO: DOWNLOAD CONCLUÍDO!")
        print(f"🎬 Arquivo: {downloaded_file.name}")
        print("🔊 Qualidade: Melhor disponível com áudio")
        print("🤖 Alfredo: Pronto para análise ou uso!")
        
    except Exception as e:
        print(f"❌ Alfredo: Falha no download: {e}")

if __name__ == "__main__":
    main()
