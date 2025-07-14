#!/usr/bin/env python3
"""
🧹 CLI Command: Clean
=====================
Intelligent cleaning system for Alfredo AI cache and data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.clean_command import main

if __name__ == "__main__":
    main()
