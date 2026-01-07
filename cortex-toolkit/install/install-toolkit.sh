#!/bin/bash
# CORTEX Toolkit Installation Script (Linux/macOS)
# Installs toolkit with global command integration

set -e

echo "=== CORTEX Toolkit Installer (Linux/macOS) ==="
echo ""

# Discover toolkit root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOLKIT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Toolkit Root: $TOOLKIT_ROOT"

# Parse arguments
SHELL_PROFILE=false
SKIP_VERIFY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --shell-profile)
            SHELL_PROFILE=true
            shift
            ;;
        --skip-verify)
            SKIP_VERIFY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# 1. Set environment variable in current session
echo ""
echo "[1/5] Setting environment variable..."
export CORTEX_TOOLKIT_ROOT="$TOOLKIT_ROOT"
echo "  ✓ Set CORTEX_TOOLKIT_ROOT (current session)"

# 2. Add to PATH (current session)
echo ""
echo "[2/5] Adding to PATH..."
CLI_PATH="$TOOLKIT_ROOT/cli"
export PATH="$CLI_PATH:$PATH"
echo "  ✓ Added to PATH (current session)"

# 3. Create user config directory
echo ""
echo "[3/5] Creating user config..."
USER_CONFIG_DIR="$HOME/.cortex"
USER_CONFIG_FILE="$USER_CONFIG_DIR/config.yaml"

if [ ! -d "$USER_CONFIG_DIR" ]; then
    mkdir -p "$USER_CONFIG_DIR"
    echo "  ✓ Created $USER_CONFIG_DIR"
fi

if [ ! -f "$USER_CONFIG_FILE" ]; then
    cat > "$USER_CONFIG_FILE" <<EOF
# CORTEX User Configuration
cortex_toolkit_root: $TOOLKIT_ROOT
python_path: python3
EOF
    echo "  ✓ Created $USER_CONFIG_FILE"
else
    echo "  ℹ Config already exists"
fi

# 4. Setup shell profile integration (optional)
if [ "$SHELL_PROFILE" = true ]; then
    echo ""
    echo "[4/5] Setting up shell profile..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    if [ "$SHELL_NAME" = "bash" ]; then
        PROFILE_FILE="$HOME/.bashrc"
    elif [ "$SHELL_NAME" = "zsh" ]; then
        PROFILE_FILE="$HOME/.zshrc"
    else
        PROFILE_FILE="$HOME/.profile"
    fi
    
    PROFILE_SNIPPET=$(cat <<'EOF'

# CORTEX Toolkit Integration
export CORTEX_TOOLKIT_ROOT="$TOOLKIT_ROOT"
export PATH="$CORTEX_TOOLKIT_ROOT/cli:$PATH"

# Load global commands (optional)
# source "$CORTEX_TOOLKIT_ROOT/install/setup-global-commands.sh"
EOF
    )
    
    if [ -f "$PROFILE_FILE" ]; then
        if ! grep -q "CORTEX Toolkit Integration" "$PROFILE_FILE"; then
            echo "$PROFILE_SNIPPET" >> "$PROFILE_FILE"
            echo "  ✓ Added to $PROFILE_FILE"
        else
            echo "  ℹ Already in $PROFILE_FILE"
        fi
    else
        echo "$PROFILE_SNIPPET" > "$PROFILE_FILE"
        echo "  ✓ Created $PROFILE_FILE"
    fi
else
    echo ""
    echo "[4/5] Skipping shell profile (use --shell-profile)"
fi

# 5. Verify installation
if [ "$SKIP_VERIFY" = false ]; then
    echo ""
    echo "[5/5] Verifying installation..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "  ✓ Python: $PYTHON_VERSION"
    else
        echo "  ⚠ Python3 not found in PATH"
    fi
    
    # Check toolkit registry
    REGISTRY_SCRIPT="$TOOLKIT_ROOT/shared/toolkit_registry.py"
    if [ -f "$REGISTRY_SCRIPT" ]; then
        if REGISTRY_OUTPUT=$(python3 "$REGISTRY_SCRIPT" version 2>&1); then
            echo "  ✓ Toolkit Registry: $REGISTRY_OUTPUT"
        else
            echo "  ⚠ Cannot execute toolkit registry"
        fi
    fi
    
    # Check manifest
    MANIFEST_PATH="$TOOLKIT_ROOT/toolkit-manifest.yaml"
    if [ -f "$MANIFEST_PATH" ]; then
        echo "  ✓ Manifest: Found"
    else
        echo "  ✗ Manifest: Missing"
    fi
else
    echo ""
    echo "[5/5] Skipping verification (use without --skip-verify)"
fi

# Summary
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next Steps:"
echo "  1. Restart your terminal or run: source $PROFILE_FILE"
echo "  2. Test installation: python3 \"$TOOLKIT_ROOT/shared/toolkit_registry.py\" list"
echo "  3. View all tools: python3 \"$TOOLKIT_ROOT/shared/toolkit_registry.py\" list"
echo ""
echo "Environment:"
echo "  CORTEX_TOOLKIT_ROOT = $TOOLKIT_ROOT"
echo "  PATH += $CLI_PATH"
echo ""
echo "Documentation: $TOOLKIT_ROOT/README.md"
