# Key Concepts

---
title: CORTEX Key Concepts — Terminology Reference for New Readers
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-18
format: 10k-view
order: 2
---

> **Purpose:** If you are reading CORTEX documentation for the first time, some terms may be unfamiliar. This page defines the most important concepts in plain language, grouped by area, so you can read any other document in the `content/src` tree without getting stuck on terminology.

---

## Architecture Concepts

### MCP · Model Context Protocol
The communication standard that connects your IDE (VS Code, Cursor, Claude Desktop) to CORTEX. Think of it as the "language" your IDE uses to talk to CORTEX. Technically it is JSON-RPC 2.0 — a structured message format passed over standard input/output in development, or over HTTP in production. You don't need to know the protocol details to use CORTEX; the IDE client handles it automatically.

### MCP Gateway
The front door of CORTEX. Every request from your IDE arrives here first. The gateway validates that the message is well-formed, authenticates it, enforces rate limits, and decides which tool should handle it. It exposes 26 production MCP tools that cover the full range of CORTEX capabilities.

### Orchestrator
A specialised processing engine responsible for one category of work. CORTEX has 20+ orchestrators including:
- **TDD Orchestrator** — manages the RED → GREEN → REFACTOR workflow
- **LENS Synthesis Orchestrator** — coordinates code analysis
- **Refactoring Orchestrator** — handles semantic code improvement
- **Planning Orchestrator** — creates development roadmaps
- **MasterOrchestrator** — the executive coordinator that dispatches to all others

An orchestrator is not a generic LLM prompt. Each one has a defined responsibility, priority level, and set of capabilities registered in the wiring contract.

### Wiring Contract (`__wiring_contract__.yaml`)
The Git-backed registry file that tells CORTEX which orchestrators exist, their priorities, and their capabilities. When CORTEX starts, it reads this file to discover all available orchestrators — no hard-coded lists. Adding a new orchestrator means adding an entry here; removal is equally simple. Hot-reload means changes take effect without restarting the server.

### Git-Backed Registry (`cortex-registry/`)
Instead of a database, CORTEX stores all configuration, governance rules, feature definitions, and knowledge in plain YAML files committed to Git. This means:
- All changes are versioned and auditable
- No PostgreSQL or MongoDB dependency
- Configuration is readable by both humans and machines
- Rollback is `git revert`

---

## Intelligence Concepts

### LENS
Stands for **L**anguage → **E**xamination → **N**avigation → **S**ynthesis. This is CORTEX's code intelligence engine. It runs 8 specialised analyzers in parallel against your codebase and produces a `LENSContext` — a unified data structure capturing code structure, security issues, complexity metrics, git patterns, and framework-specific insights. LENS is the "sensory system" that feeds the Brain.

### LENSContext
The data object produced by LENS after analysing a file or repository. It contains the combined output of all 8 analyzers and is what the Brain's Perception tier reads to identify patterns. Think of it as a comprehensive code health report reduced to a structured object.

### Brain Tier
The three-layer cognitive core of CORTEX (Perception → Reasoning → Action). See `00-getting-started/brain-tier-architecture.md` for the full explanation. In brief:
- **Perception** recognises patterns in LENS data
- **Reasoning** selects strategies based on those patterns
- **Action** builds a step-by-step execution plan with TDD gates and rollback

### Pattern Registry
A catalogue of known repository signatures (frameworks, architectural styles, testing patterns). When CORTEX analyses a new codebase, Perception matches it against this registry. Each registered pattern carries a `success_rate` — how reliably its associated strategies have worked historically.

### Strategy
A named approach to solving a class of problems. Examples: `tdd-incremental`, `refactor-extract-service`, `security-audit-first`. Strategies are ranked by Reasoning and converted into `ExecutionPlan` steps by Action.

### Confidence Score
A value between 0.0 and 1.0 that CORTEX assigns to decisions. Used in:
- Pattern matching (how well does this repo match this pattern?)
- Intent classification (how sure is CORTEX about what you asked for?)
- Strategy selection (how reliable is this strategy in this context?)

Requests with confidence ≥0.7 auto-execute. Between 0.5–0.7, CORTEX may ask for clarification. Below 0.5, it will ask before proceeding.

### Intelligence Layer
A learning subsystem built on top of LENS and the Brain. It analyses the last 48 hours of git history to detect recurring patterns and update success rates. This is what makes CORTEX improve over time — not just within a single session, but across sessions and across repositories.

---

## Governance Concepts

### CORE Rule
A numbered governance standard that CORTEX enforces automatically. There are 59 CORE rules covering coding practices, architecture, security, naming, and operational behaviour. Key examples:
- **CORE-002** — Never create `.md` or `.txt` report files; all results must be delivered inline
- **CORE-008** — Test-first (TDD) is mandatory; no implementation before a failing test exists
- **CORE-028** — File naming conventions must be followed
- **CORE-049** — MCP-first architecture; direct file operations are blocked for IMPLEMENT/FIX/REFACTOR

### Governance Gate
A blocking checkpoint that runs before any code-mutating operation. The gate is implemented by 7 enforcement agents that check different categories of CORE rules. A gate result is PASS, WARNING, or BLOCKED. BLOCKED means the operation stops immediately; no files are changed.

### Four-Layer Defence
CORTEX's governance operates at four levels:
1. **Pre-Execution** — checks before any action
2. **Runtime Monitor** — watches during execution, can halt and rollback
3. **Post-Execution Audit** — records everything that happened
4. **Production Gate** — final validation before deployment

### Audit Trail
An immutable log of every action CORTEX takes, stored in the Git-backed registry. Each entry is bracketed by `AC_START` and `AC_COMPLETE` markers. The trail records orchestrator decisions, rule checks, and outcomes — making it possible to reconstruct exactly what happened for any request.

### Holistic Validation Gate (CORE-048)
A specific governance check triggered by Reasoning before high-risk changes are planned. It scores regression risk (0.0–1.0), checks dependency graphs, detects architecture drift, and — if risk is above threshold — produces the **Mandatory Challenge**.

### Mandatory Challenge
When Reasoning detects that your requested approach carries significant risk, it presents alternatives before proceeding. The format shows your approach (pros/cons/ROI), one or more alternatives, and asks you to type "proceed" or "use A". This is not a rejection — it is CORTEX sharing its analysis so you can make an informed decision.

---

## Development Workflow Concepts

### TDD (Test-Driven Development)
The only permitted implementation workflow in CORTEX (CORE-008). The cycle is:
1. **RED** — write a failing test that defines the expected behaviour
2. **GREEN** — write the minimum code to make the test pass
3. **REFACTOR** — improve the code structure while keeping tests green

CORTEX enforces this structurally — the Action tier cannot produce an `ExecutionPlan` that places implementation before tests.

### Intent
What you are asking CORTEX to do. CORTEX recognises 12 intents: IMPLEMENT, FIX, REFACTOR, ANALYZE, TEST, PLAN, AUDIT, DESIGN, DEBUG, DIGEST, QUERY, RECALL. Intent is classified automatically from your natural language request using LENS intelligence.

### Session
A single interaction session between your IDE and CORTEX. State is maintained within a session (checkpoints, in-progress operations). Long operations (>30s) are checkpointed to SQLite so they survive interruption.

### Feature
A numbered unit of CORTEX's own development direction, stored in `cortex-registry/planning/`. When CORTEX documentation mentions "Iteration 48" or "Iteration 96", it refers to a specific completed increment of the platform itself. Phases are how CORTEX tracks its own evolution.

---

## Toolkit & Extension Concepts

### MCP Tool
A named, callable capability exposed through the MCP Gateway. Each tool has a defined JSON Schema for its inputs and outputs. Examples: `cortex_process_request` (main entry point), `cortex_lens` (trigger a LENS scan), `cortex_validate_compliance` (check CORE rules). There are 26 production tools covering ~90 operations.

### Domain Orchestrator
An orchestrator specialised for a specific business or technology domain (e.g., .NET, Angular, a specific team's conventions). Domain orchestrators extend the platform without modifying core code — they are registered in the wiring contract and can be hot-loaded.

### Knowledge Base
A collection of 45+ YAML files in `cortex-registry/knowledge-base/` containing best practices, patterns, and guidance. CORTEX's Reasoning tier consults these files when selecting strategies. The knowledge base uses a tier-precedence system: company-level rules override tier1, which override tier0 defaults.

### Context Crystallization Layer (CCL)
An async prefetch system (introduced in Iteration 49) that loads LENS state, governance rules, and infrastructure detection data in parallel with intent classification. This reduces perceived latency for complex operations by 40–60% because context is ready before it's needed.

---

## Performance Reference

| Operation | Typical Latency |
|-----------|----------------|
| Request pre-processing (Stage -1) | 15–35ms |
| MCP Gateway validation | 5–15ms |
| Intent classification | 20–40ms |
| LENS full analysis (50–100K LOC) | 300–800ms |
| LENS cache hit | 50–150ms |
| Brain (Perception + Reasoning + Action) | 50–200ms |
| Governance gate (7 agents) | <150ms |
| End-to-end for a simple query | ~300ms |
| End-to-end for a full IMPLEMENT | 2–8s (including test execution) |

---

## Reading Path

These documents build on each other. The recommended order for a new reader:

| Step | Document | What You Gain |
|------|----------|---------------|
| 1 | `00-getting-started/one-pager.md` | Platform overview in 2 minutes |
| 2 | `00-getting-started/key-concepts.md` | *(this document)* Terminology foundation |
| 3 | `00-getting-started/how-cortex-works.md` | End-to-end request lifecycle |
| 4 | `00-getting-started/brain-tier-architecture.md` | Deep dive into the cognitive core |
| 5 | `02-lens/01-overview.md` | How CORTEX reads your code |
| 6 | `03-orchestration/01-overview.md` | The orchestrator network |
| 7 | `01-capabilities/governance-compliance.md` | Governance and enforcement |
| 8 | `04-mcp/tools-catalog.md` | All 26 tools and their operations |
| 9 | `01-capabilities/extensibility.md` | Building custom extensions |

---

*CORTEX  · February 2026*
