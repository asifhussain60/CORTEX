#!/usr/bin/env bash
#
# CORTEX MCP Verification Script
# Run this after reloading VS Code to verify MCP tools are available
#

echo "═══════════════════════════════════════════════════════════════════"
echo "CORTEX MCP Post-Reload Verification"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

echo "This script verifies MCP server configuration."
echo "To test actual tool availability in Copilot Chat:"
echo ""
echo "  1. Open GitHub Copilot Chat"
echo "  2. Type: @workspace list available MCP tools"
echo "  3. Expected: 90+ cortex_* tools"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Configuration Status:"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check Python path
echo "✓ Python Virtual Environment:"
if [ -f ".venv/bin/python" ]; then
    echo "  ✅ .venv/bin/python exists"
    PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
    echo "  Version: $PYTHON_VERSION"
else
    echo "  ❌ .venv/bin/python NOT FOUND"
    exit 1
fi
echo ""

# Check VS Code settings
echo "✓ VS Code MCP Configuration:"
if [ -f ".vscode/settings.json" ]; then
    if grep -q '"github.copilot.chat.mcpServers"' .vscode/settings.json; then
        echo "  ✅ MCP servers configured"
        
        # Check for correct path
        if grep -q 'Scripts/python.exe' .vscode/settings.json; then
            echo "  ⚠️  WARNING: Windows path detected (needs macOS fix)"
            echo "     Run: sed -i '' 's/Scripts\\/python.exe/bin\\/python/g' .vscode/settings.json"
        elif grep -q 'bin/python' .vscode/settings.json; then
            echo "  ✅ macOS/Linux path detected (correct)"
        fi
    else
        echo "  ❌ MCP servers not configured"
    fi
else
    echo "  ❌ .vscode/settings.json not found"
fi
echo ""

# Check MCP module
echo "✓ MCP Module Availability:"
cd "$(dirname "$0")/.."
PYTHONPATH=. .venv/bin/python -c "import cortex.mcp; print('  ✅ cortex.mcp module importable')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ cortex.mcp module verified"
else
    echo "  ❌ cortex.mcp module import failed"
fi
echo ""

# Test MCP server startup
echo "✓ MCP Server Startup Test:"
CORTEX_ENV=development CORTEX_MCP_ENABLED=true PYTHONPATH=. CORTEX_WORKSPACE=. \
    .venv/bin/python -m cortex.mcp 2>&1 | head -20 | grep -q "Registered tool:" && \
    echo "  ✅ MCP server starts and registers tools" || \
    echo "  ⚠️  Could not verify tool registration"
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo "Next Steps:"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "1. **Reload VS Code Window** (if not done yet):"
echo "   Command Palette (Cmd+Shift+P) → Developer: Reload Window"
echo ""
echo "2. **Verify MCP Tools in Copilot Chat:**"
echo "   Open chat and run: @workspace Can you use cortex MCP tools?"
echo ""
echo "3. **Test Tool Catalog:**"
echo "   In Copilot Chat, ask me to run: mcp_cortex_cortex_tools_catalog"
echo "   Expected output: 90+ tools"
echo ""
echo "4. **Execute Waves I-J-K:**"
echo "   Once tools verified, proceed with autonomous wave execution"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
