"""
Orchestrator Composition Package

Provides composition and delegation patterns for orchestrator workflows.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from .composition_engine import (
    CompositionPattern,
    ComposedOrchestrator,
    DelegationResult,
)
from .delegation_handler import (
    DelegationHandler,
    DelegationContext,
)

__all__ = [
    "CompositionPattern",
    "ComposedOrchestrator",
    "DelegationResult",
    "DelegationHandler",
    "DelegationContext",
]
