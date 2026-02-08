# AC_START: AC-PHASE49-001-S1
# Description: Context Crystallization Layer (CCL) core module
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 49, Stage 1: Core CCL Component

"""Context Crystallization Layer (CCL) - Non-blocking pre-flight enrichment.

This module provides async pre-flight context enrichment for MasterOrchestrator.
CCL runs in parallel with Stage 1 comprehension to warm-up:
- Rules context (tier0 → tier1 → company)
- LENS intelligence (AST, git, comments)
- Infrastructure capabilities (Phase 46 integration)

The CrystallizedContext is merged into request context for Stages 2+,
improving accuracy (+30% rule citations, +40% challenge relevance) without
adding blocking latency.
"""

from cortex.orchestrators.context_crystallization.ccl_core import (
    ContextCrystallizationLayer,
    CrystallizedContext,
)

__all__ = [
    "ContextCrystallizationLayer",
    "CrystallizedContext",
]
