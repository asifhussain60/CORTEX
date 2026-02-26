"""Preflight: Orchestrator import + health_check wiring tests.

Validates key wired orchestrators are importable and expose health_check().
Each test is < 50ms — pure import + attribute check, no execution.

Tier: T0 (preflight) — runs in < 10s parallel.
"""
import pytest


# ── Core Orchestrators ─────────────────────────────────────────────────────

class TestCoreOrchestratorImports:
    """Validate core tier orchestrator imports."""

    def test_master_orchestrator_importable(self) -> None:
        """MasterOrchestrator — the top-level coordinator."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        assert hasattr(MasterOrchestrator, "health_check")

    def test_intent_router_importable(self) -> None:
        """IntentRouter — classifies user intent."""
        from cortex.orchestrators.core.intent_router import IntentRouter
        assert IntentRouter is not None

    def test_tdd_orchestrator_importable(self) -> None:
        """TDDOrchestrator — RED/GREEN/REFACTOR cycles."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "health_check")

    def test_enforcement_orchestrator_importable(self) -> None:
        """EnforcementOrchestrator — CORE rule enforcement."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
        assert hasattr(EnforcementOrchestrator, "health_check")

    def test_request_rephrase_orchestrator_importable(self) -> None:
        """RequestRephraseOrchestrator — Stage 0 governance."""
        from cortex.orchestrators.core.request_rephrase_orchestrator import RequestRephraseOrchestrator
        assert RequestRephraseOrchestrator is not None

    def test_conversation_orchestrator_importable(self) -> None:
        """ConversationOrchestrator — low-confidence routing."""
        from cortex.orchestrators.core.conversation_orchestrator import ConversationOrchestrator
        assert ConversationOrchestrator is not None


# ── Domain Orchestrators ───────────────────────────────────────────────────

class TestDomainOrchestratorImports:
    """Validate domain tier orchestrator imports."""

    def test_refactoring_orchestrator_importable(self) -> None:
        """RefactoringOrchestrator — safe code improvement."""
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
        assert hasattr(RefactoringOrchestrator, "health_check")

    def test_sdlc_workflow_orchestrator_importable(self) -> None:
        """SDLCWorkflowOrchestrator — software lifecycle."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import SDLCWorkflowOrchestrator
        assert SDLCWorkflowOrchestrator is not None

    def test_planning_orchestrator_importable(self) -> None:
        """PlanningOrchestrator — phase-based roadmaps."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
        assert PlanningOrchestrator is not None

    def test_inquiry_orchestrator_importable(self) -> None:
        """InquiryOrchestrator — query handling."""
        from cortex.orchestrators.domain.inquiry_orchestrator import InquiryOrchestrator
        assert InquiryOrchestrator is not None

    def test_dashboard_orchestrator_importable(self) -> None:
        """DashboardOrchestrator — dashboard management."""
        from cortex.orchestrators.domain.dashboard_orchestrator import DashboardOrchestrator
        assert DashboardOrchestrator is not None


# ── Support Orchestrators ──────────────────────────────────────────────────

class TestSupportOrchestratorImports:
    """Validate support tier orchestrator imports."""

    def test_health_orchestrator_importable(self) -> None:
        """HealthOrchestrator — orchestrator health checks."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        assert hasattr(HealthOrchestrator, "health_check")

    def test_vacuum_orchestrator_importable(self) -> None:
        """VacuumOrchestrator — markdown sprawl cleanup."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        assert hasattr(VacuumOrchestrator, "health_check")

    def test_upgrade_orchestrator_importable(self) -> None:
        """UpgradeOrchestrator — inflight upgrade protocol."""
        from cortex.orchestrators.support.upgrade_orchestrator import UpgradeOrchestrator
        assert UpgradeOrchestrator is not None

    def test_bulk_digest_orchestrator_importable(self) -> None:
        """BulkDigestOrchestrator — content ingestion."""
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        assert BulkDigestOrchestrator is not None

    def test_sweep_catalogue_orchestrator_importable(self) -> None:
        """SweepCatalogueOrchestrator — CORE-064 sweep tracking."""
        from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepCatalogueOrchestrator
        assert SweepCatalogueOrchestrator is not None

    def test_debugger_orchestrator_importable(self) -> None:
        """DebuggerOrchestrator — debug mode."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert DebuggerOrchestrator is not None

    def test_landing_page_generator_importable(self) -> None:
        """LandingPageGenerator — dashboard landing pages."""
        from cortex.orchestrators.support.landing_page_generator import LandingPageGenerator
        assert LandingPageGenerator is not None
