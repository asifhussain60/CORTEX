"""
Test quality analyzer - detects FLUFF tests, coverage gaps, weak assertions.

Module: cortex.orchestrators.response.test_quality_analyzer
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

# ============================================================================
# ENUMERATIONS
# ============================================================================


class TestType(str, Enum):
    """Type of test quality issue."""

    FLUFF = "fluff"
    """Zero-value test (no assertions)"""

    WEAK_ASSERTION = "weak_assertion"
    """Trivial assertions (assert True/False)"""

    COVERAGE_GAP = "coverage_gap"
    """Missing test cases (edge cases, error paths)"""

    PERFORMANCE = "performance"
    """Test is slow or inefficient"""


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class TestQualityFinding:
    """A test quality finding."""

    test_name: str
    issue_type: TestType
    severity: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class TestContext:
    """Context for test quality analysis."""

    test_code: str
    test_name: str
    assertions_count: int = 0
    lines_of_code: int = 0
    test_categories: List[str] = field(default_factory=list)


class AssertionStrength(str, Enum):
    """Assertion strength level."""

    TRIVIAL = "trivial"
    WEAK = "weak"
    STRONG = "strong"


# ============================================================================
# FLUFF DETECTOR
# ============================================================================


class FLUFFDetector:
    """Detects FLUFF (zero-value) tests."""

    def detect(self, context: TestContext) -> List[TestQualityFinding]:
        """
        Detect FLUFF tests.

        Args:
            context: Test context

        Returns:
            List of findings
        """
        findings = []

        # Check for no assertions
        if context.assertions_count == 0:
            findings.append(TestQualityFinding(
                test_name=context.test_name,
                issue_type=TestType.FLUFF,
                severity="critical",
                message="Test has no assertions - test will always pass",
                suggestion="Add at least one meaningful assertion"
            ))

        # Check for trivial assertions
        if "assert True" in context.test_code:
            findings.append(TestQualityFinding(
                test_name=context.test_name,
                issue_type=TestType.FLUFF,
                severity="critical",
                message="Test contains 'assert True' - always passes",
                suggestion="Replace with actual assertion of code behavior"
            ))

        if "assert False" in context.test_code:
            findings.append(TestQualityFinding(
                test_name=context.test_name,
                issue_type=TestType.FLUFF,
                severity="critical",
                message="Test contains 'assert False' - always fails",
                suggestion="Fix test or remove if not needed"
            ))

        return findings


# ============================================================================
# ASSERTION STRENGTH ANALYZER
# ============================================================================


class AssertionStrengthAnalyzer:
    """Analyzes assertion strength."""

    WEAK_PATTERNS = [
        r"assert\s+True\s*(?:\n|$)",
        r"assert\s+False\s*(?:\n|$)",
        r"assert\s+\d+\s*(?:\n|$)",  # assert 1, assert 0
    ]

    @staticmethod
    def analyze_strength(code: str) -> AssertionStrength:
        """Analyze assertion strength."""
        for pattern in AssertionStrengthAnalyzer.WEAK_PATTERNS:
            if re.search(pattern, code):
                return AssertionStrength.WEAK

        # Check for comparison assertions
        if re.search(r"assert\s+\w+\s*(==|!=|<|>|in|is)", code):
            return AssertionStrength.STRONG

        return AssertionStrength.TRIVIAL


# ============================================================================
# COVERAGE GAP ANALYZER
# ============================================================================


class CoverageGapAnalyzer:
    """Detects test coverage gaps."""

    def analyze(self, context: TestContext) -> List[TestQualityFinding]:
        """
        Analyze for coverage gaps.

        Args:
            context: Test context

        Returns:
            List of findings
        """
        findings = []

        # Check if only happy path tested
        if "happy_path" in context.test_categories and len(context.test_categories) == 1:
            findings.append(TestQualityFinding(
                test_name=context.test_name,
                issue_type=TestType.COVERAGE_GAP,
                severity="warning",
                message="Only happy path tested - missing edge cases",
                suggestion="Add tests for: empty inputs, None values, negative numbers, boundary conditions"
            ))

        # Check for error handling tests
        if "error" not in context.test_categories and "exception" not in context.test_categories:
            if context.lines_of_code > 2:
                findings.append(TestQualityFinding(
                    test_name=context.test_name,
                    issue_type=TestType.COVERAGE_GAP,
                    severity="info",
                    message="No error/exception tests found",
                    suggestion="Add tests for error conditions and exception handling"
                ))

        return findings


# ============================================================================
# TEST QUALITY ANALYZER (ORCHESTRATOR)
# ============================================================================


class TestQualityAnalyzer:
    """Orchestrator for test quality analysis."""

    def __init__(self):
        """Initialize analyzer."""
        self.fluff_detector = FLUFFDetector()
        self.coverage_analyzer = CoverageGapAnalyzer()

    def analyze(self, context: TestContext) -> List[TestQualityFinding]:
        """
        Analyze test quality.

        Args:
            context: Test context

        Returns:
            List of findings
        """
        findings = []

        # Run FLUFF detection
        findings.extend(self.fluff_detector.detect(context))

        # Check assertion strength
        if context.assertions_count > 0:
            strength = AssertionStrengthAnalyzer.analyze_strength(context.test_code)
            if strength == AssertionStrength.WEAK:
                findings.append(TestQualityFinding(
                    test_name=context.test_name,
                    issue_type=TestType.WEAK_ASSERTION,
                    severity="warning",
                    message="Assertion is too weak to be meaningful",
                    suggestion="Use specific assertions: assert x == value, assert y in collection, etc."
                ))

        # Check for coverage gaps
        findings.extend(self.coverage_analyzer.analyze(context))

        return findings

    @staticmethod
    def _count_assertions(code: str) -> int:
        """Count assertion statements in code."""
        pattern = r"assert\s+"
        return len(re.findall(pattern, code))


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "TestType",
    "TestQualityFinding",
    "TestContext",
    "AssertionStrength",
    "FLUFFDetector",
    "CoverageGapAnalyzer",
    "TestQualityAnalyzer",
]
