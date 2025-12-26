# ExecutionModeManager - Usage Examples

**Package:** Phase 5 Package 5 - Adaptive Execution Modes  
**Author:** Asif Hussain  
**Date:** December 21, 2025

---

## 🎯 Quick Start

### Basic Usage

```python
from src.orchestration_4_0.execution import ExecutionMode, ExecutionModeManager
from src.orchestration_4_0.execution.execution_mode_manager import (
    Operation, UserProfile
)

# 1. Create user profile
user_profile = UserProfile("user_123")

# 2. Create manager
config = {"force_mode": None}  # Optional: force specific mode
manager = ExecutionModeManager(config, user_profile)

# 3. Define operation
operation = Operation(
    name="deploy_to_production",
    category="deployment",
    estimated_duration=300
)

# 4. Get recommended mode
mode = manager.get_mode_for_operation(operation)
print(f"Recommended mode: {mode.value}")

# 5. Execute with recommended mode
result = manager.execute_with_mode(operation, mode)
print(f"Success: {result.success}")
```

---

## 📋 Usage Patterns

### Pattern 1: Automatic Mode Selection

```python
# Manager automatically selects mode based on:
# - User experience level (0.0-1.0)
# - Operation risk score (0.0-1.0)
# - Operation type

operation = Operation("cleanup_workspace", "maintenance", 60)
mode = manager.get_mode_for_operation(operation)

# New user (0 operations) → HUMAN_IN_LOOP
# Intermediate user + low risk → SUPERVISED
# Expert user + low risk → AUTONOMOUS
```

### Pattern 2: Force Specific Mode

```python
# Override automatic selection (useful for testing)
config = {"force_mode": "autonomous"}
manager = ExecutionModeManager(config, user_profile)

# All operations will use autonomous mode
mode = manager.get_mode_for_operation(any_operation)
assert mode == ExecutionMode.AUTONOMOUS
```

### Pattern 3: Failure Handling with Escalation

```python
from src.orchestration_4_0.execution.execution_mode_manager import Execution

# Track execution state
execution = Execution(
    operation=operation,
    mode=ExecutionMode.AUTONOMOUS,
    failure_count=0
)

# Simulate failures
for attempt in range(5):
    result = manager.execute_with_mode(operation, execution.mode)
    
    if not result.success:
        execution.failure_count += 1
        escalation = manager.handle_failure(execution)
        
        if escalation.escalated:
            print(f"⚠️  Escalating: {escalation.old_mode.value} → {escalation.new_mode.value}")
            execution.mode = escalation.new_mode
            execution.failure_count = 0  # Reset after escalation
        else:
            print(f"Retrying with {execution.mode.value} (attempt {execution.failure_count}/3)")
    else:
        print(f"✅ Success with {execution.mode.value}")
        break
```

### Pattern 4: Custom Operation with Execution Function

```python
def my_custom_operation():
    # Your actual operation logic
    print("Executing custom operation...")
    return {"status": "success", "data": {...}}

operation = Operation(
    name="custom_task",
    category="custom",
    estimated_duration=120,
    execution_fn=my_custom_operation  # Provide callable
)

mode = manager.get_mode_for_operation(operation)
result = manager.execute_with_mode(operation, mode)

if result.success:
    print(f"Result: {result.result}")
```

---

## 🔄 Integration with Orchestrators

### Example: Maintenance Orchestrator Integration

```python
from src.orchestration_4_0.execution import ExecutionModeManager

class MaintenanceOrchestrator(BaseOrchestrator):
    def __init__(self, config, user_id="maintenance_user"):
        super().__init__("MaintenanceOrchestrator", config=config)
        
        # Add execution mode manager
        self.user_profile = UserProfile(user_id)
        self.mode_manager = ExecutionModeManager(config, self.user_profile)
    
    def _execute_phase(self, phase_name: str, context: dict):
        # Create operation from phase
        operation = Operation(
            name=phase_name,
            category="maintenance",
            estimated_duration=context.get("duration", 60),
            execution_fn=lambda: self._run_phase_logic(phase_name, context)
        )
        
        # Get adaptive mode
        mode = self.mode_manager.get_mode_for_operation(operation)
        self.logger.info(f"Executing {phase_name} in {mode.value} mode")
        
        # Execute with selected mode
        result = self.mode_manager.execute_with_mode(operation, mode)
        
        if not result.success:
            self.logger.error(f"Phase {phase_name} failed: {result.reason}")
        
        return result
```

---

## 📊 Decision Matrix

### Mode Selection Logic

| User Experience | Operation Risk | Selected Mode |
|----------------|----------------|---------------|
| 0 operations (new) | Any | **HUMAN_IN_LOOP** |
| Any | >0.7 (high risk) | **SUPERVISED** |
| >0.7 (expert) | <0.3 (low risk) | **AUTONOMOUS** |
| 0.3-0.7 (intermediate) | 0.3-0.7 (medium) | **SUPERVISED** |

### Risk Score Mapping

| Operation Category | Risk Score |
|-------------------|------------|
| deploy, production | 0.9 (high) |
| delete | 0.8 (high) |
| cleanup, healthcheck | 0.1 (low) |
| plan | 0.3 (low-medium) |
| test | 0.2 (low) |
| Unknown | 0.5 (medium) |

### Experience Calculation

**Formula (if operations > 0):**
```
experience = min(
    (completed_operations / 100) * 0.4 +    # 40% weight
    (days_active / 30) * 0.3 +               # 30% weight
    success_rate * 0.3,                      # 30% weight
    1.0
)
```

**Examples:**
- New user (0 ops): 0.0
- 50 ops, 15 days, 90% success: 0.47
- 200 ops, 60 days, 95% success: 0.99 (expert)

---

## 🔧 Escalation Workflow

### Escalation Path

```
AUTONOMOUS (3 failures) → SUPERVISED (3 failures) → HUMAN_IN_LOOP (manual intervention)
```

### Example Escalation Scenario

```python
# Start with autonomous mode (expert user + low risk)
execution = Execution(
    operation=Operation("deploy_staging", "deployment", 180),
    mode=ExecutionMode.AUTONOMOUS,
    failure_count=0
)

# Failure 1, 2, 3: Retry in AUTONOMOUS mode
for i in range(3):
    result = manager.execute_with_mode(execution.operation, execution.mode)
    if not result.success:
        execution.failure_count += 1

# Failure 4: Escalate to SUPERVISED
escalation = manager.handle_failure(execution)
assert escalation.escalated == True
assert escalation.new_mode == ExecutionMode.SUPERVISED
execution.mode = escalation.new_mode
execution.failure_count = 0

# Failure 5, 6, 7: Retry in SUPERVISED mode
for i in range(3):
    result = manager.execute_with_mode(execution.operation, execution.mode)
    if not result.success:
        execution.failure_count += 1

# Failure 8: Escalate to HUMAN_IN_LOOP
escalation = manager.handle_failure(execution)
assert escalation.escalated == True
assert escalation.new_mode == ExecutionMode.HUMAN_IN_LOOP
execution.mode = escalation.new_mode
execution.failure_count = 0

# Now requires manual intervention
```

---

## 📈 User Profile Tracking

### Automatic Stats Updates

```python
# Stats are updated automatically after each execution
operation = Operation("test_operation", "test", 30)
mode = manager.get_mode_for_operation(operation)
result = manager.execute_with_mode(operation, mode)

# User profile automatically updated:
# - completed_operations += 1
# - successful_operations += 1 (if success)
# - Experience level recalculated

# Check current stats
user = user_profile.get_user()
print(f"Completed: {user.completed_operations}")
print(f"Success rate: {user.success_rate:.2%}")
```

### Manual Stats Updates (Advanced)

```python
# For custom tracking scenarios
user_profile.update_operation_stats("custom_op", success=True)

# Get updated user data
user = user_profile.get_user()
assert user.completed_operations == previous_count + 1
```

---

## 🎯 Best Practices

### 1. Use Descriptive Operation Names
```python
# Good
operation = Operation("deploy_to_production_us_east", "deployment", 300)

# Bad
operation = Operation("op1", "misc", 100)
```

### 2. Set Appropriate Risk Categories
```python
# High-risk operations
Operation("deploy_production", "deployment", 300)  # Risk: 0.9
Operation("delete_database", "delete", 120)        # Risk: 0.8

# Low-risk operations
Operation("cleanup_temp_files", "cleanup", 60)     # Risk: 0.1
Operation("run_healthcheck", "healthcheck", 30)    # Risk: 0.1
```

### 3. Handle Failures Gracefully
```python
result = manager.execute_with_mode(operation, mode)

if not result.success:
    logger.error(f"Operation failed: {result.reason}")
    if result.errors:
        for error in result.errors:
            logger.error(f"  - {error}")
    
    # Consider escalation
    escalation = manager.handle_failure(execution)
    if escalation.escalated:
        logger.warning(escalation.message)
```

### 4. Test with Different User Profiles
```python
# Test new user behavior
new_user = UserProfile("new_user_test")
manager_new = ExecutionModeManager({}, new_user)
mode = manager_new.get_mode_for_operation(operation)
assert mode == ExecutionMode.HUMAN_IN_LOOP

# Test expert user behavior
expert_user_profile = UserProfile("expert_test")
# Simulate 200 operations, 95% success
for i in range(200):
    expert_user_profile.update_operation_stats(f"op_{i}", success=(i % 20 != 0))
manager_expert = ExecutionModeManager({}, expert_user_profile)
mode = manager_expert.get_mode_for_operation(low_risk_operation)
assert mode == ExecutionMode.AUTONOMOUS
```

---

## 🔍 Debugging Tips

### Enable Debug Logging (Future Enhancement)
```python
import logging
logging.getLogger("execution_mode_manager").setLevel(logging.DEBUG)

# Will show:
# DEBUG: Mode selection: op=deploy_staging, risk=0.90, exp=0.45, mode=supervised
# DEBUG: Escalation check: failure_count=3/3, escalating=True
```

### Check Current Mode Selection
```python
# Manually calculate what mode would be selected
selector = ModeSelector()
risk = selector.calculate_risk_score(operation)
experience = selector.get_user_experience_level(user)
mode = selector.select_mode(operation, user)

print(f"Risk: {risk:.2f}, Experience: {experience:.2f}, Mode: {mode.value}")
```

### Test Escalation Logic
```python
escalator = ModeEscalator()

# Test escalation threshold
execution = Execution(operation, ExecutionMode.AUTONOMOUS, failure_count=2)
assert escalator.should_escalate(execution) == False

execution.failure_count = 3
assert escalator.should_escalate(execution) == True

# Test escalation path
assert escalator.escalate_mode(ExecutionMode.AUTONOMOUS) == ExecutionMode.SUPERVISED
assert escalator.escalate_mode(ExecutionMode.SUPERVISED) == ExecutionMode.HUMAN_IN_LOOP
assert escalator.escalate_mode(ExecutionMode.HUMAN_IN_LOOP) == ExecutionMode.HUMAN_IN_LOOP
```

---

## 📚 Additional Resources

- **Architecture Diagram:** See `ARCHITECTURE-PACKAGE-5.md`
- **Test Examples:** `tests/orchestration_4_0/execution/test_execution_mode_manager.py`
- **API Reference:** Docstrings in `src/orchestration_4_0/execution/execution_mode_manager.py`
- **Completion Report:** `cortex-brain/documents/reports/PHASE-5-PACKAGE-5-GREEN-PHASE-COMPLETION.md`

---

*Generated by CORTEX Planning System*
