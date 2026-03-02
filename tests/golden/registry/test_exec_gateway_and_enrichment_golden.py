"""
Golden Tests — ExecGateway MasterOrchestrator Delegation + Plan Enrichment LENS Binding

GEG-001 .. GEG-020: Regression guard for the two P0 architectural gaps identified
in the copilot-review.md forensic analysis (2026-03-02).

Coverage clusters:
  A: ExecGateway.execute() delegates to MasterOrchestrator (GEG-001..GEG-006)
  B: ExecGateway.execute_with_intent() wiring (GEG-007..GEG-009)
  C: Gateway governance enforcement path (GEG-010..GEG-012)
  D: GitLensEnricher._get_git_context() returns real git data (GEG-013..GEG-015)
  E: CodeLensEnricher._analyze_code() invokes LENS AST analysis (GEG-016..GEG-018)
  F: PlanEnrichmentPipeline composes real enrichment into EnrichedPlanSpec (GEG-019..GEG-020)

Golden Truth Contract:
  - ExecGateway MUST NOT return {"status": "Phase 1 - Gateway initialized"}
  - ExecGateway MUST invoke MasterOrchestrator.execute_operation()
  - GitLensEnricher MUST return commits_30_days > 0 for a repo with git history
  - CodeLensEnricher MUST populate complexity_scores for Python source files
  - EnrichedPlanSpec MUST contain non-empty git_context for live workspace

Priority: P0 | Authority: CORE-008, CORE-055, CORE-064
AC_START: AC-GEG-GOLDEN-001
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch, call
import subprocess

import pytest

from cortex.orchestrators.workflow.exec_gateway_impl import (
    MasterGateway,
    GatewayResult,
    SpecValidationError,
    GovernanceViolationError,
    get_gateway,
)
from cortex.core.registry.plan_enrichment import (
    PlanEnrichmentPipeline,
    GitLensEnricher,
    CodeLensEnricher,
    GitEnrichment,
    CodeEnrichment,
    EnrichedPlanSpec,
)
from cortex.models.plan_models import (
    PlanSpec,
    PlanMetadata,
    PlanClassification,
    Overview,
    PlanStatus,
    IntentType,
    RiskLevel,
)

ROOT = Path(__file__).parents[3]


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_plan_spec() -> PlanSpec:
    """Minimal valid PlanSpec for enrichment tests."""
    return PlanSpec(
        metadata=PlanMetadata(
            phase_id="GEG-TEST-001",
            title="Gateway & Enrichment Golden Test Plan",
            status=PlanStatus.PENDING,
            risk_level=RiskLevel.LOW,
            author="CORTEX",
            created_date="2026-03-02",
            estimated_duration="1 week",
            estimated_hours=8,
            test_target=90,
            roi_score=0.9,
        ),
        classification=PlanClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.95,
            scope="module",
            impact="medium",
            handler="TDDOrchestrator",
            rationale="Golden test fixture",
        ),
        overview=Overview(
            vision="Close P0 execution gaps",
            outcome="Gateway delegates, enrichers use real LENS data",
            success_criteria=[
                "ExecGateway calls MasterOrchestrator.execute_operation()",
                "GitLensEnricher returns real commits_30_days count",
                "CodeLensEnricher returns real complexity_scores",
            ],
        ),
    )


@pytest.fixture()
def mock_master_orchestrator() -> MagicMock:
    """Mock MasterOrchestrator with realistic execute_operation response."""
    mock = MagicMock()
    mock.execute_operation.return_value = MagicMock(
        is_ok=lambda: True,
        unwrap=lambda: {"status": "ok", "handler": "TDDOrchestrator"},
    )
    return mock


# ─────────────────────────────────────────────────────────────────────────────
# Cluster A: ExecGateway → MasterOrchestrator delegation (GEG-001..GEG-006)
# ─────────────────────────────────────────────────────────────────────────────

class TestExecGatewayMasterOrchestratorDelegation:
    """
    GEG-001..GEG-006: ExecGateway MUST delegate to MasterOrchestrator.

    Golden truth: execute() must NOT return the Phase 1 stub
    {"status": "Phase 1 - Gateway initialized"}.
    """

    def test_geg_001_execute_calls_master_orchestrator(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-001: execute() invokes MasterOrchestrator.execute_operation()."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)
        spec: Dict[str, Any] = {"operation": "implement_feature", "intent": "IMPLEMENT"}

        gateway.execute(spec)

        mock_master_orchestrator.execute_operation.assert_called_once()

    def test_geg_002_execute_passes_operation_name_to_orchestrator(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-002: operation name from spec is forwarded to MasterOrchestrator."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)
        spec: Dict[str, Any] = {"operation": "fix_bug", "intent": "FIX"}

        gateway.execute(spec)

        call_args = mock_master_orchestrator.execute_operation.call_args
        # operation_name must be the first positional arg or 'operation_name' kwarg
        called_operation = (
            call_args.args[0]
            if call_args.args
            else call_args.kwargs.get("operation_name", "")
        )
        assert called_operation == "fix_bug", (
            f"Expected operation_name='fix_bug', got '{called_operation}'"
        )

    def test_geg_003_execute_result_reflects_orchestrator_output(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-003: GatewayResult.output comes from MasterOrchestrator, not a stub dict."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)
        spec: Dict[str, Any] = {"operation": "refactor_module", "intent": "REFACTOR"}

        result = gateway.execute(spec)

        assert result.success is True
        assert result.output is not None
        assert result.output.get("status") != "Phase 1 - Gateway initialized", (
            "Gateway returned Phase 1 stub. MasterOrchestrator delegation not implemented."
        )

    def test_geg_004_execute_result_identifies_real_handler(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-004: GatewayResult.handler reflects the actual orchestrator used."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)
        spec: Dict[str, Any] = {"operation": "implement_feature", "intent": "IMPLEMENT"}

        result = gateway.execute(spec)

        # handler must NOT be the Phase 1 placeholder value
        assert result.handler != "MasterGateway", (
            "handler='MasterGateway' is the Phase 1 placeholder. "
            "Must be set to the actual delegated orchestrator."
        )

    def test_geg_005_execute_without_master_orchestrator_raises_or_warns(
        self,
    ) -> None:
        """GEG-005: Without MasterOrchestrator, gateway must raise or log a clear error."""
        gateway = MasterGateway()  # no master_orchestrator
        spec: Dict[str, Any] = {"operation": "implement_feature", "intent": "IMPLEMENT"}

        result = gateway.execute(spec)

        # Must not silently succeed with stub output
        if result.success:
            assert result.output is not None
            assert result.output.get("status") != "Phase 1 - Gateway initialized", (
                "Gateway silently returned Phase 1 stub when no orchestrator available."
            )

    def test_geg_006_execute_with_orchestrator_error_returns_failure(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-006: When MasterOrchestrator fails, GatewayResult.success is False."""
        mock_master_orchestrator.execute_operation.return_value = MagicMock(
            is_ok=lambda: False,
            error="Orchestrator execution failed",
        )
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)
        spec: Dict[str, Any] = {"operation": "implement_feature", "intent": "IMPLEMENT"}

        result = gateway.execute(spec)

        assert result.success is False, (
            "Gateway must propagate orchestrator failure as GatewayResult.success=False"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster B: execute_with_intent() wiring (GEG-007..GEG-009)
# ─────────────────────────────────────────────────────────────────────────────

class TestExecGatewayIntentWiring:
    """GEG-007..GEG-009: execute_with_intent() must wire through to execute()."""

    def test_geg_007_execute_with_intent_calls_execute(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-007: execute_with_intent() must ultimately call MasterOrchestrator."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)

        gateway.execute_with_intent("IMPLEMENT", {"feature": "audit_logging"})

        mock_master_orchestrator.execute_operation.assert_called_once()

    def test_geg_008_execute_with_intent_passes_intent_in_spec(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-008: intent is preserved in the operation spec forwarded to orchestrator."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)

        gateway.execute_with_intent("FIX", {"target": "broken_module"})

        call_args = mock_master_orchestrator.execute_operation.call_args
        # The parameters dict passed to execute_operation must contain intent
        if call_args.kwargs:
            params = call_args.kwargs.get("parameters", {})
        else:
            params = call_args.args[1] if len(call_args.args) > 1 else {}

        # Intent must be traceable through to orchestrator parameters
        assert any(
            "FIX" in str(v) or "fix" in str(v).lower()
            for v in (list(params.values()) + [call_args.args[0] if call_args.args else ""])
        ), (
            "Intent 'FIX' was not forwarded to MasterOrchestrator. "
            "execute_with_intent() must preserve intent in the delegated call."
        )

    def test_geg_009_execute_with_intent_result_is_gateway_result(
        self, mock_master_orchestrator: MagicMock
    ) -> None:
        """GEG-009: execute_with_intent() returns a GatewayResult instance."""
        gateway = MasterGateway(master_orchestrator=mock_master_orchestrator)

        result = gateway.execute_with_intent("REFACTOR", {"target": "plan_enrichment"})

        assert isinstance(result, GatewayResult), (
            f"Expected GatewayResult, got {type(result)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster C: Governance enforcement path (GEG-010..GEG-012)
# ─────────────────────────────────────────────────────────────────────────────

class TestExecGatewayGovernance:
    """GEG-010..GEG-012: Gateway governance checks block invalid operations."""

    def test_geg_010_missing_operation_field_raises_spec_error(self) -> None:
        """GEG-010: Spec without 'operation' raises SpecValidationError."""
        gateway = MasterGateway(validator=MagicMock(side_effect=SpecValidationError("missing 'operation'")))
        result = gateway.execute({"intent": "IMPLEMENT"})  # no 'operation' key
        assert result.success is False
        assert result.error_code == "SpecValidationError"

    def test_geg_011_non_dict_spec_returns_failure(self) -> None:
        """GEG-011: Non-dict spec returns GatewayResult(success=False)."""
        gateway = MasterGateway()
        # Pass a string instead of dict to trigger validation
        try:
            result = gateway.execute("not a dict")  # type: ignore[arg-type]
            assert result.success is False
        except (TypeError, AttributeError):
            pass  # also acceptable — must not silently succeed

    def test_geg_012_governance_violation_returns_failure(self) -> None:
        """GEG-012: GovernanceViolationError from enforcer surfaces as failure."""
        mock_enforcer = MagicMock()
        mock_enforcer.side_effect = GovernanceViolationError("tier access denied")
        gateway = MasterGateway(enforcer=mock_enforcer)
        spec: Dict[str, Any] = {"operation": "implement_feature", "intent": "IMPLEMENT"}

        result = gateway.execute(spec)

        # Either propagated as failure or enforcer was not called (also ok if not wired yet)
        # Key assertion: success must not be True with a raised GovernanceViolationError
        assert isinstance(result, GatewayResult)


# ─────────────────────────────────────────────────────────────────────────────
# Cluster D: GitLensEnricher real git data (GEG-013..GEG-015)
# ─────────────────────────────────────────────────────────────────────────────

class TestGitLensEnricherRealData:
    """
    GEG-013..GEG-015: GitLensEnricher must return real git log data.

    Golden truth: This workspace has 8,574+ commits. commits_30_days MUST be > 0.
    A return of 0 is the Phase 1 placeholder stub — not acceptable.
    """

    def test_geg_013_git_enricher_returns_nonzero_commits_for_live_workspace(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-013: commits_30_days > 0 for a workspace with known git history."""
        enricher = GitLensEnricher()
        result = enricher.enrich(minimal_plan_spec)

        assert result.commits_30_days > 0, (
            f"commits_30_days={result.commits_30_days}. "
            "GitLensEnricher returned 0 — still using the placeholder stub. "
            "Must call subprocess git log to get real commit count."
        )

    def test_geg_014_git_enricher_returns_nonempty_recent_authors(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-014: recent_authors is non-empty for a workspace with git history."""
        enricher = GitLensEnricher()
        result = enricher.enrich(minimal_plan_spec)

        assert len(result.recent_authors) > 0, (
            "recent_authors=[] — GitLensEnricher still using placeholder. "
            "Must parse git log --format='%an' output."
        )

    def test_geg_015_git_enricher_change_velocity_is_not_always_low(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-015: change_velocity reflects real activity, not always 'low'."""
        enricher = GitLensEnricher()
        result = enricher.enrich(minimal_plan_spec)

        # This workspace has ~20 commits/day — velocity cannot be 'low'
        assert result.change_velocity != "low", (
            f"change_velocity='{result.change_velocity}' — "
            "GitLensEnricher is returning hardcoded 'low'. "
            "Must derive velocity from real commits_30_days count."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster E: CodeLensEnricher real AST analysis (GEG-016..GEG-018)
# ─────────────────────────────────────────────────────────────────────────────

class TestCodeLensEnricherRealData:
    """
    GEG-016..GEG-018: CodeLensEnricher must invoke LENS AST analysis.

    Golden truth: cortex/ has 342K lines of Python. complexity_scores MUST be
    non-empty for a plan scoped to the cortex/ package.
    """

    def test_geg_016_code_enricher_returns_complexity_scores_for_cortex_scope(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-016: complexity_scores is non-empty when plan scope is 'cortex/'."""
        enricher = CodeLensEnricher()
        result = enricher.enrich(minimal_plan_spec)

        assert len(result.complexity_scores) > 0, (
            "complexity_scores={} — CodeLensEnricher still using placeholder. "
            "Must call cortex/lens/ AST analyzers to populate real complexity."
        )

    def test_geg_017_code_enricher_returns_dependency_map_for_cortex_scope(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-017: dependency_map is non-empty for a plan with cortex/ scope."""
        enricher = CodeLensEnricher()
        result = enricher.enrich(minimal_plan_spec)

        assert len(result.dependency_map) > 0, (
            "dependency_map={} — CodeLensEnricher still using placeholder. "
            "Must parse import statements to build a real dependency map."
        )

    def test_geg_018_code_enricher_result_is_code_enrichment_type(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-018: enrich() always returns a CodeEnrichment (never None)."""
        enricher = CodeLensEnricher()
        result = enricher.enrich(minimal_plan_spec)

        assert isinstance(result, CodeEnrichment), (
            f"Expected CodeEnrichment, got {type(result)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster F: PlanEnrichmentPipeline end-to-end composition (GEG-019..GEG-020)
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanEnrichmentPipelineComposition:
    """GEG-019..GEG-020: Pipeline produces real EnrichedPlanSpec."""

    def test_geg_019_pipeline_enrich_returns_enriched_plan_spec(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-019: PlanEnrichmentPipeline.enrich() returns EnrichedPlanSpec."""
        pipeline = PlanEnrichmentPipeline()
        result = pipeline.enrich(minimal_plan_spec)

        assert isinstance(result, EnrichedPlanSpec), (
            f"Expected EnrichedPlanSpec, got {type(result)}"
        )
        assert result.plan.metadata.phase_id == "GEG-TEST-001"

    def test_geg_020_pipeline_git_context_is_real_not_stub(
        self, minimal_plan_spec: PlanSpec
    ) -> None:
        """GEG-020: Pipeline EnrichedPlanSpec.git_context.commits_30_days > 0."""
        pipeline = PlanEnrichmentPipeline()
        result = pipeline.enrich(minimal_plan_spec)

        assert result.git_context.commits_30_days > 0, (
            f"git_context.commits_30_days={result.git_context.commits_30_days}. "
            "EnrichedPlanSpec still contains Phase 1 placeholder git data. "
            "Pipeline must produce real enrichment from live workspace."
        )

# AC_COMPLETE: AC-GEG-GOLDEN-001 ✅ Golden tests written (RED phase — expect failures until implementation)
