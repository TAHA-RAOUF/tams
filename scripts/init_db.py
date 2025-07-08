#!/usr/bin/env python3
"""
Database initialization script for TAQATHON Equipment Reliability API
Run this script to create the database tables
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.database import db

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Print table info
        print("\nCreated tables:")
        for table in db.metadata.tables.keys():
            print(f"  - {table}")

if __name__ == "__main__":
    init_database()
