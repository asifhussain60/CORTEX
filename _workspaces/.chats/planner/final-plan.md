# CORTEX Production Readiness — Final Holistic Plan

**Version:** 3.0 | **Date:** 2026-02-15 | **Author:** Asif Hussain
**Status:** APPROVED — Ready for Execution
**Authority:** PlanOrchestrator + LENSSynthesis
**Governance Rule:** CORE-055 (Pre-Execution Planning Completeness Gate)

---

## VISION

Unbreakable wiring, zero mocks, zero duplicates, singular execution paths.
Every test proves real systems work together — not that mock objects return expected values.

---

## CURRENT STATE (Verified 2026-02-15)

| Metric | Value |
|--------|-------|
| Tests collected | 16,224 |
| Tests passing | 908 |
| Tests failing | 5 |
| Tests skipped | 107 |
| Golden tests | 32 (8 files, all passing — but 7 of 8 use internal Mock classes) |
| Duplicate classes | IntentRouter exists in 2 locations (CORE-035 violation) |
| Stray .md in phases/ | 2 files (CORE-002 violation) |
| MEGA-B label collision | Phase 22 AND Phase 23 both claim MEGA-B |

### 5 Failing Tests (Must Fix Before Phase Execution)

| Test | Root Cause |
|------|-----------|
| test_no_wave_references_in_prompts | Nomenclature consistency — stale "wave" references in prompts |
| test_invalid_source_rejected | MasterOrchestrator enforcement — source validation |
| test_enh066_documentation_accuracy | MCP setup validation — documentation drift |
| test_render_phase_01_html | Phase detail generation — template/data mismatch |
| test_validate_html_structure | Phase detail generation — HTML structure validation |

---

## NEW GOVERNANCE RULE: CORE-055

**Name:** Pre-Execution Planning Completeness Gate
**Priority:** P0 | **Enforcement:** BLOCKING
**Note:** CORE-053 (CCL) and CORE-054 (MCP Wiring Validation) are already allocated in enforcement-patterns.yaml

| Aspect | Requirement |
|--------|-------------|
| **When** | Before ANY phase execution begins |
| **What** | Every phase MUST have ALL stages defined with: test count, file targets, acceptance criteria, estimated LOC, dependencies |
| **Holistic Review** | After all phases are planned, mandatory conflict/contradiction/regression check |
| **Clean Code Gate** | After each stage: full test suite, lint (zero errors), type hints, docstrings |
| **No Ad-Hoc Stages** | New stages CANNOT be added mid-phase. If scope changes, phase is replanned and re-reviewed first |
| **Tactical Adaptation** | Within-stage implementation details CAN adapt to reality. Stage structure stays locked. |
| **Complements** | CORE-042 (hierarchy), CORE-048 (validation gate), CORE-001 (incremental delivery) |

### CORE-028 Extension (Phase Naming Standards)

| Convention | Rule |
|------------|------|
| Phase YAML naming | `{NN}-{kebab-case-name}.yaml` (max 50 chars total) |
| Phase folders | `completed/`, `active/`, `planned/`, `deferred/`, `consolidated/` |
| No .md in phases/ | YAML only — descriptions go inside YAML `description` fields |
| Mega-phase labels | Sequential: MEGA-A, MEGA-B, MEGA-C, MEGA-D (no duplicates) |

---

## PHASE-END GATE (Mandatory After Every Stage)

| Check | Pass Criteria |
|-------|---------------|
| Full test suite | ≥ baseline (908 passing) + new phase tests |
| Lint | Zero ruff errors |
| Type hints | No new untyped public functions |
| Docstrings | No new undocumented public functions |
| Wiring | `__wiring_contract__.yaml` still valid |
| Duplicates | No new CORE-035 violations |
| AC Markers | AC_START and AC_COMPLETE present in SQLite |

---

## PHASE REGISTRY AFTER CLEANUP

| Phase | Name | Label | Status | Location |
|-------|------|-------|--------|----------|
| 02 | Registry Isolation | — | completed | `phases/completed/` |
| 09 | Unified Digest-Ingest Facade | — | completed | `phases/completed/` |
| 19 | Convergence Loop Holistic TDD | — | completed | `phases/completed/` |
| 20 | Workflow Intelligence Neurons | — | completed | `phases/completed/` |
| 01 | Business Wisdom Display | — | consolidated | `phases/consolidated/` |
| 12 | Knowledge Persistence | — | consolidated | `phases/consolidated/` |
| 16 | MCP Tools Documentation | — | consolidated | `phases/consolidated/` |
| 17 | Agent Architecture Redesign | — | consolidated | `phases/consolidated/` |
| 18 | IntentRouter Hardening | — | consolidated | `phases/consolidated/` |
| **21** | **Intelligence & Learning Core** | **MEGA-A** | **active** | `phases/active/` |
| **22** | **Developer Experience & Tooling** | **MEGA-B** | **planned** | `phases/planned/` |
| **23** | **STS Knowledge Synthesis** | **MEGA-C** | **active** | `phases/active/` |
| **24** | **Production Verification Harness** | **MEGA-D** | **planned** | `phases/planned/` |
| **25** | **Stabilization & Duplicate Elimination** | **MEGA-E** | **planned** | `phases/planned/` |
| 03-08, 11, 13-15 | Various domain expansions | — | deferred | `phases/deferred/` |

---

## EXECUTION ORDER

| Order | Phase | Priority | Sessions | Dependencies |
|-------|-------|----------|----------|--------------|
| 0 | Registry Cleanup | P0 | 1 | None |
| 1 | Phase 25 (MEGA-E): Stabilization | P0 | 2-3 | Registry cleanup |
| 2 | Phase 24 (MEGA-D): Verification Harness | P0 | 7-9 | Phase 25 complete |
| 3 | Phase 21 (MEGA-A): Intelligence Core | P0 | 7-10 | Phase 24 S2 complete |
| 4 | Phase 23 (MEGA-C): STS Knowledge | P1 | 14-18 days | Phase 21 complete |
| 5 | Phase 22 (MEGA-B): Developer Experience | P1 | 2-3 weeks | Phase 21 complete |
| 6+ | Deferred phases (03-08, 11, 13-15) | P2 | TBD | MEGA-A through MEGA-E complete |

---

## PHASE 0: REGISTRY CLEANUP (Pre-Requisite)

**Sessions:** 1 | **Tests:** 0 | **Risk:** Zero (housekeeping only)

| Stage | Action | Deliverable |
|-------|--------|-------------|
| S1 | Create folder structure | `completed/`, `active/`, `planned/`, `deferred/`, `consolidated/` under phases/ |
| S2 | Move phase YAMLs to status subfolders | All 22 YAMLs in correct subfolder, content unchanged |
| S3 | Remove stray .md files | Delete PHASE-23-OVERVIEW.md, active/phase-23-megab-*.md |
| S4 | Remove `_views/` directory | Folder structure replaces it — single source |
| S5 | Fix MEGA labeling | Phase 22 = MEGA-B, Phase 23 = MEGA-C (no collision) |
| S6 | Register CORE-055 in core-rules.yaml | New governance rule in registry |
| S7 | Update master-index.yaml | Paths reflect new folder structure |
| S8 | Register Phase 24 + Phase 25 | New phase YAMLs in phases/planned/ |

---

## PHASE 25: STABILIZATION & DUPLICATE ELIMINATION (MEGA-E)

**Sessions:** 2-3 | **Tests:** Fix 5 + eliminate duplicates | **Risk:** Low
**Why First:** You cannot build a verification harness on a broken foundation. Fix the 5 failing tests, eliminate duplicate class definitions, and establish a clean honest baseline BEFORE any new test infrastructure.

| Stage | Name | Deliverable | Acceptance Criteria |
|-------|------|-------------|---------------------|
| S1 | Fix 5 Failing Tests | All 5 tests passing | 908 → 913 passing, 0 failing |
| S2 | Duplicate IntentRouter Elimination | Single canonical IntentRouter | `cortex.brain.domain_brain.nlp_handler_router.IntentRouter` deprecated or removed; only `cortex.orchestrators.core.intent_router.IntentRouter` remains |
| S3 | Wiring Contract Audit | Verify all 28 wiring entries point to importable real classes | `python -c "from {module} import {class_name}"` succeeds for every entry |
| S4 | Regression Baseline Capture | Record passing count as immutable baseline | Baseline file: tests/baseline.json with count + timestamp |
| S5 | Install hypothesis | Added to requirements.txt, verified | `python -c "import hypothesis"` succeeds |
| **GATE** | Phase-End Gate | All checks pass | Full suite ≥ 913, zero lint, wiring valid, AC markers |

---

## PHASE 24: PRODUCTION VERIFICATION HARNESS (MEGA-D)

**Sessions:** 7-9 | **Tests:** 200-260 new | **Risk:** Medium (additive only)
**Core Principle:** ZERO MOCKS. Every golden test imports and exercises REAL CORTEX classes. No `class Mock*` patterns. Tests that need isolation use real lightweight instances, not simulations.

### Mock Elimination Strategy

The existing 8 golden test files (32 tests) contain `class Mock*` in 7 of 8 files. These must be rewritten to import real classes:

| Current Mock | Replacement (Real Import) |
|-------------|--------------------------|
| MockGovernanceEngine | `cortex.orchestrators.core.enforcement_orchestrator.EnforcementOrchestrator` |
| MockMCPGateway | `cortex.mcp.server` + real tool registry |
| MockLENSPipeline | `cortex.domain_brain.lens_integration.LENSSynthesis` |
| MockTierCascade | `cortex.core.database.tier_enforcement_queries` + real tier lookup |
| MockConflictResolver | `cortex.orchestrators.coherence` (real coherence module) |
| MockCompanyOverride | `cortex.core.event_bus.EventBus` (already real — keep) |
| MockMultiAnalyzer | Real analyzer chain from cortex_lens |

### Stage Breakdown

| Stage | Name | Tests | Status | Key Files |
|-------|------|-------|--------|-----------|
| S1 | Rewrite Golden Tests (Zero Mock) | Rewrite 32 existing → real imports | ⚪ Planned | tests/golden/*.py |
| S2 | Governance Enforcement E2E | 60-80 new | ⚪ Planned | tests/golden/governance/ |
| S3 | Intelligence Pipeline E2E | 50-65 new | ⚪ Planned | tests/golden/intelligence/ |
| S4 | TDDOrchestrator + LENSSynthesis | 45-55 new | ⚪ Planned | tests/golden/orchestrators/ |
| S5 | Context Management & Planning | 25-35 new | ⚪ Planned | tests/golden/planning/ |
| S6 | MasterOrchestrator Deep Integration | 20 new | ⚪ Planned | tests/golden/orchestrators/master/ |
| S7 | MCP Gateway Real E2E | 10-15 new | ⚪ Planned | tests/golden/mcp/ |
| **GATE** | Phase-End Gate | All checks pass | — | Full suite ≥ baseline + 200, zero lint, wiring valid |

### S1 Detail: Golden Test Rewrite (Critical Path)

Each existing golden test file gets rewritten to:
1. Remove `class Mock*` definitions
2. Import real CORTEX classes
3. Call real methods (e.g., `EnforcementOrchestrator().validate_operation()` not `MockGovernanceEngine().check()`)
4. Assert on real return types and real behavior
5. Maintain the same test count (32) — same coverage, real wiring

### S2 Detail: Governance Enforcement E2E (60-80 tests)

| Area | Tests | What It Proves |
|------|-------|----------------|
| EnforcementOrchestrator with 9 real agents | 15 | All 9 agents instantiate, validate, return correct types |
| CORE rule enforcement chain | 15 | CORE-008 blocks missing tests, CORE-002 blocks .md generation, CORE-028 blocks bad names |
| GovernanceDatabaseManager SQLite persistence | 10 | Violations write to SQLite, queries return correct data |
| Tier 0/1/2 cascade | 10 | Tier 0 = BLOCKED, Tier 1 = WARNING, Tier 2 = INFO — no crossover |
| AC marker audit trail | 10 | AC_START → AC_COMPLETE lifecycle, SQLite verification |

### S3 Detail: Intelligence Pipeline E2E (50-65 tests)

| Area | Tests | What It Proves |
|------|-------|----------------|
| Knowledge persistence service | 15 | Real data persists to SQLite, retrieves correctly |
| Learning modules (pattern capture) | 15 | Real patterns detected from real code samples |
| Perception → Reasoning → Action chain | 10 | Brain tier pipeline works end-to-end with real inputs |
| Intelligence neurons | 10 | Convergence + workflow neurons fire with real event bus |

### S4 Detail: TDDOrchestrator + LENSSynthesis (45-55 tests)

| Area | Tests | What It Proves |
|------|-------|----------------|
| TDDOrchestrator RED→GREEN→REFACTOR | 15 | Real TDD cycle executes against real test files |
| LENSSynthesis Language→Examination→Navigation→Synthesis | 15 | Real LENS pipeline produces real analysis |
| IntentRouter (singular, canonical) | 10 | Single IntentRouter routes all intents correctly |
| Cross-orchestrator delegation | 5-15 | Master → Intent → TDD/LENS → result chain works |

### S5 Detail: Context Management & Planning (25-35 tests)

| Area | Tests | What It Proves |
|------|-------|----------------|
| AutonomousPhaseExecutor | 10 | Phase execution respects CORE-055 stage manifest |
| Checkpoint/resume system | 10 | Interrupted phases resume from correct point |
| Context bundle system | 5-15 | Large orchestrators load within context limits |

### S6 Detail: MasterOrchestrator Deep Integration (20 tests)

| Area | Tests | What It Proves |
|------|-------|----------------|
| Full request lifecycle | 10 | Request → route → execute → respond chain works |
| Orchestrator delegation | 5 | Master correctly delegates to all registered orchestrators |
| Error propagation | 5 | Failures bubble up with correct context, no silent swallowing |

### S7 Detail: MCP Gateway Real E2E (10-15 tests)

| Area | Tests | What It Proves |
|------|-------|----------------|
| All 10 production MCP tools | 10 | Each tool callable through gateway, returns valid response |
| Tool routing | 3-5 | Gateway routes to correct handler, rejects unknown tools |

---

## PHASE 21: INTELLIGENCE & LEARNING CORE (MEGA-A)

**Status:** Active (partial progress)
**Sessions:** 7-10 days | **Tests:** 150
**Depends on:** Phase 25 complete, Phase 24 S2 complete (governance verification proves foundation)

Existing YAML spec at `21-intelligence-learning-core-mega.yaml` — no changes to stage structure.
Phase 24 S3 (Intelligence Pipeline E2E) validates this phase's deliverables.

---

## PHASE 23: STS KNOWLEDGE SYNTHESIS (MEGA-C)

**Status:** Active (S1-S3 progress)
**Sessions:** 14-18 days | **Tests:** 70+
**Depends on:** Phase 21 complete
**Label fix:** Renamed from MEGA-B to MEGA-C (collision resolved)

Existing YAML spec at `23-sts-knowledge-synthesis-mega.yaml` — label updated, no stage changes.

---

## PHASE 22: DEVELOPER EXPERIENCE & TOOLING (MEGA-B)

**Status:** Planned
**Sessions:** 2-3 weeks | **Tests:** 100+
**Depends on:** Phase 21 complete

Existing YAML spec at `22-developer-experience-tooling-mega.yaml` — no changes.

---

## NON-REGRESSION GUARANTEE

| Check | Status |
|-------|--------|
| Existing 16,224 test collection | Not touched — baseline captured in Phase 25 S4 |
| Existing 908 passing tests | Phase 25 fixes 5 failures → 913+ baseline, never drops below |
| Existing phase YAMLs | Moved to subfolders, content unchanged |
| Existing production code | Zero changes in Phase 0 + Phase 24 (test-only, additive) |
| Existing wiring | `__wiring_contract__.yaml` validated, not modified |
| Existing governance rules | CORE-028 extended (not replaced), CORE-055 is new |
| Golden test rewrite (S1) | Same 32 tests, same coverage — real imports replace mocks |

---

## RESOURCE SUMMARY

| Phase | Sessions | Tests | Key Deliverable |
|-------|----------|-------|-----------------|
| Registry Cleanup (Phase 0) | 1 | 0 | Clean folder structure, CORE-055 registered |
| Phase 25 (MEGA-E) | 2-3 | Fix 5 + baseline | Clean foundation, zero duplicates, honest baseline |
| Phase 24 (MEGA-D) | 7-9 | 200-260 | Zero-mock verification harness |
| Phase 21 (MEGA-A) | 7-10 days | 150 | Intelligence & learning system |
| Phase 23 (MEGA-C) | 14-18 days | 70+ | STS knowledge engine |
| Phase 22 (MEGA-B) | 2-3 weeks | 100+ | Production DX polish |
| **Total** | **~10-12 weeks** | **~520-580+** | **Production-ready CORTEX** |

---

## CONFLICT/CONTRADICTION CHECK (CORE-055 Compliance)

| Check | Result |
|-------|--------|
| Phase 25 targets overlap Phase 24? | ❌ No — Phase 25 fixes existing code; Phase 24 adds new tests |
| Phase 24 golden rewrite conflicts with Phase 25 baseline? | ❌ No — Phase 25 completes first, baseline set, then Phase 24 rewrites |
| Phase 21 and Phase 24 S3 conflict? | ❌ No — Phase 24 S3 validates Phase 21 deliverables, runs after |
| CORE-055 conflicts with CORE-001 (incremental)? | ❌ No — complementary: plan fully, deliver incrementally |
| CORE-055 conflicts with CORE-048 (validation gate)? | ❌ No — CORE-048 validates individual operations; CORE-055 validates phase plans |
| Any two phases target the same files? | ❌ No — each phase has distinct file targets |
| Mock elimination breaks existing 32 golden tests temporarily? | ⚠️ Yes — managed: S1 rewrites all 8 files atomically per file, gate verifies after |

---

## EXECUTION COMMAND

```
Start: Phase 0 (Registry Cleanup) — zero regression risk, pure housekeeping
Then: Phase 25 S1 (Fix 5 failing tests) — establishes honest baseline
```