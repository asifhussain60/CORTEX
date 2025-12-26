"""
Parallel Test Runner for TDD Orchestrator

Package 1: Multi-Agent Collaboration Integration
Executes test suites in parallel with async support.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result from test execution"""
    suite_path: Path
    success: bool
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    execution_time: float = 0.0
    output: str = ""
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ParallelTestRunner:
    """
    Run multiple test suites in parallel.
    
    Features:
    - Async parallel execution
    - Timeout handling
    - Result aggregation
    - Error recovery
    """
    
    def __init__(self, max_workers: int = 4, timeout_seconds: int = 300):
        """
        Initialize parallel test runner.
        
        Args:
            max_workers: Maximum concurrent test suites
            timeout_seconds: Timeout per test suite
        """
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        logger.info(f"🎭 Parallel Test Runner initialized (max_workers={max_workers})")
    
    async def run_tests_parallel(
        self,
        test_suites: List[Path],
        test_framework: str = "pytest"
    ) -> List[TestResult]:
        """
        Execute test suites concurrently.
        
        Args:
            test_suites: List of test suite paths
            test_framework: Test framework to use (pytest, unittest, jest, etc.)
            
        Returns:
            List of test results (one per suite)
        """
        logger.info(f"🚀 Running {len(test_suites)} test suites in parallel")
        
        # Create semaphore to limit concurrent executions
        semaphore = asyncio.Semaphore(self.max_workers)
        
        # Execute all suites
        tasks = [
            self._run_test_suite_with_semaphore(
                suite,
                test_framework,
                semaphore
            )
            for suite in test_suites
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results, convert exceptions to failed TestResults
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Suite {test_suites[i]} failed: {str(result)}")
                    processed_results.append(TestResult(
                        suite_path=test_suites[i],
                        success=False,
                        error=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            # Log summary
            successful = sum(1 for r in processed_results if r.success)
            logger.info(f"✅ Parallel tests complete: {successful}/{len(test_suites)} passed")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"❌ Parallel test execution failed: {e}")
            return [
                TestResult(suite_path=suite, success=False, error=str(e))
                for suite in test_suites
            ]
    
    async def _run_test_suite_with_semaphore(
        self,
        suite: Path,
        test_framework: str,
        semaphore: asyncio.Semaphore
    ) -> TestResult:
        """Run single test suite with semaphore control"""
        async with semaphore:
            return await self._run_test_suite(suite, test_framework)
    
    async def _run_test_suite(
        self,
        suite: Path,
        test_framework: str
    ) -> TestResult:
        """
        Run single test suite with timeout.
        
        Args:
            suite: Path to test suite
            test_framework: Test framework name
            
        Returns:
            TestResult with execution details
        """
        start_time = datetime.now()
        
        try:
            # Build command based on framework
            cmd = self._build_test_command(suite, test_framework)
            
            logger.info(f"  🧪 Running: {suite.name}")
            
            # Execute with timeout (Python 3.9 compatible using wait_for)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=suite.parent
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                # Kill process if timeout
                proc.kill()
                await proc.wait()
                execution_time = self.timeout_seconds
                logger.error(f"  ⏱️ {suite.name} timed out after {self.timeout_seconds}s")
                return TestResult(
                    suite_path=suite,
                    success=False,
                    execution_time=execution_time,
                    error=f"Test suite timed out after {self.timeout_seconds}s"
                )
            
            # Parse output
            execution_time = (datetime.now() - start_time).total_seconds()
            output = stdout.decode('utf-8', errors='replace')
            error_output = stderr.decode('utf-8', errors='replace')
            
            # Parse test counts (framework-specific)
            passed, failed, skipped = self._parse_test_counts(
                output,
                test_framework
            )
            
            success = proc.returncode == 0 and failed == 0
            
            result = TestResult(
                suite_path=suite,
                success=success,
                tests_passed=passed,
                tests_failed=failed,
                tests_skipped=skipped,
                execution_time=execution_time,
                output=output,
                error=error_output if error_output else None
            )
            
            if success:
                logger.info(f"  ✅ {suite.name}: {passed} passed ({execution_time:.1f}s)")
            else:
                logger.warning(f"  ❌ {suite.name}: {failed} failed ({execution_time:.1f}s)")
            
            return result
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"  ❌ {suite.name} failed: {str(e)}")
            return TestResult(
                suite_path=suite,
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
    
    def _build_test_command(self, suite: Path, framework: str) -> List[str]:
        """Build test command for framework"""
        if framework == "pytest":
            return ["pytest", str(suite), "-v", "--tb=short"]
        elif framework == "unittest":
            return ["python", "-m", "unittest", str(suite), "-v"]
        elif framework == "jest":
            return ["jest", str(suite), "--verbose"]
        elif framework == "mocha":
            return ["mocha", str(suite)]
        elif framework == "nunit":
            return ["dotnet", "test", str(suite), "--verbosity", "normal"]
        else:
            # Generic fallback
            return [framework, str(suite)]
    
    def _parse_test_counts(
        self,
        output: str,
        framework: str
    ) -> tuple[int, int, int]:
        """
        Parse test counts from output (passed, failed, skipped).
        
        Args:
            output: Test output
            framework: Test framework name
            
        Returns:
            Tuple of (passed, failed, skipped)
        """
        import re
        
        # Pytest patterns
        if framework == "pytest":
            # Example: "5 passed, 2 failed, 1 skipped in 1.23s"
            match = re.search(r'(\d+) passed(?:.*?(\d+) failed)?(?:.*?(\d+) skipped)?', output)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2)) if match.group(2) else 0
                skipped = int(match.group(3)) if match.group(3) else 0
                return passed, failed, skipped
        
        # Jest patterns
        elif framework == "jest":
            # Example: "Tests: 2 failed, 5 passed, 7 total"
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            skipped_match = re.search(r'(\d+) skipped', output)
            
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            skipped = int(skipped_match.group(1)) if skipped_match else 0
            return passed, failed, skipped
        
        # Unittest patterns
        elif framework == "unittest":
            # Example: "Ran 15 tests in 3.5s" (assumes all passed if no FAILED)
            # Example: "Ran 10 tests in 2.1s\nFAILED (failures=2)"
            ran_match = re.search(r'Ran (\d+) tests?', output)
            if ran_match:
                total = int(ran_match.group(1))
                failed_match = re.search(r'FAILED.*?failures=(\d+)', output)
                failed = int(failed_match.group(1)) if failed_match else 0
                passed = total - failed
                return passed, failed, 0  # unittest doesn't report skipped this way
        
        # Generic fallback: count "PASS" and "FAIL" in output
        passed = output.lower().count('pass')
        failed = output.lower().count('fail')
        skipped = output.lower().count('skip')
        
        return passed, failed, skipped
    
    def aggregate_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """
        Aggregate test results into summary.
        
        Args:
            results: List of test results
            
        Returns:
            Summary dictionary with totals
        """
        total_passed = sum(r.tests_passed for r in results)
        total_failed = sum(r.tests_failed for r in results)
        total_skipped = sum(r.tests_skipped for r in results)
        total_time = sum(r.execution_time for r in results)
        successful_suites = sum(1 for r in results if r.success)
        
        return {
            'total_suites': len(results),
            'successful_suites': successful_suites,
            'failed_suites': len(results) - successful_suites,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_skipped': total_skipped,
            'total_tests': total_passed + total_failed + total_skipped,
            'total_time': total_time,
            'pass_rate': total_passed / max(total_passed + total_failed, 1) * 100,
        }
