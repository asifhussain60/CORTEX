# Python Architecture Patterns for CORTEX

**Version:** 1.0.0  
**Status:** ✅ MANDATORY  
**Domain:** Python AI Application Development  
**Enforcement:** PythonBestPracticesValidator middleware

---

## 🎯 Overview

This document defines Python architecture patterns specifically for **AI-powered autonomous orchestration systems** like CORTEX. These patterns address unique challenges:

- **LLM → Python Handoff:** Seamless transition from language model to script execution
- **Autonomous Execution:** Scripts run without human intervention
- **Dynamic Orchestrator Loading:** Runtime plugin discovery and instantiation
- **Stateful Workflows:** Multi-phase plan execution with persistence
- **Concurrent Orchestration:** Multiple orchestrators running simultaneously

---

## 🏗️ Core Architectural Patterns

### 1. Master-Child Orchestrator Pattern

**Problem:** Centralized routing with decentralized execution.

**Solution:** Master orchestrator routes requests, child orchestrators execute specialized workflows.

```python
# Master Orchestrator (Single Entry Point)
from abc import ABC, abstractmethod
from typing import Dict, Any, Protocol

class OrchestratorInterface(Protocol):
    """Protocol defining orchestrator contract."""
    
    orchestrator_id: str
    priority: int
    patterns: List[str]
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrator logic."""
        ...
    
    def validate(self) -> bool:
        """Validate orchestrator can execute."""
        ...

class MasterOrchestrator:
    """Routes requests to child orchestrators."""
    
    def __init__(
        self,
        registry: OrchestratorRegistry,
        router: PatternRouter,
        executor: ExecutionEngine
    ):
        self.registry = registry
        self.router = router
        self.executor = executor
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Route and execute request."""
        # 1. Pattern matching
        match = self.router.match_pattern(request)
        
        # 2. Load orchestrator
        orchestrator = self.registry.get(match.orchestrator_id)
        
        # 3. Execute
        result = self.executor.execute(orchestrator, request)
        
        return result

# Child Orchestrator (Specialized Execution)
class PlanningOrchestrator:
    """Specialized orchestrator for plan generation."""
    
    orchestrator_id: str = "planning_v5"
    priority: int = 10
    patterns: List[str] = [r"^(plan|create a plan)"]
    
    def __init__(
        self,
        config_path: str,
        state_manager: StateManager,
        template_engine: TemplateEngine
    ):
        self.config = self._load_config(config_path)
        self.state = state_manager
        self.templates = template_engine
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan."""
        # Phase-based execution
        phases = self._analyze_phases(request)
        plan = self._generate_plan(phases)
        self.state.save_plan(plan)
        
        return {
            "status": "success",
            "plan_id": plan.id,
            "phases": len(phases)
        }
    
    def validate(self) -> bool:
        """Validate orchestrator ready."""
        return (
            self.config.is_valid() and
            self.state.is_healthy() and
            self.templates.are_loaded()
        )
```

**Benefits:**
- ✅ Single entry point (MasterOrchestrator)
- ✅ Isolated orchestrator logic (no coupling)
- ✅ Protocol-based interface (type safety)
- ✅ Dynamic registration (runtime plugin loading)

---

### 2. Plugin Architecture with Dynamic Loading

**Problem:** Add new orchestrators without modifying core system.

**Solution:** Registry-based plugin discovery with lazy loading.

```python
from typing import Type, Dict, Any
import importlib
import json

class OrchestratorRegistry:
    """Dynamic orchestrator plugin registry."""
    
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.orchestrators: Dict[str, OrchestratorInterface] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load orchestrator metadata from registry file."""
        with open(self.registry_path) as f:
            registry_data = json.load(f)
        
        for entry in registry_data["orchestrators"]:
            self._metadata[entry["id"]] = entry
    
    def get(self, orchestrator_id: str) -> OrchestratorInterface:
        """Get orchestrator instance (lazy loading)."""
        # Check cache first
        if orchestrator_id in self.orchestrators:
            return self.orchestrators[orchestrator_id]
        
        # Load from metadata
        if orchestrator_id not in self._metadata:
            raise OrchestratorNotFoundError(f"Unknown: {orchestrator_id}")
        
        metadata = self._metadata[orchestrator_id]
        orchestrator = self._instantiate_orchestrator(metadata)
        
        # Cache for future use
        self.orchestrators[orchestrator_id] = orchestrator
        return orchestrator
    
    def _instantiate_orchestrator(
        self,
        metadata: Dict[str, Any]
    ) -> OrchestratorInterface:
        """Dynamically import and instantiate orchestrator."""
        # Import module
        module_path = metadata["module"]
        class_name = metadata["class"]
        
        module = importlib.import_module(module_path)
        orchestrator_class = getattr(module, class_name)
        
        # Instantiate with dependencies
        dependencies = self._resolve_dependencies(metadata["dependencies"])
        orchestrator = orchestrator_class(**dependencies)
        
        # Validate before returning
        if not orchestrator.validate():
            raise OrchestratorValidationError(
                f"Orchestrator {metadata['id']} failed validation"
            )
        
        return orchestrator
    
    def register(
        self,
        orchestrator_id: str,
        orchestrator: OrchestratorInterface
    ) -> None:
        """Register orchestrator at runtime."""
        if not isinstance(orchestrator, OrchestratorInterface):
            raise TypeError("Must implement OrchestratorInterface")
        
        if not orchestrator.validate():
            raise OrchestratorValidationError("Validation failed")
        
        self.orchestrators[orchestrator_id] = orchestrator

# Registry JSON Format
# cortex-brain/registry/orchestrators.json
{
    "orchestrators": [
        {
            "id": "planning_v5",
            "module": "src.orchestrators.planning.planning_orchestrator_v5",
            "class": "PlanningOrchestratorV5",
            "priority": 10,
            "patterns": ["^(plan|create a plan)"],
            "dependencies": {
                "config_path": "cortex-brain/config/planning.yaml",
                "state_manager": {"type": "StateManager", "args": ["state.db"]},
                "template_engine": {"type": "TemplateEngine", "args": []}
            }
        }
    ]
}
```

**Benefits:**
- ✅ No core code changes for new orchestrators
- ✅ Lazy loading (performance)
- ✅ Dependency injection (testability)
- ✅ Validation before registration (safety)

---

### 3. Strategy Pattern for Execution Modes

**Problem:** Different orchestrators have different execution strategies (autonomous, guided, interactive).

**Solution:** Strategy pattern with mode-specific executors.

```python
from abc import ABC, abstractmethod
from enum import Enum

class ExecutionMode(Enum):
    """Execution mode enumeration."""
    AUTONOMOUS = "autonomous"  # Fully automated
    GUIDED = "guided"          # LLM-assisted
    INTERACTIVE = "interactive" # User-driven

class ExecutionStrategy(ABC):
    """Abstract execution strategy."""
    
    @abstractmethod
    def execute(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute orchestrator with mode-specific logic."""
        pass

class AutonomousExecutionStrategy(ExecutionStrategy):
    """Fully automated execution (Python scripts only)."""
    
    def execute(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute without LLM interaction."""
        # Pure Python execution
        return orchestrator.execute(request, context)

class GuidedExecutionStrategy(ExecutionStrategy):
    """LLM-assisted execution."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def execute(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute with LLM guidance at decision points."""
        # Get initial plan from orchestrator
        plan = orchestrator.execute(request, context)
        
        # LLM reviews each phase
        for phase in plan["phases"]:
            review = self.llm.review_phase(phase)
            if review["needs_adjustment"]:
                phase.update(review["adjustments"])
        
        return plan

class InteractiveExecutionStrategy(ExecutionStrategy):
    """User-driven execution."""
    
    def __init__(self, ui_handler: UIHandler):
        self.ui = ui_handler
    
    def execute(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute with user confirmation at each step."""
        result = {"status": "in_progress", "steps": []}
        
        for step in orchestrator.get_steps(request):
            # Ask user to proceed
            if self.ui.confirm(f"Execute: {step.description}?"):
                step_result = orchestrator.execute_step(step)
                result["steps"].append(step_result)
            else:
                result["status"] = "cancelled"
                break
        
        return result

class ExecutionEngine:
    """Execution engine with strategy pattern."""
    
    def __init__(self):
        self.strategies: Dict[ExecutionMode, ExecutionStrategy] = {
            ExecutionMode.AUTONOMOUS: AutonomousExecutionStrategy(),
            ExecutionMode.GUIDED: GuidedExecutionStrategy(llm_client),
            ExecutionMode.INTERACTIVE: InteractiveExecutionStrategy(ui_handler)
        }
    
    def execute(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        mode: ExecutionMode = ExecutionMode.AUTONOMOUS
    ) -> Dict[str, Any]:
        """Execute orchestrator with specified mode."""
        strategy = self.strategies[mode]
        return strategy.execute(orchestrator, request, {})
```

**Benefits:**
- ✅ Mode selection at runtime
- ✅ Each mode independently testable
- ✅ Easy to add new execution modes
- ✅ Clear separation of concerns

---

### 4. Repository Pattern for State Management

**Problem:** Orchestrators need persistent state across executions.

**Solution:** Repository pattern with abstract storage interface.

```python
from abc import ABC, abstractmethod
from typing import Optional, List
import json
import sqlite3

class StateRepository(ABC):
    """Abstract repository for state persistence."""
    
    @abstractmethod
    def save(self, state_id: str, state_data: Dict[str, Any]) -> None:
        """Save state."""
        pass
    
    @abstractmethod
    def load(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Load state."""
        pass
    
    @abstractmethod
    def delete(self, state_id: str) -> None:
        """Delete state."""
        pass
    
    @abstractmethod
    def list_states(self, filter_criteria: Dict[str, Any]) -> List[str]:
        """List state IDs matching criteria."""
        pass

class SQLiteStateRepository(StateRepository):
    """SQLite implementation with WAL mode for concurrency."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database with WAL mode."""
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS states (
                    state_id TEXT PRIMARY KEY,
                    state_type TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                conn.row_factory = sqlite3.Row
                yield conn
                conn.commit()
                return
            except sqlite3.OperationalError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1 * (2 ** attempt))
            finally:
                conn.close()
    
    def save(self, state_id: str, state_data: Dict[str, Any]) -> None:
        """Save state with transaction."""
        with self._get_connection() as conn:
            now = datetime.now().isoformat()
            conn.execute(
                """
                INSERT OR REPLACE INTO states 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    state_id,
                    state_data.get("type", "generic"),
                    json.dumps(state_data),
                    now,
                    now
                )
            )
    
    def load(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Load state."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT state_data FROM states WHERE state_id = ?",
                (state_id,)
            ).fetchone()
            
            if row:
                return json.loads(row["state_data"])
            return None

class StateManager:
    """High-level state management with repository pattern."""
    
    def __init__(self, repository: StateRepository):
        self.repository = repository
    
    def save_plan(self, plan: ExecutionPlan) -> None:
        """Save execution plan."""
        self.repository.save(
            state_id=f"plan_{plan.id}",
            state_data={
                "type": "execution_plan",
                "plan_id": plan.id,
                "phases": [phase.to_dict() for phase in plan.phases],
                "status": plan.status
            }
        )
    
    def load_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """Load execution plan."""
        state_data = self.repository.load(f"plan_{plan_id}")
        if state_data:
            return ExecutionPlan.from_dict(state_data)
        return None
```

**Benefits:**
- ✅ Swappable storage backends (SQLite, PostgreSQL, Redis)
- ✅ Transactional safety
- ✅ Concurrent access support (WAL mode)
- ✅ Testable with in-memory mock

---

### 5. Chain of Responsibility for Middleware

**Problem:** Cross-cutting concerns (logging, validation, caching) clutter orchestrator logic.

**Solution:** Middleware chain wraps orchestrator execution.

```python
from abc import ABC, abstractmethod
from typing import Callable

class Middleware(ABC):
    """Abstract middleware in chain."""
    
    def __init__(self, next_middleware: Optional['Middleware'] = None):
        self.next = next_middleware
    
    @abstractmethod
    def process(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process request and pass to next middleware."""
        pass

class LoggingMiddleware(Middleware):
    """Log all orchestrator executions."""
    
    def __init__(self, logger: Logger, next_middleware: Optional[Middleware] = None):
        super().__init__(next_middleware)
        self.logger = logger
    
    def process(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log execution and pass through."""
        self.logger.info(f"Executing: {orchestrator.orchestrator_id}")
        self.logger.debug(f"Request: {request}")
        
        # Execute next in chain
        result = self.next.process(orchestrator, request, context) if self.next else {}
        
        self.logger.info(f"Completed: {orchestrator.orchestrator_id}")
        self.logger.debug(f"Result: {result.get('status')}")
        
        return result

class ValidationMiddleware(Middleware):
    """Validate inputs and outputs."""
    
    def process(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and pass through."""
        # Pre-execution validation
        if not request.strip():
            raise ValueError("Empty request")
        
        if not orchestrator.validate():
            raise OrchestratorValidationError("Orchestrator not ready")
        
        # Execute next
        result = self.next.process(orchestrator, request, context) if self.next else {}
        
        # Post-execution validation
        if "status" not in result:
            raise ValueError("Missing status in result")
        
        return result

class CachingMiddleware(Middleware):
    """Cache orchestrator results."""
    
    def __init__(self, cache: Cache, next_middleware: Optional[Middleware] = None):
        super().__init__(next_middleware)
        self.cache = cache
    
    def process(
        self,
        orchestrator: OrchestratorInterface,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check cache, execute if miss, cache result."""
        cache_key = f"{orchestrator.orchestrator_id}:{hash(request)}"
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Cache miss - execute
        result = self.next.process(orchestrator, request, context) if self.next else {}
        
        # Cache result
        self.cache.set(cache_key, result, ttl=3600)
        
        return result

# Build middleware chain
chain = LoggingMiddleware(
    logger=get_logger(),
    next_middleware=ValidationMiddleware(
        next_middleware=CachingMiddleware(
            cache=get_cache(),
            next_middleware=None  # Terminal (actual execution)
        )
    )
)

# Execute through chain
result = chain.process(orchestrator, request, context)
```

**Benefits:**
- ✅ Separation of concerns
- ✅ Reusable middleware
- ✅ Composable chains
- ✅ Easy to add/remove middleware

---

## 🎯 CORTEX-Specific Patterns

### 6. LLM → Python Handoff Pattern

**Problem:** Transition from GitHub Copilot (LLM) to Python orchestrator execution.

**Solution:** Structured request transformation + terminal invocation.

```python
# GitHub Copilot Side (TypeScript/JavaScript in VS Code)
interface CortexRequest {
    rawRequest: string;
    transformedRequest: string;
    orchestratorId: string;
    confidence: number;
    context: Record<string, any>;
}

async function processCortexRequest(rawRequest: string): Promise<void> {
    // 1. Strip meta-directives
    const cleanedRequest = stripMetaDirectives(rawRequest);
    
    // 2. Pattern matching
    const match = await matchPattern(cleanedRequest);
    
    // 3. Request transformation
    const transformedRequest = await transformRequest(cleanedRequest, match);
    
    // 4. Invoke Python via terminal
    const terminalCommand = `python3 -m src.main "${transformedRequest}" --format markdown`;
    
    await vscode.window.activeTerminal.sendText(terminalCommand);
}

// Python Side (Master Orchestrator)
class MasterOrchestrator:
    """Python orchestrator receives control from LLM."""
    
    def execute_from_llm(self, transformed_request: str) -> Dict[str, Any]:
        """Execute request handed off from LLM."""
        # LLM already did pattern matching and transformation
        # Python takes over for execution
        
        # Parse request metadata
        metadata = self._extract_metadata(transformed_request)
        orchestrator_id = metadata.get("orchestrator_id")
        
        # Load and execute orchestrator
        orchestrator = self.registry.get(orchestrator_id)
        result = self.executor.execute(orchestrator, transformed_request)
        
        return result
```

---

### 7. Snowball Effect Optimization Pattern

**Problem:** Phase dependencies create bottlenecks.

**Solution:** Dependency graph analysis with parallel execution.

```python
from typing import Set, List
from dataclasses import dataclass

@dataclass
class Phase:
    """Execution phase with dependencies."""
    phase_id: str
    name: str
    dependencies: Set[str]  # Phase IDs this phase depends on
    estimated_duration: int  # Minutes
    
class SnowballOptimizer:
    """Optimize phase execution order for maximum parallelism."""
    
    def optimize_execution_order(self, phases: List[Phase]) -> List[List[Phase]]:
        """Return phases grouped by execution wave (parallelizable)."""
        dependency_graph = self._build_dependency_graph(phases)
        execution_waves = []
        executed = set()
        
        while len(executed) < len(phases):
            # Find phases with satisfied dependencies
            current_wave = [
                phase for phase in phases
                if phase.phase_id not in executed
                and phase.dependencies.issubset(executed)
            ]
            
            if not current_wave:
                raise CyclicDependencyError("Cyclic dependencies detected")
            
            execution_waves.append(current_wave)
            executed.update(phase.phase_id for phase in current_wave)
        
        return execution_waves
    
    def calculate_critical_path(self, phases: List[Phase]) -> List[Phase]:
        """Calculate critical path (longest duration chain)."""
        # Implementation of critical path method
        pass
```

---

## ✅ Pattern Enforcement

These patterns are enforced by:
1. **PythonBestPracticesValidator** middleware
2. **OrchestratorInterface** protocol (mandatory contract)
3. **Architecture review checklist** (cortex-review.prompt.md Phase 2)
4. **Pre-commit hooks** (pattern detection)

**Reference:** Used by CORTEX-5 Epic Phase 1-4 architecture implementation.
