# SPA Dashboard Refactoring Plan
**Created:** 2026-02-08 | **Author:** CORTEX | **Status:** DRAFT

---

## 📋 Context

**User Request:** Refactor SPA dashboard based on violations.md analysis  
**Current State:** Working prototype with 15 critical production issues identified  
**Goal:** Production-ready multi-layer SPA using CORTEX orchestrators  
**Constraint:** file:// protocol, no CSS changes

---

## 🎯 Architecture Decision: Local MCP vs External Server

### Current Issue
User correctly identified: MCP server startup approach is wrong for local development.

### Correct Architecture

| Environment | Approach | Configuration |
|-------------|----------|---------------|
| **Local Dev (VS Code)** | CopilotToolAdapter | Native Copilot tools (grep_search, semantic_search) |
| **Enterprise/Production** | MCPToolAdapter | External MCP server (port 8000) |

### Implementation Strategy

**Phase 1:** Use CopilotToolAdapter (already implemented in CORTEX)  
**Phase 2:** Refactor SPA using Copilot tools directly  
**Phase 3:** Add environment detection for future MCP server mode

---

## 🏗️ Refactoring Phases

### Phase 1: State Management (CRITICAL - P0)
**Issues:** Race conditions, global mutable state, no synchronization  
**Solution:** Implement state versioning + freeze pattern  
**Files:**
- company/dashboards/spa/js/state-manager.js (NEW)
- company/dashboards/spa/js/app.js (REFACTOR)

**Tests:**
- tests/spa/test_state_manager.js (NEW)
- State generation counter
- Stale update rejection
- Cache invalidation

### Phase 2: Error Boundaries (CRITICAL - P0)
**Issues:** No error handling, white screens on failure  
**Solution:** Per-tab error boundaries with fallback UI  
**Files:**
- company/dashboards/spa/js/error-handler.js (NEW)
- company/dashboards/spa/index.html (ADD error UI)

**Tests:**
- tests/spa/test_error_boundaries.js (NEW)
- Visualization crash recovery
- Network failure handling
- Partial load detection

### Phase 3: Lazy Loading & Performance (P1)
**Issues:** All tabs render on load, 8000-item graphs freeze browser  
**Solution:** Tab-based lazy loading, virtual scrolling  
**Files:**
- company/dashboards/spa/js/lazy-loader.js (NEW)
- company/dashboards/spa/js/visualizations.js (REFACTOR)

**Tests:**
- tests/spa/test_lazy_loading.js (NEW)
- Tab activation triggers
- Virtualization cutoffs
- Memory leak prevention

### Phase 4: Security Hardening (P0)
**Issues:** XSS vulnerabilities, no input sanitization  
**Solution:** DOMPurify integration, CSP headers  
**Files:**
- company/dashboards/spa/js/sanitizer.js (NEW)
- company/dashboards/spa/index.html (ADD DOMPurify CDN with SRI)

**Tests:**
- tests/spa/test_security.js (NEW)
- XSS injection attempts
- innerHTML sanitization
- Script tag filtering

### Phase 5: Schema Validation (P1)
**Issues:** No JSON validation, undefined exceptions  
**Solution:** Zod schema validation before render  
**Files:**
- company/dashboards/spa/js/schema.js (NEW)
- company/dashboards/spa/js/app.js (ADD validation)

**Tests:**
- tests/spa/test_schema_validation.js (NEW)
- Missing field detection
- Type checking
- Version compatibility

### Phase 6: SOLID Refactoring (P1)
**Issues:** 961-line monolith, no separation of concerns  
**Solution:** Modularize into Repository Service, State Manager, UI Controller, Viz Factory  
**Files:**
- company/dashboards/spa/js/repository-service.js (NEW)
- company/dashboards/spa/js/ui-controller.js (NEW)
- company/dashboards/spa/js/viz-factory.js (NEW)

**Tests:**
- tests/spa/test_solid_architecture.js (NEW)
- Service layer isolation
- Controller routing
- Factory pattern validation

---

## 🔧 CORTEX Orchestration Strategy

### Orchestrator Routing

| Phase | Orchestrator | Justification |
|-------|--------------|---------------|
| Phase 1-6 | **TDDOrchestrator** | Tests before code (CORE-008) |
| Validation | **EnforcementOrchestrator** | Pre-execution gate |
| Review | **ChallengeEngine** | Design alternatives |

### Audit Trail

All phases logged with AC markers:
```python
# AC_START: AC-SPA-REFACTOR-P1-001
# Description: State manager with versioning
# ... code ...
# AC_COMPLETE: AC-SPA-REFACTOR-P1-001 ✅ 12/12 passing
```

### Implementation Protocol

**For EACH phase:**
1. User says "proceed"
2. Show ASCII progress bar (silent execution)
3. TDDOrchestrator generates tests FIRST
4. Implementation follows (RED→GREEN→REFACTOR)
5. Commit with AC markers
6. Report completion inline

---

## 🚀 Execution Timeline

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1 | 1 day | None |
| Phase 2 | 0.5 day | Phase 1 |
| Phase 3 | 1.5 days | Phase 1, Phase 2 |
| Phase 4 | 0.5 day | None (parallel) |
| Phase 5 | 1 day | Phase 1 |
| Phase 6 | 2 days | All above |
| **Total** | **7 days** | Sequential with some parallel |

---

## 📊 Success Criteria

| Dimension | Current | Target | Measurement |
|-----------|---------|--------|-------------|
| **Correctness** | 4/10 | 9/10 | No race conditions, state versioning |
| **Reliability** | 3/10 | 9/10 | Error boundaries, retry logic |
| **Security** | 5/10 | 9/10 | DOMPurify, CSP, SRI |
| **Scalability** | 2/10 | 8/10 | Virtual scrolling, lazy loading |
| **Maintainability** | 3/10 | 8/10 | SOLID principles, 70% test coverage |

**Overall Target:** 8.6/10 (Production-ready)

---

## 🎯 Next Actions

**AWAITING USER APPROVAL:**

1. Confirm architecture approach (CopilotToolAdapter vs MCP server)
2. Prioritize phases (all 6? or focus on P0 only?)
3. Say "proceed" to start Phase 1

**Once approved, CORTEX will:**
- Execute silently with progress bars
- Generate tests before code (TDD)
- Commit incrementally with AC markers
- Report only on completion or error

---

**Ready to proceed? Say "proceed" to start Phase 1 (State Management).**
