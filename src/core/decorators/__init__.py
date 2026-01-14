"""
Governance Decorators

Auto-wired governance decorators for automatic rule enforcement and audit logging.

Available decorators:
- @governance_enforced: Validates governance rules before execution
- @audit_logged: Records operation to audit log with hash chain
- @governance_with_audit: Composite decorator combining both

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.core.decorators.governance_decorator import (
    governance_enforced,
    audit_logged,
    governance_with_audit,
)

__all__ = [
    "governance_enforced",
    "audit_logged",
    "governance_with_audit",
]
