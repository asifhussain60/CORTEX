"""Scenario Library

Author: CORTEX Framework
"""

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class ScenarioCategory(Enum):
    """Scenario categories."""
    SMOKE = "smoke"
    REGRESSION = "regression"
    INTEGRATION = "integration"
    E2E = "e2e"
    UNIT = "unit"


class ScenarioStatus(Enum):
    """Scenario execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ScenarioInput:
    """Scenario input data."""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "manual"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "metadata": self.metadata,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ScenarioInput":
        """Create from dictionary."""
        return cls(
            data=d.get("data", {}),
            metadata=d.get("metadata", {}),
            source=d.get("source", "manual"),
        )


@dataclass
class ExpectedOutput:
    """Expected output for scenario validation."""
    data: Optional[Dict[str, Any]] = None
    patterns: List[str] = field(default_factory=list)
    assertions: List[str] = field(default_factory=list)
    schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "patterns": self.patterns,
            "assertions": self.assertions,
            "schema": self.schema,
        }


@dataclass
class Scenario:
    """Test scenario."""
    name: str
    description: str = ""
    category: ScenarioCategory = ScenarioCategory.UNIT
    orchestrator: Optional[str] = None
    scenario_id: str = field(default_factory=lambda: f"scenario-{uuid.uuid4().hex[:8]}")
    input_data: Optional[ScenarioInput] = None
    expected: Optional[ExpectedOutput] = None
    tags: List[str] = field(default_factory=list)
    timeout_ms: int = 5000
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "orchestrator": self.orchestrator,
            "input_data": self.input_data.to_dict() if self.input_data else None,
            "expected": self.expected.to_dict() if self.expected else None,
            "tags": self.tags,
            "timeout_ms": self.timeout_ms,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Scenario":
        """Create from dictionary."""
        input_data = None
        if d.get("input_data"):
            input_data = ScenarioInput.from_dict(d["input_data"])

        expected = None
        if d.get("expected"):
            exp_data = d["expected"]
            expected = ExpectedOutput(
                data=exp_data.get("data"),
                patterns=exp_data.get("patterns", []),
                assertions=exp_data.get("assertions", []),
                schema=exp_data.get("schema"),
            )

        return cls(
            scenario_id=d["scenario_id"],
            name=d["name"],
            description=d.get("description", ""),
            category=ScenarioCategory(d.get("category", "unit")),
            orchestrator=d.get("orchestrator"),
            input_data=input_data,
            expected=expected,
            tags=d.get("tags", []),
            timeout_ms=d.get("timeout_ms", 5000),
            dependencies=d.get("dependencies", []),
            enabled=d.get("enabled", True),
        )

    def __hash__(self) -> int:
        """Make scenario hashable."""
        return hash(self.scenario_id)


@dataclass
class ScenarioResult:
    """Scenario execution result."""
    scenario_id: str
    status: ScenarioStatus
    actual_output: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    assertions_passed: int = 0
    assertions_failed: int = 0
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "status": self.status.value,
            "actual_output": self.actual_output,
            "execution_time_ms": self.execution_time_ms,
            "assertions_passed": self.assertions_passed,
            "assertions_failed": self.assertions_failed,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class ScenarioSnapshot:
    """Snapshot of scenario execution state."""
    snapshot_id: str
    scenario_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = datetime.now().timestamp()


class ScenarioLibrary:
    """Library of test scenarios."""

    def __init__(self, library_path: Optional[str] = None, auto_save: bool = True):
        """Initialize scenario library.

        Args:
            library_path: Path to save/load scenarios (directory or file)
            auto_save: Whether to auto-save on changes
        """
        if library_path:
            # Support both directory and file paths
            # Test expects Path(tmpdir), so store original if directory
            lib_path = Path(library_path)
            if lib_path.is_dir() or not lib_path.suffix:
                # It's a directory - store as-is for test compatibility
                self.library_path = lib_path
                self._file_path = lib_path / "scenarios.json"
            else:
                # It's a file
                self.library_path = lib_path
                self._file_path = lib_path
        else:
            self.library_path = None
            self._file_path = None

        self.auto_save = auto_save
        self._scenarios: Dict[str, Scenario] = {}
        self._assertions: Dict[str, Callable] = {}
        self._results_history: List[ScenarioResult] = []
        self._snapshots: Dict[str, ScenarioSnapshot] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "before_run": [],
            "after_run": [],
            "on_error": [],
        }

        if self._file_path and self._file_path.exists():
            self._load()

    @property
    def scenarios(self) -> List[Scenario]:
        """Get list of scenarios."""
        return list(self._scenarios.values())

    @property
    def count(self) -> int:
        """Get scenario count."""
        return len(self._scenarios)

    def add(self, scenario: Scenario) -> str:
        """Add scenario to library.

        Args:
            scenario: Scenario to add

        Returns:
            Scenario ID
        """
        self._scenarios[scenario.scenario_id] = scenario
        if self.auto_save:
            self._save()
        return scenario.scenario_id

    def get(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID.

        Args:
            scenario_id: Scenario ID

        Returns:
            Scenario or None
        """
        return self._scenarios.get(scenario_id)

    def remove(self, scenario_id: str) -> bool:
        """Remove scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            Whether removed
        """
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            if self.auto_save:
                self._save()
            return True
        return False

    def update(self, scenario: Scenario) -> bool:
        """Update scenario.

        Args:
            scenario: Updated scenario

        Returns:
            Whether updated
        """
        if scenario.scenario_id in self._scenarios:
            self._scenarios[scenario.scenario_id] = scenario
            if self.auto_save:
                self._save()
            return True
        return False

    def find(self, orchestrator: Optional[str] = None,
             category: Optional[ScenarioCategory] = None,
             tags: Optional[List[str]] = None,
             enabled_only: bool = False) -> List[Scenario]:
        """Find scenarios by criteria.

        Args:
            orchestrator: Filter by orchestrator
            category: Filter by category
            tags: Filter by tags
            enabled_only: Only return enabled scenarios

        Returns:
            List of matching scenarios
        """
        results = list(self._scenarios.values())

        if orchestrator:
            results = [s for s in results if s.orchestrator == orchestrator]

        if category:
            results = [s for s in results if s.category == category]

        if tags:
            results = [s for s in results if any(t in s.tags for t in tags)]

        if enabled_only:
            results = [s for s in results if s.enabled]

        return results

    def register_assertion(self, name: str, assertion: Callable) -> "ScenarioLibrary":
        """Register custom assertion.

        Args:
            name: Assertion name
            assertion: Assertion function

        Returns:
            Self for chaining
        """
        self._assertions[name] = assertion
        return self

    def execute(self, scenario: Scenario, executor: Callable) -> ScenarioResult:
        """Execute a scenario.

        Args:
            scenario: Scenario to execute
            executor: Function to execute scenario

        Returns:
            Scenario result
        """
        import time

        result = ScenarioResult(
            scenario_id=scenario.scenario_id,
            status=ScenarioStatus.RUNNING,
        )

        # Call before_run callbacks
        for callback in self._callbacks["before_run"]:
            try:
                callback(scenario)
            except Exception:
                pass

        start_time = time.time()

        try:
            # Execute scenario
            if scenario.input_data:
                actual_output = executor(scenario.input_data.data)
            else:
                actual_output = executor({})

            result.actual_output = actual_output
            result.execution_time_ms = (time.time() - start_time) * 1000

            # Validate output
            if scenario.expected:
                if scenario.expected.data is not None:
                    if actual_output == scenario.expected.data:
                        result.status = ScenarioStatus.PASSED
                        result.assertions_passed = 1
                    else:
                        result.status = ScenarioStatus.FAILED
                        result.assertions_failed = 1
                        result.error_message = "Output mismatch"

                # Check patterns
                if scenario.expected.patterns and not result.status == ScenarioStatus.FAILED:
                    all_patterns_match = True
                    for pattern in scenario.expected.patterns:
                        output_str = str(actual_output)
                        if re.search(pattern, output_str):
                            result.assertions_passed += 1
                        else:
                            result.assertions_failed += 1
                            all_patterns_match = False

                    if all_patterns_match:
                        result.status = ScenarioStatus.PASSED
                    else:
                        result.status = ScenarioStatus.FAILED

                # Check custom assertions
                if scenario.expected.assertions and not result.status == ScenarioStatus.FAILED:
                    all_assertions_pass = True
                    for assertion_name in scenario.expected.assertions:
                        if assertion_name in self._assertions:
                            try:
                                if self._assertions[assertion_name](actual_output, scenario.expected.data):
                                    result.assertions_passed += 1
                                else:
                                    result.assertions_failed += 1
                                    all_assertions_pass = False
                            except Exception as e:
                                result.assertions_failed += 1
                                all_assertions_pass = False
                                result.error_message = str(e)

                    if all_assertions_pass:
                        result.status = ScenarioStatus.PASSED
                    else:
                        result.status = ScenarioStatus.FAILED
            else:
                result.status = ScenarioStatus.PASSED

        except Exception as e:
            result.status = ScenarioStatus.ERROR
            result.error_message = str(e)
            result.execution_time_ms = (time.time() - start_time) * 1000

            # Call on_error callbacks
            for callback in self._callbacks["on_error"]:
                try:
                    callback(scenario, e)
                except Exception:
                    pass

        # Store result
        self._results_history.append(result)

        # Call after_run callbacks
        for callback in self._callbacks["after_run"]:
            try:
                callback(scenario, result)
            except Exception:
                pass

        return result

    def run(self, executor: Callable, orchestrator: Optional[str] = None) -> List[ScenarioResult]:
        """Run multiple scenarios.

        Args:
            executor: Executor function
            orchestrator: Filter by orchestrator (optional)

        Returns:
            List of results
        """
        # Find scenarios to run
        if orchestrator:
            scenarios = self.find(orchestrator=orchestrator)
        else:
            scenarios = list(self._scenarios.values())

        results = []
        executed = set()

        for scenario in scenarios:
            # Check dependencies
            if scenario.dependencies:
                dep_failed = False
                for dep_id in scenario.dependencies:
                    if dep_id not in executed:
                        # Dependency not executed, skip
                        result = ScenarioResult(
                            scenario_id=scenario.scenario_id,
                            status=ScenarioStatus.SKIPPED,
                            error_message=f"Dependency {dep_id} not executed",
                        )
                        results.append(result)
                        dep_failed = True
                        break

                    # Check if dependency passed
                    dep_result = next((r for r in results if r.scenario_id == dep_id), None)
                    if dep_result and dep_result.status != ScenarioStatus.PASSED:
                        result = ScenarioResult(
                            scenario_id=scenario.scenario_id,
                            status=ScenarioStatus.SKIPPED,
                            error_message=f"Dependency {dep_id} failed",
                        )
                        results.append(result)
                        dep_failed = True
                        break

                if dep_failed:
                    continue

            result = self.execute(scenario, executor)
            results.append(result)
            executed.add(scenario.scenario_id)

        return results

    def on_before_run(self, callback: Callable) -> "ScenarioLibrary":
        """Register before_run callback."""
        self._callbacks["before_run"].append(callback)
        return self

    def on_after_run(self, callback: Callable) -> "ScenarioLibrary":
        """Register after_run callback."""
        self._callbacks["after_run"].append(callback)
        return self

    def on_error(self, callback: Callable) -> "ScenarioLibrary":
        """Register error callback."""
        self._callbacks["on_error"].append(callback)
        return self

    def create_snapshot(self, scenario_id: str, state: Optional[Dict[str, Any]] = None,
                       baseline: bool = False) -> ScenarioSnapshot:
        """Create snapshot of scenario state.

        Args:
            scenario_id: Scenario ID
            state: State dict (optional, uses latest result if not provided)
            baseline: Whether this is a baseline snapshot

        Returns:
            Snapshot
        """
        snapshot_id = f"snapshot-{uuid.uuid4().hex[:8]}"

        # If state not provided, get from latest result
        if state is None:
            recent_results = [r for r in self._results_history if r.scenario_id == scenario_id]
            if recent_results:
                latest = recent_results[-1]
                state = {
                    "output": latest.actual_output,
                    "status": latest.status.value,
                    "execution_time_ms": latest.execution_time_ms,
                }
            else:
                state = {}

        # Add baseline flag and checksum to state
        if baseline:
            state["_baseline"] = True
        state["_checksum"] = hash(json.dumps(state, sort_keys=True))

        snapshot = ScenarioSnapshot(
            snapshot_id=snapshot_id,
            scenario_id=scenario_id,
            state=state,
        )

        # Add additional attributes for tests
        snapshot.baseline = baseline
        snapshot.checksum = state["_checksum"]

        self._snapshots[snapshot_id] = snapshot
        return snapshot

    def compare_to_baseline(self, scenario_id: str, baseline_snapshot_id: Optional[str] = None) -> Dict[str, Any]:
        """Compare scenario result to baseline snapshot.

        Args:
            scenario_id: Scenario ID
            baseline_snapshot_id: Baseline snapshot ID (optional, finds baseline if not provided)

        Returns:
            Comparison result
        """
        # Find baseline if not provided
        if baseline_snapshot_id is None:
            for sid, snap in self._snapshots.items():
                if snap.scenario_id == scenario_id and snap.state.get("_baseline"):
                    baseline_snapshot_id = sid
                    break

        if baseline_snapshot_id not in self._snapshots:
            return {"error": "Baseline snapshot not found"}

        # Get most recent result for scenario
        recent_results = [r for r in self._results_history if r.scenario_id == scenario_id]
        if not recent_results:
            return {"error": "No results for scenario"}

        latest_result = recent_results[-1]
        baseline = self._snapshots[baseline_snapshot_id]

        output_match = latest_result.actual_output == baseline.state.get("output")
        regression_detected = (
            latest_result.execution_time_ms > baseline.state.get("execution_time_ms", 0) * 1.5
        )

        return {
            "scenario_id": scenario_id,
            "output_match": output_match,
            "regression_detected": regression_detected,
            "differences": {},  # Could add detailed diff here
        }

    def get_results(self, scenario_id: str) -> List[ScenarioResult]:
        """Get results history for a scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            List of results
        """
        return [r for r in self._results_history if r.scenario_id == scenario_id]

    def get_results_history(self, scenario_id: Optional[str] = None) -> List[ScenarioResult]:
        """Get results history.

        Args:
            scenario_id: Filter by scenario ID (optional)

        Returns:
            List of results
        """
        if scenario_id:
            return [r for r in self._results_history if r.scenario_id == scenario_id]
        return self._results_history.copy()

    def summary(self) -> Dict[str, Any]:
        """Get library summary.

        Returns:
            Summary dict
        """
        total = len(self._scenarios)
        enabled = len([s for s in self._scenarios.values() if s.enabled])

        results = self._results_history
        passed = len([r for r in results if r.status == ScenarioStatus.PASSED])
        failed = len([r for r in results if r.status == ScenarioStatus.FAILED])

        # Count by category
        by_category = {}
        for scenario in self._scenarios.values():
            cat = scenario.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        # Count by orchestrator
        by_orchestrator = {}
        for scenario in self._scenarios.values():
            if scenario.orchestrator:
                by_orchestrator[scenario.orchestrator] = by_orchestrator.get(scenario.orchestrator, 0) + 1

        return {
            "total_scenarios": total,
            "enabled_scenarios": enabled,
            "total_executions": len(results),
            "passed": passed,
            "failed": failed,
            "by_category": by_category,
            "by_orchestrator": by_orchestrator,
        }

    def _save(self) -> None:
        """Save scenarios to file."""
        if not self._file_path:
            return

        data = {
            "scenarios": [s.to_dict() for s in self._scenarios.values()],
        }

        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        """Load scenarios from file."""
        if not self._file_path or not self._file_path.exists():
            return

        with open(self._file_path, 'r') as f:
            data = json.load(f)

        for scenario_dict in data.get("scenarios", []):
            scenario = Scenario.from_dict(scenario_dict)
            self._scenarios[scenario.scenario_id] = scenario


__all__ = [
    "ScenarioCategory",
    "ScenarioStatus",
    "ScenarioInput",
    "ExpectedOutput",
    "Scenario",
    "ScenarioResult",
    "ScenarioSnapshot",
    "ScenarioLibrary",
]
