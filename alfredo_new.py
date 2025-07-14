#!/usr/bin/env python3
"""
🤖 ALFREDO AI - New Architecture Entry Point
============================================
Modern entry point using the new modular architecture
"""

import sys
from pathlib import Path

def main():
    """Main entry point with new architecture"""
    from config.settings import config
    from config.i18n import t
    from cli.alfredo import main as cli_main
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Run CLI
    cli_main()

if __name__ == "__main__":
    main()
