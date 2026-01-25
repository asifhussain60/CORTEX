# Phase 5: Test Suite Triage & Validation

## Overview
Currently: 7,547 tests collected, 5,500 passing (73%), 2,047 failing (27%)

**Objective:** Increase pass rate to 95%+ (7,169 tests passing) by:
1. Categorizing all 2,047 failing tests (blocking vs cosmetic)
2. Fixing blocking tests (infrastructure, governance, core orchestrators)
3. Validating full compliance suite

## Test Categories

### Blocking Tests (MUST FIX - Infrastructure Critical)
- **Count:** ~400-500 tests
- **Impact:** System doesn't function without fixes
- **Examples:**
  - Orchestrator registration failures
  - MCP tool exposure issues
  - Governance rule violations
  - Core initialization errors
  - Result type system failures

### Cosmetic Tests (NICE TO FIX - Low Priority)
- **Count:** ~1,500-1,600 tests
- **Impact:** System functions, but suboptimal
- **Examples:**
  - Response formatting
  - Documentation generation
  - CLI help text
  - Log message formatting
  - Performance optimizations

### External Dependency Tests (DEFER - Out of Scope)
- **Count:** ~100-150 tests
- **Impact:** Requires external service
- **Examples:**
  - Database connectivity
  - Cloud service integration
  - Third-party API calls
  - Browser automation

## Execution Strategy

### Phase 5a: Test Analysis (1 hour)
```bash
# Collect failing test names and categorize
pytest --collect-only -q 2>/dev/null | grep FAILED | wc -l

# Run with detailed output
pytest -v 2>&1 | grep "FAILED\|PASSED" > test_results.log

# Categorize by file/module
cat test_results.log | grep "orchestrator" # Core tests
cat test_results.log | grep "governance"   # Governance tests
cat test_results.log | grep "mcp"          # MCP tests
```

### Phase 5b: Blocking Test Fixes (2 hours)
Priority order:
1. Orchestrator registration (WIRE module tests)
2. MCP tool exposure (15 tools)
3. Governance compliance (29 CORE rules)
4. Result type system
5. Bootstrap initialization

### Phase 5c: Full Suite Validation (30 min)
```bash
# Run full test suite
pytest tests/ -v --tb=short

# Generate coverage report
pytest --cov=cortex --cov-report=html

# Validate orchestrator count
pytest tests/orchestrators/test_master_orchestrator.py -v -k "test_register"
```

## Key Files to Monitor

| File | Status | Priority |
|------|--------|----------|
| `tests/orchestrators/test_master_orchestrator.py` | Wiring tests | HIGH |
| `tests/mcp/test_mcp_tools_registry.py` | Tool exposure | HIGH |
| `tests/governance/test_core_rules.py` | CORE rules | HIGH |
| `tests/core/test_result.py` | Result type system | HIGH |
| `tests/orchestrators/test_wiring_*.py` | WIRE modules | HIGH |
| `tests/documentation/` | Documentation | LOW |
| `tests/formatting/` | Response formatting | LOW |

## Expected Outcomes

### Before Phase 5
- Total: 7,547 tests
- Passing: 5,500 (73%)
- Failing: 2,047 (27%)

### After Phase 5
- Total: 7,547 tests
- Passing: 7,169 (95%)
- Failing: 378 (5% deferred)
- Coverage: 85%+ for orchestrators, 80%+ overall

## Commands

```bash
# Current status
pytest --co -q 2>/dev/null | tail -1

# Run blocking tests only
pytest tests/orchestrators/ tests/mcp/ tests/governance/ -v

# Run with markers
pytest -m "not slow and not external_dependency" -v

# Generate report
pytest --html=report.html --self-contained-html
```

---

**Next Steps:** After Phase 5, proceed to Phase 6 (CLI shortcuts) and Phase 7 (documentation)
