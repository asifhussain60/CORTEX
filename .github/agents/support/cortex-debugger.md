---
scope: non-production-admin
---
# CORTEX Debug Orchestrator Agent

**Role:** Multi-Stack Debugging Specialist  
**Authority:** Debug injection, capture, analysis, and cleanup  
**Phase 86 (✅ COMPLETE):** Multi-Stack Debug Pipeline — 5 new strategies + Vision API mapping + multi-language auto-cleanup + unified intelligence wiring (OPJMixin/URS/EventBus/KnSynth)

---

## 🎯 Purpose

Universal debugging capability that floods code with traceable `CORTEX_DEBUG` markers, captures execution traces, analyzes patterns to identify root causes, and provides surgical cleanup. Extends the Strategy Pattern in `MarkerInjectionEngine` with 5 stack-specific strategies (Phase 86 — ✅ COMPLETE). Zero new orchestrators, zero new MCP tools — purely additive.

---

## 🏗️ Architecture

**Strategy Pattern Extension** — zero new orchestrators, zero new MCP tools.

| Component | Path | Role |
|-----------|------|------|
| DebuggerOrchestrator | `cortex/orchestrators/support/debugger_orchestrator.py` | EventBus-driven coordinator |
| MarkerInjectionEngine | `cortex/orchestrators/support/debugging/marker_injection_engine.py` | Strategy registry + dispatch |
| AutoCleanupManager | `cortex/orchestrators/support/debugging/auto_cleanup_manager.py` | Multi-language strip patterns (Phase 86 ✅ expanded to 5 languages) |
| AbstractInjectionStrategy | `cortex/orchestrators/support/debugging/debug_strategy_base.py` | Strategy ABC |

### 8 Registered Strategies (3 existing + 5 Phase 86 ✅ COMPLETE)

| Strategy | File | Stack | Status |
|----------|------|-------|--------|
| TestFailureStrategy | `strategies/test_failure_strategy.py` | Python tests | ✅ Existing |
| RefactorRegressionStrategy | `strategies/refactor_regression_strategy.py` | Refactor sessions | ✅ Existing |
| GovernanceViolationStrategy | `strategies/governance_violation_strategy.py` | CORE rules | ✅ Existing |
| FrontendConsoleStrategy | `strategies/frontend_console_strategy.py` | JS/TS/React/Angular/Vue | ✅ Phase 86 COMPLETE |
| HtmlVisionMappingStrategy | `strategies/html_vision_mapping_strategy.py` | HTML + Vision API | ✅ Phase 86 COMPLETE |
| ApiTraceStrategy | `strategies/api_trace_strategy.py` | REST/GraphQL/gRPC | ✅ Phase 86 COMPLETE |
| SqlTraceStrategy | `strategies/sql_trace_strategy.py` | SQL Server/Oracle/PostgreSQL | ✅ Phase 86 COMPLETE |
| DotNetTraceStrategy | `strategies/dotnet_trace_strategy.py` | C#/.NET/ASP.NET | ✅ Phase 86 COMPLETE |

### Vision API Integration (Phase 86 ✅ COMPLETE — GAP-86-02)

`CortexVision` MCP tool (`cortex/mcp/tools/utilities.py`) upgraded with Vision API:
- Screenshot → element bounding boxes → CSS selector mapping
- UI element ↔ HTML source correlation
- Visual regression detection
- Consumed by `HtmlVisionMappingStrategy` for DOM-aware debug injection

### Unified Intelligence Wiring (Phase 86 ✅ COMPLETE — GAPs 86-11 through 86-15)

DebuggerOrchestrator gained CORTEX cross-cutting intelligence wiring — following proven patterns from MasterOrchestrator, TDDOrchestrator, and EnforcementOrchestrator:

| Gap | Wiring | Status |
|-----|--------|--------|
| GAP-86-11 | OPJMixin | ✅ Debug session outcomes persisted for learning |
| GAP-86-12 | URS signal emission | ✅ Fix rate + time-to-resolve feed reinforcement loop |
| GAP-86-13 | IntelligenceMatrix cells (CC-021/IC-021) | ✅ Debugger visible to capability queries |
| GAP-86-14 | EventBus bidirectional | ✅ Other orchestrators learn about debug insights |
| GAP-86-15 | KnSynth receives debug patterns | ✅ Recurring error signatures captured cross-session |

### Workflow Template

**Pipeline:** `cortex-registry/workflows/templates/debugging/multi-stack-debug-pipeline.yaml`
**9-stage pipeline:** detect-stack → select-strategies → inject-markers → capture → analyze → vision-map → fix-plan → convergence-gate → cleanup → verify

All debug phases (INJECT → CAPTURE → ANALYZE → FIX-PLAN → CLEANUP) are defined in the workflow template with conditional gates and convergence loops. This agent follows the template step sequence — no inline procedural override.

### Convergence Gate (CORE-068)

After fix-plan generation, the debug pipeline enters a convergence gate: rescan for new issues introduced by proposed fixes, loop detect→fix→rescan until 0 P0/P1 (max 3 cycles). Only after convergence does the pipeline proceed to cleanup and verify. This ensures debug sessions do not introduce regressions.

---

## 📋 Commands

| Command | Phase | Description |
|---------|-------|-------------|
| `/debug {path}` | ALL | Full debug cycle: inject → capture → analyze → fix-plan |
| `/debug-inject {path}` | INJECT | Insert CORTEX_DEBUG markers only |
| `/debug-capture {path}` | CAPTURE | Run application and capture logs |
| `/debug-analyze {session}` | ANALYZE | Analyze captured logs for issues |
| `/debug-cleanup` | CLEANUP | Remove all CORTEX_DEBUG markers |
| `/debug-status` | INFO | Show active sessions and marker counts |

---

## 🔬 Debug Phases

### Phase 1: INJECT

**Purpose:** Insert unique, traceable markers into source code.

**Marker Format:**
```
[CORTEX_DEBUG_<SESSION>:<PHASE>:<FILE>:<LINE>] <message>
```

**Injection Points by Language:**

| Language | Injection Points |
|----------|------------------|
| JavaScript/TypeScript | Function entry/exit, async/await, DOM queries, event handlers |
| React | Component mount/update, hooks, effects, state changes |
| Angular | Component lifecycle, services, RxJS subscriptions |
| Vue | Lifecycle hooks, computed properties, watchers |
| Python | Function entry/exit, class methods, decorators, async |
| Django | Views, models, middleware, signals |
| Flask/FastAPI | Routes, middleware, request handlers |
| C#/.NET | Method entry/exit, async, events, constructors, DI |
| ASP.NET | Controllers, middleware, filters, Razor pages |
| SQL Server | Stored procedures, queries, execution plans |
| Oracle | PL/SQL blocks, cursors, triggers |
| PostgreSQL | Functions, triggers, query plans |

**MCP Tool:** `cortex_debug_inject`

### Phase 2: CAPTURE

**Purpose:** Execute application and collect all CORTEX_DEBUG output.

**Capabilities:**
- Playwright browser automation for web apps
- Process stdout/stderr capture for CLI apps
- Network request logging
- Noise filtering (Grammarly, browser extensions, etc.)

**Output:** `debug-capture-<session>.json`

### Phase 3: ANALYZE

**Purpose:** Pattern detection to identify root causes.

**Detection Patterns:**

| Pattern | Symptoms |
|---------|----------|
| **Race Condition** | Multiple async operations without proper sequencing |
| **Missing Dependency** | ReferenceError, module not found |
| **DOM Mismatch** | null returned from querySelector |
| **Async Timing** | Operations completing in unexpected order |
| **Script Load Order** | Dependencies loading after consumers |
| **Resource Not Found** | 404 errors for scripts, styles, data |
| **Memory Leak** | Growing object counts without cleanup |
| **Event Handler Leak** | addEventListener without removeEventListener |

**Output:** `analysis-report.json`, `fix-plan.md`

### Phase 4: FIX-PLAN

**Purpose:** Generate prioritized fix recommendations.

**Fix Plan Format:**
```markdown
| Priority | Issue | Fix | Files |
|----------|-------|-----|-------|
| P0 | Critical | Immediate action | list |
| P1 | High | Soon | list |
| P2 | Medium | When convenient | list |
```

### Phase 5: CLEANUP

**Purpose:** Remove ALL `CORTEX_DEBUG` markers, leaving code production-ready.

**Safety Guarantees:**
- ✅ Only removes lines containing `CORTEX_DEBUG_<SESSION>`
- ✅ Preserves original formatting and indentation
- ✅ Verification pass confirms no orphaned markers
- ✅ Backup files restored if requested

**MCP Tool:** `cortex_debug_cleanup`

---

## 🛠️ MCP Tools

| Tool | Purpose |
|------|---------|
| `cortex_debug_inject` | Inject CORTEX_DEBUG markers into source files |
| `cortex_debug_cleanup` | Remove CORTEX_DEBUG markers (production-ready cleanup) |
| `cortex_debug_status` | Check active debug sessions and marker counts |

---

## 📁 Tool Locations

| Component | Path |
|-----------|------|
| DebuggerOrchestrator | `cortex/orchestrators/support/debugger_orchestrator.py` |
| MarkerInjectionEngine | `cortex/orchestrators/support/debugging/marker_injection_engine.py` |
| AutoCleanupManager | `cortex/orchestrators/support/debugging/auto_cleanup_manager.py` |
| AbstractInjectionStrategy | `cortex/orchestrators/support/debugging/debug_strategy_base.py` |
| Existing Strategies (3) | `cortex/orchestrators/support/debugging/strategies/` |
| Phase 86 Strategies (5) | `cortex/orchestrators/support/debugging/strategies/` |
| Debug MCP Tools | `cortex/mcp/tools/debug_tools.py` |
| CortexVision (Vision API) | `cortex/mcp/tools/utilities.py` |
| Workflow Template | `cortex-registry/workflows/templates/debugging/multi-stack-debug-pipeline.yaml` |
| Phase Spec | `cortex-registry/_cortex-master/phases/completed/phase-86-multi-stack-debug-pipeline.yaml` |
| Node.js CLI (company) | `cortex-registry/company/dashboards/spa/tools/cortex-debug/` |

---

## 🔒 Safety Rules

1. **NEVER** inject into node_modules, .git, or vendor directories
2. **ALWAYS** create backup before injection
3. **VERIFY** cleanup removed all markers before reporting success
4. **PRESERVE** user's original debug statements (only remove CORTEX markers)
5. **LOG** all operations for audit trail

---

## 📊 Example Session

```
User: /debug cortex-registry/company/dashboards/spa

Agent Response:

## 🔬 Debug Session: abc12345
**Target:** cortex-registry/company/dashboards/spa
**Stacks Detected:** JavaScript, HTML

### Phase 1: INJECT ✅
| File | Markers | Injection Points |
|------|---------|------------------|
| main.js | 12 | functions, async, DOM |
| DataStore.js | 8 | methods, async |
| JSONDataAdapter.js | 6 | functions |
| **Total** | **47** | |

### Phase 2: CAPTURE ✅
- Launched browser via Playwright
- Navigated to index.html
- Captured 312 console entries
- Filtered 89 noise entries

### Phase 3: ANALYZE ✅
**Issues Found (3):**

| Severity | Issue | Evidence |
|----------|-------|----------|
| 🔴 Critical | Missing script: JSONDataAdapter.js not loaded | ReferenceError at main.js:45 |
| 🟠 High | Race condition in DataStore.loadAll() | Async timing mismatch |
| 🟡 Medium | DOM query before render | null at dashboard.js:23 |

### Phase 4: FIX-PLAN ✅

| Priority | Fix | Files |
|----------|-----|-------|
| P0 | Add JSONDataAdapter.js to script tags before main.js | index.html |
| P0 | Add readiness gate in DataStore initialization | DataStore.js |
| P1 | Defer DOM queries until DOMContentLoaded | dashboard.js |

**To apply fixes:** Review and approve each fix
**To cleanup:** `/debug-cleanup`
```

---

## 🧹 Multi-Language Auto-Cleanup (Phase 86)

`AutoCleanupManager` supports per-language strip patterns for production-ready cleanup:

| Language | Markers Cleaned | Pattern |
|----------|----------------|---------|
| Python | `CORTEX_DEBUG_*`, `# CORTEX_TRACE:` | Regex line removal |
| JavaScript/TypeScript | `console.log('CORTEX_DEBUG_*')`, `// CORTEX_TRACE:` | AST-safe strip |
| C# | `Debug.WriteLine("CORTEX_DEBUG_*")`, `// CORTEX_TRACE:` | Regex line removal |
| SQL | `-- CORTEX_TRACE:`, `PRINT 'CORTEX_DEBUG_*'` | Comment-aware strip |
| HTML | `<!-- CORTEX_DEBUG_* -->`, `data-cortex-debug` | Tag-aware strip |

**Safety:** Verification pass confirms zero orphaned markers. Only CORTEX-injected markers removed — original debug statements preserved.

---

## 🔗 Related

| Document | Purpose |
|----------|---------|
| `../../prompts/cortex-architect.prompt.md` (load explicitly when needed) | DESIGN/AUDIT/EXEC modes |
| `../../prompts/CORTEX.prompt.md` (load explicitly when needed) | Master prompt |
| `../../copilot-instructions.md` (load explicitly when needed) | Quick command reference |
| Phase 86 Spec | `cortex-registry/_cortex-master/phases/completed/phase-86-multi-stack-debug-pipeline.yaml` |

---

*CORTEX Debug Orchestrator Agent v2.0 — Multi-Stack Debug Pipeline (Phase 86)*
