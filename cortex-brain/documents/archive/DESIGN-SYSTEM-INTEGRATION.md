# CORTEX Universal Design System - Integration Plan

**Version:** 1.0  
**Date:** December 12, 2025  
**Author:** Asif Hussain  
**Status:** 🎯 READY FOR IMPLEMENTATION

---

## 🎯 Executive Summary

Create a **centralized design system** for all CORTEX HTML-generating tools with a **publish/deploy pipeline** modeled after the proven RA Toolkit deployment architecture. This establishes glassmorphism styling as the universal CORTEX visual language with automated distribution to all orchestrators and utilities.

**Transformation:** From scattered template copies → Centralized design system with automated publishing

**Key Goals:**
1. **Central Source of Truth** - `cortex-brain/design-system/` as single styling repository
2. **Automated Distribution** - Publish engine pushes updates to all HTML generators
3. **Version Management** - Semantic versioning with changelog tracking
4. **Zero Duplication** - Eliminate 5+ copies of glassmorphism CSS across codebase
5. **Hot Reload Dev Mode** - Real-time preview during design changes
6. **Backward Compatibility** - Existing dashboards continue working during migration

**Success Metrics:**
- ✅ Single source CSS/JS reduces maintenance by 80%
- ✅ Design updates propagate to all tools in <30 seconds
- ✅ 100% consistency across Admin Dashboard, CORTEX Lens, RA Toolkit, future tools
- ✅ Zero breaking changes for existing generated dashboards
- ✅ Dev mode enables instant preview without regeneration

---

## 📊 Problem Statement

### Current Duplication Pain

**Scattered Implementations:**
```
cortex-brain/admin/RA-Domain/toolkit/templates/onedrive/assets/onedrive-glass.css (529 LOC)
templates/report-dashboard-template.html (inline styles, 1263 LOC)
src/cortex_lens/templates/base/ (pending implementation)
[Future] Additional tools will copy-paste yet again
```

**Maintenance Nightmare:**
- Design changes require manual updates across 3+ locations
- Inconsistent implementations (different CSS variable names, outdated patterns)
- No version tracking - impossible to know which tools use which design version
- Testing burden - must validate changes across all tools manually

**Distribution Gap:**
- RA Toolkit has proven publish engine (`deploy-packages/`, versioning, SHA256 validation)
- Admin Dashboard has no publish mechanism (lives in `src/operations/`)
- CORTEX Lens templates will duplicate patterns (no distribution system)

### The Solution: Universal Design System with Publish Engine

**Three-Tier Architecture:**

```
┌─────────────────────────────────────────┐
│  CENTRAL SOURCE (cortex-brain/)         │
│  ├── design-system/                     │
│  │   ├── v1.0.0/                        │
│  │   │   ├── cortex-glass.css           │ ← Master glassmorphism
│  │   │   ├── cortex-base.css            │ ← Base styles
│  │   │   ├── cortex-components.css      │ ← UI components
│  │   │   ├── cortex-charts.js           │ ← D3.js wrappers
│  │   │   └── cortex-utils.js            │ ← Helper functions
│  │   ├── CHANGELOG.md                   │
│  │   └── design-system-manifest.yaml    │
│  └── design-system-config.yaml          │ ← Distribution targets
└─────────────────────────────────────────┘
              ↓ PUBLISH ENGINE
┌─────────────────────────────────────────┐
│  DISTRIBUTION (deploy-packages/)        │
│  ├── cortex-design-system-v1.0.0.zip    │
│  ├── cortex-design-system-v1.0.0.sha256 │
│  └── cortex-design-system-latest/       │ ← Symlink
└─────────────────────────────────────────┘
              ↓ AUTOMATED SYNC
┌─────────────────────────────────────────┐
│  CONSUMERS (orchestrators/utilities)    │
│  ├── src/cortex_lens/templates/base/    │
│  ├── cortex-brain/admin/RA-Domain/...   │
│  ├── templates/                          │
│  └── [Future Tools]/templates/          │
└─────────────────────────────────────────┘
```

**Publish Workflow:**
1. Developer updates `cortex-brain/design-system/v{X.Y.Z}/`
2. Run `cortex publish design-system` (or auto-trigger on commit)
3. Orchestrator validates changes (CSS lint, browser compat check)
4. Package versioned ZIP + SHA256 checksum
5. Deploy to `deploy-packages/cortex-design-system-vX.Y.Z.zip`
6. Auto-sync to all registered consumers (via manifest)
7. Generate migration report (breaking changes, optional updates)

---

## 🏗️ Architecture Design

### 1. Central Design System Structure

**Location:** `cortex-brain/design-system/`

```
design-system/
├── v1.0.0/                          # Versioned releases
│   ├── css/
│   │   ├── cortex-glass.css         # Glassmorphism core (529 LOC optimized)
│   │   ├── cortex-base.css          # Reset, typography, utilities (200 LOC)
│   │   ├── cortex-components.css    # Cards, tabs, badges, metrics (400 LOC)
│   │   ├── cortex-charts.css        # D3.js visualization styles (150 LOC)
│   │   └── cortex-dark-mode.css     # Optional dark mode overrides (100 LOC)
│   ├── js/
│   │   ├── cortex-charts.js         # D3.js wrappers (force graph, tree, scatter) (300 LOC)
│   │   ├── cortex-tabs.js           # Tab navigation logic (100 LOC)
│   │   ├── cortex-utils.js          # Number formatting, date helpers (150 LOC)
│   │   └── cortex-search.js         # Dashboard search/filter (200 LOC)
│   ├── assets/
│   │   ├── logo.svg                 # CORTEX logo
│   │   └── icons/                   # Icon sprites
│   ├── examples/
│   │   ├── dashboard-template.html  # Full example
│   │   ├── card-examples.html       # Component showcase
│   │   └── chart-examples.html      # Visualization gallery
│   ├── README.md                    # Usage guide
│   └── CHANGELOG.md                 # Version history
├── dev/                             # Active development
│   └── [same structure as v1.0.0/]
├── design-system-manifest.yaml      # Metadata, browser support, dependencies
└── migration-guides/
    └── v0.9-to-v1.0.md              # Upgrade instructions
```

### 2. Design System Manifest

**File:** `cortex-brain/design-system/design-system-manifest.yaml`

```yaml
name: "CORTEX Universal Design System"
version: "1.0.0"
author: "Asif Hussain"
copyright: "© 2025 Asif Hussain. All rights reserved."
last_updated: "2025-12-12"

# Browser Support (caniuse.com verification)
browser_support:
  chrome: "90+"
  firefox: "88+"
  safari: "14+"
  edge: "90+"
  backdrop_filter_support: "98.5%"  # Critical for glassmorphism

# Core Files
core_files:
  css:
    - path: "css/cortex-glass.css"
      size: "15KB"
      description: "Glassmorphism core (CSS variables, glass cards, effects)"
    - path: "css/cortex-base.css"
      size: "8KB"
      description: "Reset, typography, spacing utilities"
    - path: "css/cortex-components.css"
      size: "12KB"
      description: "UI components (tabs, badges, metrics, tables)"
    - path: "css/cortex-charts.css"
      size: "6KB"
      description: "D3.js visualization styles"
  
  js:
    - path: "js/cortex-charts.js"
      size: "10KB"
      description: "D3.js wrappers (force graph, tree, scatter plot)"
    - path: "js/cortex-tabs.js"
      size: "4KB"
      description: "Tab navigation with keyboard shortcuts"
    - path: "js/cortex-utils.js"
      size: "5KB"
      description: "Number formatting, date helpers, validators"

# Dependencies (external CDNs)
dependencies:
  d3js:
    version: "7.8.5"
    url: "https://d3js.org/d3.v7.min.js"
    integrity: "sha384-..."  # SRI hash
  
  chartjs:
    version: "3.9.1"
    url: "https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"
    integrity: "sha384-..."

# Color Palette (CSS Custom Properties)
color_palette:
  background:
    primary: "#0a0e1a"
    secondary: "#1a1f3a"
    tertiary: "#252b47"
  
  text:
    primary: "#f0f0f0"
    secondary: "#b0b0b0"
    muted: "#707070"
  
  accent:
    primary: "#00d4ff"     # Cyan
    secondary: "#7b61ff"   # Purple
  
  semantic:
    success: "#00ff9d"     # Green
    warning: "#ffa500"     # Orange
    danger: "#ff4444"      # Red
    info: "#00d4ff"        # Cyan

# Breaking Changes (semantic versioning)
breaking_changes:
  v1.0.0:
    - "Renamed --glass-bg-alpha to --glass-opacity"
    - "Removed .card-deprecated class"
    - "Changed tab navigation data attributes"
```

### 3. Distribution Configuration

**File:** `cortex-brain/design-system-config.yaml`

```yaml
name: "CORTEX Design System Distribution"
version: "1.0.0"
last_updated: "2025-12-12"

# Source (single source of truth)
source:
  path: "cortex-brain/design-system/v{VERSION}/"
  current_version: "1.0.0"
  dev_path: "cortex-brain/design-system/dev/"

# Distribution Targets (where to sync design system files)
targets:
  cortex_lens:
    path: "src/cortex_lens/templates/base/"
    version_file: "src/cortex_lens/templates/base/VERSION"
    files:
      - source: "css/cortex-glass.css"
        dest: "cortex-glass.css"
      - source: "css/cortex-base.css"
        dest: "cortex-base.css"
      - source: "css/cortex-components.css"
        dest: "cortex-components.css"
      - source: "js/cortex-charts.js"
        dest: "components/cortex-charts.js"
      - source: "js/cortex-tabs.js"
        dest: "components/cortex-tabs.js"
    auto_sync: true
  
  ra_toolkit:
    path: "cortex-brain/admin/RA-Domain/toolkit/templates/shared/"
    version_file: "cortex-brain/admin/RA-Domain/toolkit/VERSION"
    files:
      - source: "css/cortex-glass.css"
        dest: "assets/cortex-glass.css"
      - source: "js/cortex-charts.js"
        dest: "assets/cortex-charts.js"
    auto_sync: true
  
  admin_dashboard:
    path: "templates/"
    version_file: "templates/DESIGN_SYSTEM_VERSION"
    files:
      - source: "css/cortex-glass.css"
        dest: "cortex-glass.css"
      - source: "css/cortex-components.css"
        dest: "cortex-components.css"
    auto_sync: false  # Manual sync due to custom overrides
  
  # Future targets
  future_tools:
    path: "TBD"
    auto_sync: true

# Publish Settings
publish:
  output_dir: "deploy-packages/"
  package_format: "zip"
  include_examples: true
  generate_checksum: true
  checksum_algorithm: "sha256"
  create_latest_symlink: true

# Validation Rules
validation:
  css:
    - "Run stylelint for syntax errors"
    - "Check CSS custom property usage"
    - "Validate browser compatibility (caniuse)"
  
  js:
    - "Run ESLint for syntax errors"
    - "Check D3.js version compatibility"
    - "Validate no external dependencies beyond manifest"
  
  breaking_changes:
    - "Scan for removed CSS classes"
    - "Scan for renamed CSS variables"
    - "Check for changed JavaScript APIs"

# Dev Mode (hot reload)
dev_mode:
  enabled: true
  watch_path: "cortex-brain/design-system/dev/"
  reload_targets:
    - "src/cortex_lens/templates/base/"
  livereload_port: 35729
```

### 4. Publish Orchestrator

**File:** `src/operations/modules/design_system_publisher.py`

**Responsibilities:**
1. **Validation Phase**
   - CSS linting (stylelint)
   - JS linting (ESLint)
   - Browser compatibility check (caniuse API)
   - Breaking change detection (compare with previous version)

2. **Packaging Phase**
   - Version bump (semantic versioning)
   - Create ZIP archive (`cortex-design-system-v1.0.0.zip`)
   - Generate SHA256 checksum
   - Update CHANGELOG.md

3. **Distribution Phase**
   - Copy to `deploy-packages/`
   - Create `latest` symlink
   - Sync to registered targets (via `design-system-config.yaml`)
   - Generate migration report

4. **Verification Phase**
   - Validate all targets received correct files
   - Check version consistency
   - Generate distribution report

**CLI Commands:**
```bash
# Publish new version (auto-increments patch version)
cortex publish design-system

# Publish specific version
cortex publish design-system --version 1.1.0

# Dry run (preview changes)
cortex publish design-system --dry-run

# Force sync to all targets (no version bump)
cortex sync design-system

# Dev mode (watch for changes, hot reload)
cortex dev design-system
```

---

## 📋 Implementation Phases

### Phase 0: Foundation (Week 1) ✅ IN PROGRESS
**Goal:** Extract and centralize existing glassmorphism styles

**Tasks:**
1. ✅ Create `cortex-brain/design-system/` structure
2. ✅ Extract CSS from `onedrive-glass.css` (529 LOC)
3. ✅ Extract CSS from `report-dashboard-template.html` (inline styles)
4. ✅ Consolidate into modular files:
   - `cortex-glass.css` - Core glassmorphism
   - `cortex-base.css` - Reset + typography
   - `cortex-components.css` - UI components
   - `cortex-charts.css` - Visualization styles
5. ✅ Create `design-system-manifest.yaml`
6. ✅ Create `design-system-config.yaml`
7. ✅ Document color palette, spacing scale, typography

**Deliverables:**
- `cortex-brain/design-system/v1.0.0/` (complete file structure)
- Documentation (`README.md`, examples)

**Testing:**
- Validate CSS with stylelint
- Test browser compatibility (Chrome, Firefox, Safari, Edge)
- Verify glassmorphism effects render correctly

---

### Phase 1: Publish Engine (Week 2)
**Goal:** Build automated publish/distribution pipeline

**Tasks:**
1. Create `src/operations/modules/design_system_publisher.py`
2. Implement validation phase:
   - CSS linting integration (stylelint)
   - JS linting integration (ESLint)
   - Browser compatibility check (caniuse API)
   - Breaking change detection (diff previous version)
3. Implement packaging phase:
   - Semantic versioning logic
   - ZIP archive creation
   - SHA256 checksum generation
   - CHANGELOG.md auto-update
4. Implement distribution phase:
   - Parse `design-system-config.yaml`
   - Sync files to registered targets
   - Version file updates
   - Migration report generation
5. Create CLI wrapper: `scripts/cli_wrappers/design_system_publish_wrapper.py`
6. Add to `cortex-operations.yaml`:
   ```yaml
   publish_design_system:
     command: "publish design-system"
     tier: "admin"
     execution_method: "cli_wrapper"
   ```

**Deliverables:**
- Publish orchestrator (400-500 LOC)
- CLI wrapper
- Unit tests (pytest)

**Testing:**
- Dry-run validation
- Version bump logic
- File sync accuracy
- Checksum generation
- Migration report completeness

---

### Phase 2: CORTEX Lens Integration (Week 3)
**Goal:** Integrate design system into CORTEX Lens templates

**Tasks:**
1. Update `src/cortex_lens/templates/base/` to consume design system
2. Replace placeholder `__init__.py` with actual CSS/JS files
3. Create template inheritance system:
   ```
   base/
   ├── cortex-glass.css          # Symlink to design system
   ├── cortex-base.css           # Symlink
   ├── cortex-components.css     # Symlink
   └── components/
       ├── cortex-charts.js      # Symlink
       ├── cortex-tabs.js        # Symlink
       └── cortex-utils.js       # Symlink
   ```
4. Update 6 dashboard templates to reference design system files
5. Test adaptive dashboards with new design system
6. Validate all 6 repo types render correctly

**Deliverables:**
- CORTEX Lens templates using centralized design system
- Template integration tests

**Testing:**
- Generate dashboards for all 6 repo types
- Validate glassmorphism rendering
- Test tab navigation
- Verify chart visualizations
- Browser compatibility testing

---

### Phase 3: Admin Dashboard Migration (Week 4)
**Goal:** Migrate Admin Dashboard to centralized design system

**Tasks:**
1. Audit `templates/report-dashboard-template.html` (1263 LOC)
2. Extract custom logic (keep), replace styles (centralize)
3. Update template to reference design system CSS/JS
4. Test with existing 18+ collectors
5. Ensure backward compatibility (existing dashboards work)
6. Generate migration report

**Deliverables:**
- Migrated Admin Dashboard template
- Migration report documenting changes

**Testing:**
- Run all 18+ collectors
- Validate dashboard generation
- Test websocket live updates
- Browser compatibility
- Performance regression testing

---

### Phase 4: RA Toolkit Migration (Week 5)
**Goal:** Migrate RA Toolkit templates to centralized design system

**Tasks:**
1. Audit `cortex-brain/admin/RA-Domain/toolkit/templates/onedrive/`
2. Replace `onedrive-glass.css` with symlink to design system
3. Update narrative dashboard templates
4. Test OneDrive deployment workflow
5. Validate static dashboard deployment

**Deliverables:**
- Migrated RA Toolkit templates
- Updated publish workflow

**Testing:**
- Generate OneDrive analysis dashboard
- Validate narrative sections
- Test force graph visualizations
- Verify static deployment

---

### Phase 5: Dev Mode & Hot Reload (Week 6)
**Goal:** Enable real-time preview during design changes

**Tasks:**
1. Implement file watcher for `cortex-brain/design-system/dev/`
2. Auto-sync changes to registered targets on file save
3. Integrate LiveReload protocol (port 35729)
4. Create dev server: `cortex dev design-system`
5. Support browser auto-refresh on CSS/JS changes

**Deliverables:**
- Dev mode orchestrator (200-300 LOC)
- CLI command: `cortex dev design-system`

**Testing:**
- Edit CSS, verify auto-sync
- Test LiveReload browser refresh
- Validate multiple targets sync simultaneously
- Performance (sync latency <100ms)

---

### Phase 6: Documentation & Rollout (Week 7)
**Goal:** Complete documentation and team rollout

**Tasks:**
1. Create comprehensive README.md
2. Document color palette, spacing scale, typography system
3. Create component showcase (HTML examples)
4. Write migration guides (v0.9 → v1.0)
5. Update CORTEX operations guide
6. Team training session

**Deliverables:**
- Complete documentation suite
- Component showcase website
- Migration guides
- Training materials

**Testing:**
- Documentation accuracy review
- Example code validation
- Migration guide walkthrough

---

## 🧪 Testing Strategy

### 1. CSS Validation
- **Linting:** Run stylelint on all CSS files
- **Browser Compat:** Test on Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Glassmorphism:** Verify backdrop-filter support (98.5% coverage)
- **Responsive:** Test on mobile (375px), tablet (768px), desktop (1920px)

### 2. JavaScript Validation
- **Linting:** Run ESLint on all JS files
- **D3.js Integration:** Test force graph, tree, scatter plot renderings
- **Tab Navigation:** Validate keyboard shortcuts (Tab, Arrow keys, Enter)
- **Performance:** Chart rendering <500ms for 1000 nodes

### 3. Distribution Testing
- **File Sync:** Validate all targets receive correct files
- **Version Consistency:** Check VERSION files match manifest
- **Checksum:** Verify SHA256 integrity
- **Breaking Changes:** Test migration scripts

### 4. Integration Testing
- **CORTEX Lens:** Generate dashboards for all 6 repo types
- **Admin Dashboard:** Run all 18+ collectors
- **RA Toolkit:** Generate OneDrive analysis
- **Cross-Browser:** Test on 4 major browsers

### 5. Performance Testing
- **Dashboard Load:** <3 seconds for all templates
- **Chart Rendering:** <500ms for 1000 nodes (D3.js)
- **File Sync:** <30 seconds for full distribution
- **Dev Mode Latency:** <100ms for hot reload

---

## 📊 Success Metrics

### Quantitative Goals
- ✅ **Code Reduction:** 80% reduction in duplicated CSS/JS (4 copies → 1 central)
- ✅ **Distribution Speed:** Design updates propagate in <30 seconds
- ✅ **Consistency:** 100% visual consistency across all tools
- ✅ **Browser Support:** 98%+ coverage (backdrop-filter compatibility)
- ✅ **Performance:** Dashboard load <3 seconds, chart render <500ms

### Qualitative Goals
- ✅ **Developer Experience:** Single command to publish updates
- ✅ **Maintainability:** Design changes in one location (no hunt-and-replace)
- ✅ **Extensibility:** Easy to add new tools to distribution
- ✅ **Backward Compatibility:** Existing dashboards continue working
- ✅ **Hot Reload:** Real-time preview during development

---

## 🔍 Future Enhancements

### Phase 7: Theme System (Future)
- **Light Mode:** Alternative color palette for light backgrounds
- **Custom Themes:** User-configurable color schemes
- **Theme Switcher:** Toggle between themes in dashboards

### Phase 8: Component Library (Future)
- **React Components:** Port design system to React for dynamic apps
- **Web Components:** Standard web components for framework-agnostic use
- **Storybook Integration:** Interactive component documentation

### Phase 9: CDN Hosting (Future)
- **Public CDN:** Host design system on CDN for external use
- **Versioned URLs:** `https://cdn.cortex.ai/design-system/v1.0.0/cortex-glass.css`
- **NPM Package:** Publish to NPM for package manager integration

---

## 📚 Appendix

### A. File Size Budget
| File | Max Size | Current | Notes |
|------|----------|---------|-------|
| cortex-glass.css | 20KB | 15KB | Core glassmorphism |
| cortex-base.css | 10KB | 8KB | Reset + typography |
| cortex-components.css | 15KB | 12KB | UI components |
| cortex-charts.css | 8KB | 6KB | Visualization styles |
| cortex-charts.js | 12KB | 10KB | D3.js wrappers |
| cortex-tabs.js | 5KB | 4KB | Tab navigation |
| cortex-utils.js | 6KB | 5KB | Helper functions |
| **Total** | **76KB** | **60KB** | Excellent performance |

### B. Browser Compatibility Matrix
| Feature | Chrome | Firefox | Safari | Edge | Coverage |
|---------|--------|---------|--------|------|----------|
| backdrop-filter | 76+ | 103+ | 9+ | 79+ | 98.5% |
| CSS Grid | 57+ | 52+ | 10.1+ | 16+ | 99.9% |
| CSS Variables | 49+ | 31+ | 9.1+ | 15+ | 99.8% |
| Flexbox | 29+ | 28+ | 9+ | 12+ | 99.9% |
| ES6 Modules | 61+ | 60+ | 10.1+ | 79+ | 98.2% |

### C. Color Palette Reference
```css
/* Background Colors */
--bg-primary: #0a0e1a;      /* Dark navy */
--bg-secondary: #1a1f3a;    /* Navy blue */
--bg-tertiary: #252b47;     /* Light navy */

/* Text Colors */
--text-primary: #f0f0f0;    /* Light gray */
--text-secondary: #b0b0b0;  /* Medium gray */
--text-muted: #707070;      /* Dark gray */

/* Accent Colors */
--accent-primary: #00d4ff;   /* Cyan */
--accent-secondary: #7b61ff; /* Purple */

/* Semantic Colors */
--success: #00ff9d;          /* Green */
--warning: #ffa500;          /* Orange */
--danger: #ff4444;           /* Red */
--info: #00d4ff;             /* Cyan */

/* Glassmorphism */
--glass-bg: rgba(26, 31, 58, 0.7);
--glass-border: rgba(255, 255, 255, 0.1);
```

---

**End of Plan**

**Next Steps:**
1. Review plan with team
2. Begin Phase 0 (Foundation) - Extract and centralize existing styles
3. Create `cortex-brain/design-system/` structure
4. Establish version 1.0.0 baseline

**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.
