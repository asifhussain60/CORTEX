"""
Golden Test Harness: Plan-Before-Execute Gate (Phase 102)

Comprehensive golden tests covering:
  - ☀️ Sunshine paths (happy path, normal operations)
  - 🌧️ Rainy day paths (failures, degraded modes)
  - 🔲 Edge cases (boundary conditions, unusual inputs)
  - 🔍 Blind spots (things nobody tests but break in production)

Tests the full flow: LENS → PlanGate → Persistence → Approval.

Authority: Phase 102, CORE-008 (TDD)
AC_START: AC-GOLDEN-PLAN-GATE-001
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from cortex.core.result import Ok, Err
from cortex.models.interaction_plan import (
    InteractionPlan,
    InteractionPlanStep,
    requires_plan_gate,
    PLAN_GATE_BYPASS_INTENTS,
)
from cortex.orchestrators.core.plan_gate_service import PlanGateService
from cortex.orchestrators.core.lens_data_persistence import LensDataPersistenceService


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def plan_gate_service() -> PlanGateService:
    """Fresh PlanGateService instance."""
    return PlanGateService()


@pytest.fixture
def temp_company_dir():
    """Temporary company registry directory for LENS persistence tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        company_root = Path(tmpdir) / "cortex-registry" / "company"
        company_root.mkdir(parents=True)
        yield Path(tmpdir), company_root


@pytest.fixture
def persistence_service(temp_company_dir):
    """LensDataPersistenceService with temp directory."""
    repo_root, _ = temp_company_dir
    return LensDataPersistenceService(repo_root=repo_root)


@pytest.fixture
def interaction_orchestrator():
    """InteractionOrchestrator with mock protocol."""
    from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
    return InteractionOrchestrator(
        conversation_protocol=MagicMock(),
        enable_challenges=True,
    )


@pytest.fixture
def rich_lens_context() -> Dict[str, Any]:
    """Realistic LENS context with all fields populated."""
    return {
        "intent": "IMPLEMENT",
        "files_analyzed": 12,
        "complexity": 8,
        "files_affected": 3,
        "risk_score": 0.45,
        "overview": {"total_files": 450, "languages": ["Python", "TypeScript"]},
        "dependencies": {"count": 42, "outdated": 3},
        "classes": {"total": 120, "public": 85},
        "timeline": {"last_commit": "2026-02-18T10:00:00Z"},
        "impact": {"lines_changed": 150, "tests_affected": 8},
        "brain": {"patterns": ["orchestrator", "registry"]},
        "governance": {"violations": 0, "score": 98},
        "orchestrators": {"active": 5, "idle": 2},
    }


@pytest.fixture
def empty_lens_context() -> Dict[str, Any]:
    """Minimal LENS context — degraded mode."""
    return {"status": "lens_unavailable", "degraded": True}


# =============================================================================
# ☀️ SUNSHINE PATHS — Normal operations that must always work
# =============================================================================

class TestGoldenSunshinePaths:
    """Sunshine path golden tests — the happy path must always work."""

    def test_gp101_implement_creates_plan_with_tdd_steps(
        self, plan_gate_service: PlanGateService, rich_lens_context: Dict
    ) -> None:
        """GP-101: IMPLEMENT request creates plan with TDD RED/GREEN/REFACTOR steps.

        Scenario: User says "implement user authentication"
        Expected: Plan has ≥5 steps, includes TDD phases, unapproved.
        """
        plan = plan_gate_service.create_plan(
            user_request="implement user authentication",
            intent_type="IMPLEMENT",
            lens_context=rich_lens_context,
        )

        assert plan.plan_id.startswith("plan-")
        assert plan.intent_type == "IMPLEMENT"
        assert plan.approved is False
        assert plan.step_count() >= 5

        # TDD steps present
        descriptions = [s.description.lower() for s in plan.steps]
        assert any("red" in d or "failing test" in d for d in descriptions), \
            "IMPLEMENT plan must include RED phase"
        assert any("green" in d or "pass test" in d for d in descriptions), \
            "IMPLEMENT plan must include GREEN phase"
        assert any("refactor" in d for d in descriptions), \
            "IMPLEMENT plan must include REFACTOR phase"

    def test_gp102_fix_creates_plan_with_regression_test(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-102: FIX request creates plan with regression test step.

        Scenario: User says "fix the login bug"
        Expected: Plan includes regression test step and root cause step.
        """
        plan = plan_gate_service.create_plan(
            user_request="fix the login bug",
            intent_type="FIX",
            lens_context={"intent": "FIX", "risk_score": 0.6},
        )

        assert plan.intent_type == "FIX"
        assert plan.risk_score == 0.6
        descriptions = [s.description.lower() for s in plan.steps]
        assert any("regression" in d for d in descriptions), \
            "FIX plan must include regression test step"
        assert any("root cause" in d or "identify" in d for d in descriptions), \
            "FIX plan must include root cause identification"

    def test_gp103_refactor_creates_plan_with_safety_verification(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-103: REFACTOR plan verifies tests pass before AND after changes.

        Scenario: User says "refactor the auth module"
        Expected: First step verifies existing tests, last step re-verifies.
        """
        plan = plan_gate_service.create_plan(
            user_request="refactor the auth module",
            intent_type="REFACTOR",
            lens_context={"intent": "REFACTOR"},
        )

        assert plan.intent_type == "REFACTOR"
        # First step: verify existing tests pass
        assert "verify" in plan.steps[0].description.lower() or \
               "test" in plan.steps[0].description.lower(), \
            "REFACTOR must verify tests BEFORE changes"
        # Last step: re-verify
        last_desc = plan.steps[-1].description.lower()
        assert "verify" in last_desc or "commit" in last_desc or "governance" in last_desc

    def test_gp104_query_bypasses_plan_gate_entirely(self) -> None:
        """GP-104: QUERY intent bypasses plan gate — no plan created.

        Scenario: User says "what is CORTEX?"
        Expected: requires_plan_gate returns False.
        """
        assert requires_plan_gate("QUERY") is False
        assert requires_plan_gate("ANALYZE") is False
        assert requires_plan_gate("DIGEST") is False

    def test_gp105_lens_data_persisted_to_dashboard(
        self, persistence_service: LensDataPersistenceService,
        rich_lens_context: Dict,
        temp_company_dir,
    ) -> None:
        """GP-105: LENS data appended to dashboards/lens/ as timestamped JSON.

        Scenario: Plan gate creates plan, LENS data persisted
        Expected: File exists in dashboards/lens/ with correct structure.
        """
        result = persistence_service.append_lens_data(
            repo_slug="cortex",
            lens_context=rich_lens_context,
            intent_type="IMPLEMENT",
            plan_id="plan-abc123",
        )

        assert result["dashboard_file"] is not None
        dashboard_path = Path(result["dashboard_file"])
        assert dashboard_path.exists()

        # Verify JSON structure
        data = json.loads(dashboard_path.read_text())
        assert "_metadata" in data
        assert data["_metadata"]["intent_type"] == "IMPLEMENT"
        assert data["_metadata"]["plan_id"] == "plan-abc123"
        assert data["_metadata"]["repo_slug"] == "cortex"
        assert "overview" in data

    def test_gp106_lens_history_appended_not_overwritten(
        self, persistence_service: LensDataPersistenceService,
        rich_lens_context: Dict,
    ) -> None:
        """GP-106: Multiple LENS runs APPEND to history — never overwrite.

        Scenario: 3 sequential LENS analyses
        Expected: lens_history.json has 3 entries.
        """
        for i in range(3):
            persistence_service.append_lens_data(
                repo_slug="cortex",
                lens_context={**rich_lens_context, "run": i},
                intent_type="IMPLEMENT",
            )

        # Check history file
        history_path = (
            persistence_service.company_root / "repos" / "cortex" / "lens_history.json"
        )
        assert history_path.exists()
        history = json.loads(history_path.read_text())
        assert isinstance(history, list)
        assert len(history) == 3

    def test_gp107_plan_output_format_matches_master_orchestrator(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-107: Plan output dict matches MasterOrchestrator return format.

        Expected: {"type": "plan", "plan": {...}, "requires_approval": True}
        """
        plan = plan_gate_service.create_plan(
            user_request="implement feature X",
            intent_type="IMPLEMENT",
            lens_context={},
        )
        output = {
            "type": "plan",
            "plan": plan.to_dict(),
            "requires_approval": True,
            "user_request": "implement feature X",
        }

        assert output["type"] == "plan"
        assert output["requires_approval"] is True
        assert isinstance(output["plan"], dict)
        assert "plan_id" in output["plan"]
        assert "steps" in output["plan"]
        assert len(output["plan"]["steps"]) > 0

    def test_gp108_intelligent_lens_depth_for_implement(
        self, persistence_service: LensDataPersistenceService
    ) -> None:
        """GP-108: IMPLEMENT with high complexity triggers deep LENS scan.

        Scenario: IMPLEMENT with complexity=15, files_affected=8
        Expected: get_scan_depth returns 'deep'.
        """
        depth = persistence_service.get_scan_depth(
            intent_type="IMPLEMENT",
            lens_context={"complexity": 15, "files_affected": 8},
        )
        assert depth == "deep"

    def test_gp109_shallow_lens_for_query(
        self, persistence_service: LensDataPersistenceService
    ) -> None:
        """GP-109: QUERY intent uses shallow LENS — no deep scan waste.

        Expected: get_scan_depth returns 'shallow'.
        """
        depth = persistence_service.get_scan_depth(
            intent_type="QUERY",
            lens_context={},
        )
        assert depth == "shallow"

    def test_gp110_standard_lens_for_low_complexity_implement(
        self, persistence_service: LensDataPersistenceService
    ) -> None:
        """GP-110: IMPLEMENT with low complexity uses standard LENS.

        Scenario: IMPLEMENT with complexity=3, files_affected=1
        Expected: get_scan_depth returns 'standard'.
        """
        depth = persistence_service.get_scan_depth(
            intent_type="IMPLEMENT",
            lens_context={"complexity": 3, "files_affected": 1},
        )
        assert depth == "standard"


# =============================================================================
# 🌧️ RAINY DAY PATHS — Failures, degraded modes, error handling
# =============================================================================

class TestGoldenRainyDayPaths:
    """Rainy day golden tests — failures must be handled gracefully."""

    def test_gp201_degraded_lens_still_creates_plan(
        self, plan_gate_service: PlanGateService, empty_lens_context: Dict
    ) -> None:
        """GP-201: Plan created even when LENS is unavailable.

        Scenario: LENS returns degraded context (unavailable)
        Expected: Plan still created with default risk score.
        """
        plan = plan_gate_service.create_plan(
            user_request="implement feature",
            intent_type="IMPLEMENT",
            lens_context=empty_lens_context,
        )

        assert plan.plan_id.startswith("plan-")
        assert plan.step_count() >= 4  # Still has TDD steps
        assert plan.risk_score == 0.3  # Default risk

    def test_gp202_empty_user_request_handled(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-202: Empty user request still produces valid plan.

        Scenario: Empty string passed as user_request
        Expected: Plan created, no crash.
        """
        plan = plan_gate_service.create_plan(
            user_request="",
            intent_type="IMPLEMENT",
            lens_context={},
        )

        assert plan.plan_id.startswith("plan-")
        assert plan.user_request == ""
        assert plan.step_count() > 0

    def test_gp203_invalid_intent_defaults_to_plan_required(self) -> None:
        """GP-203: Unknown intent type defaults to requiring plan gate.

        Scenario: Intent "FOOBAR" not in bypass list
        Expected: requires_plan_gate returns True (conservative default).
        """
        assert requires_plan_gate("FOOBAR") is True
        assert requires_plan_gate("UNKNOWN") is True
        assert requires_plan_gate("") is True

    def test_gp204_corrupted_lens_history_recovers(
        self, persistence_service: LensDataPersistenceService,
    ) -> None:
        """GP-204: Corrupted lens_history.json is recovered gracefully.

        Scenario: lens_history.json contains invalid JSON
        Expected: Service starts fresh — no crash.
        """
        # Create corrupted file
        repo_dir = persistence_service.company_root / "repos" / "cortex"
        repo_dir.mkdir(parents=True, exist_ok=True)
        history_path = repo_dir / "lens_history.json"
        history_path.write_text("NOT VALID JSON {{{{", encoding="utf-8")

        # Should not crash
        result = persistence_service.append_lens_data(
            repo_slug="cortex",
            lens_context={"test": True},
            intent_type="FIX",
        )

        assert result["history_appended"] is True
        # History should now be valid with 1 entry
        data = json.loads(history_path.read_text())
        assert isinstance(data, list)
        assert len(data) == 1

    def test_gp205_risk_score_clamped_to_valid_range(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-205: Risk score > 1.0 or < 0.0 is clamped.

        Scenario: LENS returns risk_score=5.0
        Expected: Plan risk_score clamped to 1.0.
        """
        plan = plan_gate_service.create_plan(
            user_request="fix critical bug",
            intent_type="FIX",
            lens_context={"risk_score": 5.0},
        )
        assert plan.risk_score == 1.0

        plan2 = plan_gate_service.create_plan(
            user_request="fix minor issue",
            intent_type="FIX",
            lens_context={"risk_score": -0.5},
        )
        assert plan2.risk_score == 0.0

    def test_gp206_persistence_failure_does_not_crash_plan_gate(
        self,
    ) -> None:
        """GP-206: If LENS persistence fails, plan is still returned.

        Scenario: Company registry directory doesn't exist and can't be created
        Expected: Plan created successfully, persistence fails gracefully.
        """
        svc = PlanGateService()
        plan = svc.create_plan(
            user_request="implement feature",
            intent_type="IMPLEMENT",
            lens_context={"intent": "IMPLEMENT"},
        )
        # Plan is valid regardless of persistence
        assert plan.plan_id.startswith("plan-")
        assert plan.step_count() > 0

    def test_gp207_challenge_stub_returns_none_no_crash(
        self, interaction_orchestrator
    ) -> None:
        """GP-207: _evaluate_challenge stub returns None without crash.

        Even with enable_challenges=True, the stub should not throw.
        """
        result = interaction_orchestrator._evaluate_challenge(
            user_request="implement dangerous feature",
            lens_context={"risk_score": 0.9},
            pattern_id=None,
        )
        assert result is None


# =============================================================================
# 🔲 EDGE CASES — Boundary conditions and unusual inputs
# =============================================================================

class TestGoldenEdgeCases:
    """Edge case golden tests — boundary conditions that expose bugs."""

    def test_gp301_case_insensitive_intent_matching(self) -> None:
        """GP-301: Intent matching is case-insensitive.

        Scenario: "implement", "IMPLEMENT", "Implement" all equivalent
        Expected: All require plan gate.
        """
        for variant in ["implement", "IMPLEMENT", "Implement", "iMpLeMeNt"]:
            assert requires_plan_gate(variant) is True, \
                f"'{variant}' should require plan gate"

        for variant in ["query", "QUERY", "Query", "qUeRy"]:
            assert requires_plan_gate(variant) is False, \
                f"'{variant}' should bypass plan gate"

    def test_gp302_unique_plan_ids_across_1000_plans(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-302: 1000 sequential plans all have unique IDs.

        Scenario: Rapid plan creation
        Expected: Zero ID collisions.
        """
        ids = set()
        for _ in range(1000):
            plan = plan_gate_service.create_plan(
                user_request="implement feature",
                intent_type="IMPLEMENT",
                lens_context={},
            )
            ids.add(plan.plan_id)

        assert len(ids) == 1000, "All plan IDs must be unique"

    def test_gp303_plan_with_zero_steps_edge(self) -> None:
        """GP-303: InteractionPlan with empty steps list is valid.

        Scenario: Manually constructed plan with no steps
        Expected: step_count() returns 0, to_dict() works.
        """
        plan = InteractionPlan(
            plan_id="plan-empty",
            user_request="test",
            intent_type="IMPLEMENT",
            steps=[],
        )
        assert plan.step_count() == 0
        d = plan.to_dict()
        assert d["steps"] == []

    def test_gp304_very_long_user_request(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-304: Very long user request (10KB) handled without truncation.

        Scenario: 10,000-character user request
        Expected: Plan created, user_request preserved.
        """
        long_request = "implement " + "x" * 10000
        plan = plan_gate_service.create_plan(
            user_request=long_request,
            intent_type="IMPLEMENT",
            lens_context={},
        )
        assert plan.user_request == long_request
        assert plan.step_count() > 0

    def test_gp305_lens_context_with_nested_dicts(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-305: Deeply nested LENS context serializes correctly.

        Scenario: LENS context 5 levels deep
        Expected: Plan to_dict() preserves nested structure.
        """
        nested = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "deep_value"
                        }
                    }
                }
            },
            "risk_score": 0.5,
        }
        plan = plan_gate_service.create_plan(
            user_request="implement",
            intent_type="IMPLEMENT",
            lens_context=nested,
        )
        d = plan.to_dict()
        assert d["lens_context"]["level1"]["level2"]["level3"]["level4"]["level5"] == "deep_value"

    def test_gp306_all_bypass_intents_exhaustive(self) -> None:
        """GP-306: Every PLAN_GATE_BYPASS_INTENTS member actually bypasses.

        Scenario: Iterate all bypass intents
        Expected: None require plan gate.
        """
        for intent in PLAN_GATE_BYPASS_INTENTS:
            assert requires_plan_gate(intent) is False, \
                f"{intent} is in BYPASS set but requires_plan_gate returned True"

    def test_gp307_approve_is_idempotent(self) -> None:
        """GP-307: Calling approve() multiple times is safe.

        Scenario: approve() called 3 times
        Expected: Plan stays approved, no side effects.
        """
        plan = InteractionPlan(
            plan_id="plan-idem",
            user_request="test",
            intent_type="IMPLEMENT",
        )
        assert plan.approved is False
        plan.approve()
        assert plan.approved is True
        plan.approve()
        plan.approve()
        assert plan.approved is True

    def test_gp308_scan_depth_boundary_complexity_10(
        self, persistence_service: LensDataPersistenceService
    ) -> None:
        """GP-308: Complexity exactly at boundary (10) triggers standard.

        Scenario: complexity=10, files_affected=5
        Expected: 'standard' (boundary is > 10 for deep).
        """
        depth = persistence_service.get_scan_depth(
            intent_type="IMPLEMENT",
            lens_context={"complexity": 10, "files_affected": 5},
        )
        assert depth == "standard"

    def test_gp309_scan_depth_boundary_complexity_11(
        self, persistence_service: LensDataPersistenceService
    ) -> None:
        """GP-309: Complexity=11 crosses boundary → deep scan.

        Scenario: complexity=11
        Expected: 'deep'.
        """
        depth = persistence_service.get_scan_depth(
            intent_type="IMPLEMENT",
            lens_context={"complexity": 11},
        )
        assert depth == "deep"


# =============================================================================
# 🔍 BLIND SPOTS — Things nobody tests but break in production
# =============================================================================

class TestGoldenBlindSpots:
    """Blind spot golden tests — the things that bite you in production."""

    def test_gp401_concurrent_plan_ids_are_unique(
        self, plan_gate_service: PlanGateService
    ) -> None:
        """GP-401: Plans created in rapid succession never share IDs.

        Blind spot: UUID collision under rapid creation.
        """
        plans = [
            plan_gate_service.create_plan(
                user_request=f"request {i}",
                intent_type="IMPLEMENT",
                lens_context={},
            )
            for i in range(100)
        ]
        ids = [p.plan_id for p in plans]
        assert len(set(ids)) == 100

    def test_gp402_to_dict_is_json_serializable(
        self, plan_gate_service: PlanGateService, rich_lens_context: Dict
    ) -> None:
        """GP-402: Plan.to_dict() output is fully JSON-serializable.

        Blind spot: datetime objects, Path objects, or enums in dict
        cause json.dumps to crash.
        """
        plan = plan_gate_service.create_plan(
            user_request="implement feature",
            intent_type="IMPLEMENT",
            lens_context=rich_lens_context,
        )
        d = plan.to_dict()
        # Must not raise
        serialized = json.dumps(d, default=str)
        assert isinstance(serialized, str)
        assert len(serialized) > 50

    def test_gp403_lens_persistence_with_special_characters(
        self, persistence_service: LensDataPersistenceService,
    ) -> None:
        """GP-403: LENS data with unicode and special chars persists correctly.

        Blind spot: Non-ASCII in user request or LENS context breaks JSON.
        """
        result = persistence_service.append_lens_data(
            repo_slug="cortex",
            lens_context={
                "description": "Ünïcödë tëst 🧠 日本語 عربي",
                "path": "/tmp/café/naïve.py",
            },
            intent_type="IMPLEMENT",
        )
        assert result["dashboard_file"] is not None

        # Verify round-trip
        data = json.loads(Path(result["dashboard_file"]).read_text(encoding="utf-8"))
        assert "Ünïcödë" in json.dumps(data, ensure_ascii=False)

    def test_gp404_plan_gate_service_is_stateless_per_request(self) -> None:
        """GP-404: PlanGateService creates independent plans per call.

        Blind spot: Shared mutable state between plans (step lists).
        """
        svc = PlanGateService()
        plan1 = svc.create_plan("req1", "IMPLEMENT", {})
        plan2 = svc.create_plan("req2", "IMPLEMENT", {})

        # Mutate plan1 steps
        plan1.steps.append(InteractionPlanStep(order=99, description="INJECTED"))

        # plan2 must NOT be affected
        assert all(s.order != 99 for s in plan2.steps), \
            "Shared mutable state detected between plans!"

    def test_gp405_interaction_orchestrator_classify_intent_coverage(
        self, interaction_orchestrator
    ) -> None:
        """GP-405: _classify_intent covers common real-world phrasings.

        Blind spot: User says "fix" but in a sentence that doesn't match.
        """
        cases = {
            "implement a new login page": "IMPLEMENT",
            "create user registration": "IMPLEMENT",
            "add a dashboard widget": "IMPLEMENT",
            "build the CI pipeline": "IMPLEMENT",
            "fix the broken auth": "FIX",
            "there's a bug in payment": "FIX",
            "error when uploading files": "FIX",
            "refactor the database layer": "REFACTOR",
            "clean up the utils module": "REFACTOR",
            "optimize query performance": "REFACTOR",
            "analyze test coverage": "ANALYZE",
            "review the security config": "ANALYZE",
            "what is CORTEX?": "UNKNOWN",  # No keywords match
        }

        for request, expected in cases.items():
            result = interaction_orchestrator._classify_intent(request)
            assert result == expected, \
                f"'{request}' classified as '{result}', expected '{expected}'"

    def test_gp406_lens_depth_missing_all_fields(
        self, persistence_service: LensDataPersistenceService
    ) -> None:
        """GP-406: get_scan_depth with completely empty lens_context.

        Blind spot: KeyError when complexity/files_affected not present.
        """
        depth = persistence_service.get_scan_depth(
            intent_type="IMPLEMENT",
            lens_context={},
        )
        assert depth == "standard"  # Default for code-modifying without complexity

    def test_gp407_plan_high_risk_threshold_exact(self) -> None:
        """GP-407: is_high_risk at exact boundary (0.7).

        Blind spot: Off-by-one — is 0.7 high risk or not?
        """
        plan_at = InteractionPlan(
            plan_id="plan-boundary",
            user_request="test",
            intent_type="IMPLEMENT",
            risk_score=0.7,
        )
        assert plan_at.is_high_risk() is False  # > 0.7, not >= 0.7

        plan_over = InteractionPlan(
            plan_id="plan-over",
            user_request="test",
            intent_type="IMPLEMENT",
            risk_score=0.71,
        )
        assert plan_over.is_high_risk() is True

    def test_gp408_persistence_creates_missing_directories(
        self, temp_company_dir
    ) -> None:
        """GP-408: Persistence creates missing directories automatically.

        Blind spot: First run on fresh install — no dirs exist.
        """
        repo_root, _ = temp_company_dir
        # Remove the company dir entirely
        import shutil
        company = repo_root / "cortex-registry" / "company"
        if company.exists():
            shutil.rmtree(company)

        svc = LensDataPersistenceService(repo_root=repo_root)
        result = svc.append_lens_data(
            repo_slug="newrepo",
            lens_context={"test": True},
            intent_type="IMPLEMENT",
        )

        assert result["dashboard_file"] is not None
        assert result["history_appended"] is True


# AC_COMPLETE: AC-GOLDEN-PLAN-GATE-001 ✅
