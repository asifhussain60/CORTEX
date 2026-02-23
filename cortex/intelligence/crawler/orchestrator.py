"""COMPAT shim — cortex.intelligence.crawler.orchestrator → cortex.orchestrators.support.orchestrator.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/orchestrators/support/orchestrator.py.
"""
# noqa: F401
from cortex.orchestrators.support.orchestrator import JourneyState, Result, Ok, Err, Journey, JourneyProgress, OnboardingOrchestrator

__all__ = ["JourneyState", "Result", "Ok", "Err", "Journey", "JourneyProgress", "OnboardingOrchestrator"]
