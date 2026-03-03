"""COMPAT shim — cortex.intelligence.intelligence_wiring_bridges → cortex.intelligence.analysis.intelligence_wiring_bridges

The canonical implementation moved to cortex/intelligence/analysis/intelligence_wiring_bridges.py
as part of Phase 117-c (Intelligence Diamond flatten, GAP-117-08/09).
Retained for backward compatibility (CORE-035 compat exception).
Created: 2026-03-03  |  Review after: 2026-06-03
"""
from cortex.intelligence.analysis.intelligence_wiring_bridges import *  # noqa: F401, F403
