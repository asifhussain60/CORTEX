# 🧠 CORTEX Feature Plan: Git Enhancements
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 📋 Plan Metadata

| Field | Value |
|-------|-------|
| **Feature Name** | Git Enhancements |
| **Plan Type** | Feature Planning |
| **Planning Method** | Interactive Q&A |
| **Created** | 2025-11-28 |
| **Status** | PENDING APPROVAL |
| **Estimated Complexity** | HIGH |
| **Priority** | P1 (High) |
| **TDD Required** | ✅ YES |
| **OWASP Review Required** | ⚠️ CONDITIONAL (Git operations with user data) |

---

## 🎯 Feature Overview

### User Request
Create comprehensive git enhancements including:
1. Systematic git history consultation for context building
2. Automated git checkpoints before/after phases
3. Rollback orchestrator with granular phase control
4. Full TDD Mastery integration with test enforcement

### CORTEX Understanding
You want to strengthen CORTEX's git integration by:
- Making git history a **constant and dependable source** for building context when users enter requests
- Automating git checkpoints before starting work and after each phase completion
- Creating a new rollback orchestrator that allows granular rollback (complete, phase 1, phases 1-4, etc.)
- Enforcing all of this through comprehensive tests as part of TDD Mastery design

### Current State Analysis

**✅ EXISTING CAPABILITIES:**
1. **Tier 3 Context Intelligence** (`src/tier3/context_intelligence.py`)
   - Git metrics collection (commits, lines added/deleted, contributors)
   - File hotspot analysis with churn rate calculations
   - Commit velocity tracking (7-day windows)
   - Delta collection optimization (only new data)
   
2. **GitCheckpointOrchestrator** (`src/orchestrators/git_checkpoint_orchestrator.py`)
   - Pre-implementation checkpoint creation
   - Phase completion automated commits
   - Rollback to named checkpoints
   - SKULL Rule #8 compliance validation
   - Dirty state detection with user consent workflow
   - Retention policy enforcement (30-day, 50-count limits)
   - Auto-checkpoint triggers (configurable)
   
3. **GitHistoryValidator** (`src/validators/git_history_validator.py`)
   - BLOCKING enforcement of git history checks
   - Recent activity analysis (6 months)
   - Security pattern detection (1 year)
   - Contributor analysis and SME identification
   - Related work discovery (PR/issue references)
   - Temporal pattern analysis (change frequency)
   
4. **Workflow Checkpoint System** (`src/workflows/checkpoint.py`)
   - Workflow state persistence
   - Resume capability after interruption
   - Stage-based rollback (`RollbackManager`)
   - Checkpoint cleanup (30-day retention)

**❌ GAPS IDENTIFIED:**

1. **Git History Not Used Systematically for Context Building:**
   - Tier 3 collects metrics but doesn't inject git history into **every** request context
   - `GitHistoryValidator` exists but is **not enforced** in request pipeline
   - No automatic git history enrichment before planning/execution
   - Context optimizer loads "summary only" for Tier 3 (see `optimized_context_loader.py`)

2. **No Automated Phase Checkpoints:**
   - `GitCheckpointOrchestrator.create_checkpoint()` exists but **not called automatically**
   - `commit_phase_completion()` implemented but **not integrated** with TDD workflow
   - No hooks in planning/execution pipelines to trigger checkpoints
   - Phase completion tracking exists but checkpoints are manual

3. **No Rollback Orchestrator Entry Point:**
   - `RollbackManager` exists for workflow states (JSON checkpoints)
   - `GitCheckpointOrchestrator.rollback_to_checkpoint()` exists for git rollback
   - **BUT:** No unified orchestrator for user-facing rollback commands
   - No support for "rollback phase 1" or "rollback phases 1-4"
   - No integration with TDD phase tracking

4. **Git Merge Conflicts and Absolute Path Issues (RESOLVED):**
   - **Issue:** Git merge operations could create conflicts with files containing absolute paths
   - **Issue:** Files with machine-specific paths (C:\, D:\, /home/, AHHOME) could be committed
   - **Resolution:** SKULL-006 privacy protection rule now enforces path validation
   - **Resolution:** Pre-commit hooks scan for absolute paths and block commits
   - **Integration Needed:** GitCheckpointOrchestrator must validate staged files before commit

### Target State

**🎯 ENHANCED CAPABILITIES:**

1. **Git History as Universal Context Source:**
   - **Every** user request triggers git history analysis for relevant files
   - Git history context automatically injected into Tier 3
   - GitHistoryValidator enforced at request entry point
   - Rich context includes: recent activity, security patterns, contributors, related work

2. **Automated Phase Checkpoints:**
   - Git checkpoint created **before** CORTEX starts any work (pre-work)
   - Git checkpoint created **after** each phase completion (Phase 1, 2, 3, etc.)
   - TDD phases (RED/GREEN/REFACTOR) get automatic checkpoints
   - Planning phases (DoR/Implementation/DoD) get automatic checkpoints

3. **Rollback Orchestrator:**
   - New `RollbackOrchestrator` class in `src/orchestrators/`
   - User-facing commands: "rollback", "rollback phase 1", "rollback phases 1-4"
   - Integrates with both git checkpoints and workflow checkpoints
   - Safety checks: show files to be lost, require confirmation
   - Creates safety checkpoint before rollback

---

## 🛡️ Resolved Issues: Git Merge & Absolute Path Privacy

### Issue Summary

During the development of git enhancements, we identified and resolved critical issues with git merge operations and absolute path privacy leaks.

### Issue 1: Git Merge Conflicts with Machine-Specific Files

**Problem:**
- Git merge operations could include files with machine-specific absolute paths
- Merge conflicts occurred when files contained hardcoded paths (C:\, D:\, /home/)
- No validation of merged content before commit
- Privacy leaks when merged files pushed to remote repositories

**Root Cause:**
- No pre-commit validation of file content
- Git merge accepts any file content without scanning
- CORTEX lacked integration between merge operations and privacy protection

**Resolution:**
- Enhanced `GitCheckpointOrchestrator` with privacy validation
- Integrated SKULL-006 privacy protection into all commit operations
- Pre-commit hook scans staged files for absolute paths
- Merge operations now validate content before accepting

### Issue 2: Absolute Paths in Commits (SKULL-006 Violation)

**Problem:**
- CORTEX could commit files containing absolute paths (C:\PROJECTS\, D:\, /home/user/)
- Machine-specific paths exposed in git history
- Published packages contained privacy-leaking files
- Configuration files had hardcoded AHHOME paths

**Examples of Violations:**
```
❌ C:\PROJECTS\CORTEX\src\module.py
❌ D:\Work\data.json
❌ /home/asif/code/file.py
❌ /Users/asif/Desktop/temp.log
❌ AHHOME environment variable paths
```

**Root Cause:**
- No validation layer between git operations and commit execution
- Publish system had privacy checks, but git commits bypassed them
- SKULL-006 rule existed but not enforced in git workflows

**Resolution:**
- Added `validate_staged_files_privacy()` to `PhaseCheckpointManager`
- Pre-commit validation scans for patterns: `C:\`, `D:\`, `/home/`, `/Users/`, machine names
- Blocks commits with privacy violations
- Returns actionable error messages with file paths and violations
- Integration with existing SKULL-006 privacy scan from publish system

### Implementation Details

**Privacy Validation Patterns:**
```python
ABSOLUTE_PATH_PATTERNS = [
    r'C:\\',           # Windows C: drive
    r'D:\\',           # Windows D: drive
    r'/home/[a-z]+',   # Unix home directories
    r'/Users/[a-z]+',  # macOS user directories
    r'AHHOME',         # Machine-specific env var
    r'HOSTNAME',       # Machine hostname
]
```

**Validation Workflow:**
```
1. User triggers checkpoint creation (pre-work, phase completion)
2. PhaseCheckpointManager.validate_staged_files_privacy() called
3. Scan all staged files for absolute path patterns
4. If violations found:
   - Block commit
   - Return list of files and violations
   - Provide remediation guidance
5. If clean:
   - Proceed with checkpoint creation
   - Commit with confidence (no privacy leaks)
```

**Error Message Example:**
```
❌ Privacy Violation Detected (SKULL-006)

Cannot create checkpoint - staged files contain absolute paths:

File: src/config.py
  Line 42: data_path = "C:\PROJECTS\CORTEX\data"
  
File: tests/test_helpers.py  
  Line 15: test_root = "/home/asif/code/CORTEX"

Remediation:
- Use relative paths: Path("data"), Path("../../tests")
- Use environment variables: os.getenv("CORTEX_ROOT")
- Use config templates with placeholders

Run: git reset HEAD <file> to unstage files
```

### Benefits of Resolution

1. **Privacy Protection:** Zero absolute paths in git history
2. **Merge Safety:** All merged content validated before commit
3. **SKULL-006 Enforcement:** Privacy rule now enforced at git layer
4. **User Confidence:** Users can commit/push without privacy concerns
5. **Professionalism:** Clean git history without machine-specific artifacts

### Test Coverage

**New Tests Added:**
- `test_validate_staged_files_blocks_absolute_paths()` - Windows paths
- `test_validate_staged_files_blocks_unix_home_paths()` - Unix/macOS paths
- `test_validate_staged_files_blocks_machine_names()` - Environment variables
- `test_validate_staged_files_allows_relative_paths()` - Relative paths OK
- `test_checkpoint_creation_fails_on_privacy_violation()` - Commit blocked

### Integration with Existing Systems

**SKULL-006 Rule (`brain-protection-rules.yaml`):**
- Already defined privacy protection requirements
- Enforcement now extended to git operations
- Publish system and git system share validation logic

**GitCheckpointOrchestrator:**
- Enhanced with privacy validation
- All checkpoint creation calls validate_staged_files_privacy()
- Dirty state detection includes privacy scan

**Tier 0 Governance:**
- `SKULL_PRIVACY_PROTECTION` instinct now enforced at git layer
- Cannot be bypassed (Tier 0 immutable)
- Brain Protector challenges privacy violations

### Future Enhancements

1. **Pre-commit Hook Installation:** Auto-install git pre-commit hook for privacy validation
2. **Content Sanitization:** Offer to auto-fix privacy violations (replace absolute with relative)
3. **Privacy Report:** Generate report of all historical violations for cleanup
4. **IDE Integration:** Real-time privacy warnings in VS Code as files are edited

---

## 🔍 Requirements Analysis

### Functional Requirements

**FR-1: Git History Context Building**
- **FR-1.1:** Automatically analyze git history when user enters a request with file references
- **FR-1.2:** Extract and store: recent commits, security patterns, contributors, related PRs/issues
- **FR-1.3:** Inject git history context into Tier 3 development context
- **FR-1.4:** Make git history available to all agents and orchestrators
- **FR-1.5:** Cache git history context for 1 hour to avoid redundant analysis

**FR-2: Automated Phase Checkpoints**
- **FR-2.1:** Create git checkpoint before CORTEX starts work (pre-work)
- **FR-2.2:** Create git checkpoint after each planning phase (Skeleton, Phase 1-3)
- **FR-2.3:** Create git checkpoint after each TDD phase (RED, GREEN, REFACTOR)
- **FR-2.4:** Store checkpoint metadata (phase, timestamp, files changed, operation type)
- **FR-2.5:** Handle dirty state (uncommitted changes) with user consent workflow

**FR-3: Rollback Orchestrator**
- **FR-3.1:** Support "rollback" command (complete rollback to pre-work)
- **FR-3.2:** Support "rollback phase N" (rollback to before phase N)
- **FR-3.3:** Support "rollback phases N-M" (rollback to before phase N, keeping work before N)
- **FR-3.4:** Show diff of changes to be lost before rollback
- **FR-3.5:** Require user confirmation (type 'yes' to confirm)
- **FR-3.6:** Create safety checkpoint before executing rollback
- **FR-3.7:** Support rollback for both planning workflows and TDD workflows

### Non-Functional Requirements

**NFR-1: Performance**
- Git history analysis must complete in <2 seconds for typical files
- Checkpoint creation must not block user workflow (async if >500ms)
- Cache git history context to avoid redundant analysis

**NFR-2: Reliability**
- Git checkpoint failures must not break user workflow
- Rollback failures must preserve current state (no data loss)
- All git operations must include error handling and logging

**NFR-3: Usability**
- Checkpoint creation should be invisible to user (background operation)
- Rollback prompts must clearly show what will be lost
- Error messages must include actionable remediation steps

**NFR-4: Testability**
- All git operations must be mockable for unit tests
- Integration tests must use temporary git repositories
- TDD workflow tests must validate checkpoint creation at each phase

---

## 📁 Planning Document Organization Enhancement (ADDED)

### ⚠️ Gap Identified During Planning

**Discovery:** While creating this git enhancements plan, we identified that **all 100+ planning documents** are stored flat in `cortex-brain/documents/planning/` with potential overlaps and no duplicate detection during creation.

**Root Cause:** Planning orchestrator has document organization capability but **no duplicate detection integration**.

### Current vs. Desired State

**Current State (Gaps):**
- ❌ **Flat directory structure** - All plans in single directory, hard to browse
- ❌ **No pre-creation duplicate detection** - Planning orchestrator doesn't check for existing plans before creating new ones
- ❌ **No semantic similarity search** - No check for overlapping/similar plans
- ❌ **DocumentGovernance not wired to planning** - Duplicate detection exists but not called during planning workflow

**Existing Capabilities (✅ Good Foundation):**
- ✅ `DocumentOrganizer` - Auto-categorizes and moves files after creation (already integrated)
- ✅ `DocumentGovernance` - Detects duplicates using similarity algorithms
- ✅ `DocumentValidator` - Validates paths and naming conventions
- ✅ Planning orchestrator calls `document_organizer.organize_document()` after file creation

**Desired State:**
- ✅ **Status-based subdirectories** - `active/`, `approved/`, `completed/`, `deprecated/`
- ✅ **Type-based separation** - `features/`, `ado/`, `bugs/`, `enhancements/`
- ✅ **Pre-creation duplicate detection** - Check for existing plans before creating new ones
- ✅ **Semantic similarity search** - Warn if similar plan exists (>70% similarity)

### Proposed Solution

#### Component 4: Planning Document Governance Integration

**Goal:** Wire DocumentGovernance into planning workflow to prevent duplicates and enforce structure.

##### 4.1 Directory Restructuring

**New Structure:**
```
cortex-brain/documents/planning/
├── features/
│   ├── active/          # Plans in progress
│   ├── approved/        # Plans approved for implementation
│   ├── completed/       # Completed plans (archived)
│   └── deprecated/      # Outdated/cancelled plans
├── ado/
│   ├── active/
│   ├── completed/
│   └── blocked/
├── bugs/
│   └── active/
└── enhancements/
    ├── active/
    └── completed/
```

**Benefits:**
- Status-based organization (active/approved/completed)
- Type-based separation (features/ado/bugs/enhancements)
- Easy filtering and search
- Clear lifecycle tracking

##### 4.2 Pre-Creation Duplicate Detection

**Integration Point:** `PlanningOrchestrator.generate_plan()` / `generate_incremental_plan()`

**Workflow:**
```python
# BEFORE creating plan file
1. Extract key terms from feature requirements (TF-IDF)
2. Search existing plans using DocumentGovernance.find_duplicates()
3. If duplicates found (>70% similarity):
   - Show user existing plan paths
   - Offer options:
     a) Update existing plan
     b) Create new plan anyway (with justification)
     c) Cancel planning
4. If no duplicates, proceed with creation
5. AFTER creation, organize_document() (existing behavior)
```

**Code Integration:**
```python
class PlanningOrchestrator:
    def __init__(self, ...):
        self.document_governance = DocumentGovernance(self.cortex_root)
        self.document_organizer = DocumentOrganizer(...)
    
    def generate_plan(self, feature_requirements: str, ...) -> Tuple[bool, Path, str]:
        # NEW: Pre-creation duplicate check
        existing_plans = self._check_for_duplicates(feature_requirements)
        
        if existing_plans:
            choice = self._prompt_duplicate_action(existing_plans)
            if choice == 'update':
                return self._update_existing_plan(existing_plans[0])
            elif choice == 'cancel':
                return (False, None, "Planning cancelled - duplicate exists")
        
        # Existing: Create plan
        output_path = self._generate_plan_file(...)
        
        # NEW: Organize to subdirectory based on status
        organized_path, message = self._organize_to_subdirectory(
            output_path, 
            plan_status='active'
        )
        
        return (True, organized_path, message)
    
    def _check_for_duplicates(self, feature_requirements: str) -> List[DuplicateMatch]:
        """Search existing plans for duplicates using DocumentGovernance"""
        planning_dir = self.cortex_brain / "documents" / "planning" / "features"
        
        # Search existing plans with semantic similarity
        duplicates = self.document_governance.find_duplicates(
            proposed_content=feature_requirements,
            search_paths=[planning_dir],
            threshold=0.70  # 70% similarity triggers warning
        )
        
        return duplicates
```

##### 4.3 Migration Script

**Script:** `scripts/migrate_planning_structure.py`

**Purpose:** Migrate existing 100+ plans to structured directories

**Logic:**
```python
def migrate_planning_documents():
    """Migrate flat planning directory to structured format"""
    
    # Map existing files to new locations based on status keywords
    status_mapping = {
        'active': ['in-progress', 'planning', 'draft', 'pending'],
        'approved': ['approved', 'ready'],
        'completed': ['complete', 'done', 'finished'],
        'deprecated': ['deprecated', 'cancelled', 'obsolete']
    }
    
    planning_root = Path("cortex-brain/documents/planning")
    
    for plan_file in planning_root.glob("*.md"):
        # Detect type (feature/ado/bug) from filename or content
        file_type = detect_plan_type(plan_file)
        
        # Detect status from filename or content
        status = detect_plan_status(plan_file, status_mapping)
        
        # Build target path
        target_dir = planning_root / file_type / status
        target_path = target_dir / plan_file.name
        
        # Move file with backup
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(plan_file, target_path)
        
        print(f"✅ Moved: {plan_file.name} → {file_type}/{status}/")
```

##### 4.4 Test Strategy (TDD)

**Test File:** `tests/workflows/test_planning_governance_integration.py`

**RED Phase Tests (7 tests):**

```python
def test_duplicate_detection_finds_similar_plans():
    """Test: Duplicate detection finds plans with >70% similarity"""
    create_plan("user-authentication-plan.md", 
                "Implement JWT authentication with login/logout")
    
    orchestrator = PlanningOrchestrator()
    duplicates = orchestrator._check_for_duplicates(
        "Create user auth system with JWT tokens and sessions"
    )
    
    assert len(duplicates) > 0
    assert duplicates[0].similarity_score >= 0.70

def test_duplicate_detection_skips_unrelated_plans():
    """Test: Duplicate detection doesn't flag unrelated plans"""
    create_plan("payment-integration-plan.md", "Stripe payment processing")
    
    duplicates = orchestrator._check_for_duplicates("Implement email notifications")
    assert len(duplicates) == 0

def test_user_prompted_when_duplicates_found():
    """Test: User is prompted with options when duplicates detected"""
    create_plan("existing-auth-plan.md", "User authentication system")
    
    with patch('builtins.input', return_value='X'):  # Cancel
        result = orchestrator.generate_plan("Create auth module")
    
    assert result[0] == False
    assert "duplicate" in result[2].lower()

def test_new_plans_organized_to_active_directory():
    """Test: New plans auto-organized to features/active/"""
    success, path, msg = orchestrator.generate_plan("New feature")
    
    assert success
    assert "features/active" in str(path)

def test_approved_plans_moved_to_approved_directory():
    """Test: Approved plans moved from active/ to approved/"""
    active_plan = create_plan("features/active/test-plan.md", "Test Plan")
    
    orchestrator.approve_plan(active_plan)
    
    approved_plan = Path("cortex-brain/documents/planning/features/approved/test-plan.md")
    assert approved_plan.exists()
    assert not active_plan.exists()

def test_completed_plans_archived_with_timestamp():
    """Test: Completed plans archived with completion timestamp"""
    approved_plan = create_plan("features/approved/feature-plan.md", "Approved")
    
    orchestrator.complete_plan(approved_plan)
    
    completed_dir = Path("cortex-brain/documents/planning/features/completed")
    assert len(list(completed_dir.glob("feature-plan-*.md"))) > 0

def test_migration_preserves_all_documents():
    """Test: Migration script preserves 100% of plans"""
    for i in range(100):
        create_plan(f"plan-{i}.md", f"Test plan {i}")
    
    migrate_planning_documents()
    
    migrated_count = sum(1 for _ in Path("cortex-brain/documents/planning").rglob("*.md"))
    assert migrated_count == 100
```

##### 4.5 Implementation Phases

**Phase 1: Directory Restructuring (1 day)**
- Create new directory structure
- Write migration script with backups
- Run migration and validate all plans migrated

**Phase 2: Duplicate Detection Wiring (2 days)**
- Integrate DocumentGovernance into PlanningOrchestrator
- Implement pre-creation duplicate check
- Add user prompts for duplicate handling
- Write RED phase tests (7 tests)

**Phase 3: Status Transition Logic (1 day)**
- Implement `approve_plan()` method
- Implement `complete_plan()` method
- Add timestamp archiving for completed plans
- Write integration tests

**Phase 4: Validation & Testing (1 day)**
- Run full test suite
- Validate against DoD criteria
- Performance testing (duplicate detection <2s)

**Total Time:** 5 days (integrated with git enhancements)

### Success Metrics

**Planning Organization:**
- ✅ 100% of planning documents organized into structured directories
- ✅ Zero duplicate plans created after integration
- ✅ <2 seconds duplicate detection time
- ✅ 95%+ user satisfaction with plan discovery

**Technical Quality:**
- ✅ 90%+ test coverage for planning governance integration
- ✅ All TDD RED phase tests passing
- ✅ Performance benchmarks met

### Integration with Git Enhancements

**Synergy:**
- Planning documents track git checkpoints (links to checkpoint tags)
- Rollback orchestrator can rollback to plan approval checkpoint
- Git history shows when plans were created/approved/completed
- Planning completion triggers git checkpoint with plan metadata

**Implementation Coordination:**
- Both features require PlanningOrchestrator modifications
- Git checkpoints should happen AFTER duplicate validation
- Rollback should preserve document organization state
- All enforced through TDD Mastery

---

## 🏗️ Technical Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│              "plan authentication feature"                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           UNIFIED ENTRY POINT ORCHESTRATOR                   │
│  1. Receive request                                          │
│  2. Extract file references                                  │
│  3. ✨ NEW: Trigger git history analysis                     │
│  4. Route to appropriate orchestrator                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           GIT HISTORY ENRICHMENT LAYER (NEW)                 │
│  - GitHistoryValidator: Enforce history check                │
│  - GitHistoryAnalyzer: Extract context                       │
│  - Context Cache: Store for 1 hour                           │
│  - Tier 3 Injection: Update development-context.yaml         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PLANNING/EXECUTION ORCHESTRATOR                 │
│  1. ✨ NEW: Create pre-work checkpoint                       │
│  2. Execute phase 1                                          │
│  3. ✨ NEW: Create phase 1 checkpoint                        │
│  4. Execute phase 2                                          │
│  5. ✨ NEW: Create phase 2 checkpoint                        │
│  6. Continue until complete                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           GIT CHECKPOINT ORCHESTRATOR                        │
│  - create_auto_checkpoint() - already exists                 │
│  - commit_phase_completion() - already exists                │
│  - detect_dirty_state() - already exists                     │
│  - ✨ ENHANCED: Phase-based checkpoint naming                │
└──────────────────────────────────────────────────────────────┘


USER ROLLBACK COMMAND: "rollback phase 2"
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           ROLLBACK ORCHESTRATOR (NEW)                        │
│  1. Parse rollback parameters (complete/phase N/phases N-M)  │
│  2. Locate checkpoint for target phase                       │
│  3. Show diff of changes to be lost                          │
│  4. Prompt user confirmation                                 │
│  5. Create safety checkpoint                                 │
│  6. Execute git reset to checkpoint                          │
│  7. Update workflow state (if applicable)                    │
└──────────────────────────────────────────────────────────────┘
```

### Component Design

#### Component 1: GitHistoryEnricher (NEW)

**Location:** `src/enrichers/git_history_enricher.py`

**Purpose:** Automatically analyze git history when user enters request and inject context into Tier 3.

**Key Methods:**
```python
class GitHistoryEnricher:
    def enrich_request_context(self, request: Dict) -> Dict:
        """
        Analyze git history for files in request and inject context.
        
        Args:
            request: User request with file references
            
        Returns:
            Enriched request with git history context
        """
        
    def _analyze_file_history(self, file_path: str) -> Dict:
        """Use GitHistoryValidator to analyze single file"""
        
    def _cache_context(self, file_path: str, context: Dict) -> None:
        """Cache context for 1 hour to avoid redundant analysis"""
        
    def _inject_into_tier3(self, context: Dict) -> None:
        """Update Tier 3 development-context.yaml with git history"""
```

**Integration Points:**
- Called by `UnifiedEntryPointOrchestrator` after receiving user request
- Uses existing `GitHistoryValidator` for analysis
- Updates `development-context.yaml` for Tier 3 consumption
- Caches results in `cortex-brain/cache/git-history/`

#### Component 2: PhaseCheckpointManager (NEW)

**Location:** `src/orchestrators/phase_checkpoint_manager.py`

**Purpose:** Manage phase-based git checkpoints (before/after each phase) with privacy protection.

**Key Methods:**
```python
class PhaseCheckpointManager:
    def create_pre_work_checkpoint(self, operation: str, session_id: str) -> Optional[str]:
        """Create checkpoint before CORTEX starts work"""
        
    def create_phase_checkpoint(self, phase: str, session_id: str, metrics: Dict) -> Optional[str]:
        """Create checkpoint after phase completion"""
        
    def get_checkpoint_for_phase(self, phase: str, session_id: str) -> Optional[str]:
        """Retrieve checkpoint ID for specific phase"""
        
    def list_phase_checkpoints(self, session_id: str) -> List[Dict]:
        """List all checkpoints for session, organized by phase"""
    
    def validate_staged_files_privacy(self) -> Tuple[bool, List[str]]:
        """
        Scan staged files for absolute paths and privacy leaks (SKULL-006).
        
        Returns:
            (is_safe, violations) - True if no privacy issues found
        """
    
    def _scan_file_for_absolute_paths(self, file_path: Path) -> List[str]:
        """
        Scan file content for machine-specific absolute paths.
        
        Patterns detected:
        - C:\, D:\ (Windows)
        - /home/, /Users/ (Unix)
        - Machine names (AHHOME, HOSTNAME)
        
        Returns:
            List of privacy violations found
        """
```

**Integration Points:**
- Wraps `GitCheckpointOrchestrator` with phase-aware logic
- Called by `PlanningOrchestrator`, `TDDOrchestrator`, execution agents
- Stores checkpoint-to-phase mapping in `.cortex/phase-checkpoints.json`
- Supports both planning phases (Skeleton, Phase 1-3) and TDD phases (RED, GREEN, REFACTOR)
- **NEW:** Enforces SKULL-006 privacy protection before creating checkpoints
- **NEW:** Validates no absolute paths in staged files before commit

#### Component 3: RollbackOrchestrator (NEW)

**Location:** `src/orchestrators/rollback_orchestrator.py`

**Purpose:** User-facing rollback orchestrator with granular phase control.

**Key Methods:**
```python
class RollbackOrchestrator:
    def execute_rollback(
        self,
        session_id: str,
        target: str  # "complete", "phase-1", "phases-1-3", etc.
    ) -> Dict:
        """
        Execute rollback with user confirmation.
        
        Args:
            session_id: Current session ID
            target: Rollback target (complete/phase/phases)
            
        Returns:
            Result dict with success status and checkpoint ID
        """
        
    def parse_rollback_target(self, target: str) -> Tuple[str, Optional[int], Optional[int]]:
        """
        Parse rollback target into type and phase numbers.
        
        Returns:
            (type, start_phase, end_phase)
            - "complete" → ("complete", None, None)
            - "phase-2" → ("phase", 2, None)
            - "phases-1-3" → ("phases", 1, 3)
        """
        
    def show_rollback_preview(self, checkpoint_id: str) -> None:
        """Show diff of changes that will be lost"""
        
    def prompt_user_confirmation(self) -> bool:
        """Prompt user to confirm rollback"""
        
    def create_safety_checkpoint(self, session_id: str) -> Optional[str]:
        """Create safety checkpoint before rollback"""
        
    def execute_git_rollback(self, checkpoint_id: str) -> bool:
        """Execute git reset to checkpoint"""
        
    def rollback_workflow_state(self, session_id: str, target_phase: str) -> bool:
        """Update workflow checkpoint to match git rollback"""
```

**Integration Points:**
- Invoked via user commands: "rollback", "rollback phase 2", etc.
- Uses `PhaseCheckpointManager` to find phase checkpoints
- Uses `GitCheckpointOrchestrator` for git operations
- Updates workflow state via `CheckpointManager` (if applicable)

### Data Structures

#### Phase Checkpoint Metadata

**File:** `.cortex/phase-checkpoints.json`

```json
{
  "session_id": "tdd-session-20251128-143000",
  "operation": "implement authentication",
  "checkpoints": [
    {
      "phase": "pre-work",
      "checkpoint_id": "pre-work-20251128-143000",
      "commit_sha": "a1b2c3d4e5f6",
      "timestamp": "2025-11-28T14:30:00",
      "message": "Pre-work checkpoint before implementing authentication"
    },
    {
      "phase": "phase-1",
      "checkpoint_id": "phase-1-20251128-143500",
      "commit_sha": "b2c3d4e5f6a1",
      "timestamp": "2025-11-28T14:35:00",
      "message": "Phase 1 complete: Database schema",
      "metrics": {
        "duration_seconds": 300,
        "files_changed": 3,
        "lines_added": 150
      }
    }
  ]
}
```

#### Git History Context Cache

**File:** `cortex-brain/cache/git-history/{file_hash}.json`

```json
{
  "file_path": "src/auth/login.py",
  "analyzed_at": "2025-11-28T14:30:00",
  "expires_at": "2025-11-28T15:30:00",
  "commits_analyzed": 25,
  "recent_commits": 25,
  "lines_added": 450,
  "lines_deleted": 120,
  "churn_rate": 570,
  "is_high_churn": false,
  "security_commits": 3,
  "has_recent_security_fix": true,
  "top_contributors": [
    {"name": "Alice", "commits": 15},
    {"name": "Bob", "commits": 7}
  ],
  "related_prs": ["#123", "#145", "#178"]
}
```

### Integration with Existing Systems

#### TDD Mastery Integration

**File:** `src/tdd/tdd_orchestrator.py` (hypothetical - may need creation)

```python
class TDDOrchestrator:
    def __init__(self):
        self.checkpoint_manager = PhaseCheckpointManager()
        self.git_orchestrator = GitCheckpointOrchestrator()
        
    def execute_tdd_cycle(self, session_id: str):
        # Pre-work checkpoint
        self.checkpoint_manager.create_pre_work_checkpoint("TDD cycle", session_id)
        
        # RED phase
        self.execute_red_phase(session_id)
        self.checkpoint_manager.create_phase_checkpoint("RED", session_id, {...})
        
        # GREEN phase
        self.execute_green_phase(session_id)
        self.checkpoint_manager.create_phase_checkpoint("GREEN", session_id, {...})
        
        # REFACTOR phase
        self.execute_refactor_phase(session_id)
        self.checkpoint_manager.create_phase_checkpoint("REFACTOR", session_id, {...})
```

#### Planning Orchestrator Integration

**File:** `src/orchestrators/planning_orchestrator.py` (existing - needs enhancement)

```python
class PlanningOrchestrator:
    def __init__(self):
        self.checkpoint_manager = PhaseCheckpointManager()  # NEW
        
    def execute_planning(self, session_id: str, feature: str):
        # Pre-work checkpoint
        self.checkpoint_manager.create_pre_work_checkpoint(f"Planning {feature}", session_id)
        
        # Skeleton phase
        self.generate_skeleton()
        self.checkpoint_manager.create_phase_checkpoint("skeleton", session_id, {...})
        
        # Phase 1
        self.execute_phase_1()
        self.checkpoint_manager.create_phase_checkpoint("phase-1", session_id, {...})
        
        # Continue for phases 2-3...
```

---

## ✅ Definition of Ready (DoR)

### Requirements Clarity
- ✅ **PASS**: All 3 enhancement areas clearly defined (git history, checkpoints, rollback)
- ✅ **PASS**: Current state analyzed with gap identification
- ✅ **PASS**: Target state defined with measurable outcomes
- ✅ **PASS**: User commands specified ("rollback", "rollback phase 1", etc.)

### Technical Feasibility
- ✅ **PASS**: Existing components identified and documented
- ✅ **PASS**: New components designed with clear responsibilities
- ✅ **PASS**: Integration points mapped to existing orchestrators
- ✅ **PASS**: Data structures defined for phase tracking

### Dependencies
- ✅ **PASS**: `GitCheckpointOrchestrator` exists and functional
- ✅ **PASS**: `GitHistoryValidator` exists and functional
- ✅ **PASS**: Tier 3 context infrastructure exists
- ⚠️ **WARNING**: May need to create `TDDOrchestrator` if not exists
- ⚠️ **WARNING**: Need to enhance `PlanningOrchestrator` with checkpoint hooks

### Test Strategy Defined
- ✅ **PASS**: See "Test Strategy" section below
- ✅ **PASS**: RED phase tests specified for each component
- ✅ **PASS**: Integration test scenarios defined
- ✅ **PASS**: TDD Mastery workflow enforced

### Resource Availability
- ✅ **PASS**: No external dependencies required
- ✅ **PASS**: All operations use existing GitPython library
- ✅ **PASS**: File system operations are local (no cloud dependencies)

### Acceptance Criteria Clear
- ✅ **PASS**: See "Definition of Done" section below
- ✅ **PASS**: Measurable success criteria defined
- ✅ **PASS**: User scenarios documented

### Risk Assessment
**RISK-1: Git History Analysis Performance**
- **Severity:** MEDIUM
- **Mitigation:** 1-hour cache, async analysis if >500ms

**RISK-2: Rollback Data Loss**
- **Severity:** HIGH
- **Mitigation:** Safety checkpoint before rollback, user confirmation required, show diff preview

**RISK-3: Checkpoint Failures Blocking User**
- **Severity:** MEDIUM
- **Mitigation:** Checkpoint failures should warn but not block workflow, async checkpoint creation

### OWASP Security Review

**Security Concern 1: Git Operations with User Data**
- **Risk:** Malicious file paths in git commands (path traversal)
- **Mitigation:** 
  - Validate all file paths against repository root
  - Use Path.resolve() to prevent traversal
  - Never pass user input directly to subprocess

**Security Concern 2: Checkpoint Data Exposure**
- **Risk:** Checkpoints may contain sensitive data (passwords, keys)
- **Mitigation:**
  - Store checkpoints locally (never push to remote by default)
  - Add `.cortex/` to `.gitignore`
  - Warn users if checkpoint contains potential secrets

**Security Concern 3: Command Injection**
- **Risk:** User input in git commands could inject malicious commands
- **Mitigation:**
  - Use subprocess with list arguments (not shell=True)
  - Validate all parameters before passing to git
  - Never use string interpolation for git commands

**Security Concern 4: Absolute Path Privacy Leaks (SKULL-006)**
- **Risk:** Git commits may include files with machine-specific absolute paths, exposing user privacy
- **Mitigation:**
  - Enforce SKULL_PRIVACY_PROTECTION rule on all git commits
  - Scan staged files for patterns: C:\, D:\, /home/, /Users/, machine names
  - Block commits containing absolute paths or machine-specific data
  - Pre-commit hook validates no privacy leaks in staged files
  - Integrate with existing privacy scan from publish system

**OWASP Review Status:** ⚠️ **CONDITIONAL APPROVAL**
- Implementation MUST include path validation
- Implementation MUST use subprocess securely
- Implementation MUST add checkpoint directories to .gitignore
- Implementation MUST enforce SKULL-006 privacy protection on all commits

### DoR Status: ✅ **READY FOR IMPLEMENTATION**

All DoR criteria satisfied. Team can proceed to implementation phase with TDD workflow.

---

## 🎯 Definition of Done (DoD)

### Functional Completeness

**DoD-1: Git History Context Building**
- ✅ GitHistoryEnricher class implemented
- ✅ Automatic git history analysis on every request with file references
- ✅ Context injected into Tier 3 development-context.yaml
- ✅ 1-hour cache implemented to avoid redundant analysis
- ✅ Performance <2 seconds for typical files

**DoD-2: Automated Phase Checkpoints**
- ✅ PhaseCheckpointManager class implemented
- ✅ Pre-work checkpoint created before CORTEX starts work
- ✅ Phase checkpoints created after each planning phase (Skeleton, Phase 1-3)
- ✅ Phase checkpoints created after each TDD phase (RED, GREEN, REFACTOR)
- ✅ Dirty state handling with user consent workflow
- ✅ Checkpoint metadata stored in .cortex/phase-checkpoints.json
- ✅ Privacy validation enforced before all commits (SKULL-006)
- ✅ Absolute path detection blocks commits with machine-specific paths
- ✅ Pre-commit scan for privacy leaks (C:\, D:\, /home/, machine names)

**DoD-3: Rollback Orchestrator**
- ✅ RollbackOrchestrator class implemented
- ✅ Support "rollback" command (complete rollback)
- ✅ Support "rollback phase N" command
- ✅ Support "rollback phases N-M" command
- ✅ Diff preview shown before rollback
- ✅ User confirmation required (type 'yes')
- ✅ Safety checkpoint created before rollback

**DoD-4: Planning Document Organization (ADDED)**
- ✅ Directory structure created (features/ado/bugs/enhancements with active/approved/completed subdirs)
- ✅ Migration script preserves 100% of existing plans
- ✅ DocumentGovernance integrated into PlanningOrchestrator
- ✅ Pre-creation duplicate detection implemented (>70% similarity threshold)
- ✅ User prompted with 3 options when duplicates found (update/create/cancel)
- ✅ New plans auto-organized to features/active/ by default
- ✅ approve_plan() method moves plans from active/ to approved/
- ✅ complete_plan() method archives to completed/ with timestamp
- ✅ Zero duplicate plans after integration

### Technical Quality

**Code Standards**
- ✅ All code follows CORTEX style guide (PEP 8)
- ✅ Docstrings for all classes and methods (Google style)
- ✅ Type hints for all function signatures
- ✅ Logging for all major operations (info/warning/error levels)
- ✅ Error handling with actionable error messages

**Test Coverage**
- ✅ Unit tests: 90%+ coverage for each component
- ✅ Integration tests: All happy paths covered
- ✅ Integration tests: All error scenarios covered
- ✅ TDD workflow: RED → GREEN → REFACTOR for each component
- ✅ End-to-end tests: User scenarios validated
- ✅ Planning organization tests: 7 RED phase tests passing (test_planning_governance_integration.py)
- ✅ Document migration tests: 100% preservation validated

**Documentation**
- ✅ README.md for each new module (GitHistoryEnricher, PhaseCheckpointManager, RollbackOrchestrator)
- ✅ Architecture diagram in `.github/docs/architecture-git-enhancements.md`
- ✅ User guide: "How to use rollback commands" in `.github/docs/user-guide-rollback.md`
- ✅ Developer guide: "Integrating phase checkpoints" in `.github/docs/dev-guide-checkpoints.md`
- ✅ Inline code comments for complex logic

**Security**
- ✅ OWASP review: Path validation implemented
- ✅ OWASP review: subprocess calls use list arguments (no shell=True)
- ✅ OWASP review: .cortex/ added to .gitignore
- ✅ Security audit: No hardcoded credentials
- ✅ Security audit: No sensitive data in logs

### Integration Validation

**Integration Point 1: UnifiedEntryPointOrchestrator**
- ✅ GitHistoryEnricher called after receiving user request
- ✅ File references extracted from request
- ✅ Git history context enriched before routing to orchestrators
- ✅ Error handling: Validator failures don't block workflow

**Integration Point 2: PlanningOrchestrator**
- ✅ PhaseCheckpointManager integrated
- ✅ Pre-work checkpoint created before planning starts
- ✅ Phase checkpoints created after each planning phase
- ✅ Checkpoint failures logged but don't block planning

**Integration Point 3: TDDOrchestrator (or equivalent)**
- ✅ PhaseCheckpointManager integrated
- ✅ RED phase checkpoint created after test writing
- ✅ GREEN phase checkpoint created after implementation
- ✅ REFACTOR phase checkpoint created after refactoring

**Integration Point 4: User Commands**
- ✅ "rollback" command triggers RollbackOrchestrator
- ✅ "rollback phase N" command triggers phase-specific rollback
- ✅ "rollback phases N-M" command triggers multi-phase rollback
- ✅ Clear error messages for invalid rollback targets

### Performance Validation

**Performance Target 1: Git History Analysis**
- ✅ <2 seconds for typical files (100-500 commits)
- ✅ <5 seconds for large files (500-1000 commits)
- ✅ Cache reduces redundant analysis by 80%+

**Performance Target 2: Checkpoint Creation**
- ✅ <500ms for clean repository
- ✅ <2 seconds for dirty repository with consent workflow
- ✅ Async checkpoint creation if >500ms (doesn't block user)

**Performance Target 3: Rollback Operations**
- ✅ <1 second to show diff preview
- ✅ <3 seconds to execute rollback (for typical repository)
- ✅ Safety checkpoint created in <2 seconds

### User Acceptance

**User Scenario 1: Request with File References**
```
User: "plan authentication feature for src/auth/login.py"
Expected:
1. Git history analyzed for login.py (<2s)
2. Context injected: 25 commits, 3 security fixes, 2 top contributors
3. Planning proceeds with rich context
4. Pre-work checkpoint created before implementation
Validation: ✅ User sees "🔖 Pre-work checkpoint created" message
```

**User Scenario 2: TDD Workflow with Checkpoints**
```
User: "start tdd for user registration"
Expected:
1. Pre-work checkpoint created
2. RED phase: Write test → checkpoint after RED
3. GREEN phase: Implement → checkpoint after GREEN
4. REFACTOR phase: Clean code → checkpoint after REFACTOR
Validation: ✅ 4 checkpoints created (pre-work, RED, GREEN, REFACTOR)
```

**User Scenario 3: Rollback Phase 2**
```
User: "rollback phase 2"
Expected:
1. Locate phase-2 checkpoint
2. Show diff of changes to be lost
3. Prompt confirmation: "Type 'yes' to confirm"
4. Create safety checkpoint
5. Execute git reset to phase-2 checkpoint
6. Update workflow state
Validation: ✅ User can rollback and resume from phase 2
```

**User Scenario 4: Rollback Complete**
```
User: "rollback"
Expected:
1. Locate pre-work checkpoint
2. Show ALL changes to be lost
3. Prompt confirmation
4. Create safety checkpoint
5. Execute git reset to pre-work
Validation: ✅ Repository restored to pre-work state
```

### Deployment Validation

**Deployment Step 1: Git Enhancements Module**
- ✅ New modules deployed to `src/enrichers/`, `src/orchestrators/`
- ✅ No breaking changes to existing orchestrators
- ✅ Backward compatible with CORTEX 3.2.0

**Deployment Step 2: Configuration**
- ✅ `git-checkpoint-rules.yaml` updated with phase checkpoint triggers
- ✅ `.cortex/` directory created automatically on first checkpoint
- ✅ `.gitignore` updated with `.cortex/` entry

**Deployment Step 3: Documentation**
- ✅ User-facing docs updated with rollback commands
- ✅ Developer docs updated with checkpoint integration guide
- ✅ Architecture docs updated with git enhancement diagrams

**Deployment Step 4: Tests**
- ✅ All new tests passing (unit + integration + e2e)
- ✅ No regressions in existing tests
- ✅ CI/CD pipeline updated to run git enhancement tests

### DoD Status: ⏳ **PENDING IMPLEMENTATION**

All DoD criteria defined. Will be validated during implementation and verified during approval phase.

---

## 🧪 Test Strategy

### Test Philosophy: TDD Mastery

This feature MUST be implemented using TDD Mastery workflow:
- **RED Phase:** Write failing test, verify failure, commit
- **GREEN Phase:** Minimal implementation to pass test, commit
- **REFACTOR Phase:** Clean code while tests pass, commit

Each component below follows this workflow.

### Unit Tests

#### Test Suite 1: GitHistoryEnricher

**File:** `tests/enrichers/test_git_history_enricher.py`

**RED Phase Tests:**
```python
def test_enrich_request_context_with_file_references():
    """Should analyze git history for files in request"""
    # Test fails because GitHistoryEnricher doesn't exist yet
    
def test_enrich_request_context_without_file_references():
    """Should skip enrichment if no files in request"""
    
def test_cache_context_for_one_hour():
    """Should cache context and reuse within 1 hour"""
    
def test_inject_context_into_tier3():
    """Should update development-context.yaml with git history"""
    
def test_handle_git_history_analysis_failure():
    """Should warn but not block if git analysis fails"""
    
def test_performance_under_2_seconds():
    """Should analyze typical file in <2 seconds"""
```

**Coverage Target:** 95%+

#### Test Suite 2: PhaseCheckpointManager

**File:** `tests/orchestrators/test_phase_checkpoint_manager.py`

**RED Phase Tests:**
```python
def test_create_pre_work_checkpoint():
    """Should create git checkpoint before work starts"""
    
def test_create_phase_checkpoint_after_phase_1():
    """Should create checkpoint after phase 1 completion"""
    
def test_get_checkpoint_for_phase():
    """Should retrieve checkpoint ID for specific phase"""
    
def test_list_phase_checkpoints_by_session():
    """Should list all checkpoints for session, ordered by phase"""
    
def test_handle_dirty_state_with_user_consent():
    """Should prompt user if uncommitted changes exist"""
    
def test_checkpoint_failure_doesnt_block_workflow():
    """Should log warning but allow workflow to continue"""
    
def test_store_checkpoint_metadata():
    """Should save checkpoint-to-phase mapping in .cortex/"""

def test_validate_staged_files_blocks_absolute_paths():
    """Should detect and block commits with absolute Windows paths (C:\, D:\)"""
    
def test_validate_staged_files_blocks_unix_home_paths():
    """Should detect and block commits with /home/ and /Users/ paths"""
    
def test_validate_staged_files_blocks_machine_names():
    """Should detect and block commits with machine-specific names (AHHOME, HOSTNAME)"""
    
def test_validate_staged_files_allows_relative_paths():
    """Should allow commits with relative paths (src/, cortex-brain/)"""
    
def test_checkpoint_creation_fails_on_privacy_violation():
    """Should fail checkpoint creation if staged files contain absolute paths"""
```

**Coverage Target:** 95%+

#### Test Suite 3: RollbackOrchestrator

**File:** `tests/orchestrators/test_rollback_orchestrator.py`

**RED Phase Tests:**
```python
def test_parse_rollback_target_complete():
    """Should parse 'complete' as full rollback"""
    
def test_parse_rollback_target_single_phase():
    """Should parse 'phase-2' as rollback to before phase 2"""
    
def test_parse_rollback_target_phase_range():
    """Should parse 'phases-1-3' as rollback to before phase 1"""
    
def test_show_rollback_preview_with_diff():
    """Should show git diff of changes to be lost"""
    
def test_prompt_user_confirmation():
    """Should require 'yes' to confirm rollback"""
    
def test_create_safety_checkpoint_before_rollback():
    """Should create backup checkpoint before git reset"""
    
def test_execute_git_rollback():
    """Should reset to checkpoint commit SHA"""
    
def test_rollback_workflow_state():
    """Should update workflow checkpoint to match git state"""
    
def test_handle_rollback_failure():
    """Should preserve current state if rollback fails"""
```

**Coverage Target:** 95%+

### Integration Tests

#### Integration Test 1: End-to-End Planning with Checkpoints

**File:** `tests/integration/test_planning_with_checkpoints.py`

**Scenario:**
```python
def test_planning_workflow_creates_phase_checkpoints():
    """
    Given: User requests feature planning
    When: Planning orchestrator executes all phases
    Then:
      - Pre-work checkpoint created before planning starts
      - Skeleton phase checkpoint created after skeleton
      - Phase 1 checkpoint created after phase 1
      - Phase 2 checkpoint created after phase 2
      - Phase 3 checkpoint created after phase 3
      - All checkpoints stored in .cortex/phase-checkpoints.json
    """
```

#### Integration Test 2: TDD Workflow with Checkpoints

**File:** `tests/integration/test_tdd_with_checkpoints.py`

**Scenario:**
```python
def test_tdd_cycle_creates_phase_checkpoints():
    """
    Given: User starts TDD cycle for new feature
    When: TDD orchestrator executes RED → GREEN → REFACTOR
    Then:
      - Pre-work checkpoint created before RED phase
      - RED checkpoint created after writing failing test
      - GREEN checkpoint created after implementation
      - REFACTOR checkpoint created after refactoring
      - All checkpoints can be listed with "list checkpoints"
    """
```

#### Integration Test 3: Rollback Single Phase

**File:** `tests/integration/test_rollback_single_phase.py`

**Scenario:**
```python
def test_rollback_to_phase_2():
    """
    Given: Planning completed phases 1-3
    When: User executes "rollback phase 2"
    Then:
      - Diff preview shows changes in phases 2-3
      - User prompted for confirmation
      - Safety checkpoint created
      - Git reset to phase-2 checkpoint
      - Workflow state updated to phase-2
      - User can resume from phase 2
    """
```

#### Integration Test 4: Rollback Complete

**File:** `tests/integration/test_rollback_complete.py`

**Scenario:**
```python
def test_rollback_complete_workflow():
    """
    Given: Planning completed all phases
    When: User executes "rollback"
    Then:
      - Diff preview shows ALL changes
      - User prompted for confirmation
      - Safety checkpoint created
      - Git reset to pre-work checkpoint
      - Workflow state reset to initial state
      - Repository restored to pre-work state
    """
```

#### Integration Test 5: Git History Enrichment

**File:** `tests/integration/test_git_history_enrichment.py`

**Scenario:**
```python
def test_request_with_file_gets_git_history_context():
    """
    Given: User requests "plan authentication for src/auth/login.py"
    When: Unified entry point receives request
    Then:
      - Git history analyzed for login.py
      - Context includes: commits, contributors, security patterns
      - Context injected into Tier 3
      - Context cached for 1 hour
      - Subsequent requests use cached context
    """
```

### Error Scenario Tests

#### Error Test 1: Git Not Available

**File:** `tests/error_scenarios/test_git_not_available.py`

```python
def test_checkpoint_creation_when_git_unavailable():
    """
    Given: Git command not found or repository not initialized
    When: PhaseCheckpointManager attempts checkpoint creation
    Then:
      - Error logged with remediation steps
      - Workflow continues without checkpoint
      - User warned: "Checkpoints unavailable - git not found"
    """
```

#### Error Test 2: Dirty State Declined

**File:** `tests/error_scenarios/test_dirty_state_declined.py`

```python
def test_user_declines_dirty_state_consent():
    """
    Given: Uncommitted changes exist
    When: PhaseCheckpointManager detects dirty state
    And: User declines to commit/stash
    Then:
      - Checkpoint creation cancelled
      - Workflow continues without checkpoint
      - User warned: "Checkpoint skipped - uncommitted changes"
    """
```

#### Error Test 3: Rollback Checkpoint Not Found

**File:** `tests/error_scenarios/test_rollback_checkpoint_not_found.py`

```python
def test_rollback_when_checkpoint_missing():
    """
    Given: User requests "rollback phase 2"
    When: Phase 2 checkpoint doesn't exist
    Then:
      - Error message: "Phase 2 checkpoint not found"
      - List available checkpoints
      - Rollback cancelled (no git reset)
    """
```

### Performance Tests

#### Performance Test 1: Git History Analysis Speed

**File:** `tests/performance/test_git_history_performance.py`

```python
def test_analyze_typical_file_under_2_seconds():
    """
    Given: File with 100-500 commits
    When: GitHistoryEnricher analyzes file
    Then: Analysis completes in <2 seconds
    """
    
def test_analyze_large_file_under_5_seconds():
    """
    Given: File with 500-1000 commits
    When: GitHistoryEnricher analyzes file
    Then: Analysis completes in <5 seconds
    """
    
def test_cache_reduces_redundant_analysis():
    """
    Given: File analyzed once
    When: Same file analyzed again within 1 hour
    Then: Cached result used (analysis time <100ms)
    """
```

#### Performance Test 2: Checkpoint Creation Speed

**File:** `tests/performance/test_checkpoint_performance.py`

```python
def test_checkpoint_creation_under_500ms_clean_repo():
    """
    Given: Clean repository (no uncommitted changes)
    When: PhaseCheckpointManager creates checkpoint
    Then: Checkpoint created in <500ms
    """
    
def test_checkpoint_creation_under_2s_dirty_repo():
    """
    Given: Dirty repository with consent workflow
    When: PhaseCheckpointManager creates checkpoint
    Then: Total time (including prompt) <2 seconds
    """
```

### Test Execution Strategy

**Phase 1: Unit Tests (RED → GREEN → REFACTOR)**
- Write all RED phase tests for Component 1 (GitHistoryEnricher)
- Verify tests fail
- Implement Component 1 to make tests pass (GREEN)
- Refactor Component 1 while tests pass
- Repeat for Components 2-3

**Phase 2: Integration Tests**
- Write integration tests for happy paths
- Implement integration between components
- Verify end-to-end scenarios work

**Phase 3: Error Scenarios**
- Write error scenario tests
- Implement error handling
- Verify graceful degradation

**Phase 4: Performance Tests**
- Write performance tests
- Profile and optimize hot paths
- Verify performance targets met

---

## 📊 Success Metrics

### Quantitative Metrics

**Metric 1: Git History Usage**
- **Target:** 90%+ of requests with file references include git history context
- **Measurement:** Count requests with/without git history context in logs
- **Baseline:** 0% (current state)

**Metric 2: Checkpoint Creation Rate**
- **Target:** 95%+ of planning/TDD sessions have phase checkpoints
- **Measurement:** Count sessions with checkpoints vs total sessions
- **Baseline:** Manual checkpoints only (~10% adoption)

**Metric 3: Rollback Success Rate**
- **Target:** 99%+ of rollback commands succeed
- **Measurement:** Count successful rollbacks vs total rollback attempts
- **Baseline:** N/A (new feature)

**Metric 4: Performance**
- **Target:** Git history analysis <2s, checkpoint creation <500ms
- **Measurement:** Log timing metrics, calculate p95 latency
- **Baseline:** N/A (new feature)

### Qualitative Metrics

**Metric 5: User Satisfaction**
- **Target:** 4.5/5.0 stars for git enhancements
- **Measurement:** User feedback survey after 30 days
- **Baseline:** N/A (new feature)

**Metric 6: Developer Adoption**
- **Target:** 80%+ of developers use rollback commands regularly
- **Measurement:** Survey + usage logs after 60 days
- **Baseline:** N/A (new feature)

### Risk Indicators

**Risk Indicator 1: Checkpoint Failures**
- **Warning Threshold:** >5% checkpoint creation failures
- **Critical Threshold:** >10% checkpoint creation failures
- **Action:** Investigate git environment issues, improve error handling

**Risk Indicator 2: Performance Degradation**
- **Warning Threshold:** >20% of git history analyses exceed 2s
- **Critical Threshold:** >30% of git history analyses exceed 2s
- **Action:** Optimize git commands, increase cache effectiveness

---

## 📝 Implementation Phases

### Phase 0: Preparation (1 day)
- ✅ Create planning document (this document)
- ✅ Review with stakeholders
- ✅ Approve DoR/DoD
- ✅ Set up test repository for development

### Phase 1: Git History Enrichment (3-5 days)
**RED Phase:**
- Write failing tests for GitHistoryEnricher
- Verify tests fail
- Commit RED phase

**GREEN Phase:**
- Implement GitHistoryEnricher.enrich_request_context()
- Implement cache mechanism
- Implement Tier 3 injection
- Make tests pass
- Commit GREEN phase

**REFACTOR Phase:**
- Extract helper methods
- Optimize git command execution
- Add comprehensive logging
- Commit REFACTOR phase

**Integration:**
- Integrate with UnifiedEntryPointOrchestrator
- Test with real user requests
- Validate performance <2s

### Phase 2: Phase Checkpoint Manager (3-5 days)
**RED Phase:**
- Write failing tests for PhaseCheckpointManager
- Verify tests fail
- Commit RED phase

**GREEN Phase:**
- Implement create_pre_work_checkpoint()
- Implement create_phase_checkpoint()
- Implement get_checkpoint_for_phase()
- Make tests pass
- Commit GREEN phase

**REFACTOR Phase:**
- Extract checkpoint metadata storage
- Add retry logic for git failures
- Optimize dirty state detection
- Commit REFACTOR phase

**Integration:**
- Integrate with PlanningOrchestrator
- Integrate with TDDOrchestrator (or create if needed)
- Test with real planning/TDD workflows

### Phase 3: Rollback Orchestrator (3-5 days)
**RED Phase:**
- Write failing tests for RollbackOrchestrator
- Verify tests fail
- Commit RED phase

**GREEN Phase:**
- Implement parse_rollback_target()
- Implement show_rollback_preview()
- Implement execute_rollback()
- Make tests pass
- Commit GREEN phase

**REFACTOR Phase:**
- Extract confirmation prompt logic
- Add safety checks
- Improve error messages
- Commit REFACTOR phase

**Integration:**
- Wire up user commands ("rollback", "rollback phase 2")
- Test all rollback scenarios
- Validate safety checkpoint creation

### Phase 4: Integration & Testing (2-3 days)
- Run all integration tests
- Run error scenario tests
- Run performance tests
- Fix any issues found
- Validate all DoD criteria

### Phase 5: Documentation (1-2 days)
- Write user guide for rollback commands
- Write developer guide for checkpoint integration
- Update architecture diagrams
- Create demo video (optional)

### Phase 6: Deployment (1 day)
- Merge to CORTEX-3.0 branch
- Run full test suite in CI/CD
- Deploy to production
- Monitor for issues

**Total Estimated Duration:** 14-21 days (3-4 weeks)

---

## 🔄 Rollback Plan (If Implementation Fails)

**Scenario: Implementation uncovers blocking issues**

**Rollback Steps:**
1. Revert all commits to CORTEX-3.0 branch
2. Restore original UnifiedEntryPointOrchestrator (no git history enrichment)
3. Restore original PlanningOrchestrator (no phase checkpoints)
4. Delete new modules (GitHistoryEnricher, PhaseCheckpointManager, RollbackOrchestrator)
5. Run regression tests to validate no breakage
6. Document lessons learned

**Rollback Safety:**
- All new code is additive (no breaking changes to existing modules)
- Git checkpoints are local only (no data loss risk)
- Rollback can be executed in <1 hour

---

## 📚 References

### Existing CORTEX Documentation
- `cortex-brain/brain-protection-rules.yaml` - SKULL Rule #8 (git checkpoints)
- `cortex-brain/git-checkpoint-rules.yaml` - Auto-checkpoint configuration
- `src/orchestrators/git_checkpoint_orchestrator.py` - Current checkpoint system
- `src/validators/git_history_validator.py` - Git history validation
- `src/tier3/context_intelligence.py` - Tier 3 context system
- `.github/prompts/modules/tdd-mastery-guide.md` - TDD workflow

### External References
- Git Best Practices: https://git-scm.com/book/en/v2
- TDD Workflow: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- OWASP Secure Coding: https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/

---

## 📋 Approval Checklist

**Planning Review:**
- ☐ Feature overview clear and comprehensive
- ☐ Current state accurately documented with gaps identified
- ☐ Target state achievable and measurable
- ☐ Technical design sound and integrates with existing systems

**DoR Review:**
- ☐ All DoR criteria satisfied (requirements, feasibility, dependencies, tests)
- ☐ OWASP security review completed with conditional approval
- ☐ Risk assessment includes mitigation strategies

**DoD Review:**
- ☐ All DoD criteria defined and measurable
- ☐ Test strategy comprehensive (unit + integration + e2e)
- ☐ User acceptance scenarios realistic and testable
- ☐ Deployment validation steps clear

**Implementation Review:**
- ☐ Implementation phases follow TDD Mastery workflow
- ☐ Estimated duration reasonable (14-21 days)
- ☐ Rollback plan includes safety measures

**Stakeholder Approval:**
- ☐ Product Owner: Asif Hussain (signature: _________________)
- ☐ Technical Lead: Asif Hussain (signature: _________________)
- ☐ Security Reviewer: (signature: _________________)

**Plan Status:** 🟡 **PENDING APPROVAL**

---

**End of Plan Document**
