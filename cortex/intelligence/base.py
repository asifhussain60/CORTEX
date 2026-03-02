"""
Base Intelligence Engine — compat shim (Phase 107 Sub-Phase A).

This module is now a re-export shim. The canonical definitions live in:
  cortex/intelligence/models/base_engine.py

DO NOT add logic here. Only re-exports are permitted (CORE-035).
Authority: GAP-107-01
"""
# ruff: noqa: F401 — intentional re-exports for backward compatibility
from cortex.intelligence.models.base_engine import (  # noqa: F401
    AnalysisContext,
    AnalysisResult,
    BaseIntelligenceEngine,
    EngineMetrics,
)

import logging

logger = logging.getLogger(__name__)

_COMPAT_MARKER = "Phase 107 — base.py is now a compat shim. Use cortex.intelligence.models."
