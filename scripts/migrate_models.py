#!/usr/bin/env python3
"""
Script to migrate the old monolithic models.py file to the new modular structure
"""
import os
import shutil
import re

def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def migrate_models():
    """Migrate models to new structure"""
    print("Starting models migration...")

    # Ensure models directory exists
    models_dir = os.path.join('.', 'app', 'models')
    create_directory_if_not_exists(models_dir)

    # Copy model files to new locations
    model_files = {
        'user.py': 'app/models/user.py',
        'anomaly.py': 'app/models/anomaly.py',
        'maintenance.py': 'app/models/maintenance.py',
        'action_plan.py': 'app/models/action_plan.py',
        'database.py': 'app/models/database.py'
    }

    for source, dest in model_files.items():
        dest_path = os.path.join('.', dest)
        if not os.path.exists(dest_path):
            print(f"Warning: Model file {dest_path} not found. You may need to create it manually.")

    # Update the models/__init__.py file
    init_path = os.path.join('.', 'app', 'models', '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('"""Models package initialization"""\n\n')
            f.write('from flask_sqlalchemy import SQLAlchemy\n')
            f.write('from flask_bcrypt import Bcrypt\n\n')
            f.write('db = SQLAlchemy()\n')
            f.write('bcrypt = Bcrypt()\n\n')
            f.write('# Import models to make them available when importing from app.models\n')
            f.write('from app.models.user import User\n')
            f.write('from app.models.anomaly import Anomaly\n')
            f.write('from app.models.maintenance import MaintenanceWindow\n')
            f.write('from app.models.action_plan import ActionPlan, ActionItem\n')
            f.write('from app.models.database import user_db\n')
        print(f"Created models/__init__.py file")
    
    print("Models migration complete.")

def update_all_imports():
    """Update imports in all Python files to reflect the new structure"""
    print("Updating imports in all Python files...")
    
    # Get all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and not root.startswith('./venv') and not root.startswith('./.venv'):
                python_files.append(os.path.join(root, file))
    
    # Define replacement patterns
    replacements = [
        # Fix model imports
        (r'from app.models import (.*)', r'from app.models import \1'),
        (r'from app.models import db, (.*)', r'from app.models import db, \1'),
        (r'import app.models as models', r'import app.models as models'),
        
        # Update endpoint imports
        (r'from app.api.v1.endpoints.auth import (.*)', r'from app.api.v1.endpoints.auth import \1'),
        (r'from app.api.v1.endpoints.anomalies import (.*)', r'from app.api.v1.endpoints.anomalies import \1'),
        (r'from app.api.v1.endpoints.status import (.*)', r'from app.api.v1.endpoints.status import \1'),
        (r'from app.api.v1.endpoints.maintenance import (.*)', r'from app.api.v1.endpoints.maintenance import \1'),
        (r'from app.api.v1.endpoints.dashboard import (.*)', r'from app.api.v1.endpoints.dashboard import \1'),
        (r'from app.api.v1.endpoints.import_data import (.*)', r'from app.api.v1.endpoints.import_data import \1'),
        (r'from app.api.v1.endpoints.predictions import (.*)', r'from app.api.v1.endpoints.predictions import \1'),
        (r'from app.api.v1.endpoints.action_plans import (.*)', r'from app.api.v1.endpoints.action_plans import \1'),
        
        # Update core imports
        (r'from app.core.predictor import (.*)', r'from app.core.predictor import \1'),
        (r'from app.core.browsable_api import (.*)', r'from app.core.browsable_api import \1'),
        
        # Update utils imports
        (r'from app.utils.enhanced_auth import (.*)', r'from app.utils.enhanced_auth import \1'),
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            for pattern, replacement in replacements:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated imports in {file_path}")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
    
    print("Imports update complete.")

if __name__ == "__main__":
    migrate_models()
    update_all_imports()
    print("Model migration complete!")
