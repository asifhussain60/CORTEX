"""
interaction_readiness_tracker.py — DoR Readiness Tracker for Guided Interaction.

Tracks Definition of Ready (DoR) dimensions across interaction turns.
Computes a deterministic DoR Readiness % and enforces an explicit approval
gate that only opens when DoR = 100%.

This module is the SSOT for readiness scoring in the default (non-autonomous)
interaction path.  It must never trigger execution — it only tracks, scores,
and reports.

Architecture:
    InteractionOrchestrator
        └─► InteractionReadinessTracker   ← this module
              ├── ReadinessDimension (per-dimension state)
              ├── ReadinessState      (aggregated snapshot)
              └── approvalgate        (open only at 100%)

Governance:
    - CORE-011: all public methods fully type-annotated
    - CORE-012: all public classes/methods documented
    - No autonomous execution — tracker is read/write state only

AC_START: AC-INTERACTION-DOR-TRACKER-001
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: DoR dimensions and their weights (must sum to 1.0)
DIMENSION_WEIGHTS: dict[str, float] = {
    "objective_clarity": 0.20,
    "scope_clarity": 0.15,
    "constraints": 0.10,
    "dependencies": 0.10,
    "inputs": 0.10,
    "risks": 0.10,
    "acceptance_criteria": 0.10,
    "testing_expectations": 0.05,
    "rollout_considerations": 0.05,
    "ownership": 0.05,
}

#: Human-readable labels for each dimension
DIMENSION_LABELS: dict[str, str] = {
    "objective_clarity": "Objective Clarity",
    "scope_clarity": "Scope Clarity",
    "constraints": "Constraints",
    "dependencies": "Dependencies",
    "inputs": "Inputs / Context Provided",
    "risks": "Risk Assessment",
    "acceptance_criteria": "Acceptance Criteria",
    "testing_expectations": "Testing Expectations",
    "rollout_considerations": "Rollout Considerations",
    "ownership": "Ownership / Approver",
}

#: Gate threshold — all dimensions must be at 100% to open
DOR_GATE_THRESHOLD: int = 100


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ReadinessDimension:
    """State of a single DoR dimension.

    Attributes:
        name: Machine-readable dimension key (e.g. ``"objective_clarity"``).
        label: Human-readable label (e.g. ``"Objective Clarity"``).
        weight: Fractional contribution to composite score (0.0–1.0).
        score: Current readiness score for this dimension (0–100).
        evidence: Optional text describing what was captured for this dimension.
        missing: Whether this dimension is still missing required information.
        open_question: Optional question to ask the user to resolve this dimension.
    """

    name: str
    label: str
    weight: float
    score: int = 0
    evidence: str = ""
    missing: bool = True
    open_question: Optional[str] = None


@dataclass
class ReadinessState:
    """Aggregated readiness snapshot across all dimensions.

    Attributes:
        dimensions: Ordered dict of dimension name → ReadinessDimension.
        composite_pct: Weighted composite DoR percentage (0–100).
        gate_open: True only when composite_pct == 100.
        missing_dimensions: Names of dimensions still below 100%.
        open_questions: List of pending questions for the user.
        blockers: Explicit blocker strings (e.g. dependency conflicts).
    """

    dimensions: dict[str, ReadinessDimension] = field(default_factory=dict)
    composite_pct: int = 0
    gate_open: bool = False
    missing_dimensions: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------


class InteractionReadinessTracker:
    """Tracks DoR readiness dimensions across guided interaction turns.

    Maintains per-dimension scores (0–100) and computes a deterministic
    weighted composite DoR Readiness %.  The approval gate opens **only**
    when the composite is exactly 100.

    Usage::

        tracker = InteractionReadinessTracker()
        tracker.update_dimension("objective_clarity", score=80,
                                 evidence="User wants an auth service")
        state = tracker.get_state()
        print(state.composite_pct)   # 16  (80 × 0.20 weight)
        print(tracker.is_gate_open())  # False

    Raises:
        ValueError: If an unknown dimension name is passed to update_dimension.

    AC_START: AC-INTERACTION-DOR-TRACKER-001
    """

    def __init__(self) -> None:
        """Initialise tracker with all dimensions at zero readiness."""
        self._dimensions: dict[str, ReadinessDimension] = {
            name: ReadinessDimension(
                name=name,
                label=DIMENSION_LABELS[name],
                weight=weight,
            )
            for name, weight in DIMENSION_WEIGHTS.items()
        }
        self._blockers: list[str] = []

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------

    def update_dimension(
        self,
        dimension: str,
        score: int,
        evidence: str = "",
        open_question: Optional[str] = None,
    ) -> None:
        """Update the readiness score for a single dimension.

        Args:
            dimension: Dimension key (must be in DIMENSION_WEIGHTS).
            score: Readiness score 0–100 for this dimension.
            evidence: Human-readable text captured for this dimension.
            open_question: Pending question for the user, or None if resolved.

        Raises:
            ValueError: If dimension is not a recognised key.
        """
        if dimension not in self._dimensions:
            raise ValueError(
                f"Unknown readiness dimension: '{dimension}'. "
                f"Valid keys: {sorted(self._dimensions.keys())}"
            )
        dim = self._dimensions[dimension]
        dim.score = max(0, min(100, score))
        dim.evidence = evidence
        dim.missing = dim.score < 100
        dim.open_question = open_question if dim.missing else None

    def add_blocker(self, blocker: str) -> None:
        """Register an explicit blocker that prevents gate from opening.

        Args:
            blocker: Human-readable blocker description.
        """
        if blocker and blocker not in self._blockers:
            self._blockers.append(blocker)

    def clear_blocker(self, blocker: str) -> None:
        """Remove a resolved blocker.

        Args:
            blocker: The blocker string to remove.
        """
        self._blockers = [b for b in self._blockers if b != blocker]

    def reset(self) -> None:
        """Reset all dimensions and blockers to zero state."""
        for dim in self._dimensions.values():
            dim.score = 0
            dim.evidence = ""
            dim.missing = True
            dim.open_question = None
        self._blockers.clear()

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def compute_dor_percentage(self) -> int:
        """Compute the deterministic weighted DoR composite score (0–100).

        Formula: sum(dimension.score * dimension.weight) rounded to int.
        Returns 0 if any blocker is active, regardless of dimension scores.

        Returns:
            Integer DoR percentage in range [0, 100].
        """
        if self._blockers:
            return 0

        raw = sum(
            dim.score * dim.weight
            for dim in self._dimensions.values()
        )
        return round(raw)

    def is_gate_open(self) -> bool:
        """Return True only when ALL dimensions are at 100% and no blockers are active.

        Checks both the composite score and each individual dimension.
        A composite of 100% is necessary but not sufficient — every
        dimension must individually reach 100% to prevent edge cases
        caused by weighted rounding.

        Returns:
            True if the approval gate is open, False otherwise.
        """
        if self._blockers:
            return False
        # Every individual dimension must be at 100%; composite gate is secondary
        all_complete = all(dim.score == 100 for dim in self._dimensions.values())
        return all_complete

    def get_missing_dimensions(self) -> list[str]:
        """Return human-readable labels of dimensions below 100%.

        Returns:
            List of label strings for incomplete dimensions.
        """
        return [
            dim.label
            for dim in self._dimensions.values()
            if dim.missing
        ]

    def get_open_questions(self) -> list[str]:
        """Return all pending questions for the user.

        Returns:
            List of open question strings across all dimensions.
        """
        return [
            dim.open_question
            for dim in self._dimensions.values()
            if dim.open_question is not None
        ]

    def get_next_question(self) -> Optional[str]:
        """Return the highest-priority unanswered question.

        Priority: highest-weight incomplete dimension with an open question.

        Returns:
            The next question string, or None if all dimensions are resolved.
        """
        incomplete = sorted(
            (dim for dim in self._dimensions.values() if dim.open_question),
            key=lambda d: d.weight,
            reverse=True,
        )
        return incomplete[0].open_question if incomplete else None

    def get_state(self) -> ReadinessState:
        """Return the full aggregated readiness snapshot.

        Returns:
            ReadinessState with composite %, gate status, missing dimensions,
            open questions, and active blockers.
        """
        composite = self.compute_dor_percentage()
        return ReadinessState(
            dimensions=dict(self._dimensions),
            composite_pct=composite,
            gate_open=self.is_gate_open(),
            missing_dimensions=self.get_missing_dimensions(),
            open_questions=self.get_open_questions(),
            blockers=list(self._blockers),
        )

    def get_footer_line(
        self,
        workflow_name: str = "",
        mode: str = "Guided",
    ) -> str:
        """Render the single-line status footer for Copilot Chat responses.

        Format:
            🧠 CORTEX · Guided · DoR 42% · Gate 🔴 LOCKED · ✋ 7 questions · ⚠ 0 blockers

        Args:
            workflow_name: Active workflow template name (e.g. ``"feature-planning"``).
            mode: Current orchestrator mode label.

        Returns:
            Single-line footer string — always non-empty.
        """
        composite = self.compute_dor_percentage()
        gate_icon = "✅ OPEN" if self.is_gate_open() else "🔴 LOCKED"
        open_q = len(self.get_open_questions())
        blockers = len(self._blockers)
        missing = len(self.get_missing_dimensions())

        parts = [
            "🧠 CORTEX",
            mode,
            f"DoR {composite}%",
            f"Gate {gate_icon}",
        ]
        if workflow_name:
            parts.append(f"Workflow: {workflow_name}")
        parts.append(f"✋ {open_q} questions")
        parts.append(f"⚠ {blockers} blockers")
        if missing:
            parts.append(f"📋 {missing} dimensions incomplete")

        return " · ".join(parts)


# AC_COMPLETE: AC-INTERACTION-DOR-TRACKER-001
