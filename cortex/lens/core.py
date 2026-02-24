"""COMPAT shim — cortex.lens.core → cortex.mcp.tools.core.

Phase 65 S6: Deprecated. Canonical implementation at cortex/mcp/tools/core.py.
"""
import warnings

__deprecated__ = True

warnings.warn(
    "cortex.lens.core is deprecated (Phase 65 S6). Use cortex.mcp.tools.core instead.",
    DeprecationWarning,
    stacklevel=2,
)

# noqa: F401
from cortex.mcp.tools.core import CortexProcessRequest, CortexChallenge, CortexClassify, CortexRequestLifecycle  # noqa: E402

__all__ = ["CortexProcessRequest", "CortexChallenge", "CortexClassify", "CortexRequestLifecycle"]
