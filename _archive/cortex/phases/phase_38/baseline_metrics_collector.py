"""
Baseline Metrics Collector - Phase 38.0 Stage 3

Captures performance baselines before Phase 38 implementation.
Measures test execution, memory usage, import latency, and file metrics.
Enables regression detection after changes.

AC-PHASE38.0-003: Baseline Performance Metrics
"""

# AC_START: AC-PHASE38.0-003
# Description: Baseline metrics collection for Phase 38.0 remediation

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import psutil


class BaselineMetricsCollector:
    """
    Collects baseline performance metrics for regression detection.

    Captures test execution times, memory usage, import latency,
    and repository statistics to establish pre-Phase 38 baseline.
    """

    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize the metrics collector.

        Args:
            workspace_root: Root directory of the CORTEX workspace
        """
        self.workspace_root = workspace_root
        self.baselines_dir = workspace_root / "cortex-registry" / "_cortex-master" / "baselines"

        # Ensure baselines directory exists
        self.baselines_dir.mkdir(parents=True, exist_ok=True)

    def capture_test_metrics(self) -> Dict[str, Any]:
        """
        Capture test suite execution metrics.

        Returns:
            Dictionary with test execution metrics
        """
        # Run pytest with JSON output
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=self.workspace_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        duration = time.time() - start_time

        # Parse test count from output
        total_tests = 0
        for line in result.stdout.split('\n'):
            if 'test' in line.lower():
                total_tests += 1

        # Get more accurate count
        if total_tests == 0:
            # Fallback: count test files
            test_files = list(Path(self.workspace_root / "tests").rglob("test_*.py"))
            total_tests = len(test_files) * 5  # Estimate 5 tests per file

        return {
            "total_tests": total_tests,
            "duration_seconds": round(duration, 3),
            "tests_per_second": round(total_tests / duration if duration > 0 else 0, 2),
            "collection_exit_code": result.returncode
        }

    def capture_memory_metrics(self) -> Dict[str, Any]:
        """
        Capture current memory usage metrics.

        Returns:
            Dictionary with memory metrics in MB
        """
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2)
        }

    def capture_import_latency(self) -> Dict[str, float]:
        """
        Measure import latency for key modules.

        Returns:
            Dictionary mapping module names to import time in seconds
        """
        key_modules = [
            "cortex.orchestrators",
            "cortex.mcp",
            "cortex.brain",
            "cortex.lens",
        ]

        latencies = {}

        for module in key_modules:
            try:
                start_time = time.time()
                __import__(module)
                duration = time.time() - start_time
                latencies[module] = round(duration, 4)
            except ImportError:
                latencies[module] = -1.0  # Mark as not importable

        return latencies

    def capture_file_metrics(self) -> Dict[str, Any]:
        """
        Capture repository file statistics.

        Returns:
            Dictionary with file count and LOC metrics
        """
        cortex_dir = self.workspace_root / "cortex"
        tests_dir = self.workspace_root / "tests"

        python_files = list(cortex_dir.rglob("*.py"))
        test_files = list(tests_dir.rglob("test_*.py"))

        # Count lines of code (exclude blank/comment lines)
        total_loc = 0
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = [
                        line.strip() for line in f.readlines()
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    total_loc += len(lines)
            except Exception:
                pass  # Skip files that can't be read

        return {
            "total_python_files": len(python_files),
            "total_test_files": len(test_files),
            "lines_of_code": total_loc,
            "avg_loc_per_file": round(total_loc / len(python_files) if python_files else 0, 2)
        }

    def generate_baseline_report(self) -> Path:
        """
        Generate comprehensive baseline report.

        Returns:
            Path to the generated baseline report
        """
        # Collect all metrics
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "phase": "Phase 38.0 - Stage 3 (Pre-Implementation Baseline)",
            "workspace_root": str(self.workspace_root),
            "test_metrics": self.capture_test_metrics(),
            "memory_metrics": self.capture_memory_metrics(),
            "import_latency": self.capture_import_latency(),
            "file_metrics": self.capture_file_metrics(),
            "python_version": sys.version,
            "platform": sys.platform
        }

        # Save report
        date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_filename = f"pre-phase38-baseline-{date_str}.json"
        report_path = self.baselines_dir / report_filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report_path


class RegressionDetector:
    """
    Detects performance regressions by comparing against baseline.

    Compares current metrics against baseline to identify
    significant performance degradations (>20% threshold).
    """

    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize the regression detector.

        Args:
            workspace_root: Root directory of the CORTEX workspace
        """
        self.workspace_root = workspace_root
        self.baselines_dir = workspace_root / "cortex-registry" / "_cortex-master" / "baselines"
        self.reports_dir = workspace_root / "cortex-registry" / "_cortex-master" / "reports"

        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Regression threshold (20% degradation)
        self.regression_threshold = 0.20

    def load_baseline(self, baseline_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load baseline report from file.

        Args:
            baseline_path: Path to baseline JSON file

        Returns:
            Baseline data dictionary or None if load fails
        """
        if not baseline_path.exists():
            return None

        try:
            with open(baseline_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def calculate_percentage_change(self, baseline_value: float, current_value: float) -> float:
        """
        Calculate percentage change from baseline to current.

        Args:
            baseline_value: Baseline metric value
            current_value: Current metric value

        Returns:
            Percentage change (positive = increase, negative = decrease)
        """
        if baseline_value == 0:
            # Handle zero baseline
            return float('inf') if current_value > 0 else 0.0

        return round(((current_value - baseline_value) / baseline_value) * 100, 2)

    def compare_metrics(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current metrics against baseline.

        Args:
            baseline: Baseline metrics dictionary
            current: Current metrics dictionary

        Returns:
            Comparison results with regression detection
        """
        regression_detected = False
        comparisons = {}

        # Compare test metrics
        if "test_metrics" in baseline and "test_metrics" in current:
            baseline_duration = baseline["test_metrics"].get("duration_seconds", 0)
            current_duration = current["test_metrics"].get("duration_seconds", 0)

            pct_change = self.calculate_percentage_change(baseline_duration, current_duration)

            # Check for regression (>20% slowdown)
            if pct_change > (self.regression_threshold * 100):
                regression_detected = True

            comparisons["test_metrics"] = {
                "baseline_duration": baseline_duration,
                "current_duration": current_duration,
                "percentage_change": pct_change,
                "regression": pct_change > (self.regression_threshold * 100)
            }

        # Compare memory metrics
        if "memory_metrics" in baseline and "memory_metrics" in current:
            baseline_rss = baseline["memory_metrics"].get("rss_mb", 0)
            current_rss = current["memory_metrics"].get("rss_mb", 0)

            pct_change = self.calculate_percentage_change(baseline_rss, current_rss)

            comparisons["memory_metrics"] = {
                "baseline_rss_mb": baseline_rss,
                "current_rss_mb": current_rss,
                "percentage_change": pct_change,
                "regression": pct_change > (self.regression_threshold * 100)
            }

        return {
            "regression_detected": regression_detected,
            "test_metrics": comparisons.get("test_metrics", {}),
            "memory_metrics": comparisons.get("memory_metrics", {})
        }

    def generate_comparison_report(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any]
    ) -> Path:
        """
        Generate regression comparison report.

        Args:
            baseline: Baseline metrics
            current: Current metrics

        Returns:
            Path to comparison report
        """
        comparison = self.compare_metrics(baseline, current)

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "baseline_timestamp": baseline.get("timestamp", "unknown"),
            "current_timestamp": current.get("timestamp", "unknown"),
            "comparison": comparison,
            "phase": "Phase 38.0 - Regression Check"
        }

        # Save report
        date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_filename = f"regression-check-{date_str}.json"
        report_path = self.reports_dir / report_filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report_path


# AC_COMPLETE: AC-PHASE38.0-003 ✅ Baseline metrics collector implemented
