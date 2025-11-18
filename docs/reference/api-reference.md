# CORTEX API Reference

## Overview

CORTEX provides a comprehensive API for interacting with its four-tier memory system, agent coordination, and plugin architecture.

## Core APIs

### Tier 0: Governance Rules API

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
```

### Tier 1: Working Memory API

```python
from src.tier1.working_memory import WorkingMemory

# Initialize
memory = WorkingMemory()

# Store conversation
conversation_id = memory.store_conversation(
    user_message="Add authentication",
    assistant_response="I'll implement JWT auth...",
    intent="EXECUTE"
)

# Retrieve conversations
recent = memory.get_recent_conversations(limit=5)
```

### Tier 2: Knowledge Graph API

```python
from src.tier2.knowledge_graph import KnowledgeGraph

# Initialize
kg = KnowledgeGraph()

# Store pattern
pattern_id = kg.store_pattern(
    title="Authentication Workflow",
    pattern_type="workflow",
    confidence=0.85
)

# Search patterns
patterns = kg.search_patterns(
    query="authentication",
    min_confidence=0.7
)
```

### Tier 3: Context Intelligence API

```python
from src.tier3.context_intelligence import ContextIntelligence

# Initialize
ci = ContextIntelligence()

# Analyze git activity
analysis = ci.analyze_git_activity(
    lookback_days=30,
    include_authors=True
)

# Get file stability
stability = ci.get_file_stability("auth.py")
```

## Agent System APIs

### Intent Router

```python
from src.agents.intent_router import IntentRouter

router = IntentRouter()

# Parse user request
result = router.parse(
    user_message="Add authentication to login page"
)
# Returns: {"intent": "EXECUTE", "confidence": 0.88, "agent": "code-executor"}
```

### Work Planner

```python
from src.agents.work_planner import WorkPlanner

planner = WorkPlanner()

# Create implementation plan
plan = planner.create_plan(
    feature_name="User Authentication",
    complexity="medium"
)
```

## Plugin System API

### Creating a Plugin

```python
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return ["analyze code", "review code"]
    
    def execute(self, request, context):
        # Plugin logic here
        return {"success": True, "data": results}
```

### Registering a Plugin

```python
from src.core.plugin_manager import PluginManager

manager = PluginManager()
manager.register_plugin(MyPlugin())

# Execute plugin
result = manager.execute_plugin(
    plugin_name="my-plugin",
    context={"input_data": [...]}
)
```

## Operations API

### Executing Operations

```python
from src.operations import execute_operation

# Execute operation
report = execute_operation('setup')
report = execute_operation('cleanup', profile='standard')
report = execute_operation('optimize codebase')
```

## Configuration API

### Loading Configuration

```python
from src.core.config_manager import ConfigManager

config = ConfigManager()
settings = config.get_settings()

# Update configuration
config.update_setting('tier1.maxConversations', 20)
```

## Testing APIs

### Running Tests

```python
from src.testing.test_runner import TestRunner

runner = TestRunner()

# Run test suite
results = runner.run_tests(
    test_files=["tests/tier1/*.py"],
    coverage=True
)
```

## Response Template API

### Using Response Templates

```python
from src.responses.template_engine import TemplateEngine

engine = TemplateEngine()

# Get template
template = engine.get_template("help_table")

# Render template
output = engine.render(template, context={"commands": [...]})
```

## Error Handling

All APIs use consistent error handling:

```python
try:
    result = memory.store_conversation(...)
except CortexError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.error_code}")
```

## Common Error Codes

| Code | Description |
|------|-------------|
| `TIER1_FULL` | Working memory at capacity |
| `PATTERN_NOT_FOUND` | Pattern doesn't exist in knowledge graph |
| `INVALID_INTENT` | Intent confidence too low |
| `RULE_VIOLATION` | Governance rule violated |

## See Also

- [Architecture Overview](../architecture/overview.md)
- [Plugin Development Guide](../plugins/development.md)
- [Configuration Reference](../reference/configuration.md)
- [Best Practices Guide](../guides/best-practices.md)
