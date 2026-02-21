# AC_START: AC-PHASE51-S4-QUALITY-VALIDATOR-001
# Phase 51 S4: Test Quality Validator - Advanced Quality Scoring Layer
# Purpose: Analyzes generated tests for quality, brittleness, and completion
# Authority: TDDOrchestrator | Layer 3 of intelligent test generation
# Date: 2026-02-13

"""
Test Quality Validator Layer

Provides comprehensive quality assessment for generated tests:
- Coverage scoring (demand scenario completeness)
- Realism scoring (test authenticity)
- Maintainability scoring (code clarity, no magic strings)
- Brittleness detection (fragile patterns)
- Quality gating (70%+ required for acceptance)
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import logging

# Import dependencies from earlier layers
from cortex.testing.test_demand_generator import TestDemand, DemandCategory
from cortex.testing.test_composer import ComposedTest


logger = logging.getLogger(__name__)


class BrittnessIssueType(Enum):
    """Types of brittleness issues detected in tests"""
    MAGIC_STRING = "magic_string"
    HARDCODED_PATH = "hardcoded_path"
    STATE_ASSUMPTION = "state_assumption"
    TIMING_ASSUMPTION = "timing_assumption"
    MOCK_DEPENDENCY = "mock_dependency"
    FILE_SYSTEM_DEPENDENCY = "file_system_dependency"


@dataclass
class BrittnessIssue:
    """Represents a brittleness pattern detected in test code"""
    issue_type: BrittnessIssueType
    line_number: Optional[int]
    pattern: str
    severity: str  # "low", "medium", "high"
    description: str
    fix_suggestion: str


@dataclass
class QualityReport:
    """Complete quality assessment for a generated test"""
    test_id: str
    test_name: str
    overall_score: float  # 0-100
    coverage_score: float  # 0-100
    realism_score: float  # 0-100
    maintainability_score: float  # 0-100
    brittleness_score: float  # 0-100 (higher = less brittle)
    brittleness_issues: List[BrittnessIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    passes_quality_gate: bool = False  # True if overall_score >= 70
    audit_trail: str = ""

    def to_dict(self) -> Dict:
        """Serialize quality report to dictionary"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "overall_score": round(self.overall_score, 2),
            "coverage_score": round(self.coverage_score, 2),
            "realism_score": round(self.realism_score, 2),
            "maintainability_score": round(self.maintainability_score, 2),
            "brittleness_score": round(self.brittleness_score, 2),
            "passes_quality_gate": self.passes_quality_gate,
            "brittleness_issues": [
                {
                    "type": issue.issue_type.value,
                    "line": issue.line_number,
                    "pattern": issue.pattern,
                    "severity": issue.severity,
                    "description": issue.description,
                    "fix": issue.fix_suggestion,
                }
                for issue in self.brittleness_issues
            ],
            "recommendations": self.recommendations,
        }


class TestQualityAnalyzer(ABC):
    """
    Abstract base class for analyzing test quality.
    Subclasses implement domain-specific quality analysis.
    """

    @abstractmethod
    def analyze_test(
        self, composed_test: ComposedTest, demand: TestDemand
    ) -> QualityReport:
        """
        Analyze a generated test for quality metrics.

        Args:
            composed_test: Generated test code and metadata
            demand: Original test demand specification

        Returns:
            QualityReport with comprehensive quality assessment
        """
        pass

    @abstractmethod
    def detect_brittleness_patterns(self, test_code: str) -> List[BrittnessIssue]:
        """
        Identify brittleness patterns in test code.

        Args:
            test_code: Generated test code string

        Returns:
            List of brittleness issues found
        """
        pass


class QualityScorer:
    """Calculates quality scores for different test dimensions"""

    def __init__(self) -> None:
        """Initialize instance."""
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def score_coverage(self, test_code: str, demand: TestDemand) -> float:
        """
        Score coverage: does test validate all scenario aspects?

        Args:
            test_code: Generated test code
            demand: Original demand specification

        Returns:
            Coverage score 0-100
        """
        coverage_points = 0.0
        max_points = 100.0

        # Check for scenario coverage (30 points)
        if demand.scenario and len(demand.scenario) > 20:
            if "Given" in test_code or "Setup" in test_code.upper():
                coverage_points += 10
            if "When" in test_code or "action" in test_code.lower():
                coverage_points += 10
            if "Then" in test_code or "assert" in test_code.lower():
                coverage_points += 10

        # Check for expected behavior validation (40 points)
        assertion_count = test_code.count("assert ")
        if assertion_count >= 2:
            coverage_points += 20
        elif assertion_count >= 1:
            coverage_points += 10

        # Check for edge cases (30 points)
        if "try:" in test_code or "except" in test_code:
            coverage_points += 15
        if "if " in test_code and "else:" in test_code:
            coverage_points += 15

        return min(coverage_points, max_points)

    def score_realism(self, test_code: str) -> float:
        """
        Score realism: does test represent realistic scenarios?

        Args:
            test_code: Generated test code

        Returns:
            Realism score 0-100
        """
        realism_points = 0.0
        max_points = 100.0

        # Scenario context (30 points)
        if "context" in test_code.lower() or "state" in test_code.lower():
            realism_points += 15
        if "setup" in test_code.lower() or "initialize" in test_code.lower():
            realism_points += 15

        # Realistic assertions (40 points)
        assertions = re.findall(r"assert\s+\w+\.\w+", test_code)
        if len(assertions) >= 2:
            realism_points += 40
        elif len(assertions) >= 1:
            realism_points += 20

        # Error handling (30 points)
        if "Exception" in test_code or "Error" in test_code:
            realism_points += 15
        if "assertEqual" in test_code or "assertIn" in test_code:
            realism_points += 15

        return min(realism_points, max_points)

    def score_maintainability(self, test_code: str) -> float:
        """
        Score maintainability: is test clear and changeable?

        Args:
            test_code: Generated test code

        Returns:
            Maintainability score 0-100
        """
        maintainability_points = 0.0
        max_points = 100.0

        # Docstring/comments (25 points)
        if '"""' in test_code or "'''" in test_code:
            maintainability_points += 15
        if "#" in test_code:
            maintainability_points += 10

        # Variable naming clarity (25 points)
        if "test_" in test_code and len(test_code.split("def test_")[1].split("(")[0]) > 5:
            maintainability_points += 15
        if "expected" in test_code or "actual" in test_code:
            maintainability_points += 10

        # Code organization (25 points)
        if test_code.count("\n") < 50:  # Reasonable length
            maintainability_points += 15
        if "self." in test_code:
            maintainability_points += 10

        # Fixture usage (25 points)
        if "fixture" in test_code.lower() or "@" in test_code:
            maintainability_points += 25

        return min(maintainability_points, max_points)

    def score_brittleness(self, issues: List[BrittnessIssue]) -> float:
        """
        Score brittleness resistance (inverse of brittleness).

        Args:
            issues: Brittleness issues detected

        Returns:
            Brittleness score 0-100 (higher = less brittle)
        """
        if not issues:
            return 100.0  # No issues = not brittle

        severity_weights = {"low": 5, "medium": 15, "high": 30}
        penalty = sum(severity_weights.get(issue.severity, 10) for issue in issues)

        # Score inversely: no issues = 100, issues reduce score
        brittleness_score = max(0.0, 100.0 - penalty)
        return brittleness_score

    def calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate overall quality score from component scores.

        Weights:
        - Coverage: 30% (test validates all scenarios)
        - Realism: 25% (test represents real usage)
        - Maintainability: 25% (test is clear and changeable)
        - Brittleness: 20% (test resists fragile patterns)

        Args:
            scores: Dict with keys: coverage, realism, maintainability, brittleness

        Returns:
            Overall quality score 0-100
        """
        overall = (
            scores.get("coverage", 0) * 0.30
            + scores.get("realism", 0) * 0.25
            + scores.get("maintainability", 0) * 0.25
            + scores.get("brittleness", 0) * 0.20
        )
        return overall


class BrittnessDetector:
    """Identifies patterns causing test fragility"""

    def __init__(self) -> None:
        """Initialize instance."""
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def detect_magic_strings(self, test_code: str) -> List[BrittnessIssue]:
        """Detect hardcoded string literals that might break on change"""
        issues = []
        # Look for quoted strings outside of assertions
        magic_strings = re.findall(r'["\']([a-zA-Z0-9_\-/.\s]+)["\']\s*[,;]', test_code)

        for magic_string in magic_strings:
            if len(magic_string) > 3 and not any(
                magic_string in test_code[max(0, i - 20) : i + 20]
                for i in [test_code.find("assert"), test_code.find("assertEqual")]
                if i >= 0
            ):
                issues.append(
                    BrittnessIssue(
                        issue_type=BrittnessIssueType.MAGIC_STRING,
                        line_number=None,
                        pattern=magic_string,
                        severity="medium",
                        description=f"Hardcoded string '{magic_string}' outside assertions may break if value changes",
                        fix_suggestion=f"Move to constant: {magic_string.upper()} = '{magic_string}'",
                    )
                )
        return issues[:3]  # Limit to top 3

    def detect_hardcoded_paths(self, test_code: str) -> List[BrittnessIssue]:
        """Detect hardcoded file paths that are environment-dependent"""
        issues = []
        # Look for path-like patterns
        paths = re.findall(r'["\']([/\\][^\'"]*)["\']', test_code)

        for path in paths:
            if "/" in path or "\\" in path:
                issues.append(
                    BrittnessIssue(
                        issue_type=BrittnessIssueType.HARDCODED_PATH,
                        line_number=None,
                        pattern=path,
                        severity="high",
                        description=f"Hardcoded path '{path}' will fail on different environments",
                        fix_suggestion=f"Use os.path.join() or pathlib.Path instead",
                    )
                )
        return issues[:2]  # Limit to top 2

    def detect_state_assumptions(self, test_code: str) -> List[BrittnessIssue]:
        """Detect assumptions about global or shared state"""
        issues = []

        # Look for patterns suggesting state assumptions
        if "global " in test_code:
            issues.append(
                BrittnessIssue(
                    issue_type=BrittnessIssueType.STATE_ASSUMPTION,
                    line_number=None,
                    pattern="global",
                    severity="high",
                    description="Test modifies global state (fragile when tests run in different order)",
                    fix_suggestion="Use fixtures or dependency injection instead",
                )
            )

        if re.search(r"[a-zA-Z_]\w*\s*=\s*\[\]", test_code):
            # Likely mutable default argument
            issues.append(
                BrittnessIssue(
                    issue_type=BrittnessIssueType.STATE_ASSUMPTION,
                    line_number=None,
                    pattern="mutable_default",
                    severity="medium",
                    description="Mutable default argument may retain state between tests",
                    fix_suggestion="Move list/dict initialization inside function",
                )
            )

        return issues[:2]

    def detect_timing_assumptions(self, test_code: str) -> List[BrittnessIssue]:
        """Detect assumptions about timing/delays"""
        issues = []

        if "sleep(" in test_code or "time.sleep" in test_code:
            issues.append(
                BrittnessIssue(
                    issue_type=BrittnessIssueType.TIMING_ASSUMPTION,
                    line_number=None,
                    pattern="sleep()",
                    severity="high",
                    description="Hard-coded sleep() causes flaky tests (may timeout in CI)",
                    fix_suggestion="Use wait_for() with timeout and poll instead",
                )
            )

        return issues

    def detect_all(self, test_code: str) -> List[BrittnessIssue]:
        """Run all brittleness detectors"""
        all_issues = []
        all_issues.extend(self.detect_magic_strings(test_code))
        all_issues.extend(self.detect_hardcoded_paths(test_code))
        all_issues.extend(self.detect_state_assumptions(test_code))
        all_issues.extend(self.detect_timing_assumptions(test_code))
        return all_issues


class InteractionOrchestratorQualityAnalyzer(TestQualityAnalyzer):
    """Quality analyzer specialized for InteractionOrchestrator tests"""

    def __init__(self) -> None:
        """Initialize instance."""
        self.scorer = QualityScorer()
        self.brittleness_detector = BrittnessDetector()
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def analyze_test(
        self, composed_test: ComposedTest, demand: TestDemand
    ) -> QualityReport:
        """
        Comprehensive quality analysis for InteractionOrchestrator test.

        AC_START: AC-PHASE51-S4-QUALITY-VALIDATOR-001
        """
        # Detect brittleness issues
        brittleness_issues = self.detect_brittleness_patterns(composed_test.test_code)

        # Calculate component scores
        coverage_score = self.scorer.score_coverage(composed_test.test_code, demand)
        realism_score = self.scorer.score_realism(composed_test.test_code)
        maintainability_score = self.scorer.score_maintainability(composed_test.test_code)
        brittleness_score = self.scorer.score_brittleness(brittleness_issues)

        # Calculate overall score (weighted average)
        overall_score = self.scorer.calculate_overall_score(
            {
                "coverage": coverage_score,
                "realism": realism_score,
                "maintainability": maintainability_score,
                "brittleness": brittleness_score,
            }
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            coverage_score, realism_score, maintainability_score, brittleness_issues
        )

        # Quality gate: 70% or higher
        passes_quality_gate = overall_score >= 70.0

        report = QualityReport(
            test_id=composed_test.demand_id,
            test_name=composed_test.name,
            overall_score=overall_score,
            coverage_score=coverage_score,
            realism_score=realism_score,
            maintainability_score=maintainability_score,
            brittleness_score=brittleness_score,
            brittleness_issues=brittleness_issues,
            recommendations=recommendations,
            passes_quality_gate=passes_quality_gate,
            audit_trail="AC-PHASE51-S4-QUALITY-VALIDATOR-001",
        )

        self.logger.info(f"Quality analysis complete for {composed_test.name}: {overall_score:.1f}%")
        # AC_COMPLETE: AC-PHASE51-S4-QUALITY-VALIDATOR-001 ✅

        return report

    def detect_brittleness_patterns(self, test_code: str) -> List[BrittnessIssue]:
        """Detect all brittleness patterns in test code"""
        return self.brittleness_detector.detect_all(test_code)

    def _generate_recommendations(
        self,
        coverage_score: float,
        realism_score: float,
        maintainability_score: float,
        brittleness_issues: List[BrittnessIssue],
    ) -> List[str]:
        """Generate actionable improvement recommendations"""
        recommendations = []

        if coverage_score < 70:
            recommendations.append(
                f"Coverage low ({coverage_score:.0f}%): Add more assertions for edge cases and error conditions"
            )

        if realism_score < 70:
            recommendations.append(
                f"Realism low ({realism_score:.0f}%): Test scenarios should reflect actual orchestrator usage patterns"
            )

        if maintainability_score < 70:
            recommendations.append(
                f"Maintainability low ({maintainability_score:.0f}%): Add docstrings, use descriptive variable names, reduce duplication"
            )

        if len(brittleness_issues) > 0:
            high_severity = [i for i in brittleness_issues if i.severity == "high"]
            if high_severity:
                recommendations.append(
                    f"Fix {len(high_severity)} high-severity brittleness issues: {', '.join(i.issue_type.value for i in high_severity)}"
                )

        if not recommendations:
            recommendations.append("Test quality excellent. Consider for production use as reference implementation.")

        return recommendations[:3]  # Limit to top 3 recommendations


# AC_COMPLETE: AC-PHASE51-S4-QUALITY-VALIDATOR-001 ✅
