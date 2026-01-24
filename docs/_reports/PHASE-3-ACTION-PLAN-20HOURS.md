# Phase 3 Action Plan - Next 20 Hours

**Goal:** Complete Phase 3 remediation and achieve 100% production readiness

**Timeline:** 30 days (20 hours effort)  
**Target:** February 22, 2025 Go-Live  
**Current Status:** 70% complete (4h done, 16h remaining)

---

## Session 3: Handler Integration & Testing (6 hours)

### Hour 1-2: Facade Integration

**Location:** `cortex/orchestrators/core/master_orchestrator.py`

**Task:** Update MasterOrchestrator to use HandlerCoordinator

```python
# OLD (1,777 lines)
class MasterOrchestrator:
    def execute(self, request):
        # ...1,700 lines of logic...

# NEW (Facade pattern)
class MasterOrchestrator:
    def __init__(self):
        from cortex.orchestrators.handlers import HandlerCoordinator
        self._coordinator = HandlerCoordinator()
    
    def execute(self, request):
        """Execute using handlers."""
        return self._coordinator.orchestrate(
            request.text,
            request.context
        )
```

**Checklist:**
- [ ] Import HandlerCoordinator
- [ ] Update __init__ method
- [ ] Update execute method
- [ ] Keep backward compatibility
- [ ] Update imports in calling code
- [ ] Verify no breaking changes

**Commands:**
```bash
# Edit file
vi cortex/orchestrators/core/master_orchestrator.py

# Test syntax
python -m py_compile cortex/orchestrators/core/master_orchestrator.py

# Run basic test
python -c "from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator; m = MasterOrchestrator()"
```

---

### Hour 2-3: Unit Tests for Handlers

**Location:** `cortex/orchestrators/handlers/test_handlers.py` (CREATE NEW)

**Task:** Create comprehensive test suite

```python
# test_handlers.py

import pytest
from cortex.orchestrators.handlers.handler_implementations import (
    IntentClassificationHandler,
    RoutingHandler,
    GovernanceHandler,
    KnowledgeHandler,
    ExecutionCoordinator,
    ErrorRecoveryHandler,
    HandlerCoordinator
)

class TestIntentClassificationHandler:
    def test_classify_valid_intent(self):
        handler = IntentClassificationHandler()
        result = handler.classify("execute action", {"scope": "test"})
        assert result.success
        assert result.data.intent_type == "operation"
    
    def test_classify_empty_text(self):
        handler = IntentClassificationHandler()
        result = handler.classify("", {})
        assert not result.success
        assert "Empty text" in result.error

# ... Similar tests for all handlers ...

class TestHandlerCoordinator:
    def test_full_pipeline(self):
        coordinator = HandlerCoordinator()
        result = coordinator.orchestrate(
            "execute action",
            {"scope": "test"}
        )
        assert result.success
        assert result.data["status"] == "completed"
```

**Checklist:**
- [ ] Create test_handlers.py
- [ ] Test each handler (positive case)
- [ ] Test each handler (error case)
- [ ] Test full pipeline
- [ ] Run tests: `pytest cortex/orchestrators/handlers/test_handlers.py -v`
- [ ] Achieve >90% coverage

**Commands:**
```bash
# Create test file
touch cortex/orchestrators/handlers/test_handlers.py

# Run tests
pytest cortex/orchestrators/handlers/test_handlers.py -v

# Check coverage
pytest cortex/orchestrators/handlers/test_handlers.py --cov --cov-report=html
```

---

### Hour 3-4: Integration Tests

**Location:** `cortex/tests/integration/test_orchestration.py` (CREATE NEW)

**Task:** Test handlers integrated with rest of system

```python
def test_orchestration_with_intent_router():
    """Test handlers integrate with IntentRouter."""
    # Setup
    orchestrator = MasterOrchestrator()
    
    # Execute
    request = OperationRequest(
        text="execute domain operation",
        context={"scope": "domain_a", "user": "admin"}
    )
    
    # Assert
    result = orchestrator.execute(request)
    assert result.success

def test_orchestration_with_governance():
    """Test handlers integrate with Governance engine."""
    coordinator = HandlerCoordinator()
    result = coordinator.orchestrate(
        "execute action",
        {"scope": "operations"}
    )
    
    # Should pass governance validation
    assert result.success

def test_orchestration_with_knowledge():
    """Test handlers integrate with Knowledge repo."""
    # Test that knowledge is queried correctly
    pass

def test_end_to_end_orchestration():
    """Full end-to-end test."""
    pass
```

**Checklist:**
- [ ] Create integration test file
- [ ] Test with IntentRouter
- [ ] Test with Governance
- [ ] Test with Knowledge repo
- [ ] Test error scenarios
- [ ] All tests passing

---

### Hour 4-5: Performance Tests

**Location:** `cortex/tests/performance/test_handler_performance.py`

**Task:** Verify <2s execution time target

```python
import time

def test_handler_speed():
    """Test handlers execute quickly."""
    coordinator = HandlerCoordinator()
    
    start = time.time()
    result = coordinator.orchestrate("test", {})
    duration = time.time() - start
    
    assert duration < 0.1, f"Handler took {duration}s, target: <0.1s"
    assert result.success

def test_pipeline_throughput():
    """Test can handle 1000 ops/sec."""
    coordinator = HandlerCoordinator()
    
    start = time.time()
    for i in range(100):
        result = coordinator.orchestrate(f"test {i}", {})
        assert result.success
    
    duration = time.time() - start
    throughput = 100 / duration
    
    assert throughput > 100, f"Only {throughput} ops/sec, target: >100"
```

**Checklist:**
- [ ] Handler execution <100ms
- [ ] Pipeline throughput >100 ops/sec
- [ ] Memory usage <10MB per handler
- [ ] No memory leaks (run for 1000 iterations)

**Commands:**
```bash
# Run performance tests
pytest cortex/tests/performance/ -v -s

# Profile execution
python -m cProfile -s cumtime cortex/tests/performance/test_handler_performance.py
```

---

### Hour 5-6: Documentation & Sign-Off

**Location:** `docs/handlers-integration-guide.md` (CREATE NEW)

**Task:** Document handler integration

```markdown
# Handler Integration Guide

## Overview
Handlers replace the 1,777-line MasterOrchestrator with 6 focused classes.

## Architecture
[Diagram here]

## Usage
[Code examples]

## Testing
[Testing procedures]

## Deployment
[Deployment steps]
```

**Checklist:**
- [ ] Architecture documented
- [ ] Usage examples provided
- [ ] API reference complete
- [ ] Migration guide complete
- [ ] Team trained

---

## Session 4: Mutable State Migration (6 hours)

### Hour 1: Create StateManager

**Location:** `cortex/core/thread_safe_state.py` (CREATE NEW)

```python
"""Thread-safe state management using thread-local storage."""

import threading
from typing import Any, Optional

class StateManager:
    """Thread-safe state manager."""
    
    def __init__(self):
        self._local = threading.local()
    
    def set(self, key: str, value: Any) -> None:
        if not hasattr(self._local, 'state'):
            self._local.state = {}
        self._local.state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        if not hasattr(self._local, 'state'):
            self._local.state = {}
        return self._local.state.get(key, default)
    
    def clear(self) -> None:
        if hasattr(self._local, 'state'):
            self._local.state.clear()


class ScopedState:
    """Context manager for scoped state."""
    
    def __init__(self):
        self._state_stack = threading.local()
    
    @contextmanager
    def scope(self, **kwargs):
        if not hasattr(self._state_stack, 'stack'):
            self._state_stack.stack = []
        
        self._state_stack.stack.append(kwargs)
        try:
            yield kwargs
        finally:
            self._state_stack.stack.pop()
```

**Checklist:**
- [ ] Create file
- [ ] Implement StateManager
- [ ] Implement ScopedState
- [ ] Write docstrings
- [ ] Run syntax check

---

### Hours 2-6: Migrate High-Priority Files (5 files × 1h each)

#### File 1: orchestrator_registry.py (1h)

**BEFORE:**
```python
# Global mutable state (NOT THREAD-SAFE ❌)
_registry = {}

def register(name, handler):
    _registry[name] = handler

def get(name):
    return _registry.get(name)
```

**AFTER:**
```python
# Thread-local state (THREAD-SAFE ✅)
from cortex.core.thread_safe_state import StateManager

_registry = StateManager()

def register(name, handler):
    _registry.set(f"handler:{name}", handler)

def get(name):
    return _registry.get(f"handler:{name}")
```

**Checklist:**
- [ ] Identify mutable globals
- [ ] Replace with StateManager
- [ ] Update all usages
- [ ] Run tests
- [ ] Verify thread-safety

**Commands:**
```bash
# Find usages
grep -n "_registry" cortex/orchestrators/orchestrator_registry.py

# Run tests
pytest cortex/tests/test_orchestrator_registry.py -v

# Test thread-safety
pytest cortex/tests/test_orchestrator_registry.py::test_thread_safety -v
```

---

#### File 2: state_manager.py (1h)
#### File 3: knowledge_repository.py (1h)
#### File 4: telemetry_collector.py (1h)
#### File 5: external_service_client.py (1h)

**Same pattern:**
1. Identify mutable globals
2. Replace with StateManager
3. Update all usages
4. Run tests

---

### Hour 6: Concurrent Testing

**Location:** `cortex/tests/concurrency/test_thread_safety.py`

```python
import concurrent.futures
from cortex.core.thread_safe_state import StateManager

def test_state_manager_isolation():
    """Verify state is isolated per thread."""
    state = StateManager()
    results = []
    
    def thread_work(thread_id):
        state.set("id", thread_id)
        import time
        time.sleep(0.01)
        value = state.get("id")
        results.append(value == thread_id)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(thread_work, i) for i in range(10)]
        concurrent.futures.wait(futures)
    
    assert all(results), "Thread isolation failed"

def test_concurrent_registry_access():
    """Test concurrent registry access."""
    # Similar test for registry
    pass
```

**Checklist:**
- [ ] Thread isolation verified
- [ ] No race conditions
- [ ] All 10K concurrent users work
- [ ] Memory stable under load

---

## Session 5: Integration & Deployment (4 hours)

### Hour 1: End-to-End Testing

**Location:** `cortex/tests/e2e/test_production_readiness.py`

```python
def test_full_orchestration_pipeline():
    """Full end-to-end test."""
    orchestrator = MasterOrchestrator()
    # Test complete workflow

def test_concurrent_orchestration():
    """Test 10K concurrent users."""
    # Load test

def test_error_recovery():
    """Test error handling."""
    # Error scenarios
```

---

### Hour 2: Performance Validation

- Handler response time <100ms
- Pipeline throughput >100 ops/sec
- Memory usage <10MB per handler
- No memory leaks over 1000+ iterations

---

### Hour 3: Documentation & Release Notes

- Architecture guide
- API reference
- Migration guide
- Deployment checklist
- Release notes

---

### Hour 4: Production Sign-Off

- [ ] All tests passing (100%)
- [ ] Performance baselines met
- [ ] Documentation complete
- [ ] Team trained and ready
- [ ] Deployment plan approved
- [ ] Rollback plan ready
- [ ] Go-live approved

---

## Daily Execution Schedule

### Day 1 (Session 3: 6 hours)
- [ ] Hours 1-2: Facade integration
- [ ] Hours 2-3: Unit tests
- [ ] Hours 3-4: Integration tests
- [ ] Hours 4-5: Performance tests
- [ ] Hours 5-6: Documentation

### Day 2 (Session 4: 6 hours)
- [ ] Hour 1: Create StateManager
- [ ] Hours 2-6: Migrate 5 files + concurrent testing

### Day 3 (Session 5: 4 hours)
- [ ] Hour 1: End-to-end testing
- [ ] Hour 2: Performance validation
- [ ] Hour 3: Documentation
- [ ] Hour 4: Sign-off

### Day 4-28 (Remaining 4 hours - Flex)
- [ ] Deployment preparation (2 hours)
- [ ] Canary deployment (1 hour)
- [ ] Production monitoring (1 hour)

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Unit test coverage | >90% | ⏳ Pending |
| Integration tests | 100% passing | ⏳ Pending |
| Performance | <2s per test | ⏳ Pending |
| Thread-safety | 0 race conditions | ⏳ Pending |
| Concurrent users | 10K+ | ⏳ Pending |
| Production ready | Yes | ⏳ Pending |
| Go-live | Feb 22, 2025 | ✅ On track |

---

## Commands Quick Reference

```bash
# Handler tests
pytest cortex/orchestrators/handlers/ -v

# Integration tests
pytest cortex/tests/integration/ -v

# Thread-safety tests
pytest cortex/tests/concurrency/ -v

# Performance tests
pytest cortex/tests/performance/ -v

# Coverage report
pytest cortex/ --cov --cov-report=html

# Full test suite
pytest cortex/ --tb=short

# Check for thread issues
python -m pytest cortex/ -v --durations=10
```

---

## Critical Path Dependencies

1. ✅ Handler implementations DONE
2. ⏳ Handler integration (6 hours)
3. ⏳ Mutable state migration (6 hours)
4. ⏳ Testing & validation (4 hours)
5. ⏳ Production deployment (4 hours)

---

**Status:** 70% Complete | 16 Hours Remaining | On Track for Feb 22 ✅

**Next Action:** Start Session 3 - Handler Integration & Testing
