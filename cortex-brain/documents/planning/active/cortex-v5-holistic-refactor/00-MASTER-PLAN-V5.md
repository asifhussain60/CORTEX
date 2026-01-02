# 🛡️ CORTEX v5.0 Holistic Architecture Refactor

**Plan ID:** cortex-v5-holistic-refactor  
**Feature:** System-wide Pure Autonomous Architecture Transformation  
**Created:** January 2, 2026  
**Complexity:** TIER 5 (ARCHITECTURAL)  
**Strategy:** Bootstrap Planning System v5, then use it to plan remaining migrations  
**Estimated Duration:** 35 days total (8 days bootstrap + 27 days migrations)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `██░░░░░░░░░░░░░░░░░░` **10%** ⏳ IN PROGRESS

### Bootstrap Phase (Planning System v5)

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation Setup | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 1 | MCP Tool Infra | `██████████` | 2d | ✅ Complete |
| 2 | State Database | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 3 | BaseOrch v4.1 | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
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

**Bootstrap Completion:** ~8 days  
**Full Completion:** ~35 days  
**Current Phase:** Foundation setup

---

## 🎯 Executive Summary

### The Transformation

This plan eliminates hybrid control flow ambiguity across the entire CORTEX architecture by implementing a pure autonomous system where Python owns all execution logic and manifests contain only configuration data. The approach is **bootstrapped**: we build Planning System v5 first, then use it to create detailed plans for migrating all other orchestrators and agents.

### Why Bootstrap?

**Problem:** We need Planning System v5 to create high-quality, structured plans for complex migrations, but Planning System v5 doesn't exist yet.

**Solution:** Build Planning System v5 using the current manual planning approach (this document), then immediately use the newly created v5 system to plan all remaining migrations with proper folder structure, progress tracking, and validation.

### Success Criteria

**Bootstrap Phase:**
- ✅ Planning System v5 operational with MCP tool integration
- ✅ SQLite state database functioning with ACID transactions
- ✅ BaseOrchestrator v4.1 supporting config-driven execution
- ✅ Planning orchestrator generates plans with proper structure
- ✅ Zero execution ambiguity in new planning system

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
│   ├── planning_orchestrator_v5.py (new)
│   └── ...existing...
└── utils/
    └── file_name.py (new)

cortex-brain/
├── database/                    # Database storage (new)
└── config/
    └── mcp-server.yaml (new)

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
- `context/brittleness-analysis.md` - Known issues across all components
- `context/orchestrator-inventory.md` - Complete orchestrator catalog
- `context/agent-inventory.md` - All agents and their manifest dependencies

**Content:**
- List all 4 AUTONOMOUS orchestrators with current issues
- List all GUIDED orchestrators with hybrid ambiguity points
- Catalog all agents with configuration sources
- Map state management approaches across system
- Document failure recovery capabilities (or lack thereof)

### Completion Criteria
- ✅ Project structure exists with proper organization
- ✅ Filename utility operational with 100% test coverage
- ✅ Baseline documentation complete and reviewed
- ✅ Git checkpoint created: `checkpoint-phase-0-foundation`

---

## 🔧 Phase 1: MCP Tool Infrastructure (2 days)

**Goal:** Build Model Context Protocol layer for universal orchestrator invocation

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
- ✅ Git checkpoint created: `checkpoint-phase-1-mcp-infrastructure`

---

## 🗄️ Phase 2: Planning State Database (1.5 days)

**Goal:** Single source of truth for all planning state with ACID transactions

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
- ✅ Git checkpoint created: `checkpoint-phase-2-state-database`

---

## 🏛️ Phase 3: BaseOrchestrator v4.1 (1.5 days)

**Goal:** Config-driven orchestrator base class with template rendering

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

### Completion Criteria
- ✅ BaseOrchestrator v4.1 fully functional
- ✅ Config loading works with validation
- ✅ Template rendering produces correct output
- ✅ Progress tracking updates database correctly
- ✅ Checkpoints and rollback work properly
- ✅ 100% test coverage for base class
- ✅ Git checkpoint created: `checkpoint-phase-3-base-orchestrator`

---

## 🧠 Phase 4: Planning Orchestrator v5 (2 days)

**Goal:** Pure autonomous planning orchestrator with zero natural language in manifest

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

### Completion Criteria
- ✅ Planning Orchestrator v5 generates complete plans
- ✅ Plans have proper folder structure (4 subfolders)
- ✅ Database tracks all phases and artifacts
- ✅ Templates render correctly with injected data
- ✅ Validation catches missing required content
- ✅ 100% test coverage for orchestrator
- ✅ Manual test: Generate a sample plan successfully
- ✅ Git checkpoint created: `checkpoint-phase-4-planning-v5`

---

## 🚀 Phase 5: Use Planning v5 for Migrations (0.5 days)

**Goal:** Validate Planning System v5 by using it to create detailed migration plans

### Task 5.1: Generate ADO Migration Plan
**Duration:** 1h

**Command:** `/CORTEX Plan ADO Orchestrator v2 Migration`

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

### Task 6.2: Vacuum Orchestrator v2 Migration
**Duration:** 5 days  
**Plan Reference:** `vacuum-v2-migration/00-master-plan.md`

**Key Deliverables:**
- Atomic filesystem operations
- Safe deletion with rollback
- Transaction boundaries
- Comprehensive logging

### Task 6.3: Cleanup Orchestrator v2 Migration
**Duration:** 4 days  
**Plan Reference:** `cleanup-v2-migration/00-master-plan.md`

**Key Deliverables:**
- Deterministic execution order
- Cache management strategy
- Log rotation automation
- State persistence

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

### Completion Criteria
- ✅ All orchestrators migrated per generated plans
- ✅ 100% test coverage for new implementations
- ✅ All plans marked 'completed' in database
- ✅ Migration reports generated
- ✅ Git checkpoints for each orchestrator
- ✅ Final checkpoint: `checkpoint-phase-6-all-migrations`

---

## 🔗 Phase 7: System Integration (2 days)

**Goal:** Integrate all components and update CORTEX entry point

### Task 7.1: Update CORTEX.prompt.md
**Duration:** 4h

**Changes Required:**
- Update Intent Router with new orchestrator versions
- Add MCP tool invocation instructions
- Update Orchestrator Autonomy Matrix
- Document new execution flow
- Add database state query patterns

**New Intent Routing:**
```markdown
| `/CORTEX Plan [x]` | 🛡️ Planning System v5 (AUTONOMOUS) | invoke_orchestrator("planning_system", request) |
| `ado story [x]` | 🛡️ ADO Operations v2 (AUTONOMOUS) | invoke_orchestrator("ado_operations", request) |
| `vacuum [path]` | 🛡️ Vacuum v2 (AUTONOMOUS) | invoke_orchestrator("vacuum", request) |
| `cleanup [type]` | 🛡️ Cleanup v2 (AUTONOMOUS) | invoke_orchestrator("cleanup", request) |
```

### Task 7.2: Update Response Templates
**Duration:** 3h

**Files to Update:**
- `cortex-brain/response-templates-v4.yaml`

**Add New Templates:**
- `orchestrator_execution_summary` - Standard format for all autonomous orchestrators
- `database_state_query` - Format for displaying plan status
- `migration_complete` - Celebration template for completed migrations

### Task 7.3: Agent Layer Integration
**Duration:** 1d

**Update Agents:**
- `IntentRouter` - Add MCP tool invocation capability
- `ErrorCorrector` - Integrate with orchestrator error handling
- `LearningLibrarian` - Track orchestrator execution patterns

**Integration Points:**
- Agents can query planning state database
- Agents can invoke orchestrators via MCP
- Agent configuration externalized to YAML

### Task 7.4: Onboarding Updates
**Duration:** 4h

**Update Onboarding Flow:**
- Demonstrate Planning System v5 usage
- Show database state queries
- Explain autonomous vs guided orchestrators
- Update interactive demonstrations

### Completion Criteria
- ✅ CORTEX.prompt.md reflects new architecture
- ✅ Response templates support new formats
- ✅ Agents integrated with MCP protocol
- ✅ Onboarding demonstrates new features
- ✅ End-to-end test: User command → orchestrator execution → result display
- ✅ Git checkpoint created: `checkpoint-phase-7-system-integration`

---

## ✅ Phase 8: Testing & Validation (3 days)

**Goal:** Comprehensive testing across all layers

### Task 8.1: Unit Test Suite
**Duration:** 1d

**Coverage Requirements:**
- BaseOrchestrator v4.1: 100%
- Planning Orchestrator v5: 100%
- Database layer: 100%
- MCP tools: 100%
- Migrated orchestrators: 100%

**Test Categories:**
- Happy path execution
- Error handling and rollback
- Transaction isolation
- Template rendering
- Config validation

### Task 8.2: Integration Test Suite
**Duration:** 1d

**End-to-End Scenarios:**
1. User creates plan → Planning v5 executes → Plan folder created → Database updated
2. Plan fails mid-phase → Rollback triggered → State restored → User retries
3. User resumes plan → Load from database → Continue from last phase → Complete
4. Multiple plans concurrent → No state conflicts → All complete independently

**Files to Create:**
- `tests/integration/test_planning_workflow.py`
- `tests/integration/test_orchestrator_migrations.py`
- `tests/integration/test_mcp_invocation.py`
- `tests/integration/test_database_transactions.py`

### Task 8.3: System Validation
**Duration:** 1d

**Validation Checklist:**
- [ ] All 4 AUTONOMOUS orchestrators execute via MCP
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

### Completion Criteria
- ✅ 100% test coverage achieved
- ✅ All integration tests pass
- ✅ System validation checklist complete
- ✅ No regressions detected
- ✅ Performance benchmarks met (plans generate <10s)
- ✅ Git checkpoint created: `checkpoint-phase-8-testing-complete`

---

## 📚 Phase 9: Documentation (1.5 days)

**Goal:** Comprehensive documentation for new architecture

### Task 9.1: Architecture Documentation
**Duration:** 6h

**Files to Create:**
- `docs/architecture/pure-autonomous-architecture.md`
- `docs/architecture/mcp-protocol-integration.md`
- `docs/architecture/database-state-management.md`
- `docs/architecture/orchestrator-lifecycle.md`

**Content:**
- System architecture diagrams
- Execution flow charts
- Database schema documentation
- Component interaction patterns

### Task 9.2: Developer Guide
**Duration:** 4h

**Files to Create:**
- `docs/guides/creating-autonomous-orchestrators.md`
- `docs/guides/config-manifest-specification.md`
- `docs/guides/template-development.md`
- `docs/guides/database-operations.md`

**Content:**
- Step-by-step orchestrator creation
- Manifest schema reference
- Template variable reference
- Database API documentation

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
- [ ] Planning System v5 operational via MCP
- [ ] SQLite state database with ACID transactions
- [ ] BaseOrchestrator v4.1 config-driven
- [ ] 4 AUTONOMOUS orchestrators migrated (Planning, ADO, Vacuum, Cleanup)
- [ ] GUIDED orchestrators assessed and transformed where beneficial
- [ ] Agent layer integrated with MCP protocol
- [ ] 100% test coverage across all new components
- [ ] Zero natural language in manifests
- [ ] All plans resumable from any phase
- [ ] Filename standards enforced (≤20 chars)

### Documentation Deliverables
- [ ] Architecture documentation complete
- [ ] Developer guides written
- [ ] Migration guide validated
- [ ] User documentation updated
- [ ] CORTEX.prompt.md reflects new architecture

### Validation Deliverables
- [ ] All tests pass (unit + integration)
- [ ] SKULL governance tests pass
- [ ] System validation checklist complete
- [ ] Regression testing passed
- [ ] Performance benchmarks met

### Operational Deliverables
- [ ] Old code archived
- [ ] Duplicate code removed
- [ ] Git checkpoints created for each phase
- [ ] Migration reports generated
- [ ] Lessons learned documented

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

# Plan Creation Context
manual_planning_for_bootstrap: true  # This plan created manually
use_v5_for_migrations: true          # Phase 5+ use Planning v5

# State Management
database_tracking: true
atomic_operations: true

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

# MCP Tool Integration
mcp_invocation:
  method: "autonomous"               # MCP tools invoked autonomously
  hand_off_complete: true            # CORTEX stops after routing to orchestrator
  orchestrator_owns_execution: true  # Python owns all execution logic
```

---

## ⚠️ EXECUTION PROTOCOL

**This plan executes in PURE AUTONOMOUS MODE.**

### What This Means:

1. **No User Approval Required**: Each phase executes automatically after previous phase validates
2. **Auto-Validation**: Tests run automatically, phase only completes if all tests pass
3. **Auto-Commit**: Successful validation triggers automatic git commit
4. **Auto-Transition**: Completion of phase N automatically starts phase N+1
5. **Self-Healing**: Failures trigger up to 3 automatic retry attempts before escalation
6. **CORTEX Role**: Route to orchestrator → STOP (Python executes autonomously)

### Phase Execution Flow:

```
Phase N Start → Execute Tasks → Run Tests → Validate → Pass? 
  ↓ YES                                               ↓ NO
Create Checkpoint → Auto-commit → Phase N+1     Retry (max 3) → Escalate
```

### User Interaction Points:

- **Plan Approval**: User approves THIS master plan (one-time)
- **Escalation Only**: User only engaged after 3 consecutive failures
- **Completion Review**: User reviews final deliverables at project end

**All intermediate phases execute WITHOUT user intervention.**

---

**Next Action:** Review and approve this master plan, then autonomous execution begins with Phase 0 (Foundation Setup).

**Bootstrap Note:** This plan was created using traditional planning methods because Planning System v5 doesn't exist yet. Once v5 is operational (after Phase 4), it will be used to generate all subsequent migration plans with proper structure and tracking.
