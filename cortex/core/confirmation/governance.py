"""COMPAT shim — cortex.core.confirmation.governance → cortex.mcp.tools.governance.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/mcp/tools/governance.py.
"""
# noqa: F401
from cortex.mcp.tools.governance import CortexGovernance, CortexValidate, CortexLoad, CortexValidateRequest

__all__ = ["CortexGovernance", "CortexValidate", "CortexLoad", "CortexValidateRequest"]
