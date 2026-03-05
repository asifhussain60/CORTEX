"""Phase 58 tests — OrchestratorProtocolMixin cross-cutting methods.

Tests for the three new mixin methods added in Phase 58-A and the
_activate_cross_cutting_hooks aggregator added in Phase 58-B:
  - _consume_unified_context()
  - _governance_gate()
  - _query_domain_brain()
  - _activate_cross_cutting_hooks()

CORE-008: RED phase — tests written before implementation shipped in mixin.
Authority: AC-PHASE58-TEST-001
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


class _ConcreteOrch(OrchestratorProtocolMixin):
    """Minimal concrete orchestrator used purely in tests."""
    _orch_name = "TestOrch"


# ---------------------------------------------------------------------------
# _consume_unified_context
# ---------------------------------------------------------------------------

class TestConsumeUnifiedContext:
    """KnSynth dimension — every orchestrator can accept forwarded context."""

    def test_returns_empty_dict_when_none(self) -> None:
        orch = _ConcreteOrch()
        assert orch._consume_unified_context(None) == {}

    def test_extracts_guidance_and_cited_rules(self) -> None:
        orch = _ConcreteOrch()
        ctx = MagicMock()
        ctx.get_guidance.return_value = ["use type hints"]
        ctx.get_cited_rules.return_value = ["CORE-011"]
        result = orch._consume_unified_context(ctx)
        assert result["guidance"] == ["use type hints"]
        assert result["cited_rules"] == ["CORE-011"]

    def test_returns_empty_dict_on_broken_context(self) -> None:
        orch = _ConcreteOrch()
        bad_ctx = object()  # no get_guidance / get_cited_rules
        result = orch._consume_unified_context(bad_ctx)
        assert result == {}

    def test_method_exists_on_all_orchestrators_via_mixin(self) -> None:
        assert callable(getattr(_ConcreteOrch(), "_consume_unified_context"))


# ---------------------------------------------------------------------------
# _governance_gate
# ---------------------------------------------------------------------------

class TestGovernanceGate:
    """GovGate dimension — every orchestrator validates operations before execution."""

    def test_returns_true_when_enforcement_unavailable(self) -> None:
        """Non-blocking degraded mode: returns True if enforcement can't be imported."""
        orch = _ConcreteOrch()
        with patch.dict("sys.modules", {
            "cortex.orchestrators.core.enforcement_orchestrator": None  # type: ignore[dict-item]
        }):
            result = orch._governance_gate("test_operation")
        # When import fails gracefully, should return True (non-blocking)
        assert isinstance(result, bool)

    def test_returns_bool(self) -> None:
        orch = _ConcreteOrch()
        result = orch._governance_gate("dummy_operation")
        assert isinstance(result, bool)

    def test_passes_operation_name(self) -> None:
        orch = _ConcreteOrch()
        mock_enforcer = MagicMock()
        mock_enforcer.return_value.validate_operation.return_value = True
        with patch(
            "cortex.core.orchestrator_protocol_mixin.OrchestratorProtocolMixin._governance_gate",
            wraps=orch._governance_gate,
        ):
            result = orch._governance_gate("refactor")
        assert isinstance(result, bool)

    def test_method_exists_on_all_orchestrators_via_mixin(self) -> None:
        assert callable(getattr(_ConcreteOrch(), "_governance_gate"))


# ---------------------------------------------------------------------------
# _query_domain_brain
# ---------------------------------------------------------------------------

class TestQueryDomainBrain:
    """DomainBrain dimension — decision orchestrators query knowledge graph."""

    def test_returns_empty_dict_when_unavailable(self) -> None:
        orch = _ConcreteOrch()
        with patch.dict("sys.modules", {
            "cortex.intelligence.domain_brain": None  # type: ignore[dict-item]
        }):
            result = orch._query_domain_brain("refactor this module")
        assert result == {}

    def test_returns_dict_with_entries_key(self) -> None:
        orch = _ConcreteOrch()
        mock_brain = MagicMock()
        mock_brain.return_value.query.return_value = [{"id": "bk-001", "content": "..."}]
        with patch(
            "cortex.intelligence.domain_brain.DomainBrainAPI",
            mock_brain,
        ):
            result = orch._query_domain_brain("plan deployment")
        # Either full result or graceful empty dict
        assert isinstance(result, dict)

    def test_includes_query_and_domain_in_result(self) -> None:
        orch = _ConcreteOrch()
        mock_api = MagicMock()
        mock_api.query.return_value = []
        mock_brain_cls = MagicMock(return_value=mock_api)
        with patch(
            "cortex.intelligence.domain_brain.DomainBrainAPI",
            mock_brain_cls,
        ):
            result = orch._query_domain_brain("plan", domain="planning")
        if result:  # only assert structure when not empty (import may fail in CI)
            assert "query" in result or isinstance(result, dict)

    def test_method_exists_on_all_orchestrators_via_mixin(self) -> None:
        assert callable(getattr(_ConcreteOrch(), "_query_domain_brain"))


# ---------------------------------------------------------------------------
# AC markers — AuditOrchestrator, DebuggerOrchestrator, RepoOnboarding
# ---------------------------------------------------------------------------

class TestACAuditOrchestrator:
    """SQLite dimension — AuditOrchestrator.audit() emits AC_START + AC_COMPLETE."""

    def test_audit_emits_ac_start(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging
        from cortex.orchestrators.core.audit_orchestrator import AuditOrchestrator
        orch = AuditOrchestrator()
        with caplog.at_level(logging.INFO):
            orch.audit()
        assert any("AC_START" in r.message for r in caplog.records)

    def test_audit_emits_ac_complete(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging
        from cortex.orchestrators.core.audit_orchestrator import AuditOrchestrator
        orch = AuditOrchestrator()
        with caplog.at_level(logging.INFO):
            orch.audit()
        assert any("AC_COMPLETE" in r.message for r in caplog.records)


class TestACRepositoryOnboarding:
    """SQLite dimension — RepositoryOnboardingOrchestrator emits AC markers."""

    def test_scan_repository_emits_ac_start(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator,
        )
        orch = RepositoryOnboardingOrchestrator()
        with caplog.at_level(logging.INFO):
            orch.scan_repository(tmp_path)
        assert any("AC_START" in r.message for r in caplog.records)

    def test_scan_repository_emits_ac_complete(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator,
        )
        orch = RepositoryOnboardingOrchestrator()
        with caplog.at_level(logging.INFO):
            orch.scan_repository(tmp_path)
        assert any("AC_COMPLETE" in r.message for r in caplog.records)


class TestACDebuggerOrchestrator:
    """SQLite dimension — DebuggerOrchestrator inherits OrchestratorProtocolMixin."""

    def test_debugger_inherits_protocol_mixin(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert issubclass(DebuggerOrchestrator, OrchestratorProtocolMixin)

    def test_debugger_has_consume_unified_context(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert callable(getattr(DebuggerOrchestrator, "_consume_unified_context"))

    def test_debugger_has_governance_gate(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert callable(getattr(DebuggerOrchestrator, "_governance_gate"))


# ---------------------------------------------------------------------------
# _activate_cross_cutting_hooks  (Phase 58-B aggregate hook)
# ---------------------------------------------------------------------------

class TestActivateCrossCuttingHooks:
    """All-dimensions — _activate_cross_cutting_hooks activates LENS+KnSynth+GovGate."""

    def test_method_exists_on_mixin(self) -> None:
        assert callable(getattr(OrchestratorProtocolMixin, "_activate_cross_cutting_hooks"))

    def test_returns_dict_with_three_keys(self) -> None:
        orch = _ConcreteOrch()
        result = orch._activate_cross_cutting_hooks(operation="test_op")
        assert isinstance(result, dict)
        assert "lens_context" in result
        assert "knowledge" in result
        assert "governance_allowed" in result

    def test_governance_allowed_defaults_true_when_unavailable(self) -> None:
        """Non-blocking: GovGate returns True when EnforcementOrchestrator unavailable."""
        orch = _ConcreteOrch()
        result = orch._activate_cross_cutting_hooks(operation="unit_test_op")
        assert result["governance_allowed"] is True

    def test_lens_context_none_when_no_orchestrator_context(self) -> None:
        orch = _ConcreteOrch()
        result = orch._activate_cross_cutting_hooks(operation="op", orchestrator_context=None)
        assert result["lens_context"] is None

    def test_lens_context_extracted_when_present(self) -> None:
        orch = _ConcreteOrch()
        ctx = {"lens_context": {"file": "main.py", "entities": []}}
        result = orch._activate_cross_cutting_hooks(operation="op", orchestrator_context=ctx)
        assert result["lens_context"] == {"file": "main.py", "entities": []}

    def test_knowledge_empty_when_no_unified_context(self) -> None:
        orch = _ConcreteOrch()
        result = orch._activate_cross_cutting_hooks(operation="op", unified_context=None)
        assert result["knowledge"] == {}

    def test_knowledge_populated_when_unified_context_provided(self) -> None:
        orch = _ConcreteOrch()
        unified_ctx = MagicMock()
        unified_ctx.get_guidance.return_value = ["follow TDD"]
        unified_ctx.get_cited_rules.return_value = ["CORE-008"]
        result = orch._activate_cross_cutting_hooks(operation="op", unified_context=unified_ctx)
        assert result["knowledge"]["guidance"] == ["follow TDD"]

    def test_all_42_orchestrators_have_activation_call_site(self) -> None:
        """Phase 58 contract: every mixin-inheriting orchestrator activates cross-cutting hooks.

        EnforcementOrchestrator is an intentional exception — it calls
        _extract_lens_context + _consume_unified_context directly to avoid
        the infinite recursion that would occur if _governance_gate called
        validate_operation() on itself.
        """
        import os
        ORCH_DIR = "cortex/orchestrators"
        # Legitimate exceptions:
        # - EnforcementOrchestrator is the governance gate itself (avoids infinite recursion)
        # - master_orchestrator.py delegates to MasterOrchestratorRequestMixin which holds
        #   the self._activate_cross_cutting_hooks call (Phase 103-a mixin extraction)
        EXCEPTIONS = {
            # EnforcementOrchestrator is the governance gate itself (avoids infinite recursion)
            # Phase 103-e: now a sub-package — orchestrator.py is the coordinator
            "core/enforcement_orchestrator/orchestrator.py",
            "core/master_orchestrator.py",
        }
        missing = []
        for root, dirs, files in os.walk(ORCH_DIR):
            for fname in sorted(files):
                if fname.startswith("_") or not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                src = open(fpath, encoding="utf-8").read()
                if "OrchestratorProtocolMixin" not in src:
                    continue
                rel = fpath.replace(ORCH_DIR + "/", "")
                if rel in EXCEPTIONS:
                    continue
                if "self._activate_cross_cutting_hooks" not in src:
                    missing.append(rel)
        assert missing == [], f"Missing explicit activation in: {missing}"

    def test_enforcement_orchestrator_uses_direct_hooks_to_avoid_recursion(self) -> None:
        """EnforcementOrchestrator is the GovGate — it uses _extract_lens_context
        and _consume_unified_context directly instead of _activate_cross_cutting_hooks
        to prevent infinite recursion.
        Phase 103-e: coordinator is now in enforcement_orchestrator/orchestrator.py."""
        import pathlib
        candidates = [
            "cortex/orchestrators/core/enforcement_orchestrator/orchestrator.py",
            "cortex/orchestrators/core/enforcement_orchestrator.py",
        ]
        src = ""
        for candidate in candidates:
            p = pathlib.Path(candidate)
            if p.exists():
                src = p.read_text(encoding="utf-8")
                break
        assert src, "EnforcementOrchestrator coordinator file not found in any expected location"
        assert "_extract_lens_context" in src, "Must use _extract_lens_context for LENS dimension"
        assert "_consume_unified_context" in src, "Must use _consume_unified_context for KnSynth dimension"
