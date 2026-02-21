# Key Concepts

---
title: CORTEX Key Concepts — Terminology for New Readers
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-20
source_of_truth: cortex/ + cortex-registry/ + .github/copilot-instructions.md
format: 10k-view
order: 2
---

> **Purpose:** If you are reading CORTEX documentation for the first time, this page defines the most important concepts in plain language. Every term links to where it lives in the actual codebase.

---

## Architecture Concepts

### MCP · Model Context Protocol
The communication standard connecting your IDE to CORTEX. Think of it as the **language your IDE speaks** to talk to the CORTEX brain. Technically it's JSON-RPC 2.0 passed over stdio (development) or HTTP (production). You don't need to know the protocol details — the IDE handles it automatically.

**Live location:** `cortex/mcp/` — Pylance-style stdio server, auto-starts with VS Code.

### MCP Gateway
The front door of CORTEX. Every request arrives here first. The gateway validates the message, classifies the tool tier, and dispatches to the right MCP tool. CORTEX exposes **23 canonical MCP tools**.

**Daily example:** When you type a request in VS Code Copilot Chat, it enters through the MCP Gateway, which routes it to `cortex_process_request` or another appropriate tool.

### Orchestrator
A specialized processing engine for one category of work. CORTEX has **52 orchestrator classes** across **10 domains**:

| Domain | Key Orchestrators | Files |
|--------|------------------|-------|
| **core** | MasterOrchestrator, IntentRouter, TDDOrchestrator, EnforcementOrchestrator, PlanningOrchestrator, RefactoringOrchestrator | 52 |
| **domain** | BusinessDomainOrchestrator, EcommerceOrchestrator, FinancialOrchestrator, HealthcareOrchestrator | 30 |
| **health** | HealthOrchestrator, VacuumOrchestrator | 30 |
| **intelligence** | IntelligenceOrchestrator, UnifiedAnalysisOrchestrator | 14 |
| **support** | OnboardingOrchestrator, SetupOrchestrator, UnifiedDiscoveryOrchestrator | 38 |
| **validation** | HolisticValidationOrchestrator, ReviewOrchestrator | 11 |
| **workflow** | WorkflowOrchestrator, PhaseCompletionOrchestrator | 13 |
| **git** | GitOrchestrator, GitPublishOrchestrator | 4 |
| **strategies** | Strategy selection | 1 |
| **synthesis** | Cross-domain synthesis | 1 |

**Brain analogy:** Each orchestrator is like a specialized brain region — the visual cortex processes images, the motor cortex controls movement, and Broca's area handles language. They're distinct but interconnected through the MasterOrchestrator (the thalamus).

**Live location:** `cortex/orchestrators/{domain}/`

### Git-Backed Registry (`cortex-registry/`)
Instead of a database, CORTEX stores all configuration, governance rules, workflow templates, and knowledge in plain YAML files committed to Git. This means:
- All changes are versioned and auditable
- No database dependency
- Configuration is readable by humans and machines
- Rollback is `git revert`

**Live location:** `cortex-registry/` (core rules, patterns, planning, workflows, company catalog)

### Single Canonical Package
After the 12-phase Cohesive Brain Refactor, CORTEX uses exactly **one Python package**: `cortex`. There is no `cortex_intelligence`, no `cortex_lens`, no `cortex.brain`. Every import is `cortex.*`.

**Daily example:** `from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator`

---

## Intelligence Concepts

### LENS
**L**anguage → **E**xamination → **N**avigation → **S**ynthesis. This is CORTEX's code intelligence engine. It runs **8 specialized analyzers** in parallel against your codebase and produces a unified context — a comprehensive code health report reduced to a structured object.

**Brain analogy:** LENS is the **sensory cortex** — processing raw input (source code) into structured perception (code patterns, metrics, security findings). Just as your visual cortex processes light into objects, LENS processes code into intelligence.

**Live location:** `cortex/lens/` (analyzers, adapters, models, schemas, cache)

### Brain Tiers (Perception → Reasoning → Action)
The three-layer cognitive core of CORTEX, now housed in `cortex/intelligence/`:

| Tier | Purpose | Module |
|------|---------|--------|
| **Perception** | Recognizes patterns in LENS data | `cortex/intelligence/perception/` |
| **Reasoning** | Selects strategies based on patterns | `cortex/intelligence/reasoning/` |
| **Action** | Builds step-by-step execution plans | `cortex/intelligence/action/` |

**Brain analogy:** Perception is the sensory cortex (what is happening?), Reasoning is the prefrontal cortex (what should we do?), Action is the motor cortex (how do we execute?).

### Confidence Score
A value between 0.0 and 1.0 that CORTEX assigns to decisions:
- **≥ 0.7** — auto-execute
- **0.5–0.7** — may ask for clarification
- **< 0.5** — will ask before proceeding

Used in pattern matching, intent classification, and strategy selection.

---

## Governance Concepts

### CORE Rule
A numbered governance standard enforced automatically. There are **17 actively enforced CORE rules** (35 defined total in `cortex-registry/core/governance/skull-rules.yaml`). Critical examples:

| Rule | Name | What It Does |
|------|------|-------------|
| CORE-002 | Markdown Suppression | Never create `.md`/`.txt` report files — all results inline |
| CORE-008 | TDD Mandatory | Write failing test first, then implement. No exceptions |
| CORE-011 | Type Hints | All functions must have type annotations |
| CORE-012 | Docstrings | All public APIs must have docstrings |
| CORE-028 | File Naming | snake_case only |
| CORE-035 | Single Canonical | No duplicate implementations |
| CORE-048 | Holistic Validation | Validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Silent Execution | Progress bars only, no verbose chatter |

### Enforcement Agents
Seven specialized agents within EnforcementOrchestrator that check different categories of CORE rules before any code-mutating operation. A gate result is PASS, WARNING, or BLOCKED.

**Daily example:** You ask CORTEX to implement a feature. Before any code is written, 7 agents check TDD enforcement, type hints, file naming, architecture integrity, and more. If any check fails as BLOCKED, the operation stops immediately — no files changed.

### TestQualityGate
A scoring system that rates every test 0–9 based on Impact, Likelihood, Detection, Efficiency, and Maintenance cost. Tests scoring ≥7 are KEEP, 4–6 are REVIEW, <4 are DELETE.

**Live location:** `cortex/testing/quality_gate.py` + `cortex-registry/core/test-quality-gate.yaml`

---

## Testing Concepts

### Parallel Test Framework
CORTEX uses pytest-xdist for parallel test execution with four execution profiles:

| Profile | Workers | Distribution | Batch Size |
|---------|---------|-------------|------------|
| **smoke** | auto | loadfile | 500 |
| **unit** | auto | loadscope | 500 |
| **integration** | 4 | loadfile | 200 |
| **golden** | 0 (serial) | deterministic | 100 |

**Live location:** `cortex/testing/framework/` (parallel_runner.py, progress_reporter.py, test_categorizer.py)

### Golden Tests
486 high-value tests that must always pass. They validate core contracts, governance rules, and critical workflows. Run serially for deterministic results.

### TDD Workflow
Every IMPLEMENT and FIX operation follows RED → GREEN → REFACTOR:
1. **RED** — Write a failing test that specifies the behaviour
2. **GREEN** — Write minimum code to make the test pass
3. **REFACTOR** — Improve the code while keeping all tests green

This is enforced by CORE-008 and the TDDOrchestrator. It's not a suggestion — it's architecturally mandated.

---

## Infrastructure Concepts

### CortexAuditDB
Unified SQLite database with WAL mode for audit trails. All orchestrators route through this instead of creating ad-hoc `.db` files.

**Live location:** `cortex/infrastructure/audit_db.py` → `.cortex-runtime/`

### Workflow Templates
YAML-defined workflow specifications stored in `cortex-registry/workflows/templates/`. Two categories:
- **lifecycle/** — CORTEX-internal workflows (phase execution, master plan)
- **production/** — External production workflows

### Enterprise Patterns
9 architecture patterns registered in `cortex-registry/patterns/`: mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command.

---

*See `glossary.md` for the complete alphabetical reference.*
