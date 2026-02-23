"""COMPAT shim — cortex.core.mutation_guard → cortex.core.core.mutation_guard.

Phase 58: Canonical implementation lives in cortex/core/core/mutation_guard.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.mutation_guard import ACCompletenessValidator, ImmutabilityPolicy, MutationAttempt, MutationGuard, MutationResult, MutationType, PhaseImmutabilityValidator, RuleImmutabilityValidator

__all__ = ["ACCompletenessValidator", "ImmutabilityPolicy", "MutationAttempt", "MutationGuard", "MutationResult", "MutationType", "PhaseImmutabilityValidator", "RuleImmutabilityValidator"]
