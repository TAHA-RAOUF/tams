#!/usr/bin/env python3
"""
Cleanup script to remove old files after migration is complete
"""
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of a file with timestamp before removing"""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backup_old_files"
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}")
        
        # Copy the file to backup
        shutil.copy2(file_path, backup_path)
        print(f"✓ Created backup: {backup_path}")
        return True
    return False

def remove_old_files():
    """Remove old files that have been migrated to the new structure"""
    root_files_to_remove = [
        "anomaly_api.py",
        "api.py",
        "auth.py",
        "browsable_api.py",
        "enhanced_auth.py",
        "main.py",  # Original Flask app entry point, replaced by run.py
        "models.py",
        "predictor.py",
        "migrate_structure.py",  # Migration scripts are no longer needed
        "fix_migration.py",
        "test_migration.py",
    ]
    
    print("\n\033[1;34mBacking up and removing old files...\033[0m")
    
    for file in root_files_to_remove:
        if backup_file(file):
            try:
                os.remove(file)
                print(f"✓ Removed {file}")
            except Exception as e:
                print(f"× Failed to remove {file}: {str(e)}")

def main():
    """Main cleanup function"""
    print("\033[1;32m" + "=" * 80)
    print(" TAMS Project Cleanup ")
    print("=" * 80 + "\033[0m")
    
    # Confirm before proceeding
    response = input("\nThis will backup and remove old files from the project root. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    remove_old_files()
    
    print("\n\033[1;32m" + "=" * 80)
    print(" Cleanup Complete ")
    print("=" * 80 + "\033[0m")
    
    print("\nNote: Files were backed up to the 'backup_old_files' directory.")
    print("If the application works correctly, you can safely delete the backup files.")

if __name__ == "__main__":
    main()
