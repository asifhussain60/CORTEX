"""COMPAT shim — cortex.intelligence.error_intelligence → cortex.intelligence.analysis.error_intelligence

The canonical implementation moved to cortex/intelligence/analysis/error_intelligence.py
as part of Phase 117-c (Intelligence Diamond flatten, GAP-117-08/09).
Retained for backward compatibility (CORE-035 compat exception).
Created: 2026-03-03  |  Review after: 2026-06-03
"""
from cortex.intelligence.analysis.error_intelligence import *  # noqa: F401, F403
