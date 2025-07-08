#!/usr/bin/env python3
"""
Main migration script to reorganize the entire project structure
"""
import os
import sys
import importlib.util
import subprocess

def run_script(script_path):
    """Run a Python script using the current interpreter"""
    print(f"\n\033[1;34mRunning {script_path}...\033[0m")
    
    try:
        # Load the script as a module
        spec = importlib.util.spec_from_file_location("migration_script", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"\033[1;32mCompleted {script_path} successfully\033[0m")
        return True
    except Exception as e:
        print(f"\033[1;31mError running {script_path}: {e}\033[0m")
        return False

def make_script_executable(script_path):
    """Make a script executable"""
    try:
        # Add execute permission
        subprocess.run(['chmod', '+x', script_path])
        print(f"Made {script_path} executable")
    except Exception as e:
        print(f"Error making {script_path} executable: {e}")

def main():
    """Main migration function"""
    # Make sure we're in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(project_root)
    
    print("\033[1;33m=" * 80)
    print("TAMS Project Structure Migration")
    print("=" * 80 + "\033[0m")
    
    # Ensure all necessary directories exist
    for directory in [
        'app',
        'app/api',
        'app/api/v1',
        'app/api/v1/endpoints',
        'app/core',
        'app/models',
        'app/utils',
        'app/templates',
        'app/static',
        'app/docs',
        'scripts',
    ]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    # Run the directory structure migration
    success = run_script('migrate_structure.py')
    if not success:
        print("\033[1;31mStructure migration failed, aborting.\033[0m")
        return
    
    # Run the models migration
    models_script = 'scripts/migrate_models.py'
    success = run_script(models_script)
    if not success:
        print("\033[1;31mModels migration failed.\033[0m")
    
    # Make scripts executable
    make_script_executable('run.py')
    make_script_executable('scripts/init_db.py')
    make_script_executable('scripts/seed_database.py')
    make_script_executable('scripts/migrate_models.py')
    
    print("\n\033[1;32m=" * 80)
    print("Migration complete!")
    print("=" * 80)
    print("\033[0m")
    print("Next steps:")
    print("1. Review the new project structure")
    print("2. Run tests to ensure everything works")
    print("3. Start the application with `python run.py`")

if __name__ == "__main__":
    main()
