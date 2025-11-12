#!/usr/bin/env bash

#
# CORTEX Bootstrap Installer for macOS/Linux
#
# Automated bootstrap installer that handles Python and Git installation,
# then runs the Python installer. Designed for VS Code terminal workflow.
#
# Usage:
#   chmod +x install-cortex-unix.sh
#   ./install-cortex-unix.sh [target_path]
#
# Example:
#   ./install-cortex-unix.sh /Users/YourName/Projects/KSESSIONS
#
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.
# License: Proprietary
# Version: 5.2.0
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# CORTEX Banner
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  🧠 CORTEX Bootstrap Installer (Unix)                       ║
║                                                                              ║
║  Installing prerequisites and setting up CORTEX for your project            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo "Version:    5.2.0"
echo "Author:     Asif Hussain"
echo "Copyright:  © 2024-2025 Asif Hussain. All rights reserved."
echo "License:    Proprietary"
echo "Platform:   $(uname -s)"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Detect OS
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
    Darwin*)    OS="macOS";;
    Linux*)     OS="Linux";;
    *)          OS="Unknown";;
esac

echo -e "${CYAN}Detected OS: $OS${NC}"
echo ""

# Step 1: Check for Python
echo -e "${YELLOW}🔍 Checking for Python installation...${NC}"

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    if [[ $PYTHON_VERSION =~ Python\ 3\.([8-9]|1[0-9]) ]]; then
        PYTHON_CMD="python3"
        echo -e "   ${GREEN}✅ Found: $PYTHON_VERSION${NC}"
    fi
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION =~ Python\ 3\.([8-9]|1[0-9]) ]]; then
        PYTHON_CMD="python"
        echo -e "   ${GREEN}✅ Found: $PYTHON_VERSION${NC}"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "   ${RED}❌ Python 3.8+ not found${NC}"
    echo ""
    echo -e "${YELLOW}📥 Installing Python...${NC}"
    
    if [ "$OS" = "macOS" ]; then
        # Check for Homebrew
        if command -v brew &> /dev/null; then
            echo -e "   ${GRAY}Using Homebrew to install Python...${NC}"
            brew install python@3.11
            PYTHON_CMD="python3"
            echo -e "   ${GREEN}✅ Python installed successfully${NC}"
        else
            echo -e "   ${RED}❌ Homebrew not found${NC}"
            echo -e "   ${YELLOW}Please install Homebrew first: https://brew.sh/${NC}"
            echo -e "   ${YELLOW}Or install Python manually: https://python.org/${NC}"
            exit 1
        fi
    elif [ "$OS" = "Linux" ]; then
        # Detect Linux distribution
        if [ -f /etc/debian_version ]; then
            echo -e "   ${GRAY}Using apt to install Python...${NC}"
            sudo apt update
            sudo apt install -y python3 python3-pip
            PYTHON_CMD="python3"
            echo -e "   ${GREEN}✅ Python installed successfully${NC}"
        elif [ -f /etc/redhat-release ]; then
            echo -e "   ${GRAY}Using yum to install Python...${NC}"
            sudo yum install -y python3 python3-pip
            PYTHON_CMD="python3"
            echo -e "   ${GREEN}✅ Python installed successfully${NC}"
        else
            echo -e "   ${RED}❌ Unsupported Linux distribution${NC}"
            echo -e "   ${YELLOW}Please install Python 3.8+ manually and re-run this script${NC}"
            exit 1
        fi
    else
        echo -e "   ${RED}❌ Unsupported operating system${NC}"
        exit 1
    fi
fi

# Step 2: Check for Git (optional but recommended)
echo ""
echo -e "${YELLOW}🔍 Checking for Git installation...${NC}"

GIT_INSTALLED=false
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    GIT_INSTALLED=true
    echo -e "   ${GREEN}✅ Found: $GIT_VERSION${NC}"
else
    echo -e "   ${YELLOW}⚠️  Git not found (optional but recommended)${NC}"
    read -p "   Install Git now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${YELLOW}📥 Installing Git...${NC}"
        
        if [ "$OS" = "macOS" ]; then
            if command -v brew &> /dev/null; then
                brew install git
                GIT_INSTALLED=true
                echo -e "   ${GREEN}✅ Git installed successfully${NC}"
            else
                echo -e "   ${YELLOW}⚠️  Homebrew not available, skipping Git${NC}"
            fi
        elif [ "$OS" = "Linux" ]; then
            if [ -f /etc/debian_version ]; then
                sudo apt install -y git
                GIT_INSTALLED=true
                echo -e "   ${GREEN}✅ Git installed successfully${NC}"
            elif [ -f /etc/redhat-release ]; then
                sudo yum install -y git
                GIT_INSTALLED=true
                echo -e "   ${GREEN}✅ Git installed successfully${NC}"
            fi
        fi
    fi
fi

# Step 3: Install Python dependencies
echo ""
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REQUIREMENTS_FILE="$SCRIPT_DIR/cortex-files/requirements.txt"

if [ -f "$REQUIREMENTS_FILE" ]; then
    $PYTHON_CMD -m pip install --quiet --upgrade pip
    $PYTHON_CMD -m pip install --quiet -r "$REQUIREMENTS_FILE"
    echo -e "   ${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "   ${YELLOW}⚠️  requirements.txt not found, skipping${NC}"
fi

# Step 4: Get target path
TARGET_PATH="${1:-}"
if [ -z "$TARGET_PATH" ]; then
    echo ""
    echo -e "${YELLOW}📁 Target Repository${NC}"
    echo -e "   ${GRAY}Where should CORTEX be installed?${NC}"
    echo -e "   ${GRAY}(Press Enter for current directory)${NC}"
    read -p "   Path: " TARGET_PATH
    
    if [ -z "$TARGET_PATH" ]; then
        TARGET_PATH=$(pwd)
    fi
fi

# Step 5: Run Python installer
echo ""
echo -e "${YELLOW}🚀 Running CORTEX installer...${NC}"

PYTHON_INSTALLER="$SCRIPT_DIR/install_cortex.py"
if [ ! -f "$PYTHON_INSTALLER" ]; then
    echo -e "   ${RED}❌ install_cortex.py not found in package${NC}"
    echo -e "   ${YELLOW}Please ensure you have the complete CORTEX installation package${NC}"
    exit 1
fi

if $PYTHON_CMD "$PYTHON_INSTALLER" "$TARGET_PATH"; then
    echo ""
    echo -e "${GREEN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                     ✅ Bootstrap Complete!                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${CYAN}🎯 Next Steps:${NC}"
    echo -e "   ${NC}1. Open your project in VS Code${NC}"
    echo -e "   ${NC}2. Open GitHub Copilot Chat${NC}"
    echo -e "   ${YELLOW}3. Run: /CORTEX setup${NC}"
    echo ""
    echo -e "${GRAY}📚 For help, type in Copilot Chat: /CORTEX help${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Installation failed. Check error messages above.${NC}"
    exit 1
fi
