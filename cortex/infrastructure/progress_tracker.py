"""COMPAT shim — cortex.infrastructure.progress_tracker → cortex.core.execution.progress_tracker.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/core/execution/progress_tracker.py.
"""
# noqa: F401
from cortex.core.execution.progress_tracker import ProgressSnapshot, ProgressTracker

__all__ = ["ProgressSnapshot", "ProgressTracker"]
