"""
BRT-032: Comprehensive Testing & Validation (FINAL)

Comprehensive testing framework and validation utilities for the
complete resilience framework.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List, Callable, Optional, Set
from threading import Lock
from enum import Enum
import time


class TestType(Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    LOAD = "load"
    CHAOS = "chaos"
    SECURITY = "security"


class TestResult(Enum):
    """Test result statuses."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    """Represents a test case."""
    test_id: str
    name: str
    test_type: TestType
    test_fn: Callable[[], bool]
    dependencies: Set[str] = None
    timeout_ms: int = 5000
    is_critical: bool = False


@dataclass
class TestExecution:
    """Result of test execution."""
    test_id: str
    result: TestResult
    duration_ms: float
    error_message: Optional[str] = None
    timestamp_ms: float = time.time() * 1000


class TestRunner:
    """Runs test cases."""
    
    def __init__(self):
        self._tests: Dict[str, TestCase] = {}
        self._results: List[TestExecution] = []
        self._lock = Lock()
    
    def register_test(self, test_case: TestCase) -> bool:
        """Register a test case."""
        with self._lock:
            if test_case.test_id in self._tests:
                return False
            
            self._tests[test_case.test_id] = test_case
            return True
    
    def run_test(self, test_id: str) -> Optional[TestExecution]:
        """Run a single test."""
        with self._lock:
            test = self._tests.get(test_id)
            if not test:
                return None
        
        start_time = time.time()
        
        try:
            result = test.test_fn()
            status = TestResult.PASSED if result else TestResult.FAILED
            error_msg = None
        except Exception as e:
            status = TestResult.ERROR
            error_msg = str(e)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        execution = TestExecution(
            test_id=test_id,
            result=status,
            duration_ms=duration_ms,
            error_message=error_msg
        )
        
        with self._lock:
            self._results.append(execution)
        
        return execution
    
    def run_all_tests(self) -> Dict[str, TestExecution]:
        """Run all registered tests."""
        results = {}
        
        with self._lock:
            test_ids = list(self._tests.keys())
        
        for test_id in test_ids:
            result = self.run_test(test_id)
            if result:
                results[test_id] = result
        
        return results
    
    def get_test_report(self) -> Dict[str, Any]:
        """Get comprehensive test report."""
        with self._lock:
            results = self._results.copy()
        
        total = len(results)
        passed = sum(1 for r in results if r.result == TestResult.PASSED)
        failed = sum(1 for r in results if r.result == TestResult.FAILED)
        errors = sum(1 for r in results if r.result == TestResult.ERROR)
        total_time = sum(r.duration_ms for r in results)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "total_time_ms": total_time,
            "average_time_ms": total_time / total if total > 0 else 0
        }


class ChaosEngineer:
    """Introduces chaos for resilience testing."""
    
    def __init__(self):
        self._chaos_injections: Dict[str, Callable[[], bool]] = {}
        self._lock = Lock()
    
    def register_injection(self, injection_name: str, injection_fn: Callable[[], bool]) -> bool:
        """Register a chaos injection."""
        with self._lock:
            if injection_name in self._chaos_injections:
                return False
            
            self._chaos_injections[injection_name] = injection_fn
            return True
    
    def inject_chaos(self, injection_name: str) -> Optional[bool]:
        """Inject chaos."""
        with self._lock:
            injection = self._chaos_injections.get(injection_name)
            if not injection:
                return None
        
        try:
            return injection()
        except Exception:
            return False
    
    def run_chaos_test(self, test_fn: Callable[[Callable[[], bool]], bool], injection_name: str) -> bool:
        """Run test with chaos injection."""
        injection = self._chaos_injections.get(injection_name)
        if not injection:
            return False
        
        return test_fn(injection)


class PerformanceTester:
    """Tests system performance."""
    
    def __init__(self):
        self._benchmarks: Dict[str, List[float]] = {}
        self._baselines: Dict[str, float] = {}
        self._lock = Lock()
    
    def record_performance(self, operation_name: str, time_ms: float) -> None:
        """Record performance measurement."""
        with self._lock:
            if operation_name not in self._benchmarks:
                self._benchmarks[operation_name] = []
            
            self._benchmarks[operation_name].append(time_ms)
    
    def set_baseline(self, operation_name: str, baseline_ms: float) -> bool:
        """Set performance baseline."""
        with self._lock:
            self._baselines[operation_name] = baseline_ms
            return True
    
    def check_performance(self, operation_name: str, tolerance_percent: float = 10.0) -> bool:
        """Check if performance meets baseline."""
        with self._lock:
            baseline = self._baselines.get(operation_name)
            if baseline is None:
                return True
            
            times = self._benchmarks.get(operation_name, [])
            if not times:
                return True
            
            avg_time = sum(times) / len(times)
            threshold = baseline * (1 + tolerance_percent / 100)
            
            return avg_time <= threshold
    
    def get_performance_report(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """Get performance report."""
        with self._lock:
            times = self._benchmarks.get(operation_name, [])
            baseline = self._baselines.get(operation_name)
            
            if not times:
                return None
            
            avg = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            return {
                "operation": operation_name,
                "average_ms": avg,
                "min_ms": min_time,
                "max_ms": max_time,
                "count": len(times),
                "baseline_ms": baseline
            }


class ValidationFramework:
    """Framework for comprehensive validation."""
    
    def __init__(self):
        self._validators: Dict[str, Callable[[Any], bool]] = {}
        self._lock = Lock()
    
    def register_validator(self, validator_name: str, validator_fn: Callable[[Any], bool]) -> bool:
        """Register a validator."""
        with self._lock:
            if validator_name in self._validators:
                return False
            
            self._validators[validator_name] = validator_fn
            return True
    
    def validate_component(self, component_name: str, component_data: Any) -> Dict[str, bool]:
        """Validate a component."""
        results = {}
        
        with self._lock:
            validators = self._validators.copy()
        
        for validator_name, validator_fn in validators.items():
            try:
                results[validator_name] = validator_fn(component_data)
            except Exception:
                results[validator_name] = False
        
        return results
    
    def is_component_valid(self, component_name: str, component_data: Any) -> bool:
        """Check if component is valid."""
        results = self.validate_component(component_name, component_data)
        return all(results.values()) if results else False


class QualityGate:
    """Quality gate for release decisions."""
    
    def __init__(self):
        self._criteria: Dict[str, Callable[[], bool]] = {}
        self._lock = Lock()
    
    def add_criterion(self, criterion_name: str, check_fn: Callable[[], bool]) -> bool:
        """Add quality gate criterion."""
        with self._lock:
            if criterion_name in self._criteria:
                return False
            
            self._criteria[criterion_name] = check_fn
            return True
    
    def check_quality_gate(self) -> tuple[bool, Dict[str, bool]]:
        """Check quality gate."""
        results = {}
        
        with self._lock:
            criteria = self._criteria.copy()
        
        for criterion_name, check_fn in criteria.items():
            try:
                results[criterion_name] = check_fn()
            except Exception:
                results[criterion_name] = False
        
        all_passed = all(results.values())
        return all_passed, results


# ============================================================================
# TEST SUITE
# ============================================================================

class TestRunner_Tests:
    """Test TestRunner functionality."""
    
    def test_register_test(self):
        """Test registering test case."""
        runner = TestRunner()
        test = TestCase(
            "test1",
            "Test 1",
            TestType.UNIT,
            lambda: True
        )
        
        assert runner.register_test(test)
    
    def test_run_test_success(self):
        """Test running successful test."""
        runner = TestRunner()
        test = TestCase(
            "test1",
            "Test 1",
            TestType.UNIT,
            lambda: True
        )
        runner.register_test(test)
        
        execution = runner.run_test("test1")
        assert execution.result == TestResult.PASSED
    
    def test_run_test_failure(self):
        """Test running failed test."""
        runner = TestRunner()
        test = TestCase(
            "test1",
            "Test 1",
            TestType.UNIT,
            lambda: False
        )
        runner.register_test(test)
        
        execution = runner.run_test("test1")
        assert execution.result == TestResult.FAILED
    
    def test_run_test_error(self):
        """Test running test with error."""
        runner = TestRunner()
        
        def error_test():
            raise Exception("Test error")
        
        test = TestCase(
            "test1",
            "Test 1",
            TestType.UNIT,
            error_test
        )
        runner.register_test(test)
        
        execution = runner.run_test("test1")
        assert execution.result == TestResult.ERROR
    
    def test_run_all_tests(self):
        """Test running all tests."""
        runner = TestRunner()
        
        test1 = TestCase("test1", "Test 1", TestType.UNIT, lambda: True)
        test2 = TestCase("test2", "Test 2", TestType.UNIT, lambda: True)
        
        runner.register_test(test1)
        runner.register_test(test2)
        
        results = runner.run_all_tests()
        assert len(results) == 2
    
    def test_get_test_report(self):
        """Test getting test report."""
        runner = TestRunner()
        
        test = TestCase("test1", "Test 1", TestType.UNIT, lambda: True)
        runner.register_test(test)
        runner.run_test("test1")
        
        report = runner.get_test_report()
        assert report["total_tests"] == 1
        assert report["passed"] == 1


class TestChaosEngineer:
    """Test ChaosEngineer functionality."""
    
    def test_register_injection(self):
        """Test registering chaos injection."""
        engineer = ChaosEngineer()
        injection = lambda: True
        
        assert engineer.register_injection("network_delay", injection)
    
    def test_inject_chaos(self):
        """Test injecting chaos."""
        engineer = ChaosEngineer()
        engineer.register_injection("network_delay", lambda: True)
        
        result = engineer.inject_chaos("network_delay")
        assert result is True


class TestPerformanceTester:
    """Test PerformanceTester functionality."""
    
    def test_record_performance(self):
        """Test recording performance."""
        tester = PerformanceTester()
        tester.record_performance("operation1", 100.0)
        
        report = tester.get_performance_report("operation1")
        assert report["average_ms"] == 100.0
    
    def test_set_baseline(self):
        """Test setting baseline."""
        tester = PerformanceTester()
        assert tester.set_baseline("operation1", 150.0)
    
    def test_check_performance(self):
        """Test checking performance."""
        tester = PerformanceTester()
        tester.set_baseline("operation1", 150.0)
        tester.record_performance("operation1", 140.0)
        
        assert tester.check_performance("operation1", 10.0)
    
    def test_check_performance_fails(self):
        """Test performance check fails."""
        tester = PerformanceTester()
        tester.set_baseline("operation1", 150.0)
        tester.record_performance("operation1", 200.0)
        
        assert not tester.check_performance("operation1", 10.0)


class TestValidationFramework:
    """Test ValidationFramework functionality."""
    
    def test_register_validator(self):
        """Test registering validator."""
        framework = ValidationFramework()
        validator = lambda data: data is not None
        
        assert framework.register_validator("not_null", validator)
    
    def test_validate_component(self):
        """Test validating component."""
        framework = ValidationFramework()
        framework.register_validator("not_null", lambda data: data is not None)
        
        results = framework.validate_component("component1", {"key": "value"})
        assert results["not_null"] is True
    
    def test_is_component_valid(self):
        """Test checking if component is valid."""
        framework = ValidationFramework()
        framework.register_validator("not_null", lambda data: data is not None)
        
        assert framework.is_component_valid("component1", {"key": "value"})


class TestQualityGate:
    """Test QualityGate functionality."""
    
    def test_add_criterion(self):
        """Test adding quality criterion."""
        gate = QualityGate()
        assert gate.add_criterion("test_coverage", lambda: True)
    
    def test_check_quality_gate_pass(self):
        """Test quality gate passes."""
        gate = QualityGate()
        gate.add_criterion("test_coverage", lambda: True)
        gate.add_criterion("performance", lambda: True)
        
        passed, results = gate.check_quality_gate()
        assert passed
    
    def test_check_quality_gate_fail(self):
        """Test quality gate fails."""
        gate = QualityGate()
        gate.add_criterion("test_coverage", lambda: True)
        gate.add_criterion("performance", lambda: False)
        
        passed, results = gate.check_quality_gate()
        assert not passed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
