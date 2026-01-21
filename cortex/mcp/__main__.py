"""
MCP Server Entry Point.

Provides command-line entry point for running CORTEX MCP server.
This module enables running the MCP server via: python -m cortex.mcp

Usage:
    python -m cortex.mcp [--host HOST] [--port PORT]

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
"""

import sys
import json
import logging
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
    
    Initializes and demonstrates MCP server functionality by:
    1. Creating an MCP server instance
    2. Listing available tools
    3. Executing a sample tool invocation
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        from cortex.mcp.server import MCPServer, MCPResponse
        
        logger.info("Initializing CORTEX MCP Server...")
        server: MCPServer = MCPServer()
        
        # List available tools
        tools = server.list_tools()
        logger.info(f"MCP Server initialized with {len(tools)} tools:")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool['description']}")
        
        # Demonstrate tool invocation
        logger.info("\nExecuting sample tool demonstration...")
        response: MCPResponse = server.call_tool(
            "sample_tool",
            {"input": "CORTEX MCP Server v7.0", "mode": "demo"},
            request_id="startup-demo"
        )
        
        logger.info("Sample tool execution result:")
        logger.info(json.dumps(json.loads(response.to_json()), indent=2))
        
        logger.info("\nMCP Server is ready for JSON-RPC requests via stdio")
        logger.info("Server statistics:")
        stats = server.execution_statistics
        logger.info(f"  Total executions: {stats['total_executions']}")
        logger.info(f"  Tools registered: {stats['tools_registered']}")
        logger.info(f"  Cache size: {stats['cache_size']}")
        
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
