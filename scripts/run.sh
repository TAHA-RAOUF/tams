#!/bin/bash
# Script to easily run the TAMS application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}TAMS - Technical Asset Management System${NC}"
echo -e "${BLUE}=================================${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated.${NC}"

# Check if requirements are installed
echo -e "${YELLOW}Checking requirements...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}Requirements installed/updated.${NC}"

# Check if database is initialized
if [ ! -f "taqathon.db" ]; then
    echo -e "${YELLOW}Database not found. Initializing...${NC}"
    python init_db.py
    echo -e "${GREEN}Database initialized.${NC}"
    
    # Ask if user wants to seed the database
    echo -e "${CYAN}Do you want to seed the database with sample data? (y/n)${NC}"
    read seed_choice
    
    if [[ $seed_choice == "y" || $seed_choice == "Y" ]]; then
        echo -e "${YELLOW}Seeding database...${NC}"
        python seed_database.py
        echo -e "${GREEN}Database seeded with sample data.${NC}"
    fi
fi

# Run the application
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Starting TAMS server...${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${CYAN}Access the browsable API at: ${PURPLE}http://localhost:5000/api-browser/${NC}"
echo -e "${BLUE}=================================${NC}"

# Set Flask debug mode based on user preference
echo -e "${CYAN}Run in debug mode? (y/n)${NC}"
read debug_choice

if [[ $debug_choice == "y" || $debug_choice == "Y" ]]; then
    FLASK_DEBUG=true python main.py
else
    python main.py
fi
