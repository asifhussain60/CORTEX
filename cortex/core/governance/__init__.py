"""cortex.core.governance — Domain-specific governance redirect.

SCOPE: This is NOT a duplicate of cortex/governance/ (the canonical enforcement namespace).
This sub-package provides domain-scoped governance utilities used by the intelligence
memory tiers. Specifically, it wraps the tier2_adaptive governance components.

CANONICAL ENFORCEMENT: cortex/governance/enforcement/ + cortex/orchestrators/core/enforcement_orchestrator.py
THIS MODULE: Domain-specific governance context + rule applicability for memory tiers.

Phase 102-B note: This package is documented as domain-specific (not canonical enforcement).
It redirects to cortex.intelligence.memory.tier2_adaptive.governance.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

# All governance logic is in cortex/intelligence/tier2/governance/
from cortex.intelligence.memory.tier2_adaptive.governance.context_extractor import *  # noqa: F401, F403
from cortex.intelligence.memory.tier2_adaptive.governance.rule_applicability import *  # noqa: F401, F403

__all__ = ["ContextExtractor", "GovernanceContext", "RuleApplicabilityEngine"]
