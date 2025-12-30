# Documentation Deduplication Master Plan

**Plan ID:** docs-deduplication  
**Author:** Asif Hussain  
**Date Created:** 2025-12-28  
**Status:** 🟡 IN PLANNING  
**Priority:** HIGH

---

## 🎯 Executive Summary

The CORTEX documentation site (`docs/`) contains significant content duplication causing user confusion and maintenance burden. This plan establishes a **three-tier documentation model** and systematically eliminates ~15,000 words of duplicate content while resolving critical conflicts.

**Key Findings:**
- **37 files analyzed** with **HIGH duplication score**
- **7 major repetitions** identified (Planning System, TDD, Maintenance, etc.)
- **CRITICAL conflict:** System Maintenance has conflicting phase counts (6 vs 7)
- **Planning System:** Documented 3 times with 70% content overlap
- **Estimated reduction:** 40-50% of duplicate content

---

## 📊 Problem Statement

### Current State
- Users encounter same content 2-3 times in different locations
- Conflicting information (phase counts, metrics) across pages
- Unclear hierarchy between `features/`, `orchestrators/`, and `technical/orchestrators/`
- Empty placeholder files causing confusion
- No single source of truth for canonical information

### Impact
- **User Experience:** Overwhelming, confusing navigation
- **Maintenance:** Changes require updating 2-3 files
- **Trust:** Conflicting info damages credibility
- **SEO:** Duplicate content penalties

---

## 🏗️ Solution: Three-Tier Documentation Model

### Tier 1: Features (Marketing/Overview)
**Location:** `docs/features/`  
**Purpose:** High-level benefits and use cases  
**Length:** 500-800 words per page  
**Content:**
- What problem does it solve?
- Key benefits (3-5 bullet points)
- Simple command example
- Link to full documentation

**Example:**
```html
<!-- features/planning-system.html -->
<h2>What Is Planning System?</h2>
<p>Transforms vague feature requests into executable plans</p>
<ul>
  <li>4-folder structured planning</li>
  <li>DoR/DoD compliance</li>
  <li>Automatic TDD integration</li>
</ul>
<a href="../orchestrators/planning-system.html">Full Documentation →</a>
```

### Tier 2: Orchestrators (User Documentation)
**Location:** `docs/orchestrators/`  
**Purpose:** Complete user-facing documentation  
**Length:** 1500-3000 words per page  
**Content:**
- Full workflow description
- All phases with details
- Command examples with output
- Troubleshooting guide
- Integration points
- Link to technical details

**This is the SOURCE OF TRUTH for user documentation.**

### Tier 3: Technical (Implementation Details)
**Location:** `docs/technical/orchestrators/`  
**Purpose:** Developer/contributor documentation  
**Length:** 2000-5000 words per page  
**Content:**
- Architecture diagrams
- Code structure
- API references
- Algorithm descriptions
- Contribution guidelines

---

## 📋 Implementation Phases

### Phase 1: Critical Fixes & Admin Feature Removal (IMMEDIATE)
**Estimated Time:** 3 hours  
**Priority:** CRITICAL

#### Tasks:
1. **System Maintenance Removal**
   - **Decision:** Admin feature, remove from public docs
   - **Verified:** 6-phase workflow per `cortex-maintenance.prompt.md`
   - Delete: `features/system-maintenance.html`
   - Delete: `orchestrators/system-maintenance.html`
   - Remove all links from: `orchestrators/index.html`, `features/index.html`, `getting-started/tutorial.html`, `faq.html`, `orchestrators/refinement-orchestrator.html`, `orchestrators/system-integrity.html`
   - Note: Feature still available via `system maintenance` command for admin use

2. **Populate Empty Architectural Review**
   - **Decision:** Populate with technical content
   - File: `technical/orchestrators/architectural-review.html`
   - Content source: Derive from `orchestrators/architectural-review.html` (618 lines)
   - Add: Architecture diagrams, code structure, API references, contribution guidelines

### Phase 2: Planning System Consolidation
**Estimated Time:** 3 hours  
**Priority:** HIGH

#### Tasks:
1. **Audit Phase Count**
   - Check manifest: `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
   - Verify actual implementation
   - Establish canonical phase count

2. **Consolidate Content**
   - Keep `orchestrators/planning-system.html` as SOURCE OF TRUTH
   - Reduce `features/planning-system.html` to 500-800 words (overview only)
   - Remove Planning System section from `features/orchestrators.html` (link instead)

3. **Update Cross-References**
   - All links point to `orchestrators/planning-system.html`
   - Features page has prominent "Full Documentation →" link

### Phase 3: TDD Orchestrator Consolidation
**Estimated Time:** 3 hours  
**Priority:** HIGH

#### Tasks:
1. **Merge User + Technical Versions**
   - **Decision:** Merge both files into single comprehensive page
   - Source: `orchestrators/tdd-orchestrator.html` (user-facing)
   - Append: Technical content from `technical/orchestrators/tdd-orchestrator.html`
   - Target audience: Both technical and non-technical users

2. **Create Unified Structure**
   - Section 1: Overview (non-technical)
   - Section 2: Workflow & Phases (all users)
   - Section 3: Technical Implementation (technical users)
   - Section 4: Examples (all users)
   - Section 5: Architecture & APIs (technical users)

3. **Remove Technical Duplicate**
   - Delete: `technical/orchestrators/tdd-orchestrator.html`
   - Update all links to point to: `orchestrators/tdd-orchestrator.html`

### Phase 4: CORTEX Lens Consolidation
**Estimated Time:** 2 hours  
**Priority:** MEDIUM

#### Tasks:
1. **Audit Content**
   - `orchestrators/cortex-lens.html` (663 lines) = full user docs
   - `technical/orchestrators/cortex-lens.html` (200 lines) = technical subset
   - Verify no conflicting information

2. **Deduplicate Intro**
   - Remove duplicate "repository storyteller" description
   - Technical version links to user docs for overview

### Phase 5: ADO Operations Cleanup
**Estimated Time:** 1.5 hours  
**Priority:** MEDIUM

#### Tasks:
1. **Verify Split**
   - User docs: `orchestrators/ado-operations.html`
   - Technical docs: `technical/orchestrators/ado-planning.html`
   - 25% content overlap = ACCEPTABLE (different audiences)

2. **Deduplicate Hook**
   - Remove duplicate "Writing Azure DevOps work items is tedious" intro
   - Use template variable

### Phase 6: Orchestrators Overview Consolidation
**Estimated Time:** 2 hours  
**Priority:** MEDIUM

#### Tasks:
1. **Establish Clear Hierarchy**
   - `features/index.html` → High-level grid (6 core features)
   - `features/orchestrators.html` → Remove or redirect to `orchestrators/index.html`
   - `orchestrators/index.html` → Complete catalog (16 orchestrators)

2. **Update Navigation**
   - Features page links to orchestrators catalog
   - Clear distinction: "6 core features" vs "16 orchestrators"

### Phase 7: Shared Content System
**Estimated Time:** 3 hours  
**Priority:** LOW

#### Tasks:
1. **Create Metrics Data Source**
   - File: `docs/assets/data/orchestrator-metrics.json`
   - Single source for phase counts, success rates, etc.
   - All pages reference this data

2. **Create Intro Hook Templates**
   - File: `docs/assets/data/intro-hooks.json`
   - Reusable intro paragraphs
   - Use JavaScript to inject into pages

3. **Standardize Breadcrumbs**
   - Choose separator: `→` (consistent across all)
   - Update CSS: `.breadcrumb-separator`

### Phase 8: Documentation Style Guide
**Estimated Time:** 2 hours  
**Priority:** LOW

#### Tasks:
1. **Create Style Guide**
   - File: `cortex-brain/documents/templates/documentation-hierarchy-guide.md`
   - Define three-tier model
   - Word count targets per tier
   - Content guidelines

2. **Update README**
   - Document new structure in `docs/README.md`
   - Link to style guide

---

## 📈 Success Metrics

### Quantitative
- **Content Reduction:** 40-50% duplicate content removed (~15,000 words)
- **File Changes:** 12 major, 8 minor
- **Files Removed:** 1 (empty architectural-review.html)
- **Consistency:** 100% phase counts match source code
- **Navigation:** <3 clicks to any page from home

### Qualitative
- Users can easily distinguish overview vs detailed docs
- No conflicting information
- Clear "next steps" on every page
- Single source of truth established

---

## ⚠️ Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Removing needed content | MEDIUM | HIGH | Audit before deletion, keep backups |
| Introducing new inconsistencies | MEDIUM | MEDIUM | Use metrics data source, single source of truth |
| Missing System Maintenance links | HIGH | LOW | Comprehensive grep search for all references |
| User confusion during transition | LOW | LOW | No banner needed, changes are improvements |

**Note:** Removed "Breaking bookmarks" risk - no redirects needed per user decision.

---

## 🔗 Dependencies

1. **Source Code Manifests**
   - `cortex-brain/manifests/orchestrators/*.yaml`
   - Must verify phase counts against manifests

2. **GitHub Pages Deployment**
   - Changes require git push to trigger deployment
   - Test locally before pushing

3. **Navigation Updates**
   - `docs/assets/css/main.css` (breadcrumb styles)
   - `docs/index.html` (main navigation)

---

## 📁 Deliverables

### Phase 1-6 Deliverables
- [ ] Updated documentation files (20 files)
- [ ] Removed empty placeholder (1 file)
- [ ] Redirects for moved pages (if needed)
- [ ] Updated cross-references (all links)

### Phase 7-8 Deliverables
- [ ] `docs/assets/data/orchestrator-metrics.json`
- [ ] `docs/assets/data/intro-hooks.json`
- [ ] `cortex-brain/documents/templates/documentation-hierarchy-guide.md`
- [ ] Updated `docs/README.md`

### Final Deliverable
- [ ] **Deduplication Report** (this file)
- [ ] **Before/After Metrics** (word count, file count)
- [ ] **Testing Checklist** (verify all links, no conflicts)

---

## 🚀 Execution Timeline

| Phase | Duration | Priority | Dependencies |
|-------|----------|----------|--------------|
| Phase 1: Critical Fixes & Admin Removal | 3h | CRITICAL | None |
| Phase 2: Planning System | 3h | HIGH | Phase 1 complete |
| Phase 3: TDD Consolidation | 3h | HIGH | Phase 1 complete |
| Phase 4: CORTEX Lens | 2h | MEDIUM | Phase 1 complete |
| Phase 5: ADO Operations | 1.5h | MEDIUM | Phase 1 complete |
| Phase 6: Overview Consolidation | 2h | MEDIUM | Phases 2-5 complete |
| Phase 7: Shared Content System | 3h | LOW | Phase 6 complete |
| Phase 8: Style Guide | 2h | LOW | Phase 7 complete |

**Total Estimated Time:** 19.5 hours  
**Suggested Schedule:** 2-3 days at 6-8 hours/day

---

## 📝 Notes

- **Backups:** Create backup of `docs/` folder before starting: `cp -r docs/ docs.backup/`
- **Testing:** Test locally with `./scripts/launch_docs.sh` after each phase
- **Version Control:** Commit after each phase completion
- **User Communication:** Update docs site with "Under Renovation" banner during work

---

## ✅ Definition of Done (DoD)

- [ ] All critical conflicts resolved (System Maintenance phases, Planning System phases)
- [ ] Empty files removed or populated
- [ ] Three-tier hierarchy clearly established
- [ ] No duplicate intro paragraphs
- [ ] All cross-references updated and working
- [ ] Breadcrumb separators consistent
- [ ] Metrics data source created and used
- [ ] Style guide documented
- [ ] README updated with new structure
- [ ] All links tested and working
- [ ] Local testing passed (no 404s, no broken links)
- [ ] Deployed to GitHub Pages successfully
- [ ] User testing: Can find information in <3 clicks

---

## 📞 Contact & Approval

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Status:** Ready for execution upon user approval

**Approval Required:** YES  
**Estimated Completion:** 2025-12-30

---

**Next Step:** Review this plan and approve Phase 1 (Critical Fixes) to begin execution.
