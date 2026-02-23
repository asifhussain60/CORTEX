"""COMPAT shim — cortex.orchestrators.support.rollback_orchestrator → cortex.infrastructure.deployment.rollback_orchestrator.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/infrastructure/deployment/rollback_orchestrator.py.
"""
# noqa: F401
from cortex.infrastructure.deployment.rollback_orchestrator import RollbackResult, RollbackHistory, RollbackOrchestrator

__all__ = ["RollbackResult", "RollbackHistory", "RollbackOrchestrator"]
