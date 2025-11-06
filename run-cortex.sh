#!/bin/zsh
# CORTEX Universal Entry Point Runner
# Usage: ./run-cortex.sh
#
# This script serves as a convenient shortcut to invoke the CORTEX entry point.
# When you run this script, it assumes you're invoking CORTEX for AI assistance.

CORTEX_ROOT="/Users/asifhussain/PROJECTS/CORTEX"
CORTEX_ENTRY_POINT="$CORTEX_ROOT/prompts/user/cortex.md"

# Colors for output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo "${CYAN}║            🧠 CORTEX Universal Entry Point             ║${NC}"
echo "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "${GREEN}📍 Entry Point: ${NC}$CORTEX_ENTRY_POINT"
echo ""
echo "${YELLOW}To use CORTEX with GitHub Copilot:${NC}"
echo "  ${CYAN}#file:$CORTEX_ENTRY_POINT${NC}"
echo ""
echo "${YELLOW}Quick Commands:${NC}"
echo "  ${GREEN}./run-cortex.sh${NC}  - Run this script"
echo "  ${GREEN}cortex${NC}           - Open CORTEX entry point in VS Code (alias)"
echo "  ${GREEN}cdcortex${NC}         - Navigate to CORTEX project directory (alias)"
echo ""
echo "${YELLOW}Opening CORTEX entry point...${NC}"

# Open in VS Code
if command -v code &> /dev/null; then
    code "$CORTEX_ENTRY_POINT"
    echo "${GREEN}✅ CORTEX entry point opened in VS Code${NC}"
else
    echo "${YELLOW}⚠️  VS Code command 'code' not found. Opening with default editor...${NC}"
    open "$CORTEX_ENTRY_POINT"
fi

echo ""
echo "${CYAN}Ready for AI assistance! Start your request with GitHub Copilot.${NC}"
