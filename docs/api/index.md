# CORTEX API Reference

Complete API documentation for CORTEX cognitive framework.

## Architecture Overview

CORTEX uses a layered architecture:

```
┌─────────────────────────────────────────┐
│         CORTEX Entry Point              │
│    (Natural Language → Operations)      │
├─────────────────────────────────────────┤
│         10 Specialist Agents            │
│  (Left Brain: Tactical, Right: Strategic)│
├─────────────────────────────────────────┤
│          Plugin System                  │
│     (10 Extensible Plugins)             │
├─────────────────────────────────────────┤
│         4-Tier Brain System             │
│  (Governance → Memory → Knowledge)      │
└─────────────────────────────────────────┘
```

---

## Core APIs

### [Entry Point API](./entry-point.md)
Main interface for executing CORTEX operations.

**Module:** `src.cortex_entry`  
**Key Classes:** `CortexEntry`, `OperationExecutor`

### [Brain System API](./brain-system.md)
4-tier cognitive architecture.

**Tiers:**
- [Tier 0: Governance](./tier0-governance.md) - Immutable rules
- [Tier 1: Working Memory](./tier1-memory.md) - Conversation tracking
- [Tier 2: Knowledge Graph](./tier2-knowledge.md) - Learned patterns
- [Tier 3: Development Context](./tier3-context.md) - Git metrics, health

---

## Agent System

### [Agent Base Classes](./agents/base.md)
Foundation for all CORTEX agents.

**Module:** `src.cortex_agents.base_agent`  
**Key Classes:** `BaseAgent`, `AgentMetadata`, `AgentCapability`

### Left Brain Agents (Tactical)

#### [Executor Agent](./agents/executor.md)
Implements features and fixes bugs.

**Module:** `src.cortex_agents.executor_agent`  
**Capabilities:** code_generation, bug_fixing, refactoring

#### [Tester Agent](./agents/tester.md)
Creates comprehensive test suites.

**Module:** `src.cortex_agents.tester_agent`  
**Capabilities:** test_generation, test_validation, coverage_analysis

#### [Validator Agent](./agents/validator.md)
Quality assurance and validation.

**Module:** `src.cortex_agents.validator_agent`  
**Capabilities:** code_review, quality_metrics, standards_compliance

#### [Work Planner Agent](./agents/work_planner.md)
Task breakdown and sequencing.

**Module:** `src.cortex_agents.work_planner_agent`  
**Capabilities:** task_planning, dependency_analysis, time_estimation

#### [Documenter Agent](./agents/documenter.md)
Auto-generates documentation.

**Module:** `src.cortex_agents.documenter_agent`  
**Capabilities:** doc_generation, api_docs, guide_creation

### Right Brain Agents (Strategic)

#### [Intent Detector Agent](./agents/intent_detector.md)
Routes natural language requests.

**Module:** `src.cortex_agents.intent_detector_agent`  
**Capabilities:** intent_classification, command_routing, context_extraction

#### [Architect Agent](./agents/architect.md)
System design and architecture validation.

**Module:** `src.cortex_agents.architect_agent`  
**Capabilities:** architecture_design, pattern_validation, system_review

#### [Health Validator Agent](./agents/health_validator.md)
Project health diagnostics.

**Module:** `src.cortex_agents.health_validator_agent`  
**Capabilities:** health_checks, anomaly_detection, metrics_analysis

#### [Pattern Matcher Agent](./agents/pattern_matcher.md)
Finds similar problems and solutions.

**Module:** `src.cortex_agents.pattern_matcher_agent`  
**Capabilities:** pattern_matching, solution_retrieval, similarity_scoring

#### [Learner Agent](./agents/learner.md)
Accumulates knowledge from interactions.

**Module:** `src.cortex_agents.learner_agent`  
**Capabilities:** knowledge_extraction, pattern_learning, graph_updates

---

## Plugin System

### [Plugin Base](./plugins/base.md)
Foundation for all plugins.

**Module:** `src.plugins.base_plugin`  
**Key Classes:** `BasePlugin`, `PluginMetadata`, `PluginCategory`, `PluginPriority`

### [Plugin Registry](./plugins/registry.md)
Plugin discovery and management.

**Module:** `src.plugins.plugin_registry`  
**Key Classes:** `PluginRegistry`

### Core Plugins

- [**Cleanup Plugin**](./plugins/cleanup.md) - Workspace maintenance
- [**Code Review Plugin**](./plugins/code-review.md) - Automated code review
- [**Configuration Wizard**](./plugins/configuration-wizard.md) - Interactive setup
- [**Doc Refresh Plugin**](./plugins/doc-refresh.md) - Documentation updates
- [**Extension Scaffold**](./plugins/extension-scaffold.md) - VS Code extension generator
- [**Platform Switch**](./plugins/platform-switch.md) - Cross-platform compatibility
- [**System Refactor**](./plugins/system-refactor.md) - Large-scale refactoring

### [Command Registry](./plugins/command-registry.md)
Command discovery and routing.

**Module:** `src.plugins.command_registry`  
**Key Classes:** `CommandRegistry`, `CommandMetadata`

### [Plugin Hooks](./plugins/hooks.md)
Lifecycle hooks for plugins.

**Module:** `src.plugins.hooks`  
**Enum:** `HookPoint`

---

## Tier APIs

### [Tier 0: Governance](./tier0-governance.md)
Immutable protection rules.

**Module:** `src.tier0.brain_protector`  
**Key Classes:** `BrainProtector`, `ProtectionRule`, `SKULLLayer`

**Protection Layers:**
1. SKULL Protection (test validation enforcement)
2. Command Validation
3. File System Protection
4. Memory Integrity
5. Knowledge Graph Validation
6. Context Boundaries
7. Agent Coordination

### [Tier 1: Working Memory](./tier1-memory.md)
Conversation history and state.

**Module:** `src.tier1.conversation_manager`  
**Key Classes:** `ConversationManager`, `ConversationState`

**Database:** `cortex-brain/conversation-history.db`  
**Retention:** Last 20 conversations

### [Tier 2: Knowledge Graph](./tier2-knowledge.md)
Learned patterns and accumulated wisdom.

**Module:** `src.tier2.knowledge_graph`  
**Key Classes:** `KnowledgeGraph`, `Pattern`, `Relationship`

**Storage:** `cortex-brain/knowledge-graph.yaml`  
**Structure:** Patterns, relationships, solutions, anti-patterns

### [Tier 3: Development Context](./tier3-context.md)
Real-time project health metrics.

**Module:** `src.tier3.context_intelligence`  
**Key Classes:** `ContextIntelligence`, `GitMetrics`, `TestCoverage`

**Metrics:**
- Git activity (commits, branches, authors)
- Test coverage (lines, branches, functions)
- Code quality (complexity, duplication)
- File hotspots (change frequency)

---

## Utilities

### [Configuration](./utilities/config.md)
Multi-machine configuration management.

**Module:** `src.config`  
**File:** `cortex.config.json`

### [YAML Loaders](./utilities/yaml-loaders.md)
Optimized YAML loading (73% token reduction).

**Module:** `src.utilities.yaml_loader`  
**Files:** 
- `cortex-operations.yaml`
- `cortex-brain/brain-protection-rules.yaml`
- `cortex-brain/knowledge-graph.yaml`
- `cortex-brain/development-context.yaml`

### [Token Optimizer](./utilities/token-optimizer.md)
Token usage optimization for prompts.

**Module:** `src.utilities.token_optimizer`  
**Achievement:** 97.2% token reduction (CORTEX 2.0)

---

## Testing

### [Test Infrastructure](./testing/infrastructure.md)
Pytest configuration and markers.

**Markers:**
- `cortex_internal` - Internal system tests
- `integration` - Cross-module tests
- `brain_test` - Brain protection tests
- `edge_case` - Boundary condition tests
- `performance` - Performance regression tests
- `slow` - Long-running tests
- `fifo` - FIFO ordering tests

### [Test Fixtures](./testing/fixtures.md)
Reusable test fixtures.

**Module:** `tests.conftest`

### [Mock Objects](./testing/mocks.md)
Mock implementations for testing.

**Directory:** `tests/fixtures/`

---

## Examples

### Basic Usage

```python
from src.cortex_entry import CortexEntry

# Initialize CORTEX
cortex = CortexEntry()

# Execute operation
result = cortex.execute("cortex_tutorial", profile="quick")

# Check result
if result["success"]:
    print(result["message"])
```

### Using Agents

```python
from src.cortex_agents.executor_agent import ExecutorAgent

# Create agent instance
executor = ExecutorAgent()

# Execute task
result = executor.execute({
    "task": "implement feature",
    "context": {"feature": "authentication"}
})
```

### Using Plugins

```python
from src.plugins.cleanup_plugin import Plugin as CleanupPlugin

# Initialize plugin
cleanup = CleanupPlugin()
cleanup.initialize()

# Execute cleanup
result = cleanup.execute({
    "hook": "ON_CLEANUP",
    "scan_types": ["temp_files", "old_logs"]
})
```

### Accessing Brain Tiers

```python
from src.tier1.conversation_manager import ConversationManager
from src.tier2.knowledge_graph import KnowledgeGraph
from src.tier3.context_intelligence import ContextIntelligence

# Tier 1: Get conversation history
conv_mgr = ConversationManager()
recent_convs = conv_mgr.get_recent_conversations(count=5)

# Tier 2: Query knowledge graph
kg = KnowledgeGraph()
patterns = kg.find_patterns(category="bug_fixes")

# Tier 3: Get project metrics
context = ContextIntelligence()
metrics = context.get_project_health()
```

---

## API Design Principles

### 1. **Consistent Return Types**
All APIs return dictionaries with standard keys:
```python
{
    "success": bool,
    "message": str,
    "data": Any,
    "error": Optional[str],
    "timestamp": str
}
```

### 2. **Error Handling**
All APIs use exception handling with informative errors:
```python
try:
    result = api.execute(params)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
except ExecutionError as e:
    logger.error(f"Execution failed: {e}")
```

### 3. **Type Hints**
All APIs use Python type hints:
```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute with typed parameters and return"""
    pass
```

### 4. **Logging**
All APIs use structured logging:
```python
logger.info("Operation started", extra={"operation": "demo"})
logger.error("Operation failed", extra={"error": str(e)})
```

### 5. **Configuration**
All APIs read configuration from `cortex.config.json`:
```python
from src.config import Config

config = Config()
setting = config.get("plugin.cleanup.max_age_days", default=30)
```

---

## Versioning

CORTEX uses semantic versioning:

- **Current Version:** 2.0.0
- **API Stability:** Stable (breaking changes only in major versions)
- **Deprecation Policy:** 2 minor versions notice before removal

---

## Performance Targets

### Tier Performance
- **Tier 1 (Memory):** ≤50ms per operation (99th percentile)
- **Tier 2 (Knowledge):** ≤150ms per operation (99th percentile)
- **Tier 3 (Context):** ≤500ms per operation (99th percentile)

### Operation Performance
- **Operations:** <5 seconds total (excluding long-running tasks)
- **Hot Paths:** <10ms with caching (95th percentile)

### Token Optimization
- **CORTEX 2.0:** 97.2% reduction vs CORTEX 1.0
- **YAML Files:** 73.2% reduction vs markdown equivalent

---

## Contributing

To contribute to CORTEX APIs:

1. Follow existing patterns and conventions
2. Add type hints to all new functions
3. Write comprehensive docstrings
4. Add unit tests (80% coverage minimum)
5. Update API documentation
6. Run `pytest` before submitting

See [Contributing Guide](../guides/contributing.md) for details.

---

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Plugin Development Guide](../guides/plugin-development.md)
- [Agent System Guide](../guides/agent-system.md)
- [Testing Guide](../testing/guide.md)

---

*This API reference is auto-generated from source code docstrings and manually maintained for CORTEX 2.0.*

*Last Updated: 2025-11-10 | CORTEX 2.0 API Documentation Initiative*
