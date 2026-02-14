#!/bin/bash
# CORTEX MCP Verification Script
# Confirms all 24 tools are properly configured and accessible

set -e

echo "🔧 CORTEX MCP Verification"
echo "=" | tr '=' '=' | head -c 60; echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo
echo "1️⃣  Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    check_pass "Python 3 found: $PYTHON_VERSION"
else
    check_fail "Python 3 not found"
    exit 1
fi

echo
echo "2️⃣  Checking virtual environment..."
if [ -f ".venv/bin/python" ]; then
    check_pass "Virtual environment exists: .venv/"
else
    check_fail "Virtual environment not found (.venv/)"
    echo "   Run: python3 -m venv .venv && source .venv/bin/activate"
    exit 1
fi

echo
echo "3️⃣  Checking MCP module..."
if python3 -c "import cortex.mcp; print('OK')" 2>/dev/null; then
    check_pass "cortex.mcp module imports successfully"
else
    check_fail "cortex.mcp module import failed"
    echo "   Check cortex/mcp/base.py for syntax errors"
    exit 1
fi

echo
echo "4️⃣  Checking MCP tool count..."
TOOL_COUNT=$(python3 -c "from cortex.mcp import MCPServer; print(len(MCPServer().list_tools()))" 2>/dev/null)
if [ "$TOOL_COUNT" -eq 24 ]; then
    check_pass "MCP server reports 24 tools"
else
    check_fail "MCP server reports $TOOL_COUNT tools (expected 24)"
    exit 1
fi

echo
echo "5️⃣  Checking VS Code configuration..."
if [ -f ".vscode/settings.json" ]; then
    check_pass ".vscode/settings.json exists"
    
    if grep -q "github.copilot.chat.mcpServers" .vscode/settings.json; then
        check_pass "MCP server configured in settings.json"
    else
        check_fail "MCP server not configured in settings.json"
        echo "   Run: python3 .cortex/setup-mcp.py"
        exit 1
    fi
else
    check_fail ".vscode/settings.json not found"
    echo "   Run: python3 .cortex/setup-mcp.py"
    exit 1
fi

echo
echo "6️⃣  Checking for conflicting configurations..."
if [ -f ".vscode/mcp.json" ]; then
    check_warn "Old .vscode/mcp.json exists (remove it)"
    echo "   Run: rm .vscode/mcp.json"
    ((FAIL++))
else
    check_pass "No conflicting mcp.json file"
fi

echo
echo "7️⃣  Testing JSON-RPC response..."
JSONRPC_TEST=$(echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | .venv/bin/python -m cortex.mcp 2>&1 | grep -c '"name": "cortex_' || true)
if [ "$JSONRPC_TEST" -ge 20 ]; then
    check_pass "JSON-RPC returns tool list (found $JSONRPC_TEST tools)"
else
    check_fail "JSON-RPC response incomplete (found $JSONRPC_TEST tools)"
    exit 1
fi

echo
echo "8️⃣  Checking tool categories..."
python3 <<EOF
from cortex.mcp import MCPServer
import sys

server = MCPServer()
tools = server.list_tools()
categories = {}
for tool in tools:
    cat = tool.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

expected = {
    'core': 4,
    'intelligence': 3,
    'governance': 3,
    'operations': 5,
    'utilities': 9
}

all_match = True
for cat, expected_count in expected.items():
    actual_count = categories.get(cat, 0)
    if actual_count == expected_count:
        print(f"   ✅ {cat}: {actual_count} tools")
    else:
        print(f"   ❌ {cat}: {actual_count} tools (expected {expected_count})")
        all_match = False

sys.exit(0 if all_match else 1)
EOF

if [ $? -eq 0 ]; then
    check_pass "All tool categories verified"
else
    check_fail "Tool category mismatch"
    exit 1
fi

echo
echo "=" | tr '=' '=' | head -c 60; echo
echo
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))${NC}"
    echo
    echo "Next steps:"
    echo "1. Reload VS Code: Cmd+Shift+P → Developer: Reload Window"
    echo "2. Open Copilot Chat"
    echo "3. Type '@' to see all cortex_* tools"
    echo "4. Try: @cortex_verify environment"
    echo
    echo "🟢 MCP server is ready for production use"
else
    echo -e "${RED}❌ SOME CHECKS FAILED ($FAIL failures, $PASS passed)${NC}"
    echo
    echo "See errors above for resolution steps"
    exit 1
fi
