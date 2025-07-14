#!/usr/bin/env python3
"""
📹 CLI Command: YouTube AI
==========================
Download and analyze YouTube videos with AI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.video.youtube_ai import main

if __name__ == "__main__":
    main()
