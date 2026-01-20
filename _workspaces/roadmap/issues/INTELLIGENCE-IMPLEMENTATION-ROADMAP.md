# CORTEX Intelligence Enhancement - Technical Implementation Roadmap

**Status**: Implementation ready  
**Date**: 2026-01-20  
**Target Completion**: 3-4 working days  
**Governance**: CORE-008 TDD + full compliance

---

## Module Specifications

### Module 1: Routing Intelligence (`routing_intelligence.py`)

**Purpose**: Track routing decisions → outcomes; detect misrouting patterns

**API**:
```python
class RoutingAnalyzer:
    def record_routing_outcome(
        self,
        routing_decision_id: str,
        target_handler_decided: str,
        target_handler_actual: str,
        success: bool,
        reason: str,
        duration_ms: float
    ) -> None:
        """Record outcome of a routing decision."""

    def get_routing_accuracy(
        self,
        handler_name: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get routing accuracy metrics.
        
        Returns:
            {
                "total_decisions": 150,
                "successful_routes": 145,
                "accuracy_rate": 0.9667,
                "by_handler": {
                    "handler_a": {"total": 50, "success": 48, "rate": 0.96},
                    ...
                }
            }
        """

    def detect_misrouting_patterns(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect systematic misrouting patterns.
        
        Returns:
            [
                {
                    "decided_handler": "handler_a",
                    "actual_handler": "handler_b",
                    "occurrences": 5,
                    "reason": "Fallback due to unavailability",
                    "first_seen": "2026-01-19T10:30:00Z"
                },
                ...
            ]
        """
```

**Storage**: `governance.db` → new table `routing_outcomes`
- `id` (UUID primary key)
- `decision_id` (foreign key to audit trail)
- `decided_handler` (string)
- `actual_handler` (string)
- `success` (boolean)
- `reason` (text)
- `duration_ms` (integer)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/routing_intelligence.py` (160 LOC)

**Files to Modify**:
- `cortex/orchestrators/core/master_orchestrator_stage_3.py` (+5 lines)
  ```python
  # After handler execution, in _execute_operation():
  routing_analyzer.record_routing_outcome(
      routing_decision_id=stage2_output.routing_decision.id,
      target_handler_decided=stage2_output.routing_decision.target_handler,
      target_handler_actual=handler_name,
      success=result.is_ok(),
      reason=result.error() if result.is_err() else "success",
      duration_ms=execution_time_ms
  )
  ```

**Tests** (12 tests):
- `test_record_routing_outcome()`
- `test_get_routing_accuracy_all_handlers()`
- `test_get_routing_accuracy_specific_handler()`
- `test_get_routing_accuracy_time_window()`
- `test_detect_misrouting_patterns_single()`
- `test_detect_misrouting_patterns_multiple()`
- `test_detect_misrouting_patterns_empty()`
- `test_accuracy_calculation_edge_cases()`
- `test_database_persistence()`
- `test_concurrent_updates()`
- `test_pattern_detection_threshold()`
- `test_time_window_filtering()`

---

### Module 2: Duration Intelligence (`duration_intelligence.py`)

**Purpose**: Build operation duration baselines; detect slow operations

**API**:
```python
class DurationAnalyzer:
    def record_operation_duration(
        self,
        operation_type: str,  # "implement", "fix", "refactor", "discovery", "validation"
        duration_ms: float,
        handler_name: str,
        success: bool
    ) -> None:
        """Record execution duration for an operation."""

    def get_duration_baseline(
        self,
        operation_type: str,
        days: int = 30
    ) -> Dict[str, float]:
        """Get duration baseline for operation type.
        
        Returns:
            {
                "p50": 150.0,
                "p95": 450.0,
                "p99": 800.0,
                "min": 50.0,
                "max": 2500.0,
                "mean": 200.0,
                "count": 500
            }
        """

    def detect_slow_operations(
        self,
        percentile_threshold: int = 99,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect operations slower than threshold percentile.
        
        Returns:
            [
                {
                    "operation_type": "implement",
                    "duration_ms": 2500,
                    "baseline_p99": 800,
                    "excess_ms": 1700,
                    "handler": "handler_a",
                    "timestamp": "2026-01-20T10:30:00Z"
                },
                ...
            ]
        """

    def get_handler_average_duration(
        self,
        handler_name: str,
        days: int = 7
    ) -> Dict[str, float]:
        """Get average duration by operation type for handler."""
```

**Storage**: `governance.db` → new table `operation_durations`
- `id` (UUID)
- `operation_type` (string)
- `duration_ms` (float)
- `handler_name` (string)
- `success` (boolean)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/duration_intelligence.py` (180 LOC)

**Files to Modify**:
- `cortex/orchestrators/core/master_orchestrator_stage_3.py` (+5 lines)
  ```python
  # After handler execution:
  operation_type = stage2_output.routing_decision.intent_type.value  # "implement", "fix", etc.
  duration_analyzer.record_operation_duration(
      operation_type=operation_type,
      duration_ms=execution_time_ms,
      handler_name=handler_name,
      success=result.is_ok()
  )
  ```

**Tests** (12 tests):
- `test_record_operation_duration()`
- `test_get_duration_baseline_sufficient_samples()`
- `test_get_duration_baseline_few_samples()`
- `test_percentile_calculation_p50()`
- `test_percentile_calculation_p95()`
- `test_percentile_calculation_p99()`
- `test_detect_slow_operations_above_threshold()`
- `test_detect_slow_operations_below_threshold()`
- `test_detect_slow_operations_empty()`
- `test_get_handler_average_duration()`
- `test_time_window_isolation()`
- `test_operation_type_isolation()`

---

### Module 3: Error Intelligence (`error_intelligence.py`)

**Purpose**: Detect error patterns; identify recurring failures

**API**:
```python
class ErrorAnalyzer:
    def record_error(
        self,
        error_type: str,  # e.g., "ValidationError", "TimeoutError"
        handler_name: str,
        operation_type: str,
        context: Dict[str, Any],
        traceback: Optional[str] = None
    ) -> None:
        """Record error occurrence."""

    def get_error_patterns(
        self,
        days: int = 7,
        min_occurrence: int = 3
    ) -> List[Dict[str, Any]]:
        """Get error patterns (recurring errors).
        
        Returns:
            [
                {
                    "error_type": "ValidationError",
                    "handler": "handler_a",
                    "operation_type": "implement",
                    "total_occurrences": 5,
                    "first_seen": "2026-01-18T10:30:00Z",
                    "last_seen": "2026-01-20T14:00:00Z",
                    "frequency_per_day": 1.67
                },
                ...
            ]
        """

    def get_error_frequency_by_handler(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get error frequency breakdown by handler."""

    def detect_new_errors(
        self,
        days: int = 1
    ) -> List[Dict[str, Any]]:
        """Detect errors not seen before in historical data."""
```

**Storage**: `governance.db` → new table `error_occurrences`
- `id` (UUID)
- `error_type` (string)
- `handler_name` (string)
- `operation_type` (string)
- `context` (JSON)
- `traceback` (text, nullable)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/error_intelligence.py` (160 LOC)

**Files to Modify**:
- `cortex/infrastructure/enhanced_audit_logger.py` (+5 lines)
  ```python
  # In log_operation_failed():
  error_analyzer.record_error(
      error_type=error.__class__.__name__,
      handler_name=context.get("handler"),
      operation_type=context.get("operation_type"),
      context=context,
      traceback=traceback_str
  )
  ```

**Tests** (10 tests):
- `test_record_error()`
- `test_get_error_patterns_above_threshold()`
- `test_get_error_patterns_below_threshold()`
- `test_get_error_patterns_empty()`
- `test_get_error_frequency_by_handler()`
- `test_detect_new_errors_with_history()`
- `test_detect_new_errors_no_history()`
- `test_error_type_isolation()`
- `test_time_window_filtering()`
- `test_frequency_calculation()`

---

### Module 4: Handler Load Intelligence (`handler_load_intelligence.py`)

**Purpose**: Track handler invocation load; enable load-aware routing

**API**:
```python
class HandlerLoadBalancer:
    def record_handler_invocation(
        self,
        handler_name: str,
        intent_type: str,
        duration_ms: float,
        success: bool
    ) -> None:
        """Record handler invocation."""

    def get_handler_load(
        self,
        intent_type: Optional[str] = None
    ) -> Dict[str, int]:
        """Get invocation count per handler.
        
        Returns:
            {
                "handler_a": 150,
                "handler_b": 120,
                "handler_c": 95
            }
        """

    def select_least_loaded_handler(
        self,
        candidate_handlers: List[str],
        intent_type: str
    ) -> str:
        """Select handler with lowest invocation count."""

    def get_handler_statistics(
        self,
        handler_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive handler statistics.
        
        Returns:
            {
                "total_invocations": 150,
                "success_count": 145,
                "success_rate": 0.9667,
                "avg_duration_ms": 250.0,
                "by_intent_type": {
                    "implement": {"count": 50, "success_rate": 0.98},
                    ...
                }
            }
        """
```

**Storage**: `governance.db` → new table `handler_invocations`
- `id` (UUID)
- `handler_name` (string, indexed)
- `intent_type` (string)
- `duration_ms` (float)
- `success` (boolean)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/handler_load_intelligence.py` (140 LOC)

**Files to Modify**:
- `cortex/orchestrators/core/intent_router.py` (+8 lines in routing decision)
  ```python
  # After determining candidate handlers:
  if len(candidate_handlers) > 1:
      target_handler = handler_load_balancer.select_least_loaded_handler(
          candidate_handlers, routing_decision.intent_type
      )
      routing_decision.reasoning += " (selected based on load distribution)"
  else:
      target_handler = candidate_handlers[0]
  ```
- `cortex/orchestrators/core/master_orchestrator_stage_3.py` (+3 lines)
  ```python
  # After handler execution:
  handler_load_balancer.record_handler_invocation(
      handler_name=handler_name,
      intent_type=operation_type,
      duration_ms=execution_time_ms,
      success=result.is_ok()
  )
  ```

**Tests** (12 tests):
- `test_record_handler_invocation()`
- `test_get_handler_load_all()`
- `test_get_handler_load_by_intent_type()`
- `test_select_least_loaded_handler_simple()`
- `test_select_least_loaded_handler_tied()`
- `test_select_least_loaded_handler_single_candidate()`
- `test_get_handler_statistics()`
- `test_success_rate_calculation()`
- `test_handler_isolation()`
- `test_time_window_filtering()`
- `test_concurrent_updates()`
- `test_load_balancing_integration()`

---

### Module 5: Dependency Chain Intelligence (`dependency_chain_intelligence.py`)

**Purpose**: Track orchestrator call chains; detect bottlenecks and cycles

**API**:
```python
class DependencyChainAnalyzer:
    def record_call_chain(
        self,
        chain: List[str],
        duration_ms: float,
        operation_type: str,
        success: bool
    ) -> None:
        """Record an orchestrator call chain."""

    def detect_deep_chains(
        self,
        max_depth: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect chains deeper than threshold.
        
        Returns:
            [
                {
                    "chain": ["master", "handler_a", "handler_b", "handler_c"],
                    "depth": 4,
                    "occurrences": 3,
                    "avg_duration_ms": 500,
                    "timestamp": "2026-01-20T10:30:00Z"
                },
                ...
            ]
        """

    def detect_cycles(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect cyclic chains (A→B→A patterns).
        
        Returns:
            [
                {
                    "cycle": ["handler_a", "handler_b", "handler_a"],
                    "occurrences": 2,
                    "first_seen": "2026-01-18T10:30:00Z",
                    "severity": "high"
                },
                ...
            ]
        """

    def get_bottleneck_orchestrators(
        self,
        percentile: int = 95,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Identify orchestrators in high-percentile call chains."""
```

**Storage**: `governance.db` → new table `call_chains`
- `id` (UUID)
- `chain` (JSON array of orchestrator names)
- `depth` (integer)
- `duration_ms` (float)
- `operation_type` (string)
- `success` (boolean)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/dependency_chain_intelligence.py` (200 LOC)

**Files to Modify**:
- `cortex/brain/core/orchestrator_base.py` (+5 lines in execute())
  ```python
  # Before calling delegate:
  call_chain = context.get("call_chain", [])
  call_chain.append(self.__class__.__name__)
  context["call_chain"] = call_chain
  
  # After delegate returns:
  chain_analyzer.record_call_chain(
      chain=call_chain,
      duration_ms=execution_time_ms,
      operation_type=context.get("operation_type"),
      success=result.is_ok()
  )
  ```
- `cortex/orchestrators/core/master_orchestrator.py` (+3 lines)
  ```python
  # In execute_operation():
  context["call_chain"] = [self.__class__.__name__]
  ```

**Tests** (12 tests):
- `test_record_call_chain()`
- `test_detect_deep_chains_above_threshold()`
- `test_detect_deep_chains_below_threshold()`
- `test_detect_deep_chains_empty()`
- `test_detect_cycles_simple()`
- `test_detect_cycles_complex()`
- `test_detect_cycles_none()`
- `test_get_bottleneck_orchestrators()`
- `test_chain_depth_calculation()`
- `test_cycle_detection_algorithm()`
- `test_time_window_filtering()`
- `test_chain_isolation()`

---

### Module 6: Efficiency Intelligence (`efficiency_intelligence.py`)

**Purpose**: Correlate duration with complexity; detect inefficient operations

**API**:
```python
class EfficiencyAnalyzer:
    def record_operation_metrics(
        self,
        operation_id: str,
        duration_ms: float,
        complexity_score: float,
        handler_name: str,
        operation_type: str
    ) -> None:
        """Record operation metrics for efficiency analysis."""

    def calculate_efficiency_ratio(
        self,
        operation_id: str
    ) -> float:
        """Calculate efficiency ratio (duration / complexity)."""

    def detect_inefficient_operations(
        self,
        percentile_threshold: int = 95,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect operations with poor efficiency (high duration/complexity ratio).
        
        Returns:
            [
                {
                    "operation_id": "op-123",
                    "handler": "handler_a",
                    "duration_ms": 1000,
                    "complexity_score": 2.0,
                    "efficiency_ratio": 500.0,
                    "percentile": 98,
                    "timestamp": "2026-01-20T10:30:00Z"
                },
                ...
            ]
        """

    def get_efficiency_by_handler(
        self,
        days: int = 7
    ) -> Dict[str, float]:
        """Get average efficiency ratio by handler."""
```

**Storage**: `governance.db` → new table `operation_efficiency`
- `id` (UUID)
- `operation_id` (string)
- `duration_ms` (float)
- `complexity_score` (float)
- `efficiency_ratio` (float, computed)
- `handler_name` (string)
- `operation_type` (string)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/efficiency_intelligence.py` (120 LOC)

**Files to Modify**:
- `cortex/orchestrators/core/master_orchestrator_stage_3.py` (+5 lines)
  ```python
  # After execution, extract complexity from stage4:
  efficiency_analyzer.record_operation_metrics(
      operation_id=operation_id,
      duration_ms=execution_time_ms,
      complexity_score=stage4_output.complexity_score,
      handler_name=handler_name,
      operation_type=operation_type
  )
  ```

**Tests** (8 tests):
- `test_record_operation_metrics()`
- `test_calculate_efficiency_ratio()`
- `test_detect_inefficient_operations_above_threshold()`
- `test_detect_inefficient_operations_below_threshold()`
- `test_get_efficiency_by_handler()`
- `test_efficiency_percentile_calculation()`
- `test_edge_case_zero_complexity()`
- `test_time_window_filtering()`

---

### Module 7: Governance Intelligence (`governance_intelligence.py`)

**Purpose**: Track rule hit frequency; optimize enforcement

**API**:
```python
class GovernanceIntelligence:
    def record_rule_evaluation(
        self,
        rule_id: str,
        passed: bool,
        context_type: str,  # e.g., "file_naming", "docstring", "type_hints"
        severity: str
    ) -> None:
        """Record rule evaluation result."""

    def get_rule_statistics(
        self,
        days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all rules.
        
        Returns:
            {
                "CORE-001": {
                    "total_evaluations": 500,
                    "pass_count": 495,
                    "fail_count": 5,
                    "pass_rate": 0.99,
                    "fail_rate": 0.01,
                    "context_types": ["file_naming", "function_naming"]
                },
                ...
            }
        """

    def detect_over_enforced_rules(
        self,
        fail_rate_threshold: float = 0.2,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Detect rules rarely violated (fail_rate < threshold).
        
        Interpretation: Rules triggered <20% likely have high bar relative to actual issues.
        """

    def detect_problematic_rules(
        self,
        fail_rate_threshold: float = 0.8,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Detect rules frequently violated (fail_rate > threshold)."""
```

**Storage**: `governance.db` → new table `rule_evaluations`
- `id` (UUID)
- `rule_id` (string, indexed)
- `passed` (boolean)
- `context_type` (string)
- `severity` (string)
- `timestamp` (datetime)

**Files to Create**:
- `src/core/intelligence/governance_intelligence.py` (140 LOC)

**Files to Modify**:
- `cortex/brain/core/rule_evaluator.py` (+3 lines after each rule evaluation)
  ```python
  # After evaluating each rule:
  governance_intelligence.record_rule_evaluation(
      rule_id=rule.id,
      passed=result.is_ok(),
      context_type=context.get("type"),
      severity=rule.severity
  )
  ```

**Tests** (8 tests):
- `test_record_rule_evaluation()`
- `test_get_rule_statistics()`
- `test_detect_over_enforced_rules()`
- `test_detect_problematic_rules()`
- `test_pass_rate_calculation()`
- `test_fail_rate_calculation()`
- `test_context_type_grouping()`
- `test_time_window_filtering()`

---

## Integration Points

### Master Orchestrator Stage 3 Changes

**File**: `cortex/orchestrators/core/master_orchestrator_stage_3.py`

**Additional Lines** (~25 total):
```python
# At top of file, add imports:
from src.core.intelligence.routing_intelligence import RoutingAnalyzer
from src.core.intelligence.duration_intelligence import DurationAnalyzer
from src.core.intelligence.handler_load_intelligence import HandlerLoadBalancer
from src.core.intelligence.dependency_chain_intelligence import DependencyChainAnalyzer
from src.core.intelligence.efficiency_intelligence import EfficiencyAnalyzer

# In __init__:
self.routing_analyzer = RoutingAnalyzer()
self.duration_analyzer = DurationAnalyzer()
self.handler_load_balancer = HandlerLoadBalancer()
self.chain_analyzer = DependencyChainAnalyzer()
self.efficiency_analyzer = EfficiencyAnalyzer()

# In execute_operation(), after handler execution:
operation_type = stage2_output.routing_decision.intent_type.value
execution_time_ms = time.time() - start_time

# Record all intelligence metrics
self.routing_analyzer.record_routing_outcome(...)
self.duration_analyzer.record_operation_duration(...)
self.handler_load_balancer.record_handler_invocation(...)
self.chain_analyzer.record_call_chain(...)
self.efficiency_analyzer.record_operation_metrics(...)
```

### Enhanced Audit Logger Changes

**File**: `cortex/infrastructure/enhanced_audit_logger.py`

**Additional Lines** (~10 total):
```python
# At top, add import:
from src.core.intelligence.error_intelligence import ErrorAnalyzer

# In __init__:
self.error_analyzer = ErrorAnalyzer()

# In log_operation_failed():
self.error_analyzer.record_error(
    error_type=error.__class__.__name__,
    handler_name=context.get("handler"),
    operation_type=context.get("operation_type"),
    context=context,
    traceback=traceback_str
)
```

### Intent Router Changes

**File**: `cortex/orchestrators/core/intent_router.py`

**Additional Lines** (~10 total):
```python
# At top, add import:
from src.core.intelligence.handler_load_intelligence import HandlerLoadBalancer

# In __init__:
self.load_balancer = HandlerLoadBalancer()

# In route() method, after determining candidates:
if len(candidate_handlers) > 1:
    target_handler = self.load_balancer.select_least_loaded_handler(
        candidate_handlers,
        routing_decision.intent_type
    )
else:
    target_handler = candidate_handlers[0]
```

---

## Dashboard Endpoints

**File**: `cortex/api/endpoints/intelligence.py` (new)

```python
@router.get("/intelligence/routing/accuracy")
async def routing_accuracy(handler: Optional[str] = None, days: int = 7):
    """Get routing accuracy metrics."""
    
@router.get("/intelligence/routing/misrouting-patterns")
async def misrouting_patterns(days: int = 7):
    """Get systematic misrouting patterns."""

@router.get("/intelligence/duration/baseline/{operation_type}")
async def duration_baseline(operation_type: str, days: int = 30):
    """Get duration baseline for operation type."""

@router.get("/intelligence/duration/slow-operations")
async def slow_operations(percentile: int = 99, days: int = 7):
    """Get operations slower than percentile."""

@router.get("/intelligence/errors/patterns")
async def error_patterns(min_occurrence: int = 3, days: int = 7):
    """Get recurring error patterns."""

@router.get("/intelligence/handler/load")
async def handler_load(intent_type: Optional[str] = None):
    """Get handler invocation load."""

@router.get("/intelligence/chains/deep")
async def deep_chains(max_depth: int = 10, days: int = 7):
    """Get deep orchestrator call chains."""

@router.get("/intelligence/chains/cycles")
async def chain_cycles(days: int = 7):
    """Get cyclic orchestrator chains."""

@router.get("/intelligence/efficiency/inefficient")
async def inefficient_operations(percentile: int = 95, days: int = 7):
    """Get inefficient operations."""

@router.get("/intelligence/governance/statistics")
async def governance_stats(days: int = 30):
    """Get governance rule statistics."""

@router.get("/intelligence/summary")
async def intelligence_summary(days: int = 7):
    """Get summary of all intelligence metrics."""
```

---

## Testing Strategy

**Total Tests**: ~75 unit tests

**Pattern**: CORE-008 TDD
1. Write tests first (RED phase)
2. Implement code (GREEN phase)
3. Refactor + optimize (REFACTOR phase)

**Test Categories**:
- **Unit Tests**: Isolated functionality (60 tests)
- **Integration Tests**: Database persistence (10 tests)
- **Performance Tests**: Query latency <50ms (5 tests)

**Success Criteria**:
- ≥95% pass rate
- ≥90% code coverage
- No governance violations (CORE-013: no bare except)

---

## Deployment Checklist

- [ ] All 7 modules created with full docstrings
- [ ] All 75 tests passing
- [ ] Database migrations created (5 new tables)
- [ ] Integration points modified (<50 lines total)
- [ ] Dashboard endpoints implemented (11 endpoints)
- [ ] Documentation updated (3 files)
- [ ] Governance audit trail enabled (AC logging)
- [ ] Production-ready (no debug code)

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Code Coverage | ≥90% | pytest --cov |
| Test Pass Rate | ≥95% | pytest output |
| API Response Time | <50ms | load test |
| Database Query Time | <20ms | EXPLAIN ANALYZE |
| Documentation | 100% | docstring coverage |
| Governance Compliance | 100% | audit log check |

---

**Status**: Ready for implementation  
**Estimated Timeline**: 3-4 working days  
**Risk Level**: Low (additive, no architectural changes)
