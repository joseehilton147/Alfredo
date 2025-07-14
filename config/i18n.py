#!/usr/bin/env python3
"""
🌍 Internationalization Service
===============================
Manages localization and language support for Alfredo AI.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class I18nService:
    """Internationalization service for multi-language support"""
    
    def __init__(self, default_locale: str = "pt"):
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.config_root = Path(__file__).parent.parent / "config"
        self._messages = {}
        self._load_messages()
    
    def _load_messages(self):
        """Load messages for current locale"""
        locale_path = self.config_root / "locales" / self.current_locale / "messages.json"
        
        if locale_path.exists():
            with open(locale_path, 'r', encoding='utf-8') as f:
                self._messages = json.load(f)
        else:
            # Fallback to default locale
            fallback_path = self.config_root / "locales" / self.default_locale / "messages.json"
            if fallback_path.exists():
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    self._messages = json.load(f)
    
    def set_locale(self, locale: str):
        """Set current locale and reload messages"""
        self.current_locale = locale
        self._load_messages()
    
    def get_message(self, key_path: str, **kwargs) -> str:
        """
        Get localized message by key path (e.g., 'cli.welcome')
        Supports variable substitution with kwargs
        """
        keys = key_path.split('.')
        message = self._messages
        
        try:
            for key in keys:
                message = message[key]
            
            # Format with provided kwargs
            if kwargs:
                return message.format(**kwargs)
            return message
            
        except (KeyError, TypeError):
            # Return key path if message not found
            return f"[{key_path}]"
    
    def get_available_locales(self) -> list:
        """Get list of available locales"""
        locales_dir = self.config_root / "locales"
        if locales_dir.exists():
            return [d.name for d in locales_dir.iterdir() if d.is_dir()]
        return []

# Global instance
i18n = I18nService()

def t(key_path: str, **kwargs) -> str:
    """Shorthand function for getting translated messages"""
    return i18n.get_message(key_path, **kwargs)
