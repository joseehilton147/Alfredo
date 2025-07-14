#!/usr/bin/env python3
"""
🔍 CLI Command: Groq Status
===========================
Check Groq API status and rate limits.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.groq_status import main

if __name__ == "__main__":
    main()
