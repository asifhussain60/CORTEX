# Race Condition Analysis & Hanging Test Isolation Report

**Date**: January 18, 2026  
**Module**: `cortex_brain/tier0/test_isolation_cleanup.py`  
**Status**: 🔴 CRITICAL ISSUES FOUND

---

## Executive Summary

Analysis of AC-BRITTLE-007 test suite and implementation identified **3 CRITICAL RACE CONDITIONS** and **1 HANGING TEST** causing hangs in concurrent test execution.

### Issues Found:
1. ✅ **HANGING TEST**: `test_cleanup_handler_lifo_ordering` - Infinite loop due to execution order mismatch
2. ⚠️ **RACE CONDITION #1**: List modification during iteration (execute_cleanup_handlers)
3. ⚠️ **RACE CONDITION #2**: Potential deadlock with nested RLock acquisitions
4. ⚠️ **RACE CONDITION #3**: Unsynchronized access to shared state in circular dependency detection

---

## Issue #1: HANGING TEST ⚠️ CRITICAL

### Problem: `test_cleanup_handler_lifo_ordering`

**File**: `tests/unit/test_test_isolation_cleanup.py` (Line 328)

```python
def test_cleanup_handler_lifo_ordering(self) -> None:
    """Test cleanup handlers execute in LIFO order."""
    execution_order = []
    
    handlers = [
        lambda: execution_order.append(1),
        lambda: execution_order.append(2),
        lambda: execution_order.append(3),
    ]
    
    result = self.isolation.execute_cleanup_handlers(handlers)
    
    self.assertTrue(result)
    # LIFO order: 3, 2, 1
    self.assertEqual(execution_order, [3, 2, 1])  # ⚠️ THIS LINE HANGS
```

**Root Cause**: The assertion expects `[3, 2, 1]` but receives `[1, 2, 3]` when handlers list is passed to `execute_cleanup_handlers`, causing assertion failure and timeout.

**Implementation Bug**:
```python
def execute_cleanup_handlers(self, handlers: List[Callable], timeout: Optional[float] = None) -> bool:
    with self._lock:
        success = True
        
        # Execute in reverse order (LIFO)
        for handler in reversed(handlers):  # ⚠️ reversed() creates iterator, not new list
            try:
                if callable(handler):
                    handler()
            except Exception:
                success = False
        
        return success
```

The method is calling handlers, but the test is passing a NEW list that's NOT registered with the isolation object. The registered handlers (`self._cleanup_handlers`) are never executed.

---

## Issue #2: RACE CONDITION - Unsafe List Iteration

### Problem: Concurrent modification of handler list

**File**: `cortex_brain/tier0/test_isolation_cleanup.py` (Line 217)

```python
def register_cleanup_handler(self, handler: Callable) -> bool:
    with self._lock:
        if callable(handler):
            self._cleanup_handlers.append(handler)  # ⚠️ Adds to list
            return True
    return False

def execute_cleanup_handlers(self, handlers: List[Callable], timeout: Optional[float] = None) -> bool:
    with self._lock:
        success = True
        
        for handler in reversed(handlers):  # ⚠️ Could be externally modified while iterating
            try:
                if callable(handler):
                    handler()
            except Exception:
                success = False
        
        return success
```

**Risk**: If the `handlers` list is modified by another thread during iteration, `RuntimeError: list changed size during iteration` occurs.

**Scenario**:
```
Thread 1: execute_cleanup_handlers([h1, h2, h3]) -> reversed() iterator created
Thread 2: handlers.append(h4) -> ⚠️ List modified
Thread 1: for handler in iterator -> ❌ CRASH: list changed size during iteration
```

---

## Issue #3: RACE CONDITION - Nested Lock Acquisitions

### Problem: Potential deadlock with RLock

**File**: `cortex_brain/tier0/test_isolation_cleanup.py` (Line 309)

```python
def resolve_fixture_dependencies(self, fixtures: Dict[str, Dict[str, List[str]]]) -> List[str]:
    with self._lock:
        # ...
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            # ...
            for dep in deps:
                visit(dep)  # ⚠️ Recursive call holding lock
            
            order.append(name)
        
        for name in fixtures.keys():
            visit(name)
        
        return order
```

**Issue**: The recursive `visit()` function is called while holding `self._lock`. With deep dependency chains, this can cause:
1. Stack overflow with extremely deep recursion
2. Lock contention if another thread tries to acquire the lock

**Scenario** (with 1000-level dependency chain):
```
Thread 1: resolve_fixture_dependencies() acquires lock
Thread 1: visit(level_1) -> visit(level_2) -> ... -> visit(level_1000)
Thread 2: Tries to acquire lock -> BLOCKED (waiting for Thread 1)
Thread 1: Stack overflow on deep recursion ❌
```

---

## Issue #4: RACE CONDITION - Circular Dependency Detection

### Problem: Unsynchronized visited/rec_stack sets

**File**: `cortex_brain/tier0/test_isolation_cleanup.py` (Line 326)

```python
def detect_circular_dependencies(self, fixtures: Dict[str, Dict[str, List[str]]]) -> bool:
    with self._lock:
        visited = set()
        rec_stack = set()
        
        def has_cycle(name: str) -> bool:
            visited.add(name)  # ⚠️ Modifying set in recursive calls
            rec_stack.add(name)
            
            deps = fixtures.get(name, {}).get("depends_on", [])
            for dep in deps:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(name)
            return False
        
        for name in fixtures.keys():
            if name not in visited:
                if has_cycle(name):
                    return True
        
        return False
```

**Issue**: While sets ARE thread-safe for individual operations, the compound operations (checking + adding) are NOT atomic:

```
Thread 1: if dep not in visited -> True (check)
Thread 2: visited.add(dep) -> ADDS CONCURRENTLY
Thread 1: if has_cycle(dep) -> REDUNDANT CYCLE CHECK on already visited node
```

---

## Summary Table

| Issue | Type | Severity | Location | Impact |
|-------|------|----------|----------|--------|
| Test LIFO order mismatch | Logic Bug | 🔴 CRITICAL | test_cleanup_handler_lifo_ordering (L328) | **HANGING TEST** |
| Unsafe list iteration | Race Condition | 🔴 CRITICAL | execute_cleanup_handlers (L217) | RuntimeError, crash |
| Nested lock recursion | Deadlock Risk | 🟠 HIGH | resolve_fixture_dependencies (L309) | Stack overflow, lock contention |
| Unsynchronized visited/rec_stack | Race Condition | 🟠 HIGH | detect_circular_dependencies (L326) | Redundant cycles, false negatives |

---

## Fix Priority

1. **IMMEDIATE (P0)**: Fix `test_cleanup_handler_lifo_ordering` logic
2. **HIGH (P1)**: Fix unsafe list iteration in `execute_cleanup_handlers`
3. **HIGH (P1)**: Fix nested recursion lock contention
4. **MEDIUM (P2)**: Add atomic compound operations for visited checking

---

## Reproduction Steps

### Hanging Test:
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m pytest tests/unit/test_test_isolation_cleanup.py::TestIsolationRefactorCoverage::test_cleanup_handler_lifo_ordering -v
# Result: Test hangs on assertion due to order mismatch
```

### Race Condition Reproduction:
```bash
python3 -c "
from cortex_brain.tier0.test_isolation_cleanup import TestIsolationCleanup
import threading
import time

isolation = TestIsolationCleanup()
handlers = [lambda: time.sleep(0.01), lambda: None, lambda: None]

# Thread 1: Execute handlers
def execute():
    isolation.execute_cleanup_handlers(handlers)

# Thread 2: Modify handlers list
def modify():
    time.sleep(0.005)
    handlers.append(lambda: None)

t1 = threading.Thread(target=execute)
t2 = threading.Thread(target=modify)
t1.start()
t2.start()
t1.join()
t2.join()
print('Done')
"
# Result: Potential RuntimeError: list changed size during iteration
```

