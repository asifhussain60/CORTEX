"""
MCP Server Entry Point - src.mcp.__main__

Allows running the MCP server via: python -m src.mcp

AC-MCP-001-01: MCP SDK Server Implementation
"""

import asyncio
from src.mcp.server_sdk import main


if __name__ == "__main__":
    asyncio.run(main())
