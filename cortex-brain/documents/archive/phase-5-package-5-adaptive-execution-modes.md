# Phase 5 Package 5: Adaptive Execution Modes - Worker Plan

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 21, 2025  
**Status:** 🟡 IN PROGRESS  
**Duration:** 5 days (Week 10 Day 3-7)

---

## 🎯 Executive Summary

**Goal:** Implement ExecutionModeManager to dynamically switch between human-in-loop, supervised, and autonomous execution modes based on user experience + operation risk

**Value Proposition:**
- New users: Safe learning with human-in-loop mode
- Experienced users: Faster operations with autonomous mode
- High-risk operations: Automatic escalation to supervised mode
- Failure handling: Auto-escalate after 3 retries

**Success Metrics:**
- ✅ New users: 100% start in human-in-loop mode
- ✅ High-risk ops: 100% use supervised mode
- ✅ Experienced users + routine ops: 80% autonomous
- ✅ 8/8 tests passing (85%+ coverage)

---

## 🏗️ Architecture

**Location:** `src/orchestration_4_0/execution/execution_mode_manager.py`

**Core Classes:**

```python
class ExecutionMode(Enum):
    """Execution mode types"""
    HUMAN_IN_LOOP = "human_in_loop"    # Pause after each step
    SUPERVISED = "supervised"           # Auto-validate, manual approval
    AUTONOMOUS = "autonomous"           # Full E2E with self-healing

class ModeSelector:
    """Selects appropriate mode based on context"""
    
    def calculate_risk_score(self, operation: Operation) -> float:
        """0.0 (low) to 1.0 (high)"""
        pass
    
    def get_user_experience_level(self, user: User) -> float:
        """0.0 (new) to 1.0 (expert)"""
        pass
    
    def select_mode(self, operation: Operation, user: User) -> ExecutionMode:
        """Smart mode selection"""
        pass

class ExecutionModeManager:
    """Main manager class"""
    
    def __init__(self, config: Config, user_profile: UserProfile):
        self.selector = ModeSelector()
        self.escalator = ModeEscalator()
        self.config = config
        self.user_profile = user_profile
    
    def get_mode_for_operation(self, operation: Operation) -> ExecutionMode:
        """Get recommended mode"""
        pass
    
    def execute_with_mode(self, operation: Operation, mode: ExecutionMode) -> Result:
        """Execute operation with specified mode"""
        pass
    
    def handle_failure(self, execution: Execution) -> EscalationResult:
        """Handle failure with escalation logic"""
        pass

class ModeEscalator:
    """Handles escalation logic"""
    
    def should_escalate(self, execution: Execution) -> bool:
        """Check if escalation needed (3 retries)"""
        pass
    
    def escalate_mode(self, current_mode: ExecutionMode) -> ExecutionMode:
        """Escalate to more restrictive mode"""
        pass
```

**Integration Points:**
- Phase 2 Autonomous Execution Framework (extends)
- User Profile System (tracks experience)
- All Orchestrators (mode-aware execution)

---

## 📋 TDD Implementation Plan

### Phase 1: RED - Write Failing Tests (Day 1 Morning, 3 hours)

**Test Suite:** `tests/orchestration_4_0/execution/test_execution_mode_manager.py`

**8 Core Tests:**

```python
def test_mode_selector_calculates_risk_score():
    """Test risk scoring: cleanup=0.1, deploy=0.9"""
    assert risk_score("cleanup") == 0.1
    assert risk_score("deploy_production") == 0.9

def test_mode_selector_gets_user_experience():
    """Test experience levels: new=0.0, expert=1.0"""
    assert experience(new_user) == 0.0
    assert experience(expert_user) == 1.0

def test_mode_selection_for_new_user():
    """New user always gets human-in-loop"""
    mode = selector.select_mode(any_operation, new_user)
    assert mode == ExecutionMode.HUMAN_IN_LOOP

def test_mode_selection_for_high_risk_operation():
    """High-risk operation always supervised"""
    mode = selector.select_mode(deploy_prod, expert_user)
    assert mode == ExecutionMode.SUPERVISED

def test_mode_selection_for_experienced_user_low_risk():
    """Experienced + low risk = autonomous"""
    mode = selector.select_mode(cleanup, expert_user)
    assert mode == ExecutionMode.AUTONOMOUS

def test_escalation_after_3_failures():
    """Auto-escalate after 3 retries"""
    execution.failure_count = 3
    assert escalator.should_escalate(execution) == True

def test_escalation_path():
    """Escalation: autonomous → supervised → human-in-loop"""
    assert escalate(AUTONOMOUS) == SUPERVISED
    assert escalate(SUPERVISED) == HUMAN_IN_LOOP
    assert escalate(HUMAN_IN_LOOP) == HUMAN_IN_LOOP  # Can't escalate further

def test_execution_mode_manager_integration():
    """End-to-end test with manager"""
    manager = ExecutionModeManager(config, user_profile)
    result = manager.execute_with_mode(cleanup, AUTONOMOUS)
    assert result.success == True
    assert result.mode_used == AUTONOMOUS
```

**Expected Result:** All 8 tests FAIL (no implementation yet)

---

### Phase 2: GREEN - Minimal Implementation (Day 1 Afternoon + Day 2, 12 hours)

**Implementation Order:**

**Step 1: Create ExecutionMode Enum (30 min)**
```python
# src/orchestration_4_0/execution/execution_mode.py

from enum import Enum

class ExecutionMode(Enum):
    HUMAN_IN_LOOP = "human_in_loop"
    SUPERVISED = "supervised"
    AUTONOMOUS = "autonomous"
    
    @property
    def description(self) -> str:
        descriptions = {
            self.HUMAN_IN_LOOP: "Pause after each step (learning/debugging)",
            self.SUPERVISED: "Auto-validate, manual approval (default)",
            self.AUTONOMOUS: "Full E2E with self-healing"
        }
        return descriptions[self]
    
    @property
    def risk_tolerance(self) -> float:
        """0.0 (cautious) to 1.0 (aggressive)"""
        tolerance = {
            self.HUMAN_IN_LOOP: 0.0,
            self.SUPERVISED: 0.5,
            self.AUTONOMOUS: 1.0
        }
        return tolerance[self]
```

**Step 2: Implement ModeSelector (3 hours)**
```python
# src/orchestration_4_0/execution/mode_selector.py

class ModeSelector:
    RISK_WEIGHTS = {
        "deploy": 0.9,
        "production": 0.9,
        "delete": 0.8,
        "cleanup": 0.1,
        "healthcheck": 0.1,
        "plan": 0.3
    }
    
    def calculate_risk_score(self, operation: Operation) -> float:
        """Calculate operation risk 0.0-1.0"""
        op_name = operation.name.lower()
        
        # Check for high-risk keywords
        for keyword, weight in self.RISK_WEIGHTS.items():
            if keyword in op_name:
                return weight
        
        # Default medium risk
        return 0.5
    
    def get_user_experience_level(self, user: User) -> float:
        """Get user experience 0.0-1.0"""
        # Based on: operations completed, days active, error rate
        operations = user.completed_operations
        days_active = user.days_since_first_use
        success_rate = user.success_rate
        
        # Simple scoring formula
        experience = min(
            (operations / 100) * 0.4 +
            (days_active / 30) * 0.3 +
            success_rate * 0.3,
            1.0
        )
        return experience
    
    def select_mode(self, operation: Operation, user: User) -> ExecutionMode:
        """Select appropriate execution mode"""
        risk = self.calculate_risk_score(operation)
        experience = self.get_user_experience_level(user)
        
        # Decision matrix
        if experience < 0.3:
            # New users always human-in-loop
            return ExecutionMode.HUMAN_IN_LOOP
        elif risk > 0.7:
            # High-risk always supervised
            return ExecutionMode.SUPERVISED
        elif experience > 0.7 and risk < 0.3:
            # Experienced + low risk = autonomous
            return ExecutionMode.AUTONOMOUS
        else:
            # Default to supervised
            return ExecutionMode.SUPERVISED
```

**Step 3: Implement ModeEscalator (2 hours)**
```python
# src/orchestration_4_0/execution/mode_escalator.py

class ModeEscalator:
    MAX_RETRIES = 3
    
    def should_escalate(self, execution: Execution) -> bool:
        """Check if escalation needed"""
        return execution.failure_count >= self.MAX_RETRIES
    
    def escalate_mode(self, current_mode: ExecutionMode) -> ExecutionMode:
        """Escalate to more restrictive mode"""
        escalation_path = {
            ExecutionMode.AUTONOMOUS: ExecutionMode.SUPERVISED,
            ExecutionMode.SUPERVISED: ExecutionMode.HUMAN_IN_LOOP,
            ExecutionMode.HUMAN_IN_LOOP: ExecutionMode.HUMAN_IN_LOOP  # Can't escalate further
        }
        return escalation_path[current_mode]
    
    def get_escalation_message(self, old_mode: ExecutionMode, new_mode: ExecutionMode) -> str:
        """Generate user-friendly escalation message"""
        return (
            f"⚠️ Escalating execution mode: {old_mode.value} → {new_mode.value}\n"
            f"Reason: {self.MAX_RETRIES} consecutive failures detected"
        )
```

**Step 4: Implement ExecutionModeManager (4 hours)**
```python
# src/orchestration_4_0/execution/execution_mode_manager.py

from typing import Dict, Any
from .mode_selector import ModeSelector
from .mode_escalator import ModeEscalator
from .execution_mode import ExecutionMode

class ExecutionModeManager:
    """
    Main manager for adaptive execution modes
    """
    
    def __init__(self, config: Dict[str, Any], user_profile: UserProfile):
        self.selector = ModeSelector()
        self.escalator = ModeEscalator()
        self.config = config
        self.user_profile = user_profile
    
    def get_mode_for_operation(self, operation: Operation) -> ExecutionMode:
        """Get recommended execution mode for operation"""
        # Check for user override
        if self.config.get("force_mode"):
            return ExecutionMode(self.config["force_mode"])
        
        # Use selector logic
        user = self.user_profile.get_user()
        return self.selector.select_mode(operation, user)
    
    def execute_with_mode(self, operation: Operation, mode: ExecutionMode) -> Result:
        """Execute operation with specified mode"""
        if mode == ExecutionMode.HUMAN_IN_LOOP:
            return self._execute_human_in_loop(operation)
        elif mode == ExecutionMode.SUPERVISED:
            return self._execute_supervised(operation)
        elif mode == ExecutionMode.AUTONOMOUS:
            return self._execute_autonomous(operation)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def handle_failure(self, execution: Execution) -> EscalationResult:
        """Handle execution failure with escalation logic"""
        if self.escalator.should_escalate(execution):
            new_mode = self.escalator.escalate_mode(execution.mode)
            message = self.escalator.get_escalation_message(execution.mode, new_mode)
            
            return EscalationResult(
                escalated=True,
                old_mode=execution.mode,
                new_mode=new_mode,
                message=message
            )
        
        return EscalationResult(escalated=False)
    
    def _execute_human_in_loop(self, operation: Operation) -> Result:
        """Execute with human approval after each step"""
        # TODO: Integrate with Phase 2 autonomous execution
        # For now, simple implementation
        print(f"🛑 Pausing for approval: {operation.name}")
        approval = input("Continue? (y/n): ")
        if approval.lower() == 'y':
            return operation.execute()
        else:
            return Result(success=False, reason="User cancelled")
    
    def _execute_supervised(self, operation: Operation) -> Result:
        """Execute with validation, require final approval"""
        # TODO: Integrate with Phase 2 autonomous execution
        # Validate operation first
        validation = operation.validate()
        if not validation.is_valid:
            return Result(success=False, errors=validation.errors)
        
        # Show plan, require approval
        print(f"📋 Execution plan: {operation.get_plan()}")
        approval = input("Approve execution? (y/n): ")
        if approval.lower() == 'y':
            return operation.execute()
        else:
            return Result(success=False, reason="User rejected plan")
    
    def _execute_autonomous(self, operation: Operation) -> Result:
        """Execute fully autonomous with self-healing"""
        # TODO: Integrate with Phase 2 autonomous execution
        return operation.execute_with_retries(max_retries=3)
```

**Step 5: Integration with User Profile System (2 hours)**
```python
# src/orchestration_4_0/execution/user_profile.py

class UserProfile:
    """Track user experience and preferences"""
    
    def __init__(self, user_id: str, brain: BrainInterface):
        self.user_id = user_id
        self.brain = brain
    
    def get_user(self) -> User:
        """Get or create user record"""
        user_data = self.brain.tier3.get_user_profile(self.user_id)
        if not user_data:
            return self._create_new_user()
        return User(**user_data)
    
    def update_operation_stats(self, operation: str, success: bool):
        """Update user stats after operation"""
        user = self.get_user()
        user.completed_operations += 1
        if success:
            user.successful_operations += 1
        self.brain.tier3.save_user_profile(self.user_id, user.to_dict())
    
    def _create_new_user(self) -> User:
        """Create new user with defaults"""
        return User(
            user_id=self.user_id,
            completed_operations=0,
            successful_operations=0,
            days_since_first_use=0,
            first_used_at=datetime.now()
        )
```

**Expected Result:** All 8 tests PASS

---

### Phase 3: REFACTOR - Clean Code (Day 3, 6 hours)

**Refactoring Tasks:**

1. **Extract Configuration (1 hour)**
   - Move risk weights to config file
   - Move experience thresholds to config
   - Add validation for config values

2. **Add Logging (1 hour)**
   - Log mode selection decisions
   - Log escalation events
   - Log user experience updates

3. **Error Handling (1 hour)**
   - Validate operation object
   - Handle missing user profile gracefully
   - Add timeout handling for human-in-loop

4. **Documentation (2 hours)**
   - Add comprehensive docstrings
   - Create usage examples
   - Document decision matrix

5. **Performance Optimization (1 hour)**
   - Cache user profile lookups
   - Optimize risk calculation
   - Add metrics collection

**Code Quality Checks:**
- ✅ All methods have docstrings
- ✅ Type hints on all public methods
- ✅ No magic numbers (all in config)
- ✅ Logging at appropriate levels
- ✅ Error handling for edge cases

---

## 🧪 Testing Strategy

**Test Coverage Target:** 85%+

**Test Categories:**

1. **Unit Tests (8 core tests)**
   - ModeSelector logic
   - ModeEscalator logic
   - ExecutionModeManager methods

2. **Integration Tests (3 tests)**
   - End-to-end with real operations
   - User profile updates
   - Mode escalation flow

3. **Edge Case Tests (4 tests)**
   - Missing user profile
   - Invalid operation object
   - Force mode override
   - Max escalation (human-in-loop can't escalate)

**Total Tests:** 15 tests

---

## 📊 Success Criteria

**Functional:**
- ✅ All 15 tests passing
- ✅ Mode selection follows decision matrix
- ✅ Escalation triggers after 3 failures
- ✅ User profile tracking works

**Quality:**
- ✅ 85%+ test coverage
- ✅ All public methods documented
- ✅ No code smells (pylint score 9.0+)
- ✅ Type hints on all methods

**Performance:**
- ✅ Mode selection <10ms
- ✅ User profile lookup <50ms (with caching)
- ✅ No memory leaks

**Integration:**
- ✅ Phase 2 autonomous execution integration documented
- ✅ User profile system functional
- ✅ All orchestrators can use ExecutionModeManager

---

## 📅 Timeline

**Day 1 (Friday, December 21):**
- ✅ Morning: Write 8 failing tests (RED phase)
- ☐ Afternoon: Scaffold structure + ExecutionMode enum

**Day 2 (Monday, December 23):**
- ☐ Morning: Implement ModeSelector
- ☐ Afternoon: Implement ModeEscalator + ExecutionModeManager

**Day 3 (Tuesday, December 24):**
- ☐ Morning: Integration with User Profile System
- ☐ Afternoon: Refactoring + documentation

**Day 4 (Wednesday, December 25):**
- ☐ HOLIDAY - No work

**Day 5 (Thursday, December 26):**
- ☐ Morning: Final testing + edge cases
- ☐ Afternoon: Integration validation + commit

---

## 🔗 Integration Points

**Phase 2 Autonomous Execution:**
- `_execute_autonomous()` will call Phase 2 framework
- Retry logic delegates to Phase 2 self-healing
- Checkpoint system integration

**User Profile System:**
- Tier 3 brain stores user stats
- Experience calculation based on operations
- Preference storage for mode overrides

**All Orchestrators:**
- Add `execution_mode` parameter to execute()
- Check mode before starting phases
- Report mode used in results

---

## 📝 Files Created/Modified

**New Files:**
- `src/orchestration_4_0/execution/execution_mode.py` (50 LOC)
- `src/orchestration_4_0/execution/mode_selector.py` (120 LOC)
- `src/orchestration_4_0/execution/mode_escalator.py` (80 LOC)
- `src/orchestration_4_0/execution/execution_mode_manager.py` (200 LOC)
- `src/orchestration_4_0/execution/user_profile.py` (100 LOC)
- `tests/orchestration_4_0/execution/test_execution_mode_manager.py` (300 LOC)

**Modified Files:**
- `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/CORTEX4-STATUS.md`
- `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/phases/phase-05-brain-agentic-ai.md`

**Total LOC:** ~850 LOC (code + tests)

---

## ✅ Completion Checklist

- [ ] RED phase: 8 failing tests written
- [ ] GREEN phase: All tests passing
- [ ] REFACTOR phase: Code quality validated
- [ ] Integration tests: 3 passing
- [ ] Edge case tests: 4 passing
- [ ] Documentation: Complete with examples
- [ ] Code coverage: 85%+
- [ ] Performance: Meets targets
- [ ] Commit + push to remote
- [ ] Update CORTEX4-STATUS.md progress

---

**Next Package:** Package 1 (Multi-Agent Collaboration) - Week 4-5
