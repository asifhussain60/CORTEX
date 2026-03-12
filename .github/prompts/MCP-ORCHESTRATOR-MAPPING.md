---
scope: non-production-admin
---
# MCP Orchestrator Mapping Guide
**Updated:** 2026-02-23 | **Phase:** Production Readiness  
**Authority:** CORTEX Architect | **Scope:** External Repos + SaaS Deployment

---

## 📋 Overview

CORTEX exposes **51 wired orchestrators** via **36 MCP tools registered**. This guide maps orchestrators to their MCP entry points for external repository integration and SaaS deployment.

**Architecture Principle:** 1 orchestrator ≠ 1 MCP tool. Instead, orchestrators are exposed via:
- **Direct MCP tools** for primary workflows (TDD, Refactor, Plan)
- **Parameterized operations** for shared capabilities (Governance, Debug)
- **Generic invoker** (`cortex_orchestrator`) for support orchestrators

---

## 🎯 Orchestrator → MCP Tool Mapping

### **TIER 1: Core Orchestrators (6)**

| Orchestrator | MCP Tool | Operation | Use Case |
|--------------|----------|-----------|----------|
| **MasterOrchestrator** | `cortex_orchestrator` | `operation="implement"` | Main entry point for all requests |
| **IntentRouter** | `cortex_classify` | `operation="intent"` | Classify user intent |
| **TDDOrchestrator** | `cortex_orchestrator` | `operation="test"` | Test-driven development workflow |
| **EnforcementOrchestrator** | `cortex_governance` | `operation="execute"` | Pre-execution governance gate |
| **WorkflowOrchestrator** | `cortex_workflow` | `operation="execute"` | Multi-step workflow coordination |
| **ConversationOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Multi-turn conversation state |

**Example Usage:**
```json
{
  "tool": "cortex_orchestrator",
  "parameters": {
    "operation": "implement",
    "request": "Add authentication to user service",
    "mode": "TDD"
  }
}
```

---

### **TIER 2: Domain Orchestrators (6)**

| Orchestrator | MCP Tool | Operation | Use Case |
|--------------|----------|-----------|----------|
| **RefactoringOrchestrator** | `cortex_refactor` | `operation="extract"` | Code refactoring (extract, rename, move) |
| **PlanningOrchestrator** | `cortex_plan` | `operation="create"` | Phase planning and roadmap |
| **DomainOrchestrator** | `cortex_orchestrator` | `operation="analyze"` | Domain-specific analysis |
| **DashboardOrchestrator** | `cortex_dashboard` | `operation="generate"` | Dashboard generation (HTML/JSON) |
| **EnhancedPlanningOrchestrator** | `cortex_plan` | `operation="update"` | Enhanced planning with dependencies |
| **ServiceDecompositionOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Service decomposition strategies |

**Example Usage:**
```json
{
  "tool": "cortex_refactor",
  "parameters": {
    "operation": "extract",
    "target": "src/services/user_service.py",
    "refactor_type": "method",
    "scope": "module"
  }
}
```

---

### **TIER 3: Support Orchestrators (10)**

| Orchestrator | MCP Tool | Operation | Use Case |
|--------------|----------|-----------|----------|
| **HealthOrchestrator** | `cortex_health_scan` | N/A | Repository health diagnostics |
| **VacuumOrchestrator** | `cortex_vacuum_execute` | N/A | Markdown sprawl cleanup |
| **SweepCatalogueOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Issue catalogue management |
| **DebuggerOrchestrator** | `cortex_debug` | `operation="analyze"` | Debug workflow (inject, capture, fix) |
| **RepositoryOnboardingOrchestrator** | `cortex_onboard` | `operation="full"` | Repository onboarding (LENS + security) |
| **SetupOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Environment setup |
| **UpgradeOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Version upgrades |
| **RollbackOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Rollback support |
| **PhaseCompletionOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Phase gating |
| **BulkDigestOrchestrator** | `cortex_orchestrator` | `operation="invoke"` | Bulk document ingestion |

**Example Usage:**
```json
{
  "tool": "cortex_health_scan",
  "parameters": {
    "path": "/path/to/external/repo",
    "checks": ["duplicates", "stale_imports", "naming"]
  }
}
```

---

## 🔧 Generic Orchestrator Invoker

### **`cortex_orchestrator` — Universal Entry Point**

For orchestrators without dedicated MCP tools, use the generic invoker:

```json
{
  "tool": "cortex_orchestrator",
  "parameters": {
    "operation": "invoke",
    "orchestrator": "SetupOrchestrator",
    "params": {
      "target_dir": "/path/to/repo",
      "auto_install": true
    }
  }
}
```

**Supported Operations:**
- `list` — List all 22 registered orchestrators
- `status` — Get status of specific orchestrator
- `invoke` — Invoke orchestrator with parameters
- `health_check` — Check health of orchestrators

**List All Orchestrators:**
```json
{
  "tool": "cortex_orchestrator",
  "parameters": {
    "operation": "list"
  }
}
```

**Output:**
```json
{
  "orchestrators": [
    {"name": "MasterOrchestrator", "status": "active", "type": "core", "priority": 10},
    {"name": "IntentRouter", "status": "active", "type": "core", "priority": 20},
    ...
  ],
  "total": 22,
  "by_type": {
    "core": 6,
    "domain": 6,
    "support": 10
  }
}
```

---

## 🩺 Health Check Orchestrators

### **Orchestrator Health Monitoring**

Check health of all or specific orchestrators:

**Check All Orchestrators:**
```json
{
  "tool": "cortex_check",
  "parameters": {
    "operation": "orchestrator_health",
    "parallel": true
  }
}
```

**Check Specific Orchestrator:**
```json
{
  "tool": "cortex_check",
  "parameters": {
    "operation": "orchestrator_health",
    "orchestrator": "TDDOrchestrator"
  }
}
```

**Alternative via Generic Invoker:**
```json
{
  "tool": "cortex_orchestrator",
  "parameters": {
    "operation": "health_check",
    "orchestrator": "RefactoringOrchestrator"
  }
}
```

---

## 🛡️ Stage 0 Governance Audit

### **Pre-Flight Request Validation**

**New in Production:** Stage 0 Governance Audit exposed via `cortex_governance`:

```json
{
  "tool": "cortex_governance",
  "parameters": {
    "operation": "stage0_audit",
    "request": "Create a markdown report file with test results"
  }
}
```

**Output (Violation Detected):**
```json
{
  "audit_passed": false,
  "violations": [
    {
      "rule": "CORE-002",
      "description": "All output inline — never create .md/.txt files",
      "severity": "P0"
    }
  ],
  "action": "Block execution until violations resolved"
}
```

**Authority:** `.github/prompts/cortex-architect.prompt.md` (Stage 0 Spec)

---

## 📊 Tool Category Matrix

### **36 MCP Tools (Registered)**

| Category | Count | Tools |
|----------|-------|-------|
| **CORE** | 3 | `cortex_orchestrator`, `cortex_challenge`, `cortex_classify` |
| **INTELLIGENCE** | 4 | `cortex_lens`, `cortex_knowledge`, `cortex_git`, `cortex_generate_tests` |
| **GOVERNANCE** | 4 | `cortex_governance`, `cortex_validate`, `cortex_load`, `cortex_validate_request` |
| **OPERATIONS** | 6 | `cortex_debug`, `cortex_refactor`, `cortex_plan`, `cortex_onboard`, `cortex_dashboard`, `cortex_workflow` |
| **UTILITIES** | 7 | `cortex_verify`, `cortex_ask`, `cortex_vacuum`, `cortex_tools_catalog`, `cortex_total_recall`, `cortex_metrics`, `cortex_check` |

---

## 🚀 SaaS Deployment Checklist

### **External Repository Integration**

- ✅ **Orchestrator Discovery:** `cortex_orchestrator` (operation="list") exposes all 51 orchestrators
- ✅ **Health Monitoring:** `cortex_check` (operation="orchestrator_health") for system status
- ✅ **Governance Gate:** `cortex_governance` (operation="stage0_audit") validates requests pre-flight
- ✅ **TDD Workflow:** `cortex_orchestrator` (operation="test") for test-driven development
- ✅ **Refactoring:** `cortex_refactor` with 5 operations (extract, rename, move, inline, organize)
- ✅ **Repository Onboarding:** `cortex_onboard` (operation="full") for LENS + security scan
- ✅ **Dashboard Generation:** `cortex_dashboard` (operation="generate") for repo dashboards

### **Tool Discovery**

```json
{
  "tool": "cortex_tools_catalog",
  "parameters": {
    "operation": "list",
    "category": "core"
  }
}
```

**Returns:** All 38 tools with descriptions, parameters, and operations.

---

## 🔗 References

- **MCP Registry:** `cortex/mcp/mcp_registry.py` (24 tool definitions)
- **Tool Implementations:** `cortex/mcp/tools/` 
- **Wiring Specs:** `cortex-registry/core/specifications/` (4 YAML files)
- **Architect Prompt:** `.github/prompts/cortex-architect.prompt.md`
- **Setup Guide:** `.github/prompts/MCP-SETUP-GUIDE.md`

---

## ✅ Validation

All 29 registered tools (39 target) tested:
- `python3 -m cortex.mcp` — Server starts without import errors
- `cortex_verify` (op: `mcp`) — MCP detection test passes
- `.vscode/settings.json` — Pylance-style stdio transport configured

**No tool sprawl:** Consolidated from 98 legacy tools → 29 registered (39 target) tools.

---

**AC_START:** AC-MCP-PROD-001  
**Authority:** CORTEX Architect | **Updated:** 2026-02-23
