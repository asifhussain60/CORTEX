# CORTEX Universal Orchestration Agent

**Updated:** 2026-02-20 | **Status:** ✅ ACTIVE

---

## 🎯 Purpose

**Single source of truth** for how CORTEX orchestrators work together across ALL modes.

**Architecture (Post-Refactor):**
- 51 wired orchestrators in `cortex/orchestrators/` (4 tiers: core, domain, support, git)
- 39 MCP tools (29 registered) in `cortex/mcp/tools/`
- 1 package: `cortex` (no `cortex_intelligence`, `cortex_lens`, `cortex.brain`)

---

## 📐 4-Stage Orchestration Pipeline

```
USER REQUEST → STAGE 1: Interaction → STAGE 2: Intent → STAGE 3: Intelligence → STAGE 4: Execution
```

---

## 🔄 STAGE 1: Interaction Layer

**Orchestrator:** `InteractionOrchestrator`  
**Location:** `cortex/orchestrators/core/interaction_orchestrator.py`

- Comprehends user request into structured intent
- Generates challenges via ChallengeEngine (disagreement detection)
- Displays DoR (Definition of Ready) for user approval
- Skipped in silent autonomous mode after initial approval

---

## 🧭 STAGE 2: Intent Router

**Orchestrator:** `IntentRouter`  
**Location:** `cortex/orchestrators/core/intent_router.py`

| Keywords | Intent | Target Orchestrator |
|----------|--------|---------------------|
| implement, add, create, build | IMPLEMENT | TDDOrchestrator |
| fix, bug, error, broken | FIX | TDDOrchestrator |
| refactor, improve, optimize | REFACTOR | RefactoringOrchestrator |
| investigate, analyze, root cause | INVESTIGATE | InvestigationOrchestrator |
| audit, scan, check | AUDIT | AuditCoordinator |
| plan, phase, roadmap | PLAN | PlanningCoordinator |
| design, architect, structure | DESIGN | DesignCoordinator |
| explain, how, what, why | QUERY | QueryCoordinator |
| summarize, digest, ingest | DIGEST | DigestCoordinator |
| rephrase | REPHRASE | RequestRephraseOrchestrator |

**LENS Auto-Fetch:** Triggered for IMPLEMENT, FIX, REFACTOR, INVESTIGATE, AUDIT (code analysis needed). DIGEST conditional (Pipeline 2 repo content only). NOT triggered for PLAN, DESIGN, QUERY, REPHRASE.

---

## 🧠 STAGE 3: Intelligence Layer

**Provider:** `UnifiedIntelligenceProvider`  
**Location:** `cortex/intelligence/provider.py`

| Tier | Latency | Scope | When Used |
|------|---------|-------|-----------|
| Quick | <200ms | Cached rules only | Interaction (Stage 1) |
| Targeted | <2s | LENS + relevant YAMLs | IMPLEMENT/FIX/REFACTOR |
| Full | <10s | LENS + KG + Profiles | INVESTIGATE (deep analysis) |

**LENS Analysis (4 phases):**
1. **Language** — frameworks, languages, patterns
2. **Examination** — complexity, coverage, quality
3. **Navigation** — entry points, dependencies, call graph
4. **Synthesis** — recommendations, risks

---

## ⚙️ STAGE 4: Execution Layer

**Coordinator:** `MasterOrchestrator`  
**Location:** `cortex/orchestrators/core/master_orchestrator.py`

### Domain Orchestrators (3 tiers)

| Domain | Location | Key Orchestrators |
|--------|----------|-------------------|
| core | `cortex/orchestrators/core/` | MasterOrchestrator, TDDOrchestrator, IntentRouter, EnforcementOrchestrator |
| domain | `cortex/orchestrators/domain/` | PlanningOrchestrator, RefactoringOrchestrator, DashboardOrchestrator |
| git | `cortex/orchestrators/git/` | GitOrchestrator, EnforcementOrchestrator |
| health | `cortex/orchestrators/health/` | HealthCheckOrchestrator |
| intelligence | `cortex/orchestrators/intelligence/` | LENSOrchestrator, KnowledgeSynthesis |
| strategies | `cortex/orchestrators/strategies/` | Execution strategies |
| support | `cortex/orchestrators/support/` | Support orchestrators |
| synthesis | `cortex/orchestrators/synthesis/` | Synthesis orchestrators |
| validation | `cortex/orchestrators/validation/` | ValidationOrchestrator |
| workflow | `cortex/orchestrators/workflow/` | WorkflowExecutor |

### TDD Workflow (IMPLEMENT/FIX)

1. **RED** — Write failing tests (CORE-008)
2. **GREEN** — Implement minimum code to pass
3. **REFACTOR** — Clean up, all tests still passing
4. **Validate** — EnforcementOrchestrator + CoherenceValidator
5. **Commit** — Conventional commit message

### Governance Integration

**EnforcementOrchestrator** validates before every execution:
- CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
- CORE-025 (git discipline), CORE-028 (snake_case)
- CORE-035 (single canonical implementation)
- Security scanning, dependency validation

---

## 🔧 MCP Tool Mapping (28 Registered, 39 Target)

| Tool | Purpose |
|------|---------|
| `cortex_verify` (op: `mcp`) | MCP health check |
| `cortex_validate` (op: `compliance`) | CORE rules scanning |
| `cortex_onboard` (op: `full`) | Repository onboarding + LENS |
| `cortex_refactor` | Semantic refactoring |
| `cortex_governance` (op: `remediation_plan`) | Auto-planning from audit |
| `cortex_tools_catalog` | Discover all tools |
| `cortex_load` (op: `rules`) | Load governance rules |
| `cortex_metrics` (op: `capture`) | Record TDD/debug metrics |
| `cortex_vision_analyze` | Image analysis |
| `cortex_governance` (op: `query`) | Query governance state |

**Full catalog:** Call `cortex_tools_catalog` via MCP.

---

## 🛡️ Governance Rules (38 CORE Active)

| Rule | Stage | Enforcement |
|------|-------|-------------|
| CORE-002 (inline output) | ALL | MasterOrchestrator |
| CORE-008 (TDD) | Stage 4 | EnforcementOrchestrator |
| CORE-011 (type hints) | Stage 4 | EnforcementOrchestrator |
| CORE-012 (docstrings) | Stage 4 | EnforcementOrchestrator |
| CORE-028 (snake_case) | Stage 4 | EnforcementOrchestrator |
| CORE-035 (single source) | Stage 3/4 | LENSOrchestrator |
| CORE-048 (holistic gate) | Stage 1 | HolisticValidator |
| CORE-049 (silent exec) | ALL | MasterOrchestrator |
| CORE-050 (MCP gate) | Stage 0 | Pre-flight |

---

## 📋 Quick Reference

| User Says | Intent | Orchestrator |
|-----------|--------|-------------|
| "implement auth" | IMPLEMENT | TDDOrchestrator |
| "fix this bug" | FIX | TDDOrchestrator |
| "refactor service" | REFACTOR | RefactoringOrchestrator |
| "investigate failure" | INVESTIGATE | InvestigationOrchestrator |
| "audit repo" | AUDIT | AuditCoordinator |
| "plan new feature" | PLAN | PlanningCoordinator |
| "design architecture" | DESIGN | DesignCoordinator |

---

## 🔗 References

| Document | Purpose |
|----------|---------|
| `.github/prompts/cortex-architect.prompt.md` | Architect prompt (expanded modes) |
| `.github/prompts/cortex.prompt.md` | Master orchestrator prompt |
| `cortex/orchestrators/core/master_orchestrator.py` | MasterOrchestrator implementation |
| `cortex/orchestrators/core/intent_router.py` | IntentRouter implementation |
| `cortex/intelligence/provider.py` | UnifiedIntelligenceProvider |

---

**Authority:** CORE-035 (Single Source of Truth) | **Maintainer:** Asif Hussain
