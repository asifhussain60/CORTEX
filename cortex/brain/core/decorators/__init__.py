"""
Decorators - Governance, Audit, Orchestration

Auto-wired decorators for governance, audit logging, and orchestrator registration.

Available decorators:
- @governance_enforced: Validates governance rules before execution
- @audit_logged: Records operation to audit log with hash chain
- @governance_with_audit: Composite decorator combining both
- @orchestrator: Auto-registers orchestrator in global registry

Author: Asif Hussain
"""

from cortex.brain.core.decorators.governance_decorator import (
    audit_logged,
    governance_enforced,
    governance_with_audit,
)
from cortex.brain.core.decorators.orchestrator_decorator import (
    clear_orchestrator_registry,
    get_orchestrator_by_domain,
    get_orchestrators_by_domain,
    get_registered_orchestrators,
    is_orchestrator,
    orchestrator,
)

__all__ = [
    "governance_enforced",
    "audit_logged",
    "governance_with_audit",
]
