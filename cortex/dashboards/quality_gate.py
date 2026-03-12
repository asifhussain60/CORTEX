"""DashboardQualityGate — Phase 152-e

Evaluates dashboard output against quality rules and produces a QualityReport.

Rules:
    QR-001  Five-Second Rule: at least one METRIC_CARD with five_second_primary=True
    QR-002  F-Pattern: top-left visualization must have f_pattern_position='top-left'
    QR-003  Min narrative length: each tab narrative must be ≥ 150 words
    QR-004  No dead sections: tab narrative must not be empty
    QR-005  No cross-tab duplication: each narrative must be unique across tabs

Scoring:
    score = max(0, 100 - (p0_count * 20 + len(all_issues) * 5))
    passed = (p0_count == 0)

CORE: CORE-008 (TDD), CORE-011, CORE-012
Source: GitHub Issue #18 — FB-20260312-001
"""

from __future__ import annotations

from dataclasses import dataclass, field

MIN_NARRATIVE_WORDS = 150


@dataclass
class QualityIssue:
    """A single quality rule violation."""

    rule_id: str
    tab_id: str
    severity: str  # P0 or P1
    message: str


@dataclass
class QualityReport:
    """Aggregated quality evaluation result."""

    issues: list
    passed: bool
    score: int


class DashboardQualityGate:
    """Evaluate dashboard output quality and return a QualityReport."""

    def evaluate(
        self,
        narratives: "dict[str, str]",
        viz_selections: "dict[str, list]",
    ) -> QualityReport:
        """Run all quality rules and return a QualityReport."""
        issues: list = []

        # QR-003 & QR-004: narrative length checks
        seen_narratives: set = set()
        for tab_id, narrative in narratives.items():
            word_count = len(narrative.split())

            if narrative.strip() == "":
                issues.append(
                    QualityIssue(
                        rule_id="QR-004",
                        tab_id=tab_id,
                        severity="P0",
                        message=f"Tab '{tab_id}' has an empty narrative (dead section).",
                    )
                )
            elif word_count < MIN_NARRATIVE_WORDS:
                issues.append(
                    QualityIssue(
                        rule_id="QR-003",
                        tab_id=tab_id,
                        severity="P1",
                        message=(
                            f"Tab '{tab_id}' narrative has {word_count} words "
                            f"(minimum: {MIN_NARRATIVE_WORDS})."
                        ),
                    )
                )

            # QR-005: cross-tab duplication (exact duplicate only)
            if narrative and narrative in seen_narratives:
                issues.append(
                    QualityIssue(
                        rule_id="QR-005",
                        tab_id=tab_id,
                        severity="P1",
                        message=f"Tab '{tab_id}' narrative is identical to another tab.",
                    )
                )
            seen_narratives.add(narrative)

        # QR-001 & QR-002: visualization checks
        for tab_id, choices in viz_selections.items():
            has_metric_card_primary = any(
                getattr(c, "five_second_primary", False) for c in choices
            )
            has_top_left = any(
                getattr(c, "f_pattern_position", "") == "top-left" for c in choices
            )

            if choices and not has_metric_card_primary:
                issues.append(
                    QualityIssue(
                        rule_id="QR-001",
                        tab_id=tab_id,
                        severity="P1",
                        message=f"Tab '{tab_id}' lacks a five_second_primary METRIC_CARD.",
                    )
                )

            if choices and not has_top_left:
                issues.append(
                    QualityIssue(
                        rule_id="QR-002",
                        tab_id=tab_id,
                        severity="P1",
                        message=f"Tab '{tab_id}' has no top-left F-pattern visualization.",
                    )
                )

        p0_count = sum(1 for i in issues if i.severity == "P0")
        score = max(0, 100 - (p0_count * 20 + len(issues) * 5))

        return QualityReport(issues=issues, passed=(p0_count == 0), score=score)
