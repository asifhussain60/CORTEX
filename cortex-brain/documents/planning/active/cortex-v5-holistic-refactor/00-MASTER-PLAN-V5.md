# 🛡️ CORTEX v5.0 Holistic Architecture Refactor

**Plan ID:** cortex-v5-holistic-refactor  
**Feature:** System-wide Pure Autonomous Architecture Transformation with Master Orchestrator  
**Created:** January 2, 2026 | **Updated:** January 2, 2026 (Master Orchestrator integration)  
**Complexity:** TIER 5 (ARCHITECTURAL)  
**Strategy:** Bootstrap Planning System v5 + Master Orchestrator, then use them to plan remaining migrations  
**Estimated Duration:** 38 days total (11 days bootstrap + 27 days migrations)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `████░░░░░░░░░░░░░░░░` **20%** ⏳ IN PROGRESS

### Bootstrap Phase (Planning System v5 + Master Orchestrator)

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation Setup | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 1 | MCP Tool Infra | `██████████` | 2d | ✅ Complete |
| 2 | State Database | `██████████` | 1.5d | ✅ Complete |
| 3 | BaseOrch v4.1 + Master Orch Core | `░░░░░░░░░░` | 2.5d | ⏸️ Not Started |
| 3.5 | Master Orch Integration | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 4 | PlanOrch v5 | `░░░░░░░░░░` | 2d | ⏸️ Not Started |

### Migration Phase (Using Planning System v5)

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 5 | Use v5 to Plan Migrations | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 6 | Execute Migration Plans | `░░░░░░░░░░` | 24d | ⏸️ Not Started |
| 7 | System Integration | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 8 | Testing & Validation | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 9 | Documentation | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 10 | REFACTOR & Cleanup | `░░░░░░░░░░` | 2d | ⏸️ Not Started |

**Bootstrap Completion:** ~11 days (includes Master Orchestrator)  
**Full Completion:** ~38 days  
**Current Phase:** BaseOrchestrator v4.1 + Master Orchestrator Core implementation

**Checkpoints:**
- ✅ Phase 1 checkpoint @ commit 90153190: MCP Tool Infrastructure
- ✅ Phase 2 checkpoint @ commit 3a081949: Planning State Database
- ✅ Master Orchestrator Integration @ commit 87a081529: Plan holistically updated
- ✅ Progressive Activation Strategy @ commit 4568a2f52: Master Orch activates as components are built

---

## 🎯 Executive Summary

### The Transformation

This plan eliminates hybrid control flow ambiguity across the entire CORTEX architecture by implementing a pure autonomous system where Python owns all execution logic and manifests contain only configuration data. The architecture introduces a **Master Orchestrator** - a centralized, machine-readable routing layer that eliminates LLM-dependent brittleness while enabling deterministic orchestrator coordination. The approach is **bootstrapped**: we build Planning System v5 + Master Orchestrator first, then use them to create detailed plans for migrating all other orchestrators and agents.

### Why Master Orchestrator?

**Problem:** Current intent routing via `CORTEX.prompt.md` is LLM-dependent, creating brittleness and unpredictability. No orchestrator-to-orchestrator communication exists.

**Solution:** Master Orchestrator provides:
- **Machine-Readable Routing:** Pure pattern matching via YAML config (no LLM interpretation)
- **Orchestrator Registry:** Centralized discovery and lifecycle management
- **State Coordination:** Cross-orchestrator state sharing via PlanningStateDB
- **Execution Engine:** Autonomous orchestrator invocation with monitoring
- **Hybrid Fallback:** LLM classifier for edge cases, pattern matching for 90%+ of requests

**Architecture:**
```
User Input → Master Orchestrator (Pattern Match) → Orchestrator Execution
                    ↓ (no match)
              LLM Classifier (Fallback)
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

### Task 3.3: Progress Tracking
**Duration:** 4h

**Implementation:**
- Real-time progress updates to database
- Progress bar generation for visual tracking
- Percentage calculations across phases
- Estimated vs actual time tracking
- Status change notifications

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
  required_sections:
    - "Visual Progress Tracker"
    - "Executive Summary"
    - "Implementation Phases"
```

**Zero Natural Language:** Only data structures, no commands.

### Task 4.3: Template Creation
**Duration:** 4h

**Files to Create:**
- `cortex-brain/templates/planning/master-plan.jinja2`
- `cortex-brain/templates/planning/progress-tracker.json.jinja2`
- `cortex-brain/templates/planning/README.md.jinja2`
- `cortex-brain/templates/planning/context-summary.md.jinja2`

**Template Features:**
- Dynamic progress bar generation
- Phase table rendering with status indicators
- Automatic timestamp insertion
- Context data injection
- Cross-reference generation

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
- ✅ 100% test coverage for orchestrator
- ✅ Manual test: Generate a sample plan successfully
- ✅ Git checkpoint created: `checkpoint-phase-4-planning-v5-master-orch`

---

## 🚀 Phase 5: Use Planning v5 + Master Orchestrator for Migrations (0.5 days)

**Goal:** Validate Planning System v5 + Master Orchestrator by using them to create detailed migration plans via routing layer

**ROUTING VALIDATION:** All plan generation requests will route through Master Orchestrator, validating pattern matching and orchestrator invocation.

**MASTER ORCHESTRATOR STATUS:** ✅ LIVE - Planning v5 routed via Master Orch (activated Phase 4)

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
- ✅ Git checkpoint created: `checkpoint-phase-7-master-orch-validation`

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

**Master Orchestrator Integration Guide:**
- How to register orchestrators in YAML config
- Pattern syntax (exact vs regex)
- Confidence threshold tuning
- State sharing best practices
- Lifecycle hook implementation
- Testing routing rules
- Debugging routing failures

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
