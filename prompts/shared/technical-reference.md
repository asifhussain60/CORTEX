# CORTEX Technical Reference - Architecture & API

**Purpose:** Complete technical specifications, API documentation, and architecture reference  
**Audience:** Developers, technical users, system architects, plugin developers  
**Version:** 2.0 (Full Module)  
**Status:** Production Ready

---

## 📐 Table of Contents

1. [System Architecture](#system-architecture)
2. [Tier 0 API (Instinct)](#tier-0-api-instinct)
3. [Tier 1 API (Working Memory)](#tier-1-api-working-memory)
4. [Tier 2 API (Knowledge Graph)](#tier-2-api-knowledge-graph)
5. [Tier 3 API (Context Intelligence)](#tier-3-api-context-intelligence)
6. [Agent System](#agent-system)
7. [Plugin Development](#plugin-development)
8. [Configuration Reference](#configuration-reference)
9. [Testing Protocols](#testing-protocols)
10. [Performance Benchmarks](#performance-benchmarks)

---

## 🏗️ System Architecture

### Overview

CORTEX implements a **five-tier cognitive architecture** inspired by human brain structure and neuroscience principles:

```
┌─────────────────────────────────────────────────┐
│  TIER 0: INSTINCT (Immutable Core Rules)       │
│  - TDD enforcement                              │
│  - Definition of Ready/Done                     │
│  - SOLID principles                             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 1: WORKING MEMORY (Last 20 Conversations)│
│  - Conversation history (FIFO queue)            │
│  - Message context (last 10 per conversation)   │
│  - Entity tracking (files, classes, methods)    │
│  Storage: SQLite + JSON Lines                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 2: LONG-TERM MEMORY (Knowledge Graph)    │
│  - Intent patterns                              │
│  - File relationships                           │
│  - Workflow templates                           │
│  - Validation insights                          │
│  Storage: SQLite + YAML                         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 3: CONTEXT INTELLIGENCE (Git Analysis)   │
│  - Commit velocity tracking                     │
│  - File hotspot identification                  │
│  - Code health metrics                          │
│  - Session productivity analytics               │
│  Storage: SQLite + JSON Lines                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 4: REAL-TIME EVENTS (Session Activity)   │
│  - Agent actions log                            │
│  - User commands                                │
│  - System events                                │
│  Storage: JSON Lines (logs/*.jsonl)             │
└─────────────────────────────────────────────────┘

         ┌───────────────────────────────┐
         │   CORPUS CALLOSUM             │
         │   (Hemisphere Coordination)   │
         │   - Message queue             │
         │   - State synchronization     │
         └───────────────────────────────┘

    LEFT HEMISPHERE          RIGHT HEMISPHERE
    (Tactical Execution)     (Strategic Planning)
    ├── Code Executor        ├── Intent Router
    ├── Test Generator       ├── Work Planner
    ├── Error Corrector      ├── Screenshot Analyzer
    ├── Health Validator     ├── Change Governor
    └── Commit Handler       └── Brain Protector
```

---

## 🔐 Tier 0 API (Instinct)

### Overview

Tier 0 contains **immutable core rules** that define CORTEX's fundamental behavior. These rules cannot be bypassed without explicit Brain Protector challenge.

### Governance Rules

**File:** `governance/rules.md`  
**Format:** Markdown (human-readable)  
**Enforcement:** Brain Protector agent

#### Core Rules

| Rule # | Name | Description | Enforced By |
|--------|------|-------------|-------------|
| **#1** | Definition of READY | Work must have clear requirements before starting | Right Brain (Planner) |
| **#2** | Test-Driven Development | RED → GREEN → REFACTOR cycle mandatory | Left Brain (Executor) |
| **#3** | Definition of DONE | Zero errors, zero warnings, all tests pass | Left Brain (Validator) |
| **#11** | 30-Minute Boundaries | Conversation sessions limited to 30 minutes | WorkStateManager |
| **#22** | Brain Protection | Challenge risky changes to CORTEX core | Brain Protector |
| **#23** | Incremental Creation | Large files (>100 lines) created incrementally | All Agents |

### Brain Protection Rules API

**File:** `cortex-brain/brain-protection-rules.yaml`  
**Format:** YAML (structured data)  
**API:** Python class-based

```python
from src.tier0.brain_protector import BrainProtector

# Initialize Brain Protector
protector = BrainProtector()

# Validate proposed change
result = protector.validate_change(
    intent="Modify tier0 rules",
    description="Add new governance rule",
    affected_files=["governance/rules.md"],
    scope="cortex"
)

# Result structure:
# {
#   "allowed": False,
#   "severity": "blocked",
#   "rule_triggered": "instinct_immutability",
#   "alternatives": [
#       "Create application-specific rule in your project",
#       "Propose governance change with justification",
#       "Use spike branch for experimentation"
#   ],
#   "evidence": "Intent: 'Modify tier0 rules'"
# }
```

### Protection Layers

1. **Instinct Immutability** - Core principles cannot be bypassed
2. **Critical Path Protection** - Tier 0 files protected from modification
3. **Application Separation** - Application code kept out of CORTEX core
4. **Brain State Protection** - Conversation history not committed to git
5. **Namespace Isolation** - Scope boundaries enforced
6. **Architectural Integrity** - Layered architecture maintained

---

## 📚 Tier 1 API (Working Memory)

### Overview

Tier 1 provides **short-term conversation memory** using a FIFO queue (last 20 conversations).

**Storage:** `cortex-brain/tier1/conversations.db` (SQLite)  
**Performance Target:** <50ms per query  
**Actual Performance:** 18ms average ⚡

### Core Classes

#### WorkingMemory

```python
from src.tiers.tier1.working_memory import WorkingMemory

# Initialize
memory = WorkingMemory()

# Store conversation
conversation_id = memory.store_conversation(
    user_message="Add a purple button to the control panel",
    assistant_response="I'll create that button with purple styling",
    intent="EXECUTE",
    context={
        "files_modified": ["HostControlPanel.razor"],
        "entities": ["button", "control panel", "purple"],
        "agent": "code-executor",
        "timestamp": "2025-11-08T10:30:00Z"
    }
)

# Returns: "conv_20251108_103000_a1b2c3"
```

#### Retrieve Conversations

```python
# Get recent conversations
recent = memory.get_recent_conversations(limit=5)

# Result structure:
# [
#   {
#     "conversation_id": "conv_20251108_103000_a1b2c3",
#     "user_message": "Add a purple button...",
#     "assistant_response": "I'll create that...",
#     "intent": "EXECUTE",
#     "timestamp": "2025-11-08T10:30:00Z",
#     "context": {...}
#   },
#   ...
# ]
```

#### Search Conversations

```python
# Search by query
results = memory.search_conversations(
    query="purple button",
    filters={
        "intent": "EXECUTE",
        "date_range": ("2025-11-01", "2025-11-08")
    },
    limit=10
)

# Search by entity
button_convos = memory.search_by_entity(
    entity_type="component",
    entity_value="button"
)
```

#### Conversation Context

```python
# Get context for continuity
context = memory.get_conversation_context(conversation_id)

# Returns:
# {
#   "current_conversation": {...},
#   "previous_messages": [last 10 messages],
#   "related_entities": ["button", "panel", "purple"],
#   "file_references": ["HostControlPanel.razor"],
#   "related_conversations": [similar past conversations]
# }
```

#### FIFO Queue Management

```python
# Configure FIFO queue
memory.configure_fifo(
    max_conversations=20,
    enabled=True,
    auto_cleanup=True
)

# Check queue status
status = memory.get_queue_status()
# Returns:
# {
#   "current_count": 18,
#   "max_capacity": 20,
#   "next_to_delete": "conv_20251001_140000_x9y8z7" (if at limit),
#   "fifo_enabled": True
# }

# Manually trigger cleanup (removes oldest)
deleted_count = memory.cleanup_old_conversations()
# Returns: 1 (number of conversations deleted)
```

#### Entity Tracking

```python
# Track entities in conversation
memory.track_entity(
    conversation_id="conv_20251108_103000_a1b2c3",
    entity_type="file",
    entity_value="HostControlPanel.razor",
    context="Modified to add button"
)

# Query entities
entities = memory.get_entities(
    conversation_id="conv_20251108_103000_a1b2c3"
)
```

### Database Schema

```sql
-- Conversations table
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    user_message TEXT NOT NULL,
    assistant_response TEXT,
    intent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    context_json TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Messages table (last 10 per conversation)
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT,
    role TEXT, -- 'user' or 'assistant'
    content TEXT,
    sequence_num INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Entities table
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    conversation_id TEXT,
    entity_type TEXT, -- 'file', 'class', 'method', 'component'
    entity_value TEXT,
    context TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Indexes for performance
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence_num);
CREATE INDEX idx_entities_conversation ON entities(conversation_id);
CREATE INDEX idx_entities_type_value ON entities(entity_type, entity_value);
```

---

## 🧩 Tier 2 API (Knowledge Graph)

### Overview

Tier 2 provides **long-term memory** through pattern learning and relationship tracking.

**Storage:** `cortex-brain/tier2/knowledge-graph.db` (SQLite), `knowledge-graph.yaml` (exports)  
**Performance Target:** <150ms per search  
**Actual Performance:** 92ms average ⚡

### Core Classes

#### KnowledgeGraph

```python
from src.tiers.tier2.knowledge_graph import KnowledgeGraph

# Initialize
kg = KnowledgeGraph()

# Store pattern
pattern_id = kg.store_pattern(
    title="Invoice Export Workflow",
    pattern_type="workflow",
    confidence=0.85,
    context={
        "files": ["InvoiceService.cs", "ExportController.cs", "InvoiceExportTests.cs"],
        "steps": ["validate_data", "format_invoice", "generate_pdf", "download"],
        "success_rate": 0.94,
        "avg_duration_minutes": 45,
        "common_issues": ["missing data validation", "format edge cases"]
    },
    scope="application",  # or "cortex" for core patterns
    namespaces=["KSESSIONS", "accounting"]
)

# Returns: "pattern_invoice_export_workflow_a1b2"
```

#### Search Patterns

```python
# Search for similar patterns
patterns = kg.search_patterns(
    query="export feature",
    filters={
        "pattern_type": "workflow",
        "scope": "application",
        "min_confidence": 0.7
    },
    limit=5
)

# Result structure:
# [
#   {
#     "pattern_id": "pattern_invoice_export_workflow_a1b2",
#     "title": "Invoice Export Workflow",
#     "confidence": 0.85,
#     "match_score": 0.92,
#     "context": {...},
#     "last_used": "2025-11-08T10:00:00Z",
#     "usage_count": 12
#   },
#   ...
# ]
```

#### File Relationships

```python
# Track file co-modification
kg.track_relationship(
    file_a="HostControlPanel.razor",
    file_b="noor-canvas.css",
    relationship_type="co_modification",
    strength=0.75,  # 75% of the time they change together
    context="UI styling changes"
)

# Get related files
relationships = kg.get_file_relationships(
    file_path="HostControlPanel.razor",
    relationship_types=["co_modification", "dependency"],
    min_strength=0.5
)

# Returns:
# [
#   {
#     "related_file": "noor-canvas.css",
#     "relationship_type": "co_modification",
#     "strength": 0.75,
#     "co_modification_count": 42,
#     "context": "UI styling changes"
#   },
#   ...
# ]
```

#### Intent Pattern Learning

```python
# Learn intent patterns
kg.learn_intent_pattern(
    user_phrase="add a button",
    detected_intent="PLAN",
    confidence=0.88,
    context={
        "agent_routed": "work-planner",
        "workflow_created": True,
        "success": True
    }
)

# Query intent patterns
intent = kg.predict_intent(
    user_phrase="create a new export feature",
    context_hints=["feature", "export"]
)

# Returns:
# {
#   "predicted_intent": "PLAN",
#   "confidence": 0.91,
#   "matching_patterns": [
#       {"phrase": "add a button", "similarity": 0.78},
#       {"phrase": "create new component", "similarity": 0.82}
#   ],
#   "suggested_agent": "work-planner"
# }
```

#### Workflow Templates

```python
# Store workflow template
template_id = kg.store_workflow_template(
    name="feature_development_workflow",
    phases=[
        {
            "phase": 1,
            "name": "Planning",
            "tasks": ["Define requirements", "Create test scenarios"],
            "agent": "work-planner"
        },
        {
            "phase": 2,
            "name": "Implementation",
            "tasks": ["Write failing tests", "Implement feature"],
            "agent": "code-executor"
        },
        {
            "phase": 3,
            "name": "Validation",
            "tasks": ["Run tests", "Verify no errors/warnings"],
            "agent": "health-validator"
        }
    ],
    success_rate=0.94,
    avg_duration_hours=2.5
)

# Apply workflow template
workflow = kg.apply_workflow_template(
    template_name="feature_development_workflow",
    context={
        "feature_name": "User Authentication",
        "complexity": "medium"
    }
)
```

#### Pattern Decay

```python
# Configure pattern decay
kg.configure_decay(
    enabled=True,
    decay_rate=0.05,  # 5% confidence drop per 30 days unused
    min_confidence=0.3,  # Delete patterns below this threshold
    check_interval_days=7
)

# Manually trigger decay
decay_result = kg.apply_decay()

# Returns:
# {
#   "patterns_decayed": 12,
#   "patterns_pruned": 3,
#   "average_decay": 0.05,
#   "oldest_pattern_age_days": 180
# }

# Boost pattern confidence (when used successfully)
kg.boost_pattern(
    pattern_id="pattern_invoice_export_workflow_a1b2",
    boost_amount=0.05,
    context="Successfully applied to receipt export"
)
```

### Database Schema

```sql
-- Patterns table
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    pattern_type TEXT, -- 'workflow', 'intent', 'validation'
    confidence REAL DEFAULT 0.5,
    context_json TEXT,
    scope TEXT, -- 'cortex' or 'application'
    namespaces TEXT, -- JSON array of namespaces
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME,
    usage_count INTEGER DEFAULT 0
);

-- Relationships table
CREATE TABLE relationships (
    relationship_id TEXT PRIMARY KEY,
    file_a TEXT,
    file_b TEXT,
    relationship_type TEXT, -- 'co_modification', 'dependency'
    strength REAL, -- 0.0 to 1.0
    co_modification_count INTEGER DEFAULT 0,
    context TEXT,
    last_observed DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Workflows table
CREATE TABLE workflows (
    workflow_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    phases_json TEXT, -- JSON array of phases
    success_rate REAL,
    avg_duration_hours REAL,
    usage_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 full-text search
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    pattern_id UNINDEXED,
    title,
    context_json,
    content='patterns',
    content_rowid='rowid'
);
```

---

## 📊 Tier 3 API (Context Intelligence)

### Overview

Tier 3 provides **development context analytics** through git analysis and session tracking.

**Storage:** `cortex-brain/tier3/context-intelligence.db` (SQLite), `git-analysis.jsonl`  
**Performance Target:** <200ms per analysis  
**Actual Performance:** 156ms average ⚡

### Core Classes

#### ContextIntelligence

```python
from src.tiers.tier3.context_intelligence import ContextIntelligence

# Initialize
ci = ContextIntelligence()

# Analyze git activity
analysis = ci.analyze_git_activity(
    lookback_days=30,
    include_authors=True,
    include_hotspots=True
)

# Returns:
# {
#   "commit_velocity": {
#       "total_commits": 1237,
#       "commits_per_week": 42,
#       "trend": "increasing"  # or "stable", "decreasing"
#   },
#   "file_hotspots": [
#       {
#           "file": "HostControlPanel.razor",
#           "churn_rate": 0.28,  # 28% of commits touch this file
#           "change_count": 67,
#           "stability": "unstable"  # or "stable", "volatile"
#       }
#   ],
#   "authors": [
#       {
#           "name": "John Doe",
#           "commit_count": 423,
#           "files_touched": 156,
#           "expertise_areas": ["UI", "authentication"]
#       }
#   ],
#   "health_score": 0.87  # 87% project health
# }
```

#### File Stability Classification

```python
# Get file stability
stability = ci.get_file_stability("HostControlPanel.razor")

# Returns: "stable" | "unstable" | "volatile"
# - stable: <10% churn rate
# - unstable: 10-30% churn rate (needs attention)
# - volatile: >30% churn rate (high risk)

# Get stability details
details = ci.get_file_stability_details("HostControlPanel.razor")

# Returns:
# {
#   "classification": "unstable",
#   "churn_rate": 0.28,
#   "change_count": 67,
#   "last_changed": "2025-11-08T14:30:00Z",
#   "average_change_size": 45,  # lines
#   "recommendations": [
#       "Add extra testing before changes",
#       "Consider refactoring to reduce complexity",
#       "Break into smaller, more stable components"
#   ]
# }
```

#### Session Analytics

```python
# Get development insights
insights = ci.get_development_insights()

# Returns:
# {
#   "productivity_patterns": {
#       "best_session_times": ["10:00-12:00"],
#       "avg_success_rate_by_time": {
#           "10:00-12:00": 0.94,
#           "14:00-16:00": 0.81
#       },
#       "optimal_session_duration_minutes": 45
#   },
#   "workflow_effectiveness": {
#       "test_first_success_rate": 0.89,
#       "test_last_success_rate": 0.62,
#       "rework_reduction": 0.68  # 68% less rework with TDD
#   },
#   "intent_distribution": {
#       "PLAN": 0.35,
#       "EXECUTE": 0.45,
#       "TEST": 0.15,
#       "VALIDATE": 0.05
#   }
# }
```

#### Proactive Warnings

```python
# Get proactive warnings for a file
warnings = ci.get_file_warnings("HostControlPanel.razor")

# Returns:
# [
#   {
#       "type": "hotspot_alert",
#       "severity": "warning",
#       "message": "This file is a hotspot (28% churn rate)",
#       "recommendations": [
#           "Add extra testing before changes",
#           "Consider smaller, incremental modifications"
#       ]
#   },
#   {
#       "type": "complexity_alert",
#       "severity": "info",
#       "message": "File has grown to 450 lines (consider refactoring)",
#       "recommendations": [
#           "Extract components into separate files",
#           "Apply Single Responsibility Principle"
#       ]
#   }
# ]

# Get session timing recommendations
timing = ci.get_optimal_session_timing()

# Returns:
# {
#   "current_time": "14:30",
#   "current_success_rate": 0.81,
#   "optimal_times": ["10:00-12:00"],
#   "optimal_success_rate": 0.94,
#   "recommendation": "Consider scheduling complex work for 10am-12pm"
# }
```

#### Code Health Metrics

```python
# Track code health over time
ci.track_code_health(
    test_coverage=0.76,
    build_success_rate=0.97,
    error_count=0,
    warning_count=2,
    timestamp="2025-11-08T15:00:00Z"
)

# Get health trends
trends = ci.get_health_trends(days=30)

# Returns:
# {
#   "test_coverage_trend": {
#       "start": 0.72,
#       "end": 0.76,
#       "change": +0.04,
#       "direction": "improving"
#   },
#   "build_success_trend": {
#       "average": 0.95,
#       "recent": 0.97,
#       "direction": "stable"
#   },
#   "overall_health": "excellent"  # or "good", "fair", "poor"
# }
```

### Database Schema

```sql
-- Git commits table
CREATE TABLE git_commits (
    commit_hash TEXT PRIMARY KEY,
    author TEXT,
    timestamp DATETIME,
    message TEXT,
    files_changed INTEGER,
    lines_added INTEGER,
    lines_deleted INTEGER,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- File metrics table
CREATE TABLE file_metrics (
    file_path TEXT PRIMARY KEY,
    change_count INTEGER DEFAULT 0,
    churn_rate REAL,
    stability TEXT, -- 'stable', 'unstable', 'volatile'
    last_changed DATETIME,
    avg_change_size INTEGER,
    total_lines INTEGER,
    last_analyzed DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Session analytics table
CREATE TABLE session_analytics (
    session_id TEXT PRIMARY KEY,
    start_time DATETIME,
    end_time DATETIME,
    duration_minutes INTEGER,
    intent TEXT,
    success BOOLEAN,
    productivity_score REAL,
    files_modified TEXT, -- JSON array
    tests_passed INTEGER,
    tests_failed INTEGER
);

-- Code health tracking
CREATE TABLE code_health (
    recorded_at DATETIME PRIMARY KEY,
    test_coverage REAL,
    build_success_rate REAL,
    error_count INTEGER,
    warning_count INTEGER,
    overall_health_score REAL
);
```

---

## 🤖 Agent System

### Intent Router

**Location:** `src/agents/intent_router.py`  
**Purpose:** Parse natural language and route to appropriate agent

```python
from src.agents.intent_router import IntentRouter

router = IntentRouter()

# Parse user request
result = router.parse(
    user_message="Add a purple button to the host panel",
    context_hints={"current_file": "HostControlPanel.razor"}
)

# Returns:
# {
#   "intent": "EXECUTE",
#   "confidence": 0.92,
#   "agent": "code-executor",
#   "entities": {
#       "component": "button",
#       "color": "purple",
#       "location": "host panel"
#   },
#   "suggested_workflow": "ui_component_creation",
#   "estimated_complexity": "low"
# }
```

### Intent Types

| Intent | Agent | Trigger Words | Confidence Threshold |
|--------|-------|---------------|---------------------|
| **PLAN** | work-planner | "create plan", "design", "architecture", "how should" | 0.7 |
| **EXECUTE** | code-executor | "add", "create", "implement", "build", "modify" | 0.7 |
| **TEST** | test-generator | "test", "verify", "validate", "check behavior" | 0.7 |
| **FIX** | error-corrector | "fix", "bug", "error", "broken", "not working" | 0.7 |
| **VALIDATE** | health-validator | "check health", "validate system", "run tests" | 0.7 |
| **ANALYZE** | screenshot-analyzer | "analyze image", "what's in this", "screenshot" | 0.7 |
| **PROTECT** | brain-protector | "modify tier0", "change rules", "delete brain" | 0.9 |
| **CONTINUE** | (resume previous) | "continue", "next", "keep going" | 0.8 |
| **STATUS** | (system check) | "status", "health", "how is" | 0.7 |

### Agent Coordination

```python
from src.agents.agent_coordinator import AgentCoordinator

coordinator = AgentCoordinator()

# Execute multi-agent workflow
result = coordinator.execute_workflow(
    workflow_name="feature_development",
    context={
        "feature": "User Authentication",
        "complexity": "medium"
    }
)

# Workflow executes:
# 1. Right Brain (Planner) creates strategy
# 2. Corpus Callosum delivers tasks
# 3. Left Brain (Executor) implements with TDD
# 4. Left Brain (Validator) verifies health
# 5. Right Brain updates knowledge graph
```

---

## 🔌 Plugin Development

### Creating a Custom Plugin

```python
from src.plugins.base_plugin import BasePlugin
from typing import Dict, Any

class MyCustomPlugin(BasePlugin):
    """Example custom plugin for CORTEX"""
    
    def __init__(self):
        super().__init__(
            name="my-custom-plugin",
            version="1.0.0",
            description="Does something useful",
            author="Your Name"
        )
    
    def validate(self, context: Dict[str, Any]) -> bool:
        """Validate inputs before execution"""
        required_fields = ["input_data", "options"]
        return all(field in context for field in required_fields)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic"""
        input_data = context["input_data"]
        options = context["options"]
        
        # Your plugin logic here
        result = self.process_data(input_data, options)
        
        return {
            "success": True,
            "data": result,
            "metadata": {
                "processed_items": len(input_data),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def process_data(self, data, options):
        """Helper method"""
        # Implementation here
        pass
    
    def cleanup(self):
        """Optional cleanup after execution"""
        pass
```

### Registering a Plugin

```python
from src.core.plugin_manager import PluginManager

manager = PluginManager()

# Register plugin
manager.register_plugin(MyCustomPlugin())

# Execute plugin
result = manager.execute_plugin(
    plugin_name="my-custom-plugin",
    context={
        "input_data": [...],
        "options": {...}
    }
)

# Returns:
# {
#   "success": True,
#   "data": {...},
#   "metadata": {...}
# }
```

### Plugin Hooks

```python
class MyPlugin(BasePlugin):
    """Plugin with lifecycle hooks"""
    
    def on_before_execute(self, context):
        """Called before main execution"""
        print(f"Starting {self.name}")
    
    def on_after_execute(self, result):
        """Called after execution"""
        print(f"Completed: {result['success']}")
    
    def on_error(self, error):
        """Called if execution fails"""
        print(f"Error: {error}")
        # Log to Tier 4
    
    def on_validate_failed(self, context):
        """Called if validation fails"""
        print("Validation failed")
```

---

## ⚙️ Configuration Reference

See full configuration details: `#file:prompts/shared/configuration-reference.md`

---

## 🧪 Testing Protocols

### Playwright Testing (UI Automation)

**CRITICAL: Always use element IDs for selectors**

```typescript
// ❌ WRONG - Fragile text-based selector
const button = page.locator('button:has-text("Start Session")');

// ✅ CORRECT - Robust ID-based selector
const button = page.locator('#sidebar-start-session-btn');
```

### Test Automation Script Pattern

```powershell
# Standard PowerShell test automation pattern
param([switch]$KeepAppRunning)

# Step 1: Launch application with Start-Job
$appJob = Start-Job -ScriptBlock {
    Set-Location 'D:\PROJECTS\CORTEX'
    dotnet run --project MyApp.csproj
}

# Step 2: Wait for application readiness (minimum 20 seconds)
Start-Sleep -Seconds 20

# Step 3: Run Playwright tests
try {
    Set-Location 'D:\PROJECTS\CORTEX'
    npx playwright test Tests/UI/my-test.spec.ts --headed
    $exitCode = $LASTEXITCODE
}
finally {
    # Step 4: Cleanup (unless --KeepAppRunning flag set)
    if (-not $KeepAppRunning) {
        Stop-Job -Job $appJob
        Remove-Job -Job $appJob
    }
}

exit $exitCode
```

### Python Unit Testing

```python
import pytest
from src.tiers.tier1.working_memory import WorkingMemory

def test_conversation_storage():
    """Test Tier 1 conversation storage"""
    memory = WorkingMemory()
    
    # Store conversation
    conv_id = memory.store_conversation(
        user_message="Test message",
        assistant_response="Test response",
        intent="TEST"
    )
    
    assert conv_id is not None
    assert conv_id.startswith("conv_")
    
    # Retrieve conversation
    conv = memory.get_conversation(conv_id)
    assert conv["user_message"] == "Test message"
    assert conv["intent"] == "TEST"
```

---

## 📈 Performance Benchmarks

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| **Tier 1: Store Conversation** | <30ms | 12ms | ⚡ Excellent |
| **Tier 1: Query Recent** | <50ms | 18ms | ⚡ Excellent |
| **Tier 1: Search** | <100ms | 45ms | ⚡ Excellent |
| **Tier 2: Pattern Search** | <150ms | 92ms | ⚡ Excellent |
| **Tier 2: Store Pattern** | <80ms | 56ms | ⚡ Excellent |
| **Tier 2: Relationship Query** | <120ms | 78ms | ⚡ Excellent |
| **Tier 3: Git Analysis** | <200ms | 156ms | ⚡ Excellent |
| **Tier 3: File Stability** | <100ms | 67ms | ⚡ Excellent |
| **Intent Routing** | <100ms | 45ms | ⚡ Excellent |
| **Brain Protector Check** | <150ms | 89ms | ⚡ Excellent |

**Test Environment:**
- CPU: Intel i7-11700K
- RAM: 32GB DDR4
- Storage: NVMe SSD
- Python: 3.11.5
- SQLite: 3.42.0

---

## 📞 API Support

**For more information:**
- **Configuration Details:** `#file:prompts/shared/configuration-reference.md`
- **Agent System:** `#file:prompts/shared/agents-guide.md`
- **Setup Guide:** `#file:prompts/shared/setup-guide.md`
- **Tracking Guide:** `#file:prompts/shared/tracking-guide.md`

---

**Version:** 2.0  
**Last Updated:** November 8, 2025  
**Phase:** 3.7 Complete - Full Modular Architecture  
**Performance:** All targets exceeded ⚡
