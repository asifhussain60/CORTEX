# CORTEX 4.0 Orchestration Framework

**Version:** 4.0.0  
**Status:** ✅ Foundation Complete  
**Test Coverage:** 74/74 tests passing (99.27% phase_manager, 86.51% error_handler, 80.17% execution_orchestrator)

---

## 📋 Overview

Next-generation orchestrator architecture for CORTEX 4.0 with:

- **Template Method Pattern** - BaseOrchestrator provides lifecycle hooks
- **Phase Management** - Declarative phase registration with validation
- **Error Handling** - Automatic recovery strategies and retry logic
- **Dependency Injection** - Container-managed dependencies
- **Progress Tracking** - Real-time progress metrics
- **Test Co-location** - Tests alongside implementation

---

## 🏗️ Architecture

```
src/orchestration_4_0/
├── base/
│   ├── base_orchestrator.py      # Abstract base class (template method)
│   ├── phase_manager.py           # Phase lifecycle management
│   └── error_handler.py           # Error recovery strategies
├── orchestrators/
│   └── execution/
│       └── execution_orchestrator.py  # Multi-phase execution
└── tests/
    └── unit/
        ├── test_phase_manager.py     # 25 tests
        ├── test_error_handler.py     # 26 tests
        └── execution/
            └── test_execution_orchestrator.py  # 23 tests
```

---

## 🚀 Quick Start

### Basic Usage

```python
from src.orchestration_4_0.orchestrators.execution import ExecutionOrchestrator

# Create orchestrator
orchestrator = ExecutionOrchestrator(
    logger=logger,
    config={"max_retries": 3}
)

# Define execution plan
plan = {
    "name": "my_workflow",
    "phases": [
        {"name": "setup", "description": "Setup phase", "required": True},
        {"name": "execute", "description": "Execute phase", "required": True},
        {"name": "teardown", "description": "Cleanup", "required": False}
    ]
}

# Execute
result = orchestrator.execute(context={"plan": plan})

# Check results
print(f"Completed: {result['progress']['completed']}/{result['progress']['total_phases']}")
print(f"Is Complete: {result['is_complete']}")
```

### Creating Custom Orchestrator

```python
from src.orchestration_4_0.base import BaseOrchestrator
from typing import Dict, Any, Optional

class MyOrchestrator(BaseOrchestrator):
    def __init__(self, logger=None, config=None):
        super().__init__(name="my_orchestrator", logger=logger, config=config)
    
    def _setup(self, context: Dict[str, Any]) -> None:
        """Initialize resources"""
        self.logger.info("Setting up...")
        # Your setup logic here
    
    def _register_phases(self) -> None:
        """Register workflow phases"""
        self.phase_manager.register_phase(
            name="analyze",
            description="Analyze input",
            required=True
        )
        self.phase_manager.register_phase(
            name="transform",
            description="Transform data",
            required=True
        )
        self.phase_manager.register_phase(
            name="validate",
            description="Validate output",
            required=True
        )
    
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a specific phase"""
        if phase_name == "analyze":
            # Analysis logic
            return {"analysis": "complete"}
        elif phase_name == "transform":
            # Transform logic
            return {"transformed": True}
        elif phase_name == "validate":
            # Validation logic
            return {"valid": True}
    
    def _teardown(self) -> None:
        """Cleanup resources"""
        self.logger.info("Cleaning up...")

# Usage
orch = MyOrchestrator()
result = orch.execute(context={})
```

---

## 📊 Phase Management

### Phase Lifecycle

```
PENDING → IN_PROGRESS → COMPLETED
                      ↓
                   FAILED
                      ↓
                   SKIPPED
```

### Phase Registration

```python
phase = phase_manager.register_phase(
    name="process",
    description="Process data",
    required=True,  # Must complete successfully
    validation=lambda: True,  # Optional pre-phase validation
    cleanup=lambda: None  # Optional post-phase cleanup
)
```

### Phase Transitions

```python
# Start phase
phase_manager.start_phase("process")

# Complete phase
phase_manager.complete_phase("process", result={"data": "..."})

# Fail phase
phase_manager.fail_phase("process", "Error message")

# Skip phase
phase_manager.skip_phase("process", "Not needed")
```

### Progress Tracking

```python
progress = phase_manager.get_progress()
# {
#     "total_phases": 3,
#     "completed": 1,
#     "in_progress": 1,
#     "pending": 1,
#     "failed": 0,
#     "skipped": 0,
#     "progress_percent": 33.33,
#     "current_phase": "transform"
# }
```

---

## 🛡️ Error Handling

### Error Severities

- **INFO** - Informational only
- **WARNING** - Warning, can continue
- **ERROR** - Error, phase failed but recoverable
- **CRITICAL** - Critical, orchestrator must stop

### Recovery Strategies

- **RETRY** - Retry the failed operation (max 3 attempts by default)
- **SKIP** - Skip phase and continue
- **ROLLBACK** - Rollback changes and retry
- **FAIL_FAST** - Stop immediately
- **CONTINUE** - Log and continue
- **USER_INTERVENTION** - Require user decision

### Automatic Strategy Selection

```python
# Connection errors → RETRY
ConnectionError → RecoveryStrategy.RETRY

# File not found → SKIP
FileNotFoundError → RecoveryStrategy.SKIP

# Permission errors → USER_INTERVENTION
PermissionError → RecoveryStrategy.USER_INTERVENTION

# Value errors → FAIL_FAST
ValueError → RecoveryStrategy.FAIL_FAST

# Critical severity → FAIL_FAST
ErrorSeverity.CRITICAL → RecoveryStrategy.FAIL_FAST
```

### Manual Error Handling

```python
try:
    # Risky operation
    result = process_data()
except Exception as e:
    error = error_handler.handle_error(
        phase="process",
        exception=e,
        severity=ErrorSeverity.ERROR,
        recovery_strategy=RecoveryStrategy.RETRY,
        context={"attempt": 1}
    )
    
    if error_handler.can_retry("process"):
        error_handler.record_retry("process")
        # Retry logic
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/orchestration_4_0/unit/ -v
```

### Run with Coverage

```bash
pytest tests/orchestration_4_0/unit/ \
    --cov=src/orchestration_4_0 \
    --cov-report=term-missing \
    --cov-report=html
```

### Test Structure

- **test_phase_manager.py** - 25 tests for phase lifecycle
- **test_error_handler.py** - 26 tests for error handling
- **test_execution_orchestrator.py** - 23 tests for execution logic

---

## 🔌 Dependency Injection

### Container Registration

ExecutionOrchestrator is registered in `src/di/container.py`:

```python
class CortexContainer(containers.DeclarativeContainer):
    # ...existing providers...
    
    execution_orchestrator = providers.Factory(
        "src.orchestration_4_0.orchestrators.execution.ExecutionOrchestrator",
        logger=logger_factory.provider("orchestration.execution"),
        config=config
    )
```

### Using DI Container

```python
from src.di import get_container

container = get_container()
orchestrator = container.execution_orchestrator()
```

---

## 📈 Status & Metrics

### Orchestrator Status

```python
status = orchestrator.get_status()
# {
#     "name": "execution",
#     "is_running": False,
#     "is_complete": True,
#     "started_at": "2025-12-18T15:00:00",
#     "progress": {...},
#     "errors": {...}
# }
```

### Error Summary

```python
summary = error_handler.get_error_summary()
# {
#     "total_errors": 2,
#     "by_severity": {"error": 1, "warning": 1},
#     "by_phase": {"setup": 1, "execute": 1},
#     "critical_errors": []
# }
```

---

## 🎯 Visual Progress Tracking

Orchestrators provide visual feedback via emoji hints:

- `🎭 Orchestrator engaged: execution`
- `🎭 Phase transition: setup → execute`
- `✅ Phase completed: execute (0.50s)`
- `❌ Phase failed: validate (0.10s) - Validation error`
- `🔄 Retry attempt 2/3 for phase: execute`
- `🎭 Orchestrator completing: ✅ ALL WORK COMPLETE`

---

## 🔜 Next Steps

- **Phase 1.5** - Technical documentation auto-generation with D3.js diagrams
- **Phase 3** - Migrate remaining 12 orchestrators using this foundation
- **Phase 4** - MCP Gateway integration for external tools

---

## 📚 API Reference

### BaseOrchestrator

**Abstract Methods:**
- `_setup(context)` - Initialize orchestrator
- `_register_phases()` - Define workflow phases
- `_execute_phase(phase_name, context)` - Execute single phase
- `_teardown()` - Cleanup resources

**Public Methods:**
- `execute(context)` - Main entry point
- `get_status()` - Get current status

### PhaseManager

**Methods:**
- `register_phase(name, description, required, validation, cleanup)` - Register phase
- `start_phase(phase_name)` - Start phase execution
- `complete_phase(phase_name, result)` - Mark phase complete
- `fail_phase(phase_name, error)` - Mark phase failed
- `skip_phase(phase_name, reason)` - Skip phase
- `get_progress()` - Get progress metrics
- `get_phase_status(phase_name)` - Get phase status
- `reset()` - Reset all phases

### ErrorHandler

**Methods:**
- `handle_error(phase, exception, severity, recovery_strategy, context)` - Handle error
- `can_retry(phase)` - Check if retries remain
- `record_retry(phase)` - Record retry attempt
- `reset_retries(phase)` - Reset retry counter
- `get_error_summary()` - Get error statistics
- `has_critical_errors()` - Check for critical errors
- `clear_errors()` - Clear error history

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
