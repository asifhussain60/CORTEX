# 🛡️ Autonomous Orchestrator v5.0 Implementation Plan

**Plan ID:** auto-orch-v5-impl  
**Feature:** Pure Autonomous Orchestrator System (Option 1)  
**Created:** January 2, 2026  
**Complexity:** TIER 4 (CRITICAL)  
**Estimated Duration:** 27 days

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation Setup | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 1 | MCP Tool Infra | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 2 | Plan State DB | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 3 | BaseOrch v4.1 | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 4 | PlanOrch v5 | `░░░░░░░░░░` | 4d | ⏸️ Not Started |
| 5 | Config Manifests | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 6 | ADO Orch v2 | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 7 | Vacuum Orch v2 | `░░░░░░░░░░` | 2.5d | ⏸️ Not Started |
| 8 | Cleanup Orch v2 | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 9 | Testing & Validate | `░░░░░░░░░░` | 3d | ⏸️ Not Started |
| 10 | Migration & Docs | `░░░░░░░░░░` | 2d | ⏸️ Not Started |
| 11 | REFACTOR & Clean | `░░░░░░░░░░` | 2d | ⏸️ Not Started |

**Estimated Completion:** ~27 days  
**Current Phase:** Foundation setup

---

## 🎯 Executive Summary

### Problem Being Solved

Current AUTONOMOUS orchestrators (Planning, ADO, Vacuum, Cleanup) suffer from **hybrid control flow ambiguity**:

1. **Execution Confusion** - 🛡️ signals autonomy, but manifests contain natural language instructions for CORTEX
2. **State Fragmentation** - Progress tracked in JSON files, markdown, and Python variables (no single source of truth)
3. **Output Ownership Unclear** - Both Python and CORTEX attempt to generate content

### Solution: Pure Autonomous Architecture

Transform all AUTONOMOUS orchestrators to deterministic Python systems:

```
User Request → CORTEX Detects Intent → MCP Tool invoke_orchestrator() →
Python Orchestrator (Loads Config, Executes ALL Logic, Generates Outputs) →
CORTEX Displays Summary (Thin Client)
```

**Key Principles:**
- **Zero Natural Language in Manifests** - Only data structures (YAML/JSON)
- **Python Owns Execution** - All logic, decisions, output generation
- **SQLite State Management** - ACID transactions for atomic phases
- **Config-Driven Behavior** - YAML defines templates, schemas, validation rules
- **CORTEX as Thin Client** - Route → Invoke → Display → Done

### Success Criteria

- ✅ Zero ambiguity in execution flow
- ✅ Atomic phase operations (rollback on failure)
- ✅ Single source of truth (database state)
- ✅ Deterministic output (templates + data)
- ✅ 100% test coverage for phase execution
- ✅ Plans resumable from any phase

---

## 🏗️ Phase 0: Foundation Setup (1 day)

**Goal:** Establish project structure and baseline architecture documentation

### Tasks

#### Task 0.1: Filename Convention & Monitor
**Duration:** 2h  
**Priority:** HIGH

**Implementation:**
- Create `src/utils/file_name.py` with validation rules:
  - Max length: 20 characters (excluding extension)
  - Format: `kebab-case` only
  - Allowed: `[a-z0-9-]` characters
  - No consecutive hyphens
  - Must start/end with alphanumeric

**Validation Function:**
```python
def validate_filename(name: str, max_len: int = 20) -> tuple[bool, str]:
    """Returns (is_valid, error_message)"""
    
def suggest_filename(long_name: str, max_len: int = 20) -> str:
    """Auto-shorten while preserving meaning"""
```

**Integration Points:**
- BaseOrchestrator file creation methods
- Planning folder generation
- Artifact creation utilities
- All file write operations

**Monitoring:**
- Pre-creation validation hook
- Post-creation audit scan
- Weekly compliance report
- Auto-fix suggestions in logs

**Artifacts:**
- `artifacts/file-name-rules.md`
- `src/utils/file_name.py`
- `tests/utils/test_file_name.py`

#### Task 0.2: Project Structure
**Duration:** 3h

Create implementation directories:
```
src/
├── mcp/                    # MCP protocol layer
├── orchestrators/          # v5 orchestrators
├── database/              # SQLite schemas
└── utils/                 # Shared utilities

cortex-brain/
└── config/
    └── mcp-server.yaml    # MCP configuration

tests/
├── mcp/
├── orchestrators/
└── integration/
```

**Artifacts:**
- `context/structure.md`
- Empty directories with `.gitkeep`

#### Task 0.3: Architecture Baseline Doc
**Duration:** 3h

Document current state:
- List all 4 AUTONOMOUS orchestrators
- Map current execution flow
- Identify hybrid ambiguity points
- Document state management issues

**Artifacts:**
- `context/baseline.md`
- `context/arch-issues.md`

### Completion Criteria
- ✅ Filename validation utility operational with 100% test coverage
- ✅ Project structure created
- ✅ Baseline documentation complete

---

## 🔧 Phase 1: MCP Tool Infrastructure (3 days)

**Goal:** Build MCP protocol layer for orchestrator invocation

### Tasks

#### Task 1.1: MCP Server Foundation
**Duration:** 1d  
**Files:** `src/mcp/server.py`

Implement Model Context Protocol server:
- Protocol v1.0 compliance
- Tool registration system
- Request/response handling
- Error propagation
- Logging and metrics

**Validation:**
- MCP protocol test suite passes
- Server starts/stops cleanly
- Handles malformed requests gracefully

#### Task 1.2: Orchestrator Registry
**Duration:** 1d  
**Files:** `src/mcp/registry.py`

Create orchestrator registration system:
- Map orchestrator names to Python classes
- Link to config file paths
- Validate orchestrator availability
- Support hot-reload for development

**Registry Schema:**
```python
{
    "planning_system": {
        "class": "PlanningOrchestratorV5",
        "module": "src.orchestrators.plan_orch_v5",
        "config": "cortex-brain/manifests/.../plan-sys-5.yaml"
    }
}
```

**Validation:**
- All 4 orchestrators registered
- Config files validate on startup
- Missing orchestrator returns clear error

#### Task 1.3: invoke_orchestrator Tool
**Duration:** 1d  
**Files:** `src/mcp/tools/invoke_orch.py`

Implement MCP tool for orchestrator invocation:

**Tool Signature:**
```python
@mcp_tool
def invoke_orchestrator(
    orchestrator_name: str,
    user_request: str,
    context: dict = None
) -> dict:
    """
    Returns:
    {
        "status": "success|failure",
        "summary": "Human-readable summary",
        "artifacts": ["file1.md", "file2.json"],
        "next_steps": "What user should do",
        "execution_time": 12.5
    }
    """
```

**Integration:**
- Registry lookup
- Orchestrator instantiation
- Error handling with context
- Result formatting

**Validation:**
- Tool callable via MCP protocol
- Returns valid response structure
- Errors include actionable messages

#### Task 1.4: CORTEX.prompt.md Integration
**Duration:** 4h  
**Files:** `.github/prompts/CORTEX.prompt.md`

Update intent router:
- Add MCP tool invocation examples
- Document hand-off protocol
- Update response templates section
- Add troubleshooting guide

**Validation:**
- Intent detection tests pass
- Documentation complete

#### Task 1.5: Filename Monitor Integration
**Duration:** 2h

Integrate filename validation:
- Hook into MCP tool pre-execution
- Validate orchestrator output paths
- Auto-fix violations
- Log compliance metrics

**Validation:**
- All created files comply with 20-char limit
- Violations logged with suggestions
- Auto-fix applied successfully

### Completion Criteria
- ✅ MCP server operational
- ✅ Registry loads all 4 orchestrators
- ✅ invoke_orchestrator tool functional
- ✅ CORTEX.prompt.md updated
- ✅ Filename validation enforced
- ✅ Integration tests pass

---

## 💾 Phase 2: Planning State Database (2 days)

**Goal:** SQLite database for transactional state management

### Tasks

#### Task 2.1: Database Schema Design
**Duration:** 4h  
**Files:** `src/database/schema.sql`

Define schema:

```sql
-- Plans table
CREATE TABLE plans (
    plan_id TEXT PRIMARY KEY,
    feature_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('active','complete','failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    config_snapshot TEXT
);

-- Phases table
CREATE TABLE phases (
    phase_id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES plans(plan_id),
    phase_order INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending','running','complete','failed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    phase_id TEXT REFERENCES phases(phase_id),
    description TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending','running','complete','failed')),
    estimated_hours REAL
);

-- Artifacts table
CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES plans(plan_id),
    file_path TEXT NOT NULL,
    artifact_type TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    size_bytes INTEGER,
    CONSTRAINT file_name_len CHECK(length(substr(file_path, instr(file_path, '/') + 1)) <= 20)
);

-- Validations table
CREATE TABLE validations (
    validation_id TEXT PRIMARY KEY,
    phase_id TEXT REFERENCES phases(phase_id),
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    details TEXT
);

-- State snapshots table
CREATE TABLE state_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES plans(plan_id),
    phase_id TEXT REFERENCES phases(phase_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state_data TEXT
);
```

**Validation:**
- Schema includes filename length constraint
- Foreign keys enforced
- Indexes on frequently queried columns

#### Task 2.2: Database Manager Implementation
**Duration:** 1d  
**Files:** `src/database/state_mgr.py`

Implement state manager:

```python
class PlanningStateManager:
    def create_plan(self, plan_id, feature_name, config)
    def create_phase(self, plan_id, phase_name, order)
    def update_phase_status(self, phase_id, status)
    def create_artifact(self, plan_id, file_path, type)
    def rollback_to_phase(self, phase_id)
    def get_plan_status(self, plan_id)
```

**Features:**
- Transaction boundaries per phase
- Automatic rollback on error
- Query methods for status
- Export to JSON for reports

**Validation:**
- Unit tests for all CRUD operations
- Transaction rollback tests
- Concurrent access tests

#### Task 2.3: Migration System
**Duration:** 4h  
**Files:** `src/database/migrate.py`

Schema versioning:
- Version tracking table
- Up/down migrations
- Auto-migrate on startup
- Backup before migration

**Validation:**
- Migration from empty to v1 works
- Rollback to previous version works
- Data preserved during migration

#### Task 2.4: Filename Validation in DB
**Duration:** 2h

Add database-level validation:
- CHECK constraint on artifacts table
- Trigger for filename length validation
- Audit log for violations

**Validation:**
- Insert with 25-char filename FAILS
- Insert with 18-char filename SUCCEEDS
- Violation logged to audit table

### Completion Criteria
- ✅ Database schema created and tested
- ✅ State manager operational with 100% coverage
- ✅ Migration system functional
- ✅ Filename validation enforced at DB level
- ✅ All tests pass

---

## 🏛️ Phase 3: BaseOrchestrator v4.1 (2 days)

**Goal:** Config-driven orchestrator base class

### Tasks

#### Task 3.1: Config Loader
**Duration:** 4h  
**Files:** `src/orchestrators/base_orch.py`

Load and validate YAML config:

```python
class BaseOrchestrator:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.validate_config()
        self.db = PlanningStateManager()
        
    def load_config(self, path: str) -> dict:
        """Load YAML, validate schema"""
        
    def validate_config(self):
        """Ensure required fields present"""
```

**Config Schema:**
```yaml
orchestrator:
  name: "planning_system"
  version: "5.0"
  
phases:
  - id: "discovery"
    name: "Context Discovery"
    tasks: [...]
    validations: [...]
    
folder_structure:
  root: "cortex-brain/docs/plan/active/{plan_id}/"
  subfolders: ["context", "artifacts", "reports", "tracking"]
  
output_formats:
  master_plan: "templates/plan-tmpl.jinja2"
```

**Validation:**
- Config validation rejects invalid YAML
- Required fields enforced
- Folder name validation (20-char limit)

#### Task 3.2: Phase Execution Engine
**Duration:** 1d  
**Files:** `src/orchestrators/base_orch.py`

Implement phase execution:

```python
def execute_phase(self, phase_config: dict) -> dict:
    """Execute single phase with transaction boundary"""
    phase_id = self.db.create_phase(...)
    try:
        self.db.begin_transaction()
        result = self.run_phase_tasks(phase_config)
        self.validate_phase_output(result)
        self.db.commit()
        return result
    except Exception as e:
        self.db.rollback()
        raise
```

**Features:**
- Atomic phase execution
- Rollback on failure
- Progress tracking to DB
- Validation gates

**Validation:**
- Successful phase commits to DB
- Failed phase rolls back
- Progress tracked correctly

#### Task 3.3: Template Rendering
**Duration:** 4h  
**Files:** `src/orchestrators/template.py`

Jinja2 template rendering:

```python
class TemplateRenderer:
    def render(self, template_path: str, context: dict) -> str:
        """Render template with context data"""
        
    def render_to_file(self, template, context, output_path):
        """Render and write to file"""
```

**Features:**
- Load templates from config
- Inject context data
- Write to files
- Validate output

**Validation:**
- Template renders with valid data
- Invalid template raises clear error
- Output file created correctly

#### Task 3.4: Filename Generation & Validation
**Duration:** 4h

Integrate filename validation:

```python
def create_artifact(self, 
                   artifact_type: str,
                   content: str,
                   suggested_name: str = None) -> str:
    """Create artifact with auto-validated filename"""
    
    # Validate/shorten name
    is_valid, error = validate_filename(suggested_name)
    if not is_valid:
        suggested_name = suggest_filename(suggested_name)
    
    # Create file
    path = self.write_file(suggested_name, content)
    
    # Track in DB
    self.db.create_artifact(self.plan_id, path, artifact_type)
    
    return path
```

**Validation:**
- Long filenames auto-shortened
- All created files ≤20 chars
- DB constraint enforced

### Completion Criteria
- ✅ BaseOrchestrator loads config
- ✅ Phase execution with transactions
- ✅ Template rendering operational
- ✅ Filename validation integrated
- ✅ Unit tests at 100% coverage

---

## 📋 Phase 4: Planning Orchestrator v5 (4 days)

**Goal:** Pure Python planning orchestrator

### Tasks

#### Task 4.1: Context Discovery
**Duration:** 1d  
**Files:** `src/orchestrators/plan_orch_v5.py`

Implement discovery phase:

```python
class PlanningOrchestratorV5(BaseOrchestrator):
    def phase_discovery(self, request: str) -> dict:
        """Search workspace for relevant context"""
        
        # Load search patterns from config
        patterns = self.config['phases'][0]['search_patterns']
        
        # Execute searches
        results = []
        for pattern in patterns:
            matches = self.workspace_search(
                pattern['pattern'],
                pattern['scope']
            )
            results.extend(matches)
        
        # Generate context summary
        summary = self.render_template(
            'discovery-summary.jinja2',
            {'files': results, 'request': request}
        )
        
        # Write to file (auto-validated name)
        self.create_artifact('context', summary, 'disc-context.md')
        
        return {'files_found': len(results), 'summary': summary}
```

**Config:**
```yaml
phases:
  - id: "discovery"
    search_patterns:
      - pattern: "class.*"
        scope: "src/**/*.py"
      - pattern: "def test_"
        scope: "tests/**/*.py"
    output_artifacts:
      - type: "context"
        template: "disc-summary.jinja2"
        filename: "disc-context.md"  # ≤20 chars
```

**Validation:**
- Searches execute correctly
- Context summary generated
- Artifact filename validated

#### Task 4.2: Architecture Analysis
**Duration:** 1d  
**Files:** `src/orchestrators/plan_orch_v5.py`

Implement architecture analysis:

```python
def phase_architecture(self, context: dict) -> dict:
    """Analyze codebase architecture"""
    
    # Parse Python files with AST
    modules = self.parse_modules(context['files'])
    
    # Identify patterns
    patterns = self.detect_patterns(modules)
    
    # Generate architecture doc
    arch_doc = self.render_template(
        'arch-analysis.jinja2',
        {'modules': modules, 'patterns': patterns}
    )
    
    # Write artifact (validated name)
    self.create_artifact('context', arch_doc, 'arch.md')
    
    return {'modules': len(modules), 'patterns': patterns}
```

**Validation:**
- AST parsing successful
- Patterns detected correctly
- Architecture doc generated

#### Task 4.3: Plan Generation
**Duration:** 1d  
**Files:** `src/orchestrators/plan_orch_v5.py`

Generate master plan:

```python
def phase_plan_generation(self, discovery: dict, arch: dict) -> dict:
    """Generate comprehensive master plan"""
    
    # Load plan template
    template_cfg = self.config['output_formats']['master_plan']
    
    # Build context
    plan_context = {
        'feature': self.request,
        'files': discovery['files'],
        'architecture': arch['patterns'],
        'phases': self.generate_phases(),
        'tasks': self.generate_tasks()
    }
    
    # Render plan
    plan = self.render_template(template_cfg, plan_context)
    
    # Write to 00-master-plan.md (validated)
    self.create_artifact('plan', plan, '00-master-plan.md')
    
    return {'plan_generated': True, 'phases': len(plan_context['phases'])}
```

**Validation:**
- Plan includes all required sections
- Filename validated (00-master-plan.md ≤20 chars)
- Visual progress tracker included

#### Task 4.4: Folder Structure Creation
**Duration:** 4h  
**Files:** `src/orchestrators/plan_orch_v5.py`

Create planning folders:

```python
def phase_folder_creation(self, plan_id: str) -> dict:
    """Create folder structure atomically"""
    
    # Load structure from config
    folder_cfg = self.config['folder_structure']
    root = folder_cfg['root'].format(plan_id=plan_id)
    
    # Validate root folder name (plan_id ≤20 chars)
    if len(plan_id) > 20:
        plan_id = suggest_filename(plan_id, 20)
        root = folder_cfg['root'].format(plan_id=plan_id)
    
    # Create folders
    os.makedirs(root, exist_ok=True)
    for subfolder in folder_cfg['subfolders']:
        # Validate subfolder name
        if len(subfolder) > 20:
            subfolder = suggest_filename(subfolder, 20)
        path = os.path.join(root, subfolder)
        os.makedirs(path, exist_ok=True)
    
    # Track in DB
    for folder in [root] + subfolders:
        self.db.create_artifact(plan_id, folder, 'directory')
    
    return {'folders_created': len(subfolders) + 1}
```

**Validation:**
- All folder names ≤20 chars
- Folders created successfully
- Tracked in database

#### Task 4.5: Validation & Reporting
**Duration:** 4h  
**Files:** `src/orchestrators/plan_orch_v5.py`

Implement validation phase:

```python
def phase_validation(self, plan_id: str) -> dict:
    """Validate plan completeness"""
    
    validations = self.config['validations']
    results = []
    
    for check in validations:
        passed, details = self.run_validation(check, plan_id)
        results.append({
            'check': check['name'],
            'passed': passed,
            'details': details
        })
        self.db.record_validation(plan_id, check['name'], passed, details)
    
    # Generate report
    report = self.render_template(
        'validation-rpt.jinja2',
        {'results': results}
    )
    
    # Write report (validated filename)
    self.create_artifact('report', report, 'validation.md')
    
    return {'validations': len(results), 'passed': sum(r['passed'] for r in results)}
```

**Validation:**
- All checks execute
- Results tracked in DB
- Report filename ≤20 chars

### Completion Criteria
- ✅ All 5 phases implemented
- ✅ Pure Python (no natural language in config)
- ✅ All filenames ≤20 chars
- ✅ Database state management working
- ✅ Integration tests pass

---

## 📝 Phase 5: Config-Only Manifests (1.5 days)

**Goal:** Transform all manifests to pure configuration

### Tasks

#### Task 5.1: Planning Manifest v5.0
**Duration:** 4h  
**Files:** `cortex-brain/manifests/orch/plan-sys-5.yaml`

Convert to config-only:

**BEFORE (Hybrid):**
```yaml
phases:
  - name: "Discovery"
    instructions: "Search workspace for relevant files"  # ❌
    steps:
      - "Use grep_search to find..."  # ❌
```

**AFTER (Pure Config):**
```yaml
phases:
  - id: "discovery"
    name: "Context Discovery"
    search_patterns:
      - pattern: "class.*"
        scope: "src/**/*.py"
    output_artifacts:
      - type: "context"
        template: "disc-summary.jinja2"
        filename: "disc-context.md"  # Validated ≤20
```

**Validation:**
- No natural language instructions
- All filenames ≤20 chars
- Schema validation passes

#### Task 5.2: ADO Manifest v2.0
**Duration:** 4h  
**Files:** `cortex-brain/manifests/orch/ado-ops-2.yaml`

Convert ADO manifest:

```yaml
orchestrator:
  name: "ado_operations"
  version: "2.0"
  
work_item_templates:
  user_story:
    template: "ado-story.jinja2"
    filename: "story-{id}.md"  # {id} = short ID
    fields: [title, description, acceptance_criteria]
  
  feature:
    template: "ado-feature.jinja2"
    filename: "feat-{id}.md"
    fields: [title, description, scope]
```

**Validation:**
- Config-only (no instructions)
- Template filenames ≤20 chars
- Field schemas defined

#### Task 5.3: Vacuum Manifest v2.0
**Duration:** 4h  
**Files:** `cortex-brain/manifests/orch/vacuum-2.yaml`

Convert Vacuum manifest:

```yaml
orchestrator:
  name: "vacuum"
  version: "2.0"
  
cleanup_patterns:
  temp_files:
    - "**/*.tmp"
    - "**/*.temp"
  cache_dirs:
    - "__pycache__"
    - ".pytest_cache"
    
validation_rules:
  - check: "no_large_files"
    max_size_mb: 100
```

**Validation:**
- Pure configuration
- No imperative commands
- Patterns clearly defined

#### Task 5.4: Cleanup Manifest v2.0
**Duration:** 2h  
**Files:** `cortex-brain/manifests/orch/cleanup-2.yaml`

Convert Cleanup manifest:

```yaml
orchestrator:
  name: "cleanup"
  version: "2.0"
  
targets:
  cache:
    dirs: ["cortex-brain/cache", ".venv/cache"]
  logs:
    dirs: ["logs"]
    retention_days: 30
```

**Validation:**
- Config-only format
- Clear target definitions
- Retention policies defined

### Completion Criteria
- ✅ All 4 manifests converted
- ✅ Zero natural language instructions
- ✅ All filenames validated ≤20 chars
- ✅ Schema validation passes

---

## 🔄 Phase 6-8: ADO, Vacuum, Cleanup Orchestrators (7.5 days)

**Goal:** Implement remaining 3 AUTONOMOUS orchestrators

### Phase 6: ADO Orchestrator v2 (3 days)

#### Task 6.1: Work Item Generator
**Duration:** 1d

Implement user story/feature generation:
- Load templates from config
- Parse user request
- Generate work items
- Write to files (validated names)
- Track in database

**Validation:**
- Work items generated correctly
- All filenames ≤20 chars
- Database updated

#### Task 6.2: Acceptance Criteria Generator
**Duration:** 1d

Generate acceptance criteria:
- Analyze feature requirements
- Generate testable criteria
- Format as Gherkin scenarios
- Write to artifact (validated name)

**Validation:**
- Criteria are testable
- Format is valid Gherkin
- Filename ≤20 chars

#### Task 6.3: Estimation Engine
**Duration:** 1d

Implement story point estimation:
- Analyze complexity factors
- Calculate estimates
- Generate estimation report
- Write to file (validated name)

**Validation:**
- Estimates reasonable
- Report includes rationale
- Filename ≤20 chars

### Phase 7: Vacuum Orchestrator v2 (2.5 days)

#### Task 7.1: Filesystem Scanner
**Duration:** 1d

Implement deep scan:
- Traverse directory tree
- Identify temp/cache files
- Build cleanup plan
- Write report (validated name)

**Validation:**
- Scan identifies targets correctly
- No false positives
- Report filename ≤20 chars

#### Task 7.2: Safe Deletion Engine
**Duration:** 1d

Implement safe cleanup:
- Validate targets
- Create backups if needed
- Execute deletion
- Track in database

**Validation:**
- Only intended files deleted
- Backups created
- Database updated

#### Task 7.3: Reorganization System
**Duration:** 4h

Move/rename files intelligently:
- Suggest better locations
- Validate new names (≤20 chars)
- Execute moves atomically
- Track changes

**Validation:**
- Files moved correctly
- New names ≤20 chars
- Rollback on failure

### Phase 8: Cleanup Orchestrator v2 (2 days)

#### Task 8.1: Cache Manager
**Duration:** 1d

Implement cache cleanup:
- Identify cache directories
- Calculate sizes
- Clean aged entries
- Report results (validated name)

**Validation:**
- Cache cleaned correctly
- Size calculations accurate
- Report filename ≤20 chars

#### Task 8.2: Log Rotation
**Duration:** 1d

Implement log management:
- Find log files
- Apply retention policy
- Archive/compress old logs
- Report results (validated name)

**Validation:**
- Retention policy applied
- Logs archived correctly
- Report filename ≤20 chars

### Completion Criteria
- ✅ All 3 orchestrators operational
- ✅ Pure Python implementations
- ✅ Config-driven behavior
- ✅ All filenames ≤20 chars validated
- ✅ Database state management working
- ✅ Integration tests pass

---

## ✅ Phase 9: Testing & Validation (3 days)

**Goal:** Comprehensive testing of all orchestrators

### Tasks

#### Task 9.1: Unit Tests
**Duration:** 1d

Test individual components:
- BaseOrchestrator methods
- State manager CRUD
- Template rendering
- Filename validation

**Coverage Target:** 100%

**Validation:**
- All tests pass
- Coverage report generated
- Report filename: `test-cov.md` (≤20 chars)

#### Task 9.2: Integration Tests
**Duration:** 1d

Test end-to-end flows:
- Planning orchestrator full run
- ADO work item generation
- Vacuum cleanup execution
- Cleanup cache clearing

**Test Scenarios:**
- Happy path (success)
- Failure scenarios (rollback)
- Long filenames (auto-fix)
- Concurrent access

**Validation:**
- All scenarios pass
- Rollback works correctly
- Long names auto-shortened
- Race conditions handled

#### Task 9.3: MCP Tool Tests
**Duration:** 4h

Test MCP integration:
- Tool invocation via protocol
- Registry lookup
- Error handling
- Result formatting

**Validation:**
- MCP protocol compliance
- Errors properly formatted
- Results include all required fields

#### Task 9.4: Filename Compliance Audit
**Duration:** 4h

Audit all generated files:
- Scan all plan directories
- Check filename lengths
- Validate against rules
- Generate compliance report

**Report:** `artifacts/file-audit.md` (≤20 chars)

**Validation:**
- 100% compliance (all files ≤20 chars)
- Violations auto-fixed
- Report generated

### Completion Criteria
- ✅ 100% unit test coverage
- ✅ All integration tests pass
- ✅ MCP tool functional
- ✅ Filename compliance at 100%
- ✅ All reports generated

---

## 📚 Phase 10: Migration & Documentation (2 days)

**Goal:** Migrate from v4 to v5 and document

### Tasks

#### Task 10.1: Archive Old Manifests
**Duration:** 2h

Move v4 manifests:
- Create `cortex-brain/archives/v4-manifests/`
- Move old YAML files
- Add README explaining archive
- Update gitignore if needed

**Validation:**
- Old manifests archived
- New manifests in place
- README clear

#### Task 10.2: Update CORTEX.prompt.md
**Duration:** 4h

Update intent routing:
- Document MCP tool invocation
- Update hand-off protocol
- Add troubleshooting section
- Update orchestrator table

**Validation:**
- Intent detection tests pass
- Documentation clear
- Examples accurate

#### Task 10.3: Update Response Templates
**Duration:** 4h

Update templates:
- Add v5 orchestrator templates
- Update progress indicators
- Document new format
- Test rendering

**Validation:**
- Templates render correctly
- Progress bars display properly
- Format consistent

#### Task 10.4: Migration Guide
**Duration:** 1d

Write comprehensive guide:
- What changed (hybrid → pure)
- How to migrate custom orchestrators
- Troubleshooting common issues
- FAQ section

**File:** `docs/migrate-v5.md` (≤20 chars)

**Validation:**
- Guide covers all changes
- Examples clear
- FAQ comprehensive

### Completion Criteria
- ✅ Old manifests archived
- ✅ CORTEX.prompt.md updated
- ✅ Response templates updated
- ✅ Migration guide complete
- ✅ All documentation reviewed

---

## 🧹 Phase 11: REFACTOR & Cleanup (2 days)

**Goal:** Whole-file cleanup and optimization

### Tasks

#### Task 11.1: Code Refactoring
**Duration:** 1d

Refactor for clarity:
- Remove duplicate code
- Consolidate utilities
- Improve naming
- Add docstrings

**Files to Review:**
- `src/orchestrators/*.py`
- `src/mcp/*.py`
- `src/database/*.py`
- `src/utils/*.py`

**Validation:**
- No code duplication
- All functions documented
- Type hints present
- Linting passes

#### Task 11.2: File Cleanup
**Duration:** 4h

Clean up workspace:
- Remove temp files
- Delete obsolete code
- Archive old tests
- Update .gitignore

**Validation:**
- No temp files remaining
- Git status clean
- Archive organized

#### Task 11.3: Performance Optimization
**Duration:** 4h

Optimize performance:
- Profile orchestrator execution
- Optimize database queries
- Cache template rendering
- Reduce file I/O

**Target:** <2s execution time for simple plans

**Validation:**
- Profiling report generated
- Optimizations applied
- Performance targets met
- Report: `perf-report.md` (≤20 chars)

#### Task 11.4: Final Validation
**Duration:** 4h

Final checks:
- Run all tests
- Verify filename compliance (100%)
- Check documentation complete
- Validate deployment readiness

**Validation:**
- All tests pass
- 100% filename compliance
- Documentation complete
- Ready for production

### Completion Criteria
- ✅ Code refactored and clean
- ✅ No obsolete files
- ✅ Performance optimized
- ✅ Final validation passed
- ✅ Production ready

---

## 🎯 Success Metrics

### Technical Metrics
- **Execution Reliability:** 100% success rate for valid inputs
- **Atomic Operations:** All phase failures trigger rollback
- **State Consistency:** Database always reflects actual state
- **Deterministic Output:** Same input produces same output
- **Filename Compliance:** 100% of files ≤20 chars

### Performance Metrics
- **Planning Orchestrator:** <5s for simple plans
- **ADO Orchestrator:** <3s per work item
- **Vacuum Orchestrator:** <10s for 1000 files scanned
- **Database Operations:** <50ms per transaction

### Code Quality Metrics
- **Test Coverage:** ≥95% for all components
- **Documentation Coverage:** 100% of public APIs
- **Type Hint Coverage:** 100% of function signatures
- **Linting:** Zero warnings on all files

### User Experience Metrics
- **Clear Progress Indicators:** Visual progress bars in all responses
- **Actionable Errors:** All errors include fix suggestions
- **Resumability:** Plans resumable from any phase
- **Consistency:** Predictable behavior across runs

---

## 🚨 Risks & Mitigations

### Risk 1: Database Schema Changes
**Impact:** HIGH | **Probability:** MEDIUM

**Mitigation:**
- Version schema from v1
- Write migration scripts
- Backup before changes
- Test migrations thoroughly

### Risk 2: Filename Collisions
**Impact:** MEDIUM | **Probability:** LOW

**Mitigation:**
- Add unique suffixes when needed
- Validate before creation
- Use database to track names
- Implement collision detection

### Risk 3: Config Schema Breaking Changes
**Impact:** HIGH | **Probability:** MEDIUM

**Mitigation:**
- Version config schema
- Validate on load
- Provide upgrade tool
- Maintain v4 compatibility mode

### Risk 4: MCP Protocol Changes
**Impact:** MEDIUM | **Probability:** LOW

**Mitigation:**
- Pin MCP protocol version
- Monitor spec changes
- Test against spec regularly
- Implement version negotiation

---

## 📁 Deliverables

### Code
- `src/mcp/` - MCP server and tools
- `src/orchestrators/` - v5 orchestrators (4 files)
- `src/database/` - State management
- `src/utils/file_name.py` - Filename validation

### Configuration
- `cortex-brain/manifests/orch/*.yaml` - Config-only manifests (4 files)
- `cortex-brain/config/mcp-server.yaml` - MCP configuration

### Documentation
- `docs/migrate-v5.md` - Migration guide
- `docs/arch-v5.md` - Architecture overview
- `docs/api-ref.md` - API reference
- `artifacts/file-name-rules.md` - Naming conventions

### Tests
- `tests/mcp/` - MCP tests
- `tests/orchestrators/` - Orchestrator tests
- `tests/database/` - Database tests
- `tests/integration/` - End-to-end tests

### Reports
- `reports/test-cov.md` - Test coverage report
- `reports/file-audit.md` - Filename compliance audit
- `reports/perf-report.md` - Performance analysis

---

## 📚 Reference Documentation

### Source Plans
- `autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md` - Original architecture plan
- `autonomous-orchestrator-v5/architecture/option-1-analysis.md` - Detailed analysis
- `autonomous-orchestrator-v5/architecture/database-schema.md` - DB design

### Key Files
- `CORTEX.prompt.md` - Intent routing
- `brain-protection-rules.yaml` - SKULL rules
- `response-templates-v4.yaml` - Response templates
- `planning-system-4.0-manifest.yaml` - Current (v4) manifest

### Standards
- MCP Protocol Specification v1.0
- CORTEX Filename Convention (≤20 chars, kebab-case)
- Planning System 4.0 Structure
- SQLite Best Practices

---

## 📋 Next Steps

### Immediate (This Week)
1. ✅ Review and approve this implementation plan
2. ⏸️ Begin Phase 0: Foundation Setup
3. ⏸️ Create filename validation utility
4. ⏸️ Set up project structure

### Short-term (Next 2 Weeks)
1. ⏸️ Complete Phase 1: MCP Tool Infrastructure
2. ⏸️ Complete Phase 2: Planning State Database
3. ⏸️ Begin Phase 3: BaseOrchestrator v4.1

### Long-term (Next Month)
1. ⏸️ Complete all 4 orchestrator implementations
2. ⏸️ Comprehensive testing
3. ⏸️ Migration and documentation
4. ⏸️ Production deployment

---

## 🎓 Lessons Learned (Post-Implementation)

**To be completed after Phase 11**

### What Worked Well
- TBD

### What Could Be Improved
- TBD

### Unexpected Challenges
- TBD

### Recommendations for Future Work
- TBD

---

**Response Template:** `autonomous_execution_progress` (response-templates-v4.yaml:863)  
**TDD Enforcement:** Unit tests required before implementation  
**Final Refactor Required:** Yes - Phase 11 whole-file cleanup  

---

## 📝 Copilot Instructions

```yaml
response_template: "autonomous_execution_progress"
tdd_enforcement: true
final_refactor_required: true
filename_validation: true
max_filename_length: 20
filename_format: "kebab-case"
```

---

**Plan Status:** 🟢 READY FOR IMPLEMENTATION  
**Approval Date:** January 2, 2026  
**Target Start:** January 3, 2026  
**Estimated Completion:** January 30, 2026
