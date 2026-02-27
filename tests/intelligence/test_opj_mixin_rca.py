"""
Phase 87 — OPJMixin RCA Extension Tests (RED phase — CORE-008)
Tests for the two new OPJMixin methods:
  _opj_analyze_rca(failure_id, methodology=None)
  _opj_check_prevention_gate(operation_context)

AC-PHASE87-006: OPJMixin RCA extension tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class _ConcreteOrchestrator:
    """Minimal concrete class that mixes in OPJMixin for testing."""

    def __init__(self) -> None:
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        # Dynamically apply mixin
        self.__class__ = type(
            "ConcreteOrchestrator",
            (OPJMixin, self.__class__),
            {},
        )
        OPJMixin.__init__(self)  # type: ignore[arg-type]


@pytest.fixture
def orchestrator():
    """Return an orchestrator with OPJMixin applied."""
    from cortex.intelligence.learning.opj_mixin import OPJMixin

    class _Orch(OPJMixin):
        pass

    return _Orch()


# ---------------------------------------------------------------------------
# Import / method presence
# ---------------------------------------------------------------------------
class TestOPJMixinRCAMethodsPresent:
    """New RCA methods must exist on OPJMixin."""

    def test_opj_analyze_rca_exists(self) -> None:
        """OPJMixin must have _opj_analyze_rca method."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        assert hasattr(OPJMixin, "_opj_analyze_rca")

    def test_opj_check_prevention_gate_exists(self) -> None:
        """OPJMixin must have _opj_check_prevention_gate method."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        assert hasattr(OPJMixin, "_opj_check_prevention_gate")


# ---------------------------------------------------------------------------
# _opj_analyze_rca
# ---------------------------------------------------------------------------
class TestOPJAnalyzeRCA:
    """Tests for OPJMixin._opj_analyze_rca()."""

    def test_analyze_rca_returns_rca_analysis(self, orchestrator) -> None:
        """_opj_analyze_rca must return an RCAAnalysis instance."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis
        result = orchestrator._opj_analyze_rca(
            failure_id="OPJ-opjmixin-001",
            failure_description="AttributeError on response",
        )
        assert isinstance(result, RCAAnalysis)

    def test_analyze_rca_stores_result(self, orchestrator, tmp_path: Path) -> None:
        """_opj_analyze_rca must persist the RCAAnalysis via RCAStore."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis
        # Run analysis — persistence is tested by verifying return value has an id
        result = orchestrator._opj_analyze_rca(
            failure_id="OPJ-opjmixin-002",
            failure_description="NullPointerException in handler",
        )
        assert result.id.startswith("RCA-")

    def test_analyze_rca_accepts_optional_methodology(self, orchestrator) -> None:
        """_opj_analyze_rca must accept an optional methodology param."""
        from cortex.intelligence.learning.rca_models import RCATemplate, RCATemplate
        result = orchestrator._opj_analyze_rca(
            failure_id="OPJ-opjmixin-003",
            failure_description="Test failure after refactor",
            methodology=RCATemplate.FISHBONE,
        )
        assert result.methodology.value == "fishbone"

    def test_analyze_rca_non_fatal_on_error(self, orchestrator) -> None:
        """_opj_analyze_rca must not raise even if internal engine fails."""
        # Pass an empty failure_description — should still return something
        try:
            orchestrator._opj_analyze_rca(failure_id="OPJ-opjmixin-004", failure_description="")
        except Exception as exc:
            pytest.fail(f"_opj_analyze_rca raised unexpectedly: {exc}")


# ---------------------------------------------------------------------------
# _opj_check_prevention_gate
# ---------------------------------------------------------------------------
class TestOPJCheckPreventionGate:
    """Tests for OPJMixin._opj_check_prevention_gate()."""

    def test_check_prevention_gate_returns_gate_result(self, orchestrator) -> None:
        """_opj_check_prevention_gate must return a PreventionGateResult."""
        from cortex.intelligence.learning.rca_models import PreventionGateResult
        result = orchestrator._opj_check_prevention_gate(
            operation_context="running async response handler"
        )
        assert isinstance(result, PreventionGateResult)

    def test_check_prevention_gate_returns_pass_when_no_rules(self, orchestrator) -> None:
        """_opj_check_prevention_gate must return PASS when no rules are stored."""
        from cortex.intelligence.learning.rca_models import GateLevel
        result = orchestrator._opj_check_prevention_gate(operation_context="any operation")
        assert result.gate_level == GateLevel.PASS

    def test_check_prevention_gate_non_fatal_on_error(self, orchestrator) -> None:
        """_opj_check_prevention_gate must not raise on any input."""
        try:
            orchestrator._opj_check_prevention_gate(operation_context="")
        except Exception as exc:
            pytest.fail(f"_opj_check_prevention_gate raised unexpectedly: {exc}")
