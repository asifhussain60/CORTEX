"""
ADO Integration — Master Implementation Plan
══════════════════════════════════════════════════════════════════════════════

CLASSIFICATION: IMPLEMENT
ARCHITECT:      ADOContextEnricher (Stage 1 plugin) + ADOOrchestrator (utility)
RISK:           LOW — non-breaking additions to existing orchestrators
TOTAL TESTS:    60 golden (15 per layer × 4 layers)
CORE RULES:     CORE-002, CORE-008, CORE-011, CORE-012, CORE-028, CORE-035, CORE-049

══════════════════════════════════════════════════════════════════════════════
VISION
══════════════════════════════════════════════════════════════════════════════

When a user references ANY of:
    "https://dev.azure.com/HQY01/V5/_workitems/edit/692945"
    "#692945"
    "692945"  (with context hint like "user story", "ADO", "work item")

CORTEX must:
  1. Detect the reference automatically in Stage 1 (zero user ceremony)
  2. Fetch the live story from ADO in one HTTP call ($expand=all)
  3. Inject the full UserStoryContext into UnifiedIntelligenceContext
  4. Make it available to ALL downstream orchestrators transparently
  5. TDDOrchestrator writes tests FROM acceptance criteria
  6. AuditCoordinator checks coverage AGAINST linked test case IDs
  7. QueryCoordinator answers "what does 692945 say?" from live data

══════════════════════════════════════════════════════════════════════════════
ARCHITECTURE OVERVIEW
══════════════════════════════════════════════════════════════════════════════

NEW FILES TO CREATE (in execution order):

  Layer 0 — Fixtures (test infrastructure, no prod code)
  ┌────────────────────────────────────────────────────────────────┐
  │  _workspaces/ado/fixtures/ado_fixtures.py                      │
  │    Realistic ADO REST API response payloads for story #692945  │
  │    Used by all 60 golden tests — single source of truth        │
  └────────────────────────────────────────────────────────────────┘

  Layer 1 — Provider (already stubbed, needs implementation)
  ┌────────────────────────────────────────────────────────────────┐
  │  cortex/repositories/ado/ado_provider.py  (GREEN phase)        │
  │    ADOWorkItemProvider — WorkItemProvider protocol impl        │
  │    UserStoryContext — enriched ADO dataclass                   │
  │    _get_work_item_expand_all() — single HTTP round-trip        │
  │    _run_wiql() — bulk ID fetch                                 │
  │    _batch_get() — 200-item batch field fetch                   │
  │    _map_to_context() — relation tree extraction                │
  └────────────────────────────────────────────────────────────────┘

  Layer 2 — Orchestrator (already stubbed, needs implementation)
  ┌────────────────────────────────────────────────────────────────┐
  │  cortex/repositories/ado/ado_orchestrator.py  (GREEN phase)    │
  │    ADOOrchestrator — OrchestratorBase 5-step lifecycle         │
  │    get_user_story(id) → UserStoryContext  [primary entry]      │
  │    get_user_story_with_children(id) → dict                     │
  │    get_linked_test_cases(id) → List[UserStoryContext]          │
  │    fetch_user_stories(project, **filters) → List               │
  │    search_wiql(query, project) → List                          │
  └────────────────────────────────────────────────────────────────┘

  Layer 3 — Context Enricher (NEW — the architectural centrepiece)
  ┌────────────────────────────────────────────────────────────────┐
  │  cortex/orchestrators/core/ado_context_enricher.py  [NEW]      │
  │    ADOContextEnricher — Stage 1 plugin (mirrors LENS pattern)  │
  │    detect_ado_references(request) → List[int]                  │
  │    enrich(request, intel_context) → UnifiedIntelligenceContext │
  │                                                                │
  │  Hook site: cortex/orchestrators/core/interaction_orchestrator.py
  │    InteractionOrchestrator.process_turn()                      │
  │    Add: self._ado_enricher.enrich(request, intel_ctx)          │
  │    AFTER LENS analysis, BEFORE Stage 2 routing                 │
  └────────────────────────────────────────────────────────────────┘

  Layer 4 — MCP Tools (AFTER orchestrator GREEN)
  ┌────────────────────────────────────────────────────────────────┐
  │  cortex/mcp/tools/ado_tools.py  [NEW]                          │
  │    cortex_ado_get_story(story_id: int) → dict                  │
  │    cortex_ado_get_story_full(story_id: int) → dict             │
  │    cortex_ado_get_linked_tests(story_id: int) → list           │
  │    cortex_ado_search(wiql: str, project: str) → list           │
  │    cortex_ado_health() → bool                                  │
  └────────────────────────────────────────────────────────────────┘

══════════════════════════════════════════════════════════════════════════════
DATA FLOW — STEP BY STEP
══════════════════════════════════════════════════════════════════════════════

INPUT:  "implement https://dev.azure.com/HQY01/V5/_workitems/edit/692945"

STEP 1 — Detection (ADOContextEnricher.detect_ado_references)
  Pattern 1 (full URL):  r"dev\\.azure\\.com/[^/]+/[^/]+/_workitems/edit/(\\d+)"
  Pattern 2 (hash ID):   r"#(\\d{4,7})"
  Pattern 3 (bare ID):   r"\\b(\\d{5,7})\\b"  (used only with context hint)
  → Extracts: [692945]

STEP 2 — Fetch (ADOWorkItemProvider._get_work_item_expand_all)
  GET https://dev.azure.com/HQY01/_apis/wit/workitems/692945?$expand=all&api-version=7.1
  Headers: Authorization: Basic <base64(":<PAT>")>
  → Response: raw ADO JSON dict (see fixtures/ado_fixtures.py for exact shape)

STEP 3 — Map (ADOWorkItemProvider._map_to_context)
  Extracts from raw:
    fields["System.Title"]                                → title
    fields["System.State"]                                → state
    fields["Microsoft.VSTS.Common.AcceptanceCriteria"]    → acceptance_criteria
    fields["System.IterationPath"]                        → iteration_path
    fields["Microsoft.VSTS.Scheduling.StoryPoints"]       → story_points
    relations[rel=="Hierarchy-Reverse"].url[-1]           → parent_id  (689000)
    relations[rel=="Hierarchy-Forward"].url[-1]           → child_task_ids [692946, 692947]
    relations[rel=="TestedBy-Forward"].url[-1]            → linked_test_case_ids [700100, 700101]
    _links.html.href                                      → url

  → Returns: UserStoryContext(id="692945", title="User can reset password...", ...)

STEP 4 — Inject (ADOContextEnricher.enrich)
  intel_context.ado_stories = [UserStoryContext(...)]
  intel_context.enriched_sources.append("ado")
  intel_context.ado_story_ids = [692945]
  → UnifiedIntelligenceContext updated in place (no copy needed)

STEP 5 — Stage 2 Routing (IntentRouter)
  intent=IMPLEMENT → routes to TDDOrchestrator
  TDDOrchestrator.execute() receives intel_context with ado_stories populated
  (no changes needed to TDDOrchestrator)

STEP 6 — Stage 3 Synthesis (MasterOrchestrationStage3)
  knowledge_graph["ado_story_692945"] = {
      "id": "692945",
      "title": "User can reset password via email",
      "acceptance_criteria_text": "Given a registered user on the login page...",
      "sprint": "Sprint 14",
      "story_points": 5.0,
      "parent_epic_id": 689000,
      "child_tasks": [692946, 692947],
      "existing_test_coverage": [700100, 700101],
      "source": "ado_live",
      "fetched_at": "2026-02-25T..."
  }
  lens_recommendations append:
    - "Acceptance criteria defines 3 scenarios — generate 3 test methods"
    - "2 test cases already linked in ADO — verify before creating new ones"
    - "Parent epic #689000 — align area path to Authentication"

STEP 7 — Stage 4 Execution (TDDOrchestrator)
  Reads intel_context.ado_stories[0].acceptance_criteria
  Parses Given/When/Then blocks
  Generates failing test stubs → GREEN → REFACTOR
  (Future: auto-link new test cases back to ADO story via TestedBy relation)

══════════════════════════════════════════════════════════════════════════════
ADOContextEnricher — FULL SPECIFICATION
══════════════════════════════════════════════════════════════════════════════

File:     cortex/orchestrators/core/ado_context_enricher.py
Imports:  ADOWorkItemProvider, UserStoryContext
          UnifiedIntelligenceContext
          re, logging, os

Patterns (ordered by specificity — first match wins on ID extraction):
    FULL_URL_PATTERN = re.compile(
        r"dev\\.azure\\.com/[^/\\s]+/[^/\\s]+/_workitems/edit/(\\d+)",
        re.IGNORECASE
    )
    HASH_ID_PATTERN  = re.compile(r"#(\\d{4,7})")
    BARE_ID_PATTERN  = re.compile(r"\\b(\\d{5,7})\\b")

    CONTEXT_HINTS = {
        "user story", "work item", "ado", "azure devops",
        "story", "ticket", "task", "feature", "bug", "#"
    }

Class:
    class ADOContextEnricher:
        def __init__(self, provider: ADOWorkItemProvider | None = None):
            # Provider is optional; injected for testing (no env vars needed in tests)
            # When None, lazily instantiates from env vars in enrich()

        def detect_ado_references(self, request: str) -> list[int]:
            # Returns deduplicated, sorted list of ADO IDs found
            # Bare IDs only included when a CONTEXT_HINT is also in request
            # Deduplication: set() before return

        def enrich(
            self,
            request: str,
            intel_context: UnifiedIntelligenceContext,
        ) -> UnifiedIntelligenceContext:
            # 1. detect_ado_references(request) → ids
            # 2. If no ids: return intel_context unchanged (fast path)
            # 3. For each id:
            #    try:
            #        ctx = self._get_provider().fetch_story_context(str(id))
            #        intel_context.ado_stories.append(ctx)
            #    except KeyError:
            #        logger.warning("ADO story %d not found", id)
            #    except PermissionError:
            #        logger.error("ADO auth failed — check ADO_PAT")
            #    except Exception as e:
            #        logger.error("ADO enrichment failed for %d: %s", id, e)
            # 4. if intel_context.ado_stories:
            #        intel_context.enriched_sources.append("ado")
            # 5. return intel_context

        def _get_provider(self) -> ADOWorkItemProvider:
            # Lazy init from env vars
            # Cached on self._provider after first call

Hook site in InteractionOrchestrator.process_turn() (add ~5 lines):
    # After: lens_result = self.lens_orchestrator.analyze_file(...)
    # Before: intel_context = ... routing ...
    if not hasattr(self, "_ado_enricher"):
        self._ado_enricher = ADOContextEnricher()
    intel_context = self._ado_enricher.enrich(turn_request, intel_context)

══════════════════════════════════════════════════════════════════════════════
UnifiedIntelligenceContext — EXTENSION (additive, non-breaking)
══════════════════════════════════════════════════════════════════════════════

File:     cortex/intelligence/knowledge/unified_intelligence_context.py
Change:   Add two Optional fields to UnifiedIntelligenceContext dataclass

    ado_stories: List[UserStoryContext] = field(default_factory=list)
    # All UserStoryContext objects resolved this turn. Empty = no ADO refs.

    enriched_sources: List[str] = field(default_factory=list)
    # Tracks which enrichers ran: ["lens", "ado", ...]
    # Allows downstream orchestrators to check what context is available.

    ado_story_ids: List[int] = field(default_factory=list)
    # Raw IDs detected (for audit trail even if fetch failed)

These are Optional/defaulted — zero impact on existing code that doesn't use them.
All existing UnifiedIntelligenceContext usages continue to work unchanged.

══════════════════════════════════════════════════════════════════════════════
TDD IMPLEMENTATION ORDER (CORE-008 — RED → GREEN → REFACTOR)
══════════════════════════════════════════════════════════════════════════════

SEQUENCE:
  1. Write ALL 60 golden tests (RED — all fail)
  2. Implement Layer 1: ADOWorkItemProvider GREEN
     → tests 1-15 pass (test_ado_provider_truth.py)
  3. Implement Layer 2: ADOOrchestrator GREEN
     → tests 16-30 pass (test_ado_orchestrator_truth.py)
  4. Implement Layer 3: ADOContextEnricher GREEN
     → tests 31-45 pass (test_ado_context_enricher_truth.py)
  5. Wire InteractionOrchestrator hook + extend UnifiedIntelligenceContext
     → tests 46-60 pass (test_ado_e2e_pipeline_truth.py)
  6. Implement Layer 4: MCP tools (after all 60 pass)
  7. REFACTOR pass — clean up, type check, coverage ≥95%
  8. Submit to make test-batch — must appear in PASS column

══════════════════════════════════════════════════════════════════════════════
GOLDEN TEST COUNT SUMMARY
══════════════════════════════════════════════════════════════════════════════

  Layer            File                                   Tests  AC-IDs
  ───────────────────────────────────────────────────────────────────────────
  Provider         test_ado_provider_truth.py             15     AC-ADO-P-001..015
  Orchestrator     test_ado_orchestrator_truth.py         15     AC-ADO-O-001..015
  Enricher         test_ado_context_enricher_truth.py     15     AC-ADO-E-001..015
  E2E Pipeline     test_ado_e2e_pipeline_truth.py         15     AC-ADO-X-001..015
  ───────────────────────────────────────────────────────────────────────────
  TOTAL                                                   60

══════════════════════════════════════════════════════════════════════════════
ENV VAR REQUIREMENTS
══════════════════════════════════════════════════════════════════════════════

  Production:
    ADO_ORG_URL  = "https://dev.azure.com/HQY01"
    ADO_PAT      = "<PAT with Work Items Read + Project and Team Read>"
    ADO_PROJECT  = "Quality Engineering"  (or "V5" depending on context)

  Test (CI):
    ADO_SKIP_HEALTH_CHECK = "true"  (prevents real HTTP calls in unit tests)
    ADO_ORG_URL / ADO_PAT / ADO_PROJECT = set to dummy values for fixture tests
    Live integration tests use @pytest.mark.integration and are skipped in CI

  .gitignore:
    config.json (contains credentials — matches QEMetricsCollection pattern)

══════════════════════════════════════════════════════════════════════════════
FUTURE PHASES (out of scope for this implementation)
══════════════════════════════════════════════════════════════════════════════

  Phase 15+1: Write-back — update ADO story state from CORTEX
    PATCH /_apis/wit/workitems/{id}?api-version=7.1
    Body: [{"op": "replace", "path": "/fields/System.State", "value": "Resolved"}]
    PAT scope required: Work Items (Write)

  Phase 15+2: Auto-link test cases back to story after TDD GREEN
    POST /_apis/wit/workitems/{id}?api-version=7.1
    Body: [{"op": "add", "path": "/relations/-", "value": {"rel": "TestedBy-Reverse", ...}}]

  Phase 15+3: Sprint board awareness — pull all stories for current sprint
    WIQL: WHERE [System.IterationPath] = @CurrentIteration

  Phase 15+4: PR linkage — associate CORTEX code changes with ADO story
    Read linked PRs from linked_pr_ids; update PR description with story ref
"""
