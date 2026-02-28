"""Thin re-export — canonical implementation lives in cortex.core.execution.resilience.

Phase 92: CORE-035 compliance — single canonical implementation.
The full SilentExecutionGuard lives at cortex/core/execution/resilience/execution_guard.py.
This file exists only for backward compatibility with existing imports.
"""
from cortex.core.execution.resilience.execution_guard import (  # noqa: F401
    CheckpointFailedError,
    ExecutionResult,
    RollbackError,
    SilentExecutionGuard,
)

__all__ = [
    "CheckpointFailedError",
    "ExecutionResult",
    "RollbackError",
    "SilentExecutionGuard",
]
