# Documentation Deduplication Context

**Plan ID:** docs-deduplication  
**Analysis Date:** 2025-12-28

---

## 📊 Audit Summary

### Files Analyzed
- **Total:** 37 HTML files
- **Duplication Score:** HIGH (40-50% content overlap)
- **Major Duplications:** 7 topics
- **Conflicting Information:** 2 critical conflicts

### Scope
```
docs/
├── features/*.html (8 files)
├── orchestrators/*.html (18 files)
├── technical/orchestrators/*.html (11 files)
└── architecture/*.html (0 analyzed, covered separately)
```

---

## 🔍 Key Findings

### Critical Issues
1. **System Maintenance Phase Count**
   - `features/system-maintenance.html`: 6 phases
   - `orchestrators/system-maintenance.html`: 7 phases
   - **Conflict:** Vacuum phase missing in features version
   - **Action Required:** Determine actual phase count from source

2. **Planning System Duplication**
   - Documented in 3 separate locations
   - 70% content overlap
   - Conflicting phase counts: 10 vs 5
   - Different metrics: DoR (8 vs TBD), DoD (6 vs TBD)

3. **Empty File**
   - `technical/orchestrators/architectural-review.html` is EMPTY
   - User version has 618 lines of content
   - **Action Required:** Remove or populate

### High-Priority Duplications

#### Planning System
- **Files:** 3 (features/, orchestrators/, features/orchestrators.html)
- **Overlap:** 70%
- **Conflicts:** Yes (phase counts, metrics)
- **Recommendation:** Consolidate to orchestrators/, reduce features/ to overview

#### TDD Orchestrator
- **Files:** 2 (orchestrators/, technical/orchestrators/)
- **Overlap:** 40%
- **Conflicts:** No (different audiences)
- **Recommendation:** Keep both, deduplicate intro paragraphs

#### CORTEX Lens
- **Files:** 2 (orchestrators/, technical/orchestrators/)
- **Overlap:** 30%
- **Conflicts:** No
- **Recommendation:** Deduplicate intro, ensure complementary content

---

## 🏗️ Proposed Architecture

### Three-Tier Model

```
Tier 1: Features (Overview)
├── Purpose: Marketing, high-level benefits
├── Length: 500-800 words
├── Links to: Orchestrators for details
└── Example: "What problem does it solve?"

Tier 2: Orchestrators (User Docs)
├── Purpose: Complete user documentation
├── Length: 1500-3000 words
├── Content: Full workflow, all phases, examples
└── **SOURCE OF TRUTH**

Tier 3: Technical (Implementation)
├── Purpose: Developer/contributor docs
├── Length: 2000-5000 words
├── Content: Architecture, code, APIs
└── Links to: Source code
```

---

## 📈 Metrics

### Current State
- **Duplicate words:** ~15,000
- **Files with major changes needed:** 12
- **Files with minor changes needed:** 8
- **Empty/incomplete files:** 1

### Target State
- **Content reduction:** 40-50%
- **Duplicate words removed:** ~15,000
- **Phase count conflicts resolved:** 2
- **Navigation clicks to any page:** <3

---

## 🎯 Success Criteria

### Quantitative
- [ ] All critical conflicts resolved
- [ ] Empty files removed or populated
- [ ] 40-50% content reduction achieved
- [ ] Single source of truth established for each topic
- [ ] All cross-references updated and working

### Qualitative
- [ ] Users can distinguish overview vs detailed docs
- [ ] No conflicting information anywhere
- [ ] Clear "next steps" on every page
- [ ] Breadcrumb separators consistent

---

## 🔗 Dependencies

### Source Code References
- `cortex-brain/manifests/orchestrators/*.yaml` - Phase counts, metrics
- `.github/prompts/cortex-maintenance.prompt.md` - System Maintenance truth
- Source code implementations - Verify actual behavior

### Deployment
- GitHub Pages deployment pipeline
- Local testing: `./scripts/launch_docs.sh`
- Browser cache clearing required after updates

---

## 📚 References

### Audit Report
- **Location:** `reports/audit-report.json`
- **Content:** Complete JSON analysis of all duplications

### Master Plan
- **Location:** `00-master-plan.md`
- **Content:** 8-phase implementation strategy

### Progress Tracker
- **Location:** `tracking/progress-tracker.json`
- **Content:** Real-time task completion tracking

---

## ⚠️ Risks

1. **Breaking Bookmarks**
   - Likelihood: HIGH
   - Impact: MEDIUM
   - Mitigation: Add redirects for moved pages

2. **Removing Needed Content**
   - Likelihood: MEDIUM
   - Impact: HIGH
   - Mitigation: Audit before deletion, keep backups

3. **New Inconsistencies**
   - Likelihood: MEDIUM
   - Impact: MEDIUM
   - Mitigation: Use metrics data source, single source of truth

---

## 🚀 Next Steps

1. Review master plan in detail
2. Review audit report for specific duplications
3. Approve Phase 1 (Critical Fixes)
4. Create backup of docs/ folder
5. Begin execution

---

**Last Updated:** 2025-12-28  
**Status:** Ready for execution
