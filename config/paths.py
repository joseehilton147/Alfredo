#!/usr/bin/env python3
"""
📁 ALFREDO AI - CONFIGURAÇÃO DE CAMINHOS
=========================================
Centraliza todos os caminhos do sistema seguindo padrões enterprise
"""

from pathlib import Path
from typing import Dict, Any
import os

class AlfredoPaths:
    """Gerenciador centralizado de caminhos do sistema"""
    
    def __init__(self):
        # Diretório raiz do projeto
        self.PROJECT_ROOT = Path(__file__).parent.parent
        
        # Estrutura de dados principal
        self.DATA_ROOT = self.PROJECT_ROOT / "data"
        
        # === ENTRADA (INPUT) ===
        self.INPUT_ROOT = self.DATA_ROOT / "input"
        self.INPUT_LOCAL = self.INPUT_ROOT / "local"          # Vídeos locais
        self.INPUT_YOUTUBE = self.INPUT_ROOT / "youtube"      # Vídeos baixados do YouTube
        
        # === SAÍDA (OUTPUT) ===
        self.OUTPUT_ROOT = self.DATA_ROOT / "output"
        self.OUTPUT_SUMMARIES = self.OUTPUT_ROOT / "summaries"
        self.OUTPUT_SUMMARIES_LOCAL = self.OUTPUT_SUMMARIES / "local"      # Resumos de vídeos locais
        self.OUTPUT_SUMMARIES_YOUTUBE = self.OUTPUT_SUMMARIES / "youtube"  # Resumos de vídeos do YouTube
        
        # === CACHE/TEMPORÁRIOS ===
        self.CACHE_ROOT = self.DATA_ROOT / "cache"
        self.CACHE_FRAMES = self.CACHE_ROOT / "frames"        # Frames extraídos temporariamente
        self.CACHE_DOWNLOADS = self.CACHE_ROOT / "downloads"  # Downloads temporários
        
        # === TESTES ===
        self.TESTS_ROOT = self.PROJECT_ROOT / "tests"
        self.TESTS_FIXTURES = self.TESTS_ROOT / "fixtures"
        self.TESTS_FIXTURES_VIDEOS = self.TESTS_FIXTURES / "videos"
        self.TESTS_UNIT = self.TESTS_ROOT / "unit"
        self.TESTS_INTEGRATION = self.TESTS_ROOT / "integration"
        
        # === CONFIGURAÇÃO ===
        self.CONFIG_ROOT = self.PROJECT_ROOT / "config"
        self.PROMPTS_DIR = self.CONFIG_ROOT / "prompts"
        
        # === COMANDOS E NÚCLEO ===
        self.COMMANDS_ROOT = self.PROJECT_ROOT / "commands"
        self.CORE_ROOT = self.PROJECT_ROOT / "core"
        
        # === ARQUIVOS DE CONFIGURAÇÃO ===
        self.ENV_FILE = self.PROJECT_ROOT / ".env"
        self.ENV_EXAMPLE = self.PROJECT_ROOT / ".env.example"
        self.REQUIREMENTS = self.PROJECT_ROOT / "requirements.txt"
        
        # === PATHS LEGADOS (para migração) ===
        self.LEGACY_OUTPUT = self.PROJECT_ROOT / "output"
        self.LEGACY_TEMP = self.PROJECT_ROOT / "temp"
    
    def ensure_directories(self):
        """Cria todas as pastas necessárias"""
        directories = [
            self.DATA_ROOT,
            self.INPUT_ROOT, self.INPUT_LOCAL, self.INPUT_YOUTUBE,
            self.OUTPUT_ROOT, self.OUTPUT_SUMMARIES, self.OUTPUT_SUMMARIES_LOCAL, self.OUTPUT_SUMMARIES_YOUTUBE,
            self.CACHE_ROOT, self.CACHE_FRAMES, self.CACHE_DOWNLOADS,
            self.TESTS_ROOT, self.TESTS_FIXTURES, self.TESTS_FIXTURES_VIDEOS,
            self.TESTS_UNIT, self.TESTS_INTEGRATION,
            self.CONFIG_ROOT
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_cache_frames_path(self, video_name: str) -> Path:
        """Retorna caminho para frames de um vídeo específico"""
        return self.CACHE_FRAMES / video_name
    
    def get_output_summary_path(self, video_name: str, source: str = "local") -> Path:
        """Retorna caminho para resumo de um vídeo específico"""
        if source == "youtube":
            return self.OUTPUT_SUMMARIES_YOUTUBE / f"{video_name}.md"
        elif source == "audio":
            # Criar pasta de áudio se não existir
            audio_dir = self.OUTPUT_SUMMARIES / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            return audio_dir / f"{video_name}.md"
        else:
            return self.OUTPUT_SUMMARIES_LOCAL / f"{video_name}.md"
    
    def get_video_input_path(self, source: str = "local") -> Path:
        """Retorna diretório de entrada para vídeos"""
        if source == "youtube":
            return self.INPUT_YOUTUBE
        else:
            return self.INPUT_LOCAL
    
    def migrate_legacy_files(self):
        """Migra arquivos das pastas antigas para nova estrutura"""
        import shutil
        
        migrations = []
        
        # Migra pasta output/youtube para data/input/youtube
        if self.LEGACY_OUTPUT.exists():
            legacy_youtube = self.LEGACY_OUTPUT / "youtube"
            if legacy_youtube.exists():
                for video_file in legacy_youtube.iterdir():
                    if video_file.is_file():
                        target = self.INPUT_YOUTUBE / video_file.name
                        if not target.exists():
                            shutil.move(str(video_file), str(target))
                            migrations.append(f"📹 {video_file.name} → data/input/youtube/")
            
            # Migra resumos .md para data/output/summaries/local
            for md_file in self.LEGACY_OUTPUT.glob("*.md"):
                target = self.OUTPUT_SUMMARIES_LOCAL / md_file.name
                if not target.exists():
                    shutil.move(str(md_file), str(target))
                    migrations.append(f"📄 {md_file.name} → data/output/summaries/local/")
        
        # Migra pasta temp para data/cache/frames
        if self.LEGACY_TEMP.exists():
            for temp_dir in self.LEGACY_TEMP.iterdir():
                if temp_dir.is_dir():
                    target = self.CACHE_FRAMES / temp_dir.name
                    if not target.exists():
                        shutil.move(str(temp_dir), str(target))
                        migrations.append(f"🗂️ {temp_dir.name}/ → data/cache/frames/")
        
        return migrations
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos diretórios"""
        def get_dir_size(path: Path) -> int:
            if not path.exists():
                return 0
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
            return total
        
        def count_files(path: Path, pattern: str = "*") -> int:
            if not path.exists():
                return 0
            return len(list(path.rglob(pattern)))
        
        return {
            "input": {
                "local": {"files": count_files(self.INPUT_LOCAL), "size": get_dir_size(self.INPUT_LOCAL)},
                "youtube": {"files": count_files(self.INPUT_YOUTUBE), "size": get_dir_size(self.INPUT_YOUTUBE)}
            },
            "output": {
                "summaries_local": {"files": count_files(self.OUTPUT_SUMMARIES_LOCAL, "*.md"), "size": get_dir_size(self.OUTPUT_SUMMARIES_LOCAL)},
                "summaries_youtube": {"files": count_files(self.OUTPUT_SUMMARIES_YOUTUBE, "*.md"), "size": get_dir_size(self.OUTPUT_SUMMARIES_YOUTUBE)}
            },
            "cache": {
                "frames": {"dirs": len(list(self.CACHE_FRAMES.iterdir())) if self.CACHE_FRAMES.exists() else 0, "size": get_dir_size(self.CACHE_FRAMES)},
                "downloads": {"files": count_files(self.CACHE_DOWNLOADS), "size": get_dir_size(self.CACHE_DOWNLOADS)}
            }
        }

# Instância global dos caminhos
paths = AlfredoPaths()

# Criar diretórios na importação
paths.ensure_directories()
