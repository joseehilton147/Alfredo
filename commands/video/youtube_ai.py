#!/usr/bin/env python3
"""
🎬 COMANDO: RESUMIR-YOUTUBE
===========================
Comando para baixar vídeos do YouTube e gerar resumo automático com IA
"""

import sys
from pathlib import Path

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "resumir-youtube",
    "description": "🎬 Baixar do YouTube e resumir com IA",
    "function": "main",
    "help": "Download automático de vídeo do YouTube seguido de análise e resumo com IA",
    "version": "0.0.1",
    "author": "Alfredo AI",
    "category": "video"
}

def main():
    """Baixa vídeo do YouTube e gera resumo automático"""
    print("🤖" + "=" * 58 + "🤖")
    print("║" + " " * 18 + "ALFREDO AI - YOUTUBE + IA" + " " * 15 + "║")
    print("║" + " " * 12 + "Download Automático + Resumo Inteligente" + " " * 7 + "║")
    print("║" + " " * 19 + "\"Workflow completo em 1 comando!\"" + " " * 7 + "║")
    print("🤖" + "=" * 58 + "🤖")
    
    print("🤖 Alfredo: Vou baixar o vídeo e criar um resumo completo para você!")
    
    # Solicita URL do vídeo
    url = input("\n🔗 Alfredo: URL do vídeo do YouTube: ").strip()
    if not url:
        print("❌ Alfredo: URL não fornecida")
        return
    
    try:
        # Importa e executa download
        print("\n🎬 ETAPA 1: Download do YouTube")
        print("=" * 40)
        from commands.video.youtube_downloader import download_youtube_video, check_ytdlp, install_ytdlp
        
        # Verifica yt-dlp
        if not check_ytdlp():
            print("📦 Alfredo: Instalando yt-dlp automaticamente...")
            if not install_ytdlp():
                print("❌ Alfredo: Não consegui instalar yt-dlp")
                return
        
        # Baixa o vídeo
        downloaded_video = download_youtube_video(url)
        print(f"✅ Alfredo: Vídeo baixado com sucesso!")
        
        # Importa e executa análise de vídeo
        print("\n🧠 ETAPA 2: Análise com IA")
        print("=" * 40)
        from commands.video.local_video import process_video
        
        # Processa o vídeo baixado
        success = process_video(downloaded_video)
        
        if success:
            print("\n🎊 ALFREDO: WORKFLOW COMPLETO!")
            print("=" * 40)
            print("✅ Download do YouTube: Concluído")
            print("✅ Análise com IA: Concluída")
            print("✅ Resumo gerado: Disponível")
            print(f"📁 Vídeo: {downloaded_video}")
            print(f"📄 Resumo: output/{downloaded_video.stem}.md")
            print("🤖 Alfredo: Workflow completo executado com perfeição!")
        else:
            print("\n❌ ALFREDO: PROBLEMA NA ANÁLISE")
            print("✅ Download: OK")
            print("❌ Análise IA: Falhou")
            print("🤖 Alfredo: O vídeo foi baixado, mas houve problema na análise.")
            
    except Exception as e:
        print(f"\n❌ ALFREDO: ERRO NO WORKFLOW")
        print(f"🤖 Alfredo: Encontrei um problema: {e}")
        print("💡 Dica: Execute 'Alfredo testes' para diagnóstico")

if __name__ == "__main__":
    main()
