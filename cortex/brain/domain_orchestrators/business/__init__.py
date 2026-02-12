"""
PHASE-08: Business Domain Orchestrator Package

Business domain-specific orchestrator implementations.

"""

from cortex.brain.domain_orchestrators.business.plugins import (
    DomainPlugin,
    DomainPluginRegistry,
    PluginMetadata,
)

from cortex.brain.domain_orchestrators.business.base import BusinessDomainOrchestrator
from cortex.brain.domain_orchestrators.business.context import (
    DomainContext,
    DomainContextManager,
)
from cortex.brain.domain_orchestrators.business.ecommerce import EcommerceOrchestrator
from cortex.brain.domain_orchestrators.business.financial import FinancialOrchestrator
from cortex.brain.domain_orchestrators.business.healthcare import HealthcareOrchestrator
from cortex.brain.domain_orchestrators.business.validation import (
    DomainValidator,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
)

__all__ = [
    # Base
    "BusinessDomainOrchestrator",
    # Domain orchestrators
    "FinancialOrchestrator",
    "HealthcareOrchestrator",
    "EcommerceOrchestrator",
    # Plugin system
    "DomainPlugin",
    "DomainPluginRegistry",
    "PluginMetadata",
    # Context management
    "DomainContext",
    "DomainContextManager",
    # Validation
    "DomainValidator",
    "ValidationRule",
    "ValidationResult",
    "ValidationSeverity",
]
