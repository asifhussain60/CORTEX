"""
PHASE-08: Business Domain Orchestrator Package

Business domain-specific orchestrator implementations.

"""

from cortex.orchestrators.domain.business.plugins import (
    DomainPlugin,
    DomainPluginRegistry,
    PluginMetadata,
)

from cortex.orchestrators.domain.business.business_base import BusinessDomainOrchestrator
from cortex.orchestrators.domain.business.context import (
    DomainContext,
    DomainContextManager,
)
from cortex.orchestrators.domain.business.ecommerce import EcommerceOrchestrator
from cortex.orchestrators.domain.business.financial import FinancialOrchestrator
from cortex.orchestrators.domain.business.healthcare import HealthcareOrchestrator
from cortex.orchestrators.domain.business.validation import (
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
