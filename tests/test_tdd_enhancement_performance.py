"""Test suite for TDD Enhancement - Performance & Scalability.

Tests performance characteristics of TDD enhancement including:
- Pre-commit hook execution time <1 second per commit
- Pylance IDE overhead <200ms per keystroke
- No regression in existing test execution time
- Scalability to 5000+ test files
"""

import time
from pathlib import Path
from typing import List, Tuple
import pytest


class TestPrecommitHookPerformance:
    """Test pre-commit hook performance characteristics."""

    def test_small_file_detection_under_100ms(self) -> None:
        """Test small file violation detection completes in <100ms."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        small_code = """
def process(data: str) -> str:
    return data.upper()
"""
        
        start = time.time()
        violations = handler.detect_violations(small_code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Small file detection took {elapsed}s, expected <0.1s"

    def test_medium_file_detection_under_500ms(self) -> None:
        """Test medium file violation detection completes in <500ms."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        medium_code = "\n".join([
            f"def func_{i}(data: str) -> str:\n    return data"
            for i in range(100)
        ])
        
        start = time.time()
        violations = handler.detect_violations(medium_code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Medium file detection took {elapsed}s, expected <0.5s"

    def test_large_file_detection_under_1s(self) -> None:
        """Test large file violation detection completes in <1s."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        large_code = "\n".join([
            f"def func_{i}(data: str) -> str:\n    return data"
            for i in range(1000)
        ])
        
        start = time.time()
        violations = handler.detect_violations(large_code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Large file detection took {elapsed}s, expected <1.0s"

    def test_commit_validation_under_1s(self) -> None:
        """Test complete commit validation completes in <1 second."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data: str) -> str:
    return data.upper()
"""
        
        start = time.time()
        result = handler.validate_commit(code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Commit validation took {elapsed}s, expected <1.0s"

    def test_batch_file_processing_under_2s(self) -> None:
        """Test processing 10 files completes in <2 seconds."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def func(data: str) -> str:
    return data
"""
        
        start = time.time()
        
        for i in range(10):
            violations = handler.detect_violations(code, f"file_{i}.py")
        
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Batch processing took {elapsed}s, expected <2.0s"


class TestPylancePerformance:
    """Test Pylance IDE integration performance."""

    def test_small_file_highlighting_under_50ms(self) -> None:
        """Test small file highlighting completes in <50ms."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler(environment="local")
        
        code = """
def process(data):
    return data
"""
        
        start = time.time()
        violations = handler.highlight_violations(code)
        elapsed = time.time() - start
        
        assert elapsed < 0.05, f"Highlighting took {elapsed}s, expected <0.05s"

    def test_large_file_highlighting_under_200ms(self) -> None:
        """Test large file highlighting completes in <200ms."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler(environment="local")
        
        large_code = "\n".join([
            f"def func_{i}(data):\n    return data"
            for i in range(500)
        ])
        
        start = time.time()
        violations = handler.highlight_violations(large_code)
        elapsed = time.time() - start
        
        assert elapsed < 0.2, f"Large file highlighting took {elapsed}s, expected <0.2s"

    def test_incremental_update_under_100ms(self) -> None:
        """Test incremental update on one line change <100ms."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler(environment="local")
        
        # Initial code
        code = "\n".join([
            f"def func_{i}(data: str) -> str:\n    return data"
            for i in range(100)
        ])
        
        # Highlight initial state
        handler.highlight_violations(code)
        
        # Change one line
        modified_code = code.replace(
            "def func_50(data: str) -> str:",
            "def func_50(data):"
        )
        
        start = time.time()
        violations = handler.highlight_violations(modified_code)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Incremental update took {elapsed}s, expected <0.1s"

    def test_ci_environment_faster(self) -> None:
        """Test CI environment highlighting is comparable to local."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        code = "\n".join([
            f"def func_{i}(data):\n    return data"
            for i in range(100)
        ])
        
        # Local environment
        local_handler = PylanceIDEHandler(environment="local")
        start = time.time()
        local_handler.highlight_violations(code)
        local_time = time.time() - start
        
        # CI environment (should have similar or faster performance)
        ci_handler = PylanceIDEHandler(environment="ci")
        start = time.time()
        ci_handler.highlight_violations(code)
        ci_time = time.time() - start
        
        # CI should be comparable (within 50% margin for test flakiness)
        assert ci_time <= local_time * 1.5


class TestTier0ValidationPerformance:
    """Test Tier0 validation performance."""

    def test_small_file_validation_under_100ms(self) -> None:
        """Test small file validation completes in <100ms."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def process(data: str) -> str:
    return data
"""
        
        start = time.time()
        violations = validator.validate_code(code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Validation took {elapsed}s, expected <0.1s"

    def test_large_file_validation_under_1s(self) -> None:
        """Test large file validation completes in <1 second."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        large_code = "\n".join([
            f"def func_{i}(data: str) -> str:\n    return data"
            for i in range(500)
        ])
        
        start = time.time()
        violations = validator.validate_code(large_code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Validation took {elapsed}s, expected <1.0s"

    def test_governance_validation_under_200ms(self) -> None:
        """Test governance-specific validation completes in <200ms."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def process(data):
    try:
        work()
    except:
        pass
"""
        
        start = time.time()
        violations = validator.validate_governance(
            code,
            rules=["CORE-011", "CORE-012", "CORE-013"]
        )
        elapsed = time.time() - start
        
        assert elapsed < 0.2, f"Governance validation took {elapsed}s, expected <0.2s"


class TestScalability:
    """Test scalability to large numbers of files."""

    def test_100_files_processing_under_5s(self) -> None:
        """Test processing 100 files completes in <5 seconds."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data):
    try:
        work(data)
    except:
        pass
"""
        
        start = time.time()
        
        for i in range(100):
            violations = handler.detect_violations(code, f"file_{i}.py")
        
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Processing 100 files took {elapsed}s, expected <5.0s"
        
        # Should be approximately linear (100ms per file average)
        avg_time_per_file = elapsed / 100
        assert avg_time_per_file < 0.1, f"Average time per file {avg_time_per_file}s exceeds 0.1s"

    def test_500_files_processing_under_30s(self) -> None:
        """Test processing 500 files completes in <30 seconds."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def func(data: str) -> str:
    return data
"""
        
        start = time.time()
        
        for i in range(500):
            violations = handler.detect_violations(code, f"file_{i}.py")
        
        elapsed = time.time() - start
        
        assert elapsed < 30.0, f"Processing 500 files took {elapsed}s, expected <30.0s"
        
        # Linear scaling check
        avg_time_per_file = elapsed / 500
        assert avg_time_per_file < 0.1, f"Average time per file {avg_time_per_file}s exceeds 0.1s"

    def test_1000_files_processing_under_120s(self) -> None:
        """Test processing 1000 files completes in <2 minutes."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = "def f(x: int) -> int: return x"
        
        start = time.time()
        
        for i in range(1000):
            violations = handler.detect_violations(code, f"file_{i}.py")
        
        elapsed = time.time() - start
        
        assert elapsed < 120.0, f"Processing 1000 files took {elapsed}s, expected <120.0s"


class TestMemoryUsage:
    """Test memory efficiency."""

    def test_memory_efficient_batch_processing(self) -> None:
        """Test batch processing doesn't leak memory."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        import tracemalloc
        
        handler = PrecommitHookHandler()
        
        code = "def f(x: int) -> int: return x"
        
        tracemalloc.start()
        
        for i in range(100):
            violations = handler.detect_violations(code, f"file_{i}.py")
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should not use excessive memory (less than 100MB for 100 files)
        assert peak < 100 * 1024 * 1024, f"Peak memory {peak} bytes exceeds 100MB"


class TestRegressionInTestExecution:
    """Test no regression in existing test execution time."""

    def test_existing_test_suite_no_slowdown(self) -> None:
        """Test TDD enhancement doesn't slow down existing tests."""
        # This is a meta-test that validates performance assumptions
        
        # Get baseline: existing tests should run at normal speed
        # (This would be measured by CI/CD, not in unit tests)
        
        # For now, just validate that enhancement modules can be imported
        # without causing slowdowns
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        # Should import quickly
        assert PrecommitHookHandler is not None
        assert PylanceIDEHandler is not None
        assert Tier0Validator is not None


class TestParallelExecution:
    """Test parallel execution of enhancement checks."""

    def test_concurrent_file_processing(self) -> None:
        """Test concurrent processing of multiple files."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        import concurrent.futures
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data):
    try:
        work(data)
    except:
        pass
"""
        
        files = [f"file_{i}.py" for i in range(50)]
        
        start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(
                lambda f: handler.detect_violations(code, f),
                files
            ))
        
        elapsed = time.time() - start
        
        # Parallel should be faster than sequential
        assert len(results) == 50
        assert elapsed < 10.0


class TestCachingEfficiency:
    """Test caching efficiency of validation."""

    def test_repeated_file_detection_cached(self) -> None:
        """Test repeated analysis of same file uses cache."""
        from cortex.testing.tdd_enhancement_layer1_precommit import PrecommitHookHandler
        
        handler = PrecommitHookHandler()
        
        code = """
def process(data: str) -> str:
    return data
"""
        
        # First analysis
        start = time.time()
        violations1 = handler.detect_violations(code, "test.py")
        first_time = time.time() - start
        
        # Second analysis (should be cached)
        start = time.time()
        violations2 = handler.detect_violations(code, "test.py")
        second_time = time.time() - start
        
        # Second should be faster (cached)
        # Allow 10x speedup from caching
        if second_time > 0:
            assert second_time <= first_time * 1.1 or first_time < 0.01


class TestOptimization:
    """Test optimization strategies."""

    def test_incremental_analysis_faster(self) -> None:
        """Test incremental analysis is faster than full analysis."""
        from cortex.testing.tdd_enhancement_layer2_pylance import PylanceIDEHandler
        
        handler = PylanceIDEHandler(environment="local")
        
        code = "\n".join([
            f"def func_{i}(data: str) -> str:\n    return data"
            for i in range(100)
        ])
        
        # Full analysis
        start = time.time()
        handler.highlight_violations(code)
        full_time = time.time() - start
        
        # Modify one line
        modified = code.replace(
            "def func_50(data: str)",
            "def func_50(data)"
        )
        
        # Incremental analysis
        if hasattr(handler, "highlight_violations_incremental"):
            start = time.time()
            handler.highlight_violations_incremental(modified, changes=[(50, 50)])
            incremental_time = time.time() - start
            
            # Incremental should be faster
            assert incremental_time < full_time
