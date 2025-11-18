---
title: API Reference
description: Complete CORTEX API documentation
author: 
generated: true
version: ""
last_updated: 
---

# CORTEX API Reference

**Purpose:** Complete API documentation for all CORTEX components  
**Audience:** Developers, integrators, advanced users  
**Version:**   
**Last Updated:** 

---

## Tier 0: Brain Protection API

### BrainProtector

```python
from src.tier0.brain_protector import BrainProtector

protector = BrainProtector()
result = protector.validate_change(
    intent="Modify tier0 rules",
    affected_files=["governance/rules.md"],
    scope="cortex"
)
```

**Returns:**
```python
{
    "allowed": False,
    "severity": "blocked",
    "rule_triggered": "instinct_immutability",
    "alternatives": ["Create application-specific rule"],
    "evidence": "Intent: 'Modify tier0 rules'"
}
```

---

## Tier 1: Working Memory API

### WorkingMemory

**Store Conversation:**

```python
from src.tier1.working_memory import WorkingMemory

memory = WorkingMemory()
conv_id = memory.store_conversation(
    user_message="Add purple button",
    assistant_response="Creating button...",
    intent="EXECUTE",
    context={"files_modified": ["Panel.razor"]}
)
```

**Search Conversations:**

```python
results = memory.search_conversations(
    query="purple button",
    filters={"intent": "EXECUTE"},
    limit=10
)
```

**Get Context:**

```python
context = memory.get_conversation_context(conv_id)
```

---

## Tier 2: Knowledge Graph API

### KnowledgeGraph

**Store Pattern:**

```python
from src.tier2.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()
pattern_id = kg.store_pattern(
    title="Invoice Export Workflow",
    pattern_type="workflow",
    confidence=0.85,
    context={
        "files": ["InvoiceService.cs"],
        "steps": ["validate", "export"],
        "success_rate": 0.94
    }
)
```

**Search Patterns:**

```python
patterns = kg.search_patterns(
    query="export feature",
    filters={"pattern_type": "workflow"},
    limit=5
)
```

**Track Relationships:**

```python
kg.track_relationship(
    file_a="Panel.razor",
    file_b="styles.css",
    relationship_type="co_modification",
    strength=0.75
)
```

---

## Tier 3: Context Intelligence API

### ContextIntelligence

**Analyze Git Activity:**

```python
from src.tier3.context_intelligence import ContextIntelligence

ci = ContextIntelligence()
analysis = ci.analyze_git_activity(
    lookback_days=30,
    include_authors=True
)
```

**Get File Stability:**

```python
stability = ci.get_file_stability("Panel.razor")
# Returns: "stable" | "unstable" | "volatile"
```

**Get Warnings:**

```python
warnings = ci.get_file_warnings("Panel.razor")
```

---

## Agent System API

### IntentRouter

```python
from src.cortex_agents.intent_router import IntentRouter

router = IntentRouter()
result = router.parse(
    user_message="Add authentication",
    context_hints={"current_file": "Login.cs"}
)
```

**Returns:**
```python
{
    "intent": "EXECUTE",
    "confidence": 0.88,
    "agent": "code-executor",
    "entities": {"feature": "authentication"}
}
```

### WorkPlanner

```python
from src.cortex_agents.work_planner import WorkPlanner

planner = WorkPlanner()
plan = planner.create_plan(
    feature="User Authentication",
    complexity="medium"
)
```

---

## EPM Module APIs

### DocumentationGenerator

```python
from src.epm.doc_generator import DocumentationGenerator

generator = DocumentationGenerator()
result = generator.generate(dry_run=False)
```

### CleanupModule

```python
from src.epm.cleanup import CleanupModule

cleanup = CleanupModule()
result = cleanup.execute(profile="standard")
```

---

## Plugin System API

### BasePlugin

```python
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def execute(self, context):
        return {"success": True}
```

### PluginManager

```python
from src.core.plugin_manager import PluginManager

manager = PluginManager()
manager.register_plugin(MyPlugin())
result = manager.execute_plugin("my-plugin", context)
```

---

## Performance Benchmarks

| API Call | Target | Actual | Status |
|----------|--------|--------|--------|
| Tier 1 Store | <30ms | 12ms | ⚡ |
| Tier 1 Search | <50ms | 18ms | ⚡ |
| Tier 2 Search | <150ms | 92ms | ⚡ |
| Tier 3 Analysis | <200ms | 156ms | ⚡ |
| Intent Routing | <100ms | 45ms | ⚡ |

---

## Related Documentation

- **Configuration:** [Configuration Reference](config-reference.md)
- **Examples:** [Developer Guide](../guides/developer-guide.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 