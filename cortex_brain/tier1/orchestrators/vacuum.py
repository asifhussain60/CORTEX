"""Vacuum Module

Author: CORTEX Framework
"""

from enum import Enum

class OrchestratorState(str, Enum):
    """Orchestrator states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"

__all__ = ["OrchestratorState"]
