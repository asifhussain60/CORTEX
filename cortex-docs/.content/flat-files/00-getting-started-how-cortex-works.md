# How CORTEX Works

---
title: How CORTEX Works — End-to-End Request Lifecycle
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-25
source_of_truth: cortex/orchestrators/core/ + cortex/mcp/ + cortex/lens/
phases_complete: [Phase 58, Phase 60, Phase 65, Phase 67]
format: 10k-view
order: 3
---

> **Goal:** Give you a clear mental model of what happens — step by step — from the moment you type a request to the moment CORTEX delivers a result.

---

## The Shortest Possible Summary

You type a request in your IDE. CORTEX enriches it, classifies it, analyses your codebase with 8 parallel analyzers, validates against 35 governance rules, builds an execution plan through Perception → Reasoning → Action, and delivers the result inline — all within seconds. Every step is observable and auditable.

---

## The Mental Model: A Brain Processing a Stimulus

Imagine your brain receiving a complex instruction — "catch that ball":

1. **Sensory Input** — your eyes and ears register the stimulus (→ MCP Gateway receives the request)
2. **Thalamus** — routes the signal to the right brain region (→ IntentRouter classifies intent)
3. **Sensory Cortex** — processes raw data into perception (→ LENS analyzes the codebase)
4. **Prefrontal Cortex** — decides what to do (→ Brain Reasoning selects strategy)
5. **Motor Cortex** — executes the plan (→ Orchestrator writes code via TDD)
6. **Cerebellum** — checks coordination and balance (→ Governance Gate validates)

Your brain does this in milliseconds. CORTEX does it in seconds — with full auditability.

---

## Step-by-Step: What Happens When You Send a Request

### Stage −1 · Request Pre-Processor (15–35ms)

Before your request reaches any orchestrator, the **RequestRephraseOrchestrator** (`cortex/orchestrators/core/request_rephrase_orchestrator.py`) silently enriches it:

- Adds relevant governance context (which CORE rules apply)
- Attaches a breaking-risk assessment
- Surfaces design pillar considerations
- Flags if a Challenge Gate should trigger (high-risk changes)

**You don't see this stage.** It happens automatically and ensures MasterOrchestrator always receives a fully-contextualised request.

**Business Leader:** "Every request gets a risk assessment before anything happens — like a pre-flight safety check."
**Product Owner:** "Governance context is injected automatically. I don't need to remind developers about rules."
**Developer:** "My request gets enriched with relevant CORE rules. When I say 'fix the auth module', CORTEX already knows which governance standards apply."

---

### Stage 0 · MCP Gateway (5–15ms)

Your enriched request arrives at the **MCP Gateway** (`cortex/mcp/`) over JSON-RPC 2.0 (stdio in development). The gateway:

- Validates the JSON-RPC 2.0 message
- Routes to the correct MCP tool (one of 26 active tools)
- Enforces rate limiting
- Checks the **Native Tool Gate** (CORE-049) — blocks direct file operations for IMPLEMENT/FIX/REFACTOR intents

**MCP server configuration** (`.vscode/settings.json`):
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

---

### Stage 1 · Intent Classification (20–40ms)

**IntentRouter** (`cortex/orchestrators/core/intent_router.py`) uses LENS intelligence to determine what the request is asking for:

| Intent | Routed To | Orchestrator Location |
|--------|-----------|----------------------|
| IMPLEMENT | TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| FIX | TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| REFACTOR | RefactoringOrchestrator | `cortex/orchestrators/core/refactoring_orchestrator.py` |
| ANALYZE | LENS Synthesis | `cortex/orchestrators/synthesis/` |
| PLAN | PlanningOrchestrator | `cortex/orchestrators/core/planning_orchestrator.py` |
| AUDIT | EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| DESIGN | Design Orchestrator | `cortex/orchestrators/core/` |
| DEBUG | DebuggerOrchestrator | `cortex/orchestrators/core/debugger_orchestrator.py` |
| INVESTIGATE | Intelligence Orchestrator | `cortex/orchestrators/intelligence/` |
| QUERY | Domain routing | Context-dependent |
| DIGEST | Digest Coordinator | `cortex/orchestrators/support/` |
| REPHRASE | RequestRephraseOrchestrator | `cortex/orchestrators/core/request_rephrase_orchestrator.py` |

**Brain analogy:** IntentRouter is the **thalamus** — the relay station that receives all incoming signals and routes them to the correct specialized processing region.

---

### Stage 2 · LENS Analysis (300–800ms)

When the orchestrator needs to understand the codebase, **LENS** (`cortex/lens/`) runs **8 parallel analyzers**:

| Analyzer | What It Detects |
|----------|----------------|
| **AST** | Code structure, classes, functions, imports |
| **Git History** | Change frequency, recent modifications, author patterns |
| **Comment** | Documentation coverage, TODO/FIXME density |
| **Import** | Dependency graph, circular imports, stale imports |
| **Security** | SQL injection, XSS, credential exposure, CVE patterns |
| **Pattern** | Framework signatures, architecture styles |
| **Metrics** | Cyclomatic complexity, lines of code, coupling |
| **Domain** | Business domain detection (finance, healthcare, etc.) |

**Brain analogy:** These 8 analyzers are like the **8 sensory processing streams** in the brain — each specialized for one type of perception, all running simultaneously, producing a unified awareness.

---

### Stage 3 · Brain Intelligence (50–200ms)

The intelligence system (`cortex/intelligence/`) processes LENS data through three tiers:

1. **Perception** (`cortex/intelligence/perception/`) — matches repository signatures against known patterns (9 enterprise patterns in registry)
2. **Reasoning** (`cortex/intelligence/reasoning/`) — selects the best strategy, weighted by historical success rates
3. **Action** (`cortex/intelligence/action/`) — builds a step-by-step execution plan with TDD gates and rollback points

**Product Owner:** "The Brain learns. Patterns from one repo inform recommendations in the next. Strategy success rates are tracked and ranked."

---

### Stage 4 · Governance Gate (<150ms)

**EnforcementOrchestrator** (`cortex/orchestrators/core/enforcement_orchestrator.py`) coordinates **10 enforcement agents**:

- TDD Agent — enforces CORE-008 (test before code)
- Security Agent — checks for vulnerabilities
- Compliance Agent — validates CORE rule adherence
- Naming Agent — enforces CORE-028 (snake_case)
- Incremental Agent — enforces CORE-001 (bounded execution)
- Architecture Agent — validates structural integrity
- Markdown Agent — enforces CORE-002 (no report files)

Result: **PASS**, **WARNING**, or **BLOCKED**. BLOCKED = operation stops immediately, no files changed.

---

### Stage 5 · Execution

The designated orchestrator executes the plan. For IMPLEMENT/FIX:

1. **RED** — TDDOrchestrator writes a failing test
2. **GREEN** — Minimum code to pass the test
3. **REFACTOR** — Improve code while keeping tests green

For REFACTOR: RefactoringOrchestrator performs semantic transformations with regression scoring.

For ANALYZE: LENS produces a full 8-analyzer report delivered inline.

---

### Stage 6 · Result Delivery

Results are delivered **inline** per CORE-002. No `.md` or `.txt` files are created. The audit trail is recorded in CortexAuditDB (SQLite with WAL mode, stored in `.cortex-runtime/`).

---

## Complete Pipeline Summary

```
[You] → IDE (VS Code / Cursor)
  → [Stage -1] RequestRephraseOrchestrator (15-35ms)
    → [Stage 0] MCP Gateway (5-15ms)
      → [Stage 1] IntentRouter (20-40ms)
        → [Stage 2] LENS 8-Analyzer Scan (300-800ms)
          → [Stage 3] Brain: Perception → Reasoning → Action (50-200ms)
            → [Stage 4] Governance Gate: 7 Agents (<150ms)
              → [Stage 5] Orchestrator Execution (TDD / Refactor / Analysis)
                → [Stage 6] Inline Result + Audit Trail
```

---

*All module paths verified against live codebase · 25 February 2026 · Phase 58 (OrchestratorProtocolMixin), Phase 60 (dissolved cortex/core/execution → workflow/), Phase 65/66 (Intelligence Matrix), Phase 67 (WorkflowEngine FSM) reflected*
