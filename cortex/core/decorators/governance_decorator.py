"""COMPAT shim — cortex.core.decorators.governance_decorator → cortex.core.core.decorators.governance_decorator.

Phase 58-B: Canonical implementation lives in cortex/core/core/decorators/governance_decorator.py.
"""
# noqa: F401
from cortex.core.core.decorators.governance_decorator import (
    governance_enforced,
    audit_logged,
    governance_with_audit,
)

__all__ = ["governance_enforced", "audit_logged", "governance_with_audit"]
