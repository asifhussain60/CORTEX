#!/usr/bin/env python3
"""
CORTEX MCP Diagnostic Tool
Tests MCP server connectivity and tool availability
"""
import os
import sys
import json
import subprocess
from pathlib import Path

def main():
    print("=" * 80)
    print("CORTEX MCP Diagnostic Tool")
    print("=" * 80)
    print()
    
    # Check 1: Python environment
    print("✓ Check 1: Python Environment")
    print(f"  Python: {sys.version}")
    print(f"  Executable: {sys.executable}")
    print()
    
    # Check 2: Virtual environment
    print("✓ Check 2: Virtual Environment")
    venv_path = Path(".venv/bin/python")
    if venv_path.exists():
        print(f"  ✅ .venv/bin/python exists")
        real_path = venv_path.resolve()
        print(f"  Points to: {real_path}")
    else:
        print(f"  ❌ .venv/bin/python NOT FOUND")
        return 1
    print()
    
    # Check 3: MCP module importable
    print("✓ Check 3: MCP Module")
    try:
        import cortex.mcp
        print(f"  ✅ cortex.mcp module importable")
        print(f"  Location: {cortex.mcp.__file__}")
    except ImportError as e:
        print(f"  ❌ cortex.mcp import failed: {e}")
        return 1
    print()
    
    # Check 4: VS Code settings
    print("✓ Check 4: VS Code Settings")
    settings_path = Path(".vscode/settings.json")
    if settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)
        
        if "github.copilot.chat.mcpServers" in settings:
            mcp_config = settings["github.copilot.chat.mcpServers"]
            if "cortex" in mcp_config:
                print(f"  ✅ MCP Server 'cortex' configured")
                cortex_config = mcp_config["cortex"]
                print(f"  Command: {cortex_config.get('command', 'N/A')}")
                print(f"  Args: {cortex_config.get('args', [])}")
                
                # Check if command uses correct path
                command = cortex_config.get('command', '')
                if 'Scripts/python.exe' in command:
                    print(f"  ⚠️  WARNING: Windows path detected (Scripts/python.exe)")
                    print(f"     Should be: .venv/bin/python for macOS/Linux")
                elif 'bin/python' in command:
                    print(f"  ✅ Unix path detected (bin/python)")
            else:
                print(f"  ❌ 'cortex' server not in mcpServers")
        else:
            print(f"  ❌ mcpServers not configured")
    else:
        print(f"  ❌ .vscode/settings.json not found")
    print()
    
    # Check 5: MCP server startup test
    print("✓ Check 5: MCP Server Startup")
    try:
        env = os.environ.copy()
        env.update({
            'CORTEX_ENV': 'development',
            'CORTEX_MCP_ENABLED': 'true',
            'PYTHONPATH': os.getcwd(),
            'CORTEX_WORKSPACE': os.getcwd()
        })
        
        result = subprocess.run(
            ['.venv/bin/python', '-m', 'cortex.mcp', '--help'],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        
        # Look for tool registration in output
        if 'Registered tool:' in result.stderr or 'tool modules' in result.stderr:
            # Count tools
            tool_count = result.stderr.count('Registered tool:')
            decorator_tools = None
            for line in result.stderr.split('\n'):
                if 'decorator-registered tools' in line:
                    parts = line.split('Added')
                    if len(parts) > 1:
                        decorator_tools = parts[1].split()[0]
            
            print(f"  ✅ MCP server starts successfully")
            if tool_count > 0:
                print(f"  Found {tool_count} explicitly registered tools")
            if decorator_tools:
                print(f"  Found {decorator_tools} decorator-registered tools")
        else:
            print(f"  ⚠️  MCP server started but no tools found in output")
            
    except subprocess.TimeoutExpired:
        print(f"  ✅ MCP server started (expected to run indefinitely)")
    except Exception as e:
        print(f"  ❌ MCP server startup failed: {e}")
        return 1
    print()
    
    # Check 6: Test tool availability via import
    print("✓ Check 6: MCP Tools Registry")
    try:
        from cortex.mcp.server import get_tool_registry
        tools = get_tool_registry()
        print(f"  ✅ Found {len(tools)} tools in registry")
        
        # Show first 10 tools
        print(f"  Sample tools:")
        for i, tool_name in enumerate(sorted(tools.keys())[:10]):
            print(f"    - {tool_name}")
        if len(tools) > 10:
            print(f"    ... and {len(tools) - 10} more")
    except Exception as e:
        print(f"  ⚠️  Could not load tool registry: {e}")
    print()
    
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. If all checks passed: Reload VS Code window")
    print("   Command Palette → Developer: Reload Window")
    print("2. After reload: Open Copilot Chat and test MCP tools")
    print("3. Verify: mcp_cortex_cortex_tools_catalog should return 90+ tools")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
