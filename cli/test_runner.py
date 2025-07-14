#!/usr/bin/env python3
"""
🧪 CLI Command: Test Runner
===========================
Run comprehensive system tests.
"""

import sys
from pathlib import Path

from commands.test_runner import main

if __name__ == "__main__":
    main()

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.test_runner import main

if __name__ == "__main__":
    main()
