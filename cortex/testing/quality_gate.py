"""
CORTEX Test Quality Gate — Canonical Scoring Service (Phase 07b)

Implements the 7-step algorithm from test-quality.txt.
Replaces three existing disconnected scorers (CORE-035):
  - cortex.testing.test_value_scorer (Phase 71)
  - cortex.testing.test_quality_validator (Phase 51)
  - cortex.orchestrators.intelligence.orch_test_value_scorer (Wave-2)

Scoring formula:
  Impact(0-3) + Likelihood(0-2) + Detection(0-2) + Efficiency(0-2)
  − MaintenancePenalty(0-2) = Score 0–9

Gate threshold:
  KEEP   ≥ 7  — clear production value
  REVIEW  4–6 — human review required
  DELETE  < 4  — no production value, safe to archive

Golden test detection:
  Automatically identifies cross-orchestrator tests with sqlite audit assertions.
  Golden tests are always KEEP regardless of score.

Authority: test-quality.txt | CORE-035 | CORE-011 | CORE-012
AC-ID: AC-PHASE-07B-TEST-QUALITY-GATE-001
Author: Asif Hussain
Date: 2026-02-20
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Registry YAML path — SSOT for all thresholds and patterns
_REGISTRY_YAML = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "core"
    / "test-quality-gate.yaml"
)

# Category constants
KEEP = "KEEP"
REVIEW = "REVIEW"
DELETE = "DELETE"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ScoreResult:
    """Complete quality score for a single test file.

    Attributes:
        score: Overall quality score (0–9).
        category: KEEP | REVIEW | DELETE.
        is_golden: True if auto-detected as a golden (cross-orchestrator) test.
        breakdown: Per-dimension scores for transparency.
        filename: Source filename (for reporting).
        n_tests: Number of test functions found.
    """

    score: float
    category: str
    is_golden: bool
    breakdown: Dict[str, float]
    filename: str = ""
    n_tests: int = 0


# ---------------------------------------------------------------------------
# TestQualityGate
# ---------------------------------------------------------------------------

class TestQualityGate:
    """Canonical CORTEX test quality scorer.

    Stateless by design — safe for parallel workers.
    Loads all thresholds and patterns from the registry YAML (SSOT).

    Example::

        gate = TestQualityGate()
        result = gate.score_content(content, filename="test_governance.py")
        if gate.gate_passes(result.score):
            print("KEEP")
        else:
            print(f"Score too low: {result.score} ({result.category})")
    """

    def __init__(self, registry_path: Optional[Path] = None) -> None:
        """Initialise gate, loading rules from registry YAML.

        Args:
            registry_path: Override path to test-quality-gate.yaml.
                           Defaults to cortex-registry/core/test-quality-gate.yaml.
        """
        self._config = self._load_config(registry_path or _REGISTRY_YAML)
        self._thresholds = self._config.get("thresholds", {"keep": 7, "review": 4})
        self._dims = self._config.get("dimensions", {})
        self._trivial_patterns = [
            re.compile(p) for p in self._config.get("trivial_assert_patterns", [])
        ]
        self._skip_patterns = [
            re.compile(p) for p in self._config.get("skip_patterns", [])
        ]
        self._mock_patterns = [
            re.compile(p) for p in self._config.get("mock_patterns", [])
        ]
        self._golden_cfg = self._config.get("golden_detection", {})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score_content(self, content: str, filename: str = "") -> ScoreResult:
        """Score test file content using the 7-step algorithm.

        Args:
            content: Raw Python source of the test file.
            filename: Filename (used for golden path detection).

        Returns:
            ScoreResult with score, category, is_golden, breakdown.
        """
        if not content or not content.strip():
            return ScoreResult(
                score=0,
                category=DELETE,
                is_golden=False,
                breakdown={"impact": 0, "likelihood": 0, "detection": 0,
                            "efficiency": 0, "maintenance_penalty": 0},
                filename=filename,
                n_tests=0,
            )

        # Step 1 — count test functions and basic metrics
        test_funcs = re.findall(r"def (test_\w+)", content)
        n_tests = len(test_funcs)
        n_lines = len(content.splitlines())
        lines_per_test = n_lines / n_tests if n_tests > 0 else 0

        total_asserts = len(re.findall(r"\bassert\b", content))
        asserts_per_test = total_asserts / n_tests if n_tests > 0 else 0

        # Step 2 — golden detection (before scoring — golden always KEEP)
        is_golden = self._detect_golden(content, filename)

        # Step 3 — dimension scores
        impact = self._score_impact(content)
        likelihood = self._score_likelihood(content)
        detection = self._score_detection(content)
        efficiency = self._score_efficiency(lines_per_test, asserts_per_test)
        maintenance_penalty = self._score_maintenance_penalty(
            content, n_tests, total_asserts
        )

        raw_score = impact + likelihood + detection + efficiency + maintenance_penalty
        score = max(0.0, min(9.0, raw_score))

        category = KEEP if is_golden else self.classify(score)

        return ScoreResult(
            score=round(score, 2),
            category=category,
            is_golden=is_golden,
            breakdown={
                "impact": impact,
                "likelihood": likelihood,
                "detection": detection,
                "efficiency": efficiency,
                "maintenance_penalty": maintenance_penalty,
            },
            filename=filename,
            n_tests=n_tests,
        )

    def score_file(self, path: Path) -> ScoreResult:
        """Score a test file on disk.

        Args:
            path: Absolute or relative path to the test file.

        Returns:
            ScoreResult with score, category, is_golden, breakdown.
        """
        path = Path(path)
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ScoreResult(
                score=0, category=DELETE, is_golden=False,
                breakdown={}, filename=str(path), n_tests=0,
            )
        return self.score_content(content, filename=str(path))

    def classify(self, score: float) -> str:
        """Map a numeric score to KEEP / REVIEW / DELETE.

        Args:
            score: Numeric score 0–9.

        Returns:
            "KEEP", "REVIEW", or "DELETE".
        """
        keep_threshold = self._thresholds.get("keep", 7)
        review_threshold = self._thresholds.get("review", 4)
        if score >= keep_threshold:
            return KEEP
        if score >= review_threshold:
            return REVIEW
        return DELETE

    def gate_passes(self, score: float, min_score: float = 7.0) -> bool:
        """Return True if score meets the minimum threshold.

        Args:
            score: Numeric score 0–9.
            min_score: Override threshold (default: 7).

        Returns:
            True if score >= min_score.
        """
        return score >= min_score

    # ------------------------------------------------------------------
    # Private — dimension scorers
    # ------------------------------------------------------------------

    def _score_impact(self, content: str) -> float:
        """Impact dimension (0–3): security + reliability + business invariant."""
        impact_cfg = self._dims.get("impact", {})
        signals = impact_cfg.get("signals", {})
        score = 0.0
        for sig_name, sig_cfg in signals.items():
            patterns = sig_cfg.get("patterns", [])
            points = sig_cfg.get("points", 1)
            combined = "|".join(patterns)
            if re.search(combined, content, re.IGNORECASE):
                score += points
        return min(score, impact_cfg.get("max", 3))

    def _score_likelihood(self, content: str) -> float:
        """Likelihood dimension (0–2): orchestration + integration seam signals."""
        cfg = self._dims.get("likelihood", {})
        signals = cfg.get("signals", {})
        score = 0.0
        for sig_name, sig_cfg in signals.items():
            patterns = sig_cfg.get("patterns", [])
            min_occ = sig_cfg.get("min_occurrences", 1)
            points = sig_cfg.get("points", 1)
            combined = "|".join(patterns)
            count = len(re.findall(combined, content, re.IGNORECASE))
            if count >= min_occ:
                score += points
        return min(score, cfg.get("max", 2))

    def _score_detection(self, content: str) -> float:
        """Detection gap dimension (0–2): data correctness + operational signals."""
        cfg = self._dims.get("detection", {})
        signals = cfg.get("signals", {})
        score = 0.0
        for sig_name, sig_cfg in signals.items():
            patterns = sig_cfg.get("patterns", [])
            points = sig_cfg.get("points", 1)
            combined = "|".join(patterns)
            if re.search(combined, content, re.IGNORECASE):
                score += points
        return min(score, cfg.get("max", 2))

    def _score_efficiency(self, lines_per_test: float, asserts_per_test: float) -> float:
        """Efficiency dimension (0–2): lines/test + asserts/test thresholds."""
        cfg = self._dims.get("efficiency", {})
        rules = cfg.get("rules", {})
        lpt_threshold = rules.get("lines_per_test_threshold", 15)
        apt_threshold = rules.get("asserts_per_test_threshold", 2)
        score = 0.0
        if lines_per_test > lpt_threshold:
            score += 1
        if asserts_per_test > apt_threshold:
            score += 1
        return min(score, cfg.get("max", 2))

    def _score_maintenance_penalty(
        self, content: str, n_tests: int, total_asserts: int
    ) -> float:
        """Maintenance penalty (0 to −2): mocks + stubs + trivial asserts + single-assert."""
        if n_tests == 0:
            return -2.0

        cfg = self._dims.get("maintenance_penalty", {})
        rules = cfg.get("rules", {})
        penalty = 0.0

        # Mock heaviness
        mock_count = sum(
            len(re.findall(p.pattern, content)) for p in self._mock_patterns
        )
        mock_ratio = mock_count / n_tests
        if mock_ratio > rules.get("mock_ratio_threshold", 3):
            penalty -= 1

        # Stub ratio
        skip_count = sum(
            len(re.findall(p.pattern, content)) for p in self._skip_patterns
        )
        stub_ratio = skip_count / n_tests
        if stub_ratio > rules.get("stub_ratio_threshold", 0.5):
            penalty -= 1

        # Trivial assertion ratio
        if total_asserts > 0:
            trivial_count = sum(
                len(re.findall(p.pattern, content)) for p in self._trivial_patterns
            )
            trivial_ratio = trivial_count / total_asserts
            if trivial_ratio > rules.get("trivial_assert_ratio", 0.6):
                penalty -= 1

        # Single-assert test ratio
        test_bodies = re.split(r"(?=def test_)", content)
        single_assert_count = sum(
            1 for body in test_bodies
            if len(re.findall(r"\bassert\b", body)) == 1
        )
        single_assert_ratio = single_assert_count / n_tests
        if single_assert_ratio > rules.get("single_assert_ratio", 0.6):
            penalty -= 1

        return max(penalty, cfg.get("max", -2))

    def _detect_golden(self, content: str, filename: str) -> bool:
        """Detect if content qualifies as a golden (cross-orchestrator) test.

        Criteria (ALL must match):
          1. References ≥ 2 distinct orchestrator classes, OR file in tests/golden/
          2. Contains a sqlite/audit_log query assertion

        Args:
            content: Raw Python source.
            filename: File path string (used for path-based detection).

        Returns:
            True if detected as golden.
        """
        # Path-based: any file under tests/golden/ is always golden
        golden_dir_pattern = self._golden_cfg.get("golden_dir_pattern", "tests/golden")
        if golden_dir_pattern in filename.replace("\\", "/"):
            return True

        # Content-based: 2+ orchestrators + audit log query
        orch_pattern = self._golden_cfg.get(
            "orchestrator_pattern", r"(Orchestrator|Coordinator|Runner)\("
        )
        orch_matches = re.findall(orch_pattern, content)
        min_orch = self._golden_cfg.get("min_orchestrator_references", 2)
        if len(orch_matches) < min_orch:
            return False

        audit_patterns = self._golden_cfg.get("audit_log_patterns", [])
        for audit_pat in audit_patterns:
            if re.search(audit_pat, content, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def _load_config(path: Path) -> Dict[str, Any]:
        """Load scoring configuration from registry YAML.

        Args:
            path: Path to the YAML config file.

        Returns:
            Parsed configuration dict (empty dict on failure).
        """
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return {}


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def get_quality_gate() -> TestQualityGate:
    """Return a fresh TestQualityGate instance.

    Returns:
        New TestQualityGate (stateless — callers may also instantiate directly).
    """
    return TestQualityGate()


__all__ = [
    "TestQualityGate",
    "ScoreResult",
    "KEEP",
    "REVIEW",
    "DELETE",
    "get_quality_gate",
]
