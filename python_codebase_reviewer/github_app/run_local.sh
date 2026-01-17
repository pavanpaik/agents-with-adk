#!/bin/bash
#
# Run GitHub App webhook handler locally for development and testing
#
# Usage:
#   ./run_local.sh
#
# Requirements:
#   - Python 3.11+
#   - .env file with required environment variables
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Python Codebase Reviewer GitHub App${NC}"
echo -e "${GREEN}Local Development Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Copy .env.example to .env and fill in your values:"
    echo "  cp .env.example .env"
    echo
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check required environment variables
echo
echo -e "${YELLOW}Checking configuration...${NC}"

if [ -z "$GITHUB_APP_ID" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_APP_ID not set${NC}"
fi

if [ -z "$GITHUB_WEBHOOK_SECRET" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_WEBHOOK_SECRET not set${NC}"
fi

if [ -z "$GITHUB_PRIVATE_KEY" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_PRIVATE_KEY not set${NC}"
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GOOGLE_API_KEY not set${NC}"
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Flask server...${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo "Server will be available at: http://localhost:8080"
echo "Health check: http://localhost:8080/health"
echo "Webhook endpoint: http://localhost:8080/webhook"
echo
echo "Press Ctrl+C to stop"
echo

# Run Flask app
python webhook_handler.py
