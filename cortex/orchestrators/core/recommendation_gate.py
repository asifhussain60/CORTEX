"""
RecommendationGate — Regression Prevention Layer.

AC-ID: AC-RECOMMENDATION-GATE-001
Prevents regression-causing recommendations by checking rejection history,
regression risk scoring, test health, and duplication.

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HIGH-RISK FILE PATTERNS
# ---------------------------------------------------------------------------
_HIGH_RISK_PATHS = {
    "cortex/orchestrators/core/master_orchestrator.py",
    "cortex/orchestrators/core/intent_router.py",
    "cortex/orchestrators/core/tdd_orchestrator.py",
    "cortex/orchestrators/core/enforcement_orchestrator.py",
    "cortex/wiring/specifications/wiring.yaml",
    "cortex/mcp/server.py",
    "cortex/core/orchestrator_base.py",
}

_HIGH_RISK_CHANGE_TYPES = {"rewrite", "delete", "restructure", "remove"}
_LOW_RISK_CHANGE_TYPES = {"add", "documentation", "docs", "comment", "test"}


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class GateStatus(str, Enum):
    """Status of a single gate check."""

    PASS = "pass"
    BLOCKED = "blocked"
    WARN = "warn"


class GateVerdict(str, Enum):
    """Overall verdict after all gates."""

    SAFE = "safe"
    BLOCKED = "blocked"
    WARN = "warn"


# ---------------------------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------------------------

@dataclass
class GateResult:
    """Result of a single gate check.

    Attributes:
        gate_name: Human-readable name of the gate (e.g. "REJ-History").
        status: Pass / Blocked / Warn.
        reason: Explanation string.
        score: Optional numeric score (0–1).
    """

    gate_name: str
    status: GateStatus
    reason: str
    score: Optional[float] = None


@dataclass
class GateEvaluation:
    """Aggregated evaluation result from all gates.

    Attributes:
        verdict: Overall SAFE / BLOCKED / WARN.
        gates: List of individual gate results.
        recommendation_title: Title of the evaluated recommendation.
    """

    verdict: GateVerdict
    gates: List[GateResult] = field(default_factory=list)
    recommendation_title: str = ""

    def to_markdown(self) -> str:
        """Render a Markdown summary of this evaluation.

        Returns:
            Formatted Markdown string with gate status table.
        """
        if self.verdict == GateVerdict.BLOCKED:
            header = "### ⚡ Recommendation BLOCKED"
        elif self.verdict == GateVerdict.WARN:
            header = "### ⚡ Recommendation Safety Check — ⚠️ WARNING"
        else:
            header = "### ⚡ Recommendation Safety Check"

        lines = [
            header,
            f"**Recommendation:** {self.recommendation_title}",
            f"**Verdict:** `{self.verdict.value.upper()}`",
            "",
            "| Gate | Status | Reason |",
            "|------|--------|--------|",
        ]
        for gate in self.gates:
            icon = {"pass": "✅", "blocked": "🚫", "warn": "⚠️"}.get(gate.status.value, "?")
            lines.append(f"| {gate.gate_name} | {icon} {gate.status.value} | {gate.reason} |")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# RECOMMENDATION GATE
# ---------------------------------------------------------------------------

class RecommendationGate:
    """Regression prevention gate for AI recommendations.

    Evaluates recommendations against:
    1. Rejection history (CORE-035 — no duplicate bad ideas)
    2. Regression risk scoring (based on affected files and change type)
    3. Test health check
    4. Duplication check

    Args:
        risk_threshold: Float 0–1; recommendations above this are BLOCKED
            on regression risk alone. Defaults to 0.7.
        similarity_threshold: Float 0–1; rejection match threshold.
            Defaults to 0.6.
    """

    def __init__(
        self,
        risk_threshold: float = 0.7,
        similarity_threshold: float = 0.6,
    ) -> None:
        """Initialize RecommendationGate with configurable thresholds.

        Args:
            risk_threshold: Maximum acceptable regression risk score.
            similarity_threshold: Minimum similarity to trigger rejection block.
        """
        self.risk_threshold = risk_threshold
        self.similarity_threshold = similarity_threshold
        self.rejected_recommendations: List[Dict[str, Any]] = []
        self._load_rejection_history()

    # -----------------------------------------------------------------------
    # HISTORY MANAGEMENT
    # -----------------------------------------------------------------------

    def _load_rejection_history(self) -> None:
        """Load rejection history from YAML registry if available."""
        history_paths = [
            Path("cortex-registry/memory/enhancement-history.yaml"),
            Path("cortex-registry/memory/rejection-history.yaml"),
            Path(".cortex-runtime/rejection-history.yaml"),
        ]
        for path in history_paths:
            if path.exists():
                try:
                    import yaml  # type: ignore[import]
                    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                    self.rejected_recommendations = data.get("rejected", [])
                    logger.debug(
                        "Loaded %d rejected recommendations from %s",
                        len(self.rejected_recommendations),
                        path,
                    )
                    return
                except Exception as exc:
                    logger.debug("Could not load rejection history from %s: %s", path, exc)

        # Start with empty list if no file found
        self.rejected_recommendations = []

    def refresh_history(self) -> None:
        """Reload rejection history from disk.

        Returns:
            None
        """
        self._load_rejection_history()

    # -----------------------------------------------------------------------
    # SIMILARITY
    # -----------------------------------------------------------------------

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate token-overlap similarity between two recommendation texts.

        Uses Jaccard similarity on word token sets (no external deps).

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            Float in [0.0, 1.0].
        """
        def tokenize(text: str) -> set:
            """Split text into a set of lowercase word tokens."""
            return set(re.findall(r"[a-z]+", text.lower()))

        tokens_a = tokenize(text_a)
        tokens_b = tokenize(text_b)

        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0

        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        return len(intersection) / len(union)

    # -----------------------------------------------------------------------
    # GATE CHECKS
    # -----------------------------------------------------------------------

    def check_rejection_history(self, recommendation: Dict[str, Any]) -> GateResult:
        """Check recommendation against previously rejected recommendations.

        Args:
            recommendation: Dict with at least 'title' and optional 'description'.

        Returns:
            GateResult with PASS or BLOCKED status.
        """
        rec_text = " ".join([
            recommendation.get("title", ""),
            recommendation.get("description", ""),
        ])

        for rejected in self.rejected_recommendations:
            rejected_text = " ".join([
                rejected.get("recommendation", ""),
                " ".join(rejected.get("lessons_learned", [])),
            ])
            similarity = self.calculate_similarity(rec_text, rejected_text)

            if similarity >= self.similarity_threshold:
                rejected_id = rejected.get("id", "unknown")
                return GateResult(
                    gate_name="REJ-History",
                    status=GateStatus.BLOCKED,
                    reason=f"Similar to rejected recommendation {rejected_id}: "
                           f"'{rejected.get('rejection_reason', 'see history')}'",
                    score=similarity,
                )

        return GateResult(
            gate_name="REJ-History",
            status=GateStatus.PASS,
            reason="No matching rejection in history",
            score=0.0,
        )

    def calculate_regression_risk(self, recommendation: Dict[str, Any]) -> float:
        """Score regression risk for a recommendation (0.0 = safe, 1.0 = max risk).

        Args:
            recommendation: Dict with 'affected_files' and 'change_type' keys.

        Returns:
            Float risk score in [0.0, 1.0].
        """
        affected_files: List[str] = recommendation.get("affected_files", [])
        change_type: str = recommendation.get("change_type", "").lower()

        # Base risk by change type
        if change_type in _LOW_RISK_CHANGE_TYPES:
            base_risk = 0.05
        elif change_type in _HIGH_RISK_CHANGE_TYPES:
            base_risk = 0.75
        else:
            base_risk = 0.3

        # File risk multiplier
        file_risk = 0.0
        for file_path in affected_files:
            if file_path in _HIGH_RISK_PATHS:
                file_risk += 0.3
            elif "core" in file_path or "wiring" in file_path or "mcp" in file_path:
                file_risk += 0.15
            elif "orchestrators" in file_path:
                file_risk += 0.1
            else:
                file_risk += 0.03

        # Scale file risk by count
        num_files = len(affected_files)
        if num_files > 5:
            file_risk *= 1.5
        elif num_files > 2:
            file_risk *= 1.2

        total = min(base_risk + file_risk, 1.0)
        return round(total, 4)

    def check_test_health(self, recommendation: Dict[str, Any]) -> GateResult:
        """Check test health for files affected by the recommendation.

        Args:
            recommendation: Dict with 'affected_files' list and 'change_type'.

        Returns:
            GateResult with PASS or WARN status.
        """
        affected_files = recommendation.get("affected_files", [])
        change_type = recommendation.get("change_type", "").lower()

        # Documentation / additive-only changes don't require test check
        if change_type in _LOW_RISK_CHANGE_TYPES:
            return GateResult(
                gate_name="Test-Health",
                status=GateStatus.PASS,
                reason=f"Test check skipped for '{change_type}' change type",
            )

        missing_tests = []

        for file_path in affected_files:
            # Derive expected test path
            test_path = Path(file_path.replace("cortex/", "tests/unit/", 1))
            test_file = test_path.parent / f"test_{test_path.stem}.py"
            if not test_file.exists():
                missing_tests.append(str(test_file))

        if missing_tests:
            return GateResult(
                gate_name="Test-Health",
                status=GateStatus.WARN,
                reason=f"Missing tests for: {', '.join(missing_tests[:3])}",
            )

        return GateResult(
            gate_name="Test-Health",
            status=GateStatus.PASS,
            reason="Test coverage looks adequate",
        )

    def check_duplication(self, recommendation: Dict[str, Any]) -> GateResult:
        """Check if recommended code already exists in codebase.

        Args:
            recommendation: Dict with optional 'code_snippet'.

        Returns:
            GateResult with PASS or WARN status.
        """
        snippet = recommendation.get("code_snippet", "")
        if not snippet:
            return GateResult(
                gate_name="Duplication",
                status=GateStatus.PASS,
                reason="No code snippet to check",
            )

        # Lightweight check: look for function name in codebase
        func_match = re.search(r"def (\w+)", snippet)
        if func_match:
            func_name = func_match.group(1)
            # Search cortex/ for the function name
            found = list(Path("cortex").rglob("*.py")) if Path("cortex").exists() else []
            for py_file in found[:50]:  # limit for performance
                try:
                    if func_name in py_file.read_text(encoding="utf-8"):
                        return GateResult(
                            gate_name="Duplication",
                            status=GateStatus.WARN,
                            reason=f"Function '{func_name}' may already exist in codebase",
                        )
                except OSError:
                    pass

        return GateResult(
            gate_name="Duplication",
            status=GateStatus.PASS,
            reason="No duplication detected",
        )

    # -----------------------------------------------------------------------
    # FULL EVALUATION
    # -----------------------------------------------------------------------

    def evaluate(self, recommendation: Dict[str, Any]) -> GateEvaluation:
        """Run all gate checks and return aggregated evaluation.

        Gates run (in order):
        1. REJ-History — rejection history check
        2. Regression-Risk — risk scoring
        3. Test-Health — test coverage check
        4. Duplication — code duplication check

        Args:
            recommendation: Recommendation dict with 'title', 'affected_files',
                'change_type', 'description', and optional 'code_snippet'.

        Returns:
            GateEvaluation with overall verdict and individual gate results.
        """
        gates: List[GateResult] = []

        # Gate 1: Rejection history
        rej_result = self.check_rejection_history(recommendation)
        gates.append(rej_result)

        # Gate 2: Regression risk
        risk_score = self.calculate_regression_risk(recommendation)
        if risk_score >= self.risk_threshold:
            risk_status = GateStatus.BLOCKED
            risk_reason = f"Regression risk {risk_score:.2f} exceeds threshold {self.risk_threshold:.2f}"
        elif risk_score >= 0.4:
            risk_status = GateStatus.WARN
            risk_reason = f"Moderate regression risk: {risk_score:.2f}"
        else:
            risk_status = GateStatus.PASS
            risk_reason = f"Low regression risk: {risk_score:.2f}"

        gates.append(GateResult(
            gate_name="Regression-Risk",
            status=risk_status,
            reason=risk_reason,
            score=risk_score,
        ))

        # Gate 3: Test health
        gates.append(self.check_test_health(recommendation))

        # Gate 4: Duplication
        gates.append(self.check_duplication(recommendation))

        # Determine overall verdict
        if any(g.status == GateStatus.BLOCKED for g in gates):
            verdict = GateVerdict.BLOCKED
        elif any(g.status == GateStatus.WARN for g in gates):
            verdict = GateVerdict.WARN
        else:
            verdict = GateVerdict.SAFE

        return GateEvaluation(
            verdict=verdict,
            gates=gates,
            recommendation_title=recommendation.get("title", ""),
        )
