"""
Phase 87 — Prevention Gate Tests (RED phase — CORE-008)
Tests for PreventionGate — compares incoming operations against stored rules.

AC-PHASE87-004: PreventionGate tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def empty_store(tmp_path: Path):
    """Return an initialised (empty) RCAStore bound to a temp DB."""
    from cortex.intelligence.learning.rca_store import RCAStore
    store = RCAStore(db_path=str(tmp_path / "rca_store.db"))
    store.initialize()
    return store


@pytest.fixture
def gate(empty_store):
    """Return a PreventionGate wired to an empty store."""
    from cortex.intelligence.learning.prevention_gate import PreventionGate
    return PreventionGate(store=empty_store)


@pytest.fixture
def gate_with_advisory_rule(empty_store):
    """Return a PreventionGate with one ADVISORY rule stored."""
    from cortex.intelligence.learning.rca_models import PreventionRule, GateLevel
    rule = PreventionRule(
        id="RULE-GATE-001",
        rca_id="RCA-GATE-001",
        rule_text="Prevent null handler access on response object",
        gate_level=GateLevel.ADVISORY,
    )
    empty_store.save_rule(rule)
    from cortex.intelligence.learning.prevention_gate import PreventionGate
    return PreventionGate(store=empty_store)


@pytest.fixture
def gate_with_blocking_rule(empty_store):
    """Return a PreventionGate with one BLOCKING rule stored."""
    from cortex.intelligence.learning.rca_models import PreventionRule, GateLevel
    rule = PreventionRule(
        id="RULE-GATE-002",
        rca_id="RCA-GATE-002",
        rule_text="BLOCK operation accessing deprecated endpoint without migration",
        gate_level=GateLevel.BLOCKING,
    )
    empty_store.save_rule(rule)
    from cortex.intelligence.learning.prevention_gate import PreventionGate
    return PreventionGate(store=empty_store)


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------
class TestPreventionGateImport:
    """PreventionGate must be importable and correctly structured."""

    def test_prevention_gate_is_importable(self) -> None:
        """PreventionGate must be importable from the learning module."""
        from cortex.intelligence.learning.prevention_gate import PreventionGate
        assert PreventionGate is not None

    def test_prevention_gate_has_check(self) -> None:
        """PreventionGate must expose check() method."""
        from cortex.intelligence.learning.prevention_gate import PreventionGate
        assert hasattr(PreventionGate, "check")


# ---------------------------------------------------------------------------
# check() with no rules
# ---------------------------------------------------------------------------
class TestPreventionGateNoRules:
    """Gate returns PASS when no rules are stored."""

    def test_check_returns_gate_result(self, gate) -> None:
        """check() must return a PreventionGateResult."""
        from cortex.intelligence.learning.rca_models import PreventionGateResult
        result = gate.check(operation_context="accessing response handler")
        assert isinstance(result, PreventionGateResult)

    def test_check_passes_when_no_rules(self, gate) -> None:
        """check() must return PASS gate_level when no rules exist."""
        from cortex.intelligence.learning.rca_models import GateLevel
        result = gate.check(operation_context="any operation context")
        assert result.gate_level == GateLevel.PASS

    def test_check_no_matched_rule_when_no_rules(self, gate) -> None:
        """check() must set matched_rule=None when no rules exist."""
        result = gate.check(operation_context="any operation context")
        assert result.matched_rule is None


# ---------------------------------------------------------------------------
# check() with ADVISORY rule
# ---------------------------------------------------------------------------
class TestPreventionGateAdvisory:
    """Gate returns ADVISORY when a matching advisory rule is found."""

    def test_check_returns_advisory_for_matching_context(self, gate_with_advisory_rule) -> None:
        """check() must return ADVISORY when an advisory rule matches."""
        from cortex.intelligence.learning.rca_models import GateLevel
        # Context overlaps with rule_text keywords
        result = gate_with_advisory_rule.check(operation_context="null handler access on response")
        assert result.gate_level == GateLevel.ADVISORY

    def test_check_sets_matched_rule_on_advisory_match(self, gate_with_advisory_rule) -> None:
        """check() must populate matched_rule when a rule matches."""
        result = gate_with_advisory_rule.check(operation_context="null handler access on response")
        assert result.matched_rule is not None

    def test_check_has_non_empty_message(self, gate_with_advisory_rule) -> None:
        """check() result message must be non-empty string."""
        result = gate_with_advisory_rule.check(operation_context="null handler access on response")
        assert isinstance(result.message, str)
        assert len(result.message) > 0


# ---------------------------------------------------------------------------
# check() with BLOCKING rule
# ---------------------------------------------------------------------------
class TestPreventionGateBlocking:
    """Gate returns BLOCKING when a matching blocking rule is found."""

    def test_check_returns_blocking_for_matching_context(self, gate_with_blocking_rule) -> None:
        """check() must return BLOCKING when a blocking rule matches."""
        from cortex.intelligence.learning.rca_models import GateLevel
        result = gate_with_blocking_rule.check(
            operation_context="accessing deprecated endpoint without migration"
        )
        assert result.gate_level == GateLevel.BLOCKING

    def test_check_includes_rca_summary_on_blocking(self, gate_with_blocking_rule) -> None:
        """check() result rca_summary must be non-empty when BLOCKING."""
        result = gate_with_blocking_rule.check(
            operation_context="accessing deprecated endpoint without migration"
        )
        assert isinstance(result.rca_summary, str)


# ---------------------------------------------------------------------------
# check() — unrelated context passes
# ---------------------------------------------------------------------------
class TestPreventionGateUnrelatedContext:
    """Gate returns PASS when context has no keyword overlap with any rule."""

    def test_unrelated_context_passes_advisory_gate(self, gate_with_advisory_rule) -> None:
        """A completely unrelated context must return PASS even with rules stored."""
        from cortex.intelligence.learning.rca_models import GateLevel
        result = gate_with_advisory_rule.check(operation_context="xyz_totally_unrelated_xyz")
        assert result.gate_level == GateLevel.PASS
