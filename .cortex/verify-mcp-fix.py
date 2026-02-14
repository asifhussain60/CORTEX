#!/usr/bin/env python3
"""
MCP Tool Response Format Fix - Verification
Date: 2026-02-13
Issue: VS Code Copilot error "o.content is not iterable"
Fix: Wrap tool results in MCP protocol 'content' array format
"""

import subprocess
import json
import sys

# Test tools
TEST_TOOLS = [
    {
        "name": "cortex_total_recall",
        "params": {"operation": "discover"}
    },
    {
        "name": "cortex_tools_catalog",
        "params": {"operation": "list"}
    },
    {
        "name": "cortex_verify",
        "params": {"operation": "environment"}
    },
]

def test_tool(tool_name: str, params: dict) -> bool:
    """Test a single tool invocation."""
    request = {
        "jsonrpc": "2.0",
        "id": "test",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        }
    }
    
    proc = subprocess.Popen(
        ['.venv/bin/python', '-m', 'cortex.mcp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = proc.communicate(input=json.dumps(request) + "\n", timeout=5)
    
    # Parse response
    for line in stdout.strip().split('\n'):
        try:
            data = json.loads(line)
            if 'result' in data:
                result = data['result']
                
                # Check for correct MCP format
                if 'content' not in result:
                    print(f"   ❌ Missing 'content' field")
                    return False
                
                if not isinstance(result['content'], list):
                    print(f"   ❌ 'content' is not an array")
                    return False
                
                if len(result['content']) == 0:
                    print(f"   ❌ 'content' array is empty")
                    return False
                
                # Check first content item
                item = result['content'][0]
                if 'type' not in item or item['type'] != 'text':
                    print(f"   ❌ Content item missing 'type: text'")
                    return False
                
                if 'text' not in item:
                    print(f"   ❌ Content item missing 'text' field")
                    return False
                
                # Try to parse the text as JSON (should be tool result)
                try:
                    tool_result = json.loads(item['text'])
                    if 'success' not in tool_result:
                        print(f"   ❌ Tool result missing 'success' field")
                        return False
                    
                    print(f"   ✅ Format valid | Success: {tool_result['success']}")
                    return True
                    
                except json.JSONDecodeError:
                    print(f"   ❌ Text is not valid JSON")
                    return False
                    
        except json.JSONDecodeError:
            continue
    
    print(f"   ❌ No valid response found")
    return False


def main():
    print("="*80)
    print("🔧 MCP Tool Response Format Verification")
    print("="*80 + "\n")
    
    print("Testing MCP protocol compliance:")
    print("Expected format:")
    print('  {"result": {"content": [{"type": "text", "text": "..."}]}}')
    print()
    
    passed = 0
    failed = 0
    
    for test in TEST_TOOLS:
        tool_name = test["name"]
        params = test["params"]
        
        print(f"📋 Testing: {tool_name}")
        print(f"   Params: {params}")
        
        if test_tool(tool_name, params):
            passed += 1
        else:
            failed += 1
        print()
    
    print("="*80)
    print(f"📊 Results: {passed}/{len(TEST_TOOLS)} passed")
    print("="*80 + "\n")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
        print("   MCP tools now return correct format for VS Code Copilot")
        print("   The 'o.content is not iterable' error should be resolved")
        print()
        print("⚠️  IMPORTANT: Reload VS Code for changes to take effect:")
        print("   Cmd+Shift+P → 'Developer: Reload Window'")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
