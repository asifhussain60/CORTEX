# CORTEX Total Recall - Quick Reference Guide

**Last Updated:** January 23, 2026  
**Status:** ✅ PRODUCTION READY  
**Python Version:** 3.13.7  

---

## Quick Start - Basic Usage Patterns

### Initialize the System

```python
# Get the master orchestrator (singleton)
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
master = MasterOrchestrator.instance()

# Setup conversation for multi-turn interactions
from cortex.core.orchestrator.conversation_protocol import ConversationProtocol
conversation = ConversationProtocol(master, max_turns=10)

# Setup governance validation
from cortex.brain.core.governance_registry import GovernanceRegistry
governance = GovernanceRegistry()
```

### Execute an Operation

```python
# Single operation execution
context = {"operation": "ANALYZE", "scope": "module"}
violations = governance.evaluate_operation(context)

if not violations:
    result = master.execute_operation(context, governance_enabled=True)
    print(f"Operation result: {result}")
else:
    print(f"Governance violations: {violations}")
```

### Multi-Turn Conversation

```python
# Multi-turn conversation with continuation logic
for turn in range(1, 11):
    turn_result = conversation.execute_turn(
        user_input=f"Task for turn {turn}",
        round_number=turn,
        previous_context=result.context if turn > 1 else {}
    )
    
    if not turn_result.should_continue:
        break
    
    print(f"Turn {turn}: {turn_result.decision}")
```

### Use Intent Classification

```python
from cortex.intent_router.classifier import IntentClassifier

classifier = IntentClassifier()
result = classifier.classify("user input text")

print(f"Intent: {result.intent}")
print(f"Confidence: {result.confidence}")
print(f"Recommended orchestrator: {result.orchestrator}")
```

### Access MCP Tools

```python
from cortex.mcp.registry import get_mcp_tool_registry

# Get the tool registry
registry = get_mcp_tool_registry()

# List all tools
all_tools = registry.list_all()
print(f"Available tools: {len(all_tools)}")

# List tools by category
from cortex.mcp.registry import ToolCategory
governance_tools = registry.list_by_category(ToolCategory.GOVERNANCE)
```

### Register a Custom MCP Tool

```python
from cortex.mcp.decorators import mcp_tool

@mcp_tool(
    name="analyze_code",
    description="Analyze Python code structure",
    parameters={"code": "string", "depth": "int"}
)
def analyze_code(code: str, depth: int = 1) -> dict:
    """Analyze code and return structure."""
    return {
        "lines": len(code.split("\n")),
        "depth": depth,
        "analysis": "complete"
    }
```

### Structured Logging

```python
from cortex.infrastructure.structured_logger import StructuredLogger

logger = StructuredLogger("my_module")

# Log with context
logger.info(
    "Operation started",
    context={
        "operation_id": "op_123",
        "user": "user@example.com",
        "scope": "module"
    }
)

# PII is automatically redacted
logger.warn(
    "Sensitive operation",
    context={
        "email": "user@example.com",  # Auto-redacted
        "ssn": "123-45-6789"  # Auto-redacted
    }
)
```

### Track Metrics

```python
from cortex.infrastructure.prometheus_metrics import MetricsCollector

metrics = MetricsCollector()

# Track operation duration
with metrics.track_operation("my_operation"):
    # Your operation here
    pass

# Record custom metric
metrics.record_gauge("custom_metric", 42.0)
```

### Distributed Tracing

```python
from cortex.infrastructure.tracing import TracingCollector, TracingConfig

config = TracingConfig(
    service_name="my_service",
    environment="production",
    sample_rate=0.1
)
tracer = TracingCollector(config)

# Create trace context
trace_context = tracer.create_trace_context()

# Use in operations
with tracer.start_span("my_operation", trace_context) as span:
    # Your operation here
    pass
```

### Resilient Operations

```python
from cortex.infrastructure.circuit_breaker import CircuitBreaker
from cortex.infrastructure.retry_strategy import RetryStrategy

@CircuitBreaker(failure_threshold=5, recovery_timeout=30)
@RetryStrategy(max_attempts=3, backoff_base=2)
def call_external_service():
    """Protected operation with automatic retry and circuit break."""
    # Your code here
    pass
```

### State Management with Optimistic Locking

```python
from cortex.infrastructure.transaction_manager import TransactionManager
from cortex.core.state.optimistic_lock import OptimisticLock

with TransactionManager() as tx:
    with OptimisticLock(resource_id="user_123", version=1) as lock:
        # Perform concurrent-safe operations
        lock.update_value("field", "new_value")
        tx.commit()
```

### Saga Pattern for Distributed Transactions

```python
from cortex.core.recovery.saga_coordinator import SagaCoordinator

saga = SagaCoordinator()

# Add steps with compensation
saga.add_step(
    "create_order",
    create_order_fn,
    cancel_order_fn  # Compensation function
)

saga.add_step(
    "charge_payment",
    charge_payment_fn,
    refund_payment_fn  # Compensation function
)

result = saga.execute()
if result.failed:
    # Automatic compensation already triggered
    print(f"Transaction failed: {result.error}")
```

### Get Routing Intelligence

```python
from cortex.core.intelligence.routing_intelligence import RoutingAnalyzer

analyzer = RoutingAnalyzer()

# Record decision
analyzer.record_decision(
    intent="ANALYZE",
    orchestrator="DataAnalysisOrchestrator",
    outcome="SUCCESS"
)

# Get accuracy report
report = analyzer.get_accuracy_report()
print(f"Routing accuracy: {report.accuracy_score}")
```

---

## Component Quick Reference

| Component | Import | Purpose |
|-----------|--------|---------|
| **MasterOrchestrator** | `from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator` | Main orchestration engine |
| **IntentClassifier** | `from cortex.intent_router.classifier import IntentClassifier` | Classify user intents |
| **GovernanceRegistry** | `from cortex.brain.core.governance_registry import GovernanceRegistry` | Validate operations |
| **MCP Registry** | `from cortex.mcp.registry import get_mcp_tool_registry` | Tool management |
| **ConversationProtocol** | `from cortex.core.orchestrator.conversation_protocol import ConversationProtocol` | Multi-turn orchestration |
| **CircuitBreaker** | `from cortex.infrastructure.circuit_breaker import CircuitBreaker` | Fault tolerance |
| **StructuredLogger** | `from cortex.infrastructure.structured_logger import StructuredLogger` | JSON logging |
| **MetricsCollector** | `from cortex.infrastructure.prometheus_metrics import MetricsCollector` | Metrics tracking |
| **TracingCollector** | `from cortex.infrastructure.tracing import TracingCollector` | Distributed tracing |
| **OptimisticLock** | `from cortex.core.state.optimistic_lock import OptimisticLock` | Concurrency control |
| **SagaCoordinator** | `from cortex.core.recovery.saga_coordinator import SagaCoordinator` | Distributed transactions |

---

## Common Tasks

### Task: Check System Health

```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.mcp.registry import get_mcp_tool_registry

# Check orchestrator
master = MasterOrchestrator.instance()
print(f"Orchestrator: {type(master).__name__}")

# Check governance
gov = GovernanceRegistry()
print("Governance: Loaded")

# Check MCP tools
registry = get_mcp_tool_registry()
print(f"Tools registered: {registry.count()}")
```

### Task: Execute with Full Governance

```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.brain.core.governance_registry import GovernanceRegistry

master = MasterOrchestrator.instance()
governance = GovernanceRegistry()

operation = {
    "type": "IMPLEMENT",
    "scope": "module",
    "constraints": ["incremental", "tested"]
}

# Pre-validate
violations = governance.evaluate_operation(operation)

if violations:
    print(f"Blocked: {violations}")
else:
    result = master.execute_operation(operation, governance_enabled=True)
    print(f"Success: {result}")
```

### Task: Handle External Call Safely

```python
from cortex.infrastructure.circuit_breaker import CircuitBreaker
from cortex.infrastructure.retry_strategy import RetryStrategy

@CircuitBreaker(failure_threshold=5, recovery_timeout=60)
@RetryStrategy(max_attempts=3, backoff_base=2)
def safe_external_call(url: str):
    """Call external API with protection."""
    import requests
    return requests.get(url, timeout=10).json()

try:
    result = safe_external_call("https://api.example.com/data")
except Exception as e:
    print(f"Call failed after retries: {e}")
```

### Task: Track Operation Performance

```python
from cortex.infrastructure.structured_logger import StructuredLogger
from cortex.infrastructure.prometheus_metrics import MetricsCollector
from cortex.infrastructure.tracing import TracingCollector, TracingConfig

logger = StructuredLogger("my_operation")
metrics = MetricsCollector()
tracer = TracingCollector(TracingConfig("my_service"))

trace_ctx = tracer.create_trace_context()

with tracer.start_span("operation", trace_ctx) as span:
    with metrics.track_operation("my_operation"):
        logger.info("Operation started", context={"trace_id": trace_ctx.trace_id})
        # Do work
        logger.info("Operation completed", context={"duration": "1.5s"})
```

---

## Troubleshooting

### Issue: MasterOrchestrator not initializing

```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

try:
    master = MasterOrchestrator.instance()
    print("OK: Orchestrator initialized")
except Exception as e:
    print(f"ERROR: {e}")
    # Check: Python 3.13.7 installed?
    # Check: All dependencies installed?
```

### Issue: Governance violations blocking operations

```python
from cortex.brain.core.governance_registry import GovernanceRegistry

gov = GovernanceRegistry()

# Check what rules are active
print("Governance rules loaded")

# Evaluate specific operation
context = {"operation": "TEST", "scope": "module"}
violations = gov.evaluate_operation(context)

if violations:
    print(f"Violations: {violations}")
    # Adjust operation to comply with rules
```

### Issue: MCP Tools not registering

```python
from cortex.mcp.registry import get_mcp_tool_registry

registry = get_mcp_tool_registry()
print(f"Registry status: {registry.summary()}")

# Check tool registration
from cortex.mcp.decorators import mcp_tool, get_registered_tools
tools = get_registered_tools()
print(f"Decorated tools: {len(tools)}")
```

---

## Performance Tips

1. **Use MasterOrchestrator singleton** - Don't create multiple instances
2. **Cache IntentClassifier results** - Classification can be expensive
3. **Batch metrics writes** - MetricsCollector batches automatically
4. **Use connection pooling** - ConnectionPool manages connections
5. **Sample traces in production** - Use `sample_rate=0.01` for high-volume
6. **Log with context** - Structured logging helps with debugging
7. **Monitor circuit breakers** - Watch failure rates to tune thresholds

---

## Environment Variables

```bash
# Logging
export LOG_LEVEL=INFO
export LOG_FORMAT=json

# Metrics
export METRICS_ENABLED=true
export METRICS_PORT=9090

# Tracing
export JAEGER_HOST=localhost
export JAEGER_PORT=6831
export TRACE_SAMPLE_RATE=0.1

# Database
export DATABASE_URL=sqlite:///cortex.db

# API
export API_HOST=0.0.0.0
export API_PORT=8000
```

---

## Further Reading

- **Full Documentation:** `.github/prompts/CORTEX-TOTAL-RECALL-VERIFICATION.md`
- **Authority:** `.github/prompts/cortex-total-recall.prompt.md`
- **Implementation Map:** `cortex-impl-map.yaml`
- **Configuration:** `cortex-config.yaml`

---

**Status:** ✅ PRODUCTION READY  
**Last Verified:** January 23, 2026  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

