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

from cortex.debugging.marker_injection_engine import MarkerInjectionEngine
from cortex.debugging.auto_cleanup_manager import AutoCleanupManager

__all__ = [
    "MarkerInjectionEngine",
    "AutoCleanupManager",
]
