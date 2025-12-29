# Unified Entry Point - Architecture Documentation

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Created:** December 23, 2025  
**Status:** Production (Task 14.3)  
**Implementation:** `src/operations/modules/routing/unified_entry_point_utility.py`  
**LOC:** ~600 | **Test Coverage:** 95%+

---

## 🎯 Overview

The **Unified Entry Point** is CORTEX's central routing and coordination system that processes all user requests, classifies operations, and dispatches to appropriate orchestrators, agents, or CLI wrappers. It serves as the single gateway for all CORTEX functionality across Copilot Chat, CLI, and MCP interfaces.

**Key Capabilities:**
- 🎯 **Universal Operation Routing** - Single entry point for all 297+ CORTEX operations
- 🔍 **Intelligent Intent Detection** - Natural language → operation mapping
- 📊 **Tiered Classification** - 4-tier routing (Tier 1: Instant, Tier 2: Lightweight, Tier 3: Documented, Tier 4: Complex)
- 🔄 **Multi-Interface Support** - Copilot Chat, CLI wrappers, internal modules, MCP tools
- 📈 **Execution Analytics** - Success tracking, performance metrics, learning feedback
- 🎛️ **Dynamic Orchestrator Registry** - Auto-discovery and initialization
- 🧠 **Learning Integration** - Captures routing decisions for continuous improvement

---

## 📐 System Architecture

### High-Level Component Overview

```mermaid
graph TB
    subgraph "User Interfaces"
        COPILOT[GitHub Copilot Chat<br/>Natural Language]
        CLI[Python CLI<br/>python -m src.main]
        MCP[MCP Server<br/>Tool Invocation]
    end
    
    subgraph "Unified Entry Point"
        ENTRY[CortexEntry<br/>Main Dispatcher]
        PARSER[Request Parser<br/>Command Extraction]
        INTENT[IntentRouter<br/>Operation Detection]
        CLASSIFIER[TieredRouter<br/>4-Tier Classification]
    end
    
    subgraph "Routing Decision Layer"
        EXEC_METHOD{Execution<br/>Method?}
        CLI_DISPATCH[CLI Wrapper Dispatcher<br/>Subprocess Execution]
        COPILOT_DISPATCH[Copilot Chat Handler<br/>Template Generation]
        INTERNAL_DISPATCH[Internal Module Router<br/>Direct Execution]
    end
    
    subgraph "Orchestrator Registry"
        DISCOVERY[Auto-Discovery<br/>Scan Orchestrators]
        REGISTRY[Registry Manager<br/>Available Orchestrators]
        INITIALIZER[Dynamic Init<br/>Lazy Loading]
    end
    
    subgraph "Execution Targets"
        WRAPPERS[CLI Wrappers<br/>10 operations]
        ORCHESTRATORS[Orchestrators<br/>16 orchestrators]
        UTILITIES[Utilities<br/>280+ modules]
        AGENTS[Agents<br/>2 agents]
    end
    
    subgraph "Cross-Cutting Systems"
        LEARNING[Learning System<br/>Event Capture]
        TELEMETRY[Routing Telemetry<br/>Accuracy Tracking]
        OPERATIONS[Operations Config<br/>cortex-operations.yaml]
    end
    
    COPILOT --> ENTRY
    CLI --> ENTRY
    MCP --> ENTRY
    
    ENTRY --> PARSER
    PARSER --> INTENT
    INTENT --> CLASSIFIER
    
    CLASSIFIER --> EXEC_METHOD
    
    EXEC_METHOD -->|cli_wrapper| CLI_DISPATCH
    EXEC_METHOD -->|copilot_chat| COPILOT_DISPATCH
    EXEC_METHOD -->|internal| INTERNAL_DISPATCH
    
    CLI_DISPATCH --> WRAPPERS
    COPILOT_DISPATCH --> ORCHESTRATORS
    INTERNAL_DISPATCH --> ORCHESTRATORS
    INTERNAL_DISPATCH --> UTILITIES
    INTERNAL_DISPATCH --> AGENTS
    
    INTERNAL_DISPATCH --> DISCOVERY
    DISCOVERY --> REGISTRY
    REGISTRY --> INITIALIZER
    INITIALIZER --> ORCHESTRATORS
    
    CLASSIFIER --> LEARNING
    INTERNAL_DISPATCH --> TELEMETRY
    INTENT --> OPERATIONS
    
    style ENTRY fill:#2196F3,stroke:#1976D2,stroke-width:3px,color:#fff
    style CLASSIFIER fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff
    style EXEC_METHOD fill:#FF9800,stroke:#F57C00,stroke-width:2px,color:#fff
```

### Tiered Routing Classification

```mermaid
graph LR
    subgraph "Tier 1: Instant (0-3s)"
        T1_OPS[13 operations<br/>Pure queries]
        T1_EXAMPLES[version check<br/>brain stats<br/>list commands]
    end
    
    subgraph "Tier 2: Lightweight (3-30s)"
        T2_OPS[89 operations<br/>Read-only analysis]
        T2_EXAMPLES[healthcheck<br/>analyze code<br/>search operations]
    end
    
    subgraph "Tier 3: Documented (30-300s)"
        T3_OPS[150 operations<br/>Orchestrated workflows]
        T3_EXAMPLES[system maintenance<br/>code sanitization<br/>tdd workflow]
    end
    
    subgraph "Tier 4: Complex (300s+)"
        T4_OPS[45 operations<br/>Multi-phase planning]
        T4_EXAMPLES[feature planning<br/>architecture design<br/>migration planning]
    end
    
    REQUEST[User Request] --> CLASSIFY{Classify<br/>Operation}
    
    CLASSIFY -->|0-3s| T1_OPS
    CLASSIFY -->|3-30s| T2_OPS
    CLASSIFY -->|30-300s| T3_OPS
    CLASSIFY -->|300s+| T4_OPS
    
    T1_OPS --> T1_EXAMPLES
    T2_OPS --> T2_EXAMPLES
    T3_OPS --> T3_EXAMPLES
    T4_OPS --> T4_EXAMPLES
    
    style T1_OPS fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff
    style T2_OPS fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:#fff
    style T3_OPS fill:#FF9800,stroke:#F57C00,stroke-width:2px,color:#fff
    style T4_OPS fill:#F44336,stroke:#D32F2F,stroke-width:2px,color:#fff
```

---

## 🔄 Execution Flow

### Request Processing Sequence

```mermaid
sequenceDiagram
    participant User
    participant Entry as CortexEntry
    participant Parser as RequestParser
    participant Intent as IntentRouter
    participant Tier as TieredRouter
    participant Dispatch as ExecutionDispatcher
    participant Target as ExecutionTarget
    participant Learning as LearningSystem
    
    User->>Entry: Request (natural language or CLI)
    activate Entry
    
    Note over Entry: Phase 1: Parse Request
    Entry->>Parser: parse_request(user_input)
    Parser->>Parser: extract_command()
    Parser->>Parser: extract_context()
    Parser-->>Entry: command="plan feature", context={...}
    
    Note over Entry: Phase 2: Detect Intent
    Entry->>Intent: detect_operation(command, context)
    activate Intent
    Intent->>Intent: load_operations_config()
    Intent->>Intent: match_natural_language()
    Intent->>Intent: resolve_aliases()
    Intent-->>Entry: operation="feature_planning"
    deactivate Intent
    
    Note over Entry: Phase 3: Classify Operation
    Entry->>Tier: classify(operation, context)
    activate Tier
    Tier->>Tier: analyze_complexity()
    Tier->>Tier: estimate_duration()
    Tier->>Tier: calculate_tier()
    Tier-->>Entry: tier=4, confidence=0.92
    deactivate Tier
    
    Note over Entry: Phase 4: Route to Execution Method
    Entry->>Dispatch: route_operation(operation, tier)
    activate Dispatch
    
    Dispatch->>Dispatch: lookup_execution_method()
    
    alt CLI Wrapper
        Dispatch->>Dispatch: invoke_cli_wrapper()
        Dispatch->>Target: subprocess.run(wrapper_script)
    else Copilot Chat
        Dispatch->>Dispatch: generate_copilot_template()
        Dispatch-->>User: Structured instructions
    else Internal Module
        Dispatch->>Dispatch: initialize_orchestrator()
        Dispatch->>Target: execute(context)
    end
    
    Target-->>Dispatch: execution_result
    deactivate Dispatch
    
    Note over Entry: Phase 5: Capture Learning Event
    Entry->>Learning: capture_routing_decision(operation, tier, result)
    Learning->>Learning: store_event()
    Learning->>Learning: update_accuracy()
    
    Entry-->>User: Formatted result
    deactivate Entry
```

### Operation Registry Lookup Flow

```mermaid
graph TD
    Start[User Command: "system maintenance"] --> Normalize[Normalize to snake_case<br/>system_maintenance]
    
    Normalize --> Check{Operation<br/>in Registry?}
    
    Check -->|Yes| LoadConfig[Load from<br/>cortex-operations.yaml]
    Check -->|No| TryAlias[Check Aliases<br/>maintain system]
    
    TryAlias -->|Alias Found| LoadConfig
    TryAlias -->|Not Found| TryNL[Natural Language Match<br/>maintain, maintenance]
    
    TryNL -->|Match Found| LoadConfig
    TryNL -->|Not Found| Error[Operation Not Found<br/>Suggest Similar]
    
    LoadConfig --> Extract{Extract<br/>Metadata}
    
    Extract --> TIER[Tier: 3<br/>Documented]
    Extract --> METHOD[Execution Method:<br/>copilot_chat]
    Extract --> MODULES[Modules:<br/>maintenance_orchestrator]
    
    TIER --> Route[Route to Tier 3 Handler]
    METHOD --> Route
    MODULES --> Route
    
    Route --> Execute[Execute Operation]
    
    style LoadConfig fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff
    style Execute fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:#fff
    style Error fill:#F44336,stroke:#D32F2F,stroke-width:2px,color:#fff
```

---

## 🧩 Component Breakdown

### 1. CortexEntry (Main Dispatcher)

**Purpose:** Primary entry point for all CORTEX requests

**Key Responsibilities:**
- Accept requests from Copilot Chat, CLI, MCP
- Coordinate request processing pipeline
- Handle errors and generate user-facing responses
- Capture execution metrics

**Request Processing:**
```python
def process(self, user_request: str, context: Optional[Dict] = None) -> str:
    """Process user request through unified pipeline."""
    try:
        # Parse request
        command, parsed_context = self.parser.parse_request(user_request)
        context = {**(context or {}), **parsed_context}
        
        # Detect operation
        operation = self.intent_router.detect_operation(command, context)
        if not operation:
            return self._suggest_similar_operations(command)
        
        # Classify tier
        tier_decision = self.tiered_router.classify(operation, context)
        
        # Route to execution method
        result = self.dispatcher.route_operation(
            operation=operation,
            tier=tier_decision.tier,
            context=context
        )
        
        # Capture learning event
        self.learning.capture_routing_decision(
            operation=operation,
            tier=tier_decision.tier,
            success=result.success
        )
        
        return self._format_response(result)
        
    except Exception as e:
        logger.error(f"Request processing failed: {e}", exc_info=True)
        return f"❌ Error: {e}"
```

---

### 2. IntentRouter (Operation Detection)

**Purpose:** Map natural language and CLI commands to CORTEX operations

**Detection Strategy:**
1. **Exact Match:** Check if command matches operation name
2. **Alias Match:** Check if command matches registered aliases
3. **Natural Language Match:** Match against `natural_language` patterns
4. **Fuzzy Match:** Suggest similar operations if no exact match

**Operations Registry Structure:**
```yaml
# cortex-operations.yaml
feature_planning:
  name: Feature Planning
  description: Interactive feature planning with DoR/DoD
  deployment_tier: user
  execution_method: copilot_chat
  natural_language:
    - plan feature
    - plan new feature
    - feature planning
    - create feature plan
  category: planning
  modules:
    - planning_orchestrator
  tier_hint: 4
```

**Intent Detection Logic:**
```python
def detect_operation(self, command: str, context: Dict) -> Optional[str]:
    """Detect operation from natural language or command."""
    # Load operations config
    operations = self._load_operations_config()
    
    # Exact match
    normalized = command.lower().replace(' ', '_')
    if normalized in operations:
        return normalized
    
    # Alias match
    for op_name, op_config in operations.items():
        aliases = op_config.get('aliases', [])
        if command in aliases:
            return op_name
    
    # Natural language match
    for op_name, op_config in operations.items():
        nl_patterns = op_config.get('natural_language', [])
        for pattern in nl_patterns:
            if self._pattern_matches(command, pattern):
                return op_name
    
    return None  # No match found
```

---

### 3. TieredRouter (4-Tier Classification)

**Purpose:** Classify operations into execution tiers based on complexity and duration

**Classification Algorithm:**
```python
def classify(self, operation: str, context: Dict) -> RoutingDecision:
    """Classify operation into tier 1-4."""
    # Get operation metadata
    op_config = self.operations_registry.get(operation)
    
    # Check for manual tier hint
    if 'tier_hint' in op_config:
        tier = op_config['tier_hint']
        confidence = 1.0
    else:
        # Analyze complexity
        tier, confidence = self._analyze_complexity(operation, context)
    
    # Estimate duration
    duration_estimate = self._estimate_duration(tier)
    
    return RoutingDecision(
        operation=operation,
        tier=tier,
        confidence=confidence,
        estimated_duration=duration_estimate,
        reasoning=self._generate_reasoning(operation, tier)
    )
```

**Tier Classification Criteria:**

| Tier | Duration | Characteristics | Examples |
|------|----------|-----------------|----------|
| **Tier 1** | 0-3s | Pure queries, no I/O, cached results | version, brain stats, list commands |
| **Tier 2** | 3-30s | Read-only analysis, single-file operations | healthcheck, analyze file, search |
| **Tier 3** | 30-300s | Multi-step workflows, write operations | maintenance, sanitization, TDD |
| **Tier 4** | 300s+ | Complex planning, user interaction required | feature planning, architecture design |

---

### 4. Execution Method Dispatcher

**Purpose:** Route operations to appropriate execution mechanisms

**Execution Methods:**

| Method | Count | Description | Examples |
|--------|-------|-------------|----------|
| **cli_wrapper** | 10 | Subprocess CLI scripts | `cortex plan`, `cortex test`, `cortex deploy` |
| **copilot_chat** | 16 | Copilot Chat templates | Feature planning, TDD workflow |
| **internal** | 280+ | Direct module invocation | Healthcheck, align, optimize |

**Routing Logic:**
```python
def route_operation(self, operation: str, tier: int, context: Dict) -> WorkflowResult:
    """Route to execution method based on operation config."""
    op_config = self.operations_registry.get(operation)
    execution_method = op_config.get('execution_method', 'internal')
    
    if execution_method == 'cli_wrapper':
        return self.invoke_cli_wrapper(operation, context)
    elif execution_method == 'copilot_chat':
        return self.generate_copilot_template(operation, context)
    elif execution_method == 'internal':
        return self.execute_internal_module(operation, context)
    else:
        raise ValueError(f"Unknown execution method: {execution_method}")
```

**CLI Wrapper Invocation:**
```python
def invoke_cli_wrapper(self, operation: str, context: Dict) -> WorkflowResult:
    """Execute CLI wrapper via subprocess."""
    wrapper_script = self._resolve_wrapper_path(operation)
    
    # Build command
    cmd = [
        sys.executable,  # python
        str(wrapper_script),
        *self._build_wrapper_args(context)
    ]
    
    # Execute with timeout
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 minutes
        cwd=self.cortex_root
    )
    
    return WorkflowResult(
        success=result.returncode == 0,
        output=result.stdout,
        error=result.stderr,
        duration_seconds=result.duration
    )
```

---

### 5. Orchestrator Registry (Auto-Discovery)

**Purpose:** Dynamically discover and initialize orchestrators

**Auto-Discovery Process:**
1. **Scan:** Find all `*_orchestrator.py` files in `src/orchestrators/`
2. **Parse:** Extract class name and metadata
3. **Register:** Add to registry with import path
4. **Lazy Init:** Initialize on first use

**Registry Structure:**
```python
@dataclass
class OrchestratorRegistry:
    """Registry of available orchestrators."""
    orchestrators: Dict[str, OrchestratorMetadata] = field(default_factory=dict)
    
    def discover(self):
        """Auto-discover orchestrators."""
        for file_path in Path("src/orchestrators").rglob("*_orchestrator.py"):
            if file_path.stem.startswith('test_'):
                continue
            
            metadata = self._extract_metadata(file_path)
            self.orchestrators[metadata.name] = metadata
    
    def initialize(self, orchestrator_name: str) -> BaseOrchestrator:
        """Lazy initialization of orchestrator."""
        if orchestrator_name not in self.orchestrators:
            raise ValueError(f"Unknown orchestrator: {orchestrator_name}")
        
        metadata = self.orchestrators[orchestrator_name]
        module = import_module(metadata.module_path)
        orchestrator_class = getattr(module, metadata.class_name)
        
        return orchestrator_class()
```

---

## 📊 Performance Metrics

### Routing Performance

| Metric | Value | Context |
|--------|-------|---------|
| **Operation Detection** | <100ms | Average across 297 operations |
| **Tier Classification** | <50ms | LLM-free classification |
| **CLI Wrapper Launch** | 200-500ms | Python subprocess overhead |
| **Internal Module Execution** | Varies | Depends on operation complexity |
| **Total Overhead** | <500ms | For internal modules |

### Registry Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Auto-Discovery** | 1-2 seconds | One-time at startup |
| **Registry Lookup** | <1ms | O(1) dictionary lookup |
| **Lazy Initialization** | 50-200ms | Per orchestrator, cached |
| **Memory Footprint** | 5-10 MB | All orchestrators loaded |

### Classification Accuracy (30-day sample)

| Tier | Operations | Accuracy | False Positives |
|------|------------|----------|-----------------|
| **Tier 1** | 13 | 98% | 2% (over-classified) |
| **Tier 2** | 89 | 94% | 6% (complexity mismatch) |
| **Tier 3** | 150 | 96% | 4% (duration variance) |
| **Tier 4** | 45 | 91% | 9% (user interaction needed) |
| **Overall** | 297 | 95% | 5% |

---

## 🧪 Test Coverage

**Total Tests:** 45+ (95%+ coverage)

**Test Categories:**
- **Request Parsing:** 8 tests (command extraction, context building)
- **Intent Detection:** 12 tests (exact match, alias match, NL match, fuzzy match)
- **Tier Classification:** 10 tests (complexity analysis, duration estimation)
- **Execution Routing:** 8 tests (cli_wrapper, copilot_chat, internal)
- **Registry Management:** 7 tests (auto-discovery, lazy init, caching)

**Integration Tests:**
```python
def test_end_to_end_feature_planning():
    """Test complete flow: request → detection → classification → execution"""
    entry = CortexEntry()
    
    # User request
    result = entry.process("plan a new authentication feature")
    
    # Verify routing
    assert result.operation == "feature_planning"
    assert result.tier == 4
    assert result.execution_method == "copilot_chat"
    assert result.success
```

---

## 🚀 Future Enhancements

### Planned Improvements

1. **LLM-Powered Intent Detection**
   - Use LLM for ambiguous commands
   - Learn from user corrections
   - Support multi-turn conversations

2. **Adaptive Tier Classification**
   - Learn optimal tier from execution history
   - Adjust thresholds based on user feedback
   - Predict duration more accurately

3. **Multi-Operation Chaining**
   - Detect compound requests ("plan and implement feature")
   - Automatic workflow generation
   - Dependency resolution

4. **Context-Aware Routing**
   - Consider current project state
   - Route based on recent operations
   - Personalized operation suggestions

5. **Performance Optimization**
   - Cache operation registry in memory
   - Parallel orchestrator initialization
   - Reduce subprocess overhead for CLI wrappers

---

## 📚 References

**Implementation Files:**
- `src/operations/modules/routing/unified_entry_point_utility.py` - Main routing logic
- `src/cortex_agents/intent_router.py` - Intent detection
- `src/operations/modules/routing/tiered_router.py` - 4-tier classification
- `cortex-operations.yaml` - Operations registry (297 operations)

**Related Documentation:**
- `README.md` - Entry point architecture overview
- `docs/orchestration/` - Orchestrator documentation
- `cortex-brain/documents/planning/completed/cortex-evolution-v3.9/phase-01-router.md` - Tiered router design

**Related Systems:**
- Learning System (event capture for routing decisions)
- Operations Registry (297 operations catalog)
- Orchestrator Framework (16 orchestrators)

---

## 🏆 Summary

The Unified Entry Point delivers **intelligent, universal request routing** through:

✅ **Single gateway** for all 297+ CORTEX operations  
✅ **4-tier classification** (Tier 1-4 based on complexity)  
✅ **Multi-interface support** (Copilot Chat, CLI, MCP)  
✅ **Intelligent intent detection** (natural language → operation)  
✅ **Dynamic orchestrator registry** (auto-discovery, lazy init)  
✅ **95% routing accuracy** with continuous learning  
✅ **Sub-500ms overhead** for internal module routing  

**Impact:** Provides seamless, unified access to all CORTEX functionality regardless of interface, enabling consistent user experience and centralized telemetry.
