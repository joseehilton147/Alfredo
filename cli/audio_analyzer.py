#!/usr/bin/env python3
"""
🎧 CLI Command: Audio Analyzer
==============================
Analyze audio files with speech-to-text AI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.video.audio_analyzer import main

if __name__ == "__main__":
    main()
