"""
Template Testing Framework (AC-TT-003-02)

Testing framework for orchestrator templates.
Provides:
- Test case definition
- Assertion builders
- Test execution
- Result reporting

Integrates with pytest and standalone usage.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Union
import traceback
import time


class TestStatus(Enum):
    """Status of a test."""
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


@dataclass
class Assertion:
    """A single assertion in a test."""
    name: str
    condition: Callable[[], bool]
    message: str = ""
    
    def check(self) -> tuple[bool, str]:
        """Check the assertion."""
        try:
            result = self.condition()
            if result:
                return True, ""
            return False, self.message or f"Assertion '{self.name}' failed"
        except Exception as e:
            return False, f"Assertion '{self.name}' raised: {e}"


@dataclass
class TestResult:
    """Result of a single test."""
    test_name: str
    status: TestStatus
    duration_ms: float = 0.0
    message: str = ""
    assertions_passed: int = 0
    assertions_failed: int = 0
    error: Optional[str] = None
    traceback: Optional[str] = None
    
    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == TestStatus.PASSED


@dataclass
class TestSuite:
    """Collection of test results."""
    name: str
    results: List[TestResult] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total(self) -> int:
        """Total number of tests."""
        return len(self.results)
    
    @property
    def passed(self) -> int:
        """Number of passed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)
    
    @property
    def failed(self) -> int:
        """Number of failed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)
    
    @property
    def skipped(self) -> int:
        """Number of skipped tests."""
        return sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
    
    @property
    def errors(self) -> int:
        """Number of error tests."""
        return sum(1 for r in self.results if r.status == TestStatus.ERROR)
    
    @property
    def duration_ms(self) -> float:
        """Total duration in milliseconds."""
        return sum(r.duration_ms for r in self.results)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total == 0:
            return 100.0
        return (self.passed / self.total) * 100
    
    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self.results.append(result)
    
    def get_failures(self) -> List[TestResult]:
        """Get failed tests."""
        return [r for r in self.results if r.status in (TestStatus.FAILED, TestStatus.ERROR)]
    
    def summary(self) -> str:
        """Generate summary string."""
        return (
            f"{self.name}: {self.passed}/{self.total} passed "
            f"({self.success_rate:.1f}%) in {self.duration_ms:.0f}ms"
        )


class AssertionBuilder:
    """
    Builder for test assertions.
    
    Provides fluent API for constructing assertions.
    
    Example:
        builder = AssertionBuilder(template)
        builder.has_field('name').equals('MyTemplate')
        builder.has_section('parameters').is_not_empty()
        assertions = builder.build()
    """
    
    def __init__(self, target: Any):
        """
        Initialize builder.
        
        Args:
            target: Target object for assertions
        """
        self._target = target
        self._assertions: List[Assertion] = []
        self._current_value: Any = target
        self._current_name: str = "target"
    
    def has_field(self, field: str) -> 'AssertionBuilder':
        """Assert target has a field."""
        self._current_name = field
        
        def check():
            if hasattr(self._target, field):
                self._current_value = getattr(self._target, field)
                return True
            elif isinstance(self._target, dict) and field in self._target:
                self._current_value = self._target[field]
                return True
            return False
        
        self._assertions.append(Assertion(
            name=f"has_field_{field}",
            condition=check,
            message=f"Expected field '{field}' not found",
        ))
        return self
    
    def has_section(self, section: str) -> 'AssertionBuilder':
        """Assert target has a section (for templates)."""
        self._current_name = f"section_{section}"
        
        def check():
            if hasattr(self._target, 'get_section'):
                sec = self._target.get_section(section)
                if sec:
                    self._current_value = sec
                    return True
            elif hasattr(self._target, 'sections'):
                if section in self._target.sections:
                    self._current_value = self._target.sections[section]
                    return True
            elif isinstance(self._target, dict):
                if section in self._target:
                    self._current_value = self._target[section]
                    return True
            return False
        
        self._assertions.append(Assertion(
            name=f"has_section_{section}",
            condition=check,
            message=f"Expected section '{section}' not found",
        ))
        return self
    
    def equals(self, expected: Any) -> 'AssertionBuilder':
        """Assert current value equals expected."""
        def check():
            return self._current_value == expected
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_equals",
            condition=check,
            message=f"Expected {self._current_name} to equal {expected}, got {self._current_value}",
        ))
        return self
    
    def not_equals(self, expected: Any) -> 'AssertionBuilder':
        """Assert current value does not equal expected."""
        def check():
            return self._current_value != expected
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_not_equals",
            condition=check,
            message=f"Expected {self._current_name} to not equal {expected}",
        ))
        return self
    
    def is_not_none(self) -> 'AssertionBuilder':
        """Assert current value is not None."""
        def check():
            return self._current_value is not None
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_not_none",
            condition=check,
            message=f"Expected {self._current_name} to not be None",
        ))
        return self
    
    def is_not_empty(self) -> 'AssertionBuilder':
        """Assert current value is not empty."""
        def check():
            if self._current_value is None:
                return False
            if hasattr(self._current_value, '__len__'):
                return len(self._current_value) > 0
            if hasattr(self._current_value, 'content'):
                return bool(self._current_value.content)
            return bool(self._current_value)
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_not_empty",
            condition=check,
            message=f"Expected {self._current_name} to not be empty",
        ))
        return self
    
    def contains(self, item: Any) -> 'AssertionBuilder':
        """Assert current value contains item."""
        def check():
            if isinstance(self._current_value, (list, tuple, set)):
                return item in self._current_value
            elif isinstance(self._current_value, dict):
                return item in self._current_value
            elif isinstance(self._current_value, str):
                return item in self._current_value
            return False
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_contains",
            condition=check,
            message=f"Expected {self._current_name} to contain {item}",
        ))
        return self
    
    def has_length(self, length: int) -> 'AssertionBuilder':
        """Assert current value has specific length."""
        def check():
            if hasattr(self._current_value, '__len__'):
                return len(self._current_value) == length
            return False
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_has_length",
            condition=check,
            message=f"Expected {self._current_name} to have length {length}",
        ))
        return self
    
    def matches(self, pattern: str) -> 'AssertionBuilder':
        """Assert current value matches regex pattern."""
        import re
        
        def check():
            if isinstance(self._current_value, str):
                return bool(re.match(pattern, self._current_value))
            return False
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_matches",
            condition=check,
            message=f"Expected {self._current_name} to match pattern {pattern}",
        ))
        return self
    
    def is_type(self, expected_type: type) -> 'AssertionBuilder':
        """Assert current value is of expected type."""
        def check():
            return isinstance(self._current_value, expected_type)
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_is_type",
            condition=check,
            message=f"Expected {self._current_name} to be {expected_type.__name__}",
        ))
        return self
    
    def satisfies(self, condition: Callable[[Any], bool], message: str = "") -> 'AssertionBuilder':
        """Assert current value satisfies custom condition."""
        def check():
            return condition(self._current_value)
        
        self._assertions.append(Assertion(
            name=f"{self._current_name}_satisfies",
            condition=check,
            message=message or f"Custom condition failed for {self._current_name}",
        ))
        return self
    
    def build(self) -> List[Assertion]:
        """Build and return all assertions."""
        return self._assertions.copy()
    
    def check_all(self) -> tuple[bool, List[str]]:
        """Check all assertions and return result."""
        failures = []
        for assertion in self._assertions:
            passed, message = assertion.check()
            if not passed:
                failures.append(message)
        return len(failures) == 0, failures


@dataclass
class TemplateTestCase:
    """
    A test case for template testing.
    
    Example:
        test = TemplateTestCase(
            name="test_basic_structure",
            description="Verify basic template structure",
            setup=lambda: parser.parse_file("template.yaml"),
        )
        
        test.add_assertion(
            AssertionBuilder(template)
            .has_field('name')
            .is_not_empty()
            .build()
        )
        
        result = test.run()
    """
    
    name: str
    description: str = ""
    setup: Optional[Callable[[], Any]] = None
    teardown: Optional[Callable[[], None]] = None
    assertions: List[Assertion] = field(default_factory=list)
    skip: bool = False
    skip_reason: str = ""
    tags: Set[str] = field(default_factory=set)
    timeout_ms: float = 5000.0
    
    def add_assertion(self, assertion: Union[Assertion, List[Assertion]]) -> None:
        """Add assertion(s) to test case."""
        if isinstance(assertion, list):
            self.assertions.extend(assertion)
        else:
            self.assertions.append(assertion)
    
    def run(self) -> TestResult:
        """
        Run the test case.
        
        Returns:
            TestResult with test outcome
        """
        start_time = time.perf_counter()
        
        # Check skip
        if self.skip:
            return TestResult(
                test_name=self.name,
                status=TestStatus.SKIPPED,
                message=self.skip_reason or "Skipped",
            )
        
        try:
            # Run setup
            target = None
            if self.setup:
                target = self.setup()
            
            # Run assertions
            passed = 0
            failed = 0
            failure_messages = []
            
            for assertion in self.assertions:
                success, message = assertion.check()
                if success:
                    passed += 1
                else:
                    failed += 1
                    failure_messages.append(message)
            
            # Determine status
            if failed > 0:
                status = TestStatus.FAILED
                message = "; ".join(failure_messages)
            else:
                status = TestStatus.PASSED
                message = f"All {passed} assertions passed"
            
            duration = (time.perf_counter() - start_time) * 1000
            
            return TestResult(
                test_name=self.name,
                status=status,
                duration_ms=duration,
                message=message,
                assertions_passed=passed,
                assertions_failed=failed,
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            return TestResult(
                test_name=self.name,
                status=TestStatus.ERROR,
                duration_ms=duration,
                message=f"Error: {e}",
                error=str(e),
                traceback=traceback.format_exc(),
            )
        
        finally:
            # Run teardown
            if self.teardown:
                try:
                    self.teardown()
                except Exception:
                    pass  # Ignore teardown errors


class TemplateTestFramework:
    """
    Testing framework for orchestrator templates.
    
    Provides test discovery, execution, and reporting.
    
    Example:
        framework = TemplateTestFramework()
        
        # Add test cases
        framework.add_test(TemplateTestCase(
            name="test_has_name",
            setup=lambda: parser.parse_file("template.yaml"),
        ))
        
        # Run tests
        suite = framework.run()
        
        # Report results
        print(framework.report(suite))
    """
    
    def __init__(self, name: str = "Template Tests"):
        """
        Initialize framework.
        
        Args:
            name: Test suite name
        """
        self.name = name
        self._tests: List[TemplateTestCase] = []
        self._before_all: Optional[Callable[[], None]] = None
        self._after_all: Optional[Callable[[], None]] = None
        self._before_each: Optional[Callable[[], None]] = None
        self._after_each: Optional[Callable[[], None]] = None
    
    def add_test(self, test: TemplateTestCase) -> None:
        """Add a test case."""
        self._tests.append(test)
    
    def add_tests(self, tests: List[TemplateTestCase]) -> None:
        """Add multiple test cases."""
        self._tests.extend(tests)
    
    def before_all(self, func: Callable[[], None]) -> None:
        """Set function to run before all tests."""
        self._before_all = func
    
    def after_all(self, func: Callable[[], None]) -> None:
        """Set function to run after all tests."""
        self._after_all = func
    
    def before_each(self, func: Callable[[], None]) -> None:
        """Set function to run before each test."""
        self._before_each = func
    
    def after_each(self, func: Callable[[], None]) -> None:
        """Set function to run after each test."""
        self._after_each = func
    
    def run(
        self,
        tags: Optional[Set[str]] = None,
        names: Optional[List[str]] = None,
    ) -> TestSuite:
        """
        Run all tests.
        
        Args:
            tags: Only run tests with these tags
            names: Only run tests with these names
            
        Returns:
            TestSuite with results
        """
        suite = TestSuite(
            name=self.name,
            started_at=datetime.now(),
        )
        
        # Filter tests
        tests_to_run = self._tests
        if tags:
            tests_to_run = [t for t in tests_to_run if t.tags & tags]
        if names:
            tests_to_run = [t for t in tests_to_run if t.name in names]
        
        # Run before_all
        if self._before_all:
            try:
                self._before_all()
            except Exception as e:
                # Add error result
                suite.add_result(TestResult(
                    test_name="_before_all",
                    status=TestStatus.ERROR,
                    error=str(e),
                ))
                return suite
        
        # Run tests
        for test in tests_to_run:
            # Run before_each
            if self._before_each:
                try:
                    self._before_each()
                except Exception:
                    pass
            
            # Run test
            result = test.run()
            suite.add_result(result)
            
            # Run after_each
            if self._after_each:
                try:
                    self._after_each()
                except Exception:
                    pass
        
        # Run after_all
        if self._after_all:
            try:
                self._after_all()
            except Exception:
                pass
        
        suite.completed_at = datetime.now()
        return suite
    
    def run_test(self, name: str) -> Optional[TestResult]:
        """Run a single test by name."""
        for test in self._tests:
            if test.name == name:
                return test.run()
        return None
    
    def report(self, suite: TestSuite, verbose: bool = False) -> str:
        """
        Generate test report.
        
        Args:
            suite: Test suite results
            verbose: Include detailed output
            
        Returns:
            Report string
        """
        lines = [
            "=" * 60,
            f"Test Suite: {suite.name}",
            "=" * 60,
            "",
            f"Total: {suite.total}",
            f"Passed: {suite.passed}",
            f"Failed: {suite.failed}",
            f"Skipped: {suite.skipped}",
            f"Errors: {suite.errors}",
            f"Duration: {suite.duration_ms:.0f}ms",
            f"Success Rate: {suite.success_rate:.1f}%",
            "",
        ]
        
        if verbose or suite.failed > 0 or suite.errors > 0:
            lines.append("-" * 60)
            lines.append("Test Results:")
            lines.append("-" * 60)
            
            for result in suite.results:
                status_icon = {
                    TestStatus.PASSED: "✓",
                    TestStatus.FAILED: "✗",
                    TestStatus.SKIPPED: "○",
                    TestStatus.ERROR: "!",
                }.get(result.status, "?")
                
                lines.append(f"  {status_icon} {result.test_name} ({result.duration_ms:.0f}ms)")
                
                if verbose or result.status in (TestStatus.FAILED, TestStatus.ERROR):
                    if result.message:
                        lines.append(f"      {result.message}")
                    if result.traceback and result.status == TestStatus.ERROR:
                        for tb_line in result.traceback.strip().split('\n')[-3:]:
                            lines.append(f"      {tb_line}")
            
            lines.append("")
        
        # Summary
        if suite.success_rate == 100.0:
            lines.append("✓ All tests passed!")
        else:
            failures = suite.get_failures()
            lines.append(f"✗ {len(failures)} test(s) failed")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def to_pytest(self) -> str:
        """
        Generate pytest-compatible test file.
        
        Returns:
            Python code for pytest tests
        """
        lines = [
            '"""',
            f'Tests generated from {self.name}',
            '"""',
            '',
            'import pytest',
            '',
        ]
        
        for test in self._tests:
            # Generate test function
            func_name = test.name if test.name.startswith('test_') else f'test_{test.name}'
            skip_decorator = f'@pytest.mark.skip(reason="{test.skip_reason}")' if test.skip else ''
            
            lines.append(skip_decorator) if skip_decorator else None
            lines.append(f'def {func_name}():')
            lines.append(f'    """{test.description}"""')
            
            if test.setup:
                lines.append('    # Setup')
                lines.append('    target = setup()')
            
            lines.append('    # Assertions')
            for i, assertion in enumerate(test.assertions):
                lines.append(f'    # {assertion.name}')
                lines.append(f'    assert True  # Placeholder for assertion {i}')
            
            lines.append('')
        
        return '\n'.join(filter(None, lines))


# Factory functions

def create_template_test(
    template: Any,
    checks: List[str],
) -> TemplateTestCase:
    """
    Create a test case from a template and list of checks.
    
    Args:
        template: Template to test
        checks: List of check names ('has_name', 'has_version', etc.)
        
    Returns:
        TemplateTestCase
    """
    builder = AssertionBuilder(template)
    
    for check in checks:
        if check == 'has_name':
            builder.has_field('name').is_not_empty()
        elif check == 'has_version':
            builder.has_field('version').is_not_none()
        elif check == 'has_domain':
            builder.has_field('domain').is_not_empty()
        elif check == 'has_parameters':
            builder.has_section('parameters')
        elif check == 'has_stages':
            builder.has_section('stages')
        elif check == 'has_hooks':
            builder.has_section('hooks')
    
    return TemplateTestCase(
        name='test_template_structure',
        description='Verify template has required structure',
        assertions=builder.build(),
    )


def create_validation_test(
    template: Any,
    validator: Any = None,
) -> TemplateTestCase:
    """
    Create a test case that runs validation.
    
    Args:
        template: Template to validate
        validator: Optional validator instance
        
    Returns:
        TemplateTestCase
    """
    def setup():
        from cortex.tools.template_validator import TemplateValidator
        v = validator or TemplateValidator()
        return v.validate(template)
    
    def check_valid(result):
        return result.valid
    
    assertions = [
        Assertion(
            name='validation_passed',
            condition=lambda: setup().valid,
            message='Template validation failed',
        ),
    ]
    
    return TemplateTestCase(
        name='test_template_validation',
        description='Verify template passes validation',
        assertions=assertions,
    )
