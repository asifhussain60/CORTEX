"""Phase 90-a RED tests — IntentRouter keyword lists for 7 missing IntentTypes.

AC-ID: SWEEP-90-HOLISTIC-INTENT-WIRING / GAP-90-01 through GAP-90-07
Governance: CORE-008 (TDD — tests written first, implementation forbidden until RED confirmed)

These tests assert that IntentRouter.detect_intent() correctly classifies each of the
7 IntentTypes added in Phase 89 that currently lack keyword routing:
    DEBUG, HEALTH, SYNC, TRAIN, TOTALRECALL, RCA, VACUUM (fix: return VACUUM not REFACTOR)
"""
from __future__ import annotations

import pytest

from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.intent_router_impl import IntentRouter


@pytest.fixture(scope="module")
def router() -> IntentRouter:
    """Shared IntentRouter instance (disable LLM in tests)."""
    r = IntentRouter()
    # Ensure LLM tier is disabled — fast deterministic tests only
    r.intent_classifier.enable_llm = False
    return r


def _detect(router: IntentRouter, text: str) -> IntentType:
    """Helper: classify from description text."""
    return router.detect_intent({"description": text})


# ── GAP-90-01: DEBUG ──────────────────────────────────────────────────────────

class TestDebugIntentDetection:
    """GAP-90-01 — IntentType.DEBUG must be reachable from natural language."""

    def test_debug_intent_detected_from_keyword_debug(self, router: IntentRouter) -> None:
        """'debug' keyword must route to IntentType.DEBUG."""
        result = _detect(router, "debug the failing authentication handler")
        assert result == IntentType.DEBUG, f"Expected DEBUG, got {result}"

    def test_debug_intent_detected_from_slash_debug(self, router: IntentRouter) -> None:
        """/debug command must route to IntentType.DEBUG."""
        result = _detect(router, "/debug cortex/orchestrators/core/master_orchestrator.py")
        assert result == IntentType.DEBUG, f"Expected DEBUG, got {result}"

    def test_debug_intent_detected_from_trace(self, router: IntentRouter) -> None:
        """'trace' keyword must route to IntentType.DEBUG."""
        result = _detect(router, "trace the execution path through the intent router")
        assert result == IntentType.DEBUG, f"Expected DEBUG, got {result}"

    def test_debug_intent_detected_from_diagnose(self, router: IntentRouter) -> None:
        """'diagnose' keyword must route to IntentType.DEBUG."""
        result = _detect(router, "diagnose why the health orchestrator is failing")
        assert result == IntentType.DEBUG, f"Expected DEBUG, got {result}"


# ── GAP-90-02: HEALTH ─────────────────────────────────────────────────────────

class TestHealthIntentDetection:
    """GAP-90-02 — IntentType.HEALTH must be reachable from natural language."""

    def test_health_intent_detected_from_health_check(self, router: IntentRouter) -> None:
        """'health check' must route to IntentType.HEALTH."""
        result = _detect(router, "run a health check on all orchestrators")
        assert result == IntentType.HEALTH, f"Expected HEALTH, got {result}"

    def test_health_intent_detected_from_slash_health(self, router: IntentRouter) -> None:
        """/health command must route to IntentType.HEALTH."""
        result = _detect(router, "/health")
        assert result == IntentType.HEALTH, f"Expected HEALTH, got {result}"

    def test_health_intent_detected_from_orchestrator_status(self, router: IntentRouter) -> None:
        """'orchestrator status' must route to IntentType.HEALTH."""
        result = _detect(router, "show me the orchestrator status for all 22 endpoints")
        assert result == IntentType.HEALTH, f"Expected HEALTH, got {result}"


# ── GAP-90-03: SYNC ───────────────────────────────────────────────────────────

class TestSyncIntentDetection:
    """GAP-90-03 — IntentType.SYNC must be reachable from natural language."""

    def test_sync_intent_detected_from_slash_sync(self, router: IntentRouter) -> None:
        """/sync command must route to IntentType.SYNC."""
        result = _detect(router, "/sync target=/Users/asif/company-repo")
        assert result == IntentType.SYNC, f"Expected SYNC, got {result}"

    def test_sync_intent_detected_from_sync_to_company(self, router: IntentRouter) -> None:
        """'sync to company folder' must route to IntentType.SYNC."""
        result = _detect(router, "sync to company folder using privacy-safe mode")
        assert result == IntentType.SYNC, f"Expected SYNC, got {result}"

    def test_sync_intent_detected_from_cross_repo(self, router: IntentRouter) -> None:
        """'cross-repo sync' must route to IntentType.SYNC."""
        result = _detect(router, "do a cross-repo sync from CORTEX to work")
        assert result == IntentType.SYNC, f"Expected SYNC, got {result}"


# ── GAP-90-04: TRAIN ──────────────────────────────────────────────────────────

class TestTrainIntentDetection:
    """GAP-90-04 — IntentType.TRAIN must be reachable from natural language."""

    def test_train_intent_detected_from_learn_from_repo(self, router: IntentRouter) -> None:
        """'learn from repo' must route to IntentType.TRAIN."""
        result = _detect(router, "learn from this repo and evolve our templates")
        assert result == IntentType.TRAIN, f"Expected TRAIN, got {result}"

    def test_train_intent_detected_from_slash_train(self, router: IntentRouter) -> None:
        """/train command must route to IntentType.TRAIN."""
        result = _detect(router, "/train cortex-sts/CortexLabs/BadMonolith")
        assert result == IntentType.TRAIN, f"Expected TRAIN, got {result}"

    def test_train_intent_detected_from_evolve_templates(self, router: IntentRouter) -> None:
        """'evolve templates' must route to IntentType.TRAIN."""
        result = _detect(router, "evolve templates from the patterns in this codebase")
        assert result == IntentType.TRAIN, f"Expected TRAIN, got {result}"


# ── GAP-90-05: TOTALRECALL ────────────────────────────────────────────────────

class TestTotalRecallIntentDetection:
    """GAP-90-05 — IntentType.TOTALRECALL must be reachable from natural language."""

    def test_totalrecall_intent_detected_from_slash_totalrecall(self, router: IntentRouter) -> None:
        """/totalrecall command must route to IntentType.TOTALRECALL."""
        result = _detect(router, "/totalrecall")
        assert result == IntentType.TOTALRECALL, f"Expected TOTALRECALL, got {result}"

    def test_totalrecall_intent_detected_from_total_recall(self, router: IntentRouter) -> None:
        """'total recall' must route to IntentType.TOTALRECALL."""
        result = _detect(router, "run total recall on the codebase")
        assert result == IntentType.TOTALRECALL, f"Expected TOTALRECALL, got {result}"

    def test_totalrecall_intent_detected_from_holistic_refactor(self, router: IntentRouter) -> None:
        """'holistic refactor' must route to IntentType.TOTALRECALL."""
        result = _detect(router, "holistic refactor everything — total production readiness")
        assert result == IntentType.TOTALRECALL, f"Expected TOTALRECALL, got {result}"


# ── GAP-90-06: RCA ────────────────────────────────────────────────────────────

class TestRCAIntentDetection:
    """GAP-90-06 — IntentType.RCA must be reachable from natural language."""

    def test_rca_intent_detected_from_root_cause_analysis(self, router: IntentRouter) -> None:
        """'root cause analysis' must route to IntentType.RCA."""
        result = _detect(router, "root cause analysis of why the smoke tests keep failing")
        assert result == IntentType.RCA, f"Expected RCA, got {result}"

    def test_rca_intent_detected_from_five_whys(self, router: IntentRouter) -> None:
        """'five whys' must route to IntentType.RCA."""
        result = _detect(router, "run a five whys on the authentication failure")
        assert result == IntentType.RCA, f"Expected RCA, got {result}"

    def test_rca_intent_detected_from_fishbone(self, router: IntentRouter) -> None:
        """'fishbone' must route to IntentType.RCA."""
        result = _detect(router, "do a fishbone analysis on the deployment outage")
        assert result == IntentType.RCA, f"Expected RCA, got {result}"

    def test_rca_intent_detected_from_slash_rca(self, router: IntentRouter) -> None:
        """/rca command must route to IntentType.RCA."""
        result = _detect(router, "/rca why did the CI pipeline fail last night")
        assert result == IntentType.RCA, f"Expected RCA, got {result}"


# ── GAP-90-07: VACUUM (fix: must return VACUUM not REFACTOR) ──────────────────

class TestVacuumIntentDetection:
    """GAP-90-07 — IntentType.VACUUM must return VACUUM not REFACTOR."""

    def test_vacuum_intent_not_routed_as_refactor(self, router: IntentRouter) -> None:
        """/vacuum must return IntentType.VACUUM (not REFACTOR as currently broken)."""
        result = _detect(router, "/vacuum")
        assert result == IntentType.VACUUM, (
            f"VACUUM bypasses standard pipeline and returns REFACTOR — got {result}"
        )

    def test_vacuum_keyword_returns_vacuum_intent(self, router: IntentRouter) -> None:
        """'vacuum' keyword must return IntentType.VACUUM."""
        result = _detect(router, "run vacuum to clean up markdown sprawl")
        assert result == IntentType.VACUUM, f"Expected VACUUM, got {result}"

    def test_vacuum_not_refactor_for_cleanup(self, router: IntentRouter) -> None:
        """'cortex vacuum' must return VACUUM not REFACTOR."""
        result = _detect(router, "cortex vacuum the repo and remove old files")
        assert result == IntentType.VACUUM, f"Expected VACUUM, got {result}"


# ── Operation type mappings completeness ──────────────────────────────────────

class TestOperationTypeMappingsCompleteness:
    """All 27 IntentType values must be in operation_type_mappings."""

    def test_all_27_intent_types_in_operation_type_mappings(self, router: IntentRouter) -> None:
        """Every canonical IntentType (except UNKNOWN) must have a keyword list."""
        skip = {IntentType.UNKNOWN}
        missing = [
            it for it in IntentType
            if it not in skip and it not in router.operation_type_mappings
        ]
        assert missing == [], (
            f"IntentTypes missing from operation_type_mappings: {[m.value for m in missing]}"
        )

    def test_vacuum_in_operation_type_mappings_not_separate_field(self, router: IntentRouter) -> None:
        """VACUUM must be in operation_type_mappings (not only in self.vacuum_keywords)."""
        assert IntentType.VACUUM in router.operation_type_mappings, (
            "IntentType.VACUUM must be wired into operation_type_mappings"
        )
