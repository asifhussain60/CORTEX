"""
Phase 106-B: RCA Dispatch Wiring — Golden Tests (CORE-008 RED cycle)
Authority: GAP-106-02 (RCA never dispatched) + GAP-106-06 (PreventionRules unused)
SSOT: cortex-registry/planning/phases/planned/phase-106-rca-guard-certification.yaml

Tests validate that audit-fix-pipeline.yaml Stage 9 post_run includes rca_dispatch
and Stage 2 detect_step includes prevention_rules_lookup.
"""
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[3]
PIPELINE_PATH = (
    WORKSPACE
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "audit"
    / "audit-fix-pipeline.yaml"
)


class TestRcaAuditWiringGolden:
    """Phase 106-B: 4 golden tests for RCA dispatch and PreventionRule wiring."""

    def _pipeline_text(self) -> str:
        assert PIPELINE_PATH.exists(), f"Pipeline missing: {PIPELINE_PATH}"
        return PIPELINE_PATH.read_text()

    def test_rca_dispatched_for_recurring_violation(self) -> None:
        """GAP-106-02: Stage 9 post_run must contain rca_dispatch block for recurrent violations."""
        content = self._pipeline_text()
        assert "rca_dispatch" in content, (
            "audit-fix-pipeline.yaml Stage 9 post_run is missing 'rca_dispatch' block.\n"
            "Phase 106-B: Add rca_dispatch block to Stage 9 post_run that calls "
            "RCAEngine.analyze() when pattern_detection returns recurrence_count >= 3."
        )

    def test_prevention_rule_persisted(self) -> None:
        """GAP-106-06: rca_dispatch block must reference PreventionRule persistence."""
        content = self._pipeline_text()
        assert "rca_store" in content or "prevention_rule" in content.lower(), (
            "audit-fix-pipeline.yaml rca_dispatch block must reference "
            "PreventionRule persistence via rca_store.\n"
            "Phase 106-B: Add 'persist: rca_store.persist(rca_analysis)' to rca_dispatch."
        )

    def test_known_violation_elevated_to_p0(self) -> None:
        """GAP-106-06: Stage 2 detect_step must include prevention_rules_lookup for severity escalation."""
        content = self._pipeline_text()
        assert "prevention_rules_lookup" in content or "prevention_rules" in content, (
            "audit-fix-pipeline.yaml Stage 2 detect_step is missing prevention_rules_lookup.\n"
            "Phase 106-B: Add prevention_rules_lookup to Stage 2 that elevates known "
            "recurring violations from P1 → P0 before the scan begins."
        )

    def test_rca_inline_output_not_file(self) -> None:
        """GAP-106-02: rca_dispatch must emit inline only — no .md/.txt/.json file (CORE-002)."""
        content = self._pipeline_text()
        assert "rca_dispatch" in content, "rca_dispatch block missing — see test_rca_dispatched_for_recurring_violation"

        # Find rca_dispatch block and assert it uses emit_inline pattern
        rca_idx = content.index("rca_dispatch")
        rca_block = content[rca_idx : rca_idx + 800]
        assert "emit_inline" in rca_block or "inline" in rca_block, (
            "rca_dispatch block must use emit_inline output (CORE-002 — no file output).\n"
            "Add: emit_inline: '🔬 RCA: {root_cause} → PreventionRule {rule_id}'"
        )
