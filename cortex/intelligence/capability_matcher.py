"""COMPAT shim — intelligence.capability_matcher → intelligence.intelligence_capability_matcher (Phase 60).

Canonical: cortex/intelligence/intelligence_capability_matcher.py
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .intelligence_capability_matcher import (  # noqa: F401
    MatchQuality,
    AgentMetadata,
    CapabilityMatch,
    CapabilityMatcher,
)
from .intelligence_capability_matcher import *  # noqa: F401, F403
