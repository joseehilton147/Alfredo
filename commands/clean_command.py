#!/usr/bin/env python3
"""
🧹 COMANDO: LIMPAR
==================
Sistema de limpeza inteligente do Alfredo AI usando nova arquitetura
"""

import os
import shutil
from pathlib import Path
from typing import List

# Importa configuração de caminhos
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.paths import paths

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "limpar",
    "description": "🧹 Limpar arquivos e pastas",
    "function": "main",
    "help": "Sistema de limpeza com diferentes níveis: temp, youtube, resumos ou completa",
    "version": "0.0.1",
    "author": "Alfredo AI",
    "category": "sistema"
}

def get_directory_size(path: Path) -> int:
    """Calcula o tamanho total de um diretório em bytes"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
    except (OSError, FileNotFoundError):
        pass
    return total

def format_size(size_bytes: int) -> str:
    """Formata tamanho em bytes para formato legível"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def scan_data_directory():
    """Analisa o diretório data e retorna estatísticas usando nova estrutura"""
    stats = {
        "cache_frames": {"path": paths.CACHE_FRAMES, "size": 0, "files": 0, "folders": 0},
        "cache_downloads": {"path": paths.CACHE_DOWNLOADS, "size": 0, "files": 0, "folders": 0},
        "input_youtube": {"path": paths.INPUT_YOUTUBE, "size": 0, "files": 0, "folders": 0},
        "summaries_local": {"path": paths.OUTPUT_SUMMARIES_LOCAL, "size": 0, "files": 0, "folders": 0},
        "summaries_youtube": {"path": paths.OUTPUT_SUMMARIES_YOUTUBE, "size": 0, "files": 0, "folders": 0},
        "total": {"size": 0, "files": 0, "folders": 0}
    }
    
    # Analisa cache de frames
    if paths.CACHE_FRAMES.exists():
        stats["cache_frames"]["size"] = get_directory_size(paths.CACHE_FRAMES)
        for item in paths.CACHE_FRAMES.rglob("*"):
            if item.is_file():
                stats["cache_frames"]["files"] += 1
            elif item.is_dir():
                stats["cache_frames"]["folders"] += 1
    
    # Analisa cache de downloads
    if paths.CACHE_DOWNLOADS.exists():
        stats["cache_downloads"]["size"] = get_directory_size(paths.CACHE_DOWNLOADS)
        for item in paths.CACHE_DOWNLOADS.rglob("*"):
            if item.is_file():
                stats["cache_downloads"]["files"] += 1
    
    # Analisa vídeos do YouTube
    if paths.INPUT_YOUTUBE.exists():
        stats["input_youtube"]["size"] = get_directory_size(paths.INPUT_YOUTUBE)
        for item in paths.INPUT_YOUTUBE.rglob("*"):
            if item.is_file():
                stats["input_youtube"]["files"] += 1
    
    # Analisa resumos locais
    if paths.OUTPUT_SUMMARIES_LOCAL.exists():
        for md_file in paths.OUTPUT_SUMMARIES_LOCAL.glob("*.md"):
            if md_file.is_file():
                stats["summaries_local"]["files"] += 1
                stats["summaries_local"]["size"] += md_file.stat().st_size
    
    # Analisa resumos do YouTube
    if paths.OUTPUT_SUMMARIES_YOUTUBE.exists():
        for md_file in paths.OUTPUT_SUMMARIES_YOUTUBE.glob("*.md"):
            if md_file.is_file():
                stats["summaries_youtube"]["files"] += 1
                stats["summaries_youtube"]["size"] += md_file.stat().st_size
    
    # Calcula totais
    for category in ["cache_frames", "cache_downloads", "input_youtube", "summaries_local", "summaries_youtube"]:
        stats["total"]["size"] += stats[category]["size"]
        stats["total"]["files"] += stats[category]["files"]
        stats["total"]["folders"] += stats[category]["folders"]
    
    return stats

def clean_temp_files():
    """Remove arquivos temporários (frames)"""
    temp_dir = Path("output") / "temp"
    
    if not temp_dir.exists():
        print("📁 Alfredo: Pasta temp não existe - nada para limpar")
        return 0, 0
    
    size_before = get_directory_size(temp_dir)
    files_removed = 0
    folders_removed = 0
    
    try:
        for item in temp_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                folders_removed += 1
                print(f"🗂️ Removido: {item.name}/")
            else:
                files_removed += 1
                item.unlink()
                print(f"📄 Removido: {item.name}")
        
        print(f"✅ Alfredo: {files_removed} arquivos e {folders_removed} pastas removidos")
        return size_before, files_removed + folders_removed
        
    except Exception as e:
        print(f"❌ Alfredo: Erro na limpeza temp: {e}")
        return 0, 0

def clean_youtube_files():
    """Remove vídeos baixados do YouTube"""
    youtube_dir = Path("output") / "youtube"
    
    if not youtube_dir.exists():
        print("📁 Alfredo: Pasta youtube não existe - nada para limpar")
        return 0, 0
    
    size_before = get_directory_size(youtube_dir)
    files_removed = 0
    
    try:
        for video_file in youtube_dir.iterdir():
            if video_file.is_file():
                file_size = video_file.stat().st_size
                video_file.unlink()
                files_removed += 1
                print(f"🎬 Removido: {video_file.name} ({format_size(file_size)})")
        
        print(f"✅ Alfredo: {files_removed} vídeos removidos")
        return size_before, files_removed
        
    except Exception as e:
        print(f"❌ Alfredo: Erro na limpeza youtube: {e}")
        return 0, 0

def clean_resume_files():
    """Remove arquivos de resumo (.md)"""
    output_dir = Path("output")
    
    if not output_dir.exists():
        print("📁 Alfredo: Pasta output não existe - nada para limpar")
        return 0, 0
    
    files_removed = 0
    size_removed = 0
    
    try:
        for md_file in output_dir.glob("*.md"):
            if md_file.is_file():
                file_size = md_file.stat().st_size
                md_file.unlink()
                files_removed += 1
                size_removed += file_size
                print(f"📄 Removido: {md_file.name}")
        
        print(f"✅ Alfredo: {files_removed} resumos removidos")
        return size_removed, files_removed
        
    except Exception as e:
        print(f"❌ Alfredo: Erro na limpeza resumos: {e}")
        return 0, 0

def clean_all():
    """Limpeza completa - remove tudo"""
    output_dir = Path("output")
    
    if not output_dir.exists():
        print("📁 Alfredo: Pasta output não existe - nada para limpar")
        return 0, 0
    
    size_before = get_directory_size(output_dir)
    
    try:
        # Remove todo o conteúdo mas mantém a pasta output
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                print(f"🗂️ Removido: {item.name}/")
            else:
                item.unlink()
                print(f"📄 Removido: {item.name}")
        
        print(f"✅ Alfredo: Limpeza completa realizada")
        return size_before, 0  # Retorna tamanho removido
        
    except Exception as e:
        print(f"❌ Alfredo: Erro na limpeza completa: {e}")
        return 0, 0

def main():
    """Sistema de limpeza inteligente"""
    print("🤖" + "=" * 50 + "🤖")
    print("║" + " " * 18 + "ALFREDO AI - LIMPEZA" + " " * 12 + "║")
    print("║" + " " * 16 + "Sistema de Limpeza Inteligente" + " " * 5 + "║")
    print("║" + " " * 17 + "\"Organização é fundamental!\"" + " " * 6 + "║")
    print("🤖" + "=" * 50 + "🤖")
    
    print("🤖 Alfredo: Vou analisar o que temos para limpar...")
    
    # Analisa diretório atual
    stats = scan_data_directory()
    
    if stats is None:
        print("📁 Alfredo: Estrutura de dados não existe - nada para limpar!")
        return
    
    if stats["total"]["size"] == 0:
        print("✨ Alfredo: Tudo já está limpo! Nada para remover.")
        return
    
    # Mostra estatísticas
    print(f"\n📊 ANÁLISE DO DIRETÓRIO OUTPUT:")
    print("=" * 40)
    print(f"🗂️ Arquivos temporários: {stats['temp']['files']} arquivos, {stats['temp']['folders']} pastas ({format_size(stats['temp']['size'])})")
    print(f"🎬 Vídeos YouTube: {stats['youtube']['files']} vídeos ({format_size(stats['youtube']['size'])})")
    print(f"📄 Resumos: {stats['resumos']['files']} arquivos .md ({format_size(stats['resumos']['size'])})")
    print(f"📦 TOTAL: {format_size(stats['total']['size'])}")
    
    # Menu de opções
    print(f"\n🧹 OPÇÕES DE LIMPEZA:")
    print("=" * 40)
    print("  [1] 🗂️  Limpar apenas arquivos temporários (frames)")
    print("  [2] 🎬 Limpar apenas vídeos do YouTube")
    print("  [3] 📄 Limpar apenas resumos (.md)")
    print("  [4] 🧹 Limpeza completa (tudo)")
    print("  [5] 📊 Apenas analisar (não remover nada)")
    print("  [q] ❌ Cancelar")
    
    while True:
        try:
            choice = input(f"\n🤖 Alfredo: Que tipo de limpeza deseja? (1-5, q): ").strip().lower()
            
            if choice in ['q', 'quit', 'cancelar', 'sair']:
                print("👋 Alfredo: Limpeza cancelada!")
                return
            elif choice == '1':
                print(f"\n🗂️ LIMPEZA: Arquivos Temporários")
                print("=" * 35)
                size_removed, items_removed = clean_temp_files()
                if size_removed > 0:
                    print(f"💾 Espaço liberado: {format_size(size_removed)}")
                break
            elif choice == '2':
                print(f"\n🎬 LIMPEZA: Vídeos YouTube")
                print("=" * 30)
                size_removed, items_removed = clean_youtube_files()
                if size_removed > 0:
                    print(f"💾 Espaço liberado: {format_size(size_removed)}")
                break
            elif choice == '3':
                print(f"\n📄 LIMPEZA: Resumos")
                print("=" * 25)
                size_removed, items_removed = clean_resume_files()
                if size_removed > 0:
                    print(f"💾 Espaço liberado: {format_size(size_removed)}")
                break
            elif choice == '4':
                print(f"\n🧹 LIMPEZA COMPLETA")
                print("=" * 25)
                confirm = input("⚠️ Alfredo: Tem certeza? Isso removerá TUDO! (s/N): ").strip().lower()
                if confirm in ['s', 'sim', 'y', 'yes']:
                    size_removed, _ = clean_all()
                    if size_removed > 0:
                        print(f"💾 Espaço liberado: {format_size(size_removed)}")
                else:
                    print("🤖 Alfredo: Limpeza completa cancelada.")
                break
            elif choice == '5':
                print(f"\n📊 ANÁLISE CONCLUÍDA")
                print("=" * 25)
                print("🤖 Alfredo: Análise mostrada acima. Nenhum arquivo removido.")
                break
            else:
                print("❌ Opção inválida! Digite 1-5 ou 'q'")
                
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Alfredo: Limpeza cancelada!")
            return
    
    print(f"\n🎉 ALFREDO: LIMPEZA CONCLUÍDA!")
    print("🤖 Alfredo: Sistema organizado e pronto para uso!")

if __name__ == "__main__":
    main()
