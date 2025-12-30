"""
Execution mode management for CORTEX 4.0

Provides adaptive execution modes:
- Autonomous: Full E2E with self-healing (default)
- Supervised: Auto-validate, manual approval
- Human-in-loop: Pause after each step (learning/debugging)
"""

from .execution_mode import ExecutionMode
from .execution_mode_manager import ExecutionModeManager

__all__ = [
    "ExecutionMode",
    "ExecutionModeManager",
]
