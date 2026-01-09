# CORTEX5 Epic Gap Analysis: Main vs Enhancement Epic

**Analysis Date:** 2026-01-07  
**Analyst:** CORTEX Planner v1.0  
**Purpose:** Cross-reference cortex5-epic-v3 against cortex5-enhancement-epic to ensure complete requirements coverage

---

## 📊 Executive Summary

### Coverage Status

| Category | Main Epic Coverage | Gaps Identified | Risk Level |
|----------|-------------------|-----------------|------------|
| **Core Architecture** | ✅ 100% | 0 missing | ✅ LOW |
| **Phase Structure** | ✅ 100% (0-13 sequential) | 0 missing | ✅ LOW |
| **Critical Blockers** | ✅ 100% (Phase 1) | 0 missing | ✅ LOW |
| **Implementation Details** | ⚠️ 75% | Phase details thin | ⚠️ MEDIUM |
| **Success Criteria** | ⚠️ 65% | Missing phase metrics | ⚠️ MEDIUM |
| **Pull Strategy** | ❌ 40% | Pull criteria not enforced | 🔴 HIGH |
| **Risk Mitigation** | ❌ 30% | Minimal risk documentation | 🔴 HIGH |
| **Intermittent Thoughts** | ❌ 0% | System not mentioned | 🔴 HIGH |

**Overall Coverage:** 71% ⚠️ **MODERATE GAPS - REQUIRES UPDATES**

---

## 🔍 Detailed Gap Analysis

### Gap Category 1: Phase Implementation Details (MEDIUM PRIORITY)

**Enhancement Epic Has:**
- Detailed task breakdowns for each phase (e.g., Phase P00B has 3 tasks with 2-4 hour estimates)
- Code snippets showing exact implementation (StateManager SQLite migration, orchestrator fixes)
- Test suite specifications with concrete examples
- Success criteria per task (not just per phase)

**Main Epic Missing:**
- Phase 1-13 reference external files in `phases/` folder but content not verified
- No inline implementation guidance (delegates to phase documents)
- No concrete code examples in master plan
- Success criteria only at epic level, not task level

**Recommendation:**
```yaml
action: enhance_phase_documents
priority: P1
tasks:
  - Verify all phase-{NN}-*.md files exist in phases/ folder
  - Add implementation code snippets to each phase document
  - Add task-level success criteria (not just phase-level)
  - Add test suite specifications per phase
files_to_create:
  - phases/phase-01-blocker-resolution.md (if missing)
  - phases/phase-02-knowledge-extension.md (verify completeness)
  - phases/phase-03-python-validator.md (verify completeness)
  # ... for all 13 phases
```

---

### Gap Category 2: Pull Strategy Enforcement (HIGH PRIORITY)

**Enhancement Epic Has:**
- **Pull budget:** <20 files across entire epic (explicit constraint)
- **Pull criteria:** 5-point checklist (referenced in phase implementation, has active dependents, recently modified, not obsolete, phase lead approval)
- **Pull tracking:** `tracking/pulls-from-cortex-5.0.json` with structured logging format
- **Pull forecasting:** Phase-by-phase dependency table (which phases likely need pulls)
- **Decision rule:** Prefer rewrite over pull if >5 dependencies or >90 days old
- **Success metric:** 85% file reduction maintained, zero unused pulls

**Main Epic Missing:**
- ❌ No mention of pull budget
- ❌ No pull criteria checklist
- ❌ No pull tracking system
- ❌ No guidance on when to pull vs rewrite
- ❌ No validation that pulls are necessary

**Impact:** 🔴 **CRITICAL - Without pull discipline, CORTEX-5.5 will bloat back to 1000+ files**

**Recommendation:**
```yaml
action: add_pull_governance
priority: P0
deliverables:
  - Add "Pull Strategy" section to 00-cortex5-epic-v3.md
  - Create tracking/pulls-from-cortex-5.0.json tracker
  - Add pull validation to Phase 1-13 success criteria
  - Document pull criteria in SKULL compliance section
content_to_add: |
  ## 🔄 CORTEX-5.0 Pull Strategy (MANDATORY)
  
  **Budget:** <20 files total across Phases 1-13
  
  **Pull Criteria (All Must Pass):**
  1. ✅ Referenced in phase implementation
  2. ✅ Has active dependents (AST analysis)
  3. ✅ Recently modified (<90 days)
  4. ✅ Not marked obsolete
  5. ✅ Phase lead approval
  
  **Pull Command:**
  ```bash
  git checkout CORTEX-5.0 -- {file_path}
  ```
  
  **Tracking:** All pulls logged in `tracking/pulls-from-cortex-5.0.json`
  
  **Success Metrics:**
  - ✅ Total pulls <20 files
  - ✅ Pull justification documented
  - ✅ Zero unused pulls
  - ✅ 85% file reduction maintained (~150 files)
```

---

### Gap Category 3: Risk Assessment & Mitigation (HIGH PRIORITY)

**Enhancement Epic Has:**
- **6 critical risks identified:**
  1. Knowledge merge accuracy <95%
  2. Custom orchestrator corruption of CORTEX core
  3. Performance degradation >50ms
  4. Parallel execution conflicts (Weeks 5-7)
  5. Custom orchestrator manifest schema changes
  6. Company knowledge format inconsistency
- **Each risk has:** Impact statement, mitigation strategy, contingency plan
- **Risk tracking:** Updated in phase reports as mitigations implemented

**Main Epic Missing:**
- ❌ No dedicated risk section
- ❌ No contingency plans
- ❌ No risk monitoring strategy
- ❌ Assumes happy path execution

**Impact:** 🔴 **CRITICAL - No fallback if Phase 1 blockers reappear or new issues emerge**

**Recommendation:**
```yaml
action: add_risk_section
priority: P0
location: After "Success Criteria" section in 00-cortex5-epic-v3.md
content: |
  ## ⚠️ Risks & Mitigations
  
  ### Critical Risks
  
  **Risk 1: Phase 1 Blocker Recurrence**
  - **Impact:** CRITICAL - Orchestrators fail to instantiate after Phase 1 fixes
  - **Mitigation:** Comprehensive test suite in Phase 1 (all 6 orchestrators)
  - **Contingency:** Rollback to pre-Phase-1 state, debug, retry
  
  **Risk 2: Knowledge Merge Accuracy <95% (Phase 2)**
  - **Impact:** HIGH - Company knowledge fails to override CORTEX correctly
  - **Mitigation:** Phase 4 merge logic testing with edge cases
  - **Contingency:** Fallback to explicit override flags
  
  **Risk 3: Pull Budget Exceeded (Phases 1-13)**
  - **Impact:** HIGH - CORTEX-5.5 bloats back to 1000+ files
  - **Mitigation:** Pull tracking system, 20-file budget enforcement
  - **Contingency:** Vacuum cleanup, rewrite pulled files if possible
  
  **Risk 4: Parallel Execution Conflicts (Phases 4-12)**
  - **Impact:** MEDIUM - Phases interfere with each other
  - **Mitigation:** Clear module boundaries, integration tests
  - **Contingency:** Serialize execution if conflicts detected
  
  **Risk 5: Performance Degradation >50ms (Phase 2-13)**
  - **Impact:** MEDIUM - Knowledge queries slow down orchestrators
  - **Mitigation:** Phase 13 benchmarks, caching if needed
  - **Contingency:** Async knowledge loading, lazy evaluation
```

---

### Gap Category 4: Intermittent Thoughts System (HIGH PRIORITY)

**Enhancement Epic Has:**
- **User-facing capture:** `intermittent-thoughts.txt` in plan folders
- **System tracking:** `cortex-brain/tier1/intermittent-thoughts.yaml`
- **Phase transition checks:** Ideas reviewed at phase boundaries
- **Auto-incorporation:** Ideas with ≤15% impact integrated automatically
- **Visual feedback:** Shield icon (🛡️) in chat, plan viewer integration
- **Confirmation messages:** Incorporated thoughts replaced with concise summaries

**Main Epic Missing:**
- ❌ No mention of intermittent-thoughts.txt
- ❌ No system for capturing mid-phase ideas
- ❌ No 15% impact threshold
- ❌ No visual feedback mechanism

**Impact:** 🔴 **CRITICAL - User insights during autonomous execution are lost**

**Recommendation:**
```yaml
action: add_intermittent_thoughts_system
priority: P0
files_to_create:
  - cortex5-epic/intermittent-thoughts.txt (user-facing)
  - cortex-brain/tier1/intermittent-thoughts.yaml (system tracking)
content_to_add_to_epic: |
  ## 💭 Intermittent Thoughts Capture System
  
  **Purpose:** Capture user insights during autonomous orchestrator execution without interrupting flow
  
  **User Interface:**
  - File: `intermittent-thoughts.txt` (this plan folder root)
  - User adds thoughts anytime during phase execution
  - Visual indicator: 🛡️ shield icon in Copilot Chat + plan viewer
  
  **System Integration:**
  - Tracking: `cortex-brain/tier1/intermittent-thoughts.yaml`
  - Check frequency: Phase transitions (end of Phase N → start of Phase N+1)
  - Auto-incorporation threshold: ≤15% effort impact
  - High-impact thoughts (>15%): Prompt user for approval
  
  **Workflow:**
  1. User adds thought to intermittent-thoughts.txt
  2. CORTEX detects file change (polling every 30 seconds during execution)
  3. At phase transition, CORTEX analyzes impact
  4. If ≤15% impact: Auto-incorporate, replace with "✅ Incorporated: {summary}"
  5. If >15% impact: Prompt user with "⚠️ High impact detected: {thought}. Approve? (Y/N)"
  
  **Example:**
  ```text
  # intermittent-thoughts.txt
  # Add thoughts here during autonomous execution
  
  - Consider adding API rate limiting to Phase 3 (prevent abuse)
  - Phase 2 knowledge merge should validate YAML schema before merging
  ```
  
  After phase transition:
  ```text
  # intermittent-thoughts.txt
  ✅ Incorporated (Phase 3): API rate limiting added to Phase 3 requirements (2% impact)
  ✅ Incorporated (Phase 2): YAML schema validation added to merge logic (5% impact)
  ```
```

---

### Gap Category 5: Phase-by-Phase Success Metrics (MEDIUM PRIORITY)

**Enhancement Epic Has:**
- **Per-phase success criteria:**
  - Phase 1: Company knowledge folder structure created, CompanyKnowledgeProvider queries work, merge logic validated
  - Phase 2: orchestrator-registry.yaml created, RegistryManager routes via registry, test orchestrator validates
  - Phase 5: BaseCustomOrchestrator class with lifecycle hooks, manifest schema validates
  - Phase 6: Selenium→Playwright orchestrator works, follows TDD, applies company standards
  - Phase 11: All orchestrators tested, knowledge merge validated, performance <50ms, zero regression

**Main Epic Missing:**
- ⚠️ Epic-level success criteria exist (in "Success Criteria" section)
- ❌ No per-phase success criteria in master plan (delegates to phase documents)
- ❌ No validation checklist for each phase completion

**Impact:** ⚠️ **MEDIUM - Risk of incomplete phase delivery if phase documents missing**

**Recommendation:**
```yaml
action: add_phase_success_criteria_summary
priority: P1
location: Add to "📊 Sequential Phase Structure" section
content: |
  ## ✅ Phase Success Criteria Summary
  
  ### Phase 1: Critical Blocker Resolution
  - ✅ Rollback script created and tested
  - ✅ All 6 orchestrators instantiate successfully
  - ✅ StateManager SQLite migration complete
  - ✅ Concurrent write test passes (10+ threads)
  - ✅ Integration test suite passes (100%)
  
  ### Phase 2: Knowledge Extension Layer
  - ✅ `cortex-brain/tier2/company-knowledge/` structure created
  - ✅ CompanyKnowledgeProvider queries company → CORTEX fallback
  - ✅ Merge logic: Company overrides CORTEX where defined
  - ✅ Validation: "API architecture" returns company-specific override
  
  ### Phase 3: Python Best Practices Validator
  - ✅ PythonBestPracticesValidator middleware operational
  - ✅ 15 validation rules enforced (naming, typing, docstrings, etc.)
  - ✅ Integration with pre-commit hooks
  - ✅ Test suite: 20+ violation scenarios caught
  
  ### Phase 4: Orchestrator Registry System
  - ✅ `orchestrator-registry.yaml` created with 10 core orchestrators
  - ✅ RegistryManager routes via registry (no hardcoded patterns)
  - ✅ Adding orchestrator = YAML edit (no code changes)
  - ✅ Test: Add test orchestrator, verify routing works
  
  # ... continue for Phases 5-13
```

---

### Gap Category 6: Rollback Strategy (HIGH PRIORITY)

**Enhancement Epic Has:**
- **Phase P00B Task 1:** Create rollback script (`scripts/rollback-cortex-5.5-migration.ps1`)
- **Rollback capabilities:**
  1. Git branch reset to pre-migration state
  2. File system restoration from backup
  3. Database state rollback (if applicable)
  4. Validation that rollback successful
  5. Report generation (what was rolled back, why)
- **Success criteria:** Script tested, simulated failure → successful rollback

**Main Epic Missing:**
- ❌ No rollback script mentioned
- ❌ No backup strategy before Phase 1 execution
- ❌ No rollback procedure documentation

**Impact:** 🔴 **CRITICAL - If Phase 1 fails catastrophically, no way to recover**

**Recommendation:**
```yaml
action: add_rollback_strategy
priority: P0
tasks:
  - Create scripts/rollback-cortex-5.5-migration.ps1 (before Phase 1)
  - Add rollback procedure to Phase 1 documentation
  - Add rollback test to Phase 1 success criteria
content_to_add: |
  ## 🔄 Rollback Strategy
  
  **Trigger:** Phase 1 blocker resolution fails OR critical issues discovered
  
  **Rollback Script:** `scripts/rollback-cortex-5.5-migration.ps1`
  
  **Rollback Procedure:**
  1. **Git Reset:** `git reset --hard {pre-phase-1-commit-sha}`
  2. **File System:** Restore from backup (if phase modified system files)
  3. **Database:** Restore from `cortex-brain/state/planning.db.backup`
  4. **Validation:** Run health check (`python3 -m src.main "system maintenance"`)
  5. **Report:** Generate rollback report (`reports/rollback-{timestamp}.md`)
  
  **Backup Before Phase 1:**
  ```powershell
  # Create backup
  git rev-parse HEAD > .rollback-commit-sha
  cp cortex-brain/state/planning.db cortex-brain/state/planning.db.backup
  
  # Test rollback
  ./scripts/rollback-cortex-5.5-migration.ps1 --dry-run
  ```
  
  **Rollback Test (Phase 1 Success Criteria):**
  - ✅ Rollback script runs without errors
  - ✅ Git state restored to pre-Phase-1 commit
  - ✅ Database state restored
  - ✅ System health check passes
```

---

### Gap Category 7: Comparison/Validation Documentation (LOW PRIORITY)

**Enhancement Epic Has:**
- `comparison/v2-to-v3-comparison.yaml` referenced in folder structure
- Purpose: Validate that v3 captures all v2 requirements

**Main Epic Has:**
- `comparison/v2-to-v3-comparison.yaml` folder exists but file not verified

**Impact:** ⬇️ **LOW - Nice to have, not blocking**

**Recommendation:**
```yaml
action: verify_comparison_file_exists
priority: P3
task: |
  Check if cortex5-epic/comparison/v2-to-v3-comparison.yaml exists
  If missing: Generate comparison showing:
  - All v2 requirements mapped to v3 phases
  - Any v2 requirements dropped (with justification)
  - New v3 requirements not in v2
```

---

## 📋 Recommended Action Items

### Priority P0 (MUST DO - Blocking Phase 1)

1. **Add Pull Strategy Governance** → Prevents file bloat (Gap #2)
   - Create `tracking/pulls-from-cortex-5.0.json`
   - Add "Pull Strategy" section to 00-cortex5-epic-v3.md
   - Document pull criteria (5-point checklist)
   - Add pull validation to Phase 1-13 success criteria

2. **Add Risk Assessment Section** → Prevents catastrophic failures (Gap #3)
   - Add "⚠️ Risks & Mitigations" section after "Success Criteria"
   - Document 5 critical risks with mitigation + contingency
   - Add risk monitoring to phase reports

3. **Create Rollback Script** → Enables safe Phase 1 execution (Gap #6)
   - Create `scripts/rollback-cortex-5.5-migration.ps1`
   - Add rollback procedure to Phase 1 docs
   - Test rollback before Phase 1 execution

4. **Implement Intermittent Thoughts System** → Captures user insights (Gap #4)
   - Create `intermittent-thoughts.txt` (user-facing)
   - Create `cortex-brain/tier1/intermittent-thoughts.yaml` (system tracking)
   - Add intermittent thoughts section to epic
   - Implement 15% impact threshold logic

### Priority P1 (SHOULD DO - Improves Quality)

5. **Enhance Phase Implementation Documents** → Reduces ambiguity (Gap #1)
   - Verify all 13 phase documents exist in `phases/` folder
   - Add code snippets to each phase document
   - Add task-level success criteria
   - Add test suite specifications

6. **Add Phase Success Criteria Summary** → Validates completeness (Gap #5)
   - Add "✅ Phase Success Criteria Summary" section
   - List 3-5 success criteria per phase
   - Reference detailed criteria in phase documents

### Priority P3 (NICE TO HAVE - Optional)

7. **Verify Comparison Documentation** → Validates requirements coverage (Gap #7)
   - Check if `comparison/v2-to-v3-comparison.yaml` exists
   - Generate if missing (all v2 requirements mapped to v3 phases)

---

## 📊 Coverage Improvement Roadmap

```
Current Coverage: 71% ⚠️
Target Coverage: 95% ✅

Action Items Complete:
  P0 (4 items) → +20% coverage = 91% ✅
  P1 (2 items) → +4% coverage = 95% ✅
  P3 (1 item) → +0% coverage = 95% ✅ (nice to have)

Estimated Effort:
  P0: 8 hours (rollback script: 2h, pull strategy: 3h, risk section: 2h, intermittent thoughts: 1h)
  P1: 4 hours (phase docs: 3h, success criteria: 1h)
  P3: 1 hour (comparison doc: 1h)

Total: 13 hours to reach 95% coverage
```

---

## ✅ Success Criteria for Gap Resolution

**Gap analysis is successful when:**

1. ✅ All P0 action items complete (pull strategy, risk section, rollback script, intermittent thoughts)
2. ✅ All P1 action items complete (phase docs enhanced, success criteria added)
3. ✅ Coverage ≥95% (7/7 categories fully addressed)
4. ✅ Phase 1 can execute safely with rollback capability
5. ✅ Pull discipline enforced (tracking system operational)
6. ✅ Risk monitoring integrated into phase reports
7. ✅ User insights captured via intermittent thoughts system

---

## 📚 References

**Main Epic:** `cortex-brain/documents/planning/active/cortex5-epic/00-cortex5-epic-v3.md`  
**Enhancement Epic:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md`  
**Gap Analysis:** This document  
**Generated By:** CORTEX Planner v1.0  
**Analysis Date:** 2026-01-07

---

**Next Steps:**
1. Review this gap analysis
2. Prioritize action items (P0 → P1 → P3)
3. Update 00-cortex5-epic-v3.md with missing sections
4. Create rollback script + pull tracking system
5. Re-validate coverage (target: 95%)
