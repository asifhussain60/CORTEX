---
name: cortex-debug
description: 'CORTEX debug pipeline skill. Use when: running /debug, /debug-inject, /debug-cleanup, inserting debug markers, analyzing test failures, tracing API calls, capturing frontend console output, or investigating root causes with marker injection. Covers 8 injection strategies (3 Python + 5 multi-stack), Vision API, and auto-cleanup.'
argument-hint: 'debug <file> | debug-inject <path> | debug-cleanup'
---

# CORTEX Multi-Stack Debug Pipeline

**5-phase pipeline: inject → capture → analyze → fix-plan → cleanup**

---

## Commands

| Command | What |
|---|---|
| `/debug {path}` | Full pipeline: inject markers → capture → analyze → fix-plan → cleanup |
| `/debug-inject {path}` | Insert `CORTEX_DEBUG` markers only |
| `/debug-cleanup` | Remove all `CORTEX_DEBUG` markers across all languages |

---

## 8 Injection Strategies

### Python Strategies (3)

| Strategy | Trigger |
|---|---|
| `TestFailureStrategy` | pytest failures, assertion errors |
| `RefactorRegressionStrategy` | Tests passing before refactor, failing after |
| `GovernanceViolationStrategy` | CORE-rule violations, AC marker issues |

### Multi-Stack Strategies (5 — Phase 86)

| Strategy | Scope | Markers |
|---|---|---|
| `FrontendConsoleStrategy` | JS/TS/React/Angular/Vue | `console.log('[CORTEX_DEBUG]', ...)` |
| `HtmlVisionMappingStrategy` | HTML + Vision API | Screenshot → DOM element mapping |
| `ApiTraceStrategy` | REST/GraphQL/gRPC | Request/response + timing |
| `SqlTraceStrategy` | SQL Server/Oracle/PostgreSQL | Query plan + parameter capture |
| `DotNetTraceStrategy` | C#/.NET | `Debug.WriteLine("[CORTEX_DEBUG]")` |

---

## Pipeline Phases

### Phase 1: INJECT
- Strategy auto-selected from error context
- Markers follow universal format: `[CORTEX_DEBUG:{strategy}:{id}]`
- `MarkerInjectionEngine` — `cortex/orchestrators/support/debugging/marker_injection_engine.py`

### Phase 2: CAPTURE
- Run failing operation with markers active
- Collect stdout/stderr, logs, screenshots (Vision), traces

### Phase 3: ANALYZE
- LENS analysis on captured data
- Correlation: marker → failure → root cause

### Phase 4: FIX-PLAN
- Generate fix proposal with TDD cycle
- Route to IMPLEMENT/FIX/REFACTOR as appropriate

### Phase 5: CLEANUP
- `AutoCleanupManager` — removes ALL `CORTEX_DEBUG` markers
- Cross-language: Python, JS/TS, HTML, C#, SQL
- Source: `cortex/orchestrators/support/debugging/auto_cleanup_manager.py`

---

## Entry Points

| Component | Location |
|---|---|
| DebuggerOrchestrator | `cortex/orchestrators/support/debugger_orchestrator.py` |
| MarkerInjectionEngine | `cortex/orchestrators/support/debugging/marker_injection_engine.py` |
| AutoCleanupManager | `cortex/orchestrators/support/debugging/auto_cleanup_manager.py` |
| Debug Agent | `.github/agents/support/cortex-debugger.md` |
| Pipeline Template | `cortex-registry/workflows/templates/debugging/multi-stack-debug-pipeline.yaml` |
