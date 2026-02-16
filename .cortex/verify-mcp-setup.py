"""
CORTEX MCP Setup Verification Script
Validates that all MCP components are properly configured.
"""
import sys
from pathlib import Path

def main():
    print("=" * 80)
    print("CORTEX MCP SETUP VERIFICATION")
    print("=" * 80)
    print()
    
    # Test 1: Python version
    print("✓ TEST 1: Python Version")
    print(f"  Python: {sys.version.split()[0]}")
    print()
    
    # Test 2: Critical dependencies
    print("✓ TEST 2: Critical Dependencies")
    try:
        import yaml
        print("  ✅ pyyaml - OK")
    except ImportError as e:
        print(f"  ❌ pyyaml - FAILED: {e}")
        return False
    
    try:
        import pydantic
        print("  ✅ pydantic - OK")
    except ImportError as e:
        print(f"  ❌ pydantic - FAILED: {e}")
        return False
    
    try:
        import fastapi
        print("  ✅ fastapi - OK")
    except ImportError as e:
        print(f"  ❌ fastapi - FAILED: {e}")
        return False
    
    try:
        import websockets
        print("  ✅ websockets - OK")
    except ImportError as e:
        print(f"  ❌ websockets - FAILED: {e}")
        return False
    
    print()
    
    # Test 3: CORTEX module
    print("✓ TEST 3: CORTEX MCP Module")
    try:
        from cortex.mcp import MCPServer
        print("  ✅ cortex.mcp - OK")
    except ImportError as e:
        print(f"  ❌ cortex.mcp - FAILED: {e}")
        return False
    
    print()
    
    # Test 4: MCP Server initialization
    print("✓ TEST 4: MCP Server Initialization")
    try:
        server = MCPServer()
        tools = server.list_tools()
        print(f"  ✅ MCP Server - OK ({len(tools)} tools)")
        
        # List first 10 tools
        print("\n  Available tools:")
        for tool in tools[:10]:
            print(f"    • {tool['name']}")
        if len(tools) > 10:
            print(f"    ... and {len(tools) - 10} more")
    except Exception as e:
        print(f"  ❌ MCP Server - FAILED: {e}")
        return False
    
    print()
    
    # Test 5: VS Code configuration
    print("✓ TEST 5: VS Code Configuration")
    vscode_settings = Path(".vscode/settings.json")
    vscode_mcp = Path(".vscode/mcp.json")
    
    if vscode_settings.exists():
        print("  ✅ .vscode/settings.json - EXISTS")
    else:
        print("  ❌ .vscode/settings.json - MISSING")
        return False
    
    if vscode_mcp.exists():
        print("  ✅ .vscode/mcp.json - EXISTS")
    else:
        print("  ⚠️  .vscode/mcp.json - MISSING (will use settings.json)")
    
    print()
    
    # Summary
    print("=" * 80)
    print("✅ ALL TESTS PASSED - CORTEX MCP IS READY")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("  1. Reload VS Code (Ctrl+Shift+P → Developer: Reload Window)")
    print("  2. Verify MCP server in Copilot Chat")
    print("  3. Try: /audit or /implement commands")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
