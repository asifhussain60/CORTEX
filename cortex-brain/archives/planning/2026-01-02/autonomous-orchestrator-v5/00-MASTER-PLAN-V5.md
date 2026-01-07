# 🛡️ Autonomous Orchestrator v5.0 - Pure Autonomous Architecture

**Feature:** Pure Autonomous Orchestrator System (Option 1 Implementation)  
**Created:** January 2, 2026  
**Refined:** January 2, 2026  
**Status:** 🔄 ACTIVE - Architecture Refined to Pure Autonomous  
**Complexity:** TIER 4 (CRITICAL)  
**Strategy:** Option 1 - Machine-Readable Config + Python Ownership

---

> **🎯 REFINEMENT NOTE (2026-01-02):**  
> This plan has been refined to implement **Option 1: Pure Autonomous** architecture.  
> The hybrid language/code approach has been eliminated. All orchestrators now follow:  
> - Machine-readable YAML/JSON configuration (no imperative instructions)  
> - Python orchestrator owns all execution logic  
> - CORTEX acts as thin client (route → invoke → display)  
> - Single source of truth: SQLite database with transactional phases

---

## 📊 Visual Progress Tracker

**Overall Progress:** `████░░░░░░░░░░░░░░░░` **20%** 🔄 IN PROGRESS

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| -1 | Knowledge Library Consultation | `██████████` | 15m | ✅ Complete |
| 0 | Architecture Analysis (Option 1) | `████████░░` | 2h | 🔄 In Progress |
| 1 | MCP Tool Infrastructure | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 2 | Planning State Database | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 3 | BaseOrchestrator v4.1 (Config-Driven) | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 4 | Planning Orchestrator v5 (Pure Python) | `░░░░░░░░░░` | 4d | ⏸️ Not Started |
| 5 | Config-Only Manifests | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 6 | ADO Orchestrator v2 | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 7 | Vacuum Orchestrator v2 | `░░░░░░░░░░` | 2.5d | ⏸️ Not Started |
| 8 | Cleanup Orchestrator v2 | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 9 | Testing & Validation | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 10 | Migration & Documentation | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 11 | REFACTOR & Cleanup | `░░░░░░░░░░` | 2d | ⏸️ Not Started |

**Estimated Completion:** ~27 days  
**Current Phase:** Architecture refinement and foundation design

---

## 🎯 Executive Summary

### Root Cause of Brittleness

The planning orchestrator breaks due to **hybrid control flow ambiguity**:

1. **Execution Confusion** - Shield emoji (🛡️) signals autonomy, but manifest contains natural language instructions for CORTEX
2. **State Fragmentation** - Progress tracked in JSON files, markdown reports, and Python variables with no single source of truth
3. **Output Ownership Unclear** - Templates assume Python controls output, manifest tells CORTEX to generate content

### Option 1: Pure Autonomous Solution

Transform ALL 4 AUTONOMOUS orchestrators (Planning, ADO, Vacuum, Cleanup) into deterministic Python systems:

```
┌──────────────────────────────────────────────────────┐
│              USER INTENT DETECTION                    │
│         (CORTEX.prompt.md + LLMIntentClassifier)     │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│         MCP TOOL: invoke_orchestrator()              │
│    Parameters: orchestrator_name, user_request       │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│      PYTHON ORCHESTRATOR (Owns Everything)           │
│  • Load YAML config (structure, templates, rules)    │
│  • Execute atomic phases with DB transactions        │
│  • Generate all outputs (markdown, JSON, reports)    │
│  • Return execution summary                          │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│        CORTEX DISPLAYS RESULTS (Thin Client)         │
│    Uses response template: autonomous_execution_progress │
└──────────────────────────────────────────────────────┘
```

**Key Architectural Principles:**

1. **Zero Natural Language Instructions** - Manifests contain only data structures, not commands
2. **Python Owns Execution** - All logic, all decisions, all output generation in orchestrator code
3. **Database State Management** - SQLite with ACID transactions for atomic phases
4. **Config-Driven Behavior** - YAML defines folder templates, validation schemas, output formats
5. **CORTEX as Thin Client** - Route intent → Invoke tool → Display summary → Done

---

## 🏗️ Implementation Strategy

### Phase 1: MCP Tool Infrastructure (3 days)

**Deliverables:**
- `src/mcp/server.py` - MCP protocol server
- `src/mcp/tools/invoke_orchestrator.py` - Universal orchestrator invoker
- `src/mcp/registry.py` - Orchestrator registry with validation
- `cortex-brain/config/mcp-server.yaml` - Server configuration

**Key Features:**
- Tool accepts `orchestrator_name` + `user_request` parameters
- Registry maps names to Python classes + config files
- Automatic error handling and result formatting
- Integration with CORTEX.prompt.md intent routing

### Phase 2: Planning State Database (2 days)

**Database Schema:**
```
plans (plan_id, feature_name, status, created, completed)
phases (phase_id, plan_id, name, status, order, started, completed)
tasks (task_id, phase_id, description, status, estimated_hours)
artifacts (artifact_id, plan_id, path, type, generated)
validations (validation_id, phase_id, check_name, passed, details)
state_snapshots (snapshot_id, plan_id, phase_id, timestamp, data)
```

**Benefits:**
- Atomic phase execution (commit/rollback)
- Recovery from failures at any point
- Complete audit trail
- Progress queries without parsing files

### Phase 3: BaseOrchestrator v4.1 (2 days)

**Core Capabilities:**
- Load YAML config from manifest
- Execute phases with transaction boundaries
- Template rendering (Jinja2) for output generation
- Progress tracking to database
- Validation checkpoint execution
- Result summary formatting

**Config Structure:**
```yaml
orchestrator:
  name: "planning_system"
  version: "5.0"
  
phases:
  - id: "discovery"
    tasks: [...]
    validations: [...]
    templates: [...]
    
output_formats:
  master_plan: "templates/master-plan.jinja2"
  progress_report: "templates/progress-report.jinja2"
  
folder_structure:
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  subfolders: ["context", "artifacts", "reports", "tracking"]
```

### Phase 4: Planning Orchestrator v5 (4 days)

**Pure Python Implementation:**

1. **Context Discovery** - Uses workspace search APIs to find relevant files
2. **Architecture Analysis** - AST parsing for code structure understanding
3. **Plan Generation** - Template-driven markdown generation with injected context
4. **Folder Creation** - Atomic filesystem operations
5. **Progress Tracking** - Real-time updates to state database
6. **Validation** - Automated checks after each phase

**No Natural Language** - All decision logic in Python, no manifest interpretation needed

### Phase 5: Config-Only Manifests (1.5 days)

**Transform ALL manifests to pure configuration:**

**Before (Hybrid - BROKEN):**
```yaml
phases:
  - name: "Discovery"
    instructions: "Search the workspace for relevant files..."  # ❌ Natural language
    steps:
      - "Use grep_search to find..."  # ❌ Imperative command
```

**After (Pure Config - CORRECT):**
```yaml
phases:
  - id: "discovery"
    search_patterns:
      - pattern: "class.*Controller"
        scope: "src/**/*.py"
      - pattern: "def.*test_"
        scope: "tests/**/*.py"
    output_artifacts:
      - type: "context_summary"
        template: "discovery-summary.jinja2"
```

**Python Reads Config:**
```python
for pattern in phase['search_patterns']:
    results = workspace_search(pattern['pattern'], pattern['scope'])
    context.append(results)
```

### Phase 6-8: ADO, Vacuum, Cleanup (7.5 days)

Apply same transformation to remaining orchestrators:
- Strip manifests to config-only
- Implement pure Python execution logic
- Add database state management
- Create output templates

### Phase 9-11: Testing, Migration, Refactor (7 days)

**Testing:**
- Unit tests for each orchestrator phase
- Integration tests for MCP tool invocation
- Database transaction rollback tests
- Config validation tests

**Migration:**
- Archive old manifests to `cortex-brain/archives/manifests-v4/`
- Update CORTEX.prompt.md intent routing
- Update response templates
- Generate migration guide

**Refactor:**
- Remove duplicate code across orchestrators
- Consolidate common utilities
- Clean up obsolete files
- Update documentation

---

## 🎯 Success Criteria

**Reliability:**
- ✅ Zero ambiguity in execution flow (Python owns everything)
- ✅ Atomic phase operations (rollback on failure)
- ✅ Single source of truth (database state)
- ✅ Deterministic output (templates + data)

**Maintainability:**
- ✅ Config changes don't require code changes (within defined schema)
- ✅ Clear separation: Config = Data, Python = Logic
- ✅ Testable phases (mock database, verify outputs)
- ✅ Observable execution (database queries show exact state)

**User Experience:**
- ✅ CORTEX displays clear progress indicators
- ✅ Failed executions provide actionable error messages
- ✅ Plans are resumable from any phase
- ✅ Output quality consistent across runs

---

## 📁 Implementation Artifacts

All implementation code will be created in `future-structure/` folder:

```
future-structure/
├── src/
│   ├── mcp/
│   │   ├── server.py
│   │   ├── registry.py
│   │   └── tools/
│   │       └── invoke_orchestrator.py
│   ├── orchestrators/
│   │   ├── base_orchestrator_v4_1.py
│   │   ├── planning_orchestrator_v5.py
│   │   ├── ado_orchestrator_v2.py
│   │   ├── vacuum_orchestrator_v2.py
│   │   └── cleanup_orchestrator_v2.py
│   └── database/
│       ├── planning_state.db (schema)
│       └── migrations/
├── cortex-brain/
│   ├── config/
│   │   └── mcp-server.yaml
│   └── manifests/orchestrators/
│       ├── planning-system-5.0-manifest.yaml (config-only)
│       ├── ado-operations-2.0-manifest.yaml (config-only)
│       ├── vacuum-2.0-manifest.yaml (config-only)
│       └── cleanup-2.0-manifest.yaml (config-only)
└── .github/prompts/
    └── CORTEX.prompt.md (updated intent routing)
```

---

## 🚦 Next Steps

**Immediate Actions:**
1. Review and approve Option 1 architecture
2. Begin Phase 1 (MCP Tool Infrastructure)
3. Design planning state database schema
4. Create config-only manifest specification

**Future Actions (Post-Phase 1):**
1. Implement BaseOrchestrator v4.1 foundation
2. Refactor Planning Orchestrator v5 to pure Python
3. Transform manifests to config-only format
4. Test end-to-end execution flow

---

## 📚 Reference Documentation

**Key Files:**
- `CORTEX.prompt.md` - Intent routing and hand-off protocol
- `brain-protection-rules.yaml` - SKULL rules (HAND_OFF_PROTOCOL)
- `response-templates-v4.yaml` - autonomous_execution_progress template
- `planning-system-4.0-manifest.yaml` - Current (broken) hybrid manifest

**Architecture Documents:**
- `cortex-brain/documents/planning/active/autonomous-orchestrator-v5/architecture/option-1-pure-autonomous.md`
- `cortex-brain/documents/planning/active/autonomous-orchestrator-v5/architecture/database-schema.md`
- `cortex-brain/documents/planning/active/autonomous-orchestrator-v5/architecture/config-specification.md`

---

**Response Template Compliance:** Uses `autonomous_execution_progress` template  
**TDD Enforcement:** Unit tests required for all phases  
**Final Refactor Required:** Yes (Phase 11 - whole-file cleanup)
