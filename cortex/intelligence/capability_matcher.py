"""COMPAT shim — intelligence.capability_matcher → intelligence.intelligence_capability_matcher (Phase 60).

Canonical: cortex/intelligence/intelligence_capability_matcher.py
Phase 109 audit: 5 active importers detected — shim retained by policy (CORE-035 compat exception).
90-day retention: created 2026-02-24, expires 2026-05-24. Review after expiry.
"""
from .intelligence_capability_matcher import (  # noqa: F401
    MatchQuality,
    AgentMetadata,
    CapabilityMatch,
    CapabilityMatcher,
)
from .intelligence_capability_matcher import *  # noqa: F401, F403
