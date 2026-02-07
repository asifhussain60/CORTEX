"""
Test Performance Analyzer - P1-028 AUDIT Check.

Analyzes test suite performance and detects regressions.

AC_START: AC-ENH053-004
Description: Test suite performance analysis implementation
Author: Asif Hussain
Date: 2026-02-07
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SlowTest:
    """Represents a slow test with duration."""

    test_name: str
    duration: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"test_name": self.test_name, "duration": self.duration}


@dataclass
class TestPerformanceResult:
    """Result of test performance analysis."""

    total_time: float
    slow_tests: list[SlowTest] = field(default_factory=list)
    regression_percent: float = 0.0
    severity: str = "P2"

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "total_time": self.total_time,
            "slow_tests": [test.to_dict() for test in self.slow_tests],
            "regression_percent": self.regression_percent,
            "severity": self.severity,
        }


class TestPerformanceAnalyzer:
    """
    Analyzes test suite performance and detects regressions.

    P1-028 AUDIT Check:
    - Runs pytest with --durations=10 flag
    - Identifies tests taking >10s
    - Compares against baseline (stored in .cortex/metrics/)
    - Thresholds: 120s warning, 300s critical
    """

    def __init__(self, slow_test_threshold: float = 10.0):
        """
        Initialize test performance analyzer.

        Args:
            slow_test_threshold: Duration in seconds to flag as slow
        """
        self.slow_test_threshold = slow_test_threshold
        self.duration_pattern = re.compile(r"^([\d.]+)s\s+call\s+(.+)$")
        self.total_time_pattern = re.compile(r"(\d+)\s+passed\s+in\s+([\d.]+)s")

    def analyze(self, repo_path: Path) -> TestPerformanceResult:
        """
        Analyze test suite performance.

        Args:
            repo_path: Path to repository root

        Returns:
            TestPerformanceResult with performance analysis
        """
        try:
            # Run pytest with durations flag
            result = subprocess.run(
                [
                    "pytest",
                    "tests/",
                    "--durations=10",
                    "--tb=no",
                    "-q",
                ],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            output = result.stdout

            # Parse results
            total_time = self._parse_total_time(output)
            slow_tests = self._parse_slow_tests(output, self.slow_test_threshold)

            # Load baseline for comparison
            baseline = self._load_baseline(repo_path)
            regression_percent = 0.0

            if baseline and baseline.get("total_time"):
                baseline_time = baseline["total_time"]
                regression_percent = ((total_time - baseline_time) / baseline_time) * 100

            # Determine severity
            if total_time > 300:  # 5 minutes
                severity = "P0"
            elif total_time > 120:  # 2 minutes
                severity = "P1"
            else:
                severity = "P2"

            result_obj = TestPerformanceResult(
                total_time=total_time,
                slow_tests=slow_tests,
                regression_percent=regression_percent,
                severity=severity,
            )

            # Save as new baseline
            self._save_baseline(repo_path, result_obj)

            return result_obj

        except Exception:
            # Handle timeout or other errors
            return TestPerformanceResult(
                total_time=0.0,
                slow_tests=[],
                regression_percent=0.0,
                severity="P0",
            )

    def _parse_total_time(self, output: str) -> float:
        """
        Parse total execution time from pytest output.

        Args:
            output: pytest stdout

        Returns:
            Total time in seconds
        """
        match = self.total_time_pattern.search(output)
        if match:
            return float(match.group(2))
        return 0.0

    def _parse_slow_tests(self, output: str, threshold: float) -> list[SlowTest]:
        """
        Parse slow tests from pytest --durations output.

        Args:
            output: pytest stdout
            threshold: Duration threshold in seconds

        Returns:
            List of SlowTest objects
        """
        slow_tests = []

        for line in output.splitlines():
            match = self.duration_pattern.match(line.strip())
            if match:
                duration = float(match.group(1))
                test_name = match.group(2)

                if duration >= threshold:
                    slow_tests.append(SlowTest(test_name, duration))

        return slow_tests

    def _load_baseline(self, repo_path: Path) -> Optional[dict]:
        """
        Load performance baseline from .cortex/metrics/.

        Args:
            repo_path: Path to repository root

        Returns:
            Baseline data or None
        """
        baseline_file = repo_path / ".cortex" / "metrics" / "test_performance_baseline.json"

        if not baseline_file.exists():
            return None

        try:
            return json.loads(baseline_file.read_text())
        except Exception:
            return None

    def _save_baseline(self, repo_path: Path, result: TestPerformanceResult) -> None:
        """
        Save performance baseline to .cortex/metrics/.

        Args:
            repo_path: Path to repository root
            result: TestPerformanceResult to save
        """
        baseline_dir = repo_path / ".cortex" / "metrics"
        baseline_dir.mkdir(parents=True, exist_ok=True)

        baseline_file = baseline_dir / "test_performance_baseline.json"
        baseline_file.write_text(json.dumps(result.to_dict(), indent=2))


# AC_COMPLETE: AC-ENH053-004 ✅ Implementation complete
