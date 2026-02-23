"""COMPAT shim — cortex.orchestrators.health.intelligence → cortex.mcp.tools.intelligence.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/mcp/tools/intelligence.py.
"""
# noqa: F401
from cortex.mcp.tools.intelligence import CortexLens, CortexKnowledge, CortexGit

__all__ = ["CortexLens", "CortexKnowledge", "CortexGit"]
