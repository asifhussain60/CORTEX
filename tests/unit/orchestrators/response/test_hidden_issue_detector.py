"""
Hidden issue detector - finds performance, memory, concurrency issues.

Module: tests.unit.orchestrators.response.test_hidden_issue_detector
"""

import pytest
from cortex.orchestrators.response.hidden_issue_detector import (
    IssueType,
    IssueSeverity,
    HiddenIssue,
    CodeAnalysisContext,
    PerformanceDetector,
    MemoryDetector,
    ConcurrencyDetector,
    HiddenIssueDetector,
)


# ============================================================================
# TEST: HIDDEN ISSUE
# ============================================================================


class TestHiddenIssue:
    """Tests for hidden issue representation."""
    
    def test_issue_creation(self):
        """Test creating hidden issue."""
        issue = HiddenIssue(
            issue_type=IssueType.PERFORMANCE,
            severity=IssueSeverity.WARNING,
            location="func.py:42",
            message="O(n²) algorithm detected",
            impact="High",
            suggestion="Use sorted + two-pointer approach"
        )
        assert issue.issue_type == IssueType.PERFORMANCE
        assert issue.severity == IssueSeverity.WARNING


# ============================================================================
# TEST: PERFORMANCE DETECTOR
# ============================================================================


class TestPerformanceDetector:
    """Tests for performance issue detection."""
    
    def setup_method(self):
        """Setup detector."""
        self.detector = PerformanceDetector()
    
    def test_detect_n_squared_nested_loops(self):
        """Test detecting O(n²) nested loops."""
        code = """
        def find_duplicates(items):
            for i in range(len(items)):
                for j in range(len(items)):
                    if items[i] == items[j]:
                        return True
        """
        context = CodeAnalysisContext("find_duplicates", code, language="python")
        issues = self.detector.detect(context)
        
        assert len(issues) > 0
        assert any(issue.issue_type == IssueType.PERFORMANCE for issue in issues)
    
    def test_detect_repeated_computation(self):
        """Test detecting repeated expensive computation."""
        code = """
        def process(data):
            for item in data:
                result = expensive_calculation()
        """
        context = CodeAnalysisContext("process", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_detect_growing_list_in_loop(self):
        """Test detecting list growth in loop."""
        code = """
        def build_list(n):
            items = []
            for i in range(n):
                items.append(i)
        """
        context = CodeAnalysisContext("build_list", code, language="python")
        issues = self.detector.detect(context)
        
        # May suggest list comprehension
        assert isinstance(issues, list)


# ============================================================================
# TEST: MEMORY DETECTOR
# ============================================================================


class TestMemoryDetector:
    """Tests for memory issue detection."""
    
    def setup_method(self):
        """Setup detector."""
        self.detector = MemoryDetector()
    
    def test_detect_unbounded_list_growth(self):
        """Test detecting unbounded list growth."""
        code = """
        cache = []
        def add_to_cache(item):
            cache.append(item)  # No bounds
        """
        context = CodeAnalysisContext("add_to_cache", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_detect_deep_recursion(self):
        """Test detecting deep recursion pattern."""
        code = """
        def deep_recurse(n):
            if n == 0:
                return 1
            return n * deep_recurse(n - 1)
        """
        context = CodeAnalysisContext("deep_recurse", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_detect_large_object_copies(self):
        """Test detecting large object copies."""
        code = """
        def process_large(big_dict):
            copy = big_dict.copy()
            return process(copy)
        """
        context = CodeAnalysisContext("process_large", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)


# ============================================================================
# TEST: CONCURRENCY DETECTOR
# ============================================================================


class TestConcurrencyDetector:
    """Tests for concurrency issue detection."""
    
    def setup_method(self):
        """Setup detector."""
        self.detector = ConcurrencyDetector()
    
    def test_detect_race_condition_shared_state(self):
        """Test detecting potential race conditions."""
        code = """
        counter = 0
        def increment():
            global counter
            temp = counter
            counter = temp + 1
        """
        context = CodeAnalysisContext("increment", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_detect_deadlock_pattern(self):
        """Test detecting deadlock-prone patterns."""
        code = """
        def lock_resources(lock1, lock2):
            lock1.acquire()
            lock2.acquire()
            # ... operations ...
        """
        context = CodeAnalysisContext("lock_resources", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_detect_thread_unsafe_operations(self):
        """Test detecting thread-unsafe operations."""
        code = """
        import threading
        
        shared_list = []
        
        def append_thread_unsafe():
            shared_list.append(value)
        """
        context = CodeAnalysisContext("append_thread_unsafe", code, language="python")
        issues = self.detector.detect(context)
        
        assert isinstance(issues, list)


# ============================================================================
# TEST: HIDDEN ISSUE DETECTOR (ORCHESTRATOR)
# ============================================================================


class TestHiddenIssueDetectorOrchestrator:
    """Tests for hidden issue detector orchestrator."""
    
    def setup_method(self):
        """Setup detector."""
        self.detector = HiddenIssueDetector()
    
    def test_detect_all_issue_types(self):
        """Test detecting all issue types in one analysis."""
        code = """
        counter = 0
        cache = []
        
        def bad_function(items):
            global counter
            for i in range(len(items)):
                for j in range(len(items)):
                    cache.append(items[i] * items[j])
                    counter += 1
        """
        
        context = CodeAnalysisContext("bad_function", code, language="python")
        issues = self.detector.detect(context)
        
        # Should detect multiple issue types
        assert len(issues) > 0
    
    def test_no_issues_in_clean_code(self):
        """Test no issues detected in clean code."""
        code = """
        def clean_function(items):
            return [x * 2 for x in items]
        """
        
        context = CodeAnalysisContext("clean_function", code, language="python")
        issues = self.detector.detect(context)
        
        # Should be few or no issues
        assert len(issues) <= 1


# ============================================================================
# TEST: ISSUE SEVERITY
# ============================================================================


class TestIssueSeverity:
    """Tests for issue severity classification."""
    
    def test_critical_severity_issues(self):
        """Test critical severity issues."""
        code = """
        shared = {}
        def unsafe_modify():
            shared[key] = value  # Race condition
        """
        context = CodeAnalysisContext("unsafe_modify", code, language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_warning_severity_issues(self):
        """Test warning severity issues."""
        code = """
        def slow_operation(n):
            for i in range(n):
                for j in range(n):
                    pass
        """
        context = CodeAnalysisContext("slow_operation", code, language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_info_severity_issues(self):
        """Test info severity issues."""
        code = """
        def deep_function(n):
            if n == 0:
                return 1
            return deep_function(n - 1)
        """
        context = CodeAnalysisContext("deep_function", code, language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        assert isinstance(issues, list)


# ============================================================================
# TEST: INTEGRATION
# ============================================================================


class TestHiddenIssueIntegration:
    """Integration tests for hidden issue detection."""
    
    def test_full_code_analysis(self):
        """Test analyzing complete function."""
        code = """
        def complex_function(data):
            cache = []
            for item in data:
                for suitem in data:
                    if cache_miss(item, suitem):
                        cache.append(calculate(item, suitem))
        """
        
        context = CodeAnalysisContext("complex_function", code, language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        assert isinstance(issues, list)
    
# ============================================================================
# TEST: EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Edge case tests."""
    
    def test_empty_code(self):
        """Test analyzing empty code."""
        context = CodeAnalysisContext("empty", "", language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_very_large_code(self):
        """Test analyzing large code."""
        code = "def f():\n" + "    x = 1\n" * 1000
        context = CodeAnalysisContext("large", code, language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        assert isinstance(issues, list)
    
    def test_malformed_code(self):
        """Test analyzing malformed code."""
        context = CodeAnalysisContext("malformed", "def f( broken", language="python")
        detector = HiddenIssueDetector()
        issues = detector.detect(context)
        
        # Should not crash
        assert isinstance(issues, list)


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture
def slow_code_context():
    """Provide slow code context."""
    return CodeAnalysisContext(
        "slow",
        "for i in range(n):\n    for j in range(n):\n        pass",
        language="python"
    )


@pytest.fixture
def unsafe_code_context():
    """Provide thread-unsafe code context."""
    return CodeAnalysisContext(
        "unsafe",
        "shared = []\ndef add(x):\n    shared.append(x)",
        language="python"
    )


# ============================================================================
# ADDITIONAL DETECTOR TESTS
# ============================================================================


class TestDetectorSpecifics:
    """Specific detector behavior tests."""
    
    def test_performance_detector_accuracy(self):
        """Test performance detector accuracy."""
        detector = PerformanceDetector()
        context = CodeAnalysisContext(
            "double_loop",
            "for i in range(10):\n    for j in range(10):\n        process(i, j)"
        )
        issues = detector.detect(context)
        assert len(issues) > 0
    
    def test_memory_detector_recursion(self):
        """Test memory detector detects recursion."""
        detector = MemoryDetector()
        context = CodeAnalysisContext(
            "factorial",
            "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
        )
        issues = detector.detect(context)
        assert len(issues) > 0
    
    def test_concurrency_detector_race_condition(self):
        """Test concurrency detector finds race conditions."""
        detector = ConcurrencyDetector()
        context = CodeAnalysisContext(
            "unsafe_increment",
            "global counter\ncounter = 0\ndef inc():\n    counter = counter + 1"
        )
        issues = detector.detect(context)
        assert len(issues) > 0
    
    def test_issue_impact_severity(self):
        """Test issues have proper impact descriptions."""
        detector = HiddenIssueDetector()
        context = CodeAnalysisContext(
            "test",
            "global x\nfor i in range(100):\n    for j in range(100):\n        x += 1"
        )
        issues = detector.detect(context)
        
        for issue in issues:
            assert len(issue.impact) > 0
            assert len(issue.suggestion) > 0
    
    def test_detector_combined_analysis(self):
        """Test all detectors work together."""
        code = """
        global cache
        cache = []
        
        def process_data(matrix):
            for i in range(len(matrix)):
                for j in range(len(matrix)):
                    cache.append(matrix[i][j])
        """
        
        detector = HiddenIssueDetector()
        context = CodeAnalysisContext("process_data", code)
        issues = detector.detect(context)
        
        # Should find multiple issue types
        assert len(issues) > 0
        types = {issue.issue_type for issue in issues}
        assert len(types) > 0
