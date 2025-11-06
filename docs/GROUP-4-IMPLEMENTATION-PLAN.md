# GROUP 4 Implementation Plan - Intelligence Layer

**Start Date:** November 6, 2025  
**Status:** 🎯 READY TO BEGIN  
**Estimated Duration:** 20-28 hours  
**Approach:** 3-wave incremental delivery with framework-first strategy

---

## 📋 Overview

GROUP 4 implements the Intelligence Layer - 10 specialist agents, entry point, and dashboard. Based on exceptional GROUP 3 performance (52% faster, 100% tests passing), we're applying proven patterns:

✅ **Test-Driven Development** - Write tests first, implement to pass  
✅ **Small Increments** - 100-150 line chunks (Rule #23)  
✅ **Smart Simplification** - Core features first, enhance later  
✅ **Framework First** - Common infrastructure before individual agents

---

## 🎯 Task 4.0: Agent Framework (NEW - 2 hours)

**Purpose:** Create shared infrastructure before implementing individual agents

**Priority:** CRITICAL - Fixes import errors, establishes patterns

### Deliverables

1. **Package Structure** (30 min)
```python
CORTEX/src/cortex_agents/
├── __init__.py              # Package initialization, exports
├── base_agent.py            # BaseAgent abstract class
├── agent_types.py           # Type definitions, enums
├── exceptions.py            # Custom exceptions
└── utils.py                 # Shared utilities
```

2. **BaseAgent Abstract Class** (1 hour)
```python
# base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class AgentRequest:
    """Standard request format for all agents"""
    intent: str
    context: Dict[str, Any]
    user_message: str
    conversation_id: Optional[str] = None

@dataclass
class AgentResponse:
    """Standard response format for all agents"""
    success: bool
    result: Any
    message: str
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """Base class for all CORTEX agents"""
    
    def __init__(self, name: str, tier1_api, tier2_kg, tier3_context):
        self.name = name
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        self.logger = self._setup_logging()
    
    @abstractmethod
    def can_handle(self, request: AgentRequest) -> bool:
        """Return True if agent can handle this request"""
        pass
    
    @abstractmethod
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent's primary function"""
        pass
    
    def _setup_logging(self) -> logging.Logger:
        """Configure agent logging"""
        logger = logging.getLogger(f"cortex.agents.{self.name}")
        # Standard logging configuration
        return logger
```

3. **Test Fixtures** (30 min)
```python
# tests/conftest.py (additions)
import pytest
from CORTEX.src.cortex_agents.base_agent import AgentRequest, AgentResponse

@pytest.fixture
def sample_agent_request():
    return AgentRequest(
        intent="test_intent",
        context={"file": "test.py"},
        user_message="Test message"
    )

@pytest.fixture
def mock_tier_apis():
    # Mock Tier 1, 2, 3 APIs for agent testing
    pass
```

**Exit Criteria:**
- ✅ BaseAgent class defined and documented
- ✅ AgentRequest/AgentResponse dataclasses created
- ✅ Package imports working (no ModuleNotFoundError)
- ✅ Test fixtures created
- ✅ Logging infrastructure operational

---

## 🌊 Wave 1: Foundation Agents (6 hours)

**These agents provide core routing and planning capabilities**

### Task 4.1: IntentRouter Agent (2 hours)

**Purpose:** Route user requests to appropriate specialist agents

**Implementation:**
```python
class IntentRouter(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return True  # Router handles all requests
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # Analyze intent
        # Query Tier 2 for similar past intents
        # Route to specialist agent(s)
        # Return routing decision
        pass
```

**Tests (10 tests):**
- Intent classification accuracy
- Multi-agent routing
- Unknown intent handling
- Context-based routing decisions

**Exit Criteria:**
- ✅ Routes common intents correctly (>90% accuracy)
- ✅ Falls back gracefully on unknown intents
- ✅ Tests passing (10/10)

### Task 4.2: WorkPlanner Agent (2 hours)

**Purpose:** Break down complex requests into actionable tasks

**Implementation:**
```python
class WorkPlanner(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent in ["plan", "feature", "task_breakdown"]
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # Analyze request complexity
        # Query Tier 2 for similar workflows
        # Check Tier 3 for velocity/capacity
        # Generate task breakdown
        pass
```

**Tests (7 tests):**
- Simple task planning
- Complex feature breakdown
- Integration with Tier 2 patterns
- Velocity-aware estimation

**Exit Criteria:**
- ✅ Breaks down requests into tasks
- ✅ Leverages pattern library
- ✅ Tests passing (7/7)

### Task 4.3: HealthValidator Agent (2 hours)

**Purpose:** Check system health before executing risky operations

**Implementation:**
```python
class HealthValidator(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "health_check"
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # Check all tier databases
        # Verify test pass rate
        # Check uncommitted changes
        # Return health report
        pass
```

**Tests (5 tests):**
- Database health checks
- Test status validation
- Git status checking
- Warning threshold detection

**Exit Criteria:**
- ✅ Validates system health accurately
- ✅ Catches risky states
- ✅ Tests passing (5/5)

---

## 🌊 Wave 2: Execution Agents (6 hours)

**These agents perform code operations**

### Task 4.4: CodeExecutor Agent (2 hours)
- File creation/editing
- Multi-file operations
- Tests (6 tests)

### Task 4.5: TestGenerator Agent (2 hours)
- Test file creation
- TDD workflow enforcement
- Tests (6 tests)

### Task 4.6: ErrorCorrector Agent (2 hours)
- Error analysis
- Fix suggestions
- Tests (4 tests)

---

## 🌊 Wave 3: Advanced Agents (6 hours)

**These agents provide specialized capabilities**

### Task 4.7: SessionResumer (1.5 hours)
- Tier 1 conversation restoration
- Context reconstruction
- Tests (3 tests)

### Task 4.8: ScreenshotAnalyzer (1.5 hours)
- UI element identification
- Test ID suggestions
- Tests (3 tests)

### Task 4.9: ChangeGovernor (1.5 hours)
- Rule compliance checking
- Risk assessment
- Tests (4 tests)

### Task 4.10: CommitHandler (1.5 hours)
- Git operations
- Commit message generation
- Tests (3 tests)

---

## 🧪 Task 4.11: Agent Testing (2 hours)

**Comprehensive integration testing**

**Test Suites:**
1. Agent routing tests (5 tests)
2. Multi-agent collaboration (5 tests)
3. Error handling (5 tests)
4. Performance tests (3 tests)

**Exit Criteria:**
- ✅ All 30 agent tests passing
- ✅ Integration tests passing
- ✅ Agent response time <500ms

---

## 📦 Sub-Group 4B: Entry Point (5 hours)

**Simplified from 7 hours based on Group 3 efficiency**

### Task 5.1: cortex.md Entry Point (1.5 hours)
- Basic routing to IntentRouter
- Request parsing
- Response formatting

### Tasks 5.2-5.6: Supporting Components (3.5 hours)
- Request Parser (1 hr)
- Response Formatter (1 hr)
- Session State Manager (1 hr)
- Error Handling (30 min)
- Testing (1 hr - 10 tests)

---

## 🎨 Sub-Group 4C: Dashboard (10-12 hours)

**Core features only - advanced features deferred**

### Task 4C.1-4C.3: Foundation (4.5 hours)
- React + Vite setup (1 hr)
- SQL.js integration (1.5 hrs)
- File watching (2 hrs)

### Task 4C.4-4C.6: Tier Visualization (7 hours)
- Tier 1: Conversations view (2.5 hrs)
- Tier 2: Pattern search (2.5 hrs)
- Tier 3: Git metrics (2 hrs)

### Task 4C.7-4C.8: Finalization (2 hours)
- Performance monitoring (1.5 hrs)
- E2E tests (30 min)

---

## ✅ Success Criteria

**GROUP 4 is complete when:**

### Technical
- [ ] All 10 agents implemented and tested
- [ ] 30+ agent tests passing (100%)
- [ ] Entry point functional
- [ ] Dashboard displays all 3 tiers
- [ ] No import errors

### Performance
- [ ] Agent response time <500ms
- [ ] Intent routing >90% accurate
- [ ] Dashboard loads in <2s

### Quality
- [ ] Type hints on all public APIs
- [ ] Docstrings on all classes/methods
- [ ] README for each sub-group
- [ ] Usage examples documented

---

## 🎯 Execution Order

1. **START:** Task 4.0 (Agent Framework) - 2 hours
2. **Wave 1:** Foundation Agents (Tasks 4.1-4.3) - 6 hours
3. **Wave 2:** Execution Agents (Tasks 4.4-4.6) - 6 hours
4. **Wave 3:** Advanced Agents (Tasks 4.7-4.10) - 6 hours
5. **Testing:** Task 4.11 (Integration) - 2 hours
6. **Entry Point:** Sub-Group 4B (Tasks 5.1-5.6) - 5 hours
7. **Dashboard:** Sub-Group 4C (Tasks 4C.1-4C.8) - 10-12 hours

**Total:** 20-28 hours (3-4 days at 8 hours/day)

---

## 📚 Lessons Applied from GROUP 3

✅ **TDD First:** Write tests before implementation  
✅ **Small Chunks:** 100-150 lines per increment  
✅ **Framework First:** Common infrastructure reduces duplication  
✅ **Smart Simplification:** Core features, iterate later  
✅ **Document While Building:** READMEs during implementation

---

**Ready to Begin:** November 6, 2025  
**Expected Completion:** November 9-10, 2025  
**Status:** 🎯 READY FOR EXECUTION
