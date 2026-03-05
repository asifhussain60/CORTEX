"""
Golden Truth Tests: ADO Context Enricher Layer
══════════════════════════════════════════════════════════════════════════════

Purpose:
    Verify ADOContextEnricher detects ADO references in user request strings,
    fetches stories via the provider, and injects UserStoryContext into
    UnifiedIntelligenceContext without mutating the original request.

    These tests cover Layer 3 — the architectural centrepiece that makes
    ADO context available to ALL orchestrators transparently.

    ALL 15 TESTS MUST FAIL (RED) before implementation begins (CORE-008).

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider (ADO implementation)

AC-IDs: AC-ADO-E-001 through AC-ADO-E-015
Golden count target: 15 tests
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-E-001 — Importability
# ──────────────────────────────────────────────────────────────────────────────

class TestADOContextEnricherImport:
    """ADOContextEnricher must import from its canonical path."""

    def test_enricher_importable_from_canonical_path(self):
        """
        AC-ADO-E-001: ADOContextEnricher must import from cortex.orchestrators.core.ado_context_enricher.

        RED: ImportError — file does not exist yet.
        GREEN: Class is importable.
        """
        from cortex.orchestrators.core.ado_context_enricher import ADOContextEnricher
        assert ADOContextEnricher is not None


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-E-002 through AC-ADO-E-008 — ADO reference detection
# ──────────────────────────────────────────────────────────────────────────────

class TestADOReferenceDetection:
    """detect_ado_references() must correctly detect all supported ADO reference formats."""

    def test_detect_ado_references_from_full_url(self, ado_enricher, request_full_url):
        """
        AC-ADO-E-002: Full ADO work item URL must yield the correct ID.

        Input:  "implement https://dev.azure.com/HQY01/V5/_workitems/edit/692945"
        Expect: [692945]

        RED: [] if FULL_URL_PATTERN not defined or pattern group wrong.
        GREEN: [692945].
        """
        ids = ado_enricher.detect_ado_references(request_full_url)
        assert 692945 in ids
        assert len(ids) == 1

    def test_detect_ado_references_from_hash_prefix(self, ado_enricher, request_hash_id):
        """
        AC-ADO-E-003: Hash-prefixed ID must yield the correct work item ID.

        Input:  "Can you implement the work on #692945 for the password reset feature?"
        Expect: [692945]

        RED: [] if HASH_ID_PATTERN not defined.
        GREEN: [692945].
        """
        ids = ado_enricher.detect_ado_references(request_hash_id)
        assert 692945 in ids

    def test_detect_ado_references_returns_empty_for_no_match(self, ado_enricher, request_no_ado):
        """
        AC-ADO-E-004: Request with no ADO references must return empty list.

        Input:  "Refactor the authentication module to reduce cyclomatic complexity"
        Expect: []

        RED: Returns non-empty if pattern is too broad.
        GREEN: [].
        """
        ids = ado_enricher.detect_ado_references(request_no_ado)
        assert ids == [], f"Expected no ADO references, got {ids}"

    def test_detect_ado_references_from_multiple_urls_in_text(
        self, ado_enricher, request_multiple_ids
    ):
        """
        AC-ADO-E-005: Multiple ADO IDs in one request must all be detected.

        Input:  "Review #692945 and #692940 — both are in the Authentication area"
        Expect: [692940, 692945] (or any order with both present)

        RED: Only returns first match if regex doesn't use findall.
        GREEN: Both IDs detected.
        """
        ids = ado_enricher.detect_ado_references(request_multiple_ids)
        assert 692945 in ids
        assert 692940 in ids

    def test_detect_ado_references_deduplicates_same_id(self, ado_enricher):
        """
        AC-ADO-E-006: Same ID appearing multiple times must appear once in result.

        Input:  "Story #692945 — see https://dev.azure.com/HQY01/V5/_workitems/edit/692945"
        Expect: [692945] — deduplicated

        RED: [692945, 692945] if set() not applied.
        GREEN: [692945].
        """
        text = (
            "Story #692945 — see https://dev.azure.com/HQY01/V5/_workitems/edit/692945"
        )
        ids = ado_enricher.detect_ado_references(text)
        assert ids.count(692945) == 1, f"ID 692945 appeared {ids.count(692945)} times — expected 1"

    def test_detect_bare_id_with_context_hint_is_detected(
        self, ado_enricher, request_bare_id_with_hint
    ):
        """
        AC-ADO-E-007: Bare numeric ID with context hint ('user story') must be detected.

        Input:  "Let's tackle user story 692945 in Sprint 14"
        Expect: [692945]

        RED: [] if bare ID pattern has no context-hint guard.
        GREEN: [692945] because 'user story' is a CONTEXT_HINT.
        """
        ids = ado_enricher.detect_ado_references(request_bare_id_with_hint)
        assert 692945 in ids

    def test_bare_id_without_context_hint_not_detected(self, ado_enricher):
        """
        AC-ADO-E-008: Bare numeric ID with no context hint must NOT trigger ADO lookup.

        Input:  "The answer is 692945"
        Expect: []

        RED: [692945] if bare ID pattern has no context-hint guard.
        GREEN: [] — avoids false positives on arbitrary numbers.
        """
        ids = ado_enricher.detect_ado_references("The answer is 692945")
        assert ids == [], (
            f"Bare ID with no ADO context hint must be ignored. "
            f"Got {ids}. Add context-hint guard to BARE_ID_PATTERN."
        )


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-E-009 through AC-ADO-E-012 — Context injection
# ──────────────────────────────────────────────────────────────────────────────

class TestADOContextInjection:
    """enrich() must inject UserStoryContext into UnifiedIntelligenceContext."""

    def test_enricher_injects_ado_story_into_intel_context(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-E-009: enrich() must populate intel_context.ado_stories with UserStoryContext.

        RED: ado_stories=[] if enrich() not implemented.
        GREEN: ado_stories contains one UserStoryContext for story 692945.
        """
        from cortex.repositories.ado.ado_provider import UserStoryContext

        enriched = ado_enricher.enrich(request_full_url, empty_intel_context)
        assert hasattr(enriched, "ado_stories"), (
            "UnifiedIntelligenceContext must have ado_stories field after enrichment"
        )
        assert len(enriched.ado_stories) == 1
        assert isinstance(enriched.ado_stories[0], UserStoryContext)
        assert enriched.ado_stories[0].id == "692945"

    def test_enricher_adds_ado_to_enriched_sources(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-E-010: enrich() must append 'ado' to intel_context.enriched_sources.

        RED: enriched_sources unchanged if inject step not implemented.
        GREEN: 'ado' in enriched.enriched_sources.
        """
        enriched = ado_enricher.enrich(request_full_url, empty_intel_context)
        assert hasattr(enriched, "enriched_sources")
        assert "ado" in enriched.enriched_sources

    def test_enricher_skips_when_no_ado_refs_detected(
        self, ado_enricher, empty_intel_context, request_no_ado
    ):
        """
        AC-ADO-E-011: enrich() must return intel_context unchanged when no ADO refs found.

        RED: Calls HTTP anyway if fast-path not implemented.
        GREEN: ado_stories=[], enriched_sources unchanged, provider never called.
        """
        original_stories = list(getattr(empty_intel_context, "ado_stories", []))
        enriched = ado_enricher.enrich(request_no_ado, empty_intel_context)
        assert len(getattr(enriched, "ado_stories", [])) == len(original_stories)

    def test_enricher_handles_provider_key_error_gracefully(
        self, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-E-012: enrich() must not raise when provider raises KeyError (story not found).

        RED: Raises KeyError propagated from provider.
        GREEN: Logs warning, ado_stories stays empty, no exception.
        """
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        from cortex.orchestrators.core.ado_context_enricher import ADOContextEnricher

        mock_provider = MagicMock(spec=ADOWorkItemProvider)
        mock_provider.fetch_story_context.side_effect = KeyError("Work item 692945 not found")

        enricher = ADOContextEnricher(provider=mock_provider)
        # Must NOT raise — graceful degradation
        enriched = enricher.enrich(request_full_url, empty_intel_context)
        assert isinstance(enriched, type(empty_intel_context))


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-E-013 through AC-ADO-E-015 — Safety & isolation
# ──────────────────────────────────────────────────────────────────────────────

class TestADOEnricherSafety:
    """Enricher must not mutate original request or call provider unnecessarily."""

    def test_enricher_does_not_mutate_original_request_string(
        self, ado_enricher, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-E-013: enrich() must not modify the original request string.

        RED: Would mutate if regex uses re.sub incorrectly.
        GREEN: request_full_url identical before and after enrich().
        """
        original_request = request_full_url[:]
        ado_enricher.enrich(request_full_url, empty_intel_context)
        assert request_full_url == original_request

    def test_enricher_resolves_multiple_ids_into_multiple_stories(
        self, ado_enricher, empty_intel_context, request_multiple_ids
    ):
        """
        AC-ADO-E-014: enrich() with two ADO IDs must populate ado_stories with two contexts.

        The fixture mock returns the same payload for any ID — that's OK for this test.
        We verify the count, not the distinct content.

        RED: ado_stories has only 1 entry if loop is broken.
        GREEN: ado_stories has 2 entries.
        """
        enriched = ado_enricher.enrich(request_multiple_ids, empty_intel_context)
        assert len(getattr(enriched, "ado_stories", [])) == 2

    def test_enricher_handles_permission_error_gracefully(
        self, empty_intel_context, request_full_url
    ):
        """
        AC-ADO-E-015: enrich() must not raise when provider raises PermissionError (bad PAT).

        RED: Raises PermissionError propagated to caller.
        GREEN: Logs error, ado_stories stays empty, caller continues normally.
        """
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        from cortex.orchestrators.core.ado_context_enricher import ADOContextEnricher

        mock_provider = MagicMock(spec=ADOWorkItemProvider)
        mock_provider.fetch_story_context.side_effect = PermissionError("ADO PAT invalid")

        enricher = ADOContextEnricher(provider=mock_provider)
        enriched = enricher.enrich(request_full_url, empty_intel_context)
        assert getattr(enriched, "ado_stories", []) == []
