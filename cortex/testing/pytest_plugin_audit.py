"""
Pytest plugin integration for test performance auditing.

Auto-registered via conftest.py to track all test performance metrics.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


@dataclass
class TestExecution:
    """Track single test execution."""
    test_id: str
    start_time: float
    end_time: Optional[float] = None
    status: Optional[str] = None
    duration: float = 0.0

    def complete(self, status: str):
        """Mark test as complete."""
        self.end_time = time.time()
        self.status = status
        self.duration = self.end_time - self.start_time


class CORTEXTestAuditPlugin:
    """Pytest plugin for CORTEX test performance auditing."""

    def __init__(self):
        """Initialize plugin."""
        self.session_start_time = None
        self.test_executions: Dict[str, TestExecution] = {}
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger("cortex_test_audit")

        # Only add handler if not already present
        if not logger.handlers:
            log_file = Path(__file__).parent.parent / "test_audit_trail.log"
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def pytest_sessionstart(self, session):
        """Track session start."""
        self.session_start_time = time.time()
        num_tests = session.config.hook.pytest_collection_modifyitems.get_hookimpls()
        self.logger.info("[TEST SESSION START]")

    def pytest_runtest_setup(self, item):
        """Track test setup."""
        test_id = item.nodeid
        self.test_executions[test_id] = TestExecution(test_id, time.time())

    def pytest_runtest_logreport(self, report):
        """Track test completion."""
        if report.when != "call":
            return

        test_id = report.nodeid
        if test_id not in self.test_executions:
            return

        execution = self.test_executions[test_id]

        # Map pytest outcome to status
        status_map = {
            "passed": "PASSED",
            "failed": "FAILED",
            "skipped": "SKIPPED",
            "error": "ERROR"
        }

        status = status_map.get(report.outcome, "UNKNOWN")
        execution.complete(status)

        # Flag slow tests (>1 second)
        if execution.duration > 1.0:
            self.logger.warning(
                f"SLOW TEST: {test_id} took {execution.duration:.3f}s"
            )

        # Flag very slow tests (>5 seconds)
        if execution.duration > 5.0:
            self.logger.error(
                f"VERY SLOW: {test_id} took {execution.duration:.3f}s - INVESTIGATE"
            )

    def pytest_sessionfinish(self, session, exitstatus):
        """Generate session report."""
        if not self.session_start_time:
            return

        total_duration = time.time() - self.session_start_time

        # Collect statistics
        passed = len([e for e in self.test_executions.values() if "PASSED" in (e.status or "")])
        failed = len([e for e in self.test_executions.values() if "FAILED" in (e.status or "")])
        skipped = len([e for e in self.test_executions.values() if "SKIPPED" in (e.status or "")])
        errors = len([e for e in self.test_executions.values() if "ERROR" in (e.status or "")])

        # Find slowest tests
        sorted_tests = sorted(
            self.test_executions.values(),
            key=lambda x: x.duration,
            reverse=True
        )

        slowest_5 = sorted_tests[:5]

        self.logger.info(
            f"[SESSION COMPLETE] - "
            f"Passed: {passed}, Failed: {failed}, Skipped: {skipped}, Errors: {errors} "
            f"| Total Duration: {total_duration:.2f}s"
        )

        if slowest_5:
            self.logger.info("TOP 5 SLOWEST TESTS:")
            for execution in slowest_5:
                if execution.duration > 0.1:
                    self.logger.info(
                        f"   {execution.duration:7.3f}s | {execution.status} | {execution.test_id}"
                    )


# Create plugin instance
cortex_test_audit_plugin = CORTEXTestAuditPlugin()


def pytest_configure(config):
    """Register plugin with pytest."""
    config.pluginmanager.register(cortex_test_audit_plugin, name="cortex_test_audit")
