"""
CORTEX Toolkit - Centralized Utility Package

This package consolidates scattered utility scripts from .cortex-runtime/ and scripts/
directories into a unified, MCP-exposed, testable toolkit.

**Module Structure:**
- diagnostics: MCP health checks, environment diagnostics
- setup: Cross-platform setup verification
- cleanup: Automated cleanup and vacuum operations
- validation: Governance and production readiness checks
- analysis: Trace analysis and orchestrator auditing

**Authority:** Phase 90 (Toolkit Centralization)
**Author:** Asif Hussain
**Created:** 2026-02-16
"""

# Module registry for discovery
TOOLKIT_MODULES = {
    "diagnostics": "cortex.tools.toolkit.diagnostics",
    "setup": "cortex.tools.toolkit.setup",
    "cleanup": "cortex.tools.toolkit.cleanup",
    "validation": "cortex.tools.toolkit.validation",
    "analysis": "cortex.tools.toolkit.analysis",
}

# MCP tool mapping
MCP_TOOLS = {
    "toolkit_diagnose": "diagnostics",
    "toolkit_verify": "setup",
    "toolkit_cleanup": "cleanup",
    "toolkit_validate": "validation",
    "toolkit_analyze": "analysis",
}

__all__ = ["TOOLKIT_MODULES", "MCP_TOOLS"]
