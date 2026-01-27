"""pytest plugin for test progress monitoring.

Install by adding to conftest.py:
    pytest_plugins = ['cortex.devx.pytest_progress_plugin']

Or enable via pytest.ini:
    [pytest]
    addopts = -p cortex.devx.pytest_progress_plugin
"""

import pytest
import sys
from datetime import datetime
from typing import Optional
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport


class ProgressReporter:
    """Pytest plugin that reports test progress in real-time."""
    
    def __init__(self) -> None:
        """Initialize progress reporter."""
        self.start_time: Optional[datetime] = None
        self.test_count = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.current_test: Optional[str] = None
        self.last_report_count = 0
        
    def pytest_configure(self, config: Config) -> None:
        """Hook called before test collection."""
        self.start_time = datetime.now()
        sys.stdout.write("[PYTEST] Test execution started\n")
        sys.stdout.flush()
        
    def pytest_collection_finish(self, session) -> None:
        """Hook called after test collection."""
        self.test_count = len(session.items)
        sys.stdout.write(f"[PYTEST PROGRESS] Collected {self.test_count} tests\n")
        sys.stdout.flush()
        
    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Hook called after test result is known."""
        if report.when == "call":
            self.current_test = report.nodeid.split("::")[-1]
            
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1
            elif report.skipped:
                self.skipped += 1
                
            # Report progress every 10 tests
            total = self.passed + self.failed + self.errors + self.skipped
            if total - self.last_report_count >= 10:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = total / elapsed if elapsed > 0 else 0
                sys.stdout.write(
                    f"[PYTEST PROGRESS] {total}/{self.test_count} - "
                    f"{self.passed}P {self.failed}F {self.errors}E "
                    f"({rate:.1f} tests/sec) - {self.current_test}\n"
                )
                sys.stdout.flush()
                self.last_report_count = total
    def pytest_terminal_summary(self, terminalreporter, exitstatus) -> None:
        """Hook called at end of test run."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        total = self.passed + self.failed + self.errors + self.skipped
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        sys.stdout.write("\n" + "="*70 + "\n")
        sys.stdout.write("PYTEST PROGRESS SUMMARY\n")
        sys.stdout.write("="*70 + "\n")
        sys.stdout.write(f"Total:    {total}/{self.test_count}\n")
        sys.stdout.write(f"Passed:   {self.passed} ({pass_rate:.1f}%)\n")
        sys.stdout.write(f"Failed:   {self.failed}\n")
        sys.stdout.write(f"Errors:   {self.errors}\n")
        sys.stdout.write(f"Skipped:  {self.skipped}\n")
        sys.stdout.write(f"Duration: {elapsed:.1f}s\n")
        sys.stdout.write(f"Rate:     {total/elapsed if elapsed > 0 else 0:.1f} tests/sec\n")
        sys.stdout.write("="*70 + "\n")
        sys.stdout.flush()


def pytest_configure(config: Config) -> None:
    """Register the plugin."""
    config.addinivalue_line(
        "markers",
        "progress: mark test for progress tracking"
    )
    config.pluginmanager.register(ProgressReporter(), "progress_reporter")


__all__ = ["ProgressReporter"]
