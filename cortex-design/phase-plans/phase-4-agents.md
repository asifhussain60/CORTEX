# Phase 4: Agents (Left/Right Brain Architecture)

**Version:** 1.0  
**Date:** 2025-11-05  
**Duration:** 12-16 hours + 1 hour holistic review  
**Dependencies:** Phase 0, 1, 2, 3 complete + reviewed  
**Storage:** Agent code in `CORTEX/cortex-agents/` (strategic/ and tactical/)  
**Performance Target:** Agent routing <50ms, coordination <100ms

---

## 🎯 Overview

**Purpose:** Build the agent ecosystem with clear LEFT BRAIN (tactical execution) and RIGHT BRAIN (strategic planning) separation. Implements Rule #27 (Hemisphere Separation) with message-based coordination.

**Key Deliverables:**
- RIGHT BRAIN agents (strategic): Planner, Router, Risk Assessor, Protector
- LEFT BRAIN agents (tactical): Executor, Tester, Validator, Archivist
- Agent orchestrator with message passing (Command Pattern)
- Plugin architecture for extensibility (Rule #28)
- Complete test coverage (32 unit + 8 integration tests)

---

## 📊 What We're Building

### Agent Architecture (Hemisphere Separation - Rule #27)

```
┌─────────────────────────────────────────────────────────────┐
│               AGENT ORCHESTRATOR (Corpus Callosum)          │
│                   Message Passing Layer                      │
└─────────────────────────────────────────────────────────────┘
         ▲                                     ▲
         │                                     │
    ┌────┴────┐                           ┌────┴────┐
    │  RIGHT  │                           │  LEFT   │
    │  BRAIN  │                           │  BRAIN  │
    │(Strategic)                          │(Tactical)│
    └─────────┘                           └─────────┘

RIGHT BRAIN (cortex-agents/strategic/):
├── intent_router.py          → Intent detection & routing
├── work_planner.py            → Multi-phase planning
├── risk_assessor.py           → Risk analysis
├── brain_protector.py         → Rule #22 challenges
└── pattern_matcher.py         → Tier 2 pattern queries

LEFT BRAIN (cortex-agents/tactical/):
├── code_executor.py           → Precise file edits
├── test_generator.py          → Test creation & execution
├── health_validator.py        → DoD validation
├── commit_handler.py          → Git commits
└── file_accessor.py           → File operations
```

### Agent Registry (Plugin Architecture - Rule #28)

```sql
CREATE TABLE agent_registry (
    agent_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    hemisphere TEXT CHECK(hemisphere IN ('RIGHT', 'LEFT')),
    agent_type TEXT,                    -- strategic, tactical
    responsibilities TEXT,              -- JSON array
    enabled BOOLEAN DEFAULT TRUE,
    plugin BOOLEAN DEFAULT FALSE,       -- Is this a plugin agent?
    version TEXT DEFAULT '1.0'
);

CREATE TABLE agent_capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT REFERENCES agent_registry(agent_id),
    capability_name TEXT NOT NULL,
    input_schema TEXT,                  -- JSON schema
    output_schema TEXT                  -- JSON schema
);
```

---

## 🏗️ Implementation Tasks

### Task 1: Agent Base Classes & Orchestrator
**File:** `CORTEX/cortex-agents/base_agent.py` + `orchestrator.py`  
**Duration:** 2.5 hours  
**Tests:** 5 unit tests

**Description:**
Base classes for all agents and message-passing orchestrator.

**Implementation Details:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import uuid

class AgentHemisphere(Enum):
    """Agent hemisphere classification (Rule #27)"""
    RIGHT = "RIGHT"  # Strategic
    LEFT = "LEFT"    # Tactical

class AgentMessage:
    """Message passed between agents via orchestrator"""
    def __init__(self, from_agent: str, to_agent: str, 
                 command: str, payload: Dict[str, Any]):
        self.message_id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.command = command
        self.payload = payload
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'command': self.command,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat()
        }

class BaseAgent(ABC):
    """Base class for all CORTEX agents"""
    
    def __init__(self, agent_id: str, agent_name: str, hemisphere: AgentHemisphere):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.hemisphere = hemisphere
        self.orchestrator: Optional['AgentOrchestrator'] = None
    
    def set_orchestrator(self, orchestrator: 'AgentOrchestrator'):
        """Register orchestrator for message passing"""
        self.orchestrator = orchestrator
    
    def send_message(self, to_agent: str, command: str, payload: Dict):
        """Send message to another agent via orchestrator"""
        if not self.orchestrator:
            raise ValueError("Orchestrator not set")
        
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            command=command,
            payload=payload
        )
        
        return self.orchestrator.route_message(message)
    
    @abstractmethod
    def handle_message(self, message: AgentMessage) -> Any:
        """Handle incoming message (must be implemented by subclass)"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        pass

class AgentOrchestrator:
    """
    Corpus Callosum: Message passing between hemispheres
    
    Enforces Rule #27: No direct cross-hemisphere calls
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: List[AgentMessage] = []
    
    def register_agent(self, agent: BaseAgent):
        """Register agent with orchestrator"""
        self.agents[agent.agent_id] = agent
        agent.set_orchestrator(self)
    
    def route_message(self, message: AgentMessage) -> Any:
        """
        Route message to destination agent
        
        Validates:
        - Destination agent exists
        - No invalid cross-hemisphere communication
        """
        if message.to_agent not in self.agents:
            raise ValueError(f"Agent '{message.to_agent}' not registered")
        
        destination_agent = self.agents[message.to_agent]
        
        # Validate hemisphere separation (Rule #27)
        if message.from_agent in self.agents:
            from_agent = self.agents[message.from_agent]
            self._validate_hemisphere_communication(from_agent, destination_agent, message)
        
        # Deliver message
        return destination_agent.handle_message(message)
    
    def _validate_hemisphere_communication(self, from_agent: BaseAgent, 
                                          to_agent: BaseAgent, 
                                          message: AgentMessage):
        """
        Validate communication follows hemisphere rules
        
        RIGHT → LEFT: OK (strategic plans → tactical execution)
        LEFT → RIGHT: OK (tactical results → strategic learning)
        RIGHT → RIGHT: OK (strategic collaboration)
        LEFT → LEFT: OK (tactical coordination)
        
        All communication goes through orchestrator (no direct calls)
        """
        # For now, all communication allowed via orchestrator
        # Direct calls are prevented by architecture (agents don't have references)
        pass
    
    def get_agent_by_capability(self, capability: str) -> Optional[BaseAgent]:
        """Find agent with specific capability"""
        for agent in self.agents.values():
            if capability in agent.get_capabilities():
                return agent
        return None
```

**Success Criteria:**
- [ ] BaseAgent abstract class enforces contract
- [ ] AgentMessage encapsulates communication
- [ ] AgentOrchestrator routes messages
- [ ] Hemisphere validation works
- [ ] Agent registration functional

---

### Task 2: RIGHT BRAIN - Intent Router
**File:** `CORTEX/cortex-agents/strategic/intent_router.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Strategic agent that detects user intent and routes to appropriate workflow.

**Implementation Details:**
```python
from typing import Dict, Any
from ..base_agent import BaseAgent, AgentHemisphere, AgentMessage

class IntentRouter(BaseAgent):
    """
    RIGHT BRAIN: Strategic intent detection and routing
    
    Responsibilities:
    - Analyze user request
    - Detect intent (PLAN, EXECUTE, TEST, FIX, QUERY)
    - Query Tier 2 for intent patterns
    - Route to appropriate workflow agent
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        super().__init__(
            agent_id="intent-router",
            agent_name="Intent Router",
            hemisphere=AgentHemisphere.RIGHT
        )
        self.db_path = db_path
    
    def get_capabilities(self) -> List[str]:
        return ['intent_detection', 'request_routing', 'pattern_matching']
    
    def handle_message(self, message: AgentMessage) -> Any:
        """Handle incoming routing request"""
        command = message.command
        
        if command == 'route_request':
            return self.route_request(message.payload['user_request'])
        
        elif command == 'detect_intent':
            return self.detect_intent(message.payload['user_request'])
        
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def route_request(self, user_request: str) -> Dict:
        """
        Route user request to appropriate workflow
        
        Returns:
            {
                'intent': 'PLAN',
                'confidence': 0.95,
                'target_agent': 'work-planner',
                'reasoning': 'User requested feature plan'
            }
        """
        # Detect intent
        intent_result = self.detect_intent(user_request)
        
        # Map intent to agent
        agent_mapping = {
            'PLAN': 'work-planner',
            'EXECUTE': 'code-executor',
            'TEST': 'test-generator',
            'FIX': 'error-corrector',
            'QUERY': 'knowledge-retriever',
            'VALIDATE': 'health-validator'
        }
        
        target_agent = agent_mapping.get(intent_result['intent'], 'work-planner')
        
        return {
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'target_agent': target_agent,
            'reasoning': intent_result['reasoning']
        }
    
    def detect_intent(self, user_request: str) -> Dict:
        """
        Detect user intent using Tier 2 patterns + heuristics
        
        1. Query Tier 2 for learned intent patterns
        2. Apply heuristic rules if no high-confidence match
        3. Return intent with confidence score
        """
        from ...tier2.intent_pattern_manager import IntentPatternManager
        
        # Try Tier 2 pattern match first
        ipm = IntentPatternManager(self.db_path)
        matched_intent = ipm.match_intent(user_request, min_confidence=0.7)
        
        if matched_intent:
            return {
                'intent': matched_intent,
                'confidence': 0.85,  # High confidence from learned pattern
                'reasoning': 'Matched learned pattern from Tier 2'
            }
        
        # Fallback to heuristic rules
        return self._heuristic_intent_detection(user_request)
    
    def _heuristic_intent_detection(self, user_request: str) -> Dict:
        """Heuristic intent detection (fallback)"""
        request_lower = user_request.lower()
        
        # Intent patterns (ordered by priority)
        if any(word in request_lower for word in ['plan', 'design', 'create plan', 'phases']):
            return {
                'intent': 'PLAN',
                'confidence': 0.75,
                'reasoning': 'Contains planning keywords'
            }
        
        if any(word in request_lower for word in ['implement', 'build', 'create', 'add']):
            return {
                'intent': 'EXECUTE',
                'confidence': 0.70,
                'reasoning': 'Contains execution keywords'
            }
        
        if any(word in request_lower for word in ['test', 'verify', 'validate']):
            return {
                'intent': 'TEST',
                'confidence': 0.75,
                'reasoning': 'Contains testing keywords'
            }
        
        if any(word in request_lower for word in ['fix', 'debug', 'error', 'bug']):
            return {
                'intent': 'FIX',
                'confidence': 0.80,
                'reasoning': 'Contains fix keywords'
            }
        
        if any(word in request_lower for word in ['explain', 'what is', 'how does']):
            return {
                'intent': 'QUERY',
                'confidence': 0.70,
                'reasoning': 'Contains query keywords'
            }
        
        # Default: PLAN (conservative choice)
        return {
            'intent': 'PLAN',
            'confidence': 0.50,
            'reasoning': 'No clear intent detected, defaulting to PLAN'
        }
```

**Success Criteria:**
- [ ] Intent detection works (heuristic + Tier 2)
- [ ] Routing maps intent to correct agent
- [ ] Confidence scores accurate
- [ ] Message handling functional

---

### Task 3: RIGHT BRAIN - Work Planner
**File:** `CORTEX/cortex-agents/strategic/work_planner.py`  
**Duration:** 2.5 hours  
**Tests:** 6 unit tests

**Description:**
Strategic planning agent that creates multi-phase execution plans.

**Implementation Details:**
```python
from typing import Dict, List, Any
from ..base_agent import BaseAgent, AgentHemisphere, AgentMessage
import json

class WorkPlanner(BaseAgent):
    """
    RIGHT BRAIN: Strategic work planning
    
    Responsibilities:
    - Break features into phases
    - Create task breakdown
    - Query Tier 2 for similar workflows
    - Query Tier 3 for time estimates
    - Generate execution plan
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        super().__init__(
            agent_id="work-planner",
            agent_name="Work Planner",
            hemisphere=AgentHemisphere.RIGHT
        )
        self.db_path = db_path
    
    def get_capabilities(self) -> List[str]:
        return ['planning', 'task_breakdown', 'estimation', 'workflow_matching']
    
    def handle_message(self, message: AgentMessage) -> Any:
        """Handle planning requests"""
        command = message.command
        
        if command == 'create_plan':
            return self.create_plan(
                message.payload['feature_description'],
                message.payload.get('constraints', {})
            )
        
        elif command == 'estimate_duration':
            return self.estimate_duration(message.payload['task_description'])
        
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def create_plan(self, feature_description: str, constraints: Dict = None) -> Dict:
        """
        Create multi-phase execution plan
        
        Steps:
        1. Query Tier 2 for similar workflows
        2. Query Tier 3 for time estimates
        3. Break into logical phases
        4. Create task breakdown
        5. Apply DoR/DoD (Rule #20, #21)
        
        Returns:
            {
                'plan_id': 'uuid',
                'feature': 'description',
                'phases': [
                    {
                        'phase': 0,
                        'name': 'Test Infrastructure',
                        'tasks': [...],
                        'duration_hours': 2.5
                    }
                ],
                'total_duration_hours': 12.5,
                'workflow_pattern_used': 'test_first_tdd'
            }
        """
        from ...tier2.workflow_pattern_manager import WorkflowPatternManager
        
        # Query Tier 2 for similar workflows
        wpm = WorkflowPatternManager(self.db_path)
        workflow_type = self._detect_workflow_type(feature_description)
        similar_workflow = wpm.recommend_workflow(workflow_type)
        
        # Create phases
        phases = self._create_phases(feature_description, similar_workflow)
        
        # Estimate durations using Tier 3
        for phase in phases:
            phase['duration_hours'] = self._estimate_phase_duration(phase)
        
        plan_id = str(uuid.uuid4())
        
        return {
            'plan_id': plan_id,
            'feature': feature_description,
            'phases': phases,
            'total_duration_hours': sum(p['duration_hours'] for p in phases),
            'workflow_pattern_used': workflow_type,
            'similar_workflow': similar_workflow
        }
    
    def _detect_workflow_type(self, description: str) -> str:
        """Detect workflow type from description"""
        desc_lower = description.lower()
        
        if 'test' in desc_lower or 'tdd' in desc_lower:
            return 'test_first_tdd'
        
        if 'feature' in desc_lower or 'add' in desc_lower:
            return 'feature_creation'
        
        if 'fix' in desc_lower or 'bug' in desc_lower:
            return 'bug_fix'
        
        return 'feature_creation'  # Default
    
    def _create_phases(self, description: str, 
                      similar_workflow: Optional[Dict]) -> List[Dict]:
        """Create phase breakdown"""
        phases = []
        
        # Phase 0: Test Infrastructure (if TDD)
        if 'test' in description.lower():
            phases.append({
                'phase': 0,
                'name': 'Test Infrastructure',
                'tasks': [
                    'Define test scenarios',
                    'Create test fixtures',
                    'Setup test environment'
                ]
            })
        
        # Phase 1: Core Implementation
        phases.append({
            'phase': len(phases),
            'name': 'Core Implementation',
            'tasks': self._break_into_tasks(description)
        })
        
        # Phase N: Validation
        phases.append({
            'phase': len(phases),
            'name': 'Validation & Documentation',
            'tasks': [
                'Run all tests',
                'Validate DoD criteria',
                'Update documentation',
                'Commit changes'
            ]
        })
        
        return phases
    
    def _break_into_tasks(self, description: str) -> List[str]:
        """Break feature into tasks"""
        # Simplified task breakdown (can be enhanced)
        return [
            f"Implement {description}",
            "Write unit tests",
            "Integration testing",
            "Code review"
        ]
    
    def _estimate_phase_duration(self, phase: Dict) -> float:
        """Estimate phase duration using Tier 3 metrics"""
        # Query Tier 3 for historical data
        # For now, simple heuristic
        task_count = len(phase['tasks'])
        return task_count * 0.5  # 30 min per task
```

**Success Criteria:**
- [ ] Plans created with phases
- [ ] Tasks broken down logically
- [ ] Tier 2 workflow matching works
- [ ] Duration estimates reasonable
- [ ] DoR/DoD included

---

### Task 4: LEFT BRAIN - Code Executor
**File:** `CORTEX/cortex-agents/tactical/code_executor.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Tactical agent for precise code implementation.

**Implementation Details:**
```python
from typing import Dict, List, Any
from ..base_agent import BaseAgent, AgentHemisphere, AgentMessage

class CodeExecutor(BaseAgent):
    """
    LEFT BRAIN: Tactical code execution
    
    Responsibilities:
    - Execute implementation tasks
    - Make precise file edits
    - Follow TDD cycle (RED → GREEN → REFACTOR)
    - Coordinate with test-generator
    """
    
    def __init__(self):
        super().__init__(
            agent_id="code-executor",
            agent_name="Code Executor",
            hemisphere=AgentHemisphere.LEFT
        )
    
    def get_capabilities(self) -> List[str]:
        return ['code_implementation', 'file_editing', 'tdd_execution']
    
    def handle_message(self, message: AgentMessage) -> Any:
        """Handle execution requests"""
        command = message.command
        
        if command == 'execute_task':
            return self.execute_task(message.payload['task'])
        
        elif command == 'edit_file':
            return self.edit_file(
                message.payload['file_path'],
                message.payload['changes']
            )
        
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def execute_task(self, task: Dict) -> Dict:
        """
        Execute implementation task following TDD
        
        Steps:
        1. Request test from test-generator (RED)
        2. Implement minimum code (GREEN)
        3. Refactor if needed (REFACTOR)
        4. Validate with health-validator
        
        Returns:
            {
                'status': 'success',
                'files_modified': [...],
                'tests_passing': True,
                'tdd_cycle': 'RED → GREEN → REFACTOR'
            }
        """
        # Step 1: Request RED test
        test_message = self.send_message(
            to_agent='test-generator',
            command='create_test',
            payload={'task': task}
        )
        
        # Step 2: Implement code (GREEN)
        implementation_result = self._implement_code(task)
        
        # Step 3: Run tests (verify GREEN)
        test_result = self.send_message(
            to_agent='test-generator',
            command='run_tests',
            payload={'test_file': test_message['test_file']}
        )
        
        # Step 4: Refactor if needed
        if test_result['passing'] and implementation_result.get('needs_refactor'):
            self._refactor_code(implementation_result['files'])
        
        # Step 5: Validate DoD
        validation = self.send_message(
            to_agent='health-validator',
            command='validate_dod',
            payload={'files': implementation_result['files']}
        )
        
        return {
            'status': 'success',
            'files_modified': implementation_result['files'],
            'tests_passing': test_result['passing'],
            'tdd_cycle': 'RED → GREEN → REFACTOR',
            'dod_validated': validation['dod_met']
        }
    
    def _implement_code(self, task: Dict) -> Dict:
        """Implement code changes"""
        # File editing logic here
        return {
            'files': task.get('files', []),
            'needs_refactor': False
        }
    
    def _refactor_code(self, files: List[str]):
        """Refactor code while maintaining tests"""
        # Refactoring logic here
        pass
```

**Success Criteria:**
- [ ] Task execution follows TDD cycle
- [ ] File edits precise
- [ ] Coordination with test-generator works
- [ ] DoD validation enforced

---

### Task 5: LEFT BRAIN - Test Generator
**File:** `CORTEX/cortex-agents/tactical/test_generator.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Tactical agent for test creation and execution.

**Implementation Details:**
```python
from typing import Dict, List, Any
from ..base_agent import BaseAgent, AgentHemisphere, AgentMessage

class TestGenerator(BaseAgent):
    """
    LEFT BRAIN: Tactical test generation and execution
    
    Responsibilities:
    - Create failing tests (RED phase)
    - Run tests and report results
    - Enforce Rule #5 (Test-First TDD)
    - Validate test coverage
    """
    
    def __init__(self):
        super().__init__(
            agent_id="test-generator",
            agent_name="Test Generator",
            hemisphere=AgentHemisphere.LEFT
        )
    
    def get_capabilities(self) -> List[str]:
        return ['test_creation', 'test_execution', 'tdd_enforcement', 'coverage_validation']
    
    def handle_message(self, message: AgentMessage) -> Any:
        """Handle test requests"""
        command = message.command
        
        if command == 'create_test':
            return self.create_test(message.payload['task'])
        
        elif command == 'run_tests':
            return self.run_tests(message.payload['test_file'])
        
        elif command == 'validate_coverage':
            return self.validate_coverage(message.payload['files'])
        
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def create_test(self, task: Dict) -> Dict:
        """
        Create failing test (RED phase)
        
        Returns:
            {
                'test_file': 'path/to/test.py',
                'test_name': 'test_feature_xyz',
                'status': 'RED',
                'expected_failure': True
            }
        """
        # Test generation logic
        test_file = f"tests/test_{task['name']}.py"
        
        # Generate test code
        test_code = self._generate_test_code(task)
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Run to verify it fails
        result = self.run_tests(test_file)
        
        if result['status'] != 'FAILED':
            raise ValueError("Test should fail (RED phase)")
        
        return {
            'test_file': test_file,
            'test_name': task['name'],
            'status': 'RED',
            'expected_failure': True
        }
    
    def run_tests(self, test_file: str) -> Dict:
        """Run tests and return results"""
        import subprocess
        
        # Run pytest
        result = subprocess.run(
            ['pytest', test_file, '-v'],
            capture_output=True,
            text=True
        )
        
        passing = result.returncode == 0
        
        return {
            'test_file': test_file,
            'status': 'PASSED' if passing else 'FAILED',
            'passing': passing,
            'output': result.stdout
        }
    
    def _generate_test_code(self, task: Dict) -> str:
        """Generate test code for task"""
        # Test template
        return f"""
import pytest

def test_{task['name']}():
    \"\"\"Test for {task['description']}\"\"\"
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented yet (RED phase)"
"""
```

**Success Criteria:**
- [ ] Tests created (RED phase verified)
- [ ] Test execution works
- [ ] Coverage validation functional
- [ ] TDD cycle enforced

---

### Task 6: Agent Plugin System
**File:** `CORTEX/cortex-agents/plugin_manager.py`  
**Duration:** 2 hours  
**Tests:** 4 unit tests

**Description:**
Plugin system for extensible agents (Rule #28).

**Implementation Details:**
```python
from typing import Dict, Type, List
import importlib
import inspect

class AgentPluginManager:
    """
    Manage agent plugins (Rule #28)
    
    Allows third-party agents to be registered and used
    """
    
    def __init__(self):
        self.registered_plugins: Dict[str, Type[BaseAgent]] = {}
        self.enabled_plugins: List[str] = []
    
    def register_plugin(self, agent_class: Type[BaseAgent]):
        """
        Register agent plugin
        
        Usage:
            @plugin_manager.register_plugin
            class CustomAnalyzer(BaseAgent):
                ...
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError("Plugin must inherit from BaseAgent")
        
        agent_id = agent_class.agent_id if hasattr(agent_class, 'agent_id') else agent_class.__name__
        
        self.registered_plugins[agent_id] = agent_class
    
    def load_plugins_from_directory(self, directory: str):
        """Load all plugins from directory"""
        import os
        
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                module = importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")
                
                # Find BaseAgent subclasses
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj != BaseAgent:
                        self.register_plugin(obj)
    
    def enable_plugin(self, agent_id: str):
        """Enable plugin for use"""
        if agent_id not in self.registered_plugins:
            raise ValueError(f"Plugin '{agent_id}' not registered")
        
        if agent_id not in self.enabled_plugins:
            self.enabled_plugins.append(agent_id)
    
    def create_plugin_instance(self, agent_id: str) -> BaseAgent:
        """Create instance of plugin agent"""
        if agent_id not in self.enabled_plugins:
            raise ValueError(f"Plugin '{agent_id}' not enabled")
        
        agent_class = self.registered_plugins[agent_id]
        return agent_class()
```

**Success Criteria:**
- [ ] Plugins registered via decorator
- [ ] Plugins loaded from directory
- [ ] Plugin enabling/disabling works
- [ ] Plugin instances created

---

## 📋 Test Plan (32 Unit + 8 Integration = 40 Total)

### Unit Tests (32 tests)

**BaseAgent & Orchestrator (5 tests):**
- [ ] `test_base_agent_abstract()` - Cannot instantiate base class
- [ ] `test_message_passing()` - Messages routed correctly
- [ ] `test_orchestrator_registration()` - Agents register successfully
- [ ] `test_hemisphere_validation()` - Communication validated
- [ ] `test_capability_lookup()` - Agents found by capability

**IntentRouter (5 tests):**
- [ ] `test_detect_intent_heuristic()` - Heuristics work
- [ ] `test_detect_intent_tier2()` - Tier 2 patterns used
- [ ] `test_route_request()` - Routing maps correctly
- [ ] `test_confidence_scoring()` - Confidence scores accurate
- [ ] `test_fallback_plan()` - Defaults to PLAN when uncertain

**WorkPlanner (6 tests):**
- [ ] `test_create_plan()` - Plans created with phases
- [ ] `test_workflow_matching()` - Tier 2 workflows matched
- [ ] `test_duration_estimation()` - Tier 3 used for estimates
- [ ] `test_phase_breakdown()` - Phases logical
- [ ] `test_task_breakdown()` - Tasks clear and actionable
- [ ] `test_dor_dod_inclusion()` - DoR/DoD criteria included

**CodeExecutor (5 tests):**
- [ ] `test_execute_task()` - Tasks executed
- [ ] `test_tdd_cycle()` - TDD cycle followed
- [ ] `test_file_editing()` - Files edited precisely
- [ ] `test_test_generator_coordination()` - Coordination works
- [ ] `test_dod_validation()` - DoD enforced

**TestGenerator (5 tests):**
- [ ] `test_create_test()` - RED test created
- [ ] `test_run_tests()` - Tests executed
- [ ] `test_red_verification()` - RED phase verified
- [ ] `test_coverage_validation()` - Coverage checked
- [ ] `test_tdd_enforcement()` - Rule #5 enforced

**PluginManager (4 tests):**
- [ ] `test_register_plugin()` - Plugins registered
- [ ] `test_load_plugins()` - Directory loading works
- [ ] `test_enable_plugin()` - Enabling works
- [ ] `test_create_instance()` - Instances created

**BrainProtector (2 tests):**
- [ ] `test_challenge_risky_change()` - Rule #22 challenges work
- [ ] `test_suggest_alternatives()` - Alternatives provided

### Integration Tests (8 tests)

**End-to-End Workflows:**
- [ ] `test_plan_to_execution_workflow()` - RIGHT BRAIN plans → LEFT BRAIN executes
- [ ] `test_tdd_full_cycle()` - RED → GREEN → REFACTOR complete
- [ ] `test_intent_routing_execution()` - Request → Route → Execute
- [ ] `test_tier2_pattern_usage()` - Agents query Tier 2 for patterns
- [ ] `test_tier3_metrics_usage()` - Agents use Tier 3 for estimates
- [ ] `test_hemisphere_coordination()` - Message passing works
- [ ] `test_plugin_integration()` - Custom plugin works in workflow
- [ ] `test_governance_enforcement()` - Agents enforce Rule #5, #20, #21

---

## ⚡ Performance Benchmarks

```python
def test_routing_performance():
    """Ensure routing meets <50ms target"""
    import time
    
    router = IntentRouter()
    
    start = time.perf_counter()
    result = router.route_request("Add purple button to control panel")
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 50, f"Routing took {elapsed}ms (target: <50ms)"

def test_coordination_performance():
    """Ensure agent coordination meets <100ms target"""
    import time
    
    orchestrator = AgentOrchestrator()
    planner = WorkPlanner()
    executor = CodeExecutor()
    
    orchestrator.register_agent(planner)
    orchestrator.register_agent(executor)
    
    start = time.perf_counter()
    
    # Planner sends task to executor
    message = AgentMessage(
        from_agent='work-planner',
        to_agent='code-executor',
        command='execute_task',
        payload={'task': {'name': 'test'}}
    )
    
    orchestrator.route_message(message)
    
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 100, f"Coordination took {elapsed}ms (target: <100ms)"
```

**Targets:**
- Agent routing: <50ms
- Message passing: <100ms
- Plan creation: <500ms
- Task execution: Varies by task

---

## 🎯 Success Criteria

**Phase 4 complete when:**
- ✅ All 32 unit tests passing
- ✅ All 8 integration tests passing
- ✅ LEFT/RIGHT brain separation enforced (Rule #27)
- ✅ Plugin architecture functional (Rule #28)
- ✅ Message passing works (no direct cross-hemisphere calls)
- ✅ TDD cycle enforced (Rule #5)
- ✅ DoR/DoD validated (Rule #20, #21)
- ✅ Integration with Tiers 0-3 validated
- ✅ Documentation complete
- ✅ **Holistic review passed** ⚠️ MANDATORY

---

## 📖 Documentation Deliverables

1. **Agent Architecture:** `CORTEX/docs/agent-architecture.md`
2. **Hemisphere Separation:** `CORTEX/docs/hemisphere-separation-guide.md`
3. **Plugin Development:** `CORTEX/docs/plugin-development-guide.md`
4. **Message Protocol:** `CORTEX/docs/agent-message-protocol.md`

---

## 🔍 MANDATORY: Holistic Review (Phase 4 Complete)

**⚠️ DO NOT PROCEED TO PHASE 5 UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase 4 Section

#### 1. Design Alignment ✅
- [ ] Does hemisphere separation match Rule #27?
- [ ] Is plugin architecture per Rule #28?
- [ ] Does message passing prevent direct calls?
- [ ] Are agent responsibilities clear (SRP)?
- [ ] Does TDD enforcement work (Rule #5)?

#### 2. Implementation Quality ✅
- [ ] All 32 unit tests passing?
- [ ] All 8 integration tests passing?
- [ ] Code follows Python best practices?
- [ ] Type hints used consistently?
- [ ] Error handling comprehensive?
- [ ] Logging implemented?

#### 3. Performance Validation ✅
- [ ] Routing <50ms achieved?
- [ ] Coordination <100ms achieved?
- [ ] No performance regressions?

#### 4. Integration with Previous Phases ✅
- [ ] Phase 0 rules enforced by agents?
- [ ] Phase 1 conversations accessible?
- [ ] Phase 2 patterns used for recommendations?
- [ ] Phase 3 metrics used for estimates?

#### 5. Integration Readiness for Next Phase ✅
- [ ] Phase 5 can use agents for routing?
- [ ] Entry point can invoke intent-router?
- [ ] No blocking issues?

#### 6. Adjustments Needed
- [ ] Should more agents be added?
- [ ] Should message protocol be enhanced?
- [ ] Should plugin examples be added?

### Review Output Document
**Create:** `cortex-design/reviews/phase-4-review.md`

### Actions After Review
[Same structure as previous phases]

### Success Metrics for Phase 4
- ✅ All tests passing (40 total)
- ✅ All benchmarks met (<50ms, <100ms)
- ✅ Hemisphere separation enforced
- ✅ Plugin architecture functional
- ✅ Review report created and approved
- ✅ Phase 5 plan updated with learnings

---

## 📊 Phase Timeline

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|------------|
| 1 | Task 1 (Base + Orchestrator) + Task 2 (Router) | 4.5 | 4.5 |
| 2 | Task 3 (Planner) + Task 4 (Executor) | 4.5 | 9 |
| 3 | Task 5 (TestGen) + Task 6 (Plugins) | 4 | 13 |
| 4 | Integration Tests + Docs | 4 | 17 |
| 5 | **Holistic Review** + Adjustments | 1.5 | 18.5 |

**Total Estimated:** 12-16 hours implementation + 1 hour review + 1.5 hours adjustments = 14.5-18.5 hours

---

## ✅ Phase Completion Checklist

**Implementation:**
- [ ] All tasks complete
- [ ] All 32 unit tests written and passing
- [ ] All 8 integration tests written and passing
- [ ] All benchmarks met
- [ ] Documentation written
- [ ] Code reviewed

**Review:**
- [ ] Holistic review checklist completed
- [ ] Review report written
- [ ] Issues documented
- [ ] Adjustments (if any) implemented
- [ ] Phase 5 plan updated

**Commit:**
- [ ] Implementation committed
- [ ] Review report committed
- [ ] Updated plans committed

**Proceed:**
- [ ] Review status is PASS ✅
- [ ] Team notified of completion
- [ ] Phase 5 ready to start

---

**Status:** Ready for implementation  
**Next:** Phase 5 (Entry Point & Workflows)  
**Estimated Completion:** 14.5-18.5 hours  
**⚠️ CRITICAL:** Complete holistic review before Phase 5!

---

## 🔗 Related Documents

- `HOLISTIC-REVIEW-PROTOCOL.md` - Complete review process
- `phase-3-context-intelligence-updated.md` - Previous phase
- `phase-5-entry-point.md` - Next phase
- `DESIGN-IMPROVEMENTS-SUMMARY.md` - Architecture decisions
- `unified-database-schema.sql` - Database schema
- `CORTEX-DNA.md` - Core design principles
- `WHY-CORTEX-IS-BETTER.md` - Rationale
