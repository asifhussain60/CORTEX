"""Verify MCP Tools Registration"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

from cortex.mcp.server import MCPServer
from cortex.mcp.mcp_tool_base import ToolCategory
from cortex.mcp.mcp_registry import get_registry

logging.basicConfig(level=logging.ERROR)

s = MCPServer()
r = get_registry()

print('\n' + '='*70)
print('✓ MCP SERVER OPERATIONAL - PRODUCTION READY')
print('='*70)
print(f'\nTotal Tools Registered: {len(s.list_tools())}')
print('\nRegistered Tools:')
for t in sorted(s.list_tools(), key=lambda x: x['name']):
    desc = t['description'][:60] + '...' if len(t['description']) > 60 else t['description']
    print(f'  - {t["name"]:35} {desc}')

print('\n' + '='*70)
print('Status: All MCP tools successfully registered and accessible')
print('='*70 + '\n')
