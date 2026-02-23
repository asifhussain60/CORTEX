"""COMPAT shim — cortex.intelligence.crawler.pipeline → cortex.orchestrators.health.pipeline.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/orchestrators/health/pipeline.py.
"""
# noqa: F401
from cortex.orchestrators.health.pipeline import HealthVacuumPipeline

__all__ = ["HealthVacuumPipeline"]
