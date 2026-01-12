# Prompt Integration Audit & Governance Compliance Report

**Date:** 2026-01-12  
**Auditor:** GitHub Copilot  
**Status:** FINDINGS IDENTIFIED - ACTION REQUIRED  
**Severity:** HIGH (Multiple CORE rule violations)

---

## Executive Summary

Comprehensive audit of `.github/prompts/` revealed **3 critical integration gaps** across multiple prompt files:

1. **AC-ID Generation WITHOUT Integration** → Brittleness review generates 29 AC-IDs but doesn't append to AC-INDEX.yaml
2. **File Organization Violations** → 400+ generated report files violate CORE-002, CORE-009, CORE-022 (kebab-naming)
3. **Missing Plan-Viewer Sync** → Report outputs not reflected in progress-tracker.json or plan-viewer-data.json

**Governance Rules Violated:**
- ❌ **CORE-002** (No Summary File Generation) - 400+ TDD reports in cortex-brain/documents/reports/tdd/
- ❌ **CORE-009** (Plan Files in Plan Folder) - Brittleness reports at cortex-brain/documents/reports/ root
- ❌ **CORE-022** (Kebab-Case Naming) - File names violate 20-char limit + camelCase usage

**Impact:**
- Brittleness findings invisible to governance pipeline (MasterOrchestrator doesn't read isolated YAML files)
- Workspace clutter from 400+ TDD reports blocking phase visibility
- Plan-viewer.html shows stale data (no sync after reports generated)

---

## Detailed Findings by Prompt

### Finding 1: cortex-brittleness-review.prompt.md

**Issue:** AC-ID generation WITHOUT AC-INDEX.yaml integration

**Evidence:**
```
Generated File:  cortex-brain/documents/reports/AC-IDS-BRITTLENESS-2026-01-12.yaml
Expected Location: cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml (appended)

Current State:
- 29 AC-IDs exist under root key `brittleness_acs:` in separate file
- AC-INDEX.yaml remains at 102 AC-IDs (unchanged)
- MasterOrchestrator reads ONLY AC-INDEX.yaml → Can't see 29 new AC-IDs
- TodoManager has no tasks for brittleness work
- TDD-Master can't enforce test-first on unregistered AC-IDs
```

**Root Cause:** Prompt output template creates separate YAML file instead of mandating AC-INDEX.yaml append

**CORE Rules Violated:**
- **CORE-009:** Brittleness reports should be in tier1/acceptance-criteria/ (not documents/reports/)
- **CORE-022:** File name `AC-IDS-BRITTLENESS-2026-01-12.yaml` is 31 chars (max 20 allowed)

**Fix Applied:** Updated prompt.md with mandatory integration section (Section B)

**Status:** ✅ PROMPT UPDATED - Still requires manual AC-ID integration into AC-INDEX.yaml

---

### Finding 2: cortex-evidence-validator.prompt.md

**Issue:** No explicit guidance on output location or naming

**Evidence:**
```
Validation reports generated but not stored in organized location
No requirement for plan-viewer synchronization after validation
```

**Root Cause:** Prompt assumes standard outputs but doesn't specify location/naming

**CORE Rules Violated:**
- **CORE-002:** Summary files might be created at root level without restriction
- **CORE-009:** Evidence reports should live in evidence-bundles/ or validation/ subfolder

**Recommended Fix:**
Add section requiring:
1. Evidence reports → `cortex-brain/tier1/evidence-bundles/validation-{date}.yaml`
2. Call `sync_plan_viewer_data.py` after validation
3. Update progress-tracker.json with verification_rate

**Status:** ⚠️ NEEDS UPDATE

---

### Finding 3: cortex-exec.prompt.md

**Issue:** Implementation reports not synced to plan-viewer

**Evidence:**
```
Script calls sync_plan_viewer_data.py but doesn't verify success
No mandate to update plan-viewer-data.json completion percentages
Dashboard shows stale data while execution happens
```

**Root Cause:** Sync exists but not required; async execution means data lag

**CORE Rules Violated:**
- **CORE-002** (if summary files created)
- **CORE-003** (Visual Progress Format)

**Recommended Fix:**
1. Add validation that sync succeeded
2. Verify plan-viewer-data.json updated with current metrics
3. Report sync status in response

**Status:** ⚠️ NEEDS UPDATE

---

### Finding 4: Documents/Reports Folder Structure

**Issue:** MASSIVE file organization violation

**Evidence:**
```
cortex-brain/documents/reports/
├── AC-IDS-BRITTLENESS-2026-01-12.yaml          ❌ 31 chars (max 20)
├── BRITTLENESS-REVIEW-EXECUTIVE-SUMMARY-2026-01-12.md  ❌ 54 chars (max 20)
├── CORTEX6-BRITTLENESS-REVIEW-2026-01-12.md    ❌ 35 chars (max 20)
├── architecture-audit-*.json                     ✅ Kebab-case (11 chars)
├── implementation-progress-*.md                  ✅ Kebab-case (20 chars)
└── tdd/
    └── tdd-report-20260111-154948.md             ✅ Kebab-case (24 chars - over limit!)
    └── tdd-report-*.md (400+ files)              ❌ MASSIVE clutter
```

**Root Cause:** Multiple prompt outputs not organized by purpose/category

**CORE Rules Violated:**
- **CORE-022:** File names exceed 20-character limit (kebab-case max)
- **CORE-009:** Report files should be in organized subfolders (by type, not flat)
- **CORE-002:** TDD reports might be summary files (should be evidence bundles)

**Proper Structure (Proposed):**
```
cortex-brain/documents/reports/
├── brittleness/
│   ├── findings-2026-01-12.yaml           ✅ 18 chars
│   ├── executive-summary-2026-01-12.md    ✅ 28 chars (over by 8, needs shorten)
│   └── analysis-2026-01-12.md             ✅ 19 chars
├── evidence-bundles/
│   ├── ac-audit-001-evidence.yaml         ✅ 24 chars (still over - needs discussion)
│   └── phase-1-validation.yaml            ✅ 20 chars
└── tdd/
    ├── evidence-summary-2026-01-12.yaml   ✅ 28 chars (needs shortening)
    └── [individual test reports organized by AC-ID, not timestamp]
```

**Issue:** Even "proper" structure still violates 20-char limit on some filenames

**Discussion Needed:** Should CORE-022 be relaxed for dated files / evidence bundles?
- **Option A:** Strict 20-char limit + shorten all filenames
- **Option B:** Extend limit to 32 chars for dated/versioned files (e.g., `brittleness-findings-2026-01-12.yaml` = 31)
- **Option C:** Use version numbers only: `brittleness-findings-v001.yaml` (24 chars)

**Status:** ⚠️ AWAITING DECISION - Governance conflict needs resolution

---

## Integration Requirements (All Prompts)

### Standard Output Template (PROPOSED)

All prompts generating artifacts should follow this pattern:

```yaml
# Prompt Output Organization Template

output_artifacts:
  ac_ids:
    location: cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
    action: APPEND to acceptanceCriteria[] array (NOT separate file)
    validation: Schema compliance check, no duplicates
    
  evidence_reports:
    location: cortex-brain/tier1/evidence-bundles/
    naming: "{category}-evidence-{date}.yaml"  # e.g., brittleness-evidence-2026-01-12.yaml
    action: Create in proper subfolder, validate schema
    
  progress_tracking:
    location: cortex-brain/tier1/tracking/progress-tracker.json
    action: UPDATE (don't replace) with new completion percentages
    
  sync:
    location: scripts/sync_plan_viewer_data.py
    action: RUN after each update
    validate: Verify plan-viewer-data.json updated
    report: Status in response (✅ sync successful)
```

---

## Action Plan

### Phase 1: Fix Governance Violations (Immediate)

**Deliverable:** cortex-brain/tier0/governance/file-organization-policy.yaml

**Actions:**
1. ✅ **CORE-022 Interpretation** - Decide: strict 20-char OR relaxed limit for dated files?
   - **Recommended:** 32-char limit for date-versioned files (backward compatible)
   - **Rationale:** Evidence bundles need timestamps; 20 is too restrictive for purpose clarity

2. ✅ **Create Proper Folder Structure**
   ```
   cortex-brain/documents/reports/
   ├── brittleness/        (brittleness findings)
   ├── evidence/           (evidence bundles)
   ├── tdd/                (TDD test reports - archived)
   └── validation/         (validator output)
   ```

3. ✅ **Reorganize Existing Files**
   - Rename brittleness reports following new convention
   - Move/archive 400+ TDD reports → cortex-brain/archives/tdd-reports-historical/
   - Update references in prompts

4. ✅ **Document in CORE-022 Amendment**
   - File naming exception for date-versioned reports: "yyyy-mm-dd" pattern allowed
   - Example: `brittleness-findings-2026-01-12.yaml` (28 chars with exception)

**Timeline:** 2 hours  
**Owner:** Infrastructure Team  
**Blocker:** None (can execute immediately)

---

### Phase 2: Fix AC-ID Integration (Critical Path)

**Deliverable:** 29 brittleness AC-IDs appended to AC-INDEX.yaml

**Actions:**
1. ✅ **Create Migration Script**
   ```python
   # scripts/migrate-brittleness-acs.py
   # Reads: AC-IDS-BRITTLENESS-2026-01-12.yaml
   # Writes: Appends to AC-INDEX.yaml acceptanceCriteria[] array
   # Validates: Schema compliance
   # Updates: AC-INDEX metadata (total_ac_count, last_updated)
   ```

2. ✅ **Execute Migration**
   - Validate no duplicates
   - Verify schema matches AC-INDEX format
   - Run pytest to ensure no JSON schema breaks

3. ✅ **Verification**
   - MasterOrchestrator can now read all 131 AC-IDs (102 + 29)
   - TodoManager creates tasks for new AC-IDs
   - Progress-tracker.json reflectsnew AC-IDs in appropriate phase

4. ✅ **Clean Up**
   - Delete/archive AC-IDS-BRITTLENESS-2026-01-12.yaml (no longer source of truth)
   - Archive report documents in cortex-brain/archives/brittleness-review-2026-01-12/

**Timeline:** 1 hour  
**Owner:** Infrastructure Team  
**Blocker:** None (script is straightforward)

---

### Phase 3: Update Prompt Files (Governance Compliance)

**Deliverable:** Updated `.github/prompts/` with proper output specifications

**Actions:**

1. **cortex-brittleness-review.prompt.md**
   - ✅ Section B already updated with integration mandate
   - Add: Output location specification
   - Add: File naming rules (kebab-case, date format)

2. **cortex-evidence-validator.prompt.md**
   - Add: Output location → `cortex-brain/tier1/evidence-bundles/validator-evidence-{date}.yaml`
   - Add: Sync requirement → Call `sync_plan_viewer_data.py` after validation
   - Add: Progress update → Update progress-tracker.json with verification_rate

3. **cortex-exec.prompt.md**
   - Add: Sync validation → Verify `sync_plan_viewer_data.py` succeeds
   - Add: Dashboard update → Report sync status in response

4. **Create: .github/prompts/output-standards.md**
   - Template for all prompts to follow
   - Location, naming, sync, validation rules
   - Example implementations

**Timeline:** 3 hours  
**Owner:** Infrastructure Team  
**Blocker:** Decision on CORE-022 limits needed first

---

### Phase 4: Update Master Plan & Plan-Viewer (Final)

**Deliverable:** master-plan.yaml + plan-viewer-data.json updated with brittleness work

**Actions:**

1. **Integrate Brittleness AC-IDs into Phase Assignments**
   - 4 CRITICAL AC-IDs → Phase 1 (week 1-2) with high priority
   - 6 HIGH AC-IDs → Phase 2 (week 3-4) with medium priority
   - Remaining → Phase 3 as technical debt track

2. **Update Phase Completion Metrics**
   - Phase 1: 33 AC-IDs + 4 brittleness CRITICAL = 37 total
   - Completion % recalculated based on new total
   - Reorder Phase 1 tasks: critical brittleness first, then foundation

3. **Sync plan-viewer-data.json**
   - Run: `python3 scripts/sync_plan_viewer_data.py`
   - Verify: plan-viewer.html dashboard shows updated phase info
   - Validate: No hardcoded data in HTML (use JSON only)

4. **Create Phase 1.5: Critical Path Brittleness**
   - Option: Add Phase 1.5 (1-2 days) for CRITICAL issues only
   - Or: Integrate into Phase 1 with priority sequencing

**Timeline:** 2 hours  
**Owner:** Planning Team  
**Blocker:** AC-ID integration (Phase 2) must complete first

---

## Governance Rule Resolution

### CORE-022 Decision Required

**Issue:** File naming limit of 20 characters conflicts with date-versioned reports

**Examples:**
- ❌ `AC-IDS-BRITTLENESS-2026-01-12.yaml` (31 chars)
- ❌ `BRITTLENESS-REVIEW-EXECUTIVE-SUMMARY-2026-01-12.md` (54 chars)
- ✅ `brittleness-findings-2026-01-12.yaml` (28 chars with kebab-case)

**Proposed Amendment to CORE-022:**

```yaml
exception:
  pattern: "date-versioned reports"
  format: "{name}-{yyyy-mm-dd}.{ext}"
  max_length: 32  # Accommodate ISO 8601 date suffix
  example:
    - "brittleness-findings-2026-01-12.yaml"     ✅ 28 chars
    - "evidence-validator-2026-01-12.yaml"       ✅ 28 chars
    - "phase-1-report-2026-01-12.md"             ✅ 24 chars
  rationale: "Evidence and audit reports require timestamps for version tracking"
```

**Decision Needed:**
- [ ] Accept 32-char limit exception for date-versioned files
- [ ] Strict 20-char limit, use version numbers instead: `brittleness-findings-v001.yaml`
- [ ] Alternative: Store timestamps in metadata, not filename

**Recommendation:** Accept 32-char exception (Option 1) - preserves intent while accommodating practical needs

---

## Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|-----------|
| AC-ID integration incomplete | HIGH | Medium | Execute Phase 2 migration script |
| Workspace clutter persists | MEDIUM | Low | Archive TDD reports to historical/ |
| Plan-viewer shows stale data | MEDIUM | Medium | Mandatory sync after updates |
| CORE-022 violations not resolved | HIGH | High | Governance amendment needed |
| Other prompts have same issue | MEDIUM | High | Comprehensive prompt audit (ongoing) |

---

## Checklist for Completion

- [ ] Phase 1: Reorganize files, update CORE-022, archive TDD reports
- [ ] Phase 2: Run migration script, verify AC-IDs in AC-INDEX.yaml, cleanup
- [ ] Phase 3: Update all 4 prompt files with output standards
- [ ] Phase 4: Update master plan, sync plan-viewer, validate dashboard
- [ ] Audit: Verify no other prompts have same integration gaps
- [ ] Documentation: Update .github/prompts/output-standards.md
- [ ] Testing: Run tests to verify AC-INDEX.yaml schema compliance
- [ ] Sign-off: Review with governance team, update TRUTH-SOURCES.yaml

---

## Files Affected

**To Create:**
- `cortex-brain/tier0/governance/file-organization-policy.yaml`
- `.github/prompts/output-standards.md`
- `scripts/migrate-brittleness-acs.py`

**To Update:**
- `.github/prompts/cortex-brittleness-review.prompt.md` (✅ DONE)
- `.github/prompts/cortex-evidence-validator.prompt.md`
- `.github/prompts/cortex-exec.prompt.md`
- `cortex-brain/cx6-plan/master-plan.yaml`

**To Reorganize:**
- `cortex-brain/documents/reports/` (flatten, rename, move to subfolders)
- `cortex-brain/documents/reports/tdd/` (archive to historical/)

**To Archive:**
- `cortex-brain/documents/reports/AC-IDS-BRITTLENESS-2026-01-12.yaml`
- 400+ TDD reports → `cortex-brain/archives/tdd-reports-historical-2026-01-10-2026-01-12/`

---

## Related Documentation

- CORE-002: Block Summary File Generation
- CORE-009: Plan File Organization
- CORE-022: Kebab-Case File Naming (20-char limit)
- cortex-brittleness-review.prompt.md (Section B - just updated)
- AC-INDEX.yaml (acceptance criteria registry)
- progress-tracker.json (phase tracking)
- master-plan.yaml (implementation roadmap)

---

**Report Generated:** 2026-01-12T14:30:00Z  
**Status:** ACTIONABLE - All phases have clear owners and timelines  
**Next Step:** Execute Phase 1 (file organization) before proceeding to other phases
