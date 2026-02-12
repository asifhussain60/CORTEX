"""
MCP Server Entry Point.

Provides command-line entry point for running CORTEX MCP server.
This module enables running the MCP server via: python -m cortex.mcp

Usage:
    python -m cortex.mcp [--host HOST] [--port PORT]

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
"""

import json
import logging
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main entry point for MCP server.

    Runs CORTEX MCP v2 server with stdio transport for Copilot integration.
    Handles JSON-RPC 2.0 requests via stdin/stdout.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        # Use MCP v2 by default (WAVE-100)
        from cortex.mcp.v2 import MCPServerV2

        logger.info("Initializing CORTEX MCP Server v2 with stdio transport...")
        logger.info("Using 24 production tools (75% reduction from v1)")
        
        # Create server
        server = MCPServerV2()
        
        # List available tools
        tools = server.list_tools()
        logger.info(f"MCP Server v2 initialized with {len(tools)} tools")
        
        logger.info("Starting stdio JSON-RPC transport...")
        logger.info("CORTEX MCP Server v2 ready for Copilot integration")

        # Run stdio server (blocks until terminated)
        server.run_stdio()
        return 0

    except ImportError as e:
        logger.error(f"Failed to import MCP server components: {e}")
        logger.error("Ensure CORTEX is properly installed")
        return 1
    except Exception as e:
        logger.error(f"MCP server initialization failed: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
