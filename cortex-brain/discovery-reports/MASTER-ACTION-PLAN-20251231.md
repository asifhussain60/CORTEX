# 🎯 CORTEX Maintenance Master Action Plan

**Date:** December 31, 2025  
**Phase:** Discovery Complete  
**Maintenance Mode:** AUTONOMOUS

---

## 📋 Discovery Summary

| Category | Issues Found | Priority | Target Phase | Status |
|----------|--------------|----------|--------------|--------|
| **Wiring** | 1 unwired agent | HIGH | Phase 5 | 🔧 Auto-repair |
| **Backups** | 5 backup folders | MEDIUM | Phase 0 | ✅ Cleaned |
| **Prompt Bloat** | 5 bloated prompts | LOW | Phase 10 | 📝 Optimize |
| **Reports** | Duplicate reports | LOW | Phase 8 | 🗂️ Organize |
| **Knowledge** | 5 YAML, 0 MD | MEDIUM | Phase 7 | 📚 Sync |
| **Tests** | 3246 tests, 2 errors | MEDIUM | Phase 6 | 🧪 Fix |
| **Templates** | Template refs | MEDIUM | Phase 2 | ✅ Validate |

---

## 🔍 Detailed Findings

### 1. Wiring Coverage: 99.7% (1 component unwired)

**Unwired Components:**
- `SecurityScannerAgent` (src\cortex_agents\security_scanner_agent.py)

**Action:** Phase 5 will auto-wire this agent using bulk wiring system

**Coverage:**
- Orchestrators: 26/26 ✅ 100%
- Agents: 10/11 ⚠️ 90.9%
- Modules: 250/250 ✅ 100%
- Plugins: 13/13 ✅ 100%
- **Total: 299/300 (99.7%)**

---

### 2. Backup Bloat: 5 folders in backups/

**Folders:**
- auto_wire_20251230_113053/
- auto_wire_20251230_113541/
- cleanup_20251230_113718/
- cleanup_20251230_114039/
- cleanup_20251230_114059/

**Status:** ✅ CLEAN - Marked for retention (recent auto-wire/cleanup manifests)

**Action:** No action needed - cleanup orchestrator already removed old backups

---

### 3. Prompt Bloat: 5 files exceeding 200 lines

| File | Lines | Bloat Factor | Action |
|------|-------|--------------|--------|
| cortex-maintenance.prompt.md | 3194 | 🔴 15.97x | Phase 10 - Regenerate lean |
| cortex-backlog.prompt.md | 353 | 🟡 1.77x | Phase 10 - Optimize |
| cortex-upgrade.prompt.md | 342 | 🟡 1.71x | Phase 10 - Optimize |
| CORTEX-GitCommit.prompt.md | 316 | 🟡 1.58x | Phase 10 - Optimize |
| cortex-cleanup.prompt.md | 241 | 🟡 1.21x | Phase 10 - Optimize |
| CORTEX.prompt.md | 157 | ✅ 0.79x | OK - No action |

**Target:** All prompts <200 lines (except orchestrator manifests)

**Action:** Phase 10 will regenerate lean prompts while preserving all orchestrators + Vision API

---

### 4. Knowledge Library: Sync Issue Detected

**Current State:**
- YAML files: 5
- Markdown files: 0
- Status: ⚠️ OUT OF SYNC

**Action:** Phase 7 will generate markdown documentation from YAML rules

---

### 5. Test Suite: 3246 tests collected, 2 errors

**Status:** 🟡 MEDIUM PRIORITY
- Total tests: 3246
- Errors: 2 (collection errors)
- Pass rate: Unknown (need to run tests)

**Action:** Phase 6 will run full test suite and fix errors

---

### 6. Duplicate Reports: Organizational Issue

**Location:** cortex-brain/documents/reports/

**Issues:**
- Multiple validation reports (ado, deployment, phase)
- Execution history not archived
- Performance data not consolidated

**Action:** Phase 8 will organize reports into proper categories

---

### 7. Template Validation: Pending

**Status:** ⏳ PENDING VALIDATION
- Response templates need integrity check
- Routing rules need validation
- Orphaned references detection

**Action:** Phase 2 will validate all template references

---

## 🎯 Phase Execution Plan

### Phase 2: Template Validation
- Validate response-templates-v4.yaml integrity
- Check routing rules for broken paths
- Remove orphaned template references
- Verify schema consistency (v4.0)

### Phase 3: Brain Protection
- Verify protected data paths exist
- Confirm no critical data in cleanup targets
- Validate lessons-learned.yaml preserved
- Check tier1/tier2/tier3 DBs intact

### Phase 4: Scaffolding
- Verify toolkit generators exist
- Test generation functionality
- Validate scaffold templates

### Phase 5: Wiring
- **Auto-wire SecurityScannerAgent**
- Update wiring manifests
- Verify 100% coverage
- Re-run wiring integrity check

### Phase 6: Testing
- Run full test suite (3246 tests)
- Fix 2 collection errors
- Delete obsolete test markers
- Achieve 100% pass rate

### Phase 7: Knowledge Library
- Generate markdown docs from 5 YAML files
- Sync YAML ↔ MD
- Validate plan content (Rule 9)
- Ensure all plans have mandatory sections

### Phase 8: Organization
- Archive old reports to archives/
- Organize reports by category
- Consolidate duplicate validation files
- Clean report hierarchy

### Phase 9: Routing
- Validate intent router entries
- Fix broken manifest paths
- Verify HAND-OFF orchestrators (Rule 10)
- Test all routing rules

### Phase 10: Prompt Optimization
- Regenerate cortex-maintenance.prompt.md (<200 lines)
- Optimize 4 other bloated prompts
- Preserve all orchestrators + Vision API
- Maintain full functionality

### Phase 11: Final Verification
- Run health diagnostics
- Verify health score ≥95%
- Confirm all issues resolved
- Generate consolidated report

---

## 📊 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Wiring Coverage | 99.7% | 100% | 🟡 |
| Backup Bloat | 0 MB | 0 MB | ✅ |
| Prompt Lines (avg) | 967 | <200 | 🔴 |
| Knowledge Sync | 0% | 100% | 🔴 |
| Test Pass Rate | Unknown | 100% | ⏳ |
| Health Score | Unknown | ≥95% | ⏳ |

---

## 🚀 Next Steps

1. ✅ Phase 0 Complete - Cleanup orchestrator executed
2. ✅ Phase 1 Complete - Discovery report generated
3. 🔄 Phase 2 Starting - Template validation...

**Estimated Total Duration:** ~30 minutes  
**Auto-Repair Mode:** ENABLED  
**User Interaction:** NONE (autonomous)

---

**Generated by:** CORTEX Maintenance Pipeline v4.0  
**Report Location:** cortex-brain/discovery-reports/MASTER-ACTION-PLAN-20251231.md
