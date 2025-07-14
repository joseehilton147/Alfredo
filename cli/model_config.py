#!/usr/bin/env python3
"""
🧠 CLI Command: Model Config
============================
Configure AI models automatically.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.model_config_command import main

if __name__ == "__main__":
    main()
