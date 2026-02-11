"""
Orchestrator Composition Package

Provides composition and delegation patterns for orchestrator workflows.

Author: Asif Hussain
"""

from .composition_engine import (
    ComposedOrchestrator,
    CompositionPattern,
    DelegationResult,
)
from .delegation_handler import (
    DelegationContext,
    DelegationHandler,
)

__all__ = [
    "CompositionPattern",
    "ComposedOrchestrator",
    "DelegationResult",
    "DelegationHandler",
    "DelegationContext",
]
