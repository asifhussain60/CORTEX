# Master Orchestrator

**Status:** Production Ready | **Version:** 1.0.0 | **Category:** Core Orchestrators | **Module:** `cortex/orchestrators/core/master_orchestrator.py`

---

## Overview

The **MasterOrchestrator** is the central coordinator and facade for the entire CORTEX orchestration system. It implements the **Coordinator/Facade pattern** to manage complex, multi-step operations by intelligently delegating work to specialized domain orchestrators.

### Purpose

- Centralized entry point for all orchestration operations
- Coordinates interactions between multiple domain orchestrators
- Manages cross-cutting concerns (audit, state, governance)
- Aggregates results from multiple orchestrators
- Maintains comprehensive audit trail for compliance
- Enforces governance rules and behavioral boundaries

---

## Architecture

### Design Pattern: Coordinator Facade

The MasterOrchestrator uses the **Coordinator pattern** combined with the **Facade pattern**:

```
┌──────────────────────────────┐
│   Client/External Interface  │
└──────────────┬───────────────┘
               │ Request
               ▼
┌──────────────────────────────┐
│   MasterOrchestrator         │
│  (Coordinator/Facade)        │
│                              │
│  - Routes to domain orchs    │
│  - Aggregates results        │
│  - Manages state & audit     │
└──────┬───┬────────┬──────┬───┘
       │   │        │      │
       │   │        │      └─────────────────────┐
       │   │        │                            │
    ┌──▼─┐├─┐  ┌────┴─┐  ┌──────────────┐  ┌────▼──┐
    │Ac  ││Go│  │Audit │  │Governance    │  │Custom │
    │Orch││v │  │Orch  │  │Orch          │  │Orch   │
    └────┘└─┘  └──────┘  └──────────────┘  └───────┘
```

### Key Components

1. **Domain Orchestrator Registry**
   - Maintains registry of all registered domain orchestrators
   - Maps domains to orchestrator instances
   - Lazy-loads orchestrators on demand
   - Type: `Dict[str, OrchestratorMetadata]`

2. **Operation Router**
   - Analyzes incoming operations
   - Determines applicable domain orchestrators
   - Routes based on operation type, domain, and context
   - Implements confidence scoring for decisions

3. **Result Aggregator**
   - Collects results from multiple orchestrators
   - Merges result data intelligently
   - Handles conflicts and contradictions
   - Produces unified response

4. **Audit & Logging**
   - Logs all delegation decisions
   - Maintains operation history
   - Generates hash-chain audit trail
   - Tracks execution flow

5. **State Manager Integration**
   - Maintains cross-phase state consistency
   - Persists state between operations
   - Provides state context to orchestrators
   - Enables state recovery

6. **Governance Integration**
   - Enforces TIER 0 governance rules
   - Validates operations against boundaries
   - Manages compliance requirements
   - Tracks governance violations

---

## How It Works

### Operation Flow

```
1. REQUEST ARRIVES
   └─ Operation request with context/parameters

2. INTAKE & VALIDATION
   ├─ Validate request format
   ├─ Check governance rules (TIER 0)
   ├─ Enforce behavioral boundaries
   └─ Log operation initiation

3. ROUTING DECISION
   ├─ Analyze operation characteristics
   ├─ Determine applicable domains
   ├─ Score confidence (0.0-1.0)
   └─ Select orchestrators if confidence ≥ 0.7

4. DELEGATION
   ├─ Invoke primary orchestrator
   ├─ Invoke fallback/secondary orchestrators
   ├─ Monitor execution with timeout
   └─ Collect results

5. AGGREGATION
   ├─ Merge results from all orchestrators
   ├─ Resolve conflicts intelligently
   ├─ Enrich with master context
   └─ Format unified response

6. AUDIT & PERSISTENCE
   ├─ Write operation to audit log
   ├─ Update state manager
   ├─ Generate completion event
   └─ Invoke post-operation hooks

7. RESPONSE
   └─ Return aggregated results to client
```

### Key Algorithms

#### 1. Confidence Scoring
```python
def score_routing_decision(operation, domains) -> float:
    """
    Score = (domain_match_score * 0.4) +
            (operation_history_score * 0.3) +
            (context_relevance * 0.2) +
            (orchestrator_availability * 0.1)
    
    Range: 0.0 (no confidence) to 1.0 (high confidence)
    Threshold for auto-execution: 0.7
    """
```

#### 2. Result Aggregation Strategy
```python
def aggregate_results(results_list):
    """
    For multiple orchestrator results:
    1. Collect all output objects
    2. Merge data structures (prefer non-empty values)
    3. Combine metadata (timestamps, durations)
    4. Resolve conflicts by voting/priority
    5. Create unified response wrapper
    """
```

### State Management

The MasterOrchestrator maintains state across phases:

| State Type | Storage | Purpose |
|-----------|---------|---------|
| **Operation State** | StateManager | Tracks current operation progress |
| **Domain State** | Database | Persists domain-specific data |
| **Audit State** | Audit Log | Maintains compliance history |
| **Governance State** | Governance Registry | Tracks rule violations |

---

## How to Use It

### Basic Usage

```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

# Get singleton instance
master = MasterOrchestrator.instance()

# Register a domain orchestrator
master.register_orchestrator(
    domain="financial",
    orchestrator=financial_orch,
    capabilities=["transaction_processing", "reconciliation"]
)

# Execute an operation
result = master.execute_operation(
    operation_name="process_payments",
    context={
        "domain": "financial",
        "operation_type": "batch",
        "batch_size": 1000
    }
)

# Check result
if result.is_ok():
    print(f"Operation succeeded: {result.value}")
else:
    print(f"Operation failed: {result.error}")
```

### Advanced Usage Patterns

#### Pattern 1: Multi-Domain Operation
```python
# Operation that spans multiple domains
result = master.coordinate_operation(
    operation="cross_domain_audit",
    context={
        "domains": ["financial", "governance", "audit"],
        "scope": "full_system",
        "report_to": "compliance_team"
    }
)
```

#### Pattern 2: Custom Routing
```python
# Override default routing with custom logic
result = master.execute_with_routing(
    operation="custom_workflow",
    routing_strategy=CustomRoutingStrategy(),
    context=custom_context
)
```

#### Pattern 3: Fallback Orchestrators
```python
# Specify fallback options for resilience
result = master.execute_with_fallbacks(
    operation="critical_operation",
    primary_domain="financial",
    fallback_domains=["governance", "audit"],
    timeout=60
)
```

### Configuration

The MasterOrchestrator reads configuration from:

```yaml
# cortex_brain/tier0/orchestrator-config.yaml

master_orchestrator:
  # Routing settings
  confidence_threshold: 0.7
  timeout_seconds: 300
  
  # State management
  state_persistence: true
  state_cache_ttl: 3600
  
  # Audit settings
  audit_level: "comprehensive"
  hash_chain_enabled: true
  
  # Governance
  enforce_tier0_rules: true
  boundary_check_mode: "strict"
  
  # Optimization
  parallel_orchestrator_execution: true
  max_parallel_tasks: 10
  result_caching: true
  cache_ttl: 1800
```

---

## Integration Points

### Dependencies

- **EnhancedAuditLogger**: Audit trail logging
- **StateManager**: Cross-phase state management
- **DatabaseTransactionManager**: Atomic operations
- **GovernanceRegistry**: Rule enforcement
- **BehavioralBoundaryRules**: Boundary enforcement
- **KnowledgeRepository**: Best practices
- **BusinessKnowledgeRepository**: Domain knowledge

### Dependents

- All domain orchestrators
- All custom orchestrators
- Intent Router (for stage 2 delegation)
- Workflow Orchestrator (for stage coordination)

### MCP Tools Exposed

The MasterOrchestrator exposes the following MCP tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `register_orchestrator` | Register domain orchestrator | domain, orchestrator, capabilities |
| `get_orchestrator` | Get orchestrator instance | domain |
| `coordinate_operation` | Coordinate multi-orchestrator operation | operation, context |
| `get_registered_domains` | List registered domains | (none) |
| `get_operation_history` | Get operation history | limit, domain_filter |
| `audit_operation` | Get audit trail for operation | operation_id |
| `validate_operation` | Pre-validate operation | operation, context |

### Registry Entries

Registered in `cortex/orchestrators/registry/orchestrator_registry.py`:

```python
ORCHESTRATOR_METADATA = {
    "master-orchestrator": {
        "domain": "core",
        "version": "1.0.0",
        "capabilities": [
            "coordination",
            "multi_domain_orchestration",
            "result_aggregation",
            "audit_logging",
            "state_management",
            "governance_enforcement"
        ]
    }
}
```

---

## Design Principles

### 1. Single Responsibility Principle (SRP)
Each domain orchestrator has ONE responsibility. MasterOrchestrator only coordinates.

### 2. Open/Closed Principle (OCP)
Open for extension (new domains) via registry, closed for modification.

### 3. Liskov Substitution Principle (LSP)
All orchestrators implement `IOrchestrator` interface consistently.

### 4. Interface Segregation Principle (ISP)
Minimal, focused interfaces for each orchestrator type.

### 5. Dependency Inversion Principle (DIP)
Depends on abstractions (IOrchestrator), not concrete implementations.

---

## Governance Rules Enforced

### TIER 0 Rules (Non-Negotiable)

| Rule | Impact | Action |
|------|--------|--------|
| CORE-008 | TDD enforcement | Verify tests exist before code |
| CORE-011 | Type hints mandatory | Reject un-typed operations |
| CORE-012 | Docstring requirement | Validate documentation |
| CORE-013 | No bare except | Reject bare exception handlers |
| CORE-029 | Response header format | Wrap response with mandated header |

### Domain-Specific Rules

- **Financial**: SOX, PCI-DSS compliance
- **Healthcare**: HIPAA compliance
- **E-Commerce**: PCI-DSS payment requirements
- **Audit**: Complete audit trail

---

## Error Handling Strategy

### Error Classification

```
┌─ VALIDATION ERRORS (recoverable)
│  └─ Retry with different parameters
│
├─ ROUTING ERRORS (fallback available)
│  └─ Route to fallback orchestrator
│
├─ EXECUTION ERRORS (retry possible)
│  └─ Retry with exponential backoff
│
├─ GOVERNANCE ERRORS (blocking)
│  └─ Halt operation, log violation
│
└─ CRITICAL ERRORS (system-level)
   └─ Escalate to admin, trigger alerting
```

### Recovery Strategies

| Error Type | Strategy 1 | Strategy 2 | Strategy 3 |
|-----------|-----------|-----------|-----------|
| Validation | Fix & retry | Use default | Abort |
| Routing | Fallback orch | Manual route | Abort |
| Execution | Retry + backoff | Alternative approach | Abort |
| Governance | Log violation | Alert admin | Abort |
| Critical | Alert + escalate | Failover system | Manual intervention |

---

## Performance Characteristics

### Execution Time Breakdown

| Phase | Typical Duration | Notes |
|-------|-----------------|-------|
| Intake & Validation | 5-10ms | Governance checks |
| Routing Decision | 10-20ms | Confidence scoring |
| Orchestrator Invocation | 100-500ms | Domain-dependent |
| Result Aggregation | 10-50ms | Merge complexity-dependent |
| Audit & Persistence | 20-100ms | Log size-dependent |
| **Total** | **~200-700ms** | Varies by domain & complexity |

### Scalability

- **Parallel Orchestrators**: Up to 10 concurrent domain orchestrators
- **Result Aggregation**: O(n) where n = number of orchestrators
- **Audit Log**: Append-only, scales linearly
- **Registry**: O(1) lookup by domain

---

## Testing

### Unit Tests
- Located in: `tests/unit/orchestrators/test_master_orchestrator.py`
- Coverage: ~95%
- Key test suites:
  - Registration and discovery
  - Routing logic and confidence scoring
  - Result aggregation
  - Audit trail generation
  - Governance enforcement

### Integration Tests
- Located in: `tests/integration/orchestrators/test_master_integration.py`
- Scenarios:
  - Multi-domain operations
  - Fallback mechanisms
  - State persistence
  - Cross-orchestrator communication

### Test Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| Core routing | 98% | ✅ |
| Result aggregation | 94% | ✅ |
| Audit logging | 100% | ✅ |
| Governance enforcement | 96% | ✅ |
| State management | 91% | ✅ |

---

## Best Practices

### DO ✅

- Register orchestrators at startup
- Use confidence scoring for automatic routing
- Implement fallback orchestrators for critical operations
- Log all operations with full context
- Validate governance rules before execution
- Cache results when safe to do so
- Use timeouts for all operations
- Aggregate results intelligently

### DON'T ❌

- Register orchestrators multiple times for same domain
- Ignore governance violations
- Execute operations without audit trail
- Skip confidence scoring
- Neglect error handling
- Assume orchestrator availability
- Ignore state management requirements
- Execute unbounded operations

---

## Example Workflows

### Workflow 1: Financial Transaction Processing

```python
# Step 1: Register financial orchestrator
master.register_orchestrator(
    domain="financial",
    orchestrator=FinancialOrchestrator(),
    capabilities=["transaction", "reconciliation"]
)

# Step 2: Execute operation
result = master.execute_operation(
    operation_name="process_batch_payments",
    context={
        "domain": "financial",
        "batch_size": 1000,
        "priority": "high"
    }
)

# Step 3: Results include:
# - Transaction summary
# - Reconciliation report
# - Audit trail
# - Compliance attestation
```

### Workflow 2: Cross-Domain Audit

```python
# Execute operation across multiple domains
result = master.coordinate_operation(
    operation="system_audit",
    context={
        "scope": ["financial", "governance", "audit"],
        "report_format": "comprehensive"
    }
)

# Results aggregated from:
# - Financial: Transaction audit
# - Governance: Compliance check
# - Audit: Trail verification
```

### Workflow 3: Resilient Critical Operation

```python
# Execute with fallback chain
result = master.execute_with_fallbacks(
    operation="critical_update",
    primary_domain="financial",
    fallback_domains=["governance", "audit"],
    timeout=300,
    retry_count=3
)

# MasterOrchestrator will:
# 1. Try financial orchestrator
# 2. If fails, try governance orchestrator
# 3. If fails, try audit orchestrator
# 4. Return best available result
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No orchestrator for domain" | Domain not registered | Register orchestrator first |
| Low confidence score | Ambiguous routing context | Provide more specific context |
| Timeout errors | Orchestrator is slow | Increase timeout or use async |
| Governance violation | Rule enforcement active | Check TIER 0 rules |
| State not persisting | StateManager not initialized | Verify database connection |

### Debug Mode

```python
# Enable debug logging
master.enable_debug_logging()

# Get detailed operation trace
trace = master.get_operation_trace(operation_id)
print(trace.to_json())

# Get performance metrics
metrics = master.get_performance_metrics()
print(f"Avg routing time: {metrics['avg_routing_ms']}ms")
```

---

## Related Documentation

- 📖 [Intent Router](02-intent-router.md) - Stage 2 routing
- 📖 [Workflow Orchestrator](03-workflow-orchestrator.md) - Stage coordination
- 📖 [Orchestrator Registry](../patterns/registry-pattern.md) - Discovery system
- 📖 [Governance Rules](../patterns/governance-enforcement.md) - Rule engine
- 📊 [Architecture Overview](01-architecture-overview.md) - System diagram

---

## Copyright & License

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

CORTEX Framework - Master Orchestrator Module
Status: Production Ready | Version: 1.0.0

---

**Last Updated:** 2026-01-22 | **Author:** CORTEX Documentation Generator
