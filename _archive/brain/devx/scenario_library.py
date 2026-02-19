"""
ODX-001-02: Scenario Library

Test case management for orchestrator development and validation.
Provides a structured library of scenarios for testing orchestrator behavior.

AC-ID: ODX-001-02
Phase: PHASE-18-ORCHESTRATOR-DEVX
TDD Status: GREEN phase

Features:
- Scenario definition and management
- Category-based organization
- Execution and result tracking
- Snapshot comparison for regression testing
"""

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)


class ScenarioCategory(Enum):
    """Category of test scenario."""
    UNIT = "unit"  # Single function/method test
    INTEGRATION = "integration"  # Multiple component interaction
    E2E = "e2e"  # End-to-end workflow
    REGRESSION = "regression"  # Regression test
    EDGE_CASE = "edge_case"  # Edge case handling
    PERFORMANCE = "performance"  # Performance benchmark
    STRESS = "stress"  # Stress test


# CONSOLIDATED: Import from cortex.devx.scenario_library
# class ScenarioStatus(Enum):
    """Execution status of scenario."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ScenarioInput:
    """Input data for a scenario.

    Attributes:
        data: Input data dictionary
        metadata: Additional input metadata
        source: Where input came from (file, generated, etc.)
    """
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
    """Expected output for scenario validation.

    Attributes:
        data: Expected output data (exact match)
        patterns: Regex patterns to match
        assertions: Custom assertion functions
        schema: JSON schema for validation
    """
    data: Optional[Dict[str, Any]] = None
    patterns: List[str] = field(default_factory=list)
    assertions: List[str] = field(default_factory=list)  # Assertion function names
    schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "patterns": self.patterns,
            "assertions": self.assertions,
            "schema": self.schema,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ExpectedOutput":
        """Create from dictionary."""
        return cls(
            data=d.get("data"),
            patterns=d.get("patterns", []),
            assertions=d.get("assertions", []),
            schema=d.get("schema"),
        )


@dataclass
class ScenarioResult:
    """Result of scenario execution.

    Attributes:
        scenario_id: ID of the executed scenario
        status: Execution status
        actual_output: Actual output from execution
        execution_time_ms: Time taken in milliseconds
        timestamp: When execution occurred
        error_message: Error message if failed
        assertions_passed: Number of assertions that passed
        assertions_failed: Number of assertions that failed
        details: Additional result details
    """
    scenario_id: str = ""
    status: ScenarioStatus = ScenarioStatus.PENDING
    actual_output: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "status": self.status.value,
            "actual_output": self.actual_output,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message,
            "assertions_passed": self.assertions_passed,
            "assertions_failed": self.assertions_failed,
            "details": self.details,
        }


@dataclass
class Scenario:
    """A test scenario for orchestrator validation.

    Attributes:
        scenario_id: Unique identifier
        name: Human-readable name
        description: Description of what scenario tests
        category: Scenario category
        orchestrator: Target orchestrator name
        input_data: Input for the scenario
        expected: Expected output/behavior
        tags: Tags for filtering
        timeout_ms: Maximum execution time
        dependencies: Other scenarios that must pass first
        enabled: Whether scenario is enabled
        created_at: When scenario was created
        updated_at: When scenario was last updated
    """
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: ScenarioCategory = ScenarioCategory.UNIT
    orchestrator: str = ""
    input_data: ScenarioInput = field(default_factory=ScenarioInput)
    expected: ExpectedOutput = field(default_factory=ExpectedOutput)
    tags: List[str] = field(default_factory=list)
    timeout_ms: int = 30000  # 30 seconds default
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __hash__(self):
        return hash(self.scenario_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "orchestrator": self.orchestrator,
            "input_data": self.input_data.to_dict(),
            "expected": self.expected.to_dict(),
            "tags": self.tags,
            "timeout_ms": self.timeout_ms,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Scenario":
        """Create from dictionary."""
        return cls(
            scenario_id=d.get("scenario_id", str(uuid.uuid4())),
            name=d.get("name", ""),
            description=d.get("description", ""),
            category=ScenarioCategory(d.get("category", "unit")),
            orchestrator=d.get("orchestrator", ""),
            input_data=ScenarioInput.from_dict(d.get("input_data", {})),
            expected=ExpectedOutput.from_dict(d.get("expected", {})),
            tags=d.get("tags", []),
            timeout_ms=d.get("timeout_ms", 30000),
            dependencies=d.get("dependencies", []),
            enabled=d.get("enabled", True),
            created_at=datetime.fromisoformat(d["created_at"]) if "created_at" in d else datetime.utcnow(),
            updated_at=datetime.fromisoformat(d["updated_at"]) if "updated_at" in d else datetime.utcnow(),
        )


@dataclass
class ScenarioSnapshot:
    """Snapshot of scenario results for regression comparison.

    Attributes:
        snapshot_id: Unique identifier
        scenario_id: ID of scenario this snapshots
        result: Result data
        timestamp: When snapshot was taken
        checksum: Data integrity hash
        baseline: Whether this is the baseline snapshot
    """
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checksum: str = ""
    baseline: bool = False

    def __post_init__(self):
        """Compute checksum."""
        if self.result and not self.checksum:
            data_str = json.dumps(self.result, sort_keys=True, default=str)
            self.checksum = hashlib.sha256(data_str.encode()).hexdigest()


class ScenarioLibrary:
    """Library of test scenarios for orchestrator development.

    Provides scenario management, execution, and regression tracking.

    Example:
        library = ScenarioLibrary(Path("scenarios"))

        # Add a scenario
        library.add(Scenario(
            name="Intent Classification Test",
            category=ScenarioCategory.UNIT,
            orchestrator="IntentRouter",
            input_data=ScenarioInput(data={"query": "Create a new file"}),
            expected=ExpectedOutput(data={"intent": "file_creation"}),
        ))

        # Run scenarios
        results = library.run(tags=["intent"])
    """

    def __init__(
        self,
        library_path: Optional[Union[str, Path]] = None,
        auto_save: bool = True,
    ):
        """Initialize scenario library.

        Args:
            library_path: Path to scenario files (or None for in-memory)
            auto_save: Whether to auto-save changes to disk
        """
        self.library_path = Path(library_path) if library_path else None
        self.auto_save = auto_save

        # Scenario storage
        self._scenarios: Dict[str, Scenario] = {}
        self._results: Dict[str, List[ScenarioResult]] = {}
        self._snapshots: Dict[str, List[ScenarioSnapshot]] = {}

        # Custom assertions
        self._assertions: Dict[str, Callable[[Any, Any], bool]] = {}

        # Execution callbacks
        self._before_run: List[Callable[[Scenario], None]] = []
        self._after_run: List[Callable[[Scenario, ScenarioResult], None]] = []

        # Load from disk if path provided
        if self.library_path and self.library_path.exists():
            self._load_from_disk()

    def _load_from_disk(self):
        """Load scenarios from disk."""
        if not self.library_path:
            return

        # Load scenarios
        scenario_files = list(self.library_path.glob("**/*.scenario.json"))
        for file_path in scenario_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    scenario = Scenario.from_dict(data)
                    self._scenarios[scenario.scenario_id] = scenario
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading scenario {file_path}: {e}")

        # Load snapshots
        snapshot_dir = self.library_path / "snapshots"
        if snapshot_dir.exists():
            for file_path in snapshot_dir.glob("*.snapshot.json"):
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        snapshot = ScenarioSnapshot(**data)
                        if snapshot.scenario_id not in self._snapshots:
                            self._snapshots[snapshot.scenario_id] = []
                        self._snapshots[snapshot.scenario_id].append(snapshot)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error loading snapshot {file_path}: {e}")

    def _save_to_disk(self):
        """Save scenarios to disk."""
        if not self.library_path or not self.auto_save:
            return

        self.library_path.mkdir(parents=True, exist_ok=True)

        # Save scenarios
        for scenario_id, scenario in self._scenarios.items():
            # Organize by category
            category_dir = self.library_path / scenario.category.value
            category_dir.mkdir(exist_ok=True)

            file_path = category_dir / f"{scenario_id}.scenario.json"
            with open(file_path, "w") as f:
                json.dump(scenario.to_dict(), f, indent=2)

    def add(self, scenario: Scenario) -> str:
        """Add a scenario to the library.

        Args:
            scenario: Scenario to add

        Returns:
            Scenario ID
        """
        self._scenarios[scenario.scenario_id] = scenario
        self._save_to_disk()
        return scenario.scenario_id

    def get(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID.

        Args:
            scenario_id: Scenario ID

        Returns:
            Scenario or None
        """
        return self._scenarios.get(scenario_id)

    def remove(self, scenario_id: str) -> bool:
        """Remove a scenario from the library.

        Args:
            scenario_id: Scenario ID

        Returns:
            True if removed
        """
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            self._save_to_disk()
            return True
        return False

    def update(self, scenario: Scenario) -> bool:
        """Update an existing scenario.

        Args:
            scenario: Updated scenario

        Returns:
            True if updated
        """
        if scenario.scenario_id in self._scenarios:
            scenario.updated_at = datetime.utcnow()
            self._scenarios[scenario.scenario_id] = scenario
            self._save_to_disk()
            return True
        return False

    def find(
        self,
        orchestrator: Optional[str] = None,
        category: Optional[ScenarioCategory] = None,
        tags: Optional[List[str]] = None,
        enabled_only: bool = True,
    ) -> List[Scenario]:
        """Find scenarios matching criteria.

        Args:
            orchestrator: Filter by orchestrator name
            category: Filter by category
            tags: Filter by tags (any match)
            enabled_only: Only return enabled scenarios

        Returns:
            List of matching scenarios
        """
        results = []

        for scenario in self._scenarios.values():
            # Filter by enabled
            if enabled_only and not scenario.enabled:
                continue

            # Filter by orchestrator
            if orchestrator and scenario.orchestrator != orchestrator:
                continue

            # Filter by category
            if category and scenario.category != category:
                continue

            # Filter by tags
            if tags:
                if not any(tag in scenario.tags for tag in tags):
                    continue

            results.append(scenario)

        return results

    def register_assertion(
        self,
        name: str,
        func: Callable[[Any, Any], bool],
    ) -> "ScenarioLibrary":
        """Register a custom assertion function.

        Args:
            name: Assertion name (referenced in ExpectedOutput.assertions)
            func: Function taking (actual, expected) and returning bool

        Returns:
            Self for method chaining
        """
        self._assertions[name] = func
        return self

    def _validate_result(
        self,
        scenario: Scenario,
        actual: Any,
    ) -> Tuple[bool, int, int, List[str]]:
        """Validate actual result against expected.

        Args:
            scenario: Scenario with expected output
            actual: Actual output

        Returns:
            Tuple of (success, passed_count, failed_count, failure_messages)
        """
        passed = 0
        failed = 0
        failures = []
        expected = scenario.expected

        # Check exact data match
        if expected.data is not None:
            if actual == expected.data:
                passed += 1
            else:
                failed += 1
                failures.append(f"Data mismatch: expected {expected.data}, got {actual}")

        # Check patterns
        import re
        actual_str = json.dumps(actual, default=str) if isinstance(actual, dict) else str(actual)
        for pattern in expected.patterns:
            if re.search(pattern, actual_str):
                passed += 1
            else:
                failed += 1
                failures.append(f"Pattern not matched: {pattern}")

        # Check custom assertions
        for assertion_name in expected.assertions:
            if assertion_name in self._assertions:
                try:
                    if self._assertions[assertion_name](actual, expected.data):
                        passed += 1
                    else:
                        failed += 1
                        failures.append(f"Assertion failed: {assertion_name}")
                except Exception as e:
                    failed += 1
                    failures.append(f"Assertion error ({assertion_name}): {e}")
            else:
                failed += 1
                failures.append(f"Unknown assertion: {assertion_name}")

        # Check JSON schema
        if expected.schema:
            try:
                import jsonschema
                jsonschema.validate(actual, expected.schema)
                passed += 1
            except ImportError:
                # jsonschema not installed, skip
                pass
            except jsonschema.ValidationError as e:
                failed += 1
                failures.append(f"Schema validation failed: {e.message}")

        success = failed == 0 and (passed > 0 or not (expected.data or expected.patterns or expected.assertions or expected.schema))
        return success, passed, failed, failures

    def execute(
        self,
        scenario: Scenario,
        executor: Callable[[Dict[str, Any]], Any],
    ) -> ScenarioResult:
        """Execute a single scenario.

        Args:
            scenario: Scenario to execute
            executor: Function that takes input data and returns output

        Returns:
            ScenarioResult with execution details
        """
        result = ScenarioResult(scenario_id=scenario.scenario_id)

        # Trigger before callbacks
        for callback in self._before_run:
            try:
                callback(scenario)
            except Exception:
                pass

        start_time = time.time()

        try:
            result.status = ScenarioStatus.RUNNING

            # Execute with timeout
            actual = executor(scenario.input_data.data)

            # Validate
            success, passed, failed, failures = self._validate_result(scenario, actual)

            result.actual_output = actual if isinstance(actual, dict) else {"result": actual}
            result.assertions_passed = passed
            result.assertions_failed = failed
            result.status = ScenarioStatus.PASSED if success else ScenarioStatus.FAILED

            if failures:
                result.error_message = "; ".join(failures)
                result.details["failures"] = failures

        except Exception as e:
            result.status = ScenarioStatus.ERROR
            result.error_message = str(e)
            result.details["traceback"] = __import__("traceback").format_exc()

        result.execution_time_ms = (time.time() - start_time) * 1000
        result.timestamp = datetime.utcnow()

        # Store result
        if scenario.scenario_id not in self._results:
            self._results[scenario.scenario_id] = []
        self._results[scenario.scenario_id].append(result)

        # Trigger after callbacks
        for callback in self._after_run:
            try:
                callback(scenario, result)
            except Exception:
                pass

        return result

    def run(
        self,
        executor: Callable[[Dict[str, Any]], Any],
        orchestrator: Optional[str] = None,
        category: Optional[ScenarioCategory] = None,
        tags: Optional[List[str]] = None,
        scenario_ids: Optional[List[str]] = None,
    ) -> List[ScenarioResult]:
        """Run multiple scenarios.

        Args:
            executor: Function that takes input data and returns output
            orchestrator: Filter by orchestrator
            category: Filter by category
            tags: Filter by tags
            scenario_ids: Specific scenarios to run

        Returns:
            List of ScenarioResults
        """
        # Get scenarios to run
        if scenario_ids:
            scenarios = [self._scenarios[sid] for sid in scenario_ids if sid in self._scenarios]
        else:
            scenarios = self.find(orchestrator, category, tags)

        # Sort by dependencies (simple topological sort)
        scenarios = self._sort_by_dependencies(scenarios)

        results = []
        passed_ids: Set[str] = set()

        for scenario in scenarios:
            # Check dependencies
            deps_met = all(dep in passed_ids for dep in scenario.dependencies)

            if not deps_met:
                result = ScenarioResult(
                    scenario_id=scenario.scenario_id,
                    status=ScenarioStatus.SKIPPED,
                    error_message="Dependencies not met",
                )
                results.append(result)
                continue

            # Execute
            result = self.execute(scenario, executor)
            results.append(result)

            if result.status == ScenarioStatus.PASSED:
                passed_ids.add(scenario.scenario_id)

        return results

    def _sort_by_dependencies(self, scenarios: List[Scenario]) -> List[Scenario]:
        """Sort scenarios by dependencies (topological sort).

        Args:
            scenarios: List of scenarios

        Returns:
            Sorted list
        """
        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}

        for s in scenarios:
            graph[s.scenario_id] = list(s.dependencies)
            in_degree[s.scenario_id] = len(s.dependencies)

        # Kahn's algorithm
        result = []
        queue = [sid for sid, deg in in_degree.items() if deg == 0]

        while queue:
            sid = queue.pop(0)
            scenario = self._scenarios.get(sid)
            if scenario and scenario in scenarios:
                result.append(scenario)

            # Update degrees
            for s in scenarios:
                if sid in s.dependencies:
                    in_degree[s.scenario_id] -= 1
                    if in_degree[s.scenario_id] == 0:
                        queue.append(s.scenario_id)

        # Add any remaining (cycles or missing deps)
        remaining = [s for s in scenarios if s not in result]
        result.extend(remaining)

        return result

    def create_snapshot(
        self,
        scenario_id: str,
        baseline: bool = False,
    ) -> Optional[ScenarioSnapshot]:
        """Create a snapshot of the latest result for regression comparison.

        Args:
            scenario_id: Scenario ID
            baseline: Whether this is the baseline snapshot

        Returns:
            ScenarioSnapshot or None if no results exist
        """
        if scenario_id not in self._results or not self._results[scenario_id]:
            return None

        latest_result = self._results[scenario_id][-1]

        snapshot = ScenarioSnapshot(
            scenario_id=scenario_id,
            result=latest_result.to_dict(),
            baseline=baseline,
        )

        if scenario_id not in self._snapshots:
            self._snapshots[scenario_id] = []
        self._snapshots[scenario_id].append(snapshot)

        return snapshot

    def compare_to_baseline(
        self,
        scenario_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Compare latest result to baseline snapshot.

        Args:
            scenario_id: Scenario ID

        Returns:
            Comparison result or None
        """
        if scenario_id not in self._snapshots:
            return None

        # Find baseline
        baseline = None
        for snapshot in self._snapshots[scenario_id]:
            if snapshot.baseline:
                baseline = snapshot
                break

        if not baseline:
            return None

        # Get latest result
        if scenario_id not in self._results or not self._results[scenario_id]:
            return None

        latest = self._results[scenario_id][-1]

        # Compare
        baseline_output = baseline.result.get("actual_output")
        latest_output = latest.actual_output

        return {
            "scenario_id": scenario_id,
            "baseline_timestamp": baseline.timestamp.isoformat(),
            "latest_timestamp": latest.timestamp.isoformat(),
            "output_match": baseline_output == latest_output,
            "status_match": baseline.result.get("status") == latest.status.value,
            "regression_detected": baseline.result.get("status") == "passed" and latest.status != ScenarioStatus.PASSED,
            "baseline_output": baseline_output,
            "latest_output": latest_output,
        }

    def get_results(self, scenario_id: str) -> List[ScenarioResult]:
        """Get execution history for a scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            List of results
        """
        return list(self._results.get(scenario_id, []))

    def on_before_run(self, callback: Callable[[Scenario], None]) -> "ScenarioLibrary":
        """Register callback before scenario execution.

        Args:
            callback: Function called with scenario

        Returns:
            Self for method chaining
        """
        self._before_run.append(callback)
        return self

    def on_after_run(self, callback: Callable[[Scenario, ScenarioResult], None]) -> "ScenarioLibrary":
        """Register callback after scenario execution.

        Args:
            callback: Function called with scenario and result

        Returns:
            Self for method chaining
        """
        self._after_run.append(callback)
        return self

    def summary(self) -> Dict[str, Any]:
        """Get library summary statistics.

        Returns:
            Dictionary with statistics
        """
        total = len(self._scenarios)
        by_category = {}
        by_orchestrator = {}

        for scenario in self._scenarios.values():
            cat = scenario.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

            orch = scenario.orchestrator or "unassigned"
            by_orchestrator[orch] = by_orchestrator.get(orch, 0) + 1

        # Results summary
        total_runs = sum(len(r) for r in self._results.values())
        passed_runs = sum(
            1 for results in self._results.values()
            for r in results if r.status == ScenarioStatus.PASSED
        )

        return {
            "total_scenarios": total,
            "by_category": by_category,
            "by_orchestrator": by_orchestrator,
            "total_executions": total_runs,
            "passed_executions": passed_runs,
            "pass_rate": (passed_runs / total_runs * 100) if total_runs > 0 else 0.0,
            "snapshots_count": sum(len(s) for s in self._snapshots.values()),
        }

    @property
    def scenarios(self) -> List[Scenario]:
        """Get all scenarios."""
        return list(self._scenarios.values())

    @property
    def count(self) -> int:
        """Get scenario count."""
        return len(self._scenarios)
