# Multi-Cycle TDD User Guide

**Authority:** WAVE-3 Stage 3 - ENH-088 Documentation  
**Version:** 1.0  
**Date:** 2026-02-13

---

## Overview

Multi-Cycle TDD enables iterative test-driven development with quality gates at each cycle. The TDD Orchestrator runs RED→GREEN→REFACTOR cycles until all success criteria are met, with automatic metrics tracking and holistic refactoring gates.

---

## Key Concepts

### SuccessCriteria

Define quality thresholds for TDD completion:

```python
from cortex.orchestrators.core.tdd_orchestrator import SuccessCriteria

criteria = SuccessCriteria(
    min_coverage=0.85,           # 85% code coverage required
    max_latency_ms=500,          # 500ms max test execution time
    extensibility_score=0.7,     # 70% extensibility threshold
    custom_checks=[]             # Optional custom validation functions
)
```

### CycleMetrics

Tracks metrics for each TDD cycle:

```python
@dataclass
class CycleMetrics:
    cycle_number: int            # Current cycle iteration
    tests_written: int           # Tests created this cycle
    tests_passing: int           # Tests passing this cycle
    tests_failing: int           # Tests still failing
    coverage_percent: float      # Code coverage achieved
    avg_latency_ms: float        # Average test execution time
```

### GateResult

Quality gate validation result:

```python
@dataclass
class GateResult:
    passed: bool                 # Whether all criteria met
    gaps: List[str]              # Unmet criteria descriptions
    recommendations: List[str]   # Suggested improvements
```

---

## Usage Patterns

### Basic Multi-Cycle Execution

```python
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator, SuccessCriteria

orchestrator = TDDOrchestrator()

# Define success criteria
criteria = SuccessCriteria(
    min_coverage=0.80,
    max_latency_ms=1000
)

# Execute multi-cycle TDD
result = orchestrator.execute_multi_cycle(
    feature_spec="User authentication with JWT tokens",
    success_criteria=criteria,
    max_cycles=5  # Safety limit
)

# Check result
if result.passed:
    print(f"✅ TDD complete after {result.cycle_number} cycles")
    print(f"Coverage: {result.coverage_percent}%")
else:
    print(f"⚠️ Gaps remain: {', '.join(result.gaps)}")
```

### Custom Success Criteria

```python
def custom_security_check() -> bool:
    """Custom check for security requirements."""
    # Verify authentication tests exist
    # Verify authorization tests exist
    # Verify input validation tests exist
    return all_security_tests_present()

criteria = SuccessCriteria(
    min_coverage=0.90,           # Higher coverage for security
    max_latency_ms=300,          # Stricter latency
    custom_checks=[
        custom_security_check,
        custom_performance_check
    ]
)
```

### Tracking Cycle Metrics

```python
orchestrator = TDDOrchestrator()

# Enable metric tracking
orchestrator.track_cycle_metrics(enabled=True)

# Execute cycles
result = orchestrator.execute_multi_cycle(
    feature_spec="Shopping cart checkout",
    success_criteria=criteria
)

# Retrieve metrics history
metrics = orchestrator.get_cycle_history()

for cycle in metrics:
    print(f"Cycle {cycle.cycle_number}:")
    print(f"  Coverage: {cycle.coverage_percent}%")
    print(f"  Tests: {cycle.tests_passing}/{cycle.tests_written}")
    print(f"  Latency: {cycle.avg_latency_ms}ms")
```

### Holistic Refactor Gate

The refactor gate ensures code quality before marking TDD complete:

```python
# Automatic gate check after all tests pass
gate_result = orchestrator.holistic_refactor_gate(
    coverage=0.87,
    latency_ms=450,
    success_criteria=criteria
)

if not gate_result.passed:
    print("Refactor needed:")
    for gap in gate_result.gaps:
        print(f"  - {gap}")
    
    for rec in gate_result.recommendations:
        print(f"  💡 {rec}")
```

---

## Event Integration

Multi-Cycle TDD emits events for monitoring and debugging:

```python
from cortex.core.event_bus import EventBus, Event

# Subscribe to TDD events
bus = EventBus(log_file=".cortex/events.jsonl")

def tdd_event_handler(event: Event):
    if event.type == "tdd.cycle.started":
        print(f"🔄 Cycle {event.payload['cycle_number']} started")
    elif event.type == "tdd.cycle.completed":
        metrics = event.payload['metrics']
        print(f"✅ Cycle complete: {metrics['coverage_percent']}% coverage")
    elif event.type == "tdd.gate.failed":
        gaps = event.payload['gaps']
        print(f"⚠️ Gate failed: {', '.join(gaps)}")

bus.subscribe("tdd.cycle.started", tdd_event_handler)
bus.subscribe("tdd.cycle.completed", tdd_event_handler)
bus.subscribe("tdd.gate.failed", tdd_event_handler)
```

---

## Best Practices

### 1. Set Realistic Criteria

```python
# ❌ Too strict - will never complete
criteria = SuccessCriteria(
    min_coverage=1.0,      # 100% coverage unrealistic
    max_latency_ms=10      # 10ms too strict
)

# ✅ Realistic for production
criteria = SuccessCriteria(
    min_coverage=0.80,     # 80% is industry standard
    max_latency_ms=500,    # 500ms reasonable
    extensibility_score=0.7
)
```

### 2. Use Max Cycles Safety Limit

```python
# Always set max_cycles to prevent infinite loops
result = orchestrator.execute_multi_cycle(
    feature_spec=spec,
    success_criteria=criteria,
    max_cycles=5  # Exit after 5 cycles regardless
)
```

### 3. Monitor Cycle Metrics

```python
# Enable tracking to diagnose issues
orchestrator.track_cycle_metrics(enabled=True)

# Check if stuck in a cycle
metrics = orchestrator.get_cycle_history()
if len(metrics) > 3:
    recent_coverage = [m.coverage_percent for m in metrics[-3:]]
    if max(recent_coverage) - min(recent_coverage) < 0.05:
        print("⚠️ Coverage plateau detected - review test strategy")
```

### 4. Leverage Custom Checks

```python
def check_edge_cases() -> bool:
    """Ensure edge cases are tested."""
    required_tests = [
        "test_empty_input",
        "test_null_input",
        "test_boundary_values",
        "test_concurrent_access"
    ]
    return all(test_exists(t) for t in required_tests)

criteria = SuccessCriteria(
    min_coverage=0.85,
    custom_checks=[check_edge_cases]
)
```

---

## Troubleshooting

### Issue: Cycles Not Converging

**Symptoms:** Multiple cycles with minimal coverage improvement

**Solutions:**
1. Review test strategy - are tests targeting right areas?
2. Check for test brittleness (use QualityValidator)
3. Verify mocks are not hiding real failures
4. Lower max_cycles to force manual review

### Issue: Gate Always Failing

**Symptoms:** Tests pass but gate fails

**Solutions:**
1. Check coverage threshold - may be too high
2. Verify latency measurement accuracy
3. Review custom_checks for bugs
4. Use `gate_result.recommendations` for guidance

### Issue: High Latency

**Symptoms:** avg_latency_ms exceeds threshold

**Solutions:**
1. Optimize test setup/teardown
2. Use mocks for external dependencies
3. Parallelize independent tests
4. Review database fixture performance

---

## Integration with CORTEX Orchestrators

### With EnforcementOrchestrator

```python
from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator

# Enforcement runs BEFORE each TDD cycle
enforcement = EnforcementOrchestrator()
tdd = TDDOrchestrator()

# Automatic enforcement at cycle start
result = tdd.execute_multi_cycle(
    feature_spec=spec,
    success_criteria=criteria,
    pre_cycle_hook=enforcement.validate_pre_execution
)
```

### With LENSSynthesis

```python
from cortex.orchestrators.core.lens_synthesis import LENSSynthesis

# LENS provides context for TDD
lens = LENSSynthesis()
tdd = TDDOrchestrator()

# Analyze codebase before TDD
analysis = lens.analyze_codebase(scope="authentication")

# Use analysis to inform TDD
result = tdd.execute_multi_cycle(
    feature_spec=f"Implement {analysis.recommended_approach}",
    success_criteria=criteria,
    context=analysis
)
```

---

## API Reference

### `execute_multi_cycle()`

**Signature:**
```python
def execute_multi_cycle(
    self,
    feature_spec: str,
    success_criteria: SuccessCriteria,
    max_cycles: int = 10,
    context: Optional[Dict[str, Any]] = None
) -> GateResult:
    """Execute multi-cycle TDD until criteria met or max_cycles reached."""
```

**Parameters:**
- `feature_spec`: Feature description for test generation
- `success_criteria`: Quality thresholds
- `max_cycles`: Maximum iterations (default 10)
- `context`: Optional additional context

**Returns:** `GateResult` with final status

### `track_cycle_metrics()`

**Signature:**
```python
def track_cycle_metrics(
    self,
    enabled: bool = True
) -> None:
    """Enable or disable cycle metrics tracking."""
```

### `holistic_refactor_gate()`

**Signature:**
```python
def holistic_refactor_gate(
    self,
    coverage: float,
    latency_ms: float,
    success_criteria: SuccessCriteria
) -> GateResult:
    """Validate if code meets all quality gates."""
```

**Parameters:**
- `coverage`: Current code coverage (0.0-1.0)
- `latency_ms`: Average test execution time
- `success_criteria`: Quality thresholds

**Returns:** `GateResult` with validation status

---

## Examples

### Example 1: API Endpoint Development

```python
criteria = SuccessCriteria(
    min_coverage=0.85,
    max_latency_ms=300,
    custom_checks=[
        lambda: test_exists("test_authentication"),
        lambda: test_exists("test_authorization"),
        lambda: test_exists("test_input_validation")
    ]
)

result = orchestrator.execute_multi_cycle(
    feature_spec="RESTful API endpoint for user registration",
    success_criteria=criteria,
    max_cycles=5
)
```

### Example 2: Database Integration

```python
def check_transaction_tests() -> bool:
    return all([
        test_exists("test_transaction_rollback"),
        test_exists("test_concurrent_writes"),
        test_exists("test_connection_pooling")
    ])

criteria = SuccessCriteria(
    min_coverage=0.90,  # Higher coverage for DB layer
    max_latency_ms=1000,  # Allow more time for DB tests
    custom_checks=[check_transaction_tests]
)

result = orchestrator.execute_multi_cycle(
    feature_spec="Database repository layer with transactions",
    success_criteria=criteria
)
```

---

## See Also

- **EventBus Debugger User Guide** - Event monitoring and debugging
- **TDD Orchestrator Wiring Spec** - `cortex/wiring/specifications/tdd_orchestrator.yaml`
- **Enforcement Rules** - `cortex-registry/governance/rules/core/`
- **Test Intelligence Layers** - `cortex/testing/intelligence/`

---

**Version:** 1.0 | **Last Updated:** 2026-02-13  
**Authority:** WAVE-3 Stage 3 - ENH-088 Multi-Cycle TDD Documentation
