# SOLID Principles for Python - CORTEX Guide

**Version:** 1.0.0  
**Status:** ✅ MANDATORY  
**Authority:** Robert C. Martin (Uncle Bob) + Python Best Practices  
**Enforcement:** PythonBestPracticesValidator middleware

---

## 🎯 Overview

SOLID principles are five design principles that make software designs more understandable, flexible, and maintainable. This guide provides Python-specific examples for CORTEX development.

**The Five Principles:**
1. **S**ingle Responsibility Principle (SRP)
2. **O**pen/Closed Principle (OCP)
3. **L**iskov Substitution Principle (LSP)
4. **I**nterface Segregation Principle (ISP)
5. **D**ependency Inversion Principle (DIP)

---

## 1️⃣ Single Responsibility Principle (SRP)

**Definition:** A class should have ONE and only ONE reason to change.

### ✅ CORRECT Example

```python
# Each class has a single, well-defined responsibility

class OrchestratorRegistry:
    """ONLY manages orchestrator registration and lookup."""
    
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.orchestrators: Dict[str, BaseOrchestrator] = {}
    
    def register(self, orchestrator: BaseOrchestrator) -> None:
        """Register an orchestrator."""
        if orchestrator.orchestrator_id in self.orchestrators:
            raise DuplicateOrchestratorError(
                f"Orchestrator {orchestrator.orchestrator_id} already registered"
            )
        self.orchestrators[orchestrator.orchestrator_id] = orchestrator
    
    def get(self, orchestrator_id: str) -> BaseOrchestrator:
        """Retrieve registered orchestrator."""
        if orchestrator_id not in self.orchestrators:
            raise OrchestratorNotFoundError(
                f"Orchestrator {orchestrator_id} not found"
            )
        return self.orchestrators[orchestrator_id]
    
    def list_all(self) -> List[str]:
        """List all registered orchestrator IDs."""
        return list(self.orchestrators.keys())


class OrchestratorExecutor:
    """ONLY executes orchestrators (separate responsibility)."""
    
    def __init__(self, registry: OrchestratorRegistry):
        self.registry = registry
    
    def execute(
        self,
        orchestrator_id: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute orchestrator with request."""
        orchestrator = self.registry.get(orchestrator_id)
        
        if not orchestrator.validate():
            raise OrchestratorValidationError(
                f"Orchestrator {orchestrator_id} failed validation"
            )
        
        return orchestrator.execute(request, context)


class OrchestratorMetrics:
    """ONLY tracks orchestrator execution metrics (separate responsibility)."""
    
    def __init__(self):
        self.execution_counts: Dict[str, int] = {}
        self.execution_times: Dict[str, List[float]] = {}
    
    def record_execution(
        self,
        orchestrator_id: str,
        duration: float,
        status: str
    ) -> None:
        """Record orchestrator execution metrics."""
        if orchestrator_id not in self.execution_counts:
            self.execution_counts[orchestrator_id] = 0
            self.execution_times[orchestrator_id] = []
        
        self.execution_counts[orchestrator_id] += 1
        self.execution_times[orchestrator_id].append(duration)
    
    def get_average_duration(self, orchestrator_id: str) -> float:
        """Get average execution duration."""
        times = self.execution_times.get(orchestrator_id, [])
        return sum(times) / len(times) if times else 0.0
```

**Why This Is Better:**
- `OrchestratorRegistry` changes ONLY if registration logic changes
- `OrchestratorExecutor` changes ONLY if execution logic changes
- `OrchestratorMetrics` changes ONLY if metrics tracking changes
- Each class is easier to test, understand, and maintain

---

### ❌ INCORRECT Example (SRP Violation)

```python
class OrchestratorManager:
    """Does too much - violates SRP."""
    
    def __init__(self, registry_path: str, db_path: str):
        self.orchestrators: Dict[str, BaseOrchestrator] = {}
        self.db_connection = sqlite3.connect(db_path)
        self.metrics = {}
    
    # Responsibility 1: Registration
    def register(self, orchestrator: BaseOrchestrator) -> None:
        """Register orchestrator."""
        self.orchestrators[orchestrator.orchestrator_id] = orchestrator
    
    # Responsibility 2: Execution
    def execute(self, orchestrator_id: str, request: str) -> Dict:
        """Execute orchestrator."""
        orchestrator = self.orchestrators[orchestrator_id]
        return orchestrator.execute(request, {})
    
    # Responsibility 3: Logging
    def log_execution(self, orchestrator_id: str, result: Dict) -> None:
        """Log execution to database."""
        self.db_connection.execute(
            "INSERT INTO logs VALUES (?, ?, ?)",
            (orchestrator_id, datetime.now(), json.dumps(result))
        )
        self.db_connection.commit()
    
    # Responsibility 4: Metrics
    def calculate_metrics(self) -> Dict:
        """Calculate execution metrics."""
        return {
            "total_executions": len(self.metrics),
            "average_duration": sum(self.metrics.values()) / len(self.metrics)
        }
    
    # Responsibility 5: Configuration
    def save_config(self, config_path: str) -> None:
        """Save configuration to file."""
        with open(config_path, 'w') as f:
            json.dump({"orchestrators": list(self.orchestrators.keys())}, f)
```

**Problems:**
- Changes to logging require modifying `OrchestratorManager`
- Changes to metrics require modifying `OrchestratorManager`
- Changes to configuration require modifying `OrchestratorManager`
- Class is difficult to test (needs database, filesystem mocking)
- High coupling - everything depends on this one class

---

## 2️⃣ Open/Closed Principle (OCP)

**Definition:** Software entities should be OPEN for extension, but CLOSED for modification.

### ✅ CORRECT Example

```python
from abc import ABC, abstractmethod

# Base abstraction (CLOSED for modification)
class BaseOrchestrator(ABC):
    """Abstract base class for all orchestrators."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator_id = config["id"]
        self.priority = config.get("priority", 50)
    
    @abstractmethod
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrator logic (subclass implements)."""
        pass
    
    def validate(self) -> bool:
        """Validate orchestrator can execute (default implementation)."""
        return self.config is not None

# Extend via inheritance (OPEN for extension)
class PlanningOrchestrator(BaseOrchestrator):
    """Planning orchestrator implementation."""
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan."""
        phases = self._analyze_phases(request)
        plan = self._generate_plan(phases)
        
        return {
            "status": "success",
            "plan_id": plan.id,
            "phases": len(phases)
        }
    
    def _analyze_phases(self, request: str) -> List[Phase]:
        """Analyze request to identify phases."""
        # Planning-specific logic
        pass

class TDDOrchestrator(BaseOrchestrator):
    """TDD orchestrator implementation."""
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TDD workflow."""
        test_file = self._create_test(request)
        implementation = self._implement_code(test_file)
        
        return {
            "status": "success",
            "test_file": test_file,
            "implementation": implementation
        }
    
    def _create_test(self, request: str) -> str:
        """Create test file."""
        # TDD-specific logic
        pass

# Add new orchestrator WITHOUT modifying existing code
class InvestigationOrchestrator(BaseOrchestrator):
    """Investigation orchestrator implementation."""
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Investigate root cause."""
        symptoms = self._collect_symptoms(request)
        root_cause = self._analyze_root_cause(symptoms)
        
        return {
            "status": "success",
            "root_cause": root_cause,
            "evidence": symptoms
        }
```

**Why This Is Better:**
- Adding `InvestigationOrchestrator` doesn't modify `BaseOrchestrator`
- Existing orchestrators (`PlanningOrchestrator`, `TDDOrchestrator`) unaffected
- Easier to test new orchestrators in isolation
- Reduced risk of breaking existing functionality

---

### ❌ INCORRECT Example (OCP Violation)

```python
class Orchestrator:
    """Monolithic orchestrator - violates OCP."""
    
    def execute(self, request: str, orchestrator_type: str) -> Dict:
        """Execute based on type (BAD - requires modification for new types)."""
        
        if orchestrator_type == "planning":
            # Planning logic
            phases = self._analyze_phases(request)
            return {"status": "success", "phases": phases}
        
        elif orchestrator_type == "tdd":
            # TDD logic
            test = self._create_test(request)
            return {"status": "success", "test": test}
        
        elif orchestrator_type == "investigation":
            # Investigation logic (MODIFIED existing class)
            symptoms = self._collect_symptoms(request)
            return {"status": "success", "symptoms": symptoms}
        
        # Adding new orchestrator requires modifying this method
        elif orchestrator_type == "ado":
            # ADO logic (ANOTHER modification)
            work_item = self._create_work_item(request)
            return {"status": "success", "work_item": work_item}
        
        else:
            raise ValueError(f"Unknown orchestrator type: {orchestrator_type}")
```

**Problems:**
- Every new orchestrator requires modifying `Orchestrator.execute()`
- High risk of breaking existing orchestrator types
- Difficult to test (all types in one method)
- Violates Single Responsibility Principle too

---

## 3️⃣ Liskov Substitution Principle (LSP)

**Definition:** Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

### ✅ CORRECT Example

```python
from abc import ABC, abstractmethod

class BaseOrchestrator(ABC):
    """Base orchestrator with contract."""
    
    @abstractmethod
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrator.
        
        Contract:
        - Returns Dict[str, Any] with 'status' key
        - 'status' is one of: 'success', 'failure', 'partial'
        - Raises OrchestratorError on unrecoverable failure
        """
        pass
    
    def validate(self) -> bool:
        """Validate orchestrator ready.
        
        Contract:
        - Returns True if orchestrator can execute
        - Returns False otherwise (no exceptions)
        """
        return True

# Subclass 1: Respects contract
class PlanningOrchestrator(BaseOrchestrator):
    """Planning orchestrator - respects LSP."""
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning (respects contract)."""
        try:
            plan = self._generate_plan(request)
            return {
                "status": "success",
                "plan_id": plan.id,
                "phases": len(plan.phases)
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e)
            }
    
    def validate(self) -> bool:
        """Validate planning orchestrator."""
        return self.config is not None and self.state_manager.is_healthy()

# Subclass 2: Also respects contract
class TDDOrchestrator(BaseOrchestrator):
    """TDD orchestrator - respects LSP."""
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TDD workflow (respects contract)."""
        test_result = self._run_tdd_cycle(request)
        
        return {
            "status": "success" if test_result.passed else "partial",
            "tests_created": test_result.test_count,
            "tests_passed": test_result.passed_count
        }
    
    def validate(self) -> bool:
        """Validate TDD orchestrator."""
        return self.test_framework.is_available()

# Client code: Works with ANY orchestrator (LSP satisfied)
def execute_orchestrator(
    orchestrator: BaseOrchestrator,
    request: str
) -> Dict[str, Any]:
    """Execute any orchestrator (type-safe substitution)."""
    if not orchestrator.validate():
        return {"status": "failure", "error": "Validation failed"}
    
    result = orchestrator.execute(request, {})
    
    # Can safely access 'status' - contract guaranteed
    if result["status"] == "success":
        print("✅ Execution successful")
    else:
        print("❌ Execution failed")
    
    return result

# Both work identically
planning = PlanningOrchestrator(config)
tdd = TDDOrchestrator(config)

execute_orchestrator(planning, "plan API")  # ✅ Works
execute_orchestrator(tdd, "test auth")      # ✅ Works
```

---

### ❌ INCORRECT Example (LSP Violation)

```python
class BaseOrchestrator(ABC):
    @abstractmethod
    def execute(self, request: str, context: Dict) -> Dict:
        """Returns Dict with 'status' key."""
        pass

class PlanningOrchestrator(BaseOrchestrator):
    def execute(self, request: str, context: Dict) -> Dict:
        """Returns Dict (respects contract)."""
        return {"status": "success", "plan_id": "abc123"}

# ❌ LSP VIOLATION: Changes return type
class TDDOrchestrator(BaseOrchestrator):
    def execute(self, request: str, context: Dict) -> str:
        """Returns string instead of Dict (violates contract)."""
        return "Test created successfully"

# Client code breaks
def execute_orchestrator(orchestrator: BaseOrchestrator, request: str):
    result = orchestrator.execute(request, {})
    print(result["status"])  # ❌ Crashes if TDDOrchestrator (no 'status' key)

# ❌ Another LSP VIOLATION: Adds precondition
class SanitizationOrchestrator(BaseOrchestrator):
    def execute(self, request: str, context: Dict) -> Dict:
        """Requires context['file_path'] (stricter precondition)."""
        if "file_path" not in context:
            raise ValueError("Missing file_path")  # ❌ Base class doesn't require this
        
        return {"status": "success"}

# ❌ LSP VIOLATION: Weakens postcondition
class DebugOrchestrator(BaseOrchestrator):
    def execute(self, request: str, context: Dict) -> Dict:
        """Sometimes returns None (weakens contract)."""
        if self.can_debug(request):
            return {"status": "success"}
        else:
            return None  # ❌ Base class says "returns Dict", not Optional[Dict]
```

**Problems:**
- `TDDOrchestrator` breaks client code expecting Dict
- `SanitizationOrchestrator` requires extra context (client must know specific type)
- `DebugOrchestrator` returns None (client must check type before accessing)
- Cannot substitute subclass for base class without breaking code

---

## 4️⃣ Interface Segregation Principle (ISP)

**Definition:** Clients should not be forced to depend on interfaces they don't use.

### ✅ CORRECT Example

```python
from typing import Protocol

# Small, focused interfaces (protocols)
class Executable(Protocol):
    """Interface for executable components."""
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        ...

class Cancellable(Protocol):
    """Interface for cancellable components."""
    def cancel(self) -> None:
        ...
    
    def is_cancelled(self) -> bool:
        ...

class Pausable(Protocol):
    """Interface for pausable components."""
    def pause(self) -> None:
        ...
    
    def resume(self) -> None:
        ...
    
    def is_paused(self) -> bool:
        ...

class Monitorable(Protocol):
    """Interface for monitorable components."""
    def get_status(self) -> str:
        ...
    
    def get_progress(self) -> float:
        ...

# Orchestrator 1: Only needs execute (implements ONE interface)
class QuickOrchestrator:
    """Quick orchestrator - only executable."""
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quickly (no cancellation, pause, monitoring needed)."""
        return {"status": "success"}

# Orchestrator 2: Needs execute + cancel (implements TWO interfaces)
class LongRunningOrchestrator:
    """Long-running orchestrator - executable + cancellable."""
    
    def __init__(self):
        self._cancelled = False
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with cancellation support."""
        while not self._cancelled:
            # Process work
            pass
        return {"status": "cancelled"}
    
    def cancel(self) -> None:
        """Cancel execution."""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._cancelled

# Orchestrator 3: Needs all features (implements FOUR interfaces)
class InteractiveOrchestrator:
    """Interactive orchestrator - all capabilities."""
    
    def __init__(self):
        self._cancelled = False
        self._paused = False
        self._progress = 0.0
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with full control."""
        return {"status": "success"}
    
    def cancel(self) -> None:
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        return self._cancelled
    
    def pause(self) -> None:
        self._paused = True
    
    def resume(self) -> None:
        self._paused = False
    
    def is_paused(self) -> bool:
        return self._paused
    
    def get_status(self) -> str:
        return "running" if not self._paused else "paused"
    
    def get_progress(self) -> float:
        return self._progress

# Client code: Only depends on needed interface
def execute_simple(orchestrator: Executable):
    """Only needs execute capability."""
    return orchestrator.execute("request", {})

def execute_cancellable(orchestrator: Cancellable & Executable):
    """Needs execute + cancel capability."""
    result = orchestrator.execute("request", {})
    if should_cancel():
        orchestrator.cancel()
    return result
```

---

### ❌ INCORRECT Example (ISP Violation)

```python
from abc import ABC, abstractmethod

# Fat interface - forces all orchestrators to implement everything
class OrchestratorInterface(ABC):
    """Fat interface - violates ISP."""
    
    @abstractmethod
    def execute(self, request: str) -> Dict:
        """Execute orchestrator."""
        pass
    
    @abstractmethod
    def cancel(self) -> None:
        """Cancel execution (NOT all orchestrators need this)."""
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Pause execution (NOT all orchestrators need this)."""
        pass
    
    @abstractmethod
    def resume(self) -> None:
        """Resume execution (NOT all orchestrators need this)."""
        pass
    
    @abstractmethod
    def get_progress(self) -> float:
        """Get progress (NOT all orchestrators need this)."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback changes (NOT all orchestrators need this)."""
        pass

# ❌ Forced to implement unused methods
class QuickOrchestrator(OrchestratorInterface):
    """Quick orchestrator - doesn't need cancel/pause/progress."""
    
    def execute(self, request: str) -> Dict:
        """Actually needed."""
        return {"status": "success"}
    
    # ❌ Forced to implement (doesn't make sense for this orchestrator)
    def cancel(self) -> None:
        raise NotImplementedError("Quick orchestrator cannot be cancelled")
    
    def pause(self) -> None:
        raise NotImplementedError("Quick orchestrator cannot be paused")
    
    def resume(self) -> None:
        raise NotImplementedError("Quick orchestrator cannot be resumed")
    
    def get_progress(self) -> float:
        raise NotImplementedError("Quick orchestrator has no progress")
    
    def rollback(self) -> None:
        raise NotImplementedError("Quick orchestrator has no rollback")
```

**Problems:**
- `QuickOrchestrator` forced to implement 5 methods it doesn't need
- Raises `NotImplementedError` at runtime (defeats purpose of type checking)
- Misleads clients (interface says `cancel()` exists, but it throws exception)

---

## 5️⃣ Dependency Inversion Principle (DIP)

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

### ✅ CORRECT Example

```python
from abc import ABC, abstractmethod

# Abstraction (neither high-level nor low-level depends on concrete)
class StateStore(ABC):
    """Abstract state storage interface."""
    
    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """Save state."""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Any:
        """Load state."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete state."""
        pass

# Low-level module (depends on abstraction)
class SQLiteStateStore(StateStore):
    """Concrete SQLite implementation."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def save(self, key: str, value: Any) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO states VALUES (?, ?)",
            (key, json.dumps(value))
        )
        self.conn.commit()
    
    def load(self, key: str) -> Any:
        row = self.conn.execute(
            "SELECT value FROM states WHERE key = ?",
            (key,)
        ).fetchone()
        return json.loads(row[0]) if row else None
    
    def delete(self, key: str) -> None:
        self.conn.execute("DELETE FROM states WHERE key = ?", (key,))
        self.conn.commit()

# Another low-level module (depends on same abstraction)
class RedisStateStore(StateStore):
    """Concrete Redis implementation."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def save(self, key: str, value: Any) -> None:
        self.redis.set(key, json.dumps(value))
    
    def load(self, key: str) -> Any:
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def delete(self, key: str) -> None:
        self.redis.delete(key)

# High-level module (depends on abstraction, NOT concrete implementation)
class PlanningOrchestrator:
    """High-level orchestrator."""
    
    def __init__(self, state_store: StateStore):  # Depends on abstraction
        self.state = state_store
    
    def execute(self, request: str) -> Dict[str, Any]:
        """Execute planning."""
        # Load previous state (doesn't care if SQLite or Redis)
        previous_plan = self.state.load("last_plan")
        
        # Generate new plan
        new_plan = self._generate_plan(request, previous_plan)
        
        # Save state (doesn't care about implementation)
        self.state.save("last_plan", new_plan)
        
        return {"status": "success", "plan": new_plan}

# Dependency injection: Choose implementation at runtime
sqlite_store = SQLiteStateStore("state.db")
redis_store = RedisStateStore(redis.Redis())

# Both work (orchestrator doesn't care)
orchestrator1 = PlanningOrchestrator(sqlite_store)  # ✅
orchestrator2 = PlanningOrchestrator(redis_store)   # ✅
```

**Benefits:**
- `PlanningOrchestrator` doesn't know about SQLite or Redis
- Easy to test (`PlanningOrchestrator` with `MockStateStore`)
- Easy to switch storage (production vs. test)
- New storage backends don't affect orchestrator

---

### ❌ INCORRECT Example (DIP Violation)

```python
# ❌ High-level module depends on low-level concrete implementation
class PlanningOrchestrator:
    """High-level orchestrator - violates DIP."""
    
    def __init__(self, db_path: str):
        # ❌ Tightly coupled to SQLite (low-level)
        self.db = sqlite3.connect(db_path)
        self.db.execute("CREATE TABLE IF NOT EXISTS states ...")
    
    def execute(self, request: str) -> Dict:
        """Execute planning."""
        # ❌ Directly uses SQLite API
        row = self.db.execute(
            "SELECT value FROM states WHERE key = ?",
            ("last_plan",)
        ).fetchone()
        
        previous_plan = json.loads(row[0]) if row else None
        new_plan = self._generate_plan(request, previous_plan)
        
        # ❌ Directly uses SQLite API
        self.db.execute(
            "INSERT OR REPLACE INTO states VALUES (?, ?)",
            ("last_plan", json.dumps(new_plan))
        )
        self.db.commit()
        
        return {"status": "success"}

# ❌ Cannot switch to Redis without modifying PlanningOrchestrator
# ❌ Cannot test with mock (hardcoded sqlite3.connect)
# ❌ High coupling to SQLite
```

---

## 📊 SOLID Compliance Checklist

Use this checklist when reviewing code:

### Single Responsibility Principle (SRP)
- [ ] Each class has ONE reason to change
- [ ] Class name clearly describes its single responsibility
- [ ] No "Manager" or "Handler" god classes
- [ ] Extract helper classes if class >300 lines

### Open/Closed Principle (OCP)
- [ ] Use inheritance/composition to extend, not modification
- [ ] Abstract base classes define contracts
- [ ] New features added via new classes, not `if/elif` chains
- [ ] Plugins loadable without core code changes

### Liskov Substitution Principle (LSP)
- [ ] Subclass can replace parent without breaking code
- [ ] Subclass doesn't strengthen preconditions
- [ ] Subclass doesn't weaken postconditions
- [ ] Return types consistent across hierarchy

### Interface Segregation Principle (ISP)
- [ ] Small, focused interfaces (protocols)
- [ ] Clients only depend on methods they use
- [ ] No fat interfaces forcing unused method implementations
- [ ] Compose interfaces when multiple capabilities needed

### Dependency Inversion Principle (DIP)
- [ ] Depend on abstractions (ABC, Protocol), not concretions
- [ ] Dependency injection (pass dependencies to `__init__`)
- [ ] High-level modules independent of low-level modules
- [ ] Easy to swap implementations (e.g., SQLite → PostgreSQL)

---

## 🎯 CORTEX-Specific Application

**Master Orchestrator (SRP + DIP):**
- Single responsibility: Route requests
- Depends on abstractions: `OrchestratorRegistry`, `PatternRouter`, `ExecutionEngine`

**Orchestrator Registry (OCP + ISP):**
- Open for extension: Add orchestrators without modification
- Interface segregation: Only defines registration/lookup, not execution

**Child Orchestrators (LSP + OCP):**
- Liskov substitution: All return `Dict[str, Any]` with 'status'
- Open/closed: Extend `BaseOrchestrator`, don't modify it

**State Management (DIP):**
- Dependency inversion: Orchestrators depend on `StateStore` abstraction
- Implementations: `SQLiteStateStore`, `RedisStateStore`, `InMemoryStateStore`

---

## ✅ Enforcement

SOLID principles enforced by:
1. **PythonBestPracticesValidator** middleware (Phase P01.4)
2. **Architecture review** (cortex-review.prompt.md Phase 7, Section D)
3. **Code review checklist** (mandatory before PR approval)
4. **Static analysis** (pylint SOLID checks)

**Non-compliance results in PR rejection.**
