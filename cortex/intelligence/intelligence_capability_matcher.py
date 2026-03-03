"""COMPAT shim — cortex.intelligence.intelligence_capability_matcher → cortex.intelligence.analysis.intelligence_capability_matcher

The canonical implementation moved to cortex/intelligence/analysis/intelligence_capability_matcher.py
as part of Phase 117-c (Intelligence Diamond flatten, GAP-117-09).
Retained for backward compatibility (CORE-035 compat exception).
Created: 2026-03-03  |  Review after: 2026-06-03
"""
from cortex.intelligence.analysis.intelligence_capability_matcher import *  # noqa: F401, F403
