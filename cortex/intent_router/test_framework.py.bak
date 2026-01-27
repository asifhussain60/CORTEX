"""Test Framework - Testing utilities for intent routing.

Author: CORTEX Framework
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a test execution."""
    
    test_name: str
    passed: bool
    duration_ms: float = 0.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class TestSuite:
    """A collection of tests."""
    
    def __init__(self, name: str):
        """Initialize test suite.
        
        Args:
            name: Name of the test suite
        """
        self.name = name
        self.tests: List[Callable] = []
        self.results: List[TestResult] = []
    
    def add_test(self, test: Callable) -> None:
        """Add a test to the suite.
        
        Args:
            test: Test function to add
        """
        self.tests.append(test)
    
    def run(self) -> List[TestResult]:
        """Run all tests in the suite.
        
        Returns:
            List of test results
        """
        self.results.clear()
        
        for test in self.tests:
            try:
                test()
                result = TestResult(
                    test_name=test.__name__,
                    passed=True,
                    message="Test passed"
                )
            except Exception as e:
                result = TestResult(
                    test_name=test.__name__,
                    passed=False,
                    message=str(e)
                )
            
            self.results.append(result)
        
        return self.results


class TestFramework:
    """Testing framework for intent routing components."""
    
    def __init__(self):
        """Initialize test framework."""
        self.test_suites: Dict[str, List[Any]] = {}
        self.results: List[TestResult] = []
    
    def register_suite(self, name: str, tests: List[Any]) -> None:
        """Register a test suite.
        
        Args:
            name: Name of the test suite
            tests: List of tests
        """
        self.test_suites[name] = tests
        logger.info(f"Registered test suite: {name} with {len(tests)} tests")
    
    def get_test_count(self) -> int:
        """Get total number of tests across all suites.
        
        Returns:
            Total count of tests
        """
        return sum(len(tests) for tests in self.test_suites.values())
    
    def run_suite(self, name: str) -> List[TestResult]:
        """Run a specific test suite.
        
        Args:
            name: Name of the suite to run
            
        Returns:
            List of test results
        """
        if name not in self.test_suites:
            logger.warning(f"Test suite not found: {name}")
            return []
        
        tests = self.test_suites[name]
        results = []
        
        for test in tests:
            if callable(test):
                try:
                    test()
                    result = TestResult(
                        test_name=str(test),
                        passed=True,
                        message="Test passed"
                    )
                except Exception as e:
                    result = TestResult(
                        test_name=str(test),
                        passed=False,
                        message=str(e)
                    )
            else:
                result = TestResult(
                    test_name=str(test),
                    passed=True,
                    message="Non-callable test item"
                )
            
            results.append(result)
        
        self.results.extend(results)
        return results
    
    def run_all(self) -> Dict[str, List[TestResult]]:
        """Run all test suites.
        
        Returns:
            Dictionary mapping suite names to results
        """
        all_results = {}
        
        for name in self.test_suites:
            all_results[name] = self.run_suite(name)
        
        return all_results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of test results.
        
        Returns:
            Dictionary with test statistics
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "suites": list(self.test_suites.keys())
        }


__all__ = ["TestFramework", "TestSuite", "TestResult"]
