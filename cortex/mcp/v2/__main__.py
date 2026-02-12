"""
CORTEX MCP v2 - Module Entry Point

Allows running MCP server via:
    python -m cortex.mcp.v2

AC_START: AC-WAVE100-S3-002
"""

import asyncio
import sys
import logging

from cortex.mcp.v2.server import MCPServerV2
from cortex.mcp.v2.tools import register_all_tools
from cortex.mcp.v2.registry import get_registry


def setup_logging() -> None:
    """Configure logging for MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )


def main() -> int:
    """
    Main entry point for MCP server.
    
    Returns:
        Exit code
    """
    setup_logging()
    logger = logging.getLogger("cortex.mcp.v2")
    
    logger.info("Starting CORTEX MCP v2 Server...")
    
    # Register all tool implementations
    registry = get_registry()
    count = register_all_tools(registry)
    logger.info(f"Registered {count} tool implementations")
    
    # Create and run server
    server = MCPServerV2()
    
    try:
        server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# AC_COMPLETE: AC-WAVE100-S3-002 ✅ Module entry point
