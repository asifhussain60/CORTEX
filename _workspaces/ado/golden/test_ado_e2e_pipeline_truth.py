"""
Golden Truth Tests: ADO End-to-End Pipeline
══════════════════════════════════════════════════════════════════════════════

Purpose:
    Verify the FULL pipeline from raw user request string to UserStoryContext
    available in UnifiedIntelligenceContext — ready for ALL downstream
    orchestrators (TDD, Audit, Query, Planning) to consume transparently.

    This is the complete integration truth: if these 15 tests pass, the ADO
    integration is production-ready across the entire CORTEX intelligence pipeline.

    ALL 15 TESTS MUST FAIL (RED) before implementation begins (CORE-008).

Tested path:
    User request
      → ADOContextEnricher.detect_ado_references()   [Layer 3]
      → ADOWorkItemProvider.fetch_story_context()     [Layer 1]
      → UserStoryContext                              [data contract]
      → UnifiedIntelligenceContext.ado_stories        [intelligence injection]
      → downstream orchestrator reads accepted requirements + test link data

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider (ADO implementation)

AC-IDs: AC-ADO-X-001 through AC-ADO-X-015
Golden count target: 15 tests
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Shared E2E setup helper
# ──────────────────────────────────────────────────────────────────────────────

def _build_enriched_context(request: str, ado_enricher, empty_intel_context):
    """Run the full enrichment pipeline and return the enriched intel context."""
    return ado_enricher.enrich(request, empty_intel_context)


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-X-001 through AC-ADO-X-003 — Full URL + Hash ID pipeline
# ──────────────────────────────────────────────────────────────────────────────

class TestADOE2EFullURLRequest:
    """Full ADO URL in request flows to UserStoryContext in intel context."""

    def test_full_url_resolves_to_story_id_in_intel_context(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-X-001: Full ADO URL in IMPLEMENT request resolves to story in intel_context.

        Pipeline: URL detected → story fetched → context injected.
        Verifies the id field survives the full round-trip.

        RED: ado_stories empty if any pipeline stage is stub.
        GREEN: ado_stories[0].id == '692945'.
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        stories = getattr(enriched, "ado_stories", [])
        assert len(stories) == 1
        assert stories[0].id == "692945"

    def test_hash_id_in_query_request_resolves_to_story(
        self, ado_enricher, empty_intel_context, request_hash_id
    ):
        """
        AC-ADO-X-002: Hash-prefixed ID in QUERY request resolves to story context.

        Input:  "Can you implement the work on #692945 for the password reset feature?"
        Verifies: ado_stories[0].title contains "reset password".

        RED: ado_stories empty if HASH_ID_PATTERN not wired to enricher.
        GREEN: title matches.
        """
        enriched = _build_enriched_context(request_hash_id, ado_enricher, empty_intel_context)
        stories = getattr(enriched, "ado_stories", [])
        assert len(stories) >= 1
        assert "reset password" in stories[0].title.lower()

    def test_no_ado_request_does_not_trigger_enricher_fetch(
        self, ado_enricher, empty_intel_context, request_no_ado
    ):
        """
        AC-ADO-X-003: Request with no ADO reference must not call the provider at all.

        Verifies fast-path: no HTTP calls, no ado_stories populated.

        RED: provider called unnecessarily if fast-path not implemented.
        GREEN: ado_stories=[], provider.fetch_story_context never called.
        """
        call_count_before = ado_enricher._get_provider().fetch_story_context.call_count
        enriched = _build_enriched_context(request_no_ado, ado_enricher, empty_intel_context)
        call_count_after = ado_enricher._get_provider().fetch_story_context.call_count
        assert call_count_after == call_count_before
        assert getattr(enriched, "ado_stories", []) == []


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-X-004 through AC-ADO-X-007 — Story field availability downstream
# ──────────────────────────────────────────────────────────────────────────────

class TestADOStoryContextFieldAvailability:
    """All key story fields must be available in intel_context after enrichment."""

    def test_acceptance_criteria_available_post_enrichment(
        self, ado_enricher, empty_intel_context, request_full_url, expected_692945
    ):
        """
        AC-ADO-X-004: acceptance_criteria must be non-empty after enrichment.

        TDDOrchestrator reads this to generate failing test assertions.
        This is the primary value of ADO enrichment for IMPLEMENT intents.

        RED: acceptance_criteria='' if _map_to_context doesn't extract AcceptanceCriteria.
        GREEN: Non-empty string containing ADO acceptance criteria HTML.
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        assert story.acceptance_criteria, (
            "acceptance_criteria must not be empty after enrichment. "
            "TDDOrchestrator depends on this to write test stubs."
        )
        assert expected_692945["acceptance_criteria_contains"] in story.acceptance_criteria

    def test_sprint_iteration_path_available_post_enrichment(
        self, ado_enricher, empty_intel_context, request_full_url, expected_692945
    ):
        """
        AC-ADO-X-005: iteration_path (sprint) must be populated after enrichment.

        PlanningOrchestrator uses this to associate work with correct sprint.

        RED: iteration_path='' if field mapping incomplete.
        GREEN: 'Sprint 14' in iteration_path.
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        assert "Sprint 14" in story.iteration_path

    def test_child_task_ids_available_post_enrichment(
        self, ado_enricher, empty_intel_context, request_full_url, expected_692945
    ):
        """
        AC-ADO-X-006: child_task_ids must be populated from relation tree.

        Downstream orchestrators use this to understand existing work breakdown.

        RED: child_task_ids=[] if relation parsing not implemented.
        GREEN: [692946, 692947] (both child tasks resolved).
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        assert 692946 in story.child_task_ids
        assert 692947 in story.child_task_ids

    def test_linked_test_case_ids_available_post_enrichment(
        self, ado_enricher, empty_intel_context, request_full_url, expected_692945
    ):
        """
        AC-ADO-X-007: linked_test_case_ids must be populated from TestedBy relations.

        AuditCoordinator uses this to verify coverage against pre-existing test cases.
        TDDOrchestrator should not create duplicate test cases if these already exist in ADO.

        RED: linked_test_case_ids=[] if TestedBy relation not parsed.
        GREEN: [700100, 700101].
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        assert 700100 in story.linked_test_case_ids
        assert 700101 in story.linked_test_case_ids


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-X-008 through AC-ADO-X-010 — Enriched sources flag
# ──────────────────────────────────────────────────────────────────────────────

class TestADOEnrichedSourcesFlag:
    """enriched_sources flag enables downstream orchestrators to check context availability."""

    def test_ado_in_enriched_sources_after_successful_enrich(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-X-008: 'ado' must appear in intel_context.enriched_sources after enrichment.

        This flag lets TDDOrchestrator, AuditCoordinator, etc. check:
            if 'ado' in intel_context.enriched_sources:
                story = intel_context.ado_stories[0]
                # Use acceptance criteria

        RED: enriched_sources unchanged if injection step not wired.
        GREEN: 'ado' in enriched_sources.
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        assert "ado" in getattr(enriched, "enriched_sources", [])

    def test_ado_not_in_enriched_sources_when_no_refs_found(
        self, ado_enricher, empty_intel_context, request_no_ado
    ):
        """
        AC-ADO-X-009: 'ado' must NOT be in enriched_sources when no ADO refs detected.

        Downstream logic uses absence of 'ado' in enriched_sources as a fast check.

        RED: 'ado' added unconditionally if fast-path not applied.
        GREEN: enriched_sources does not contain 'ado'.
        """
        enriched = _build_enriched_context(request_no_ado, ado_enricher, empty_intel_context)
        assert "ado" not in getattr(enriched, "enriched_sources", [])

    def test_story_url_matches_original_request_url(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-X-010: story.url in intel_context must match the URL from the original request.

        Provides traceability: user can verify CORTEX fetched the right story.

        RED: URL mismatch if _links.html.href not extracted by _map_to_context.
        GREEN: story.url == "https://dev.azure.com/HQY01/V5/_workitems/edit/692945".
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        expected_url = "https://dev.azure.com/HQY01/V5/_workitems/edit/692945"
        assert story.url == expected_url


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-X-011 through AC-ADO-X-013 — Multi-story + parent linkage
# ──────────────────────────────────────────────────────────────────────────────

class TestADOE2EMultiStory:
    """Multiple ADO IDs in one request must all be independently resolved."""

    def test_multiple_ado_refs_all_resolved_in_context(
        self, ado_enricher, empty_intel_context, request_multiple_ids
    ):
        """
        AC-ADO-X-011: Two #IDs in one request must produce two UserStoryContext objects.

        Input:  "Review #692945 and #692940 — both are in the Authentication area"
        Expect: intel_context.ado_stories has 2 entries.

        RED: Only 1 entry if enricher doesn't loop over all detected IDs.
        GREEN: 2 entries, both UserStoryContext.
        """
        from cortex.repositories.ado.ado_provider import UserStoryContext
        enriched = _build_enriched_context(request_multiple_ids, ado_enricher, empty_intel_context)
        stories = getattr(enriched, "ado_stories", [])
        assert len(stories) == 2
        assert all(isinstance(s, UserStoryContext) for s in stories)

    def test_parent_epic_id_available_in_story_context(
        self, ado_enricher, empty_intel_context, request_full_url, expected_692945
    ):
        """
        AC-ADO-X-012: parent_id must be populated — links story to its Epic.

        PlanningOrchestrator uses parent_id to understand story hierarchy.
        AuditCoordinator uses it to verify epic-level coverage.

        RED: parent_id=None if Hierarchy-Reverse relation not parsed.
        GREEN: parent_id == 689000.
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        assert story.parent_id == expected_692945["parent_id"], (
            f"Expected parent_id={expected_692945['parent_id']}, got {story.parent_id}. "
            f"Hierarchy-Reverse relation must be parsed by _map_to_context."
        )

    def test_story_tags_are_a_list_not_raw_string(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-X-013: story.tags must be a Python list — not the raw 'auth; security;...' string.

        Downstream orchestrators check tag membership with 'in' operator.

        RED: tags=['auth; security; password-reset'] as single element.
        GREEN: tags=['auth', 'security', 'password-reset'] — 3 clean strings.
        """
        enriched = _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        story = enriched.ado_stories[0]
        assert isinstance(story.tags, list)
        assert all(isinstance(t, str) for t in story.tags)
        assert all(";" not in t for t in story.tags)
        assert "auth" in story.tags


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-X-014, AC-ADO-X-015 — Performance + robustness
# ──────────────────────────────────────────────────────────────────────────────

class TestADOE2EPerformanceAndRobustness:
    """Enrichment must complete within budget and survive provider failures silently."""

    def test_enrichment_completes_within_500ms_budget(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-X-014: Full enrichment cycle must complete in under 500ms (mocked HTTP).

        The 500ms budget covers: pattern detection + mock HTTP call + mapping.
        In production with real HTTP: 30s timeout applies at provider level.
        Here we verify the pipeline itself adds negligible overhead.

        RED: Takes >500ms if enricher does unnecessary work.
        GREEN: Completes in <500ms with mocked provider.
        """
        start = time.perf_counter()
        _build_enriched_context(request_full_url, ado_enricher, empty_intel_context)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500, (
            f"Enrichment took {elapsed_ms:.1f}ms — exceeds 500ms budget. "
            f"Check for unnecessary loops or synchronous calls."
        )

    def test_enrichment_survives_provider_exception_silently(
        self, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-X-015: Enrichment must not crash the pipeline on any provider exception.

        CORTEX pipelines must be resilient — ADO enrichment is supplementary,
        not critical. If ADO is down, requests should continue without story context.

        RED: Exception propagates if enrich() doesn't catch generic Exception.
        GREEN: Returns empty ado_stories, no exception, pipeline continues.

        Tests: generic Exception (network timeout, JSON decode error, etc.)
        """
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        from cortex.orchestrators.core.ado_context_enricher import ADOContextEnricher

        mock_provider = MagicMock(spec=ADOWorkItemProvider)
        mock_provider.fetch_story_context.side_effect = Exception(
            "Connection timeout after 30s"
        )

        enricher = ADOContextEnricher(provider=mock_provider)
        enriched = enricher.enrich(request_full_url, empty_intel_context)

        # Must not raise — must return context with empty ado_stories
        assert isinstance(enriched, type(empty_intel_context))
        assert getattr(enriched, "ado_stories", []) == []
