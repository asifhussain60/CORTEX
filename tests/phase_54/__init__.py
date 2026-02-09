# AC_START: AC-PHASE54-S1-S9-001
# Description: Phase 54 - Unified Intelligence Layer CCL Enhancement test module
# Author: Asif Hussain
# Date: 2026-02-09
# Phase: 54, Stage 1-9: CCL Enhancement + Intelligence Warming + Integration

"""Phase 54 Test Suite - Unified Intelligence Layer Enhancement.

This module contains comprehensive tests for Phase 54 orchestrators:
- S1-S3: CCL Enhancement (rules warming, context synthesis, pre-flight)
- S4-S6: Intelligence Warming Layer (synthesis, caching, LENS integration)
- S7-S9: Integration & Governance (orchestrator registration, enforcement, production readiness)

All tests are TDD-first, ensuring 100% passing rate before orchestrator wiring.
"""

from cortex.orchestrators.phase_49.context_crystallization_layer import (
    ContextCrystallizationLayer,
    CrystallizedContext,
)

__all__ = [
    "ContextCrystallizationLayer",
    "CrystallizedContext",
]
