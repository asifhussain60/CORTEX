# 🎯 CORTEX 4.0 - Master Migration & Enhancement Plan

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** December 17, 2025  
**Status:** 📋 READY FOR REVIEW  
**Branch Strategy:** `CORTEX-4.0` (clean rebuild, incremental migration)

---

## 📊 Executive Summary

**Problem:** CORTEX 3.0 is a "spaghetti mess" with unclear file organization, scattered orchestrators, constant unwiring/rewiring issues, and no deployment strategy.

**Solution:** Complete architectural rebuild with:
- ✅ **MCP-First Design** - All operations exposed via Model Context Protocol
- ✅ **Incremental Migration** - One orchestrator at a time, fully tested
- ✅ **Deployment-Ready** - PyPI, Docker, VS Code extension from day 1
- ✅ **Team-Level Operations** - Enhanced brain for team knowledge sharing
- ✅ **LLM-Based Intent** - Replace keyword matching with intelligent routing
- ✅ **Sustainable Architecture** - Built-once, no constant rewiring

**Timeline:** 12-14 weeks (1-2 orchestrators/week)  
**Risk:** Low-Medium (incremental, well-tested approach)  
**Dependencies:** CORTEX 5.0 deferred (was 4.0), 3.x continues maintenance

---

## 🎯 Version Strategy & Renaming

| Version | Purpose | Status | Timeline |
|---------|---------|--------|----------|
| **CORTEX 3.x** | Current production | ✅ Maintenance Mode | Ongoing (bug fixes only) |
| **CORTEX 4.0** | **Clean rebuild (THIS PLAN)** | 📋 Planning | Q1-Q2 2026 (12-14 weeks) |
| **CORTEX 5.0** | Multi-agent, distributed brain | ⏳ Future | Q3 2026+ |

**CORTEX 4.0 Goals:**
1. Fix architectural mess (clear folder structure)
2. Enable deployment (PyPI, Docker, VS Code)
3. Implement MCP server (standardized tooling)
4. Add team-level features (shared brain, LLM intent)
5. Create sustainable architecture (no more rewiring)

---

## 🏛️ CORTEX 4.0 Architecture Enhancements

### 1. MCP-First Architecture (NEW)

**Model Context Protocol Integration:**
- All orchestrators exposed as MCP tools
- Standardized JSON Schema interfaces
- Type-safe with automatic validation
- Works with Claude, Copilot, any MCP client

**Benefits:**
- No more custom CLI wrappers
- Auto-discovery by AI clients
- Protocol version negotiation
- Permission-based access control

### 2. Team-Level Brain (ENHANCED)

**Current (3.0):** Individual developer brain, no sharing

**New (4.0):**
```
cortex_core/brain/
├── personal/           # Individual developer context
│   ├── tier0/          # Personal governance overrides
│   ├── tier1/          # Personal conversation history
│   ├── tier3/          # Personal metrics
│   └── preferences.yaml
├── team/               # Shared team knowledge (NEW)
│   ├── tier2_shared/   # Team knowledge graph
│   ├── patterns/       # Discovered patterns (team-wide)
│   ├── conventions/    # Code conventions (team standards)
│   ├── architecture/   # Architecture decisions (ADRs)
│   └── lessons/        # Lessons learned (retros)
└── project/            # Per-project context
    ├── dependencies/   # Project-specific dependencies
    ├── tech_stack/     # Technology choices
    └── domain/         # Domain knowledge
```

**Features:**
- **Pattern Sharing:** Discovered patterns shared across team
- **Convention Sync:** Code style/standards synchronized
- **Knowledge Graph:** Team-wide knowledge connections
- **Privacy Controls:** Personal vs team data separation
- **Opt-In Sharing:** Developers control what's shared

### 3. LLM-Based Intent Router (NEW)

**Current (3.0):** Keyword matching in `cortex-operations.yaml`

**Problem:**
```yaml
natural_language:
  - plan feature
  - create plan
  - plan authentication  # Brittle - must match exactly
```

**New (4.0):** LLM-powered intent classification

```python
# cortex_core/intent/llm_router.py

class LLMIntentRouter:
    """
    LLM-powered intent classification replacing keyword matching.
    
    Uses lightweight local model (e.g., Llama 3.2 1B) for:
    - Natural language understanding
    - Context-aware routing
    - Ambiguity resolution
    """
    
    def classify_intent(self, user_request: str, context: Dict) -> Intent:
        """
        Classify user intent using LLM.
        
        Args:
            user_request: Natural language request
            context: Conversation history, active files, etc.
            
        Returns:
            Intent with orchestrator, confidence, parameters
        """
        
        # Build prompt with available operations
        prompt = self._build_classification_prompt(
            user_request=user_request,
            available_operations=self._get_operations(),
            context=context
        )
        
        # Query local LLM
        response = self.llm.generate(prompt)
        
        # Parse structured output
        intent = self._parse_intent(response)
        
        # Validate confidence threshold
        if intent.confidence < 0.7:
            return self._request_clarification(intent)
        
        return intent
```

**Benefits:**
- **Natural Language:** "Can you help me plan an auth feature?" → Planning Orchestrator
- **Context-Aware:** Uses active file, conversation history
- **Handles Ambiguity:** Asks clarifying questions when unsure
- **No Keyword Maintenance:** No more updating natural_language lists

**Implementation:**
- Local model (privacy-preserving)
- Fast inference (<100ms)
- Fallback to keyword matching if LLM unavailable
- Learning from corrections (user feedback)

### 4. Sustainable Orchestrator Architecture (FIXED)

**Problem (3.0):** Constant unwiring/rewiring as orchestrators evolve

**Root Cause:**
- Tight coupling between orchestrators
- Direct imports creating circular dependencies
- No stable interfaces
- Shared state management

**Solution (4.0):**

```python
# cortex_core/orchestrators/base_orchestrator.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from cortex_core.mcp import MCPTool

class BaseOrchestrator(ABC):
    """
    Base orchestrator with stable interface.
    
    All orchestrators inherit from this - NO EXCEPTIONS.
    Provides dependency injection, event system, and MCP integration.
    """
    
    def __init__(self, container: ServiceContainer):
        """
        Dependency injection via container.
        
        Args:
            container: Service locator for all dependencies
        """
        self.container = container
        self.brain = container.get('brain_engine')
        self.event_bus = container.get('event_bus')
        self.logger = container.get('logger')
        
    @abstractmethod
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrator logic."""
        pass
    
    @abstractmethod
    def get_mcp_tools(self) -> List[MCPTool]:
        """Return MCP tools provided by this orchestrator."""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return required service names."""
        pass
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to event bus (decoupled communication)."""
        self.event_bus.emit(event_type, data)
    
    def subscribe_event(self, event_type: str, handler):
        """Subscribe to events from other orchestrators."""
        self.event_bus.subscribe(event_type, handler)
```

**Key Principles:**
1. **Dependency Injection:** All dependencies via container (no direct imports)
2. **Event-Driven:** Orchestrators communicate via events (loose coupling)
3. **Stable Interface:** BaseOrchestrator interface never changes
4. **Service Locator:** Container manages all service lifetimes
5. **Testing:** Easy to mock dependencies

**Example:**

```python
# cortex_orchestrators/planning/planning_orchestrator.py

class PlanningOrchestrator(BaseOrchestrator):
    
    def get_dependencies(self) -> List[str]:
        return [
            'brain_engine',
            'complexity_analyzer',
            'dor_validator',
            'tdd_orchestrator'  # No direct import!
        ]
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Get TDD orchestrator from container
        tdd = self.container.get('tdd_orchestrator')
        
        # Or subscribe to TDD events
        self.subscribe_event('tdd.tests_passed', self._on_tests_passed)
        
        # Execute planning logic...
```

**Benefits:**
- ✅ No circular dependencies
- ✅ Easy to add new orchestrators
- ✅ Simple testing (mock container)
- ✅ Hot-reload orchestrators
- ✅ No more unwiring/rewiring

### 5. Deployment-First Design (NEW)

**Goal:** Make CORTEX distributable and easy to install

**Deployment Targets:**

1. **PyPI Package** (Primary)
   ```bash
   pip install cortex-ai
   cortex init
   cortex plan "auth feature"
   ```

2. **Docker Image**
   ```bash
   docker run -v $(pwd):/workspace cortex-ai:4.0 plan "auth feature"
   ```

3. **VS Code Extension**
   - One-click install from marketplace
   - Auto-configures MCP server
   - Embedded CORTEX engine

4. **GitHub Action**
   ```yaml
   - uses: asifhussain60/cortex-action@v4
     with:
       command: plan
       feature: "authentication system"
   ```

---

## 📁 CORTEX 4.0 Folder Structure

```
cortex-4.0/
├── 📦 cortex_core/              # Core engine (STABLE)
│   ├── brain/                   # 4-tier brain system
│   │   ├── tier0/               # Governance (SKULL)
│   │   ├── tier1/               # Working memory (personal)
│   │   ├── tier2/               # Knowledge graph (team-shared)
│   │   ├── tier3/               # Dev context (personal)
│   │   ├── brain_engine.py      # Unified brain API
│   │   └── team_brain.py        # Team knowledge manager (NEW)
│   ├── mcp/                     # MCP server infrastructure
│   │   ├── server.py            # MCP server core
│   │   ├── protocol.py          # Protocol handlers
│   │   ├── tools/               # Tool registry
│   │   └── schemas/             # Tool schemas (JSON Schema)
│   ├── intent/                  # Intent routing (NEW)
│   │   ├── llm_router.py        # LLM-powered intent classifier
│   │   ├── keyword_fallback.py  # Fallback to keyword matching
│   │   └── models/              # Local LLM models
│   ├── orchestrators/           # Orchestrator framework
│   │   ├── base_orchestrator.py # Base class (STABLE INTERFACE)
│   │   ├── registry.py          # Orchestrator registry
│   │   └── service_container.py # Dependency injection
│   ├── operations/              # Base operation framework
│   │   ├── base_operation.py   # Abstract base class
│   │   ├── operation_router.py # Request routing
│   │   └── response_builder.py # Response formatting
│   ├── events/                  # Event system (NEW)
│   │   ├── event_bus.py         # Pub/sub event bus
│   │   └── event_types.py       # Standard event types
│   └── config/                  # Configuration management
│       ├── loader.py            # Config loader
│       ├── validator.py         # Schema validation
│       └── defaults.yaml        # Default settings
│
├── 🎭 cortex_orchestrators/     # Orchestrator implementations
│   ├── planning/                # Planning System
│   │   ├── planning_orchestrator.py
│   │   ├── complexity_analyzer.py
│   │   ├── dor_validator.py
│   │   ├── incremental_planner.py
│   │   ├── skeleton_planner.py
│   │   ├── tests/
│   │   │   ├── test_planning_orchestrator.py
│   │   │   ├── test_complexity_detection.py
│   │   │   ├── test_tdd_integration.py
│   │   │   └── fixtures/
│   │   └── README.md
│   ├── ado/                     # ADO Operations
│   │   ├── ado_orchestrator.py
│   │   ├── story_generator.py
│   │   ├── feature_generator.py
│   │   ├── tests/
│   │   └── README.md
│   ├── tdd/                     # TDD Mastery
│   │   ├── tdd_orchestrator.py
│   │   ├── red_phase.py
│   │   ├── green_phase.py
│   │   ├── refactor_phase.py
│   │   ├── tests/
│   │   └── README.md
│   ├── maintenance/             # System Maintenance
│   │   ├── maintenance_orchestrator.py
│   │   ├── healthcheck_module.py
│   │   ├── align_module.py
│   │   ├── cleanup_module.py
│   │   ├── optimize_module.py
│   │   ├── vacuum_module.py
│   │   ├── tests/
│   │   └── README.md
│   ├── sanitization/            # Code Sanitization
│   │   ├── sanitization_orchestrator.py
│   │   ├── analyzer.py
│   │   ├── mapper.py
│   │   ├── transformer.py
│   │   ├── validator.py
│   │   ├── tests/
│   │   └── README.md
│   ├── review/                  # Architecture Review
│   │   ├── review_orchestrator.py
│   │   ├── scoring_engine.py
│   │   ├── tests/
│   │   └── README.md
│   ├── refinement/              # System Refinement
│   │   ├── refinement_orchestrator.py
│   │   ├── discovery_phase.py
│   │   ├── skull_review_phase.py
│   │   ├── tests/
│   │   └── README.md
│   └── __init__.py              # Orchestrator registry
│
├── 🧰 cortex_tools/              # Reusable utilities
│   ├── ast_analyzer/            # Code analysis
│   ├── git_ops/                 # Git operations
│   ├── file_ops/                # File system operations
│   ├── test_runner/             # Test execution
│   ├── metrics/                 # Metrics collection
│   └── llm/                     # LLM utilities (NEW)
│
├── 🧠 cortex_brain/              # Brain data & rules
│   ├── tier0/                   # Governance rules (SKULL)
│   ├── tier1/                   # Conversation history
│   ├── tier2/                   # Knowledge graph
│   ├── tier3/                   # Dev context
│   ├── team/                    # Team-shared knowledge (NEW)
│   └── templates/               # Response templates
│
├── 🚀 cortex_deployment/         # Deployment artifacts
│   ├── pypi/                    # PyPI packaging
│   │   ├── setup.py
│   │   ├── pyproject.toml
│   │   ├── MANIFEST.in
│   │   └── README.md
│   ├── docker/                  # Docker images
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── entrypoint.sh
│   ├── vscode/                  # VS Code extension
│   │   ├── package.json
│   │   ├── extension.ts
│   │   ├── mcp-config.json
│   │   └── README.md
│   ├── github_action/           # GitHub Action
│   │   ├── action.yml
│   │   └── index.js
│   └── ci/                      # CI/CD configs
│       ├── .github/workflows/
│       │   ├── ci.yml
│       │   ├── release.yml
│       │   └── publish.yml
│       └── codecov.yml
│
├── 📚 docs/                      # Documentation
│   ├── architecture/            # Architecture docs
│   │   ├── mcp-integration.md
│   │   ├── orchestrator-framework.md
│   │   ├── team-brain.md
│   │   └── llm-intent-router.md
│   ├── api/                     # MCP API docs
│   ├── guides/                  # User guides
│   │   ├── quick-start.md
│   │   ├── installation.md
│   │   ├── team-setup.md
│   │   └── orchestrator-development.md
│   ├── migration/               # 3.0 → 4.0 migration
│   │   ├── migration-guide.md
│   │   ├── breaking-changes.md
│   │   └── upgrade-checklist.md
│   └── adr/                     # Architecture Decision Records
│
└── 🧪 tests/                     # Test suites
    ├── unit/                    # Unit tests (per-module)
    ├── integration/             # Integration tests (orchestrator + brain)
    ├── e2e/                     # End-to-end tests (full workflows)
    ├── performance/             # Performance benchmarks
    └── fixtures/                # Test fixtures & mocks
```

---

## 🚀 12-Week Migration Plan

### Week 1-2: Phase 0 - Foundation

**Goal:** Set up CORTEX 4.0 infrastructure

**Tasks:**
1. ✅ Create `CORTEX-4.0` branch
2. ✅ Initialize clean directory structure
3. ✅ Implement `cortex_core/` foundation:
   - Brain engine (unified 4-tier API)
   - Event bus (orchestrator communication)
   - Service container (dependency injection)
   - Base orchestrator (stable interface)
   - MCP server scaffolding
4. ✅ Set up LLM intent router:
   - Local model integration (Llama 3.2 1B)
   - Intent classification logic
   - Keyword fallback system
5. ✅ Create testing infrastructure:
   - pytest configuration
   - Coverage reporting (100% requirement)
   - CI pipeline (GitHub Actions)
6. ✅ Set up deployment scaffolding:
   - setup.py (PyPI)
   - Dockerfile
   - VS Code extension skeleton
   - GitHub Action template

**Validation:**
- [ ] Brain engine operational (all 4 tiers + team brain)
- [ ] Event bus working (pub/sub verified)
- [ ] Service container functional (DI tested)
- [ ] MCP server starts successfully
- [ ] LLM intent router classifies basic requests
- [ ] CI pipeline green
- [ ] Test coverage reporting works

**Deliverables:**
- `cortex_core/` foundation (1000 LOC)
- Test infrastructure (pytest, coverage)
- CI/CD pipeline (GitHub Actions)
- Deployment scaffolding (PyPI, Docker, VS Code)

---

### Week 3: Phase 1.1 - TDD Orchestrator

**Priority:** P0 (Foundation for all others)

**Current Location:** `src/workflows/tdd_workflow_orchestrator.py`

**Migration Steps:**

1. **Analysis** (Day 1)
   - Map current TDD orchestrator functionality
   - Identify dependencies (test runner, metrics)
   - Document test coverage gaps

2. **Port Core Logic** (Day 2-3)
   ```
   cortex_orchestrators/tdd/
   ├── tdd_orchestrator.py        # Main orchestrator
   ├── red_phase.py               # RED: Write failing tests
   ├── green_phase.py             # GREEN: Make tests pass
   ├── refactor_phase.py          # REFACTOR: Improve code
   ├── coverage_validator.py      # Per-layer coverage
   ├── empty_test_detector.py     # Detect placeholder tests
   └── tests/
       ├── test_tdd_orchestrator.py
       ├── test_red_phase.py
       ├── test_green_phase.py
       ├── test_refactor_phase.py
       └── fixtures/
   ```

3. **Extract Utilities** (Day 3-4)
   ```
   cortex_tools/test_runner/
   ├── pytest_runner.py
   ├── coverage_reporter.py
   └── test_discovery.py
   ```

4. **Write Tests** (Day 4-5)
   - Unit tests (100% coverage)
   - Integration tests (with brain)
   - E2E tests (full RED→GREEN→REFACTOR)

5. **Implement MCP Tools** (Day 5)
   - `cortex_tdd_start` - Begin TDD workflow
   - `cortex_tdd_validate` - Validate TDD compliance
   - `cortex_tdd_status` - Get current phase status

6. **Brain Integration** (Day 5)
   - Tier1: Conversation context
   - Tier3: Test metrics, coverage trends

**Success Criteria:**
- [ ] 100% test coverage
- [ ] All 3.0 features preserved
- [ ] MCP tools callable from Copilot Chat
- [ ] Brain integration working
- [ ] RED→GREEN→REFACTOR enforced
- [ ] Empty test detection functional
- [ ] Per-layer coverage validation

**Deliverables:**
- TDD orchestrator (600 LOC)
- Test suite (400 LOC, 100% coverage)
- MCP tool definitions
- Migration report

---

### Week 4: Phase 1.2 - Planning Orchestrator

**Priority:** P0 (Just developed, fresh in memory)

**Current Location:** `src/orchestrators/planning/` (multiple files)

**Migration Steps:**

1. **Consolidation** (Day 1-2)
   - Merge scattered planning modules
   - Map Planning System components
   - Document DoR/DoD compliance

2. **Port to 4.0 Architecture** (Day 2-4)
   ```
   cortex_orchestrators/planning/
   ├── planning_orchestrator.py     # Main orchestrator
   ├── complexity_analyzer.py       # AUTO complexity detection
   ├── dor_validator.py             # Definition of Ready
   ├── dod_validator.py             # Definition of Done
   ├── incremental_planner.py       # HIGH complexity workflow
   ├── skeleton_planner.py          # LOW complexity workflow
   ├── interactive_session.py       # Refinement sessions
   ├── plan_generator.py            # Unified plan generation
   └── tests/
       ├── test_planning_orchestrator.py
       ├── test_complexity_detection.py
       ├── test_incremental_routing.py
       ├── test_tdd_integration.py
       ├── test_dor_validation.py
       └── fixtures/
   ```

3. **Extract Utilities** (Day 3)
   ```
   cortex_tools/ast_analyzer/
   ├── ast_parser.py
   ├── complexity_metrics.py
   └── dependency_graph.py
   ```

4. **Write Tests** (Day 4-5)
   - Unit tests (100% coverage)
   - Integration tests (TDD orchestrator integration)
   - E2E tests (full planning workflow)
   - Complexity detection tests (HIGH/MEDIUM/LOW)

5. **Implement MCP Tools** (Day 5)
   - `cortex_plan` - Interactive planning
   - `cortex_plan_refine` - Refine existing plan
   - `cortex_plan_execute` - Execute plan autonomously

6. **Validate Manifest Compliance** (Day 5)
   - DoR/DoD gates functional
   - TDD auto-integration working
   - Acceptance criteria validated

**Success Criteria:**
- [ ] 100% test coverage
- [ ] Auto-complexity detection (HIGH→incremental)
- [ ] TDD auto-integration functional
- [ ] DoR/DoD compliance validated
- [ ] Interactive refinement sessions working
- [ ] Planning System manifest preserved

**Deliverables:**
- Planning orchestrator (800 LOC)
- Test suite (500 LOC, 100% coverage)
- MCP tool definitions
- DoR/DoD validation report

---

### Week 5: Phase 1.3 - ADO Orchestrator

**Priority:** P0 (Builds on Planning)

**Current Location:** `src/operations/ado.py` + related modules

**Migration Steps:**

1. **Port to 4.0** (Day 1-3)
   ```
   cortex_orchestrators/ado/
   ├── ado_orchestrator.py          # Main orchestrator
   ├── story_generator.py           # User Story generation
   ├── feature_generator.py         # Feature generation
   ├── task_generator.py            # Task generation
   ├── completion_summary.py        # Completion summaries
   ├── code_review_planner.py       # Code review planning
   └── tests/
       ├── test_ado_orchestrator.py
       ├── test_story_generation.py
       ├── test_feature_generation.py
       └── fixtures/
   ```

2. **Inherit Planning System** (Day 2)
   - Extend Planning orchestrator
   - Apply ADO-specific formatting
   - Preserve DoR/DoD compliance

3. **Write Tests** (Day 3-4)
   - Unit tests (100% coverage)
   - ADO format validation tests
   - Planning System compliance tests

4. **Implement MCP Tools** (Day 4-5)
   - `cortex_ado_story` - Generate user story
   - `cortex_ado_feature` - Generate feature
   - `cortex_ado_task` - Generate task
   - `cortex_ado_summary` - Completion summary

**Success Criteria:**
- [ ] 100% test coverage
- [ ] All ADO formats validated (Story, Feature, Task)
- [ ] Planning System compliance inherited
- [ ] Completion summaries working
- [ ] Code review planning functional

**Deliverables:**
- ADO orchestrator (400 LOC)
- Test suite (300 LOC, 100% coverage)
- MCP tool definitions
- ADO format validation report

---

### Week 6: Phase 1.4 - Maintenance Orchestrator

**Priority:** P0 (Critical for system health)

**Current Location:** Scattered across `src/operations/` (align, healthcheck, optimize, cleanup)

**Migration Steps:**

1. **Consolidate 7-Phase Workflow** (Day 1-2)
   ```
   cortex_orchestrators/maintenance/
   ├── maintenance_orchestrator.py  # Main orchestrator
   ├── healthcheck_module.py        # Pre/post healthcheck
   ├── align_module.py              # System alignment
   ├── cleanup_module.py            # Workspace cleanup
   ├── optimize_module.py           # System optimization
   ├── vacuum_module.py             # Brain vacuum
   ├── refresh_prompts_module.py    # Prompt refresh
   ├── tiered_router.py             # Planning System
   └── tests/
       ├── test_maintenance_orchestrator.py
       ├── test_healthcheck.py
       ├── test_align.py
       ├── test_cleanup.py
       ├── test_optimize.py
       └── fixtures/
   ```

2. **Port Phase Modules** (Day 2-4)
   - Extract each phase into separate module
   - Implement event-driven communication
   - Add phase transition logging (🎭 hints)

3. **Write Tests** (Day 4-5)
   - Unit tests per phase (100% coverage)
   - Integration tests (all 7 phases)
   - Success template trigger tests

4. **Implement MCP Tools** (Day 5)
   - `cortex_maintain` - Full 7-phase maintenance
   - `cortex_healthcheck` - Health check only
   - `cortex_align` - Alignment only
   - `cortex_cleanup` - Cleanup only
   - `cortex_optimize` - Optimization only

**Success Criteria:**
- [ ] 100% test coverage
- [ ] All 7 phases tested independently
- [ ] Success template triggers on completion
- [ ] Orchestrator engagement hints working (🎭)
- [ ] Tiered routing functional

**Deliverables:**
- Maintenance orchestrator (700 LOC)
- 7 phase modules (100 LOC each)
- Test suite (600 LOC, 100% coverage)
- MCP tool definitions

---

### Week 7: Phase 2.1 - Sanitization Orchestrator

**Priority:** P1 (Enhancement)

**Current Location:** `src/operations/modules/orchestration/sanitization_orchestrator.py`

**Migration Steps:**

1. **Port 5-Phase Workflow** (Day 1-3)
   ```
   cortex_orchestrators/sanitization/
   ├── sanitization_orchestrator.py # Main orchestrator
   ├── analyzer.py                  # Phase 1: Analyze
   ├── mapper.py                    # Phase 2: Mapping
   ├── transformer.py               # Phase 3: Transform
   ├── validator.py                 # Phase 4: Validate
   ├── reporter.py                  # Phase 5: Report
   └── tests/
       ├── test_sanitization_orchestrator.py
       ├── test_analyzer.py
       ├── test_transformer.py
       └── fixtures/
   ```

2. **Write Tests** (Day 3-4)
   - Unit tests (100% coverage)
   - Integration tests (full workflow)
   - Build validation tests

3. **Implement MCP Tools** (Day 4-5)
   - `cortex_sanitize` - Full sanitization workflow
   - `cortex_sanitize_analyze` - Analysis only

**Success Criteria:**
- [ ] 100% test coverage
- [ ] 5-phase workflow validated
- [ ] Build/test validation working
- [ ] Audit report generation functional

---

### Week 8: Phase 2.2 - Review Orchestrator

**Priority:** P1 (Enhancement)

**Current Location:** `src/operations/review.py` + CLI wrapper

**Migration Steps:**

1. **Port 6-Phase Review** (Day 1-3)
   ```
   cortex_orchestrators/review/
   ├── review_orchestrator.py       # Main orchestrator
   ├── scoring_engine.py            # 0-100 scoring
   ├── architecture_analyzer.py     # Architecture review
   ├── complexity_analyzer.py       # Complexity analysis
   ├── security_analyzer.py         # Security review
   └── tests/
   ```

2. **Write Tests** (Day 3-5)
   - Unit tests (100% coverage)
   - Scoring validation tests

3. **Implement MCP Tools** (Day 5)
   - `cortex_review` - Full architecture review

**Success Criteria:**
- [ ] 100% test coverage
- [ ] 6-phase review validated
- [ ] 0-100 scoring functional

---

### Week 9: Phase 2.3 - Refinement Orchestrator

**Priority:** P1 (Enhancement)

**Current Location:** `src/operations/modules/orchestration/refinement_orchestrator_v1.py`

**Migration Steps:**

1. **Port 7-Phase Refinement** (Day 1-3)
   ```
   cortex_orchestrators/refinement/
   ├── refinement_orchestrator.py   # Main orchestrator
   ├── discovery_phase.py           # Phase 1: Discovery
   ├── skull_review_phase.py        # Phase 2: SKULL review
   ├── documentation_phase.py       # Phase 3: Docs
   ├── quality_phase.py             # Phase 4: Code quality
   ├── architecture_phase.py        # Phase 5: Architecture
   ├── performance_phase.py         # Phase 6: Performance
   ├── validation_phase.py          # Phase 7: Validation
   └── tests/
   ```

2. **Write Tests** (Day 3-5)
   - Unit tests (100% coverage)
   - Rollback safety tests

3. **Implement MCP Tools** (Day 5)
   - `cortex_refine` - Full refinement workflow

**Success Criteria:**
- [ ] 100% test coverage
- [ ] 7-phase refinement validated
- [ ] Rollback safety functional

---

### Week 10-11: Phase 3 - Utility Orchestrators

**Priority:** P2 (Lower complexity)

**Orchestrators:**
- Upgrade (Week 10, Day 1-2)
- Deploy (Week 10, Day 3-4)
- Help (Week 10, Day 5)
- Feedback (Week 11, Day 1-2)
- Command Search (Week 11, Day 3)
- Feature Planning (Week 11, Day 4)
- Application Onboarding (Week 11, Day 5)
- User Onboarding (Week 11, Day 5)

**Approach:** Lightweight migrations, standard 100% coverage

---

### Week 12: Phase 4 - Finalization

**Goal:** Complete migration, publish deployments

**Tasks:**

1. **Documentation** (Day 1-2)
   - Complete all orchestrator README files
   - Write migration guide (3.0 → 4.0)
   - Create deployment guides
   - Generate API documentation

2. **Deployment** (Day 3-4)
   - Publish to PyPI: `pip install cortex-ai`
   - Release Docker image: `docker pull cortex-ai:4.0`
   - Submit VS Code extension to marketplace
   - Publish GitHub Action

3. **Archive CORTEX 3.0** (Day 4)
   - Create `archive/v3.0/` directory
   - Move all 3.0 code to archive
   - Update README with migration notes

4. **Final Testing** (Day 5)
   - Run full test suite (all orchestrators)
   - Validate 100% coverage maintained
   - Test all MCP tools
   - Performance benchmarking

**Validation:**
- [ ] All 16 orchestrators migrated
- [ ] 100% test coverage maintained
- [ ] All MCP tools functional
- [ ] PyPI package published
- [ ] Docker image available
- [ ] VS Code extension submitted
- [ ] Documentation complete
- [ ] Migration guide published

---

## 🎯 Orchestrator Consolidation Strategy

### Which Orchestrators to Combine?

**Problem (3.0):** Too many small orchestrators doing similar things

**Solution (4.0):** Consolidate into cohesive units

| 3.0 Orchestrators | 4.0 Consolidated | Rationale |
|-------------------|------------------|-----------|
| align, healthcheck, optimize, cleanup, vacuum | **MaintenanceOrchestrator** (7 phases) | All system health operations |
| planning, incremental_planning, skeleton_planning | **PlanningOrchestrator** (unified) | Single entry point, auto-routing |
| ado_story, ado_feature, ado_task | **ADOOrchestrator** (extends Planning) | Inherits Planning System |
| sanitize_analyze, sanitize_transform, sanitize_validate | **SanitizationOrchestrator** (5 phases) | Single workflow |
| refine_discovery, refine_quality, refine_validate | **RefinementOrchestrator** (7 phases) | Single workflow |

**Result:** 16 orchestrators → 12 orchestrators (25% reduction)

---

## 🧠 Team Brain Enhancements

### Architecture

```python
# cortex_core/brain/team_brain.py

class TeamBrain:
    """
    Team-level knowledge sharing and pattern discovery.
    
    Features:
    - Shared knowledge graph (Tier 2)
    - Team conventions and standards
    - Architecture Decision Records (ADRs)
    - Cross-developer pattern learning
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.shared_kg = Tier2SharedGraph()
        self.conventions = ConventionManager()
        self.adrs = ADRManager()
        self.patterns = PatternLibrary()
    
    def share_pattern(self, pattern: Pattern, developer_id: str):
        """
        Share discovered pattern with team.
        
        Args:
            pattern: Discovered pattern
            developer_id: Developer who discovered it
        """
        # Privacy check
        if not self._is_shareable(pattern):
            return
        
        # Add to team knowledge graph
        self.shared_kg.add_pattern(pattern, source=developer_id)
        
        # Notify team members
        self._notify_team(f"New pattern discovered: {pattern.name}")
    
    def get_team_conventions(self) -> List[Convention]:
        """Get team coding conventions."""
        return self.conventions.get_all()
    
    def suggest_pattern(self, context: Dict) -> Optional[Pattern]:
        """
        Suggest pattern based on current context.
        
        Uses team knowledge to recommend patterns.
        """
        return self.patterns.find_matching(context)
```

### Privacy & Control

**Opt-In Sharing:**
```yaml
# cortex.config.json
team:
  enabled: true
  team_id: "acme-backend-team"
  sharing:
    patterns: true          # Share discovered patterns
    conventions: true       # Share code conventions
    metrics: false          # Don't share personal metrics
    conversations: false    # Keep conversations private
```

**Shared vs Personal:**

| Data Type | Storage | Shareable | Use Case |
|-----------|---------|-----------|----------|
| Conversation history | Personal (Tier 1) | ❌ No | Privacy-preserving |
| Knowledge graph | Team (Tier 2 shared) | ✅ Yes | Pattern discovery |
| Dev metrics | Personal (Tier 3) | ❌ No | Individual performance |
| Code conventions | Team | ✅ Yes | Team standards |
| Architecture decisions | Team | ✅ Yes | ADRs |
| Lessons learned | Team | ✅ Yes | Retrospectives |

---

## 🧪 Testing Strategy

### Coverage Requirements

**Mandatory:** 100% test coverage for each orchestrator

**Test Pyramid:**

```
         E2E (10%)
        /         \
   Integration (30%)
   /                \
Unit Tests (60%)
```

**Test Types:**

1. **Unit Tests** (60% of tests)
   - Individual methods/functions
   - Mocked dependencies
   - Fast execution (<1ms each)

2. **Integration Tests** (30% of tests)
   - Orchestrator + brain + tools
   - Real dependencies (in-memory)
   - Medium execution (<100ms each)

3. **E2E Tests** (10% of tests)
   - Full workflow via MCP
   - Real brain, real file system
   - Slow execution (<5s each)

**Example Test Structure:**

```python
# tests/unit/orchestrators/planning/test_planning_orchestrator.py

import pytest
from cortex_orchestrators.planning import PlanningOrchestrator
from cortex_core.orchestrators import ServiceContainer

class TestPlanningOrchestrator:
    
    @pytest.fixture
    def container(self):
        """Mock service container."""
        container = ServiceContainer()
        container.register('brain_engine', MockBrain())
        container.register('complexity_analyzer', MockAnalyzer())
        container.register('tdd_orchestrator', MockTDD())
        return container
    
    @pytest.fixture
    def orchestrator(self, container):
        return PlanningOrchestrator(container)
    
    def test_complexity_detection_high(self, orchestrator):
        """Test auto-detection of HIGH complexity (auth feature)."""
        result = orchestrator.detect_complexity("authentication system")
        assert result == "HIGH"
    
    def test_incremental_routing(self, orchestrator):
        """Test incremental planning workflow."""
        request = {"feature": "authentication system"}
        plan = orchestrator.execute(request)
        
        assert plan["workflow_type"] == "incremental"
        assert "DoR" in plan["phases"]
        assert "TDD" in plan["phases"]
    
    def test_tdd_auto_integration(self, orchestrator):
        """Test TDD automatically included in plan."""
        request = {"feature": "simple utility function"}
        plan = orchestrator.execute(request)
        
        assert any("TDD" in phase for phase in plan["phases"])
    
    def test_event_emission(self, orchestrator, container):
        """Test orchestrator emits events."""
        events = []
        container.get('event_bus').subscribe('planning.started', events.append)
        
        orchestrator.execute({"feature": "test"})
        
        assert len(events) == 1
        assert events[0]['type'] == 'planning.started'
```

### CI/CD Pipeline

**File:** `.github/workflows/ci.yml`

```yaml
name: CORTEX 4.0 CI

on: [push, pull_request]

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
        run: |
          pytest \
            --cov=cortex_core \
            --cov=cortex_orchestrators \
            --cov=cortex_tools \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=100
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Lint
        run: |
          pip install ruff mypy
          ruff check .
          mypy cortex_core cortex_orchestrators
  
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Integration tests
        run: |
          pip install -r requirements.txt
          pytest tests/integration/ -v
  
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: E2E tests
        run: |
          pip install -r requirements.txt
          pytest tests/e2e/ -v --slow
```

---

## 📊 Migration Tracking Dashboard

### Orchestrator Status

| Priority | Orchestrator | Week | Status | Coverage | MCP Tools | Tests |
|----------|--------------|------|--------|----------|-----------|-------|
| P0-1 | TDD | 3 | ⏳ Not Started | 0% | 3 | 0/12 |
| P0-2 | Planning | 4 | ⏳ Not Started | 0% | 3 | 0/15 |
| P0-3 | ADO | 5 | ⏳ Not Started | 0% | 4 | 0/10 |
| P0-4 | Maintenance | 6 | ⏳ Not Started | 0% | 5 | 0/20 |
| P1-5 | Sanitization | 7 | ⏳ Not Started | 0% | 2 | 0/12 |
| P1-6 | Review | 8 | ⏳ Not Started | 0% | 1 | 0/10 |
| P1-7 | Refinement | 9 | ⏳ Not Started | 0% | 1 | 0/15 |
| P2-8 | Upgrade | 10 | ⏳ Not Started | 0% | 1 | 0/6 |
| P2-9 | Deploy | 10 | ⏳ Not Started | 0% | 1 | 0/5 |
| P2-10 | Help | 10 | ⏳ Not Started | 0% | 1 | 0/3 |
| P2-11 | Feedback | 11 | ⏳ Not Started | 0% | 1 | 0/4 |
| P2-12 | Command Search | 11 | ⏳ Not Started | 0% | 1 | 0/4 |

**Legend:**
- ⏳ Not Started
- 🔄 In Progress
- ✅ Complete (100% coverage)

**Overall Progress:** 0/12 orchestrators (0%)

---

## 📦 Deployment Strategy

### 1. PyPI Package (Primary Distribution)

**Package Name:** `cortex-ai` (already reserved)

**Files:**

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="cortex-ai",
    version="4.0.0",
    author="Asif Hussain",
    author_email="asifhussain60@users.noreply.github.com",
    description="GitHub Copilot memory & planning system with MCP integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/asifhussain60/CORTEX",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "mcp>=1.0.0",
        "pyyaml>=6.0",
        "click>=8.0",
        "rich>=13.0",
        "pydantic>=2.0",
        "httpx>=0.25.0",
        "aiofiles>=23.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-asyncio>=0.21",
            "ruff>=0.1.0",
            "mypy>=1.7",
        ],
        "llm": [
            "llama-cpp-python>=0.2.0",  # Local LLM
            "transformers>=4.35.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cortex=cortex_core.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

**Installation:**
```bash
# Install CORTEX 4.0
pip install cortex-ai

# With LLM support (local intent router)
pip install cortex-ai[llm]

# Development installation
pip install cortex-ai[dev]

# Initialize brain
cortex init

# Verify installation
cortex healthcheck

# Start MCP server
cortex serve
```

### 2. Docker Image

**File:** `cortex_deployment/docker/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY cortex_core/ ./cortex_core/
COPY cortex_orchestrators/ ./cortex_orchestrators/
COPY cortex_tools/ ./cortex_tools/
COPY cortex_brain/ ./cortex_brain/

# Expose MCP server port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import cortex_core; cortex_core.healthcheck()"

# Entry point
ENTRYPOINT ["python", "-m", "cortex_core.mcp.server"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  cortex:
    image: cortex-ai:4.0
    container_name: cortex-mcp-server
    ports:
      - "5000:5000"
    volumes:
      - ./cortex-brain:/app/cortex_brain
      - ./workspace:/workspace
    environment:
      - CORTEX_CONFIG=/app/cortex.config.json
      - CORTEX_LOG_LEVEL=INFO
    restart: unless-stopped
```

**Usage:**
```bash
# Build image
docker build -t cortex-ai:4.0 .

# Run container
docker run -d -p 5000:5000 \
  -v $(pwd)/cortex-brain:/app/cortex_brain \
  -v $(pwd)/workspace:/workspace \
  cortex-ai:4.0

# Use with docker-compose
docker-compose up -d
```

### 3. VS Code Extension

**File:** `cortex_deployment/vscode/package.json`

```json
{
  "name": "cortex-copilot-brain",
  "displayName": "CORTEX - Copilot Brain",
  "version": "4.0.0",
  "publisher": "asifhussain60",
  "description": "Memory & planning for GitHub Copilot with MCP integration",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["AI", "Programming Languages", "Other"],
  "keywords": ["copilot", "ai", "planning", "tdd", "memory"],
  "icon": "images/icon.png",
  "repository": {
    "type": "git",
    "url": "https://github.com/asifhussain60/CORTEX"
  },
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "cortex.init",
        "title": "CORTEX: Initialize Brain"
      },
      {
        "command": "cortex.healthcheck",
        "title": "CORTEX: Health Check"
      },
      {
        "command": "cortex.plan",
        "title": "CORTEX: Plan Feature"
      }
    ],
    "configuration": {
      "title": "CORTEX",
      "properties": {
        "cortex.mcpServer.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable CORTEX MCP server"
        },
        "cortex.mcpServer.port": {
          "type": "number",
          "default": 5000,
          "description": "MCP server port"
        },
        "cortex.llmIntent.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable LLM-powered intent routing"
        },
        "cortex.team.enabled": {
          "type": "boolean",
          "default": false,
          "description": "Enable team brain features"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.3.0"
  },
  "dependencies": {
    "mcp": "^1.0.0"
  }
}
```

**Installation:**
1. Publish to VS Code Marketplace
2. Users install via: `code --install-extension asifhussain60.cortex-copilot-brain`
3. Or search "CORTEX" in VS Code Extensions

### 4. GitHub Action

**File:** `cortex_deployment/github_action/action.yml`

```yaml
name: 'CORTEX Planning'
description: 'AI-powered feature planning and TDD workflow'
author: 'Asif Hussain'

inputs:
  command:
    description: 'CORTEX command to run (plan, tdd, sanitize, etc.)'
    required: true
  feature:
    description: 'Feature description (for plan command)'
    required: false
  directory:
    description: 'Target directory (for sanitize command)'
    required: false

outputs:
  result:
    description: 'Command execution result'
  
runs:
  using: 'node20'
  main: 'dist/index.js'

branding:
  icon: 'cpu'
  color: 'blue'
```

**Usage in workflow:**

```yaml
name: Feature Planning

on:
  issues:
    types: [labeled]

jobs:
  plan:
    if: contains(github.event.issue.labels.*.name, 'needs-plan')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Plan feature
        uses: asifhussain60/cortex-action@v4
        with:
          command: plan
          feature: ${{ github.event.issue.body }}
      
      - name: Comment plan
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: ${{ steps.plan.outputs.result }}
            })
```

---

## 🎓 Success Criteria

### Technical Metrics

- [ ] **100% Test Coverage** - Maintained throughout migration
- [ ] **All MCP Tools Functional** - 20+ tools working
- [ ] **CI/CD Success Rate > 95%** - Stable builds
- [ ] **Zero Critical Bugs** - No P0 issues in production
- [ ] **LLM Intent Accuracy > 90%** - Correct orchestrator routing
- [ ] **Event Bus Latency < 10ms** - Fast orchestrator communication

### Deployment Metrics

- [ ] **PyPI Package Published** - `pip install cortex-ai` works
- [ ] **Docker Image Available** - DockerHub/GHCR published
- [ ] **VS Code Extension Approved** - Listed in marketplace
- [ ] **GitHub Action Published** - Available in marketplace
- [ ] **Documentation Complete** - All guides written

### User Experience Metrics

- [ ] **Installation Time < 2 minutes** - Fast setup
- [ ] **Setup Time < 5 minutes** - Brain initialization
- [ ] **Response Time < 100ms** - MCP tool latency
- [ ] **No Rewiring Issues** - Stable orchestrator architecture
- [ ] **Team Onboarding < 30 minutes** - Easy team setup

---

## 🔮 Future (CORTEX 5.0)

**Deferred Features:**

- **Multi-Agent Collaboration** - Multiple AI agents working together
- **Distributed Brain** - Cloud-based brain synchronization
- **Real-Time Collaboration** - Multiple developers sharing brain
- **Advanced ML** - Deep learning for pattern recognition
- **Cloud Deployment** - SaaS offering

**Timeline:** Q3 2026+

---

## 📞 Review & Approval

**This plan requires your review and approval before execution.**

**Key Questions:**

1. ✅ **Renaming Strategy** - Agree with CORTEX 4.0 (clean rebuild) and 5.0 (future)?
2. ✅ **MCP-First Approach** - Comfortable with MCP server architecture?
3. ✅ **Team Brain Features** - Want team-level knowledge sharing?
4. ✅ **LLM Intent Router** - Replace keyword matching with LLM?
5. ✅ **Incremental Migration** - 12-week timeline acceptable?
6. ✅ **100% Coverage Requirement** - Agree with strict testing?
7. ✅ **Deployment Strategy** - PyPI + Docker + VS Code + GitHub Action?

**Next Steps After Approval:**

1. Create `CORTEX-4.0` branch
2. Execute Phase 0 (Foundation) - Week 1-2
3. Begin orchestrator migration - Week 3+

---

**Author:** Asif Hussain  
**GitHub:** https://github.com/asifhussain60/CORTEX  
**Contact:** asifhussain60@users.noreply.github.com

