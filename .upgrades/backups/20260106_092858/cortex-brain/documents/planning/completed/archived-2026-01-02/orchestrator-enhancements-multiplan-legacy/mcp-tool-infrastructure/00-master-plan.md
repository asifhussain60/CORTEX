# 🔧 MCP Tool Infrastructure - Enhancement Plan

**Plan ID:** `mcp-tool-infrastructure-2026-01-02`  
**Parent Tracker:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**Priority:** 🔴 P0 (FIRST - Cross-cutting fix)  
**Created:** January 2, 2026  
**Status:** ⏸️ NOT STARTED

---

## 📊 Progress Tracker

```
░░░░░░░░░░░░░░░░░░░░  0% Complete
```

| Phase | Name | Progress | Tasks | Status |
|-------|------|----------|-------|--------|
| -1 | Knowledge Library Consultation | `░░░░░░░░░░` | 0/3 | ⏸️ |
| 0 | Requirements & Design | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 1 | MCP Server Setup | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 2 | invoke_orchestrator() Tool | `░░░░░░░░░░` | 0/8 | ⏸️ |
| 3 | Orchestrator Registry | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 4 | Testing & Validation | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 5 | REFACTOR & Cleanup | `░░░░░░░░░░` | 0/4 | ⏸️ |

**Total Tasks:** 0/37  
**Estimated Duration:** 3 days

---

## 🎯 Executive Summary

This plan implements the **MCP (Model Context Protocol) Tool Infrastructure** that enables all AUTONOMOUS orchestrators to be invoked from GitHub Copilot.

### Problem Statement
`CORTEX.prompt.md` instructs Copilot to "STOP and hand-off" to orchestrators, but **no mechanism exists** to actually invoke the Python orchestrator code.

### Solution
Create an MCP tool `invoke_orchestrator()` that:
- Receives orchestrator name from Copilot
- Looks up orchestrator in registry
- Executes Python orchestrator code
- Returns execution result to Copilot

### Impact
**Fixes ALL 4 AUTONOMOUS orchestrators** with one implementation:
- Planning System
- ADO Operations
- Vacuum
- Cleanup

---

## 📋 Phase Details

### Phase -1: Knowledge Library Consultation
**Duration:** 15 minutes

| # | Task | Deliverable |
|---|------|-------------|
| -1.1 | Query MCP server patterns | `context/mcp-patterns.md` |
| -1.2 | Query tool registration patterns | `context/tool-registration.md` |
| -1.3 | Query orchestrator interfaces | `context/orchestrator-interfaces.md` |

### Phase 0: Requirements & Design
**Duration:** 2 hours

| # | Task | Deliverable |
|---|------|-------------|
| 0.1 | Define MCP tool interface | `artifacts/mcp-tool-interface.md` |
| 0.2 | Design orchestrator registry | `artifacts/registry-design.md` |
| 0.3 | Define execution protocol | `artifacts/execution-protocol.md` |
| 0.4 | List supported orchestrators | `artifacts/supported-orchestrators.md` |
| 0.5 | Create test strategy | `artifacts/test-strategy.md` |

### Phase 1: MCP Server Setup
**Duration:** 1 day

| # | Task | Deliverable |
|---|------|-------------|
| 1.1 | Create MCP server module | `src/mcp/__init__.py` |
| 1.2 | Implement server base | `src/mcp/server.py` |
| 1.3 | Add tool registration | `src/mcp/tools.py` |
| 1.4 | Configure server startup | `src/mcp/config.py` |
| 1.5 | Add logging & observability | `src/mcp/logging.py` |
| 1.6 | Write unit tests | `tests/mcp/test_server.py` |

### Phase 2: invoke_orchestrator() Tool
**Duration:** 1 day

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Define tool schema | `artifacts/invoke-schema.json` |
| 2.2 | Implement tool function | `src/mcp/tools/invoke_orchestrator.py` |
| 2.3 | Add parameter validation | Validation logic |
| 2.4 | Add orchestrator lookup | Registry lookup |
| 2.5 | Implement execution wrapper | Execution logic |
| 2.6 | Add result serialization | JSON response |
| 2.7 | Add error handling | Exception handling |
| 2.8 | Write unit tests | `tests/mcp/test_invoke_orchestrator.py` |

### Phase 3: Orchestrator Registry
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 3.1 | Create registry interface | `src/mcp/registry.py` |
| 3.2 | Register Planning orchestrator | Registry entry |
| 3.3 | Register ADO orchestrator | Registry entry |
| 3.4 | Register Vacuum orchestrator | Registry entry |
| 3.5 | Register Cleanup orchestrator | Registry entry |

### Phase 4: Testing & Validation
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 4.1 | Integration test: Planning | Test case |
| 4.2 | Integration test: ADO | Test case |
| 4.3 | Integration test: Vacuum | Test case |
| 4.4 | Integration test: Cleanup | Test case |
| 4.5 | End-to-end test | Full flow test |
| 4.6 | Performance validation | <100ms response |

### Phase 5: REFACTOR & Cleanup
**Duration:** 2 hours

| # | Task | Deliverable |
|---|------|-------------|
| 5.1 | Remove unused imports | Clean code |
| 5.2 | Fix code smells | Refactored code |
| 5.3 | Add documentation | Docstrings |
| 5.4 | Update type hints | Type annotations |

---

## 📐 Architecture

### Current (BROKEN)
```
User Intent
    ↓
CORTEX.prompt.md ("STOP")
    ↓
??? (nothing happens)
```

### Target (v5.0)
```
User Intent
    ↓
CORTEX.prompt.md
    ↓
MCP Tool: invoke_orchestrator(name="planning")
    ↓
MCP Server
    ↓
Orchestrator Registry
    ↓
planning_orchestrator.py.execute()
    ↓
Result returned to Copilot
```

### MCP Tool Schema

```json
{
  "name": "invoke_orchestrator",
  "description": "Invoke a CORTEX orchestrator by name",
  "parameters": {
    "type": "object",
    "properties": {
      "orchestrator_name": {
        "type": "string",
        "enum": ["planning", "ado", "vacuum", "cleanup"],
        "description": "Name of the orchestrator to invoke"
      },
      "context": {
        "type": "object",
        "description": "Context to pass to orchestrator",
        "properties": {
          "user_request": { "type": "string" },
          "workspace_path": { "type": "string" },
          "conversation_id": { "type": "string" }
        }
      }
    },
    "required": ["orchestrator_name"]
  }
}
```

---

## 🔗 Dependencies

### Upstream
- None (foundational component)

### Downstream (depends on this)
- [Planning System v5](../planning-system-v5/00-master-plan.md)
- [ADO Operations v2](../ado-operations-v2/00-master-plan.md)
- [Vacuum v2](../vacuum-v2/00-master-plan.md)
- [Cleanup v2](../cleanup-v2/00-master-plan.md)

---

## ✅ Definition of Done

- [ ] MCP server starts without errors
- [ ] `invoke_orchestrator()` tool registered
- [ ] All 4 orchestrators in registry
- [ ] Unit tests passing (≥80% coverage)
- [ ] Integration tests passing
- [ ] Response time <100ms
- [ ] Documentation complete
- [ ] REFACTOR phase complete

---

## 📞 Copilot Instructions

```yaml
plan_id: mcp-tool-infrastructure-2026-01-02
priority: P0
cross_cutting: true
tdd_enforcement: mandatory
deliverable: src/mcp/
test_coverage_target: 80%
```

---

**⬆️ Back to:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**➡️ Next:** [Planning System v5](../planning-system-v5/00-master-plan.md) (after this completes)
