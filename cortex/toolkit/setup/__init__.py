"""
CORTEX Toolkit - Setup Module

Consolidates setup verification scripts.

**Consolidated Scripts:**
- .cortex/verify-setup.py
- .cortex/verify-autonomous-setup.py
- .cortex/setup-mcp.py (verification functions)

**Authority:** Phase 90 S-90-04
"""

from cortex.toolkit.setup.verifier import SetupVerifier

__all__ = ["SetupVerifier"]
