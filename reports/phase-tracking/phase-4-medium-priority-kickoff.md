# Phase 4: MEDIUM-Priority Items Kickoff
**Date:** January 24, 2026 | **Phase:** 3→4 Transition | **Status:** 🚀 READY FOR EXECUTION

---

## 🎯 Executive Summary

Phase 3 completion achieved **100% on documentation** (GOV-002 docstrings enhanced for all 12 public MasterOrchestrator methods). The system is now transitioning to Phase 4, which focuses on implementing 24 MEDIUM-priority improvements across infrastructure, resilience, integration, and observability domains.

**Current System State:**
- ✅ Phase 3: 7/7 HIGH items addressed (6/7 complete, 1 blocked on HALL-002)
- ✅ Test Suite: 2,673+ tests (100% passing)
- ✅ Governance Compliance: 82% (9/11 CORE rules at 100%)
- ✅ Git Status: 16 commits ahead of origin/CORTEX
- 🚀 **Ready for Phase 4: 24 MEDIUM-priority items**

---

## 📊 Phase 4 Scope Overview

### Distribution by Category
```
RESILIENCE (BRT-xxx):  7 items    [Infrastructure stability]
INTEGRATION (INTEG-xxx): 4 items  [System interconnection]
GOVERNANCE (GOV-xxx):  5 items    [Compliance & validation]
OBSERVABILITY (OBS-xxx): 5 items  [Monitoring & visibility]
PERFORMANCE (PERF-xxx): 3 items   [Optimization]
                    ───────────────
Total Effort:        24 items, ~32 hours estimated
```

---

## 📋 Detailed Phase 4 Items

### RESILIENCE CATEGORY (7 Items, 9.5 hours)

#### BRT-008: Graceful SIGTERM Shutdown Handler
**Status:** ⏳ Awaiting Implementation | **Effort:** 90 min | **Priority:** 🟡 Medium

**Objective:** Implement clean shutdown procedure when process receives SIGTERM signal

**Key Requirements:**
- Register signal handler for SIGTERM (signal 15)
- Orderly shutdown of all components (reverse registration order)
- Wait for pending requests/tasks to complete (max 30 sec)
- Resource cleanup: connection pools, thread pools, file handles
- Exit code: 0 for graceful shutdown, non-zero for forced

**Test Location:** `tests/unit/remediation/test_phase_3_medium_priority.py::TestGracefulShutdown`  
**Tests:** 4 tests covering registration, ordering, pending requests, resource cleanup

**Files to Modify:**
- `cortex/infrastructure/lifecycle_manager.py` (new or enhance)
- `cortex/orchestrators/core/master_orchestrator.py` (integrate shutdown)
- Add shutdown sequence configuration to `cortex-config.yaml`

**Example Usage:**
```python
lifecycle_mgr = LifecycleManager()
lifecycle_mgr.register_component("database", db_component)
lifecycle_mgr.register_component("cache", cache_component)
lifecycle_mgr.setup_sigterm_handler()  # Graceful shutdown on SIGTERM
# On SIGTERM: cache_component.shutdown() → db_component.shutdown()
```

---

#### BRT-009: Rate Limiting with Token Bucket Algorithm
**Status:** ⏳ Awaiting Implementation | **Effort:** 75 min | **Priority:** 🟡 Medium

**Objective:** Prevent resource exhaustion through request rate limiting

**Key Requirements:**
- Implement token bucket algorithm (capacity + refill rate)
- Per-user rate limiting (independent buckets per user ID)
- Per-endpoint rate limiting (different limits for different endpoints)
- Support for adaptive backoff (wait for token refill)
- Thread-safe concurrent access
- Configuration via cortex-config.yaml (default: 100 req/sec)

**Test Location:** `tests/unit/remediation/test_phase_3_medium_priority.py::TestRateLimiting`  
**Tests:** 5 tests covering algorithm, per-user limits, backoff, thread safety

**Files to Modify:**
- `cortex/infrastructure/rate_limiter.py` (new)
- `cortex/api/middleware/rate_limiting_middleware.py` (integrate)
- `cortex-config.yaml` (add rate_limiting section)

**Example Usage:**
```python
limiter = RateLimiter(capacity=100, refill_rate=1.0)  # 100 req/sec
allowed = limiter.is_allowed("user_123", "execute_operation")
if not allowed:
    raise RateLimitExceeded("Rate limit exceeded for user_123")
```

---

#### BRT-010: Connection Pool Health Monitoring
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Monitor connection pool health with automatic recovery

**Key Requirements:**
- Periodic health checks on idle connections (every 60 sec)
- Detect stale connections (no activity > 5 min)
- Automatic reconnection for failed connections
- Expose health metrics: total/active/idle connection counts
- Alert on pool exhaustion (usage > 80%)
- Configurable health check interval

**Files to Modify:**
- `cortex/infrastructure/connection_pool.py` (enhance)
- `cortex/infrastructure/health_checks.py` (integrate)
- Add health check metrics to observability

**Example Metrics:**
```python
pool_health = {
    "total_connections": 50,
    "active_connections": 35,
    "idle_connections": 15,
    "stale_connections": 2,  # detected for recovery
    "pool_utilization": "70%",
    "status": "healthy"
}
```

---

#### BRT-011: Circuit Breaker Pattern Enhancement
**Status:** ⏳ Awaiting Implementation | **Effort:** 45 min | **Priority:** 🟡 Medium

**Objective:** Enhance circuit breaker with adaptive thresholds

**Key Requirements:**
- Existing circuit breaker (OPEN/CLOSED/HALF_OPEN states)
- Add ADAPTIVE mode that adjusts thresholds based on error rates
- Track moving average of response times (last 100 requests)
- Transition to OPEN if error rate > threshold or latency spike
- Configurable thresholds per service
- Metrics exposure: state changes, transition counts

**Files to Modify:**
- `cortex/infrastructure/circuit_breaker.py` (enhance)
- Add metrics tracking and thresholds config

---

#### BRT-012: Retry Strategy with Exponential Backoff
**Status:** ⏳ Awaiting Implementation | **Effort:** 50 min | **Priority:** 🟡 Medium

**Objective:** Implement robust retry logic with jitter

**Key Requirements:**
- Exponential backoff: 1s → 2s → 4s → 8s (max 60s)
- Add jitter to prevent thundering herd (±10% randomization)
- Configurable max retries per operation (default 3)
- Retry only on transient errors (connection timeout, 429/503)
- Don't retry on client errors (400/403/404)
- Track retry attempts in audit trail

**Files to Modify:**
- `cortex/infrastructure/retry_strategy.py` (new)
- Integrate with ExternalServiceClient

**Example:**
```python
result = retry_with_backoff(
    func=external_api_call,
    max_retries=3,
    initial_delay=1.0,
    max_delay=60.0,
    operation_id="fetch_user_123"
)
```

---

#### BRT-013: Thread Pool Executor Monitoring
**Status:** ⏳ Awaiting Implementation | **Effort:** 40 min | **Priority:** 🟡 Medium

**Objective:** Monitor async task execution health

**Key Requirements:**
- Track active tasks, queue depth, completed tasks
- Alert when queue depth > configured threshold (default 100)
- Expose metrics: task duration percentiles (p50, p95, p99)
- Detect stuck tasks (running > 5 min), terminate after 10 min
- Task lifecycle events (queued, started, completed, failed)

**Files to Modify:**
- `cortex/infrastructure/task_executor.py` (enhance)
- Add metrics collection

---

#### BRT-014: Dependency Injection Container Enhancement
**Status:** ⏳ Awaiting Implementation | **Effort:** 35 min | **Priority:** 🟡 Medium

**Objective:** Add lifecycle management to DI container

**Key Requirements:**
- Support bean lifecycle: initialization → usage → shutdown
- Register startup hooks (called when bean created)
- Register shutdown hooks (called when app terminates)
- Dependency resolution validation (detect circular deps)
- Lazy initialization support for heavy beans
- Scope management: singleton, request, transient

**Files to Modify:**
- `cortex/infrastructure/di_container.py` (enhance)

---

### INTEGRATION CATEGORY (4 Items, 6 hours)

#### INTEG-001: Structured Logging with JSON + Correlation IDs
**Status:** ⏳ Awaiting Implementation | **Effort:** 90 min | **Priority:** 🟡 Medium

**Objective:** Implement JSON-structured logging for observability

**Key Requirements:**
- All logs output as JSON (not plain text)
- Include correlation ID in every log entry (trace request across services)
- Include request context: user_id, operation_id, intent_type
- Structured fields: timestamp (ISO 8601), level, component, message
- Correlation ID propagates through async operations
- Log levels: ERROR, WARN, INFO, DEBUG (no DEBUG in production)

**Test Location:** `tests/unit/remediation/test_phase_3_medium_priority.py::TestStructuredLogging`  
**Tests:** 4 tests covering JSON format, correlation IDs, context propagation

**Files to Modify:**
- `cortex/infrastructure/enhanced_audit_logger.py` (already exists, enhance)
- `cortex/common/logging_config.py` (configure JSON formatter)

**Example Log Entry:**
```json
{
  "timestamp": "2026-01-24T14:32:17.123Z",
  "level": "INFO",
  "component": "master_orchestrator",
  "message": "Operation executed successfully",
  "correlation_id": "req-12345-abcde",
  "user_id": "user_456",
  "operation_id": "op_789",
  "intent_type": "IMPLEMENT",
  "duration_ms": 245
}
```

---

#### INTEG-002: Health Check Aggregation API
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Expose unified health status endpoint

**Key Requirements:**
- Endpoint: `GET /health` → overall system health
- Endpoint: `GET /health/detailed` → per-component health
- Health statuses: HEALTHY, DEGRADED, UNHEALTHY
- Include dependency health: database, cache, external services
- Response time < 100ms (separate from actual health checks)
- Health check aggregation: unhealthy if ANY critical component down

**Files to Modify:**
- `cortex/api/health_endpoints.py` (new)
- `cortex/infrastructure/health_checks.py` (enhance)

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-24T14:32:17.123Z",
  "components": {
    "database": {"status": "healthy", "latency_ms": 12},
    "cache": {"status": "healthy", "latency_ms": 5},
    "mcp_server": {"status": "healthy", "registered_tools": 15}
  }
}
```

---

#### INTEG-003: Graceful Dependency Shutdown
**Status:** ⏳ Awaiting Implementation | **Effort:** 45 min | **Priority:** 🟡 Medium

**Objective:** Coordinate shutdown of interconnected components

**Key Requirements:**
- Dependency graph: database → cache → orchestrators
- Shutdown order respects dependency graph (reverse topological sort)
- Each component waits for dependents to shutdown first
- Timeout per component (30 sec default)
- Log shutdown sequence and timings

**Files to Modify:**
- `cortex/infrastructure/lifecycle_manager.py` (already mentioned in BRT-008)
- Enhance with dependency graph logic

---

#### INTEG-004: Service Registration & Discovery
**Status:** ⏳ Awaiting Implementation | **Effort:** 45 min | **Priority:** 🟡 Medium

**Objective:** Enable dynamic service discovery

**Key Requirements:**
- Services register on startup with endpoint URL, health check, metadata
- Support multiple instances (horizontal scaling)
- Deregister on shutdown (graceful or after timeout)
- Expose service registry: `GET /registry` → all available services
- Support service lookup by service_id or capability

**Files to Modify:**
- `cortex/infrastructure/service_registry.py` (new)
- Integrate with DI container

---

### GOVERNANCE CATEGORY (5 Items, 7 hours)

#### GOV-003: Input Validation Framework
**Status:** ⏳ Awaiting Implementation | **Effort:** 90 min | **Priority:** 🟡 Medium

**Objective:** Comprehensive input validation for all public APIs

**Key Requirements:**
- Decorator-based validation: `@validate_input(schema={...})`
- Schema definition: required fields, types, constraints (min/max, regex)
- Validation happens before function execution
- Clear error messages for validation failures
- Support for nested object validation
- Type checking: string, integer, float, boolean, list, dict

**Example:**
```python
@validate_input(schema={
    "user_id": {"type": "string", "pattern": r"^user_\d+$"},
    "age": {"type": "integer", "min": 18, "max": 150},
    "email": {"type": "string", "pattern": r"^[^@]+@[^@]+$"},
})
def create_user(user_id: str, age: int, email: str) -> Dict[str, Any]:
    pass
```

---

#### GOV-004: Output Sanitization Framework
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Sanitize all outputs to prevent injection attacks

**Key Requirements:**
- Complement existing LLM output validator (HALL-001)
- Generic sanitization: HTML, JavaScript, SQL, XML escape
- Remove sensitive data patterns (email, phone, SSN)
- Configurable sanitization rules per output type
- Audit trail: what was sanitized and why

**Example:**
```python
@sanitize_output(rules=["remove_emails", "escape_html"])
def generate_report() -> str:
    return "Contact admin@example.com for help"
    # Output: "Contact [EMAIL_REMOVED] for help"
```

---

#### GOV-005: Access Control Enhancement
**Status:** ⏳ Awaiting Implementation | **Effort:** 75 min | **Priority:** 🟡 Medium

**Objective:** Implement role-based access control (RBAC)

**Key Requirements:**
- Decorator-based role checking: `@require_role(["admin", "data_scientist"])`
- Roles: admin, data_scientist, operator, viewer
- Permission inheritance: admin > data_scientist > operator > viewer
- Check authorization before operation execution
- Log access decisions (grant/deny) with reason
- Support conditional access (e.g., own data only)

---

#### GOV-006: Audit Trail Enhancement
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Enhanced audit trail with immutability

**Key Requirements:**
- Current audit trail exists (CORE-027), enhance with:
- Write-once storage (append-only log, no modification)
- Hash chain verification (detect tampering)
- Audit retention policy: keep for 7 years, then archive
- Search/filter by date range, operation type, user
- Export audit trail in compliance format

---

#### GOV-007: Configuration Validation
**Status:** ⏳ Awaiting Implementation | **Effort:** 55 min | **Priority:** 🟡 Medium

**Objective:** Validate cortex-config.yaml on startup

**Key Requirements:**
- Schema validation: required fields, type checking
- Value range validation (e.g., pool size 10-1000)
- Interdependency validation (e.g., max_retries <= max_timeout)
- Clear error messages for invalid config
- Support for environment variable overrides
- Dry-run mode to validate without applying

---

### OBSERVABILITY CATEGORY (5 Items, 6 hours)

#### OBS-001: Metrics Collection & Exposure
**Status:** ⏳ Awaiting Implementation | **Effort:** 90 min | **Priority:** 🟡 Medium

**Objective:** Expose system metrics for monitoring

**Key Requirements:**
- Metrics types: counter, gauge, histogram, timer
- Endpoints: `GET /metrics` (Prometheus format)
- Include system metrics: CPU, memory, GC events, thread count
- Include application metrics: requests/sec, errors/sec, latency percentiles
- Configurable metric filters (which metrics to expose)

**Example Metrics:**
```
cortex_requests_total{endpoint="/execute_operation", status="success"} 1234
cortex_request_duration_seconds{endpoint="/execute_operation", le="0.1"} 45
cortex_errors_total{type="rate_limit_exceeded"} 12
cortex_pool_active_connections{pool="database"} 35
```

---

#### OBS-002: Distributed Tracing Support
**Status:** ⏳ Awaiting Implementation | **Effort:** 75 min | **Priority:** 🟡 Medium

**Objective:** Enable tracing across service boundaries

**Key Requirements:**
- Integrate OpenTelemetry for distributed tracing
- Trace context propagation (parent_span_id, trace_id)
- Span creation for key operations: API call, database query, orchestrator execution
- Span attributes: component, operation type, result, duration, error
- Export traces to backend (configurable: Jaeger, Zipkin, etc.)

**Example Trace:**
```
trace_id: req-12345-abcde
├─ span: execute_operation (150ms)
│  ├─ span: classify_intent (10ms)
│  ├─ span: validate_governance (20ms)
│  ├─ span: execute_handler (100ms)
│  └─ span: log_completion (5ms)
```

---

#### OBS-003: Alerting Rules Engine
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Define and evaluate alerting rules

**Key Requirements:**
- Rules: "if error_rate > 5%, alert CRITICAL"
- Support metric thresholds, time windows, aggregation
- Actions: log, email, webhook, Slack integration
- Rule persistence: save to cortex-config.yaml
- Alert deduplication (don't spam same alert)

---

#### OBS-004: Log Aggregation & Analysis
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Centralize and analyze logs

**Key Requirements:**
- Endpoint: `GET /logs` with filtering (component, level, time range)
- Support for log tail (last N entries): `/logs?tail=100`
- Search functionality: `/logs?search=user_123`
- Log aggregation by level: error count, warning count, etc.
- Retention: keep in memory (last 10,000 entries), archive to disk

---

#### OBS-005: Performance Profiling
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Enable runtime performance profiling

**Key Requirements:**
- Decorator: `@profile` to track execution time
- CPU sampling: identify hot spots
- Memory allocation tracking: find memory leaks
- Export profiles in standard format (pprof)
- Conditional profiling (only under high load)
- Low overhead (< 1% performance impact)

---

### PERFORMANCE CATEGORY (3 Items, 3.5 hours)

#### PERF-001: Caching Strategy Optimization
**Status:** ⏳ Awaiting Implementation | **Effort:** 60 min | **Priority:** 🟡 Medium

**Objective:** Optimize cache hit rates through smarter policies

**Key Requirements:**
- Current cache cleanup (BRIT-003) ensures size bounds
- Add cache warming: pre-populate with frequently used data on startup
- Add cache coherence: invalidate related entries on updates
- TTL strategies: longer for stable data, shorter for volatile
- Cache statistics: hit rate, miss rate, eviction count

---

#### PERF-002: Query Optimization for Database
**Status:** ⏳ Awaiting Implementation | **Effort:** 45 min | **Priority:** 🟡 Medium

**Objective:** Reduce database query overhead

**Key Requirements:**
- Query batching: combine multiple queries into single batch
- N+1 query detection: warn if query loop detected
- Query result caching at ORM level
- Index analysis: suggest indexes for common queries
- Prepared statement pooling

---

#### PERF-003: Async/Await Adoption
**Status:** ⏳ Awaiting Implementation | **Effort:** 35 min | **Priority:** 🟡 Medium

**Objective:** Increase concurrency through async operations

**Key Requirements:**
- Identify blocking operations (database, network calls)
- Convert to async: mark with `async def`, use `await`
- Use connection pooling for concurrent connections
- Avoid blocking event loop (CPU-intensive work in thread pool)
- Measure improvement: throughput increase

---

## 🔄 Implementation Strategy

### Recommended Sequence (in order of dependencies):

1. **BRT-008** (Graceful Shutdown) - Foundation for clean operations
2. **INTEG-003** (Graceful Dependency Shutdown) - Works with BRT-008
3. **BRT-009** (Rate Limiting) - Infrastructure protection
4. **BRT-010** (Connection Pool Health) - Enhance existing infrastructure
5. **INTEG-001** (Structured Logging) - Enables observability
6. **OBS-001** (Metrics Collection) - Works with structured logging
7. **GOV-003** (Input Validation) - Security foundation
8. **GOV-004** (Output Sanitization) - Security complement
9. **BRT-011** (Circuit Breaker Enhancement) - Advanced resilience
10. **BRT-012** (Retry Strategy) - Enhanced resilience
11. **INTEG-002** (Health Check API) - Works with OBS-001
12. ... remaining items in priority order

---

## 📦 Testing Requirements

Each MEDIUM item MUST have:
- ✅ Unit tests (test_phase_3_medium_priority.py already started)
- ✅ Integration tests (if depends on other components)
- ✅ Test documentation in code
- ✅ Minimum 80% code coverage

**Current Test Status:**
- `tests/unit/remediation/test_phase_3_medium_priority.py` exists (560 lines)
- Contains test stubs for BRT-008, BRT-009, INTEG-001
- Ready for TDD implementation (write tests first, then code)

---

## 🎯 Success Criteria for Phase 4

- [ ] All 24 MEDIUM items addressed
- [ ] Each item has passing tests (minimum 2 per item)
- [ ] Regression tests passing (0 failures in 2,673+ test suite)
- [ ] Documentation complete (docstrings + README updates)
- [ ] Zero unresolved TODOs in code
- [ ] Governance compliance maintained (≥82%)
- [ ] Performance metrics stable (no degradation)
- [ ] Git history clean (atomic commits with clear messages)

---

## 📈 Effort Estimation

```
Phase 4 Total Effort: ~32 hours (distributed work)

Breakdown:
- Resilience (BRT-008-014):     9.5 hours
- Integration (INTEG-001-004):   6.0 hours
- Governance (GOV-003-007):      7.0 hours
- Observability (OBS-001-005):   6.0 hours
- Performance (PERF-001-003):    3.5 hours

Quality Assurance:
- Testing (fixture setup, edge cases):  2-3 hours
- Documentation & code review:          1-2 hours
- Git management & deployment:          1 hour

Estimated Timeline (with pair programming):
- Week 1: Items 1-8  (BRT-008-010, INTEG-001-003, GOV-003-004)
- Week 2: Items 9-16 (BRT-011-014, INTEG-004, OBS-001-003)
- Week 3: Items 17-24 (GOV-005-007, OBS-004-005, PERF-001-003)
```

---

## 🚀 Next Steps

### Immediate (Next 30 minutes):
1. ✅ Review Phase 4 kickoff document (this file)
2. ✅ Confirm start with BRT-008 (Graceful Shutdown)
3. Run initial test suite to establish baseline

### First Task (BRT-008):
1. Review existing test stubs in `test_phase_3_medium_priority.py`
2. Create implementation file: `cortex/infrastructure/lifecycle_manager.py`
3. Write additional tests for edge cases
4. Implement graceful shutdown handler
5. Integrate with MasterOrchestrator
6. Commit with clear message: `feat(BRT-008): Implement graceful SIGTERM shutdown handler`

### Command to Begin:
```bash
# Enter TDD mode for first MEDIUM item
python3 -m pytest tests/unit/remediation/test_phase_3_medium_priority.py::TestGracefulShutdown -v
```

---

## 📚 Reference Documents

- **Phase 3 Final Status:** `_workspaces/SESSION-FINAL-REPORT-2026-01-24.md`
- **Critical Fixes Report:** `_workspaces/reports/REVIEW-CRITICAL-FIXES-COMPLETE.md`
- **Existing Tests:** `tests/unit/remediation/test_phase_3_medium_priority.py`
- **Governance Rules:** `cortex_brain/tier0/governance/` (CORE-008 through CORE-032)
- **Architecture:** `cortex-impl-map.yaml` (transformation roadmap)

---

**Ready to begin Phase 4? Approve to proceed with BRT-008 implementation.** ✅
