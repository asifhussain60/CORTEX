"""
PHASE 54-A WIRING MANIFEST
==========================

Integration Map: Phase 54-A (Repository Onboarding Incremental Refactoring)
with existing CORTEX orchestrators and infrastructure.

TDD Framework: 66 tests ready for implementation
Platform Support: Windows, macOS, Linux
Date: 2026-02-09
Authority: cortex-architect.prompt.md v7.7 (MCP-FIRST SaaS Architecture)

SECTION 1: COMPONENT DEPENDENCIES
==================================

Phase 54-A Components:
├── Stage 1: OnboardingUseCases (6 use cases, 41 tests)
│   ├── LoadRepoOverviewUseCase
│   ├── AnalyzeSecurityThreatsUseCase
│   ├── GenerateBusinessNarrativeUseCase
│   ├── BuildDependencyGraphUseCase
│   ├── RenderDashboardJSONUseCase
│   └── UpdateLandingPageUseCase
│
├── Stage 2: Repository Pattern (15 tests)
│   ├── JSONProfileRepository
│   └── RepositoryInterface
│
└── Stage 3: Jinja2 MVP (10 tests)
    ├── DashboardRenderer
    └── onboarding_dashboard.html.j2

ORCHESTRATOR INTEGRATIONS
==========================

Phase 54-A integrates with these existing phases:

1. Phase 28: RepositoryOnboardingOrchestrator (SOURCE)
   - Current implementation: 2,418 LOC monolith
   - Extraction target: 6 independent use cases
   - Dependency: Feeds data to Phase 54-A use cases
   - Integration point: Extract without breaking current flow

2. Phase 20: LENS Synthesis (LENS INTEGRATION)
   - LENSOrchestrator provides code intelligence
   - Phase 54-A imports: SecurityRisk, DependencyGraph models
   - Use case: AnalyzeSecurityThreatsUseCase delegates to LENS
   - Use case: RenderDashboardJSONUseCase converts LENS output

3. Phase 46: Infrastructure Discovery (INFRASTRUCTURE CONTEXT)
   - Provides: GitHub API client, environment discovery
   - Use case: LoadRepoOverviewUseCase reads GitHub metadata
   - Integration: Phase 46 GitHub client optional (graceful fallback)

4. Phase 43: MCP-First Enforcement (MCP TOOLS)
   - Exposes onboarding via MCP after Phase 54-A completes
   - Tool: cortex_onboard_repository (uses extracted use cases)
   - Prerequisite: Phase 54-A wiring complete

5. Phase 48: Holistic Validation (PRE-FLIGHT GATE)
   - Validates Phase 54-A implementation before merge
   - Checks: 66 tests passing, 90% coverage, no regressions
   - Challenge: Mandatory review of use case extraction

6. Phase 49: Context Crystallization Layer (CCL)
   - Provides: RulesCache, LENS pre-warming
   - Benefit: Phase 54-A dashboards render faster (CCL context)
   - Async integration: DashboardRenderer uses pre-warmed LENS

7. Phase 47: Company/CORTEX Separation (REGISTRY STRUCTURE)
   - Provides: Registry patterns for profile storage
   - Repository pattern: JSONProfileRepository follows company/cortex model
   - Integration: Supports future multi-tenant profile isolation

SECTION 2: DATA FLOW
====================

┌─────────────────────────────────────────────────────────────────┐
│ USER TRIGGER: cortex_onboard_repository(repo_path, options)    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │ RepositoryOnboardingOrchestrator         │ (Phase 28)
        │ (existing 2,418 LOC coordinator)         │
        └──────────────────┬───────────────────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
    ┌─────────────────────┐  ┌──────────────────────┐
    │ S1: Load Overview   │  │ S2: Repository Repo  │
    │ (use case extracted)│  │ (stores profiles)    │
    └────────┬────────────┘  └──────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ S2: Analyze Security Threats        │
    │ (LENS SecurityRisk models)          │
    │ ↓ delegates to LENS Phase 20        │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ S3: Generate Business Narrative     │
    │ (business language orchestrator)    │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ S4: Build Dependency Graph          │
    │ (PackageDependency models)          │
    │ ↓ reads from package manifest       │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ S5: Render Dashboard JSON           │
    │ (RepoDashboardModel v3.0)           │
    │ ↓ converts all context to model     │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ S6: Update Landing Page             │
    │ (LandingPageEntry model)            │
    │ ↓ adds hub entry                    │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ DASHBOARD RENDERER (S3 - MVP)       │
    │ - Loads onboarding_dashboard.html.j2│
    │ - Applies 3 custom filters          │
    │ - Renders HTML from dashboard model │
    │ ↓ uses CCL pre-warmed context       │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ RETURN: Dashboard HTML + Profile    │
    └─────────────────────────────────────┘

SECTION 3: REPOSITORY PATTERN INTEGRATION
==========================================

JSONProfileRepository (S2 - Repository Pattern)

Interface:
  - get_by_name(repo_name: str) → OnboardingProfile
  - save(profile: dict) → str (file path)
  - delete(repo_name: str) → bool
  - list_all() → List[OnboardingProfile]
  - exists(repo_name: str) → bool

Storage Path: cortex-registry/company/onboarding_profiles/

Integration Points:
  1. Phase 28: RepositoryOnboardingOrchestrator uses repo.save(profile)
  2. Phase 47: Company registry isolation (storage in company/)
  3. Future Phase 54-B: SQLite migration (interface unchanged)
  4. Future Phase 54-C: API backend (interface unchanged)

Benefits:
  ✅ Abstraction: Can swap JSON → SQLite → API later
  ✅ Testability: Mock repository in tests
  ✅ Encapsulation: Hide storage implementation
  ✅ MCP-FIRST: Accessible via cortex_onboard_repository

SECTION 4: JINJA2 TEMPLATE SYSTEM (MVP)
========================================

DashboardRenderer Orchestrator (S3)

Single Template MVP: onboarding_dashboard.html.j2

Features:
  - Renders dashboard HTML from RepoDashboardModel
  - 3 custom filters: format_number, round_decimal, format_date
  - Auto-escape enabled (security)
  - Template inheritance ready (future expansion)

Integration:
  1. Input: RepoDashboardModel from RenderDashboardJSONUseCase
  2. Processing: DashboardRenderer.render(template_name, context)
  3. Output: HTML string for browser display
  4. Future: Template library (S4 phase 54-B)

Benefits:
  ✅ Designer-friendly: Non-technical UI editing
  ✅ Separation: Business logic separate from presentation
  ✅ Extensible: Component library ready
  ✅ DRY: Template inheritance eliminates duplication

SECTION 5: MCP TOOL EXPOSURE (PHASE 43)
========================================

After Phase 54-A completes:

Tool: cortex_onboard_repository
Module: cortex.mcp.tools.onboarding
Parameters:
  - repo_path: str (required)
  - repo_name: str (optional, derived from path)
  - analysis_depth: "quick" | "full" (default: "full")
  - cache_enabled: bool (default: true)

Implementation:
  1. Orchestrator: RepositoryOnboardingOrchestrator (Phase 28)
  2. Use Cases: 6 extracted cases (Phase 54-A S1)
  3. Repository: JSONProfileRepository (Phase 54-A S2)
  4. Renderer: DashboardRenderer (Phase 54-A S3)

Flow: cortex_onboard_repository → MCP adapter → orchestrator → use cases → renderer

SECTION 6: TEST INTEGRATION
============================

TDD Framework (66 tests ready):

Stage 1 Tests (41 tests):
  - test_load_repo_overview_use_case.py (5 tests)
  - test_analyze_security_threats_use_case.py (8 tests)
  - test_generate_business_narrative_use_case.py (6 tests)
  - test_build_dependency_graph_use_case.py (7 tests)
  - test_render_dashboard_json_use_case.py (10 tests)
  - test_update_landing_page_use_case.py (5 tests)

Stage 2 Tests (15 tests):
  - test_json_profile_repository.py (15 tests)
    ├── CRUD operations (5 tests)
    ├── Validation (2 tests)
    ├── Error handling (5 tests)
    └── Integration (3 tests)

Stage 3 Tests (10 tests):
  - test_dashboard_renderer.py (10 tests)
    ├── Jinja2 setup (3 tests)
    ├── Template rendering (3 tests)
    ├── Custom filters (3 tests)
    └── Integration (1 test)

Total: 66 tests
Coverage Target: 90%
Platform Support: Windows, macOS, Linux

SECTION 7: PHASE DEPENDENCIES GRAPH
====================================

Phase 54-A Dependency Graph:

        ┌─────────────────────┐
        │ Phase 28            │
        │ Repository          │ (SOURCE - feeds data)
        │ Onboarding Orch.     │
        └────────┬────────────┘
                 │ extracts to
                 ▼
        ┌─────────────────────┐
        │ Phase 54-A (THIS)   │
        │ - S1: Use Cases     │ (14 hours)
        │ - S2: Repository    │ (66 tests)
        │ - S3: Jinja2 MVP    │ (90% coverage)
        └────────┬────────────┘
                 │ enables
        ┌────────┴─────────────────────┐
        │                              │
        ▼                              ▼
    ┌──────────────────┐      ┌──────────────────┐
    │ Phase 43         │      │ Phase 54-B       │
    │ MCP-FIRST        │      │ Template Expand. │
    │ (exposes tools)  │      │ (deferred)       │
    └──────────────────┘      └──────────────────┘

Blocked By: None (Phase 28 already running)
Blocks: None directly (Phase 43 integration optional)
Enhances: Phase 28 (RepositoryOnboardingOrchestrator modularity)

SECTION 8: ROLLBACK PROCEDURE
==============================

If Phase 54-A fails at any stage:

Stage 1 Rollback (Use Cases):
  1. git revert <commits>
  2. Delete cortex/orchestrators/support/onboarding_use_cases/
  3. Delete tests/orchestrators/support/onboarding_use_cases/
  4. Restore Phase 28 to pre-extraction state

Stage 2 Rollback (Repository):
  1. git revert <commits>
  2. Delete cortex/repositories/
  3. Delete tests/repositories/
  4. Phase 28 falls back to inline dict storage

Stage 3 Rollback (Template):
  1. git revert <commits>
  2. Delete cortex/templates/dashboards/
  3. Phase 28 falls back to HTML string generation

Complete Rollback:
  git revert <phase-54-a-start>..<phase-54-a-end>
  pytest tests/ -k "not phase_54_a"  # Verify regressions

SECTION 9: WINDOWS PLATFORM SUPPORT
====================================

Platform Compatibility Established:

✅ Path handling: WindowsPathCompatibility in cortex_brain/tier0/
✅ File operations: pathlib.Path (cross-platform)
✅ Repository: JSONProfileRepository Windows-tested
✅ Tests: pytest Windows-compatible
✅ Jinja2: Template library Windows-compatible
✅ Registry: YAML parsing platform-agnostic

Tested on Windows:
  - Git operations (rebase, push, pull)
  - Path normalization (backslash vs forward slash)
  - File I/O (JSON profile storage)
  - Jinja2 template rendering

SECTION 10: SUCCESS CRITERIA
=============================

Phase 54-A is complete when:

✅ All 66 tests passing (41 S1 + 15 S2 + 10 S3)
✅ 90% code coverage achieved
✅ Zero regressions (515+ existing tests still passing)
✅ Use cases extract correctly (SOLID compliance verified)
✅ Repository pattern abstracts storage (interface validated)
✅ Jinja2 MVP renders dashboard (template system proven)
✅ Windows platform tracking maintained
✅ Git history clean (no merge conflicts)
✅ Registry updated with completion status
✅ Audit trail documented (AC markers logged)

SECTION 11: NEXT PHASES (DEFERRED)
===================================

Phase 54-B: Template Expansion (8 hours)
  - Component library (dashboard_components/*.j2)
  - Template inheritance
  - Advanced Jinja2 filters
  - Multi-language support
  Trigger: Designer feedback on MVP template

Phase 54-C: Performance Optimization (12 hours)
  - Benchmark ENH-042 cache
  - Tune cache TTL and eviction policies
  - Profile onboarding bottlenecks
  Trigger: User reports performance issues

Phase 54-D: Orchestrator Coordinator (8 hours)
  - Refactor Phase 28 to 500 LOC
  - Wire use cases via dependency injection
  - Remove legacy helper methods
  Trigger: Orchestrator maintenance becomes painful

Phase 54-E: Advanced Patterns (20 hours)
  - TDD state machine (if phase transitions complex)
  - Plugin registry (if 4th language requested)
  - Batch optimization (if performance critical)
  Trigger: Specific pain points in production

---
End of Phase 54-A Wiring Manifest
Date: 2026-02-09
Authority: Asif Hussain (CORTEX Architect)
Status: READY FOR IMPLEMENTATION
"""
