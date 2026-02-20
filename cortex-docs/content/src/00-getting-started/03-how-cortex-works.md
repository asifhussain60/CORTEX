# How CORTEX Works

---
title: How CORTEX Works — End-to-End Request Lifecycle
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-18
source_of_truth: cortex/__wiring_contract__.yaml + cortex/orchestrators/ + cortex/04-mcp/
format: 10k-view
order: 3
---

> **Goal of this document:** Give you a clear mental model of what happens — step by step — from the moment you type a request to the moment CORTEX delivers a result. No prior knowledge of the internals is assumed.

---

## The Shortest Possible Summary

You type a request in your IDE. CORTEX enriches it, classifies it, analyses your codebase, validates it against governance rules, builds an execution plan using its Brain, and delivers the result inline — all within seconds. Every step is observable and auditable.

---

## The Mental Model: A Smart Factory Floor

Imagine a modern factory with a central control room and specialised production lines. When an order arrives:

1. **Reception** checks the order is valid and enriches it with production context
2. **Control Room** classifies the order and assigns it to the right production line
3. **Quality Lab** scans the raw materials (your codebase) before work begins
4. **Production Line** does the actual work, with quality checks at each station
5. **Inspection** validates the output before it leaves the factory

CORTEX's pipeline maps directly onto this structure. The "factory" is your local machine; the "control room" is the MCP Gateway and orchestration layer; the "quality lab" is LENS; the "production line" is the TDD or Refactoring orchestrator; and "inspection" is the governance enforcement layer.

---

## Step-by-Step: What Happens When You Send a Request

### Stage −1 · Request Pre-Processor (15–35ms)

Before your request reaches any orchestrator, the **RequestRephraseOrchestrator** silently enriches it:

- Adds relevant governance context (which CORE rules apply)
- Attaches a breaking-risk assessment
- Surfaces any design pillar considerations
- Flags if a Challenge Gate should be shown (high-risk changes)

**You don't see this stage.** It happens automatically and ensures MasterOrchestrator always receives a self-documenting, fully-contextualised request.

---

### Stage 0 · MCP Gateway (5–15ms)

Your enriched request arrives at the **MCP Gateway** over JSON-RPC 2.0 (stdio in development, HTTP on port 8000 in production). The gateway:

- Validates the JSON-RPC 2.0 schema
- Authenticates the request (API key / JWT)
- Applies rate limiting (60 req/min default)
- Checks the **Native Tool Gate** (CORE-049) — blocks direct file operations for IMPLEMENT/FIX/REFACTOR intents, enforcing MCP-first architecture

The gateway exposes **26 production MCP tools** (90+ operations) across five tiers. Most requests enter through `cortex_process_request`.

---

### Stage 1 · Intent Classification (20–40ms)

**IntentRouter** uses LENS intelligence to determine what the request is asking for. It recognises 12 intent types:

| Intent | Description | Routed To |
|--------|-------------|-----------|
| IMPLEMENT | Build new functionality | TDD Orchestrator |
| FIX | Repair a defect | TDD Orchestrator |
| REFACTOR | Improve existing code | Refactoring Orchestrator |
| ANALYZE | Understand the codebase | LENS Synthesis Orchestrator |
| TEST | Generate or improve tests | TDD Orchestrator |
| PLAN | Create a development plan | Planning Orchestrator |
| AUDIT | Check compliance and quality | Audit Coordinator |
| DESIGN | Architect a solution | Design Orchestrator |
| DEBUG | Diagnose a problem | Debug Orchestrator |
| DIGEST | Summarise a topic | Digest Coordinator |
| QUERY | Look something up | Query Coordinator |
| RECALL | Retrieve past context | Memory / Registry |

If a request contains multiple intents (e.g., IMPLEMENT + TEST), composite intent detection handles both. Classification confidence must reach ≥0.7 for auto-execution; below 0.5, CORTEX asks for clarification.

---

### Stage 2 · Intelligence Gathering: LENS (300–800ms)

In parallel with intent classification, **LENS** (Language → Examination → Navigation → Synthesis) scans the relevant parts of your codebase using 8 specialised analyzers running concurrently:

| Analyzer | What It Detects |
|----------|-----------------|
| AST Analyzer | Syntax structure, code complexity, maintainability index |
| Git History Analyzer | Change frequency, churn hotspots, author patterns (24h window) |
| Security Analyzer | OWASP vulnerability patterns, hardcoded secrets, unsafe APIs |
| Pattern Analyzer | Design patterns (Singleton, Factory, Observer), anti-patterns |
| Metrics Analyzer | Cyclomatic complexity, Halstead metrics, test coverage |
| Import Analyzer | Dependencies, circular imports, unused packages |
| Comment Analyzer | TODOs, FIXMEs, documentation coverage |
| Domain Analyzer | Framework-specific patterns (Django, React, .NET, Angular) |

Results are aggregated into a **`LENSContext`** object that the Brain's Perception tier uses to match patterns. SQLite caching means unchanged files are served in 50–150ms on repeat analysis (60–70% typical cache hit rate).

---

### Stage 3 · Brain Processing (Perception → Reasoning → Action)

The **Brain tier** converts raw LENS intelligence into a concrete execution plan. This is the cognitive core of CORTEX:

**Perception** — Matches the `LENSContext` against the Pattern Registry. Finds known signatures (frameworks, architectural styles, testing patterns) and scores them by confidence.

**Reasoning** — Takes confident matches and selects the best strategy. Weighs historical success rates, current context, and risk factors. Triggers the **Holistic Validation Gate** (CORE-048) which scores regression risk and, for high-risk changes, generates the Mandatory Challenge (presenting alternatives before proceeding).

**Action** — Converts the chosen strategy into an ordered `ExecutionPlan` with TDD gates, validation checkpoints, and rollback steps at every stage.

See `00-getting-started/brain-tier-architecture.md` for the full explanation.

---

### Stage 4 · Governance Gate (Pre-execution, <150ms)

Before any file is modified, **EnforcementOrchestrator** runs 7 enforcement agents in parallel:

| Agent | Rules Enforced |
|-------|---------------|
| Governance Agent | TDD-first (CORE-008), documentation (CORE-027) |
| Security Agent | Secrets detection, unsafe patterns |
| Compliance Agent | Coverage thresholds, licence checks |
| File Agent | Naming conventions (CORE-028), placement rules |
| Architecture Agent | Structural integrity, layer separation |
| Incremental Agent | Step-size limits (CORE-001) |
| Markdown Agent | No report file sprawl (CORE-002) |

Result is one of: **PASS** (execution continues), **WARNING** (execution continues with flag), or **BLOCKED** (execution halts, violation reported inline).

---

### Stage 5 · Execution

The appropriate orchestrator executes the `ExecutionPlan`. For an IMPLEMENT request this means:

```
For each feature unit:
  1. Write failing test          ← RED   (committed, CI must fail)
  2. Write minimal implementation ← GREEN (tests must now pass)
  3. Refactor + verify           ← REFACTOR (no regressions)
  4. Governance check            ← Gate before next unit
```

For a REFACTOR request, the Refactoring Orchestrator uses semantic analysis (not text replacement) and validates that no observable behaviour changes.

---

### Stage 6 · Audit & Response

After execution:

- Every action is logged with AC_START → AC_COMPLETE markers
- The audit trail is written to the Git-backed registry (immutable)
- Results are delivered **inline** in your IDE — no `.md` or `.txt` report files are created (CORE-002)
- For IMPLEMENT completions, a session summary with test counts and coverage metrics is shown

---

## Visualising the Full Pipeline

```
Your IDE
   │
   │  JSON-RPC 2.0
   ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage -1  RequestRephraseOrchestrator                           │
│            + governance context + risk assessment (15–35ms)      │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 0   MCP Gateway                                           │
│            schema validation · auth · rate limit · tool gate     │
└──────────────────────────┬───────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌─────────────────────┐    ┌────────────────────────────────────┐
│  Stage 1            │    │  Stage 2                            │
│  IntentRouter       │    │  LENS (8 parallel analyzers)        │
│  12 intent types    │    │  AST · Git · Security · Patterns    │
│  (20–40ms)          │    │  Metrics · Import · Domain · Comment│
└──────────┬──────────┘    └─────────────────┬──────────────────┘
           └────────────────┬────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 3   Brain                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Perception  │→ │  Reasoning   │→ │  Action              │   │
│  │  Pattern     │  │  Strategy    │  │  Execution Plan      │   │
│  │  Registry    │  │  Selector    │  │  + TDD gates         │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 4   Governance Gate (7 agents · 59 CORE rules · <150ms)  │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 5   Orchestrator Execution                                │
│  TDD Orchestrator | Refactoring | Planning | Audit               │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Stage 6   Audit Trail + Inline Result Delivery                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Frequently Asked Questions

**Q: Do I need to configure anything to use CORTEX?**  
The MCP server auto-starts when you invoke any `cortex_*` tool from your IDE — similar to how Pylance starts automatically in VS Code. No manual `python -m cortex.mcp.server` is required.

**Q: What happens if CORTEX rejects my request?**  
The governance layer returns the specific CORE rule that was violated and explains why. The most common rejection is missing a failing test before implementation (CORE-008). You can often resolve it immediately by following the inline guidance.

**Q: Can CORTEX work on any codebase?**  
LENS supports Python, TypeScript/JavaScript, C#/.NET, Angular, React, and Vue out of the box. Additional language adapters can be added through the Extensibility layer.

**Q: Why does CORTEX sometimes ask me "are you sure?" before proceeding?**  
The Reasoning tier's Holistic Validation Gate detected a regression risk score above the threshold for your change. It is presenting alternatives — the "Mandatory Challenge". You can type "proceed" to continue with your original approach or "use A" to take the recommended alternative.

**Q: How does CORTEX get smarter over time?**  
Every execution updates pattern success rates in the Brain's Perception tier. The Intelligence Layer (LENS + Pattern Learner) analyses the last 48 hours of git history to continuously adjust which patterns and strategies it recommends.

---

## Where to Go Next

| Topic | Document |
|-------|----------|
| The Brain tiers in depth | `00-getting-started/brain-tier-architecture.md` |
| LENS analyzer details | `02-lens/01-overview.md` |
| Orchestration architecture | `03-orchestration/01-overview.md` |
| All 26 MCP tools | `04-mcp/tools-catalog.md` |
| Governance rules reference | `01-capabilities/governance-compliance.md` |
| Adding custom tools | `01-capabilities/extensibility.md` |

---

*CORTEX  · February 2026 · Source of truth: `cortex/__wiring_contract__.yaml`*
