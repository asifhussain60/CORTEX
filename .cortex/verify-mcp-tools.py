#!/usr/bin/env python3
"""
MCP Tool Discovery Verification Script

Run this after reloading VS Code to verify all 24 tools are discoverable.

Usage:
    python .cortex/verify-mcp-tools.py
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cortex.mcp import MCPServer
from cortex.mcp.server import MCPRequest


def main():
    print("=" * 70)
    print("🔍 CORTEX MCP Tool Discovery Verification")
    print("=" * 70)
    print()
    
    # Initialize server
    print("1️⃣ Initializing MCP server...")
    server = MCPServer()
    print(f"   ✅ Server initialized: cortex-mcp v2.0.0")
    print()
    
    # Test initialize handshake
    print("2️⃣ Testing MCP initialize handshake...")
    req1 = MCPRequest(
        method='initialize',
        params={
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'}
        },
        id=1
    )
    resp1 = server.handle_request(req1)
    print(f"   ✅ Initialize successful")
    print(f"   Protocol: {resp1.result['protocolVersion']}")
    print(f"   Server: {resp1.result['serverInfo']['name']} v{resp1.result['serverInfo']['version']}")
    print()
    
    # Test tools/list
    print("3️⃣ Testing tools/list endpoint...")
    req2 = MCPRequest(method='tools/list', params={}, id=2)
    resp2 = server.handle_request(req2)
    tools = resp2.result
    
    if len(tools) != 24:
        print(f"   ❌ FAILED: Expected 24 tools, got {len(tools)}")
        return 1
    
    print(f"   ✅ All 24 tools discovered!")
    print()
    
    # Count by category
    print("4️⃣ Tools by category:")
    by_category = {}
    for tool in tools:
        cat = tool.get('category', 'unknown')
        by_category[cat] = by_category.get(cat, 0) + 1
    
    expected = {
        'core': 4,
        'intelligence': 3,
        'governance': 3,
        'operations': 5,
        'utilities': 9,
    }
    
    all_match = True
    for cat, expected_count in sorted(expected.items()):
        actual_count = by_category.get(cat, 0)
        status = "✅" if actual_count == expected_count else "❌"
        print(f"   {status} {cat}: {actual_count}/{expected_count} tools")
        if actual_count != expected_count:
            all_match = False
    print()
    
    if not all_match:
        print("❌ Category counts don't match expected values!")
        return 1
    
    # List all tools
    print("5️⃣ Complete tool list:")
    for i, tool in enumerate(tools, 1):
        name = tool['name']
        cat = tool['category']
        desc = tool['description'][:50]
        print(f"   {i:2d}. [{cat:13s}] {name}: {desc}...")
    print()
    
    print("=" * 70)
    print("✅ MCP VERIFICATION COMPLETE - ALL CHECKS PASSED")
    print("=" * 70)
    print()
    print("🎯 Next steps:")
    print("   1. Reload VS Code: Cmd+Shift+P → 'Developer: Reload Window'")
    print("   2. Open Copilot Chat")
    print("   3. Check MCP server status in bottom-right corner")
    print("   4. Try: 'list all cortex tools' to verify discovery")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
