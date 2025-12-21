"""
Execution mode management for CORTEX 4.0

Provides adaptive execution modes:
- Human-in-loop: Pause after each step (learning/debugging)
- Supervised: Auto-validate, manual approval (default)
- Autonomous: Full E2E with self-healing
"""

from .execution_mode import ExecutionMode
from .execution_mode_manager import ExecutionModeManager

__all__ = [
    "ExecutionMode",
    "ExecutionModeManager",
]
