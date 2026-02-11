"""
Orchestrators Domains - Domain Classification System

Orchestrator domain classification and trait definitions.

Exports:
- DomainClassifier: Classify orchestrators into 5 domains
- Trait protocols: ComposableOrchestrator, AnalyticalOrchestrator, etc.
"""

from cortex.orchestrators.domains.domain_classifier import DomainClassifier
from cortex.orchestrators.domains.orchestrator_traits import (
    AnalyticalOrchestrator,
    ComposableOrchestrator,
    ExecutiveOrchestrator,
    IntegrativeOrchestrator,
    ValidatingOrchestrator,
    detect_cycles,
    get_reachable_traits,
    get_trait_hierarchy,
    is_dag,
)

__all__ = [
    "DomainClassifier",
    "ComposableOrchestrator",
    "AnalyticalOrchestrator",
    "ExecutiveOrchestrator",
    "ValidatingOrchestrator",
    "IntegrativeOrchestrator",
    "get_trait_hierarchy",
    "detect_cycles",
    "is_dag",
    "get_reachable_traits",
]
