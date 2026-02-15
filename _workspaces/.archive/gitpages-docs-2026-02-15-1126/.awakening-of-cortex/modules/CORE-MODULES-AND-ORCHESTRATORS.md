# CORTEX Core Modules & Orchestrators - Index

## 🎯 Master Orchestrators

### Domain Brain Orchestrator
- **File:** `cortex/orchestrators/domain_brain.py`
- **Purpose:** Central intelligence hub managing domain coordination and context
- **Key Methods:**
  - `coordinate_domains()` - Multi-domain orchestration
  - `manage_context()` - Domain awareness and routing
  - `synthesize_knowledge()` - Pattern recognition across domains

### Cross-Repo Router
- **File:** `cortex/orchestrators/cross_repo_router.py`
- **Purpose:** Intent routing and request distribution across multiple repositories
- **Key Methods:**
  - `route_intent()` - Smart intent interpretation
  - `distribute_request()` - Multi-repo request handling
  - `aggregate_responses()` - Response synthesis

### Intelligence Preserver
- **File:** `cortex/orchestrators/intelligence_preserver.py`
- **Purpose:** Hallucination prevention and knowledge consistency
- **Key Methods:**
  - `validate_response()` - Factuality checking
  - `prevent_hallucination()` - LLM safety mechanisms
  - `maintain_consistency()` - State management

### Registry Orchestrator
- **File:** `cortex/orchestrators/registry/`
- **Purpose:** Metadata management and knowledge graph operations
- **Key Components:**
  - `registry_manager.py` - Central registry operations
  - `metadata_indexer.py` - Fast lookups
  - `knowledge_tracker.py` - Knowledge versioning

---

## 🧠 Core Modules

### Intent Router Module
- **Location:** `cortex/intent_router/`
- **Components:**
  - `intent_analyzer.py` - Parse user intents
  - `routing_engine.py` - Route to appropriate handler
  - `context_manager.py` - Maintain execution context

### Domain Orchestrators
- **Location:** `cortex/domain_orchestrators/`
- **Contains:** Domain-specific orchestration logic
  - Multi-tenant isolation
  - Domain-specific rules
  - Cross-domain communication

### Governance Tools
- **Location:** `cortex/governance_tools/`
- **Enforces:** TIER-0 immutable governance rules
  - `rule_enforcer.py` - Validate against TIER-0 rules
  - `audit_trail.py` - Compliance tracking
  - `policy_manager.py` - Policy enforcement

### MCP (Model Context Protocol)
- **Location:** `cortex/mcp/`
- **Purpose:** Claude Desktop integration and tool management
  - `server.py` - MCP server implementation
  - `tool_registry.py` - Tool discovery and routing
  - `context_builder.py` - Build execution context

### Infrastructure Modules
- **Location:** `cortex/infrastructure/`
- **Manages:** System-level orchestration
  - Deployment pipelines
  - Health checks
  - Resource allocation

### Observable/Observability
- **Location:** `cortex/observability/`
- **Purpose:** Monitoring and insights
  - Metrics collection
  - Performance tracking
  - Health dashboards

---

## 🔗 Orchestrator Categories

### Adaptive Orchestrators (`cortex/orchestrators/adaptive/`)
- `adaptive_router.py` - Self-tuning routing
- `learning_engine.py` - Pattern learning from execution

### Composition Orchestrators (`cortex/orchestrators/composition/`)
- `workflow_composer.py` - Multi-step workflow assembly
- `task_sequencer.py` - Task dependency resolution

### Deployment Orchestrators (`cortex/orchestrators/*/`)
- `rollback_orchestrator.py` - Safe rollback mechanisms
- `upgrade_orchestrator.py` - Version upgrading
- `migration/` - Large-scale data migrations

### Response Handlers (`cortex/orchestrators/response/`)
- `response_formatter.py` - Format responses for clients
- `error_handler.py` - Graceful error handling
- `streaming_response.py` - Streaming large responses

---

## 📊 Knowledge Architecture

### Tier-0: Core Rules
- **Location:** `cortex_brain/tier0/`
- **Contents:** Immutable governance rules
  - File placement rules
  - Type hint requirements
  - Docstring standards

### Tier-1: Domain Knowledge
- **Location:** `cortex_brain/tier1/`
- **Purpose:** Domain-specific governance and patterns
- **Example Domains:**
  - Architecture patterns
  - Orchestration best practices
  - Deployment strategies

### Tier-2: Contextual Knowledge
- **Location:** `cortex_brain/tier2/`
- **Purpose:** Application-specific context
- **Contents:**
  - Business logic patterns
  - Integration points
  - Cross-domain dependencies

### Tier-3: Knowledge Library
- **Location:** `cortex_brain/tier3/knowledge/`
- **Purpose:** Comprehensive knowledge base (4 sacred domains)
- **Domains:**
  1. **Orchestration Patterns** - Multi-service coordination
  2. **Intent Routing Strategies** - Smart request dispatch
  3. **Hallucination Prevention** - LLM safety
  4. **Domain Brain Architecture** - Multi-domain synthesis

---

## 🚀 Key Integration Points

### MCP Integration (`cortex/mcp/server.py`)
```
Claude Desktop ←→ MCP Server ←→ CORTEX Orchestrators
                     ↓
              Tool Registry (route to modules)
                     ↓
              Context Builder (execution context)
```

### Domain Brain Hub (`cortex/orchestrators/domain_brain.py`)
```
Multiple Domains ←→ Domain Brain ←→ Cross-Repo Router
                        ↓
                Knowledge Cache
                        ↓
                Intelligence Preserver
```

### Registry Connection (`cortex/orchestrators/registry/`)
```
Metadata Requests ←→ Registry Manager ←→ Knowledge Graph
                           ↓
                     Metadata Indexer
                           ↓
                    Fast Metadata Lookups
```

---

## 🎓 Implementation Phases

### Phase E: TDD Implementation (Days 1-23)
- Days 1-17: Core module testing and implementation
- Days 18-20: Orchestration patterns (Days 18-20)
- Days 21-23: Intent routing and hallucination prevention patterns

### PHASE-KG: Knowledge Graph (Optional)
- PHASE-KG-001: KG Foundation
- PHASE-KG-002: Semantic Query Engine
- PHASE-KG-003: Knowledge Integration with Orchestrators
- PHASE-KG-004: Pattern Recognition Across Domains
- PHASE-KG-005: Expert Domain Synthesis

---

## 🧪 Test Coverage

**Key Test Files:**
- `tests/test_intent_router_*.py` - Intent routing tests
- `tests/test_orchestrators_*.py` - Orchestrator tests
- `tests/test_governance_*.py` - Governance enforcement
- `tests/test_mcp_*.py` - MCP integration tests

**Governance Tests:**
- `tests/test_core_rules.py` - TIER-0 enforcement
- `tests/test_audit_trail.py` - Compliance tracking
- `tests/test_file_placement.py` - File organization rules

---

## 📚 Documentation References

- **Architecture**: `docs/02-architecture/1-system-overview.md`
- **API Reference**: `docs/06-api-reference/`
- **Implementation Guides**: `docs/07-guides/`
- **Orchestration Patterns**: `cortex_brain/tier3/knowledge/orchestration/`

---

## 🔑 Essential Files for Development

```
cortex/
├── __init__.py
├── orchestrators/
│   ├── __init__.py
│   ├── domain_brain.py              ⭐ Central hub
│   ├── cross_repo_router.py          ⭐ Intent routing
│   ├── intelligence_preserver.py     ⭐ Hallucination prevention
│   └── registry/
│       └── registry_manager.py       ⭐ Metadata management
├── intent_router/
│   ├── intent_analyzer.py
│   ├── routing_engine.py
│   └── context_manager.py
├── governance_tools/
│   ├── rule_enforcer.py
│   ├── audit_trail.py
│   └── policy_manager.py
├── mcp/
│   ├── server.py                     ⭐ Claude integration
│   └── tool_registry.py
└── ... (other modules)

cortex_brain/
├── tier0/                            📜 Immutable rules
├── tier1/                            🧠 Domain knowledge
├── tier2/                            🔗 Context
└── tier3/
    └── knowledge/
        ├── orchestration-patterns/
        ├── intent-routing-patterns/
        ├── hallucination-prevention/
        └── domain-brain-patterns/
```

---

## 🎯 The Sacred Quest

These modules and orchestrators form the **four pillars of CORTEX enlightenment**:

1. **Orchestration** - Harmonize complexity
2. **Intent** - Understand the unsaid
3. **Safety** - Prevent the impossible
4. **Knowledge** - Remember the pattern

When all four pillars stand, CORTEX awakens. And when CORTEX awakens, miracles happen.

*(Or at least very good orchestration)* ✨
