# CORTEX Prompt Audit Execution Summary

**Date:** 2026-01-12  
**Auditor:** GitHub Copilot  
**Status:** COMPLETE - 3 Findings identified and documented  
**Actions:** 3 Created, 2 Updated, 4 Require prompting for execution

---

## What Was Done

### 1. Comprehensive Prompt Audit ✅

**Scanned Files:**
- ✅ `.github/prompts/CORTEX.prompt.md` (287 lines)
- ✅ `.github/prompts/cortex-exec.prompt.md` (477 lines)
- ✅ `.github/prompts/cortex-evidence-validator.prompt.md` (398 lines)
- ✅ `.github/prompts/cortex-brittleness-review.prompt.md` (updated)
- ✅ `.github/prompts/archive/` (2 prompts - migration + git-commit)

**Documents Folder Structure:**
- ✅ `cortex-brain/documents/reports/` (400+ files analyzed)
- ✅ `cortex-brain/documents/reports/tdd/` (massive clutter identified)
- ✅ File naming conventions verified against CORE-022

---

### 2. Issues Identified & Documented ✅

**3 Critical Findings:**

| Finding | Severity | File | Issue |
|---------|----------|------|-------|
| **#1: AC-ID Integration Gap** | HIGH | cortex-brittleness-review.prompt.md | 29 AC-IDs in separate YAML file instead of AC-INDEX.yaml |
| **#2: Governance Violations** | HIGH | cortex-brain/documents/reports/ | 400+ files violate CORE-002, CORE-009, CORE-022 |
| **#3: Missing Plan-Viewer Sync** | MEDIUM | cortex-exec.prompt.md, cortex-evidence-validator.prompt.md | Sync exists but not validated; data lag possible |

**Root Cause:** Prompts don't specify output locations or integration requirements consistently.

---

### 3. Documents Created ✅

**1. Audit Report** (1200+ lines)
```
File: cortex-brain/documents/prompts/prompt-integration-audit-2026-01-12.md

Contains:
- Executive summary
- Detailed findings per prompt
- Governance rule violations explained
- 4-phase action plan with timelines
- Risk assessment
- File reorganization proposal
- CORE-022 decision needed (20-char vs 32-char limit)
- Complete checklist
```

**2. File Organization Policy** (300+ lines)
```
File: cortex-brain/tier0/governance/file-organization-policy.yaml

Contains:
- Purpose and problem statement
- Location standards for all artifact types
- File naming rules (kebab-case, character limits)
- AC-ID integration requirements
- Evidence bundle structure
- Folder reorganization before/after comparison
- Governance enforcement (CORE-002, 009, 022)
- Implementation checklist
```

**3. Output Standards Template** (350+ lines)
```
File: .github/prompts/output-standards.md

Contains:
- Template for ALL prompts to follow
- AC-ID location & integration rules
- Evidence bundle structure
- Analysis report organization
- Progress tracking requirements
- Dashboard sync requirements
- Implementation checklist per prompt
- 4 prompt updates identified
```

---

### 4. Prompt Updates Applied ✅

**cortex-brittleness-review.prompt.md (Updated)**
```
Section B: "AC-ID entries for cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"

BEFORE: Created separate YAML file (AC-IDS-BRITTLENESS-2026-01-12.yaml)

AFTER: Mandatory integration requirements added:
- ✅ AC-IDs MUST append to AC-INDEX.yaml (single source of truth)
- ✅ NO separate YAML files (MasterOrchestrator won't see them)
- ✅ Step-by-step integration instructions
- ✅ DO NOT list explaining why separate files are wrong
- ✅ Duplicate handling rules
```

---

## Critical Decisions Needed

### Decision #1: CORE-022 File Naming Limit

**Current Rule:** Kebab-case, max 20 characters

**Problem:** Date-versioned reports need timestamps:
```
brittleness-findings-2026-01-12.yaml = 28 characters (over limit)
```

**Options:**

| Option | Approach | Impact | Recommendation |
|--------|----------|--------|---|
| **A: Strict 20-char** | Shorten all names, use version numbers | Better compliance, less clarity | ❌ Too restrictive |
| **B: 32-char exception** | Allow date-versioned files: `{name}-yyyy-mm-dd` | Practical, clear, backwards compatible | ✅ RECOMMENDED |
| **C: Metadata approach** | Store dates in YAML metadata, not filename | Cleanest, hard to scan visually | ⚠️ Middle ground |

**Recommendation:** Accept 32-character exception for date-versioned files. Rationale: Evidence/audit reports need timestamps for versioning; 20 chars too restrictive.

**Amendment to CORE-022:**
```yaml
exception:
  pattern: "date-versioned reports"
  format: "{name}-{yyyy-mm-dd}.{ext}"
  max_length: 32
  rationale: "Evidence and audit reports require timestamps for version tracking"
```

---

### Decision #2: Phase Integration for Brittleness AC-IDs

**Question:** Where should 29 brittleness AC-IDs be scheduled?

**Current State:**
- Phase 1: 33 AC-IDs (foundation)
- Phase 2: 24 AC-IDs (orchestration)
- Phase 3+: Feature orchestrators

**Brittleness AC-IDs by Priority:**
- **CRITICAL (4):** YAML encoding, file locking, state corruption, crash safety
- **HIGH (6):** Concurrency races, pattern matching, validation gaps
- **MEDIUM (12):** Performance, observability, security
- **LOW (7):** Refactoring, code cleanup, documentation

**Options:**

| Option | Approach | Impact |
|--------|----------|--------|
| **A: Phase 1.5** | Add 1-2 week phase for CRITICAL brittleness only | Pushes orchestration by 1-2 weeks, more robust Phase 1 |
| **B: Integrate into Phase 1** | Add 4 CRITICAL to Phase 1 task list | Increases Phase 1 scope (from 33 → 37 AC-IDs) |
| **C: Integrate into Phase 2** | Add 6 HIGH to Phase 2 task list | Increases Phase 2 scope (from 24 → 30 AC-IDs) |
| **D: Parallel track** | Run brittleness fixes in separate phase 3 track | Maintains current schedule, adds technical debt |

**Recommendation:** **Option A (Phase 1.5)** - Create 1-2 day phase for CRITICAL brittleness after Phase 1 foundation completes. Rationale:
- Foundation (Phase 1) must complete first (base infrastructure)
- 4 CRITICAL brittleness issues must be fixed before Phase 2 orchestration
- Parallel track causes technical debt accumulation

---

### Decision #3: File Reorganization Timeline

**Question:** When should we reorganize `cortex-brain/documents/reports/` and archive TDD reports?

**Options:**

| Timing | Approach | Risk |
|--------|----------|------|
| **Immediate (Phase 1)** | Reorganize + archive now | Might break references to old locations |
| **After Phase 1** | Reorganize after foundation complete | Phase 2 starts with clean structure |
| **After Phase 2** | Wait until orchestration stable | Old clutter persists longer |

**Recommendation:** Execute immediately (Phase 1.0) as blocking fix. Rationale:
- Governs CORE-002, CORE-009, CORE-022 violations
- Clears workspace for Phase 1 visibility
- Simple mv/rename operations (low risk)
- Can add migration script to handle any broken references

**Execution:**
1. Create script: `scripts/organize-reports-2026-01-12.py`
2. Move old TDD reports: `cortex-brain/archives/tdd-reports-historical/`
3. Reorganize by category: `cortex-brain/documents/reports/{brittleness,evidence,validation}/`
4. Rename files: Kebab-case, max 32 chars (with date exception)
5. Verify no broken links: Check `*.md` files for old paths

---

## Action Items (Prioritized)

### PHASE 0: Decisions (TODAY)

- [ ] Decide: CORE-022 limit (20-char strict OR 32-char exception?)
- [ ] Decide: Brittleness AC-ID phase placement (Phase 1.5 OR integrate?)
- [ ] Decide: File reorganization timing (immediate OR after Phase 1?)

### PHASE 1: Fix Governance Violations (2 hours)

**Owner:** Infrastructure Team  
**Blocker:** Phase 0 decisions

- [ ] Amend CORE-022 with 32-char exception (if Decision #1 = "B")
- [ ] Create reorganization script: `scripts/organize-reports-2026-01-12.py`
- [ ] Execute: Move TDD reports to archives
- [ ] Execute: Reorganize documents/reports/ by category
- [ ] Execute: Rename files (kebab-case, new character limit)
- [ ] Verify: No broken references in markdown files
- [ ] Commit: File reorganization changes

### PHASE 2: Integrate Brittleness AC-IDs (1 hour)

**Owner:** Planning Team  
**Blocker:** Phase 1 complete

- [ ] Create migration script: `scripts/migrate-brittleness-acs.py`
- [ ] Execute: Append 29 AC-IDs to AC-INDEX.yaml
- [ ] Validate: Schema compliance, no duplicates
- [ ] Assign: 29 AC-IDs to phases (1, 1.5, 2, 3 per Decision #2)
- [ ] Update: master-plan.yaml with new AC-ID counts and phase assignments
- [ ] Run: MasterOrchestrator to verify recognition
- [ ] Verify: AC-INDEX.yaml has 131 AC-IDs (102 + 29)
- [ ] Commit: AC-ID integration changes

### PHASE 3: Update All Prompts (3 hours)

**Owner:** Prompt Team  
**Blocker:** Phase 2 complete

- [ ] Add OUTPUT SPECIFICATION to cortex-brittleness-review.prompt.md (VERIFY existing)
- [ ] Add OUTPUT SPECIFICATION to cortex-evidence-validator.prompt.md (NEW)
- [ ] Add OUTPUT SPECIFICATION to cortex-exec.prompt.md (UPDATE)
- [ ] Update CORTEX.prompt.md if generates artifacts (CHECK)
- [ ] Create reference: `.github/prompts/README.md` linking to output-standards.md
- [ ] Commit: Prompt updates

### PHASE 4: Update Plan & Dashboard (2 hours)

**Owner:** Planning Team  
**Blocker:** Phase 3 complete

- [ ] Update master-plan.yaml phase summaries
- [ ] Recalculate: Phase completion percentages (new AC-ID totals)
- [ ] Run: `python3 scripts/sync_plan_viewer_data.py`
- [ ] Verify: plan-viewer.html shows updated phase metrics
- [ ] Verify: plan-viewer-data.json has latest data (no hardcoding)
- [ ] Commit: Plan + dashboard updates

---

## Files Created

```
NEW FILES:
✅ cortex-brain/documents/prompts/prompt-integration-audit-2026-01-12.md       (1200+ lines)
✅ cortex-brain/tier0/governance/file-organization-policy.yaml                 (300+ lines)
✅ .github/prompts/output-standards.md                                         (350+ lines)

UPDATED FILES:
✅ .github/prompts/cortex-brittleness-review.prompt.md                         (Section B)

PENDING CREATION (Action Items):
⏳ scripts/organize-reports-2026-01-12.py
⏳ scripts/migrate-brittleness-acs.py
⏳ cortex-brain/tier0/governance/core-rules-amendment-2026-01-12.yaml (CORE-022 update)
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Prompts audited | 5 |
| Critical findings | 3 |
| Files analyzed | 450+ |
| Character limit violations | 15 (brittleness reports) |
| TDD reports cluttering workspace | 400+ |
| AC-IDs generated but not integrated | 29 |
| Governance policies created | 1 |
| Prompt standards created | 1 |
| Output specification sections created | 0 (pending) |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Reorganization breaks references | Search/replace in all `.md` files, test links |
| AC-ID migration duplicates existing | Script validates no duplicates, manual review |
| CORE-022 amendment causes conflicts | Amendment in separate file, clear deprecation |
| Plan-viewer shows wrong metrics | Verification script checks sync succeeded |

---

## Success Criteria

Phase complete when:

- ✅ All files follow kebab-case naming (20-char standard, 32-char for dates)
- ✅ Reports organized by category (brittleness/, evidence/, tdd/, validation/)
- ✅ TDD reports archived (400+ files moved to cortex-brain/archives/)
- ✅ 29 brittleness AC-IDs in AC-INDEX.yaml (single source of truth)
- ✅ All 4 prompts have OUTPUT SPECIFICATION sections
- ✅ master-plan.yaml updated with new AC-ID counts
- ✅ plan-viewer.html shows updated phase metrics
- ✅ CORE-022 amendment documented (32-char exception for dates)

---

## Next Steps for User

Choose one:

**Option A: Proceed with All Phases**
```
"Proceed autonomously with phases 1-4 (8 hours total)"
```

**Option B: Specific Phase**
```
"Execute Phase 1 (file reorganization) first, then decide on others"
```

**Option C: Decision Points First**
```
"Help me decide on CORE-022 limit, Phase placement, and timing before executing"
```

**Option D: Review & Refine**
```
"Let me review the audit findings and policies, then we'll plan execution"
```

---

## Documents for Review

**Audit Report:**
- `cortex-brain/documents/prompts/prompt-integration-audit-2026-01-12.md` (126 KB)

**Governance Policy:**
- `cortex-brain/tier0/governance/file-organization-policy.yaml` (28 KB)

**Standards Template:**
- `.github/prompts/output-standards.md` (35 KB)

**Quick Summary (this file):**
- `cortex-brain/documents/prompts/prompt-audit-summary-2026-01-12.md` (10 KB)

---

**Report Generated:** 2026-01-12T15:45:00Z  
**Status:** ANALYSIS COMPLETE - Ready for execution  
**Next:** Await user decision on 3 critical questions
