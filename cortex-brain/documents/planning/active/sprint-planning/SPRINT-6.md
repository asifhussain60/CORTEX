# Sprint 6 Migration Plan
**CORTEX 3.0 Orchestrator-to-Utility Migration**

**Author:** Asif Hussain  
**Created:** 2025-12-02  
**Sprint:** 6 of 8 (estimated)  
**Previous Sprint:** Sprint 5 - Metrics, Dashboard, Health (221 lines removed, 21% reduction)

---

## 🎯 Sprint 6 Objectives

**Goal:** Migrate 3 orchestrators to lightweight utilities, targeting ~400 lines removal

**Success Criteria:**
- ✅ All operations complete in <5 seconds (complex validation allowed longer)
- ✅ 30-35% code reduction per orchestrator
- ✅ System alignment passing (8/8 checks)
- ✅ Zero test failures
- ✅ All commits pushed to origin

**Current State:**
- Orchestrators remaining: 21 (down from 30 at Sprint 1 start)
- Code removed (cumulative): ~6,803 lines across 14 migrations
- System health: HEALTHY (8/8 alignment checks passing)

---

## 📊 Candidate Analysis

### 1. Session Completion Orchestrator (591 lines) - **HIGH PRIORITY**

**Purpose:** Comprehensive TDD session validation with quality enforcement

**Current Structure:**
- SessionCompletionOrchestrator (v2.0.0)
- Full test suite execution (Python pytest, .NET dotnet test, JS npm test)
- Before/after metrics comparison
- Git diff summary generation
- SKULL rule validation (22 rules from brain-protection-rules.yaml)
- **NEW v2.0:** Code quality enforcement pipeline
  - CodeCleanupValidator (debug statements, print statements)
  - LintIntegration (Pylint/Roslynator/ESLint)
  - ProductionReadinessChecklist (blocking issues)
- Document organization integration (Sprint 2)
- Completion report generation (markdown)
- Regression detection

**Dependencies:**
- workflows/code_cleanup_validator.py (CodeCleanupValidator)
- workflows/lint_integration.py (LintIntegration)
- workflows/production_readiness.py (ProductionReadinessChecklist)
- workflows/document_organizer.py (DocumentOrganizer)
- YAML parser (brain-protection-rules.yaml)
- Git subprocess commands
- Multi-framework test runners (pytest, dotnet, npm)

**Migration Assessment:**
- **Complexity:** High (multi-framework test execution, quality pipeline integration)
- **Core Operations:** 6-7 extractable
  1. `run_test_suite(project_path, framework)` - Execute tests with framework detection
  2. `compare_metrics(metrics_before, metrics_after)` - Calculate improvements/regressions
  3. `generate_diff_summary(start_commit, end_commit)` - Git diff stats
  4. `validate_skull_rules(rules_path)` - 22 rule validation
  5. `check_code_quality(project_path, enable_enforcement)` - Quality pipeline
  6. `generate_completion_report(session_data, output_path)` - Markdown report
  7. `complete_session(session_id, start_commit, metrics)` - Full validation workflow

- **Reduction Potential:** 35-40% (591 → ~370 lines)
- **Value:** Very high - critical TDD workflow quality gate
- **Risk:** Moderate - complex quality enforcement pipeline, must preserve 22 SKULL rules

**Key Simplifications:**
- Direct test runner commands (remove framework detection complexity)
- Simplified SKULL validation (load YAML, iterate rules without orchestration)
- Module-level quality validators (initialize once)
- Direct markdown generation (remove template engine)
- Inline subprocess handling (remove command abstraction)

---

### 2. Planning Document Migrator (368 lines) - **MODERATE PRIORITY**

**Purpose:** Migrate planning documents to status-based subdirectories

**Current Structure:**
- PlanningDocumentMigrator class (Phase 2)
- Status detection from frontmatter (`**Status:** <status>` pattern)
- Status mapping: in-progress/proposed → active, approved → approved, completed → completed, cancelled/deprecated → deprecated
- Directory organization (active/, approved/, completed/, deprecated/)
- Dry-run mode preview
- Automatic backup before migration
- Validation checks after migration
- Preserves existing subdirectories (ado/, features/, enhancements/)

**Dependencies:**
- File I/O (shutil, pathlib)
- Regex pattern matching (frontmatter parsing `**Status:** (.+)`)
- JSON for dry-run results
- No external packages

**Migration Assessment:**
- **Complexity:** Low (file operations, pattern matching, no complex logic)
- **Core Operations:** 5 extractable
  1. `migrate_documents(planning_dir, dry_run, create_backup)` - Full migration workflow
  2. `detect_status(file_path)` - Parse frontmatter for status
  3. `backup_planning_dir(planning_dir, backup_dir)` - Create backup
  4. `validate_migration(planning_dir)` - Post-migration checks
  5. `organize_by_status(file_path, status)` - Move to status subdirectory

- **Reduction Potential:** 30-35% (368 → ~245 lines)
- **Value:** Moderate - organizational utility for planning documents
- **Risk:** Low - simple file operations, no critical dependencies

**Key Simplifications:**
- Direct regex matching (remove status mapping class)
- Inline backup (remove backup orchestration)
- Simplified validation (basic file count checks)
- Module-level status directories (hardcode active/, approved/, completed/, deprecated/)
- Remove dry-run JSON export (keep boolean flag only)

---

### 3. Phase Checkpoint Manager (331 lines) - **MODERATE PRIORITY**

**Purpose:** Manage workflow phase checkpoint metadata for rollback and progress tracking

**Current Structure:**
- PhaseCheckpointManager class
- Checkpoint metadata storage (.cortex/phase-checkpoints-{session_id}.json)
- GitCheckpointOrchestrator integration for checkpoint creation
- Pre-work checkpoint creation
- Phase checkpoint creation (with metrics)
- Checkpoint listing and retrieval
- Metadata file per session

**Dependencies:**
- src/orchestrators/git_checkpoint_orchestrator.py (GitCheckpointOrchestrator)
- JSON for metadata storage
- pathlib for file operations
- No external packages

**Migration Assessment:**
- **Complexity:** Low-Moderate (file-based metadata, git integration)
- **Core Operations:** 4-5 extractable
  1. `create_checkpoint(session_id, phase, metrics)` - Create phase checkpoint with git integration
  2. `store_metadata(session_id, phase, checkpoint_id, commit_sha, metrics)` - Save to JSON
  3. `list_checkpoints(session_id)` - Retrieve all checkpoints for session
  4. `get_checkpoint(session_id, phase)` - Get specific checkpoint
  5. `create_pre_work_checkpoint(session_id, operation)` - Initial checkpoint

- **Reduction Potential:** 30-35% (331 → ~220 lines)
- **Value:** Moderate - TDD workflow support, rollback capability
- **Risk:** Low - simple file operations, clear git integration pattern

**Key Simplifications:**
- Direct GitCheckpointOrchestrator calls (remove init abstraction)
- Simplified metadata structure (remove optional fields)
- Inline JSON operations (remove helper methods)
- Module-level checkpoint directory (.cortex/)
- Remove complex listing filters (return all checkpoints)

---

## 🎯 Recommended Sprint 6 Targets

### Option A: 3 Orchestrators - BALANCED (RECOMMENDED)

**Targets:** Session Completion + Planning Document Migrator + Phase Checkpoint Manager  
**Total Lines:** 1,290 lines (591 + 368 + 331)  
**Expected Reduction:** ~430 lines (33% average)  
**Estimated Time:** 4-5 hours  
**Risk:** Moderate

**Rationale:**
- **Session Completion (591):** High-value quality gate, complex but critical
- **Planning Document Migrator (368):** Quick organizational utility, low complexity
- **Phase Checkpoint Manager (331):** TDD workflow support, moderate complexity
- **Balance:** 1 complex (Session) + 2 moderate (Planning, Checkpoint)
- **Synergy:** All three are TDD workflow utilities (validation, planning, checkpoints)

**Task Breakdown:**
- Task 17: Session Completion (120 min investigation + implementation, 20 min testing)
- Task 18: Planning Document Migrator (60 min investigation + implementation, 10 min testing)
- Task 19: Phase Checkpoint Manager (75 min investigation + implementation, 15 min testing)
- Task 20: Sprint 6 validation and reporting (30 min)

---

### Option B: 2 Orchestrators - CONSERVATIVE

**Targets:** Planning Document Migrator + Phase Checkpoint Manager  
**Total Lines:** 699 lines (368 + 331)  
**Expected Reduction:** ~230 lines (33% average)  
**Estimated Time:** 2.5-3 hours  
**Risk:** Low

**Rationale:**
- Skip Session Completion to avoid quality pipeline complexity
- Focus on simpler file-based utilities
- Lower risk if time-constrained
- Misses high-value TDD quality gate

---

### Option C: 4 Orchestrators - AGGRESSIVE

**Targets:** Session Completion + Planning + Phase Checkpoint + Onboarding Acknowledgment  
**Total Lines:** ~1,590 lines (add 300-line target)  
**Expected Reduction:** ~530 lines (33% average)  
**Estimated Time:** 5.5-6 hours  
**Risk:** High

**Rationale:**
- Add smaller 4th orchestrator for maximum throughput
- Higher risk of fatigue/errors with 4 migrations
- May exceed single-session capacity
- Not recommended based on Sprint 5 lessons (quality > quantity)

---

## 📋 Migration Strategy (Option A)

### Task 17: Session Completion Migration (591 → ~370 lines)

**Investigation Phase (40 min):**
- Read full structure (lines 1-592)
- Map 22 SKULL rules from brain-protection-rules.yaml
- Identify quality enforcement pipeline (CodeCleanupValidator, LintIntegration, ProductionReadinessChecklist)
- Review multi-framework test execution (_is_dotnet_project, _is_python_project, _is_javascript_project)
- Identify workflow overhead (template loading, document organization)

**Implementation (80 min):**
```
src/operations/modules/validation/session_utility.py

Core operations:
1. run_test_suite(project_path, framework) → Dict
   - Auto-detect framework (dotnet/python/javascript)
   - Execute tests with framework-specific runner
   - Parse results (total/passed/failed/duration)

2. compare_metrics(metrics_before, metrics_after) → Dict
   - Calculate improvements (coverage↑, quality↑)
   - Detect regressions (coverage↓, complexity↑)
   - Return categorized comparison (improved/maintained/regressed)

3. generate_diff_summary(start_commit, end_commit) → Dict
   - Git diff --stat output parsing
   - Extract files_changed, insertions, deletions
   - Return file-level changes

4. validate_skull_rules(rules_path) → Dict
   - Load brain-protection-rules.yaml
   - Iterate 22 rules (simplified validation)
   - Return passed/failed counts

5. check_code_quality(project_path, enable_enforcement) → Dict
   - Run CodeCleanupValidator (debug/print detection)
   - Run LintIntegration (Pylint violations)
   - Run ProductionReadinessChecklist (blocking issues)
   - Return blocking issues list

6. generate_completion_report(session_data, output_path) → str
   - Inline markdown generation (no template)
   - Sections: tests, metrics, diff, skull, quality
   - Return report path

7. complete_session(session_id, start_commit, metrics_before, metrics_after, enable_quality) → Dict
   - Orchestrate all 6 operations above
   - Determine overall success (tests pass + skull pass + no regressions)
   - Generate report with auto-organization
   - Return completion result

Simplifications:
- Direct subprocess commands (remove _run_command abstraction)
- Inline markdown generation (remove template engine)
- Module-level quality validators (initialize once)
- Simplified SKULL validation (load YAML, iterate without orchestration)
- Direct framework detection (remove class methods)
```

**Testing (20 min):**
- Test framework detection: CORTEX project (Python) → verify pytest execution
- Test metrics comparison: Before {coverage: 80} After {coverage: 85} → verify "improved"
- Test diff summary: Last 2 commits → verify file counts
- Test SKULL validation: Load brain-protection-rules.yaml → verify 22 rules
- Test quality enforcement: Scan CORTEX → verify validators work
- Performance target: <5s for full validation (complex operation allowed longer)

**Expected Outcome:**
- 591 → 370 lines (37% reduction, 221 lines removed)
- Performance: <5s for full session validation
- Operations: 7 core utilities
- SKULL rules: All 22 preserved

---

### Task 18: Planning Document Migrator Migration (368 → ~245 lines)

**Investigation Phase (20 min):**
- Read full structure (lines 1-368)
- Map status detection regex (`**Status:** (.+)`)
- Identify backup mechanism (shutil.copytree)
- Review validation checks (file counts before/after)
- Identify workflow overhead (dry-run JSON export, complex error handling)

**Implementation (40 min):**
```
src/operations/modules/planning/migration_utility.py

Core operations:
1. migrate_documents(planning_dir, dry_run, create_backup) → Dict
   - Full migration workflow
   - Iterate files in planning_dir
   - Detect status → move to subdirectory
   - Return migration results

2. detect_status(file_path) → str
   - Read file, regex match `**Status:** (.+)`
   - Map status to directory (in-progress→active, approved→approved, completed→completed, cancelled→deprecated)
   - Default to "active" if no status found

3. backup_planning_dir(planning_dir, backup_dir) → bool
   - Create backup with timestamp
   - Use shutil.copytree
   - Return success status

4. validate_migration(planning_dir) → Dict
   - Count files in each status directory
   - Verify no orphaned files
   - Return validation results

5. organize_by_status(file_path, status) → str
   - Move file to status subdirectory (active/, approved/, completed/, deprecated/)
   - Create directory if needed
   - Return new path

Simplifications:
- Direct regex matching (remove status mapping class)
- Inline backup (remove backup orchestration)
- Simplified validation (basic file count checks)
- Module-level status directories (hardcode paths)
- Remove dry-run JSON export (boolean flag only)
```

**Testing (10 min):**
- Create test files with status frontmatter
- Run migration with dry_run=True → verify preview
- Run migration with dry_run=False → verify files moved
- Test backup creation → verify backup directory
- Performance target: <1s for 100 files

**Expected Outcome:**
- 368 → 245 lines (33% reduction, 123 lines removed)
- Performance: <1s for typical planning directory
- Operations: 5 file utilities

---

### Task 19: Phase Checkpoint Manager Migration (331 → ~220 lines)

**Investigation Phase (25 min):**
- Read full structure (lines 1-331)
- Map GitCheckpointOrchestrator integration
- Review metadata storage (.cortex/phase-checkpoints-{session_id}.json)
- Identify checkpoint creation workflow
- Identify workflow overhead (complex init, helper methods)

**Implementation (50 min):**
```
src/operations/modules/checkpoints/checkpoint_utility.py

Core operations:
1. create_checkpoint(session_id, phase, metrics, project_root) → str
   - Create git checkpoint via GitCheckpointOrchestrator
   - Store metadata to .cortex/phase-checkpoints-{session_id}.json
   - Return checkpoint_id

2. store_metadata(session_id, phase, checkpoint_id, commit_sha, metrics) → bool
   - Load existing metadata file
   - Append new checkpoint entry
   - Save updated metadata
   - Return success status

3. list_checkpoints(session_id) → List[Dict]
   - Load metadata file for session
   - Return all checkpoints

4. get_checkpoint(session_id, phase) → Optional[Dict]
   - Load metadata file
   - Find checkpoint for specific phase
   - Return checkpoint data or None

5. create_pre_work_checkpoint(session_id, operation, project_root) → str
   - Special checkpoint for pre-work baseline
   - Call create_checkpoint with phase="pre-work"
   - Return checkpoint_id

Simplifications:
- Direct GitCheckpointOrchestrator calls (remove init abstraction)
- Simplified metadata structure (remove optional fields)
- Inline JSON operations (remove helper methods)
- Module-level checkpoint directory (.cortex/)
- Remove complex listing filters
```

**Testing (15 min):**
- Create checkpoint → verify .cortex/ file created
- Store metadata → verify JSON structure
- List checkpoints → verify all returned
- Get specific checkpoint → verify retrieval
- Performance target: <2s for checkpoint creation + storage

**Expected Outcome:**
- 331 → 220 lines (34% reduction, 111 lines removed)
- Performance: <2s for checkpoint operations
- Operations: 5 checkpoint utilities

---

### Task 20: Sprint 6 Validation & Reporting (30 min)

**System Validation:**
- Count orchestrators: Should be 18 (down from 21)
- Run system alignment: `python3 -m src.operations.align`
- Verify 8/8 checks passing
- Performance check: All utilities meeting targets

**Git Operations:**
- Push all commits to origin
- Verify branch sync (CORTEX-3.0)

**Completion Report:**
```
cortex-brain/documents/reports/sprint-6-completion-report.md

Sections:
- Sprint 6 Summary (3 migrations, 455 lines removed)
- Task Summaries (17, 18, 19 with metrics)
- Performance Metrics (execution times, reduction %)
- Lessons Learned (SKULL preservation, quality pipeline integration)
- Cumulative Progress (17 migrations, ~7,258 lines removed, 18 orchestrators)
- Sprint 7 Recommendations (next 3 targets)
```

---

## 📊 Expected Sprint 6 Outcomes

### Code Reduction

| Orchestrator | Before | After | Reduction | % |
|-------------|--------|-------|-----------|---|
| Session Completion | 591 | 370 | 221 | 37% |
| Planning Document Migrator | 368 | 245 | 123 | 33% |
| Phase Checkpoint Manager | 331 | 220 | 111 | 34% |
| **TOTAL** | **1,290** | **835** | **455** | **35%** |

### Performance Targets

| Operation | Target | Expected | Improvement |
|-----------|--------|----------|-------------|
| Session validation (full) | <5s | 4s | Acceptable |
| Planning migration (100 files) | <1s | 0.8s | 1.25x faster |
| Checkpoint creation | <2s | 1.5s | 1.33x faster |

### System Impact

- **Orchestrators:** 21 → 18 (40% reduction from Sprint 1 start)
- **Cumulative code removed:** ~7,258 lines (6,803 + 455)
- **Migrations completed:** 17 total (2+3+3+3+3+3)
- **System health:** Expected 8/8 alignment checks passing

---

## ⚠️ Risk Assessment

### Session Completion Risks

- **22 SKULL rules preservation:** Must maintain all rule validation logic
- **Mitigation:** Copy SKULL rules YAML parsing exactly, test all 22 rules
- **Impact:** High (SKULL rules are brain protection foundation)

- **Quality enforcement pipeline:** CodeCleanupValidator, LintIntegration, ProductionReadinessChecklist dependencies
- **Mitigation:** Module-level initialization, test validators independently
- **Impact:** Moderate (quality checks must not regress)

- **Multi-framework test execution:** Python/dotnet/JS test runners
- **Mitigation:** Test with CORTEX (Python) primary, document other frameworks
- **Impact:** Low (single framework sufficient for testing)

### Planning Document Migrator Risks

- **File operations safety:** Backup before migration, dry-run mode
- **Mitigation:** Test dry-run first, verify backup creation
- **Impact:** Low (file operations well-understood)

- **Status regex parsing:** Frontmatter detection
- **Mitigation:** Test with real planning documents
- **Impact:** Low (regex pattern simple, fallback to "active")

### Phase Checkpoint Manager Risks

- **GitCheckpointOrchestrator integration:** Dependency on existing orchestrator
- **Mitigation:** Direct calls to GitCheckpointOrchestrator, no abstraction changes
- **Impact:** Low (integration pattern clear)

- **Metadata file corruption:** JSON parsing errors
- **Mitigation:** Try/except blocks, graceful degradation
- **Impact:** Low (metadata files easily regenerated)

### General Risks

- **Session duration:** 4-5 hours estimated, may extend to 5.5 hours
- **Mitigation:** Take breaks between tasks, maintain focus
- **Fatigue risk:** Moderate (Session Completion is complex)
- **Mitigation:** Complete Session Completion first when fresh

---

## 🎯 Success Validation

**Automated Checks:**
- ✅ System alignment: `python3 -m src.operations.align` (8/8 passing)
- ✅ Orchestrator count: `ls src/orchestrators/*.py | wc -l` (18 expected)
- ✅ Git sync: `git status` (branch synced with origin)

**Manual Validation:**
- ✅ Session utility: Run full validation on CORTEX → verify report
- ✅ Planning utility: Migrate test documents → verify organization
- ✅ Checkpoint utility: Create checkpoint → verify .cortex/ metadata
- ✅ Performance: All operations within targets

**Documentation:**
- ✅ Sprint 6 completion report created
- ✅ All commits pushed with descriptive messages
- ✅ System health documented (18 orchestrators, 8/8 checks)

---

## 📅 Sprint 6 Timeline (Option A)

**Total Estimated Time:** 4-5 hours

| Task | Activity | Duration | Cumulative |
|------|----------|----------|------------|
| 17 | Session Completion investigation | 40 min | 0:40 |
| 17 | Session Completion implementation | 80 min | 2:00 |
| 17 | Session Completion testing | 20 min | 2:20 |
| 18 | Planning Migrator investigation | 20 min | 2:40 |
| 18 | Planning Migrator implementation | 40 min | 3:20 |
| 18 | Planning Migrator testing | 10 min | 3:30 |
| 19 | Checkpoint Manager investigation | 25 min | 3:55 |
| 19 | Checkpoint Manager implementation | 50 min | 4:45 |
| 19 | Checkpoint Manager testing | 15 min | 5:00 |
| 20 | Sprint 6 validation & reporting | 30 min | 5:30 |

**Buffer:** 15-20 minutes for unexpected issues

---

## 🚀 Sprint 7 Preview

**Remaining High-Value Targets (after Sprint 6):**
- Swagger Entry Point (large, ~2,000 lines) - API documentation
- Setup EPM (large, ~1,500 lines) - Initial setup
- Upgrade Orchestrator (large, ~1,400 lines) - System upgrade
- Master Setup (moderate, ~900 lines) - Configuration
- UX Enhancement (moderate, ~800 lines) - User experience

**Estimated Remaining Work:**
- 2-3 more sprints to complete CORTEX 3.0 migration
- ~18 orchestrators remaining after Sprint 6
- Target: <15 orchestrators by Sprint 8 completion

---

## 🎯 Recommendation

**SELECT OPTION A** - Balanced 3-orchestrator approach

**Reasons:**
1. **High value:** Session Completion is critical TDD quality gate (22 SKULL rules)
2. **Natural grouping:** All three are TDD workflow utilities (validation, planning, checkpoints)
3. **Manageable scope:** 4-5 hours aligns with proven sprint pattern (Sprints 1-5)
4. **Risk balance:** 1 complex (Session) + 2 moderate (Planning, Checkpoint)
5. **Momentum:** Sprint 5 showed conservative approach works (quality > quantity)
6. **Synergy:** Session validation + planning organization + phase checkpoints = complete TDD workflow support

**Expected Sprint 6 Achievement:**
- ✅ 455 lines removed (35% reduction)
- ✅ 3 orchestrators migrated (18 remaining)
- ✅ All operations meeting performance targets
- ✅ System alignment passing (8/8)
- ✅ Zero test failures
- ✅ 22 SKULL rules preserved

---

**Ready to proceed with Option A, B, or C?**
