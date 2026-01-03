# 🏗️ CORTEX Documentation Generation Orchestrator

**Version:** 5.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Created:** January 3, 2026  
**Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Comprehensive documentation generation orchestrator that creates, validates, and maintains CORTEX documentation following glassmorphism design standards, enforcing CSS quality rules, and leveraging toolkit orchestrator automation for maximum efficiency.

**Target:** CORTEX documentation site (`docs/` folder)  
**Scope:** Documentation generation, validation, quality enforcement, design compliance  
**Integration:** Toolkit Orchestrator scripts + Glassmorphism Design Standard v4.2.6 + Planning System v5.0

---

## 🔀 Command Patterns

| Pattern | Action | Type |
|---------|--------|------|
| `generate docs`, `docgen [feature]` | Generate new documentation page | 📋 GUIDED |
| `validate docs`, `check docs quality` | Full quality validation pipeline | 📋 GUIDED |
| `cleanup docs`, `organize docs` | Cleanup + stub generation | 📋 GUIDED |
| `enforce design`, `validate glassmorphism` | Design standard compliance check | 📋 GUIDED |
| `sync docs sitemap`, `update sitemap` | Sync master documentation files | 📋 GUIDED |
| `fix docs [issue]`, `repair docs` | Auto-fix common documentation issues | 📋 GUIDED |

---

## 🧰 Toolkit Integration

### Available Validation Scripts

| Script | Purpose | Usage Pattern |
|--------|---------|---------------|
| `validate-css-duplicates.ps1` | Detect CSS redundancy | `.\cortex-toolkit\validate-css-duplicates.ps1 -Detailed -ThresholdPercentage 2` |
| `validate-css-usage.ps1` | Check CSS class usage | `.\cortex-toolkit\validate-css-usage.ps1 -IncludeOrphans -DetectCompound -StrictMode` |
| `validate-responsive-design.ps1` | Mobile-first compliance | `.\cortex-toolkit\validate-responsive-design.ps1 -IncludeTouchTargets -StrictMode -StandardBreakpoints` |
| `validate-glassmorphism-compliance.ps1` | Design standard enforcement | `.\cortex-toolkit\validate-glassmorphism-compliance.ps1 -StandardVersion 4.2.6 -StrictMode` |
| `validate-icon-title-spacing.ps1` | Icon-title gap validation | `.\cortex-toolkit\validate-icon-title-spacing.ps1 -DetectOnly` |
| `validate-css-paths.ps1` | **CSS path integrity (CRITICAL)** | **`.\cortex-toolkit\validate-css-paths.ps1 -Detailed`** |
| `docs-organizer.ps1` | Link validation + archival | `.\cortex-toolkit\docs-organizer.ps1 -DryRun` |
| `create-stub-pages.ps1` | Generate stub placeholders | `.\cortex-toolkit\create-stub-pages.ps1` |

### Available Fix Scripts

| Script | Purpose | Usage Pattern |
|--------|---------|---------------|
| `fix-inline-styles.ps1` | Convert inline styles to CSS | `.\cortex-toolkit\fix-inline-styles.ps1 -AutoFix` |
| `fix-missing-css-classes.ps1` | Add missing class definitions | `.\cortex-toolkit\fix-missing-css-classes.ps1 -AutoGenerate` |
| `fix-viewport-tags.ps1` | Add mobile viewport meta tags | `.\cortex-toolkit\fix-viewport-tags.ps1 -Apply` |
| `fix-animation-tiers.ps1` | Enforce T1 animation compliance | `.\cortex-toolkit\fix-animation-tiers.ps1 -Level1Only` |
| `fix-icon-title-spacing.ps1` | Auto-fix icon-title gaps | `.\cortex-toolkit\validate-icon-title-spacing.ps1 -AutoFix` |
| `fix-duplicate-mobile-styles.ps1` | **Remove duplicate mobile styles in body** | **`.\cortex-toolkit\fix-duplicate-mobile-styles.ps1 -ShowDetails`** |
| `reduce-css-redundancy.ps1` | Remove duplicate CSS rules | `.\cortex-toolkit\reduce-css-redundancy.ps1 -Apply` |
| `replace-bullets-with-cards.ps1` | Convert lists to card grids | `.\cortex-toolkit\replace-bullets-with-cards.ps1 -Preview` |

---

## 📐 Design Standards Enforcement

### Glassmorphism Standard v4.2.6

**Reference:** `cortex-brain/documents/standards/glassmorphism-design-standard.md`

**Core Requirements:**
1. **Zero Inline Styles** - All styling via CSS classes
2. **CSS Quality Rules:**
   - <2% CSS redundancy (duplicates)
   - 100% CSS usage (no unused classes)
   - Zero missing classes (all HTML classes defined)
   - A+ mobile-friendliness (95%+ score)
3. **Animation Tiers:**
   - **T1 (Level 1+ pages):** Subtle only (0.2-0.3s transitions, no infinite animations)
   - **T3 (Level 0 only):** Dramatic effects allowed on hero sections
4. **Icon-Title Spacing:** `gap: var(--spacing-sm)` (8px) for tight coupling
5. **Tetris Layout:** Responsive `clamp()` font sizes, container query units (cqi)
6. **Glass Effects:** 20px backdrop blur, soft animations (8s reflection sweep)

### Validation Pipeline

```powershell
# Step 1: CSS Quality Check
.\cortex-toolkit\validate-css-duplicates.ps1 -ThresholdPercentage 2
.\cortex-toolkit\validate-css-usage.ps1 -StrictMode
.\cortex-toolkit\validate-responsive-design.ps1 -StrictMode

# Step 2: Design Compliance
.\cortex-toolkit\validate-glassmorphism-compliance.ps1 -StandardVersion 4.2.6
.\cortex-toolkit\validate-icon-title-spacing.ps1 -DetectOnly

# Step 3: Link & Structure
.\cortex-toolkit\docs-organizer.ps1 -DryRun

# Step 4: CSS Path Integrity (CRITICAL)
.\cortex-toolkit\validate-css-paths.ps1
```

**Success Criteria:**
- ✅ CSS redundancy <2%
- ✅ Zero unused CSS classes
- ✅ Zero missing CSS classes
- ✅ A+ mobile-friendliness
- ✅ All icon-title pairs use 8px gap
- ✅ No broken internal links
- ✅ T1 animations only on Level 1+ pages
- ✅ **Zero malformed CSS paths (NEW)**

---

## 🏗️ Documentation Generation Workflow

### Phase 1: Pre-Generation Validation ✈️

**Purpose:** Analyze current state before generating new documentation

**Steps:**
1. Identify target location in documentation hierarchy (Level 0/1/2)
2. Check for existing content at target path
3. Determine parent hub for navigation breadcrumbs
4. Review glassmorphism design standard for page type (standard tile, multi-panel, tetris)
5. Scan `docs-sitemap.md` for visual hierarchy context

**Output:** Generation plan with:
- Target file path
- Page type (hub, detail page, stub)
- Parent navigation
- Required CSS classes
- Animation tier (T1/T3)

---

### Phase 2: Content Structure Generation 📝

**Purpose:** Create semantic HTML structure following design standards

**Required Elements:**

#### Level 0 Pages (Home)
- Glass header with logo + navigation
- T3 animations allowed (hero section only)
- Multi-panel or tetris layout for 4+ categories
- Glass footer with links

#### Level 1 Pages (Hub Pages)
- Glass header with Home link only (no logo)
- Page title card with icon-title pair (8px gap)
- T1 animations only (subtle hover effects)
- Tetris layout with responsive font sizes (`clamp()`)
- Glass breadcrumb navigation
- Glass footer

#### Level 2 Pages (Detail Pages)
- Same as Level 1 structure
- Content-driven layout (principle-card-grid, capability-tiles, masonry-grid)
- Code examples in styled blocks
- Related documentation links
- Back navigation to parent hub

**Template Selection:**

```yaml
page_types:
  standard_tile:
    conditions: ["3-5 items", "<50 chars each"]
    layout: "3-column grid"
    classes: [".principle-card-grid", ".glass-card-clickable", ".animation-t1"]
  
  multi_panel:
    conditions: ["4+ categories", "hierarchical structure"]
    layout: "2x2 or 2x3 grid with subpanels"
    classes: [".category-panels-grid", ".category-subpanel", ".category-tags"]
  
  tetris_layout:
    conditions: ["6 metrics", "asymmetric importance"]
    layout: "3x3 grid with varied spanning"
    classes: [".token-metrics-tetris", ".token-metric-tile", "container-type: inline-size"]
  
  capability_tiles:
    conditions: ["vertical stack", "detailed features"]
    layout: "single column with left border accent"
    classes: [".capability-tiles", ".glass-card-clickable"]
```

---

### Phase 3: Styling & Assets Integration 🎨

**Purpose:** Apply glassmorphism styles and ensure asset resolution

**CSS Integration:**
```html
<link rel="stylesheet" href="../assets/css/main.css?v=2026-01-03-v4">
<link rel="stylesheet" href="../assets/css/intentional-classes.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

**Path Resolution Rules:**
- `docs/*.html` → `assets/css/`
- `docs/[category]/*.html` → `../assets/css/`
- `docs/[category]/[subcategory]/*.html` → `../../assets/css/`

**Icon Requirements:**
- All icons must have `fas`/`far`/`fab`/`fal`/`fad` prefix
- Icons in titles use `pulse-glow-glass--fast` animation
- Icon-title pairs use `gap: var(--spacing-sm)` (8px)

**Font Size Responsiveness:**
```css
/* Tetris tiles - responsive with cqi */
.token-metric-tile i {
    font-size: clamp(1.5rem, 4cqi + 0.5rem, 2.5rem);
}

.token-metric-tile .metric-value {
    font-size: clamp(1.25rem, 4cqi + 0.5rem, 2rem);
}

.token-metric-tile .metric-label {
    font-size: clamp(0.7rem, 2cqi + 0.2rem, 0.875rem);
}

/* Category tags - responsive with cqi */
.category-tag {
    font-size: clamp(0.75rem, 2.5cqi + 0.2rem, 1.1rem);
}
```

**Container Queries:**
```css
.token-metrics-tetris,
.category-subpanel {
    container-type: inline-size; /* Enable cqi units */
}
```

---

### Phase 4: Quality Validation 🔍

**Purpose:** Ensure generated documentation meets all quality standards

**Validation Checklist:**

✅ **CSS Quality (CRITICAL)**
- Run `validate-css-duplicates.ps1`: <2% redundancy
- Run `validate-css-usage.ps1`: Zero unused classes
- Run `validate-css-usage.ps1`: Zero missing classes
- No inline styles (`style="..."` forbidden)

✅ **Design Compliance**
- Run `validate-glassmorphism-compliance.ps1`: v4.2.6 standard
- Run `validate-icon-title-spacing.ps1`: All icon-title pairs 8px gap
- Animation tier correct (T1 for Level 1+, T3 only on Level 0 hero)
- Responsive font sizes use `clamp()`

✅ **Mobile-Friendliness**
- Run `validate-responsive-design.ps1`: A+ grade (95%+)
- Viewport meta tag present: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- Touch targets ≥44px × 44px
- Mobile breakpoints: 375px, 768px, 1440px

✅ **Link Validation**
- Run `docs-organizer.ps1 -DryRun`: No broken internal links
- External links use `target="_blank"`
- Breadcrumb navigation resolves correctly
- CSS/JS/image paths resolve based on depth

✅ **Content Structure**
- Page title with icon (icon-title gap 8px)
- Glass breadcrumb navigation
- Glass footer present
- Mermaid diagrams initialized (if used)
- Code blocks styled correctly

---

### Phase 5: Documentation Sync 📋

**Purpose:** Update master documentation files with new content

**Files to Update:**

#### 1. `docs-sitemap.md` (VISUAL TOOL ONLY)
**⚠️ CRITICAL:** This file shows **node structure** from Home (root). It is **NOT for status tracking**.

**Update only:**
- Total HTML files count
- Stub pages count
- Add new page to visual hierarchy tree
- Update "Last Updated" date

**DO NOT update:**
- Implementation status
- Completion percentages
- Progress tracking metrics

**For status tracking, use:**
- `00-master-plan.md` - Progress, completion %
- `executive-summary.md` - Multi-panel status
- `glassmorphism-design-standard.md` - Design compliance

#### 2. `00-master-plan.md`
**Update:**
- Total HTML files (current: 339 with v5.0)
- Level 1/2 status counts
- Completion percentages
- New page categorization (standard tile, multi-panel, orchestrators)
- v5.0 architecture pages (Master Orchestrator Hub + Planning v5 + ADO v2)

#### 3. `glassmorphism-design-standard.md`
**Update only if:**
- New pattern introduced (add to Pattern Library)
- Scope changed (add new tile/category)
- CSS quality rules violated (document exception)
- Design standard version bump needed

**Increment:**
- Patch version (4.2.6 → 4.2.7) for scope updates
- Minor version (4.2.x → 4.3.0) for new patterns
- Major version (4.x.x → 5.0.0) for breaking changes

#### 4. `executive-summary.md`
**Update:**
- Page status summary table
- Implementation priorities
- Completion status by multi-panel
- Orchestrators page counts

**Consistency Validation:**
All 4 files must show:
- ✅ Same total file count (339 HTML with v5.0)
- ✅ Same stub page count (188 with v5.0)
- ✅ Same completion percentages
- ✅ No conflicting information
- ✅ Synchronized "Last Updated" dates

---

## 🛠️ Common Documentation Issues & Fixes

### Issue 0: Malformed CSS Paths (CRITICAL)

**Symptom:** CSS links with repeated dots `../..../..../..../..../../assets/css/`  
**Impact:** Complete CSS failure, broken page layouts, no styling  
**Root Cause:** Automated tool error inserting invalid relative paths  
**Detection:**
```powershell
.\cortex-toolkit\validate-css-paths.ps1 -Detailed
```

**Fix Complexity Analysis:**
- Script calculates fix complexity score (0-10)
- Recommends REPAIR vs RECREATE based on:
  - Affected file count
  - Pattern consistency
  - Structure integrity
  - Content validity

**Auto-Fix:**
```powershell
# Dry run first (preview changes)
.\cortex-toolkit\validate-css-paths.ps1 -AutoFix -DryRun

# Apply global fix
.\cortex-toolkit\validate-css-paths.ps1 -AutoFix
```

**Prevention:** Run `validate-css-paths.ps1` in pre-commit validation pipeline

---

### Issue 1: Inline Styles Present

**Symptom:** `style="..."` attributes in HTML  
**Impact:** Violates Zero Inline Styles rule  
**Fix:**
```powershell
.\cortex-toolkit\fix-inline-styles.ps1 -AutoFix
```

**Validation:**
```powershell
Select-String -Path "docs/**/*.html" -Pattern 'style="' -Exclude "node_modules","archives"
# Should return 0 matches
```

---

### Issue 1: Duplicate Mobile Optimization Styles (CRITICAL)

**Symptom:** Style blocks appear twice - once in `<head>` and again inside `<header>` in `<body>`  
**Impact:** HTML parsing errors, invalid document structure, CSS not applied correctly  
**Root Cause:** Automated tool injecting styles in wrong location  
**Detection:**
```powershell
# Check for duplicate "Mobile font optimization" comments
Select-String -Path "docs/**/*.html" -Pattern "Mobile font optimization" | 
    Group-Object Path | Where-Object { $_.Count -gt 1 }
```

**Fix:**
```powershell
# Remove duplicate styles from body (keeps only head styles)
.\cortex-toolkit\fix-duplicate-mobile-styles.ps1 -ShowDetails
```

**Prevention:** Styles MUST only appear in `<head>`, never in `<body>` or inside other elements

---

### Issue 2: Inline Styles Present

**Symptom:** `style="..."` attributes in HTML  
**Impact:** Violates Zero Inline Styles rule  
**Fix:**
```powershell
.\cortex-toolkit\fix-inline-styles.ps1 -AutoFix
```

**Validation:**
```powershell
Select-String -Path "docs/**/*.html" -Pattern 'style="' -Exclude "node_modules","archives"
# Should return 0 matches
```

---

### Issue 3: Missing CSS Classes

**Symptom:** HTML uses classes not defined in CSS  
**Impact:** Broken styling, elements render incorrectly  
**Detection:**
```powershell
.\cortex-toolkit\validate-css-usage.ps1 -DetectCompound -StrictMode
```

**Fix:**
```powershell
.\cortex-toolkit\fix-missing-css-classes.ps1 -AutoGenerate
```

---

### Issue 4: CSS Duplicates

**Symptom:** Same CSS rules repeated across files  
**Impact:** File bloat, maintenance burden, performance hit  
**Detection:**
```powershell
.\cortex-toolkit\validate-css-duplicates.ps1 -Detailed -ThresholdPercentage 2
```

**Fix:**
```powershell
.\cortex-toolkit\reduce-css-redundancy.ps1 -Apply
```

**Backup:** Always preserved at `backups/css-backup-{timestamp}/`

---

### Issue 5: Unused CSS Classes

**Symptom:** CSS classes defined but never used in HTML  
**Impact:** Dead code, larger file sizes, confusion  
**Detection:**
```powershell
.\cortex-toolkit\validate-css-usage.ps1 -IncludeOrphans -StrictMode
```

**Fix:**
1. Review unused classes report
2. Move intentional utility classes to `intentional-classes.css`
3. Delete truly unused classes
4. Backup CSS first: `backups/css-backup-{timestamp}/`

---

### Issue 6: Icon-Title Spacing Violations

**Symptom:** Icon-title pairs using inconsistent gaps  
**Impact:** Visual inconsistency, violates tight coupling principle  
**Standard:** `gap: var(--spacing-sm)` (8px)

**Detection:**
```powershell
.\cortex-toolkit\validate-icon-title-spacing.ps1 -DetectOnly
```

**Fix:**
```powershell
.\cortex-toolkit\validate-icon-title-spacing.ps1 -AutoFix
```

**Affected Classes:**
- `.section-title`
- `.page-title`
- `.tier-header`
- `.capability-tile`
- `.card-header-with-icon`

---

### Issue 7: Mobile Viewport Missing

**Symptom:** Missing `<meta name="viewport">` tag  
**Impact:** Poor mobile rendering, fails mobile-friendliness check  
**Fix:**
```powershell
.\cortex-toolkit\fix-viewport-tags.ps1 -Apply
```

**Required Tag:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

---

### Issue 8: Wrong Animation Tier

**Symptom:** T3 dramatic animations on Level 1+ pages  
**Impact:** Violates animation philosophy, distracting UX  
**Rule:** T1 only on Level 1+, T3 only on Level 0 hero sections

**Detection:**
```powershell
Select-String -Path "docs/**/*.html" -Pattern "borderGlowSweep|blobMorph|lightLeakPrimary" -Exclude "index.html"
```

**Fix:**
```powershell
.\cortex-toolkit\fix-animation-tiers.ps1 -Level1Only
```

---

### Issue 9: Non-Responsive Font Sizes

**Symptom:** Fixed font sizes (e.g., `font-size: 2rem`)  
**Impact:** Poor scaling across screen sizes  
**Standard:** Use `clamp()` with cqi units

**Fix Pattern:**
```css
/* ❌ Before - Fixed size */
.metric-value {
    font-size: 2rem;
}

/* ✅ After - Responsive */
.metric-value {
    font-size: clamp(1.25rem, 4cqi + 0.5rem, 2rem);
}
```

**Container Query Requirement:**
```css
.parent-container {
    container-type: inline-size; /* Enable cqi units */
}
```

---

### Issue 10: Broken Internal Links

**Symptom:** Links to non-existent pages (404 errors)  
**Impact:** Navigation fails, poor UX  
**Detection:**
```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun
```

**Fix Options:**
1. Create stub page: `.\cortex-toolkit\create-stub-pages.ps1`
2. Update link to correct path
3. Remove broken link if obsolete

---

### Issue 11: Missing Font Awesome Prefix

**Symptom:** Icons not rendering (empty boxes)  
**Impact:** Visual breaks, unclear meaning  
**Rule:** All icons require `fas`/`far`/`fab`/`fal`/`fad` prefix

**Detection:**
```powershell
Select-String -Path "docs/**/*.html" -Pattern 'class="[^"]*\bfa-[a-z-]+' | 
    Where-Object { $_.Line -notmatch '\bfas\b|\bfar\b|\bfab\b|\bfal\b|\bfad\b' }
```

**Fix:**
```html
<!-- ❌ Before -->
<i class="fa-brain"></i>

<!-- ✅ After -->
<i class="fas fa-brain"></i>
```

---

## 📊 Documentation Quality Metrics

### Target Metrics (MUST ACHIEVE)

| Metric | Target | Validation Script |
|--------|--------|-------------------|
| CSS Redundancy | <2% | `validate-css-duplicates.ps1` |
| CSS Usage | 100% | `validate-css-usage.ps1` |
| Missing Classes | 0 | `validate-css-usage.ps1` |
| Inline Styles | 0 | `grep 'style="'` |
| Mobile-Friendliness | A+ (95%+) | `validate-responsive-design.ps1` |
| Icon-Title Spacing | 8px (100%) | `validate-icon-title-spacing.ps1` |
| Broken Links | <5% | `docs-organizer.ps1` |
| Glassmorphism Compliance | 100% | `validate-glassmorphism-compliance.ps1` |
| **CSS Path Integrity** | **0 malformed** | **`validate-css-paths.ps1`** |

### Quality Gates

**Pre-Commit:**
- ✅ CSS redundancy <2%
- ✅ Zero inline styles
- ✅ Zero missing classes
- ✅ Viewport tags present
- ✅ **Zero malformed CSS paths (CRITICAL)**

**Pre-Deployment:**
- ✅ All quality metrics met
- ✅ Broken links <5%
- ✅ Mobile-friendliness A+
- ✅ Design compliance 100%
- ✅ **CSS path validation passes**

**Post-Deployment:**
- ✅ Visual regression test
- ✅ Link validation
- ✅ Performance audit
- ✅ Accessibility scan

---

## 🔄 Continuous Maintenance

### Weekly Tasks
1. Run `validate-css-duplicates.ps1` - identify new redundancy
2. Run `validate-css-usage.ps1` - detect unused classes
3. Run `docs-organizer.ps1 -DryRun` - check for broken links
4. Run `validate-css-paths.ps1` - ensure CSS path integrity
5. Review stub page creation backlog

### Monthly Tasks
1. Full quality audit across all metrics
2. Update `glassmorphism-design-standard.md` version
3. Archive obsolete documentation
4. Generate comprehensive CSS quality report
5. Sync all master documentation files

### Version Bump Triggers

**Patch (x.x.N):**
- CSS quality improvements
- Bug fixes in existing pages
- Stub page creation
- Link fixes

**Minor (x.N.0):**
- New documentation pages
- New design patterns
- Scope expansion
- Feature additions

**Major (N.0.0):**
- Breaking design standard changes
- Architecture refactor (v5.0)
- Complete documentation restructure

---

## 🚨 Critical Reminders

### 0. Holistic Validation Pipeline (MANDATORY)

**⛔ BEFORE ANY DOCUMENTATION CHANGES:**

Run the complete validation pipeline to prevent breaking existing pages:

```powershell
# Full validation suite (run in order)
.\cortex-toolkit\validate-css-paths.ps1              # Check path integrity
.\cortex-toolkit\fix-duplicate-mobile-styles.ps1 -DryRun  # Preview style issues
.\cortex-toolkit\validate-css-usage.ps1 -StrictMode  # Check CSS quality
.\cortex-toolkit\validate-glassmorphism-compliance.ps1 -StandardVersion 4.2.6
```

**AFTER MAKING CHANGES:**

```powershell
# Auto-fix common issues
.\cortex-toolkit\validate-css-paths.ps1 -AutoFix
.\cortex-toolkit\fix-duplicate-mobile-styles.ps1
.\cortex-toolkit\fix-inline-styles.ps1 -AutoFix

# Verify no regressions
.\cortex-toolkit\validate-css-usage.ps1 -StrictMode
```

**Why This Matters:**
- Prevents 42-file CSS path disasters
- Detects 72-file duplicate style issues
- Catches structural HTML violations early
- Ensures zero broken pages on commit

**Rule:** Documentation generation orchestrator MUST NOT leave broken HTML. Holistic review = REQUIRED.

---

### 1. CSS Backup Protocol
**⚠️ ALWAYS backup CSS before modifications:**
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path "docs/assets/css" -Destination "backups/css-backup-$timestamp" -Recurse
```

**Backup Location:** `backups/css-backup-20260103_093835/`  
**Contains:** All 14 CSS files, 2,043 classes total

### 2. docs-sitemap.md is Visual Only
**⛔ FORBIDDEN:**
- Status tracking
- Progress percentages
- Implementation metrics
- Completion checkboxes

**✅ ALLOWED:**
- Visual node hierarchy
- File path structure
- Category organization
- Total file counts

### 3. Icon-Title Spacing is Sacred
**Standard:** `gap: var(--spacing-sm)` (8px) - NO EXCEPTIONS

**Toolkit Validation:** `validate-icon-title-spacing.ps1` enforces this rule

### 4. Animation Tier Discipline
- **Level 0 (Home):** T3 allowed on hero sections only
- **Level 1+ (All other pages):** T1 subtle animations ONLY
- **NO borderGlowSweep, blobMorph, or lightLeakPrimary on Level 1+**

### 5. Container Query Units (cqi)
**Required for responsive font sizes:**
```css
.parent-container {
    container-type: inline-size; /* Must be set */
}

.child-element {
    font-size: clamp(min, Ncqi + offset, max);
}
```

### 6. Zero Inline Styles
**Absolutely forbidden:** `style="..."`  
**Use:** CSS classes only, defined in `main.css` or `intentional-classes.css`

---

## 📚 Reference Documentation

### Primary Sources
1. **Glassmorphism Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` (v4.2.6)
2. **Master Plan:** `cortex-brain/documents/planning/active/cortex-documentation/00-master-plan.md`
3. **Visual Sitemap:** `cortex-brain/documents/planning/active/cortex-documentation/artifacts/docs-sitemap.md`
4. **Toolkit Manifest:** `cortex-toolkit/toolkit-manifest.yaml`

### Toolkit Scripts Location
**Path:** `cortex-toolkit/`

**Categories:**
- **Validation:** `validate-*.ps1`
- **Fixes:** `fix-*.ps1`
- **Organization:** `docs-organizer.ps1`, `create-stub-pages.ps1`
- **Cleanup:** `cleanup-unused-css.ps1`, `reduce-css-redundancy.ps1`
- **Transformation:** `replace-bullets-with-cards.ps1`, `link-generated-css.ps1`

### Design Pattern Examples
- **Standard Tile:** `docs/architecture/index.html`
- **Multi-Panel:** `docs/index.html` (Security panel)
- **Tetris Layout:** `docs/token-optimization/index.html`
- **Capability Tiles:** `docs/orchestrators/planning-system.html`
- **Principle Cards:** `docs/architecture/brain-tiers.html`

---

## ✅ Success Criteria

### Documentation Generation Complete When:
1. ✅ All quality metrics met (CSS, mobile, design)
2. ✅ Zero inline styles
3. ✅ Zero missing CSS classes
4. ✅ CSS redundancy <2%
5. ✅ Mobile-friendliness A+
6. ✅ Icon-title spacing 8px (100%)
7. ✅ Broken links <5%
8. ✅ Master docs synced (4 files)
9. ✅ Visual sitemap updated
10. ✅ Toolkit validation passes

### Master Documentation Sync Complete When:
1. ✅ `docs-sitemap.md` shows visual hierarchy
2. ✅ `00-master-plan.md` shows progress/completion
3. ✅ `glassmorphism-design-standard.md` updated (if scope changed)
4. ✅ `executive-summary.md` shows status/priorities
5. ✅ All 4 files show same total counts
6. ✅ No conflicting information
7. ✅ Versions incremented appropriately
8. ✅ "Last Updated" dates synchronized

---

**Anti-Bloat:** This prompt replaces `cortex-doc-cleanup.prompt.md` and consolidates all documentation operations into a single, comprehensive orchestrator.
