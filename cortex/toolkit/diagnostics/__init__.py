"""
CORTEX Toolkit - Diagnostics Module

Consolidates MCP health checks and environment diagnostics.

**Consolidated Scripts:**
- .cortex/diagnose-mcp.py
- .cortex/verify-mcp-setup.py
- .cortex/verify-mcp-tools.py
- .cortex/verify-mcp-fix.py

**Authority:** Phase 90 S-90-03
"""

from cortex.toolkit.diagnostics.mcp_health import MCPHealthChecker

__all__ = ["MCPHealthChecker"]
