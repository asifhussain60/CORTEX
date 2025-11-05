# Phase 5: Entry Point & Workflows

**Version:** 1.0  
**Date:** 2025-11-05  
**Duration:** 6-8 hours + 1 hour holistic review  
**Dependencies:** Phase 0, 1, 2, 3, 4 complete + reviewed  
**Storage:** Entry point in `CORTEX/cortex.md`, workflows in `CORTEX/src/workflows/`  
**Performance Target:** Intent routing <100ms, context injection <200ms

---

## 🎯 Overview

**Purpose:** Create the unified entry point (CORTEX equivalent of `kds.md`) with intent detection, workflow orchestration, and context injection. This is where users interact with CORTEX.

**Key Deliverables:**
- Universal entry point (`cortex.md`)
- Intent detection → workflow routing
- Workflow orchestration (TDD, feature creation, bug fix)
- Context injection (Tiers 1-3)
- Session management (conversation boundaries)
- Complete test coverage (22 unit + 7 integration tests)

---

## 📊 What We're Building

### Entry Point Flow

```
User Request → cortex.md
              ↓
       Intent Detection (Phase 4: intent-router)
              ↓
       Context Injection (Tiers 1-3)
              ↓
       Workflow Selection
              ↓
    ┌──────────┴──────────┐
    ↓                     ↓
TDD Workflow       Feature Workflow       Bug Fix Workflow
    ↓                     ↓                      ↓
RED → GREEN → REFACTOR   PLAN → EXECUTE → TEST  DIAGNOSE → FIX → VERIFY
```

### Workflow Types

1. **TDD Workflow** (Rule #5)
   - RED: Create failing test
   - GREEN: Minimum implementation
   - REFACTOR: Improve while keeping tests green

2. **Feature Creation Workflow**
   - PLAN: Multi-phase breakdown (Phase 4: work-planner)
   - EXECUTE: Implement with TDD (Phase 4: code-executor)
   - TEST: Validate DoD (Phase 4: test-generator)

3. **Bug Fix Workflow**
   - DIAGNOSE: Analyze error logs
   - FIX: Implement fix with tests
   - VERIFY: Validate fix + prevent regression

4. **Query Workflow**
   - ANALYZE: Parse question
   - SEARCH: Query Tier 2 patterns
   - RESPOND: Provide context-rich answer

---

## 🏗️ Implementation Tasks

### Task 1: Universal Entry Point
**File:** `CORTEX/cortex.md`  
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
Universal markdown entry point (like `kds.md`). Receives user requests, routes to workflows.

**Implementation Details:**
```markdown
# CORTEX - Development Intelligence System

**Purpose:** Unified entry point for all development tasks  
**Usage:** Send development requests here (planning, implementation, testing, queries)

---

## 🚀 Quick Start

**For Planning:**
> "Create a plan for adding authentication to the dashboard"

**For Implementation:**
> "Implement the login form with validation"

**For Testing:**
> "Run all tests and validate code coverage"

**For Queries:**
> "Explain how the brain update process works"

---

## 📋 How It Works

1. **Intent Detection:** Your request is analyzed to determine intent (PLAN, EXECUTE, TEST, FIX, QUERY)
2. **Context Injection:** Relevant context from brain (Tiers 1-3) is loaded
3. **Workflow Selection:** Appropriate workflow is selected
4. **Execution:** Task is executed following best practices (TDD, DoD, etc.)
5. **Learning:** Outcomes are recorded for future pattern matching

---

## 🧠 Internal Processing

<!-- AGENT ROUTING METADATA -->
<!-- This section is processed by cortex-router.py -->

```yaml
request_metadata:
  source: "cortex.md"
  conversation_id: auto-generated
  timestamp: auto-generated
  
context_requirements:
  working_memory: true     # Load Tier 1 (last 50 conversations)
  knowledge_graph: true    # Load Tier 2 (patterns)
  dev_context: true        # Load Tier 3 (recent activity)
  
routing_config:
  intent_router: "cortex-agents/strategic/intent_router.py"
  confidence_threshold: 0.7
  fallback_workflow: "plan"
```

---

## 🔧 Developer Notes

**For CORTEX Developers:**
- Entry point processed by `CORTEX/src/router.py`
- User requests extracted from conversation
- Intent detection via Phase 4 agents
- Workflow orchestration via Phase 5 workflows
- All interactions logged to Tier 1

**Performance:**
- Intent detection: <100ms
- Context injection: <200ms
- Total routing: <300ms

---

## 📊 Workflow Status

Current workflow: `<auto-populated>`  
Phase: `<auto-populated>`  
Progress: `<auto-populated>`

```

**Supporting Python Router:**
```python
# CORTEX/src/router.py

from typing import Dict, Any
import yaml
import sqlite3
from cortex_agents.strategic.intent_router import IntentRouter
from tier1.working_memory_engine import WorkingMemoryEngine
from tier2.knowledge_graph_engine import KnowledgeGraphEngine
from tier3.dev_context_engine import DevContextEngine

class CortexRouter:
    """
    Universal router for cortex.md entry point
    
    Responsibilities:
    - Extract user request from cortex.md
    - Detect intent via Phase 4 agents
    - Inject context from Tiers 1-3
    - Route to appropriate workflow
    - Log interaction to Tier 1
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
        self.intent_router = IntentRouter(db_path)
        self.wm_engine = WorkingMemoryEngine(db_path)
        self.kg_engine = KnowledgeGraphEngine(db_path)
        self.dc_engine = DevContextEngine(db_path)
    
    def process_request(self, user_request: str, conversation_id: str = None) -> Dict:
        """
        Process request from cortex.md
        
        Steps:
        1. Detect intent
        2. Inject context
        3. Route to workflow
        4. Log interaction
        
        Returns:
            {
                'intent': 'PLAN',
                'workflow': 'feature_creation',
                'context': {...},
                'next_step': '...'
            }
        """
        import time
        start = time.perf_counter()
        
        # Step 1: Detect intent (Phase 4: intent-router)
        intent_result = self.intent_router.route_request(user_request)
        
        # Step 2: Inject context from Tiers 1-3
        context = self._inject_context(user_request, conversation_id)
        
        # Step 3: Select workflow
        workflow = self._select_workflow(intent_result, context)
        
        # Step 4: Log interaction (Tier 1)
        if not conversation_id:
            conversation_id = self.wm_engine.start_conversation()
        
        self.wm_engine.add_message(
            conversation_id=conversation_id,
            role='user',
            content=user_request
        )
        
        elapsed = (time.perf_counter() - start) * 1000
        
        return {
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'workflow': workflow,
            'context': context,
            'conversation_id': conversation_id,
            'routing_time_ms': elapsed
        }
    
    def _inject_context(self, user_request: str, conversation_id: str = None) -> Dict:
        """
        Inject context from Tiers 1-3
        
        Performance: <200ms total
        """
        context = {}
        
        # Tier 1: Recent conversations + entities (last 50 conversations)
        if conversation_id:
            context['current_conversation'] = self.wm_engine.get_conversation(conversation_id)
        
        context['recent_entities'] = self.wm_engine.extract_entities_from_recent(limit=20)
        
        # Tier 2: Relevant patterns
        context['patterns'] = self.kg_engine.search_patterns(user_request, limit=5)
        
        # Tier 3: Recent development context
        context['dev_activity'] = self.dc_engine.get_recent_activity(hours=24)
        context['active_files'] = self.dc_engine.get_active_files(hours=48)
        
        return context
    
    def _select_workflow(self, intent_result: Dict, context: Dict) -> str:
        """Select appropriate workflow based on intent"""
        intent = intent_result['intent']
        
        workflow_mapping = {
            'PLAN': 'feature_creation',
            'EXECUTE': 'tdd_implementation',
            'TEST': 'test_validation',
            'FIX': 'bug_fix',
            'QUERY': 'knowledge_query'
        }
        
        return workflow_mapping.get(intent, 'feature_creation')
```

**Success Criteria:**
- [ ] `cortex.md` created with clear user interface
- [ ] Router extracts requests and detects intent
- [ ] Context injection <200ms
- [ ] Workflow selection correct
- [ ] Conversation logging works

---

### Task 2: TDD Workflow Orchestrator
**File:** `CORTEX/src/workflows/tdd_workflow.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Orchestrate RED → GREEN → REFACTOR TDD cycle (Rule #5).

**Implementation Details:**
```python
from typing import Dict, Any
from ..cortex_agents.strategic.work_planner import WorkPlanner
from ..cortex_agents.tactical.test_generator import TestGenerator
from ..cortex_agents.tactical.code_executor import CodeExecutor
from ..cortex_agents.tactical.health_validator import HealthValidator

class TDDWorkflow:
    """
    TDD Workflow Orchestrator (Rule #5)
    
    Orchestrates RED → GREEN → REFACTOR cycle
    
    Phases:
    1. RED: Create failing test
    2. GREEN: Minimum implementation to pass
    3. REFACTOR: Improve code while keeping tests green
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.test_gen = TestGenerator()
        self.code_exec = CodeExecutor()
        self.validator = HealthValidator()
    
    def execute(self, task: Dict, context: Dict) -> Dict:
        """
        Execute TDD cycle
        
        Args:
            task: {'name': 'feature_name', 'description': '...'}
            context: Injected context from router
        
        Returns:
            {
                'status': 'success',
                'cycle': 'RED → GREEN → REFACTOR',
                'files_modified': [...],
                'tests_created': [...],
                'tests_passing': True
            }
        """
        results = {
            'status': 'in_progress',
            'cycle': 'RED → GREEN → REFACTOR',
            'phases': []
        }
        
        # PHASE 1: RED - Create failing test
        red_result = self._red_phase(task)
        results['phases'].append(red_result)
        
        if red_result['status'] != 'RED':
            raise ValueError("RED phase failed: Test must fail initially")
        
        # PHASE 2: GREEN - Minimum implementation
        green_result = self._green_phase(task, red_result['test_file'])
        results['phases'].append(green_result)
        
        if green_result['status'] != 'GREEN':
            raise ValueError("GREEN phase failed: Tests not passing")
        
        # PHASE 3: REFACTOR - Improve code
        refactor_result = self._refactor_phase(green_result['files'])
        results['phases'].append(refactor_result)
        
        # Validate DoD (Rule #21)
        dod_result = self._validate_dod(refactor_result['files'])
        results['dod_validated'] = dod_result['passed']
        
        results['status'] = 'success'
        results['files_modified'] = refactor_result['files']
        results['tests_passing'] = True
        
        return results
    
    def _red_phase(self, task: Dict) -> Dict:
        """
        RED phase: Create failing test
        
        Returns:
            {
                'status': 'RED',
                'test_file': 'path/to/test.py',
                'test_name': 'test_feature'
            }
        """
        # Use test-generator agent
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='test-generator',
            command='create_test',
            payload={'task': task}
        )
        
        result = self.orchestrator.route_message(message)
        
        # Verify test fails
        if result['status'] != 'RED':
            raise ValueError("Test must fail in RED phase")
        
        return {
            'phase': 'RED',
            'status': 'RED',
            'test_file': result['test_file'],
            'test_name': result['test_name']
        }
    
    def _green_phase(self, task: Dict, test_file: str) -> Dict:
        """
        GREEN phase: Minimum implementation to pass test
        
        Returns:
            {
                'status': 'GREEN',
                'files': [...],
                'tests_passing': True
            }
        """
        # Use code-executor agent
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='code-executor',
            command='execute_task',
            payload={'task': task, 'test_file': test_file}
        )
        
        result = self.orchestrator.route_message(message)
        
        # Verify tests pass
        if not result['tests_passing']:
            raise ValueError("Tests must pass in GREEN phase")
        
        return {
            'phase': 'GREEN',
            'status': 'GREEN',
            'files': result['files_modified'],
            'tests_passing': True
        }
    
    def _refactor_phase(self, files: List[str]) -> Dict:
        """
        REFACTOR phase: Improve code while keeping tests green
        
        Returns:
            {
                'status': 'REFACTORED',
                'files': [...],
                'improvements': [...]
            }
        """
        # Apply refactoring patterns
        # For now, placeholder
        return {
            'phase': 'REFACTOR',
            'status': 'REFACTORED',
            'files': files,
            'improvements': ['Code structure improved']
        }
    
    def _validate_dod(self, files: List[str]) -> Dict:
        """Validate Definition of Done (Rule #21)"""
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='health-validator',
            command='validate_dod',
            payload={'files': files}
        )
        
        return self.orchestrator.route_message(message)
```

**Success Criteria:**
- [ ] RED → GREEN → REFACTOR cycle enforced
- [ ] Tests fail in RED, pass in GREEN
- [ ] DoD validated at end
- [ ] Agent coordination works

---

### Task 3: Feature Creation Workflow
**File:** `CORTEX/src/workflows/feature_workflow.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Orchestrate feature creation: PLAN → EXECUTE → TEST.

**Implementation Details:**
```python
from typing import Dict, Any
from .tdd_workflow import TDDWorkflow

class FeatureCreationWorkflow:
    """
    Feature Creation Workflow
    
    Phases:
    1. PLAN: Multi-phase breakdown (work-planner agent)
    2. EXECUTE: Implement each phase with TDD
    3. TEST: Validate complete feature
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.tdd_workflow = TDDWorkflow(orchestrator)
    
    def execute(self, feature_description: str, context: Dict) -> Dict:
        """
        Execute feature creation
        
        Args:
            feature_description: User's feature request
            context: Injected context (Tiers 1-3)
        
        Returns:
            {
                'status': 'success',
                'plan': {...},
                'phases_completed': 3,
                'files_modified': [...],
                'tests_created': [...]
            }
        """
        results = {
            'status': 'in_progress',
            'workflow': 'feature_creation',
            'phases_completed': 0
        }
        
        # PHASE 1: PLAN
        plan = self._create_plan(feature_description, context)
        results['plan'] = plan
        
        # PHASE 2: EXECUTE each phase with TDD
        for phase in plan['phases']:
            phase_result = self._execute_phase(phase)
            results['phases_completed'] += 1
        
        # PHASE 3: TEST complete feature
        validation_result = self._validate_feature(plan)
        results['validation'] = validation_result
        
        results['status'] = 'success'
        return results
    
    def _create_plan(self, feature_description: str, context: Dict) -> Dict:
        """Create multi-phase plan using work-planner agent"""
        from ..cortex_agents.base_agent import AgentMessage
        
        message = AgentMessage(
            from_agent='feature-workflow',
            to_agent='work-planner',
            command='create_plan',
            payload={
                'feature_description': feature_description,
                'context': context
            }
        )
        
        return self.orchestrator.route_message(message)
    
    def _execute_phase(self, phase: Dict) -> Dict:
        """Execute phase using TDD workflow"""
        results = []
        
        for task in phase['tasks']:
            task_result = self.tdd_workflow.execute(
                task={'name': task, 'description': task},
                context={}
            )
            results.append(task_result)
        
        return {
            'phase': phase['phase'],
            'tasks_completed': len(results),
            'results': results
        }
    
    def _validate_feature(self, plan: Dict) -> Dict:
        """Validate complete feature meets DoD"""
        from ..cortex_agents.base_agent import AgentMessage
        
        message = AgentMessage(
            from_agent='feature-workflow',
            to_agent='health-validator',
            command='validate_feature',
            payload={'plan': plan}
        )
        
        return self.orchestrator.route_message(message)
```

**Success Criteria:**
- [ ] Plans created via work-planner
- [ ] Each phase executed with TDD
- [ ] Feature validated at end
- [ ] Context used for planning

---

### Task 4: Session Manager
**File:** `CORTEX/src/session_manager.py`  
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
Manage conversation sessions and boundaries (Rule #11).

**Implementation Details:**
```python
import sqlite3
from typing import Optional, Dict
from datetime import datetime, timedelta

class SessionManager:
    """
    Manage conversation sessions
    
    Responsibilities:
    - Track active conversations
    - Detect conversation boundaries (30-min idle)
    - Coordinate with Tier 1 FIFO queue
    - Session metadata (start, end, intent)
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def start_session(self, intent: str = None) -> str:
        """
        Start new conversation session
        
        Returns:
            conversation_id (UUID)
        """
        import uuid
        
        conversation_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO working_memory_conversations 
            (conversation_id, start_time, intent, status)
            VALUES (?, ?, ?, 'active')
        """, (conversation_id, datetime.now(), intent))
        
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def end_session(self, conversation_id: str):
        """End conversation session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE working_memory_conversations
            SET end_time = ?, status = 'completed'
            WHERE conversation_id = ?
        """, (datetime.now(), conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_active_session(self) -> Optional[str]:
        """
        Get active session if exists
        
        Returns None if:
        - No active session
        - Last activity >30 min ago (conversation boundary)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get most recent active conversation
        cursor.execute("""
            SELECT conversation_id, start_time
            FROM working_memory_conversations
            WHERE status = 'active'
            ORDER BY start_time DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        conversation_id, start_time = row
        
        # Check if conversation boundary reached (30 min idle)
        last_activity = self._get_last_activity_time(conversation_id)
        
        if datetime.now() - last_activity > timedelta(minutes=30):
            # Conversation boundary reached
            self.end_session(conversation_id)
            return None
        
        return conversation_id
    
    def _get_last_activity_time(self, conversation_id: str) -> datetime:
        """Get timestamp of last message in conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(timestamp)
            FROM working_memory_messages
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        if result:
            return datetime.fromisoformat(result)
        
        # No messages yet, use conversation start time
        return datetime.now()
```

**Success Criteria:**
- [ ] Sessions start/end correctly
- [ ] 30-min idle detection works
- [ ] Active session retrieval works
- [ ] Integration with Tier 1

---

### Task 5: Context Injection Engine
**File:** `CORTEX/src/context_injector.py`  
**Duration:** 1 hour  
**Tests:** 4 unit tests

**Description:**
Inject relevant context from Tiers 1-3 into workflows.

**Implementation Details:**
```python
from typing import Dict, List
from tier1.working_memory_engine import WorkingMemoryEngine
from tier2.knowledge_graph_engine import KnowledgeGraphEngine
from tier3.dev_context_engine import DevContextEngine

class ContextInjector:
    """
    Inject context from Tiers 1-3 into workflows
    
    Performance: <200ms total
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.wm_engine = WorkingMemoryEngine(db_path)
        self.kg_engine = KnowledgeGraphEngine(db_path)
        self.dc_engine = DevContextEngine(db_path)
    
    def inject_context(self, user_request: str, 
                      conversation_id: str = None,
                      include_tiers: Dict[str, bool] = None) -> Dict:
        """
        Inject context from specified tiers
        
        Args:
            user_request: User's request text
            conversation_id: Current conversation (if exists)
            include_tiers: {'tier1': True, 'tier2': True, 'tier3': True}
        
        Returns:
            {
                'tier1': {...},  # Recent conversations + entities
                'tier2': {...},  # Patterns
                'tier3': {...}   # Dev activity
            }
        """
        import time
        start = time.perf_counter()
        
        if include_tiers is None:
            include_tiers = {'tier1': True, 'tier2': True, 'tier3': True}
        
        context = {}
        
        # Tier 1: Working Memory
        if include_tiers.get('tier1'):
            context['tier1'] = self._inject_tier1(conversation_id)
        
        # Tier 2: Knowledge Graph
        if include_tiers.get('tier2'):
            context['tier2'] = self._inject_tier2(user_request)
        
        # Tier 3: Development Context
        if include_tiers.get('tier3'):
            context['tier3'] = self._inject_tier3()
        
        elapsed = (time.perf_counter() - start) * 1000
        context['injection_time_ms'] = elapsed
        
        return context
    
    def _inject_tier1(self, conversation_id: str = None) -> Dict:
        """Inject Tier 1: Recent conversations + entities"""
        tier1_context = {}
        
        # Current conversation
        if conversation_id:
            tier1_context['current_conversation'] = \
                self.wm_engine.get_conversation(conversation_id)
        
        # Recent entities (files, components, rules mentioned)
        tier1_context['recent_entities'] = \
            self.wm_engine.extract_entities_from_recent(limit=20)
        
        # Recent conversations (summary)
        tier1_context['recent_conversations'] = \
            self.wm_engine.get_recent_conversations(limit=5)
        
        return tier1_context
    
    def _inject_tier2(self, user_request: str) -> Dict:
        """Inject Tier 2: Relevant patterns"""
        tier2_context = {}
        
        # Search for relevant patterns
        tier2_context['patterns'] = \
            self.kg_engine.search_patterns(user_request, limit=5)
        
        # Intent patterns
        tier2_context['intent_patterns'] = \
            self.kg_engine.get_intent_patterns(user_request)
        
        # Workflow patterns
        tier2_context['workflow_patterns'] = \
            self.kg_engine.get_workflow_patterns(min_confidence=0.7)
        
        return tier2_context
    
    def _inject_tier3(self) -> Dict:
        """Inject Tier 3: Recent dev activity"""
        tier3_context = {}
        
        # Recent activity (24 hours)
        tier3_context['recent_activity'] = \
            self.dc_engine.get_recent_activity(hours=24)
        
        # Active files (48 hours)
        tier3_context['active_files'] = \
            self.dc_engine.get_active_files(hours=48)
        
        # Performance trends
        tier3_context['performance_trends'] = \
            self.dc_engine.get_performance_trends(days=7)
        
        return tier3_context
```

**Success Criteria:**
- [ ] Context injection <200ms
- [ ] All tiers injected correctly
- [ ] Selective tier inclusion works
- [ ] Context relevant to request

---

### Task 6: Integration & Documentation
**File:** Various  
**Duration:** 1 hour  
**Tests:** None (documentation)

**Description:**
Integration testing and documentation.

**Deliverables:**
1. **User Guide:** `CORTEX/docs/user-guide.md`
2. **Workflow Guide:** `CORTEX/docs/workflow-guide.md`
3. **Developer Guide:** `CORTEX/docs/developer-guide.md`
4. **Integration Tests:** Run all 7 integration tests

---

## 📋 Test Plan (22 Unit + 7 Integration = 29 Total)

### Unit Tests (22 tests)

**CortexRouter (4 tests):**
- [ ] `test_process_request()` - Request processing works
- [ ] `test_intent_detection()` - Intent detected via Phase 4
- [ ] `test_context_injection()` - Context injected <200ms
- [ ] `test_conversation_logging()` - Logged to Tier 1

**TDDWorkflow (5 tests):**
- [ ] `test_red_phase()` - RED phase creates failing test
- [ ] `test_green_phase()` - GREEN phase passes test
- [ ] `test_refactor_phase()` - REFACTOR phase improves code
- [ ] `test_complete_cycle()` - Full cycle works
- [ ] `test_dod_validation()` - DoD enforced

**FeatureCreationWorkflow (5 tests):**
- [ ] `test_plan_creation()` - Plans created via work-planner
- [ ] `test_phase_execution()` - Phases executed with TDD
- [ ] `test_context_usage()` - Context used in planning
- [ ] `test_feature_validation()` - Feature validated
- [ ] `test_multi_phase_coordination()` - Multiple phases coordinated

**SessionManager (4 tests):**
- [ ] `test_start_session()` - Sessions started
- [ ] `test_end_session()` - Sessions ended
- [ ] `test_conversation_boundary()` - 30-min idle detected
- [ ] `test_active_session_retrieval()` - Active session retrieved

**ContextInjector (4 tests):**
- [ ] `test_inject_all_tiers()` - All tiers injected
- [ ] `test_selective_injection()` - Selective tiers work
- [ ] `test_injection_performance()` - <200ms achieved
- [ ] `test_context_relevance()` - Context relevant

### Integration Tests (7 tests)

**End-to-End Workflows:**
- [ ] `test_cortex_md_to_execution()` - cortex.md → workflow → execution
- [ ] `test_tdd_workflow_complete()` - Full TDD cycle with agents
- [ ] `test_feature_creation_complete()` - Full feature creation
- [ ] `test_context_injection_all_tiers()` - Context from all 3 tiers
- [ ] `test_session_management()` - Session boundaries work
- [ ] `test_intent_routing_accuracy()` - Intent detection accurate
- [ ] `test_performance_targets()` - <100ms routing, <200ms context

---

## ⚡ Performance Benchmarks

```python
def test_routing_performance():
    """Ensure routing meets <100ms target"""
    import time
    
    router = CortexRouter()
    
    start = time.perf_counter()
    result = router.process_request(
        "Create a plan for adding authentication",
        conversation_id=None
    )
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 100, f"Routing took {elapsed}ms (target: <100ms)"

def test_context_injection_performance():
    """Ensure context injection meets <200ms target"""
    import time
    
    injector = ContextInjector()
    
    start = time.perf_counter()
    context = injector.inject_context(
        "Implement login form",
        conversation_id=None
    )
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 200, f"Context injection took {elapsed}ms (target: <200ms)"

def test_end_to_end_performance():
    """Ensure complete routing + context <300ms"""
    import time
    
    router = CortexRouter()
    
    start = time.perf_counter()
    result = router.process_request("Add purple button")
    elapsed = (time.perf_counter() - start) * 1000
    
    assert result['routing_time_ms'] < 300, \
        f"End-to-end took {result['routing_time_ms']}ms (target: <300ms)"
```

**Targets:**
- Intent routing: <100ms
- Context injection: <200ms
- Total (routing + context): <300ms

---

## 🎯 Success Criteria

**Phase 5 complete when:**
- ✅ All 22 unit tests passing
- ✅ All 7 integration tests passing
- ✅ `cortex.md` created and functional
- ✅ Intent routing <100ms
- ✅ Context injection <200ms
- ✅ TDD workflow enforces Rule #5
- ✅ Feature workflow creates plans
- ✅ Session management works (Rule #11)
- ✅ Integration with Phases 0-4 validated
- ✅ Documentation complete
- ✅ **Holistic review passed** ⚠️ MANDATORY

---

## 📖 Documentation Deliverables

1. **User Guide:** `CORTEX/docs/user-guide.md` (how to use cortex.md)
2. **Workflow Guide:** `CORTEX/docs/workflow-guide.md` (TDD, feature creation, bug fix)
3. **Developer Guide:** `CORTEX/docs/developer-guide.md` (extending workflows)
4. **API Reference:** `CORTEX/docs/api-reference.md` (router, workflows, injector)

---

## 🔍 MANDATORY: Holistic Review (Phase 5 Complete)

**⚠️ DO NOT PROCEED TO PHASE 6 UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase 5 Section

#### 1. Design Alignment ✅
- [ ] Does entry point match kds.md pattern?
- [ ] Are workflows following best practices?
- [ ] Is TDD enforced per Rule #5?
- [ ] Is session management per Rule #11?
- [ ] Does context injection use all tiers?

#### 2. Implementation Quality ✅
- [ ] All 22 unit tests passing?
- [ ] All 7 integration tests passing?
- [ ] Code follows Python best practices?
- [ ] Type hints used consistently?
- [ ] Error handling comprehensive?

#### 3. Performance Validation ✅
- [ ] Routing <100ms achieved?
- [ ] Context injection <200ms achieved?
- [ ] Total <300ms achieved?

#### 4. Integration with Previous Phases ✅
- [ ] Phase 0 rules enforced?
- [ ] Phase 1 conversations accessible?
- [ ] Phase 2 patterns used?
- [ ] Phase 3 metrics used?
- [ ] Phase 4 agents coordinated?

#### 5. Integration Readiness for Next Phase ✅
- [ ] Phase 6 can validate KDS → CORTEX migration?
- [ ] Entry point ready for production use?
- [ ] No blocking issues?

#### 6. Adjustments Needed
- [ ] Should more workflows be added?
- [ ] Should context injection be optimized?
- [ ] Should session management be enhanced?

### Review Output Document
**Create:** `cortex-design/reviews/phase-5-review.md`

### Success Metrics for Phase 5
- ✅ All tests passing (29 total)
- ✅ All benchmarks met (<100ms, <200ms, <300ms)
- ✅ Entry point functional
- ✅ Workflows orchestrated correctly
- ✅ Review report created and approved
- ✅ Phase 6 plan updated with learnings

---

## 📊 Phase Timeline

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|------------|
| 1 | Task 1 (Entry Point) + Task 2 (TDD Workflow) | 3.5 | 3.5 |
| 2 | Task 3 (Feature Workflow) + Task 4 (Session Mgr) | 3.5 | 7 |
| 3 | Task 5 (Context Injector) + Task 6 (Integration) | 2 | 9 |
| 4 | **Holistic Review** + Adjustments | 1.5 | 10.5 |

**Total Estimated:** 6-8 hours implementation + 1 hour review + 1.5 hours adjustments = 8.5-10.5 hours

---

## ✅ Phase Completion Checklist

**Implementation:**
- [ ] All tasks complete
- [ ] All 22 unit tests written and passing
- [ ] All 7 integration tests written and passing
- [ ] All benchmarks met
- [ ] Documentation written
- [ ] Code reviewed

**Review:**
- [ ] Holistic review checklist completed
- [ ] Review report written
- [ ] Issues documented
- [ ] Adjustments (if any) implemented
- [ ] Phase 6 plan updated

**Commit:**
- [ ] Implementation committed
- [ ] Review report committed
- [ ] Updated plans committed

**Proceed:**
- [ ] Review status is PASS ✅
- [ ] Team notified of completion
- [ ] Phase 6 ready to start

---

**Status:** Ready for implementation  
**Next:** Phase 6 (Migration Validation)  
**Estimated Completion:** 8.5-10.5 hours  
**⚠️ CRITICAL:** Complete holistic review before Phase 6!

---

## 🔗 Related Documents

- `HOLISTIC-REVIEW-PROTOCOL.md` - Complete review process
- `phase-4-agents.md` - Previous phase
- `phase-6-migration-validation.md` - Next phase
- `DESIGN-IMPROVEMENTS-SUMMARY.md` - Architecture decisions
- `unified-database-schema.sql` - Database schema
- `CORTEX-DNA.md` - Core design principles
- `WHY-CORTEX-IS-BETTER.md` - Rationale
