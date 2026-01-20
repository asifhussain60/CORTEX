"""Scenario Library

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class ScenarioResult:
    """Scenario execution result."""
    scenario_id: str
    passed: bool
    duration_ms: float = 0.0

__all__ = ["ScenarioResult"]
