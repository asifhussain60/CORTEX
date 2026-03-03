# CORTEX Agent Index

**Updated:** 2026-03-03 (Total Recall — Production Truth Reconciliation) | **Refresh:** `python3 scripts/refresh_prompt_suite.py`  
**Package:** `cortex` (single canonical — no `cortex_intelligence`, `cortex_lens`, `cortex.brain`)  
**Phases:** 97 completed, 5 planned | **Tests:** ~18,874 | **Intent Types:** 29

---

## Loading Protocol

**CRITICAL:** This file replaces bulk agent loading. Load specific agents ONLY when needed per intent.

```yaml
Default Context: THIS FILE ONLY (~200 tokens)
Per Intent Load: 1-2 relevant agents (~1,000-2,500 tokens)
```

**Drift Detection Protocol (Total Recall Learnings):**
- All numeric values in this file are SOURCE OF TRUTH for agent consumption
- Values derived from file system via `python3 scripts/refresh_prompt_suite.py --counts-only`
- Any drift between this file and implementation triggers P0 validation failure
- Verification command: `python3 scripts/refresh_prompt_suite.py --counts-only`

### Status Icons

| Icon | Meaning |
|------|---------|
| ✅ | Complete |
| 🔵 | In Progress |
| ⚪ | Pending |
| 🔴 | Failed/Blocked |

**Progress Bar SSOT:** `.github/templates/cortex-response-templates.md` — all orchestrators use this single golden template.

---

## Architecture Quick Reference

| Metric | Value |
|--------|-------|
| Orchestrator files | **320** across 15 domains (`core:139 domain:33 support:55 health:31 intelligence:17 persona:7 workflow:7 validation:13 git:5 _top_level:3 response:3 registry:2 synthesis:2 tools:2 strategies:1`) |
| MCP Tools | **30 registered** in `mcp_registry.py`; 54 tool files in `cortex/mcp/tools/` |
| Governance YAMLs | **36** across `cortex-registry/core/` (23) and `cortex-registry/governance/` (13) |
| Package | `cortex` (single) |
| Tests | **~18,874** collected |
| Intent Types | **29** (see `cortex/models/canonical_enums.py`) |
| Entry Point | MasterOrchestrator → IntentRouter → InteractionOrchestrator → Domain Orchestrator |
| URS | Unified Reinforcement Signal — closed-loop learning (`cortex_learning` tool: `emit|history|decay|promote|quarantine|metrics|rca`) |
| RCA Engine | 4 methodologies: Five-Whys, Fishbone, Fault-Tree, Causal-Chain (`cortex/intelligence/learning/rca_engine.py`) |
| Debug Strategies | 8 total: 3 Python + 5 multi-stack (Frontend/HTML-Vision/API/SQL/DotNet) |
| Response Format | phase-list+bar mandatory; SSOT: `.github/templates/cortex-response-templates.md` |
| Engagement Blocks | BLOCK-ENGAGEMENT-BREADCRUMB, BLOCK-ENGAGEMENT-TIMELINE, BLOCK-PHASE-ROADMAP |
| SQLite Databases | 7 in `.cortex-runtime/` — cleanup: `python3 scripts/refresh_prompt_suite.py --db-cleanup` |
| Prompt Refresh | `python3 scripts/refresh_prompt_suite.py` — self-healing, architecture-introspecting |

---

## Agent Registry

### Core Agents

| Agent | Purpose | Load When |
|-------|---------|-----------|
| **cortex.md** | Master orchestrator — routes all requests | Any production request |
| **cortex-architect.md** | Mode router + challenge enforcer + production readiness | Architecture, audits, design |
| **cortex-holistic-validator.md** | Pre-implementation validation gate | Before IMPLEMENT/FIX/REFACTOR |
| **cortex-auditor.md** | Codebase health + P0-P3 scanning | `/audit`, quality analysis |
| **cortex-executor.md** | Code execution + TDD implementation | Running tests, implementation |
| **cortex-interactive.md** | Conversational mode | Questions, exploratory |
| **cortex-meta-auditor.md** | Meta-level governance auditing | Governance coherence checks |
| **cortex-master-plan-auditor.md** | Master plan validation | Plan integrity verification |

### Specialist Agents

| Agent | Purpose | Load When |
|-------|---------|-----------|
| **cortex-trainer.md** | Gap-driven template evolution — analyze repos, detect gaps, propose changes | `/train {path}`, "learn from {repo}" |
| **cortex-sync-agent.md** | 4-gate one-way sync: PULL→DIFF→SANITIZE→MERGE into company folder | `/sync target=<path>` — cross-repo privacy-safe sync |
| **cortex-sts-refactoring.md** | STS pipeline: 7-gate refactoring for external codebases | `cortex-sts/` REFACTOR sessions, BadMonolith-style analysis |
| **cortex-digest.md** | Learning extraction from chat history | Processing chat files |
| **cortex-environment-setup.md** | Environment validation | Pre-flight checks, setup issues |
| **cortex-phase-resolver.md** | Plan phase management | `/plan` mode |
### Documentation Agents

**Directory:** `.github/agents/docs/`
**Prompt:** `.github/prompts/cortex-doc.prompt.md`
**Trigger:** `/doc`, `/doc-discover`, `/doc-drift`, `/doc-sync`, `/doc-narrative`, `/doc-audit`, `/doc-release`, `/doc-diagrams`, `/doc-media`

| Agent | Role | Pipeline Phase |
|-------|------|----------------|
| **git-discovery-agent.md** | Git history inspection, change classification | 1 — Discovery |
| **drift-detection-agent.md** | Implementation vs documentation cross-reference | 2 — Drift Detection |
| **doc-sync-agent.md** | Update `.content/`, glossary, media prompts | 3 — Synchronization |
| **diagram-regeneration-agent.md** | Regenerate Mermaid/D3.js diagrams | 3 — Synchronization |
| **media-prompt-agent.md** | Maintain DALL-E image + video script prompts | 3 — Synchronization |
| **narrative-continuity-agent.md** | Guard Awakening of CORTEX story arc | 4 — Narrative Update |
| **comedy-enhancement-agent.md** | Apply comedic writing principles to chapters (INTERNAL ONLY — sub-agent of narrative-continuity) | 4 — Comedy Enhancement |
| **coverage-audit-agent.md** | Validate completeness, produce certification | 5 — Certification |
| **release-notes-agent.md** | Generate changelogs from Git diffs | 5 — Certification |
| **request-rephrase-orchestrator.md** | Request token optimization | `/rephrase` command |
| **architecture-integrity-agent.md** | Wiring alignment enforcement | Pre-commit, CI/CD |
| **cortex-debugger.md** | Multi-stack debugging: 8 strategies + Vision API + auto-cleanup ✅ Phase 86 complete | `/debug`, "trace", "diagnose" |
| **cortex-learning** (via `cortex_learning` op=`rca`) | Phase 87 RCA Memory Engine: root cause analysis (4 methodologies: Five-Whys, Fishbone, Fault-Tree, Causal-Chain) | "root cause", "why did it fail", "rca", `/rca` |

### Support Files

| File | Purpose |
|------|---------|
| **phase-creation-standards.md** | Standards for new phases |
| **cleanup-audit-guide.md** | Cleanup procedure reference |
| **STAGE-0-GOVERNANCE-AUDIT-SPEC.md** | Governance audit specification |

### Certification Agents (Total Recall)

**Directory:** `.github/agents/certification/`
**Prompt:** `.github/prompts/cortex-total-recall.prompt.md`
**Trigger:** `/totalrecall`

| Agent | Role | Phases |
|-------|------|--------|
| **cortex-certification-coordinator.md** | Pipeline orchestrator, state persistence, multi-session continuity | ALL |
| **cortex-audit-agent.md** | Git delta analysis, drift detection, duplication discovery | 1–2 |
| **cortex-regression-agent.md** | Regression identification, dead code, bloat, backward compatibility | 3 |
| **cortex-refactor-agent.md** | Prompt/agent optimization, Intelligence Diamond wiring validation | 4–5 |
| **cortex-memory-agent.md** | Adaptive learning, failure patterns, document lifecycle hygiene | 6 |
| **cortex-vacuum-agent.md** | Workspace cleanup — markdown sprawl, empty dirs, orphans, OS/build artifacts | 7 |
| **cortex-db-agent.md** | SQLite integrity, schema optimization, self-healing migrations | 8 |
| **cortex-certification-agent.md** | Production hardening, scoring, release sign-off, report generation | 9–10 |

---

## Total Recall — Production Certification Authority

**Authority:** `.github/prompts/cortex-total-recall.prompt.md`
**Trigger:** `/totalrecall`, or when production readiness certification is needed
**Purpose:** Autonomous 10-phase production certification pipeline

**10-Phase Pipeline:**
1. **DELTA ANALYSIS** — Git diff since last execution, build change manifest
2. **DRIFT DETECTION** — Numeric, version, structural, architectural, config, dependency drift
3. **REGRESSION SCAN** — Test regressions, dead code, bloat, duplicates, backward compat
4. **PROMPT OPTIMIZATION** — Holistic review of `copilot-instructions.md`, `prompts/`, `agents/`
5. **INTELLIGENCE WIRING** — Validate Intelligence Diamond (Reasoning, Memory, Orchestration, Validation)
6. **MEMORY HYGIENE** — Adaptive learning, document lifecycle, recurring failure detection
7. **WORKSPACE CLEANUP** — VacuumOrchestrator 8-stage cleanup pipeline
8. **SQLITE INTEGRITY** — Schema optimization, self-healing migrations, unbounded growth prevention
9. **PRODUCTION HARDENING** — 12-point hardening checklist (H1–H12)
10. **CERTIFICATION** — Weighted scorecard, release sign-off or block

**Certification Levels:** 🟢 CERTIFIED (≥95%) · 🟡 CONDITIONAL (85–94%) · 🟠 DEFERRED (70–84%) · 🔴 BLOCKED (<70%)

**Validation Command:** `python3 scripts/validate-architecture-counts.py` (should output: ALL CHECKS PASSED)

---

## Sweep Completeness Contract (CORE-064)

**New in Phase 16.** Every FIX, REFACTOR, and AUDIT-with-fix session opens a durable
`SweepCatalogue` before routing and is BLOCKED from completing until all catalogued items
are resolved or explicitly approved as WONT-FIX.

| Component | Location | Role |
|-----------|----------|------|
| `SweepCatalogueOrchestrator` | `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` | Opens, tracks, asserts catalogue |
| `cortex_sweep_status` MCP tool | `cortex/mcp/tools/sweep_status_tool.py` | Surfaces open items to user |
| CORE-064 | `cortex-registry/core/tier0-skull/skull-rules.yaml` | Governance rule — severity: blocked |

**VacuumOrchestrator guard:** Never deletes `.cortex-runtime/sweeps/*.db` — open catalogue protection.  
**HealthOrchestrator check:** Includes `SweepCatalogueOrchestrator` in L1 wiring validation.

---

## Intent → Agent Mapping

| User Intent | Load These Agents | Token Cost |
|-------------|-------------------|-----------|
| **IMPLEMENT** | cortex.md + cortex-holistic-validator.md + cortex-executor.md | ~7,000 |
| **FIX** | cortex.md + cortex-holistic-validator.md + cortex-executor.md | ~7,000 |
| **REFACTOR** | cortex.md + cortex-holistic-validator.md + cortex-executor.md | ~7,000 |
| **AUDIT** | cortex.md + cortex-architect.md + cortex-auditor.md | ~8,000 |
| **AUDIT FIX** | cortex.md + cortex-auditor.md + architecture-integrity-agent.md + cortex-meta-auditor.md | ~12,000 |
| **TOTALRECALL** | cortex-total-recall.prompt.md → certification-coordinator.md + 7 specialist agents | ~8,800 |
| **INVESTIGATE** | cortex.md + cortex-architect.md | ~6,000 |
| **QUERY** | cortex.md + cortex-interactive.md | ~4,500 |
| **DESIGN** | cortex.md + cortex-architect.md | ~6,000 |
| **PLAN** | cortex-architect.md + cortex-phase-resolver.md | ~6,000 |
| **DIGEST** | cortex-architect.md + cortex-digest.md | ~6,000 |
| **TRAIN** | cortex-trainer.md + cortex-sts-refactoring.md | ~6,500 |
| **REPHRASE** | request-rephrase-orchestrator.md | ~2,000 |
| **SETUP** | cortex-environment-setup.md | ~2,000 |
| **META-AUDIT** | cortex-meta-auditor.md + cortex-auditor.md | ~6,500 |
| **UPGRADE** | cortex-environment-setup.md + cortex-auditor.md | ~5,500 |
| **WIRING/CI** | architecture-integrity-agent.md | ~5,000 |
| **VACUUM** | cortex-vacuum.md | ~2,000 |
| **DEBUG** | cortex-debugger.md + cortex-auditor.md | ~5,000 |
| **HEALTH** | cortex-auditor.md (Check #11) | ~3,500 |
| **SYNC** | cortex-sync.prompt.md + cortex-sync-agent.md | ~6,000 |
| **RCA** | cortex-architect.prompt.md + `cortex_learning` op=`rca` | ~3,500 |
| **GOLDEN_TEST** | cortex-executor.md + cortex-holistic-validator.md | ~5,500 |
| **WORKFLOW_COMPOSE** | cortex-architect.prompt.md (§ WORKFLOW COMPOSE MODE) | ~3,000 |

> **Default context:** `cortex-architect.prompt.md` only (~2,700 tokens). Load specialist agents on-demand per intent above.

### `/audit fix` Pipeline (Canonical Production-Readiness Command)

**Single command → 9 integrated stages — no duplication, all wired components:**

```
/audit fix
  Stage 1: Stage 0 Governance Pre-Flight      → STAGE-0-GOVERNANCE-AUDIT-SPEC.md
  Stage 2: 24-Point Production Scan           → cortex-auditor.md (Checks #1–#24)
  Stage 3: Wiring Contract Validation         → architecture-integrity-agent.md (L1→L3)
  Stage 4: Orchestrator Health (all 22)       → HealthOrchestrator.run_health_check()
  Stage 5: Vacuum Cleanup                     → VacuumOrchestrator + cortex_vacuum
  Stage 6: Prompt/Agent Meta-Audit            → cortex-meta-auditor.md (26 checks)
  Stage 7: Auto-Fix confidence >90%           → autonomous remediation
  Stage 8: Re-validate → zero-violation gate  → 0 P0, 0 P1 required
  Stage 9: Tests + AC_COMPLETE                → python3 scripts/run_tests.py preflight
```

**Activity Log:** Every stage emits AC markers → `.cortex-runtime/traces/orchestrator-traces.db`

---

## Governance Architecture (Hybrid)

### Tier 1: YAML Structural Rules (Read-Only)

**Location:** `cortex-registry/core/` — 23 governance YAMLs + `cortex-registry/governance/` — 13 governance YAMLs (36 total)

| Category | Change Frequency |
|----------|-----------------|
| CORE rules | Rarely |
| Progress bar format | Never |
| Status icons | Never |
| File naming rules | Never |
| Risk thresholds | Quarterly |

### Tier 2: Agent Behavioral Rules

**Location:** `.github/agents/core/` — agent specification files

| Category | Owner Agent |
|----------|------------|
| Challenge gate logic | cortex-holistic-validator.md |
| Mode detection | cortex-architect.md |
| Response formats | cortex-response-templates.md |
| Validation sequences | cortex-holistic-validator.md |

---

## Validation Flow (IMPLEMENT/FIX/REFACTOR)

**Workflow Primitive:** `cortex-registry/workflows/templates/primitives/governance/holistic-validation-gate.yaml`

```
User Request
    ↓
Load: cortex-holistic-validator.md
    ↓
Execute holistic-validation-gate.yaml primitive (5 steps)
    ↓
IF PASS → Load executor → Proceed via mode workflow template
IF BLOCK → Show remediation, require override
```

---

## STS Documentation Intent

| User Intent | Load These Agents | Token Cost |
|-------------|-------------------|-----------|
| **DOCUMENT (STS)** | doc-sync-agent.md | ~4,500 |
| **DOCUMENT (CORTEX)** | cortex-doc.prompt.md → 9 docs agents (git-discovery, drift-detection, doc-sync, diagram-regeneration, media-prompt, narrative-continuity, comedy-enhancement[internal], coverage-audit, release-notes) | ~8,500 |

**STS Trigger Phrases:** "document STS", "review STS", "STS sample app docs", "account-modernized README", "payment-processor README", "fix mmd diagrams", "STS architecture diagram"

**STS Documentation Authority:** `cortex-doc.prompt.md` + `doc-sync-agent.md` (Section: Documentation Sync)

**STS `.mmd` Quality Gate (run before marking complete):**
- `participant` keyword only in sequenceDiagram (never `user`)
- Start nodes use actual HTTP endpoints (not "API Invoked" / "Execute")
- No truncated labels (`_less`, `Conta`, `Emptyc`, etc.)
- Error nodes include HTTP status codes
- D3.js interactive diagram present at workspace root

---

## ⛔ Deleted Constructs (Never Reference)

- `cortex/brain/` — dissolved into `cortex/orchestrators/`
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `cortex_brain/` — dissolved; governance rules are at `cortex-registry/core/`
- `_archive/` — permanently deleted
- Phase 49 CCL / CrystallizedContext — removed
- `cortex_process_request` — replaced by specific MCP tools
- `cortex_lens_analyze` — replaced by `cortex_onboard` (op: `full`)
- `cortex/orchestrators/internal/` — not a canonical wired tier

---

## 🔄 Self-Healing Prompt Suite

**Refresh playbook:** `python3 scripts/refresh_prompt_suite.py`

| Command | Purpose |
|---|---|
| `--counts-only` | Show live architecture counts (no file changes) |
| `--db-cleanup` | SQLite 30-day retention + VACUUM (7 databases) |
| `--dry-run` | Preview all changes without writing |
| (no args) | Full refresh: cleanup → validate → report |

**When to run:** After phase completion, after `/audit fix`, after major refactoring, monthly.

**SQLite databases (7):**
- `orchestrator-traces.db` — primary trace store (AC markers, workflow runs)
- `rca_store.db` — root cause analysis
- `intelligence_audit.db` — intelligence traces
- `contract_validation_audit.db` — wiring contracts
- `audit.db` — audit events
- `governance.db` — scaffolder audit
- `conversations.db` — session state (90-day retention)

---

