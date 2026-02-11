"""Test Progress Monitor - Real-time test execution tracking and hanging detection.

Provides continuous progress feedback, hanging test detection, and execution analysis.

Author: CORTEX Framework
"""

import json
import re
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class TestMetrics:
    """Metrics for a test execution."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    last_update: datetime = field(default_factory=datetime.now)
    hanging_detected: bool = False
    hang_timeout_seconds: int = 30


class TestProgressMonitor:
    """Monitors test execution with real-time progress reporting."""

    def __init__(
        self,
        command: List[str],
        progress_callback: Optional[Callable[[str], None]] = None,
        hang_timeout: int = 30,
        verbose: bool = True
    ):
        """Initialize test progress monitor.

        Args:
            command: pytest command as list (e.g., ['python3', '-m', 'pytest', 'tests/', '-v'])
            progress_callback: Optional callback for progress updates
            hang_timeout: Seconds without output before marking as hanging (default 30)
            verbose: Print progress to stdout (default True)
        """
        self.command = command
        self.progress_callback = progress_callback
        self.hang_timeout = hang_timeout
        self.verbose = verbose
        self.metrics = TestMetrics(hang_timeout_seconds=hang_timeout)
        self.current_test: Optional[str] = None
        self.lock = threading.Lock()
        self.process: Optional[subprocess.Popen] = None
        self.output_lines: List[str] = []
        self.last_output_time = datetime.now()

    def _print(self, message: str) -> None:
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(message)

    def _report_progress(self, message: str) -> None:
        """Report progress via callback and print."""
        self._print(f"[TEST PROGRESS] {message}")
        if self.progress_callback:
            self.progress_callback(message)

    def _monitor_output(self, process: subprocess.Popen) -> None:
        """Monitor subprocess output in real-time.

        Args:
            process: Subprocess to monitor
        """
        import sys

        while True:
            line = process.stdout.readline()
            if not line:
                break

            line_str = line.decode('utf-8', errors='replace').rstrip()

            with self.lock:
                self.output_lines.append(line_str)
                self.last_output_time = datetime.now()

                # Track current test
                if "PASSED" in line_str or "FAILED" in line_str or "ERROR" in line_str:
                    match = re.search(r'test_\w+', line_str)
                    if match:
                        self.current_test = match.group(0)

                    # Update metrics
                    if "PASSED" in line_str:
                        self.metrics.passed += 1
                    elif "FAILED" in line_str:
                        self.metrics.failed += 1
                    elif "ERROR" in line_str:
                        self.metrics.errors += 1

                    elapsed = (datetime.now() - self.metrics.start_time).total_seconds()
                    rate = (self.metrics.passed + self.metrics.failed + self.metrics.errors) / elapsed if elapsed > 0 else 0
                    self._report_progress(
                        f"Progress: {self.metrics.passed}✓ {self.metrics.failed}✗ {self.metrics.errors}⚠ "
                        f"({rate:.1f} tests/sec) - Current: {self.current_test}"
                    )

                # Collect collection summary
                if "collected" in line_str.lower():
                    match = re.search(r'collected\s+(\d+)', line_str)
                    if match:
                        self.metrics.total_tests = int(match.group(1))
                        self._report_progress(f"Test Collection: {self.metrics.total_tests} tests discovered")

            self._print(line_str)

    def _detect_hanging(self, process: subprocess.Popen) -> None:
        """Detect and report hanging tests.

        Args:
            process: Subprocess to monitor
        """
        while process.poll() is None:
            time.sleep(1)

            with self.lock:
                time_since_output = (datetime.now() - self.last_output_time).total_seconds()

                if time_since_output > self.hang_timeout and not self.metrics.hanging_detected:
                    self.metrics.hanging_detected = True
                    self._report_progress(
                        f"⚠️ HANGING DETECTED: No output for {time_since_output:.0f}s. "
                        f"Current test: {self.current_test}"
                    )
                elif time_since_output > self.hang_timeout * 2:
                    self._report_progress(
                        f"🔴 CRITICAL HANG: {time_since_output:.0f}s without output! "
                        f"Test likely deadlocked: {self.current_test}"
                    )

    def run(self) -> int:
        """Run test command with progress monitoring.

        Returns:
            Exit code of test process
        """
        self._report_progress(f"Starting tests: {' '.join(self.command)}")
        self.metrics.start_time = datetime.now()

        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=False,
                bufsize=1
            )

            # Start output monitoring thread
            output_thread = threading.Thread(target=self._monitor_output, args=(self.process,), daemon=True)
            output_thread.start()

            # Start hanging detection thread
            hang_thread = threading.Thread(target=self._detect_hanging, args=(self.process,), daemon=True)
            hang_thread.start()

            # Wait for process completion
            exit_code = self.process.wait()
            self.metrics.end_time = datetime.now()

            # Final report
            duration = (self.metrics.end_time - self.metrics.start_time).total_seconds()
            self._report_progress(
                f"Tests Complete: {self.metrics.passed}✓ {self.metrics.failed}✗ {self.metrics.errors}⚠ "
                f"(Duration: {duration:.1f}s)"
            )

            if self.metrics.hanging_detected:
                self._report_progress("⚠️ HANGING WAS DETECTED during execution")

            return exit_code

        except Exception as e:
            self._report_progress(f"❌ Error running tests: {e}")
            return 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of test metrics.

        Returns:
            Dictionary with test metrics
        """
        duration = (
            (self.metrics.end_time - self.metrics.start_time).total_seconds()
            if self.metrics.end_time
            else (datetime.now() - self.metrics.start_time).total_seconds()
        )

        total_run = self.metrics.passed + self.metrics.failed + self.metrics.errors
        pass_rate = (self.metrics.passed / total_run * 100) if total_run > 0 else 0

        return {
            "total_tests": self.metrics.total_tests,
            "passed": self.metrics.passed,
            "failed": self.metrics.failed,
            "errors": self.metrics.errors,
            "skipped": self.metrics.skipped,
            "duration_seconds": duration,
            "tests_per_second": total_run / duration if duration > 0 else 0,
            "pass_rate_percent": pass_rate,
            "hanging_detected": self.metrics.hanging_detected,
            "current_test_at_end": self.current_test,
        }


def run_tests_with_progress(
    test_path: str,
    pytest_args: Optional[List[str]] = None,
    hang_timeout: int = 30,
    verbose: bool = True
) -> int:
    """Run pytest with real-time progress monitoring.

    Args:
        test_path: Path to tests (e.g., 'tests/unit/infrastructure/')
        pytest_args: Additional pytest arguments (e.g., ['-v', '--tb=short'])
        hang_timeout: Timeout in seconds for hanging detection
        verbose: Print progress to stdout

    Returns:
        Exit code of pytest

    Example:
        >>> exit_code = run_tests_with_progress('tests/unit/core/', ['-q', '--tb=no'])
        [TEST PROGRESS] Starting tests: python3 -m pytest tests/unit/core/ -q --tb=no
        [TEST PROGRESS] Test Collection: 354 tests discovered
        [TEST PROGRESS] Progress: 45✓ 3✗ 1⚠ (127.3 tests/sec) - Current: test_ac_deletion
        ...
    """
    command = ['python3', '-m', 'pytest', test_path]
    if pytest_args:
        command.extend(pytest_args)

    def progress_callback(message: str) -> None:
        """Callback for progress updates."""
        # Can be extended to log to file, send to monitoring service, etc.
        pass

    monitor = TestProgressMonitor(
        command=command,
        progress_callback=progress_callback,
        hang_timeout=hang_timeout,
        verbose=verbose
    )

    exit_code = monitor.run()

    # Print final metrics
    metrics = monitor.get_metrics_summary()
    print("\n" + "="*70)
    print("TEST EXECUTION SUMMARY")
    print("="*70)
    print(f"Total Tests:      {metrics['total_tests']}")
    print(f"Passed:           {metrics['passed']} ({metrics['pass_rate_percent']:.1f}%)")
    print(f"Failed:           {metrics['failed']}")
    print(f"Errors:           {metrics['errors']}")
    print(f"Duration:         {metrics['duration_seconds']:.1f}s")
    print(f"Rate:             {metrics['tests_per_second']:.1f} tests/sec")
    if metrics['hanging_detected']:
        print("⚠️  HANGING:        Detected during execution")
    print("="*70 + "\n")

    return exit_code


__all__ = [
    "TestProgressMonitor",
    "TestMetrics",
    "run_tests_with_progress",
]
