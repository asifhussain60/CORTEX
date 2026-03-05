"""
ADOContextEnricher — Stage 1 pipeline plugin for ADO work item context injection.

Mirrors the LENS enricher pattern in InteractionOrchestrator: detects ADO
work item references in the user request string, fetches story context via
ADOWorkItemProvider, and injects UserStoryContext into UnifiedIntelligenceContext
BEFORE intent routing occurs.

This makes ADO story data (acceptance criteria, sprint, child tasks, test links)
transparently available to ALL downstream orchestrators:
    TDDOrchestrator    — reads acceptance_criteria to generate failing test stubs
    AuditCoordinator   — checks coverage against linked_test_case_ids
    QueryOrchestrator  — answers "what does this story do?" from title + description
    PlanningOrchestrator — uses iteration_path and parent_id for sprint association

Detection patterns (in priority order):
    1. FULL_URL_PATTERN  — https://dev.azure.com/{org}/{proj}/_workitems/edit/{id}
    2. HASH_ID_PATTERN   — #692945 (hash prefix)
    3. BARE_ID_PATTERN   — bare integer preceded by a CONTEXT_HINT keyword

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-012 (docstrings)
Phase: Phase 15 — Work Item Provider (ADO implementation)
AC-IDs: AC-ADO-E-001 through AC-ADO-E-015
"""

from __future__ import annotations

import logging
import re
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Detection patterns
# ──────────────────────────────────────────────────────────────────────────────

# Pattern 1: Full ADO work item URL
FULL_URL_PATTERN = re.compile(
    r"https?://dev\.azure\.com/[^/]+/[^/]+/_workitems/edit/(\d+)",
    re.IGNORECASE,
)

# Pattern 2: Hash-prefixed ID  (#692945)
HASH_ID_PATTERN = re.compile(r"#(\d{4,7})\b")

# Context hint keywords that validate a bare integer as an ADO ID
CONTEXT_HINTS = frozenset({
    "user story", "work item", "story", "issue", "task", "bug",
    "ticket", "backlog item", "pbi", "feature", "epic", "ado",
    "workitem", "wi", "implement", "tackle",
})

# Pattern 3: Bare integer preceded by a context hint (within 25 chars)
BARE_ID_PATTERN = re.compile(
    r"(?:" + "|".join(re.escape(h) for h in sorted(CONTEXT_HINTS, key=len, reverse=True)) + r")\s+(\d{4,7})\b",
    re.IGNORECASE,
)


class ADOContextEnricher:
    """
    Stage 1 enricher that injects ADO story context into UnifiedIntelligenceContext.

    Usage (in InteractionOrchestrator.process_turn())::

        enricher = ADOContextEnricher(provider=ado_provider)
        intel_context = enricher.enrich(user_request, intel_context)
        # intel_context.ado_stories is now populated

    The enricher is cheap to reconstruct but designed to be reused per-session
    (single provider instance across turns).
    """

    def __init__(self, provider: Any) -> None:
        """
        Initialise with an ADOWorkItemProvider instance.

        Args:
            provider: ADOWorkItemProvider (or any object with fetch_story_context).
        """
        self._provider = provider

    def _get_provider(self) -> Any:
        """Return the internal provider (used by tests to check call counts)."""
        return self._provider

    def detect_ado_references(self, request: str) -> List[int]:
        """
        Extract ADO work item IDs from a user request string.

        Applies three patterns in order, deduplicates results.

        Args:
            request: Raw user request / chat message string.

        Returns:
            Deduplicated list of integer ADO work item IDs.
        """
        ids: List[int] = []

        for m in FULL_URL_PATTERN.finditer(request):
            ids.append(int(m.group(1)))

        for m in HASH_ID_PATTERN.finditer(request):
            candidate = int(m.group(1))
            if candidate not in ids:
                ids.append(candidate)

        for m in BARE_ID_PATTERN.finditer(request):
            candidate = int(m.group(1))
            if candidate not in ids:
                ids.append(candidate)

        # Deduplicate while preserving order
        seen = set()
        unique: List[int] = []
        for i in ids:
            if i not in seen:
                seen.add(i)
                unique.append(i)
        return unique

    def enrich(self, request: str, intel_context: Any) -> Any:
        """
        Detect ADO references and inject story context into intel_context.

        Gracefully handles all provider exceptions — ADO enrichment is
        supplementary; the pipeline must never fail because ADO is unavailable.

        Args:
            request: Raw user request string.
            intel_context: UnifiedIntelligenceContext to enrich.

        Returns:
            The intel_context with ado_stories and enriched_sources populated.
        """
        # Ensure required fields exist (additive — never removes existing data)
        if not hasattr(intel_context, "ado_stories"):
            intel_context.ado_stories = []
        if not hasattr(intel_context, "enriched_sources"):
            intel_context.enriched_sources = []
        if not hasattr(intel_context, "ado_story_ids"):
            intel_context.ado_story_ids = []

        ids = self.detect_ado_references(request)
        if not ids:
            return intel_context

        fetched = False
        for story_id in ids:
            try:
                ctx = self._provider.fetch_story_context(str(story_id))
                intel_context.ado_stories.append(ctx)
                intel_context.ado_story_ids.append(story_id)
                fetched = True
            except KeyError as exc:
                logger.warning("ADO story not found (id=%s): %s", story_id, exc)
            except PermissionError as exc:
                logger.error("ADO permission denied (id=%s): %s", story_id, exc)
            except Exception as exc:  # noqa: BLE001
                logger.error("ADO enrichment failed (id=%s): %s", story_id, exc)

        if fetched and "ado" not in intel_context.enriched_sources:
            intel_context.enriched_sources.append("ado")

        return intel_context
