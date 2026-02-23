# CORTEX Agent Index

**Updated:** 2026-02-21 | **Purpose:** Lazy loading + intent-based agent selection  
**Package:** `cortex` (single canonical — no `cortex_intelligence`, `cortex_lens`, `cortex.brain`)

---

## Loading Protocol

**CRITICAL:** This file replaces bulk agent loading. Load specific agents ONLY when needed per intent.

```yaml
Default Context: THIS FILE ONLY (~200 tokens)
Per Intent Load: 1-2 relevant agents (~1,000-2,500 tokens)
```

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
| Orchestrators | 22 wired across 10 domains (6 core, 6 domain, 10 support) |
| MCP Tools | 24 production tools |
| CORE Rules | 35 active CORE governance rules (+ 2 AC rules, incl. CORE-064 Sweep Completeness) |
| Package | `cortex` (single) |
| Tests | 15,230 (539 golden, 177 phase) |
| Entry Point | MasterOrchestrator → IntentRouter → Domain Orchestrator |

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
| **cortex-sts-refactoring.md** | STS pipeline: 7-gate refactoring for external codebases | `cortex-sts/` REFACTOR sessions, BadMonolith-style analysis |
| **cortex-digest.md** | Learning extraction from chat history | Processing chat files |
| **cortex-environment-setup.md** | Environment validation | Pre-flight checks, setup issues |
| **cortex-phase-resolver.md** | Plan phase management | `/plan` mode |
| **cortex-storyteller.md** | Documentation generation | Creating narratives |
| **cortex-documentation-architect.md** | Doc architecture + site builder | Documentation structure |
| **cortex-gitpages-builder.md** | GitHub Pages deployment | Site publishing |
| **request-rephrase-orchestrator.md** | Request token optimization | `/rephrase` command |
| **architecture-integrity-agent.md** | Wiring alignment enforcement | Pre-commit, CI/CD |

### Support Files

| File | Purpose |
|------|---------|
| **phase-creation-standards.md** | Standards for new phases |
| **cleanup-audit-guide.md** | Cleanup procedure reference |
| **STAGE-0-GOVERNANCE-AUDIT-SPEC.md** | Governance audit specification |

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
| **INVESTIGATE** | cortex.md + cortex-architect.md | ~6,000 |
| **QUERY** | cortex.md + cortex-interactive.md | ~4,500 |
| **DESIGN** | cortex.md + cortex-architect.md | ~6,000 |
| **PLAN** | cortex-architect.md + cortex-phase-resolver.md | ~6,000 |
| **DIGEST** | cortex-architect.md + cortex-digest.md | ~6,000 |
| **REPHRASE** | request-rephrase-orchestrator.md | ~2,000 |
| **SETUP** | cortex-environment-setup.md | ~2,000 |
| **META-AUDIT** | cortex-meta-auditor.md + cortex-auditor.md | ~6,500 |
| **WIRING/CI** | architecture-integrity-agent.md | ~5,000 |
| **VACUUM** | cortex-vacuum.md | ~2,000 |
| **DEBUG** | cortex-debugger.md + cortex-auditor.md | ~4,500 |
| **HEALTH** | cortex-auditor.md (Check #11) | ~3,500 |

> **Default context:** `cortex-architect.prompt.md` only (~2,700 tokens). Load specialist agents on-demand per intent above.

### `/audit fix` Pipeline (Canonical Production-Readiness Command)

**Single command → 9 integrated stages — no duplication, all wired components:**

```
/audit fix
  Stage 1: Stage 0 Governance Pre-Flight      → STAGE-0-GOVERNANCE-AUDIT-SPEC.md
  Stage 2: 14-Point Production Scan           → cortex-auditor.md (Checks #1–#14)
  Stage 3: Wiring Contract Validation         → architecture-integrity-agent.md (L1→L3)
  Stage 4: Orchestrator Health (all 22)       → HealthOrchestrator.run_health_check()
  Stage 5: Vacuum Cleanup                     → VacuumOrchestrator + cortex_vacuum
  Stage 6: Prompt/Agent Meta-Audit            → cortex-meta-auditor.md (12 checks)
  Stage 7: Auto-Fix confidence >90%           → autonomous remediation
  Stage 8: Re-validate → zero-violation gate  → 0 P0, 0 P1 required
  Stage 9: Tests + AC_COMPLETE                → python3 scripts/run_tests.py batch
```

**Activity Log:** Every stage emits AC markers → `.cortex-runtime/traces/orchestrator-traces.db`

---

## Governance Architecture (Hybrid)

### Tier 1: YAML Structural Rules (Read-Only)

**Location:** `cortex-registry/core/` — governance rules YAML

| Category | Change Frequency |
|----------|-----------------|
| CORE rules (17) | Rarely |
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

```
User Request
    ↓
Load: cortex-holistic-validator.md
    ↓
Validation Sequence:
  1. Registry check
  2. Dependency analysis
  3. Regression risk scoring
  4. Architecture drift detection
  5. Challenge gate (if risk > 0.4)
    ↓
IF PASS → Load executor → Proceed
IF BLOCK → Show remediation, require override
```

---

## STS Documentation Intent

| User Intent | Load These Agents | Token Cost |
|-------------|-------------------|-----------|
| **DOCUMENT (STS)** | cortex-documentation-architect.md | ~4,500 |
| **DOCUMENT (CORTEX)** | cortex-documentation-architect.md + cortex-gitpages-builder.md | ~8,000 |

**STS Trigger Phrases:** "document STS", "review STS", "STS sample app docs", "account-modernized README", "payment-processor README", "fix mmd diagrams", "STS architecture diagram"

**STS Documentation Authority:** `cortex-doc.prompt.md` (Section: 🏗️ STS Sample Application Documentation) + `cortex-documentation-architect.md` (Section: 🏗️ STS Sample App Documentation Scope)

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

