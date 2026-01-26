# PERMANENT FIX: Implementation Guide for SSOT Orchestrator Registry
**Date:** 2026-01-25 | **Effort:** 10-15 hours | **Outcome:** Never Fix Wiring Again

---

## 🎯 Implementation Roadmap

### Phase 1: Create Core SSOT Registry (4-6 hours)

**File:** `cortex/orchestrators/core/orchestrator_registry.py`

```python
"""
Orchestrator Registry - Single Source of Truth (SSOT)

This replaces fragmented wiring across:
- MasterOrchestrator.__init__()
- OrchestratorBootstrap.initialize()
- IntentRouter.setup_routing()
- Multiple ad-hoc initialization points

Authority: CORE-031 (new rule: Single Orchestrator Registry)
"""

from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WiringState(Enum):
    """Orchestrator registry state machine."""
    UNINITIALIZED = "uninitialized"
    REGISTERING = "registering"
    COMPUTING_ORDER = "computing_order"
    WIRING = "wiring"
    WIRED = "wired"
    VALIDATION_FAILED = "validation_failed"
    UNWIRED = "unwired"  # Detected at runtime


@dataclass
class OrchestrationDependency:
    """Dependency specification for orchestrator."""
    name: str
    required: bool = True
    initialization_before: List[str] = field(default_factory=list)
    initialization_after: List[str] = field(default_factory=list)


@dataclass
class WiringResult:
    """Result of wiring operation."""
    success: bool
    orchestrator_name: str
    timestamp: datetime
    duration_ms: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistryValidation:
    """Result of validation check."""
    passed: bool
    timestamp: datetime
    checked_count: int
    passed_count: int
    failures: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class OrchestratorRegistry:
    """
    SSOT for orchestrator registration, wiring, and validation.
    
    Replaces:
    - MasterOrchestrator._wire_orchestrators()
    - OrchestratorBootstrap.auto_wire()
    - IntentRouter.setup_routing()
    - All ad-hoc registration calls
    
    Guarantees:
    - All orchestrators wired in deterministic order
    - No silent failures
    - Continuous validation
    - Automatic detection of unwiring
    """
    
    _instance = None
    
    def __init__(self):
        """Initialize empty registry."""
        self._orchestrators: Dict[str, Dict[str, Any]] = {}
        self._wiring_order: List[str] = []
        self._state = WiringState.UNINITIALIZED
        self._validation_log: List[RegistryValidation] = []
        self._wiring_results: List[WiringResult] = []
        self._last_validation: Optional[RegistryValidation] = None
        self._initialization_time: Optional[float] = None
    
    @classmethod
    def instance(cls):
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(
        self,
        name: str,
        orchestrator: Any,
        priority: int = 100,
        dependencies: Optional[List[str]] = None,
        optional: bool = False,
    ) -> None:
        """
        Register an orchestrator.
        
        Args:
            name: Orchestrator name (must be unique)
            orchestrator: Orchestrator instance
            priority: Lower number = higher priority (1-1000)
            dependencies: List of orchestrator names this depends on
            optional: If True, missing dependencies don't block
            
        Raises:
            ValueError: If orchestrator already registered
            TypeError: If orchestrator is invalid type
        """
        if self._state != WiringState.UNINITIALIZED:
            raise RuntimeError(
                f"Cannot register after wiring started (state={self._state})"
            )
        
        if name in self._orchestrators:
            raise ValueError(f"Duplicate registration: {name}")
        
        if not hasattr(orchestrator, 'execute'):
            raise TypeError(f"{name}: orchestrator must have execute() method")
        
        # Validate dependencies exist (will be checked again during topological sort)
        if dependencies is None:
            dependencies = []
        
        self._orchestrators[name] = {
            'instance': orchestrator,
            'priority': priority,
            'dependencies': dependencies,
            'optional': optional,
            'registered_at': datetime.now(),
            'initialized': False,
        }
        
        logger.debug(f"Registered orchestrator: {name} (priority={priority})")
    
    def _topological_sort(self) -> List[str]:
        """
        Compute deterministic wiring order using topological sort.
        
        Returns:
            List of orchestrator names in wiring order
            
        Raises:
            ValueError: If circular dependency detected
        """
        # Build adjacency list
        graph: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}
        
        for name in self._orchestrators:
            graph[name] = set()
            in_degree[name] = 0
        
        # Add edges for dependencies
        for name, info in self._orchestrators.items():
            for dep in info['dependencies']:
                if dep not in self._orchestrators:
                    if not info['optional']:
                        raise ValueError(
                            f"Missing required dependency: {name} depends on {dep}"
                        )
                    continue
                graph[dep].add(name)
                in_degree[name] += 1
        
        # Kahn's algorithm for topological sort
        queue = [name for name, degree in in_degree.items() if degree == 0]
        
        # Sort by priority within same level
        queue.sort(
            key=lambda n: self._orchestrators[n]['priority']
        )
        
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Process neighbors
            neighbors = list(graph[node])
            neighbors.sort(
                key=lambda n: self._orchestrators[n]['priority']
            )
            
            for neighbor in neighbors:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    queue.sort(
                        key=lambda n: self._orchestrators[n]['priority']
                    )
        
        # Check for cycles
        if len(result) != len(self._orchestrators):
            remaining = [
                n for n in self._orchestrators if n not in result
            ]
            raise ValueError(
                f"Circular dependency detected in: {remaining}"
            )
        
        return result
    
    def wire_all(self) -> RegistryValidation:
        """
        Execute wiring for all registered orchestrators.
        
        Returns:
            RegistryValidation with explicit success/failure
            
        Raises:
            RuntimeError: If wiring fails (no silent failures)
            ValueError: If dependencies or circular refs detected
        """
        import time
        
        start_time = time.time()
        
        try:
            # Step 1: State transition
            self._state = WiringState.REGISTERING
            logger.info(f"Wiring {len(self._orchestrators)} orchestrators")
            
            # Step 2: Compute deterministic order
            self._state = WiringState.COMPUTING_ORDER
            self._wiring_order = self._topological_sort()
            logger.info(f"Wiring order: {self._wiring_order}")
            
            # Step 3: Wire in deterministic order
            self._state = WiringState.WIRING
            for name in self._wiring_order:
                try:
                    wire_start = time.time()
                    self._wire_single(name)
                    wire_duration = (time.time() - wire_start) * 1000
                    
                    result = WiringResult(
                        success=True,
                        orchestrator_name=name,
                        timestamp=datetime.now(),
                        duration_ms=wire_duration,
                    )
                    self._wiring_results.append(result)
                    logger.debug(f"Wired {name} ({wire_duration:.1f}ms)")
                    
                except Exception as e:
                    logger.error(f"Failed to wire {name}: {e}")
                    raise RuntimeError(
                        f"Wiring failed at {name}: {e}"
                    ) from e
            
            # Step 4: Validate immediately
            self._state = WiringState.WIRED
            validation = self.validate_wiring()
            
            if not validation.passed:
                raise RuntimeError(
                    f"Validation failed after wiring: {validation.failures}"
                )
            
            duration = time.time() - start_time
            logger.info(f"✅ All orchestrators wired successfully ({duration:.2f}s)")
            
            return validation
            
        except Exception as e:
            self._state = WiringState.VALIDATION_FAILED
            logger.critical(f"🔴 Wiring FAILED: {e}")
            raise
    
    def _wire_single(self, name: str) -> None:
        """Wire a single orchestrator."""
        info = self._orchestrators[name]
        orchestrator = info['instance']
        
        # Call orchestrator's initialization
        if hasattr(orchestrator, 'initialize'):
            orchestrator.initialize()
        
        # Register with master if needed
        if hasattr(orchestrator, 'register_with_master'):
            orchestrator.register_with_master()
        
        info['initialized'] = True
    
    def validate_wiring(self) -> RegistryValidation:
        """
        Validate all orchestrators are wired and callable.
        
        Returns:
            RegistryValidation with detailed pass/fail info
        """
        failures = []
        passed = 0
        checked = 0
        suggestions = []
        
        for name, info in self._orchestrators.items():
            checked += 1
            orchestrator = info['instance']
            
            try:
                # Check 1: Orchestrator exists
                if orchestrator is None:
                    failures.append(f"{name}: instance is None")
                    continue
                
                # Check 2: Orchestrator is callable
                if not callable(getattr(orchestrator, 'execute', None)):
                    failures.append(f"{name}: execute() not callable")
                    suggestions.append(
                        f"Check {name} implements execute() method"
                    )
                    continue
                
                # Check 3: Dependencies are wired
                for dep in info['dependencies']:
                    if dep not in self._orchestrators:
                        failures.append(
                            f"{name}: missing dependency {dep}"
                        )
                        suggestions.append(
                            f"Register {dep} before {name}"
                        )
                        continue
                    
                    dep_info = self._orchestrators[dep]
                    if not dep_info['initialized']:
                        failures.append(
                            f"{name}: dependency {dep} not initialized"
                        )
                        suggestions.append(
                            f"Wire {dep} before {name}"
                        )
                        continue
                
                # Check 4: Can call a test method
                if hasattr(orchestrator, 'get_name'):
                    try:
                        _ = orchestrator.get_name()
                    except Exception as e:
                        failures.append(
                            f"{name}: get_name() failed: {e}"
                        )
                        continue
                
                passed += 1
                
            except Exception as e:
                failures.append(f"{name}: validation error: {e}")
        
        validation = RegistryValidation(
            passed=len(failures) == 0,
            timestamp=datetime.now(),
            checked_count=checked,
            passed_count=passed,
            failures=failures,
            suggestions=suggestions,
        )
        
        self._validation_log.append(validation)
        self._last_validation = validation
        
        if validation.passed:
            logger.debug(
                f"✅ Validation passed: {passed}/{checked} orchestrators"
            )
        else:
            logger.warning(
                f"❌ Validation failed: {len(failures)} issues"
            )
            for failure in failures:
                logger.warning(f"   - {failure}")
        
        return validation
    
    def get_orchestrator(self, name: str) -> Any:
        """
        Get orchestrator instance (guaranteed wired).
        
        Args:
            name: Orchestrator name
            
        Returns:
            Orchestrator instance
            
        Raises:
            RuntimeError: If not wired
            KeyError: If orchestrator doesn't exist
        """
        if self._state != WiringState.WIRED:
            raise RuntimeError(
                f"Orchestrator registry not wired (state={self._state})"
            )
        
        if name not in self._orchestrators:
            raise KeyError(f"Unknown orchestrator: {name}")
        
        info = self._orchestrators[name]
        if not info['initialized']:
            raise RuntimeError(f"Orchestrator {name} not initialized")
        
        return info['instance']
    
    def get_wiring_status(self) -> Dict[str, Any]:
        """Get current wiring status (for monitoring)."""
        return {
            'state': self._state.value,
            'total_registered': len(self._orchestrators),
            'total_wired': sum(
                1 for i in self._orchestrators.values() if i['initialized']
            ),
            'wiring_order': self._wiring_order,
            'last_validation': (
                self._last_validation.__dict__
                if self._last_validation
                else None
            ),
            'initialization_time_ms': (
                self._initialization_time * 1000
                if self._initialization_time
                else None
            ),
        }

```

---

### Phase 2: Create Health Checker (2-3 hours)

**File:** `cortex/orchestrators/core/health_checker.py`

```python
"""
Orchestrator Health Checker - Continuous Validation

Runs every 60 seconds to ensure wiring hasn't degraded.
Detects and heals unwiring automatically.
"""

import time
import threading
import logging
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class OrchestratorHealthChecker:
    """Continuous validation of orchestrator wiring."""
    
    def __init__(self, registry: 'OrchestratorRegistry'):
        """
        Initialize health checker.
        
        Args:
            registry: OrchestratorRegistry to monitor
        """
        self.registry = registry
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._check_interval = 60  # seconds
        self._consecutive_failures = 0
        self._max_heal_attempts = 3
        self._on_unwiring: Optional[Callable] = None
    
    def start(self):
        """Start background health checks."""
        if self._running:
            logger.warning("Health checker already running")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._check_loop,
            daemon=True,
        )
        self._thread.start()
        logger.info("🟢 Health checker started (checks every 60s)")
    
    def stop(self):
        """Stop background health checks."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🔴 Health checker stopped")
    
    def set_unwiring_handler(self, handler: Callable[[str], None]):
        """
        Set callback for unwiring detection.
        
        Args:
            handler: Callable(message) called when unwiring detected
        """
        self._on_unwiring = handler
    
    def _check_loop(self):
        """Background validation loop."""
        while self._running:
            try:
                validation = self.registry.validate_wiring()
                
                if validation.passed:
                    # All good
                    self._consecutive_failures = 0
                    logger.debug(
                        f"✅ Health check passed: {validation.passed_count}/"
                        f"{validation.checked_count}"
                    )
                else:
                    # Unwiring detected
                    self._handle_unwiring(validation)
                
                time.sleep(self._check_interval)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(self._check_interval)
    
    def _handle_unwiring(self, validation):
        """Handle detected unwiring."""
        self._consecutive_failures += 1
        
        logger.warning(
            f"⚠️  UNWIRING DETECTED (attempt {self._consecutive_failures}): "
            f"{len(validation.failures)} issues"
        )
        for failure in validation.failures:
            logger.warning(f"   - {failure}")
        
        # First attempt: Auto-heal
        if self._consecutive_failures <= self._max_heal_attempts:
            try:
                logger.info("🔄 Attempting auto-heal...")
                self.registry.wire_all()
                logger.info("✅ Auto-heal succeeded")
                self._consecutive_failures = 0
                return
            except Exception as e:
                logger.error(f"Auto-heal failed: {e}")
        
        # Repeated failures: Escalate
        logger.critical(
            f"🔴 PERSISTENT UNWIRING: Failed {self._consecutive_failures} "
            f"times. Manual intervention required."
        )
        
        if self._on_unwiring:
            self._on_unwiring(
                f"Persistent unwiring detected ({self._consecutive_failures} "
                f"failures). Failures: {validation.failures}"
            )
```

---

### Phase 3: Update Initialization (2-3 hours)

**File:** `cortex/orchestrators/core/cortex_initializer.py`

```python
"""
CORTEX Initialization - Centralized one-time setup.

Replaces fragmented initialization across multiple modules.
Guarantees all 23 orchestrators are wired before first request.
"""

import logging
from cortex.orchestrators.core.orchestrator_registry import (
    OrchestratorRegistry,
)
from cortex.orchestrators.core.health_checker import (
    OrchestratorHealthChecker,
)
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.interaction_orchestrator import (
    InteractionOrchestrator,
)
from cortex.orchestrators.core.intent_router import IntentRouter
# ... import all 23 orchestrators

logger = logging.getLogger(__name__)


def initialize_cortex() -> OrchestratorRegistry:
    """
    One-time initialization of CORTEX system.
    
    Must succeed completely or application refuses to start.
    
    Returns:
        OrchestratorRegistry (guaranteed fully wired)
        
    Raises:
        RuntimeError: If wiring fails
    """
    
    # Get singleton registry
    registry = OrchestratorRegistry.instance()
    
    logger.info("🚀 Initializing CORTEX orchestration system...")
    
    # Register all 23 orchestrators (declarative)
    _register_all_orchestrators(registry)
    
    # Wire all in deterministic order
    registry.wire_all()
    
    # Set up continuous health checks
    health_checker = OrchestratorHealthChecker(registry)
    health_checker.set_unwiring_handler(_handle_persistent_unwiring)
    health_checker.start()
    
    logger.info("✅ CORTEX initialization complete")
    return registry


def _register_all_orchestrators(registry: OrchestratorRegistry):
    """Register all 23 orchestrators in dependency order."""
    
    # CORE (6)
    registry.register(
        "MasterOrchestrator",
        MasterOrchestrator.instance(),
        priority=1,
    )
    
    registry.register(
        "InteractionOrchestrator",
        InteractionOrchestrator(),
        priority=2,
        dependencies=["MasterOrchestrator"],
    )
    
    registry.register(
        "IntentRouter",
        IntentRouter(),
        priority=3,
        dependencies=["MasterOrchestrator"],
    )
    
    # ... register remaining orchestrators ...
    
    logger.debug(f"Registered {len(registry._orchestrators)} orchestrators")


def _handle_persistent_unwiring(message: str):
    """Handle persistent unwiring (escalation)."""
    logger.critical(f"🔴 PERSISTENT UNWIRING: {message}")
    # TODO: Send alert to monitoring system
    # TODO: Log to incident tracking
    # TODO: Notify on-call engineer
```

---

### Phase 4: Update Tests (2-3 hours)

**File:** `tests/unit/orchestrators/test_orchestrator_registry.py`

```python
"""Tests for OrchestratorRegistry (SSOT)."""

import pytest
from cortex.orchestrators.core.orchestrator_registry import (
    OrchestratorRegistry,
    WiringState,
)


class MockOrchestrator:
    """Mock orchestrator for testing."""
    
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.execute_called = False
    
    def get_name(self) -> str:
        return self.name
    
    def initialize(self):
        self.initialized = True
    
    def execute(self):
        self.execute_called = True


class TestOrchestratorRegistry:
    """Test cases for OrchestratorRegistry."""
    
    def test_singleton_pattern(self):
        """Test registry is singleton."""
        reg1 = OrchestratorRegistry.instance()
        reg2 = OrchestratorRegistry.instance()
        assert reg1 is reg2
    
    def test_register_orchestrator(self):
        """Test orchestrator registration."""
        registry = OrchestratorRegistry()
        orch = MockOrchestrator("Test")
        
        registry.register("Test", orch)
        assert "Test" in registry._orchestrators
    
    def test_duplicate_registration_fails(self):
        """Test duplicate registration is blocked."""
        registry = OrchestratorRegistry()
        orch1 = MockOrchestrator("Test")
        orch2 = MockOrchestrator("Test")
        
        registry.register("Test", orch1)
        
        with pytest.raises(ValueError, match="Duplicate"):
            registry.register("Test", orch2)
    
    def test_topological_sort(self):
        """Test dependency resolution."""
        registry = OrchestratorRegistry()
        
        # A -> B -> C
        a = MockOrchestrator("A")
        b = MockOrchestrator("B")
        c = MockOrchestrator("C")
        
        registry.register("A", a, priority=1)
        registry.register("B", b, priority=2, dependencies=["A"])
        registry.register("C", c, priority=3, dependencies=["B"])
        
        order = registry._topological_sort()
        assert order == ["A", "B", "C"]
    
    def test_circular_dependency_detection(self):
        """Test circular dependencies are caught."""
        registry = OrchestratorRegistry()
        
        a = MockOrchestrator("A")
        b = MockOrchestrator("B")
        
        registry.register("A", a, dependencies=["B"])
        registry.register("B", b, dependencies=["A"])
        
        with pytest.raises(ValueError, match="Circular"):
            registry._topological_sort()
    
    def test_wire_all_succeeds(self):
        """Test successful wiring."""
        registry = OrchestratorRegistry()
        orch = MockOrchestrator("Test")
        
        registry.register("Test", orch)
        validation = registry.wire_all()
        
        assert validation.passed
        assert orch.initialized
    
    def test_validate_wiring(self):
        """Test validation of wired orchestrators."""
        registry = OrchestratorRegistry()
        orch = MockOrchestrator("Test")
        
        registry.register("Test", orch)
        registry.wire_all()
        
        validation = registry.validate_wiring()
        assert validation.passed
        assert validation.passed_count == 1
    
    def test_get_orchestrator_only_if_wired(self):
        """Test orchestrators only accessible when wired."""
        registry = OrchestratorRegistry()
        orch = MockOrchestrator("Test")
        
        registry.register("Test", orch)
        
        # Before wiring
        with pytest.raises(RuntimeError):
            registry.get_orchestrator("Test")
        
        # After wiring
        registry.wire_all()
        assert registry.get_orchestrator("Test") == orch
```

---

## 📋 Checklist for Implementation

### Code Creation
- [ ] Create `orchestrator_registry.py` (~300 lines)
- [ ] Create `health_checker.py` (~200 lines)
- [ ] Create `cortex_initializer.py` (~150 lines)
- [ ] Create comprehensive tests (~400 lines)

### Code Updates
- [ ] Update `master_orchestrator.py` to use registry
- [ ] Update `application.py` to call `initialize_cortex()`
- [ ] Remove duplicate registration code in other modules
- [ ] Add registry import to all orchestrator modules

### Testing
- [ ] Unit tests pass (registry, health checker, initialization)
- [ ] Integration tests pass (full wiring)
- [ ] Load tests pass (health checker under load)
- [ ] Failure scenario tests pass (simulated unwiring)

### Documentation
- [ ] Update CORTEX.prompt.md with SSOT explanation
- [ ] Add orchestrator registry guide to docs/
- [ ] Document health checker behavior
- [ ] Update initialization flow diagram

### Validation
- [ ] No orchestrators unwired after pull
- [ ] No orchestrators unwired after merge
- [ ] Health checker runs continuously
- [ ] Auto-heal works correctly
- [ ] Escalation works correctly

---

## 🚀 Deployment Plan

### Pre-Deployment
- [ ] All tests passing locally
- [ ] All tests passing in CI/CD
- [ ] Code review complete
- [ ] Documentation complete

### Deployment
- [ ] Merge to main branch
- [ ] Deploy to production
- [ ] Monitor health checks
- [ ] Watch for any escalations

### Post-Deployment
- [ ] Verify wiring stays intact for 7 days
- [ ] Verify health checker runs continuously
- [ ] Verify auto-heal works
- [ ] Gather metrics on uptime

---

## ✅ Success Criteria

After implementation:
- ✅ No manual wiring fixes needed
- ✅ No silent orchestrator failures
- ✅ Health checks run every 60 seconds
- ✅ Auto-healing works automatically
- ✅ Clear audit trail of all wiring operations
- ✅ Explicit failures (no hidden ones)
- ✅ Scales with team growth

---

**Estimated Total Effort:** 10-15 hours  
**Expected ROI:** Never fix wiring again (infinite ROI)

**Ready to implement?** Start with Phase 1 (registry).
