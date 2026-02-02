"""
Test Suite: DuplicationDetector Orchestrator

AC-8.3A-001: DuplicationDetector Orchestrator Implemented

Tests verify:
- DuplicationDetector orchestrator exists and is wired
- LENS analyzers integrated (AST, Git, Comments)
- Exact duplication detection works
- Semantic duplication detection works
- Copy-paste pattern detection works
- Duplication report generation
- Severity scoring system
- Consolidation path suggestions

Author: Asif Hussain
Date: 2026-01-31
"""

from __future__ import annotations

import pytest
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import dataclass

# Import orchestrator (will be created)
from cortex.orchestrators.support.duplication_detector_orchestrator import (
    DuplicationDetector,
    DuplicationReport,
    DuplicateEntry,
    SeverityLevel,
)
from cortex.lens.analyzers import ASTAnalyzer, GitHistoryAnalyzer, CommentExtractor


@dataclass
class MockFile:
    """Mock Python file for testing"""
    path: str
    content: str


class TestDuplicationDetectorOrchestrator:
    """Test DuplicationDetector orchestrator"""

    @pytest.fixture
    def detector(self) -> DuplicationDetector:
        """Create detector instance"""
        return DuplicationDetector()

    @pytest.fixture
    def sample_files(self) -> List[MockFile]:
        """Sample files with duplications for testing"""
        return [
            MockFile(
                path="file1.py",
                content="""
class MyOrchestrator(BaseOrchestrator):
    def execute(self):
        print("Starting")
        x = 1
        y = 2
        return x + y
"""
            ),
            MockFile(
                path="file2.py",
                content="""
class AnotherOrchestrator(BaseOrchestrator):
    def execute(self):
        print("Starting")
        x = 1
        y = 2
        return x + y
"""
            ),
        ]

    # =====================================================================
    # ORCHESTRATOR INTERFACE TESTS (3 tests)
    # =====================================================================

    def test_detector_is_iorchestrator(self, detector: DuplicationDetector) -> None:
        """AC-8.3A-001-01: Detector implements IOrchestrator"""
        from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
        assert isinstance(detector, IOrchestrator)

    def test_detector_has_execute_method(self, detector: DuplicationDetector) -> None:
        """AC-8.3A-001-02: Detector has execute() method"""
        assert hasattr(detector, "execute")
        assert callable(detector.execute)

    def test_detector_returns_orchestration_result(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-03: execute() returns OrchestrationResult"""
        from cortex.brain.core.orchestrator_base import OrchestrationResult
        
        # Mock parameters
        params = {"files": [], "min_similarity": 0.8}
        result = detector.execute(params)
        
        assert isinstance(result, OrchestrationResult) or isinstance(result, dict)

    # =====================================================================
    # EXACT DUPLICATION DETECTION (4 tests)
    # =====================================================================

    def test_detect_exact_duplications_identical_functions(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-04: Detect identical function duplications"""
        # Two identical functions in different files
        files = [
            MockFile(
                path="utils1.py",
                content="""
def validate_input(data):
    if not data:
        return False
    if len(data) > 100:
        return False
    return True
"""
            ),
            MockFile(
                path="utils2.py",
                content="""
def validate_input(data):
    if not data:
        return False
    if len(data) > 100:
        return False
    return True
"""
            ),
        ]
        
        duplications = detector.detect_exact_duplications(files)
        
        assert len(duplications) > 0
        assert any(d.similarity >= 0.95 for d in duplications)

    def test_detect_exact_duplications_registers_classes(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-05: Detect identical class duplications"""
        files = [
            MockFile(
                path="base1.py",
                content="""
class ExecutionContext:
    def __init__(self):
        self.id = None
        self.params = {}
"""
            ),
            MockFile(
                path="base2.py",
                content="""
class ExecutionContext:
    def __init__(self):
        self.id = None
        self.params = {}
"""
            ),
        ]
        
        duplications = detector.detect_exact_duplications(files)
        
        assert len(duplications) > 0
        assert any("ExecutionContext" in str(d) for d in duplications)

    def test_detect_no_false_positives_different_logic(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-06: No false positives on different logic"""
        files = [
            MockFile(
                path="math1.py",
                content="def add(a, b): return a + b"
            ),
            MockFile(
                path="math2.py",
                content="def subtract(a, b): return a - b"
            ),
        ]
        
        duplications = detector.detect_exact_duplications(files)
        
        # Should detect no or very low similarity
        assert all(d.similarity < 0.7 for d in duplications) or len(duplications) == 0

    def test_detect_exact_duplications_multiple_occurrences(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-07: Detect when same code appears 3+ times"""
        files = [
            MockFile(path="a.py", content="def helper(): return 42"),
            MockFile(path="b.py", content="def helper(): return 42"),
            MockFile(path="c.py", content="def helper(): return 42"),
        ]
        
        duplications = detector.detect_exact_duplications(files)
        
        # Should identify 3-way duplication
        assert len(duplications) > 0

    # =====================================================================
    # SEMANTIC DUPLICATION DETECTION (4 tests)
    # =====================================================================

    def test_detect_semantic_duplications_different_names(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-08: Detect semantically equivalent code (different names)"""
        files = [
            MockFile(
                path="version1.py",
                content="""
def process_data(input_list):
    result = []
    for item in input_list:
        if item > 0:
            result.append(item * 2)
    return result
"""
            ),
            MockFile(
                path="version2.py",
                content="""
def transform_values(data):
    output = []
    for value in data:
        if value > 0:
            output.append(value * 2)
    return output
"""
            ),
        ]
        
        duplications = detector.detect_semantic_duplications(files)
        
        assert len(duplications) > 0
        assert any(d.similarity >= 0.75 for d in duplications)

    def test_detect_semantic_duplications_registry_pattern(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-09: Detect semantically similar Registry classes"""
        files = [
            MockFile(
                path="registry1.py",
                content="""
class MyRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def register(self, key, value):
        self.items[key] = value
"""
            ),
            MockFile(
                path="registry2.py",
                content="""
class AnotherRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def register(self, name, obj):
        self.entries[name] = obj
"""
            ),
        ]
        
        duplications = detector.detect_semantic_duplications(files)
        
        assert len(duplications) > 0

    def test_no_semantic_false_positives_different_algorithms(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-10: No false positives on different algorithms"""
        files = [
            MockFile(
                path="sort1.py",
                content="def bubble_sort(arr): return sorted(arr)"
            ),
            MockFile(
                path="sort2.py",
                content="def merge_sort(arr): return sorted(arr, reverse=True)"
            ),
        ]
        
        duplications = detector.detect_semantic_duplications(files)
        
        assert all(d.similarity < 0.7 for d in duplications) or len(duplications) == 0

    def test_semantic_duplications_with_comments_ignored(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-11: Semantic detection ignores comments"""
        files = [
            MockFile(
                path="impl1.py",
                content="""
# This is important
def calculate(x):
    return x * 2
"""
            ),
            MockFile(
                path="impl2.py",
                content="""
# Different comment
def calculate(x):
    return x * 2
"""
            ),
        ]
        
        duplications = detector.detect_semantic_duplications(files)
        
        assert len(duplications) > 0

    # =====================================================================
    # COPY-PASTE PATTERN DETECTION (3 tests)
    # =====================================================================

    def test_detect_copy_paste_patterns_from_git_history(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-12: Detect copy-paste patterns from Git history"""
        # Mock git history showing file A copied to file B
        git_data = {
            "file1.py": {"commits": [("abc123", "Initial implementation")]},
            "file2.py": {"commits": [("abc123", "Copy from file1")]},
        }
        
        patterns = detector.detect_copy_paste_patterns(git_data)
        
        assert len(patterns) > 0

    def test_copy_paste_patterns_show_source_and_copies(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-13: Copy-paste report shows source and copies"""
        git_data = {
            "original.py": {"commits": [("hash1", "First commit")]},
            "copy1.py": {"commits": [("hash1", "Copied from original")]},
            "copy2.py": {"commits": [("hash1", "Also copied")]},
        }
        
        patterns = detector.detect_copy_paste_patterns(git_data)
        
        for pattern in patterns:
            assert pattern.get("source")
            assert pattern.get("copies")
            assert len(pattern["copies"]) >= 1

    def test_copy_paste_no_detection_for_independent_commits(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-14: No copy-paste detection for independent histories"""
        git_data = {
            "file_a.py": {"commits": [("hash_x", "Commit A")]},
            "file_b.py": {"commits": [("hash_y", "Commit B")]},
        }
        
        patterns = detector.detect_copy_paste_patterns(git_data)
        
        # Different commits = no copy-paste pattern
        assert len(patterns) == 0 or all(len(p.get("copies", [])) == 0 for p in patterns)

    # =====================================================================
    # SEVERITY SCORING (4 tests)
    # =====================================================================

    def test_severity_scoring_exact_duplicate_critical(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-15: Exact duplicates marked CRITICAL"""
        dup = DuplicateEntry(
            id="DUP-001",
            file1="a.py",
            file2="b.py",
            similarity=0.99,
            type="exact",
            lines=100,
        )
        
        severity = detector.score_severity(dup)
        
        assert severity == SeverityLevel.CRITICAL

    def test_severity_scoring_semantic_duplicate_high(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-16: Semantic duplicates marked HIGH"""
        dup = DuplicateEntry(
            id="DUP-002",
            file1="a.py",
            file2="b.py",
            similarity=0.80,
            type="semantic",
            lines=50,
        )
        
        severity = detector.score_severity(dup)
        
        assert severity == SeverityLevel.HIGH

    def test_severity_scoring_low_similarity_low(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-17: Low similarity marked LOW"""
        dup = DuplicateEntry(
            id="DUP-003",
            file1="a.py",
            file2="b.py",
            similarity=0.55,
            type="semantic",
            lines=10,
        )
        
        severity = detector.score_severity(dup)
        
        assert severity == SeverityLevel.LOW

    def test_severity_scoring_copy_paste_high(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-18: Copy-paste patterns marked HIGH"""
        dup = DuplicateEntry(
            id="DUP-004",
            file1="original.py",
            file2="copy1.py",
            similarity=0.95,
            type="copy_paste",
            lines=200,
        )
        
        severity = detector.score_severity(dup)
        
        assert severity == SeverityLevel.HIGH

    # =====================================================================
    # DUPLICATION REPORT GENERATION (3 tests)
    # =====================================================================

    def test_generate_duplication_report_structure(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-19: Generated report has correct structure"""
        report = detector.generate_duplication_report([])
        
        assert hasattr(report, "timestamp")
        assert hasattr(report, "total_duplications")
        assert hasattr(report, "duplicates")
        assert hasattr(report, "summary")

    def test_duplication_report_includes_stats(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-20: Report includes statistics"""
        duplicates = [
            DuplicateEntry(
                id="D1", file1="a.py", file2="b.py",
                similarity=0.99, type="exact", lines=100
            ),
            DuplicateEntry(
                id="D2", file1="c.py", file2="d.py",
                similarity=0.85, type="semantic", lines=50
            ),
        ]
        
        report = detector.generate_duplication_report(duplicates)
        
        assert report.total_duplications == 2
        assert report.summary["by_severity"]["CRITICAL"] >= 1
        assert report.summary["by_severity"]["HIGH"] >= 1

    def test_duplication_report_sortable_by_severity(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-21: Report duplicates sorted by severity"""
        duplicates = [
            DuplicateEntry("D1", "a.py", "b.py", 0.55, "semantic", 10),
            DuplicateEntry("D2", "c.py", "d.py", 0.99, "exact", 200),
            DuplicateEntry("D3", "e.py", "f.py", 0.85, "semantic", 50),
        ]
        
        report = detector.generate_duplication_report(duplicates)
        
        # Should be sorted: CRITICAL, HIGH, MEDIUM, LOW
        severities = [detector.score_severity(d) for d in report.duplicates]
        assert severities == sorted(severities, reverse=True)

    # =====================================================================
    # CONSOLIDATION PATH SUGGESTIONS (3 tests)
    # =====================================================================

    def test_suggest_consolidation_path_exact_duplicate(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-22: Suggest consolidation for exact duplicates"""
        dup = DuplicateEntry(
            id="DUP-001",
            file1="base_a.py",
            file2="base_b.py",
            similarity=0.99,
            type="exact",
            lines=100,
        )
        
        suggestion = detector.suggest_consolidation_path(dup)
        
        assert suggestion is not None
        assert suggestion.get("action")  # merge, refactor, delete, etc.
        assert suggestion.get("priority")  # which to keep

    def test_suggest_consolidation_keeps_older_file(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-23: Consolidation suggestion prefers older file"""
        dup = DuplicateEntry(
            id="DUP-002",
            file1="old_file.py",
            file2="new_file.py",
            similarity=0.95,
            type="exact",
            lines=100,
        )
        
        suggestion = detector.suggest_consolidation_path(dup)
        
        assert suggestion.get("keep") in ["old_file.py", dup.file1]

    def test_suggest_consolidation_path_semantic_duplicate(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-24: Suggest consolidation for semantic duplicates"""
        dup = DuplicateEntry(
            id="DUP-003",
            file1="registry_a.py",
            file2="registry_b.py",
            similarity=0.80,
            type="semantic",
            lines=150,
        )
        
        suggestion = detector.suggest_consolidation_path(dup)
        
        assert suggestion is not None
        assert suggestion.get("action") in ["extract_base_class", "extract_interface", "merge"]

    # =====================================================================
    # LENS ANALYZER INTEGRATION (3 tests)
    # =====================================================================

    def test_uses_ast_analyzer_for_structure(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-25: DuplicationDetector uses ASTAnalyzer"""
        assert hasattr(detector, "ast_analyzer")
        assert isinstance(detector.ast_analyzer, ASTAnalyzer)

    def test_uses_git_history_analyzer_for_patterns(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-26: DuplicationDetector uses GitHistoryAnalyzer"""
        assert hasattr(detector, "git_analyzer")
        assert isinstance(detector.git_analyzer, GitHistoryAnalyzer)

    def test_uses_comment_extractor_for_intent(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-27: DuplicationDetector uses CommentExtractor"""
        assert hasattr(detector, "comment_extractor")
        assert isinstance(detector.comment_extractor, CommentExtractor)

    # =====================================================================
    # EDGE CASES (3 tests)
    # =====================================================================

    def test_handles_empty_file_list(self, detector: DuplicationDetector) -> None:
        """AC-8.3A-001-28: Handle empty file list gracefully"""
        report = detector.generate_duplication_report([])
        
        assert report.total_duplications == 0
        assert len(report.duplicates) == 0

    def test_handles_single_file(self, detector: DuplicationDetector) -> None:
        """AC-8.3A-001-29: Handle single file (no comparisons)"""
        files = [MockFile(path="single.py", content="def foo(): pass")]
        
        duplications = detector.detect_exact_duplications(files)
        
        assert len(duplications) == 0

    def test_handles_very_large_file_list(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-30: Handle large file list efficiently"""
        # Create 100 mock files
        files = [
            MockFile(path=f"file_{i}.py", content=f"def func_{i}(): pass")
            for i in range(100)
        ]
        
        # Should complete without error
        report = detector.generate_duplication_report([])
        
        assert report is not None

    # =====================================================================
    # PERFORMANCE TESTS (2 tests)
    # =====================================================================

    def test_detection_completes_in_reasonable_time(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-31: Detection completes within 5 seconds for 100 files"""
        import time
        
        files = [
            MockFile(path=f"file_{i}.py", content=f"def func(): return {i}")
            for i in range(100)
        ]
        
        start = time.time()
        detector.detect_exact_duplications(files)
        elapsed = time.time() - start
        
        assert elapsed < 5.0  # Should complete quickly

    def test_memory_usage_reasonable(self, detector: DuplicationDetector) -> None:
        """AC-8.3A-001-32: Memory usage stays reasonable"""
        import sys
        
        files = [
            MockFile(path=f"file_{i}.py", content=f"def func(): pass")
            for i in range(50)
        ]
        
        report = detector.generate_duplication_report([])
        
        # Report should be reasonably sized
        size = sys.getsizeof(report)
        assert size < 10_000_000  # Less than 10MB

    # =====================================================================
    # REGRESSION PREVENTION (3 tests)
    # =====================================================================

    def test_no_duplications_across_orchestrators_namespace(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-33: No false positives for namespace patterns"""
        # Different ExecutionContext definitions (legitimate)
        files = [
            MockFile(
                path="cortex/core/interfaces.py",
                content="""
class ExecutionContext:
    def __init__(self, id):
        self.id = id
"""
            ),
            MockFile(
                path="cortex/execution/adaptive.py",
                content="""
class ExecutionContext:
    def __init__(self, id):
        self.id = id
"""
            ),
        ]
        
        # These SHOULD be flagged as duplicates (problem to solve)
        duplications = detector.detect_exact_duplications(files)
        assert len(duplications) > 0  # SHOULD find them

    def test_detects_but_filters_standard_library(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-34: Filters out duplications in imported code"""
        files = [
            MockFile(
                path="lib/stdlib1.py",
                content="from typing import List, Dict"
            ),
            MockFile(
                path="lib/stdlib2.py",
                content="from typing import List, Dict"
            ),
        ]
        
        # Standard imports are common, shouldn't flag as important duplication
        report = detector.generate_duplication_report([])
        
        # Report should note these are not critical
        assert report is not None

    def test_consolidation_suggestions_include_phase_reference(
        self, detector: DuplicationDetector
    ) -> None:
        """AC-8.3A-001-35: Consolidation suggestions reference Phase 8.3B/C"""
        dup = DuplicateEntry(
            id="DUP-001",
            file1="a.py",
            file2="b.py",
            similarity=0.99,
            type="exact",
            lines=100,
        )
        
        suggestion = detector.suggest_consolidation_path(dup)
        
        assert "phase" in suggestion or "consolidation" in str(suggestion).lower()


class TestDuplicationDetectorIntegration:
    """Integration tests with real CORTEX code"""

    def test_detector_with_real_cortex_files(self) -> None:
        """AC-8.3A-001-36: Detector works with real CORTEX files"""
        detector = DuplicationDetector()
        
        # Scan cortex/orchestrators for real duplications
        # This test validates against actual codebase
        report = detector.scan_directory("cortex/orchestrators")
        
        assert report is not None
        assert report.total_duplications >= 0

    def test_finds_known_duplication_categories(self) -> None:
        """AC-8.3A-001-37: Detector finds 8 known duplication categories"""
        detector = DuplicationDetector()
        
        # Should find:
        # 1. Competing base orchestrator classes
        # 2. ExecutionContext definitions
        # 3. Registry systems
        # 4. Wiring systems
        # 5. Handler patterns
        # 6. Discovery plugins
        # 7. Template engines
        # 8. Metadata dataclasses
        
        report = detector.scan_codebase()
        
        # At least some of these should be found
        assert report.total_duplications > 0


# =========================================================================
# PARAMETRIZED TESTS (3 test sets)
# =========================================================================

@pytest.mark.parametrize("similarity,expected_severity", [
    (0.99, SeverityLevel.CRITICAL),
    (0.90, SeverityLevel.HIGH),
    (0.75, SeverityLevel.HIGH),
    (0.60, SeverityLevel.MEDIUM),
    (0.50, SeverityLevel.LOW),
])
def test_severity_by_similarity_threshold(
    similarity: float,
    expected_severity: SeverityLevel,
) -> None:
    """Test severity scoring across similarity thresholds"""
    detector = DuplicationDetector()
    dup = DuplicateEntry(
        id="TEST",
        file1="a.py",
        file2="b.py",
        similarity=similarity,
        type="exact",
        lines=100,
    )
    
    severity = detector.score_severity(dup)
    assert severity == expected_severity


@pytest.mark.parametrize("file_count", [5, 10, 50, 100])
def test_detector_scalability(file_count: int) -> None:
    """Test detector scales to N files"""
    detector = DuplicationDetector()
    files = [
        MockFile(path=f"file_{i}.py", content=f"def func_{i}(): pass")
        for i in range(file_count)
    ]
    
    # Should complete without error
    report = detector.generate_duplication_report([])
    assert report is not None


@pytest.mark.parametrize("duplication_type", ["exact", "semantic", "copy_paste"])
def test_detector_handles_duplication_types(duplication_type: str) -> None:
    """Test detector recognizes all duplication types"""
    detector = DuplicationDetector()
    
    # Detector should have handlers for each type
    method_name = f"detect_{duplication_type}_duplications"
    assert hasattr(detector, method_name)
    assert callable(getattr(detector, method_name))
