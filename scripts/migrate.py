#!/usr/bin/env python3
"""
🔄 Migration Script
===================
Script to help migrate from old structure to new modular architecture.
"""

import shutil
import sys
from pathlib import Path

def main():
    """Run migration from old to new structure"""
    project_root = Path(__file__).parent.parent
    
    print("🤖 Alfredo AI - Migration Script")
    print("=" * 40)
    print("This script helps migrate from the old structure to the new modular architecture.")
    print()
    
    # Check if old structure exists
    old_files = [
        project_root / "Alfredo.py",
        project_root / "commands",
        project_root / "services"
    ]
    
    missing_files = [f for f in old_files if not f.exists()]
    
    if missing_files:
        print("❌ Migration already completed or old files not found:")
        for f in missing_files:
            print(f"   - {f}")
        print()
        print("✅ New structure is already in place!")
        return
    
    print("🔍 Old structure detected. Migration options:")
    print()
    print("1. 🔄 Complete migration (move old files to legacy/)")
    print("2. 📋 Show migration status only")
    print("3. ❌ Cancel")
    print()
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        migrate_to_legacy(project_root)
    elif choice == "2":
        show_migration_status(project_root)
    else:
        print("👋 Migration cancelled")

def migrate_to_legacy(project_root: Path):
    """Move old files to legacy directory"""
    legacy_dir = project_root / "legacy"
    legacy_dir.mkdir(exist_ok=True)
    
    files_to_move = [
        ("Alfredo.py", "legacy/Alfredo_old.py"),
        ("Alfredo_testes.py", "legacy/Alfredo_testes.py"),
        ("install.py", "legacy/install_old.py")
    ]
    
    dirs_to_move = [
        ("services", "legacy/services_old"),
    ]
    
    print("🔄 Moving files to legacy directory...")
    
    # Move files
    for old_file, new_location in files_to_move:
        old_path = project_root / old_file
        new_path = project_root / new_location
        
        if old_path.exists() and not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"   ✅ Moved {old_file} -> {new_location}")
    
    # Move directories
    for old_dir, new_location in dirs_to_move:
        old_path = project_root / old_dir
        new_path = project_root / new_location
        
        if old_path.exists() and not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"   ✅ Moved {old_dir}/ -> {new_location}/")
    
    print()
    print("✅ Migration completed!")
    print("🤖 You can now use the new CLI structure:")
    print("   python cli/alfredo.py --list")

def show_migration_status(project_root: Path):
    """Show current migration status"""
    print("📊 Migration Status:")
    print("-" * 20)
    
    # Check new structure
    new_dirs = ["cli", "api", "integrations", "config", "tests", "scripts"]
    
    for dir_name in new_dirs:
        dir_path = project_root / dir_name
        status = "✅" if dir_path.exists() else "❌"
        print(f"   {status} {dir_name}/")
    
    # Check old structure
    print()
    print("📂 Legacy Files:")
    print("-" * 15)
    
    old_items = [
        ("Alfredo.py", "file"),
        ("commands/", "dir"),
        ("services/", "dir"),
        ("install.py", "file")
    ]
    
    for item, item_type in old_items:
        item_path = project_root / item
        if item_type == "dir":
            exists = item_path.is_dir()
        else:
            exists = item_path.is_file()
        
        status = "🔄" if exists else "✅"
        action = "needs migration" if exists else "migrated"
        print(f"   {status} {item} ({action})")

if __name__ == "__main__":
    main()
