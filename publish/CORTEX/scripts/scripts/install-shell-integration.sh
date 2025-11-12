#!/usr/bin/env bash
# CORTEX Shell Integration Installer
#
# Installs shell completions and git hooks for CORTEX
#
# Usage:
#   ./install-shell-integration.sh
#   ./install-shell-integration.sh --uninstall
#
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.
# Phase: Phase 4.2 - Shell Integration

set -e

CORTEX_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPLETIONS_DIR="$CORTEX_ROOT/scripts/completions"
GIT_HOOKS_DIR="$CORTEX_ROOT/.git/hooks"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect shell
detect_shell() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    else
        echo "unknown"
    fi
}

# Install bash completions
install_bash_completions() {
    echo -e "${YELLOW}Installing bash completions...${NC}"
    
    local rc_file="$HOME/.bashrc"
    [ -f "$HOME/.bash_profile" ] && rc_file="$HOME/.bash_profile"
    
    local source_line="source \"$COMPLETIONS_DIR/cortex-completions.bash\""
    
    if grep -q "cortex-completions.bash" "$rc_file" 2>/dev/null; then
        echo -e "${YELLOW}  Bash completions already installed${NC}"
    else
        echo "" >> "$rc_file"
        echo "# CORTEX shell completions" >> "$rc_file"
        echo "$source_line" >> "$rc_file"
        echo -e "${GREEN}  ✅ Added to $rc_file${NC}"
        echo -e "${YELLOW}  Run: source $rc_file${NC}"
    fi
}

# Install zsh completions
install_zsh_completions() {
    echo -e "${YELLOW}Installing zsh completions...${NC}"
    
    local rc_file="$HOME/.zshrc"
    
    # Check if fpath includes completions dir
    if ! grep -q "fpath=.*$COMPLETIONS_DIR" "$rc_file" 2>/dev/null; then
        echo "" >> "$rc_file"
        echo "# CORTEX shell completions" >> "$rc_file"
        echo "fpath=($COMPLETIONS_DIR \$fpath)" >> "$rc_file"
        echo "autoload -Uz compinit && compinit" >> "$rc_file"
        echo -e "${GREEN}  ✅ Added to $rc_file${NC}"
        echo -e "${YELLOW}  Run: source $rc_file${NC}"
    else
        echo -e "${YELLOW}  Zsh completions already installed${NC}"
    fi
}

# Install git hooks
install_git_hooks() {
    echo -e "${YELLOW}Installing git hooks...${NC}"
    
    if [ ! -d "$GIT_HOOKS_DIR" ]; then
        echo -e "${RED}  ❌ Not a git repository${NC}"
        return 1
    fi
    
    # Install post-commit hook
    local hook_file="$GIT_HOOKS_DIR/post-commit"
    
    if [ -f "$hook_file" ]; then
        # Backup existing hook
        cp "$hook_file" "$hook_file.backup"
        echo -e "${YELLOW}  Backed up existing post-commit hook${NC}"
    fi
    
    # Create new hook
    cat > "$hook_file" << 'EOF'
#!/usr/bin/env bash
# CORTEX Auto-Capture Post-Commit Hook
# Automatically captures context after git commits

# Get commit message
COMMIT_MSG=$(git log -1 --pretty=%B)

# Skip if commit message is empty or merge commit
if [ -z "$COMMIT_MSG" ] || [[ "$COMMIT_MSG" == Merge* ]]; then
    exit 0
fi

# Check if CORTEX is available
if ! command -v cortex-capture &> /dev/null; then
    # Try direct path
    CORTEX_CAPTURE="$(git rev-parse --show-toplevel)/scripts/cortex-capture"
    if [ ! -f "$CORTEX_CAPTURE" ]; then
        exit 0
    fi
else
    CORTEX_CAPTURE="cortex-capture"
fi

# Detect type from commit message
TYPE="general"
if [[ "$COMMIT_MSG" =~ ^feat: ]] || [[ "$COMMIT_MSG" =~ ^feature: ]]; then
    TYPE="feature"
elif [[ "$COMMIT_MSG" =~ ^fix: ]] || [[ "$COMMIT_MSG" =~ ^bug: ]]; then
    TYPE="bug"
elif [[ "$COMMIT_MSG" =~ ^refactor: ]]; then
    TYPE="refactor"
fi

# Capture (silent mode, don't block commit)
$CORTEX_CAPTURE "$COMMIT_MSG" --type "$TYPE" > /dev/null 2>&1 &

exit 0
EOF
    
    chmod +x "$hook_file"
    echo -e "${GREEN}  ✅ Installed post-commit hook${NC}"
}

# Uninstall completions
uninstall_completions() {
    echo -e "${YELLOW}Uninstalling shell completions...${NC}"
    
    # Remove from bash
    if [ -f "$HOME/.bashrc" ]; then
        sed -i.bak '/cortex-completions.bash/d' "$HOME/.bashrc"
        echo -e "${GREEN}  ✅ Removed from ~/.bashrc${NC}"
    fi
    
    if [ -f "$HOME/.bash_profile" ]; then
        sed -i.bak '/cortex-completions.bash/d' "$HOME/.bash_profile"
        echo -e "${GREEN}  ✅ Removed from ~/.bash_profile${NC}"
    fi
    
    # Remove from zsh
    if [ -f "$HOME/.zshrc" ]; then
        sed -i.bak '/CORTEX shell completions/d' "$HOME/.zshrc"
        sed -i.bak "\|fpath=.*$COMPLETIONS_DIR|d" "$HOME/.zshrc"
        echo -e "${GREEN}  ✅ Removed from ~/.zshrc${NC}"
    fi
}

# Uninstall git hooks
uninstall_git_hooks() {
    echo -e "${YELLOW}Uninstalling git hooks...${NC}"
    
    local hook_file="$GIT_HOOKS_DIR/post-commit"
    
    if [ -f "$hook_file.backup" ]; then
        mv "$hook_file.backup" "$hook_file"
        echo -e "${GREEN}  ✅ Restored backup hook${NC}"
    elif [ -f "$hook_file" ]; then
        rm "$hook_file"
        echo -e "${GREEN}  ✅ Removed post-commit hook${NC}"
    fi
}

# Main installation
install() {
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  CORTEX Shell Integration Installer"
    echo "═══════════════════════════════════════════"
    echo ""
    
    # Detect shell
    SHELL_TYPE=$(detect_shell)
    echo "Detected shell: $SHELL_TYPE"
    echo ""
    
    # Install completions
    case "$SHELL_TYPE" in
        bash)
            install_bash_completions
            ;;
        zsh)
            install_zsh_completions
            ;;
        *)
            echo -e "${YELLOW}Unknown shell, skipping completions${NC}"
            ;;
    esac
    
    echo ""
    
    # Install git hooks
    install_git_hooks
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Installation Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Reload your shell: source ~/.${SHELL_TYPE}rc"
    echo "  2. Try tab completion: cortex-<TAB>"
    echo "  3. Git commits will auto-capture context"
    echo ""
}

# Main uninstallation
uninstall() {
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  CORTEX Shell Integration Uninstaller"
    echo "═══════════════════════════════════════════"
    echo ""
    
    uninstall_completions
    echo ""
    uninstall_git_hooks
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Uninstallation Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo ""
}

# Parse arguments
if [ "$1" = "--uninstall" ]; then
    uninstall
else
    install
fi
