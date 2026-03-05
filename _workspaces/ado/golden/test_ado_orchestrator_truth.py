"""
Golden Truth Tests: ADO Orchestrator Layer
══════════════════════════════════════════════════════════════════════════════

Purpose:
    Verify ADOOrchestrator satisfies OrchestratorBase lifecycle,
    governance gates block invalid inputs, mode dispatch is correct,
    and ADOResult carries the expected output structure.

    These tests cover Layer 2 of the ADO integration.
    ALL 15 TESTS MUST FAIL (RED) before implementation begins (CORE-008).

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider (ADO implementation)

AC-IDs: AC-ADO-O-001 through AC-ADO-O-015
Golden count target: 15 tests
"""

from __future__ import annotations

import pytest
from dataclasses import fields


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-O-001, AC-ADO-O-002 — Importability + inheritance
# ──────────────────────────────────────────────────────────────────────────────

class TestADOOrchestratorImport:
    """ADOOrchestrator must import from canonical path and inherit OrchestratorBase."""

    def test_ado_orchestrator_importable_from_canonical_path(self):
        """
        AC-ADO-O-001: ADOOrchestrator must import from cortex.repositories.ado.ado_orchestrator.

        RED: ImportError if module not present.
        GREEN: Class is importable and not None.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        assert ADOOrchestrator is not None

    def test_ado_orchestrator_inherits_orchestrator_base(self):
        """
        AC-ADO-O-002: ADOOrchestrator must be a subclass of OrchestratorBase.

        RED: Not a subclass if class definition omits OrchestratorBase.
        GREEN: issubclass check passes.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        from cortex.core.orchestrator_base import OrchestratorBase

        assert issubclass(ADOOrchestrator, OrchestratorBase), (
            "ADOOrchestrator must inherit from cortex.core.orchestrator_base.OrchestratorBase"
        )

    def test_orchestrator_id_set_to_ado_orchestrator(self):
        """
        AC-ADO-O-003: orchestrator_id must be 'ado_orchestrator' for audit trail.

        RED: orchestrator_id is wrong string or not set.
        GREEN: orch.orchestrator_id == 'ado_orchestrator'.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(story_id=692945, mode="fetch_story")
        assert orch.orchestrator_id == "ado_orchestrator"


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-O-004 — ADOResult dataclass shape
# ──────────────────────────────────────────────────────────────────────────────

class TestADOResultShape:
    """ADOResult dataclass must have all required fields."""

    def test_ado_result_dataclass_has_required_fields(self):
        """
        AC-ADO-O-004: ADOResult must have mode, story, stories, healthy, errors, metadata.

        RED: Missing fields if dataclass definition is incomplete.
        GREEN: All 6 required fields present.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOResult

        field_names = {f.name for f in fields(ADOResult)}
        required = {"mode", "story", "stories", "healthy", "errors", "metadata"}
        missing = required - field_names
        assert not missing, f"ADOResult missing fields: {missing}"

    def test_ado_result_stories_defaults_to_empty_list(self):
        """
        AC-ADO-O-005: ADOResult.stories must default to [] (never None).

        RED: Default is None if field_default is missing.
        GREEN: stories=[] on construction.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOResult
        result = ADOResult(mode="fetch_story")
        assert result.stories == []
        assert result.errors == []


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-O-006 through AC-ADO-O-010 — Governance gate correctness
# ──────────────────────────────────────────────────────────────────────────────

class TestADOOrchestratorGovernance:
    """govern() must block all invalid inputs and pass all valid ones."""

    def test_govern_blocks_negative_story_id(self):
        """
        AC-ADO-O-006: govern() must block negative story_id.

        RED: GovernanceDecision.allowed=True if validation not implemented.
        GREEN: allowed=False with descriptive reason.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(story_id=-1, mode="fetch_story")
        decision = orch.govern()
        assert not decision.allowed, "Negative story_id must be rejected by governance"
        assert decision.violations, "Must include violation message"

    def test_govern_blocks_zero_story_id(self):
        """
        AC-ADO-O-007: govern() must block story_id=0.

        RED: GovernanceDecision.allowed=True if 0 is not excluded.
        GREEN: allowed=False.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(story_id=0, mode="fetch_story")
        decision = orch.govern()
        assert not decision.allowed

    def test_govern_blocks_none_story_id_for_single_story_modes(self):
        """
        AC-ADO-O-008: govern() must block story_id=None for single-story modes.

        RED: allowed=True if None not validated.
        GREEN: allowed=False with violation about story_id being required.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(story_id=None, mode="fetch_story")
        decision = orch.govern()
        assert not decision.allowed

    def test_govern_passes_valid_story_id(self):
        """
        AC-ADO-O-009: govern() must pass when story_id is a positive integer.

        RED: allowed=False if governance is overly restrictive.
        GREEN: allowed=True for story_id=692945.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(story_id=692945, mode="fetch_story")
        decision = orch.govern()
        assert decision.allowed, (
            f"Governance blocked valid story_id=692945. "
            f"Violations: {decision.violations}"
        )

    def test_govern_blocks_fetch_bulk_with_empty_project(self):
        """
        AC-ADO-O-010: govern() must block fetch_bulk mode when project is empty string.

        RED: allowed=True if project validation not implemented.
        GREEN: allowed=False — project is required for bulk fetches.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(mode="fetch_bulk", project="")
        decision = orch.govern()
        assert not decision.allowed

    def test_govern_blocks_unknown_filter_keys_in_fetch_bulk(self):
        """
        AC-ADO-O-011: govern() must block unrecognised filter keys for fetch_bulk.

        RED: allowed=True if filter key validation not implemented.
        GREEN: allowed=False — "team" is not in ALLOWED_FILTERS.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(
            mode="fetch_bulk",
            project="V5",
            filters={"team": "Authentication"},  # 'team' is not an allowed filter
        )
        decision = orch.govern()
        assert not decision.allowed

    def test_govern_blocks_search_wiql_not_starting_with_select(self):
        """
        AC-ADO-O-012: govern() must block WIQL queries that don't start with SELECT.

        RED: allowed=True if inject-guard not implemented.
        GREEN: allowed=False — basic WIQL injection guard.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(
            mode="search_wiql",
            project="V5",
            wiql="DROP TABLE WorkItems",  # Injection attempt
        )
        decision = orch.govern()
        assert not decision.allowed


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-O-013, AC-ADO-O-014 — execute() return type
# ──────────────────────────────────────────────────────────────────────────────

class TestADOOrchestratorExecute:
    """execute() must return ExecutionResult with correct structure."""

    def test_execute_returns_execution_result_type(self, ado_orchestrator_fetch_story):
        """
        AC-ADO-O-013: execute() must return an ExecutionResult instance.

        RED: Returns wrong type or raises Exception.
        GREEN: isinstance(result, ExecutionResult) is True.
        """
        from cortex.core.orchestrator_base import ExecutionResult
        result = ado_orchestrator_fetch_story.execute()
        assert isinstance(result, ExecutionResult), (
            f"execute() must return ExecutionResult, got {type(result)}"
        )

    def test_execute_health_check_mode_sets_healthy_key_in_output(self):
        """
        AC-ADO-O-014: execute() in health_check mode must include 'healthy' in output dict.

        RED: 'healthy' key absent from result.output.
        GREEN: result.output["healthy"] is a bool.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        orch = ADOOrchestrator(mode="health_check")
        result = orch.execute()
        assert "healthy" in result.output, (
            "health_check mode must populate result.output['healthy'] with a bool"
        )
        assert isinstance(result.output["healthy"], bool)

    def test_execute_fetch_story_mode_sets_story_key_in_output_on_success(
        self, ado_provider_with_mock_http
    ):
        """
        AC-ADO-O-015: execute() in fetch_story mode sets result.output['story'] on success.

        RED: 'story' key absent if dispatch not implemented.
        GREEN: result.output['story'] is a UserStoryContext.

        Provider is pre-mocked — no HTTP calls.
        """
        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
        from cortex.repositories.ado.ado_provider import UserStoryContext

        orch = ADOOrchestrator(story_id=692945, mode="fetch_story")
        orch._provider = ado_provider_with_mock_http
        result = orch.execute()
        assert result.success, f"execute() failed: {result.error}"
        assert "story" in result.output
        assert isinstance(result.output["story"], UserStoryContext)
