"""
CORTEX Security Module - Unified vulnerability management framework

Provides:
- Vulnerability models (canonical, multi-tool)
- SecurityVulnerabilityOrchestrator (canonical orchestrator)
- RemediationRulesRegistry (pattern-based fixes)
- VulnerabilityOrchestrationGateway (CORTEX integration)
"""

from cortex.infrastructure.security.vulnerability_models import (
    RemediationBatch,
    RemediationResult,
    RemediationRule,
    RemediationStatus,
    RemediationType,
    Severity,
    VulnerabilityFinding,
    VulnerabilityScanResult,
)
from cortex.infrastructure.security.remediation_rules import (
    RemediationRulesRegistry,
    get_registry,
)
from cortex.infrastructure.security.vulnerability_orchestration_gateway import (
    VulnerabilityOrchestrationGateway,
    get_vulnerability_gateway,
)

# Lazy imports for orchestrator to avoid circular dependencies
def __getattr__(name):
    if name == "SecurityVulnerabilityOrchestrator":
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import (
            SecurityVulnerabilityOrchestrator,
        )
        return SecurityVulnerabilityOrchestrator
    elif name == "VulnerabilityAction":
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import (
            VulnerabilityAction,
        )
        return VulnerabilityAction
    elif name == "RemediationHandler":
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import (
            RemediationHandler,
        )
        return RemediationHandler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Models
    "Severity",
    "RemediationType",
    "RemediationStatus",
    "VulnerabilityFinding",
    "RemediationRule",
    "RemediationResult",
    "VulnerabilityScanResult",
    "RemediationBatch",
    # Orchestrator (lazy-loaded)
    "SecurityVulnerabilityOrchestrator",
    "VulnerabilityAction",
    "RemediationHandler",
    # Registry & Gateway
    "RemediationRulesRegistry",
    "get_registry",
    "VulnerabilityOrchestrationGateway",
    "get_vulnerability_gateway",
]
