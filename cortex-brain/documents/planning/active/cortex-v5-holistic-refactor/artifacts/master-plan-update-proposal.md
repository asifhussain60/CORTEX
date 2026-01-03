# 📋 Master Plan Update Proposal - Gap Remediation

**Plan ID:** cortex-v5-holistic-refactor  
**Update Date:** January 3, 2026  
**Update Type:** Gap Remediation (Critical)  
**Based On:** Brittleness & Acceptance Criteria Gap Analysis

---

## 🎯 Executive Summary

**Gaps Identified:** 18 critical gaps across acceptance validation, mandatory content, and brittleness mitigation.

**Proposed Changes:**
1. **Add Phase -1:** Knowledge Library Consultation (SKULL compliance)
2. **Update Phase 6.2:** Add 6 acceptance validation tasks
3. **Add Phase 6.4:** AST Integration (14h)
4. **Add Phase 7.1:** Orchestrator Lifecycle Hooks (14h)
5. **Expand Phase 10:** REFACTOR automation with 18+ tasks

**Timeline Impact:** +2 days (40.5 days → 42.5 days total)

---

## 🆕 Phase -1: Knowledge Library Consultation

**Status:** NEW - Insert before Phase 0  
**Duration:** 1 hour  
**Rationale:** SKULL rule `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT` requires consultation before new work

### Purpose

Consult Tier 2 Knowledge Graph and governance documents before planning execution to:
- Identify existing patterns for orchestrator brittleness mitigation
- Apply lessons learned from similar architectural refactors
- Ensure SKULL rule compliance from the start
- Leverage authoritative references (BaseOrchestrator v4.1 design patterns)

### Tasks

**Task -1.1: Query Knowledge Graph** (15 min)
```bash
# Query Tier 2 for related patterns
python -m src.tier2.knowledge_graph query \
  --topic "orchestrator brittleness" \
  --topic "architectural refactor" \
  --output context/knowledge-graph-findings.md
```

**Task -1.2: Review Lessons Learned** (15 min)
```bash
# Extract relevant lessons
grep -i "orchestrator\|refactor\|migration" \
  cortex-brain/lessons-learned.yaml \
  > context/lessons-learned-relevant.md
```

**Task -1.3: Consult TRUTH-SOURCES** (15 min)
```yaml
# Review authoritative references
references:
  - BaseOrchestrator v4.1 design patterns
  - Master Orchestrator architecture decisions
  - Planning System v5 specifications
  - SKULL brain protection rules
```

**Task -1.4: Query Brain Protection Rules** (15 min)
```bash
# Extract applicable SKULL rules
python -m src.tier0.governance query_rules \
  --plan-type "architectural" \
  --scope "orchestrator_migration" \
  --output context/applicable-skull-rules.md
```

### Deliverable

**Artifact:** `context/knowledge-library-findings.md`

**Content Structure:**
```markdown
# Knowledge Library Findings

## Knowledge Graph Patterns
- Pattern 1: Hybrid control flow → Pure autonomous pattern
- Pattern 2: File-based state → SQLite database pattern
- ...

## Lessons Learned Applied
- Lesson 1: Start with BaseOrchestrator abstraction (from v3.0 refactor)
- Lesson 2: Use MCP protocol for universal invocation
- ...

## Authoritative References
- BaseOrchestrator v4.1: [link to design doc]
- Master Orchestrator ADR: [link]
- ...

## Applicable SKULL Rules
1. TDD_ENFORCEMENT
2. KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
3. GIT_CHECKPOINT_ENFORCEMENT
4. REFACTOR_CODE_CLEANUP_ENFORCEMENT
...

## Recommendations for Plan Execution
- Use BaseOrchestrator v4.1 patterns for consistency
- Implement git checkpoints after each phase
- Include REFACTOR phase with ≥18 cleanup tasks
```

### Definition of Done

- [ ] Knowledge Graph queried (≥3 patterns identified)
- [ ] Lessons learned reviewed (≥5 relevant lessons)
- [ ] TRUTH-SOURCES consulted (≥3 authoritative references)
- [ ] Brain protection rules queried (≥10 applicable SKULL rules)
- [ ] Findings documented in `context/knowledge-library-findings.md`
- [ ] Recommendations applied to plan phases

---

## 📝 Phase 6.2 Updates: Acceptance Validation Tasks

**Current Status:** Phase 6.2 (Cleanup v2) marked complete, but missing acceptance validation

**Proposed Change:** Add 6 new tasks to Phase 6.2 for acceptance criteria validation

### Task 6.2.1: Master Orchestrator Acceptance Validation (4h)

**Purpose:** Validate MO-1.1.* through MO-1.3.* acceptance criteria

**Test Suite:** `tests/acceptance/test_master_orchestrator_acceptance.py`

**Test Cases:**
```python
def test_pattern_matching_90_percent_accuracy():
    """MO-1.1.1: Pattern matching ≥90% accuracy"""
    master = MasterOrchestrator(...)
    test_inputs = load_test_corpus(100)  # 100 sample inputs
    
    matches = [master.route_request(input) for input in test_inputs]
    accuracy = sum(1 for m in matches if m.is_matched) / len(matches)
    
    assert accuracy >= 0.90, f"Match accuracy {accuracy} < 0.90"

def test_planning_pattern_detection_100_percent():
    """MO-1.1.2: Planning patterns detected correctly"""
    patterns = [
        "/CORTEX Plan user authentication",
        "create a plan for payment system",
        "plan: database migration"
    ]
    
    for pattern in patterns:
        match = master.route_request(pattern)
        assert match.orchestrator_id == "planning_orchestrator"
        assert match.confidence >= 0.95

def test_continuation_detection_100_percent():
    """MO-1.1.4: Continuation patterns route to last orchestrator"""
    continuation_patterns = ["continue", "resume", "keep going", "next phase"]
    
    for pattern in continuation_patterns:
        context = middleware.enrich_context(pattern, {})
        assert context["continuation_detected"] == True

def test_token_count_under_200():
    """MO-1.3.1: Tier 1 continuation <200 tokens"""
    context = middleware.enrich_context("continue", {})
    token_count = count_tokens(json.dumps(context))
    
    assert token_count <= 200, f"Token count {token_count} > 200"
```

**Deliverable:** Acceptance validation report (`reports/master-orchestrator-acceptance-report.md`)

---

### Task 6.2.2: Cross-Session Context Acceptance Validation (3h)

**Purpose:** Validate MO-1.3.* criteria for context middleware

**Test Suite:** `tests/acceptance/test_cross_session_context_acceptance.py`

**Test Cases:**
```python
def test_orchestrator_continuation_priority():
    """MO-1.3.3: Priority logic (orchestrator > project)"""
    # Setup: Both orchestrator session and active project exist
    session_mgr.record_session(orchestrator="tdd_master")
    project_tracker.create_project("active-project")
    
    context = middleware.enrich_context("continue", {})
    
    # Orchestrator session should win
    assert context["continuation_type"] == "orchestrator_session"
    assert context["recent_activity"][0]["orchestrator"] == "tdd_master"

def test_context_structure_validation():
    """MO-1.3.5: Context injection includes metadata only"""
    context = middleware.enrich_context("continue", {})
    
    required_keys = ["recent_activity", "continuation_detected", "continuation_type"]
    for key in required_keys:
        assert key in context
    
    # Should NOT include full conversation history
    assert "full_conversation" not in context
    assert "message_history" not in context
```

**Deliverable:** Context middleware acceptance report

---

### Task 6.2.3: Plan Filename Standardization (2h)

**Purpose:** Fix PS-2.1.5 gap - standardize plan filename casing

**Changes:**
1. Rename `00-MASTER-PLAN-V5.md` → `00-master-plan.md` (lowercase)
2. Update Planning System v5 generator to use lowercase
3. Create validation test suite

**Validation Test:**
```python
def test_master_plan_filename_lowercase():
    """PS-2.1.5: Master plan uses lowercase naming"""
    plan_folder = Path("cortex-brain/documents/planning/active/test-plan")
    plan_file = plan_folder / "00-master-plan.md"
    
    assert plan_file.exists(), "Master plan file missing"
    assert plan_file.name == "00-master-plan.md", "Filename not lowercase"
```

**Deliverable:** Standardized filenames + validation tests

---

### Task 6.2.4: Update Master Plan with Mandatory Content (2h)

**Purpose:** Fix PS-2.2.2 and PS-2.2.4 gaps - add missing mandatory blocks

**Additions to 00-MASTER-PLAN-V5.md:**

**1. Response Template Reference (after Visual Progress Tracker):**
```markdown
## 🎯 Response Template Reference

**Orchestrator Type:** 🛡️ AUTONOMOUS  
**Template:** `response-templates-v4.yaml:863` (autonomous_execution_progress)  
**Reference:** See `.github/prompts/CORTEX.prompt.md` lines 118-157

**Visual Marker:** When this orchestrator is engaged, user sees `🛡️` in response header.
```

**2. Copilot Instructions Block (after Executive Summary):**
```markdown
## 🤖 Copilot Instructions

```yaml
copilot_instructions:
  # Response template
  response_template: "autonomous_execution_progress"
  template_reference: "response-templates-v4.yaml:863"
  
  # SKULL enforcement
  tdd_enforcement: true
  tdd_cycle_required: "RED→GREEN→REFACTOR"
  
  # REFACTOR requirements
  final_refactor_required: true
  refactor_phase: "Phase 10"
  refactor_task_minimum: 18
  refactor_categories:
    - orphaned_function_removal
    - duplicate_code_elimination
    - unused_import_cleanup
    - code_smell_remediation
    - complexity_reduction
    - magic_number_extraction
    - type_hint_validation
    - docstring_completeness
  
  # Governance integration
  knowledge_library_consultation: true
  phase_minus_one_required: true
  skull_rules_applicable:
    - TDD_ENFORCEMENT
    - KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
    - GIT_CHECKPOINT_ENFORCEMENT
    - REFACTOR_CODE_CLEANUP_ENFORCEMENT
    - PROGRESS_TRACKER_ENFORCEMENT
```
```

**Deliverable:** Updated master plan with mandatory content

---

### Task 6.2.5: Insert Phase -1 Knowledge Library Consultation (1h)

**Purpose:** Fix PS-2.3.* gaps - add Phase -1 to plan

**Change:** Add Phase -1 section before Phase 0 in 00-MASTER-PLAN-V5.md

**Content:** (See Phase -1 section above)

**Deliverable:** Updated plan with Phase -1

---

### Task 6.2.6: ADO v2 Acceptance Validation Report (2h)

**Purpose:** Validate ADO-4.1.* criteria and generate report

**Test Execution:**
```bash
# Run ADO v2 acceptance tests
pytest tests/acceptance/test_ado_v2_acceptance.py -v \
  --cov=src/orchestrators/ado/v2 \
  --cov-report=html

# Generate report
python scripts/generate_acceptance_report.py \
  --component ado_v2 \
  --criteria cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md \
  --section 4 \
  --output reports/ado-v2-acceptance-report.md
```

**Report Template:**
```markdown
# ADO v2 Acceptance Report

## Summary
- Total Criteria: 5 (ADO-4.1.1 through ADO-4.1.5)
- Passed: 4
- Failed: 1
- Compliance: 80%

## Detailed Results

### ADO-4.1.1: User Story Format
✅ PASS - All fields validated by wizard

### ADO-4.1.2: Acceptance Criteria ≥3
✅ PASS - Wizard enforces minimum 3 criteria

### ADO-4.1.3: Fibonacci Estimation
✅ PASS - Wizard validates points [1,2,3,5,8,13,21]

### ADO-4.1.4: Task Breakdown
✅ PASS - Wizard prompts for ≥5 tasks

### ADO-4.1.5: Vision API Auto-Trigger
❌ FAIL - Vision API integration not tested
```

**Deliverable:** ADO v2 acceptance report

---

## 🆕 Phase 6.4: AST Integration into Planning System v5

**Status:** NEW - Insert after Phase 6.3 (Vacuum v2)  
**Duration:** 14 hours  
**Rationale:** Fix PS-2.4.* gaps - AST scanning for holistic discovery

### Purpose

Integrate AST (Abstract Syntax Tree) scanning into Planning System v5 to enable:
- Orphaned function detection (no callers)
- Duplicate code detection (identical signatures)
- Unused import identification
- Complexity metrics (cyclomatic complexity)
- Holistic code discovery before planning

### Task 6.4.1: Create AST Scanner Agent (6h)

**File:** `src/cortex_agents/ast_scanner.py` (400-500 lines)

**Features:**
```python
class ASTScanner:
    """
    Abstract Syntax Tree analyzer for Python codebases.
    
    Capabilities:
    - Parse all Python files in workspace
    - Build call graph (function → callers mapping)
    - Detect orphaned functions (zero callers)
    - Identify duplicate function signatures
    - Count complexity metrics
    - Find unused imports
    """
    
    def scan_workspace(self, root_path: Path) -> ScanResult:
        """Full workspace AST scan"""
        pass
    
    def detect_orphans(self, call_graph: CallGraph) -> List[OrphanedFunction]:
        """Find functions with zero callers"""
        pass
    
    def detect_duplicates(self, functions: List[FunctionDef]) -> List[Duplicate]:
        """Find functions with identical signatures"""
        pass
    
    def analyze_complexity(self, functions: List[FunctionDef]) -> Dict[str, int]:
        """Calculate cyclomatic complexity per function"""
        pass
```

**Dependencies:**
- `ast` (stdlib)
- `radon` (for complexity metrics)
- `rope` (for call graph analysis)

**Test Suite:** `tests/cortex_agents/test_ast_scanner.py` (100+ tests)

---

### Task 6.4.2: Integrate AST Scanning into Planning v5 Phase 0 (4h)

**Change:** Update Planning Orchestrator v5 to run AST scan in Phase 0 (Discovery)

**Implementation:**
```python
# src/orchestrators/planning_orchestrator_v5.py

def _execute_phase_0_discovery(self, context: Dict[str, Any]) -> PhaseResult:
    """
    Phase 0: Context Discovery
    
    NEW: Includes AST scanning for holistic code analysis
    """
    
    # Existing: Semantic search
    relevant_files = self._semantic_search(context["feature_description"])
    
    # NEW: AST scanning
    ast_scanner = ASTScanner()
    scan_result = ast_scanner.scan_workspace(self.workspace_root)
    
    # Save AST findings
    ast_output = {
        "scan_timestamp": datetime.now().isoformat(),
        "files_scanned": scan_result.file_count,
        "functions": {
            "total": len(scan_result.functions),
            "public": len([f for f in scan_result.functions if not f.name.startswith("_")]),
            "private": len([f for f in scan_result.functions if f.name.startswith("_")]),
            "orphaned": len(scan_result.orphaned_functions)
        },
        "classes": {
            "total": len(scan_result.classes),
            "methods": sum(len(c.methods) for c in scan_result.classes)
        },
        "imports": {
            "total": len(scan_result.imports),
            "unused": len(scan_result.unused_imports)
        },
        "duplicates": [
            {
                "signature": dup.signature,
                "locations": [str(loc) for loc in dup.locations]
            }
            for dup in scan_result.duplicates
        ],
        "orphaned_functions": [
            f"{f.file_path}::{f.name}()"
            for f in scan_result.orphaned_functions
        ]
    }
    
    # Write to context/ast-analysis.json
    ast_file = self.plan_folder / "context" / "ast-analysis.json"
    ast_file.write_text(json.dumps(ast_output, indent=2))
    
    return PhaseResult(
        phase_name="Phase 0: Discovery",
        artifacts=[
            "context/discovery.md",
            "context/ast-analysis.json"  # NEW
        ]
    )
```

---

### Task 6.4.3: Generate AST Findings Report (2h)

**Purpose:** Surface AST findings in plan generation

**Template Addition:**
```markdown
## 📊 Codebase Analysis (AST Scan)

**Scan Date:** {scan_timestamp}  
**Files Scanned:** {files_scanned}

### Function Statistics
- **Total Functions:** {total_functions}
- **Public Functions:** {public_functions}
- **Private Functions:** {private_functions}
- **Orphaned Functions:** {orphaned_functions} ⚠️

### Code Health Metrics
- **Duplicate Code Blocks:** {duplicate_count} 🔴
- **Unused Imports:** {unused_imports} 🟡
- **High Complexity Functions:** {high_complexity_count} 🟡

### Recommendations
{{#if orphaned_functions}}
⚠️ **REFACTOR PHASE:** {orphaned_functions} orphaned functions detected. Plan Phase 10 should include removal.
{{/if}}

{{#if duplicates}}
🔴 **REFACTOR PHASE:** {duplicates} duplicate code blocks detected. Consolidation required.
{{/if}}

**Full Report:** See `context/ast-analysis.json`
```

---

### Task 6.4.4: Test AST Integration (2h)

**Test Suite:** `tests/orchestrators/planning/test_ast_integration.py`

**Test Cases:**
```python
def test_ast_scan_executes_in_phase_0():
    """PS-2.4.1: AST scan executes in Phase 0"""
    orchestrator = PlanningOrchestratorV5(...)
    
    result = orchestrator.execute_phase(0, context)
    
    ast_file = orchestrator.plan_folder / "context" / "ast-analysis.json"
    assert ast_file.exists()

def test_ast_output_schema_valid():
    """PS-2.4.2: Scan results include function/class/import counts"""
    orchestrator = PlanningOrchestratorV5(...)
    orchestrator.execute_phase(0, context)
    
    ast_data = json.loads((orchestrator.plan_folder / "context" / "ast-analysis.json").read_text())
    
    assert "functions" in ast_data
    assert "classes" in ast_data
    assert "imports" in ast_data
    assert ast_data["functions"]["total"] > 0

def test_duplicate_detection():
    """PS-2.4.3: Duplicate code detection runs"""
    # Create workspace with duplicate functions
    test_workspace = create_test_workspace_with_duplicates()
    
    orchestrator = PlanningOrchestratorV5(workspace_root=test_workspace)
    orchestrator.execute_phase(0, context)
    
    ast_data = json.loads((orchestrator.plan_folder / "context" / "ast-analysis.json").read_text())
    assert len(ast_data["duplicates"]) >= 1

def test_orphaned_function_detection():
    """PS-2.4.4: Orphaned code detection runs"""
    test_workspace = create_test_workspace_with_orphans()
    
    orchestrator = PlanningOrchestratorV5(workspace_root=test_workspace)
    orchestrator.execute_phase(0, context)
    
    ast_data = json.loads((orchestrator.plan_folder / "context" / "ast-analysis.json").read_text())
    assert len(ast_data["orphaned_functions"]) >= 1
```

### Deliverables

- [ ] AST Scanner agent implemented (400-500 lines)
- [ ] Planning v5 Phase 0 includes AST scan
- [ ] `context/ast-analysis.json` generated per acceptance schema
- [ ] AST findings surfaced in plan generation
- [ ] Test suite passing (100% coverage)

---

## 🆕 Phase 7.1: Orchestrator Lifecycle Hooks

**Status:** NEW - Insert before current Phase 7  
**Duration:** 14 hours  
**Rationale:** Fix MO-1.2.* gaps - implement lifecycle hooks for all orchestrators

### Purpose

Implement standardized lifecycle hooks for orchestrators:
- **Pre-execution:** Workspace validation, dependency checks
- **Post-execution:** Git checkpoint creation, artifact finalization
- **Error cleanup:** Rollback partial artifacts, state cleanup

### Task 7.1.1: Pre-Execution Workspace Validation Hook (3h)

**Implementation:** `src/orchestrators/hooks/pre_execution.py`

```python
class PreExecutionHook:
    """
    Validates workspace readiness before orchestrator execution.
    
    Checks:
    - Workspace is git repository
    - No uncommitted changes (clean state)
    - Required directories exist
    - Sufficient disk space
    - Python environment valid
    """
    
    def validate(self, orchestrator: BaseOrchestratorV4_1) -> ValidationResult:
        """Run all pre-execution validations"""
        checks = [
            self._check_git_repo(),
            self._check_clean_state(),
            self._check_disk_space(),
            self._check_python_env()
        ]
        
        failed = [c for c in checks if not c.passed]
        
        if failed:
            raise PreExecutionValidationError(failed)
        
        return ValidationResult(passed=True)
```

**Integration:**
```python
# src/orchestrators/base_orchestrator_v4_1.py

def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    # NEW: Pre-execution hook
    PreExecutionHook().validate(self)
    
    # Existing execution logic
    result = self._execute_internal(context)
    
    return result
```

---

### Task 7.1.2: Post-Execution Git Checkpoint Hook (4h)

**Implementation:** `src/orchestrators/hooks/post_execution.py`

```python
class PostExecutionHook:
    """
    Creates git checkpoint after successful orchestrator execution.
    
    Checkpoint naming: checkpoint-{orchestrator}-{phase}-{timestamp}
    Example: checkpoint-planning-phase-2-20260103-143022
    """
    
    def create_checkpoint(
        self,
        orchestrator: BaseOrchestratorV4_1,
        phase: str,
        artifacts: List[Path]
    ) -> GitCheckpoint:
        """Create git commit + tag for phase completion"""
        
        # Stage artifacts
        for artifact in artifacts:
            git.add(artifact)
        
        # Commit with structured message
        commit_msg = f"""
        {orchestrator.name} - {phase} Complete
        
        Artifacts:
        {chr(10).join(f"- {a}" for a in artifacts)}
        
        Orchestrator: {orchestrator.id}
        Phase: {phase}
        Timestamp: {datetime.now().isoformat()}
        """
        
        commit_sha = git.commit(commit_msg)
        
        # Create lightweight tag
        tag_name = f"checkpoint-{orchestrator.id}-{phase}-{int(time.time())}"
        git.tag(tag_name, commit_sha)
        
        return GitCheckpoint(sha=commit_sha, tag=tag_name)
```

**Integration:**
```python
# src/orchestrators/base_orchestrator_v4_1.py

def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    PreExecutionHook().validate(self)
    
    result = self._execute_internal(context)
    
    # NEW: Post-execution hook
    PostExecutionHook().create_checkpoint(
        orchestrator=self,
        phase=context.get("phase", "execution"),
        artifacts=result["artifacts"]
    )
    
    return result
```

---

### Task 7.1.3: Error Cleanup Hook (3h)

**Implementation:** `src/orchestrators/hooks/error_cleanup.py`

```python
class ErrorCleanupHook:
    """
    Cleans up partial artifacts on orchestrator failure.
    
    Cleanup actions:
    - Remove incomplete artifact files
    - Rollback database transactions
    - Clear in-memory state
    - Log failure details
    """
    
    def cleanup(
        self,
        orchestrator: BaseOrchestratorV4_1,
        error: Exception,
        partial_artifacts: List[Path]
    ) -> CleanupResult:
        """Clean up after orchestrator failure"""
        
        cleanup_log = []
        
        # Remove partial files
        for artifact in partial_artifacts:
            if artifact.exists():
                artifact.unlink()
                cleanup_log.append(f"Removed partial artifact: {artifact}")
        
        # Rollback state database
        orchestrator.state_db.rollback()
        cleanup_log.append("Database transaction rolled back")
        
        # Log error
        self.logger.error(
            f"Orchestrator {orchestrator.id} failed: {error}",
            extra={"cleanup_actions": cleanup_log}
        )
        
        return CleanupResult(
            cleaned_artifacts=len(partial_artifacts),
            actions=cleanup_log
        )
```

**Integration:**
```python
# src/orchestrators/base_orchestrator_v4_1.py

def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    PreExecutionHook().validate(self)
    
    try:
        result = self._execute_internal(context)
        
        PostExecutionHook().create_checkpoint(
            orchestrator=self,
            phase=context.get("phase", "execution"),
            artifacts=result["artifacts"]
        )
        
        return result
    
    except Exception as error:
        # NEW: Error cleanup hook
        ErrorCleanupHook().cleanup(
            orchestrator=self,
            error=error,
            partial_artifacts=self._get_partial_artifacts()
        )
        
        raise  # Re-raise after cleanup
```

---

### Task 7.1.4: Test Lifecycle Hooks (4h)

**Test Suite:** `tests/orchestrators/hooks/test_lifecycle_hooks.py`

**Test Cases:**
```python
def test_pre_execution_validation_blocks_dirty_workspace():
    """MO-1.2.1: Pre-execution hook validates workspace"""
    # Create dirty workspace
    workspace = create_test_workspace()
    (workspace / "temp.txt").write_text("uncommitted")
    
    orchestrator = TestOrchestrator(workspace_root=workspace)
    
    with pytest.raises(PreExecutionValidationError) as exc_info:
        orchestrator.execute({})
    
    assert "uncommitted changes" in str(exc_info.value).lower()

def test_post_execution_creates_git_checkpoint():
    """MO-1.2.2: Post-execution hook creates git checkpoint"""
    orchestrator = TestOrchestrator(...)
    
    result = orchestrator.execute({"phase": "test-phase"})
    
    # Verify git tag created
    tags = git.tag(list=True)
    assert any("checkpoint-test-phase" in tag for tag in tags)

def test_error_cleanup_removes_partial_artifacts():
    """MO-1.2.3: Error hooks cleanup partial artifacts"""
    orchestrator = FailingOrchestrator(...)  # Orchestrator that fails mid-execution
    
    # Create partial artifact
    partial_file = orchestrator.plan_folder / "partial-artifact.md"
    
    with pytest.raises(Exception):
        orchestrator.execute({})
    
    # Verify partial artifact removed
    assert not partial_file.exists()
```

### Deliverables

- [ ] Pre-execution validation hook implemented
- [ ] Post-execution git checkpoint hook implemented
- [ ] Error cleanup hook implemented
- [ ] All hooks integrated into BaseOrchestrator v4.1
- [ ] Test suite passing (100% coverage)
- [ ] Documentation updated

---

## 🔧 Phase 10 Expansion: REFACTOR Automation

**Current Status:** Phase 10 exists but lacks detail  
**Proposed Change:** Expand Phase 10 with 18+ automated cleanup tasks

### Additional Tasks for Phase 10

**Task 10.1: Automated Orphaned Function Detection & Removal** (6h)
- Use AST scanner to identify functions with zero callers
- Generate removal plan (review before delete)
- Execute removal with test validation

**Task 10.2: Automated Duplicate Code Detection & Consolidation** (8h)
- Clone detection across codebase
- Identify consolidation targets
- Refactor duplicates into shared utilities

**Task 10.3: Unused Import Removal** (2h)
- Scan all Python files for unused imports
- Auto-remove with validation

**Task 10.4: Code Smell Detection & Refactoring** (8h)
- Run Pylint/Flake8 with strict rules
- Auto-fix where possible
- Generate manual fix plan for complex smells

**Task 10.5: Complexity Reduction** (6h)
- Identify functions with cyclomatic complexity >10
- Refactor into smaller functions
- Validate with tests

**Task 10.6: Extract Magic Numbers to Constants** (4h)
- Scan for magic numbers
- Extract to named constants
- Update all references

**Task 10.7: Type Hint Validation & Addition** (4h)
- Check type hint completeness
- Add missing type hints
- Validate with mypy

**Task 10.8: Docstring Completeness Check** (3h)
- Identify functions without docstrings
- Generate docstring templates
- Validate with pydocstyle

**Task 10.9: Final Acceptance Criteria Validation** (6h)
- Run all acceptance test suites
- Generate final acceptance report
- Address any failures

### REFACTOR Phase Structure

```markdown
## Phase 10: REFACTOR & Cleanup (2 days → 4 days)

**Goal:** Automated code cleanup with 18+ tasks

### Cleanup Categories (18+ tasks)

1. **Orphaned Code Removal** (Task 10.1)
   - Remove functions with zero callers
   - Validation: All removed functions have no references

2. **Duplicate Code Elimination** (Task 10.2)
   - Consolidate duplicate implementations
   - Validation: No duplicate signatures remain

3. **Unused Import Cleanup** (Task 10.3)
   - Auto-remove unused imports
   - Validation: All imports in use

4. **Code Smell Remediation** (Task 10.4)
   - Fix Pylint/Flake8 violations
   - Validation: Zero high-severity smells

5. **Complexity Reduction** (Task 10.5)
   - Refactor functions with complexity >10
   - Validation: All functions ≤10 complexity

6. **Magic Number Extraction** (Task 10.6)
   - Extract to named constants
   - Validation: Zero magic numbers

7. **Type Hint Validation** (Task 10.7)
   - Add missing type hints
   - Validation: 100% type hint coverage

8. **Docstring Completeness** (Task 10.8)
   - Add missing docstrings
   - Validation: All public functions documented

... (10 more tasks)

18. **Final Acceptance Validation** (Task 10.9)
    - Run all acceptance test suites
    - Generate final report
    - Validation: 100% acceptance criteria met
```

### Definition of Done (Updated)

- [ ] All 18+ cleanup tasks completed
- [ ] Zero orphaned functions
- [ ] Zero duplicate code blocks
- [ ] Zero unused imports
- [ ] Zero high-severity code smells
- [ ] All functions ≤10 cyclomatic complexity
- [ ] 100% type hint coverage
- [ ] 100% docstring coverage
- [ ] All acceptance criteria validated
- [ ] Final acceptance report generated

---

## 📊 Timeline Impact Summary

| Phase | Current Duration | New Duration | Change |
|-------|------------------|--------------|--------|
| **Phase -1** (NEW) | — | 1h | +1h |
| **Phase 6.2** (Acceptance) | Complete | +14h | +14h |
| **Phase 6.4** (NEW - AST) | — | 14h | +14h |
| **Phase 7.1** (NEW - Hooks) | — | 14h | +14h |
| **Phase 10** (REFACTOR) | 2d (16h) | 4d (32h) | +16h |
| **Total Impact** | 40.5 days | **42.5 days** | **+2 days** |

---

## 🎯 Updated Success Criteria

**Bootstrap Phase (Phases 0-4.5):**
- ✅ All original criteria met
- 🆕 Phase -1 Knowledge Library consultation complete
- 🆕 Mandatory plan content present (copilot_instructions, template reference)

**Migration Phase (Phases 5-9):**
- ✅ All original criteria met
- 🆕 AST scanning integrated into Planning v5
- 🆕 Orchestrator lifecycle hooks operational
- 🆕 Acceptance validation for completed phases

**REFACTOR Phase (Phase 10):**
- ✅ All original criteria met
- 🆕 18+ automated cleanup tasks executed
- 🆕 100% acceptance criteria compliance validated
- 🆕 Final acceptance report generated

---

## ✅ Approval Checklist

Before applying these changes, confirm:

- [ ] Gap analysis reviewed and accepted
- [ ] Timeline impact (+2 days) acceptable
- [ ] Phase -1 approach approved
- [ ] AST integration scope approved
- [ ] Lifecycle hooks design approved
- [ ] REFACTOR automation scope approved
- [ ] Resource allocation confirmed (14h blocks available)

---

**Prepared By:** CORTEX Gap Analysis Engine  
**Review Status:** Pending User Approval  
**Next Step:** Apply updates to 00-MASTER-PLAN-V5.md upon approval
