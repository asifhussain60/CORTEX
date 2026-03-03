# CORTEX GitHub Copilot Instructions

**Updated:** 2026-03-03 (Total Recall — Phase 117 Production Truth Reconciliation) | **Refresh:** `python3 scripts/refresh_prompt_suite.py`

---

## 🧠 RESPONSE HEADER — MANDATORY (EVERY FIRST RESPONSE PER REQUEST)

**P0 RULE — applies regardless of which LLM is active (GPT-4o, Claude, Gemini, etc.):**

Every **first response** to a user request MUST begin with this exact header block — rendered once, never repeated mid-response or on subsequent turns within the same request:

```
# 🧠 CORTEX {mode}
**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
**Via:** {DisplayName} → {DisplayName}  ← omit if single-hop

> *"{quote}"*
> — {Author}, **{Book}**

---
```

*When `cortex-architect.prompt.md` is active, replace `🧠 CORTEX` with `🛠️ CORTEX Architect`. All other fields are identical.*

**Rules (non-negotiable):**

- ✅ Render ONCE per user request — at the very top of the first response only
- ✅ `**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.` — verbatim, on one line
- ✅ `**Via:**` line shows plain-language orchestrator display names (e.g. `Classifier → TDD Builder`) — omit for single-hop simple responses
- ✅ **Product icon is fixed**: 🧠 for `CORTEX.prompt.md` · 🛠️ for `cortex-architect.prompt.md` — never swapped for a mode-specific icon
- ✅ `{mode}` is a plain-language verb phrase: `Building` · `Fixing` · `Auditing` · `Answering` · `Designing` · `Planning` · `Debugging` · `Investigating` · `Cleaning` · `Introducing`
- ✅ If `cortex-architect.prompt.md` is active: use `🛠️ CORTEX Architect` as the product title; otherwise use `🧠 CORTEX`
- ✅ One blank line between the `**Author:**` / `**Via:**` line and the `>` quote blockquote
- ✅ Quote selected from `📚 Quote Library` in `cortex-response-templates.md` — match `themes` to user intent (TDD/testing → `quality`, security → `security`, refactor → `improvement`, architecture → `architecture`, audit/governance → `discipline`, fix/debug → `systems-thinking`, plan/roadmap → `strategy`, team/process → `flow`, learn/digest → `learning`, default → `universal`)
- ✅ Both quote and attribution inside the same `>` blockquote block — renders as one unified left-accent callout
- ✅ Followed by `---` (Markdown HR — never `<hr>`) after the blockquote
- ❌ NO mode-specific icon (⚡ 🔧 ♻️ etc.) in the H1 heading — 🧠 / 🛠️ are the only valid leading icons
- ❌ NO `**Orchestrator:** {Name} ✅` field — replaced by `**Via:**` breadcrumb only
- ❌ NO separate `*🧭 Classifier → ...*` italic block after `---` — `**Via:**` in the header already IS the breadcrumb; rendering both makes the Classifier appear twice (P1 duplication violation)
- ❌ NO mid-response headers — ONE header per request, period
- ❌ NO secondary title headings inside the response body — the H1 is the only title
- ❌ NO header during silent autonomous execution (after `proceed`) — progress bars only
- ❌ NO fabricated quotes — only quotes from `📚 Quote Library`
- ❌ DO NOT skip or omit — this is a P0 governance rule (Check #14, meta-audit)

**SSOT:** `.github/templates/cortex-response-templates.md` § Response Header — Canonical Spec + § 📚 Quote Library

---

## 🧩 COMPOSABLE SECTIONS — MANDATORY SYNTHESIS RULES

**Authority:** `.github/templates/cortex-response-templates.md` § 📦 Composable Content Sections

Every response is assembled from composable sections. The following rules are **non-negotiable**:

### Assembly Order (canonical)

```
🧠 Session Identity (once per session, first turn only)
→ Response Header (# 🧠 CORTEX {mode} + Author + **Via:** chain + Quote blockquote + ---)
   ↳ **Via:** IS the breadcrumb — the *🧭 ...* italic block MUST NOT repeat it after ---
→ 🪞 Intent Reflection (before any work — first-person, business language)
→ [Work content: 5-Section Golden Format OR Silent Autonomous progress bars]
→ ⏱️ Engagement Timeline (collapsible, 3+ step operations only)
→ 📈 Metrics Dashboard (IMPLEMENT/FIX/REFACTOR completions only)
→ 🎯 Next Steps (educational responses only — Immediate + Later bullets, NO proceed content)
→ ⚡ Proceed Gate  ← work pending: "### ⚡ If you say proceed, I will:" — ALWAYS LAST
→ ✅ Completion State  ← work done: Variant A (phase complete) = "✅ Phase {id} complete." + "### 🚀 Next Phase" handoff; Variant B (non-phase) = "✅ All work is complete." — ALWAYS LAST
```

**CORE-RESP-001 (P0 — non-negotiable):** Every response MUST end with exactly ONE of:
- `⚡ Proceed Gate` — when work is pending user confirmation (`### ⚡ If you say \`proceed\`, I will:` + numbered list)
- `✅ Completion State` — when all work is done. **Two variants:**
  - **Variant A** (a `cortex-master.yaml` phase was marked COMPLETE): `✅ **Phase {id} complete.**` + `### 🚀 Next Phase` sub-block with paste-ready continuation prompt for next VS Code Copilot Chat session (reads next `PLANNED` phase from `cortex-master.yaml`)
  - **Variant B** (non-phase work done): `✅ **All work is complete.**` + confirmation sentence

Never both. Never neither (for any actionable or completed response). Always the absolute last rendered block. Proceed bullets MUST NOT appear inside `## 🎯 Next Steps` — that section ends at "Later:" bullets. The proceed gate lives exclusively in `⚡ Proceed Gate`.

**SSOT for both sections:** `.github/templates/cortex-response-templates.md` § ⚡ Proceed Gate & ✅ Completion State

### Anti-Duplication Contract (MANDATORY — final synthesis cycle)

Before emitting any response, run a **synthesis pass**:

1. **Scan for duplicate headers** — if the same `##` heading appears twice, collapse to one
2. **Scan for duplicate content** — if the same concept appears in multiple sections, keep the first occurrence only and remove subsequent repetitions
3. **Scan for duplicate breadcrumbs** — `**Via:**` in the response header IS the routing chain. NEVER render a separate `*🧭 Classifier → ...*` italic block after `---` — that is a P1 duplication violation (the Classifier appears twice)
4. **Scan for empty headers** — any `##` or `###` with no content below it must be removed (R4: no phantom whitespace)
5. **Enforce block boundaries** — INTRO stops before capabilities, CAPABILITIES stops before LENS detail, LENS stops before orchestrators (no overlap)
6. **Max 800 words** — trim to keep responses scannable and ≤60 second read time

**Rule:** Do NOT emit the response until the synthesis pass is complete. Zero duplication is the standard.

### When to use each template

| Situation | Template to Use |
|-----------|----------------|
| User says `proceed` / `implement` / `yes` / `continue` | Silent Autonomous Mode (progress bars only — NO educational blocks) |
| IMPLEMENT / FIX / REFACTOR / DESIGN / PLAN / AUDIT request | 5-Section Golden Format (before `proceed`) |
| "Who are you?" / "What can you do?" / onboarding | Composable blocks (INTRO + CAPABILITIES + TUTORIAL + NEXT-STEPS) |
| Simple one-line QUERY | Answer directly — skip full 5-section structure |

---

## 🧭 ORCHESTRATOR ENGAGEMENT VISUAL CUE (MANDATORY)

**Every orchestrator invocation in VS Code GitHub Copilot Chat MUST render a visual engagement cue.**

This gives users a real-time signal showing which orchestrator is responding and why — without needing to know class names.

### 🧭 Routing Breadcrumb (always rendered for multi-hop)

**The `**Via:**` field in the response header IS the breadcrumb.** For multi-hop responses, populate `**Via:**` with the plain-language routing chain on the same line as the author/copyright — e.g. `**Via:** Classifier → TDD Builder`. Do NOT render a separate `*🧭 Classifier → ...*` italic block after `---`; that duplicates the chain and makes the Classifier appear twice.

- ✅ Rendered as `**Via:** {DisplayName} → {DisplayName}` in the response header (same block as `**Author:**`)
- ✅ Plain-language display names only (from map below — never class names)
- ✅ Omit `**Via:**` entirely for single-hop simple responses (keep lean)
- ❌ NEVER render a separate `*🧭 ...*` italic breadcrumb block after the `---` separator — `**Via:**` already serves this role
- ❌ Never use `├─ └─` tree characters (collapse in Copilot Chat)

**Display name map (class → plain language):**

| Class Name | Display Name |
|---|---|
| IntentRouter | Classifier |
| MasterOrchestrator | Mission Control |
| TDDOrchestrator | TDD Builder |
| AuditOrchestrator / AuditCoordinator | Audit Coordinator |
| EnforcementOrchestrator | Governance Enforcer |
| HealthOrchestrator | Health Monitor |
| VacuumOrchestrator | Workspace Cleaner |
| RefactoringOrchestrator | Code Improver |
| DebuggerOrchestrator | Debug Tracer |
| DigestSessionOrchestrator | Content Ingestor |
| DesignCoordinator | Architect |
| PlanningOrchestrator | Roadmap Planner |
| WorkflowComposer | Workflow Composer |
| RCAEngine | Root Cause Analyst |
| MarkerInjectionEngine | Debug Injector |
| InteractionOrchestrator | Stage 1 Comprehension |
| LearningOrchestrator | Learning Engine |
| GitOrchestrator | Git Manager |

**Pre-built `**Via:**` values for common commands:**

| Command | `**Via:**` value |
|---|---|
| `/audit` or `/audit fix` | `Classifier → Audit Coordinator → Health Monitor → Workspace Cleaner → Governance Enforcer` |
| `/implement` or `/fix` | `Classifier → TDD Builder` |
| `/refactor` | `Classifier → Code Improver → Workflow Composer` |
| `/health` | `Classifier → Health Monitor` |
| `/vacuum` | `Classifier → Workspace Cleaner` |
| `/debug` | `Classifier → Debug Tracer → Debug Injector` |
| `/totalrecall` | `Classifier → Mission Control → Audit Coordinator → Code Improver` |
| `/rca` | `Classifier → Learning Engine → Root Cause Analyst` |
| `/sync` | `Classifier → Git Manager → Workflow Engine` |

### ⏱️ Engagement Timeline (collapsible, 3+ step operations)

Wrap in `<details>` always. Shows per-orchestrator timing. See SSOT for full format.

### 🔵 Stage Progress (in-progress pulse)

Phase-list+bar format is MANDATORY — bar-only is a P1 violation. See SSOT for full format.

---

## About CORTEX

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework:

- **320 Orchestrator files** across 15 domains (`core:139 domain:33 support:55 health:31 intelligence:17 persona:7 workflow:7 validation:13 git:5 _top_level:3 response:3 registry:2 synthesis:2 tools:2 strategies:1`) — all satisfy IOrchestrator protocol
- **30 MCP Tools registered** in `mcp_registry.py` via Pylance-style stdio server — 54 tool files in `cortex/mcp/tools/`
- **36 Governance YAMLs** across `cortex-registry/core/` (23) and `cortex-registry/governance/` (13) enforced at pre-commit, CI, and runtime
- **TDD-First Development** — CORE-008: tests before implementation, no exceptions
- **Sweep Completeness Contract** — CORE-064: every FIX/REFACTOR/AUDIT exhausts its full issue catalogue (no partial sweeps)
- **LENS Analysis** — workspace-aware code intelligence (Language → Examination → Navigation → Synthesis)
- **Unified Reinforcement Signal (URS)** — closed-loop learning across all orchestrators via `cortex_learning` MCP tool (`emit|history|decay|promote|quarantine|metrics|rca`)
- **RCA Memory Engine** — 4 root cause analysis methodologies (Five-Whys, Fishbone, Fault-Tree, Causal-Chain) via `cortex_learning` op=`rca`; `cortex/intelligence/learning/rca_engine.py`
- **Multi-Stack Debug Pipeline** — 8 injection strategies (3 Python + 5 multi-stack: Frontend/HTML-Vision/API/SQL/DotNet), Vision API, auto-cleanup
- **Self-Healing Prompt Suite** — `scripts/refresh_prompt_suite.py` introspects live architecture + SQLite audit logs to regenerate all prompts/agents with zero drift
- **29 Intent Types** routed via IntentRouter (`cortex/orchestrators/core/intent_router_impl.py`) — plus INTRODUCE for interactive onboarding
- **1 Canonical Package** — all imports use `cortex.*` (no `cortex_intelligence`, `cortex_lens`, or `cortex.brain`)
- **LLM-Orchestration Architecture** — CORTEX orchestrates the host LLM (GitHub Copilot/GPT) as the AI engine; it does not embed ML models
- **Intelligence Facade** — `cortex/intelligence/facade.py` — `IntelligenceFacade` is the single canonical entry point replacing 3 legacy facades (Phase 107 Sub-Phase C)

---

## Architecture

| Metric | Value |
|---|---|
| Package | `cortex` (single canonical) |
| Orchestrator files | 320 across 15 domains in `cortex/orchestrators/` |
| MCP Tools | 30 registered in `mcp_registry.py`; 54 tool files in `cortex/mcp/tools/` |
| Top-level Dirs | 21 under `cortex/` |
| Governance YAMLs | 36 across `cortex-registry/core/` (23) and `cortex-registry/governance/` (13) |
| Test Suite | ~18,874 tests collected (run `python3 -m pytest --collect-only -q` for current count) |
| Parallel Testing | pytest-xdist (`-n auto --dist loadscope`) |
| Phases | 97 completed, 5 planned |
| Master YAML | 348/800 lines (THIN INDEX CONTRACT) |
| Intent Types | 29 (see `cortex/models/canonical_enums.py`) |
| SQLite Databases | 7 in `.cortex-runtime/` (cleanup: `refresh_prompt_suite.py --db-cleanup`) |
| **Intelligence Facade** | `cortex/intelligence/facade.py` — `IntelligenceFacade` canonical entry (Phase 107) |

---

## MCP Architecture

CORTEX uses **Pylance-style MCP** — works automatically like Pylance (no manual server startup). The server auto-starts when VS Code opens the workspace via stdio transport.

**MCP ARCHITECTURE:** Pylance-style stdio transport, auto-detected by VS Code Copilot Chat. Configuration lives in `.vscode/settings.json`.

**Configuration** (`.vscode/settings.json`):
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**MCP Detection Methods — 3 ways to verify MCP is active:**

- **Method 1 (Tool Registry):** Call `cortex_verify` (op: `mcp`) in Copilot Chat — if it responds, MCP is running. This checks the Tool Registry directly.
- **Method 2 (Environment Variable / Settings):** Check `.vscode/settings.json` for `github.copilot.chat.mcpServers.cortex` key — if present, server is configured.
- **Method 3 (Network Port / Process):** Run `python3 -m cortex.mcp` in terminal — if it starts without import errors, MCP server is healthy. Check port binding or process listing to verify.

**Setup:** Run `python3 scripts/setup-mcp.py` for cross-platform MCP configuration (auto-detects Windows/macOS/Linux).

---

## Development Standards

| Rule | Description |
|---|---|
| CORE-002 | All output inline — never create .md/.txt report files |
| CORE-008 | TDD mandatory — write failing test first, then implement |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-048 | Holistic validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Silent autonomous execution (progress bars only) |
| CORE-064 | Sweep Completeness Contract — no partial sweeps; every FIX/REFACTOR/AUDIT must exhaust its full catalogue |
| CORE-068 | Universal Convergence Gate — detect→fix→rescan until 0 P0/P1 before AC_COMPLETE (max 3 cycles) |

**MCP Tool Authoring — `validate_orchestrator_context` guard:** All MCP tool functions that
call `validate_orchestrator_context(orchestrator_context)` must guard the call:
```python
if orchestrator_context is not None:
    validate_orchestrator_context(orchestrator_context)
```
This allows direct test invocation without a `MasterOrchestrator` context while still
enforcing routing in production (where context is always supplied).

---

## Workflow Composer Architecture

**All code-touching operations flow through declarative workflow templates** — no inline procedural logic in prompts or agents.

**Specification:** `cortex-registry/workflows/workflow-composer-spec.yaml`

### 3-Tier Hierarchy

| Tier | Purpose | Location |
|------|---------|----------|
| **Tier 1: Primitives** | Atomic, reusable steps (gates, loops, markers) | `cortex-registry/workflows/templates/primitives/` |
| **Tier 2: Mode Workflows** | One per execution mode (IMPLEMENT, FIX, REFACTOR, etc.) | `cortex-registry/workflows/templates/{category}/` |
| **Tier 3: Composite Pipelines** | Multi-mode compositions (audit-fix, totalrecall) | `cortex-registry/workflows/templates/composites/` |

### Intent → Workflow Routing (SSOT: `workflow-composer-spec.yaml` § intent_routing)

| Intent | Workflow Template | Pre-Gate |
|--------|------------------|----------|
| IMPLEMENT | `sdlc/implement-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| FIX | `sdlc/fix-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| REFACTOR | `quality/refactor-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| AUDIT | `audit/audit-fix-pipeline.yaml` | — |
| VACUUM | `maintenance/vacuum-workflow.yaml` | — |
| HEALTH | `maintenance/health-check-workflow.yaml` | — |
| DEBUG | `debugging/multi-stack-debug-pipeline.yaml` | — |
| DIGEST | `lifecycle/digest-workflow.yaml` | — |
| TOTALRECALL | `lifecycle/totalrecall-workflow.yaml` | — |
| SYNC | `lifecycle/sync-workflow.yaml` | — |
| TRAIN | `lifecycle/train-workflow.yaml` | — |
| META-AUDIT | `governance/meta-audit-workflow.yaml` | — |
| **FRONTEND** | **`frontend/html-view-lifecycle.yaml`** | **`primitives/governance/holistic-validation-gate.yaml`** |
| TDD | `tdd/tdd-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| TYPESCRIPT | `frontend/typescript-refactor-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| CSHARP_REFACTOR | `backend/csharp-refactor-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| CSHARP_SECURITY | `backend/csharp-security-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |
| SECURITY_AUDIT | `security/security-compliance-audit.yaml` | — |
| ONBOARD | `lifecycle/onboarding-workflow.yaml` | — |
| DECOMPOSE | `lifecycle/service-decomposition-workflow.yaml` | `primitives/governance/holistic-validation-gate.yaml` |

### Universal Primitives (injected into every code-modifying workflow)

| Primitive | Purpose |
|-----------|---------|
| `primitives/execution/ac-marker-emit.yaml` | AC_START / AC_COMPLETE markers |
| `primitives/execution/git-checkpoint.yaml` | Safe rollback point before changes |
| `primitives/governance/dor-display.yaml` | Definition of Ready display |
| `primitives/governance/holistic-validation-gate.yaml` | CORE-048 pre-execution gate |
| `primitives/governance/challenge-gate.yaml` | Risk-based alternative presentation |
| `primitives/governance/sweep-catalogue-open.yaml` | CORE-064 sweep tracking open |
| `primitives/governance/sweep-catalogue-close.yaml` | CORE-064 sweep tracking close |
| `primitives/validation/detect-fix-rescan-loop.yaml` | CORE-068 convergence gate |

---

## File Organization

```
cortex/              ← Python source (21 dirs)
  orchestrators/     ← 320 orchestrator files across 15 domains (core:139 domain:33 support:55 health:31 intelligence:17 +more)
  mcp/tools/         ← 30 registered MCP tools (54 tool files)
  core/              ← OrchestratorProtocolMixin (primary, Phase 58), OrchestratorBase (legacy), FileFactory, WorkflowEngine
  testing/           ← Test framework, parallel runner, quality gate
  intelligence/      ← LENS, domain brain, knowledge synthesis
  governance/        ← Rule enforcement, compliance
cortex-registry/     ← YAML governance rules, patterns, plans
tests/               ← All tests (mirrors cortex/ structure — excludes dissolved packages: cortex_brain, cortex_intelligence, cortex_lens)
.cortex-runtime/     ← Runtime data (logs, traces, 7 .db files)
.github/             ← CI/CD, prompts, agents, templates
cortex-docs/         ← User-facing documentation (HTML/CSS only)
```

---

## Key Entry Points

| Component | Location |
|---|---|
| MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` |
| IntentRouter | `cortex/orchestrators/core/intent_router.py` |
| InteractionOrchestrator | `cortex/orchestrators/core/interaction_orchestrator.py` (Stage 1 LENS per-turn comprehension) |
| TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| HealthOrchestrator | `cortex/orchestrators/health/health_orchestrator.py` |
| VacuumOrchestrator | `cortex/orchestrators/health/vacuum_orchestrator.py` — 8-stage pipeline: naming → root → empty → orphan → markdown → digest → build artifacts → OS artifacts |
| DebuggerOrchestrator | `cortex/orchestrators/support/debugger_orchestrator.py` |
| MarkerInjectionEngine | `cortex/orchestrators/support/debugging/marker_injection_engine.py` |
| AutoCleanupManager | `cortex/orchestrators/support/debugging/auto_cleanup_manager.py` |
| RCA Engine | `cortex/intelligence/learning/rca_engine.py` (Phase 87 — 4 methodologies) |
| RCA Store | `cortex/intelligence/learning/rca_store.py` |
| **Intelligence Facade** | `cortex/intelligence/facade.py` — `IntelligenceFacade` canonical entry point (Phase 107 Sub-Phase C) |

---

## Cross-Cutting Intelligence (Universal — All Orchestrators)

**Every orchestrator invocation must emit AC markers** — handled by the `primitives/execution/ac-marker-emit.yaml` workflow primitive.

**Primitive:** `cortex-registry/workflows/templates/primitives/execution/ac-marker-emit.yaml`
**Persistence:** `.cortex-runtime/traces/orchestrator-traces.db`
**Enforced by:** `EnforcementOrchestrator` pre-commit hook + `cortex_validate` (op: `compliance`)
**Audited by:** Check #19 (SQLite activity log health) + Meta-Audit Check #23

**AC Marker Format Standard:** `AC-{DOMAIN}-{SEQUENCE}` (e.g. `AC-P89-001`, `AC-CORE-042`). Domain is the phase or module identifier; sequence is a 3-digit zero-padded counter.

**AC Marker Rules:**
- `AC_START` at entry point of every public orchestrator method
- `AC_COMPLETE` on success with ✅ + timing (ms)
- `AC_COMPLETE` on failure with ❌ + error classification
- No orphaned `AC_START` without matching `AC_COMPLETE` (P0 governance violation)

**SQLite Activity Logging:** 7 databases in `.cortex-runtime/`:

| Database | Path | Tables | Purpose |
|---|---|---|---|
| orchestrator-traces | `traces/orchestrator-traces.db` | `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs`, `trace_*` | Primary trace store |
| rca-store | `rca/rca_store.db` | `rca_analyses`, `prevention_rules`, `recurrence_*` | Root cause analysis |
| audit | `audit.db` | `audit_events`, `orchestrator_traces`, `governance_checks`, `phase_progress` | Audit events |
| governance | `governance.db` | `scaffolder_audit_log` | Scaffolder audit |
| conversations | `state/conversations.db` | `conversations`, `turn_records` | Session state |
| wiring-audit | `wiring/contract_validation_audit.db` | `validation_audit`, `contract_versions` | Wiring contracts |
| intelligence-audit | `intelligence/intelligence_audit.db` | `intelligence_audit` | Intelligence traces |

**Cleanup:** `python3 scripts/refresh_prompt_suite.py --db-cleanup` (30-day retention + VACUUM). Guard: `CORTEX_DISABLE_DB_CLEANUP=true` to skip (CI environments).

---

## ⚡ Quick Command Reference

| Command | What It Does | Stages |
|---------|-------------|--------|
| **`/audit fix`** | **Full production-readiness scan + autonomous fix** | 9 stages (see below) |
| `/audit` | Scan only, no auto-fix | Stages 1–6 |
| `/vacuum` | Markdown sprawl + root clutter + OS artifacts + build artifacts cleanup | Stage 5 only |
| `/health` | All 22 orchestrator health endpoints | Stage 4 only |
| `/healthcheck` | Full test suite (all tiers, parallel) | On-demand |
| `/upgrade` | Check origin/main, merge if ahead, run audit fix | Inflight upgrade |
| `/digest {path}` | Intelligent content ingestion (3-pipeline) | — |
| `/onboard {repo}` | LENS analysis + SQLite dashboard | — |
| `/challenge {request}` | Generate ≥2 alternatives with trade-offs | — |
| `/totalrecall` | Production certification — 10-phase autonomous pipeline (delta→drift→regression→optimize→wire→memory→vacuum→db→harden→certify) | 10 phases |
| `/sync target={path}` | One-way privacy-safe sync: CORTEX → company folder | — |
| `/debug {path}` | Multi-stack debug: inject → capture → analyze → fix-plan → cleanup | 5 phases |
| `/debug-inject {path}` | Insert CORTEX_DEBUG markers (8 strategies: 3 Python + 5 multi-stack) | INJECT |
| `/debug-cleanup` | Remove all CORTEX_DEBUG markers across all languages | CLEANUP |

**Phase 85 — Response Format (canonical):** Every progress display uses the **phase-list+bar** format (not bar-only). SSOT: `.github/templates/cortex-response-templates.md`. Engagement blocks: `BLOCK-ENGAGEMENT-BREADCRUMB` (routing chain, always rendered), `BLOCK-ENGAGEMENT-TIMELINE` (collapsible timing), `BLOCK-PHASE-ROADMAP` (full journey at operation start).

**Phase 86 — Debug strategies (8 total):**
- `TestFailureStrategy`, `RefactorRegressionStrategy`, `GovernanceViolationStrategy` — existing Python strategies
- `FrontendConsoleStrategy` (JS/TS/React/Angular/Vue), `HtmlVisionMappingStrategy` (Vision API + DOM), `ApiTraceStrategy` (REST/GraphQL/gRPC), `SqlTraceStrategy` (SQL Server/Oracle/PostgreSQL), `DotNetTraceStrategy` (C#/.NET) — Phase 86 additions

**Phase 87 — RCA Memory Engine (121 GREEN tests):**
- `RCAEngine` — 4 methodologies: Five-Whys, Fishbone (Ishikawa), Fault-Tree, Causal-Chain
- `RCAStore` — SQLite-backed persistence at `.cortex-runtime/traces/rca.db`
- Exposed via `cortex_learning` MCP tool (op=`rca`, sub-actions: `analyze|query|list`)
- Category → methodology auto-selection: TECHNOLOGY→Five-Whys, PROCESS/PEOPLE→Fishbone, DATA→Causal-Chain
- Each completed RCA generates a `PreventionRule` (ADVISORY by default)

### `/audit fix` — 9-Stage Pipeline

**Workflow Template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`
**Loop Primitive:** `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`
**Test Tier Manifest:** `cortex-registry/workflows/templates/testing/test-tier-manifest.yaml`
**Activity log:** `.cortex-runtime/traces/orchestrator-traces.db`
**Convergence guarantee:** Stages 7–8 loop until `p0_count == 0 and p1_count == 0` (CORE-064) — not a single pass.

---

## 📋 Master Plan Decomposition — THIN INDEX CONTRACT

**`cortex-master.yaml` is a REFERENCE INDEX only — never a detail document.**

| Rule | Detail |
|------|--------|
| **Max size** | ≤ 800 lines (alarm at 700) |
| **Prohibited inline** | `phases`, `gap_catalogue`, `tdd_sequence`, `rewrites`, `new_files`, `files_to_edit`, `implementation`, `code_snippets` |
| **Allowed per entry** | `id`, `title`, `status`, `priority`, `sweep_id`, `gaps`, `sub_phases`, `file`, `note`, `phases` (list of IDs only) |
| **Detail location** | `cortex-registry/planning/phases/planned/<phase-id>.yaml` (active/upcoming) |
| **Completed detail** | `cortex-registry/planning/phases/completed/<phase-id>.yaml` |
| **Template** | `cortex-registry/planning/phases/_template.yaml` |
| **Lifecycle governance** | `cortex-registry/workflows/templates/governance/master-plan-phase-lifecycle.yaml` |

### Decomposition Checks — Run at TWO points:

**① BEFORE adding any phase to cortex-master.yaml (checkpoint_create):**
1. Create dedicated file first at `cortex-registry/planning/phases/planned/<phase-id>.yaml`
2. Use `cortex-registry/planning/phases/_template.yaml` as scaffold
3. Write ALL detail in the dedicated file (gap catalogue, TDD sequences, acceptance criteria)
4. Add ONLY a thin reference entry to `cortex-master.yaml`
5. Verify `cortex-master.yaml` is still ≤ 800 lines: `wc -l cortex-registry/cortex-master.yaml`
6. Validate YAML: `python3 -c "import yaml; yaml.safe_load(open('cortex-registry/cortex-master.yaml'))"`

**② BEFORE marking any phase COMPLETE in the pipeline (checkpoint_complete):**
1. All gaps in `sweep_catalogue` have `status: CLOSED` (CORE-064)
2. All acceptance criteria documented with ✅ in the dedicated file
3. Move dedicated file from `planned/` → `completed/`
4. Update `file:` reference in `cortex-master.yaml` to point to `completed/`
5. Update `status: COMPLETE` in both `cortex-master.yaml` entry and dedicated file
6. Run smoke gate: `make test-smoke`
7. Verify `cortex-master.yaml` remains ≤ 800 lines

### Why This Exists:
`cortex-master.yaml` grew from ~150L to 3,007L because inline phase detail was written directly to it. This caused: 40+ YAML syntax errors, un-reviewable diffs, context exhaustion when loading the file, and no single-file accountability for each phase's detail. The THIN INDEX CONTRACT prevents recurrence.

---

## References

- Architecture: `cortex-docs/architecture-recommendation.md`
- MCP Setup: `.github/prompts/MCP-SETUP-GUIDE.md`
- Security: `cortex-docs/security.md`
- Architect Prompt: `.github/prompts/cortex-architect.prompt.md`
- Response Templates: `.github/templates/cortex-response-templates.md`
- Master Plan Lifecycle: `cortex-registry/workflows/templates/governance/master-plan-phase-lifecycle.yaml`
- Phase Template: `cortex-registry/planning/phases/_template.yaml`
- Debug Agent: `.github/agents/support/cortex-debugger.md`
- Debug Pipeline Template: `cortex-registry/workflows/templates/debugging/multi-stack-debug-pipeline.yaml`
- **Prompt Refresh Playbook**: `scripts/refresh_prompt_suite.py` (self-healing prompt suite)

---

## ⛔ Test Execution — MANDATORY RULES

**Four-tier optimised execution. Never bypass `run_tests.py`.**

| Mode | Command (macOS/Linux) | Command (Windows) | When to use |
|---|---|---|---|
| **preflight** | `make test-preflight` | `python scripts\run_tests.py preflight` | `/audit fix` Stage 9 — critical wiring (< 10s) |
| **changed** | `make test-changed` | `python scripts\run_tests.py changed` | TDD inner loop — after every save |
| **smoke** | `make test-smoke` | `python scripts\run_tests.py smoke` | Quick sanity before commit (< 60s) |
| **unit** | `make test` | `python scripts\run_tests.py unit` | Default local dev |
| **parallel** | `make test-parallel` | `python scripts\run_tests.py parallel` | Pre-commit full speed |
| **healthcheck** | `make test-healthcheck` | `python scripts\run_tests.py healthcheck` | Full suite on-demand (parallel) |
| **batch** | `make test-batch` | `python scripts\run_tests.py batch` | CI gate (sequential) |

**Three Layers:**
- **Layer 1 — Parallel:** `pytest-xdist` with `-n auto --dist loadscope`. 10 cores → ~3–4× faster. Falls back to sequential if xdist is absent.
- **Layer 2 — Smart:** `pytest-testmon` with `--testmon`. Runs only tests covering changed source files. Ideal for TDD. Incompatible with xdist (runs sequentially). Set `CORTEX_DISABLE_TESTMON=true` for a clean full run.
- **Layer 3 — Import:** `--import-mode=importlib` in `pytest.ini`. Cuts cold collection from ~17s → ~7s.

| ✅ DO — Canonical Methods | ❌ NEVER — Forbidden Patterns |
|---|---|
| `make test-preflight` / `make test-smoke` | `python3 -m pytest tests/ -x -q` |
| `python3 scripts/run_tests.py {mode}` | `pytest --tb=no -q` (silences batch reporter) |
| VS Code tasks (tasks.json) — all modes | `pytest -o addopts=` (wipes import-mode + sugar settings) |
| `CORTEX_WORKERS=4 make test-parallel` | `.venv/bin/python -m pytest` (hard-codes Unix venv path) |

**When running tests in a terminal, always use:**
```
make test-preflight  # fastest — audit gate (< 10s)
make test-changed    # TDD loop (testmon)
make test-smoke      # sanity gate (< 60s)
```
or a VS Code task from `tasks.json`.

**Windows users:** All `make` commands have VS Code Task equivalents in `tasks.json`.
Use `python scripts\run_tests.py {mode}` in PowerShell/cmd — `python3` may not be on PATH.

**Environment overrides:**
- `CORTEX_WORKERS=4` — cap xdist to 4 workers (CI with limited cores)
- `CORTEX_DISABLE_PARALLEL=true` — force sequential (any mode)
- `CORTEX_DISABLE_TESTMON=true` — skip testmon DB (clean run after large refactor)

---

## 🔄 Self-Healing Prompt Suite — Repeatable Refresh Playbook

**Script:** `python3 scripts/refresh_prompt_suite.py`
**Purpose:** Regenerate `copilot-instructions.md`, `AGENT-INDEX.md`, and validate all prompts/agents against live architecture.

### Playbook Steps (execute in order)

| Step | Command | What It Does |
|---|---|---|
| 1 | `python3 scripts/refresh_prompt_suite.py --counts-only` | Introspect live architecture: orchestrators, MCP tools, tests, governance |
| 2 | `python3 scripts/refresh_prompt_suite.py --db-cleanup` | Enforce 30-day retention, delete orphaned AC_START, VACUUM all 7 databases |
| 3 | `python3 scripts/refresh_prompt_suite.py` | Full refresh: cleanup → counts → validate → report |
| 4 | `python3 scripts/refresh_prompt_suite.py --dry-run` | Preview all changes without writing |

### When to Run

- **After every phase completion** — counts drift, new orchestrators/tools added
- **After `/audit fix`** — validates prompt/agent accuracy against live state
- **After major refactoring** — ensures no stale references to deleted files
- **Monthly maintenance** — SQLite cleanup + VACUUM

### SQLite Cleanup Details

| Database | Retention | Cleanup Actions |
|---|---|---|
| orchestrator-traces | 30 days | Delete old traces, orphaned AC_START, VACUUM |
| rca-store | 30 days | Retain analyses, prune old prevention rules |
| conversations | 90 days | Longer retention for session continuity |
| All others | 30 days | Standard retention + VACUUM |

**Guard:** Set `CORTEX_DISABLE_DB_CLEANUP=true` to skip cleanup in CI environments.

### Architecture Drift Detection

The playbook detects drift between documentation and live code:
- Orchestrator file count mismatch → P0 violation
- MCP tool registry vs tool files mismatch → P1 violation
- Intent types in `canonical_enums.py` not covered in agent routing → P1 violation
- `cortex-master.yaml` exceeding 500 lines → P0 violation
- Stray `.db` files outside `.cortex-runtime/` → P1 violation

---

## ✅ Preflight Requirements Validation

CORTEX auto-validates `requirements.txt` at session start via `UpgradeOrchestrator.validate_requirements()`. If the environment is incomplete, CORTEX will attempt `pip install -r requirements.txt` autonomously before proceeding.

- **Silent if all packages satisfied** (CORE-049)
- **P0 hard-stop** if any `[PREFLIGHT CRITICAL]` package is missing
- **To skip** (CI/CD): set `CORTEX_SKIP_PREFLIGHT=true`
