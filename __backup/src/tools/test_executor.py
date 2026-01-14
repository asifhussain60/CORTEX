"""
Test Executor - Run Python tests and collect results.

This module executes tests and collects results:
1. pytest integration
2. unittest integration
3. Coverage measurement
4. Result parsing
5. Failure analysis

AC-ID: AC-TESTEXEC-001
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of single test."""
    name: str
    status: TestStatus
    duration: float = 0.0
    message: Optional[str] = None
    traceback: Optional[str] = None


@dataclass
class TestExecutionResult:
    """Result of test execution."""
    success: bool
    passed: int
    failed: int
    skipped: int
    total: int
    duration: float
    coverage_percent: float = 0.0
    tests: List[TestResult] = None
    output: str = ""
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.tests is None:
            self.tests = []


class TestExecutor:
    """
    Test Executor.
    
    Executes Python tests using pytest or unittest and collects results.
    
    Acceptance Criteria:
    - AC-TESTEXEC-001: pytest/unittest integration
    - AC-TESTEXEC-002: Coverage measurement
    - AC-TESTEXEC-003: Result parsing and reporting
    """
    
    def __init__(
        self,
        workspace_root: Path,
        use_pytest: bool = True,
        coverage_enabled: bool = True,
    ):
        """
        Initialize Test Executor.
        
        Args:
            workspace_root: Workspace root directory
            use_pytest: Use pytest (vs unittest)
            coverage_enabled: Measure coverage
        """
        self.logger = logging.getLogger("cortex.tools.test_executor")
        self.workspace_root = Path(workspace_root)
        self.use_pytest = use_pytest
        self.coverage_enabled = coverage_enabled
        
        # Check pytest availability
        if self.use_pytest:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pytest", "--version"],
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                self.logger.warning("pytest not available, falling back to unittest")
                self.use_pytest = False
        
        self.logger.info(f"TestExecutor initialized (pytest={self.use_pytest}, coverage={coverage_enabled})")
    
    def run_tests(
        self,
        test_file: str,
        test_function: Optional[str] = None,
        verbose: bool = True
    ) -> TestExecutionResult:
        """
        Run tests from file.
        
        Args:
            test_file: Path to test file (relative or absolute)
            test_function: Specific test function to run (optional)
            verbose: Verbose output
            
        Returns:
            TestExecutionResult with execution details
        """
        try:
            test_path = self._resolve_path(test_file)
            
            if not test_path.exists():
                return TestExecutionResult(
                    success=False,
                    passed=0,
                    failed=0,
                    skipped=0,
                    total=0,
                    duration=0.0,
                    error=f"Test file not found: {test_path}"
                )
            
            # Run tests
            if self.use_pytest:
                result = self._run_pytest(test_path, test_function, verbose)
            else:
                result = self._run_unittest(test_path, test_function, verbose)
            
            self.logger.info(
                f"Tests completed: {result.passed}/{result.total} passed "
                f"({result.duration:.2f}s)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return TestExecutionResult(
                success=False,
                passed=0,
                failed=0,
                skipped=0,
                total=0,
                duration=0.0,
                error=str(e)
            )
    
    def _run_pytest(
        self,
        test_path: Path,
        test_function: Optional[str],
        verbose: bool
    ) -> TestExecutionResult:
        """Run tests using pytest."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_path),
            "--json-report",
            "--json-report-file=/tmp/cortex_test_report.json",
            "-v" if verbose else "-q"
        ]
        
        if test_function:
            cmd[3] += f"::{test_function}"
        
        if self.coverage_enabled:
            cmd.extend([
                "--cov",
                "--cov-report=json:/tmp/cortex_coverage.json"
            ])
        
        # Run pytest
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.workspace_root
        )
        
        # Parse results
        try:
            with open("/tmp/cortex_test_report.json") as f:
                report = json.load(f)
            
            tests = []
            for test in report.get("tests", []):
                tests.append(TestResult(
                    name=test.get("nodeid", ""),
                    status=TestStatus(test.get("outcome", "error")),
                    duration=test.get("duration", 0.0),
                    message=test.get("call", {}).get("longrepr", "")
                ))
            
            summary = report.get("summary", {})
            passed = summary.get("passed", 0)
            failed = summary.get("failed", 0)
            skipped = summary.get("skipped", 0)
            total = summary.get("total", 0)
            duration = report.get("duration", 0.0)
            
            # Get coverage
            coverage_percent = 0.0
            if self.coverage_enabled:
                try:
                    with open("/tmp/cortex_coverage.json") as f:
                        coverage_data = json.load(f)
                        coverage_percent = coverage_data.get("totals", {}).get("percent_covered", 0.0)
                except Exception:
                    pass
            
            return TestExecutionResult(
                success=(process.returncode == 0),
                passed=passed,
                failed=failed,
                skipped=skipped,
                total=total,
                duration=duration,
                coverage_percent=coverage_percent,
                tests=tests,
                output=process.stdout + process.stderr
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse pytest report: {e}")
            # Fallback: parse from output
            return self._parse_pytest_output(process.stdout, process.stderr)
    
    def _run_unittest(
        self,
        test_path: Path,
        test_function: Optional[str],
        verbose: bool
    ) -> TestExecutionResult:
        """Run tests using unittest."""
        cmd = [
            sys.executable,
            "-m",
            "unittest",
            "discover" if not test_function else str(test_path),
            "-v" if verbose else "-q"
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.workspace_root
        )
        
        # Parse unittest output
        return self._parse_unittest_output(process.stdout, process.stderr)
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> TestExecutionResult:
        """Parse pytest output as fallback."""
        output = stdout + stderr
        lines = output.split('\n')
        
        passed = 0
        failed = 0
        skipped = 0
        
        for line in lines:
            if " passed" in line:
                try:
                    passed = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif " failed" in line:
                try:
                    failed = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif " skipped" in line:
                try:
                    skipped = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
        
        total = passed + failed + skipped
        
        return TestExecutionResult(
            success=(failed == 0),
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration=0.0,
            output=output
        )
    
    def _parse_unittest_output(self, stdout: str, stderr: str) -> TestExecutionResult:
        """Parse unittest output."""
        output = stdout + stderr
        lines = output.split('\n')
        
        passed = 0
        failed = 0
        errors = 0
        skipped = 0
        
        for line in lines:
            if line.startswith("Ran "):
                try:
                    total = int(line.split()[1])
                except (ValueError, IndexError):
                    total = 0
            
            if "FAILED" in line or "ERRORS" in line:
                # Parse failures/errors from summary line
                if "failures=" in line:
                    try:
                        failed = int(line.split("failures=")[1].split(',')[0].split(')')[0])
                    except (ValueError, IndexError):
                        pass
                
                if "errors=" in line:
                    try:
                        errors = int(line.split("errors=")[1].split(',')[0].split(')')[0])
                    except (ValueError, IndexError):
                        pass
                
                if "skipped=" in line:
                    try:
                        skipped = int(line.split("skipped=")[1].split(',')[0].split(')')[0])
                    except (ValueError, IndexError):
                        pass
        
        total = passed + failed + errors + skipped
        if total == 0:
            total = passed + failed + errors
        
        passed = total - failed - errors - skipped
        
        return TestExecutionResult(
            success=(failed == 0 and errors == 0),
            passed=passed,
            failed=failed + errors,
            skipped=skipped,
            total=total,
            duration=0.0,
            output=output
        )
    
    def _resolve_path(self, file_path: str) -> Path:
        """Resolve file path relative to workspace root."""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.workspace_root / path
    
    def run_all_tests(self, test_dir: str = "tests") -> TestExecutionResult:
        """
        Run all tests in directory.
        
        Args:
            test_dir: Test directory (relative to workspace_root)
            
        Returns:
            TestExecutionResult with aggregated results
        """
        test_path = self._resolve_path(test_dir)
        
        if not test_path.exists():
            return TestExecutionResult(
                success=False,
                passed=0,
                failed=0,
                skipped=0,
                total=0,
                duration=0.0,
                error=f"Test directory not found: {test_path}"
            )
        
        return self.run_tests(str(test_path))
