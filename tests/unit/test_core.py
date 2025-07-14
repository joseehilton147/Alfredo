#!/usr/bin/env python3
"""
🧪 Unit Tests for Core System
==============================
Test suite for core Alfredo AI functionality.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.alfredo_core import AlfredoCore

class TestAlfredoCore(unittest.TestCase):
    """Test cases for AlfredoCore class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.alfredo = AlfredoCore()
    
    def test_core_initialization(self):
        """Test that core system initializes properly"""
        self.assertIsInstance(self.alfredo, AlfredoCore)
        self.assertTrue(hasattr(self.alfredo, 'commands'))
        self.assertGreater(len(self.alfredo.commands), 0)
    
    def test_command_loading(self):
        """Test that commands are loaded correctly"""
        self.assertIn('limpar', self.alfredo.commands)
        self.assertIn('groq-status', self.alfredo.commands)
    
    def test_banner_display(self):
        """Test banner display functionality"""
        try:
            self.alfredo.show_banner()
        except Exception as e:
            self.fail(f"Banner display failed: {e}")

class TestIntegrations(unittest.TestCase):
    """Test cases for integrations"""
    
    def test_groq_import(self):
        """Test Groq integration imports"""
        try:
            from integrations.groq import provider, monitor
        except ImportError as e:
            self.fail(f"Groq integration import failed: {e}")
    
    def test_groq_import(self):
        """Test Groq integration imports"""
        try:
            from integrations.groq import provider
        except ImportError as e:
            self.fail(f"Groq integration import failed: {e}")

if __name__ == '__main__':
    unittest.main()
