"""
Unified Intelligence Context — compat shim (Phase 107 Sub-Phase A).

Canonical definitions now live in:
  cortex/intelligence/models/context.py

This file re-exports ALL public names so existing callers continue to work
without modification (zero breaking changes, CORE-035).

Authority: GAP-107-02
"""
# ruff: noqa: F401 — intentional re-exports for backward compatibility
from cortex.intelligence.models.context import (  # noqa: F401
    CORTEXKnowledge,
    CompanyKnowledge,
    LENSIntelligence,
    SynthesisResult,
    UnifiedIntelligenceContext,
)

_COMPAT_MARKER = (
    "Phase 107 — unified_intelligence_context.py is now a compat shim. "
    "Use cortex.intelligence.models.context."
)
