# 🎨 Glassmorphism CSS Standardization Plan
## GitHub Pages Design System with Named Panel Taxonomy

**Plan ID:** `glassmorphism-css-standardization`  
**Status:** 🟢 ACTIVE  
**Created:** 2026-01-03  
**Author:** Asif Hussain  
**Target:** `docs/` folder (GitHub Pages deployment)

---

## 📋 Executive Summary

**Objective:** Create a unified glassmorphism design system for CORTEX documentation with named panel taxonomy, enabling semantic styling commands like "style panel X like panel Y".

**Vision Context (from attached images):**
- **Image 1:** CORTEX Lens dashboard showing "Tetris" (top grid layout) + "Intro" (bottom description card)
- **Image 2:** "Compact Cards" (5-card horizontal row for key capabilities)
- **Image 3:** "Grid Cards" (6-card grid for analysis capabilities)

**Core Innovation:** Named panel system allowing CORTEX to apply consistent styles via natural language commands.

---

## 🎯 Goals

### Primary Goals
1. **Named Panel Taxonomy:** Define 8-12 unique panel styles with semantic names
2. **CSS Consolidation:** Merge 24+ CSS files into unified design system
3. **GitHub Pages Optimization:** Ensure fast loading, mobile responsiveness
4. **CORTEX Integration:** Enable "style X like Y" command routing

### Secondary Goals
5. **Pattern Library:** Document all glassmorphism patterns with examples
6. **Design Tokens:** Extract CSS variables for consistent theming
7. **Performance:** Reduce CSS bloat, optimize backdrop-filter usage
8. **Accessibility:** Ensure WCAG 2.1 AA compliance

---

## 🧩 Named Panel Taxonomy (Initial Design)

Based on vision analysis and existing patterns:

| Panel Name | Use Case | Visual Signature | CSS Class |
|------------|----------|------------------|-----------|
| **Tetris** | Dashboard grid, metrics display | Compact tiles, horizontal layout, icon+value pairs | `.panel-tetris` |
| **Intro** | Hero sections, feature descriptions | Large centered card, gradient background, descriptive text | `.panel-intro` |
| **Compact Cards** | Capability highlights, feature lists | 5-6 cards horizontal row, icon+title+description | `.panel-compact-cards` |
| **Grid Cards** | Detailed listings, analysis views | 2x3 or 3x3 grid, detailed content, badges | `.panel-grid-cards` |
| **Hero Glass** | Landing sections, CTAs | Full-width, strong blur, centered content | `.panel-hero-glass` |
| **Sidebar Glass** | Navigation, filters, metadata | Vertical layout, sticky positioning, subtle blur | `.panel-sidebar-glass` |
| **Modal Glass** | Overlays, dialogs, confirmations | Centered overlay, strong backdrop, dismiss actions | `.panel-modal-glass` |
| **Toast Glass** | Notifications, alerts, status messages | Small floating panel, auto-dismiss, icon+message | `.panel-toast-glass` |
| **Blob Glass** | Decorative elements, backgrounds | Organic shapes, liquid morphing, subtle animations | `.panel-blob-glass` |
| **Neon Glass** | Accent panels, highlights, CTAs | Glowing borders, vibrant colors, high contrast | `.panel-neon-glass` |

---

## 📊 Current State Analysis

### CSS Files Discovered (24 files)
```
docs/assets/css/
├── glass-patterns.css         ← 1024 lines, comprehensive patterns
├── main.css                   ← Core styles
├── intentional-classes.css    ← Utility classes
├── index-multipanel.css       ← Multi-panel layouts
├── variables.css              ← Design tokens
├── micro-interactions.css     ← Animations
└── [18 other CSS files]

docs/technical/assets/styles/
├── glassmorphism.css          ← Technical docs glass theme
└── shared-styles.css          ← Shared orchestrator docs

docs/lens/index.html           ← Inline styles (Tetris override)
```

### Glassmorphism Patterns Detected
- **Backdrop-filter:** 20+ occurrences (`blur(10px)` to `blur(25px)`)
- **Gradient borders:** Linear gradients on borders
- **Box shadows:** Multi-layer depth effects
- **RGBA backgrounds:** Transparent backgrounds (0.4-0.7 opacity)
- **Hover transitions:** Transform + blur enhancements

### Inconsistencies Found
1. **Blur values:** Inconsistent (5px, 10px, 20px, 25px)
2. **Border styles:** Some gradient borders, some solid borders
3. **Shadow depths:** Varying shadow strengths
4. **Naming conventions:** `.glass-card` vs `.glass-panel` vs `.tetris-panel`
5. **Inline styles:** Tetris override in `lens/index.html` (lines 45-83)

---

## 🏗️ Architecture Design

### Design System Structure
```
docs/assets/css/
├── cortex-glass-system.css           ← Master import file
├── glass-design-tokens.css           ← CSS variables (colors, blur, spacing)
├── glass-base-patterns.css           ← 5 core patterns (from glass-patterns.css)
├── glass-named-panels.css            ← NEW: 10 named panel styles
├── glass-ui-components.css           ← Modals, toasts, dropdowns
├── glass-animations.css              ← Hover, focus, loading states
└── glass-utilities.css               ← Helper classes (blur-lg, shadow-deep, etc.)
```

### Panel Taxonomy Implementation
```css
/* glass-named-panels.css */

/* TETRIS PANEL: Compact metrics grid */
.panel-tetris {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
    /* Base glassmorphism from tokens */
    background: var(--glass-bg-base);
    backdrop-filter: blur(var(--glass-blur-md));
    border: 1px solid var(--glass-border-subtle);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
}

.panel-tetris .tile {
    /* Horizontal icon+value layout */
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem;
    background: var(--glass-bg-tile);
    border-radius: var(--radius-md);
}

/* INTRO PANEL: Hero description card */
.panel-intro {
    max-width: 800px;
    margin: 0 auto;
    background: linear-gradient(135deg, 
        var(--glass-bg-hero-start), 
        var(--glass-bg-hero-end)
    );
    backdrop-filter: blur(var(--glass-blur-lg));
    border: 1px solid var(--glass-border-accent);
    box-shadow: var(--shadow-hero);
    padding: var(--space-2xl);
    text-align: center;
}

/* COMPACT CARDS PANEL: Horizontal capability row */
.panel-compact-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    padding: var(--space-xl);
}

.panel-compact-cards .card {
    background: var(--glass-bg-card);
    backdrop-filter: blur(var(--glass-blur-md));
    padding: 1.5rem;
    border-radius: var(--radius-md);
    transition: var(--transition-glass);
}

/* ... (remaining 7 panel styles) ... */
```

---

## 🔧 Implementation Phases

### **Phase 1: Discovery & Documentation** (2 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ✅ Audit all CSS files in `docs/` (COMPLETED via grep_search)
2. ⬜ Extract all glassmorphism patterns to spreadsheet
3. ⬜ Screenshot existing panels for visual reference
4. ⬜ Map current class names to proposed panel taxonomy
5. ⬜ Document design token values (blur, colors, shadows)

**Deliverables:**
- `context/css-audit-report.md`
- `context/glassmorphism-patterns-inventory.csv`
- `context/visual-reference-screenshots/` (10+ images)
- `artifacts/design-tokens-extraction.json`

---

### **Phase 2: Design Token Extraction** (3 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Create `glass-design-tokens.css` with CSS variables
2. ⬜ Define blur values: `--glass-blur-sm` (10px), `--glass-blur-md` (20px), `--glass-blur-lg` (30px)
3. ⬜ Define background colors: `--glass-bg-base`, `--glass-bg-hover`, `--glass-bg-active`
4. ⬜ Define border styles: `--glass-border-subtle`, `--glass-border-accent`, `--glass-border-neon`
5. ⬜ Define shadow depths: `--shadow-glass-sm`, `--shadow-glass-md`, `--shadow-glass-lg`
6. ⬜ Define animation durations: `--transition-glass`, `--transition-morph`

**Deliverables:**
- `docs/assets/css/glass-design-tokens.css`
- `artifacts/design-tokens-documentation.md`

---

### **Phase 3: Named Panel System Creation** (4 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Create `glass-named-panels.css` with 10 panel styles
2. ⬜ Implement `.panel-tetris` (grid metrics layout)
3. ⬜ Implement `.panel-intro` (hero description card)
4. ⬜ Implement `.panel-compact-cards` (horizontal capability row)
5. ⬜ Implement `.panel-grid-cards` (2x3/3x3 detailed grid)
6. ⬜ Implement remaining 6 panel styles
7. ⬜ Add hover states, focus states, active states
8. ⬜ Add responsive breakpoints (mobile, tablet, desktop)

**Deliverables:**
- `docs/assets/css/glass-named-panels.css`
- `artifacts/panel-style-guide.html` (visual examples)

---

### **Phase 4: CSS Consolidation** (5 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Merge duplicate glassmorphism patterns from 24 CSS files
2. ⬜ Refactor `glass-patterns.css` (1024 lines) → modular files
3. ⬜ Remove inline styles from `lens/index.html` → use `.panel-tetris`
4. ⬜ Update `main.css` to import new design system
5. ⬜ Create `cortex-glass-system.css` master import file
6. ⬜ Remove deprecated CSS files (backup first)
7. ⬜ Validate no broken styles across 30+ HTML pages

**Deliverables:**
- `docs/assets/css/cortex-glass-system.css` (master import)
- `docs/assets/css/glass-base-patterns.css` (5 core patterns)
- `docs/assets/css/glass-ui-components.css` (modals, toasts, etc.)
- `reports/css-consolidation-report.md` (before/after metrics)

---

### **Phase 5: CORTEX Integration** (3 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Create `src/orchestrators/styling/panel_styler.py`
2. ⬜ Implement panel taxonomy mapping (`tetris` → `.panel-tetris`)
3. ⬜ Add command parsing for "style X like Y"
4. ⬜ Integrate with Master Orchestrator routing
5. ⬜ Add panel preview generator (HTML + CSS)
6. ⬜ Test styling commands in Copilot Chat

**Example Commands:**
```
"style the metrics dashboard like tetris panel"
→ Apply .panel-tetris class

"make this section look like compact cards"
→ Apply .panel-compact-cards class

"use grid cards layout for analysis section"
→ Apply .panel-grid-cards class
```

**Deliverables:**
- `src/orchestrators/styling/panel_styler.py`
- `cortex-brain/manifests/orchestrators/panel-styling-manifest.yaml`
- `artifacts/styling-command-examples.md`

---

### **Phase 6: GitHub Pages Optimization** (3 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Minify all CSS files (reduce from ~3000 lines to ~1500 lines)
2. ⬜ Optimize backdrop-filter usage (CPU-intensive)
3. ⬜ Add preload hints for critical CSS
4. ⬜ Test mobile performance (iOS Safari, Chrome Mobile)
5. ⬜ Validate W3C CSS standards
6. ⬜ Test cross-browser compatibility (Firefox, Edge, Safari)
7. ⬜ Deploy to GitHub Pages staging branch

**Performance Targets:**
- CSS load time: <100ms
- First Contentful Paint: <1.5s
- Lighthouse Performance: >90

**Deliverables:**
- `docs/assets/css/*.min.css` (minified versions)
- `reports/performance-optimization-report.md`
- GitHub Pages staging deployment

---

### **Phase 7: Documentation & Style Guide** (2 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Create `docs/design-system/glassmorphism-guide.html`
2. ⬜ Document all 10 named panels with examples
3. ⬜ Create interactive panel selector tool
4. ⬜ Write migration guide for existing HTML pages
5. ⬜ Create video tutorial (5 min screencast)
6. ⬜ Update main `docs/index.html` with design system link

**Deliverables:**
- `docs/design-system/glassmorphism-guide.html`
- `docs/design-system/panel-selector.html` (interactive)
- `docs/design-system/migration-guide.md`
- `assets/videos/panel-styling-tutorial.mp4`

---

### **Phase 8: Testing & Validation** (3 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Visual regression testing (30+ HTML pages)
2. ⬜ WCAG 2.1 AA accessibility audit
3. ⬜ Color contrast testing (all text on glass backgrounds)
4. ⬜ Keyboard navigation testing
5. ⬜ Screen reader testing (NVDA, JAWS)
6. ⬜ Mobile device testing (iOS 15+, Android 12+)
7. ⬜ Cross-browser testing (Chrome, Firefox, Safari, Edge)

**Deliverables:**
- `reports/visual-regression-report.html`
- `reports/accessibility-audit-report.md`
- `reports/cross-browser-test-results.md`

---

### **Phase 9: Migration & Deployment** (4 hours)
**Status:** ⬜ NOT STARTED

**Tasks:**
1. ⬜ Backup existing CSS files to `backups/css-pre-standardization/`
2. ⬜ Update all 30+ HTML files to use new panel classes
3. ⬜ Remove inline styles from `lens/index.html`
4. ⬜ Update `docs/index.html` with new panel styles
5. ⬜ Deploy to GitHub Pages production
6. ⬜ Monitor for broken styles (24-hour watch)
7. ⬜ Create rollback plan

**Deliverables:**
- GitHub Pages production deployment
- `backups/css-pre-standardization/` (rollback archive)
- `reports/deployment-checklist.md`

---

### **Phase 10: REFACTOR & Cleanup** (2 hours)
**Status:** ⬜ NOT STARTED

**SKULL Rule Enforcement:** Remove all orphaned code, duplicates, and bloat.

**Tasks:**
1. ⬜ Delete deprecated CSS files (18 files → 7 files)
2. ⬜ Remove unused CSS classes (grep search across HTML)
3. ⬜ Consolidate duplicate selectors
4. ⬜ Remove commented-out code
5. ⬜ Validate no broken imports
6. ⬜ Run final CSS linter
7. ⬜ Update `.gitignore` for CSS build artifacts

**Deliverables:**
- Clean CSS architecture (7 core files)
- `reports/refactor-cleanup-report.md`
- Git commit: "REFACTOR: Glassmorphism CSS standardization complete"

---

## 📈 Progress Tracking

### Overall Progress
```
[▓▓▓░░░░░░░░░░░░░░░░░] 10% Complete (Phase 1: 20% done)
```

### Phase Progress
| Phase | Status | Progress | Est. Time | Actual Time |
|-------|--------|----------|-----------|-------------|
| 1. Discovery | 🟡 IN PROGRESS | 20% | 2h | 0.5h |
| 2. Design Tokens | ⬜ NOT STARTED | 0% | 3h | - |
| 3. Named Panels | ⬜ NOT STARTED | 0% | 4h | - |
| 4. Consolidation | ⬜ NOT STARTED | 0% | 5h | - |
| 5. CORTEX Integration | ⬜ NOT STARTED | 0% | 3h | - |
| 6. GitHub Pages | ⬜ NOT STARTED | 0% | 3h | - |
| 7. Documentation | ⬜ NOT STARTED | 0% | 2h | - |
| 8. Testing | ⬜ NOT STARTED | 0% | 3h | - |
| 9. Deployment | ⬜ NOT STARTED | 0% | 4h | - |
| 10. REFACTOR | ⬜ NOT STARTED | 0% | 2h | - |

**Total Estimated Time:** 31 hours  
**Completion Target:** 2026-01-07

---

## 🎨 Visual Examples (from attached images)

### Image 1: CORTEX Lens Dashboard
- **Top Section:** Tetris panel (6-tile metrics grid)
  - AST Analysis, Pattern Detect, Intel Extract, Deps Map, 30 Score, Jan 2026
- **Bottom Section:** Intro panel (description card)
  - "What Is CORTEX Lens?" + actionable intelligence description

### Image 2: Key Capabilities
- **Layout:** Compact Cards panel (5-card horizontal row)
  - AST Analysis, Pattern Detection, Dependency Mapping, Intelligence Extraction, Reverse Engineering
  - Each card: Icon + Title + 2-line description

### Image 3: Analysis Capabilities
- **Layout:** Grid Cards panel (3x2 grid)
  - AST Analysis, Pattern Detection, Dependency Mapping
  - Architecture Extraction, Code Smell Detection, Complexity Metrics
  - Each card: Larger icon + Title + 3-line description + badges

---

## 🛡️ Brain Protection (SKULL) Rules

### Planning Isolation
✅ **This is a PLAN, not implementation**  
- No code changes until plan approved
- All phases clearly defined
- REFACTOR phase mandatory (Phase 10)

### Holistic Discovery
✅ **Search before create**  
- 24 CSS files discovered via file_search
- Existing patterns documented
- No duplicate creation

### Git Isolation
✅ **Backup strategy defined**  
- Phase 9: Backup to `backups/css-pre-standardization/`
- Rollback plan included
- No destructive changes without backup

---

## 📝 Copilot Instructions

When implementing this plan, Copilot MUST:

```yaml
response_template: "autonomous_execution_progress"
tdd_enforcement: false  # CSS refactoring, not code
final_refactor_required: true  # Phase 10 mandatory
visual_validation_required: true  # Screenshots for each phase
backup_before_changes: true  # Phase 9 backup step
github_pages_testing: true  # Deploy to staging first
```

---

## 🔗 Related Resources

- **Design System Reference:** `docs/assets/css/glass-patterns.css` (existing patterns)
- **Response Template:** `cortex-brain/response-templates-v4.yaml:863` (progress tracking)
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Deployment Guide:** `DEPLOYMENT.md`

---

## 📊 Success Metrics

### Technical Metrics
- **CSS File Count:** 24 → 7 files (70% reduction)
- **CSS Total Lines:** ~3000 → ~1500 lines (50% reduction)
- **Load Time:** <100ms for all CSS
- **Lighthouse Score:** >90 Performance, >95 Accessibility

### User Experience Metrics
- **Panel Taxonomy:** 10 named panels documented
- **Command Success Rate:** >95% for "style X like Y" commands
- **Visual Consistency:** 100% of pages use named panels
- **Mobile Responsiveness:** All panels work on 320px+ screens

### Developer Experience Metrics
- **Style Guide Completeness:** Interactive examples for all 10 panels
- **Migration Ease:** <5 min per HTML page
- **CORTEX Integration:** Natural language styling commands work

---

## 🎉 Definition of Done

This plan is COMPLETE when:

1. ✅ All 10 phases executed successfully
2. ✅ 10 named panels documented with examples
3. ✅ GitHub Pages deployed with new design system
4. ✅ CORTEX "style X like Y" commands functional
5. ✅ All tests passing (visual, accessibility, performance)
6. ✅ Phase 10 REFACTOR completed (orphaned code removed)
7. ✅ Style guide published at `docs/design-system/glassmorphism-guide.html`

---

**Generated by:** CORTEX Planning System (Manual Fallback)  
**Plan Location:** `cortex-brain/documents/planning/active/glassmorphism-css-standardization/`  
**Next Step:** Execute Phase 1 - Discovery & Documentation
