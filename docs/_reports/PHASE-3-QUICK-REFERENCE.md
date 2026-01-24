# CORTEX PHASE 3 REMEDIATION - QUICK REFERENCE CARD

**Print & Post!** — Team execution guide for Phase 3 hardening  
**Authority:** REM-PHASE-3-FINDINGS | **Duration:** 30 days (24-30 hours active work)

---

## AT A GLANCE

| Item | Priority | Effort | Owner | Deadline |
|------|----------|--------|-------|----------|
| **REM-CRIT-003** | 🔴 BLOCKER | 2h | eng-1 | Jan 31 |
| **REM-CRIT-004** | 🔴 BLOCKER | 6h | eng-2,3 | Feb 7 |
| **REM-HIGH-001** | 🔴 BLOCKER | 10h | eng-4,5 | Feb 15 |
| **Integration Tests** | 🟡 HIGH | 4h | eng-1,2 | Feb 22 |

---

## REM-CRIT-003: BARE EXCEPTION CLAUSES

### What's Wrong?
```python
try:
    some_operation()
except:  # ❌ CATCHES SystemExit, KeyboardInterrupt, etc.
    log_error()
```

### Quick Fix
```python
try:
    some_operation()
except ValueError as e:
    log_error(f"Invalid input: {e}")
except RuntimeError as e:
    log_error(f"Runtime error: {e}")
except Exception as e:
    log_error(f"Unexpected: {e}", exc_info=True)
```

### Locations
- [ ] `cortex/tools/cortex_brain_integration.py`
- [ ] `cortex/tools/toolkit.py`
- [ ] `cortex/orchestrators/core/master_orchestrator.py` (3 instances)

### Validation
```bash
# Find all violations
grep -rn "except:" cortex/ | grep -v "Exception"

# Must return 0 matches after fix
```

### Test Template
```python
def test_handles_value_error():
    """Verify specific exception handling."""
    result = function_that_raises_value_error()
    assert isinstance(result, Err)
```

---

## REM-CRIT-004: MUTABLE GLOBAL STATE

### What's Wrong?
```python
# Module level (unsafe in multi-threaded env)
_cache = {}  # Shared across all threads!

def get_value(key):
    if key not in _cache:
        _cache[key] = expensive_operation()  # Race condition!
    return _cache[key]
```

### Quick Fix (Thread-Local)
```python
import threading

_thread_local = threading.local()

def get_value(key):
    if not hasattr(_thread_local, 'cache'):
        _thread_local.cache = {}
    
    if key not in _thread_local.cache:
        _thread_local.cache[key] = expensive_operation()
    
    return _thread_local.cache[key]
```

### High-Priority Files
- [ ] `cortex/brain/core/state_manager.py`
- [ ] `cortex/orchestrators/registry/orchestrator_registry.py`
- [ ] `cortex/brain/core/knowledge_repository.py`
- [ ] `cortex/infrastructure/telemetry.py`
- [ ] `cortex/api/external_service_client.py`

### Medium-Priority Files (8 more)
[See CORTEX-REMEDIATION-GUIDE.md for full list]

### Test Template
```python
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_access():
    """Verify no race conditions."""
    results = []
    
    def worker():
        for i in range(100):
            results.append(get_value(i))
    
    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.map(lambda _: worker(), range(10))
    
    # Verify results (no corruption)
    assert len(results) == 1000
```

---

## REM-HIGH-001: MASTER ORCHESTRATOR REFACTORING

### Current Problem
1,568-line `MasterOrchestrator` class does too many things:
- Intent classification
- Routing logic
- Governance validation
- Knowledge queries
- State management
- Error recovery

### Solution: Extract 6 Handler Classes

**Step 1:** Create handlers directory
```bash
mkdir -p cortex/orchestrators/handlers
touch cortex/orchestrators/handlers/__init__.py
```

**Step 2:** Extract handlers
```bash
# Each takes ~1-2 hours
touch cortex/orchestrators/handlers/intent_classification_handler.py
touch cortex/orchestrators/handlers/routing_handler.py
touch cortex/orchestrators/handlers/governance_handler.py
touch cortex/orchestrators/handlers/knowledge_handler.py
touch cortex/orchestrators/handlers/execution_coordinator.py
touch cortex/orchestrators/handlers/error_recovery_handler.py
```

**Step 3:** Refactor MasterOrchestrator to facade (200 lines)
```python
class MasterOrchestrator:
    def __init__(self, ...handlers...):
        self._intent_handler = intent_handler
        self._routing_handler = routing_handler
        # ... etc
    
    def execute(self, request):
        # Delegate to handlers
        # Compose results
        # Return output
```

**Step 4:** Update tests
```bash
# Before: 1 file (2000+ lines)
# After: 6 files (150-200 lines each)
```

### Validation
```bash
# Check MasterOrchestrator line count
wc -l cortex/orchestrators/core/master_orchestrator.py
# Target: < 300 lines

# Run orchestrator tests
pytest tests/unit/orchestrators/ -v
# Target: 600+/613 passing (98%+)
```

---

## REM-CRIT-002: ALREADY COMPLETE ✅

External API timeouts are implemented:
- 30s timeout ✅
- Exponential backoff ✅
- Circuit breaker ✅

No action required.

---

## DAILY CHECKLIST

### Day 1: Setup
- [ ] Clone latest main branch
- [ ] Review CORTEX-REMEDIATION-GUIDE.md (read Section 1-2)
- [ ] Assign tasks to team
- [ ] Setup concurrent test harness

### Day 2-3: Bare Exceptions (REM-CRIT-003)
- [ ] Identify all bare except clauses
  ```bash
  grep -rn "except:" cortex/ | grep -v "Exception"
  ```
- [ ] Write replacement code with specific exceptions
- [ ] Add unit tests for each exception path
- [ ] Run pytest to verify no regressions

### Day 4-5: Globals (REM-CRIT-004) — Thread 1
- [ ] Audit high-priority files (5 files)
- [ ] Choose strategy (thread-local vs class-manager)
- [ ] Implement with proper locking
- [ ] Write concurrent tests

### Day 4-5: Globals (REM-CRIT-004) — Thread 2
- [ ] Audit medium-priority files (8 files)
- [ ] Implement refactoring
- [ ] Concurrent test harness

### Day 6-10: Handler Extraction (REM-HIGH-001)
- [ ] Extract handlers (2h each, 6 total = 12h)
- [ ] Update tests
- [ ] Integration testing
- [ ] Performance baseline

### Day 11-30: Integration & Validation
- [ ] End-to-end tests
- [ ] Load testing
- [ ] Security audit
- [ ] Canary deployment prep

---

## CODE TEMPLATES

### Exception Handling Template
```python
def operation(self, param: str) -> Result[str]:
    """Perform operation.
    
    Args:
        param: Input parameter
        
    Returns:
        Result with output or error
        
    Raises:
        ValueError: If param is invalid
    """
    try:
        # Implementation
        return Ok(result)
    except ValueError as e:
        self.logger.error(f"Validation failed: {e}")
        return Err(f"Invalid parameter: {e}")
    except RuntimeError as e:
        self.logger.error(f"Runtime error: {e}")
        return Err(f"Execution failed: {e}")
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return Err(f"Unexpected error: {e}")
```

### Thread-Local Template
```python
import threading
from typing import Dict, Any

_thread_local = threading.local()

def get_cached_value(key: str) -> Any:
    """Get cached value from thread-local storage."""
    if not hasattr(_thread_local, 'cache'):
        _thread_local.cache = {}
    
    if key not in _thread_local.cache:
        _thread_local.cache[key] = compute_value(key)
    
    return _thread_local.cache[key]

def clear_cache() -> None:
    """Clear thread-local cache (call on thread exit)."""
    if hasattr(_thread_local, 'cache'):
        del _thread_local.cache
```

### Handler Template
```python
from typing import Result
from cortex.core.result import Ok, Err

class MyHandler:
    """Handle specific concern.
    
    AC-ID: REM-HIGH-001
    """
    
    def __init__(self, dependency: SomeDependency):
        self.dependency = dependency
    
    def handle(self, request: Request) -> Result[Output]:
        """Process request.
        
        Args:
            request: Handler request
            
        Returns:
            Result with output or error
        """
        try:
            output = self.dependency.process(request)
            return Ok(output)
        except ValueError as e:
            return Err(f"Invalid: {e}")
        except Exception as e:
            return Err(f"Error: {e}")
```

---

## TESTING COMMANDS

```bash
# Find bare excepts
grep -rn "except:" cortex/ | grep -v Exception

# Find module-level mutable state
grep -E "^[a-z_]+ = (\{|\[)" cortex/**/*.py

# Run specific test suite
pytest tests/unit/orchestrators/ -v

# Run concurrent stress test
pytest tests/unit/ -k "concurrent" -v

# Generate coverage report
pytest --cov=cortex --cov-report=html

# Check type hints
mypy cortex/

# Check for hardcoded paths
grep -r "^/Users\|^C:\\\\" cortex/
```

---

## SUCCESS CRITERIA

**Phase 3 Complete When:**
- [ ] 0 bare `except:` clauses (grep returns nothing)
- [ ] 0 module-level mutable globals (audit complete)
- [ ] MasterOrchestrator < 300 lines
- [ ] 600+/613 orchestrator tests passing
- [ ] 100/100 integration tests passing
- [ ] <2s all tests (except intentional waits)
- [ ] All TIER 0 rules enforced

**Go-Live Decision:** Feb 22

---

## ESCALATION CONTACTS

| Issue | Contact | Response |
|-------|---------|----------|
| Blocker | eng-lead | Same day |
| Design question | arch-team | 4 hours |
| Test failure | qa-lead | 2 hours |
| Performance | perf-team | 24 hours |

---

## LINKS

- **Full Review:** CORTEX-PRODUCTION-READINESS-REVIEW.md (60 pages)
- **Remediation Guide:** CORTEX-REMEDIATION-GUIDE.md (40 pages)
- **Executive Summary:** CORTEX-EXECUTIVE-SUMMARY.md
- **Test Logs:** cortex/test_audit_trail.log
- **Prompt Authority:** .github/prompts/CORTEX.prompt.md

---

**Print Date:** 2026-01-23  
**Revision:** 1.0  
**Status:** APPROVED FOR EXECUTION
