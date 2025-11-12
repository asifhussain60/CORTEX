# CORTEX 2.0 API Changes & Interfaces

**Document:** 15-api-changes.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose
Describe the public-facing internal APIs (agent interfaces, plugin contracts, service abstractions) updated for CORTEX 2.0 so implementers can migrate custom logic while preserving stability.

---

## 🧱 Design Principles
- Backwards-tolerant: existing 1.0 agents can run with shims
- Explicit contracts: typed dataclasses / pydantic (future) for structured data
- Plugin-first: extensibility through hook points vs ad-hoc calls
- Observable: execution surfaces produce telemetry (hook executions, boundary events)
- Safe by default: write operations validated through boundary guard

---

## 📦 Core Data Models (Python Dataclasses)
```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ConversationStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"

@dataclass
class ConversationTurn:
    session_id: str
    turn_number: int
    user_input: str
    agent_output: str
    actions: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class ActionRecord:
    action_type: str                     # retrieval|generation|write|maintenance|self_review
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True

@dataclass
class ConversationState:
    session_id: str
    status: ConversationStatus
    open_tasks: List[str]
    completed_tasks: List[str]
    last_updated: datetime
    pending_actions: List[ActionRecord] = field(default_factory=list)

@dataclass
class PluginExecutionResult:
    success: bool
    payload: Dict[str, Any]
    issues: List[str] = field(default_factory=list)

@dataclass
class MaintenancePlanItem:
    operation: str                       # vacuum|analyze|reindex|enforce_retention|archival
    reason: str
    priority: str                        # high|medium|low

@dataclass
class MaintenanceSchedule:
    tier: str
    items: List[MaintenancePlanItem]
```

---

## 🔌 Plugin Interface (Updated)

Old 1.0 (conceptual):
```python
class LegacyPlugin:
    def run(self, context: dict) -> dict:
        ...
```

New 2.0:
```python
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class PluginMetadata:
    plugin_id: str
    name: str
    version: str
    category: str
    priority: int
    description: str
    dependencies: list
    hooks: list

class BasePlugin:
    def _get_metadata(self) -> PluginMetadata:
        raise NotImplementedError

    def initialize(self) -> bool:
        return True

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def shutdown(self) -> None:
        pass
```

Hook contract:
- Input context keys vary by hook (e.g., `auto_fix` for self-review)
- Always returns `{ "success": bool, ... }`
- Additional keys documented per hook below

---

## 🪝 Hook Points & Contracts

| Hook | Purpose | Input Context | Return Payload Keys |
|------|---------|---------------|---------------------|
| `ON_STARTUP` | Initialize systems | config, path_resolver | success, warnings |
| `ON_CONVERSATION_CYCLE` | Per turn processing | session_id, turn, user_input | success, actions, state_delta |
| `ON_SELF_REVIEW` | Health check | auto_fix (bool) | success, report, status, score, issues |
| `ON_DB_MAINTENANCE` | Maintenance planning/run | operation, tier | success, schedule|metrics|archival |
| `ON_GENERATE_DOC` | Large doc creation | filename, content | success, path, chunks_written |
| `ON_BEFORE_WRITE` | Pre-write validation | path, intent | success, allowed, reason |
| `ON_AFTER_WRITE` | Post-write logging | path, bytes | success, provenance_id |

Return semantics:
- Failure triggers fallback or abort depending on severity
- Plugin errors logged to `plugin_hook_executions`

---

## 🧠 Agent Interfaces

### ConversationAgent
```python
class ConversationAgent:
    def __init__(self, repositories, path_resolver, plugins):
        self.repos = repositories
        self.paths = path_resolver
        self.plugins = plugins

    def process_turn(self, session_id: str, user_input: str) -> ConversationTurn:
        # 1. Load state
        state = self._load_state(session_id)
        # 2. Run context injection plugin(s)
        ctx = {"session_id": session_id, "user_input": user_input, "turn": state}
        self.plugins.run_hook("ON_CONVERSATION_CYCLE", ctx)
        # 3. Generate response (LLM or rule engine)
        response = self._generate_response(state, user_input)
        # 4. Persist turn
        turn = self._save_turn(session_id, user_input, response)
        # 5. Return structured turn
        return turn
```

### DocumentationAgent
Adds incremental creation support (see doc 09).

### MaintenanceAgent
Coordinates scheduling + immediate execution.

### SelfReviewAgent
Thin wrapper around SelfReviewEngine plugin hook.

---

## 🛡️ Boundary Guard API
```python
class BoundaryGuard:
    def can_write(self, path: str, intent: str) -> (bool, str):  # returns allowed, reason
        ...

    def record_event(self, path: str, allowed: bool, reason: str, rule_reference: str, plugin_id: str = None):
        ...
```
Usage pattern:
```python
allowed, reason = boundary_guard.can_write(target_path, "generate_document")
if not allowed:
    boundary_guard.record_event(target_path, False, reason, "RULE#22")
    raise PermissionError(f"Write denied: {reason}")
```

---

## 🧪 Error Handling Changes

| Area | 1.0 Behavior | 2.0 Behavior |
|------|--------------|--------------|
| Plugin failure | Silent or generic log | Logged with hook, duration, stack snippet |
| Write denial | Generic exception | Structured PermissionError with rule reference |
| Maintenance failure | Partial output | Rollback + metrics row with status=failed |
| Self-review failure | Aborts silently | Report row with critical issue + retry guidance |
| Incremental creation failure | Partial file left | Progress file saved + resumable |

---

## 🔄 Versioning Strategy

- Internal API version constant: `API_VERSION = "2.0-alpha"`
- Provide `get_api_version()` helper for plugins
- Deprecation warnings emitted when 1.0 method signatures detected
- Removal timeline documented (e.g., after stable release + 2 minor versions)

---

## ⛳ Deprecations

| Deprecated | Replacement | Removal Target |
|------------|------------|----------------|
| `LegacyPlugin.run(context)` | `BasePlugin.execute(context)` | 2.1.0 |
| Direct DB access in agents | Repository abstractions | 2.0 stable |
| Ad-hoc path joins | PathResolver methods | 2.0 stable |
| Monolithic document writes | IncrementalCreationEngine | 2.0 stable |

---

## 📊 Telemetry Surfaces
- `plugin_hook_executions` (success, failure, duration_ms)
- `boundary_events` (allow/deny counts)
- `maintenance_runs` (space reclaimed, speedup)
- `health_reports` (trend per day)

Agents consume telemetry for adaptive scheduling (future 2.1+ capability).

---

## 🧪 Example: Writing a New Plugin
```python
# src/plugins/example_cleanup_plugin.py
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint

class Plugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="example_cleanup_plugin",
            name="Example Cleanup",
            version="1.0.0",
            category=PluginCategory.UTILITY,
            priority=PluginPriority.MEDIUM,
            description="Removes obsolete temp files",
            dependencies=[],
            hooks=[HookPoint.ON_STARTUP.value, HookPoint.ON_DB_MAINTENANCE.value]
        )

    def execute(self, context):
        if context.get("hook") == HookPoint.ON_STARTUP.value:
            return {"success": True, "removed": 0}
        if context.get("hook") == HookPoint.ON_DB_MAINTENANCE.value:
            # Provided maintenance schedule context
            return {"success": True, "schedule_adjustments": []}
        return {"success": True}
```

---

## ✅ Migration Steps for Custom Integrations
1. Wrap legacy plugins with adapter class implementing `BasePlugin`.
2. Replace direct DB calls with repository methods (create thin repo layer now if absent).
3. Update write operations to call `boundary_guard.can_write()` first.
4. Adopt new dataclasses for structured state passing.
5. Surface errors using structured exceptions (PermissionError, RuntimeError with codes).

---

## 🧪 Validation Checklist
```
[ ] All new hooks produce expected payload keys
[ ] Legacy plugins adapted or disabled
[ ] Boundary events recorded for denied writes
[ ] Self-review and maintenance plugins visible via telemetry tables
[ ] API_VERSION exposed and matches docs
```

---

**Next:** 16-plugin-examples.md (Sample plugins for cleanup, validation, organization)
