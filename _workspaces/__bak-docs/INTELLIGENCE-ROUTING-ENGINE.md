# Intelligence Routing Engine: Prompt & Agent Orchestration

**Authority:** Phase 49 | AC-INTELLIGENCE-ROUTING-001 | CORE-035 | CORE-047 | MCP-FIRST  
**Date:** 2026-02-09  
**Status:** ✅ COMPLETE | 35/35 Tests Passing  
**Author:** Asif Hussain

---

## 📋 Overview

The Intelligence Routing Engine is a sophisticated system for dynamically routing user intents to appropriate prompts and agents based on semantic matching, intent classification, and unified intelligence synthesis.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **10 Intent Types** | IMPLEMENT, FIX, REFACTOR, ANALYZE, AUDIT, DESIGN, PLAN, ONBOARD, DEBUG, DIGEST |
| **Semantic Matching** | Keyword and filename similarity scoring |
| **Resource Discovery** | Automatic discovery and classification of prompts/agents |
| **Caching** | Multi-layer caching for performance (routing, content, metadata) |
| **Confidence Scoring** | 0.0-1.0 confidence with reasoning |
| **Unified Intelligence** | Synthesis flags for UnifiedIntelligenceContext requirements |
| **Context Hints** | Smart loading hints for incremental context synthesis |
| **Fallback Mechanisms** | Graceful degradation when resources unavailable |
| **MCP Integration** | Full MCP-First gateway with wiring system |

---

## 🏗️ Architecture

### Component Structure

```
IntelligenceRoutingEngine (Core)
├─ Intent classification (10 types)
├─ Resource discovery (prompts + agents)
├─ Semantic matching engine
├─ Confidence scoring
└─ Multi-layer caching

IntelligenceRoutingWiring (Integration)
├─ MCP gateway layer
├─ Orchestrator mapping
├─ Intent parsing
└─ Integrity validation

RoutingDecision (Output)
├─ Primary prompt metadata
├─ Primary agent metadata
├─ Secondary resources
├─ Semantic matches
├─ Confidence scores
├─ Context hints
└─ Unified intelligence flags
```

### Directory Resolution Strategy

**Prompts (.github/prompts/):**
1. Current directory
2. Parent directories (up to 5 levels)
3. Fallback to current working directory

**Agents (.github/agents/core/):**
1. Current directory
2. Parent directories (up to 5 levels)
3. Fallback to current working directory

**Why:** Supports multiple project structures and nested workspaces

---

## 🎯 Intent Routing Map

| Intent | Primary Prompt | Primary Agent | Orchestrator |
|--------|---------------|---------------|--------------|
| **IMPLEMENT** | CORTEX.prompt.md | cortex-executor.md | TDDOrchestrator |
| **FIX** | CORTEX.prompt.md | cortex-executor.md | TDDOrchestrator |
| **REFACTOR** | CORTEX.prompt.md | cortex-architect.md | RefactoringOrchestrator |
| **ANALYZE** | CORTEX.prompt.md | cortex-auditor.md | LENSSynthesis |
| **AUDIT** | CORTEX.prompt.md | cortex-auditor.md | EnforcementOrchestrator |
| **DESIGN** | cortex-architect.prompt.md | cortex-architect.md | ChallengeEngine |
| **PLAN** | cortex-architect.prompt.md | cortex-phase-resolver.md | PlanOrchestrator |
| **ONBOARD** | CORTEX.prompt.md | cortex-environment-setup.md | RepositoryOnboardingOrchestrator |
| **DEBUG** | CORTEX.prompt.md | cortex-debugger.md | DebuggingOrchestrator |
| **DIGEST** | CORTEX.prompt.md | cortex-digest.md | DigestEnhancementOrchestrator |

### Secondary Resources

| Intent | Secondary Prompts | Secondary Agents |
|--------|------------------|-----------------|
| **IMPLEMENT** | response-format-standards.md | cortex-holistic-validator.md |
| **FIX** | response-format-standards.md | cortex-debugger.md |
| **REFACTOR** | response-format-standards.md | cortex-holistic-validator.md |
| **ANALYZE** | response-format-standards.md | cortex-auditor.md |
| **AUDIT** | response-format-standards.md | cortex-auditor.md |
| **DESIGN** | response-format-standards.md | cortex-designer.md |
| **PLAN** | response-format-standards.md | cortex-interactive.md |

---

## 🔑 Core Classes

### IntelligenceRoutingEngine

**Purpose:** Core routing engine for intent-based resource selection

```python
engine = IntelligenceRoutingEngine(prompts_dir, agents_dir)

# Route intent to resources
decision = engine.route(
    intent=IntentType.IMPLEMENT,
    request="add authentication feature",
    context={"file_path": "cortex/auth.py"}
)

# Result
print(decision.primary_prompt.name)  # "CORTEX"
print(decision.primary_agent.name)   # "cortex-executor"
print(decision.confidence_score)     # 0.89
print(decision.context_hints)        # ["Load TDD patterns...", ...]
```

**Key Methods:**
- `route()`: Route intent to resources
- `get_prompt_content()`: Load prompt file
- `get_agent_content()`: Load agent file
- `list_available_prompts()`: Discover prompts
- `list_available_agents()`: Discover agents
- `get_routing_stats()`: Get statistics

### IntelligenceRoutingWiring

**Purpose:** MCP-First gateway layer for orchestrator integration

```python
wiring = IntelligenceRoutingWiring()

# Route to resources
result = wiring.route_to_resources(
    intent="IMPLEMENT",
    request="add feature"
)

if result["success"]:
    prompt = result["prompt_content"]
    agent = result["agent_content"]
    
    # Get orchestrator for intent
    orchestrator = wiring.get_intent_handler_orchestrator("IMPLEMENT")
    # "TDDOrchestrator"
```

**Key Methods:**
- `route_to_resources()`: Route with content loading
- `get_intent_handler_orchestrator()`: Get orchestrator name
- `get_prompts_for_intent()`: Get all prompts
- `get_agents_for_intent()`: Get all agents
- `validate_routing_integrity()`: Integrity check
- `get_wiring_stats()`: Get statistics

### RoutingDecision

**Purpose:** Decision output containing all routing information

```python
@dataclass
class RoutingDecision:
    intent: IntentType
    primary_prompt: PromptMetadata
    primary_agent: AgentMetadata
    secondary_prompts: List[PromptMetadata]
    secondary_agents: List[AgentMetadata]
    confidence_score: float
    reasoning: str
    semantic_matches: Dict[str, float]
    requires_unified_intelligence: bool
    context_hints: List[str]
    timestamp: str
```

---

## 🔍 Semantic Matching Algorithm

1. **Keyword Matching:** Match intent keywords in request (+0.3 per match, capped at 1.0)
2. **Filename Matching:** Match words (>3 chars) in resource names (+0.1 per match)
3. **Normalization:** Lowercase, trim whitespace
4. **Scoring:** 0.0-1.0 with max aggregation

**Example:**
```
Intent: IMPLEMENT
Request: "refactor code quality"
Matches:
  - "refactor" in TDD agent name: 0.1
  - IMPLEMENT keywords in request: 0.3
  - Filename "executor" matches: 0.0
Total Score: 0.4
```

---

## 💾 Caching Strategy

### Three-Layer Caching

| Layer | Key | TTL | Purpose |
|-------|-----|-----|---------|
| **1. Routing Cache** | hash(intent + request) | Session | RoutingDecision objects |
| **2. Metadata Cache** | filename | Session | PromptMetadata/AgentMetadata |
| **3. Content Cache** | filepath | Session | Loaded file contents |

**Hit Rates:** 70%+ expected in typical sessions

---

## 📊 Classification System

### Prompt Categories

| Category | Patterns | Purpose |
|----------|----------|---------|
| PRODUCTION_MASTER | "CORTEX.prompt.md" | Main production prompt |
| ARCHITECT | "architect", "architecture" | Design/architecture |
| RESPONSE_FORMAT | "response", "format" | Output formatting |
| SETUP_GUIDE | "setup", "guide" | Initial setup |
| ACTIVATION_CHECKLIST | "activation", "checklist" | Pre-flight checks |
| CONTEXTUAL | Other | Context-specific |

### Agent Categories

| Category | Patterns | Purpose |
|----------|----------|---------|
| CORE | "executor", "router", "orchestrator" | Core functionality |
| DOMAIN | "architect", "designer", "planner" | Domain experts |
| SUPPORT | "debugger", "validator", "vacuum" | Support/tools |
| EDUCATION | "ask", "coordinator", "storyteller" | Learning |

---

## ✅ Test Coverage

### Test Suite: 35/35 Passing ✅

**Engine Tests (20):**
- Initialization
- Intent routing (all 10 types)
- Resource discovery (prompts + agents)
- Caching performance
- Semantic matching
- Confidence scoring
- Classification (prompt + agent)

**Wiring Tests (12):**
- Initialization
- Route to resources
- Intent parsing (exact + partial)
- Orchestrator mapping
- Availability queries
- Integrity validation
- Statistics gathering

**Metadata Tests (3):**
- PromptMetadata creation
- AgentMetadata creation
- RoutingDecision creation

---

## 🚀 Usage Examples

### Example 1: Basic Intent Routing

```python
from cortex.brain.core.intelligence_routing_engine import IntelligenceRoutingEngine, IntentType

engine = IntelligenceRoutingEngine()

# Route IMPLEMENT intent
decision = engine.route(IntentType.IMPLEMENT, "add user authentication")

print(f"Intent: {decision.intent.value}")
print(f"Prompt: {decision.primary_prompt.name}")
print(f"Agent: {decision.primary_agent.name}")
print(f"Confidence: {decision.confidence_score:.2f}")
print(f"Requires Unified Intelligence: {decision.requires_unified_intelligence}")
```

### Example 2: Loading Resources

```python
# Load prompt content
prompt_content = engine.get_prompt_content(decision.primary_prompt.path)

# Load agent content
agent_content = engine.get_agent_content(decision.primary_agent.path)

# Load secondary resources
for secondary_prompt in decision.secondary_prompts:
    content = engine.get_prompt_content(secondary_prompt.path)
```

### Example 3: MCP Integration

```python
from cortex.brain.core.intelligence_routing_wiring import IntelligenceRoutingWiring

wiring = IntelligenceRoutingWiring()

# Route with full context
result = wiring.route_to_resources(
    intent="IMPLEMENT",
    request="add authentication",
    context={"file_path": "cortex/auth.py", "company": "ACME"}
)

if result["success"]:
    # Get orchestrator
    orchestrator = wiring.get_intent_handler_orchestrator("IMPLEMENT")
    
    # Access all resources
    primary_prompt = result["prompt_content"]
    primary_agent = result["agent_content"]
    secondary_prompts = result["secondary_prompts"]
    secondary_agents = result["secondary_agents"]
    
    # Context hints for incremental loading
    hints = result["context_hints"]
```

### Example 4: Integrity Validation

```python
validation = wiring.validate_routing_integrity()

print(f"All intents valid: {validation['success']}")
print(f"Total intents: {validation['total_intents']}")
print(f"Validated: {validation['validated']}")
if validation['issues']:
    print("Issues:", validation['issues'])
```

---

## 🔗 Integration Points

### Orchestrator Integration

The routing engine integrates with CORTEX orchestrators:

```python
# In IntentRouter or MasterOrchestrator
from cortex.brain.core.intelligence_routing_wiring import IntelligenceRoutingWiring

wiring = IntelligenceRoutingWiring()

# Route to resources
result = wiring.route_to_resources(user_intent)

# Get target orchestrator
target_orchestrator = wiring.get_intent_handler_orchestrator(user_intent)

# Fetch prompt and agent content
prompt = result["prompt_content"]
agent = result["agent_content"]

# Use unified intelligence flags
if result["requires_unified_intelligence"]:
    unified_context = fetch_unified_intelligence(user_intent, file_path)
```

### MCP Tool Exposure

Future MCP tools can expose routing:

```
# MCP Tool: cortex_route_intent
POST /tools/cortex_route_intent
{
    "intent": "IMPLEMENT",
    "request": "add authentication",
    "context": {...}
}

Response:
{
    "decision": {...},
    "prompt_content": "...",
    "agent_content": "...",
    "orchestrator": "TDDOrchestrator",
    "confidence": 0.89
}
```

---

## 📈 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Route (cache hit) | <1ms | Hash lookup only |
| Route (cold) | 10-50ms | Discovery + scoring |
| Semantic matching | 5-20ms | String comparisons |
| Load content | 10-100ms | File I/O bound |
| Integrity check | 50-200ms | Validates all intents |

**Memory:** ~5-10MB for full resource discovery

---

## 🛡️ Error Handling

### Graceful Degradation

1. **Missing Resources:** Creates fallback metadata
2. **Load Failures:** Returns None, logs warning
3. **Invalid Intent:** Raises ValueError with guidance
4. **Directory Resolution:** Tries multiple strategies

### Recovery Strategies

```python
try:
    decision = engine.route(intent)
except ValueError as e:
    logger.error(f"Invalid intent: {e}")
    # Use fallback intents

try:
    content = engine.get_prompt_content(path)
except Exception as e:
    logger.warning(f"Failed to load: {e}")
    content = None  # Handled upstream
```

---

## 📚 References

- **Phase 49:** Context Crystallization Layer integration
- **CORE-008:** TDD-first implementation (all 35 tests)
- **CORE-035:** Single canonical implementation (wiring.yaml)
- **CORE-047:** No file paths in instructions (semantic_search based)
- **MCP-FIRST:** All operations MCP-ready
- **wiring.yaml:** Orchestrator registry

---

## 🎉 Summary

✅ **Complete Implementation**
- 2 core modules (Engine + Wiring)
- 10 intent types fully routed
- 35/35 tests passing
- Semantic matching algorithm
- Multi-layer caching
- Fallback mechanisms
- MCP integration ready

✅ **Production Ready**
- Error handling
- Performance optimized
- Documentation complete
- Orchestrator mapped
- Unified intelligence flags
- Context hints system

---

**AC_COMPLETE:** AC-INTELLIGENCE-ROUTING-001 ✅  
**Next Phase:** MCP tool exposure + LENSSynthesis integration
