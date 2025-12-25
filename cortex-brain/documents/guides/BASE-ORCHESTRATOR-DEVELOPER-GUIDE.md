# Base Orchestrator Developer Guide

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Status:** ✅ Production Ready  
**Updated:** December 25, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Lifecycle & Phases](#lifecycle--phases)
5. [State Management](#state-management)
6. [Error Handling](#error-handling)
7. [Workspace Awareness](#workspace-awareness)
8. [Advanced Features](#advanced-features)
9. [Testing Patterns](#testing-patterns)
10. [Best Practices](#best-practices)

---

## 🎯 Overview

### What is BaseOrchestrator?

`BaseOrchestrator` is the foundational abstract class for all CORTEX 4.0 orchestrators. It provides:

- ✅ **Standardized Lifecycle:** Setup → Execute → Teardown
- ✅ **Workspace Detection:** Automatic workspace context (Phase 11)
- ✅ **Error Handling:** Built-in error recovery and rollback
- ✅ **State Management:** Checkpoints, phase tracking, progress
- ✅ **Brain Integration:** Unified access to 4-tier brain
- ✅ **Adaptive Execution:** AUTONOMOUS, SUPERVISED, MANUAL modes
- ✅ **Validation Framework:** Input validation and safety checks

### Design Philosophy

**Template Method Pattern:** BaseOrchestrator defines the skeleton of the execution workflow, with subclasses implementing specific logic.

```python
# BaseOrchestrator provides:
run()           # Full lifecycle wrapper
  ├── execute() # ← YOUR IMPLEMENTATION HERE
  ├── validate_input()
  ├── handle_error()
  └── create_checkpoint()
```

**Benefits:**
- Consistent behavior across all orchestrators
- Reduced boilerplate code
- Easy to extend and maintain
- Built-in best practices

---

## 🏗️ Architecture

### Class Hierarchy

```
BaseOrchestrator (Abstract)
├── PlanningOrchestrator
├── ExecutionOrchestrator
├── TDDOrchestrator
├── DocumentationOrchestrator
├── MaintenanceOrchestrator
├── QAOrchestrator
├── DevOpsOrchestrator
├── IntelligenceOrchestrator
├── ObservabilityOrchestrator
├── OnboardingOrchestrator
├── SanitizationOrchestrator
├── ADOOperationsOrchestrator
└── ErrorRecoveryOrchestrator (future)
```

### Core Components

```python
from src.orchestrators.base import (
    BaseOrchestrator,      # Base class
    OrchestratorResult,    # Return type
    OrchestratorStatus,    # Execution status enum
    ValidationResult,      # Input validation result
    ErrorResult            # Error handling result
)
```

### Workspace Structure

```
.
├── cortex-operations.yaml         # Operations manifest
├── cortex.config.json             # Machine-specific config
├── src/
│   └── orchestrators/
│       └── base/
│           ├── base_orchestrator.py
│           ├── phase_manager.py
│           └── error_handler.py
└── .cortex/                       # Workspace metadata
    └── tier3/
        └── context.db             # Workspace-specific data
```

---

## 🚀 Quick Start

### Minimal Orchestrator

```python
from src.orchestrators.base import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus
)
from typing import Dict, Any
from pathlib import Path

class HelloWorldOrchestrator(BaseOrchestrator):
    """Simple orchestrator that writes a hello world file."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Custom initialization
        self.greeting = config.get("greeting", "Hello, World!")
    
    def execute(self) -> OrchestratorResult:
        """
        Execute orchestrator logic.
        
        Uses self.target_directory (workspace-aware path)
        Returns OrchestratorResult with status and data.
        """
        try:
            # Write file to workspace
            output_file = self.target_directory / "hello.txt"
            output_file.write_text(self.greeting)
            
            self.logger.info(f"Created {output_file}")
            
            return OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message=f"Successfully wrote greeting to {output_file}",
                data={
                    "file_path": str(output_file),
                    "greeting": self.greeting
                }
            )
        
        except Exception as e:
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Failed to write greeting: {str(e)}",
                errors=[str(e)]
            )

# Usage
config = {
    "name": "hello-world",
    "version": "1.0.0",
    "greeting": "Hello from CORTEX 4.0!"
}

orchestrator = HelloWorldOrchestrator(config)
result = orchestrator.run()  # Full lifecycle

print(f"Status: {result.status.value}")
print(f"Success: {result.success}")
print(f"Message: {result.message}")
print(f"Data: {result.data}")
```

**Output:**
```
🎭 Orchestrator engaged: hello-world [workspace:CORTEX]
Created /Users/asifhussain/PROJECTS/CORTEX/hello.txt
🎭 Orchestrator completing: ✅ hello-world - Successfully wrote greeting
Status: completed
Success: True
Message: Successfully wrote greeting to /Users/asifhussain/PROJECTS/CORTEX/hello.txt
Data: {'file_path': '/Users/asifhussain/PROJECTS/CORTEX/hello.txt', 'greeting': 'Hello from CORTEX 4.0!'}
```

---

## 🔄 Lifecycle & Phases

### Execution Flow

```python
orchestrator.run()
    ↓
1. INITIALIZATION
    - Set status to RUNNING
    - Record start_time
    - Log engagement hint
    ↓
2. EXECUTION
    - Call execute() (YOUR CODE)
    - Update status based on result
    - Record end_time
    ↓
3. ERROR HANDLING (if exception)
    - Call handle_error()
    - Attempt auto-rollback (if enabled)
    - Return error result
    ↓
4. COMPLETION
    - Log completion hint
    - Return OrchestratorResult
```

### Lifecycle Hooks

```python
class MyOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        """REQUIRED: Main orchestrator logic."""
        # YOUR IMPLEMENTATION
        pass
    
    def validate_input(self, params: Dict[str, Any]) -> ValidationResult:
        """OPTIONAL: Custom input validation."""
        errors = []
        
        if "required_param" not in params:
            errors.append("Missing required_param")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
    
    def handle_error(self, error: Exception) -> ErrorResult:
        """OPTIONAL: Custom error handling."""
        # Log, recover, or transform error
        return super().handle_error(error)
```

### Status Transitions

```python
OrchestratorStatus.NOT_STARTED  # Initial state
    ↓
OrchestratorStatus.RUNNING      # During execution
    ↓
OrchestratorStatus.COMPLETED    # Success
OrchestratorStatus.FAILED       # Error occurred
OrchestratorStatus.CANCELLED    # User cancelled
```

---

## 💾 State Management

### Checkpoints

Create checkpoints to enable rollback on failure:

```python
class MultiPhaseOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        phases = ["discovery", "implementation", "testing"]
        
        for phase in phases:
            # Create checkpoint before each phase
            checkpoint = self.create_checkpoint(
                phase=phase,
                state={"current_phase": phase, "completed": []}
            )
            
            try:
                # Execute phase
                self._execute_phase(phase)
                
            except Exception as e:
                # Restore to checkpoint on error
                self.restore_checkpoint(checkpoint["checkpoint_id"])
                return OrchestratorResult(
                    status=OrchestratorStatus.FAILED,
                    success=False,
                    message=f"Failed at phase {phase}",
                    errors=[str(e)]
                )
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="All phases complete"
        )
    
    def _execute_phase(self, phase: str):
        """Execute a single phase."""
        self.logger.info(f"🎭 Phase transition: → {phase.upper()}")
        # Phase logic here
```

### Checkpoint Management

```python
# Create checkpoint
checkpoint = orchestrator.create_checkpoint(
    phase="implementation",
    state={"files_modified": ["file1.py", "file2.py"]}
)

# List all checkpoints
checkpoints = orchestrator.list_checkpoints()
for cp in checkpoints:
    print(f"{cp['checkpoint_id']}: {cp['phase']} at {cp['timestamp']}")

# Restore specific checkpoint
success = orchestrator.restore_checkpoint(checkpoint_id="abc-123")
```

### Auto-Rollback

```python
# Enable auto-rollback in AUTONOMOUS mode
config = {
    "name": "my-orchestrator",
    "execution_mode": ExecutionMode.AUTONOMOUS
}

orchestrator = MyOrchestrator(config)
# auto_rollback_enabled = True automatically

# On failure, last checkpoint auto-restored
result = orchestrator.run()
if not result.success:
    print(f"Rolled back: {result.data['rolled_back']}")
    print(f"Checkpoint: {result.data['checkpoint_restored']}")
```

---

## 🚨 Error Handling

### Built-In Error Handling

```python
class RobustOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        try:
            # Your logic
            risky_operation()
            
            return OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message="Operation complete"
            )
        
        except ValueError as e:
            # Handle specific errors
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Invalid input: {str(e)}",
                errors=[str(e)]
            )
        
        except Exception as e:
            # Handle unexpected errors
            error_result = self.handle_error(e)
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Unexpected error: {error_result.error_message}",
                errors=[error_result.error_message]
            )
```

### Custom Error Handler

```python
from src.orchestrators.base import ErrorResult

class MyOrchestrator(BaseOrchestrator):
    def handle_error(self, error: Exception) -> ErrorResult:
        """Custom error handling with recovery."""
        error_type = error.__class__.__name__
        error_message = str(error)
        
        # Log error
        self.logger.error(f"{error_type}: {error_message}", exc_info=True)
        
        # Attempt recovery
        recovery_successful = False
        if error_type == "ConnectionError":
            recovery_successful = self._retry_connection()
        
        return ErrorResult(
            handled=True,
            error_type=error_type,
            error_message=error_message,
            recovery_attempted=True,
            recovery_successful=recovery_successful,
            should_retry=not recovery_successful,
            retry_delay_seconds=5.0 if not recovery_successful else 0.0
        )
    
    def _retry_connection(self) -> bool:
        """Attempt to recover from connection error."""
        try:
            # Recovery logic
            return True
        except:
            return False
```

### Error Propagation

```python
# Errors automatically propagated to result
result = orchestrator.run()

if not result.success:
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    
    for error in result.errors:
        print(f"Error: {error}")
    
    # Check if rolled back
    if result.data.get("rolled_back"):
        checkpoint = result.data.get("checkpoint_restored")
        print(f"Auto-rollback to checkpoint: {checkpoint}")
```

---

## 📁 Workspace Awareness

### Automatic Workspace Detection (Phase 11)

```python
class WorkspaceAwareOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        # Workspace info auto-detected
        self.logger.info(f"Workspace: {self.workspace_name}")
        self.logger.info(f"Workspace ID: {self.workspace_id}")
        self.logger.info(f"Target directory: {self.target_directory}")
        
        # Write files to workspace
        output_file = self.target_directory / "report.txt"
        output_file.write_text("Workspace report")
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message=f"Report written to {self.workspace_name}",
            data={
                "workspace_id": self.workspace_id,
                "workspace_name": self.workspace_name,
                "output_file": str(output_file)
            }
        )
```

### Workspace Properties

| Property | Type | Description |
|----------|------|-------------|
| `self.workspace_info` | `WorkspaceInfo` | Full workspace information object |
| `self.target_directory` | `Path` | Where to write files (workspace path) |
| `self.workspace_id` | `str` | Unique workspace UUID |
| `self.workspace_name` | `str` | Human-readable workspace name |

### Fallback Handling

```python
# If workspace detection fails (rare)
if self.workspace_info is None:
    # Falls back to workspace_root from config
    self.logger.warning("Using fallback workspace_root")
    target = self.target_directory  # Still available
else:
    # Normal workspace detected
    self.logger.info(f"Active workspace: {self.workspace_name}")
```

---

## 🎯 Advanced Features

### Adaptive Execution Modes

```python
from src.operations.modules.orchestration.adaptive_execution import (
    ExecutionMode,
    AdaptiveExecutionConfig,
    SafetyGuardrail
)

# AUTONOMOUS: Full automation with self-healing
config = {
    "name": "auto-orchestrator",
    "execution_mode": ExecutionMode.AUTONOMOUS,
    "adaptive_config": {
        "max_retries": 3,
        "checkpoint_frequency": "per_phase"
    }
}

# SUPERVISED: Human approval at gates
config = {
    "name": "supervised-orchestrator",
    "execution_mode": ExecutionMode.SUPERVISED
}

# MANUAL: Step-by-step control
config = {
    "name": "manual-orchestrator",
    "execution_mode": ExecutionMode.MANUAL
}

orchestrator = MyOrchestrator(config)
```

### Safety Guardrails

```python
class SafeOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        # Validate action before execution
        action = {
            "type": "file_delete",
            "path": "/important/file.txt",
            "risk_level": "high"
        }
        
        validation = self.validate_action(action)
        
        if not validation.valid:
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Unsafe action blocked: {validation.errors}",
                errors=validation.errors
            )
        
        # Safe to proceed
        self._execute_action(action)
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Action executed safely"
        )
```

### Brain Integration

```python
class BrainAwareOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        # Access brain tiers if available
        if self.brain:
            # Query Tier 1 (Working Memory)
            recent_data = self.brain.tier1.get_recent_conversations(limit=10)
            
            # Query Tier 2 (Knowledge Graph)
            patterns = self.brain.tier2.query_patterns("authentication")
            
            # Query Tier 3 (Dev Context)
            metrics = self.brain.tier3.get_code_metrics(self.workspace_id)
            
            self.logger.info(f"Brain data retrieved: {len(patterns)} patterns")
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Brain integration successful"
        )
```

### Input Validation

```python
class ValidatedOrchestrator(BaseOrchestrator):
    def validate_input(self, params: Dict[str, Any]) -> ValidationResult:
        """Custom validation logic."""
        errors = []
        warnings = []
        
        # Required parameters
        if "feature_name" not in params:
            errors.append("Missing required parameter: feature_name")
        
        if "complexity" not in params:
            warnings.append("Complexity not specified, will auto-detect")
        
        # Type validation
        if "max_retries" in params:
            if not isinstance(params["max_retries"], int):
                errors.append("max_retries must be an integer")
            elif params["max_retries"] < 0:
                errors.append("max_retries must be non-negative")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

# Usage with validation
orchestrator = ValidatedOrchestrator(config)

params = {"feature_name": "user-auth"}
validation = orchestrator.validate_input(params)

if not validation.valid:
    print(f"Validation errors: {validation.errors}")
else:
    result = orchestrator.run()
```

---

## 🧪 Testing Patterns

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

def test_orchestrator_initialization():
    """Test orchestrator initializes correctly."""
    config = {
        "name": "test-orchestrator",
        "version": "1.0.0"
    }
    
    orchestrator = HelloWorldOrchestrator(config)
    
    assert orchestrator.name == "test-orchestrator"
    assert orchestrator.version == "1.0.0"
    assert orchestrator.status == OrchestratorStatus.NOT_STARTED

def test_orchestrator_execution():
    """Test orchestrator executes successfully."""
    config = {
        "name": "test-orchestrator",
        "greeting": "Test greeting",
        "workspace_root": Path("/tmp/test")
    }
    
    orchestrator = HelloWorldOrchestrator(config)
    result = orchestrator.run()
    
    assert result.success is True
    assert result.status == OrchestratorStatus.COMPLETED
    assert "Test greeting" in result.message

def test_orchestrator_error_handling():
    """Test orchestrator handles errors correctly."""
    config = {
        "name": "test-orchestrator",
        "workspace_root": Path("/invalid/path")
    }
    
    with patch.object(Path, 'write_text', side_effect=PermissionError("Access denied")):
        orchestrator = HelloWorldOrchestrator(config)
        result = orchestrator.run()
        
        assert result.success is False
        assert result.status == OrchestratorStatus.FAILED
        assert len(result.errors) > 0
```

### Integration Testing

```python
def test_orchestrator_with_workspace_detection(tmp_path):
    """Test orchestrator with real workspace."""
    # Create temporary workspace
    workspace = tmp_path / "test-workspace"
    workspace.mkdir()
    
    config = {
        "name": "test-orchestrator",
        "workspace_root": workspace
    }
    
    orchestrator = HelloWorldOrchestrator(config)
    result = orchestrator.run()
    
    # Verify file created
    output_file = workspace / "hello.txt"
    assert output_file.exists()
    assert output_file.read_text() == "Hello, World!"
    
    # Verify result
    assert result.success is True
    assert result.data["file_path"] == str(output_file)

def test_orchestrator_checkpoint_restore():
    """Test checkpoint creation and restoration."""
    orchestrator = MultiPhaseOrchestrator(config)
    
    # Create checkpoint
    checkpoint = orchestrator.create_checkpoint(
        phase="test_phase",
        state={"key": "value"}
    )
    
    assert checkpoint["phase"] == "test_phase"
    assert checkpoint["state"]["key"] == "value"
    
    # List checkpoints
    checkpoints = orchestrator.list_checkpoints()
    assert len(checkpoints) == 1
    
    # Restore checkpoint
    success = orchestrator.restore_checkpoint(checkpoint["checkpoint_id"])
    assert success is True
    assert orchestrator.current_phase == "test_phase"
```

---

## ✅ Best Practices

### 1. Always Use Type Hints

```python
from typing import Dict, Any, Optional

class MyOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        """Type hints improve code clarity."""
        pass
    
    def custom_method(self, param: str) -> Optional[Dict[str, Any]]:
        """Return types documented."""
        return {"result": param}
```

### 2. Log Important Events

```python
class MyOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        self.logger.info("🎭 Starting custom operation")
        
        # Phase transitions
        self.logger.info("🎭 Phase transition: DISCOVER → IMPLEMENT")
        
        # Completion
        self.logger.info("🎭 Orchestrator completing: ✅ OPERATION COMPLETE")
        
        return OrchestratorResult(...)
```

### 3. Use Workspace-Aware Paths

```python
# ✅ GOOD: Use self.target_directory
output_file = self.target_directory / "output.txt"

# ❌ BAD: Hardcoded paths
output_file = Path("/hardcoded/path/output.txt")
```

### 4. Return Meaningful Results

```python
# ✅ GOOD: Rich result data
return OrchestratorResult(
    status=OrchestratorStatus.COMPLETED,
    success=True,
    message="Successfully processed 42 files",
    data={
        "files_processed": 42,
        "files_skipped": 3,
        "total_size_bytes": 1024000,
        "output_directory": str(output_dir)
    }
)

# ❌ BAD: Minimal data
return OrchestratorResult(
    status=OrchestratorStatus.COMPLETED,
    success=True,
    message="Done"
)
```

### 5. Handle Errors Gracefully

```python
def execute(self) -> OrchestratorResult:
    try:
        # Main logic
        pass
    except SpecificError as e:
        # Handle known errors
        return OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message=f"Known error: {e}",
            errors=[str(e)]
        )
    except Exception as e:
        # Handle unexpected errors
        error_result = self.handle_error(e)
        return OrchestratorResult(...)
```

### 6. Use Checkpoints for Long Operations

```python
def execute(self) -> OrchestratorResult:
    phases = ["phase1", "phase2", "phase3"]
    
    for phase in phases:
        # Checkpoint before each phase
        self.create_checkpoint(phase, {"completed": phases[:phases.index(phase)]})
        
        try:
            self._execute_phase(phase)
        except Exception as e:
            # Rollback on error
            return OrchestratorResult(...)
```

### 7. Validate Inputs Early

```python
def execute(self) -> OrchestratorResult:
    # Validate before expensive operations
    validation = self.validate_input(self.config)
    
    if not validation.valid:
        return OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message="Invalid input",
            errors=validation.errors
        )
    
    # Proceed with execution
    ...
```

### 8. Document Your Orchestrator

```python
class MyOrchestrator(BaseOrchestrator):
    """
    Brief description of what this orchestrator does.
    
    Features:
    - Feature 1
    - Feature 2
    
    Usage:
        orchestrator = MyOrchestrator(config)
        result = orchestrator.run()
    
    Configuration:
        - name: Orchestrator name (required)
        - param1: Description (optional)
        - param2: Description (required)
    """
    
    def execute(self) -> OrchestratorResult:
        """Execute orchestrator logic with detailed steps."""
        pass
```

---

## 📚 Additional Resources

### Documentation
- **Base Orchestrator API:** `docs/orchestration_4_0/base_framework/modules/base_orchestrator.md`
- **Phase Manager:** `src/orchestrators/base/phase_manager.py`
- **Error Handler:** `src/orchestrators/base/error_handler.py`
- **Orchestrators README:** `src/orchestrators/README.md`

### Examples
- **Planning Orchestrator:** `src/orchestrators/planning/planning_orchestrator.py`
- **Execution Orchestrator:** `src/orchestration_4_0/orchestrators/execution/execution_orchestrator.py`
- **Maintenance Orchestrator:** `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`

### Related Guides
- **Migration Guide:** `cortex-brain/documents/guides/CORTEX-3.0-TO-4.0-MIGRATION-GUIDE.md`
- **Execution Orchestrator Guide:** `cortex-brain/documents/guides/EXECUTION-ORCHESTRATOR-GUIDE.md`
- **Release Notes:** `cortex-brain/documents/guides/RELEASE-NOTES-v4.0-GA.md`

---

## 🔗 Quick Reference

### Essential Imports
```python
from src.orchestrators.base import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
    ValidationResult,
    ErrorResult
)
```

### Minimal Template
```python
class MyOrchestrator(BaseOrchestrator):
    def execute(self) -> OrchestratorResult:
        # Your logic here
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation complete"
        )
```

### Full Lifecycle
```python
orchestrator = MyOrchestrator(config)
result = orchestrator.run()  # Handles everything
```

---

**Happy Orchestrating! 🎭**

**Version:** 1.0.0  
**Last Updated:** December 25, 2025  
**Author:** Asif Hussain
