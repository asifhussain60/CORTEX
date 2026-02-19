asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
digest #file:gpt-review.txt espeically GPT Recommendation. Show me your plan. I want CORTEX to operate as a SINGLE cohesive brain. Ensure there is zero regression and loss of capability after this refactoring. Suggest create a manifest document checklist listing all capabiltiies to check against ehwn done. 

Analyze my request using CORTEX's challenge-first protocol: audit existing capabilities. Assume user has no knowledge of CORTEX architecture. Identify architectural fit within current patterns, then deliver your SINGLE BEST recommendation  that addresses the ask vs. challenge tension inline. Evaluate through CORTEX's core design pillars: extensibility, scalability, accuracy, team collaboration, and long-term maintainability. Ensure MCP-first exposure, orchestrator integrity, and zero regression risk. Present findings in executive-ready format: ≤60 seconds read time, comparison tables, clear sections with visual hierarchy optimized for VS Code Copilot Chat rendering. All response feedback in VSCode GitHub Copilot Chat Session should be inline. Never create summary, reports or other markdown files.

GitHub Copilot: 

I need to do a comprehensive scan of the current CORTEX capabilities before presenting the plan. Let me audit the full state. 

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type f -name "*.py" | xargs grep -l "class.*Orchestrator" 2>/dev/null | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex/mcp/tools -type f -name "*.py" | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type d -maxdepth 1 | sort | xargs -I {} sh -c 'echo "$(basename {}): $(find {} -name "*.py" -type f | wc -l) files"'

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex/brain -type d -maxdepth 1 | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/tests -type d -maxdepth 1 | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex_intelligence -type d | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex_lens -type d | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type f -name "*.py" | xargs grep -l "def execute\|def run\|def process\|def handle" 2>/dev/null | xargs grep -l "class.*Orchestrator" 2>/dev/null | wc -l

Ran terminal command: echo "=== DUPLICATE CONCEPTS ===" && echo "--- governance ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "governance" -print 2>/dev/null && echo "--- lens ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "lens" -print 2>/dev/null && echo "--- domain_brain ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "domain_brain" -print 2>/dev/null && echo "--- wiring ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "wiring" -print 2>/dev/null && echo "--- observability ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "observability" -print 2>/dev/null

Now I have the complete picture. Let me present the comprehensive plan.

---

## 📋 CORTEX PLAN — Cohesive Brain Refactor
**Author:** Asif Hussain | **Orchestrator:** PlanningCoordinator ✅

---

## 📋 Summary

After scanning **1,288 source files**, **1,139 test files**, **~110 orchestrator classes** (54 truly active), **3 top-level packages**, and **20+ duplicate concept directories**, the GPT review is directionally correct. Below is my synthesized plan with a **Capability Manifest Checklist** to guarantee zero regression.

---

## 🔍 Analysis — Current State vs GPT Recommendation

### Duplication Severity Map

| Concept | Locations Found | SSOT? |
|---|---|---|
| `governance/` | **9 directories** across cortex, brain, core, knowledge, cortex_intelligence | ❌ NO |
| `lens/` | **3 directories** — cortex/lens, brain/lens, cortex_lens | ❌ NO |
| `domain_brain/` | **3 directories** — cortex, brain, cortex_intelligence | ❌ NO |
| `observability/` | **5 directories** — cortex, orchestrators, brain/core, brain, cortex_intelligence | ❌ NO |
| `wiring/` | **3 directories** — cortex, cortex_intelligence, tests | ❌ NO |
| `domain_orchestrators/` | **2 directories** — cortex, brain | ❌ NO |
| Top-level packages | **3** — cortex, cortex_intelligence, cortex_lens | ❌ NO |

### Orchestrator Sprawl

| Category | Count | Active (has execute/run) |
|---|---|---|
| orchestrators | 183 files | ~35 |
| brain | 261 files | ~12 |
| tools | 44 files | ~7 |
| Phase-named | 9 files | ~0 (legacy) |
| **Total** | **~110 classes** | **~54 active** |

### GPT Review Assessment

| GPT Recommendation | My Assessment |
|---|---|
| Separate legacy branch/repo | ⚠️ **Over-engineered** — git branch separation adds ops overhead without proportional benefit. Archive folder is simpler and achievable. |
| Kernel-first plugin architecture | ✅ **Correct direction** — but the kernel already exists in core + core. Consolidate, don't rebuild. |
| Composition root (DI) | ✅ **Already partially exists** — wiring, bootstrap. Needs unification, not creation. |
| 6 factories (Workflow, Orchestrator, Rule, Artifact, FileNaming, Adapter) | ⚠️ **Too many** — 3 factories max (File, Orchestrator, Workflow). Others are over-abstraction. |
| Strangler fig pattern | ✅ **Best migration pattern** — but combine with archive for clarity. |

---

## ⚠️ MANDATORY CHALLENGE

**Your Request:** Single cohesive brain, zero regression, capability manifest checklist.

**Risk:** 0.75 | **Impact:** Full repo restructure

### Your Approach (Archive + Incremental Migration)
| Aspect | Assessment |
|---|---|
| ✅ Pros | Clean separation, no mixing, easy rollback, simple mental model |
| ⚠️ Risk | If archive phase is too large, tests break en masse |
| Mitigation | **Per-domain archival** (not all-at-once) |

### GPT's Approach (Separate Legacy Branch)
| Aspect | Assessment |
|---|---|
| ✅ Pros | Physically impossible to import legacy |
| ❌ Cons | Git overhead, cherry-pick hell, can't run tests against both simultaneously, team confusion |
| Verdict | **Rejected** — operational complexity exceeds benefit |

### 🏆 SINGLE BEST Recommendation

**Phased domain-level archive + consolidate** with these constraints:

1. **Archive one domain at a time** (governance first, then lens, then brain, etc.)
2. **Each domain consolidation is a self-contained PR** with its own test gate
3. **Capability Manifest Checklist** is built FIRST and validated AFTER each phase
4. **No phase starts until the previous phase is 100% green**

This gives you: **zero mixing** (archived domain can't be imported because imports are rewritten) + **zero regression** (tests gate every merge) + **rollback at domain level** (revert one PR, not the whole thing).

---

## 💡 The Plan — 7 Phases

### Target Architecture (End State)

```
cortex/                          ← SINGLE Python package (brain)
├── core/                        ← Kernel: base classes, DI, event bus, file factory
│   ├── orchestrator_base.py
│   ├── event_bus.py
│   ├── file_factory.py          ← Canonical file naming (YAML-configured)
│   ├── workflow_engine.py       ← Universal workflow template executor
│   └── composition_root.py     ← Wiring / DI entry point
├── governance/                  ← ONE governance directory (SSOT)
├── intelligence/                ← LENS + analysis + pattern detection
│   ├── lens/                    ← CCL, analyzers, tiered API
│   ├── domain_brain/            ← Domain inference, KG
│   └── memory/                  ← Adaptive intelligence, learned patterns
├── orchestrators/               ← ALL orchestrators (flat registry, no nesting >1)
│   ├── core/                    ← master, tdd, enforcement, intent_router
│   ├── domain/                  ← planning, dashboard, refactoring
│   ├── git/                     ← git ops, publish, sanitize
│   ├── health/                  ← health, vacuum
│   ├── support/                 ← debugger, rollback, setup
│   └── registry/                ← orchestrator lookup, factory
├── mcp/                         ← External API surface (MCP tools)
├── infrastructure/              ← Logging, tracing, DB, caching, security
├── observability/               ← Metrics, visibility (ONE location)
├── models/                      ← All data models, enums, events
├── config/                      ← Configuration loading
└── testing/                     ← Test scaffolding, demand generator

cortex-registry/                 ← YAML SSOT (governance rules, workflows, company data)
cortex-docs/                     ← Architecture docs (generated + curated)
tests/                           ← Mirrors cortex/ structure exactly
_archive/                        ← Temporary, deleted after Phase 7
```

### Phase 0: Capability Manifest & Foundation

**Goal:** Build the safety net BEFORE touching anything.

| Deliverable | Description |
|---|---|
| **Capability Manifest** | YAML checklist of every capability (28 MCP tools, 54 active orchestrators, all governance rules, all LENS features). This is your regression gate. |
| **File Factory** | Merge `filename_factory.py` (677 lines) + `file_naming_factory.py` (546 lines) → `cortex/core/file_factory.py`. YAML-configured. No versions in names. |
| **Workflow Engine** | `cortex/core/workflow_engine.py` — every orchestrator executes through this. Reads workflow YAML from templates. |
| **Migration test suite** | Golden tests that exercise every capability in the manifest. Run before AND after each phase. |

### Phase 1: Package Consolidation

**Goal:** 3 packages → 1 package.

| From | To | Action |
|---|---|---|
| cortex_intelligence | `_archive/cortex_intelligence/` | Archive, migrate unique logic to `cortex/intelligence/memory/` |
| cortex_lens | `_archive/cortex_lens/` | Archive, migrate unique logic to `cortex/intelligence/lens/` |
| All imports | `cortex.*` only | Rewrite with sed + manual validation |
| **Gate** | Run capability manifest checklist | ✅ All 28 MCP tools respond |

### Phase 2: Brain Deduplication

**Goal:** brain (261 files, 28 subdirs) → dissolved into proper domains.

| Brain Subdirectory | Destination | Rationale |
|---|---|---|
| `brain/core/orchestrator_base.py` | core | Kernel belongs in core |
| `brain/core/master_orchestrator_gateway.py` | core | Kernel |
| `brain/governance/` | governance | SSOT governance |
| `brain/lens/` | `cortex/intelligence/lens/` | SSOT lens |
| `brain/domain_brain/` | `cortex/intelligence/domain_brain/` | SSOT domain brain |
| `brain/domain_orchestrators/` | domain | SSOT orchestrators |
| `brain/observability/` | observability | SSOT observability |
| `brain/knowledge/` | intelligence | Knowledge = intelligence |
| `brain/devx/`, `brain/cli/` etc. | Respective cortex dirs | Dissolve into proper homes |
| **Gate** | Run capability manifest | ✅ Zero orchestrator regressions |

### Phase 3: Orchestrator Rationalization

**Goal:** ~110 orchestrator classes → ~40 active, all workflow-template-driven.

| Action | Detail |
|---|---|
| Classify all 110 | Active (has tests + callers), Dormant (no callers), Dead (empty/stub) |
| Archive dead + dormant | Move to `_archive/orchestrators/` |
| Merge duplicates | `enforcement_orchestrator` (2 copies), `rollback_orchestrator` (2 copies), `hot_reload` (2 copies) |
| Bind all to workflow YAML | Every surviving orchestrator gets a templates entry |
| Remove phase-named dirs | `phase_38/`, `phase_executors/`, `phase_management/` → archive |
| **Gate** | Run capability manifest | ✅ All active orchestrators respond |

### Phase 4: Directory Cleanup

**Goal:** Eliminate small/redundant directories from cortex.

| Directory | Action | Rationale |
|---|---|---|
| automation (3 files) | → core or infrastructure | Too small for own dir |
| capacity (3 files) | → infrastructure | Infra concern |
| collaboration (3 files) | → infrastructure | Too small |
| confirmation (2 files) | → core | Core concern |
| devx (11 files) | → infrastructure | DX tooling |
| domain_brain (13 files) | → `cortex/intelligence/domain_brain/` | Consolidate |
| domain_orchestrators (5 files) | → domain | Consolidate |
| explainability (3 files) | → intelligence | Intelligence concern |
| intent_router (19 files) | → core | Router = core orchestration |
| phase_38 | → `_archive/` | Phase-named |
| phase_executors | → `_archive/` | Phase-named |
| phase_management | → `_archive/` | Phase-named |
| reports (1 file) | → observability | Reporting = observability |
| repositories (4 files) | → infrastructure | Infra concern |
| scripts (6 files) | → scripts (top-level) | Not a package |
| sensory (4 files) | → intelligence | Intelligence concern |
| sts (1 file) | → testing or archive | Eval concern |
| versioning (3 files) | → infrastructure | Infra concern |
| **Gate** | Run capability manifest | ✅ All imports resolve |

### Phase 5: Test Consolidation

**Goal:** 1,139 test files → high-value suite, structure mirrors cortex.

| Action | Detail |
|---|---|
| Archive phase-named test dirs | `phase_23`, `phase_49`, `phase_52`, `phase_53`, `phase_54_a`, `phase_55`, `phase_56`, `phase_56_a`, `phase_71` |
| Merge duplicate test dirs | `dashboard/` + `dashboards/` → `dashboards/`; cortex + `cortex_brain/` → `core/` |
| Delete low-value tests | Score < 0.3 on test value scorer |
| Restructure to mirror source | core, intelligence, orchestrators, mcp, etc. |
| **Gate** | Coverage ≥ 90% across active code | ✅ |

### Phase 6: Registry & Docs Alignment

**Goal:** cortex-registry = one-stop YAML shop, cortex-docs = clean architecture reference.

| Action | Detail |
|---|---|
| Audit all workflow templates | Ensure every active orchestrator has a template |
| Clean stale YAMLs | Remove references to deleted/archived components |
| Update cortex-docs | Reflect new structure, generate from live code |
| Validate registry integrity | All YAML references resolve |
| **Gate** | Registry valid, docs match code | ✅ |

### Phase 7: Archive Deletion & Release

**Goal:** Burn `_archive/`, tag release.

| Action | Detail |
|---|---|
| Run full capability manifest | All items green |
| Run full regression suite | Unit + integration + golden + e2e |
| Verify all 28 MCP tools | Each tool responds correctly |
| Delete `_archive/` | Permanently |
| Tag release | `v2.0.0-cohesive-brain` |

---

## 📊 Capability Manifest Checklist (Pre-Built)

This is the **zero-regression gate** — built in Phase 0, validated after every subsequent phase.

### Section 1: MCP Tools (28 tools)

| # | Tool | Category | Status |
|---|---|---|---|
| 1 | `cortex_approve_request` | Request | ⬜ |
| 2 | `cortex_ask` | Education | ⬜ |
| 3 | `cortex_audit_remediation_plan` | Governance | ⬜ |
| 4 | `cortex_capture_metrics` | Observability | ⬜ |
| 5 | `cortex_challenge` | Governance | ⬜ |
| 6 | `cortex_check_dependency_drift` | DevOps | ⬜ |
| 7 | `cortex_execute_governance` | Governance | ⬜ |
| 8 | `cortex_generate_dashboard_suite` | Dashboard | ⬜ |
| 9 | `cortex_generate_landing_page` | Dashboard | ⬜ |
| 10 | `cortex_generate_repo_dashboard` | Dashboard | ⬜ |
| 11 | `cortex_load_audit_checklist` | Governance | ⬜ |
| 12 | `cortex_load_core_rules` | Governance | ⬜ |
| 13 | `cortex_load_modes` | Config | ⬜ |
| 14 | `cortex_load_response_format` | Config | ⬜ |
| 15 | `cortex_metrics_report` | Observability | ⬜ |
| 16 | `cortex_onboard_repository` | Onboarding | ⬜ |
| 17 | `cortex_onboard_repository_v3` | Onboarding | ⬜ |
| 18 | `cortex_query_governance` | Governance | ⬜ |
| 19 | `cortex_refactor` | Refactoring | ⬜ |
| 20 | `cortex_refactor_available_operations` | Refactoring | ⬜ |
| 21 | `cortex_refactor_supported_languages` | Refactoring | ⬜ |
| 22 | `cortex_tools_catalog` | Discovery | ⬜ |
| 23 | `cortex_total_recall` | Discovery | ⬜ |
| 24 | `cortex_vacuum` | Maintenance | ⬜ |
| 25 | `cortex_validate_compliance` | Governance | ⬜ |
| 26 | `cortex_validate_venv` | Environment | ⬜ |
| 27 | `cortex_verify_claim` | Verification | ⬜ |
| 28 | `cortex_verify_environment` | Environment | ⬜ |

### Section 2: Core Orchestrators (Active, ~54)

| # | Orchestrator | Domain | Location | Status |
|---|---|---|---|---|
| 1 | `MasterOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 2 | `TDDOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 3 | `EnforcementOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 4 | `IntentRouter` | Core | orchestrators/core/ | ⬜ |
| 5 | `InteractionOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 6 | `WorkflowOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 7 | `MasterPlanOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 8 | `ReviewOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 9 | `SecurityOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 10 | `PlanningOrchestrator` | Domain | orchestrators/domain/ | ⬜ |
| 11 | `DashboardOrchestrator` | Domain | orchestrators/domain/ | ⬜ |
| 12 | `RefactoringOrchestrator` | Domain | orchestrators/domain/ | ⬜ |
| 13 | `GitOrchestrator` | Git | orchestrators/git/ | ⬜ |
| 14 | `GitPublishOrchestrator` | Git | orchestrators/git/ | ⬜ |
| 15 | `SanitizationOrchestrator` | Git | orchestrators/git/ | ⬜ |
| 16 | `HealthOrchestrator` | Health | orchestrators/health/ | ⬜ |
| 17 | `VacuumOrchestrator` | Health | orchestrators/health/ | ⬜ |
| 18 | `IntelligenceOrchestrator` | Intel | orchestrators/intelligence/ | ⬜ |
| 19 | `HolisticValidationOrchestrator` | Validation | orchestrators/validation/ | ⬜ |
| 20 | `DebuggerOrchestrator` | Support | orchestrators/support/ | ⬜ |
| 21 | `RollbackOrchestrator` | Support | orchestrators/support/ | ⬜ |
| 22 | `SetupOrchestrator` | Support | orchestrators/support/ | ⬜ |
| 23 | `ObservabilityOrchestrator` | Observability | orchestrators/observability/ | ⬜ |
| 24 | `OnboardingOrchestrator` | Onboarding | orchestrators/onboarding/ | ⬜ |
| 25 | `LensOrchestrator` | Intelligence | lens/ | ⬜ |
| 26 | `CachedLensOrchestrator` | Intelligence | lens/ | ⬜ |
| 27 | `RegressionSafetyOrchestrator` | Governance | governance/ | ⬜ |
| 28 | `ConversationOrchestrator` | Core | orchestrators/ | ⬜ |
| 29 | `AutoHealingMcpOrchestrator` | Core | orchestrators/ | ⬜ |
| 30 | `RequestRephraseOrchestrator` | Core | orchestrators/ | ⬜ |

*(Full list of 54 active orchestrators will be enumerated in the Phase 0 YAML)*

### Section 3: Governance Rules

| Rule | Description | Status |
|---|---|---|
| CORE-002 | No markdown/text file generation via bash | ⬜ |
| CORE-008 | Test-first development (TDD mandatory) | ⬜ |
| CORE-011 | Type hints on all functions | ⬜ |
| CORE-012 | Docstrings on all public APIs | ⬜ |
| CORE-028 | File naming: snake_case only | ⬜ |
| CORE-035 | Single canonical implementation | ⬜ |
| CORE-048 | Holistic validation gate | ⬜ |
| CORE-049 | Silent autonomous execution | ⬜ |
| CORE-050 | Intent-based MCP blocking | ⬜ |
| CORE-051 | Cross-platform audit | ⬜ |
| CORE-053 | Auto-healing when MCP unavailable | ⬜ |

### Section 4: Intelligence Capabilities

| Capability | Component | Status |
|---|---|---|
| LENS workspace analysis | lens | ⬜ |
| CCL (CORTEX Code Language) | lens | ⬜ |
| Domain inference | intelligence or cortex_lens | ⬜ |
| Knowledge graph | knowledge_graph | ⬜ |
| Pattern detection | intelligence | ⬜ |
| Adaptive memory | memory | ⬜ |
| Learned patterns | learned_patterns | ⬜ |
| Hallucination prevention | adaptive_intelligence | ⬜ |
| Credential protection | adaptive_intelligence | ⬜ |

### Section 5: Infrastructure

| Capability | Component | Status |
|---|---|---|
| EventBus pub/sub | infrastructure | ⬜ |
| Orchestrator tracing | infrastructure | ⬜ |
| SQLite storage | storage | ⬜ |
| Prometheus metrics | prometheus_metrics.py | ⬜ |
| OpenTelemetry tracing | opentelemetry_tracing.py | ⬜ |
| Health check service | health_check_service.py | ⬜ |
| Bootstrap/startup | bootstrap | ⬜ |
| Security defense | security | ⬜ |

### Section 6: Workflow Templates

| Template | Location | Status |
|---|---|---|
| Orchestrator execution (universal) | internal | ⬜ |
| TDD workflow | tdd | ⬜ |
| Governance workflow | governance | ⬜ |
| Quality workflow | quality | ⬜ |
| Security workflow | security | ⬜ |
| Lifecycle workflow | lifecycle | ⬜ |
| Maintenance workflow | maintenance | ⬜ |

---

## ⚖️ Benefits & Risks

| Benefit | Risk | Mitigation | Phase |
|---|---|---|---|
| Single cohesive brain | Import breakage | Per-domain archive + import rewriter | 1-2 |
| 110 → ~40 orchestrators | Lost undocumented functionality | Capability manifest built FIRST | 0 |
| 3 packages → 1 | cortex_intelligence has runtime data (DBs) | Separate data from code, data stays in .cortex-runtime | 1 |
| Clean internal/external boundary | MCP tool paths change | MCP regression suite per phase | All |
| High-value tests only | Coverage drop | Score before delete, gate at ≥90% | 5 |
| File factory SSOT | Existing code uses old factories | Factory built in Phase 0, enforced from Phase 1 | 0 |

---

## 🎯 Next Steps

1. **Review this plan** — approve, modify, or challenge any phase
2. **Approve the Capability Manifest** — this is your zero-regression insurance
3. Once approved, I create the full YAML phase files in gpt-refactor

### ⚡ If you type `proceed`, CORTEX will:
- Create `00-overview.yaml` — full refactor manifest with DoD
- Create `01-capability-manifest.yaml` — the complete checklist (~100 items)
- Create `phase-00-foundation.yaml` through `phase-07-release.yaml` — 8 detailed phase specs
- Create `migration-tracker.yaml` — tracks archive → migrate → validate → delete lifecycle
- Build the File Factory config at `cortex-registry/core/config/file-naming-rules.yaml`
- Define the universal workflow template schema

> Type `proceed` to execute, or correct anything above before confirming.
> **Confidence:** High

asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
digest #file:gpt-review.txt espeically GPT Recommendation. Show me your plan. I want CORTEX to operate as a SINGLE cohesive brain. Ensure there is zero regression and loss of capability after this refactoring. Suggest create a manifest document checklist listing all capabiltiies to check against ehwn done. 

Analyze my request using CORTEX's challenge-first protocol: audit existing capabilities. Assume user has no knowledge of CORTEX architecture. Identify architectural fit within current patterns, then deliver your SINGLE BEST recommendation  that addresses the ask vs. challenge tension inline. Evaluate through CORTEX's core design pillars: extensibility, scalability, accuracy, team collaboration, and long-term maintainability. Ensure MCP-first exposure, orchestrator integrity, and zero regression risk. Present findings in executive-ready format: ≤60 seconds read time, comparison tables, clear sections with visual hierarchy optimized for VS Code Copilot Chat rendering. All response feedback in VSCode GitHub Copilot Chat Session should be inline. Never create summary, reports or other markdown files.

GitHub Copilot: 

I need to do a comprehensive scan of the current CORTEX capabilities before presenting the plan. Let me audit the full state. 

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type f -name "*.py" | xargs grep -l "class.*Orchestrator" 2>/dev/null | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex/mcp/tools -type f -name "*.py" | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type d -maxdepth 1 | sort | xargs -I {} sh -c 'echo "$(basename {}): $(find {} -name "*.py" -type f | wc -l) files"'

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex/brain -type d -maxdepth 1 | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/tests -type d -maxdepth 1 | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex_intelligence -type d | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex_lens -type d | sort

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type f -name "*.py" | xargs grep -l "def execute\|def run\|def process\|def handle" 2>/dev/null | xargs grep -l "class.*Orchestrator" 2>/dev/null | wc -l

Ran terminal command: echo "=== DUPLICATE CONCEPTS ===" && echo "--- governance ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "governance" -print 2>/dev/null && echo "--- lens ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "lens" -print 2>/dev/null && echo "--- domain_brain ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "domain_brain" -print 2>/dev/null && echo "--- wiring ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "wiring" -print 2>/dev/null && echo "--- observability ---" && find /Users/asifhussain/PROJECTS/CORTEX -path "*/__pycache__" -prune -o -type d -name "observability" -print 2>/dev/null

Now I have the complete picture. Let me present the comprehensive plan.

---

## 📋 CORTEX PLAN — Cohesive Brain Refactor
**Author:** Asif Hussain | **Orchestrator:** PlanningCoordinator ✅

---

## 📋 Summary

After scanning **1,288 source files**, **1,139 test files**, **~110 orchestrator classes** (54 truly active), **3 top-level packages**, and **20+ duplicate concept directories**, the GPT review is directionally correct. Below is my synthesized plan with a **Capability Manifest Checklist** to guarantee zero regression.

---

## 🔍 Analysis — Current State vs GPT Recommendation

### Duplication Severity Map

| Concept | Locations Found | SSOT? |
|---|---|---|
| `governance/` | **9 directories** across cortex, brain, core, knowledge, cortex_intelligence | ❌ NO |
| `lens/` | **3 directories** — cortex/lens, brain/lens, cortex_lens | ❌ NO |
| `domain_brain/` | **3 directories** — cortex, brain, cortex_intelligence | ❌ NO |
| `observability/` | **5 directories** — cortex, orchestrators, brain/core, brain, cortex_intelligence | ❌ NO |
| `wiring/` | **3 directories** — cortex, cortex_intelligence, tests | ❌ NO |
| `domain_orchestrators/` | **2 directories** — cortex, brain | ❌ NO |
| Top-level packages | **3** — cortex, cortex_intelligence, cortex_lens | ❌ NO |

### Orchestrator Sprawl

| Category | Count | Active (has execute/run) |
|---|---|---|
| orchestrators | 183 files | ~35 |
| brain | 261 files | ~12 |
| tools | 44 files | ~7 |
| Phase-named | 9 files | ~0 (legacy) |
| **Total** | **~110 classes** | **~54 active** |

### GPT Review Assessment

| GPT Recommendation | My Assessment |
|---|---|
| Separate legacy branch/repo | ⚠️ **Over-engineered** — git branch separation adds ops overhead without proportional benefit. Archive folder is simpler and achievable. |
| Kernel-first plugin architecture | ✅ **Correct direction** — but the kernel already exists in core + core. Consolidate, don't rebuild. |
| Composition root (DI) | ✅ **Already partially exists** — wiring, bootstrap. Needs unification, not creation. |
| 6 factories (Workflow, Orchestrator, Rule, Artifact, FileNaming, Adapter) | ⚠️ **Too many** — 3 factories max (File, Orchestrator, Workflow). Others are over-abstraction. |
| Strangler fig pattern | ✅ **Best migration pattern** — but combine with archive for clarity. |

---

## ⚠️ MANDATORY CHALLENGE

**Your Request:** Single cohesive brain, zero regression, capability manifest checklist.

**Risk:** 0.75 | **Impact:** Full repo restructure

### Your Approach (Archive + Incremental Migration)
| Aspect | Assessment |
|---|---|
| ✅ Pros | Clean separation, no mixing, easy rollback, simple mental model |
| ⚠️ Risk | If archive phase is too large, tests break en masse |
| Mitigation | **Per-domain archival** (not all-at-once) |

### GPT's Approach (Separate Legacy Branch)
| Aspect | Assessment |
|---|---|
| ✅ Pros | Physically impossible to import legacy |
| ❌ Cons | Git overhead, cherry-pick hell, can't run tests against both simultaneously, team confusion |
| Verdict | **Rejected** — operational complexity exceeds benefit |

### 🏆 SINGLE BEST Recommendation

**Phased domain-level archive + consolidate** with these constraints:

1. **Archive one domain at a time** (governance first, then lens, then brain, etc.)
2. **Each domain consolidation is a self-contained PR** with its own test gate
3. **Capability Manifest Checklist** is built FIRST and validated AFTER each phase
4. **No phase starts until the previous phase is 100% green**

This gives you: **zero mixing** (archived domain can't be imported because imports are rewritten) + **zero regression** (tests gate every merge) + **rollback at domain level** (revert one PR, not the whole thing).

---

## 💡 The Plan — 7 Phases

### Target Architecture (End State)

```
cortex/                          ← SINGLE Python package (brain)
├── core/                        ← Kernel: base classes, DI, event bus, file factory
│   ├── orchestrator_base.py
│   ├── event_bus.py
│   ├── file_factory.py          ← Canonical file naming (YAML-configured)
│   ├── workflow_engine.py       ← Universal workflow template executor
│   └── composition_root.py     ← Wiring / DI entry point
├── governance/                  ← ONE governance directory (SSOT)
├── intelligence/                ← LENS + analysis + pattern detection
│   ├── lens/                    ← CCL, analyzers, tiered API
│   ├── domain_brain/            ← Domain inference, KG
│   └── memory/                  ← Adaptive intelligence, learned patterns
├── orchestrators/               ← ALL orchestrators (flat registry, no nesting >1)
│   ├── core/                    ← master, tdd, enforcement, intent_router
│   ├── domain/                  ← planning, dashboard, refactoring
│   ├── git/                     ← git ops, publish, sanitize
│   ├── health/                  ← health, vacuum
│   ├── support/                 ← debugger, rollback, setup
│   └── registry/                ← orchestrator lookup, factory
├── mcp/                         ← External API surface (MCP tools)
├── infrastructure/              ← Logging, tracing, DB, caching, security
├── observability/               ← Metrics, visibility (ONE location)
├── models/                      ← All data models, enums, events
├── config/                      ← Configuration loading
└── testing/                     ← Test scaffolding, demand generator

cortex-registry/                 ← YAML SSOT (governance rules, workflows, company data)
cortex-docs/                     ← Architecture docs (generated + curated)
tests/                           ← Mirrors cortex/ structure exactly
_archive/                        ← Temporary, deleted after Phase 7
```

### Phase 0: Capability Manifest & Foundation

**Goal:** Build the safety net BEFORE touching anything.

| Deliverable | Description |
|---|---|
| **Capability Manifest** | YAML checklist of every capability (28 MCP tools, 54 active orchestrators, all governance rules, all LENS features). This is your regression gate. |
| **File Factory** | Merge `filename_factory.py` (677 lines) + `file_naming_factory.py` (546 lines) → `cortex/core/file_factory.py`. YAML-configured. No versions in names. |
| **Workflow Engine** | `cortex/core/workflow_engine.py` — every orchestrator executes through this. Reads workflow YAML from templates. |
| **Migration test suite** | Golden tests that exercise every capability in the manifest. Run before AND after each phase. |

### Phase 1: Package Consolidation

**Goal:** 3 packages → 1 package.

| From | To | Action |
|---|---|---|
| cortex_intelligence | `_archive/cortex_intelligence/` | Archive, migrate unique logic to `cortex/intelligence/memory/` |
| cortex_lens | `_archive/cortex_lens/` | Archive, migrate unique logic to `cortex/intelligence/lens/` |
| All imports | `cortex.*` only | Rewrite with sed + manual validation |
| **Gate** | Run capability manifest checklist | ✅ All 28 MCP tools respond |

### Phase 2: Brain Deduplication

**Goal:** brain (261 files, 28 subdirs) → dissolved into proper domains.

| Brain Subdirectory | Destination | Rationale |
|---|---|---|
| `brain/core/orchestrator_base.py` | core | Kernel belongs in core |
| `brain/core/master_orchestrator_gateway.py` | core | Kernel |
| `brain/governance/` | governance | SSOT governance |
| `brain/lens/` | `cortex/intelligence/lens/` | SSOT lens |
| `brain/domain_brain/` | `cortex/intelligence/domain_brain/` | SSOT domain brain |
| `brain/domain_orchestrators/` | domain | SSOT orchestrators |
| `brain/observability/` | observability | SSOT observability |
| `brain/knowledge/` | intelligence | Knowledge = intelligence |
| `brain/devx/`, `brain/cli/` etc. | Respective cortex dirs | Dissolve into proper homes |
| **Gate** | Run capability manifest | ✅ Zero orchestrator regressions |

### Phase 3: Orchestrator Rationalization

**Goal:** ~110 orchestrator classes → ~40 active, all workflow-template-driven.

| Action | Detail |
|---|---|
| Classify all 110 | Active (has tests + callers), Dormant (no callers), Dead (empty/stub) |
| Archive dead + dormant | Move to `_archive/orchestrators/` |
| Merge duplicates | `enforcement_orchestrator` (2 copies), `rollback_orchestrator` (2 copies), `hot_reload` (2 copies) |
| Bind all to workflow YAML | Every surviving orchestrator gets a templates entry |
| Remove phase-named dirs | `phase_38/`, `phase_executors/`, `phase_management/` → archive |
| **Gate** | Run capability manifest | ✅ All active orchestrators respond |

### Phase 4: Directory Cleanup

**Goal:** Eliminate small/redundant directories from cortex.

| Directory | Action | Rationale |
|---|---|---|
| automation (3 files) | → core or infrastructure | Too small for own dir |
| capacity (3 files) | → infrastructure | Infra concern |
| collaboration (3 files) | → infrastructure | Too small |
| confirmation (2 files) | → core | Core concern |
| devx (11 files) | → infrastructure | DX tooling |
| domain_brain (13 files) | → `cortex/intelligence/domain_brain/` | Consolidate |
| domain_orchestrators (5 files) | → domain | Consolidate |
| explainability (3 files) | → intelligence | Intelligence concern |
| intent_router (19 files) | → core | Router = core orchestration |
| phase_38 | → `_archive/` | Phase-named |
| phase_executors | → `_archive/` | Phase-named |
| phase_management | → `_archive/` | Phase-named |
| reports (1 file) | → observability | Reporting = observability |
| repositories (4 files) | → infrastructure | Infra concern |
| scripts (6 files) | → scripts (top-level) | Not a package |
| sensory (4 files) | → intelligence | Intelligence concern |
| sts (1 file) | → testing or archive | Eval concern |
| versioning (3 files) | → infrastructure | Infra concern |
| **Gate** | Run capability manifest | ✅ All imports resolve |

### Phase 5: Test Consolidation

**Goal:** 1,139 test files → high-value suite, structure mirrors cortex.

| Action | Detail |
|---|---|
| Archive phase-named test dirs | `phase_23`, `phase_49`, `phase_52`, `phase_53`, `phase_54_a`, `phase_55`, `phase_56`, `phase_56_a`, `phase_71` |
| Merge duplicate test dirs | `dashboard/` + `dashboards/` → `dashboards/`; cortex + `cortex_brain/` → `core/` |
| Delete low-value tests | Score < 0.3 on test value scorer |
| Restructure to mirror source | core, intelligence, orchestrators, mcp, etc. |
| **Gate** | Coverage ≥ 90% across active code | ✅ |

### Phase 6: Registry & Docs Alignment

**Goal:** cortex-registry = one-stop YAML shop, cortex-docs = clean architecture reference.

| Action | Detail |
|---|---|
| Audit all workflow templates | Ensure every active orchestrator has a template |
| Clean stale YAMLs | Remove references to deleted/archived components |
| Update cortex-docs | Reflect new structure, generate from live code |
| Validate registry integrity | All YAML references resolve |
| **Gate** | Registry valid, docs match code | ✅ |

### Phase 7: Archive Deletion & Release

**Goal:** Burn `_archive/`, tag release.

| Action | Detail |
|---|---|
| Run full capability manifest | All items green |
| Run full regression suite | Unit + integration + golden + e2e |
| Verify all 28 MCP tools | Each tool responds correctly |
| Delete `_archive/` | Permanently |
| Tag release | `v2.0.0-cohesive-brain` |

---

## 📊 Capability Manifest Checklist (Pre-Built)

This is the **zero-regression gate** — built in Phase 0, validated after every subsequent phase.

### Section 1: MCP Tools (28 tools)

| # | Tool | Category | Status |
|---|---|---|---|
| 1 | `cortex_approve_request` | Request | ⬜ |
| 2 | `cortex_ask` | Education | ⬜ |
| 3 | `cortex_audit_remediation_plan` | Governance | ⬜ |
| 4 | `cortex_capture_metrics` | Observability | ⬜ |
| 5 | `cortex_challenge` | Governance | ⬜ |
| 6 | `cortex_check_dependency_drift` | DevOps | ⬜ |
| 7 | `cortex_execute_governance` | Governance | ⬜ |
| 8 | `cortex_generate_dashboard_suite` | Dashboard | ⬜ |
| 9 | `cortex_generate_landing_page` | Dashboard | ⬜ |
| 10 | `cortex_generate_repo_dashboard` | Dashboard | ⬜ |
| 11 | `cortex_load_audit_checklist` | Governance | ⬜ |
| 12 | `cortex_load_core_rules` | Governance | ⬜ |
| 13 | `cortex_load_modes` | Config | ⬜ |
| 14 | `cortex_load_response_format` | Config | ⬜ |
| 15 | `cortex_metrics_report` | Observability | ⬜ |
| 16 | `cortex_onboard_repository` | Onboarding | ⬜ |
| 17 | `cortex_onboard_repository_v3` | Onboarding | ⬜ |
| 18 | `cortex_query_governance` | Governance | ⬜ |
| 19 | `cortex_refactor` | Refactoring | ⬜ |
| 20 | `cortex_refactor_available_operations` | Refactoring | ⬜ |
| 21 | `cortex_refactor_supported_languages` | Refactoring | ⬜ |
| 22 | `cortex_tools_catalog` | Discovery | ⬜ |
| 23 | `cortex_total_recall` | Discovery | ⬜ |
| 24 | `cortex_vacuum` | Maintenance | ⬜ |
| 25 | `cortex_validate_compliance` | Governance | ⬜ |
| 26 | `cortex_validate_venv` | Environment | ⬜ |
| 27 | `cortex_verify_claim` | Verification | ⬜ |
| 28 | `cortex_verify_environment` | Environment | ⬜ |

### Section 2: Core Orchestrators (Active, ~54)

| # | Orchestrator | Domain | Location | Status |
|---|---|---|---|---|
| 1 | `MasterOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 2 | `TDDOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 3 | `EnforcementOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 4 | `IntentRouter` | Core | orchestrators/core/ | ⬜ |
| 5 | `InteractionOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 6 | `WorkflowOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 7 | `MasterPlanOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 8 | `ReviewOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 9 | `SecurityOrchestrator` | Core | orchestrators/core/ | ⬜ |
| 10 | `PlanningOrchestrator` | Domain | orchestrators/domain/ | ⬜ |
| 11 | `DashboardOrchestrator` | Domain | orchestrators/domain/ | ⬜ |
| 12 | `RefactoringOrchestrator` | Domain | orchestrators/domain/ | ⬜ |
| 13 | `GitOrchestrator` | Git | orchestrators/git/ | ⬜ |
| 14 | `GitPublishOrchestrator` | Git | orchestrators/git/ | ⬜ |
| 15 | `SanitizationOrchestrator` | Git | orchestrators/git/ | ⬜ |
| 16 | `HealthOrchestrator` | Health | orchestrators/health/ | ⬜ |
| 17 | `VacuumOrchestrator` | Health | orchestrators/health/ | ⬜ |
| 18 | `IntelligenceOrchestrator` | Intel | orchestrators/intelligence/ | ⬜ |
| 19 | `HolisticValidationOrchestrator` | Validation | orchestrators/validation/ | ⬜ |
| 20 | `DebuggerOrchestrator` | Support | orchestrators/support/ | ⬜ |
| 21 | `RollbackOrchestrator` | Support | orchestrators/support/ | ⬜ |
| 22 | `SetupOrchestrator` | Support | orchestrators/support/ | ⬜ |
| 23 | `ObservabilityOrchestrator` | Observability | orchestrators/observability/ | ⬜ |
| 24 | `OnboardingOrchestrator` | Onboarding | orchestrators/onboarding/ | ⬜ |
| 25 | `LensOrchestrator` | Intelligence | lens/ | ⬜ |
| 26 | `CachedLensOrchestrator` | Intelligence | lens/ | ⬜ |
| 27 | `RegressionSafetyOrchestrator` | Governance | governance/ | ⬜ |
| 28 | `ConversationOrchestrator` | Core | orchestrators/ | ⬜ |
| 29 | `AutoHealingMcpOrchestrator` | Core | orchestrators/ | ⬜ |
| 30 | `RequestRephraseOrchestrator` | Core | orchestrators/ | ⬜ |

*(Full list of 54 active orchestrators will be enumerated in the Phase 0 YAML)*

### Section 3: Governance Rules

| Rule | Description | Status |
|---|---|---|
| CORE-002 | No markdown/text file generation via bash | ⬜ |
| CORE-008 | Test-first development (TDD mandatory) | ⬜ |
| CORE-011 | Type hints on all functions | ⬜ |
| CORE-012 | Docstrings on all public APIs | ⬜ |
| CORE-028 | File naming: snake_case only | ⬜ |
| CORE-035 | Single canonical implementation | ⬜ |
| CORE-048 | Holistic validation gate | ⬜ |
| CORE-049 | Silent autonomous execution | ⬜ |
| CORE-050 | Intent-based MCP blocking | ⬜ |
| CORE-051 | Cross-platform audit | ⬜ |
| CORE-053 | Auto-healing when MCP unavailable | ⬜ |

### Section 4: Intelligence Capabilities

| Capability | Component | Status |
|---|---|---|
| LENS workspace analysis | lens | ⬜ |
| CCL (CORTEX Code Language) | lens | ⬜ |
| Domain inference | intelligence or cortex_lens | ⬜ |
| Knowledge graph | knowledge_graph | ⬜ |
| Pattern detection | intelligence | ⬜ |
| Adaptive memory | memory | ⬜ |
| Learned patterns | learned_patterns | ⬜ |
| Hallucination prevention | adaptive_intelligence | ⬜ |
| Credential protection | adaptive_intelligence | ⬜ |

### Section 5: Infrastructure

| Capability | Component | Status |
|---|---|---|
| EventBus pub/sub | infrastructure | ⬜ |
| Orchestrator tracing | infrastructure | ⬜ |
| SQLite storage | storage | ⬜ |
| Prometheus metrics | prometheus_metrics.py | ⬜ |
| OpenTelemetry tracing | opentelemetry_tracing.py | ⬜ |
| Health check service | health_check_service.py | ⬜ |
| Bootstrap/startup | bootstrap | ⬜ |
| Security defense | security | ⬜ |

### Section 6: Workflow Templates

| Template | Location | Status |
|---|---|---|
| Orchestrator execution (universal) | internal | ⬜ |
| TDD workflow | tdd | ⬜ |
| Governance workflow | governance | ⬜ |
| Quality workflow | quality | ⬜ |
| Security workflow | security | ⬜ |
| Lifecycle workflow | lifecycle | ⬜ |
| Maintenance workflow | maintenance | ⬜ |

---

## ⚖️ Benefits & Risks

| Benefit | Risk | Mitigation | Phase |
|---|---|---|---|
| Single cohesive brain | Import breakage | Per-domain archive + import rewriter | 1-2 |
| 110 → ~40 orchestrators | Lost undocumented functionality | Capability manifest built FIRST | 0 |
| 3 packages → 1 | cortex_intelligence has runtime data (DBs) | Separate data from code, data stays in .cortex-runtime | 1 |
| Clean internal/external boundary | MCP tool paths change | MCP regression suite per phase | All |
| High-value tests only | Coverage drop | Score before delete, gate at ≥90% | 5 |
| File factory SSOT | Existing code uses old factories | Factory built in Phase 0, enforced from Phase 1 | 0 |

---

## 🎯 Next Steps

1. **Review this plan** — approve, modify, or challenge any phase
2. **Approve the Capability Manifest** — this is your zero-regression insurance
3. Once approved, I create the full YAML phase files in gpt-refactor

### ⚡ If you type `proceed`, CORTEX will:
- Create `00-overview.yaml` — full refactor manifest with DoD
- Create `01-capability-manifest.yaml` — the complete checklist (~100 items)
- Create `phase-00-foundation.yaml` through `phase-07-release.yaml` — 8 detailed phase specs
- Create `migration-tracker.yaml` — tracks archive → migrate → validate → delete lifecycle
- Build the File Factory config at `cortex-registry/core/config/file-naming-rules.yaml`
- Define the universal workflow template schema

> Type `proceed` to execute, or correct anything above before confirming.
> **Confidence:** High

asifhussain60: proceed. First create all the phases in a dedicated folder so that the archival and restore process does not influence the plan Add a final refactor and verification phase that ensures zero regression. Find all consolidation opportunities for tests, orchestrators, components as party of your plan.  Review existing knowledge yamls for design patterns, enterprise architecture and others to bild the best entierpise soluiton. CORTEX should be built for team collaboration. Accuracy, efficiency, security, quality should be at the heart of EVERY Single operations.


Factor in making workflow templates an intrinsic part of the orchestrator so they all work via dedicated workflow templates to ensure consistency in operations. Each dedicated workflow template shold have a setup and teardown step. dedicated workflow template should be able to use existing workflow templates. Review entier GIT HISTORY for origin/CORTEX to understand the kind of work we've been doing. Create a proper architecture to handle this effectively. Challenge with bettter alternatives if you disagree and reflect back plan

GitHub Copilot: 

I'll start by reviewing the git history and existing knowledge YAMLs to inform the plan, then create all phase files. 

Ran terminal command: git --no-pager log origin/CORTEX --oneline --no-merges -100

Ran terminal command: git --no-pager log origin/CORTEX --oneline --no-merges --skip=100 -100

Ran terminal command: git --no-pager log origin/CORTEX --oneline --no-merges --skip=200 -100

Ran terminal command: find cortex-registry/knowledge-base -type f -name "*.yaml" -o -name "*.yml" | sort

Ran terminal command: find cortex-registry/core -type f -name "*.yaml" -o -name "*.yml" | sort

Ran terminal command: find cortex-registry/patterns -type f -name "*.yaml" -o -name "*.yml" | sort && echo "---" && find cortex-registry/workflows -type f -name "*.yaml" -o -name "*.yml" | sort

Ran terminal command: cat cortex-registry/workflows/templates/tdd/tdd-feature-implementation.yaml | head -80

Ran terminal command: cat cortex-registry/core/specifications/orchestration-master-wiring.yaml | head -80

Ran terminal command: cat cortex-registry/core/governance/skull-rules.yaml | head -100

Ran terminal command: find cortex-registry/patterns -type f 2>/dev/null | sort && echo "---" && find cortex-registry -maxdepth 1 -type d | sort

Ran terminal command: find cortex-registry/governance -type f | sort && echo "---INTEGRATION---" && find cortex-registry/integration -type f | sort

Ran terminal command: cat cortex-registry/core/tier2-engineering/engineering-standards.yaml | head -80

Now let me check the existing workflow template engine and orchestrator base to understand what we're building on: 

Ran terminal command: cat cortex/core/orchestrator_base.py 2>/dev/null | head -60 || cat cortex/brain/core/orchestrator_base.py 2>/dev/null | head -60

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -name "orchestrator_base.py" -type f

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/core/orchestrator_base.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/core/orchestrator_base.py#80-80), lines 80 to 200

Now let me check the existing workflow template engine from Phase 100: 

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -name "*workflow*" -type f -name "*.py" | sort

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/workflow/workflow_runtime.py#1-1), lines 1 to 80

Ran terminal command: ls -la cortex-registry/_cortex-master/phases/planned/gpt-refactor/ 2>/dev/null || echo "Directory does not exist"

Ran terminal command: git --no-pager log origin/CORTEX --format="%s" --no-merges | grep -iE "phase|refactor|consolidat|migrat" | head -40

Now I have comprehensive context. Let me create all the phase YAML files: 

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/00-overview.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-00-foundation.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-01-package-consolidation.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-02-brain-deduplication.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-03-orchestrator-rationalization.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-04-directory-cleanup.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-05-test-consolidation.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-06-registry-docs.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/phase-07-final-verification.yaml)

Now create the capability manifest and migration tracker: 

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/capability-manifest.yaml)

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor/migration-tracker.yaml)

Summarized conversation historyNow let me verify the full directory listing of everything created: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/planned/gpt-refactor)

All **11 files** are in place. Here's the complete delivery summary:

---

### `gpt-refactor/` — Comprehensive Refactoring Plan

| File | Purpose |
|---|---|
| `00-overview.yaml` | Master plan — DoD, architecture, workflow template spec, file factory spec, migration strategy, phase index |
| `phase-00-foundation.yaml` | Safety net — capability manifest, file factory, workflow engine, migration tracker, orchestrator workflow binding |
| `phase-01-package-consolidation.yaml` | 3 packages → 1 (cortex_intelligence, cortex_lens → cortex) |
| `phase-02-brain-deduplication.yaml` | Dissolve brain (261 files, 28 subdirs) into proper domain directories |
| `phase-03-orchestrator-rationalization.yaml` | ~110 → ~40 orchestrators, all workflow-template-driven, 5 known duplicates resolved |
| `phase-04-directory-cleanup.yaml` | ~50 → ~15 canonical directories, 30+ consolidation mappings |
| `phase-05-test-consolidation.yaml` | 1,139 tests → high-value suite mirroring source structure, 9 phase-named dirs archived |
| `phase-06-registry-docs.yaml` | Registry as one-stop YAML shop, 9 enterprise patterns, team collaboration enhancements |
| `phase-07-final-verification.yaml` | 5 verification stages, 6 final refactor passes, archive deletion protocol, 18-item DoD |
| `capability-manifest.yaml` | ~100-item regression gate (28 MCP tools, 40 orchestrators, 12 governance rules, 10 intelligence, 8 infra, 21+ templates, 10 patterns) |
| `migration-tracker.yaml` | Lifecycle tracker for every migrated component: source → archive → target → validated → deleted |

### Key Architecture Decisions Embedded

1. **Workflow templates are intrinsic** — every orchestrator gets a 5-step lifecycle (`setup → governance_gate → execute → validate → teardown`), not optional
2. **Templates compose** — `use_template` directive lets templates reference other templates
3. **Archive-first migration** — `mv` to `_archive/`, build new, test, then delete archive in Phase 07 only
4. **File factory is single SSOT** — merges two existing implementations (677 + 546 lines) into `cortex/core/file_factory.py` with YAML-driven rules
5. **No big-bang** — each phase has independent convergence gates; a phase can be reverted without affecting others
6. **Capability manifest is the regression contract** — Phase 07 can only proceed when every item shows `status: verified`

Ready for your review. When satisfied, say **proceed** and I'll begin Phase 00 implementation (the safety-net foundation).

Made changes.