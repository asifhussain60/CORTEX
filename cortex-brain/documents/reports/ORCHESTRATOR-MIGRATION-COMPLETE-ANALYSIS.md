# Orchestrator Migration: Complete Analysis

**Author:** Asif Hussain  
**Date:** December 2, 2025  
**Status:** 📋 ANALYSIS COMPLETE  
**Purpose:** Identify all orchestrators requiring conversion to fast utilities

---

## Executive Summary

Analyzed all 23 orchestrators in CORTEX to determine which require user-facing utility conversion. **CRITICAL FINDING:** Commit, Planning, and TDD orchestrators are **core TDD Mastery features** documented in .github/prompts/modules/. These are THE defining features users interact with constantly and require HIGH priority optimization for production release.

**Orchestrator Categorization:**
- **USER-FACING (18):** feedback, commit, planning, tdd, git_checkpoint, rollback, ado_work_item, swagger_entry_point, code_review, ux_enhancement, lint_validation, realignment, application_health, rca, onboarding, onboarding_acknowledgment
- **DUAL-CONTEXT (3):** align, optimize, healthcheck (ADMIN for CORTEX maintenance, USER for application analysis)
- **ADMIN-ONLY (5):** deploy, master_setup, setup_epm, upgrade, session_completion, brain_init, unified_entry_point

**Recommendation:** Prioritize USER orchestrators (Phases 5-8: commit, planning, tdd, git_checkpoint, rollback, upgrade). All ADMIN orchestrators kept as-is (thoroughness > speed).

---

## Quick Reference: All Orchestrators by Category

### 🔵 USER-FACING (18 Total)

| # | Orchestrator | Status | Performance | Priority | Context |
|---|-------------|--------|-------------|----------|----------|
| 1 | feedback | ✅ Optimized (agent-based) | <1s | Complete | USER apps |
| 2 | commit | ⚠️ Needs profiling | Unknown | 🔥 Critical | USER apps |
| 3 | planning | ⚠️ Needs profiling | Unknown | 🔥 Critical | USER apps |
| 4 | tdd | ⚠️ Needs profiling | Unknown | 🔥 Critical | USER apps |
| 5 | git_checkpoint | ⚠️ Needs profiling | Unknown | High | USER apps |
| 6 | rollback | ⚠️ Needs profiling | Unknown | High | USER apps |
| 7 | upgrade | ⚠️ Needs profiling | Unknown | Medium | CORTEX itself |
| 8 | ado_work_item | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 9 | swagger_entry_point | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 10 | code_review | ⚠️ Needs profiling | Unknown | High | USER apps |
| 11 | ux_enhancement | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 12 | lint_validation | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 13 | realignment | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 14 | application_health | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 15 | rca | ⚠️ Needs profiling | Unknown | Medium | USER apps |
| 16 | onboarding | ✅ Keep as-is | Unknown | Low | One-time |
| 17 | onboarding_acknowledgment | ✅ Keep as-is | Unknown | Low | One-time |
| 18 | align | ⚠️ DUAL | 0.76s | High | CORTEX + USER |
| 19 | optimize | ⚠️ DUAL | 1.09s | High | CORTEX + USER |
| 20 | healthcheck | ⚠️ DUAL | 0.95s | High | CORTEX + USER |

### 🔴 ADMIN-ONLY (5 Total)

| # | Orchestrator | Size | Purpose | Status |
|---|-------------|------|---------|--------|
| 1 | deploy | 500+ lines | ADMIN - Publish CORTEX to cortex-publish | ✅ Keep as-is (18.68s) |
| 2 | master_setup | 28KB | ADMIN - Complete CORTEX setup | ✅ Keep as-is |
| 3 | setup_epm | 44KB | ADMIN - Entry Point Module setup | ✅ Keep as-is |
| 4 | session_completion | 22KB | ADMIN - Session cleanup | ✅ Keep as-is |
| 5 | brain_init | 19KB | ADMIN - Brain initialization | ✅ Keep as-is |
| 6 | unified_entry_point | 18KB | ADMIN - Entry point routing | ✅ Keep as-is |

---

## Orchestrator Inventory (23 Total)

---

## 🔵 USER-FACING ORCHESTRATORS (18 Total + 3 Dual-Context)

**These orchestrators analyze and improve USER applications. Application improvement orchestrators MUST be optimized and enforced by deploy gates.**

### Category 1: Already Optimized (Phases 1-4) ✅

| Orchestrator | Size | Status | Performance |
|-------------|------|--------|-------------|
| align | - | ✅ USER - Replaced with align_utility.py | 0.76s |
| healthcheck | - | ✅ USER - Replaced with healthcheck_utility.py | 0.95s |
| optimize | 901 lines | ✅ USER - Routing fix (skip SKULL tests) | 1.09s |

---

### Category 2: TDD Mastery Features (CRITICAL) 🔥

**These orchestrators are THE core TDD Mastery workflow documented in .github/prompts/modules/. Users interact with these constantly.**

#### Phase 5: commit_orchestrator.py 🔥 CRITICAL - USER
- **Size:** 16KB (449 lines)
- **Purpose:** USER - Git checkpoint creation during TDD cycle (RED→GREEN→REFACTOR)
- **User Commands:** `create checkpoint`, `git checkpoint`, `commit phase`, `rollback to checkpoint`
- **Guide:** .github/prompts/modules/git-checkpoint-orchestrator-guide.md (811 lines)
- **TDD Integration:** SKULL Rule #8 enforcement, automated phase commits with metadata
- **Features:**
  - Pre-flight validation (dirty state, untracked files)
  - Stash management (auto-stash uncommitted changes)
  - Phase completion commits with rich metadata (session ID, phase, metrics)
  - Rollback capability (restore to any checkpoint)
  - Branch preservation
- **Performance:** Unknown - needs profiling
- **Target:** <3s for checkpoint creation (developers expect instant commits)
- **Dependencies:** GitCheckpointOrchestrator
- **Recommendation:** 🔥 CRITICAL - Profile immediately. If >3s, MUST optimize

#### Phase 6: planning_orchestrator.py 🔥 CRITICAL - USER
- **Size:** 112KB (largest orchestrator - potential code duplication)
- **Purpose:** USER - Interactive feature planning with DoR/DoD validation (Planning System 2.0)
- **User Commands:** `plan [feature]`, `plan ado`, `approve plan`, `resume plan [name]`
- **Guide:** .github/prompts/modules/planning-orchestrator-guide.md (1133 lines)
- **TDD Integration:** Zero-ambiguity requirements before TDD cycle, Vision API screenshot analysis
- **Features:**
  - Vision API integration (screenshot → requirements extraction)
  - DoR/DoD validation (Definition of Ready/Done)
  - ADO work item integration
  - File-based planning (persistent .md files, git-trackable)
  - OWASP security review
  - Unified planning core (ADO, Feature, Vision planning share 80% code)
- **Performance:** Unknown - likely slow due to size (112KB unusual)
- **Target:** <5s without Vision API, <15s with Vision API
- **Dependencies:** Vision API, ADO client, file system operations
- **Recommendation:** 🔥 CRITICAL - Profile immediately. Check for code duplication (112KB red flag)

#### Phase 7: tdd_orchestrator.py 🔥 HIGHEST PRIORITY - USER
- **Size:** 23KB
- **Purpose:** USER - THE core TDD Mastery workflow automation (RED→GREEN→REFACTOR)
- **User Commands:** `start tdd`, `run tests`, `suggest refactorings`, `tdd status`
- **Guide:** .github/prompts/modules/tdd-mastery-guide.md (363 lines)
- **TDD Integration:** THE defining CORTEX feature
- **Features:**
  - State machine (IDLE → RED → GREEN → REFACTOR → COMPLETE)
  - Terminal integration (auto-detect test execution)
  - Auto-debug on RED phase failures
  - Performance-based refactoring (timing data analysis)
  - Multi-language support (Python, JS, TS, C# with AST parsing)
  - Test location isolation (user repo vs CORTEX)
  - Git checkpoint integration (auto-commit each phase)
  - Vision API auto-scan (screenshot → UI element extraction)
  - Code smell detection (11 types including performance-based)
- **Performance:** Unknown - state transitions should be <2s
- **Target:** <2s for state transitions (excluding user test execution)
- **Dependencies:** Test runners (pytest/jest/xunit), debuggers, git checkpoint, Vision API
- **Recommendation:** 🔥 HIGHEST PRIORITY - THE core CORTEX feature. Must optimize immediately

#### Phase 8: feedback ✅ VERIFIED OPTIMIZED - USER
- **Size:** 10KB (289 lines)
- **Architecture:** USER - Agent-based (src/agents/feedback_agent.py)
- **Purpose:** USER - Structured bug/feature/improvement reporting
- **User Commands:** `feedback`, `report issue`
- **Features:** Anonymized data, privacy protection, GitHub Gist auto-upload
- **Performance:** <1s (agent-based, no orchestrator overhead)
- **Recommendation:** ✅ NO ACTION - Already optimized

---

### Category 3: Application Analysis & Improvement (Need Profiling) ⚠️

**These orchestrators analyze and improve USER applications - must be optimized for deploy gates.**

| Orchestrator | Size | Purpose | Status | User Commands |
|-------------|------|---------|--------|---------------|
| git_checkpoint_orchestrator | 27KB | USER - Git checkpoint management | ⚠️ Needs profiling | `create checkpoint`, `rollback to` |
| rollback_orchestrator | 15KB | USER - Rollback workflows | ⚠️ Needs profiling | `rollback to [checkpoint]` |
| ado_work_item_orchestrator | 64KB | USER - Azure DevOps work items | ⚠️ Needs profiling | `plan ado` |
| swagger_entry_point_orchestrator | 62KB | USER - SWAGGER/OpenAPI analysis | ⚠️ Needs profiling | SWAGGER complexity analysis |
| code_review_orchestrator | 38KB | USER - Pull request analysis | ⚠️ Needs profiling | `code review`, `review pr` |
| ux_enhancement_orchestrator | 25KB | USER - UX improvement analysis | ⚠️ Needs profiling | `ux enhancement` |
| lint_validation_orchestrator | 16KB | USER - Code linting/validation | ⚠️ Needs profiling | Integrated with TDD |
| realignment_orchestrator | 14KB | USER - System realignment | ⚠️ Needs profiling | `align` (system alignment) |
| application_health_orchestrator | 10KB | USER - Application health dashboard | ⚠️ Needs profiling | `show health dashboard`, `onboard application` |
| rca_orchestrator | 42KB | USER - Root cause analysis | ⚠️ Needs profiling | Interactive RCA with 5 Whys |
| onboarding_orchestrator | 28KB | USER - User onboarding workflow | ✅ Keep as-is | First-time 3-question onboarding |
| onboarding_acknowledgment_orchestrator | 11KB | USER - Onboarding acknowledgment | ✅ Keep as-is | Part of onboarding flow |

### Category 4: Dual-Context Orchestrators (CORTEX + USER) 🔄

**These orchestrators work on BOTH CORTEX maintenance AND user application analysis.**

| Orchestrator | Size | CORTEX Context | USER Context | Status |
|-------------|------|----------------|--------------|--------|
| align (realignment_orchestrator) | 14KB | ADMIN - Align CORTEX system | USER - Align user application | ✅ Optimized (utility) |
| optimize | 901 lines | ADMIN - Clean CORTEX brain DBs | USER - Optimize user application | ✅ Optimized (routing fix) |
| healthcheck | Unknown | ADMIN - Check CORTEX system health | USER - Check application health | ✅ Optimized (utility) |

---

## 🔴 ADMIN-ONLY ORCHESTRATORS (6 Total)

**These orchestrators maintain CORTEX itself. Thoroughness > speed.**

### Category 5: CORTEX Maintenance Operations ✅

| Orchestrator | Size | Purpose | Recommendation |
|-------------|------|---------|----------------|
| deploy_orchestrator | 500+ lines | ADMIN - Deploy CORTEX to cortex-publish branch | ✅ Admin-only (18.68s acceptable) |
| master_setup_orchestrator | 28KB | ADMIN - Complete CORTEX setup workflow | ✅ Admin-only |
| setup_epm_orchestrator | 44KB | ADMIN - Entry Point Module setup | ✅ Admin-only |
| upgrade_orchestrator | Unknown | ADMIN - Upgrade CORTEX installation | ✅ Admin-only (safety-critical) |
| session_completion_orchestrator | 22KB | ADMIN - Session completion tasks | ✅ Admin-only (end-of-session) |
| brain_init_orchestrator | 19KB | ADMIN - Brain initialization | ✅ Admin-only (startup) |
| unified_entry_point_orchestrator | 18KB | ADMIN - Entry point routing | ✅ Admin-only (routing) |

---

### Category 5: Supporting Modules (Not Orchestrators) ✅

**These are helper classes, not orchestrators:**

| Module | Size | Purpose | Recommendation |
|--------|------|---------|----------------|
| phase8_operation_handler | - | Phase 8 operation routing | ✅ Keep as-is |
| phase_checkpoint_manager | - | Checkpoint management | ✅ Keep as-is |
| base_incremental_orchestrator | - | Base class for incremental work | ✅ Keep as-is |
| dashboard_generator | - | Dashboard generation | ✅ Keep as-is |
| analysis_engine | - | Analysis utilities | ✅ Keep as-is |
| metrics_tracker | - | Metrics collection | ✅ Keep as-is |
| cleanup_strategy | - | Cleanup utilities | ✅ Keep as-is |
| pr_context_builder | - | Pull request context | ✅ Keep as-is |
| planning_document_migrator | - | Planning doc migration | ✅ Keep as-is |
| ado_client | - | ADO API client | ✅ Keep as-is |
| rollback_command_parser | - | Command parsing | ✅ Keep as-is |

---

## 📊 Complete Orchestrator Summary

### USER-FACING (18 Total)
✅ **Optimized (1):** feedback (agent-based)  
🔥 **Critical TDD (3):** commit, planning, tdd  
⚠️ **Application Analysis (11):** git_checkpoint, rollback, ado_work_item, swagger_entry_point, code_review, ux_enhancement, lint_validation, realignment, application_health, rca  
✅ **Keep As-Is (2):** onboarding, onboarding_acknowledgment (one-time)  
🔄 **Dual-Context (3):** align, optimize, healthcheck (ADMIN for CORTEX + USER for applications)

### ADMIN-ONLY (6 Total)
✅ **CORTEX Maintenance:** deploy, master_setup, setup_epm, upgrade, session_completion, brain_init, unified_entry_point

### SUPPORTING MODULES (12 Total)
✅ **Helper classes** - not orchestrators, no action needed

---

## Recommended Migration Plan Extension

### Phases 1-3: ✅ COMPLETE
- Phase 1: align (0.76s, 26x faster)
- Phase 2: healthcheck (0.95s, 11x faster)
- Phase 3: optimize (1.09s, 28x faster)

### Phase 4: deploy_orchestrator ⚠️ ADMIN-ONLY

**Current Status:** 18.68s (dry-run), ~30s (full deployment)
**Category:** ADMIN-ONLY
**Decision:** Keep as-is (admin publishing to cortex-publish branch, safety-critical)

**Note:** This is distinct from upgrade_orchestrator (user upgrades local installation)

### Phase 5: commit_orchestrator 🔥 CRITICAL - USER TDD Mastery

**Priority:** 🔥 CRITICAL (USER - git checkpoint during TDD cycle)

**Investigation Steps:**
1. Profile checkpoint creation during TDD workflow (RED, GREEN, REFACTOR phases)
2. Measure: stash management, commit with metadata, rollback capability
3. Target: <3s for checkpoint creation
4. Decision:
   - **If <3s:** Keep as-is but verify user experience
   - **If 3-5s:** Create commit_utility.py (fast checkpoint creation)
   - **If >5s:** MUST optimize - TDD workflow requires instant git operations

**Expected Performance:**
- Stash uncommitted changes: <0.5s
- Commit with metadata: <1s
- Checkpoint tracking: <0.5s
- **Total estimated:** 2-3s (acceptable)

**Recommendation:** 🔥 CRITICAL - Profile immediately. Git checkpoints are core TDD Mastery feature.

---

### Phase 6: planning_orchestrator 🔥 CRITICAL - USER TDD Mastery

**Priority:** 🔥 CRITICAL (USER - feature planning before TDD cycle)

**Investigation Steps:**
1. ✅ Verify Planning System 2.0 guide exists (1133 lines in .github/prompts/modules/)
2. Profile planning workflow: With Vision API vs without
3. Identify bottlenecks: Vision API (5-10s), file operations, DoR/DoD validation, ADO calls
4. **CRITICAL:** Check for code duplication (112KB is red flag - largest orchestrator)
5. Decision:
   - **Vision API slow:** Create dual-track (fast without Vision, full with Vision)
   - **Code duplication found:** Refactor before creating utility
   - **Target:** <5s without Vision API, <15s with Vision API

**Expected Performance:**
- File-based planning: <2s
- DoR/DoD validation: <1s
- Vision API (screenshot analysis): 5-10s (slow)
- **Total:** 3-15s depending on features used

**Recommendation:** ⚠️ Profile first. May need dual-track (fast planning without Vision API, comprehensive with Vision API).

---

### Phase 7: tdd_orchestrator ⚠️ USER - NEEDS PROFILING

**Priority:** MEDIUM-HIGH (USER - developers use TDD frequently)

**Investigation Steps:**
1. Profile TDD workflow execution time
2. Identify bottlenecks (test execution, debug session startup, refactoring suggestions)
3. Decision:
   - **If <5s:** Keep as-is
   - **If >5s:** Create tdd_utility.py (simplified workflow without auto-debug)

**Expected Performance:**
- RED phase validation: <1s
- Test execution: Variable (depends on test suite size)
- Auto-debug: 5-10s (slow)
- **Total:** 1-15s depending on test suite

**Recommendation:** ⚠️ Profile first. TDD should be fast for developer flow. Consider skipping auto-debug for fast path.

---

### Phase 8: upgrade_orchestrator ⚠️ USER - NEEDS PROFILING

**Priority:** LOW-MEDIUM (USER - users upgrade occasionally)

**Investigation Steps:**
1. Profile upgrade workflow execution time
2. Identify bottlenecks (file operations, database migrations, git operations)
3. Decision:
   - **If <10s:** Keep as-is (upgrade should be safe, not fast)
   - **If >10s:** Optimize database migrations, file operations

**Expected Performance:**
- Brain backup: 1-2s
- File operations: 2-3s
- Database migrations: 3-5s
- Git operations: 1-2s
- **Total:** 7-12s (acceptable for upgrade)

**Recommendation:** ⏳ Low priority. Upgrade should prioritize safety over speed. Profile only if users complain.

---

### Phase 9-14: Onboarding/Session (ADMIN - LOW PRIORITY) ⏳

**Not recommended for migration:**
- Onboarding (ADMIN - one-time operation)
- Session completion (ADMIN - end-of-session, not time-sensitive)
- Brain initialization (ADMIN - startup, acceptable delay)
- Application health (ADMIN - similar to healthcheck utility)

---

## Migration Decision Matrix

**Use this matrix to decide if orchestrator needs utility conversion:**

| Factor | Create Utility | Keep Orchestrator |
|--------|---------------|-------------------|
| **User-facing?** | ✅ Yes | ❌ No (admin-only) |
| **Execution time** | ✅ >5s | ❌ <5s |
| **Usage frequency** | ✅ Daily/hourly | ❌ Rare (setup, upgrade) |
| **Fast path exists?** | ❌ No | ✅ Yes (use routing fix) |
| **Complex dependencies?** | ✅ Yes (10+ modules) | ❌ No (<5 modules) |
| **Safety-critical?** | ❌ No | ✅ Yes (deployment, upgrade) |
| **Performance complaints?** | ✅ Yes | ❌ No |

**Examples:**
- **commit:** USER app, unknown time, frequent use → ⚠️ Profile first
- **planning:** USER app, likely >5s (112KB), frequent use → ⚠️ Profile first
- **tdd:** USER app, unknown time, frequent use → ⚠️ Profile first
- **code_review:** USER app, 2-5 min, frequent use → ⚠️ Profile first
- **lint_validation:** USER app, unknown time, frequent use → ⚠️ Profile first
- **application_health:** USER app, analyzes application → ⚠️ Profile first (deploy gate)
- **rca:** USER app, root cause analysis → ⚠️ Profile first (deploy gate)
- **ux_enhancement:** USER app, UX analysis → ⚠️ Profile first (deploy gate)
- **git_checkpoint:** USER app, unknown time, frequent use → ⚠️ Profile first
- **rollback:** USER app, unknown time, occasional use → ⚠️ Profile first
- **ado_work_item:** USER app, unknown time, frequent use → ⚠️ Profile first
- **swagger_entry_point:** USER app, planning use → ⚠️ Profile first
- **realignment:** USER app, occasional use → ⚠️ Profile first
- **onboarding:** USER, one-time use → ✅ Keep as-is
- **onboarding_acknowledgment:** USER, one-time use → ✅ Keep as-is
- **align:** DUAL (CORTEX + USER app) → ✅ Already optimized (utility)
- **optimize:** DUAL (CORTEX + USER app) → ✅ Already optimized (routing)
- **healthcheck:** DUAL (CORTEX + USER app) → ✅ Already optimized (utility)
- **upgrade:** ADMIN (CORTEX upgrade), safety-critical → ✅ Keep as-is
- **deploy:** ADMIN (CORTEX publish), safety-critical → ✅ Keep as-is

---

## Profiling Plan

### Phase 5: commit_orchestrator
```bash
# Profile full commit workflow
$ Measure-Command { 
    python -c "from src.orchestrators.commit_orchestrator import CommitOrchestrator; from pathlib import Path; co = CommitOrchestrator(Path.cwd()); result = co.execute(auto_add_untracked=False, rebase=False)" 
} | Select-Object TotalSeconds

# Profile individual steps
# 1. Pre-flight check
# 2. Untracked file scan
# 3. Pull from origin
# 4. Push to origin
# 5. Checkpoint creation
```

### Phase 6: planning_orchestrator
```bash
# Profile planning workflow
$ Measure-Command { 
    python -c "from src.orchestrators.planning_orchestrator import PlanningOrchestrator; from pathlib import Path; po = PlanningOrchestrator(Path.cwd()); result = po.create_plan('test feature')" 
} | Select-Object TotalSeconds

# Check for existing utilities
$ ls .github/prompts/modules/planning*
```

### Phase 7: tdd_orchestrator
```bash
# Profile TDD workflow
$ Measure-Command { 
    python -c "from src.orchestrators.tdd_orchestrator import TDDOrchestrator; from pathlib import Path; tdd = TDDOrchestrator(Path.cwd()); result = tdd.start_red_phase()" 
} | Select-Object TotalSeconds
```

### Phase 8: upgrade_orchestrator
```bash
# Profile upgrade workflow (dry-run)
$ Measure-Command { 
    python -c "from src.orchestrators.upgrade_orchestrator import UpgradeOrchestrator; from pathlib import Path; uo = UpgradeOrchestrator(Path.cwd()); result = uo.check_for_updates()" 
} | Select-Object TotalSeconds
```

---

## Success Criteria (Extended)

### Phase 5-8 Targets

| Phase | Orchestrator | Target | Priority |
|-------|-------------|--------|----------|
| Phase 5 | commit | <5s | HIGH (if slow) |
| Phase 6 | planning | <10s (fast path), <30s (Vision API) | HIGH |
| Phase 7 | tdd | <5s (fast path), <15s (auto-debug) | MEDIUM |
| Phase 8 | upgrade | <15s | LOW |

### Overall Migration Goals

- ✅ All user-facing commands <5s (or dual-track if validation required)
- ✅ Admin commands prioritize thoroughness over speed
- ✅ Zero dependencies for utilities (stdlib only)
- ✅ Dual-track pattern for safety-critical operations
- ✅ Clear documentation of when to use utility vs orchestrator

---

## Recommendations

### Immediate Actions (Phase 5-7 Profiling)

1. **Profile commit_orchestrator:** Measure full workflow execution time
2. **Profile planning_orchestrator:** Check for existing utilities in prompts/modules/
3. **Profile tdd_orchestrator:** Measure RED phase, test execution, auto-debug
4. **Decision:** Create utilities only if >5s and frequent user complaints

### Optional Actions (Phase 8+)

5. **Profile upgrade_orchestrator:** Measure upgrade workflow (if user complaints)
6. **Skip onboarding/session:** Low priority (rare use or acceptable performance)

### Documentation Updates

7. **Update migration plan:** Add Phases 5-9 with profiling results
8. **Create decision matrix:** Document when to create utility vs keep orchestrator
9. **Update CORTEX.prompt.md:** Add new utility commands to help documentation

---

## Conclusion

**23 orchestrators analyzed:**
- ✅ **1 USER optimized** (feedback - agent-based)
- 🔥 **3 USER critical TDD** (commit, planning, tdd - need profiling)
- ⚠️ **11 USER application analysis** (git_checkpoint, rollback, ado_work_item, swagger_entry_point, code_review, ux_enhancement, lint_validation, realignment, application_health, rca - need profiling)
- ✅ **2 USER keep as-is** (onboarding, onboarding_acknowledgment - one-time operations)
- 🔄 **3 DUAL-CONTEXT** (align, optimize, healthcheck - ADMIN for CORTEX + USER for applications)
- ✅ **6 ADMIN-only** (deploy, master_setup, setup_epm, upgrade, session_completion, brain_init, unified_entry_point)
- ✅ **12 supporting modules** (not orchestrators)

**Category Breakdown:**
- **USER-FACING:** 18 orchestrators (1 optimized, 3 TDD critical, 11 application analysis, 2 one-time, 3 dual-context)
- **ADMIN-ONLY:** 6 orchestrators (CORTEX maintenance, thoroughness > speed)
- **KEY INSIGHT:** Application improvement orchestrators (analysis, design, coding, enhancements, testing) are USER-facing and must be optimized for deploy gate enforcement

**Recommendation:**
1. **Profile USER application improvement orchestrators** (commit, planning, tdd, git_checkpoint, rollback, ado_work_item, swagger_entry_point, code_review, lint_validation, realignment, application_health, rca, ux_enhancement) to determine optimization needs
2. **Prioritize high-frequency operations** (commit, planning, tdd, code_review, lint_validation)
3. **Create utilities for >5s operations** that users frequently use
4. **Enforce deploy gate validation** for all application improvement orchestrators
5. **Document decision matrix** for future orchestrator additions
6. **Monitor production usage** for performance complaints
7. **Keep all ADMIN orchestrators as-is** - CORTEX maintenance prioritizes thoroughness over speed
8. **Keep onboarding orchestrators as-is** - one-time operations, acceptable performance
9. **Dual-context orchestrators** (align, optimize, healthcheck) already optimized for both CORTEX and USER contexts

**Next Steps:** Profile application improvement orchestrators to determine deploy gate requirements.

---

## 🆕 API Enhancement Orchestrator Gap (December 2, 2025)

### Gap Analysis

CORTEX lacks a dedicated **API Enhancement Orchestrator** despite having specialized orchestrators for code review, planning, TDD, system alignment, and cleanup.

**Current API Coverage:**
- **Planning System:** Handles API feature planning with DoR/DoD validation, OWASP security review
- **Code Review:** Analyzes API endpoints during PR review, dependency-driven crawling, security scanning
- **Enhancement Workflow:** `enhance_existing` template with API discovery, TDD integration, View Discovery

**Missing Capabilities:**
- ❌ OpenAPI/Swagger spec generation from code
- ❌ API design pattern validation (RESTful principles, versioning)
- ❌ Endpoint coverage and contract validation
- ❌ API performance analysis (response times, payload sizes)
- ❌ API governance enforcement (naming conventions, error standards)

### Viability Assessment: ✅ HIGHLY VIABLE

**Arguments FOR Dedicated API Orchestrator:**
1. **API-Specific Patterns:** REST principles, versioning strategies, contract-first vs code-first, rate limiting, auth patterns
2. **Growing Complexity:** Microservices, GraphQL, gRPC, webhooks, async APIs
3. **Business Value:** Breaking changes are expensive, contract violations cause runtime failures, security vulnerabilities are high-impact
4. **Clear Scope:** Input (codebase), Output (OpenAPI spec, validation report), Operations (design validation, contract generation, breaking change detection)

**Arguments AGAINST (Trade-offs):**
1. **Overlap Risk:** Planning, Code Review, Enhancement already handle 70% of needs
2. **Maintenance Burden:** ~40-60 hours initial + 10-15 hours/quarter, multiple API types/frameworks
3. **Token Budget:** Route + controller + model crawling, OpenAPI generation (5K+ tokens)

### Strategic Recommendation: Hybrid 3.x + Full 4.0

**Option C: Hybrid Approach for 3.x (RECOMMENDED)**
- **Effort:** 20-25 hours
- **Scope:**
  1. **API Planning Template:** Specialized DoR/DoD for REST/GraphQL/gRPC
     - API design patterns validation
     - Contract-first vs code-first decision
     - Versioning strategy
     - Authentication/authorization requirements
     - Rate limiting specifications
  2. **Enhancement Workflow API Discovery:** Extend existing discovery phase
     - Route crawling (Express, FastAPI, ASP.NET, Spring)
     - Controller analysis
     - Model structure extraction
  3. **Manual OpenAPI Scaffolding:** Generate spec skeleton for manual completion
     - Basic endpoint structure
     - Request/response schemas
     - Authentication requirements
     - Error codes
- **Benefit:** End-to-end API workflow without new orchestrator, leverages existing systems
- **Limitation:** Manual spec maintenance, no automated validation

**Full API Orchestrator for 4.0:**
- **Effort:** 40-60 hours initial + ongoing maintenance
- **Architecture:** Enhancement Engine with Plugin-Based Specialization
  ```yaml
  enhancement_engine:
    core:
      discovery: UnifiedCodeCrawler (AST-based, multi-language)
      analysis: PluginArchitecture (API, UI, DB, Architecture)
      reporting: TemplateEngine (markdown, HTML, JSON)
      integration: OrchestrationBus (planning, TDD, review)
    
    api_plugin:
      capabilities:
        - OpenAPI spec generation (automated)
        - Breaking change detection
        - Contract validation
        - Performance analysis
        - Security scanning (OWASP API Top 10)
      
      supported_types:
        - REST (OpenAPI 3.1)
        - GraphQL (Schema SDL)
        - gRPC (Protocol Buffers)
        - WebSocket (AsyncAPI)
  ```

### 3.x Roadmap (Option C Implementation)

**Sprint 1 (Week 1-2): API Planning Template**
- Add `api_feature_planning` template to response-templates.yaml
- Specialized DoR checklist (design patterns, versioning, auth, rate limiting)
- Specialized DoD checklist (spec generation, contract tests, docs, breaking changes)
- Integration with PlanningOrchestrator

**Sprint 2 (Week 3-4): Enhancement Workflow API Discovery**
- Extend discovery phase with API-specific crawlers
- Route detection for Express, FastAPI, ASP.NET Core, Spring Boot
- Controller/handler analysis (parameters, return types, middleware)
- Model/schema extraction (request/response DTOs)

**Sprint 3 (Week 5-6): OpenAPI Scaffolding Generator**
- Basic spec generation (info, servers, paths skeleton)
- Request/response schema extraction from code
- Authentication requirement detection
- Manual completion workflow documentation

### Alternative Solutions Comparison

| Solution | Effort | Value | 3.x Compatible | Recommendation |
|----------|--------|-------|----------------|----------------|
| **A: API Template Enhancement** | 4-6h | HIGH | ✅ Yes | Good for quick wins |
| **B: Code Review API Plugin** | 15-20h | MEDIUM | ✅ Yes | Reactive only (PR-time) |
| **C: Hybrid (Planning + Enhancement)** | 20-25h | HIGH | ✅ Yes | ✅ **RECOMMENDED** |
| **D: Full API Orchestrator** | 40-60h | HIGH | ❌ No | Defer to 4.0 |

### Integration with Existing Orchestrators

**Planning Orchestrator:**
- Add `api_feature_planning` to template routing
- Trigger: `plan api`, `design api`, `create endpoint`
- Output: Planning file with API-specific DoR/DoD

**Enhancement Workflow:**
- Extend discovery phase with API structure crawling
- Add OpenAPI scaffolding generation step
- Integrate with TDD for contract test generation

**Code Review Orchestrator:**
- Add API-specific checks (route naming, HTTP verbs, status codes)
- Breaking change detection for existing APIs
- Response structure consistency validation

### Decision Point

**Question:** Should we implement Option C (hybrid) for 3.2.2, or defer all API work to 4.0?

**Factors to Consider:**
1. **Current project priorities:** Are API features high-demand from users?
2. **Resource availability:** 20-25 hours over 6 weeks feasible?
3. **Strategic timeline:** When is 4.0 planned (Q2 2026)?

**Recommendation:** Implement Option C in 3.2.2 if API enhancement is in top 3 user requests. Otherwise, defer to 4.0 with full Enhancement Engine architecture.

---

**Status:** 📋 ANALYSIS COMPLETE  
**Phases Identified:** 5-9 (profiling required) + API Enhancement (strategic planning)  
**Priority:** Profile commit, planning, tdd first | API Enhancement pending decision  
**Expected Time:** 4-8 hours (profiling) + 20-25 hours (Option C if approved)
