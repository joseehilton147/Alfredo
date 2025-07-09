#!/usr/bin/env python3
"""
📁 COMANDO: ORGANIZAR-ARQUIVOS
==============================
Comando para organizar arquivos da pasta atual por tipo
"""

import os
import shutil
from pathlib import Path

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "organizar-arquivos",
    "description": "📁 Organizar arquivos por tipo",
    "function": "main",
    "help": "Organiza arquivos da pasta atual criando subpastas por categoria (Imagens, Vídeos, etc.)",
    "version": "0.0.1",
    "author": "Alfredo AI"
}

def main():
    """Organiza arquivos da pasta atual por tipo"""
    print("📁 Organizando arquivos da pasta atual...")
    
    current_dir = Path.cwd()
    
    # Tipos de arquivo e suas pastas
    file_types = {
        'Imagens': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'Videos': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
        'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'Planilhas': ['.xls', '.xlsx', '.csv'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'Compactados': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Codigo': ['.py', '.js', '.html', '.css', '.java', '.cpp']
    }
    
    moved_files = 0
    
    for file_path in current_dir.iterdir():
        if file_path.is_file():
            extension = file_path.suffix.lower()
            
            for folder_name, extensions in file_types.items():
                if extension in extensions:
                    # Cria pasta se não existir
                    target_folder = current_dir / folder_name
                    target_folder.mkdir(exist_ok=True)
                    
                    # Move arquivo
                    target_path = target_folder / file_path.name
                    try:
                        shutil.move(str(file_path), str(target_path))
                        print(f"  📄 {file_path.name} → {folder_name}/")
                        moved_files += 1
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {file_path.name}: {e}")
                    break
    
    print(f"\n✅ Organização concluída!")
    print(f"📊 {moved_files} arquivo(s) organizados")

if __name__ == "__main__":
    main()
