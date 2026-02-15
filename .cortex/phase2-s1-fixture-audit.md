# PHASE 2-S1: Fixture Consolidation Audit

**Date:** 2026-02-15  
**Status:** IN PROGRESS

## Fixture Inventory

### Root Level (conftest.py)
- `enable_traces_for_session` (session, autouse) - Enable tracing
- `flush_traces_after_test` (autouse) - Flush traces after each test
- `trace_logger_instance` - Provide trace logger
- `trace_statistics` - Provide trace statistics

### Tests Root (tests/conftest.py)
- `test_db_path` (function) - Temporary database path

### E2E Tests (tests/e2e/conftest.py)
- `e2e_environment` (session) - E2E environment setup
- `test_client` (function) - Test HTTP client
- `test_database` (function) - Test database connection
- `test_metrics` (function) - Test metrics collection
- `test_audit_log` (function) - Test audit logging
- `cleanup_after_test` (autouse) - Cleanup after each test

### Golden Tests (tests/golden/conftest.py)
- `audit_db_session` (session) - Audit DB session
- 4 other fixtures (TBD - need to read file)

### Integration Tests (tests/integration/conftest.py)
- 1 fixture (TBD)

### LENS Integration (tests/integration/cortex_lens/conftest.py)
- 1 fixture (TBD)

## Duplication Analysis

### Potential Duplicates
1. **Database fixtures**: `test_database` (e2e), `test_db_path` (tests), `audit_db_session` (golden)
   - **Action**: Consolidate into single parameterized fixture

2. **Cleanup fixtures**: `cleanup_after_test` (e2e), `flush_traces_after_test` (root)
   - **Action**: Verify no conflict, both are autouse

3. **Client fixtures**: `test_client` (e2e), potential duplicates in integration
   - **Action**: Check integration conftest for HTTP client

## Next Steps
1. Read all conftest files completely
2. Map fixture dependencies
3. Identify true duplicates
4. Create consolidation plan
5. Implement single source of truth in tests/conftest.py
