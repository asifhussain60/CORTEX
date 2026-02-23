"""COMPAT shim — cortex.lens.core → cortex.mcp.tools.core.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/mcp/tools/core.py.
"""
# noqa: F401
from cortex.mcp.tools.core import CortexProcessRequest, CortexChallenge, CortexClassify, CortexRequestLifecycle

__all__ = ["CortexProcessRequest", "CortexChallenge", "CortexClassify", "CortexRequestLifecycle"]
