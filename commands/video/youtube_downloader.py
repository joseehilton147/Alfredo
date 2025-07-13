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

def download_youtube_video(url: str, output_dir: Path = None) -> Path:
    """
    Baixa video do YouTube na melhor qualidade com audio usando nova estrutura
    Retorna o caminho do arquivo baixado
    """
    if output_dir is None:
        output_dir = paths.INPUT_YOUTUBE
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '--embed-subs',
        '--write-auto-sub',
        '--sub-lang', 'pt,en',
        '--no-playlist',
        '-o', '%(title)s.%(ext)s',
        url
    ]
    # NUNCA imprime nada, suprime todo output
    try:
        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)
        if result.returncode == 0:
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
