# 🛡️ CORTEX v5.0 Holistic Architecture Refactor

**Plan ID:** cortex-v5-holistic-refactor  
**Feature:** System-wide Pure Autonomous Architecture Transformation with Master Orchestrator + Cross-Session Context  
**Created:** January 2, 2026 | **Updated:** January 2, 2026 (Cross-Session Context Middleware integration)  
**Complexity:** TIER 5 (ARCHITECTURAL)  
**Strategy:** Bootstrap Planning System v5 + Master Orchestrator + Context Middleware, then use them to plan remaining migrations  
**Estimated Duration:** 40 days total (13 days bootstrap + 27 days migrations)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `█████░░░░░░░░░░░░░░░` **25%** ⏳ IN PROGRESS

### Bootstrap Phase (Planning System v5 + Master Orchestrator + Context Middleware)

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation Setup | `██████████` | 1d | ✅ Complete |
| 1 | MCP Tool Infra | `██████████` | 2d | ✅ Complete |
| 2 | State Database | `██████████` | 1.5d | ✅ Complete |
| 3 | BaseOrch v4.1 + Master Orch Core | `██████████` | 2.5d | ✅ Complete |
| 3.5 | Master Orch Integration | `██████████` | 1d | ✅ Complete |
| 4 | PlanOrch v5 | `██████████` | 2d | ✅ Complete |
| 4.5 | **Cross-Session Context Middleware** | `██████████` | **2d** | ✅ **COMPLETE** |

### Migration Phase (Using Planning System v5)

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 5 | Use v5 to Plan Migrations | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 6 | Execute Migration Plans | `░░░░░░░░░░` | 24d | ⏸️ Not Started |
| 7 | System Integration | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 8 | Testing & Validation | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 9 | Documentation | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 10 | REFACTOR & Cleanup | `░░░░░░░░░░` | 2d | ⏸️ Not Started |

**Bootstrap Completion:** ~13 days (includes Master Orchestrator + Context Middleware)  
**Full Completion:** ~40 days  
**Current Phase:** BaseOrchestrator v4.1 + Master Orchestrator Core implementation

**Checkpoints:**
- ✅ Phase 1 checkpoint @ commit 90153190: MCP Tool Infrastructure
- ✅ Phase 2 checkpoint @ commit 3a081949: Planning State Database
- ✅ Master Orchestrator Integration @ commit 87a081529: Plan holistically updated
- ✅ Progressive Activation Strategy @ commit 4568a2f52: Master Orch activates as components are built
- ✅ Holistic Plan Review @ commit 35329a224: Master Orch context added to all phases (0-10)
- ✅ Session Management System @ commit a93860329: Continuation prompt for multi-session execution
- ✅ **Continuation Prompt ACTIVATED** @ commit 40abf77af: Live implementation with 12/12 tests passing
- ✅ **Phase 4.5 COMPLETE** @ commit [PENDING]: Cross-Session Context Middleware operational (99.6% token efficiency)

---

## 🎯 Executive Summary

### The Transformation

This plan eliminates hybrid control flow ambiguity across the entire CORTEX architecture by implementing a pure autonomous system where Python owns all execution logic and manifests contain only configuration data. The architecture introduces a **Master Orchestrator** - a centralized, machine-readable routing layer that eliminates LLM-dependent brittleness while enabling deterministic orchestrator coordination. The approach is **bootstrapped**: we build Planning System v5 + Master Orchestrator first, then use them to create detailed plans for migrating all other orchestrators and agents.

### Why Master Orchestrator?

**Problem:** Current intent routing via `CORTEX.prompt.md` is LLM-dependent, creating brittleness and unpredictability. No orchestrator-to-orchestrator communication exists. **No cross-session context preservation.**

**Solution:** Master Orchestrator + Cross-Session Context Middleware provides:
- **Machine-Readable Routing:** Pure pattern matching via YAML config (no LLM interpretation)
- **Orchestrator Registry:** Centralized discovery and lifecycle management
- **State Coordination:** Cross-orchestrator state sharing via PlanningStateDB
- **Execution Engine:** Autonomous orchestrator invocation with monitoring
- **Hybrid Fallback:** LLM classifier for edge cases, pattern matching for 90%+ of requests
- **🆕 Cross-Session Memory:** Lightweight context injection from Tier 1 Working Memory (last 3 sessions)
- **🆕 Continuation Intelligence:** Automatic "continue" detection routes to last-used orchestrator

**Architecture:**
```
User Input → Context Middleware (Tier 1 Query) → Master Orchestrator (Pattern Match) → Orchestrator Execution
                  ↓ ("continue" detected)              ↓ (no match)
              Last 3 Sessions Metadata            LLM Classifier (Fallback)
                  ↓
              Inject into context (200 tokens)
```

### Why Bootstrap?

**Problem:** We need Planning System v5 to create high-quality, structured plans for complex migrations, but Planning System v5 doesn't exist yet.

**Solution:** Build Planning System v5 using the current manual planning approach (this document), then immediately use the newly created v5 system to plan all remaining migrations with proper folder structure, progress tracking, and validation.

### Success Criteria

**Bootstrap Phase:**
- ✅ Master Orchestrator routing layer operational (pattern matching + LLM fallback)
- ✅ Planning System v5 operational with MCP tool integration
- ✅ SQLite state database functioning with ACID transactions
- ✅ BaseOrchestrator v4.1 supporting config-driven execution
- ✅ Planning orchestrator generates plans with proper structure
- ✅ Zero execution ambiguity in new planning system
- ✅ Orchestrator registry supports dependency chains
- ✅ Cross-orchestrator state sharing functional
- 🆕 **Cross-Session Context Middleware operational (Tier 1 integration)**
- 🆕 **"Continue" pattern detection routes to last orchestrator automatically**
- 🆕 **Session metadata tracked (orchestrator_used, primary_intent) in Tier 1**
- 🆕 **Context injection adds <200 tokens per request (lightweight)**

**Migration Phase:**
- ✅ All 4 AUTONOMOUS orchestrators migrated (ADO, Vacuum, Cleanup)
- ✅ All 4 GUIDED orchestrators assessed and transformed where beneficial
- ✅ Agent layer integrated with MCP protocol
- ✅ 100% test coverage for new implementations
- ✅ All plans resumable from any phase
- ✅ Single source of truth via database state

---

## 🏗️ Phase 0: Foundation Setup (1 day)

**Goal:** Establish project structure, filename standards, and baseline documentation

### Task 0.1: Project Structure Creation
**Duration:** 2h

Create implementation directories:
```
src/
├── mcp/                         # MCP protocol layer (new)
├── database/                    # SQLite schemas (new)
│   ├── planning_state.db
│   └── migrations/
├── orchestrators/
│   ├── base_orchestrator_v4_1.py (new)
│   ├── master_orchestrator.py (new - Phase 3)
│   ├── pattern_router.py (new - Phase 3)
│   ├── state_manager.py (new - Phase 3)
│   ├── execution_engine.py (new - Phase 3)
│   ├── planning_orchestrator_v5.py (new)
│   └── ...existing...
└── utils/
    └── file_name.py (new)

cortex-brain/
├── database/                    # Database storage (new)
└── config/
    ├── mcp-server.yaml (new)
    └── master-orchestrator.yaml (new - Phase 3)

tests/
├── mcp/ (new)
├── database/ (new)
├── orchestrators/
│   └── test_planning_v5.py (new)
└── integration/ (new)
```

**Deliverables:**
- Empty directory structure with `.gitkeep` files
- `context/project-structure.md` documenting organization

### Task 0.2: Filename Validation Utility
**Duration:** 3h

Implement strict filename standards (≤20 chars, kebab-case):

**Files to Create:**
- `src/utils/file_name.py` - Validation and suggestion logic
- `tests/utils/test_file_name.py` - 100% coverage tests

**Functions:**
- `validate_filename(name: str, max_len: int = 20) -> tuple[bool, str]`
- `suggest_filename(long_name: str, max_len: int = 20) -> str`
- `sanitize_filename(name: str) -> str`

**Integration Points:**
- BaseOrchestrator file creation hooks
- Planning folder generation
- All artifact creation utilities

### Task 0.3: Architecture Baseline Documentation
**Duration:** 3h

Document current state for comparison:

**Artifacts to Create:**
- `context/baseline-architecture.md` - Current system state
- `context/brittleness-analysis.md` - Known issues across all components (including LLM-dependent routing)
- `context/orchestrator-inventory.md` - Complete orchestrator catalog
- `context/agent-inventory.md` - All agents and their manifest dependencies

**Content:**
- List all 4 AUTONOMOUS orchestrators with current issues
- List all GUIDED orchestrators with hybrid ambiguity points
- Catalog all agents with configuration sources
- Map state management approaches across system
- Document failure recovery capabilities (or lack thereof)
- **Document current routing mechanism (CORTEX.prompt.md LLM-based) and its brittleness**
- **Identify lack of orchestrator-to-orchestrator communication**
- **Baseline for measuring Master Orchestrator improvements (Phase 3+)**

### Completion Criteria
- ✅ Project structure exists with proper organization
- ✅ Filename utility operational with 100% test coverage
- ✅ Baseline documentation complete and reviewed
- ✅ Git checkpoint created: `checkpoint-phase-0-foundation`

---

## 🔧 Phase 1: MCP Tool Infrastructure (2 days)

**Goal:** Build Model Context Protocol layer for universal orchestrator invocation

**Master Orchestrator Context:** MCP tools provide the universal invocation mechanism that Master Orchestrator will use to execute orchestrators. The OrchestratorRegistry built here will be extended in Phase 3 to support Master Orchestrator's dependency resolution and lifecycle management.

### Task 1.1: MCP Server Foundation
**Duration:** 1d

**Files to Create:**
- `src/mcp/server.py` - MCP v1.0 protocol server
- `src/mcp/__init__.py` - Package initialization
- `tests/mcp/test_server.py` - Server tests

**Implementation:**
- Protocol v1.0 compliance (request/response handling)
- Tool registration system
- Error propagation with context
- Logging and metrics integration
- Graceful shutdown handling

**Validation:**
- MCP protocol compliance tests pass
- Server starts/stops cleanly
- Handles malformed requests without crashing
- Logs all requests with timing

### Task 1.2: Orchestrator Registry
**Duration:** 4h

**Files to Create:**
- `src/mcp/registry.py` - Orchestrator registration and lookup
- `cortex-brain/config/mcp-server.yaml` - Server configuration
- `tests/mcp/test_registry.py` - Registry tests

**Registry Schema:**
```yaml
orchestrators:
  planning_system:
    class: "PlanningOrchestratorV5"
    module: "src.orchestrators.planning_orchestrator_v5"
    config: "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml"
    type: "autonomous"
  ado_operations:
    class: "AdoOrchestratorV2"
    module: "src.orchestrators.ado_orchestrator_v2"
    config: "cortex-brain/manifests/orchestrators/ado-operations-2.0-manifest.yaml"
    type: "autonomous"
```

**Features:**
- Map orchestrator names to Python classes
- Link to config file paths
- Validate orchestrator availability on startup
- Support hot-reload for development
- **Foundation for Master Orchestrator registry (Phase 3 will extend)**

### Task 1.3: Universal Invocation Tool
**Duration:** 4h

**Files to Create:**
- `src/mcp/tools/invoke_orchestrator.py` - Universal invocation tool
- `src/mcp/tools/__init__.py` - Tools package
- `tests/mcp/test_invoke_orchestrator.py` - Tool tests

**Tool Signature:**
```python
@mcp_tool
def invoke_orchestrator(
    orchestrator_name: str,
    user_request: str,
    options: dict = {}
) -> dict:
    """
    Invoke an autonomous orchestrator with user request.
    
    Returns:
        {
            "status": "success|error",
            "orchestrator": "planning_system",
            "execution_time": 3.2,
            "artifacts": ["path/to/plan.md", ...],
            "summary": "Created plan with 5 phases...",
            "progress": {"current_phase": 3, "total_phases": 5}
        }
    """
```

**Integration:**
- Load orchestrator from registry
- Instantiate with config
- Execute with error handling
- Format results for CORTEX display
- Track execution metrics

### Completion Criteria
- ✅ MCP server operational and tested
- ✅ Registry loads orchestrator configs correctly
- ✅ Universal tool invokes orchestrators successfully
- ✅ Error handling prevents crashes
- ✅ **Foundation ready for Master Orchestrator integration (Phase 3)**
- ✅ Git checkpoint created: `checkpoint-phase-1-mcp-infrastructure`

---

## 🗄️ Phase 2: Planning State Database (1.5 days)

**Goal:** Single source of truth for all planning state with ACID transactions

**Master Orchestrator Context:** The PlanningStateDB built here will be used by Master Orchestrator's StateManager (Phase 3) for cross-orchestrator state coordination. The execution_log table will track Master Orchestrator routing decisions and orchestrator lifecycle events.

### Task 2.1: Database Schema Implementation
**Duration:** 6h

**Files to Create:**
- `src/database/planning_state_schema.sql` - Complete schema
- `src/database/planning_state_db.py` - Database manager class
- `src/database/__init__.py` - Package initialization
- `tests/database/test_planning_state_db.py` - Database tests

**Tables to Implement:**
1. `plans` - High-level plan metadata
2. `phases` - Individual execution phases
3. `tasks` - Granular tasks within phases
4. `artifacts` - Registry of generated files
5. `validations` - Checkpoint results
6. `state_snapshots` - Point-in-time captures
7. **`execution_log` - Orchestrator execution tracking (includes Master Orch routing)**
8. **`shared_state` - Cross-orchestrator state (for Master Orch StateManager - Phase 3)**

**Key Features:**
- Foreign key relationships with CASCADE
- Indexes for query performance
- JSON fields for extensibility
- CHECK constraints for valid states
- Timestamps with timezone support

### Task 2.2: Database Manager Class
**Duration:** 6h

**Implementation:**
```python
class PlanningStateDB:
    def create_plan(self, feature_name: str, metadata: dict) -> str
    def start_phase(self, plan_id: str, phase_number: int, config: dict) -> str
    def complete_phase(self, phase_id: str) -> bool
    def fail_phase(self, phase_id: str, error: str) -> bool
    def create_task(self, phase_id: str, description: str) -> str
    def register_artifact(self, plan_id: str, path: str, type: str) -> str
    def create_snapshot(self, plan_id: str, phase_id: str, data: dict) -> str
    def get_plan_status(self, plan_id: str) -> dict
    def resume_from_snapshot(self, snapshot_id: str) -> dict
```

**Transaction Support:**
- Context manager for automatic commit/rollback
- Savepoints for nested transactions
- Explicit transaction control methods

### Task 2.3: Migration System
**Duration:** 4h

**Files to Create:**
- `src/database/migrations/001_initial_schema.sql`
- `src/database/migration_runner.py`
- `tests/database/test_migrations.py`

**Features:**
- Version tracking in `schema_migrations` table
- Idempotent migrations (safe to re-run)
- Rollback support
- Migration validation before apply

### Completion Criteria
- ✅ Database schema created and tested
- ✅ All CRUD operations functional
- ✅ Transactions properly isolate changes
- ✅ Rollback works correctly on errors
- ✅ Migration system operational
- ✅ 100% test coverage for database layer
- ✅ **Execution tracking tables ready for Master Orchestrator (Phase 3)**
- ✅ Git checkpoint created: `checkpoint-phase-2-state-database`

---

## 🏛️ Phase 3: BaseOrchestrator v4.1 + Master Orchestrator Core (2.5 days)

**Goal:** Config-driven orchestrator base class with template rendering + Centralized routing layer

**MAJOR ADDITION:** This phase now includes the **Master Orchestrator Core** - a machine-readable, pattern-based routing layer that eliminates LLM-dependent brittleness and enables deterministic orchestrator coordination. This is a critical architectural component that provides centralized orchestrator management, state coordination, and hybrid routing (pattern matching primary, LLM fallback).

### Task 3.1: Core Base Class
**Duration:** 8h

**Files to Create:**
- `src/orchestrators/base_orchestrator_v4_1.py` - New base class
- `tests/orchestrators/test_base_orchestrator_v4_1.py` - Tests

**Key Methods:**
```python
class BaseOrchestratorV4_1:
    def __init__(self, config_path: str, db: PlanningStateDB)
    def load_config(self) -> dict
    def execute(self, user_request: str) -> OrchestratorResult
    def execute_phase(self, phase_config: dict) -> PhaseResult
    def render_template(self, template_name: str, data: dict) -> str
    def create_artifact(self, path: str, content: str, type: str) -> str
    def validate_phase(self, phase_id: str, validations: list) -> ValidationResult
    def create_checkpoint(self, phase_id: str) -> str
    def rollback_to_checkpoint(self, snapshot_id: str) -> bool
```

**Configuration Loading:**
- YAML parsing with schema validation
- Environment variable substitution
- Config inheritance (from parent orchestrators)
- Validation against manifest schema

### Task 3.2: Template System Integration
**Duration:** 4h

**Integration with Jinja2:**
- Template discovery from config
- Context injection (plan data, user request, system state)
- Custom filters for CORTEX-specific formatting
- Error handling for missing variables

**Template Locations:**
```
cortex-brain/templates/
├── planning/
│   ├── master-plan.jinja2
│   ├── progress-tracker.json.jinja2
│   └── phase-report.md.jinja2
├── ado/
└── common/
    ├── header.jinja2
    └── footer.jinja2
```

### Task 3.3: Progress Tracking + Session Management
**Duration:** 6h

**Implementation:**
- Real-time progress updates to database
- Progress bar generation for visual tracking
- Percentage calculations across phases
- Estimated vs actual time tracking
- Status change notifications
- **Session continuation prompt generation (NEW)**
- **Token usage monitoring (NEW)**

**Session Management Features:**

```python
class BaseOrchestratorV4_1:
    # ... existing methods ...
    
    def update_continuation_prompt(self, phase_id: str) -> None:
        """Update CONTINUATION-PROMPT.md after phase completion."""
        plan_state = self.state_db.get_plan_status(self.plan_id)
        context = {
            'plan_name': plan_state['name'],
            'timestamp': datetime.now().isoformat(),
            'completed_phases': plan_state['completed_phases'],
            'total_phases': plan_state['total_phases'],
            'progress_percentage': plan_state['progress_percentage'],
            'current_phase': plan_state['current_phase'],
            'next_phase': plan_state['next_phase'],
            'checkpoints': self._get_git_checkpoints(),
            'plan_id': self.plan_id,
            'database_status': plan_state['status'],
            'last_checkpoint_commit': self._get_last_checkpoint()
        }
        
        prompt_content = self.render_template(
            'continuation-prompt.jinja2', 
            context
        )
        
        prompt_path = f"{self.plan_dir}/tracking/CONTINUATION-PROMPT.md"
        with open(prompt_path, 'w') as f:
            f.write(prompt_content)
    
    def check_token_usage(self) -> dict:
        """Monitor conversation token usage (requires Copilot API access)."""
        # NOTE: This requires Copilot Chat API integration
        # For now, returns estimated usage based on phase count
        return {
            'estimated_tokens': self._estimate_tokens(),
            'threshold': 80000,
            'should_warn': self._estimate_tokens() > 80000,
            'continuation_prompt_path': f"{self.plan_dir}/tracking/CONTINUATION-PROMPT.md"
        }
    
    def _estimate_tokens(self) -> int:
        """Rough token estimation based on conversation length."""
        # Heuristic: ~1000 tokens per phase interaction
        completed_phases = self.state_db.get_completed_phase_count(self.plan_id)
        return completed_phases * 1000
```

**Automation Strategy:**

1. **Automatic Generation:** 
   - `update_continuation_prompt()` called after each phase completion
   - Triggered in `complete_phase()` method
   - File always up-to-date for session handoff

2. **Token Monitoring:**
   - **Current Limitation:** Copilot Chat doesn't expose token usage via API
   - **Phase 7 Enhancement:** Integrate with Copilot Chat API if available
   - **Fallback:** Manual monitoring via phase count heuristic
   - **User Warning:** Display prompt path when estimated tokens > 80k

3. **Manual Handoff (Phase 4-6):**
   ```python
   # In phase completion
   self.update_continuation_prompt(phase_id)
   if self.check_token_usage()['should_warn']:
       print(f"⚠️ Token limit approaching. Use continuation prompt:")
       print(f"   {self.plan_dir}/tracking/CONTINUATION-PROMPT.md")
   ```

4. **Future Automation (Phase 7+):**
   - Research Copilot Chat Extensions API
   - Implement token usage subscription
   - Auto-display continuation prompt at 80% threshold
   - Potential: Auto-create new chat window with continuation prompt

### Task 3.4: Master Orchestrator Core
**Duration:** 1 day (NEW)

**Files to Create:**
- `src/orchestrators/master_orchestrator.py` - Centralized routing engine
- `cortex-brain/config/master-orchestrator.yaml` - Routing config
- `src/orchestrators/pattern_router.py` - Pattern matching engine
- `src/orchestrators/state_manager.py` - Cross-orchestrator state coordination
- `src/orchestrators/execution_engine.py` - Lifecycle management
- `tests/orchestrators/test_master_orchestrator.py` - Comprehensive routing tests

**Architecture:**
```python
class MasterOrchestrator:
    """Centralized orchestrator routing and lifecycle management."""
    
    def __init__(self, config_path: str, registry: OrchestratorRegistry, 
                 state_db: PlanningStateDB, llm_fallback: Optional[LLMIntentClassifier]):
        self.router = PatternRouter(config_path)
        self.registry = registry
        self.state_manager = StateManager(state_db)
        self.execution_engine = ExecutionEngine()
        self.llm_fallback = llm_fallback
    
    def route_request(self, user_input: str, context: dict) -> OrchestratorMatch:
        """Primary pattern-based routing with LLM fallback."""
        match = self.router.match_intent(user_input)
        if match.confidence < 0.9 and self.llm_fallback:
            match = self.llm_fallback.classify(user_input, context)
        return match
    
    def execute_orchestrator(self, orchestrator_id: str, params: dict) -> ExecutionResult:
        """Lifecycle management for orchestrator execution."""
        orch = self.registry.get(orchestrator_id)
        self.state_manager.begin_execution(orchestrator_id, params)
        
        try:
            result = self.execution_engine.run(
                orchestrator=orch,
                params=params,
                hooks=self._get_lifecycle_hooks(orchestrator_id)
            )
            self.state_manager.complete_execution(orchestrator_id, result)
            return result
        except Exception as e:
            self.state_manager.fail_execution(orchestrator_id, str(e))
            raise
```

**Routing Config (`cortex-brain/config/master-orchestrator.yaml`):**
```yaml
routing_rules:
  - pattern: "^(plan|create a plan|make a plan)$"
    orchestrator: planning_v5
    confidence: 1.0
    match_type: exact
  
  - pattern: "^(tdd|start tdd|run tests)$"
    orchestrator: tdd_orchestrator
    confidence: 1.0
    match_type: exact
  
  - pattern: "^(ado|ado story|ado feature).*$"
    orchestrator: ado_orchestrator
    confidence: 1.0
    match_type: regex
  
  - pattern: "^(sanitize|make generic).*$"
    orchestrator: sanitization_orchestrator
    confidence: 1.0
    match_type: regex
  
  - pattern: "^(maintenance|health check)$"
    orchestrator: maintenance_orchestrator
    confidence: 1.0
    match_type: exact
  
  - pattern: "^(refine|improve).*$"
    orchestrator: refinement_orchestrator
    confidence: 1.0
    match_type: regex

fallback:
  enabled: true
  classifier: llm_intent_classifier
  confidence_threshold: 0.7
  log_unmatched: true

lifecycle_hooks:
  pre_execution:
    - validate_dependencies
    - check_state_conflicts
  post_execution:
    - save_artifacts
    - update_metrics
  on_error:
    - log_failure
    - notify_user
```

**Pattern Router:**
```python
class PatternRouter:
    """Machine-readable pattern matching engine."""
    
    def __init__(self, config_path: str):
        self.rules = self._load_routing_rules(config_path)
    
    def match_intent(self, user_input: str) -> OrchestratorMatch:
        """Match input against routing patterns."""
        for rule in self.rules:
            if rule['match_type'] == 'exact':
                if re.match(rule['pattern'], user_input.strip().lower()):
                    return OrchestratorMatch(
                        orchestrator_id=rule['orchestrator'],
                        confidence=rule['confidence'],
                        match_type='exact'
                    )
            elif rule['match_type'] == 'regex':
                if re.search(rule['pattern'], user_input, re.IGNORECASE):
                    return OrchestratorMatch(
                        orchestrator_id=rule['orchestrator'],
                        confidence=rule['confidence'],
                        match_type='regex'
                    )
        
        return OrchestratorMatch(orchestrator_id=None, confidence=0.0, match_type='none')
```

**State Manager:**
```python
class StateManager:
    """Cross-orchestrator state coordination via PlanningStateDB."""
    
    def __init__(self, db: PlanningStateDB):
        self.db = db
    
    def begin_execution(self, orchestrator_id: str, params: dict) -> int:
        """Create execution log entry."""
        return self.db.log_execution(orchestrator_id, 'started', params)
    
    def share_state(self, from_orch: str, to_orch: str, data: dict) -> None:
        """Enable orchestrator-to-orchestrator data sharing."""
        self.db.save_artifact(from_orch, 'shared_state', data, destination=to_orch)
    
    def get_shared_state(self, orchestrator_id: str) -> dict:
        """Retrieve state shared by other orchestrators."""
        return self.db.get_artifacts_for(orchestrator_id)
```

**Execution Engine:**
```python
class ExecutionEngine:
    """Orchestrator lifecycle management with hooks."""
    
    def run(self, orchestrator: BaseOrchestrator, params: dict, 
            hooks: dict) -> ExecutionResult:
        """Execute orchestrator with lifecycle hooks."""
        # Pre-execution hooks
        for hook in hooks.get('pre_execution', []):
            self._execute_hook(hook, orchestrator, params)
        
        # Main execution
        result = orchestrator.execute_autonomous()
        
        # Post-execution hooks
        for hook in hooks.get('post_execution', []):
            self._execute_hook(hook, orchestrator, result)
        
        return result
```

**Integration with Phase 1-2:**
- Reuses `OrchestratorRegistry` from Phase 1 (MCP tools)
- Reuses `PlanningStateDB` from Phase 2 (state persistence)
- Extends registry for dependency resolution
- Adds orchestrator lifecycle tracking to database

**Testing Strategy:**
- Unit tests: Pattern matching (exact/regex), config validation, lifecycle hooks
- Integration tests: End-to-end routing for all 6 orchestrators, state sharing, fallback scenarios
- Performance tests: Routing latency (<100ms), config reload (<50ms)
- Edge cases: No match (LLM fallback), conflicting patterns, dependency chains

### Completion Criteria
- ✅ BaseOrchestrator v4.1 fully functional
- ✅ Config loading works with validation
- ✅ Template rendering produces correct output
- ✅ Progress tracking updates database correctly
- ✅ Checkpoints and rollback work properly
- ✅ **Master Orchestrator routing operational (pattern matching + LLM fallback)**
- ✅ **Orchestrator registry supports dependency resolution**
- ✅ **Cross-orchestrator state sharing functional**
- ✅ **All 6 orchestrators routable via YAML config**
- ✅ 100% test coverage for base class and routing layer
- ✅ Git checkpoint created: `checkpoint-phase-3-base-orchestrator-master-orch`

---

## 🧠 Phase 4: Planning Orchestrator v5 + Master Orchestrator Integration (2 days)

**Goal:** Pure autonomous planning orchestrator with zero natural language in manifest + First Master Orchestrator client

**INTEGRATION:** Planning v5 becomes the first orchestrator to integrate with Master Orchestrator, validating the routing layer and state coordination mechanisms.

### Task 4.1: Planning Orchestrator Implementation
**Duration:** 1d

**Files to Create:**
- `src/orchestrators/planning_orchestrator_v5.py` - Pure Python implementation
- `tests/orchestrators/test_planning_orchestrator_v5.py` - Comprehensive tests

**Core Capabilities:**
```python
class PlanningOrchestratorV5(BaseOrchestratorV4_1):
    def discover_context(self, user_request: str) -> ContextResult
    def analyze_architecture(self, context: ContextResult) -> ArchitectureAnalysis
    def generate_plan(self, analysis: ArchitectureAnalysis) -> PlanDocument
    def create_folder_structure(self, plan: PlanDocument) -> FolderStructure
    def validate_plan(self, plan: PlanDocument) -> ValidationResult
    def execute(self, user_request: str) -> OrchestratorResult
```

**Execution Flow:**
1. Parse user request (extract feature name, complexity hints)
2. Create plan in database (status: 'active')
3. **Phase 0: Context Discovery** - Search workspace for relevant files
4. **Phase 1: Architecture Analysis** - AST parsing, dependency analysis
5. **Phase 2: Plan Generation** - Template-driven markdown creation
6. **Phase 3: Folder Creation** - Atomic filesystem operations
7. **Phase 4: Validation** - Automated checks (structure, content, references)
8. Update database (status: 'completed')
9. Return execution summary

**No Natural Language:** All decisions in Python code, no manifest interpretation.

### Task 4.2: Config-Only Manifest
**Duration:** 4h

**Files to Create:**
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`

**Manifest Structure (Configuration Only):**
```yaml
schema_version: "5.0"
orchestrator:
  name: "planning_system"
  version: "5.0"
  type: "autonomous"
  
folder_structure:
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  subfolders:
    - "context"
    - "artifacts"
    - "reports"
    - "tracking"
  required_files:
    - "tracking/progress-tracker.json"
    - "tracking/CONTINUATION-PROMPT.md"  # Session handoff for token limit

context_discovery:
  search_patterns:
    - pattern: "class.*"
      file_types: ["*.py"]
      scope: "src/"
    - pattern: "def test_"
      file_types: ["*.py"]
      scope: "tests/"

output_templates:
  master_plan: "templates/planning/master-plan.jinja2"
  progress_tracker: "templates/planning/progress-tracker.json.jinja2"
  context_summary: "templates/planning/context-summary.md.jinja2"

validation:
  required_files:
    - "00-master-plan.md"
    - "README.md"
    - "tracking/progress-tracker.json"
    - "tracking/CONTINUATION-PROMPT.md"  # Session handoff
  required_sections:
    - "Visual Progress Tracker"
    - "Executive Summary"
    - "Implementation Phases"

session_management:
  continuation_prompt:
    enabled: true
    update_frequency: "after_each_phase"
    template: "templates/planning/continuation-prompt.jinja2"
    token_warning_threshold: 80000  # Warn at 80% of typical limit
```

**Zero Natural Language:** Only data structures, no commands.

### Task 4.3: Template Creation
**Duration:** 4h

**Files to Create:**
- `cortex-brain/templates/planning/master-plan.jinja2`
- `cortex-brain/templates/planning/progress-tracker.json.jinja2`
- `cortex-brain/templates/planning/README.md.jinja2`
- `cortex-brain/templates/planning/context-summary.md.jinja2`
- `cortex-brain/templates/planning/continuation-prompt.jinja2` **(NEW - Session handoff)**

**Template Features:**
- Dynamic progress bar generation
- Phase table rendering with status indicators
- Automatic timestamp insertion
- Context data injection
- Cross-reference generation

**Continuation Prompt Template Structure:**
```jinja2
# 🔄 CORTEX Plan Continuation Prompt

**Plan:** {{ plan_name }}
**Last Updated:** {{ timestamp }}
**Progress:** {{ completed_phases }}/{{ total_phases }} phases ({{ progress_percentage }}%)
**Token Usage Context:** This prompt enables seamless continuation across chat sessions.

---

## 📋 Quick Context

**What we're building:** {{ feature_description }}

**Completed Phases:**
{% for phase in completed_phases_list %}
- ✅ Phase {{ phase.number }}: {{ phase.name }} ({{ phase.duration }})
{% endfor %}

**Current Phase:** {{ current_phase.number }}: {{ current_phase.name }}
**Next Phase:** {{ next_phase.number }}: {{ next_phase.name }}

---

## 🎯 Continuation Instructions

**Copy this prompt into a new Copilot Chat window:**

```
Follow instructions in CORTEX.prompt.md.

Continue executing plan: {{ plan_name }}
Location: cortex-brain/documents/planning/active/{{ plan_name }}/

Context:
- We are at Phase {{ current_phase.number }}: {{ current_phase.name }}
- {{ completed_phases }}/{{ total_phases }} phases complete
- Last checkpoint: {{ last_checkpoint_commit }}
- Database state: {{ database_status }}

Next Action: {{ next_action }}

Refer to 00-master-plan.md for full context. Use planning database for state:
python -c "from src.database.planning_state_db import PlanningStateDB; db = PlanningStateDB(); print(db.get_plan_status('{{ plan_id }}'))"
```

---

## 📊 State Summary

**Git Checkpoints:**
{% for checkpoint in checkpoints %}
- {{ checkpoint.commit }}: {{ checkpoint.description }}
{% endfor %}

**Database State:**
- Plan ID: {{ plan_id }}
- Status: {{ plan_status }}
- Active phase: {{ current_phase.number }}
- Artifacts generated: {{ artifact_count }}

**Key Files:**
- Plan: `{{ plan_path }}/00-master-plan.md`
- Tracker: `{{ plan_path }}/tracking/progress-tracker.json`
- Database: `cortex-brain/database/planning_state.db`

---

## ⚠️ Important Notes

1. **State Recovery:** All plan state is in PlanningStateDB - query it first
2. **Git History:** Check `git log --oneline | head -10` for recent checkpoints
3. **Phase Dependencies:** Refer to master plan for phase dependencies
4. **Testing:** Run tests before marking phases complete

**Last Updated:** {{ timestamp }} | **Auto-generated after Phase {{ last_completed_phase }}**
```

**Update Triggers:**
- After each phase completion
- Before creating git checkpoint
- When progress tracker updates
- Manual: `orchestrator.update_continuation_prompt()`

### Task 4.4: Master Orchestrator Integration (NEW)
**Duration:** 4h

**Integration Steps:**
1. Register Planning v5 in `master-orchestrator.yaml` with patterns
2. Implement `PlanningOrchestratorV5.get_registration_config()` for self-registration
3. Add state coordination with Master Orchestrator's StateManager
4. Test routing from user input → Master Orchestrator → Planning v5
5. Validate lifecycle hooks (pre/post execution, error handling)

**Registration Config:**
```python
class PlanningOrchestratorV5(BaseOrchestratorV4_1):
    @staticmethod
    def get_registration_config() -> dict:
        return {
            'orchestrator_id': 'planning_v5',
            'patterns': [
                {'pattern': r'^(plan|create a plan|make a plan)$', 'match_type': 'exact', 'confidence': 1.0}
            ],
            'dependencies': ['mcp_tools', 'planning_state_db'],
            'lifecycle_hooks': {
                'pre_execution': ['validate_workspace'],
                'post_execution': ['save_plan_artifact']
            }
        }
```

**Testing:**
- End-to-end: User input "plan feature X" → Routed to Planning v5 → Plan generated
- State sharing: Planning v5 shares context with other orchestrators via StateManager
- Error handling: Failed planning execution logged correctly

### Completion Criteria
- ✅ Planning Orchestrator v5 generates complete plans
- ✅ Plans have proper folder structure (4 subfolders)
- ✅ Database tracks all phases and artifacts
- ✅ Templates render correctly with injected data
- ✅ Validation catches missing required content
- ✅ **Planning v5 integrated with Master Orchestrator (routing + state sharing)**
- ✅ **End-to-end routing test passes**
- ✅ **CORTEX.prompt.md updated: Planning v5 routes via Master Orchestrator (LIVE)**
- ✅ **Master Orchestrator ACTIVE for planning commands ("plan", "create a plan")**
- ✅ **Continuation prompt template renders correctly**
- ✅ **CONTINUATION-PROMPT.md generated in tracking/ folder**
- ✅ **Token warning displays when approaching limit (80k threshold)**
- ✅ **Copy-paste prompt successfully recreates context in new chat**
- ✅ 100% test coverage for orchestrator
- ✅ Manual test: Generate a sample plan successfully
- ✅ Git checkpoint created: `checkpoint-phase-4-planning-v5-master-orch`

---

## 🔗 Phase 4.5: Cross-Session Context Middleware (2 days) 🎯 IMMEDIATE

**Goal:** Enable Master Orchestrator to track user context across multiple chat sessions via Tier 1 Working Memory integration

**Status:** 🎯 **IMMEDIATE ACTIVATION** - Executes immediately after Phase 4 completion

**Architectural Rationale:** 

The proposal emerged from recognizing a critical gap: CORTEX can lose track of what users were working on when chat sessions restart. By integrating Tier 1 Working Memory (which tracks the last 70 conversations) with Master Orchestrator, we enable **lightweight context injection** that preserves continuity without token bloat.

**Key Design Decisions:**
- ✅ **Context Middleware Pattern:** Pre-routing enrichment keeps Master Orchestrator focused (separation of concerns)
- ✅ **Metadata-Only Injection:** <200 tokens vs 50k+ for full conversation text (99.6% efficiency gain)
- ✅ **Tier 1 Integration:** Leverage existing SQLite conversation tracking (no new database)
- ✅ **Continuation Intelligence:** "continue" + last orchestrator metadata = automatic routing

**Architecture Enhancement:**
```
User Input → CrossSessionContextMiddleware → Master Orchestrator → Orchestrator Execution
               ↓ ("continue" detected)              ↓
           Query Tier 1 (last 3 sessions)    Route to last orchestrator
               ↓
           Inject metadata context (200 tokens)
```

---

### Task 4.5.1: Extend Tier 1 Working Memory Schema (4h)

**Goal:** Add orchestrator tracking to Tier 1 session management

**Database Schema Changes:**
```sql
-- Add to existing sessions table
ALTER TABLE sessions ADD COLUMN orchestrator_used TEXT;
ALTER TABLE sessions ADD COLUMN primary_intent TEXT;
ALTER TABLE sessions ADD COLUMN artifacts_generated TEXT;  -- JSON array of artifact IDs

-- Index for fast lookups
CREATE INDEX idx_sessions_orchestrator ON sessions(orchestrator_used);
CREATE INDEX idx_sessions_timestamp ON sessions(created_at DESC);
```

**Python API Updates:**
```python
# src/tier1/sessions.py

class SessionManager:
    def record_orchestrator_usage(
        self,
        session_id: str,
        orchestrator: str,
        intent: str,
        artifacts: List[str] = None
    ) -> bool:
        """Record which orchestrator handled this session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions
            SET orchestrator_used = ?,
                primary_intent = ?,
                artifacts_generated = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (orchestrator, intent, json.dumps(artifacts or []), session_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_recent_session_context(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get lightweight metadata for last N sessions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                session_id,
                orchestrator_used,
                primary_intent,
                artifacts_generated,
                created_at
            FROM sessions
            WHERE orchestrator_used IS NOT NULL
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": row["session_id"],
                "orchestrator": row["orchestrator_used"],
                "intent": row["primary_intent"],
                "artifacts": json.loads(row["artifacts_generated"] or "[]"),
                "timestamp": row["created_at"]
            }
            for row in rows
        ]
```

**Migration Script:**
```python
# src/database/migrations/tier1_add_orchestrator_tracking.py

def migrate():
    """Add orchestrator tracking to Tier 1 sessions."""
    db_path = Path("cortex-brain/tier1/working_memory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add columns
    cursor.execute("ALTER TABLE sessions ADD COLUMN orchestrator_used TEXT")
    cursor.execute("ALTER TABLE sessions ADD COLUMN primary_intent TEXT")
    cursor.execute("ALTER TABLE sessions ADD COLUMN artifacts_generated TEXT")
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_sessions_orchestrator ON sessions(orchestrator_used)")
    cursor.execute("CREATE INDEX idx_sessions_timestamp ON sessions(created_at DESC)")
    
    conn.commit()
    conn.close()
```

**Testing:**
- Unit tests: `record_orchestrator_usage()` updates session correctly
- Unit tests: `get_recent_session_context()` returns last 3 sessions
- Integration test: Session creation → Orchestrator execution → Metadata recorded → Query returns correct data

**Deliverables:**
- ✅ Tier 1 schema updated (3 new columns, 2 indexes)
- ✅ `SessionManager.record_orchestrator_usage()` implemented
- ✅ `SessionManager.get_recent_session_context()` implemented
- ✅ Migration script created and tested
- ✅ 100% test coverage for new APIs

---

### Task 4.5.2: Build Cross-Session Context Middleware (8h)

**Goal:** Create middleware layer that detects continuation patterns and injects Tier 1 context

**File:** `src/orchestrators/context_middleware.py`

**Implementation:**
```python
"""
Cross-Session Context Middleware.

Pre-routing enrichment layer that injects lightweight session context
from Tier 1 Working Memory into Master Orchestrator requests.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.tier1.working_memory import WorkingMemory


class CrossSessionContextMiddleware:
    """
    Middleware for cross-session context injection.
    
    Detects continuation patterns and enriches routing requests with
    lightweight session metadata from Tier 1 Working Memory.
    
    Architecture:
        User Input → Middleware (continuation detection)
                  ↓
              Query Tier 1 (last 3 sessions)
                  ↓
              Inject metadata (<200 tokens)
                  ↓
              Pass to Master Orchestrator
    
    Usage:
        middleware = CrossSessionContextMiddleware()
        enriched_context = middleware.enrich_context(
            user_input="continue",
            existing_context={}
        )
        master_orch.handle_request(user_input, enriched_context)
    """
    
    # Continuation patterns (same as ExecutionModeDetector for consistency)
    CONTINUATION_PATTERNS = [
        r'\bcontinue\b',
        r'\bresume\b',
        r'\bkeep going\b',
        r'\bnext phase\b',
        r'\bproceed\b',
        r'\bcontinue with\b',
        r'\bresume execution\b',
        r'\bnext\b'
    ]
    
    def __init__(self, tier1_instance: Optional[WorkingMemory] = None):
        """
        Initialize context middleware.
        
        Args:
            tier1_instance: Optional Tier 1 Working Memory instance.
                          If None, creates default instance.
        """
        self.tier1 = tier1_instance or WorkingMemory()
        self.logger = logging.getLogger("cortex.orchestrators.context_middleware")
        
        # Compile continuation patterns for performance
        self._continuation_regex = re.compile(
            '|'.join(self.CONTINUATION_PATTERNS),
            re.IGNORECASE
        )
        
        self.logger.info("CrossSessionContextMiddleware initialized")
    
    def enrich_context(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enrich routing context with cross-session metadata if continuation detected.
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Enriched context dict with 'recent_activity' if continuation detected,
            otherwise returns existing_context unchanged
        """
        context = existing_context or {}
        
        # Check if continuation pattern detected
        if not self._is_continuation(user_input):
            self.logger.debug("No continuation pattern detected")
            return context
        
        self.logger.info("Continuation pattern detected, injecting session context")
        
        # Query Tier 1 for recent sessions
        recent_sessions = self.tier1.session_manager.get_recent_session_context(limit=3)
        
        if not recent_sessions:
            self.logger.warning("No recent sessions found in Tier 1")
            return context
        
        # Inject lightweight metadata
        context['recent_activity'] = recent_sessions
        context['continuation_detected'] = True
        context['context_source'] = 'tier1_working_memory'
        
        self.logger.info(
            f"Injected {len(recent_sessions)} session(s) metadata "
            f"(last orchestrator: {recent_sessions[0]['orchestrator']})"
        )
        
        return context
    
    def _is_continuation(self, user_input: str) -> bool:
        """Check if user input matches continuation patterns."""
        return bool(self._continuation_regex.search(user_input))
    
    def get_last_orchestrator(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get last used orchestrator if continuation detected.
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Orchestrator ID from last session, or None if not continuation
        """
        enriched = self.enrich_context(user_input, existing_context)
        
        if 'recent_activity' in enriched and enriched['recent_activity']:
            return enriched['recent_activity'][0]['orchestrator']
        
        return None
```

**Testing:**
```python
# tests/orchestrators/test_context_middleware.py

def test_continuation_detection():
    """Test continuation pattern matching."""
    middleware = CrossSessionContextMiddleware()
    
    # Should detect
    assert middleware._is_continuation("continue")
    assert middleware._is_continuation("resume execution")
    assert middleware._is_continuation("keep going with the plan")
    assert middleware._is_continuation("next phase")
    
    # Should NOT detect
    assert not middleware._is_continuation("plan user auth")
    assert not middleware._is_continuation("run tests")

def test_context_enrichment_with_continuation(mock_tier1):
    """Test context enrichment when continuation detected."""
    middleware = CrossSessionContextMiddleware(tier1_instance=mock_tier1)
    
    # Mock recent sessions
    mock_tier1.session_manager.get_recent_session_context.return_value = [
        {
            "session_id": "session-123",
            "orchestrator": "planning_v5",
            "intent": "plan user authentication",
            "artifacts": ["plan-001", "plan-002"],
            "timestamp": "2026-01-02T10:15:00Z"
        }
    ]
    
    context = middleware.enrich_context("continue", {})
    
    assert "recent_activity" in context
    assert context["continuation_detected"] is True
    assert len(context["recent_activity"]) == 1
    assert context["recent_activity"][0]["orchestrator"] == "planning_v5"

def test_no_enrichment_without_continuation():
    """Test that context unchanged when no continuation detected."""
    middleware = CrossSessionContextMiddleware()
    
    original = {"existing": "data"}
    context = middleware.enrich_context("plan feature X", original)
    
    assert context == original
    assert "recent_activity" not in context
```

**Deliverables:**
- ✅ `CrossSessionContextMiddleware` implemented (250 lines)
- ✅ Continuation pattern detection with regex compilation
- ✅ Tier 1 query integration
- ✅ Context enrichment logic (<200 tokens injected)
- ✅ 100% test coverage (pattern detection, enrichment, edge cases)

---

### Task 4.5.3: Integrate Middleware with Master Orchestrator (4h)

**Goal:** Update Master Orchestrator to use context middleware before routing

**File Updates:** `src/orchestrators/master_orchestrator.py`

**Changes:**
```python
from src.orchestrators.context_middleware import CrossSessionContextMiddleware

class MasterOrchestrator:
    def __init__(
        self,
        config_path: str,
        registry: OrchestratorRegistry,
        state_db: PlanningStateDB,
        llm_fallback: Optional[Any] = None,
        context_middleware: Optional[CrossSessionContextMiddleware] = None  # NEW
    ):
        # ...existing init...
        
        # Initialize context middleware
        self.context_middleware = context_middleware or CrossSessionContextMiddleware()
        
        self.logger.info("MasterOrchestrator initialized with context middleware")
    
    def handle_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Route and execute user request with cross-session context awareness.
        
        Enhanced with context middleware for continuation detection.
        """
        self._request_count += 1
        
        # STEP 1: Enrich context with cross-session metadata (NEW)
        enriched_context = self.context_middleware.enrich_context(user_input, context)
        
        # STEP 2: Check if continuation with last orchestrator
        if enriched_context.get('continuation_detected'):
            last_orch = enriched_context['recent_activity'][0]['orchestrator']
            self.logger.info(
                f"Continuation detected → routing to last orchestrator: {last_orch}"
            )
            return self._resume_orchestrator(last_orch, enriched_context)
        
        # STEP 3: Standard pattern-based routing
        match = self.router.match_intent(user_input)
        
        if match and match.confidence >= 0.9:
            self._pattern_match_count += 1
            return self._execute_orchestrator(match, enriched_context)
        
        # STEP 4: LLM fallback if enabled
        if self.llm_fallback:
            self._llm_fallback_count += 1
            return self._llm_route(user_input, enriched_context)
        
        # No match
        return ExecutionResult(
            success=False,
            message="No orchestrator matched the request",
            routing_decision="no_match"
        )
    
    def _resume_orchestrator(
        self,
        orchestrator_id: str,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Resume execution with last orchestrator.
        
        Args:
            orchestrator_id: ID of orchestrator to resume
            context: Enriched context with recent_activity
        
        Returns:
            ExecutionResult from orchestrator execution
        """
        # Get orchestrator from registry
        orchestrator = self.registry.get_orchestrator(orchestrator_id)
        
        if not orchestrator:
            self.logger.error(f"Orchestrator not found for resume: {orchestrator_id}")
            return ExecutionResult(
                success=False,
                message=f"Cannot resume: orchestrator '{orchestrator_id}' not found",
                routing_decision="orchestrator_not_found"
            )
        
        # Execute with context
        self.logger.info(f"Resuming orchestrator: {orchestrator_id}")
        
        result = self.execution_engine.execute(
            orchestrator=orchestrator,
            context=context,
            lifecycle_hooks=self._get_lifecycle_hooks(orchestrator_id)
        )
        
        # Record orchestrator usage in Tier 1
        if result.success and 'session_id' in context:
            self._record_session_metadata(
                session_id=context['session_id'],
                orchestrator=orchestrator_id,
                intent=context.get('user_intent', 'continuation'),
                artifacts=result.artifacts
            )
        
        return result
    
    def _record_session_metadata(
        self,
        session_id: str,
        orchestrator: str,
        intent: str,
        artifacts: List[str]
    ) -> None:
        """Record orchestrator usage in Tier 1 for future continuations."""
        try:
            from src.tier1.working_memory import WorkingMemory
            tier1 = WorkingMemory()
            
            tier1.session_manager.record_orchestrator_usage(
                session_id=session_id,
                orchestrator=orchestrator,
                intent=intent,
                artifacts=artifacts
            )
            
            self.logger.debug(f"Recorded session metadata: {orchestrator}")
        
        except Exception as e:
            self.logger.error(f"Failed to record session metadata: {e}")
```

**Testing:**
```python
# tests/orchestrators/test_master_orchestrator_context.py

def test_continuation_routing_to_last_orchestrator(mock_registry, mock_tier1):
    """Test that 'continue' routes to last used orchestrator."""
    master = MasterOrchestrator(
        config_path="test-config.yaml",
        registry=mock_registry,
        state_db=mock_db,
        context_middleware=CrossSessionContextMiddleware(tier1_instance=mock_tier1)
    )
    
    # Mock recent session
    mock_tier1.session_manager.get_recent_session_context.return_value = [
        {
            "session_id": "session-123",
            "orchestrator": "planning_v5",
            "intent": "plan feature",
            "artifacts": ["plan-001"],
            "timestamp": "2026-01-02T10:15:00Z"
        }
    ]
    
    # Mock orchestrator
    mock_orch = MagicMock()
    mock_registry.get_orchestrator.return_value = mock_orch
    
    result = master.handle_request("continue")
    
    # Verify routing to last orchestrator
    mock_registry.get_orchestrator.assert_called_with("planning_v5")
    assert result.routing_decision == "continuation"

def test_session_metadata_recording(mock_registry, mock_tier1):
    """Test that orchestrator usage recorded in Tier 1."""
    master = MasterOrchestrator(...)
    
    context = {"session_id": "session-456"}
    result = master._execute_orchestrator(match, context)
    
    # Verify Tier 1 recording
    mock_tier1.session_manager.record_orchestrator_usage.assert_called_once_with(
        session_id="session-456",
        orchestrator="planning_v5",
        intent=mock.ANY,
        artifacts=mock.ANY
    )
```

**Deliverables:**
- ✅ Master Orchestrator enhanced with context middleware
- ✅ `_resume_orchestrator()` method implemented
- ✅ Session metadata recording integrated
- ✅ Continuation routing functional
- ✅ 100% test coverage for context-aware routing

---

### Task 4.5.4: Update CORTEX.prompt.md Integration (2h)

**Goal:** Document cross-session context middleware in CORTEX entry point

**File:** `.github/prompts/CORTEX.prompt.md`

**Addition to Intent Router section:**
```markdown
### 🔗 Cross-Session Context Awareness

**Status:** ✅ ACTIVE - Master Orchestrator integrated with Tier 1 Working Memory

**How It Works:**
1. User says "continue", "resume", "keep going", or "next phase"
2. `CrossSessionContextMiddleware` detects continuation pattern
3. Queries Tier 1 for last 3 session metadata (orchestrator_used, intent, artifacts)
4. Injects <200 tokens of lightweight context into routing request
5. Master Orchestrator routes to last-used orchestrator automatically

**Example Flow:**
```
Session 1: User says "plan user authentication" → Planning v5 executes
           → Session metadata recorded in Tier 1

Session 2: User says "continue" → Middleware queries Tier 1
           → Finds last orchestrator: planning_v5
           → Master Orchestrator routes to Planning v5
           → Resumes plan execution
```

**Context Injected (Lightweight):**
```json
{
  "recent_activity": [
    {
      "session_id": "session-20260102-101500",
      "orchestrator": "planning_v5",
      "intent": "plan user authentication",
      "artifacts": ["plan-001", "00-master-plan.md"],
      "timestamp": "2026-01-02T10:15:00Z"
    }
  ],
  "continuation_detected": true,
  "context_source": "tier1_working_memory"
}
```

**Token Efficiency:** 200 tokens (metadata) vs 50,000 tokens (full conversation text) = **99.6% reduction**

**Orchestrators Tracked:** All orchestrators (Planning, ADO, Vacuum, Cleanup, TDD, Debug, etc.)
```

**Deliverables:**
- ✅ CORTEX.prompt.md updated with cross-session documentation
- ✅ Example flows documented
- ✅ Token efficiency metrics included
- ✅ Integration points clarified

---

### Task 4.5.5: End-to-End Validation (4h)

**Goal:** Validate complete cross-session workflow with real scenarios

**Test Scenarios:**

**Scenario 1: Plan → Continue Workflow**
```
Session 1:
User: "plan user authentication feature"
→ Master Orch routes to Planning v5
→ Planning v5 executes, creates plan folder
→ Session metadata recorded: {orchestrator: "planning_v5", intent: "plan user authentication"}

Session 2 (new chat):
User: "continue"
→ Middleware detects continuation
→ Queries Tier 1: finds last orchestrator = "planning_v5"
→ Master Orch routes to Planning v5
→ Planning v5 resumes (loads plan from database)
→ User continues plan execution
```

**Scenario 2: Multi-Orchestrator Switching**
```
Session 1:
User: "plan API migration"
→ Planning v5 executes (metadata recorded)

Session 2:
User: "ado story for API migration"
→ ADO Orchestrator executes (metadata recorded)

Session 3:
User: "continue"
→ Middleware finds last orchestrator = "ado_orchestrator"
→ Master Orch routes to ADO (not Planning)
→ ADO continues work item generation
```

**Scenario 3: Context Enrichment Without Continuation**
```
User: "plan database refactor"
→ No continuation pattern
→ Middleware returns context unchanged
→ Master Orch uses standard pattern routing
→ Planning v5 executes
```

**Validation Checklist:**
- [ ] Continuation pattern detected correctly (8 patterns tested)
- [ ] Tier 1 query returns last 3 sessions
- [ ] Context enriched with <200 tokens
- [ ] Master Orchestrator routes to last orchestrator
- [ ] Session metadata recorded after execution
- [ ] Multi-session workflow preserves context
- [ ] Non-continuation requests unaffected
- [ ] Performance: <50ms middleware overhead

**Performance Benchmarks:**
- Context middleware overhead: <50ms ✓
- Tier 1 query latency: <30ms ✓
- Total routing latency with context: <150ms ✓

**Deliverables:**
- ✅ 3 end-to-end scenarios validated
- ✅ Performance benchmarks met
- ✅ Validation report generated
- ✅ Edge cases tested (no recent sessions, corrupted metadata)

---

### Completion Criteria (Phase 4.5)

- ✅ Tier 1 Working Memory extended with orchestrator tracking (3 columns, 2 indexes)
- ✅ `CrossSessionContextMiddleware` implemented (250 lines, 100% coverage)
- ✅ Master Orchestrator integrated with middleware
- ✅ Continuation routing functional ("continue" → last orchestrator)
- ✅ Session metadata recording operational
- ✅ CORTEX.prompt.md documentation updated
- ✅ End-to-end validation complete (3 scenarios)
- ✅ Performance benchmarks met (<150ms total routing)
- ✅ Token efficiency validated (99.6% reduction)
- ✅ 100% test coverage across all components
- ✅ Git checkpoint created: `checkpoint-phase-4-5-cross-session-context`

**Integration Points Validated:**
- ✅ Tier 1 ↔ Context Middleware (session queries)
- ✅ Context Middleware ↔ Master Orchestrator (context enrichment)
- ✅ Master Orchestrator ↔ Orchestrators (session metadata recording)

**Documentation Deliverables:**
- ✅ `docs/architecture/cross-session-context-middleware.md` (architecture design)
- ✅ `docs/guides/continuation-routing.md` (developer guide)
- ✅ `.github/prompts/CORTEX.prompt.md` (user-facing documentation)

---

## 🚀 Phase 5: Use Planning v5 + Master Orchestrator for Migrations (0.5 days)

**Goal:** Validate Planning System v5 + Master Orchestrator + Cross-Session Context by using them to create detailed migration plans via routing layer

**ROUTING VALIDATION:** All plan generation requests will route through Master Orchestrator with cross-session context awareness

**MASTER ORCHESTRATOR STATUS:** ✅ LIVE - Planning v5 routed via Master Orch (activated Phase 4)

**CROSS-SESSION CONTEXT STATUS:** ✅ LIVE - Continuation routing operational (activated Phase 4.5)

### Task 5.1: Generate ADO Migration Plan
**Duration:** 1h

**Command:** `/CORTEX Plan ADO Orchestrator v2 Migration`

**Routing Flow:** User input → MasterOrchestrator.route_request() → Pattern match "plan" → Planning v5 execution

**Expected Output:**
```
cortex-brain/documents/planning/active/ado-v2-migration/
├── 00-master-plan.md
├── context/
│   ├── ado-v1-analysis.md
│   └── work-item-generation-patterns.md
├── artifacts/
├── reports/
└── tracking/
    └── progress-tracker.json
```

**Validation:**
- Plan includes config-only manifest design
- Work item generation logic documented
- Database integration specified
- Test strategy defined

### Task 5.2: Generate Vacuum Migration Plan
**Duration:** 1h

**Command:** `/CORTEX Plan Vacuum Orchestrator v2 Migration`

**Expected Output:**
```
cortex-brain/documents/planning/active/vacuum-v2-migration/
├── 00-master-plan.md
├── context/
│   ├── filesystem-operations-analysis.md
│   └── safe-deletion-patterns.md
├── artifacts/
├── reports/
└── tracking/
    └── progress-tracker.json
```

### Task 5.3: Generate Cleanup Migration Plan
**Duration:** 1h

**Command:** `/CORTEX Plan Cleanup Orchestrator v2 Migration`

### Task 5.4: Generate GUIDED Orchestrator Assessment Plan
**Duration:** 1h

**Command:** `/CORTEX Plan GUIDED Orchestrators Autonomous Assessment`

**Expected Output:**
- Detailed analysis for TDD, Debug, Sanitization, Refinement
- Decision criteria for autonomous vs guided
- Migration strategy for each orchestrator
- Timeline and dependencies

### Completion Criteria
- ✅ 4 migration plans generated using Planning v5
- ✅ All plans have proper structure
- ✅ Database contains all plan metadata
- ✅ Plans are detailed and actionable
- ✅ Planning v5 successfully used in production
- ✅ Git checkpoint created: `checkpoint-phase-5-migration-plans`

---

## 🔄 Phase 6: Execute Migration Plans (24 days)

**Goal:** Implement all orchestrator migrations using the generated plans

### Execution Strategy

**Use the generated plans as authoritative guides:**
1. Open plan from `cortex-brain/documents/planning/active/{migration-name}/`
2. Execute phases sequentially
3. Update progress in database using Planning v5 APIs
4. Create checkpoints after each phase
5. Generate phase completion reports

**Migration Order:**
1. **ADO Orchestrator v2** (6 days) - Work item generation
2. **Vacuum Orchestrator v2** (5 days) - Filesystem operations
3. **Cleanup Orchestrator v2** (4 days) - Cache management
4. **TDD Orchestrator Assessment** (3 days) - Evaluate autonomous conversion
5. **Debug Orchestrator Assessment** (2 days) - Evaluate autonomous conversion
6. **Sanitization Orchestrator** (2 days) - Evaluate and migrate if beneficial
7. **Refinement Orchestrator** (2 days) - Evaluate and migrate if beneficial

### Task 6.1: ADO Orchestrator v2 Migration
**Duration:** 6 days  
**Plan Reference:** `ado-v2-migration/00-master-plan.md`

**Key Deliverables:**
- Pure Python work item generator
- Config-only manifest
- Database state tracking
- Template-driven outputs
- 100% test coverage

**🔴 ACTIVATION STEP (Day 6):**
1. Add ADO v2 patterns to `master-orchestrator.yaml`:
   ```yaml
   - pattern: "^(ado|ado story|ado feature).*$"
     orchestrator: ado_orchestrator_v2
     confidence: 1.0
     match_type: regex
   ```
2. Register ADO v2 in OrchestratorRegistry
3. Update CORTEX.prompt.md Intent Router: ADO v2 routes via Master Orch
4. Test: "ado story X" → Master Orch routes → ADO v2 executes
5. **Master Orchestrator now handles: Planning v5 + ADO v2**

### Task 6.2: Vacuum Orchestrator v2 Migration
**Duration:** 5 days  
**Plan Reference:** `vacuum-v2-migration/00-master-plan.md`

**Key Deliverables:**
- Atomic filesystem operations
- Safe deletion with rollback
- Transaction boundaries
- Comprehensive logging

**🔴 ACTIVATION STEP (Day 5):**
1. Add Vacuum v2 patterns to `master-orchestrator.yaml`:
   ```yaml
   - pattern: "^(vacuum|deep clean|organize files).*$"
     orchestrator: vacuum_orchestrator_v2
     confidence: 1.0
     match_type: regex
   ```
2. Register Vacuum v2 in OrchestratorRegistry
3. Update CORTEX.prompt.md Intent Router: Vacuum v2 routes via Master Orch
4. Test: "vacuum path/" → Master Orch routes → Vacuum v2 executes
5. **Master Orchestrator now handles: Planning v5 + ADO v2 + Vacuum v2**

### Task 6.3: Cleanup Orchestrator v2 Migration
**Duration:** 4 days  
**Plan Reference:** `cleanup-v2-migration/00-master-plan.md`

**Key Deliverables:**
- Deterministic execution order
- Cache management strategy
- Log rotation automation
- State persistence

**🔴 ACTIVATION STEP (Day 4):**
1. Add Cleanup v2 patterns to `master-orchestrator.yaml`:
   ```yaml
   - pattern: "^(cleanup|clear cache).*$"
     orchestrator: cleanup_orchestrator_v2
     confidence: 1.0
     match_type: regex
   ```
2. Register Cleanup v2 in OrchestratorRegistry
3. Update CORTEX.prompt.md Intent Router: Cleanup v2 routes via Master Orch
4. Test: "cleanup cache" → Master Orch routes → Cleanup v2 executes
5. **Master Orchestrator now handles: Planning v5 + ADO v2 + Vacuum v2 + Cleanup v2**

### Task 6.4: GUIDED Orchestrator Assessments
**Duration:** 9 days  
**Plan Reference:** `guided-orchestrators-assessment/00-master-plan.md`

**Decision Criteria:**
- Complexity of operations (AST parsing, complex analysis → autonomous)
- Workflow simplicity (tool call sequences → remain guided)
- State management needs (multi-phase rollback → autonomous)
- User interaction requirements (approval workflows → guided)

**Likely Outcomes:**
- **TDD Mastery:** Remain GUIDED (workflow benefits from CORTEX interpretation)
- **Debug Orchestrator:** Convert to AUTONOMOUS (complex marker injection)
- **Sanitization:** Convert to AUTONOMOUS (5-phase transformation needs transactions)
- **Refinement:** Remain GUIDED (analysis phases benefit from tool call sequences)

**🔴 ACTIVATION STEPS (Progressive):**

For each orchestrator converted to AUTONOMOUS:
1. Add patterns to `master-orchestrator.yaml` (e.g., TDD: `^(tdd|start tdd|run tests)$`)
2. Register in OrchestratorRegistry
3. Update CORTEX.prompt.md Intent Router (change 📋 GUIDED → 🛡️ AUTONOMOUS)
4. Test routing: command → Master Orch routes → Orchestrator executes
5. Document in routing config

For orchestrators remaining GUIDED:
- Add patterns to `master-orchestrator.yaml` with `type: guided`
- Master Orch routes to CORTEX for manifest interpretation
- CORTEX follows manifest instructions (existing behavior preserved)

**By end of Phase 6, Master Orchestrator handles ALL orchestrators (AUTONOMOUS + GUIDED routing)**

### Completion Criteria
- ✅ All orchestrators migrated per generated plans
- ✅ 100% test coverage for new implementations
- ✅ All plans marked 'completed' in database
- ✅ Migration reports generated
- ✅ Git checkpoints for each orchestrator
- ✅ **Master Orchestrator progressively activated after each migration**
- ✅ **master-orchestrator.yaml contains ALL orchestrator patterns**
- ✅ **CORTEX.prompt.md Intent Router fully updated**
- ✅ **Master Orchestrator routing 100% of orchestrator traffic**
- ✅ Final checkpoint: `checkpoint-phase-6-all-migrations-master-orch-complete`

---

## 🔗 Phase 7: System Integration + Master Orchestrator Final Validation (2 days)

**Goal:** Validate complete Master Orchestrator deployment, finalize system integration, conduct end-to-end testing

**MASTER ORCHESTRATOR STATUS:** ✅ FULLY DEPLOYED - All orchestrators routing via Master Orch (progressively activated Phases 4-6)

**NOTE:** Master Orchestrator is ALREADY LIVE by Phase 7. This phase focuses on validation, optimization, documentation consolidation, and cleanup.

### Task 7.1: Master Orchestrator Deployment Validation (6h)

**Validation Tasks:**

1. **Routing Coverage Audit:**
   - Verify all orchestrators in `master-orchestrator.yaml`
   - Confirm CORTEX.prompt.md Intent Router matches config
   - Test each pattern (exact + regex) with sample inputs
   - Measure pattern match rate (target: 90%+)

2. **Performance Benchmarking:**
   - Routing latency: <100ms for pattern matching ✓
   - Config reload time: <50ms ✓
   - LLM fallback latency: <500ms ✓
   - State coordination overhead: <20ms ✓

3. **LLM Fallback Testing:**
   - Test edge cases that don't match patterns
   - Verify 70% confidence threshold enforcement
   - Confirm LLM classifier routes to correct orchestrator
   - Log fallback rate (target: <10%)

4. **State Coordination Validation:**
   - Test cross-orchestrator state sharing
   - Verify PlanningStateDB integration
   - Confirm lifecycle hooks execute correctly (pre/post execution)
   - Test concurrent orchestrator execution (no state conflicts)

5. **End-to-End Routing Tests:**
   - Test all AUTONOMOUS orchestrators (Planning, ADO, Vacuum, Cleanup, etc.)
   - Test all GUIDED orchestrators (TDD, Debug, Sanitization, Refinement)
   - Verify correct hand-off for 🛡️ AUTONOMOUS (CORTEX stops)
   - Verify correct interpretation for 📋 GUIDED (CORTEX follows manifest)

### Task 7.2: CORTEX.prompt.md Final Documentation (4h)

### Task 7.2: CORTEX.prompt.md Final Documentation (4h)

**Changes Required:**
- Document Master Orchestrator as primary routing mechanism
- Update Intent Router table with final orchestrator versions
- Add Master Orchestrator configuration reference
- Document pattern-based routing + LLM fallback strategy
- Add state coordination examples
- Update hand-off protocol for all orchestrators

**Key Documentation Sections:**

```markdown
## 🔀 Intent Routing (Master Orchestrator)

**Status:** ✅ LIVE - All orchestrators route through Master Orchestrator

**Architecture:**
User Input → MasterOrchestrator.route_request()
  → Pattern Match (90%+) OR LLM Fallback (10%)
  → Orchestrator Execution with lifecycle hooks

**Configuration:** cortex-brain/config/master-orchestrator.yaml

**Routing Coverage:**
- Planning v5 (patterns: "plan", "create a plan", "make a plan")
- ADO v2 (patterns: "ado", "ado story", "ado feature")
- Vacuum v2 (patterns: "vacuum", "deep clean", "organize files")
- Cleanup v2 (patterns: "cleanup", "clear cache")
- TDD (patterns: "tdd", "start tdd", "run tests")
- Debug (patterns: "debug", "fix bug", "troubleshoot")
- Sanitization (patterns: "sanitize", "make generic")
- Refinement (patterns: "refine", "improve")
- Maintenance (patterns: "system maintenance", "health check")

**State Coordination:**
Orchestrators share state via StateManager + PlanningStateDB
```

### Task 7.3: Remove Obsolete Routing Code (3h)

**Deprecation Tasks:**
1. Archive old LLM-only routing logic (if any hardcoded routing exists)
2. Remove redundant intent classification code
3. Consolidate routing to Master Orchestrator entry point only
4. Update all orchestrator invocations to use Master Orch
5. Clean up legacy routing configuration files

### Task 7.4: Update Response Templates (2h)

### Task 7.4: Update Response Templates (2h)

**Files to Update:**
- `cortex-brain/response-templates-v4.yaml`

**Add New Templates:**
- `orchestrator_execution_summary` - Standard format for all autonomous orchestrators
- `database_state_query` - Format for displaying plan status
- `migration_complete` - Celebration template for completed migrations
- `master_orchestrator_routing` - Display routing decision (pattern matched vs LLM fallback)

### Task 7.5: Agent Layer Integration (4h)

**Update Agents:**
- `IntentRouter` - DEPRECATED (replaced by Master Orchestrator)
- `ErrorCorrector` - Integrate with orchestrator error handling via lifecycle hooks
- `LearningLibrarian` - Track orchestrator execution patterns from StateManager

**Integration Points:**
- Agents query planning state database via `StateManager`
- Agents DO NOT invoke orchestrators (Master Orchestrator owns invocation)
- Agent configuration externalized to YAML

### Task 7.6: Onboarding Updates (2h)

**Update Onboarding Flow:**
- Demonstrate Master Orchestrator routing (show pattern match vs LLM fallback)
- Show Planning System v5 usage via Master Orchestrator
- Show database state queries
- Explain autonomous vs guided orchestrators
- Update interactive demonstrations

### Completion Criteria
- ✅ Master Orchestrator deployment validated (routing coverage, performance, fallback)
- ✅ All orchestrators routable via YAML config (verified end-to-end)
- ✅ Pattern matching handles 90%+ requests (measured)
- ✅ LLM fallback functional for edge cases (<10% traffic)
- ✅ CORTEX.prompt.md reflects Master Orchestrator architecture (final docs)
- ✅ Response templates support routing display
- ✅ Agents integrated with Master Orchestrator
- ✅ Onboarding demonstrates Master Orchestrator
- ✅ Obsolete routing code removed
- ✅ End-to-end test: User command → Master Orch routing → orchestrator execution → result display
- ✅ **Copilot Chat API automation research completed**
- ✅ **Session management automation strategy documented**
- ✅ Git checkpoint created: `checkpoint-phase-7-master-orch-validation`

### Task 7.7: Session Management Automation Research (NEW)
**Duration:** 4h

**Goal:** Research Copilot Chat Extensions API capabilities for automated token monitoring and continuation prompt display

**Research Areas:**
1. **Copilot Chat Extensions API Exploration**
   - Token usage event subscriptions
   - Chat window lifecycle hooks
   - API capabilities for token counting
   - Webhook/callback availability

2. **Automation Feasibility Assessment**
   - Can we subscribe to token usage updates?
   - Can we programmatically display continuation prompt at 80% threshold?
   - Can we auto-create new chat window with pre-filled prompt?
   - API rate limits and restrictions

3. **Implementation Prototype (if API available)**
   - Subscribe to token usage events
   - Trigger continuation prompt display at 80k tokens
   - Test auto-handoff workflow
   - Document API integration pattern

4. **Fallback Strategy Documentation (if API unavailable)**
   - Confirm heuristic token estimation accuracy
   - Document manual warning system limitations
   - Propose alternative approaches (VS Code extension, external monitoring)
   - Update session management guide with findings

**Deliverables:**
- `cortex-brain/documents/reports/copilot-chat-api-research.md`
- API integration code (if feasible) or fallback strategy
- Updated `session-management-and-continuation.md` with automation status
- Recommendation for Phase 10 enhancement priority

**Completion Criteria:**
- ✅ Copilot Chat Extensions API capabilities documented
- ✅ Token usage subscription feasibility determined
- ✅ Prototype implemented (if API available) or fallback confirmed
- ✅ Session management guide updated with research findings
- ✅ Recommendation provided for future automation work

---

## ✅ Phase 8: Testing & Validation + Master Orchestrator (3 days)

**Goal:** Comprehensive testing across all layers including Master Orchestrator routing

### Task 8.1: Unit Test Suite + Routing Tests
**Duration:** 1d

**Coverage Requirements:**
- BaseOrchestrator v4.1: 100%
- Planning Orchestrator v5: 100%
- Database layer: 100%
- **Master Orchestrator: 100% (pattern matching, config loading, lifecycle hooks)**
- **PatternRouter: 100% (exact/regex matching, confidence scoring)**
- **StateManager: 100% (state sharing, execution tracking)**
- **ExecutionEngine: 100% (lifecycle management, hook execution)**
- MCP tools: 100%
- Migrated orchestrators: 100%

**Test Categories:**
- Happy path execution
- Error handling and rollback
- Transaction isolation
- Template rendering
- Config validation

### Task 8.2: Integration Test Suite + Master Orchestrator Routing
**Duration:** 1d

**End-to-End Scenarios:**
1. User creates plan → Master Orchestrator routes → Planning v5 executes → Plan folder created → Database updated
2. Plan fails mid-phase → Rollback triggered → State restored → User retries
3. User resumes plan → Load from database → Continue from last phase → Complete
4. Multiple plans concurrent → No state conflicts → All complete independently
5. **Routing edge cases → Pattern matching fails → LLM fallback succeeds → Orchestrator executes**
6. **State sharing → Orchestrator A saves context → Orchestrator B retrieves → Workflow continues**
7. **Lifecycle hooks → Pre-execution validation → Main execution → Post-execution artifacts saved**

**Files to Create:**
- `tests/integration/test_planning_workflow.py`
- `tests/integration/test_orchestrator_migrations.py`
- `tests/integration/test_mcp_invocation.py`
- `tests/integration/test_database_transactions.py`
- **`tests/integration/test_master_orchestrator_routing.py` (NEW)**
- **`tests/integration/test_state_coordination.py` (NEW)**
- **`tests/integration/test_lifecycle_hooks.py` (NEW)**

**Master Orchestrator Routing Tests:**
- Pattern exact match: "plan" → planning_v5
- Pattern regex match: "ado story X" → ado_orchestrator
- No pattern match: "do something unusual" → LLM fallback → correct orchestrator
- Confidence threshold: LLM returns 0.5 confidence → Reject (threshold 0.7)
- Config reload: Update master-orchestrator.yaml → Reload without restart
- Dependency validation: Orchestrator X requires Y → Validation passes/fails
- Concurrent routing: 10 simultaneous requests → All routed correctly

### Task 8.3: System Validation + Master Orchestrator
**Duration:** 1d

**Validation Checklist:**
- [ ] All 6+ orchestrators execute via Master Orchestrator routing
- [ ] Pattern matching handles 90%+ test cases
- [ ] LLM fallback correctly handles edge cases
- [ ] Routing latency <100ms for pattern matching
- [ ] Config reload <50ms
- [ ] State coordination works across orchestrators
- [ ] Lifecycle hooks execute in correct order
- [ ] Database state queries return accurate data
- [ ] Templates render without errors
- [ ] Config validation catches schema violations
- [ ] Rollback restores state correctly
- [ ] Progress tracking updates in real-time
- [ ] File naming standards enforced (≤20 chars)
- [ ] No natural language in manifests
- [ ] All plans resumable from any phase
- [ ] Git isolation maintained (CORTEX code separate)

**Regression Testing:**
- Existing functionality still works
- Old plans remain accessible (archived)
- Backward compatibility maintained during transition
- Master Orchestrator doesn't break existing agents

**Performance Benchmarks:**
- Routing latency: <100ms (pattern), <500ms (LLM fallback)
- Plan generation: <10s
- Database query: <50ms
- Config reload: <50ms

### Completion Criteria
- ✅ 100% test coverage achieved
- ✅ All integration tests pass
- ✅ System validation checklist complete
- ✅ No regressions detected
- ✅ Performance benchmarks met (plans generate <10s)
- ✅ Git checkpoint created: `checkpoint-phase-8-testing-complete`

---

## 📚 Phase 9: Documentation + Master Orchestrator (1.5 days)

**Goal:** Comprehensive documentation for new architecture including Master Orchestrator

### Task 9.1: Architecture Documentation + Master Orchestrator
**Duration:** 6h

**Files to Create:**
- `docs/architecture/pure-autonomous-architecture.md`
- `docs/architecture/mcp-protocol-integration.md`
- `docs/architecture/database-state-management.md`
- `docs/architecture/orchestrator-lifecycle.md`
- **`docs/architecture/master-orchestrator-design.md` (NEW)**

**Master Orchestrator Documentation:**
- Pattern-based routing architecture
- Routing config schema (`master-orchestrator.yaml`)
- State coordination mechanisms
- Lifecycle hook system
- LLM fallback strategy
- Performance characteristics
- Extensibility patterns (adding new orchestrators)

**Content:**
- System architecture diagrams (with Master Orchestrator as central hub)
- Execution flow charts (user input → routing → execution)
- Database schema documentation
- Component interaction patterns

### Task 9.2: Developer Guide + Master Orchestrator
**Duration:** 4h

**Files to Create:**
- `docs/guides/creating-autonomous-orchestrators.md`
- `docs/guides/config-manifest-specification.md`
- `docs/guides/template-development.md`
- `docs/guides/database-operations.md`
- **`docs/guides/master-orchestrator-integration.md` (NEW)**
- **`docs/guides/session-management-and-continuation.md` (NEW)**

**Master Orchestrator Integration Guide:**
- How to register orchestrators in YAML config
- Pattern syntax (exact vs regex)
- Confidence threshold tuning
- State sharing best practices
- Lifecycle hook implementation
- Testing routing rules
- Debugging routing failures

**Session Management Guide:**
- Token limit monitoring (heuristic estimation)
- Continuation prompt structure and usage
- Copy-paste session handoff instructions
- Database state recovery procedures
- Git checkpoint verification
- Phase dependency validation

**Content:**
- Step-by-step orchestrator creation
- Manifest schema reference
- Template variable reference
- Database API documentation
- **Routing config examples**

### Task 9.3: Migration Guide
**Duration:** 2h

**Files to Create:**
- `docs/migration/v4-to-v5-migration-guide.md`
- `docs/migration/orchestrator-conversion-patterns.md`

**Content:**
- Hybrid to autonomous conversion process
- Common migration pitfalls
- Testing strategies
- Rollback procedures

### Task 9.4: User Guide Updates
**Duration:** 3h

**Files to Update:**
- `README.md` - New architecture overview
- `.github/copilot-instructions.md` - Updated orchestrator usage
- `docs/user-guide/planning-system-v5.md` - Planning workflow

**Content:**
- User-facing command changes
- New capabilities (resumable plans, state queries)
- Visual progress tracking
- Database state inspection

### Completion Criteria
- ✅ All architecture docs complete
- ✅ Developer guides written and reviewed
- ✅ Migration guide validated with actual migration
- ✅ User documentation updated
- ✅ All docs cross-referenced correctly
- ✅ Git checkpoint created: `checkpoint-phase-9-documentation`

---

## 🧹 Phase 10: REFACTOR & Cleanup (2 days)

**Goal:** Remove obsolete code, consolidate utilities, enforce standards

### Task 10.1: Archive Old Implementations
**Duration:** 4h

**Files to Archive:**
```
cortex-brain/archives/v4-orchestrators/
├── planning_orchestrator_v4.py
├── ado_orchestrator_v1.py
├── planning-system-4.0-manifest.yaml
└── migration-notes.md
```

**Archive Process:**
- Move old orchestrators to archives
- Update import statements
- Add deprecation notices
- Document breaking changes

### Task 10.2: Remove Duplicate Code
**Duration:** 6h

**Areas to Consolidate:**
- Common orchestrator utilities → `src/utils/orchestrator_utils.py`
- Template helpers → `src/templates/template_helpers.py`
- Database query builders → `src/database/query_builders.py`
- Validation functions → `src/utils/validation.py`

**Deduplication Targets:**
- File creation logic (use filename validator)
- Progress bar generation (standardize format)
- Checkpoint creation (use base class method)
- Config loading (centralize in BaseOrchestrator)

### Task 10.3: Enforce Filename Standards
**Duration:** 4h

**Cleanup Operations:**
- Scan all files for length violations (>20 chars)
- Rename violators using `file_name.py` suggestions
- Update all references (imports, docs)
- Generate compliance report

**Target Files:**
- Python modules
- Markdown documentation
- Configuration files
- Templates

### Task 10.4: Optimize Imports
**Duration:** 2h

**Optimization Tasks:**
- Remove unused imports across all files
- Consolidate related imports
- Apply isort formatting
- Resolve circular dependencies

**Tools:**
- `autoflake` for unused import removal
- `isort` for import organization
- Custom scripts for validation

### Task 10.5: Final Validation
**Duration:** 6h

**Validation Suite:**
- Run full test suite (must pass 100%)
- Execute SKULL governance tests
- Perform static analysis (mypy, pylint)
- Check documentation links
- Validate manifest schemas
- Test sample operations end-to-end

**Quality Gates:**
- Zero test failures
- Zero SKULL violations
- Zero linting errors above warning
- All docs render correctly
- All manifests validate against schema

### Completion Criteria
- ✅ Old code archived with migration notes
- ✅ Duplicate code consolidated
- ✅ 100% filename compliance (≤20 chars)
- ✅ All imports optimized
- ✅ Final validation passed
- ✅ Git checkpoint created: `checkpoint-phase-10-refactor-complete`

---

## 🎉 Project Completion Checklist

### Technical Deliverables
- [ ] **Master Orchestrator operational with pattern-based routing**
- [ ] **90%+ routing accuracy via pattern matching (measured)**
- [ ] **LLM fallback handles edge cases (10% traffic)**
- [ ] **Cross-orchestrator state coordination functional**
- [ ] **Lifecycle hooks operational (pre/post execution, error handling)**
- [ ] Planning System v5 operational via MCP
- [ ] SQLite state database with ACID transactions
- [ ] BaseOrchestrator v4.1 config-driven
- [ ] 4+ AUTONOMOUS orchestrators migrated (Planning, ADO, Vacuum, Cleanup)
- [ ] GUIDED orchestrators assessed and transformed where beneficial
- [ ] Agent layer integrated with Master Orchestrator
- [ ] 100% test coverage across all new components (including Master Orchestrator)
- [ ] Zero natural language in manifests
- [ ] All plans resumable from any phase
- [ ] Filename standards enforced (≤20 chars)

### Documentation Deliverables
- [ ] Architecture documentation complete (with Master Orchestrator design)
- [ ] Master Orchestrator integration guide written
- [ ] Developer guides written
- [ ] Migration guide validated
- [ ] User documentation updated
- [ ] CORTEX.prompt.md reflects Master Orchestrator architecture

### Validation Deliverables
- [ ] All tests pass (unit + integration + routing)
- [ ] Master Orchestrator routing tests pass (100% coverage)
- [ ] Performance benchmarks met (routing <100ms, config reload <50ms)
- [ ] SKULL governance tests pass
- [ ] System validation checklist complete
- [ ] Regression testing passed
- [ ] End-to-end routing validated for all orchestrators

### Operational Deliverables
- [ ] Old code archived
- [ ] Duplicate code removed
- [ ] Git checkpoints created for each phase
- [ ] Migration reports generated
- [ ] Lessons learned documented
- [ ] Master Orchestrator config YAML validated

---

## 📖 Reference Documents

**Source Plans:**
- `autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md` - Architecture blueprint
- `autonomous-orchestrator-v5/architecture/option-1-analysis.md` - Decision rationale
- `autonomous-orchestrator-v5/architecture/database-schema.md` - Database design
- `auto-orch-v5-impl/mst-pure-autonomous.md` - Implementation details

**Key Files:**
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-brain/response-templates-v4.yaml` - Response templates
- `.github/prompts/CORTEX.prompt.md` - Entry point (will be updated)

**Related Plans:**
- All generated migration plans in Phase 5

---

## 🎓 Lessons from Previous Attempts

**Problem:** Multiple fragmented plans without clear execution order.

**Solution:** Bootstrap approach - build the planning tool first, then use it.

**Problem:** Hybrid manifests with natural language and config mixed.

**Solution:** Strict separation - manifests are data only, Python owns logic.

**Problem:** State fragmentation preventing recovery.

**Solution:** Single database source of truth with ACID transactions.

**Problem:** Execution ambiguity between CORTEX and Python.

**Solution:** Clear hand-off protocol via MCP tool invocation.

---

## 📝 copilot_instructions

```yaml
# Response & Tracking
response_template: "autonomous_execution_progress"
tdd_enforcement: true
final_refactor_required: true

# Master Orchestrator Integration (NEW)
master_orchestrator_enabled: true
routing_mode: "pattern_primary_llm_fallback"  # 90% pattern, 10% LLM
state_coordination: true
lifecycle_hooks: true

# Plan Creation Context
manual_planning_for_bootstrap: true  # This plan created manually
use_v5_for_migrations: true          # Phase 5+ use Planning v5
master_orch_routing: true            # All requests route via Master Orchestrator

# State Management
database_tracking: true
atomic_operations: true
cross_orchestrator_sharing: true     # Master Orchestrator StateManager enabled

# ⚠️ CRITICAL: Autonomous Execution Mode (ALWAYS ENFORCED)
execution_mode: "autonomous"         # MANDATORY - No supervised mode allowed
phase_execution_protocol: "AUTONOMOUS_ONLY"  # CORTEX hands off, Python executes

# Autonomous Execution Configuration
autonomous_enforcement:
  validation: true                   # Auto-validate using tests
  auto_commit: true                  # Auto-commit on validation pass
  auto_transition: true              # Auto-transition to next phase
  self_healing: true                 # Self-heal failures (3 attempts)
  escalation_threshold: 3            # Escalate after 3 failures
  user_approval_required: false      # No manual approval needed

# Phase Execution Rules
phase_transition:
  method: "automatic"                # Phases transition automatically
  validation_required: true          # Each phase must validate before transition
  checkpoint_creation: true          # Create git checkpoint after each phase
  rollback_on_failure: true          # Auto-rollback on critical failure

# Master Orchestrator Integration
master_orchestrator_protocol:
  routing_invocation: "automatic"    # Route all requests via Master Orchestrator
  pattern_matching_primary: true     # Pattern matching handles 90%+
  llm_fallback_enabled: true         # LLM handles edge cases
  state_manager_active: true         # Cross-orchestrator state sharing
  lifecycle_hooks_active: true       # Pre/post execution hooks

# MCP Tool Integration
mcp_invocation:
  method: "autonomous"               # MCP tools invoked autonomously
  hand_off_complete: true            # CORTEX stops after routing to orchestrator
  orchestrator_owns_execution: true  # Python owns all execution logic
  master_orch_routes_first: true     # Master Orchestrator routes before MCP invocation
```

---

## ⚠️ EXECUTION PROTOCOL (Master Orchestrator Enhanced)

**This plan executes in PURE AUTONOMOUS MODE with Master Orchestrator routing.**

### What This Means:

1. **Master Orchestrator Routing**: All user requests route through Master Orchestrator first
2. **Pattern Matching Primary**: 90%+ requests handled by deterministic pattern matching
3. **LLM Fallback**: Edge cases (10%) route to LLM classifier with 70% confidence threshold
4. **State Coordination**: Orchestrators share state via StateManager + PlanningStateDB
5. **Lifecycle Management**: Pre/post execution hooks for validation, artifact saving
6. **No User Approval Required**: Each phase executes automatically after previous phase validates
7. **Auto-Validation**: Tests run automatically, phase only completes if all tests pass
8. **Auto-Commit**: Successful validation triggers automatic git commit
9. **Auto-Transition**: Completion of phase N automatically starts phase N+1
10. **Self-Healing**: Failures trigger up to 3 automatic retry attempts before escalation
11. **CORTEX Role**: Route to Master Orchestrator → Master Orch routes to orchestrator → STOP (Python executes)

### Phase Execution Flow with Master Orchestrator:

```
User Input → Master Orchestrator.route_request()
    ↓
Pattern Match (90%) OR LLM Fallback (10%)
    ↓
Master Orchestrator.execute_orchestrator()
    ↓
Pre-Execution Hooks (validate dependencies, check state)
    ↓
Orchestrator Autonomous Execution (Phase N)
    ↓
Execute Tasks → Run Tests → Validate
    ↓ PASS                    ↓ FAIL
Post-Exec Hooks          Retry (max 3) → Escalate
    ↓
Save Artifacts, Update Metrics
    ↓
Create Checkpoint → Auto-commit → Phase N+1
```

### User Interaction Points:

- **Plan Approval**: User approves THIS master plan (one-time)
- **Escalation Only**: User only engaged after 3 consecutive failures or routing failures
- **Routing Review**: User can inspect routing decisions in logs (pattern match vs LLM fallback)
- **Completion Review**: User reviews final deliverables at project end

**All intermediate phases execute WITHOUT user intervention.**

---

**Next Action:** Review and approve this master plan, then autonomous execution begins with Phase 0 (Foundation Setup).

**Bootstrap Note:** This plan was created using traditional planning methods because Planning System v5 doesn't exist yet. Once v5 is operational (after Phase 4), it will be used to generate all subsequent migration plans with proper structure and tracking.
