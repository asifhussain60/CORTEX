"""
Pytest Plugin: Real-time Test Timing and Hanging Detection
============================================================

Tracks execution time for each test and logs slow/hanging tests in real-time.
Integrates with pytest-timeout for comprehensive timeout handling.

Install as plugin in conftest.py or register via pytest.ini [pytest].plugins

Features:
- Real-time timing for each test
- Automatic detection of slow tests (configurable threshold)
- JSON output for programmatic consumption
- Terminal logging with color coding
- Integration with pytest-timeout plugin
"""

import pytest
import time
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TestTiming:
    """Timing information for a test."""
    test_id: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: str = "PENDING"  # PENDING, PASSED, FAILED, ERROR, TIMEOUT, SKIPPED
    is_slow: bool = False
    slow_threshold: float = 5.0
    
    def finish(self, status: str):
        """Mark test as finished."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        self.is_slow = self.duration > self.slow_threshold
    
    def to_dict(self):
        return {
            'test_id': self.test_id,
            'duration': self.duration,
            'status': self.status,
            'is_slow': self.is_slow,
            'slow_threshold': self.slow_threshold
        }


class TestTimingPlugin:
    """Pytest plugin for tracking test timings."""
    
    def __init__(self, slow_threshold: float = 5.0, json_output: Optional[str] = None):
        """
        Initialize plugin.
        
        Args:
            slow_threshold: Threshold for slow test detection (seconds)
            json_output: Output file for JSON timing report
        """
        self.slow_threshold = slow_threshold
        self.json_output = json_output
        self.test_timings: Dict[str, TestTiming] = {}
        self.slow_tests: List[TestTiming] = []
        self.hanging_tests: List[TestTiming] = []
        
    def pytest_configure(self, config):
        """Configure plugin at start of session."""
        logger.info(f"🎬 Test Timing Plugin initialized (slow threshold: {self.slow_threshold}s)")
        config.addinivalue_line(
            "markers",
            "slow: mark test as slow (should complete < 5s normally)"
        )
    
    def pytest_runtest_setup(self, item):
        """Called before each test."""
        test_id = item.nodeid
        self.test_timings[test_id] = TestTiming(
            test_id=test_id,
            start_time=time.time(),
            slow_threshold=self.slow_threshold
        )
        logger.debug(f"⏱️  Starting: {test_id}")
    
    def pytest_runtest_makereport(self, item, call):
        """Called after each test phase."""
        if call.when == "call":
            # This is the main test execution phase
            test_id = item.nodeid
            
            # Determine status
            if call.excinfo is None:
                status = "PASSED"
            elif "timeout" in str(call.excinfo).lower():
                status = "TIMEOUT"
                self.hanging_tests.append(self.test_timings[test_id])
            else:
                status = "FAILED"
            
            # Record timing
            self.test_timings[test_id].finish(status)
            timing = self.test_timings[test_id]
            
            # Log result with color coding
            if timing.is_slow:
                self.slow_tests.append(timing)
                color_code = '\033[93m'  # Yellow
                symbol = "⚠️ "
            elif status == "TIMEOUT":
                color_code = '\033[91m'  # Red
                symbol = "🔴"
            elif status == "PASSED":
                color_code = '\033[92m'  # Green
                symbol = "✅"
            else:
                color_code = '\033[91m'  # Red
                symbol = "❌"
            
            reset_code = '\033[0m'
            
            logger.info(
                f"{symbol} {color_code}[{timing.duration:.2f}s]{reset_code} {test_id} - {status}"
            )
    
    def pytest_runtest_logreport(self, report):
        """Called after test report is created."""
        if report.when == "teardown":
            test_id = report.nodeid
            if test_id in self.test_timings and self.test_timings[test_id].duration is None:
                # Still running, likely in teardown
                logger.debug(f"⏳ Teardown: {test_id}")
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called after all tests are completed."""
        logger.info("\n" + "="*80)
        logger.info("📊 TEST TIMING SUMMARY")
        logger.info("="*80)
        
        # Summary statistics
        total_tests = len(self.test_timings)
        total_duration = sum(t.duration or 0 for t in self.test_timings.values())
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info(f"Average Duration: {total_duration/total_tests:.2f}s")
        
        # Slow tests
        if self.slow_tests:
            logger.info(f"\n⚠️  SLOW TESTS ({len(self.slow_tests)} total):")
            for timing in sorted(self.slow_tests, key=lambda x: x.duration or 0, reverse=True)[:20]:
                logger.info(f"   • {timing.duration:.2f}s - {timing.test_id}")
        
        # Hanging tests
        if self.hanging_tests:
            logger.info(f"\n🔴 HANGING TESTS ({len(self.hanging_tests)} total):")
            for timing in self.hanging_tests:
                logger.info(f"   • {timing.test_id}")
        
        # Generate JSON report if requested
        if self.json_output:
            self._generate_json_report()
        
        logger.info("="*80 + "\n")
    
    def _generate_json_report(self):
        """Generate JSON timing report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.test_timings),
                'total_duration': sum(t.duration or 0 for t in self.test_timings.values()),
                'slow_tests': len(self.slow_tests),
                'hanging_tests': len(self.hanging_tests)
            },
            'slow_tests': [t.to_dict() for t in sorted(self.slow_tests, key=lambda x: x.duration or 0, reverse=True)[:50]],
            'hanging_tests': [t.to_dict() for t in self.hanging_tests],
            'all_tests': [t.to_dict() for t in sorted(self.test_timings.values(), key=lambda x: x.duration or 0, reverse=True)]
        }
        
        with open(self.json_output, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"💾 JSON report saved: {self.json_output}")


def pytest_addoption(parser):
    """Add command-line options."""
    parser.addoption(
        "--slow-threshold",
        action="store",
        default=5.0,
        type=float,
        help="Threshold for slow test detection (default: 5.0s)"
    )
    parser.addoption(
        "--timing-json",
        action="store",
        default=None,
        help="Output JSON timing report to file"
    )


def pytest_configure(config):
    """Register plugin."""
    slow_threshold = config.getoption("--slow-threshold")
    json_output = config.getoption("--timing-json")
    
    plugin = TestTimingPlugin(
        slow_threshold=slow_threshold,
        json_output=json_output
    )
    
    config.pluginmanager.register(plugin, "test_timing")
