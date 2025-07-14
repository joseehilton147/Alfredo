#!/usr/bin/env python3
"""
⚙️ Global Configuration
=======================
Global settings and configuration for Alfredo AI.
"""

import os
from pathlib import Path
from typing import Dict, Any

class AlfredoConfig:
    """Global configuration manager for Alfredo AI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.default_locale = "pt"
        self.current_locale = self._detect_locale()
        
        # Directory structure
        self.dirs = {
            'cli': self.project_root / 'cli',
            'api': self.project_root / 'api', 
            'core': self.project_root / 'core',
            'integrations': self.project_root / 'integrations',
            'config': self.project_root / 'config',
            'data': self.project_root / 'data',
            'tests': self.project_root / 'tests',
            'scripts': self.project_root / 'scripts',
            'legacy': self.project_root / 'legacy'
        }
        
        # Command mappings for backward compatibility
        self.legacy_command_mappings = {
            'resumir-video-local': 'cli.video_local',
            'resumir-audio-local': 'cli.audio_analyzer',
            'resumir-yt': 'cli.youtube_ai',
            'baixar-yt': 'cli.youtube_downloader',
            'limpar-cache': 'cli.clean',
            'limpar': 'cli.clean',
            'groq-status': 'cli.groq_status',
            'info-pc': 'cli.pc_info',
            'configurar-modelos': 'cli.model_config',
            'testes': 'cli.test_runner'
        }
        
        # AI Provider settings
        self.ai_providers = {
            'default': 'ollama',
            'groq': {
                'enabled': True,
                'rate_limit_check': True
            },
            'ollama': {
                'enabled': True,
                'host': 'http://127.0.0.1:11434'
            }
        }
    
    def _detect_locale(self) -> str:
        """Detect system locale or use default"""
        system_locale = os.environ.get('LANG', '').lower()
        if 'pt' in system_locale or 'br' in system_locale:
            return 'pt'
        elif 'en' in system_locale:
            return 'en'
        return self.default_locale
    
    def get_dir(self, name: str) -> Path:
        """Get directory path by name"""
        return self.dirs.get(name, self.project_root)
    
    def get_command_module(self, command: str) -> str:
        """Get module path for legacy command"""
        return self.legacy_command_mappings.get(command)
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

# Global configuration instance
config = AlfredoConfig()
