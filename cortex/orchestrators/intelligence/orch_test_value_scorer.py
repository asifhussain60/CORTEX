"""
Test Value Scorer - Calculate priority scores for test candidates.

Authority: MASTER-5-WAVE-PLAN-2026-02-13.yaml WAVE-2 Stage S1
Purpose: Prioritize high-value tests using multi-factor scoring
Formula: (Severity × 0.4) + (Likelihood × 0.3) + (Coverage Gap × 0.3)
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class IssueSeverity(Enum):
    """Severity levels for potential bugs."""
    CRITICAL = 100  # Security vulnerabilities, data loss
    HIGH = 75       # System crashes, major functionality broken
    MEDIUM = 50     # Partial functionality broken, workarounds exist
    LOW = 25        # Minor issues, cosmetic problems
    TRIVIAL = 10    # Edge cases unlikely to occur


class ScenarioLikelihood(Enum):
    """Likelihood of scenario occurring in production."""
    VERY_HIGH = 100  # Common operations (CRUD, authentication)
    HIGH = 75        # Frequent operations (search, filtering)
    MEDIUM = 50      # Occasional operations (configuration, reports)
    LOW = 25         # Rare operations (admin tasks, exports)
    VERY_LOW = 10    # Edge cases (invalid input, race conditions)


@dataclass
class TestCandidate:
    """A potential test to be generated."""

    name: str
    description: str
    issue_type: str  # "blind_spot" | "edge_case" | "security_risk"
    target_function: str
    target_file: str

    # Scoring factors
    severity: IssueSeverity
    likelihood: ScenarioLikelihood
    coverage_gap: float  # 0-100 (percentage of uncovered code)

    # Metadata
    category: Optional[str] = None
    owasp_category: Optional[str] = None


@dataclass
class TestValueScore:
    """Calculated test value score with breakdown."""

    total: float  # 0-100
    severity_score: float  # 0-40
    likelihood_score: float  # 0-30
    coverage_gap_score: float  # 0-30

    candidate: TestCandidate

    @property
    def should_generate(self) -> bool:
        """Whether this test exceeds generation threshold."""
        return self.total >= 70.0  # Default threshold

    @property
    def priority(self) -> str:
        """Priority tier based on score."""
        if self.total >= 90:
            return "P0-CRITICAL"
        elif self.total >= 75:
            return "P1-HIGH"
        elif self.total >= 60:
            return "P2-MEDIUM"
        else:
            return "P3-LOW"


class TestValueScorer:
    """
    Calculate test value scores for test candidates.

    Uses multi-factor formula to prioritize high-value tests:
    - Severity: How bad if this bug reaches production? (0-100)
    - Likelihood: How likely is this scenario to occur? (0-100)
    - Coverage Gap: Is this code path currently untested? (0-100)

    Formula: (Severity × 0.4) + (Likelihood × 0.3) + (Gap × 0.3)

    Example:
        >>> scorer = TestValueScorer()
        >>> candidate = TestCandidate(
        ...     name="test_sql_injection",
        ...     description="Test SQL injection prevention",
        ...     issue_type="security_risk",
        ...     target_function="execute_query",
        ...     target_file="database.py",
        ...     severity=IssueSeverity.CRITICAL,
        ...     likelihood=ScenarioLikelihood.HIGH,
        ...     coverage_gap=100.0
        ... )
        >>> score = scorer.calculate_score(candidate)
        >>> score.total
        92.5
        >>> score.should_generate
        True
    """

    def __init__(
        self,
        severity_weight: float = 0.4,
        likelihood_weight: float = 0.3,
        coverage_gap_weight: float = 0.3,
    ) -> None:
        """
        Initialize scorer with custom weights.

        Args:
            severity_weight: Weight for severity factor (default: 0.4)
            likelihood_weight: Weight for likelihood factor (default: 0.3)
            coverage_gap_weight: Weight for coverage gap factor (default: 0.3)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        total_weight = severity_weight + likelihood_weight + coverage_gap_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {total_weight}. "
                f"Provided: severity={severity_weight}, "
                f"likelihood={likelihood_weight}, "
                f"coverage_gap={coverage_gap_weight}"
            )

        self.severity_weight = severity_weight
        self.likelihood_weight = likelihood_weight
        self.coverage_gap_weight = coverage_gap_weight

    def calculate_score(self, candidate: TestCandidate) -> TestValueScore:
        """
        Calculate test value score for a candidate.

        Args:
            candidate: Test candidate to score

        Returns:
            TestValueScore with total and breakdown

        Example:
            >>> candidate = TestCandidate(
            ...     name="test_empty_list",
            ...     description="Test empty list handling",
            ...     issue_type="edge_case",
            ...     target_function="process_items",
            ...     target_file="processor.py",
            ...     severity=IssueSeverity.MEDIUM,
            ...     likelihood=ScenarioLikelihood.MEDIUM,
            ...     coverage_gap=80.0
            ... )
            >>> score = scorer.calculate_score(candidate)
            >>> score.total
            59.0
        """
        # Calculate weighted components
        severity_score = candidate.severity.value * self.severity_weight
        likelihood_score = candidate.likelihood.value * self.likelihood_weight
        coverage_gap_score = candidate.coverage_gap * self.coverage_gap_weight

        # Total score (0-100)
        total = severity_score + likelihood_score + coverage_gap_score

        return TestValueScore(
            total=round(total, 2),
            severity_score=round(severity_score, 2),
            likelihood_score=round(likelihood_score, 2),
            coverage_gap_score=round(coverage_gap_score, 2),
            candidate=candidate,
        )

    def get_severity_score(self, issue_type: str) -> IssueSeverity:
        """
        Get default severity for issue type.

        Args:
            issue_type: Type of issue ("blind_spot", "edge_case", "security_risk")

        Returns:
            IssueSeverity enum value

        Example:
            >>> scorer.get_severity_score("security_risk")
            IssueSeverity.CRITICAL
        """
        severity_map: Dict[str, IssueSeverity] = {
            "security_risk": IssueSeverity.CRITICAL,
            "blind_spot": IssueSeverity.HIGH,
            "edge_case": IssueSeverity.MEDIUM,
            "error_recovery": IssueSeverity.MEDIUM,
            "concurrency": IssueSeverity.HIGH,
            "golden_path": IssueSeverity.LOW,
        }
        return severity_map.get(issue_type, IssueSeverity.MEDIUM)

    def get_likelihood_score(self, scenario: str) -> ScenarioLikelihood:
        """
        Get default likelihood for scenario type.

        Args:
            scenario: Scenario type (e.g., "empty_input", "null_value")

        Returns:
            ScenarioLikelihood enum value

        Example:
            >>> scorer.get_likelihood_score("sql_injection")
            ScenarioLikelihood.HIGH
        """
        likelihood_map: Dict[str, ScenarioLikelihood] = {
            # High likelihood scenarios
            "empty_input": ScenarioLikelihood.HIGH,
            "null_value": ScenarioLikelihood.HIGH,
            "sql_injection": ScenarioLikelihood.HIGH,
            "xss_attack": ScenarioLikelihood.HIGH,
            "auth_bypass": ScenarioLikelihood.MEDIUM,

            # Medium likelihood scenarios
            "overflow": ScenarioLikelihood.MEDIUM,
            "underflow": ScenarioLikelihood.MEDIUM,
            "race_condition": ScenarioLikelihood.LOW,

            # Low likelihood scenarios
            "unicode_edge_case": ScenarioLikelihood.LOW,
            "max_int": ScenarioLikelihood.LOW,
        }
        return likelihood_map.get(scenario, ScenarioLikelihood.MEDIUM)

    def get_coverage_gap_score(self, code_path: str, coverage_data: Optional[Dict] = None) -> float:
        """
        Calculate coverage gap score for code path.

        Args:
            code_path: Path to code being tested
            coverage_data: Optional coverage data from pytest-cov

        Returns:
            Coverage gap percentage (0-100)

        Example:
            >>> scorer.get_coverage_gap_score("error_handler_branch")
            100.0  # Uncovered path
        """
        if coverage_data is None:
            # Default: assume uncovered if no data
            return 100.0

        # Check if code path is covered
        is_covered = coverage_data.get(code_path, {}).get("covered", False)
        if not is_covered:
            return 100.0  # Completely uncovered

        # Check execution count
        execution_count = coverage_data.get(code_path, {}).get("count", 0)
        if execution_count == 0:
            return 100.0
        elif execution_count == 1:
            return 75.0  # Minimally covered
        elif execution_count < 5:
            return 50.0  # Partially covered
        else:
            return 25.0  # Well covered

    # ── Phase 83-e: URS recalibration ───────────────────────────────────────

    def recalibrate_from_signals(
        self,
        signal_history: List[Any],
    ) -> Dict[str, Any]:
        """Recalibrate scoring weights based on reinforcement signal history.

        Examines signal context for ``factor`` keys matching weight names.
        Patterns receiving STRONG_REWARD for a factor → increase that weight.
        Weights are re-normalised to sum to 1.0.

        Args:
            signal_history: List of ReinforcementSignal objects.

        Returns:
            Dict with ``adjusted`` (bool) and ``weights`` snapshot.
        """
        # Count positive signals per factor
        factor_boosts: Dict[str, float] = {
            "severity": 0.0,
            "likelihood": 0.0,
            "coverage_gap": 0.0,
        }
        _BOOST = 0.02  # per positive signal

        for sig in signal_history:
            factor = getattr(sig, "context", {}).get("factor", "")
            score = getattr(getattr(sig, "signal_type", None), "score", 0.0)
            if factor in factor_boosts and score > 0:
                factor_boosts[factor] += _BOOST * score

        total_boost = sum(factor_boosts.values())
        adjusted = total_boost > 0

        if adjusted:
            self.severity_weight += factor_boosts["severity"]
            self.likelihood_weight += factor_boosts["likelihood"]
            self.coverage_gap_weight += factor_boosts["coverage_gap"]
            # Re-normalise to 1.0
            total = self.severity_weight + self.likelihood_weight + self.coverage_gap_weight
            if total > 0:
                self.severity_weight /= total
                self.likelihood_weight /= total
                self.coverage_gap_weight /= total

        return {
            "adjusted": adjusted,
            "weights": {
                "severity": round(self.severity_weight, 4),
                "likelihood": round(self.likelihood_weight, 4),
                "coverage_gap": round(self.coverage_gap_weight, 4),
            },
        }

# AC_COMPLETE: AC-WAVE-2-S1-001 ✅ TestValueScorer implementation complete
