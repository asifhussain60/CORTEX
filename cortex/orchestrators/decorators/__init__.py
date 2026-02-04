"""
Orchestrator Decorators Package

Provides decorators for enhancing orchestrator functionality:
- @inject_orchestrator_context: Auto-inject visibility badges
- Future: @audit_trail, @circuit_breaker, @rate_limit

Authority: AC-UX-VISIBILITY-001 (Phase 20.2)
"""

from cortex.orchestrators.decorators.orchestrator_context_injector import (
    inject_orchestrator_context,
    OrchestratorMetadataRegistry,
    extract_orchestrator_metadata_from_wiring,
)

__all__ = [
    "inject_orchestrator_context",
    "OrchestratorMetadataRegistry",
    "extract_orchestrator_metadata_from_wiring",
]
