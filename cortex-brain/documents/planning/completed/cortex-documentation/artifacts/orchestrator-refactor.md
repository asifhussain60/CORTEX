# 🎯 Orchestrator Panel Documentation Refactor Guide

**Version:** 1.0.0 | **Status:** ✅ ACTIVE  
**Author:** Asif Hussain | **Last Updated:** January 2, 2026  
**Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 📋 Purpose

This document provides comprehensive specifications for generating the CORTEX Orchestrators documentation site with:
- **Level 1 Detail Pages** - Individual orchestrator deep-dives
- **Level 2 Granular Views** - Phase-by-phase breakdowns with interactive diagrams
- **Master Orchestrator Architecture** - Puppeteer pattern coordinating all orchestrators
- **Interactive Visualizations** - D3.js and Mermaid diagrams for architecture understanding

**Target Audience:** CORTEX development team generating docs/ site content

---

## 🔗 Linked Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Glassmorphism Design Standard** | UI/UX patterns and CSS classes | `cortex-brain/documents/standards/glassmorphism-design-standard.md` |
| **Level 1 Specs** | Detailed page specifications | `cortex-brain/documents/planning/active/cortex-documentation/artifacts/level1-specs/` |
| **Site Map** | Complete documentation hierarchy | `cortex-brain/documents/planning/active/cortex-documentation/artifacts/docs-sitemapd.md` |
| **V5 Holistic Refactor Plan** | System-wide architecture transformation | `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md` |

---

## 🏗️ Architecture Overview

### Master Orchestrator Concept

**Core Principle:** One orchestrator to rule them all - the Master Orchestrator acts as a puppeteer, coordinating specialized orchestrators based on user intent.

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX Entry Point                        │
│              (.github/prompts/CORTEX.prompt.md)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              🎭 MASTER ORCHESTRATOR                          │
│         (MasterOrchestratorCoordinator)                      │
│                                                               │
│  Responsibilities:                                            │
│  • Intent classification (LLMIntentClassifier)               │
│  • Orchestrator selection and routing                        │
│  • State management and persistence                          │
│  • Progress tracking and reporting                           │
│  • Error handling and recovery                               │
│  • Multi-orchestrator coordination                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
        ▼             ▼             ▼              ▼
   ┌────────┐   ┌─────────┐   ┌────────┐    ┌─────────┐
   │Planning│   │Execution│   │ System │    │Analysis │
   └────────┘   └─────────┘   └────────┘    └─────────┘
        │             │             │              │
   ┌────┴───┐   ┌────┴───┐   ┌────┴───┐    ┌────┴───┐
   │4 Orch. │   │2 Orch. │   │4 Orch. │    │3 Orch. │
   └────────┘   └────────┘   └────────┘    └────────┘
```

**Key Innovation:** The Master Orchestrator doesn't execute work directly - it coordinates, routes, and monitors specialized orchestrators that handle specific domains.

---

## 📊 Current State Analysis

### Existing Orchestrator Multi-Panel (docs/index.html)

**Location:** Lines 573-700 in `docs/index.html`

**Current Structure:**
```html
<section class="key-features-section" id="orchestrators-panel">
    <div class="main-panel-wrapper animation-t3">
        <div class="panel-header-centered">
            <h2 class="panel-title-main">🎯 ORCHESTRATORS</h2>
            <p class="panel-subtitle-main">...</p>
        </div>
        
        <div class="category-panels-grid">
            <!-- 5 Category Subpanels (2x3 grid) -->
            <!-- Planning, Execution, System, Analysis, Debug -->
        </div>
    </div>
</section>
```

**Current Categories (5):**

| Category | Icon | Orchestrators | Status |
|----------|------|---------------|--------|
| **Planning** (🧠) | 4 orchestrators | Planning System, ADO Orchestrator, ADO Operations, ADO Planning | ✅ Linked |
| **Execution** (⚙️) | 2 orchestrators | TDD Orchestrator, Execution Orchestrator | ✅ Linked |
| **System** (🔧) | 4 orchestrators | Cleanup, Sanitization, System Integrity, Git Checkpoint | ✅ Linked |
| **Analysis** (📊) | 3 orchestrators | Refinement, CORTEX Lens, Architectural Review | ✅ Linked |
| **Debug** (🐛) | 2 orchestrators | Debug Orchestrator, Rollback Orchestrator | ✅ Linked |

**Total:** 15 orchestrators linked from index.html

---

## 🎯 Compliance Issues

From Site Map audit (January 2, 2026):

**Critical Violations (19 files - 100%):**
- 🔴 ALL 19 files use breadcrumb navigation + logo-header (Level 0 pattern on Level 1 pages)
- 🔴 10 files have embedded `<style>` tags in `<head>` (violates zero inline styles rule)
- ❌ 1 file missing (ado-planning.html linked but doesn't exist)
- 🔗 5 files orphaned (exist but not linked in navigation)
- ⛔ **0% COMPLIANCE** - Complete pattern mismatch with design standard

**Priority Fixes:**
1. Replace breadcrumb + logo-header with Level 1 glass header (ALL 19 files)
2. Extract inline styles to main.css (10 files)
3. Create missing ado-planning.html
4. Link or remove 5 orphaned files

---

## 🎭 Master Orchestrator Detailed Architecture (v5.0)

### Component Breakdown

#### 1. Intent Classification Layer

**File:** `src/cortex_agents/llm_intent_classifier.py`

**Purpose:** Hybrid routing with pattern matching (90%+) and LLM fallback (10%)

**v5.0 Architecture:**
- **Primary:** Pattern-based routing via `master-orchestrator.yaml` (regex matching)
- **Fallback:** LLM intent classification for ambiguous requests
- **Confidence Scoring:** HIGH (≥0.8) = execute, MEDIUM (0.5-0.8) = confirm, LOW (<0.5) = fallback

**Pattern Matching Examples:**
```yaml
routing_rules:
  - pattern: "^/CORTEX Plan |^create a plan|^make a plan"
    orchestrator: "planning_system"
    confidence: 1.0
    
  - pattern: "^ado wizard "
    orchestrator: "ado_conversational_wizard"
    confidence: 1.0
    
  - pattern: "^ado story |^ado feature "
    orchestrator: "ado_auto_generator"
    confidence: 1.0
```

**LLM Classification Flow:**
```python
# User: "I need to plan a new authentication feature"

# Step 1: Pattern matching (checks master-orchestrator.yaml)
pattern_result = pattern_router.match(user_request)  # No exact match

# Step 2: LLM classification (fallback)
classifier = LLMIntentClassifier()
result = classifier.classify(user_request)

# Result:
{
    "orchestrator": "planning_system",
    "confidence": 0.95,  # HIGH
    "reasoning": "User mentions 'plan' + 'feature' (planning intent detected)",
    "parameters": {
        "feature_name": "authentication",
        "complexity": "TIER_3_DOCUMENTED"
    }
}
```

---

#### 2. Master Orchestrator Coordinator (NEW)

**File:** `src/orchestrators/master_orchestrator.py`

**Purpose:** Centralized routing layer eliminating LLM-dependent brittleness

**Core Components:**

**A. Orchestrator Registry Management**
```python
class MasterOrchestrator:
    """
    Master Orchestrator coordinates all specialized orchestrators.
    
    Architecture:
    - Machine-readable routing (YAML config)
    - State coordination (PlanningStateDB)
    - Progress monitoring (real-time updates)
    - Error recovery (checkpoints + rollback)
    """
    
    def __init__(self):
        # Load registry from master-orchestrator.yaml
        self.config = self.load_config("cortex-brain/config/master-orchestrator.yaml")
        self.registry = self.build_registry()
        self.db = PlanningStateDB()
        
    def build_registry(self) -> Dict[str, OrchestratorSpec]:
        """
        Build orchestrator registry from config.
        
        Registry Structure:
        {
            "planning_system": {
                "class": "PlanningOrchestratorV5",
                "module": "src.orchestrators.planning_orchestrator_v5",
                "config": "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
                "type": "autonomous",
                "dependencies": []
            },
            "ado_operations": {
                "class": "AdoOrchestratorV2",
                "module": "src.orchestrators.ado_orchestrator_v2",
                "config": "cortex-brain/manifests/orchestrators/ado-operations-2.0-manifest.yaml",
                "type": "autonomous",
                "dependencies": ["planning_system"]  # Can invoke planning for complex features
            }
        }
        """
        
    def route_to_orchestrator(self, intent: Intent) -> OrchestratorResult:
        """
        Route intent to appropriate orchestrator with full lifecycle management.
        
        Flow:
        1. Pattern matching (master-orchestrator.yaml)
        2. LLM fallback if no pattern match (LLMIntentClassifier)
        3. Load orchestrator class from registry
        4. Check dependencies (invoke parent orchestrators if needed)
        5. Instantiate with config + manifest
        6. Register with Master Orchestrator (for callbacks)
        7. Execute with progress tracking
        8. Save execution state to database
        9. Handle errors and recovery
        10. Return formatted result
        """
        # Pattern matching
        orchestrator_name = self.pattern_router.match(intent.raw_request)
        
        if not orchestrator_name:
            # LLM fallback
            orchestrator_name = self.llm_classifier.classify(intent.raw_request)
        
        # Load from registry
        spec = self.registry[orchestrator_name]
        orchestrator_class = self.load_class(spec.module, spec.class_name)
        orchestrator = orchestrator_class(config=spec.config)
        
        # Register callbacks
        orchestrator.master = self
        orchestrator.execution_id = str(uuid.uuid4())
        
        # Execute with monitoring
        with self.progress_monitor(orchestrator):
            result = orchestrator.execute(intent.parameters)
        
        # Save state
        self.db.save_execution_result(orchestrator.execution_id, result)
        
        return result
```

**B. State Persistence (SQLite)**
```python
# Database: cortex-brain/database/orchestration_state.db

Tables:
- orchestrator_executions (id, orchestrator, start_time, end_time, status, result)
- phase_tracking (execution_id, phase_number, phase_name, status, duration, artifacts)
- artifact_registry (execution_id, artifact_path, artifact_type, size, checksum)
- error_log (execution_id, phase_id, error_type, error_message, stack_trace)
- checkpoints (execution_id, phase_id, snapshot_data, created_at)
- orchestrator_dependencies (parent_execution_id, child_execution_id, dependency_type)
```

**C. Progress Monitoring**
```python
class ProgressMonitor:
    """
    Real-time progress tracking across all orchestrators.
    
    Features:
    - Phase completion tracking
    - Token usage monitoring
    - Time estimation (actual vs estimated)
    - Visual progress bars (maintenance-style)
    - Cross-orchestrator coordination
    """
    
    def render_progress(self, orchestrator: BaseOrchestrator):
        """
        Render progress in response format (response-templates-v4.yaml):
        
        ## 🛡️🧠 CORTEX [Orchestrator] Execution
        **Author:** Asif Hussain | **Execution ID:** abc-123-def
        
        **Overall Progress:** ████████░░ 80% 🔄 IN PROGRESS
        
        | Phase | Name | Progress | Duration | Status |
        |-------|------|----------|----------|--------|
        | 1 | Context Discovery | ██████████ | 2m 15s | ✅ Complete |
        | 2 | Governance Validation | ██████████ | 1m 45s | ✅ Complete |
        | 3 | Architecture Analysis | ████████░░ | 1m 30s | 🔄 In Progress |
        | 4 | Plan Generation | ░░░░░░░░░░ | -- | ⏸️ Not Started |
        | 5 | Folder Creation | ░░░░░░░░░░ | -- | ⏸️ Not Started |
        
        **Next:** Analyzing architecture with governance constraints...
        """
```

**D. Cross-Session Context Middleware (Phase 4.5 - COMPLETE)**
```python
class CrossSessionContextMiddleware:
    """
    Lightweight context injection from Tier 1 Working Memory.
    
    Features:
    - Last 3 sessions metadata (<200 tokens)
    - "continue" pattern detection → automatic routing
    - Session tracking: orchestrator_used, primary_intent, artifacts_created
    - 99.6% token efficiency (context only when needed)
    
    Integration:
    User Input → Middleware (Tier 1 query) → Master Orchestrator → Orchestrator
                      ↓ ("continue" detected)
                  Route to last_orchestrator_used
    """
    
    def inject_context(self, user_request: str) -> ContextInjection:
        """
        Query Tier 1 Working Memory for last 3 sessions.
        
        Returns:
        {
            "is_continuation": true,
            "last_orchestrator": "planning_system",
            "last_execution_id": "abc-123-def",
            "session_metadata": [
                {
                    "session_id": "session-001",
                    "orchestrator_used": "planning_system",
                    "primary_intent": "plan authentication feature",
                    "artifacts_created": ["00-master-plan.md", "context/discovery.md"],
                    "status": "in_progress"
                }
            ]
        }
        """
```

---

#### 3. Orchestrator Base Class v4.1 (Enhanced)

**File:** `src/orchestrators/base/base_orchestrator_v4_1.py`

**Current Features:**
- Standardized initialization
- Workspace detection
- Brain tier integration
- Template management
- Error handling

**v4.1 Enhancements (NEW):**
```python
class BaseOrchestratorV4_1(ABC):
    """
    Enhanced base class with Master Orchestrator integration.
    
    Key Changes:
    - Config-driven execution (no natural language interpretation)
    - Master Orchestrator callbacks
    - Database state tracking
    - Progress reporting hooks
    - Checkpoint/rollback support
    """
    
    def __init__(self, config_path: str):
        # Existing
        self.workspace_root = self.detect_workspace()
        self.brain_path = Path(self.workspace_root) / "cortex-brain"
        
        # NEW: Master Orchestrator integration
        self.master = None  # Set by MasterOrchestrator.route_to_orchestrator()
        self.execution_id = str(uuid.uuid4())
        self.db = PlanningStateDB()
        
        # NEW: Config loading (YAML only, no natural language)
        self.config = self.load_config(config_path)
        
        # NEW: Progress callback hooks
        self.on_phase_start = None
        self.on_phase_complete = None
        self.on_task_complete = None
        
    def execute(self, user_request: str) -> OrchestratorResult:
        """
        Execute orchestrator workflow (must be implemented by subclass).
        
        Flow:
        1. Parse user request (extract parameters)
        2. Create execution record in database
        3. Execute phases sequentially
        4. Report progress after each phase
        5. Create checkpoints for resumability
        6. Handle errors with rollback
        7. Return formatted result
        """
        
    def execute_phase(self, phase_config: dict) -> PhaseResult:
        """
        Execute a single phase with progress tracking.
        
        Args:
            phase_config: Phase configuration from manifest (YAML)
        
        Returns:
            PhaseResult with status, duration, artifacts
        """
        phase_id = self.db.start_phase(
            execution_id=self.execution_id,
            phase_number=phase_config["number"],
            phase_name=phase_config["name"]
        )
        
        try:
            # Execute phase logic (implemented by subclass)
            result = self._execute_phase_logic(phase_config)
            
            # Report progress to Master Orchestrator
            self.report_progress(
                phase=phase_config["number"],
                progress=1.0,  # 100% complete
                status="completed"
            )
            
            # Create checkpoint
            self.checkpoint(phase_id, result.data)
            
            self.db.complete_phase(phase_id, duration=result.duration)
            return result
            
        except Exception as e:
            self.db.fail_phase(phase_id, error=str(e))
            raise
        
    def report_progress(self, phase: int, progress: float, status: str):
        """Report progress to master orchestrator."""
        if self.master:
            self.master.update_progress(
                execution_id=self.execution_id,
                phase=phase,
                progress=progress,
                status=status
            )
    
    def checkpoint(self, phase_id: str, data: Dict):
        """Save checkpoint to database for resumability."""
        self.db.create_snapshot(
            execution_id=self.execution_id,
            phase_id=phase_id,
            snapshot_data=data
        )
    
    def rollback_to_checkpoint(self, snapshot_id: str) -> bool:
        """Rollback to previous checkpoint on error."""
        snapshot = self.db.get_snapshot(snapshot_id)
        if snapshot:
            self.restore_state(snapshot.data)
            return True
        return False
```

---

## 📚 Complete Orchestrator Catalog

### Category 1: Planning (🧠)

#### 1.1 Planning System v5 (PURE AUTONOMOUS)
**File:** `src/orchestrators/planning_orchestrator_v5.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`  
**Type:** 🛡️ AUTONOMOUS (Config-Only)  
**Status:** 🚧 IN DEVELOPMENT (v5.0 - Pure Autonomous Architecture)

**Purpose:** Pure autonomous planning with zero natural language in manifest, integrated with Tier 0 Governance, Tier 2 Knowledge Graphs, and AST-based context discovery

**v5.0 ENHANCEMENTS:**
- ✨ **Zero Natural Language:** All execution logic in Python, manifest contains only configuration data
- ✨ **Tier 0 Governance Integration:** Validates plans against `brain-protection-rules.yaml` (61 rules, 24 layers)
- ✨ **Knowledge Graph Queries:** Leverages Tier 2 knowledge graphs for feature relationships, dependencies, and risks
- ✨ **AST-Based Discovery:** Incremental AST builder for per-turn context gathering (559 lines)
- ✨ **Master Orchestrator Integration:** Registered with Master Orchestrator for coordinated execution
- ✨ **Cross-Session Context:** Integrates with Context Middleware for continuation intelligence
- ✨ **SQLite State Tracking:** All phases tracked in PlanningStateDB with ACID transactions
- ✨ **Resumable Plans:** Can resume from any phase using database snapshots

**New Execution Flow (10 Phases):**
0. **Phase 0:** Context Discovery - AST parsing, workspace search, related files
1. **Phase 1:** Governance Validation (NEW) - Tier 0 rules check, Tier 2 knowledge graph queries
2. **Phase 2:** Architecture Analysis - with governance constraints applied
3. **Phase 3:** Plan Generation - SKULL rules enforced, template-driven markdown
4. **Phase 4:** Folder Creation - atomic filesystem operations (context/, artifacts/, reports/, tracking/)
5. **Phase 5:** Validation - automated compliance checks, governance review

**Governance Features:**
- **tier0_instincts Enforcement:** TDD_ENFORCEMENT, INCREMENTAL_PLAN_GENERATION, DOCUMENT_ORGANIZATION
- **Critical Path Protection:** Blocks modifications to `CORTEX/src/tier0/`, `.github/prompts/internal/`
- **Knowledge Graph Context:** Provides related features, dependencies, historical risks automatically

**Components:**
- `planning_orchestrator_v5.py` - Pure Python implementation (732 lines)
- `incremental_ast_builder.py` - Per-turn AST context building (559 lines)
- `governance_integrator.py` - Tier 0 brain protection validation (NEW)
- `knowledge_graph_query.py` - Tier 2 knowledge graph queries (NEW)

**Level 2 Visualization:** 
- Flowchart: 10-phase execution flow with governance gates
- Sequence diagram: Tier 0 + Tier 2 integration pattern
- State diagram: Plan lifecycle with checkpoints

---

#### 1.2 ADO Orchestrator v2 (ENHANCED)
**File:** `src/orchestrators/ado/ado_orchestrator_v2.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/ado-operations-2.0-manifest.yaml`  
**Type:** 🛡️ AUTONOMOUS (Config-Only)  
**Status:** 🚧 IN DEVELOPMENT (v2.0 - Pure Autonomous with Conversational Wizard)

**Purpose:** Azure DevOps work item generation with dual-mode operation: auto-generation + conversational wizard

**v2.0 ENHANCEMENTS:**
- ✨ **Dual-Mode Operation:**
  - **Auto Mode:** `ado story [feature]` - Full auto-generation (original 6-phase workflow)
  - **Wizard Mode:** `ado wizard [feature]` - Multi-turn conversational wizard (NEW)
- ✨ **Conversational Wizard:** 7-stage interactive workflow for complex requirements gathering
- ✨ **Zero Natural Language Manifest:** Config-only YAML, all logic in Python
- ✨ **Master Orchestrator Integration:** Pattern-based routing (`ado wizard` vs `ado story`)
- ✨ **State Persistence:** Wizard state saved to database, resumable across sessions
- ✨ **18x Faster:** Pure conversational (5s) vs browser SPA (36s+ with context switching)

**Conversational Wizard Stages (NEW - Task 5.1a):**
1. **Stage 1:** Work Item Type Selection (Story/Feature/Epic/Bug)
2. **Stage 2:** Title + Description Gathering (multi-turn clarification)
3. **Stage 3:** Acceptance Criteria Collection (iterative refinement)
4. **Stage 4:** Dependencies Identification (related work items)
5. **Stage 5:** Effort Estimation (Story Points with justification)
6. **Stage 6:** Tags + Metadata (area path, iteration, priority)
7. **Stage 7:** Review + Confirmation (preview before submission)

**Auto-Generation Phases (Original):**
1. **Phase 1:** Work Item Type Selection
2. **Phase 2:** Requirements Analysis
3. **Phase 3:** Acceptance Criteria Generation
4. **Phase 4:** Effort Estimation
5. **Phase 5:** Dependencies Mapping
6. **Phase 6:** ADO Payload Generation

**Architecture Decision (Conversational vs SPA):**
- ❌ **Rejected:** Browser SPA with form UI (36s+, context switching, security risks, external server)
- ✅ **Accepted:** Conversational wizard in chat (5s, no context loss, zero security risk, maintainable)

**Components:**
- `ado_orchestrator_v2.py` - Main orchestrator with mode detection
- `ado_conversational_wizard.py` - Multi-turn wizard implementation (NEW)
- `ado_auto_generator.py` - Original auto-generation workflow

**Level 2 Visualization:** 
- Flowchart: Dual-mode routing decision tree
- Sequence diagram: Wizard stages with user interaction points
- Comparison diagram: Conversational vs SPA architecture

---

#### 1.3 ADO Operations
**File:** `src/orchestrators/ado/ado_operations.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/ado-operations-manifest.yaml`  
**Type:** 🛡️ AUTONOMOUS  
**Status:** ✅ ACTIVE

**Purpose:** CRUD operations for ADO work items

**Key Features:**
- Create/Update/Delete work items
- Query work items by filter
- Link parent/child relationships
- Attach files and comments
- Bulk operations

---

#### 1.4 ADO Planning
**File:** NOT CREATED (❌ MISSING)  
**Manifest:** TBD  
**Type:** 🛡️ AUTONOMOUS  
**Status:** ⏸️ PLANNED

**Purpose:** Sprint planning and backlog management

**Planned Features:**
- Sprint capacity planning
- Backlog prioritization
- Velocity tracking
- Burndown chart generation

---

### Category 2: Execution (⚙️)

#### 2.1 TDD Orchestrator
**File:** `src/orchestrators/tdd/tdd_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE (v4.0)

**Purpose:** Test-Driven Development workflow automation

**Key Features:**
- RED→GREEN→REFACTOR cycle enforcement
- Pytest integration
- Test generation from specs
- Coverage tracking
- Mutation testing

**Phases:**
1. **RED:** Write failing test
2. **GREEN:** Minimal implementation to pass
3. **REFACTOR:** Improve code quality
4. **VALIDATE:** Run full test suite
5. **COVERAGE:** Measure code coverage
6. **REPORT:** Generate test report

**Level 2 Visualization:** Flowchart showing TDD cycle with decision points

---

#### 2.2 Execution Orchestrator
**File:** `src/orchestrators/execution_orchestrator.py`  
**Manifest:** TBD  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** General execution coordination

**Key Features:**
- Multi-phase execution
- Checkpoint management
- Rollback support
- Error recovery

---

### Category 3: System (🔧)

#### 3.1 Cleanup Orchestrator
**File:** `src/orchestrators/system/cleanup_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/aggressive-cleanup-rules.yaml`  
**Type:** 🛡️ AUTONOMOUS  
**Status:** ✅ ACTIVE

**Purpose:** Automated cache and temporary file cleanup

**Key Features:**
- Cache cleanup (pytest, mypy, Python)
- Bloat detection and removal
- Duplicate file detection
- Safe deletion with rollback

**Cleanup Types:**
- `cache`: Clear all caches
- `bloat`: Remove large unused files
- `temp`: Remove temporary files
- `duplicates`: Remove duplicate files
- `full`: All of the above

**Level 2 Visualization:** DFD showing cleanup workflow and decision tree

---

#### 3.2 Sanitization Orchestrator
**File:** `src/orchestrators/sanitization/sanitization_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml`  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** Code anonymization and genericization

**Phases:**
1. **Phase 1:** Scan for sensitive data
2. **Phase 2:** Replace identifiers
3. **Phase 3:** Sanitize comments
4. **Phase 4:** Update documentation
5. **Phase 5:** Validation

---

#### 3.3 System Integrity
**File:** `src/orchestrators/system/system_integrity.py`  
**Manifest:** TBD  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** System health validation

**Key Features:**
- Brain tier validation
- File integrity checks
- Dependency validation
- Configuration verification

---

#### 3.4 Git Checkpoint
**File:** `src/orchestrators/git_checkpoint_orchestrator.py`  
**Manifest:** TBD  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** Automated git commit and branch management

**Key Features:**
- Auto-commit on phase complete
- Checkpoint tagging
- Branch creation
- Rollback support

---

### Category 4: Analysis (📊)

#### 4.1 Refinement Orchestrator
**File:** `src/orchestrators/refinement_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml`  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** Code quality improvement workflow

**Phases:**
1. **Phase 1:** Static Analysis
2. **Phase 2:** Code Smell Detection
3. **Phase 3:** Refactoring Recommendations
4. **Phase 4:** Test Coverage Analysis
5. **Phase 5:** Performance Profiling
6. **Phase 6:** Security Audit
7. **Phase 7:** Documentation Review

**Level 2 Visualization:** Mind map showing quality dimensions

---

#### 4.2 CORTEX Lens
**File:** `src/orchestrators/cortex_lens_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml`  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE (v3.0)

**Purpose:** AST-based code analysis and visualization

**Key Features:**
- Abstract Syntax Tree parsing
- Dependency graph generation
- Complexity metrics
- Interactive dashboards

**Level 2 Visualization:** D3.js interactive dependency graph

---

#### 4.3 Architectural Review
**File:** `src/orchestrators/architectural_review_orchestrator.py`  
**Manifest:** TBD  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** Architecture assessment and recommendations

**Key Features:**
- SOLID principles validation
- Design pattern detection
- Architecture smell detection
- Improvement recommendations

---

### Category 5: Debug (🐛)

#### 5.1 Debug Orchestrator
**File:** `src/orchestrators/debug_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml`  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** Intelligent debugging workflow

**Phases:**
1. **Phase 1:** Error Analysis
2. **Phase 2:** Root Cause Identification
3. **Phase 3:** Fix Recommendation
4. **Phase 4:** Test Case Generation
5. **Phase 5:** Validation

**Level 2 Visualization:** Sequence diagram showing debug workflow

---

#### 5.2 Rollback Orchestrator
**File:** `src/orchestrators/rollback_orchestrator.py`  
**Manifest:** TBD  
**Type:** 📋 GUIDED  
**Status:** ✅ ACTIVE

**Purpose:** Undo operations and restore previous states

**Key Features:**
- Phase-level rollback
- Git-based restoration
- Database snapshot restoration
- File system rollback

---

## 📄 Level 1 Page Template

### Standard Structure (All Orchestrators)

**File Pattern:** `docs/orchestrators/{orchestrator-name}.html`

**Required Sections:**

#### 1. Glass Header (Level 1 Pattern)
```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav">
            <a href="../index.html" class="nav-link">
                <i class="fas fa-home"></i> Home
            </a>
        </nav>
    </div>
</header>
```

**⛔ NO LOGO on Level 1 pages** - Only home link navigation

---

#### 2. Hero Section
```html
<section class="hero-section">
    <div class="glass-card-display">
        <div class="hero-icon-wrapper">
            <i class="fas fa-brain"></i> <!-- Orchestrator-specific icon -->
        </div>
        <h1 class="hero-title">{Orchestrator Name}</h1>
        <p class="hero-subtitle">{One-line description}</p>
    </div>
</section>
```

---

#### 3. Key Metrics (4-Column Grid)
```html
<section class="metrics-section">
    <div class="metrics-grid metrics-grid-4">
        <div class="metric-card glass-card-display animation-t1">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">2-5 min</div>
            <div class="metric-label">Execution Time</div>
        </div>
        <!-- 3 more metrics -->
    </div>
</section>
```

**Common Metrics:**
- Execution Time
- Success Rate
- Automation Level
- Integration Points

---

#### 4. Overview Card
```html
<article class="glass-card-display">
    <h2>Overview</h2>
    <p>{Detailed description of orchestrator purpose and capabilities}</p>
    
    <h3>Key Capabilities</h3>
    <ul class="feature-list">
        <li><i class="fas fa-check-circle"></i> Capability 1</li>
        <li><i class="fas fa-check-circle"></i> Capability 2</li>
        <!-- More capabilities -->
    </ul>
</article>
```

---

#### 5. Architecture Diagram (Mermaid)
```html
<article class="glass-card-display">
    <h2>Architecture</h2>
    <div class="mermaid-container">
        <div class="mermaid">
        graph TD
            A[User Request] --> B[Master Orchestrator]
            B --> C[{Orchestrator Name}]
            C --> D[Phase 1]
            C --> E[Phase 2]
            D --> F[Output]
            E --> F
        </div>
    </div>
</article>
```

---

#### 6. Phase Breakdown (Interactive Cards)
```html
<article class="glass-card-display">
    <h2>Execution Phases</h2>
    
    <div class="phase-cards-grid">
        <div class="phase-card glass-card-clickable animation-t1" 
             onclick="window.location.href='{orchestrator-name}-phase-1.html'">
            <div class="phase-number">1</div>
            <h3 class="phase-title">Phase Name</h3>
            <p class="phase-description">Brief description</p>
            <div class="phase-duration">⏱️ 30s</div>
        </div>
        <!-- More phase cards -->
    </div>
</article>
```

**⚠️ Clickable Cards:** Use `.glass-card-clickable` + `.animation-t1` for interactive elements

---

#### 7. Integration Points
```html
<article class="glass-card-display">
    <h2>Integrations</h2>
    
    <div class="integration-grid">
        <div class="integration-card">
            <i class="fas fa-database"></i>
            <span>Brain Tiers</span>
        </div>
        <div class="integration-card">
            <i class="fas fa-file-code"></i>
            <span>Templates</span>
        </div>
        <!-- More integrations -->
    </div>
</article>
```

---

#### 8. Usage Examples
```html
<article class="glass-card-display">
    <h2>Usage</h2>
    
    <div class="code-example">
        <div class="code-header">
            <span class="code-language">Command</span>
        </div>
        <pre><code>/CORTEX Plan user authentication</code></pre>
    </div>
    
    <div class="expected-output">
        <h4>Expected Output:</h4>
        <p>Creates planning structure in cortex-brain/documents/planning/active/...</p>
    </div>
</article>
```

---

#### 9. Configuration
```html
<article class="glass-card-display">
    <h2>Configuration</h2>
    
    <div class="config-table">
        <table>
            <thead>
                <tr>
                    <th>Parameter</th>
                    <th>Type</th>
                    <th>Default</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>execution_mode</code></td>
                    <td>enum</td>
                    <td>autonomous</td>
                    <td>Execution mode (autonomous/supervised)</td>
                </tr>
                <!-- More config -->
            </tbody>
        </table>
    </div>
</article>
```

---

#### 10. Related Orchestrators (Clickable Cards)
```html
<article class="glass-card-display">
    <h2>Related Orchestrators</h2>
    
    <div class="related-grid">
        <a href="tdd-orchestrator.html" class="related-card glass-card-clickable animation-t1">
            <div class="related-icon">✅</div>
            <div class="related-title">TDD Orchestrator</div>
            <div class="related-description">Test-driven development workflow</div>
        </a>
        <!-- More related orchestrators -->
    </div>
</article>
```

---

## 📑 Level 2 Page Template (Granular Phase View)

### Purpose
Deep-dive into individual phases with:
- Step-by-step execution flow
- Input/output specifications
- Interactive diagrams
- Code examples
- Troubleshooting guides

---

### File Pattern
`docs/orchestrators/{orchestrator-name}-phase-{N}.html`

Example: `docs/orchestrators/planning-system-phase-1.html`

---

### Required Sections

#### 1. Glass Header (Same as Level 1)
```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav">
            <a href="../index.html" class="nav-link">
                <i class="fas fa-home"></i> Home
            </a>
            <a href="planning-system.html" class="nav-link">
                <i class="fas fa-arrow-left"></i> Planning System
            </a>
        </nav>
    </div>
</header>
```

**Breadcrumb:** Home → Parent Orchestrator → Current Phase

---

#### 2. Phase Hero
```html
<section class="hero-section">
    <div class="glass-card-display">
        <div class="phase-badge">Phase 1</div>
        <h1 class="hero-title">Feature Analysis & Complexity Assessment</h1>
        <p class="hero-subtitle">Planning System</p>
    </div>
</section>
```

---

#### 3. Phase Metrics
```html
<div class="metrics-grid metrics-grid-4">
    <div class="metric-card glass-card-display">
        <div class="metric-icon">⏱️</div>
        <div class="metric-value">30-45s</div>
        <div class="metric-label">Duration</div>
    </div>
    <div class="metric-card glass-card-display">
        <div class="metric-icon">🔄</div>
        <div class="metric-value">Automatic</div>
        <div class="metric-label">Mode</div>
    </div>
    <div class="metric-card glass-card-display">
        <div class="metric-icon">📊</div>
        <div class="metric-value">5 tasks</div>
        <div class="metric-label">Task Count</div>
    </div>
    <div class="metric-card glass-card-display">
        <div class="metric-icon">✅</div>
        <div class="metric-value">100%</div>
        <div class="metric-label">Success Rate</div>
    </div>
</div>
```

---

#### 4. Phase Overview
```html
<article class="glass-card-display">
    <h2>Phase Overview</h2>
    <p>{Detailed description of what this phase does}</p>
    
    <h3>Inputs</h3>
    <ul>
        <li><strong>user_request:</strong> Feature description from user</li>
        <li><strong>target_files:</strong> Optional list of files to analyze</li>
    </ul>
    
    <h3>Outputs</h3>
    <ul>
        <li><strong>complexity_tier:</strong> TIER_1 to TIER_4</li>
        <li><strong>feature_analysis:</strong> JSON with feature breakdown</li>
        <li><strong>estimated_duration:</strong> Time estimate in hours</li>
    </ul>
</article>
```

---

#### 5. Execution Flow (Mermaid Flowchart)
```html
<article class="glass-card-display">
    <h2>Execution Flow</h2>
    
    <div class="mermaid-container">
        <div class="mermaid">
        flowchart TD
            A[Start Phase 1] --> B{Parse User Request}
            B -->|Success| C[Analyze Complexity]
            B -->|Failure| Z[Error: Invalid Request]
            C --> D{Complexity Tier?}
            D -->|TIER_1| E[Quick Response Path]
            D -->|TIER_2| F[Inline Plan Path]
            D -->|TIER_3/4| G[Full Planning Path]
            E --> H[Complete Phase 1]
            F --> H
            G --> H
            H --> I[Save Analysis]
            I --> J[Proceed to Phase 2]
            Z --> K[Abort Execution]
        </div>
    </div>
</article>
```

---

#### 6. Task Breakdown (Expandable Cards)
```html
<article class="glass-card-display">
    <h2>Tasks</h2>
    
    <div class="task-list">
        <div class="task-card glass-card-display animation-t1">
            <div class="task-header" onclick="toggleTask(1)">
                <div class="task-number">1</div>
                <h3 class="task-title">Parse User Request</h3>
                <i class="fas fa-chevron-down task-toggle"></i>
            </div>
            <div class="task-content" id="task-1" style="display: none;">
                <p><strong>Purpose:</strong> Extract feature name, scope, and initial requirements</p>
                
                <h4>Steps:</h4>
                <ol>
                    <li>Remove meta-directives (e.g., "Follow instructions in...")</li>
                    <li>Identify core intent (plan vs implement)</li>
                    <li>Extract feature name</li>
                    <li>Identify target files (if any)</li>
                    <li>Classify complexity signals</li>
                </ol>
                
                <h4>Code Example:</h4>
                <pre><code class="language-python">
def parse_request(user_request: str) -> ParsedRequest:
    # Remove meta-directives
    cleaned = remove_meta_directives(user_request)
    
    # Extract feature name
    feature_name = extract_feature_name(cleaned)
    
    # Identify complexity signals
    signals = identify_complexity_signals(cleaned)
    
    return ParsedRequest(
        feature_name=feature_name,
        signals=signals
    )
                </code></pre>
            </div>
        </div>
        <!-- More task cards -->
    </div>
</article>

<script>
function toggleTask(taskId) {
    const content = document.getElementById(`task-${taskId}`);
    const toggle = content.previousElementSibling.querySelector('.task-toggle');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.classList.add('rotated');
    } else {
        content.style.display = 'none';
        toggle.classList.remove('rotated');
    }
}
</script>
```

---

#### 7. Data Flow Diagram (D3.js)
```html
<article class="glass-card-display">
    <h2>Data Flow</h2>
    
    <div id="data-flow-diagram" class="d3-diagram"></div>
    
    <script src="../assets/js/d3.min.js"></script>
    <script>
    // D3.js visualization of data flow
    const width = 800;
    const height = 400;
    
    const svg = d3.select("#data-flow-diagram")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Nodes
    const nodes = [
        {id: "input", label: "User Request", x: 100, y: 200},
        {id: "parser", label: "Parser", x: 300, y: 200},
        {id: "analyzer", label: "Complexity Analyzer", x: 500, y: 200},
        {id: "output", label: "Analysis Result", x: 700, y: 200}
    ];
    
    // Links
    const links = [
        {source: "input", target: "parser"},
        {source: "parser", target: "analyzer"},
        {source: "analyzer", target: "output"}
    ];
    
    // Render nodes and links
    // ... D3.js rendering code ...
    </script>
</article>
```

---

#### 8. Decision Logic (Mermaid Decision Tree)
```html
<article class="glass-card-display">
    <h2>Decision Logic</h2>
    
    <div class="mermaid-container">
        <div class="mermaid">
        graph TD
            A[Analyze Request] --> B{Contains 'plan' keyword?}
            B -->|Yes| C{Contains target files?}
            B -->|No| D{Contains 'implement'?}
            C -->|Yes| E[TIER_3: File-specific plan]
            C -->|No| F{Estimated complexity?}
            F -->|Low| G[TIER_2: Inline plan]
            F -->|High| H[TIER_4: Complex nested plan]
            D -->|Yes| I[Skip planning, direct implementation]
            D -->|No| J[Default to TIER_3]
        </div>
    </div>
</article>
```

---

#### 9. Troubleshooting
```html
<article class="glass-card-display">
    <h2>Troubleshooting</h2>
    
    <div class="troubleshooting-list">
        <div class="trouble-item">
            <div class="trouble-header">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Error: Invalid feature name</h3>
            </div>
            <div class="trouble-content">
                <p><strong>Cause:</strong> Feature name contains special characters or is too long</p>
                <p><strong>Solution:</strong> Sanitize feature name using kebab-case, max 50 chars</p>
                <pre><code>sanitized_name = sanitize_feature_name(feature_name)</code></pre>
            </div>
        </div>
        <!-- More troubleshooting items -->
    </div>
</article>
```

---

#### 10. Phase Navigation
```html
<article class="glass-card-display">
    <h2>Phase Navigation</h2>
    
    <div class="phase-nav-grid">
        <a href="planning-system-phase-0.html" class="phase-nav-card glass-card-clickable animation-t1">
            <i class="fas fa-arrow-left"></i>
            <span>Previous: Phase 0 - Discovery</span>
        </a>
        <a href="planning-system.html" class="phase-nav-card glass-card-clickable animation-t1">
            <i class="fas fa-th"></i>
            <span>All Phases</span>
        </a>
        <a href="planning-system-phase-2.html" class="phase-nav-card glass-card-clickable animation-t1">
            <i class="fas fa-arrow-right"></i>
            <span>Next: Phase 2 - Requirements</span>
        </a>
    </div>
</article>
```

---


## 📊 Diagram Specifications

### Mermaid Diagrams

#### 1. Flowchart (Process Flow)
**Use Case:** Show sequential steps, decision points, and branching logic

**Example: Planning System Tier Routing**
```mermaid
flowchart TD
    A[User Request] --> B{Parse Intent}
    B -->|Plan Command| C[Planning Mode]
    B -->|Implement Command| D[Implementation Mode]
    C --> E{Complexity Analysis}
    E -->|<2s| F[TIER 1: INSTANT]
    E -->|<10s| G[TIER 2: LIGHTWEIGHT]
    E -->|10-60min| H[TIER 3: DOCUMENTED]
    E -->|>1hr| I[TIER 4: COMPLEX]
    F --> J[Direct Response]
    G --> K[Inline Validation]
    H --> L[Single MD Plan]
    I --> M[Nested Plan Structure]
```

---

## 🔄 Updating docs/index.html Multi-Panel

### Current Structure Analysis

**Location:** Lines 573-700 in `docs/index.html`

**Current Implementation:**
- Static HTML with hardcoded orchestrator links
- 5 categories in 2x3 grid layout
- 15 total orchestrators linked

**Issues:**
- Not maintainable (requires manual HTML editing)
- No status indicators (active/planned)
- No version information
- Missing orchestrator metadata

---

### Proposed Dynamic Implementation

#### Step 1: Create Data File

**File:** `docs/assets/data/orchestrators.json`

Store all orchestrator metadata in structured JSON format with categories, orchestrators, status, versions, and phase counts.

#### Step 2: JavaScript Generator

**File:** `docs/assets/js/orchestrators-panel.js`

Dynamic panel generator that:
- Fetches JSON data
- Generates HTML structure
- Applies glassmorphism classes
- Handles status indicators
- Maintains accessibility

#### Step 3: Update HTML

Replace static content with dynamic container and loading placeholder.

#### Step 4: Add Status CSS

Add visual indicators for planned/active status with proper hover states.

---


## 🎯 Implementation Strategy

### Phase 1: Master Orchestrator Foundation (Week 1)

**Goal:** Build core coordination layer

**Tasks:**
1. Create `src/orchestrators/master_orchestrator.py`
2. Implement orchestrator registry
3. Add state database (SQLite)
4. Build progress monitoring system
5. Test with 2-3 existing orchestrators

**Deliverables:**
- Working master orchestrator
- Database schema
- Unit tests (>80% coverage)
- Integration tests

---

### Phase 2: Fix Existing Pages (Week 2)

**Goal:** Bring all 19 orchestrator pages to 100% compliance

**Tasks:**
1. Replace breadcrumb navigation with glass header (ALL files)
2. Extract inline styles to main.css (10 files)
3. Create missing ado-planning.html
4. Link or archive 5 orphaned files
5. Validate against glassmorphism standard

**Deliverables:**
- 19 compliant Level 1 pages
- 0% → 100% compliance rate
- Validation report

---

### Phase 3: Level 2 Pages (Weeks 3-4)

**Goal:** Create granular phase views for top 5 orchestrators

**Priority Orchestrators:**
1. Planning System (10 phases)
2. TDD Orchestrator (6 phases)
3. Refinement Orchestrator (7 phases)
4. ADO Orchestrator (7 phases)
5. Debug Orchestrator (5 phases)

**Per Orchestrator:**
- Create Level 2 pages for each phase
- Add interactive diagrams (Mermaid + D3.js)
- Include code examples
- Add troubleshooting guides

**Deliverables:**
- 35 Level 2 pages (5 orchestrators × 7 avg phases)
- Interactive visualizations
- Navigation between phases

---

### Phase 4: Dynamic Panel System (Week 5)

**Goal:** Make index.html orchestrators panel data-driven

**Tasks:**
1. Create orchestrators.json data file
2. Build JavaScript panel generator
3. Update index.html to use dynamic system
4. Add status indicators and tooltips
5. Test responsiveness

**Deliverables:**
- JSON data file
- Panel generator script
- Updated index.html
- Documentation

---

### Phase 5: Documentation & Testing (Week 6)

**Goal:** Complete documentation and comprehensive testing

**Tasks:**
1. Write developer guide for adding new orchestrators
2. Create design system documentation
3. Build automated compliance checker
4. Perform accessibility audit
5. Cross-browser testing

**Deliverables:**
- Developer guide
- Compliance checker script
- Accessibility report
- Browser compatibility matrix

---

## 📚 Quick Reference

### File Locations

| File Type | Location | Example |
|-----------|----------|---------|
| **Level 1 Pages** | `docs/orchestrators/{name}.html` | `planning-system.html` |
| **Level 2 Pages** | `docs/orchestrators/{name}-phase-{N}.html` | `planning-system-phase-1.html` |
| **Orchestrator Data** | `docs/assets/data/orchestrators.json` | Central metadata |
| **JavaScript** | `docs/assets/js/orchestrators-panel.js` | Panel generator |
| **Diagrams** | `docs/assets/js/{name}-diagram.js` | D3.js visualizations |
| **Python Orchestrators** | `src/orchestrators/{category}/{name}.py` | Implementation |
| **Manifests** | `cortex-brain/manifests/orchestrators/{name}.yaml` | Configuration |

---

### CSS Classes Reference

| Class | Purpose | Use When |
|-------|---------|----------|
| `.glass-header` | Level 1 navigation header | All Level 1/2 pages |
| `.glass-card-display` | Non-interactive cards | Information display |
| `.glass-card-clickable` | Interactive cards/links | Navigational elements |
| `.animation-t1` | Subtle hover effects | Level 1/2 pages (required) |
| `.category-panels-grid` | Multi-panel grid | Orchestrators panel |
| `.category-subpanel` | Individual category panel | Within multi-panel |
| `.category-tag` | Clickable orchestrator link | Within subpanels |
| `.phase-card` | Phase navigation card | Level 1 phase sections |
| `.mermaid-container` | Diagram wrapper | All Mermaid diagrams |

---

### Mermaid Diagram Types

| Type | Syntax | Best For |
|------|--------|----------|
| **Flowchart** | `flowchart TD` | Process flows, decision logic |
| **Sequence** | `sequenceDiagram` | Component interactions |
| **Mindmap** | `mindmap` | Conceptual hierarchies |
| **State** | `stateDiagram-v2` | Status transitions |
| **Gantt** | `gantt` | Timeline visualizations |

---

### D3.js Visualizations

| Type | Best For | Example |
|------|----------|---------|
| **Force Graph** | Dependencies, relationships | Orchestrator dependencies |
| **Tree** | Hierarchies, phases | Planning phase breakdown |
| **Sankey** | Flow diagrams | Data flow between components |
| **Network** | Connections, integrations | Brain tier connections |

---

## ✅ Compliance Checklist

Use this checklist when creating new orchestrator pages:

### Level 1 Pages

- [ ] Glass header with home link only (NO logo)
- [ ] Hero section with orchestrator icon
- [ ] 4-column metrics grid
- [ ] Overview card with capabilities
- [ ] Architecture diagram (Mermaid)
- [ ] Phase breakdown (clickable cards)
- [ ] Integration points
- [ ] Usage examples
- [ ] Configuration table
- [ ] Related orchestrators
- [ ] Zero inline styles
- [ ] T1 animations only
- [ ] Mobile responsive (375px/768px/1440px)
- [ ] Proper spacing (min 24px between cards)

### Level 2 Pages

- [ ] Glass header with breadcrumb (Home → Parent → Phase)
- [ ] Phase hero with badge
- [ ] Phase metrics (4-column)
- [ ] Phase overview with inputs/outputs
- [ ] Execution flow diagram (Mermaid)
- [ ] Task breakdown (expandable cards)
- [ ] Data flow diagram (D3.js or Mermaid)
- [ ] Decision logic diagram
- [ ] Troubleshooting section
- [ ] Phase navigation (prev/all/next)
- [ ] Zero inline styles
- [ ] T1 animations only

---

## 🔗 Related Documents

| Document | Purpose |
|----------|---------|
| [Glassmorphism Design Standard](../../../../standards/glassmorphism-design-standard.md) | UI/UX patterns |
| [Level 1 Specs](./level1-specs/) | Page specifications |
| [Site Map](./docs-sitemapd.md) | Complete hierarchy |
| [V5 Holistic Refactor](../../cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md) | Architecture plan |
| [CORTEX Entry Point](../../../../../.github/prompts/CORTEX.prompt.md) | Intent routing |

---

## 📝 Notes for CORTEX Development

### When Adding New Orchestrators

1. **Create Python Implementation:** `src/orchestrators/{category}/{name}.py`
2. **Create Manifest:** `cortex-brain/manifests/orchestrators/{name}-manifest.yaml`
3. **Register in Master:** Add to `MasterOrchestrator` registry
4. **Update JSON:** Add entry to `docs/assets/data/orchestrators.json`
5. **Create Level 1 Page:** Follow template in this document
6. **Create Level 2 Pages:** One per phase
7. **Add Diagrams:** Mermaid + D3.js visualizations
8. **Update CORTEX.prompt.md:** Add intent routing entry
9. **Test Integration:** Verify master orchestrator routing
10. **Validate Compliance:** Run compliance checker

### Design Principles

1. **Master Orchestrator = Puppeteer** - Coordinates but doesn't execute
2. **Specialized Orchestrators = Performers** - Handle specific domains
3. **State Persistence = Single Source of Truth** - SQLite database
4. **Progress Tracking = User Visibility** - Real-time updates
5. **Error Recovery = Resilience** - Graceful degradation

### Anti-Patterns to Avoid

❌ **DON'T:**
- Hardcode orchestrator logic in master
- Use inline styles in HTML
- Create Level 2 pages beyond phases
- Skip compliance validation
- Mix breadcrumb with glass header
- Use T3 animations on Level 1/2 pages

✅ **DO:**
- Keep master orchestrator generic
- Use CSS classes for all styling
- Stop at Level 2 (no Level 3)
- Validate against design standard
- Use glass header consistently
- Use T1 animations only

---

**Document Version:** 1.0.0  
**Last Updated:** January 2, 2026  
**Status:** ✅ ACTIVE - Ready for implementation  
**Next Review:** After Phase 1 completion

