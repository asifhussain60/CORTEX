"""
Phase Executor Base Class

Provides abstract foundation for all phase executors.

CORE Rules:
- CORE-008: TDD-First (tests before code)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-027: Audit trail logging
- CORE-049: Silent autonomous execution

AC-PHASE80-EXE-001: Base Phase Executor
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging
import yaml
import time
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of phase execution."""
    phase_id: str
    status: str  # "SUCCESS", "FAILED", "PARTIAL"
    duration_seconds: float
    tests_passed: int
    tests_total: int
    coverage_percent: float
    git_commit: Optional[str]
    error_message: Optional[str]
    timestamp: str


class PhaseExecutorBase(ABC):
    """
    Abstract base class for phase executors.

    Responsibilities:
    - Load phase specification from YAML
    - Execute stages sequentially
    - Collect test results
    - Generate git commits
    - Report progress via ASCII bars
    - Handle failures gracefully
    """

    def __init__(self, phase_id: str, cortex_root: Path):
        """
        Initialize phase executor.

        Args:
            phase_id: Phase identifier (e.g., "phase-80")
            cortex_root: Root path of CORTEX repository
        """
        self.phase_id = phase_id
        self.cortex_root = cortex_root
        self.registry_root = cortex_root / "cortex-registry" / "_cortex-master"
        self.phase_file = (
            self.registry_root / "phases" / "active" / f"{phase_id}.yaml"
        )
        self.start_time: Optional[float] = None
        self.stage_results: List[Dict[str, Any]] = []

    def load_phase_spec(self) -> Dict[str, Any]:
        """
        Load phase specification from YAML.

        Returns:
            Dict containing phase metadata and stages.

        Raises:
            FileNotFoundError: If phase file not found.
        """
        if not self.phase_file.exists():
            raise FileNotFoundError(f"Phase file not found: {self.phase_file}")

        with open(self.phase_file) as f:
            spec = yaml.safe_load(f)
            logger.info(f"Loaded phase spec: {self.phase_id}")
            return spec

    def print_progress_bar(
        self, current: int, total: int, stage_name: str = ""
    ) -> None:
        """
        Print ASCII progress bar.

        Args:
            current: Current stage number.
            total: Total number of stages.
            stage_name: Optional stage name.
        """
        percentage = (current / total) * 100
        filled = int(percentage / 10)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        status = "✅" if current == total else "🔵"
        print(f"[{bar}] {percentage:3.0f}% {status} {stage_name}")

    @abstractmethod
    def execute(self) -> ExecutionResult:
        """
        Execute all phases.

        Must be implemented by subclasses.

        Returns:
            ExecutionResult with completion details.
        """
        pass

    def _record_stage_result(
        self,
        stage_num: int,
        stage_name: str,
        tests_passed: int,
        tests_total: int,
        coverage: float,
    ) -> None:
        """
        Record results from a completed stage.

        Args:
            stage_num: Stage number.
            stage_name: Stage name.
            tests_passed: Number of passing tests.
            tests_total: Total number of tests.
            coverage: Code coverage percentage.
        """
        self.stage_results.append(
            {
                "stage": stage_num,
                "name": stage_name,
                "tests_passed": tests_passed,
                "tests_total": tests_total,
                "coverage": coverage,
                "timestamp": datetime.now().isoformat(),
            }
        )
        logger.info(
            f"Stage {stage_num} result: {tests_passed}/{tests_total} tests, "
            f"{coverage}% coverage"
        )

    def calculate_total_tests(self) -> Tuple[int, int]:
        """
        Calculate total passed/failed tests across all stages.

        Returns:
            Tuple of (total_passed, total_tests).
        """
        total_passed = sum(r["tests_passed"] for r in self.stage_results)
        total_tests = sum(r["tests_total"] for r in self.stage_results)
        return total_passed, total_tests

    def calculate_avg_coverage(self) -> float:
        """
        Calculate average code coverage across stages.

        Returns:
            Average coverage percentage.
        """
        if not self.stage_results:
            return 0.0
        avg = sum(r["coverage"] for r in self.stage_results) / len(
            self.stage_results
        )
        return round(avg, 1)

    def log_completion(self, result: ExecutionResult) -> None:
        """
        Log phase completion to audit trail.

        Args:
            result: ExecutionResult from execution.
        """
        status_icon = "✅" if result.status == "SUCCESS" else "⚠️"
        logger.info(
            f"{status_icon} Phase {self.phase_id} COMPLETE | "
            f"{result.tests_passed}/{result.tests_total} tests | "
            f"{result.coverage_percent}% coverage | {result.duration_seconds:.1f}s"
        )
