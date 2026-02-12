# Cross-Orchestrator Coordination

**Purpose:** Documentation of orchestrator coordination patterns  
**Audience:** Architects, Senior Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Coordination Patterns](#coordination-patterns)
- [Event-Driven Communication](#event-driven-communication)
- [State Management](#state-management)
- [Conflict Resolution](#conflict-resolution)
- [Performance Considerations](#performance-considerations)
- [Related Documents](#related-documents)

---

## Overview

CORTEX orchestrators coordinate through well-defined patterns that ensure consistency, performance, and reliability. This document describes how orchestrators communicate and work together.

### Coordination Principles

1. **Single Responsibility** — Each orchestrator owns its domain
2. **Loose Coupling** — Minimal direct dependencies
3. **Event-Driven** — Async communication where possible
4. **Hierarchical Authority** — MasterOrchestrator as coordinator
5. **Graceful Degradation** — Fallback chains

---

## Coordination Patterns

### Pattern 1: Hierarchical Delegation

```
┌─────────────────────────────────────────────────────────────────┐
│                HIERARCHICAL DELEGATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                  ┌─────────────────────┐                        │
│                  │  MasterOrchestrator │                        │
│                  └──────────┬──────────┘                        │
│                             │                                    │
│            ┌────────────────┼────────────────┐                  │
│            ▼                ▼                ▼                  │
│  ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐       │
│  │  IntentRouter   │ │   LENS     │ │ Enforcement     │       │
│  └─────────────────┘ └─────────────┘ └─────────────────┘       │
│            │                                                     │
│            ▼                                                     │
│  ┌─────────────────┐                                            │
│  │ Target Handler  │                                            │
│  └─────────────────┘                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Usage:** Standard request processing flow.

**Implementation:**
```python
async def delegate_hierarchically(
    self,
    request: Request,
    context: Context
) -> Result:
    """Delegate through hierarchy."""
    # Step 1: Route
    routing = await self.intent_router.route(request)
    
    # Step 2: Enrich
    enriched = await self.lens.enrich(routing, context)
    
    # Step 3: Validate
    validated = await self.enforcement.validate(enriched)
    
    # Step 4: Execute
    return await routing.target_handler.execute(validated)
```

---

### Pattern 2: Chain of Responsibility

```
┌─────────────────────────────────────────────────────────────────┐
│                CHAIN OF RESPONSIBILITY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Request → [Handler 1] → [Handler 2] → [Handler 3] → Response  │
│                 │             │             │                    │
│                 ▼             ▼             ▼                    │
│              Handle?       Handle?       Handle?                │
│                │             │             │                    │
│             (pass)        (pass)       (handle)                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Usage:** Finding appropriate handler for operation.

**Implementation:**
```python
async def execute_chain(
    self,
    request: Request,
    handlers: List[IOrchestrator]
) -> Optional[Result]:
    """Execute chain until handler found."""
    for handler in handlers:
        if await handler.can_handle(request):
            return await handler.execute(request)
    return None
```

---

### Pattern 3: Parallel Aggregation

```
┌─────────────────────────────────────────────────────────────────┐
│                PARALLEL AGGREGATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌──────────────┐                             │
│                    │   Request    │                             │
│                    └──────┬───────┘                             │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                    │
│         ▼                 ▼                 ▼                    │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │ Analyzer 1  │   │ Analyzer 2  │   │ Analyzer 3  │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                    │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                      │
│                    ┌──────────────┐                             │
│                    │  Aggregator  │                             │
│                    └──────────────┘                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Usage:** LENS analysis with multiple analyzers.

**Implementation:**
```python
async def aggregate_parallel(
    self,
    request: Request,
    analyzers: List[Analyzer]
) -> AggregatedResult:
    """Run analyzers in parallel and aggregate."""
    tasks = [
        asyncio.create_task(analyzer.analyze(request))
        for analyzer in analyzers
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = [r for r in results if not isinstance(r, Exception)]
    
    return self.aggregator.combine(successful)
```

---

### Pattern 4: Saga (Distributed Transaction)

```
┌─────────────────────────────────────────────────────────────────┐
│                      SAGA PATTERN                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Forward Path:                                                   │
│  [Step 1] ──✓──> [Step 2] ──✓──> [Step 3] ──✓──> Complete      │
│                                                                  │
│  Compensation (on failure at Step 3):                           │
│  [Comp 3] ◄──── [Comp 2] ◄──── [Comp 1] ◄──── Failed           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Usage:** Multi-step operations requiring atomicity.

**Implementation:**
```python
async def execute_saga(
    self,
    steps: List[SagaStep]
) -> SagaResult:
    """Execute saga with compensation."""
    completed = []
    
    try:
        for step in steps:
            result = await step.execute()
            completed.append((step, result))
            
            if not result.success:
                raise SagaStepFailed(step, result)
        
        return SagaResult(success=True, steps=completed)
        
    except SagaStepFailed as e:
        # Compensate in reverse order
        for step, _ in reversed(completed):
            await step.compensate()
        
        return SagaResult(
            success=False,
            failed_step=e.step,
            compensated=True
        )
```

---

### Pattern 5: Circuit Breaker

```
┌─────────────────────────────────────────────────────────────────┐
│                  CIRCUIT BREAKER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  States:                                                         │
│                                                                  │
│  ┌──────────┐    failures     ┌──────────┐                     │
│  │  CLOSED  │ ───────────────>│   OPEN   │                     │
│  │(normal)  │                 │(blocking)│                     │
│  └────┬─────┘                 └────┬─────┘                     │
│       │                            │                            │
│       │<──────────────────────────┐│                            │
│       │       success             ││                            │
│       │                           ▼│ timeout                    │
│  ┌────┴─────┐               ┌──────────┐                       │
│  │  CLOSED  │<──────────────│HALF-OPEN │                       │
│  └──────────┘    success    │(testing) │                       │
│                             └──────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Usage:** Protecting against cascading failures.

**Implementation:**
```python
class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure: Optional[datetime] = None
    
    async def call(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError()
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

---

## Event-Driven Communication

### Event Types

```python
class OrchestrationEvent(Enum):
    """Events for orchestrator communication."""
    
    # Lifecycle events
    REQUEST_RECEIVED = "request.received"
    REQUEST_ROUTED = "request.routed"
    REQUEST_COMPLETED = "request.completed"
    REQUEST_FAILED = "request.failed"
    
    # Governance events
    GOVERNANCE_PASSED = "governance.passed"
    GOVERNANCE_BLOCKED = "governance.blocked"
    
    # Execution events
    EXECUTION_STARTED = "execution.started"
    EXECUTION_CHECKPOINT = "execution.checkpoint"
    EXECUTION_COMPLETED = "execution.completed"
```

### Event Bus

```python
class OrchestratorEventBus:
    """Central event bus for orchestrator communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(
        self,
        event_type: OrchestrationEvent,
        handler: Callable
    ):
        """Subscribe to event type."""
        key = event_type.value
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(handler)
    
    async def publish(
        self,
        event: Event
    ):
        """Publish event to subscribers."""
        handlers = self._subscribers.get(event.type.value, [])
        
        await asyncio.gather(*[
            handler(event)
            for handler in handlers
        ])
```

---

## State Management

### Shared State

```python
@dataclass
class OrchestrationState:
    """Shared state across orchestrators."""
    
    request_id: str
    started_at: datetime
    current_stage: str
    
    # Routing
    intent: IntentType
    target_orchestrator: str
    confidence: float
    
    # Context
    lens_context: UnifiedIntelligenceContext
    governance_result: GovernanceResult
    
    # Execution
    checkpoints: List[Checkpoint]
    artifacts: List[str]
    
    # Status
    status: ExecutionStatus
    error: Optional[str] = None
```

### State Transitions

```
┌─────────────────────────────────────────────────────────────────┐
│                   STATE TRANSITIONS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RECEIVED → ROUTING → ENRICHING → VALIDATING → EXECUTING       │
│                                                                  │
│               ↓           ↓            ↓           ↓            │
│                                                                  │
│            FAILED      FAILED      BLOCKED      FAILED          │
│                                                                  │
│                                                                  │
│  EXECUTING → PROCESSING → DELIVERING → COMPLETED                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conflict Resolution

### Priority-Based Resolution

```python
def resolve_conflict(
    self,
    orchestrators: List[IOrchestrator],
    context: Context
) -> IOrchestrator:
    """Resolve conflicting orchestrator claims."""
    # Sort by priority (lower = higher precedence)
    by_priority = sorted(
        orchestrators,
        key=lambda o: o.priority
    )
    
    # Check capability match
    for orchestrator in by_priority:
        if orchestrator.can_handle(context):
            return orchestrator
    
    # Fallback to MasterOrchestrator
    return self.master_orchestrator
```

### Capability Negotiation

```python
def negotiate_capabilities(
    self,
    required: Set[str],
    available: List[IOrchestrator]
) -> Optional[IOrchestrator]:
    """Find orchestrator with all required capabilities."""
    for orchestrator in available:
        if required.issubset(set(orchestrator.capabilities)):
            return orchestrator
    
    # Try combination
    combination = self._find_combination(required, available)
    if combination:
        return CompositeOrchestrator(combination)
    
    return None
```

---

## Performance Considerations

### Coordination Overhead

| Pattern | Overhead | Use When |
|---------|----------|----------|
| Hierarchical | Low (5ms) | Standard requests |
| Chain | Medium (10ms) | Unknown handler |
| Parallel | Variable | Independent operations |
| Saga | High (50ms+) | Atomic multi-step |
| Circuit Breaker | Minimal | External calls |

### Optimization Strategies

1. **Cache Routing Decisions** — Avoid repeated classification
2. **Parallel Where Possible** — Run independent operations concurrently
3. **Short-Circuit** — Skip unnecessary steps
4. **Pool Orchestrators** — Reuse instances

---

## Related Documents

- [Orchestration Overview](overview.md) — Architecture
- [MasterOrchestrator](master-orchestrator.md) — Coordinator
- [End-to-End Flow](end-to-end-flow.md) — Complete lifecycle

---

*Part of CORTEX Architecture Documentation*
