# CORTEX Agent Index

**Updated:** 2026-02-20 | **Purpose:** Lazy loading + intent-based agent selection  
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
| Orchestrators | 52 canonical across 10 domains |
| MCP Tools | 23 production tools |
| CORE Rules | 17 active governance rules |
| Package | `cortex` (single) |
| Tests | 15,230 (486 golden, 177 phase) |
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

## Intent → Agent Mapping

| User Intent | Load These Agents |
|-------------|-------------------|
| **IMPLEMENT** | cortex.md + cortex-holistic-validator.md + cortex-executor.md |
| **FIX** | cortex.md + cortex-holistic-validator.md + cortex-executor.md |
| **REFACTOR** | cortex.md + cortex-holistic-validator.md |
| **AUDIT** | cortex.md + cortex-architect.md + cortex-auditor.md |
| **INVESTIGATE** | cortex.md + cortex-architect.md |
| **QUERY** | cortex.md + cortex-interactive.md |
| **DESIGN** | cortex.md + cortex-architect.md |
| **PLAN** | cortex-architect.md + cortex-phase-resolver.md |
| **DIGEST** | cortex-architect.md + cortex-digest.md |
| **REPHRASE** | request-rephrase-orchestrator.md |
| **SETUP** | cortex-environment-setup.md |

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

## ⛔ Deleted Constructs (Never Reference)

- `cortex/brain/` — dissolved into `cortex/orchestrators/`
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `_archive/` — permanently deleted
- Phase 49 CCL / CrystallizedContext — removed
- `cortex_process_request` — replaced by specific MCP tools
- `cortex_lens_analyze` — replaced by `cortex_onboard_repository_v3`

---

