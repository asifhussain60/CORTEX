"""
Test Intelligence Foundation: Layer 3 - Quality Validator

Scores and validates generated tests for quality, brittleness, and maintainability.

Authority: WAVE-1 Stage 3, cortex-architect.prompt.md v15.3
Phase: THEME-A Intelligence Foundation
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import re


@dataclass
class QualityScore:
    """Represents quality scoring for a test."""
    
    test_name: str
    coverage_score: float  # 0.0 - 1.0
    realism_score: float  # 0.0 - 1.0
    maintainability_score: float  # 0.0 - 1.0
    brittleness_score: float  # 0.0 - 1.0 (lower is better)
    overall_score: float  # 0.0 - 1.0
    issues: List[str]
    passed_threshold: bool  # True if overall_score >= 0.70


class QualityValidator:
    """
    Validate generated tests for quality and maintainability.
    
    Features:
    - Coverage scoring (does it test the right things?)
    - Realism scoring (are assertions meaningful?)
    - Maintainability scoring (is it easy to understand and update?)
    - Brittleness detection (20 anti-patterns)
    - 70% quality gate (tests below threshold are rejected)
    """
    
    QUALITY_THRESHOLD = 0.70
    
    # 20 brittleness anti-patterns
    BRITTLENESS_PATTERNS = [
        r"time\.sleep",  # Sleep calls make tests slow and brittle
        r"assert.*==\s*True",  # Should use "assert condition"
        r"assert.*==\s*False",  # Should use "assert not condition"
        r"except\s*:",  # Bare except catches too much
        r"\.internal",  # Testing internal implementation
        r"_private_method",  # Testing private methods
        r"import\s+\*",  # Wildcard imports
        r"global\s+",  # Global state mutation
        r"os\.system",  # Shell commands in tests
        r"subprocess\.call",  # Subprocess in tests
        r"random\.",  # Non-deterministic behavior
        r"datetime\.now\(\)",  # Non-deterministic time
        r"\.sleep\(",  # Any sleep
        r"assert\s+\w+\s+==\s+\w+\s+==",  # Chained comparisons
        r"assert.*len\(.*\)\s*>\s*0",  # Should check actual contents
        r"mock\.patch\(.*autospec=False",  # Should use autospec
        r"monkeypatch\.\w+\(.*None\)",  # Setting to None without reason
        r"@pytest\.mark\.skip",  # Skipping tests without reason
        r"\.xfail\(",  # Expected failures without reason
        r"TODO|FIXME|XXX",  # Unfinished tests
    ]
    
    def __init__(self) -> None:
        """Initialize quality validator."""
        self._initialized = True
    
    def validate_test_file(self, test_file: Path) -> List[QualityScore]:
        """
        Validate all tests in a file.
        
        Args:
            test_file: Path to test file
        
        Returns:
            List of QualityScore objects (one per test)
        """
        # Read test file
        with open(test_file) as f:
            content = f.read()
        
        # Extract individual tests
        tests = self._extract_tests(content)
        
        # Score each test
        scores = []
        for test_name, test_code in tests.items():
            score = self._score_test(test_name, test_code)
            scores.append(score)
        
        return scores
    
    def validate_test_suite(self, tests_dir: Path) -> Dict[str, List[QualityScore]]:
        """
        Validate all test files in a directory.
        
        Args:
            tests_dir: Path to tests directory
        
        Returns:
            Dict mapping file paths to lists of QualityScore objects
        """
        results = {}
        
        for test_file in tests_dir.glob("test_*.py"):
            scores = self.validate_test_file(test_file)
            results[str(test_file)] = scores
        
        return results
    
    def generate_quality_report(self, scores: List[QualityScore]) -> Dict:
        """
        Generate quality report from scores.
        
        Args:
            scores: List of QualityScore objects
        
        Returns:
            Dict with summary statistics
        """
        total_tests = len(scores)
        passed_tests = sum(1 for s in scores if s.passed_threshold)
        failed_tests = total_tests - passed_tests
        
        avg_coverage = sum(s.coverage_score for s in scores) / total_tests if total_tests > 0 else 0.0
        avg_realism = sum(s.realism_score for s in scores) / total_tests if total_tests > 0 else 0.0
        avg_maintainability = sum(s.maintainability_score for s in scores) / total_tests if total_tests > 0 else 0.0
        avg_brittleness = sum(s.brittleness_score for s in scores) / total_tests if total_tests > 0 else 0.0
        avg_overall = sum(s.overall_score for s in scores) / total_tests if total_tests > 0 else 0.0
        
        return {
            "total_tests": total_tests,
            "passed_threshold": passed_tests,
            "failed_threshold": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "average_scores": {
                "coverage": avg_coverage,
                "realism": avg_realism,
                "maintainability": avg_maintainability,
                "brittleness": avg_brittleness,
                "overall": avg_overall,
            },
            "issues": [issue for score in scores for issue in score.issues],
        }
    
    # Private methods
    
    def _extract_tests(self, content: str) -> Dict[str, str]:
        """Extract individual test functions from file content."""
        tests = {}
        
        # Match test functions
        pattern = r"def (test_\w+)\([^)]*\):.*?(?=\ndef |$)"
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            test_name = match.group(1)
            test_code = match.group(0)
            tests[test_name] = test_code
        
        return tests
    
    def _score_test(self, test_name: str, test_code: str) -> QualityScore:
        """Score a single test."""
        # Coverage scoring
        coverage_score = self._score_coverage(test_code)
        
        # Realism scoring
        realism_score = self._score_realism(test_code)
        
        # Maintainability scoring
        maintainability_score = self._score_maintainability(test_code)
        
        # Brittleness scoring
        brittleness_score, brittleness_issues = self._score_brittleness(test_code)
        
        # Overall score (weighted average)
        overall_score = (
            coverage_score * 0.30 +
            realism_score * 0.25 +
            maintainability_score * 0.25 +
            (1.0 - brittleness_score) * 0.20  # Invert brittleness (lower is better)
        )
        
        # Check threshold
        passed_threshold = overall_score >= self.QUALITY_THRESHOLD
        
        return QualityScore(
            test_name=test_name,
            coverage_score=coverage_score,
            realism_score=realism_score,
            maintainability_score=maintainability_score,
            brittleness_score=brittleness_score,
            overall_score=overall_score,
            issues=brittleness_issues,
            passed_threshold=passed_threshold
        )
    
    def _score_coverage(self, test_code: str) -> float:
        """Score test coverage (does it test the right things?)."""
        score = 0.5  # Base score
        
        # Check for arrange/act/assert pattern
        if "# Arrange" in test_code and "# Act" in test_code and "# Assert" in test_code:
            score += 0.2
        
        # Check for meaningful assertions
        assert_count = test_code.count("assert ")
        if assert_count >= 2:
            score += 0.2
        elif assert_count >= 1:
            score += 0.1
        
        # Check for docstring
        if '"""' in test_code or "'''" in test_code:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_realism(self, test_code: str) -> float:
        """Score realism (are assertions meaningful?)."""
        score = 0.5  # Base score
        
        # Check for specific assertions (not just "assert True")
        if "assert" in test_code:
            if "is not None" in test_code or "!= None" in test_code:
                score += 0.2
            if "success" in test_code.lower():
                score += 0.2
            if "pytest.raises" in test_code:
                score += 0.1
        
        return min(score, 1.0)
    
    def _score_maintainability(self, test_code: str) -> float:
        """Score maintainability (is it easy to understand?)."""
        score = 0.5  # Base score
        
        # Check for comments
        if "#" in test_code:
            score += 0.1
        
        # Check for docstring
        if '"""' in test_code:
            score += 0.2
        
        # Check for fixtures (good practice)
        if "def test_" in test_code and "(" in test_code and ")" in test_code:
            params = re.search(r"def test_\w+\(([^)]+)\)", test_code)
            if params and params.group(1).strip():
                score += 0.2
        
        return min(score, 1.0)
    
    def _score_brittleness(self, test_code: str) -> tuple[float, List[str]]:
        """Score brittleness (does it have anti-patterns?)."""
        issues = []
        matches = 0
        
        for pattern in self.BRITTLENESS_PATTERNS:
            if re.search(pattern, test_code):
                matches += 1
                issues.append(f"Brittleness pattern detected: {pattern}")
        
        # Brittleness score: 0.0 = no issues, 1.0 = many issues
        brittleness_score = min(matches / 5.0, 1.0)  # Cap at 5 patterns
        
        return brittleness_score, issues
