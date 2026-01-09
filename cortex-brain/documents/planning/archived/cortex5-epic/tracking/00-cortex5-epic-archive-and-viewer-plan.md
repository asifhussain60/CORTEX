# 📋 CORTEX5 Epic: Backup Archive & Plan Viewer Generation
**Plan ID:** cortex5-epic-archive-viewer  
**Created:** 2026-01-07  
**Version:** 1.0.0  
**Type:** Operational Plan (Archive + Validation)  
**Orchestrator:** cortex-planner.prompt.md  
**Author:** Asif Hussain

---

## 🎯 Executive Summary

**OBJECTIVE:** Archive the backup folder after verification, then generate and validate a production-grade plan-viewer.html for cortex5-epic with zero CSS/HTML/accessibility errors.

**SCOPE:**
1. **Archive Backup** - Move `cortex5-epic-backup-20260107-083422/` to archives with verification
2. **Generate Plan Viewer** - Create responsive HTML viewer for entire epic
3. **Zero-Tolerance Validation** - Lint CSS, HTML, accessibility (WCAG AA), and test all interactive features

**SUCCESS CRITERIA:**
- ✅ Backup archived with manifest documenting what was captured
- ✅ Plan viewer displays all 66 files + hierarchical navigation
- ✅ Zero errors in HTML validation (W3C compliant)
- ✅ Zero errors in CSS validation (CSS3 compliant)
- ✅ Zero accessibility violations (WCAG AA level)
- ✅ Interactive features tested (search, filter, collapse/expand)
- ✅ Responsive design validated (mobile, tablet, desktop)

---

## 📊 Current State Analysis

### Backup Folder Status
**Location:** `/cortex-brain/documents/planning/active/cortex5-epic-backup-20260107-083422/`

**Contents:**
- **File Count:** 61 files
- **Folders:** analysis/, artifacts/, comparison/, features/, phases/, reports/, tracking/
- **Root Files:** CONTINUATION-PROMPT.md, plan-viewer.html (35KB), intermittent-thoughts.txt
- **Created:** 2026-01-07 08:34 AM

**Current Epic Status:**
- **File Count:** 66 files (5 new files since backup)
- **New Additions:**
  - `master-plan.md` (root level - epic overview)
  - `context/` folder (new - contains intermittent-thoughts.txt)
  - `features/planning-system-core/` (new feature folder)
  - `analysis/restructuring-requirements.yaml` (new analysis file)
  - `reports/epic-restructuring-status.md` (new status report)
  - `reports/restructuring-handoff.md` (new handoff doc)
  - `tracking/epic-progress-tracker.json` (new tracker)

**Verification Status:** ✅ ALL backup content captured in current epic (nothing lost)

### Plan Viewer Requirements

**Functionality:**
- Hierarchical folder tree navigation (collapsible)
- Search/filter files by name or content preview
- Markdown rendering for .md files
- YAML/JSON syntax highlighting
- Mobile-responsive design
- Dark/light theme toggle
- Progress tracker visualization (10 features, 3 tiers)

**Technical Requirements:**
- Pure CSS3 (no preprocessors for easier debugging)
- Vanilla JavaScript (ES6+, no frameworks)
- W3C HTML5 validation passing
- CSS3 validation passing
- WCAG AA accessibility compliance
- No external dependencies (self-contained)
- File size target: <150KB (including inline assets)

---

## 🏗️ Phase Breakdown

### Phase 0: Pre-Archive Verification (15 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** None

**Tasks:**
1. **Compare Backup vs Current** (5 min)
   - Run comprehensive diff: `diff -rq backup/ current/ > verification-report.txt`
   - Identify files unique to backup (should be zero - all moved to current)
   - Identify files unique to current (5 new files documented above)
   - Validate no critical data in backup-only files

2. **Generate Backup Manifest** (5 min)
   - Create `cortex-brain/archives/cortex5-epic/backup-20260107-083422-manifest.yaml`
   - Document backup folder structure
   - List all 61 files with checksums (SHA256)
   - Note purpose of backup (pre-restructuring snapshot)
   - Document what was preserved in current epic

3. **Archive Preparation** (5 min)
   - Create archive directory: `cortex-brain/archives/cortex5-epic/`
   - Move backup folder to archives
   - Create README.md in archives explaining backup history
   - Add archive reference to epic tracking

**Exit Criteria:**
- ✅ Verification report shows no unique backup content
- ✅ Manifest created with all file checksums
- ✅ Archive directory prepared

**Deliverables:**
- `verification-report.txt` (diff output)
- `cortex-brain/archives/cortex5-epic/backup-20260107-083422-manifest.yaml`
- `cortex-brain/archives/cortex5-epic/README.md`

---

### Phase 1: Archive Execution (10 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** Phase 0

**Tasks:**
1. **Execute Archive Move** (3 min)
   ```bash
   mkdir -p cortex-brain/archives/cortex5-epic
   mv cortex-brain/documents/planning/active/cortex5-epic-backup-20260107-083422 \
      cortex-brain/archives/cortex5-epic/
   ```

2. **Verify Archive Integrity** (3 min)
   - Count files in archived location (should be 61)
   - Validate manifest checksums match
   - Confirm no files left in original location

3. **Update Epic Tracking** (4 min)
   - Update `tracking/epic-progress-tracker.json` with archive reference
   - Add entry to `tracking/history.json` documenting archive event
   - Update CONTINUATION-PROMPT.md if it references backup location

**Exit Criteria:**
- ✅ Backup folder moved to archives/
- ✅ File count matches (61 files)
- ✅ Checksums validated
- ✅ Epic tracking updated

**Deliverables:**
- Archived folder in `cortex-brain/archives/cortex5-epic/backup-20260107-083422/`
- Updated tracking files

---

### Phase 2: Plan Viewer - Architecture & Data Extraction (30 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** Phase 1

**Tasks:**
1. **Extract Epic Metadata** (10 min)
   - Parse `master-plan.md` (epic title, goals, timeline)
   - Parse `tracking/epic-progress-tracker.json` (10 features, progress %)
   - Parse `tracking/epic-requirements-todo.yaml` (TODO items)
   - Extract folder structure (9 folders, 66 files)
   - Generate file tree JSON for navigation

2. **Design Component Architecture** (10 min)
   ```
   plan-viewer.html
   ├── <header> Epic title + metadata
   ├── <nav> Folder tree (collapsible)
   ├── <main> Content viewer (markdown/code rendering)
   ├── <aside> Progress tracker + stats
   └── <footer> Validation badges + metadata
   ```

3. **Define CSS Architecture** (10 min)
   ```
   :root { --colors, --spacing, --typography }
   .layout { header, nav, main, aside, footer }
   .components { tree-node, file-item, progress-bar }
   .themes { light-mode, dark-mode }
   .responsive { mobile, tablet, desktop }
   .utilities { hidden, active, collapsed }
   ```

**Exit Criteria:**
- ✅ File tree JSON generated with all 66 files
- ✅ Metadata extracted from tracking files
- ✅ Component architecture documented
- ✅ CSS variables defined for theming

**Deliverables:**
- `artifacts/file-tree.json` (hierarchical structure)
- `artifacts/epic-metadata.json` (title, goals, progress)
- `artifacts/viewer-architecture.yaml` (component spec)

---

### Phase 3: Plan Viewer - HTML Structure (45 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** Phase 2

**Tasks:**
1. **Generate Semantic HTML5** (20 min)
   - DOCTYPE, meta tags (charset, viewport, description)
   - Semantic structure: header, nav, main, aside, footer
   - Accessibility attributes: aria-labels, roles, landmarks
   - Navigation tree with nested <ul>/<li> structure
   - Content viewer with <article> sections
   - Progress tracker with <svg> visualization

2. **Implement Interactive Features (Vanilla JS)** (15 min)
   - Folder collapse/expand (toggle .collapsed class)
   - File selection (update main viewer with file content)
   - Search/filter (debounced input handler)
   - Theme toggle (localStorage persistence)
   - Keyboard navigation (arrow keys, Enter, Escape)

3. **Accessibility Implementation** (10 min)
   - Keyboard focus management (visible focus indicators)
   - Screen reader announcements (aria-live regions)
   - Skip navigation links
   - High contrast mode support
   - Focus trap for modal dialogs (if applicable)

**Exit Criteria:**
- ✅ Valid HTML5 structure (no errors)
- ✅ All interactive features functional
- ✅ Keyboard navigation working
- ✅ Screen reader compatible

**Deliverables:**
- `plan-viewer.html` (HTML structure + inline JS)

---

### Phase 4: Plan Viewer - CSS Styling (60 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** Phase 3

**Tasks:**
1. **Layout & Grid System** (15 min)
   - CSS Grid for main layout (header, nav, main, aside, footer)
   - Flexbox for navigation tree and file list
   - Sticky header/sidebar (position: sticky)
   - Responsive breakpoints: 480px, 768px, 1024px, 1440px

2. **Component Styling** (20 min)
   - Navigation tree styling (indentation, icons, hover states)
   - File item styling (badges, hover effects, active state)
   - Progress tracker styling (circular progress, status badges)
   - Content viewer styling (code blocks, headings, lists)
   - Button/input styling (consistent design system)

3. **Theme Implementation** (15 min)
   - Light theme: White backgrounds, dark text, blue accents
   - Dark theme: Dark backgrounds, light text, cyan accents
   - High contrast theme: Pure black/white with orange accents
   - Color contrast ratios: ≥4.5:1 for text, ≥3:1 for UI components

4. **Responsive Design** (10 min)
   - Mobile (<768px): Stacked layout, hamburger menu
   - Tablet (768px-1024px): Side-by-side navigation + content
   - Desktop (>1024px): Full layout with aside panel

**Exit Criteria:**
- ✅ CSS3 valid (no errors)
- ✅ Responsive at all breakpoints
- ✅ Themes toggle smoothly
- ✅ Color contrast ratios compliant

**Deliverables:**
- Inline `<style>` block in plan-viewer.html (CSS complete)

---

### Phase 5: Validation - Zero Tolerance Linting (45 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** Phase 4

**Tasks:**
1. **HTML Validation (W3C)** (10 min)
   ```bash
   # Use W3C validator API or local validator
   curl -H "Content-Type: text/html; charset=utf-8" \
        --data-binary @plan-viewer.html \
        https://validator.w3.org/nu/?out=json
   ```
   - Fix all errors (no warnings allowed)
   - Validate DOCTYPE, meta tags, semantic structure
   - Check for unclosed tags, invalid nesting, deprecated attributes

2. **CSS Validation (CSS3)** (10 min)
   ```bash
   # Use W3C CSS validator
   curl -H "Content-Type: text/css" \
        --data-binary @<(sed -n '/<style>/,/<\/style>/p' plan-viewer.html) \
        https://jigsaw.w3.org/css-validator/validator?output=json
   ```
   - Fix all errors and warnings
   - Validate vendor prefixes, property values, selectors
   - Remove unused CSS rules

3. **Accessibility Audit (WCAG AA)** (15 min)
   ```bash
   # Use axe-core or Pa11y
   npm install -g pa11y
   pa11y --standard WCAG2AA file://$(pwd)/plan-viewer.html
   ```
   - Fix all violations (zero tolerance)
   - Check color contrast (≥4.5:1 for text)
   - Validate ARIA attributes
   - Test keyboard navigation
   - Test screen reader compatibility (VoiceOver on macOS)

4. **JavaScript Linting** (10 min)
   ```bash
   # Extract inline JS and lint with ESLint
   eslint --env browser --no-inline-config <(sed -n '/<script>/,/<\/script>/p' plan-viewer.html)
   ```
   - Fix all errors (no warnings allowed)
   - Validate ES6+ syntax
   - Check for security issues (XSS risks)
   - Validate error handling

**Exit Criteria:**
- ✅ Zero HTML validation errors
- ✅ Zero CSS validation errors
- ✅ Zero accessibility violations
- ✅ Zero JavaScript lint errors
- ✅ Manual testing passed (keyboard, screen reader)

**Deliverables:**
- `validation-reports/html-validation-report.json`
- `validation-reports/css-validation-report.json`
- `validation-reports/accessibility-audit-report.json`
- `validation-reports/javascript-lint-report.txt`

---

### Phase 6: Testing & Finalization (30 minutes)
**Priority:** 🔥 CRITICAL | **Dependencies:** Phase 5

**Tasks:**
1. **Functional Testing** (15 min)
   - Test all interactive features:
     - [x] Folder collapse/expand (all 9 folders)
     - [x] File selection (all 66 files display correctly)
     - [x] Search/filter (matches file names and content previews)
     - [x] Theme toggle (3 themes: light, dark, high-contrast)
     - [x] Keyboard navigation (Tab, Enter, Escape, Arrow keys)
   - Test edge cases:
     - [x] Empty search results
     - [x] Large file content rendering
     - [x] Rapid theme switching
     - [x] Mobile touch interactions

2. **Cross-Browser Testing** (10 min)
   - Safari (primary on macOS)
   - Chrome (secondary)
   - Firefox (tertiary)
   - Mobile Safari (iOS simulator)

3. **Performance Testing** (5 min)
   - File size check (<150KB target)
   - Initial load time (<1 second)
   - Search performance (<100ms)
   - Theme switch performance (<50ms)

**Exit Criteria:**
- ✅ All functional tests passed
- ✅ Cross-browser compatibility verified
- ✅ Performance targets met
- ✅ File size within target

**Deliverables:**
- `testing-reports/functional-test-results.md`
- `testing-reports/cross-browser-test-results.md`
- `testing-reports/performance-test-results.md`

---

### Phase 7: Documentation & Handoff (20 minutes)
**Priority:** 🟡 RECOMMENDED | **Dependencies:** Phase 6

**Tasks:**
1. **Create Viewer Documentation** (10 min)
   - Usage guide (how to navigate, search, toggle themes)
   - Technical documentation (architecture, component breakdown)
   - Maintenance guide (how to regenerate viewer when epic changes)

2. **Update Epic Tracking** (5 min)
   - Add plan-viewer.html to tracking/plan-data.yaml
   - Update CONTINUATION-PROMPT.md with viewer reference
   - Update master-plan.md with viewer link

3. **Create Validation Badge** (5 min)
   - Generate badge SVG showing validation status
   - Add badge to plan-viewer footer
   - Document validation process for future regeneration

**Exit Criteria:**
- ✅ Viewer documented fully
- ✅ Epic tracking updated
- ✅ Validation badge displayed

**Deliverables:**
- `reports/plan-viewer-documentation.md`
- `artifacts/validation-badge.svg`
- Updated tracking files

---

## 📊 Resource Requirements

### Time Estimate
- **Phase 0:** 15 minutes (verification)
- **Phase 1:** 10 minutes (archive)
- **Phase 2:** 30 minutes (architecture)
- **Phase 3:** 45 minutes (HTML)
- **Phase 4:** 60 minutes (CSS)
- **Phase 5:** 45 minutes (validation)
- **Phase 6:** 30 minutes (testing)
- **Phase 7:** 20 minutes (documentation)
- **Total:** 4 hours 15 minutes

### Tools Required
- `diff` (file comparison)
- `sha256sum` (checksum validation)
- `curl` (W3C validators)
- `pa11y` (accessibility auditing)
- `eslint` (JavaScript linting)
- Web browsers (Safari, Chrome, Firefox)

### Dependencies
- No external CSS/JS frameworks (self-contained)
- W3C validators (HTML, CSS)
- Accessibility auditing tools (pa11y or axe-core)

---

## 🎯 Success Metrics

### Archive Success
- ✅ Backup folder moved to archives/
- ✅ 61 files preserved with checksums
- ✅ Manifest created documenting backup history
- ✅ Epic tracking updated with archive reference

### Viewer Success
- ✅ All 66 epic files accessible via viewer
- ✅ Hierarchical navigation functional
- ✅ Search/filter working across all files
- ✅ 3 themes implemented (light, dark, high-contrast)
- ✅ Keyboard navigation complete

### Validation Success
- ✅ **Zero HTML errors** (W3C validator)
- ✅ **Zero CSS errors** (CSS validator)
- ✅ **Zero accessibility violations** (WCAG AA)
- ✅ **Zero JavaScript lint errors** (ESLint)
- ✅ Cross-browser compatibility (Safari, Chrome, Firefox)

### Performance Success
- ✅ File size <150KB
- ✅ Initial load <1 second
- ✅ Search <100ms
- ✅ Theme switch <50ms

---

## 🚨 Risk Mitigation

### Risk 1: Backup Contains Unique Content
**Likelihood:** Low | **Impact:** HIGH  
**Mitigation:** Comprehensive diff in Phase 0, manual review of verification report

### Risk 2: Validation Tools Unavailable
**Likelihood:** Medium | **Impact:** HIGH  
**Mitigation:** Use online validators (W3C API), fallback to manual review

### Risk 3: File Size Exceeds 150KB
**Likelihood:** Medium | **Impact:** Medium  
**Mitigation:** Minify CSS/JS, remove unused code, optimize SVG assets

### Risk 4: Accessibility Violations Difficult to Fix
**Likelihood:** Low | **Impact:** HIGH  
**Mitigation:** Follow WCAG AA guidelines from start, test incrementally

---

## 📝 Next Steps After Completion

1. **Generate Viewer for Other Active Plans** (if applicable)
   - Apply same process to other epics/features
   - Create reusable generator script

2. **Automate Viewer Regeneration**
   - Create script to regenerate viewer when epic changes
   - Add to CI/CD pipeline (if applicable)

3. **Archive Historical Backups**
   - Review other backup folders in workspace
   - Apply same archival process

---

## 🎉 Completion Criteria

**This plan is complete when:**
- ✅ Backup archived with manifest
- ✅ Plan viewer generated and validated
- ✅ Zero errors in all validation categories
- ✅ All interactive features tested and working
- ✅ Documentation complete
- ✅ Epic tracking updated

**Final Deliverable:** Production-grade `plan-viewer.html` in cortex5-epic root folder

---

**Plan Status:** ⏳ READY FOR EXECUTION  
**Next Action:** Execute Phase 0 (Pre-Archive Verification)
