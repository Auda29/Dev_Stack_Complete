#!/bin/bash
# Dev_Stack Host Setup Script (Linux/Mac)
# Installs Python dependencies required for running Dev_Stack utility scripts

set -e  # Exit on error

echo "========================================="
echo "Dev_Stack Host Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${GREEN}✓${NC} Detected OS: ${MACHINE}"
echo ""

# Check Python 3
echo "Checking Python 3 installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Found: ${PYTHON_VERSION}"
else
    echo -e "${RED}✗${NC} Python 3 not found!"
    echo "Please install Python 3.8+ first:"
    if [ "$MACHINE" = "Linux" ]; then
        echo "  sudo apt update && sudo apt install -y python3"
    elif [ "$MACHINE" = "Mac" ]; then
        echo "  brew install python3"
    fi
    exit 1
fi
echo ""

# Check pip3
echo "Checking pip3 installation..."
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip3 is already installed"
else
    echo -e "${YELLOW}!${NC} pip3 not found, installing..."
    
    if [ "$MACHINE" = "Linux" ]; then
        # Detect if sudo is available
        if command -v sudo &> /dev/null; then
            sudo apt update
            sudo apt install -y python3-pip
        else
            echo -e "${RED}✗${NC} sudo not available. Please install pip3 manually:"
            echo "  apt install python3-pip"
            exit 1
        fi
    elif [ "$MACHINE" = "Mac" ]; then
        python3 -m ensurepip --upgrade
    fi
    
    echo -e "${GREEN}✓${NC} pip3 installed successfully"
fi
echo ""

# Install Python packages
echo "Installing Python dependencies from requirements.txt..."
echo ""

# Check if we're in an externally managed environment (Ubuntu 24.04+)
# Try installing without --break-system-packages first
if pip3 install -r requirements.txt &> /dev/null; then
    echo -e "${GREEN}✓${NC} Dependencies installed successfully"
else
    echo -e "${YELLOW}!${NC} Standard installation failed, trying with --break-system-packages flag..."
    echo "  (This is normal for Ubuntu 24.04+ with externally-managed Python)"
    
    if pip3 install --break-system-packages -r requirements.txt; then
        echo -e "${GREEN}✓${NC} Dependencies installed successfully with --break-system-packages"
    else
        echo -e "${RED}✗${NC} Failed to install dependencies"
        echo ""
        echo "You may need to create a virtual environment instead:"
        echo "  python3 -m venv .venv"
        echo "  source .venv/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
fi

echo ""
echo "========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================="
echo ""
echo "You can now run Dev_Stack utility scripts:"
echo "  python3 scripts/embed_codebase.py"
echo "  python3 scripts/task_manager.py"
echo "  python3 scripts/watcher.py"
echo ""
