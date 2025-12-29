"""
Validation Gate Runner for CORTEX 4.0

Runs phase-specific validation scripts and parses results for autonomous execution.

Phase 0.5 Component
"""

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class ValidationGateResult:
    """Result of validation gate execution."""
    passed: bool
    message: str
    test_count: int = 0
    tests_passed: int = 0
    coverage_percentage: float = 0.0
    duration_seconds: float = 0.0
    output: str = ""
    exit_code: int = 0
    
    @property
    def pass_rate(self) -> float:
        """Calculate test pass rate."""
        if self.test_count == 0:
            return 0.0
        return (self.tests_passed / self.test_count) * 100.0


class ValidationGateRunner:
    """
    Runs validation scripts and parses output for pass/fail determination.
    
    Supports:
    - pytest output parsing
    - coverage report parsing
    - custom validation scripts
    - timeout handling
    
    Usage:
        runner = ValidationGateRunner(logger)
        result = runner.run_validation(
            script_path="scripts/validate_phase_1.sh",
            timeout_seconds=300
        )
    """
    
    def __init__(self, logger: logging.Logger):
        """Initialize validation gate runner."""
        self.logger = logger
    
    def run_validation(
        self,
        script_path: str,
        timeout_seconds: int = 300,
        working_dir: Optional[str] = None
    ) -> ValidationGateResult:
        """
        Run validation script and parse output.
        
        Args:
            script_path: Path to validation script
            timeout_seconds: Max execution time (default: 5 minutes)
            working_dir: Working directory for script execution
        
        Returns:
            ValidationGateResult with parsed test metrics
        """
        script = Path(script_path)
        
        # Validate script exists
        if not script.exists():
            return ValidationGateResult(
                passed=False,
                message=f"Validation script not found: {script_path}",
                exit_code=-1
            )
        
        self.logger.info(f"🔍 Running validation: {script.name}")
        
        try:
            # Execute validation script
            result = subprocess.run(
                [str(script)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=working_dir,
                shell=True
            )
            
            output = result.stdout + result.stderr
            exit_code = result.returncode
            
            # Parse output for test metrics
            test_count, tests_passed = self._parse_test_counts(output)
            coverage = self._parse_coverage(output)
            
            # Determine pass/fail
            passed = (exit_code == 0 and tests_passed == test_count and test_count > 0)
            
            if passed:
                message = f"All {test_count} tests passed ({coverage:.1f}% coverage)"
            else:
                message = f"Validation failed: {tests_passed}/{test_count} tests passed"
            
            return ValidationGateResult(
                passed=passed,
                message=message,
                test_count=test_count,
                tests_passed=tests_passed,
                coverage_percentage=coverage,
                duration_seconds=0.0,  # TODO: Parse duration from output
                output=output,
                exit_code=exit_code
            )
        
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏱️ Validation timeout after {timeout_seconds}s")
            return ValidationGateResult(
                passed=False,
                message=f"Validation timeout after {timeout_seconds}s",
                exit_code=-2
            )
        
        except Exception as e:
            self.logger.error(f"❌ Validation error: {e}")
            return ValidationGateResult(
                passed=False,
                message=f"Validation error: {str(e)}",
                exit_code=-3
            )
    
    def _parse_test_counts(self, output: str) -> Tuple[int, int]:
        """
        Parse test counts from pytest output.
        
        Patterns:
        - "10 passed in 1.23s"
        - "8 passed, 2 failed in 2.34s"
        - "passed: 10, failed: 0"
        """
        # Pattern 1: "X passed"
        passed_match = re.search(r'(\d+)\s+passed', output, re.IGNORECASE)
        failed_match = re.search(r'(\d+)\s+failed', output, re.IGNORECASE)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        
        total = passed + failed
        return total, passed
    
    def _parse_coverage(self, output: str) -> float:
        """
        Parse coverage percentage from pytest-cov output.
        
        Pattern: "TOTAL    1234    567    85%"
        """
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if coverage_match:
            return float(coverage_match.group(1))
        
        # Alternative pattern: "Coverage: 85.3%"
        alt_match = re.search(r'Coverage:\s+(\d+\.?\d*)%', output, re.IGNORECASE)
        if alt_match:
            return float(alt_match.group(1))
        
        return 0.0
