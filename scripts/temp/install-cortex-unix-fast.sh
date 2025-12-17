#!/bin/bash
# CORTEX Fast Bootstrap Installer for Unix/macOS
# Optimized installation: Core packages first, optional later

echo "🧠 CORTEX Fast Bootstrap Installer for Unix/macOS"
echo "=================================================="
echo ""

# Check Python
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+ first"
    echo "   macOS: brew install python@3.12"
    echo "   Ubuntu/Debian: sudo apt install python3.12"
    exit 1
else
    PY_VERSION=$(python3 --version)
    echo "✅ Python found: $PY_VERSION"
fi

# Check Git
echo "🔍 Checking Git installation..."
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first"
    echo "   macOS: brew install git"
    echo "   Ubuntu/Debian: sudo apt install git"
    exit 1
else
    GIT_VERSION=$(git --version)
    echo "✅ Git found: $GIT_VERSION"
fi

echo ""
echo "🗑️  Cleaning up legacy packages from CORTEX 3.9.0..."
echo "   (Removing 67 unused packages, ~780 MB)"
echo ""

# Unused packages to remove
UNUSED_PACKAGES=(
    "matplotlib" "Flask" "networkx"
    "playwright" "selenium" "pytest-selenium"
    "PyGithub" "esprima" "tree-sitter-languages"
    "python-docx" "pypdf" "tomli"
    "pytest-cov" "pytest-asyncio"
    "scikit-learn" "numpy" "send2trash"
)

REMOVED=0
for PKG in "${UNUSED_PACKAGES[@]}"; do
    if python3 -m pip show "$PKG" &> /dev/null; then
        echo -n "  🗑️  Removing $PKG... "
        if python3 -m pip uninstall -y "$PKG" --quiet 2>/dev/null; then
            ((REMOVED++))
            echo "✅"
        else
            echo "⚠️  (skipped)"
        fi
    fi
done

if [ $REMOVED -gt 0 ]; then
    echo ""
    echo "✅ Removed $REMOVED unused packages"
fi

echo ""
echo "📦 Installing CORTEX Core Dependencies..."
echo "   (9 packages, ~20 MB, takes 30-45 seconds)"
echo ""

if [ -d "cortex-files" ]; then
    cd cortex-files
    
    # Install core dependencies first (fast)
    CORE_START=$(date +%s)
    python3 -m pip install --upgrade pip --quiet
    python3 -m pip install -r requirements.txt
    CORE_END=$(date +%s)
    CORE_TIME=$((CORE_END - CORE_START))
    
    echo ""
    echo "✅ Core dependencies installed in $CORE_TIME seconds"
    echo ""
    echo "🚀 CORTEX is ready for basic usage!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Use '/CORTEX setup' in GitHub Copilot Chat"
    echo "2. Start with: '/CORTEX help'"
    echo ""
    echo "⚡ Optional: Install enhanced features (ML token optimization)"
    echo "   Run: pip install -r requirements-optional.txt"
    echo "   (Takes ~3 minutes, enables ML-powered context compression)"
    echo ""
    
    # Ask if user wants optional features
    read -p "Install optional features now? (y/N): " INSTALL_OPTIONAL
    if [[ "$INSTALL_OPTIONAL" =~ ^[Yy]$ ]]; then
        echo ""
        echo "📦 Installing optional features..."
        echo "   (3 packages: scikit-learn, numpy, send2trash - ~3 minutes, 205 MB)"
        OPTIONAL_START=$(date +%s)
        python3 -m pip install -r requirements-optional.txt
        OPTIONAL_END=$(date +%s)
        OPTIONAL_TIME=$((OPTIONAL_END - OPTIONAL_START))
        echo ""
        echo "✅ Optional features installed in $((OPTIONAL_TIME / 60)) minutes"
        echo "🎉 Full CORTEX installation complete!"
    else
        echo ""
        echo "⏩ Skipping optional features (you can install later)"
        echo "   To install later: pip install -r requirements-optional.txt"
    fi
    
    echo ""
    echo "==============================================="
    echo "✅ CORTEX Installation Complete!"
    echo "==============================================="
    echo ""
    echo "Use '/CORTEX' in GitHub Copilot Chat to get started"
    echo ""
    
else
    echo "❌ cortex-files directory not found!"
    echo "   Please extract the CORTEX package first."
    exit 1
fi
