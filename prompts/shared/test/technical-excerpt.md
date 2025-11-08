# CORTEX Technical Excerpt - Architecture & API Reference

**Purpose:** Technical specifications, API details, and architecture reference  
**Audience:** Developers, technical users, system architects  
**Source:** Extracted from full CORTEX documentation

---

## 🏗️ System Architecture

### Tier Architecture

CORTEX uses a 5-tier memory architecture inspired by human cognition:

```
TIER 0: Instinct (Core Rules)
  ├─ Immutable principles (TDD, SOLID, DoR/DoD)
  └─ Stored: governance/rules.md

TIER 1: Working Memory (Last 20 conversations)
  ├─ Conversations (FIFO queue)
  ├─ Messages (last 10 per conversation)
  ├─ Entities (files, classes, methods)
  └─ Stored: cortex-brain/tier1/*.db (SQLite)

TIER 2: Long-Term Memory (Knowledge Graph)
  ├─ Intent patterns
  ├─ File relationships
  ├─ Workflow templates
  ├─ Validation insights
  └─ Stored: cortex-brain/tier2/*.db (SQLite + YAML)

TIER 3: Context Intelligence (Git Analysis)
  ├─ Commit velocity
  ├─ File hotspots
  ├─ Code health metrics
  └─ Stored: cortex-brain/tier3/*.db (SQLite)

TIER 4: Real-Time Events (Session Activity)
  ├─ Agent actions
  ├─ User commands
  ├─ System events
  └─ Stored: logs/*.jsonl (JSON Lines)
```

---

## 📊 Tier 1 API (Working Memory)

### Core Classes

#### WorkingMemory
```python
from src.tiers.tier1.working_memory import WorkingMemory

# Initialize
memory = WorkingMemory()

# Store conversation
conversation_id = memory.store_conversation(
    user_message="Add a purple button",
    assistant_response="I'll create that for you",
    intent="EXECUTE",
    context={
        "files_modified": ["HostControlPanel.razor"],
        "agent": "code-executor"
    }
)

# Retrieve recent conversations
recent = memory.get_recent_conversations(limit=5)

# Search conversations
results = memory.search_conversations(
    query="purple button",
    filters={"intent": "EXECUTE"}
)

# Get conversation continuity
context = memory.get_conversation_context(conversation_id)
# Returns: Previous messages, related entities, file references
```

#### FIFO Queue Management
```python
# Enable FIFO (delete oldest when limit reached)
memory.configure_fifo(
    max_conversations=20,
    enabled=True
)

# Check queue status
status = memory.get_queue_status()
# Returns: {
#   "current": 18,
#   "max": 20,
#   "next_to_delete": "conv_123" (if at limit)
# }

# Manually trigger cleanup
deleted_count = memory.cleanup_old_conversations()
```

---

## 🧩 Tier 2 API (Knowledge Graph)

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
        "files": ["InvoiceService.cs", "ExportController.cs"],
        "steps": ["validate", "format", "download"],
        "success_rate": 0.94
    },
    scope="application",  # or "cortex" for core patterns
    namespaces=["KSESSIONS"]  # project-specific
)

# Search patterns
patterns = kg.search_patterns(
    query="export",
    filters={
        "pattern_type": "workflow",
        "scope": "application"
    },
    min_confidence=0.7
)

# Get file relationships
relationships = kg.get_file_relationships(
    file_path="HostControlPanel.razor"
)
# Returns: Files that often change together with co-modification rates
```

#### Pattern Decay
```python
# Patterns decay over time if not used
kg.configure_decay(
    enabled=True,
    decay_rate=0.05,  # 5% confidence drop per 30 days unused
    min_confidence=0.3  # Delete below this threshold
)

# Manually trigger decay
decayed_count = kg.apply_decay()
```

---

## 🎯 Tier 3 API (Context Intelligence)

### Core Classes

#### ContextIntelligence
```python
from src.tiers.tier3.context_intelligence import ContextIntelligence

# Initialize
ci = ContextIntelligence()

# Analyze git activity
analysis = ci.analyze_git_activity(
    lookback_days=30,
    include_authors=True
)
# Returns: {
#   "commit_velocity": 42,  # commits/week
#   "file_hotspots": [
#       {"file": "HostControlPanel.razor", "churn_rate": 0.28}
#   ],
#   "authors": [...]
# }

# Get file stability
stability = ci.get_file_stability("HostControlPanel.razor")
# Returns: "stable" | "unstable" | "volatile"

# Get development insights
insights = ci.get_development_insights()
# Returns: {
#   "best_session_times": ["10am-12pm"],
#   "success_rate": 0.94,
#   "workflow_effectiveness": {
#       "test_first": 0.68  # 68% less rework
#   }
# }
```

---

## 🤖 Agent System Architecture

### Intent Router
```python
from src.agents.intent_router import IntentRouter

router = IntentRouter()

# Parse user request
result = router.parse(
    user_message="Add a purple button to the host panel"
)
# Returns: {
#   "intent": "EXECUTE",
#   "agent": "code-executor",
#   "confidence": 0.92,
#   "entities": {
#       "component": "button",
#       "color": "purple",
#       "location": "host panel"
#   }
# }
```

### Available Intents
| Intent | Agent | Trigger Words |
|--------|-------|---------------|
| **PLAN** | work-planner | "create plan", "design", "architecture" |
| **EXECUTE** | code-executor | "add", "create", "implement", "build" |
| **TEST** | test-generator | "test", "verify", "validate" |
| **FIX** | error-corrector | "fix", "bug", "error", "broken" |
| **VALIDATE** | health-validator | "check", "validate", "health" |
| **ANALYZE** | screenshot-analyzer | "analyze image", "what's in this" |
| **PROTECT** | brain-protector | "delete", "modify tier0", "change rules" |

---

## 🔌 Plugin System

### Creating a Plugin

```python
from src.plugins.base_plugin import BasePlugin

class MyCustomPlugin(BasePlugin):
    """Example custom plugin"""
    
    def __init__(self):
        super().__init__(
            name="my-custom-plugin",
            version="1.0.0",
            description="Does something useful"
        )
    
    def execute(self, context: dict) -> dict:
        """Main execution method"""
        # Your plugin logic here
        return {
            "success": True,
            "data": {...}
        }
    
    def validate(self, context: dict) -> bool:
        """Validate inputs before execution"""
        return "required_field" in context
```

### Registering a Plugin

```python
from src.core.plugin_manager import PluginManager

manager = PluginManager()

# Register plugin
manager.register_plugin(MyCustomPlugin())

# Execute plugin
result = manager.execute_plugin(
    "my-custom-plugin",
    context={"required_field": "value"}
)
```

---

## 📝 Configuration Reference

### cortex.config.json Structure

```json
{
  "machines": {
    "YOUR-PC-NAME": {
      "rootPath": "D:\\PROJECTS\\CORTEX",
      "brainPath": "D:\\PROJECTS\\CORTEX\\cortex-brain"
    }
  },
  "cortex": {
    "tier1": {
      "maxConversations": 20,
      "fifoEnabled": true,
      "messageRetention": 10
    },
    "tier2": {
      "patternDecay": {
        "enabled": true,
        "decayRate": 0.05,
        "minConfidence": 0.3
      },
      "fts5": {
        "enabled": true,
        "languages": ["en"]
      }
    },
    "tier3": {
      "gitAnalysis": {
        "enabled": true,
        "lookbackDays": 30,
        "includeAuthors": true
      }
    },
    "agents": {
      "intentRouter": {
        "confidenceThreshold": 0.7
      },
      "codeExecutor": {
        "tddEnforced": true,
        "maxFileSize": 500
      }
    }
  }
}
```

---

## 🧪 Testing Protocols

### Playwright Testing (PowerShell)

**CRITICAL: Always use element IDs for selectors**

```typescript
// ❌ WRONG - Fragile text-based selector
const button = page.locator('button:has-text("Start Session")');

// ✅ CORRECT - Robust ID-based selector
const button = page.locator('#sidebar-start-session-btn');
```

### Test Script Pattern

```powershell
# Standard test automation script pattern
param([switch]$KeepAppRunning)

# Step 1: Launch app with Start-Job
$appJob = Start-Job -ScriptBlock {
    Set-Location 'D:\PROJECTS\CORTEX'
    dotnet run
}

# Step 2: Wait for readiness (20s minimum)
Start-Sleep -Seconds 20

# Step 3: Run tests
try {
    Set-Location 'D:\PROJECTS\CORTEX'
    npx playwright test Tests/UI/my-test.spec.ts --headed
    $exitCode = $LASTEXITCODE
}
finally {
    # Step 4: Cleanup
    if (-not $KeepAppRunning) {
        Stop-Job -Job $appJob
        Remove-Job -Job $appJob
    }
}

exit $exitCode
```

---

## 🛡️ Rule System (Tier 0)

### Core Rules (Immutable)

| Rule | Description | Enforced By |
|------|-------------|-------------|
| **#1** | Definition of READY required | Right Brain |
| **#2** | Test-Driven Development (RED → GREEN → REFACTOR) | Left Brain |
| **#3** | Definition of DONE (zero errors/warnings) | Left Brain |
| **#11** | 30-minute conversation boundaries | WorkStateManager |
| **#22** | Brain Protection (challenge risky changes) | Brain Protector |
| **#23** | Incremental file creation (>100 lines) | All Agents |

---

## 📈 Performance Benchmarks

| Operation | Target | Actual |
|-----------|--------|--------|
| **Tier 1 Query** | <50ms | 18ms ⚡ |
| **Tier 2 Pattern Search** | <150ms | 92ms ⚡ |
| **Tier 3 Git Analysis** | <200ms | 156ms ⚡ |
| **Intent Routing** | <100ms | 45ms ⚡ |
| **Conversation Storage** | <30ms | 12ms ⚡ |

---

**Full Documentation:** See `#file:prompts/user/cortex.md` for complete CORTEX documentation  
**Related Modules:**
- Story: `#file:prompts/shared/test/story-excerpt.md`
- Setup Guide: `#file:prompts/shared/test/setup-excerpt.md`
