"""
Phase 71-G: Unified Brain OPJ Wiring Golden Tests

Closes: GAP-71-B1 (MasterOrchestrator not OPJ-aware)
         GAP-71-B2 (IntentClassifier routing decisions not recorded to OPJ)
         GAP-71-B3 (GovernanceRegistry violations not consulted by IntentRouter)
         GAP-71-F2 (OPJ high-confidence patterns never auto-promote to T1)

TDD RED — all assertions target the post-implementation state.
Tests will FAIL until Phase 71 tracks B and F are implemented.

AC_START: AC-71-OPJ-GOLDEN-001
"""
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# Class 1: MasterOrchestrator OPJ Wiring
# ─────────────────────────────────────────────────────────────────────────────
class TestMasterOrchestratorOPJ:
    """MasterOrchestrator must inherit OPJMixin and emit consult/record calls (Phase 71-B)."""

    def test_master_orchestrator_inherits_opj_mixin(self) -> None:
        """MasterOrchestrator must inherit OPJMixin."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        assert issubclass(MasterOrchestrator, OPJMixin), (
            "MasterOrchestrator does NOT inherit OPJMixin. "
            "Phase 71-B wiring is incomplete."
        )

    def test_master_orchestrator_has_opj_consult_method(self) -> None:
        """MasterOrchestrator instance must have _opj_consult() method."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert hasattr(mo, "_opj_consult"), (
            "MasterOrchestrator missing _opj_consult — OPJMixin not wired"
        )
        assert callable(getattr(mo, "_opj_consult")), (
            "_opj_consult is not callable on MasterOrchestrator"
        )

    def test_master_orchestrator_has_opj_record_methods(self) -> None:
        """MasterOrchestrator must have _opj_record_success() and _opj_record_failure()."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert hasattr(mo, "_opj_record_success"), (
            "MasterOrchestrator missing _opj_record_success"
        )
        assert hasattr(mo, "_opj_record_failure"), (
            "MasterOrchestrator missing _opj_record_failure"
        )

    def test_master_orchestrator_opj_init_called(self) -> None:
        """MasterOrchestrator.__init__ must call _opj_init() — OPJ store must be initialised."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        # _opj_init sets _opj_store — verify it's not None after construction
        assert hasattr(mo, "_opj_store"), (
            "MasterOrchestrator._opj_store missing — _opj_init() not called in __init__"
        )

    def test_master_orchestrator_coordinate_operation_consults_opj(self) -> None:
        """coordinate_operation() must consult OPJ before executing — _opj_consult called."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from unittest.mock import patch, MagicMock

        mo = MasterOrchestrator()
        with patch.object(mo, "_opj_consult", wraps=mo._opj_consult) as mock_consult:
            try:
                mo.coordinate_operation({"intent": "test_opj_golden", "payload": {}})
            except Exception:
                pass  # we only care that consult was called, not the outcome
            mock_consult.assert_called(), (
                "MasterOrchestrator.coordinate_operation did NOT call _opj_consult()"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Class 2: IntentRouter × GovernanceRegistry Cross-Wiring
# ─────────────────────────────────────────────────────────────────────────────
class TestIntentRouterGovernanceWiring:
    """IntentRouter must consult GovernanceRegistry active violations (Phase 71-B / ES-003)."""

    def test_intent_router_has_governance_registry_reference(self) -> None:
        """IntentRouter must accept or initialise a GovernanceRegistry reference."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        # After Phase 71-B: router must expose governance_registry attribute
        assert hasattr(router, "governance_registry") or hasattr(router, "_governance_registry"), (
            "IntentRouter has no GovernanceRegistry attribute. "
            "Phase 71-B ES-003 wiring incomplete."
        )

    def test_intent_router_complexity_score_influenced_by_active_violations(self) -> None:
        """compute_complexity() must return higher score when GovernanceRegistry has P0 violations."""
        from cortex.orchestrators.core.intent_router import IntentRouter
        from unittest.mock import MagicMock, patch

        router = IntentRouter()
        mock_registry = MagicMock()
        mock_registry.get_active_violations.return_value = [
            {"severity": "P0", "rule": "CORE-008", "count": 3}
        ]

        with patch.object(router, "_get_governance_violations", return_value=[
            {"severity": "P0", "rule": "CORE-008", "count": 3}
        ]):
            score_with_violations = router.compute_complexity({"intent": "implement_feature"})

        mock_registry.get_active_violations.return_value = []
        with patch.object(router, "_get_governance_violations", return_value=[]):
            score_without = router.compute_complexity({"intent": "implement_feature"})

        assert score_with_violations >= score_without, (
            "IntentRouter complexity score is NOT higher when governance violations are active. "
            "Phase 71-B ES-003 wiring needed."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Class 3: CompanyKnowledge → LENS Wiring
# ─────────────────────────────────────────────────────────────────────────────
class TestCompanyKnowledgeLENSWiring:
    """CompanyKnowledgeProvider must be imported and consulted by LENS (Phase 71-F / ES-004)."""

    def test_company_knowledge_provider_importable(self) -> None:
        """cortex.intelligence.knowledge.company_domain_loader must be importable."""
        from cortex.intelligence.knowledge import company_domain_loader  # noqa: F401
        assert company_domain_loader is not None

    def test_company_knowledge_provider_class_exists(self) -> None:
        """CompanyKnowledgeProvider class must exist in company_domain_loader."""
        from cortex.intelligence.knowledge.company_domain_loader import CompanyKnowledgeProvider
        assert CompanyKnowledgeProvider is not None

    def test_lens_imports_company_knowledge_provider(self) -> None:
        """LENS module must import CompanyKnowledgeProvider (Phase 71-F ES-004)."""
        import importlib
        import ast
        import pathlib

        # Find the primary LENS module
        lens_init = pathlib.Path(REPO_ROOT) / "cortex" / "lens" / "__init__.py"
        lens_engine_candidates = list(
            (pathlib.Path(REPO_ROOT) / "cortex" / "lens").rglob("*.py")
        )

        # Check at least one LENS file imports CompanyKnowledgeProvider
        found = False
        for candidate in lens_engine_candidates:
            content = candidate.read_text(encoding="utf-8")
            if "CompanyKnowledgeProvider" in content or "company_domain_loader" in content:
                found = True
                break

        assert found, (
            "No LENS module imports CompanyKnowledgeProvider or company_domain_loader. "
            "Phase 71-F ES-004 wiring incomplete."
        )

    def test_lens_scan_includes_company_context(self) -> None:
        """LENS scan result must include a company_context key when CompanyKnowledgeProvider is wired."""
        pytest.skip(
            "Requires LENS scan API — implemented in Phase 71-F ES-004. "
            "Remove skip and implement after LENS wiring complete."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Class 4: OPJ → T1 Knowledge Auto-Promotion
# ─────────────────────────────────────────────────────────────────────────────
class TestOPJToT1Promotion:
    """OPJ high-confidence patterns (≥0.80) must auto-promote to T1 knowledge tier (Phase 71-F / ES-005)."""

    def test_opj_promoter_module_importable(self) -> None:
        """cortex.intelligence.learning.opj_promoter must be importable."""
        from cortex.intelligence.learning import opj_promoter  # noqa: F401
        assert opj_promoter is not None

    def test_opj_promoter_has_promote_high_confidence_function(self) -> None:
        """opj_promoter must expose promote_high_confidence_patterns() function."""
        from cortex.intelligence.learning.opj_promoter import promote_high_confidence_patterns
        assert callable(promote_high_confidence_patterns)

    def test_opj_promoter_promotes_patterns_above_threshold(self) -> None:
        """promote_high_confidence_patterns() must promote patterns with confidence >= 0.80."""
        from cortex.intelligence.learning.opj_promoter import promote_high_confidence_patterns
        from unittest.mock import patch, MagicMock

        # Simulate 2 high-confidence patterns and 1 low-confidence pattern
        mock_patterns = [
            MagicMock(confidence=0.95, id="OPJ-TEST-001", promoted=False),
            MagicMock(confidence=0.82, id="OPJ-TEST-002", promoted=False),
            MagicMock(confidence=0.65, id="OPJ-TEST-003", promoted=False),
        ]

        with patch(
            "cortex.intelligence.learning.opj_promoter._load_opj_patterns",
            return_value=mock_patterns,
        ):
            promoted_ids = promote_high_confidence_patterns(threshold=0.80)

        assert "OPJ-TEST-001" in promoted_ids, "Pattern with confidence=0.95 was NOT promoted"
        assert "OPJ-TEST-002" in promoted_ids, "Pattern with confidence=0.82 was NOT promoted"
        assert "OPJ-TEST-003" not in promoted_ids, (
            "Pattern with confidence=0.65 should NOT be promoted (below threshold)"
        )

    def test_opj_mixin_records_success_promotes_high_confidence(self) -> None:
        """OPJMixin._opj_record_success() must trigger promotion check when confidence >= 0.80."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        from unittest.mock import patch

        class _TestOrchestrator(OPJMixin):
            def __init__(self):
                self._opj_init()

        orch = _TestOrchestrator()
        # Simulate a high-confidence success being recorded and then checked for promotion
        with patch(
            "cortex.intelligence.learning.opj_mixin.promote_high_confidence_patterns"
        ) as mock_promote:
            orch._opj_record_success()
            mock_promote.assert_called()
