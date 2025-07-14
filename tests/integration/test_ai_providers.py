#!/usr/bin/env python3
"""
🔄 Integration Tests
====================
End-to-end tests for Alfredo AI integrations.
"""

import sys
import unittest
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestGroqIntegration(unittest.TestCase):
    """Test Groq API integration"""
    
    def test_groq_api_connection(self):
        """Test basic Groq API connectivity"""
        # This would be a real integration test
        # For now, just check if the modules can be imported
        try:
            from integrations.groq.provider import GroqProvider
            from integrations.groq.monitor import groq_monitor
        except ImportError as e:
            self.fail(f"Groq integration modules not found: {e}")

class TestOllamaIntegration(unittest.TestCase):
    """Test Ollama integration"""
    
    def test_ollama_connection(self):
        """Test Ollama local server connection"""
        try:
            response = requests.get("http://127.0.0.1:11434", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.RequestException:
            self.skipTest("Ollama server not running")

if __name__ == '__main__':
    unittest.main()
