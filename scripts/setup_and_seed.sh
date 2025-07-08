#!/bin/bash

echo "🚀 Setting up TAMS environment and seeding the database..."
echo "=====================================================\n"

# Create and activate Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Source the virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📊 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Initialize the database
echo "🗄️ Initializing database..."
python init_db.py

# Seed the database
echo "🌱 Seeding database with anomalies..."
python seed_database.py

echo "✅ Setup complete!"
echo "📝 To start the server, run:"
echo "   source venv/bin/activate"
echo "   python main.py"
