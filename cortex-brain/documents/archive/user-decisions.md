# User Decisions Log

**Date:** 2025-12-28  
**Plan:** Documentation Deduplication & Consolidation

---

## 📝 Decisions Made

### 1. TDD Orchestrator - MERGE
**Question:** Should we keep both user and technical versions of TDD Orchestrator?

**User Decision:** ❌ NO - Merge into single comprehensive page

**Rationale:** "If it makes sense considering both technical and non-technical users will be reading it. I prefer we merge them in one."

**Implementation:**
- Merge `orchestrators/tdd-orchestrator.html` + `technical/orchestrators/tdd-orchestrator.html`
- Create sections for different audiences within single page
- Delete technical duplicate after merge
- Update all cross-references to point to unified page

**Impact:** +1 hour to Phase 3 (from 2h to 3h)

---

### 2. System Maintenance - REMOVE
**Question:** What's the correct System Maintenance phase count? (verify from source)

**User Decision:** 🗑️ REMOVE from public docs - "this is admin feature and should be removed from doc"

**Verification:**
- Source: `.github/prompts/cortex-maintenance.prompt.md`
- Actual phases: 6 (Quick Health Check, Full Diagnostic, Wiring Integrity, Review Reports, Intent Router Validation, Regenerate Lean Prompts)
- Core manifest: `cortex-brain/manifests/core-manifest.yaml` shows 7-phase workflow with vacuum
- Available via: `system maintenance` command (admin only)

**Implementation:**
- Delete: `docs/features/system-maintenance.html`
- Delete: `docs/orchestrators/system-maintenance.html`
- Remove links from: `orchestrators/index.html`, `features/index.html`, `getting-started/tutorial.html`, `faq.html`, `orchestrators/refinement-orchestrator.html`, `orchestrators/system-integrity.html`

**Impact:** +1 hour to Phase 1 (from 2h to 3h) for comprehensive link removal

---

### 3. Architectural Review - POPULATE
**Question:** Should empty architectural-review.html be removed or populated?

**User Decision:** ✅ POPULATE - "populated"

**Implementation:**
- Source content from: `orchestrators/architectural-review.html` (618 lines)
- Add technical details:
  - Architecture diagrams
  - Code structure
  - API references
  - Contribution guidelines
  - Implementation details

**Impact:** Included in Phase 1 scope

---

### 4. Redirects - NOT NEEDED
**Question:** Do you want redirects for moved pages to preserve bookmarks?

**User Decision:** ❌ NO - "Remove links for Removed pages"

**Implementation:**
- No redirects for deleted files
- Simply remove all links pointing to deleted pages
- Clean removal (no 404 handling needed)

**Impact:** Simplifies implementation, reduces risk

---

### 5. Renovation Banner - NOT NEEDED
**Question:** Should we add a "Under Renovation" banner during the work?

**User Decision:** ❌ NO - "no"

**Implementation:**
- No banner added
- Work proceeds without user notification
- Changes are improvements, not breaking changes

**Impact:** Simplifies workflow

---

## 📊 Impact Summary

### Time Estimates Updated
- **Phase 1:** 2h → 3h (+1h for System Maintenance removal)
- **Phase 3:** 2h → 3h (+1h for TDD merge work)
- **Total:** 17.5h → 19.5h

### Scope Changes
- **Files to Remove:** 1 → 3 (added 2 System Maintenance files)
- **Total Tasks:** 22 → 23 (+1 for link removal)
- **Merge Work:** New task to merge TDD Orchestrator

### Risks Removed
- ✅ No bookmark breakage risk (no redirects needed)
- ✅ No user confusion risk (no banner needed)
- ✅ System Maintenance phase count conflict resolved (removed from docs)

### New Considerations
- ⚠️ Ensure all System Maintenance links found and removed
- ⚠️ TDD merge must serve both technical and non-technical audiences
- ⚠️ Architectural Review content must be comprehensive technical documentation

---

## ✅ Approval Status

**Phase 1 Approved:** ✅ YES (with modifications)  
**Overall Plan Approved:** ⏳ Pending final user confirmation

**Next Step:** User says "Start Phase 1" to begin execution

---

**Documented By:** CORTEX AI  
**Last Updated:** 2025-12-28
