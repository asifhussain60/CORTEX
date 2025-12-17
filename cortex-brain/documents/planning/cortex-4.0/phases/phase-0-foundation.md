# 📦 CORTEX 4.0 - Phase 0: Foundation

**Duration:** 2 weeks (Week 1-2)  
**Goal:** Set up CORTEX 4.0 infrastructure  
**Status:** ⏳ Not Started

---

## 🎯 Objectives

1. Create clean `CORTEX-4.0` branch
2. Implement core engine (`cortex_core/`)
3. Set up MCP server scaffolding
4. Implement LLM intent router
5. Create testing infrastructure
6. Set up deployment scaffolding

---

## 📋 Task Breakdown

### Week 1: Core Infrastructure

#### Day 1-2: Branch Setup & Directory Structure

**Tasks:**
- [ ] Create `CORTEX-4.0` branch from `main`
- [ ] Initialize clean directory structure (see folder tree)
- [ ] Create `.gitignore` for new structure
- [ ] Set up `.editorconfig` for consistent formatting
- [ ] Create initial `README.md` for 4.0

**Deliverables:**
- Empty folder structure (as per master plan)
- Branch created and pushed
- Documentation stubs

**Validation:**
```bash
# Verify structure
tree cortex-4.0/ -L 2

# Check branch
git branch --show-current  # Should show: CORTEX-4.0
```

---

#### Day 3-4: Brain Engine Implementation

**File:** `cortex_core/brain/brain_engine.py`

**Tasks:**
- [ ] Implement unified brain API
- [ ] Integrate 4 tiers (Tier 0-3)
- [ ] Add team brain support
- [ ] Create brain initialization logic
- [ ] Implement query/store methods

**Code Structure:**

```python
# cortex_core/brain/brain_engine.py

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class BrainContext:
    """Context retrieved from brain."""
    tier0_rules: Dict[str, Any]      # Governance rules
    tier1_conversations: List[Dict]   # Recent conversations
    tier2_patterns: List[Dict]        # Knowledge patterns
    tier3_metrics: Dict[str, Any]     # Dev metrics
    team_knowledge: Optional[Dict]    # Team-shared knowledge

class BrainEngine:
    """
    Unified brain API for CORTEX 4.0.
    
    Provides single interface to all 4 tiers + team brain.
    """
    
    def __init__(self, brain_root: Path, team_id: Optional[str] = None):
        self.brain_root = brain_root
        self.team_id = team_id
        
        # Initialize tier handlers
        self.tier0 = Tier0Handler(brain_root / "tier0")
        self.tier1 = Tier1Handler(brain_root / "tier1")
        self.tier2 = Tier2Handler(brain_root / "tier2")
        self.tier3 = Tier3Handler(brain_root / "tier3")
        
        # Team brain (optional)
        if team_id:
            self.team = TeamBrainHandler(brain_root / "team", team_id)
    
    def get_context(
        self,
        conversation_id: Optional[str] = None,
        include_patterns: bool = True,
        include_metrics: bool = False,
        include_team: bool = False
    ) -> BrainContext:
        """
        Get unified context from brain.
        
        Args:
            conversation_id: Current conversation ID
            include_patterns: Include Tier 2 patterns
            include_metrics: Include Tier 3 metrics
            include_team: Include team knowledge
            
        Returns:
            BrainContext with requested data
        """
        context = BrainContext(
            tier0_rules=self.tier0.get_active_rules(),
            tier1_conversations=[],
            tier2_patterns=[],
            tier3_metrics={},
            team_knowledge=None
        )
        
        # Load conversation history
        if conversation_id:
            context.tier1_conversations = self.tier1.get_recent(
                conversation_id,
                limit=10
            )
        
        # Load patterns
        if include_patterns:
            context.tier2_patterns = self.tier2.get_patterns()
        
        # Load metrics
        if include_metrics:
            context.tier3_metrics = self.tier3.get_metrics()
        
        # Load team knowledge
        if include_team and self.team:
            context.team_knowledge = self.team.get_shared_knowledge()
        
        return context
    
    def store_conversation(
        self,
        conversation_id: str,
        message: Dict[str, Any]
    ):
        """Store conversation message in Tier 1."""
        self.tier1.store(conversation_id, message)
    
    def learn_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        share_with_team: bool = False
    ):
        """
        Learn new pattern (Tier 2).
        
        Args:
            pattern_type: Type of pattern (e.g., "tdd_success")
            pattern_data: Pattern details
            share_with_team: Share with team brain
        """
        self.tier2.add_pattern(pattern_type, pattern_data)
        
        if share_with_team and self.team:
            self.team.share_pattern(pattern_type, pattern_data)
    
    def update_metrics(
        self,
        metric_type: str,
        value: Any
    ):
        """Update Tier 3 metrics."""
        self.tier3.update(metric_type, value)
    
    def validate_against_skull(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate operation against SKULL rules (Tier 0).
        
        Returns:
            (is_valid, error_message)
        """
        return self.tier0.validate(operation, context)
```

**Tests:**

```python
# tests/unit/brain/test_brain_engine.py

import pytest
from pathlib import Path
from cortex_core.brain import BrainEngine

class TestBrainEngine:
    
    @pytest.fixture
    def brain_root(self, tmp_path):
        return tmp_path / "brain"
    
    @pytest.fixture
    def brain(self, brain_root):
        return BrainEngine(brain_root)
    
    def test_initialization(self, brain):
        """Test brain engine initializes correctly."""
        assert brain.tier0 is not None
        assert brain.tier1 is not None
        assert brain.tier2 is not None
        assert brain.tier3 is not None
    
    def test_get_context_minimal(self, brain):
        """Test getting minimal context."""
        context = brain.get_context()
        
        assert context.tier0_rules is not None
        assert isinstance(context.tier1_conversations, list)
        assert isinstance(context.tier2_patterns, list)
    
    def test_store_conversation(self, brain):
        """Test storing conversation message."""
        brain.store_conversation(
            "conv-123",
            {"role": "user", "content": "test"}
        )
        
        context = brain.get_context(conversation_id="conv-123")
        assert len(context.tier1_conversations) == 1
    
    def test_learn_pattern(self, brain):
        """Test pattern learning."""
        brain.learn_pattern(
            "tdd_success",
            {"test_count": 10, "coverage": 100}
        )
        
        context = brain.get_context(include_patterns=True)
        assert len(context.tier2_patterns) > 0
    
    def test_skull_validation(self, brain):
        """Test SKULL rule validation."""
        is_valid, error = brain.validate_against_skull(
            "tdd_skip_red_phase",
            {"reason": "test"}
        )
        
        assert not is_valid
        assert "RED phase" in error
```

**Validation:**
```bash
pytest tests/unit/brain/ -v --cov=cortex_core/brain
# Should show 100% coverage
```

---

#### Day 5: Event Bus & Service Container

**File:** `cortex_core/events/event_bus.py`

**Tasks:**
- [ ] Implement pub/sub event bus
- [ ] Add event type definitions
- [ ] Create subscription management
- [ ] Add event filtering

**Code:**

```python
# cortex_core/events/event_bus.py

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
import asyncio
from enum import Enum

class EventType(Enum):
    """Standard event types."""
    PLANNING_STARTED = "planning.started"
    PLANNING_COMPLETED = "planning.completed"
    TDD_PHASE_CHANGE = "tdd.phase_change"
    TDD_TESTS_PASSED = "tdd.tests_passed"
    MAINTENANCE_STARTED = "maintenance.started"
    ORCHESTRATOR_ERROR = "orchestrator.error"

@dataclass
class Event:
    """Event data structure."""
    type: str
    data: Dict[str, Any]
    source: str
    timestamp: float

class EventBus:
    """
    Pub/sub event bus for orchestrator communication.
    
    Enables loose coupling between orchestrators.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue = asyncio.Queue()
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to events.
        
        Args:
            event_type: Event type to subscribe to
            handler: Callback function
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from events."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
    
    async def emit(self, event_type: str, data: Dict[str, Any], source: str):
        """
        Emit event to subscribers.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Event source (orchestrator name)
        """
        event = Event(
            type=event_type,
            data=data,
            source=source,
            timestamp=asyncio.get_event_loop().time()
        )
        
        # Notify subscribers
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def emit_sync(self, event_type: str, data: Dict[str, Any], source: str):
        """Synchronous emit (for non-async contexts)."""
        asyncio.create_task(self.emit(event_type, data, source))
```

**File:** `cortex_core/orchestrators/service_container.py`

```python
# cortex_core/orchestrators/service_container.py

from typing import Dict, Any, Callable, Optional

class ServiceContainer:
    """
    Dependency injection container.
    
    Manages service lifetimes and dependencies.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, name: str, instance: Any):
        """Register service instance."""
        self._services[name] = instance
    
    def register_factory(self, name: str, factory: Callable):
        """Register service factory (creates on demand)."""
        self._factories[name] = factory
    
    def register_singleton(self, name: str, factory: Callable):
        """Register singleton service (created once)."""
        self._factories[name] = factory
        self._singletons[name] = None
    
    def get(self, name: str) -> Optional[Any]:
        """Get service by name."""
        # Check direct registration
        if name in self._services:
            return self._services[name]
        
        # Check singleton
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name](self)
            return self._singletons[name]
        
        # Check factory
        if name in self._factories:
            return self._factories[name](self)
        
        raise KeyError(f"Service '{name}' not registered")
    
    def has(self, name: str) -> bool:
        """Check if service exists."""
        return (name in self._services or 
                name in self._factories or 
                name in self._singletons)
```

**Tests:**

```python
# tests/unit/events/test_event_bus.py

import pytest
import asyncio
from cortex_core.events import EventBus, EventType

@pytest.mark.asyncio
async def test_event_bus_subscribe_emit():
    """Test basic pub/sub."""
    bus = EventBus()
    received = []
    
    def handler(event):
        received.append(event)
    
    bus.subscribe(EventType.PLANNING_STARTED.value, handler)
    await bus.emit(EventType.PLANNING_STARTED.value, {"test": True}, "test")
    
    await asyncio.sleep(0.1)  # Allow event to propagate
    assert len(received) == 1
    assert received[0].data["test"] is True
```

**Validation:**
```bash
pytest tests/unit/events/ -v --cov=cortex_core/events
pytest tests/unit/orchestrators/test_service_container.py -v
```

---

### Week 2: MCP Server & Testing

#### Day 1-2: MCP Server Implementation

**File:** `cortex_core/mcp/server.py`

**Tasks:**
- [ ] Implement MCP server core
- [ ] Add protocol handlers
- [ ] Create tool registry
- [ ] Add JSON Schema validation

**Code:**

```python
# cortex_core/mcp/server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Dict, Any, List
import asyncio

class CortexMCPServer:
    """
    MCP server for CORTEX 4.0.
    
    Exposes all orchestrators as MCP tools.
    """
    
    def __init__(self, container):
        self.server = Server("cortex-4.0")
        self.container = container
        self._tools: Dict[str, Any] = {}
        
        # Register core handlers
        self.server.set_request_handler("list_tools", self.list_tools)
        self.server.set_request_handler("call_tool", self.call_tool)
    
    def register_tool(self, tool: Tool):
        """Register MCP tool."""
        self._tools[tool.name] = tool
    
    async def list_tools(self) -> List[Tool]:
        """List all available tools."""
        return list(self._tools.values())
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """
        Execute tool.
        
        Args:
            name: Tool name (e.g., "cortex_plan")
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        
        tool = self._tools[name]
        orchestrator_name = tool.metadata.get("orchestrator")
        
        # Get orchestrator from container
        orchestrator = self.container.get(orchestrator_name)
        
        # Execute
        result = await orchestrator.execute(arguments)
        
        return TextContent(
            type="text",
            text=result.get("output", "")
        )
    
    async def start(self, host: str = "localhost", port: int = 5000):
        """Start MCP server."""
        await self.server.run(host, port)
```

**Validation:**
```bash
# Start server
python -m cortex_core.mcp.server

# Test with MCP client
mcp-client --server http://localhost:5000 list-tools
```

---

#### Day 3-4: LLM Intent Router

**File:** `cortex_core/intent/llm_router.py`

**Tasks:**
- [ ] Implement LLM-based intent classification
- [ ] Add local model integration (Llama 3.2 1B)
- [ ] Create keyword fallback
- [ ] Add confidence scoring

**Code:**

```python
# cortex_core/intent/llm_router.py

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Intent:
    """Classified user intent."""
    orchestrator: str
    confidence: float
    parameters: Dict[str, Any]
    clarification_needed: bool = False

class LLMIntentRouter:
    """
    LLM-powered intent classification.
    
    Replaces keyword matching with natural language understanding.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or self._default_model_path()
        self.llm = self._load_model()
        self.keyword_fallback = KeywordFallback()
    
    def _load_model(self):
        """Load local LLM (Llama 3.2 1B)."""
        try:
            from llama_cpp import Llama
            return Llama(
                model_path=str(self.model_path),
                n_ctx=2048,
                n_threads=4
            )
        except ImportError:
            print("Warning: llama-cpp-python not installed. Using keyword fallback.")
            return None
    
    async def classify(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Classify user intent.
        
        Args:
            user_request: Natural language request
            context: Conversation context (optional)
            
        Returns:
            Intent with orchestrator, confidence, parameters
        """
        # Fallback if LLM unavailable
        if self.llm is None:
            return self.keyword_fallback.classify(user_request)
        
        # Build classification prompt
        prompt = self._build_prompt(user_request, context)
        
        # Query LLM
        response = self.llm(
            prompt,
            max_tokens=100,
            temperature=0.1,
            stop=["###"]
        )
        
        # Parse response
        intent = self._parse_response(response["choices"][0]["text"])
        
        # Validate confidence
        if intent.confidence < 0.7:
            intent.clarification_needed = True
        
        return intent
    
    def _build_prompt(self, request: str, context: Optional[Dict]) -> str:
        """Build classification prompt."""
        return f"""Classify the user's request into one of these orchestrators:

Orchestrators:
- planning: Feature planning, requirements analysis
- tdd: Test-driven development, testing
- ado: Azure DevOps work items (story, feature, task)
- maintenance: System maintenance, health checks
- sanitization: Code sanitization, removing sensitive data
- review: Architecture review, code review
- refinement: System refinement, code quality

User Request: {request}

Context: {context or "None"}

Classification (format: orchestrator|confidence|parameters):
"""
    
    def _parse_response(self, response: str) -> Intent:
        """Parse LLM response into Intent."""
        parts = response.strip().split("|")
        
        return Intent(
            orchestrator=parts[0].strip(),
            confidence=float(parts[1].strip()),
            parameters=eval(parts[2].strip()) if len(parts) > 2 else {}
        )
```

**Tests:**

```python
# tests/unit/intent/test_llm_router.py

import pytest
from cortex_core.intent import LLMIntentRouter

@pytest.mark.asyncio
async def test_classify_planning():
    """Test planning intent classification."""
    router = LLMIntentRouter()
    
    intent = await router.classify("I need to plan an authentication feature")
    
    assert intent.orchestrator == "planning"
    assert intent.confidence > 0.7

@pytest.mark.asyncio
async def test_classify_tdd():
    """Test TDD intent classification."""
    router = LLMIntentRouter()
    
    intent = await router.classify("Let's start TDD for the login module")
    
    assert intent.orchestrator == "tdd"
    assert intent.confidence > 0.7
```

**Validation:**
```bash
pytest tests/unit/intent/ -v --cov=cortex_core/intent
```

---

#### Day 5: Testing Infrastructure & CI/CD

**Tasks:**
- [ ] Set up pytest configuration
- [ ] Configure coverage reporting
- [ ] Create GitHub Actions CI pipeline
- [ ] Add pre-commit hooks

**Files:**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=cortex_core
    --cov=cortex_orchestrators
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=100
```

```yaml
# .github/workflows/ci.yml
name: CORTEX 4.0 CI

on:
  push:
    branches: [CORTEX-4.0]
  pull_request:
    branches: [CORTEX-4.0]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: pytest
      
      - name: Upload coverage
        if: matrix.python-version == '3.11'
        uses: codecov/codecov-action@v3
```

**Validation:**
```bash
# Local test
pytest

# Check coverage
pytest --cov-report=html
open htmlcov/index.html
```

---

## 📊 Phase 0 Completion Checklist

### Week 1
- [ ] Branch created (`CORTEX-4.0`)
- [ ] Directory structure initialized
- [ ] Brain engine implemented (100% coverage)
- [ ] Event bus implemented (100% coverage)
- [ ] Service container implemented (100% coverage)

### Week 2
- [ ] MCP server implemented (100% coverage)
- [ ] LLM intent router implemented (100% coverage)
- [ ] Testing infrastructure configured
- [ ] CI/CD pipeline working
- [ ] All tests passing

### Validation
- [ ] Brain engine operational (all 4 tiers accessible)
- [ ] Event bus working (pub/sub verified)
- [ ] Service container functional (DI tested)
- [ ] MCP server starts successfully
- [ ] LLM intent router classifies requests
- [ ] CI pipeline green (all Python versions)
- [ ] Test coverage 100%

---

## 📈 Metrics

**Expected Metrics:**
- Lines of code: ~2000 LOC
- Test coverage: 100%
- CI build time: <5 minutes
- Tests passing: 100%

**Files Created:**
- `cortex_core/` - 15 files
- `tests/` - 20 test files
- CI/CD configs - 3 files

---

## 🔄 Next Phase

**Phase 1.1: TDD Orchestrator** (Week 3)

After Phase 0 completion:
1. Foundation is stable
2. All core services available
3. Ready to migrate first orchestrator

