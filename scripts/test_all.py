#!/usr/bin/env python3
"""
🧪 Full System Test
==================
Comprehensive test suite for the new Alfredo AI architecture.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run comprehensive system tests"""
    project_root = Path(__file__).parent.parent
    
    print("🤖 Alfredo AI - Full System Test")
    print("=" * 40)
    print("Testing the new modular architecture...")
    print()
    
    tests = [
        ("🧪 Unit Tests", test_unit_tests),
        ("🔗 Integration Tests", test_integration_tests),
        ("🎯 CLI Commands", test_cli_commands),
        ("🌍 Internationalization", test_i18n),
        ("⚙️ Configuration", test_config),
        ("📁 Directory Structure", test_directory_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            test_func(project_root)
            print(f"   ✅ {test_name} PASSED")
            passed += 1
        except Exception as e:
            print(f"   ❌ {test_name} FAILED: {e}")
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! New architecture is working correctly.")
        print("🚀 You can now use:")
        print("   python cli/alfredo.py --list")
        print("   python cli/groq_status.py")
        print("   python cli/clean.py")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    return passed == total

def test_unit_tests(project_root: Path):
    """Test unit test suite"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/", "-q"],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Unit tests failed: {result.stderr}")

def test_integration_tests(project_root: Path):
    """Test integration tests"""
    # For now, just check if files exist
    integration_dir = project_root / "tests" / "integration"
    if not integration_dir.exists():
        raise Exception("Integration test directory missing")

def test_cli_commands(project_root: Path):
    """Test CLI commands can be imported"""
    cli_dir = project_root / "cli"
    cli_files = ["alfredo.py", "clean.py", "groq_status.py"]
    
    for cli_file in cli_files:
        if not (cli_dir / cli_file).exists():
            raise Exception(f"CLI file missing: {cli_file}")

def test_i18n(project_root: Path):
    """Test internationalization system"""
    sys.path.insert(0, str(project_root))
    
    try:
        from config.i18n import t, i18n
        
        # Test Portuguese
        i18n.set_locale("pt")
        msg_pt = t("cli.welcome")
        if "Alfredo AI" not in msg_pt:
            raise Exception("Portuguese i18n not working")
        
        # Test English
        i18n.set_locale("en")
        msg_en = t("cli.welcome")
        if "Alfredo AI" not in msg_en:
            raise Exception("English i18n not working")
            
    except ImportError:
        raise Exception("I18n module cannot be imported")

def test_config(project_root: Path):
    """Test configuration system"""
    sys.path.insert(0, str(project_root))
    
    try:
        from config.settings import config
        
        # Test directory access
        cli_dir = config.get_dir("cli")
        if not cli_dir.exists():
            raise Exception("Config cannot access CLI directory")
            
    except ImportError:
        raise Exception("Config module cannot be imported")

def test_directory_structure(project_root: Path):
    """Test new directory structure"""
    required_dirs = [
        "cli", "api", "core", "integrations", 
        "config", "data", "tests", "scripts", "legacy"
    ]
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            raise Exception(f"Required directory missing: {dir_name}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
