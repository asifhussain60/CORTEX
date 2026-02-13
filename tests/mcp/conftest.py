"""
MCP tests configuration and module-level skip marker.
MCP infrastructure is under development in Phase 82+.
"""

import pytest

# Module-level skip for all tests in tests/mcp/
pytestmark = pytest.mark.skip(reason="MCP tools and infrastructure implementation pending Phase 82+ (tool registry, metrics, health checks, refactoring operations)")
