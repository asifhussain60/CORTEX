"""
CORTEX Debugging Module

Provides automatic debug marker injection and cleanup capabilities.

Components:
    - MarkerInjectionEngine: Strategy-based marker injection
    - AutoCleanupManager: Automatic marker cleanup on success
    - Strategies: TestFailure, RefactorRegression, GovernanceViolation

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Execution Plan

AC-ID: AC-WAVE-R-S2-001
"""

from cortex.orchestrators.support.debugging.marker_injection_engine import MarkerInjectionEngine

__all__ = [
    "MarkerInjectionEngine",
]
