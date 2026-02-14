"""
AC-TRACE-001 through AC-TRACE-004: Orchestrator Trace Logging Specification

Purpose:
Implement comprehensive SQLite trace logging for all CORTEX orchestrators
with automatic flush policies to prevent unbounded database growth.

Scope: 28 orchestrators across 3 categories (core, domain, support)

Key Requirements:
1. Development-only tracing (production disabled via CORTEX_TRACE_ENABLED)
2. Per-orchestrator trace tables (28 total tables)
3. Automatic strategic flushing (time-based and size-based)
4. Test auto-enablement (pytest auto-enables for all tests)
5. Correlation ID tracking for request tracing
6. Violation detection and context preservation
7. Non-blocking insertion (async where possible)

Configuration:
- CORTEX_TRACE_ENABLED: true/false (default: true for dev, false for prod)
- CORTEX_TRACE_DB: database path (default: .cortex/traces/orchestrator-traces.db)
- CORTEX_TRACE_MAX_ROWS: per-table row limit (default: 10000, 50000 for tests)
- CORTEX_TRACE_FLUSH_INTERVAL: flush interval in hours (default: 24)
- CORTEX_TRACE_ASYNC_FLUSH: enable async flushing (default: true)

Database Schema:

1. trace_metadata (master registry)
   - id: UUID
   - orchestrator_id: Orchestrator identifier
   - orchestrator_class: Full class name
   - table_name: SQLite table name for traces
   - created_at: Creation timestamp
   - last_updated: Last update timestamp
   - row_count: Current row count
   - last_flush_time: Last flush timestamp

2. Per-orchestrator trace tables (trace_ORCHESTRATOR_ID)
   Example: trace_master_orchestrator, trace_enforcement, trace_tdd, etc.

   - trace_id: UUID (PRIMARY KEY)
   - timestamp: ISO 8601 timestamp
   - action: Action name (EXECUTE_OPERATION, VALIDATE_GOVERNANCE, etc.)
   - level: Trace level (DEBUG, INFO, ACTION, VIOLATION, ERROR)
   - correlation_id: Request correlation ID
   - request_id: Request ID
   - context: JSON context data
   - result: OK, ERR, RUNNING
   - violation_type: Governance violation type (if applicable)
   - duration_ms: Operation duration in milliseconds
   - metadata: Additional JSON metadata

   Indexes:
   - idx_ORCHESTRATOR_timestamp (timestamp DESC)
   - idx_ORCHESTRATOR_correlation (correlation_id)

3. trace_flush_log (audit trail for flush operations)
   - flush_id: UUID (PRIMARY KEY)
   - timestamp: Flush timestamp
   - reason: Flush reason (max_rows_reached, time_based_rotation, manual_request, startup_cleanup)
   - tables_flushed: JSON map of {table_name: rows_removed}
   - total_rows_removed: Total rows deleted
   - total_rows_remaining: Rows remaining after flush
   - duration_ms: Flush operation duration

Integration Points:

1. Orchestrator Methods:
   @trace_orchestrator_action("ACTION_NAME")
   def execute(self, ...):
       ...

2. Violation Tracking:
   trace_violation(
       orchestrator_id="enforcement",
       violation_type="CORE-002",
       context={"rule": "no_markdown_generation", "file": "file.md"}
   )

3. Generic Actions:
   trace_action(
       orchestrator_id="master",
       action="EXECUTE_OPERATION",
       context={...},
       result="OK",
       duration_ms=125.5
   )

4. Test Enablement (automatic via conftest.py):
   - All tests automatically have tracing enabled
   - Traces flushed after each test
   - Separate test database at .cortex/traces/test-orchestrator-traces.db

Flush Policy:

1. Size-based flushing:
   - When table reaches MAX_ROWS_PER_TABLE (10000 default)
   - Delete oldest 50% of rows
   - Update metadata row count

2. Time-based flushing:
   - Run every FLUSH_INTERVAL_HOURS (24 default)
   - Remove rows older than interval
   - Log flush event to trace_flush_log

3. Manual flushing:
   - Via get_trace_logger().flush_traces(reason)
   - Returns TraceFlushEvent with statistics

4. Startup cleanup:
   - Run on OrchestratorTraceLogger initialization
   - Remove stale traces from previous sessions

Monitoring:

Query traces:
```python
logger = get_trace_logger()
traces = logger.query_traces(
    orchestrator_id="master",
    level=TraceLevel.VIOLATION,
    since=datetime.utcnow() - timedelta(hours=1),
    limit=100
)
```

Get statistics:
```python
stats = logger.get_statistics()
# Returns: {
#     'enabled': True,
#     'total_tables': 28,
#     'total_rows': 45000,
#     'latest_trace': '2026-02-13T14:30:00',
#     'db_path': '.cortex/traces/orchestrator-traces.db',
#     'db_size_mb': 125.5,
#     'max_rows_per_table': 10000
# }
```

Production Deployment:

1. Environment Setup:
   - Set CORTEX_TRACE_ENABLED=false in production
   - Keeps code intact but disables tracing
   - No performance impact

2. Testing in Production:
   - Can enable tracing temporarily: CORTEX_TRACE_ENABLED=true
   - Traces automatically flushed to prevent growth
   - Separate database path can be configured

Development Workflow:

1. Running tests:
   pytest tests/
   # Traces automatically enabled
   # Traces automatically flushed after each test

2. Debugging issues:
   logger = get_trace_logger()
   traces = logger.query_traces(
       orchestrator_id="master",
       level=TraceLevel.VIOLATION,
       limit=50
   )

3. Analyzing performance:
   stats = get_trace_logger().get_statistics()
   # Shows DB size, row counts, latest operations

Files Implemented:

1. cortex/infrastructure/orchestrator_trace_logger.py
   - OrchestratorTraceLogger (singleton)
   - PerOrchestrationTraceWriter
   - TraceEntry dataclass
   - TraceFlushPolicy
   - TraceFlushEvent dataclass

2. cortex/infrastructure/trace_integration.py
   - TraceContext context manager
   - @trace_orchestrator_action decorator
   - trace_violation() function
   - trace_action() function
   - enable_trace_for_tests() / disable_trace_for_production()
   - is_trace_enabled() check

3. conftest.py (pytest fixtures)
   - enable_traces_for_session (autouse)
   - flush_traces_after_test (autouse)
   - trace_logger_instance fixture
   - trace_statistics fixture
   - orchestrator_trace_writer fixture
   - pytest_configure() / pytest_unconfigure() hooks

4. cortex-registry/_cortex-master/orchestrator-tracing.yaml
   - Trace configuration for all 28 orchestrators
   - Per-orchestrator table mappings
   - Flush policies
   - Monitoring guidelines

Testing:

Unit tests for trace logger:
- test_orchestrator_trace_logger.py (in tests/unit/infrastructure/)
  - Test trace recording
  - Test flush policies
  - Test statistics reporting
  - Test violation tracking
  - Test correlation ID propagation
  - Test dev/prod mode switching

Integration tests:
- test_orchestrator_integration_tracing.py
  - Test tracing across multiple orchestrators
  - Test trace context propagation
  - Test violation detection in enforcement
  - Test test-mode auto-enablement

Performance Considerations:

1. Database Size:
   - ~10KB per trace entry (with context)
   - 10,000 rows per table = ~100MB per orchestrator
   - 28 orchestrators × 100MB max = ~2.8GB theoretical max
   - Strategic flushing keeps size bounded

2. Write Performance:
   - SQLite: ~1000 writes/sec typical
   - Orchestrators log max 1-2 traces per operation
   - 100 operations/sec = 100-200 traces/sec (well within limits)

3. Flush Performance:
   - Flushing 50% of 10K rows: ~100ms
   - Async flushing: non-blocking to orchestrators

Future Enhancements:

1. Trace Querying UI:
   - Dashboard widget for trace visualization
   - Filter by orchestrator, level, time range
   - Export to CSV for analysis

2. Automated Analysis:
   - Detect patterns in violations
   - Identify performance bottlenecks
   - Generate performance reports

3. Remote Logging:
   - Send traces to central logging service
   - Aggregated monitoring across deployments
   - Alert on violation patterns

4. Compression:
   - Archive old traces to compressed format
   - Long-term retention without growth

Author: Asif Hussain
Version: 1.0
Status: IMPLEMENTED
"""
