# Python Style Guide - CORTEX Standards

**Version:** 1.0.0  
**Status:** ✅ MANDATORY  
**Applies To:** All Python code in CORTEX project  
**Authority:** PEP 8, PEP 257, PEP 484, Python Best Practices  
**Enforcement:** PythonBestPracticesValidator middleware

---

## 🎯 Overview

This guide defines mandatory Python coding standards for CORTEX, an AI-powered autonomous orchestration system. Code quality is CRITICAL because CORTEX generates and executes Python scripts autonomously.

**Key Principles:**
1. **Readability Over Cleverness** - Code is read 10x more than written
2. **Type Safety** - Type hints MANDATORY for all functions/methods
3. **Explicit Over Implicit** - No magic, no surprises
4. **Test-Driven** - Tests written BEFORE implementation
5. **Self-Documenting** - Code explains itself, docstrings explain why

---

## 📋 PEP 8 Compliance (Mandatory)

### Indentation
```python
# ✅ CORRECT: 4 spaces per indentation level
def process_data(items: List[str]) -> Dict[str, int]:
    result = {}
    for item in items:
        result[item] = len(item)
    return result

# ❌ INCORRECT: Tabs or 2 spaces
def process_data(items: List[str]) -> Dict[str, int]:
  result = {}
  for item in items:
    result[item] = len(item)
  return result
```

### Line Length
```python
# ✅ CORRECT: Max 100 characters (more practical than PEP 8's 79)
def calculate_weighted_score(
    metrics: Dict[str, float],
    weights: Dict[str, float],
    normalize: bool = True
) -> float:
    """Calculate weighted score with optional normalization."""
    pass

# ❌ INCORRECT: Over 100 characters
def calculate_weighted_score(metrics: Dict[str, float], weights: Dict[str, float], normalize: bool = True) -> float:
    pass
```

### Naming Conventions
```python
# ✅ CORRECT
class OrchestratorRegistry:           # PascalCase for classes
    DEFAULT_TIMEOUT = 30              # SCREAMING_SNAKE_CASE for constants
    
    def __init__(self, config_path: str):
        self.config_path = config_path   # snake_case for attributes
        self._cache = {}                 # Leading underscore for private
    
    def register_orchestrator(self, name: str) -> bool:  # snake_case for methods
        """Register an orchestrator."""
        pass

# ❌ INCORRECT
class orchestrator_registry:          # Wrong case
    defaultTimeout = 30               # Wrong case for constant
    
    def RegisterOrchestrator(self, name):  # Wrong case for method
        pass
```

### Import Organization
```python
# ✅ CORRECT: Organized in 3 groups with blank line separation
# 1. Standard library
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party
import yaml
from pydantic import BaseModel

# 3. Local application
from src.orchestrators.base import BaseOrchestrator
from src.utils.logger import get_logger

# ❌ INCORRECT: Mixed order, no separation
from src.orchestrators.base import BaseOrchestrator
import json
from pydantic import BaseModel
import sys
```

### Whitespace Rules
```python
# ✅ CORRECT: Proper spacing
result = calculate_score(x=10, y=20)
items = [1, 2, 3, 4]
config = {"timeout": 30, "retries": 3}

if score > threshold:
    process_data()

# ❌ INCORRECT: Inconsistent spacing
result=calculate_score( x = 10,y= 20 )
items=[1,2,3,4]
config={ "timeout":30 , "retries" : 3 }

if score>threshold:
    process_data( )
```

---

## 🏷️ Type Hints (Mandatory)

### Function Signatures
```python
# ✅ CORRECT: Complete type hints
from typing import Dict, List, Optional, Union

def process_orchestrator(
    orchestrator_id: str,
    config: Dict[str, Any],
    timeout: Optional[int] = None
) -> Dict[str, str]:
    """Process orchestrator with configuration."""
    return {"status": "success", "id": orchestrator_id}

# ❌ INCORRECT: Missing type hints
def process_orchestrator(orchestrator_id, config, timeout=None):
    return {"status": "success", "id": orchestrator_id}
```

### Class Attributes
```python
# ✅ CORRECT: Typed class attributes
from typing import ClassVar

class OrchestratorConfig:
    """Configuration for orchestrator execution."""
    
    # Class variable with type hint
    DEFAULT_TIMEOUT: ClassVar[int] = 30
    
    # Instance attributes with type hints
    name: str
    priority: int
    enabled: bool
    
    def __init__(self, name: str, priority: int = 10):
        self.name = name
        self.priority = priority
        self.enabled = True

# ❌ INCORRECT: Untyped attributes
class OrchestratorConfig:
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, name, priority=10):
        self.name = name
        self.priority = priority
```

### Complex Types
```python
# ✅ CORRECT: Proper complex type annotations
from typing import Callable, Dict, List, Optional, Union, TypedDict

class ExecutionResult(TypedDict):
    """Typed dictionary for execution results."""
    status: str
    message: str
    artifacts: List[str]

def execute_with_callback(
    orchestrator_id: str,
    callback: Callable[[ExecutionResult], None],
    retry_strategy: Optional[Union[str, Dict[str, int]]] = None
) -> ExecutionResult:
    """Execute orchestrator with callback."""
    pass
```

---

## 📚 Docstrings (PEP 257 + Google Style)

### Module Docstrings
```python
"""Orchestrator pattern router for CORTEX.

This module provides pattern matching and routing capabilities for the master
orchestrator. It uses regex patterns with priority-based routing to determine
which child orchestrator should handle a given request.

Classes:
    PatternRouter: Main router implementation
    PatternMatch: Dataclass for match results

Example:
    >>> router = PatternRouter()
    >>> match = router.match_pattern("plan user authentication")
    >>> print(match.orchestrator_id)
    'planning_v5'

Author: Asif Hussain
Version: 2.0.0
"""
```

### Class Docstrings
```python
class PatternRouter:
    """Routes user requests to appropriate orchestrators via pattern matching.
    
    The PatternRouter maintains a registry of regex patterns mapped to orchestrators.
    When given a user request, it evaluates all patterns in priority order and
    returns the first match. If no pattern matches, it triggers LLM-based
    intent classification as a fallback.
    
    Attributes:
        patterns: Ordered dictionary of {priority: [(regex, orchestrator_id)]}
        llm_classifier: Fallback LLM-based intent classifier
        metrics: Pattern matching performance metrics
    
    Thread Safety:
        This class is NOT thread-safe. Create separate instances per thread
        or use external locking.
    
    Example:
        >>> router = PatternRouter("config/patterns.yaml")
        >>> match = router.match_pattern("investigate database slowness")
        >>> if match.confidence > 0.8:
        ...     orchestrator = load_orchestrator(match.orchestrator_id)
    """
```

### Function/Method Docstrings
```python
def match_pattern(
    self,
    user_request: str,
    context: Optional[Dict[str, Any]] = None
) -> PatternMatch:
    """Match user request against registered patterns.
    
    Evaluates all regex patterns in descending priority order. Returns the
    first match with confidence >= 0.7. If no pattern matches, falls back
    to LLM-based intent classification.
    
    Args:
        user_request: Raw user input string (case-insensitive matching)
        context: Optional context dictionary with keys:
            - conversation_history: List of previous exchanges
            - workspace_state: Current workspace metadata
            - user_preferences: User-specific settings
    
    Returns:
        PatternMatch object containing:
            - orchestrator_id: Matched orchestrator identifier
            - confidence: Match confidence (0.0-1.0)
            - matched_pattern: The regex pattern that matched
            - extracted_params: Dict of extracted parameters
    
    Raises:
        PatternRoutingError: If no pattern matches AND LLM fallback fails
        InvalidRequestError: If user_request is empty or malformed
    
    Example:
        >>> match = router.match_pattern("plan API with auth")
        >>> assert match.orchestrator_id == "planning_v5"
        >>> assert match.confidence >= 0.9
        >>> assert "api" in match.extracted_params
    
    Performance:
        O(n) where n = number of registered patterns
        Typical: <5ms for 50 patterns
        
    Side Effects:
        - Increments self.metrics["total_matches"]
        - Logs match to audit trail (if enabled)
    """
```

---

## 🧱 SOLID Principles for Python

### Single Responsibility Principle (SRP)
```python
# ✅ CORRECT: Each class has ONE responsibility
class OrchestratorRegistry:
    """ONLY manages orchestrator registration and lookup."""
    
    def register(self, orchestrator: BaseOrchestrator) -> None:
        """Register an orchestrator."""
        pass
    
    def get(self, orchestrator_id: str) -> BaseOrchestrator:
        """Retrieve registered orchestrator."""
        pass

class OrchestratorExecutor:
    """ONLY executes orchestrators."""
    
    def execute(self, orchestrator: BaseOrchestrator, request: str) -> Dict:
        """Execute orchestrator with request."""
        pass

# ❌ INCORRECT: Class does too much
class OrchestratorManager:
    """Manages registration AND execution AND logging AND metrics."""
    
    def register(self, orchestrator): pass
    def execute(self, orchestrator, request): pass
    def log_execution(self, orchestrator, result): pass
    def calculate_metrics(self): pass
```

### Open/Closed Principle (OCP)
```python
# ✅ CORRECT: Open for extension, closed for modification
from abc import ABC, abstractmethod

class BaseOrchestrator(ABC):
    """Base class for all orchestrators."""
    
    @abstractmethod
    def execute(self, request: str) -> Dict[str, Any]:
        """Execute orchestrator logic."""
        pass

# Extend via inheritance, not modification
class PlanningOrchestrator(BaseOrchestrator):
    def execute(self, request: str) -> Dict[str, Any]:
        """Plan generation logic."""
        return {"status": "success", "plan": "..."}

# ❌ INCORRECT: Modify existing class for new functionality
class Orchestrator:
    def execute(self, request, orchestrator_type):
        if orchestrator_type == "planning":
            # Planning logic
            pass
        elif orchestrator_type == "tdd":
            # TDD logic  (BAD: modifying existing class)
            pass
```

### Liskov Substitution Principle (LSP)
```python
# ✅ CORRECT: Subclass can replace parent without breaking behavior
class BaseOrchestrator(ABC):
    def execute(self, request: str) -> Dict[str, Any]:
        """Execute and return result dict with 'status' key."""
        pass

class PlanningOrchestrator(BaseOrchestrator):
    def execute(self, request: str) -> Dict[str, Any]:
        """Executes planning logic, returns dict with 'status' key."""
        return {"status": "success", "plan_id": "abc123"}

# Substitutable:
orchestrator: BaseOrchestrator = PlanningOrchestrator()
result = orchestrator.execute("plan API")  # Always returns dict with 'status'

# ❌ INCORRECT: Subclass changes contract
class TDDOrchestrator(BaseOrchestrator):
    def execute(self, request: str) -> str:  # Returns str, not dict (LSP violation)
        return "Test created"
```

### Interface Segregation Principle (ISP)
```python
# ✅ CORRECT: Small, focused interfaces
class Executable(Protocol):
    """Interface for executable components."""
    def execute(self, request: str) -> Dict[str, Any]: ...

class Cancellable(Protocol):
    """Interface for cancellable components."""
    def cancel(self) -> None: ...

class Monitorable(Protocol):
    """Interface for monitorable components."""
    def get_status(self) -> str: ...

# Implement only needed interfaces
class QuickOrchestrator(Executable):
    """Only needs execute, not cancel or monitor."""
    def execute(self, request: str) -> Dict[str, Any]:
        return {"status": "success"}

# ❌ INCORRECT: Fat interface forcing unnecessary implementations
class OrchestratorInterface(ABC):
    @abstractmethod
    def execute(self, request: str): pass
    
    @abstractmethod
    def cancel(self): pass  # Not all orchestrators need this
    
    @abstractmethod
    def pause(self): pass   # Not all orchestrators need this
    
    @abstractmethod
    def resume(self): pass  # Not all orchestrators need this
```

### Dependency Inversion Principle (DIP)
```python
# ✅ CORRECT: Depend on abstractions, not concretions
from abc import ABC, abstractmethod

class StateStore(ABC):
    """Abstract state storage interface."""
    @abstractmethod
    def save(self, key: str, value: Any) -> None: ...
    
    @abstractmethod
    def load(self, key: str) -> Any: ...

class SQLiteStateStore(StateStore):
    """Concrete SQLite implementation."""
    def save(self, key: str, value: Any) -> None:
        # SQLite-specific logic
        pass
    
    def load(self, key: str) -> Any:
        # SQLite-specific logic
        pass

class Orchestrator:
    def __init__(self, state_store: StateStore):  # Depends on abstraction
        self.state = state_store

# ❌ INCORRECT: Depend on concrete implementation
class Orchestrator:
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)  # Tightly coupled to SQLite
```

---

## 🎯 Code Quality Standards

### DRY (Don't Repeat Yourself)
```python
# ✅ CORRECT: Extract common logic
def validate_orchestrator_config(config: Dict[str, Any]) -> bool:
    """Shared validation logic."""
    required_keys = ["name", "priority", "pattern"]
    return all(key in config for key in required_keys)

class PlanningOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        if not validate_orchestrator_config(config):
            raise ValueError("Invalid config")

class TDDOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        if not validate_orchestrator_config(config):
            raise ValueError("Invalid config")

# ❌ INCORRECT: Duplicated validation logic
class PlanningOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        if "name" not in config or "priority" not in config:
            raise ValueError("Invalid config")

class TDDOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        if "name" not in config or "priority" not in config:
            raise ValueError("Invalid config")
```

### KISS (Keep It Simple, Stupid)
```python
# ✅ CORRECT: Simple and clear
def is_valid_orchestrator_id(orchestrator_id: str) -> bool:
    """Check if orchestrator ID is valid."""
    return orchestrator_id.isidentifier() and not orchestrator_id.startswith("_")

# ❌ INCORRECT: Unnecessarily complex
def is_valid_orchestrator_id(orchestrator_id: str) -> bool:
    """Check if orchestrator ID is valid."""
    return bool(
        re.match(
            r'^(?!_)[a-zA-Z_][a-zA-Z0-9_]*$',
            orchestrator_id
        )
    ) if orchestrator_id and isinstance(orchestrator_id, str) else False
```

### YAGNI (You Aren't Gonna Need It)
```python
# ✅ CORRECT: Implement only what's needed now
class OrchestratorRegistry:
    def __init__(self):
        self.orchestrators: Dict[str, BaseOrchestrator] = {}
    
    def register(self, orchestrator: BaseOrchestrator) -> None:
        self.orchestrators[orchestrator.id] = orchestrator

# ❌ INCORRECT: Premature optimization/features
class OrchestratorRegistry:
    def __init__(self):
        self.orchestrators: Dict[str, BaseOrchestrator] = {}
        self.cache = LRUCache(maxsize=1000)  # Not needed yet
        self.metrics = MetricsCollector()     # Not needed yet
        self.event_bus = EventBus()           # Not needed yet
        self.backup_store = BackupStore()     # Not needed yet
```

### Cyclomatic Complexity Limit
```python
# ✅ CORRECT: Complexity <= 10, extract helper functions
def process_request(request: str, config: Dict) -> Dict:
    """Process request with validation."""
    if not request:
        raise ValueError("Empty request")
    
    # Extract validation to helper
    _validate_config(config)
    
    # Extract processing to helper
    result = _execute_processing(request, config)
    
    return result

def _validate_config(config: Dict) -> None:
    """Validate configuration."""
    if "timeout" not in config:
        raise ValueError("Missing timeout")
    if config["timeout"] <= 0:
        raise ValueError("Invalid timeout")

def _execute_processing(request: str, config: Dict) -> Dict:
    """Execute core processing logic."""
    # Implementation
    return {"status": "success"}

# ❌ INCORRECT: High cyclomatic complexity (>10)
def process_request(request: str, config: Dict) -> Dict:
    if not request:
        raise ValueError("Empty request")
    if "timeout" not in config:
        raise ValueError("Missing timeout")
    if config["timeout"] <= 0:
        raise ValueError("Invalid timeout")
    if "retry" in config:
        if config["retry"] < 0:
            raise ValueError("Invalid retry")
        if config["retry"] > 5:
            config["retry"] = 5
    # ... 20 more nested ifs
```

---

## 🧪 Testing Best Practices

### Test Structure (AAA Pattern)
```python
# ✅ CORRECT: Arrange-Act-Assert pattern
def test_orchestrator_registration():
    """Test orchestrator registration success."""
    # Arrange
    registry = OrchestratorRegistry()
    orchestrator = PlanningOrchestrator(config={"name": "planning_v5"})
    
    # Act
    registry.register(orchestrator)
    
    # Assert
    assert registry.get("planning_v5") == orchestrator
    assert len(registry.orchestrators) == 1
```

### Test Naming
```python
# ✅ CORRECT: Descriptive test names
def test_pattern_router_matches_planning_request():
    """Test pattern router correctly identifies planning requests."""
    pass

def test_pattern_router_returns_none_for_invalid_request():
    """Test pattern router returns None for unrecognized patterns."""
    pass

# ❌ INCORRECT: Vague test names
def test_router():
    pass

def test_case_1():
    pass
```

### Test Coverage Requirements
- **Unit Tests:** 80%+ coverage for all modules
- **Integration Tests:** 60%+ coverage for orchestrator coordination
- **Edge Cases:** All error paths must have tests
- **Concurrency Tests:** All state management must have race condition tests

---

## 🔒 Error Handling Best Practices

### Specific Exceptions
```python
# ✅ CORRECT: Custom exception hierarchy
class CortexError(Exception):
    """Base exception for CORTEX."""
    pass

class OrchestratorError(CortexError):
    """Orchestrator-specific errors."""
    pass

class OrchestratorNotFoundError(OrchestratorError):
    """Orchestrator not found in registry."""
    pass

def get_orchestrator(orchestrator_id: str) -> BaseOrchestrator:
    if orchestrator_id not in registry:
        raise OrchestratorNotFoundError(
            f"Orchestrator '{orchestrator_id}' not found. "
            f"Available: {list(registry.keys())}"
        )

# ❌ INCORRECT: Generic exceptions
def get_orchestrator(orchestrator_id: str) -> BaseOrchestrator:
    if orchestrator_id not in registry:
        raise Exception("Not found")  # Too generic
```

### Context Managers for Resources
```python
# ✅ CORRECT: Use context managers
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path: str):
    """Manage database connection lifecycle."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with get_db_connection("state.db") as conn:
    conn.execute("INSERT INTO states VALUES (?, ?)", (key, value))

# ❌ INCORRECT: Manual resource management
def save_state(key: str, value: str):
    conn = sqlite3.connect("state.db")
    try:
        conn.execute("INSERT INTO states VALUES (?, ?)", (key, value))
        conn.commit()
    finally:
        conn.close()  # Easy to forget
```

---

## 📏 Complexity Limits

| Metric | Limit | Rationale |
|--------|-------|-----------|
| **Lines per function** | 50 | Maintainability |
| **Lines per class** | 300 | Single Responsibility |
| **Parameters per function** | 5 | Cognitive load |
| **Cyclomatic complexity** | 10 | Testability |
| **Nesting depth** | 4 | Readability |
| **Module lines** | 500 | Modularity |

---

## 🔍 Static Analysis Tools

**Mandatory Tools:**
- `mypy` - Type checking
- `pylint` - Code quality
- `black` - Code formatting
- `isort` - Import sorting
- `pytest` - Testing
- `coverage.py` - Coverage reporting

**Pre-commit Configuration:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--strict]
```

---

## ✅ Enforcement

This style guide is enforced by:
1. **PythonBestPracticesValidator** middleware (Phase P01.4)
2. Pre-commit hooks (black, isort, mypy, pylint)
3. CI/CD pipeline checks (pytest, coverage, type checking)
4. Code review checklist

**Non-compliance results in:**
- ❌ PR rejection (CI/CD failure)
- ❌ Orchestrator registration rejection
- ❌ Plan execution blocked

**Reference:** This guide is referenced by `cortex-review.prompt.md` Phase 7 (Best Practices Enforcement).
