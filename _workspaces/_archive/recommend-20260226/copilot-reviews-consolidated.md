# CORTEX Independent Reviews — Consolidated Canon
**Consolidated:** 2026-02-24 | **Source reviews:** 01–05 | **Authority:** Gap capture for Phase 64 planning

> All five prior reviews (copilot-review.md through copilot-review05.md) are consolidated here.
> Deleted source files. This file is the single SSOT for all historical gap findings.
> Gaps are captured as golden-test-harnessed acceptance criteria in `_cortex-master/phases/`.

---

## Score Trajectory

| Review | Score | Key Finding |
|--------|-------|-------------|
| Review 01 | 6.2/10 | Baseline — fractured orchestrator protocol (3 base class patterns, 30+ bare classes), LENS/KnSynth only in MasterOrchestrator, domain tier intelligence-isolated, 144 silent `ImportError` suppressions, knowledge best-practices directories empty |
| Review 02 | 6.5/10 | OrchestratorProtocolMixin rollout began; `core/core` double-nesting identified as root cause of 3-path IOrchestrator; 9 duplicate `AuditEntry` classes; 2 competing `Result/Ok/Err` families; 2 `OperationMode` enums; documentation vs. reality gap (docs say "17 wired / OrchestratorBase" — reality: 124 classes / 10 dirs, 2 use OrchestratorBase) |
| Review 03 | 5.8/10 | Enterprise SaaS readiness: no billing, no real auth in MCP path, tenant middleware exists but not wired to server.py; 124 orchestrator classes vs "17 wired" in docs; 874 `except ImportError` silences; MasterOrchestrator 5,087 lines (god object); 373 YAML + 1,346 Python files; 103+ self-refactoring phases |
| Review 04 | 7.0/10 | `core/core` eliminated ✅, `AuditEntry` canonical ✅, `Result/Ok/Err` canonical ✅, `OperationMode` unified ✅, `IOrchestrator` single path ✅, smoke tests green ✅, `tier1_learned` populated ✅, 11 domain LENS hooks added ✅; remaining: 151 silent ImportError, MCP auth not wired, 24 orchestrators without mixin, LENS domain calls still conditional/stub |
| Review 05 | 7.3/10 | Knowledge unified 30/30 YAMLs ✅, `KnowledgeRegistryProxy` dual-root ✅, `best_practices` package populated ✅, `MasterOrchestrator` wired to proxy ✅; remaining open: MCP auth (ship-blocker), 151 silent imports, 24 un-mixed orchestrators, MasterOrchestrator still 5,095 lines, domain LENS calls still stubs in practice |

---

## Confirmed Fixes (All Resolved Before Phase 64)

| # | Issue | Resolution |
|---|-------|-----------|
| F1 | `core/core` double-nesting | ✅ Eliminated (Phase 62a/b — 63 refs swept) |
| F2 | 9 `AuditEntry` duplicates | ✅ 1 canonical `cortex.core.audit_models.AuditEntry` |
| F3 | 2 `Result/Ok/Err` families | ✅ `cortex.core.result` is sole path, 0 `core.core.result` refs |
| F4 | 2 `OperationMode` enums | ✅ 1 definition in `cortex.core.interfaces.i_orchestrator` |
| F5 | 3-path `IOrchestrator` hydra | ✅ Single `cortex.core.interfaces.i_orchestrator` |
| F6 | Smoke tests failing | ✅ Green — 1,365+ passed |
| F7 | `tier1_learned` empty | ✅ Populated with cleaners, governance, templates |
| F8 | Knowledge fragmented (11/30 visible) | ✅ 30/30 via `KnowledgeRegistryProxy` dual-root |
| F9 | `best-practices` ghost dirs | ✅ `best_practices` package, proxy-backed sub-packages |
| F10 | Domain tier zero LENS hooks | ✅ 44/68 orchestrators now extend `OrchestratorProtocolMixin` |

---

## Open Gaps — Golden Test Acceptance Criteria

Each gap below is captured as an acceptance criterion for Phase 64 (`_cortex-master/phases/planned/phase-64-unified-brain-golden-coverage.yaml`).

### GAP-64-01 — Workflow Template Runtime Execution
**Source:** Reviews 01, 02 (structural wiring gap); chat01.md (workflow templates not in golden tests)
**Symptom:** `test_workflow_templates_golden.py` validates schema only — `WorkflowRuntime`, `StepStateMachine`, `ConvergenceLoopExecutor` are never invoked in any golden test.
**Acceptance Criteria (Golden Test):**
- `AC-64-01-A`: `test_workflow_runtime_golden.py::test_step_state_machine_executes_steps` — given a Phase 22 template, `StepStateMachine.execute()` runs all steps, emits AC markers, returns `COMPLETE` state
- `AC-64-01-B`: `test_workflow_runtime_golden.py::test_convergence_loop_executes_until_success` — `ConvergenceLoopExecutor` loops detect→fix→rescan, terminates when p0=0, p1=0
- `AC-64-01-C`: `test_workflow_runtime_golden.py::test_workflow_runtime_persists_to_sqlite` — execution writes `workflow_runs` rows to `.cortex-runtime/traces/orchestrator-traces.db`

### GAP-64-02 — Stage 0 Governance Audit (No Golden Coverage)
**Source:** Review 02 (governance self-compliance gap); chat01.md analysis
**Symptom:** `RequestRephraseOrchestrator._run_stage_0_audit()` has zero golden tests. CORE-002 (md scope), CORE-008 (TDD bypass) violation detection is unverified at golden tier.
**Acceptance Criteria (Golden Test):**
- `AC-64-02-A`: `test_execution_modes_golden.py::test_stage0_detects_md_file_creation_outside_github` — request containing "create report.md" triggers CORE-002 violation inline
- `AC-64-02-B`: `test_execution_modes_golden.py::test_stage0_detects_tdd_bypass` — request containing "skip tests" triggers CORE-008 flag before routing
- `AC-64-02-C`: `test_execution_modes_golden.py::test_stage0_passes_clean_request` — valid IMPLEMENT request passes Stage 0 with no violations injected

### GAP-64-03 — Response Template Rendering (Unit Only, No E2E)
**Source:** Review 02 (cross-cutting wiring matrix), chat01.md analysis
**Symptom:** `response_template_generator.py` and `template_engine.py` only have unit tests in `tests/unit/brain/core/`. No golden test verifies a full request produces a response with canonical header + sections in VSCode Copilot Chat format.
**Acceptance Criteria (Golden Test):**
- `AC-64-03-A`: `test_response_templates_golden.py::test_implement_mode_response_has_canonical_header` — IMPLEMENT intent produces response with `**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅`
- `AC-64-03-B`: `test_response_templates_golden.py::test_audit_mode_response_has_violation_table` — AUDIT intent produces response with inline violations table (P0/P1/P2 columns)
- `AC-64-03-C`: `test_response_templates_golden.py::test_all_modes_have_progress_bar` — all 13 execution modes produce response containing exactly 10-block progress bar format

### GAP-64-04 — 13 Execution Modes — No Full-Chain Golden
**Source:** Reviews 01–04 (cross-cutting utilization ~38%); chat01.md analysis
**Symptom:** IntentRouter routes correctly for 13 modes — but zero golden tests verify the full chain (request → Stage 0 → IntentRouter → Orchestrator → LENS → Response Template → AC_COMPLETE) for any mode.
**Acceptance Criteria (Golden Test):**
- `AC-64-04-A`: `test_execution_modes_golden.py::test_implement_full_chain[IMPLEMENT]` — request "build feature X" traverses full chain, produces TDDOrchestrator invocation, AC_COMPLETE in trace
- `AC-64-04-B`: `test_execution_modes_golden.py::test_audit_full_chain[AUDIT]` — `/audit` traverses to AuditCoordinator, produces violations inline, AC_COMPLETE
- `AC-64-04-C`: `test_execution_modes_golden.py::test_golden_test_intent_routes[GOLDEN_TEST]` — "review golden tests" routes to GOLDEN_TEST intent, correct orchestrator delegated
- `AC-64-04-D`: Parametrized across all 13 modes + GOLDEN_TEST (14 total)

### GAP-64-05 — TestValueScorer Not Self-Validated
**Source:** Reviews 01, 02 (test coverage dimension); chat01.md analysis
**Symptom:** `TestValueScorer` and `QualityGate` in `cortex/orchestrators/intelligence/test_value_scorer.py` are not scored against their own criteria. Scorer does not include `workflow_template`, `response_template`, or `trace_assertion` signals.
**Acceptance Criteria (Golden Test):**
- `AC-64-05-A`: `test_scorer_self_golden.py::test_scorer_awards_workflow_template_signal` — test containing "workflow template" keyword scores ≥ 1 additional point vs plain assertion test
- `AC-64-05-B`: `test_scorer_self_golden.py::test_scorer_awards_trace_assertion_signal` — test asserting AC_START/AC_COMPLETE in SQLite scores ≥ 1 additional point
- `AC-64-05-C`: `test_scorer_self_golden.py::test_cortex_own_tests_meet_threshold` — running scorer on `tests/golden/` confirms ≥90% of golden tests score ≥7 (KEEP threshold)

### GAP-64-06 — 26 MCP Tools — No Operation-Level Golden
**Source:** Reviews 01–04 (MCP tool layer 7/10 but no E2E operation tests); chat01.md analysis
**Symptom:** `test_mcp_e2e_truth.py` tests init/registry only. No golden test calls an actual MCP tool operation end-to-end (e.g., `cortex_refactor`, `cortex_onboard`, `cortex_vacuum`, `cortex_metrics`, `cortex_knowledge`).
**Acceptance Criteria (Golden Test):**
- `AC-64-06-A`: `test_mcp_operations_golden.py::test_cortex_vacuum_operation_returns_result` — `cortex_vacuum` op dispatched, returns structured result dict with `files_archived` count
- `AC-64-06-B`: `test_mcp_operations_golden.py::test_cortex_knowledge_query_returns_entries` — `cortex_knowledge` query returns ≥1 entry from the 30-entry unified proxy
- `AC-64-06-C`: `test_mcp_operations_golden.py::test_all_26_tools_importable` — all 26 registered MCP tools import without error and return non-None from their handler factory

### GAP-64-07 — DebuggerOrchestrator + 4 Strategies — No Golden
**Source:** Reviews 01, 04 (cross-cutting wiring matrix); chat01.md analysis
**Symptom:** `DebuggerOrchestrator` and its 4 debug strategies (`test_failure_strategy`, `governance_violation_strategy`, `refactor_regression_strategy`, `marker_injection_engine`) have zero golden test coverage.
**Acceptance Criteria (Golden Test):**
- `AC-64-07-A`: `test_debug_mode_golden.py::test_debug_mode_selects_correct_strategy` — DEBUG intent with "test failure" context routes to `TestFailureStrategy`, produces fix plan
- `AC-64-07-B`: `test_debug_mode_golden.py::test_debug_mode_governance_strategy` — DEBUG intent with governance violation routes to `GovernanceViolationStrategy`
- `AC-64-07-C`: `test_debug_mode_golden.py::test_debug_mode_emits_ac_markers` — full debug chain emits `AC_START` + `AC_COMPLETE` to SQLite

### GAP-64-08 — HolisticIntegrationHarness Uses Mocked Audit Trail
**Source:** Review 04 (cross-cutting wiring); chat01.md — "harness exists but audit trail assertions are mocked"
**Symptom:** 25 S01–S25 `expected_audit_events` fields define trace contracts but `HolisticIntegrationHarness` never queries real SQLite. Trace assertions are aspirational YAML, not enforced Python.
**Acceptance Criteria (Golden Test — Harness Upgrade):**
- `AC-64-08-A`: `holistic_integration_harness.py::assert_trace_chain(scenario_id, expected_events)` — method queries real `orchestrator-traces.db` (via `tmp_path` fixture), asserts each event present in order
- `AC-64-08-B`: `test_holistic_integration_simple.py` — S01–S10 scenarios use real trace assertions (not mocked), all pass
- `AC-64-08-C`: Orphan `AC_START` detection — harness fails test if any `AC_START` in the session has no matching `AC_COMPLETE`

### GAP-64-09 — Multi-Repo Tools — No Golden Coverage
**Source:** Review 04 (enterprise readiness); chat01.md analysis
**Symptom:** 6 multi-repo tools (`cross_repo_search`, `context_switcher`, `dependency_graph`, `shared_audit`, `profile_manager`, `project_scanner`) exist with zero golden coverage.
**Acceptance Criteria (Golden Test):**
- `AC-64-09-A`: `test_mcp_operations_golden.py::test_cross_repo_search_returns_results` — `cross_repo_search` with a pattern returns structured result list
- `AC-64-09-B`: `test_mcp_operations_golden.py::test_dependency_graph_builds_graph` — `dependency_graph` given 2 repos returns edge list

### GAP-64-10 — Agent Matrix — 15 of 17 Agents Unverified at Golden Tier
**Source:** Chat01.md analysis; agent-index.md lists 17 agents, golden tests cover 2
**Symptom:** Only `test_meta_auditor.py` and `test_plan_auditor.py` exist. 15 agents (`cortex-executor.md`, `cortex-digest.md`, `cortex-vacuum.md`, `cortex-debugger.md`, `cortex-interactive.md`, `cortex-holistic-validator.md`, `cortex-phase-resolver.md`, `cortex-storyteller.md`, `cortex-documentation-architect.md`, `cortex-environment-setup.md`, `architecture-integrity-agent.md`, `cortex-sts-refactoring.md`, `cortex-gitpages-builder.md`, `request-rephrase-orchestrator.md`, `cortex-architect.md`) have no golden verification of their loading protocol or delegation chain.
**Acceptance Criteria (Golden Test):**
- `AC-64-10-A`: `test_agent_matrix_golden.py::test_all_agent_files_exist_and_loadable` — all 17 agent `.md` files exist at expected paths in `.github/agents/`
- `AC-64-10-B`: `test_agent_matrix_golden.py::test_agent_intent_mapping_complete` — `AGENT-INDEX.md` intent→agent table covers all 13 execution modes + GOLDEN_TEST
- `AC-64-10-C`: `test_agent_matrix_golden.py::test_each_mode_has_at_least_one_agent` — parametrized across all 14 intents (including GOLDEN_TEST), each maps to ≥1 agent path

### GAP-64-11 — MCP Auth Not Wired (Ship-Blocker — Deferred to Phase 65)
**Source:** Reviews 03, 04, 05 (enterprise SaaS readiness — unanimous ship-blocker)
**Symptom:** `tenant_context_middleware.py` fully built with `workspace_id`/`tenant_id` dataclasses. `server.py` (440 lines) does not import it. No `auth`, `jwt`, `api_key`, or `X-Tenant` in `server.py`.
**Note:** Deferred to Phase 65 (enterprise hardening) per Phase 59 Track B/C deferral pattern. Phase 64 will add the golden test scaffold but not the implementation.
**Acceptance Criteria (Golden Test — scaffold only in Phase 64):**
- `AC-64-11-A`: `test_mcp_operations_golden.py::test_mcp_server_accepts_tenant_header` — test scaffolded RED (fails) to enforce Phase 65 implementation

### GAP-64-12 — 151 Silent ImportError Suppressions
**Source:** Reviews 01, 02, 03, 04, 05 (unanimous — present in all 5 reviews, count unchanged at 151)
**Symptom:** System silently degrades to stubs when imports fail. Operator sees nothing. `DependencyWarning` infrastructure (`safe_import()` from Phase 62-C) exists but 151 raw `except ImportError: pass` remain.
**Note:** Deferred to Phase 65 sweep. Phase 64 golden test scaffolds the diagnostic.
**Acceptance Criteria (Golden Test — scaffold in Phase 64):**
- `AC-64-12-A`: `test_scorer_self_golden.py::test_no_silent_import_errors_in_golden_path` — the orchestrator chain for all 14 intents produces zero silent degradations (all dependency warnings surfaced)

---

## Architectural Complexity Anti-Patterns (Do Not Reintroduce)

Distilled from all 5 reviews — patterns that consistently increased technical debt:

| Anti-Pattern | How It Manifested | Guard |
|---|---|---|
| **Phase proliferation** | 103 self-refactoring phases; system exists to govern itself | No phase without a closing golden test AC criteria |
| **Tier sprawl** | 3 documented tiers → 10 actual dirs; `wiring.yaml` invisible to 4 tiers | Every new dir must be registered in `wiring.yaml` before merge |
| **Duplicate canonical definitions** | 9 `AuditEntry`, 2 `Result` families, 2 `OperationMode` | CORE-035 enforced by `test_base_class_convergence.py` golden test |
| **Documentation-reality gap** | Docs say "17 wired / OrchestratorBase" — reality was 124 classes / 2 using base | Every architecture claim must have a `test_capability_manifest.py` AC |
| **Silent degradation** | 874 → 151 `except ImportError: pass` — system masks its own failures | `safe_import()` with structured `DependencyWarning` mandatory |
| **God object accumulation** | MasterOrchestrator 5,095 lines; intent_router 2,401 lines | New orchestrator logic → new file; max 500L per file (CORE-028) |
| **Aspirational YAML** | S01–S25 `expected_audit_events` defined but never asserted | Every YAML contract must have a Python assertion within the same phase |

---

## Current Overall Score: 7.3/10

Next target: **8.5/10** after Phase 64 (Unified Brain Golden Coverage) and Phase 65 (Enterprise Hardening — MCP auth, silent import sweep).
