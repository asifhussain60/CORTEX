"""
AC-TEST-002: Test Execution
Run tests and capture results by AC-ID.

Executes pytest for specific AC-IDs or full suite, captures results,
and formats them for evidence bundle generation.
"""

import subprocess
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of running tests for an AC-ID."""
    ac_id: str
    passed: int
    failed: int
    skipped: int
    total: int
    success_rate: float
    coverage: Optional[float] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class TestExecutor:
    """Execute tests and collect results by AC-ID."""
    
    def __init__(self, test_dir: Path = None):
        """
        Initialize test executor.
        
        Args:
            test_dir: Root directory containing tests (default: ./tests)
        """
        if test_dir is None:
            test_dir = Path("tests")
        
        self.test_dir = test_dir
    
    def run_tests_for_ac(self, ac_id: str, verbose: bool = False) -> TestResult:
        """
        Run all tests for a specific AC-ID.
        
        Args:
            ac_id: Acceptance Criteria ID to test
            verbose: Enable verbose output
            
        Returns:
            TestResult with pass/fail counts
        """
        cmd = [
            "python3", "-m", "pytest",
            str(self.test_dir),
            "-k", ac_id,
            "-v" if verbose else "-q",
            "--tb=short",
            "--no-header"
        ]
        
        logger.debug(f"Running tests for {ac_id}: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        output = result.stdout + result.stderr
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")
        total = passed + failed + skipped
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return TestResult(
            ac_id=ac_id,
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            success_rate=success_rate
        )
    
    def run_all_tests(self, verbose: bool = False) -> Dict:
        """
        Run full test suite.
        
        Args:
            verbose: Enable verbose output
            
        Returns:
            Dictionary with overall statistics
        """
        cmd = [
            "python3", "-m", "pytest",
            str(self.test_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--no-header"
        ]
        
        logger.info(f"Running full test suite")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        output = result.stdout + result.stderr
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")
        total = passed + failed + skipped
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "exit_code": result.returncode
        }
    
    def run_tests_with_coverage(self, ac_id: Optional[str] = None) -> Dict:
        """
        Run tests with coverage measurement.
        
        Args:
            ac_id: Optional AC-ID to filter tests
            
        Returns:
            Dictionary with test results and coverage data
        """
        cmd = [
            "python3", "-m", "pytest",
            str(self.test_dir),
            "-v",
            "--cov=src",
            "--cov-report=json:/tmp/coverage.json",
            "--tb=short"
        ]
        
        if ac_id:
            cmd.extend(["-k", ac_id])
        
        logger.info(f"Running tests with coverage")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        output = result.stdout + result.stderr
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        
        # Read coverage data
        coverage_data = {}
        try:
            with open("/tmp/coverage.json") as f:
                coverage_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not read coverage data: {e}")
        
        return {
            "tests": {
                "passed": passed,
                "failed": failed,
                "total": passed + failed
            },
            "coverage": coverage_data
        }
