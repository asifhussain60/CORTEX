# CORTEX 2.0 Agent Workflows

**Document:** 10-agent-workflows.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Define clear, reliable workflows for CORTEX agents that leverage the new 2.0 capabilities:
- Plugin-first execution with explicit hooks
- Conversation state continuity and task tracking
- Incremental creation for large outputs
- Self-review and database maintenance integration
- Safety boundaries (knowledge protection, paths, config)

---

## 🧠 Agent Roles (High-Level)

- Tier 0 — Core Guardians
  - Rule Engine: enforce 27 rules
  - Path Resolver: environment-agnostic paths
  - Config Loader: typed config resolution
  - Knowledge Boundary Guard: prevent core/project leakage

- Tier 1 — Conversation & Tasks
  - Conversation Manager: resume, summarize, archive
  - Task Runner: actionable requests + checklists
  - Context Injector: minimal, targeted context

- Tier 2 — Knowledge & Patterns
  - Retriever: FTS/semantic lookup from brain
  - Pattern Synthesizer: normalize/aggregate signals
  - Evidence Tracker: provenance + confidence

- Tier 3 — Content & Ops
  - Documentation Agent: generate docs with incremental creation
  - Migration Agent: scaffold/plan migrations
  - Maintenance Agent: schedule DB maintenance
  - Self-Review Agent: run health checks + auto-fixes (safe)

---

## 🔌 Hooked Execution Model

CORTEX 2.0 runs a plugin-first flow. Agents trigger hooks at well-defined points.

Hook overview:
- on_startup: boot-time checks (paths, config, env)
- on_conversation_cycle: per-turn context, state save
- on_self_review: periodic health checks and reports
- on_db_maintenance: optimize/retention when needed
- on_generate_doc: large doc creation (incremental)
- on_before_write / on_after_write: integrity + boundary checks

```python
# src/router.py (conceptual)
def run_hook(hook: HookPoint, context: dict) -> dict:
    results = []
    for plugin in registry.plugins_for(hook):
        res = plugin.execute(context)
        results.append(res)
    return merge_hook_results(results)

# Example conversation cycle
context = session_manager.load_context(session_id)
run_hook(HookPoint.ON_CONVERSATION_CYCLE, context)

# Trigger self-review daily or on-demand
if should_self_review():
    report = run_hook(HookPoint.ON_SELF_REVIEW, {"auto_fix": True})

# Trigger DB maintenance if schedule says so
plan = run_hook(HookPoint.ON_DB_MAINTENANCE, {"operation": "auto"})
```

---

## 🧭 Core Conversation Workflow

```
User Message → Tier1.ConversationManager
  1) Load session + last N turns (Tier 1 DB)
  2) Inject targeted context (Tier 2 retrieval)
  3) Validate boundaries (Tier 0 rules)
  4) Plan: actions + sub-tasks
  5) Execute actions via agents/plugins
  6) Persist: state, deltas, decisions
  7) Check capacity: FIFO + archival if near limit
```

Key rules:
- Minimal context injection—only what’s necessary for the turn
- Persist actionable state + decisions for resumability
- Never bypass the knowledge boundary guard

---

## 🧩 Documentation Workflow (Incremental Creation)

```
Tier3.DocumentationAgent
  1) Produce high-level outline
  2) Generate content section-by-section
  3) Use IncrementalCreationEngine (chunks)
  4) Validate each chunk + full doc
  5) Update index/status
```

```python
# src/tier3/documentation_agent.py (conceptual)
from utils.incremental_creation import create_large_file, FileValidator

class DocumentationAgent:
    def create_design_doc(self, filename: str, content: str) -> bool:
        file_path = self.paths.resolve(f"cortex-brain/cortex-2.0-design/{filename}")
        return create_large_file(file_path, content, file_type="markdown")
```

---

## 🛡️ Self-Review + Maintenance in the Loop

- Daily: run self-review with safe auto-fixes
- Weekly: run DB optimization (VACUUM/ANALYZE/REINDEX)
- On-demand: enforce retention when Tier 1 nears capacity

```python
# src/workflows/ops.py (conceptual)
def nightly_ops():
    run_hook(HookPoint.ON_SELF_REVIEW, {"auto_fix": True})
    run_hook(HookPoint.ON_DB_MAINTENANCE, {"operation": "auto"})
```

---

## 🔄 Task Execution Contract

- Inputs
  - session_id (str)
  - user_intent (str)
  - context_hints (list[str])
- Outputs
  - actions_taken (list[dict])
  - artifacts (paths, ids)
  - next_steps (list[str])
  - state_delta (dict)
- Error Modes
  - boundary_violation → abort + log + guidance
  - missing_context → targeted retrieval
  - write_conflict → retry with backoff
  - length_limit → incremental creation fallback

---

## 🧱 Knowledge Boundary Guardrails

- Never read/write outside allowed roots (PathResolver)
- Enforce core vs project separation
- Validate plugin operations through guard hooks
- Record provenance for any cross-tier movement

```python
# Pseudocode
if not boundary_guard.can_write(target_path):
    raise BoundaryViolation("Write outside allowed scope")
```

---

## 📐 Workflow Diagrams

Conversation cycle (simplified):

```
┌─────────────┐  message  ┌──────────────────────┐
│   User      ├──────────▶│ ConversationManager  │
└─────┬───────┘           └──────────┬───────────┘
      │                              │
      │context                       │actions
      ▼                              ▼
┌─────────────┐                ┌───────────────┐
│ Retriever   │◀──────────────▶│ Plugin Hooks  │
└─────────────┘                └──────┬────────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │ Persist/Log  │
                               └──────────────┘
```

---

## 🧪 Testing Workflows (Happy + Edge Cases)

- Happy path
  - Resume conversation with injected context; produce artifact; persist
- Edge cases
  - Tier1 near-capacity → archive oldest; continue
  - Length limit → incremental creation path
  - Rule violation → abort write + suggest fix
  - DB fragmentation high → maintenance scheduled before heavy read

---

## 📊 Metrics & Telemetry

- Per-turn latency breakdown (retrieve/plan/execute/persist)
- Retrieval hit rate + confidence distribution
- Incremental creation: chunks, retries, validation warnings
- Maintenance: reclaimed MB, speedup X, schedule adherence
- Self-review: overall score, issue counts, auto-fixes

---

## ⚙️ Minimal Config

```json
{
  "workflows": {
    "conversation": {
      "context_injection": "targeted",
      "max_tier1_conversations": 20,
      "auto_archive_days": 30
    },
    "documentation": {
      "incremental_creation": true,
      "validator": "markdown"
    },
    "ops": {
      "self_review_daily": true,
      "db_maintenance_weekly": true
    }
  }
}
```

---

## ✅ Outcomes

- Deterministic, inspectable execution through hooks
- Resilient long-output generation via incremental creation
- Proactive health with self-review + maintenance
- Strong safety with boundary + path guards
- Clear contracts for inputs/outputs and errors

---

**Next:** 11-database-schema-updates.md (New tables to support 2.0 features)
