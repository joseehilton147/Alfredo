#!/usr/bin/env python3
"""Teste básico para verificar a estrutura do projeto Alfredo AI."""

import os
import sys
from pathlib import Path


def check_structure():
    """Verifica se a estrutura do projeto está correta."""
    print("🔍 Verificando estrutura do Alfredo AI...")
    
    # Diretórios obrigatórios
    required_dirs = [
        "src",
        "src/application",
        "src/application/use_cases",
        "src/domain",
        "src/domain/entities",
        "src/domain/repositories",
        "src/infrastructure",
        "src/infrastructure/providers",
        "src/infrastructure/repositories",
        "data",
        "data/input/local",
        "data/input/youtube",
        "data/output",
        "data/logs",
        "data/temp",
        "tests",
        "examples",
    ]
    
    # Arquivos obrigatórios
    required_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "setup.py",
        "README.md",
        "INSTALL.md",
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
    ]
    
    missing_dirs = []
    missing_files = []
    
    # Verificar diretórios
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
            print(f"❌ Diretório ausente: {dir_path}")
        else:
            print(f"✅ Diretório encontrado: {dir_path}")
    
    # Verificar arquivos
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ Arquivo ausente: {file_path}")
        else:
            print(f"✅ Arquivo encontrado: {file_path}")
    
    return missing_dirs, missing_files


def check_dependencies():
    """Verifica se as dependências principais estão instaladas."""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        "groq",
        "pydantic",
        "python-dotenv",
        "requests",
        "yt-dlp",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} instalado")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} não encontrado")
    
    return missing_packages


def check_ffmpeg():
    """Verifica se o FFmpeg está instalado."""
    print("\n🎬 Verificando FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ FFmpeg está instalado")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg não está instalado ou não está no PATH")
        return False


def main():
    """Função principal de verificação."""
    print("🤖 Alfredo AI - Verificação de Instalação")
    print("=" * 50)
    
    # Verificar estrutura
    missing_dirs, missing_files = check_structure()
    
    # Verificar dependências
    missing_packages = check_dependencies()
    
    # Verificar FFmpeg
    ffmpeg_ok = check_ffmpeg()
    
    # Resumo
    print("\n📊 Resumo da verificação:")
    print("=" * 30)
    
    if not missing_dirs and not missing_files and not missing_packages and ffmpeg_ok:
        print("🎉 Tudo pronto! Alfredo AI está configurado corretamente.")
        print("\nPróximos passos:")
        print("1. Configure sua chave de API no arquivo .env")
        print("2. Coloque vídeos em data/input/local/")
        print("3. Execute: python -m src.main -i data/input/local/seu_video.mp4")
        return 0
    else:
        print("\n❌ Existem problemas na configuração:")
        
        if missing_dirs:
            print(f"  - Diretórios ausentes: {', '.join(missing_dirs)}")
        
        if missing_files:
            print(f"  - Arquivos ausentes: {', '.join(missing_files)}")
        
        if missing_packages:
            print(f"  - Pacotes não instalados: {', '.join(missing_packages)}")
        
        if not ffmpeg_ok:
            print("  - FFmpeg não está instalado")
        
        print("\nConsulte INSTALL.md para instruções de instalação.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
