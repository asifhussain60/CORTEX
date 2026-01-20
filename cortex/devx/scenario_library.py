"""Scenario Library

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum


class ScenarioCategory(Enum):
    """Scenario categories."""
    SMOKE = "smoke"
    REGRESSION = "regression"
    INTEGRATION = "integration"
    E2E = "e2e"


@dataclass
class ScenarioResult:
    """Scenario execution result."""
    scenario_id: str
    passed: bool
    duration_ms: float = 0.0


@dataclass
class ScenarioInput:
    """Scenario input data."""
    input_type: str
    data: dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class Scenario:
    """Test scenario."""
    name: str
    steps: list = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []


class ScenarioStatus(Enum):
    """Scenario execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


from typing import List

class ScenarioLibrary:
    """Library of test scenarios."""
    
    def get_scenarios(self) -> List[str]:
        """Get available scenarios."""
        return []
    
    def run_scenario(self, scenario_id: str) -> ScenarioResult:
        """Run a scenario."""
        return ScenarioResult(scenario_id=scenario_id, passed=True)


@dataclass
class ExpectedOutput:
    """Expected output for scenario validation."""
    output_type: str
    expected_value: any = None
    tolerance: float = 0.0


@dataclass
class ScenarioSnapshot:
    """Snapshot of scenario execution state."""
    snapshot_id: str
    scenario_id: str
    state: dict = field(default_factory=dict)
    timestamp: float = 0.0

__all__ = ["ScenarioCategory", "ScenarioResult", "ScenarioStatus", "ExpectedOutput", "ScenarioSnapshot", "ScenarioLibrary"]
