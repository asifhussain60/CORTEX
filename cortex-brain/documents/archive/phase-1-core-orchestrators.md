# 🎭 CORTEX 4.0 - Phase 1: Core Orchestrators

**Duration:** 4 weeks (Week 3-6)  
**Goal:** Migrate 4 critical orchestrators with 100% test coverage  
**Status:** ⏳ Not Started

---

## 📊 Overview

| Week | Orchestrator | Priority | Complexity | Expected LOC | Tests |
|------|--------------|----------|------------|--------------|-------|
| 3 | TDD | P0-1 | Medium | 600 | 12 |
| 4 | Planning | P0-2 | High | 800 | 15 |
| 5 | ADO | P0-3 | Low | 400 | 10 |
| 6 | Maintenance | P0-4 | Medium | 700 | 20 |

**Total:** 2500 LOC, 57 tests, 100% coverage requirement

---

## 🔴 Week 3: TDD Orchestrator (P0-1)

### Why First?
- Foundation for all other orchestrators
- Validates testing infrastructure
- Sets quality bar for remaining migrations

### Current Location
`src/workflows/tdd_workflow_orchestrator.py`

### Dependencies
- Test runner utility
- Coverage reporter
- Metrics collector
- Brain engine (Tier 1, Tier 3)

---

### Day 1: Analysis & Planning

**Tasks:**
- [ ] Map current TDD orchestrator functionality
- [ ] Document all entry points
- [ ] Identify dependencies
- [ ] Create test plan (RED→GREEN→REFACTOR validation)
- [ ] Document coverage gaps

**Deliverables:**
- Analysis report: `TDD-MIGRATION-ANALYSIS.md`
- Test plan: `TDD-TEST-STRATEGY.md`
- Dependency graph

**Time:** 6-8 hours

---

### Day 2-3: Core Logic Migration

**Target Structure:**

```
cortex_orchestrators/tdd/
├── __init__.py
├── tdd_orchestrator.py          # Main orchestrator (200 LOC)
├── phases/
│   ├── __init__.py
│   ├── red_phase.py             # RED: Write failing tests (100 LOC)
│   ├── green_phase.py           # GREEN: Make tests pass (100 LOC)
│   └── refactor_phase.py        # REFACTOR: Improve code (100 LOC)
├── validators/
│   ├── __init__.py
│   ├── coverage_validator.py   # Per-layer coverage (50 LOC)
│   └── empty_test_detector.py  # Detect placeholder tests (50 LOC)
└── tests/
    ├── __init__.py
    ├── test_tdd_orchestrator.py
    ├── test_red_phase.py
    ├── test_green_phase.py
    ├── test_refactor_phase.py
    ├── test_coverage_validator.py
    └── fixtures/
```

**Key Implementation:**

```python
# cortex_orchestrators/tdd/tdd_orchestrator.py

from cortex_core.orchestrators import BaseOrchestrator
from cortex_core.mcp import MCPTool
from .phases import RedPhase, GreenPhase, RefactorPhase

class TDDOrchestrator(BaseOrchestrator):
    """
    TDD Mastery orchestrator for CORTEX 4.0.
    
    Enforces RED→GREEN→REFACTOR workflow with validation.
    """
    
    def __init__(self, container):
        super().__init__(container)
        
        # Get dependencies from container
        self.test_runner = container.get('test_runner')
        self.coverage_reporter = container.get('coverage_reporter')
        
        # Initialize phases
        self.red_phase = RedPhase(container)
        self.green_phase = GreenPhase(container)
        self.refactor_phase = RefactorPhase(container)
        
        # Current phase tracking
        self.current_phase = "RED"
        self.session_id = None
    
    def get_dependencies(self) -> list[str]:
        return [
            'brain_engine',
            'test_runner',
            'coverage_reporter',
            'event_bus',
            'logger'
        ]
    
    def get_mcp_tools(self) -> list[MCPTool]:
        return [
            MCPTool(
                name="cortex_tdd_start",
                description="Start TDD workflow (RED phase)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["module", "description"]
                },
                metadata={"orchestrator": "tdd_orchestrator"}
            ),
            MCPTool(
                name="cortex_tdd_validate",
                description="Validate TDD compliance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"}
                    },
                    "required": ["session_id"]
                },
                metadata={"orchestrator": "tdd_orchestrator"}
            ),
            MCPTool(
                name="cortex_tdd_status",
                description="Get current TDD phase status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"}
                    },
                    "required": ["session_id"]
                },
                metadata={"orchestrator": "tdd_orchestrator"}
            )
        ]
    
    async def execute(self, request: dict) -> dict:
        """
        Execute TDD workflow.
        
        Args:
            request: {
                "command": "start" | "validate" | "status",
                "module": str,
                "description": str
            }
        """
        command = request.get("command", "start")
        
        if command == "start":
            return await self._start_tdd(request)
        elif command == "validate":
            return await self._validate_compliance(request)
        elif command == "status":
            return await self._get_status(request)
        else:
            raise ValueError(f"Unknown command: {command}")
    
    async def _start_tdd(self, request: dict) -> dict:
        """Start TDD workflow (RED phase)."""
        module = request["module"]
        description = request["description"]
        
        # Emit event
        await self.event_bus.emit(
            "tdd.started",
            {"module": module, "phase": "RED"},
            "tdd_orchestrator"
        )
        
        # Execute RED phase
        result = await self.red_phase.execute({
            "module": module,
            "description": description
        })
        
        # Store in brain
        self.brain.store_conversation(
            self.session_id,
            {
                "phase": "RED",
                "module": module,
                "result": result
            }
        )
        
        return result
    
    async def _validate_compliance(self, request: dict) -> dict:
        """Validate TDD compliance."""
        # Check if RED phase was executed
        # Check if tests failed initially
        # Check if GREEN phase made tests pass
        # Check coverage requirements
        pass
```

**Tasks:**
- [ ] Implement `TDDOrchestrator` base class
- [ ] Implement RED phase (write failing tests)
- [ ] Implement GREEN phase (make tests pass)
- [ ] Implement REFACTOR phase (improve code)
- [ ] Implement coverage validator
- [ ] Implement empty test detector
- [ ] Add brain integration (Tier 1 for context, Tier 3 for metrics)
- [ ] Add event emission (phase transitions)

**Time:** 12-16 hours

---

### Day 3: Utility Extraction

**Target:**

```
cortex_tools/test_runner/
├── __init__.py
├── pytest_runner.py         # pytest integration (100 LOC)
├── coverage_reporter.py     # Coverage reporting (80 LOC)
├── test_discovery.py        # Test file discovery (50 LOC)
└── tests/
    ├── test_pytest_runner.py
    └── test_coverage_reporter.py
```

**Key Implementation:**

```python
# cortex_tools/test_runner/pytest_runner.py

from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import json

class PytestRunner:
    """
    pytest integration for CORTEX 4.0.
    
    Runs tests and collects results.
    """
    
    def run_tests(
        self,
        test_path: Path,
        coverage: bool = True,
        verbose: bool = False
    ) -> Dict:
        """
        Run pytest tests.
        
        Args:
            test_path: Path to test file or directory
            coverage: Collect coverage data
            verbose: Verbose output
            
        Returns:
            {
                "passed": int,
                "failed": int,
                "skipped": int,
                "total": int,
                "coverage": float (if coverage=True),
                "failures": List[Dict]
            }
        """
        cmd = ["pytest", str(test_path), "--json-report"]
        
        if coverage:
            cmd.extend(["--cov", "--cov-report=json"])
        
        if verbose:
            cmd.append("-v")
        
        # Run pytest
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        # Parse results
        return self._parse_results(result)
```

**Tasks:**
- [ ] Extract test runner to `cortex_tools/`
- [ ] Extract coverage reporter
- [ ] Write unit tests for utilities

**Time:** 4-6 hours

---

### Day 4-5: Testing

**Test Coverage Target:** 100%

**Test Structure:**

```python
# tests/unit/orchestrators/tdd/test_tdd_orchestrator.py

import pytest
from cortex_orchestrators.tdd import TDDOrchestrator
from cortex_core.orchestrators import ServiceContainer

class TestTDDOrchestrator:
    
    @pytest.fixture
    def container(self):
        container = ServiceContainer()
        container.register('brain_engine', MockBrain())
        container.register('test_runner', MockTestRunner())
        container.register('coverage_reporter', MockCoverageReporter())
        container.register('event_bus', MockEventBus())
        container.register('logger', MockLogger())
        return container
    
    @pytest.fixture
    def orchestrator(self, container):
        return TDDOrchestrator(container)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator.current_phase == "RED"
        assert orchestrator.red_phase is not None
        assert orchestrator.green_phase is not None
        assert orchestrator.refactor_phase is not None
    
    @pytest.mark.asyncio
    async def test_start_tdd_red_phase(self, orchestrator):
        """Test starting TDD workflow (RED phase)."""
        result = await orchestrator.execute({
            "command": "start",
            "module": "auth.login",
            "description": "User authentication"
        })
        
        assert result["phase"] == "RED"
        assert result["tests_created"] > 0
        assert result["tests_failed"] > 0  # Should fail initially
    
    @pytest.mark.asyncio
    async def test_red_to_green_transition(self, orchestrator):
        """Test RED→GREEN phase transition."""
        # Start RED
        await orchestrator.execute({
            "command": "start",
            "module": "auth.login",
            "description": "User authentication"
        })
        
        # Verify can't skip to REFACTOR
        with pytest.raises(ValueError, match="Must complete GREEN"):
            await orchestrator.execute({
                "command": "refactor",
                "session_id": orchestrator.session_id
            })
    
    @pytest.mark.asyncio
    async def test_tdd_compliance_validation(self, orchestrator):
        """Test TDD compliance validation."""
        # Complete RED→GREEN→REFACTOR
        session_id = await self._complete_cycle(orchestrator)
        
        # Validate compliance
        result = await orchestrator.execute({
            "command": "validate",
            "session_id": session_id
        })
        
        assert result["compliant"] is True
        assert result["coverage"] >= 80  # Per-layer coverage
    
    @pytest.mark.asyncio
    async def test_empty_test_detection(self, orchestrator):
        """Test detection of empty/placeholder tests."""
        # Create test with placeholder (pass)
        result = await orchestrator.execute({
            "command": "start",
            "module": "test_module",
            "description": "Test with placeholder"
        })
        
        # Should detect empty test
        assert "empty_tests_detected" in result
        assert result["empty_tests_detected"] > 0
    
    @pytest.mark.asyncio
    async def test_brain_integration(self, orchestrator, container):
        """Test brain stores TDD session data."""
        brain = container.get('brain_engine')
        
        await orchestrator.execute({
            "command": "start",
            "module": "test_module",
            "description": "Test brain integration"
        })
        
        # Verify stored in Tier 1 (conversation)
        context = brain.get_context(conversation_id=orchestrator.session_id)
        assert len(context.tier1_conversations) > 0
        assert context.tier1_conversations[0]["phase"] == "RED"
    
    @pytest.mark.asyncio
    async def test_event_emission(self, orchestrator, container):
        """Test orchestrator emits events."""
        event_bus = container.get('event_bus')
        events = []
        
        event_bus.subscribe("tdd.started", events.append)
        event_bus.subscribe("tdd.phase_change", events.append)
        
        await orchestrator.execute({
            "command": "start",
            "module": "test_module",
            "description": "Test events"
        })
        
        assert len(events) >= 1
        assert events[0].type == "tdd.started"
```

**Integration Tests:**

```python
# tests/integration/orchestrators/test_tdd_integration.py

import pytest
from pathlib import Path
from cortex_orchestrators.tdd import TDDOrchestrator
from cortex_core.brain import BrainEngine
from cortex_core.orchestrators import ServiceContainer

class TestTDDIntegration:
    
    @pytest.fixture
    def workspace(self, tmp_path):
        """Create temporary workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        return workspace
    
    @pytest.fixture
    def brain(self, tmp_path):
        """Create real brain engine."""
        brain_root = tmp_path / "brain"
        return BrainEngine(brain_root)
    
    @pytest.fixture
    def orchestrator(self, workspace, brain):
        """Create orchestrator with real dependencies."""
        container = ServiceContainer()
        container.register('brain_engine', brain)
        # ... register real services
        
        return TDDOrchestrator(container)
    
    @pytest.mark.asyncio
    async def test_full_tdd_cycle(self, orchestrator, workspace):
        """Test complete RED→GREEN→REFACTOR cycle."""
        # RED: Create failing tests
        red_result = await orchestrator.execute({
            "command": "start",
            "module": "calculator",
            "description": "Simple calculator with add/subtract"
        })
        
        assert red_result["phase"] == "RED"
        assert red_result["tests_failed"] > 0
        
        # GREEN: Make tests pass
        green_result = await orchestrator.execute({
            "command": "green",
            "session_id": orchestrator.session_id,
            "implementation": "def add(a, b): return a + b"
        })
        
        assert green_result["phase"] == "GREEN"
        assert green_result["tests_passed"] == green_result["tests_total"]
        
        # REFACTOR: Improve code
        refactor_result = await orchestrator.execute({
            "command": "refactor",
            "session_id": orchestrator.session_id
        })
        
        assert refactor_result["phase"] == "REFACTOR"
        assert refactor_result["tests_passed"] == refactor_result["tests_total"]
```

**E2E Tests:**

```python
# tests/e2e/test_tdd_workflow.py

import pytest
from cortex_core.mcp import CortexMCPServer

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_tdd_via_mcp(mcp_server: CortexMCPServer):
    """Test TDD workflow via MCP server."""
    # Call cortex_tdd_start
    result = await mcp_server.call_tool(
        "cortex_tdd_start",
        {
            "module": "user_auth",
            "description": "User authentication system"
        }
    )
    
    assert "RED" in result.text
    assert "tests created" in result.text
```

**Tasks:**
- [ ] Write unit tests (12 tests, 100% coverage)
- [ ] Write integration tests (3 tests)
- [ ] Write E2E tests (1 test)
- [ ] Validate all tests passing
- [ ] Verify 100% coverage

**Time:** 12-16 hours

---

### Day 5: MCP Integration & Documentation

**Tasks:**
- [ ] Implement MCP tool definitions
- [ ] Test MCP tools via server
- [ ] Write orchestrator README
- [ ] Document RED→GREEN→REFACTOR workflow
- [ ] Create usage examples

**MCP Tool Testing:**

```python
# tests/mcp/test_tdd_mcp_tools.py

import pytest
from cortex_core.mcp import CortexMCPServer

class TestTDDMCPTools:
    
    @pytest.fixture
    async def mcp_server(self, container):
        server = CortexMCPServer(container)
        await server.register_orchestrator('tdd_orchestrator')
        return server
    
    @pytest.mark.asyncio
    async def test_cortex_tdd_start_tool(self, mcp_server):
        """Test cortex_tdd_start MCP tool."""
        result = await mcp_server.call_tool(
            "cortex_tdd_start",
            {"module": "test", "description": "test"}
        )
        
        assert result.type == "text"
        assert "RED phase" in result.text
    
    @pytest.mark.asyncio
    async def test_cortex_tdd_validate_tool(self, mcp_server):
        """Test cortex_tdd_validate MCP tool."""
        # Start TDD first
        start_result = await mcp_server.call_tool(
            "cortex_tdd_start",
            {"module": "test", "description": "test"}
        )
        
        # Extract session_id from result
        session_id = self._extract_session_id(start_result.text)
        
        # Validate
        result = await mcp_server.call_tool(
            "cortex_tdd_validate",
            {"session_id": session_id}
        )
        
        assert "compliance" in result.text
```

**Documentation:**

```markdown
# TDD Orchestrator

## Overview

TDD Mastery orchestrator enforces RED→GREEN→REFACTOR workflow.

## Features

- ✅ RED phase: Write failing tests first
- ✅ GREEN phase: Make tests pass
- ✅ REFACTOR phase: Improve code quality
- ✅ Per-layer coverage validation (80% minimum)
- ✅ Empty test detection (no placeholders)
- ✅ Brain integration (context + metrics)

## Usage

### Via MCP

```python
# Start TDD workflow
await mcp.call_tool("cortex_tdd_start", {
    "module": "auth.login",
    "description": "User authentication"
})

# Validate compliance
await mcp.call_tool("cortex_tdd_validate", {
    "session_id": "session-123"
})
```

### Direct API

```python
from cortex_orchestrators.tdd import TDDOrchestrator

orchestrator = TDDOrchestrator(container)

result = await orchestrator.execute({
    "command": "start",
    "module": "auth.login",
    "description": "User authentication"
})
```

## Configuration

```yaml
# cortex.config.json
tdd:
  min_coverage_per_layer: 80
  detect_empty_tests: true
  enforce_red_phase: true
```

## Testing

100% test coverage maintained.

```bash
pytest tests/unit/orchestrators/tdd/ -v --cov
```
```

**Time:** 4-6 hours

---

### Week 3 Completion Checklist

- [ ] TDD orchestrator implemented (600 LOC)
- [ ] RED/GREEN/REFACTOR phases functional
- [ ] Coverage validator working (80% per-layer)
- [ ] Empty test detection functional
- [ ] Test runner utilities extracted
- [ ] Unit tests written (12 tests, 100% coverage)
- [ ] Integration tests written (3 tests)
- [ ] E2E tests written (1 test)
- [ ] MCP tools tested
- [ ] Documentation complete
- [ ] Brain integration working
- [ ] Event emission verified

### Validation

```bash
# Run all tests
pytest tests/unit/orchestrators/tdd/ -v

# Check coverage
pytest --cov=cortex_orchestrators/tdd --cov-report=html

# Test MCP tools
pytest tests/mcp/test_tdd_mcp_tools.py -v

# Integration test
pytest tests/integration/orchestrators/test_tdd_integration.py -v
```

**Expected Results:**
- Tests passing: 16/16 (100%)
- Coverage: 100%
- MCP tools: 3/3 working

---

## ✅ Week 4: Planning Orchestrator (P0-2)

[Detailed plan similar to Week 3 - deferred to separate file]

---

## ✅ Week 5: ADO Orchestrator (P0-3)

[Detailed plan - deferred to separate file]

---

## ✅ Week 6: Maintenance Orchestrator (P0-4)

[Detailed plan - deferred to separate file]

---

## 📊 Phase 1 Success Metrics

**Technical:**
- [ ] 4 orchestrators migrated (TDD, Planning, ADO, Maintenance)
- [ ] 2500 LOC written
- [ ] 57 tests written (100% coverage)
- [ ] All MCP tools functional (15 tools)
- [ ] Brain integration verified (all orchestrators)
- [ ] Event system working (orchestrator communication)

**Quality:**
- [ ] Zero P0 bugs
- [ ] CI/CD pipeline green (100% pass rate)
- [ ] Code review approved
- [ ] Documentation complete

**Timeline:**
- [ ] Week 3: TDD complete
- [ ] Week 4: Planning complete
- [ ] Week 5: ADO complete
- [ ] Week 6: Maintenance complete

---

## 🔄 Next Phase

**Phase 2: Enhancement Orchestrators** (Week 7-9)
- Sanitization
- Review
- Refinement

