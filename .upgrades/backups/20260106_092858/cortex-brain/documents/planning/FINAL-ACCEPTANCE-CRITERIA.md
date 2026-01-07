# 🎯 CORTEX v4.0+ Final Acceptance Criteria

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** January 2, 2026  
**Status:** ✅ ACTIVE - Comprehensive Testing Authority  
**Purpose:** Granular acceptance criteria for final implementation testing across all orchestrators and enhancements  
**Governance Compliance:** 10.0/10 - Fully aligned with brain-protection-rules.yaml  

---

## 📋 Document Purpose

This document serves as the **final testing authority** for CORTEX v4.0+ implementation. All features, orchestrators, and enhancements MUST pass these criteria before being considered complete.

**Testing Approach:**
- **Granular Level:** Each criterion is individually testable
- **Rule-Based:** Explicitly references SKULL brain protection rules
- **Measurable:** Quantifiable pass/fail conditions
- **Comprehensive:** Covers all orchestrators and enhancements
- **Governance-Aligned:** Every criterion maps to brain-protection-rules.yaml

---

## 🛡️ Section 1: Master Orchestrator (CORE REQUIREMENT)

### 1.1 Pattern-Based Routing
**SKULL Rule:** `TIERED_PLANNING_ENFORCEMENT`, `MANDATORY_PLANNING_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| MO-1.1.1 | Exact pattern matching for 90%+ of requests | Unit test with 100 sample inputs | ≥90% match success rate |
| MO-1.1.2 | Planning patterns detected correctly (`/CORTEX Plan`, `create a plan`) | Regex pattern test suite | 100% detection accuracy |
| MO-1.1.3 | Implementation patterns bypass planning (`implement`, `build`, `create`) | Pattern differentiation tests | 100% correct routing |
| MO-1.1.4 | Continuation patterns route to last orchestrator (`continue`, `resume`) | Context middleware integration test | 100% continuation detection |
| MO-1.1.5 | Ambiguous inputs fallback to LLM classifier | Mock LLM classifier test | Fallback triggers <10% of time |

**Test File:** `tests/orchestrators/test_master_orchestrator.py`

**Evidence Required:**
```python
# Test case example
def test_planning_pattern_detection():
    master = MasterOrchestrator(...)
    
    planning_inputs = [
        "/CORTEX Plan user authentication",
        "create a plan for payment system",
        "plan: database migration"
    ]
    
    for input_text in planning_inputs:
        match = master.route_request(input_text)
        assert match.orchestrator_id == "planning_orchestrator"
        assert match.confidence >= 0.95
```

### 1.2 Orchestrator Lifecycle Management
**SKULL Rule:** `GIT_CHECKPOINT_ENFORCEMENT`, `DEFINITION_OF_DONE`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| MO-1.2.1 | Pre-execution hooks validate workspace | Integration test with invalid workspace | Hook prevents execution |
| MO-1.2.2 | Post-execution hooks create git checkpoints | Mock git operations test | Checkpoint created after each phase |
| MO-1.2.3 | Error hooks cleanup partial artifacts | Failure simulation test | Orphaned files removed on error |
| MO-1.2.4 | State sharing between orchestrators works | Cross-orchestrator integration test | State persists and retrieves correctly |
| MO-1.2.5 | Metrics tracking captures all executions | Metrics assertion test | `_request_count`, `_pattern_match_count` accurate |

**Test File:** `tests/orchestrators/test_master_orchestrator_lifecycle.py`

**Evidence Required:**
- Pre-execution hook log entries
- Git checkpoint commit history
- Cleanup log after forced error
- State DB query results showing cross-orchestrator data

### 1.3 Cross-Session Context Middleware (Phase 4.5)
**SKULL Rule:** `OPERATIONAL_READINESS_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| MO-1.3.1 | Tier 1 orchestrator session continuation (<200 tokens) | Token counter test | Context ≤200 tokens |
| MO-1.3.2 | Tier 2 project-level continuation (fallback) | Active project simulation test | Routes to Planning v5 |
| MO-1.3.3 | Priority logic (orchestrator > project) works | Dual context test (both available) | Orchestrator session wins |
| MO-1.3.4 | `continue`, `resume`, `keep going` detected | Continuation pattern regex test | 100% detection rate |
| MO-1.3.5 | Context injection includes metadata only | Context structure validation test | No full conversation history |

**Test File:** `tests/middleware/test_cross_session_context.py`

**Evidence Required:**
```json
{
  "recent_activity": [{
    "session_id": "session-20260102-101500",
    "orchestrator": "tdd_master",
    "intent": "run tests for auth module",
    "artifacts": ["test_results.json"],
    "timestamp": "2026-01-02T10:15:00Z"
  }],
  "continuation_detected": true,
  "continuation_type": "orchestrator_session",
  "context_source": "tier1_working_memory",
  "token_count": 187
}
```

---

## 🧠 Section 2: Planning System Orchestrator (🛡️ AUTONOMOUS)

### 2.1 Folder Structure Creation
**SKULL Rule:** `PLAN_ARTIFACT_LOCATION_ENFORCEMENT`, `FILE_ORGANIZATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| PS-2.1.1 | Creates correct folder structure | Filesystem assertion test | All 4 subfolders exist |
| PS-2.1.2 | Folder name sanitization (lowercase, hyphens) | Naming validation test | No spaces/special chars |
| PS-2.1.3 | Path is `cortex-brain/documents/planning/active/{PLAN_NAME}/` | Path validation test | Exact path match |
| PS-2.1.4 | Subfolders: `context/`, `reports/`, `artifacts/`, `tracking/` | Subfolder existence test | All 4 present |
| PS-2.1.5 | `00-master-plan.md` created in root | File existence test | File present in root |

**Test File:** `tests/orchestrators/planning/test_folder_structure.py`

**Required Structure:**
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md
├── context/
├── reports/
├── artifacts/
└── tracking/
    └── progress-tracker.json
```

### 2.2 Mandatory Plan Content (00-master-plan.md)
**SKULL Rule:** `PROGRESS_TRACKER_ENFORCEMENT`, `REFACTOR_CODE_CLEANUP_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| PS-2.2.1 | Visual progress tracking present | Markdown parser test | Progress bar ASCII art found |
| PS-2.2.2 | Response template reminder included | Grep for `response-templates-v4.yaml:863` | Reference present |
| PS-2.2.3 | Final REFACTOR phase exists | Phase list parser test | Phase 5/N is "REFACTOR Cleanup" |
| PS-2.2.4 | `copilot_instructions` block present | YAML/Markdown parser test | Block with 3+ keys exists |
| PS-2.2.5 | REFACTOR phase has ≥18 cleanup tasks | Task counter test | Task count ≥18 |

**Test File:** `tests/orchestrators/planning/test_master_plan_content.py`

**Evidence Required:**
````markdown
## 📊 Visual Progress Tracking

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🎨 PLAN NAME - EXECUTION PROGRESS                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Phase 1: Discovery              [████████████████████] 100% │ ✅ COMPLETE    ║
║ Phase 5: REFACTOR Cleanup       [░░░░░░░░░░░░░░░░░░░░]  0% │ ⏳ PENDING     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Response Template:** `response-templates-v4.yaml:863` (autonomous_execution_progress)

---

## Phase 5: REFACTOR Cleanup

### Tasks (18+ required)
1. Remove orphaned functions
2. Eliminate duplicate code
3. Clean unused imports
4. Fix code smells
...
````

### 2.3 Governance Integration (Phase -1)
**SKULL Rule:** `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| PS-2.3.1 | Phase -1 "Knowledge Library" exists | Phase list parser test | Phase -1 present |
| PS-2.3.2 | Phase -1 executes BEFORE Phase 0 | Execution order test | Phase -1 timestamp < Phase 0 |
| PS-2.3.3 | Knowledge Library consultation documented | Artifact existence test | `context/knowledge-library-findings.md` exists |
| PS-2.3.4 | Phase -1 includes ≥4 consultation tasks | Task counter test | ≥4 tasks in Phase -1 |
| PS-2.3.5 | DoD includes "Knowledge Library reviewed" | DoD parser test | Checklist item present |

**Test File:** `tests/orchestrators/planning/test_governance_integration.py`

**Required Phase -1 Structure:**
```markdown
## Phase -1: Knowledge Library Consultation

**Purpose:** Consult existing knowledge before new work

### Tasks
1. Query Tier 2 knowledge graph for related patterns
2. Review lessons-learned.yaml for similar projects
3. Check TRUTH-SOURCES.yaml for authoritative references
4. Document findings in `context/knowledge-library-findings.md`

### Definition of Done
- [ ] Knowledge Library reviewed
- [ ] Relevant patterns identified
- [ ] Lessons learned applied to plan
```

### 2.4 AST Scanning During Planning
**SKULL Rule:** `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| PS-2.4.1 | AST scan executes in Phase 0 (Discovery) | Execution trace test | AST scan logged in Phase 0 |
| PS-2.4.2 | Scan results include function/class/import counts | JSON schema validation | Output has `functions`, `classes`, `imports` keys |
| PS-2.4.3 | Duplicate code detection runs | AST analysis assertion | Duplicates reported if >2 identical signatures |
| PS-2.4.4 | Orphaned code detection runs | Call graph analysis test | Uncalled functions identified |
| PS-2.4.5 | AST findings saved to `context/ast-analysis.json` | File existence + schema test | File present, valid JSON |

**Test File:** `tests/orchestrators/planning/test_ast_scanning.py`

**Required AST Output Schema:**
```json
{
  "scan_timestamp": "2026-01-02T10:15:00Z",
  "files_scanned": 42,
  "functions": {
    "total": 128,
    "public": 95,
    "private": 33,
    "orphaned": 3
  },
  "classes": {
    "total": 24,
    "methods": 87
  },
  "imports": {
    "total": 56,
    "unused": 8
  },
  "duplicates": [
    {
      "signature": "def calculate_total(items: List[Item]) -> float",
      "locations": [
        "src/billing/invoice.py:45",
        "src/orders/cart.py:123"
      ]
    }
  ],
  "orphaned_functions": [
    "src/utils/legacy_helpers.py::old_transform_data()"
  ]
}
```

### 2.5 Worker Plan Task Injection
**SKULL Rule:** `SUB_PLAN_TASK_INJECTION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| PS-2.5.1 | Worker plans inherit tasks from master plan | Task comparison test | 100% task match |
| PS-2.5.2 | No manual task definition in worker plans | Worker plan parser test | No hardcoded tasks |
| PS-2.5.3 | Standard tasks injected (git, analysis, docs, TDD, DoD) | Standard task presence test | All 6 standard tasks present |
| PS-2.5.4 | Task injection happens via `UnifiedPlanGenerator` | Code path trace test | `inject_standard_tasks()` called |
| PS-2.5.5 | Worker plan references master plan | Cross-reference validation | `# Tasks (injected from master plan)` comment present |

**Test File:** `tests/orchestrators/planning/test_task_injection.py`

**Evidence Required:**
```markdown
# Worker Plan: WP01-Discovery.md

## ✅ Tasks (injected from master plan)

### 📌 Phase Start
- [ ] 🔄 Git Checkpoint (Start): Create phase start checkpoint

### 🔍 Analysis
- [ ] 📊 AST & Cortex Lens: Run AST and Cortex Lens analysis

### Phase-Specific Tasks (from master plan Phase 1)
- [ ] Analyze existing codebase patterns
- [ ] Document current architecture

### 📝 Documentation
- [ ] 📝 Update Documentation: Update README, API docs

### ✅ TDD & DoD
- [ ] ✅ TDD Validation: Verify RED→GREEN→REFACTOR cycle
- [ ] 🎯 DoD Validation: Validate all DoD criteria met
```

---

## 🧪 Section 3: TDD Orchestrator (📋 GUIDED)

### 3.1 RED→GREEN→REFACTOR Cycle
**SKULL Rule:** `TDD_ENFORCEMENT`, `RED_PHASE_VALIDATION`, `GREEN_PHASE_VALIDATION`, `REFACTOR_CODE_CLEANUP_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| TDD-3.1.1 | RED phase: Test must fail first | Test runner assertion | Exit code != 0 |
| TDD-3.1.2 | GREEN phase: Simplest implementation passes test | Code complexity metric | Cyclomatic complexity ≤3 |
| TDD-3.1.3 | GREEN phase blocks over-engineering | Code review plugin test | No features beyond test scope |
| TDD-3.1.4 | REFACTOR phase removes orphaned code | AST diff analysis | Orphaned function count decreases |
| TDD-3.1.5 | REFACTOR phase eliminates duplicates | Clone detection test | Duplicate code blocks removed |

**Test File:** `tests/orchestrators/tdd/test_tdd_cycle.py`

**Evidence Required:**
```bash
# RED Phase
$ pytest tests/test_auth.py::test_login
FAILED tests/test_auth.py::test_login - AssertionError: Expected 200, got 401
✅ RED phase validated (test failed as expected)

# GREEN Phase  
$ pytest tests/test_auth.py::test_login
PASSED tests/test_auth.py::test_login
✅ GREEN phase validated (test passed)

# REFACTOR Phase (orphan detection)
$ python -m cortex_lens.ast_analyzer --detect-orphans src/auth/
Orphaned functions removed: 2
- src/auth/helpers.py::old_validate_token()
- src/auth/helpers.py::legacy_hash_password()
✅ REFACTOR phase validated (orphans removed)
```

### 3.2 Test File Location Validation
**SKULL Rule:** `TEST_LOCATION_SEPARATION`, `TDD_TEST_FILE_VALIDATION`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| TDD-3.2.1 | User app tests in user repo `tests/` folder | Path validation test | No user tests in `CORTEX/tests/` |
| TDD-3.2.2 | CORTEX tests in `CORTEX/tests/` folder | Path validation test | CORTEX tests not in user repos |
| TDD-3.2.3 | Test files follow `test_*.py` naming | Filename pattern test | All test files match pattern |
| TDD-3.2.4 | Empty test files detected and blocked | File content validation | Tests have ≥1 test function |
| TDD-3.2.5 | Test isolation enforced (no cross-contamination) | Import analysis test | User tests don't import CORTEX tests |

**Test File:** `tests/orchestrators/tdd/test_file_location.py`

**Evidence Required:**
```python
# test_file_location.py
def test_user_app_tests_in_user_repo():
    user_test_files = find_test_files("/path/to/user/app")
    cortex_test_files = find_test_files("/path/to/CORTEX")
    
    # Ensure no overlap
    assert len(set(user_test_files) & set(cortex_test_files)) == 0
    
    # Ensure user tests not in CORTEX folder
    for test_file in user_test_files:
        assert "/CORTEX/tests/" not in test_file
```

### 3.3 REFACTOR Phase Code Cleanup (18+ Tasks)
**SKULL Rule:** `REFACTOR_CODE_CLEANUP_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| TDD-3.3.1 | Orphaned function detection | AST call graph analysis | ≥1 orphaned function identified (if any exist) |
| TDD-3.3.2 | Duplicate code detection | Clone detection tool | ≥1 duplicate block identified (if any exist) |
| TDD-3.3.3 | Unused import removal | Import usage analysis | All unused imports removed |
| TDD-3.3.4 | Code smell detection (long functions) | Metrics analysis | Functions >50 lines flagged |
| TDD-3.3.5 | Complexity reduction | Cyclomatic complexity metric | Complexity ≤10 per function |

**Test File:** `tests/orchestrators/tdd/test_refactor_cleanup.py`

**Minimum REFACTOR Tasks (18+):**
1. Remove orphaned functions (0 calls)
2. Eliminate duplicate function implementations
3. Clean unused imports
4. Fix long functions (>50 lines)
5. Reduce cyclomatic complexity (>10)
6. Extract magic numbers to constants
7. Rename cryptic variable names
8. Add missing type hints
9. Remove dead code branches
10. Consolidate similar classes
11. Extract repeated logic to helpers
12. Fix code smells (Pylint/Flake8)
13. Update stale comments
14. Add missing docstrings
15. Optimize inefficient loops
16. Remove debug print statements
17. Simplify nested conditionals
18. Apply SOLID principles

---

## 🧹 Section 4: ADO Operations Orchestrator (🛡️ AUTONOMOUS)

### 4.1 Work Item Generation
**SKULL Rule:** `SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT`, `DEFINITION_OF_READY`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| ADO-4.1.1 | User story format correct | Story parser test | Title, description, acceptance criteria present |
| ADO-4.1.2 | Acceptance criteria ≥3 items | Criteria counter test | ≥3 testable criteria |
| ADO-4.1.3 | Effort estimation realistic (Fibonacci) | Estimation validation | Points in [1,2,3,5,8,13,21] |
| ADO-4.1.4 | Tasks broken down granularly | Task counter test | ≥5 tasks per story |
| ADO-4.1.5 | Definition of Ready checklist included | Checklist parser test | DoR section present |

**Test File:** `tests/orchestrators/ado/test_work_item_generation.py`

**Required Work Item Format:**
```markdown
# User Story: User Authentication

**As a** user  
**I want** to log in securely  
**So that** my data is protected

## Acceptance Criteria
1. User can log in with email + password
2. Invalid credentials show error message
3. Session expires after 30 minutes

## Effort Estimation
**Story Points:** 5 (Fibonacci)

## Tasks
1. Create login API endpoint
2. Implement JWT token generation
3. Add session management
4. Write unit tests (RED→GREEN→REFACTOR)
5. Update API documentation

## Definition of Ready
- [ ] Requirements clarified with stakeholder
- [ ] Design mockups approved
- [ ] API contract defined
- [ ] Test scenarios documented
```

### 4.2 Vision API Integration
**SKULL Rule:** `VISION_API_INTEGRATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| ADO-4.2.1 | Image attachments auto-trigger Vision API | Image detection test | Vision API called on PNG/JPG/JPEG |
| ADO-4.2.2 | Vision analysis <500ms | Performance benchmark test | P95 latency <500ms |
| ADO-4.2.3 | Analysis results injected into context | Context validation test | Vision data in orchestrator context |
| ADO-4.2.4 | UI elements extracted from screenshots | Entity extraction test | Buttons, forms, navigation extracted |
| ADO-4.2.5 | Work items generated from visual analysis | Integration test | Screenshot → Work items automatically |

**Test File:** `tests/orchestrators/ado/test_vision_integration.py`

**Vision Analysis Output Example:**
```json
{
  "image_path": "attachments/screenshot.png",
  "analysis_timestamp": "2026-01-02T10:15:00Z",
  "latency_ms": 423,
  "ui_elements": {
    "buttons": ["Login", "Sign Up", "Forgot Password"],
    "forms": ["Login Form (email, password)"],
    "navigation": ["Home", "Dashboard", "Settings"],
    "layouts": ["2-column responsive grid"]
  },
  "suggested_work_items": [
    {
      "type": "feature",
      "title": "Implement Login Form",
      "description": "2-field form with email/password validation"
    }
  ]
}
```

---

## 🧼 Section 5: Vacuum Orchestrator (🛡️ AUTONOMOUS)

### 5.1 Deep Filesystem Cleanup
**SKULL Rule:** `VACUUM_CYCLE_ENFORCEMENT`, `FILE_ORGANIZATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| VAC-5.1.1 | Orphaned files detected | Filesystem scan test | Files not referenced elsewhere identified |
| VAC-5.1.2 | Duplicate files detected (hash-based) | SHA256 comparison test | Files with identical hashes flagged |
| VAC-5.1.3 | Empty directories removed | Directory cleanup test | 0-file directories deleted |
| VAC-5.1.4 | Temp files cleaned (`.tmp`, `.bak`) | Pattern matching test | Temp extensions removed |
| VAC-5.1.5 | Reorganization preserves git history | Git log validation | `git log --follow` works for moved files |

**Test File:** `tests/orchestrators/vacuum/test_filesystem_cleanup.py`

**Evidence Required:**
```bash
$ python -m src.orchestrators.vacuum --path cortex-brain/documents/

🧹 Vacuum Orchestrator Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Files scanned: 1,247
🗑️ Orphaned files: 12 (deleted)
📋 Duplicate files: 5 groups (deduplicated)
📂 Empty directories: 8 (removed)
🧹 Temp files: 23 (cleaned)
✅ Reorganization complete (git history preserved)
```

### 5.2 Safe Deletion Workflow
**SKULL Rule:** `PREVENT_DIRTY_STATE_WORK`, `GIT_CHECKPOINT_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| VAC-5.2.1 | Git checkpoint before vacuum | Git operations test | Checkpoint commit created |
| VAC-5.2.2 | User approval required for deletion | Interactive prompt test | Deletion blocked without approval |
| VAC-5.2.3 | Dry-run mode available | Dry-run flag test | No files deleted in dry-run |
| VAC-5.2.4 | Undo command available post-vacuum | Git revert test | `git revert` restores deleted files |
| VAC-5.2.5 | Summary report generated | Report file validation | `vacuum-report.md` exists |

**Test File:** `tests/orchestrators/vacuum/test_safe_deletion.py`

---

## 🔧 Section 6: Refinement Orchestrator (📋 GUIDED)

### 6.1 7-Phase Improvement Workflow
**SKULL Rule:** `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`, `SOLID_PRINCIPLES`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| REF-6.1.1 | Phase 1: Code analysis completes | AST scan validation | Analysis artifact generated |
| REF-6.1.2 | Phase 2: SOLID violations detected | SOLID checker test | ≥1 violation identified (if any exist) |
| REF-6.1.3 | Phase 3: Security scan runs | Security scanner integration | OWASP report generated |
| REF-6.1.4 | Phase 4: Performance profiling executes | Profiler output validation | Flame graph generated |
| REF-6.1.5 | Phase 5-7: Refactoring + validation + docs | Integration test | All 3 phases complete |

**Test File:** `tests/orchestrators/refinement/test_improvement_workflow.py`

**Phase Validation Checklist:**
- [ ] Phase 1: AST analysis artifact in `artifacts/`
- [ ] Phase 2: SOLID report in `reports/`
- [ ] Phase 3: Security scan results in `reports/`
- [ ] Phase 4: Performance profile in `artifacts/`
- [ ] Phase 5: Refactored code passes tests
- [ ] Phase 6: Validation report generated
- [ ] Phase 7: Documentation updated

---

## 🔍 Section 7: Debug Orchestrator (📋 GUIDED)

### 7.1 Error Analysis and Fix
**SKULL Rule:** `TDD_ENFORCEMENT`, `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| DBG-7.1.1 | Error reproduction test case created | Test file validation | `test_bug_reproduction.py` exists |
| DBG-7.1.2 | Root cause analysis documented | Analysis report validation | `debug-report.md` includes root cause section |
| DBG-7.1.3 | Fix follows TDD cycle (test first) | Test execution order validation | Test created before fix |
| DBG-7.1.4 | Regression tests added | Test coverage analysis | Coverage includes bug scenario |
| DBG-7.1.5 | Fix validated in multiple scenarios | Test suite validation | ≥3 test cases for bug |

**Test File:** `tests/orchestrators/debug/test_error_analysis.py`

---

## 📊 Section 8: CORTEX Lens (📋 GUIDED)

### 8.1 Dashboard Visualization
**SKULL Rule:** `MACHINE_READABLE_FORMATS`, `INLINE_CSS_PROHIBITION`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| LENS-8.1.1 | Dashboard HTML generates without errors | HTML validation test | Valid HTML5 |
| LENS-8.1.2 | D3.js visualizations render | Headless browser test | SVG elements present |
| LENS-8.1.3 | Data sources machine-readable (JSON) | JSON schema validation | All data sources valid JSON |
| LENS-8.1.4 | No inline CSS (all styles external) | CSS linter test | 0 inline styles found |
| LENS-8.1.5 | Responsive design (3 breakpoints) | Viewport test | Works at 375px/768px/1440px |

**Test File:** `tests/orchestrators/lens/test_dashboard_visualization.py`

---

## 🛡️ Section 9: Brain Protection Rules (SKULL) - Cross-Cutting

### 9.1 Git Isolation
**SKULL Rule:** `GIT_ISOLATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| SKULL-9.1.1 | CORTEX code never commits to user repos | Git log analysis test | No CORTEX files in user repo history |
| SKULL-9.1.2 | User repo changes isolated from CORTEX | Path validation test | User changes outside `CORTEX/` folder |
| SKULL-9.1.3 | `.gitignore` prevents brain state commits | Gitignore rule test | Brain files in `.gitignore` |
| SKULL-9.1.4 | Separate repos for CORTEX vs user apps | Repository detection test | Different `.git` folders |
| SKULL-9.1.5 | Git checkpoints use correct repo context | Commit repo validation | Checkpoints in correct repo |

**Test File:** `tests/brain_protection/test_git_isolation.py`

### 9.2 Document Organization
**SKULL Rule:** `DOCUMENT_ORGANIZATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| SKULL-9.2.1 | No root-level docs allowed | Filesystem scan test | 0 `.md` files in repo root (except README) |
| SKULL-9.2.2 | All docs in `cortex-brain/documents/{category}/` | Path validation test | 100% compliance |
| SKULL-9.2.3 | Valid categories enforced | Category whitelist test | Only allowed categories used |
| SKULL-9.2.4 | Automatic relocation on violation | Filesystem watcher test | Misplaced docs moved automatically |
| SKULL-9.2.5 | Blocking error on manual root-level doc creation | File creation hook test | Operation blocked with error |

**Test File:** `tests/brain_protection/test_document_organization.py`

**Allowed Categories:**
- `reports/`
- `analysis/`
- `summaries/`
- `investigations/`
- `planning/`
- `implementation-guides/`

### 9.3 TDD Enforcement (Cross-Orchestrator)
**SKULL Rule:** `TDD_ENFORCEMENT`, `RED_PHASE_VALIDATION`, `GREEN_PHASE_VALIDATION`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| SKULL-9.3.1 | All orchestrators follow RED→GREEN→REFACTOR | Orchestrator workflow audit | 100% compliance |
| SKULL-9.3.2 | Production code requires passing tests | Code deployment gate | Deployment blocked without tests |
| SKULL-9.3.3 | RED phase validation logs test failures | Log analysis test | Failure logs present for all RED phases |
| SKULL-9.3.4 | GREEN phase prevents over-engineering | Code review automated check | No features beyond test scope |
| SKULL-9.3.5 | REFACTOR phase documented in all plans | Plan content validation | REFACTOR phase present in all plans |

**Test File:** `tests/brain_protection/test_tdd_enforcement.py`

### 9.4 Knowledge Library Integration
**SKULL Rule:** `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| SKULL-9.4.1 | Phase -1 mandatory in all plans | Phase list parser test | Phase -1 present |
| SKULL-9.4.2 | Knowledge graph queried before work | Query log analysis | Query executed in Phase -1 |
| SKULL-9.4.3 | Lessons learned reviewed | Artifact validation | `lessons-learned.yaml` access logged |
| SKULL-9.4.4 | TRUTH-SOURCES.yaml referenced | Reference parser test | Truth sources cited in plan |
| SKULL-9.4.5 | Phase -1 findings documented | Artifact existence test | `knowledge-library-findings.md` exists |

**Test File:** `tests/brain_protection/test_knowledge_library.py`

### 9.5 REFACTOR Code Cleanup Enforcement
**SKULL Rule:** `REFACTOR_CODE_CLEANUP_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| SKULL-9.5.1 | Final REFACTOR phase in all plans | Phase list validation | Last phase is REFACTOR |
| SKULL-9.5.2 | ≥18 cleanup tasks per file category | Task counter test | Task count ≥18 |
| SKULL-9.5.3 | Orphaned code detection runs | AST analysis assertion | Orphan detection executed |
| SKULL-9.5.4 | Duplicate code removal verified | Clone detection validation | Duplicates removed |
| SKULL-9.5.5 | Per-artifact cleanup documented | Cleanup report validation | Report includes per-file analysis |

**Test File:** `tests/brain_protection/test_refactor_cleanup.py`

**18+ Cleanup Task Categories:**
1. **Orphaned Functions** (≥3 tasks)
2. **Duplicate Code** (≥3 tasks)
3. **Unused Imports** (≥2 tasks)
4. **Code Smells** (≥4 tasks: long functions, complexity, magic numbers, cryptic names)
5. **Documentation** (≥3 tasks: docstrings, comments, type hints)
6. **Performance** (≥3 tasks: inefficient loops, nested conditionals, optimizations)

---

## 🎯 Section 10: All Orchestrators - Common Requirements

### 10.1 Autonomous Execution Progress Template
**SKULL Rule:** `AUTONOMOUS_EXECUTION_PROTECTION`, `PROGRESS_TRACKER_ENFORCEMENT`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| ALL-10.1.1 | 🛡️ orchestrators use correct response template | Template validation test | `autonomous_execution_progress` used |
| ALL-10.1.2 | Response header includes 🛡️ shield icon | Markdown parser test | `## 🛡️🧠 CORTEX` found |
| ALL-10.1.3 | CORTEX stops after hand-off header | Execution flow test | No CORTEX guidance after header |
| ALL-10.1.4 | Orchestrator Python code executes independently | Process isolation test | Separate Python process spawned |
| ALL-10.1.5 | Visual progress bar renders correctly | ASCII art validation | Progress bar pattern matches template |

**Test File:** `tests/orchestrators/common/test_autonomous_execution.py`

**Required Response Template (🛡️ Orchestrators):**
````markdown
## 🛡️🧠 CORTEX {Orchestrator Name} Execution
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 📊 Execution Progress

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🎨 {OPERATION NAME} - AUTONOMOUS EXECUTION                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Phase 1: {Name}                 [████████████████████] 100% │ ✅ COMPLETE    ║
║ Phase 2: {Name}                 [████████░░░░░░░░░░░░]  45% │ 🔄 IN PROGRESS ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Orchestrator:** {orchestrator_name}.py executing independently...
````

### 10.2 Git Checkpoint Integration
**SKULL Rule:** `GIT_CHECKPOINT_ENFORCEMENT`, `PREVENT_DIRTY_STATE_WORK`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| ALL-10.2.1 | Checkpoint created at phase start | Git log validation | Commit with phase marker exists |
| ALL-10.2.2 | Checkpoint includes phase metadata | Commit message parser | Metadata in commit body |
| ALL-10.2.3 | Dirty state prevents phase start | Git status check test | Error on uncommitted changes |
| ALL-10.2.4 | Checkpoint restoration available | Git reset test | Previous phase restorable |
| ALL-10.2.5 | Phase end checkpoint created | Git log validation | 2 commits per phase (start + end) |

**Test File:** `tests/orchestrators/common/test_git_checkpoint.py`

**Commit Message Format:**
```
Phase 2 Start: {Phase Name}

Plan: {plan_id}
Orchestrator: {orchestrator_name}
Timestamp: 2026-01-02T10:15:00Z
Tasks: {task_count}
```

### 10.3 Definition of Done Validation
**SKULL Rule:** `DEFINITION_OF_DONE`

| ID | Criterion | Test Method | Pass Condition |
|----|-----------|-------------|----------------|
| ALL-10.3.1 | DoD checklist in every phase | Phase content parser | DoD section present |
| ALL-10.3.2 | ≥5 DoD items per phase | Checklist counter | ≥5 items in DoD |
| ALL-10.3.3 | DoD validated before phase completion | Validation hook test | Incomplete DoD blocks transition |
| ALL-10.3.4 | TDD validation in DoD | DoD item parser | "TDD validation" item present |
| ALL-10.3.5 | Documentation update in DoD | DoD item parser | "Documentation updated" item present |

**Test File:** `tests/orchestrators/common/test_dod_validation.py`

**Standard DoD Template:**
```markdown
## Definition of Done
- [ ] All tasks completed
- [ ] Tests pass (RED→GREEN→REFACTOR)
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Git checkpoint created
- [ ] DoD validated
```

---

## 🎓 Section 11: Testing Methodology

### 11.1 Test Execution Order

1. **Unit Tests** (isolated component testing)
   - Master Orchestrator routing
   - Pattern matching logic
   - AST scanning algorithms
   - Individual SKULL rule enforcement

2. **Integration Tests** (cross-component testing)
   - Orchestrator hand-off workflow
   - Git checkpoint integration
   - Context middleware injection
   - Vision API → ADO Operations flow

3. **End-to-End Tests** (full workflow testing)
   - Complete planning workflow (Phase -1 → Phase N)
   - TDD RED→GREEN→REFACTOR cycle
   - Vacuum deep cleanup
   - Debug analysis → fix → validation

4. **Compliance Tests** (SKULL rule validation)
   - Git isolation enforcement
   - Document organization enforcement
   - TDD enforcement across orchestrators
   - REFACTOR cleanup enforcement

### 11.2 Test Coverage Requirements

| Component | Minimum Coverage | Tool |
|-----------|------------------|------|
| Master Orchestrator | 95% | pytest-cov |
| Planning System | 90% | pytest-cov |
| TDD Orchestrator | 95% | pytest-cov |
| ADO Operations | 85% | pytest-cov |
| Vacuum Orchestrator | 85% | pytest-cov |
| Brain Protection Rules | 100% | custom validator |

### 11.3 Performance Benchmarks

| Operation | P50 | P95 | P99 | Test Tool |
|-----------|-----|-----|-----|-----------|
| Pattern matching | <50ms | <100ms | <200ms | pytest-benchmark |
| AST scanning (100 files) | <2s | <5s | <10s | pytest-benchmark |
| Vision API analysis | <300ms | <500ms | <1s | pytest-benchmark |
| Git checkpoint creation | <100ms | <300ms | <500ms | pytest-benchmark |
| Plan generation (10 phases) | <5s | <10s | <15s | pytest-benchmark |

---

## 📝 Section 12: Final Acceptance Process

### 12.1 Test Suite Execution

```bash
# 1. Run all unit tests
pytest tests/unit/ -v --cov=src --cov-report=html

# 2. Run integration tests
pytest tests/integration/ -v

# 3. Run E2E tests
pytest tests/e2e/ -v --slow

# 4. Run SKULL compliance tests
pytest tests/brain_protection/ -v

# 5. Run performance benchmarks
pytest tests/benchmarks/ --benchmark-only

# 6. Generate final report
python scripts/generate_acceptance_report.py
```

### 12.2 Acceptance Report Format

```markdown
# CORTEX v4.0+ Final Acceptance Report

**Date:** {timestamp}  
**Tested By:** {tester_name}  
**Test Suite Version:** {version}

## Summary
- **Total Tests:** {total}
- **Passed:** {passed} ({percentage}%)
- **Failed:** {failed}
- **Skipped:** {skipped}

## Section Results
- [x] Section 1: Master Orchestrator (100%)
- [x] Section 2: Planning System (100%)
- [x] Section 3: TDD Orchestrator (100%)
- [ ] Section 4: ADO Operations (95% - 2 failures)
...

## Failed Tests
### ADO-4.2.2: Vision API latency
**Expected:** <500ms P95  
**Actual:** 547ms P95  
**Action:** Optimize Vision API request batching

## Performance Benchmarks
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Pattern matching P95 | <100ms | 87ms | ✅ PASS |
| AST scanning P95 | <5s | 4.2s | ✅ PASS |

## SKULL Compliance
| Rule | Status | Evidence |
|------|--------|----------|
| GIT_ISOLATION_ENFORCEMENT | ✅ PASS | No CORTEX files in user repos |
| TDD_ENFORCEMENT | ✅ PASS | 100% orchestrator compliance |

## Final Verdict
✅ **ACCEPTED** (98% pass rate, all critical tests passed)

**Conditions:**
- Fix ADO Vision API latency before production deployment
- All other tests passed
```

### 12.3 Sign-Off Checklist

- [ ] All unit tests pass (≥95% coverage)
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] All SKULL compliance tests pass (100%)
- [ ] Performance benchmarks meet targets
- [ ] Documentation updated
- [ ] Final acceptance report generated
- [ ] Stakeholder approval obtained

---

## 🎉 Conclusion

This document provides **comprehensive, granular acceptance criteria** for CORTEX v4.0+ implementation. All features, orchestrators, and enhancements MUST pass these criteria before being considered production-ready.

**Key Principles:**
1. **Testability:** Every criterion is individually testable
2. **Measurability:** Clear pass/fail conditions
3. **Governance Alignment:** Maps to brain-protection-rules.yaml
4. **Comprehensiveness:** Covers all orchestrators and enhancements
5. **Granularity:** Detailed enough for precise testing

**Testing Authority:** This document is the **final authority** for acceptance testing. No feature passes without meeting these criteria.

---

**End of Final Acceptance Criteria v1.0.0**
