"""
Decorators - Governance, Audit, Orchestration

Auto-wired decorators for governance, audit logging, and orchestrator registration.

Available decorators:
- @governance_enforced: Validates governance rules before execution
- @audit_logged: Records operation to audit log with hash chain
- @governance_with_audit: Composite decorator combining both
- @orchestrator: Auto-registers orchestrator in global registry

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.core.decorators.governance_decorator import (
    governance_enforced,
    audit_logged,
    governance_with_audit,
)
from src.core.decorators.orchestrator_decorator import (
    orchestrator,
    get_registered_orchestrators,
    get_orchestrator_by_domain,
    get_orchestrators_by_domain,
    is_orchestrator,
    clear_orchestrator_registry,
)

__all__ = [
    "governance_enforced",
    "audit_logged",
    "governance_with_audit",
]
