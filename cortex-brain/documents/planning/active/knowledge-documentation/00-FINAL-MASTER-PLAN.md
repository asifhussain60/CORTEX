# 📚 Knowledge Library Documentation & Learning Hub - FINAL PLAN
**Progressive Disclosure UI with Modern Responsive Design**

**Plan Name:** Knowledge Library Documentation & Learning Hub v2.0  
**Created:** December 28, 2025  
**Author:** Asif Hussain  
**Status:** Active - PROGRESSIVE DISCLOSURE DESIGN  
**GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Executive Summary

**Goal:** Create a modern, scalable web documentation system for CORTEX Knowledge Library using **progressive disclosure** design patterns to manage 80+ knowledge files across 17 categories with intuitive navigation, gradual drill-downs, and mobile-first responsive design.

**Design Philosophy:**
- **Progressive Disclosure:** Start simple, reveal complexity gradually
- **Information Hierarchy:** 4-level drill-down (Home → Domain Groups → Categories → Knowledge Files)
- **Modern Navigation:** Breadcrumbs, sticky navigation, back buttons, deep linking
- **Mobile-First:** Touch-optimized, thumb-friendly zones, swipe gestures
- **Performance:** Lazy loading, skeleton screens, progressive enhancement

**Styling Standards Hierarchy:**
- **PRIMARY:** `cortex-brain/documents/templates/documentation-styling-standards.md` (v1.1.0 - Latest)
- **SECONDARY:** `.github/prompts/docgen.old` (v4.2 - Base glassmorphism system)
- **CONFLICT RESOLUTION:** documentation-styling-standards.md OVERRIDES docgen.old for:
  - Logo sizing (300px desktop, 200px mobile)
  - Icon sizing (2.4rem for phase-icon, tier-icon)
  - Panel spacing (48px minimum via var(--spacing-2xl))
  - Typography (line-height 1.5 lists, 1.7 body)
  - Bullets (CSS ::before with position: absolute, 1.5rem, brand color)
  - Mobile breakpoints (320px, 768px, 1024px)
  - Zero inline styles policy (except story button preservation)

**Scope:** 
- **17 categories** organized into 5 domain groups
- **80+ YAML files** (38 existing + 42 new) with ~35,000 rules
- **4-level information architecture** for gradual complexity revelation
- **Interactive visualizations:** D3.js (category relationships) + Mermaid (concepts)
- **Responsive design:** 320px-4K with touch optimization
- **Full glassmorphism styling**

**Timeline:** 6-8 days (expanded for UX design)

---

## 🏗️ Information Architecture (4-Level Hierarchy)

### Level 1: Home Page (docs/index.html)
**Single Entry Point:** "📚 Knowledge Library" tile in Core Capabilities

### Level 2: Domain Overview (docs/knowledge/index.html)
**5 Domain Groups** - High-level organization
```
┌─────────────────────────────────────────────────────────┐
│ 🎨 FRONTEND & UI (3 categories)                        │
│ Frontend • UI/UX • Mobile                              │
├─────────────────────────────────────────────────────────┤
│ 🔌 BACKEND & APIs (3 categories)                       │
│ API • Microservices • Messaging                        │
├─────────────────────────────────────────────────────────┤
│ 🗄️ DATA & STORAGE (2 categories)                       │
│ Databases • Performance                                │
├─────────────────────────────────────────────────────────┤
│ ☁️ INFRASTRUCTURE (3 categories)                       │
│ Cloud • Containers • DevOps                            │
├─────────────────────────────────────────────────────────┤
│ 🏗️ SOFTWARE CRAFT (6 categories)                       │
│ Engineering • DDD • Security • Testing • Domains       │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Reduces cognitive load (5 groups vs 17 categories)
- ✅ Logical grouping by development workflow
- ✅ Easy to scan and navigate
- ✅ Mobile-friendly (large touch targets)

### Level 3: Category Detail (e.g., docs/knowledge/frontend.html)
**Category-specific page** with:
- Knowledge files list (collapsible accordion)
- High-priority rules showcase
- Mermaid concept diagram
- Learning resources
- Breadcrumb: Home > Frontend & UI > Frontend

### Level 4: Knowledge File Detail (e.g., docs/knowledge/frontend/react-best-practices.html)
**Individual YAML file documentation** with:
- All rules with examples
- Code snippets with syntax highlighting
- Cross-references to other knowledge files
- Breadcrumb: Home > Frontend & UI > Frontend > React Best Practices

---

## 📐 Progressive Disclosure Design Patterns

### Pattern 1: Collapsible Accordions
**Use Case:** Knowledge files list on category pages

```html
<div class="knowledge-files-accordion">
    <div class="accordion-item">
        <button class="accordion-header" aria-expanded="false">
            <span class="accordion-icon">📄</span>
            <span class="accordion-title">React Best Practices</span>
            <span class="accordion-badge badge badge-info">35 rules</span>
            <span class="accordion-chevron">▼</span>
        </button>
        <div class="accordion-content" hidden>
            <p>React Hooks, Context API, Performance optimization...</p>
            <ul>
                <li><strong>High Priority:</strong> Use functional components</li>
                <li><strong>Medium:</strong> Implement error boundaries</li>
            </ul>
            <a href="frontend/react-best-practices.html" class="btn-link">View Full Details →</a>
        </div>
    </div>
</div>

<style>
.accordion-item { margin-bottom: var(--spacing-sm); }
.accordion-header {
    width: 100%;
    padding: var(--spacing-md);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    transition: all var(--transition-base);
}
.accordion-header:hover { background: rgba(26, 31, 58, 0.9); }
.accordion-header[aria-expanded="true"] .accordion-chevron { transform: rotate(180deg); }
.accordion-content {
    padding: var(--spacing-md);
    background: rgba(26, 31, 58, 0.5);
    border-radius: 0 0 var(--radius-md) var(--radius-md);
}
</style>
```

### Pattern 2: Tabbed Content
**Use Case:** Category detail pages (Overview, Files, Resources, Usage)

```html
<div class="tabs-container">
    <div class="tabs-nav" role="tablist">
        <button class="tab-button active" role="tab" aria-selected="true" data-tab="overview">
            Overview
        </button>
        <button class="tab-button" role="tab" aria-selected="false" data-tab="files">
            Knowledge Files (8)
        </button>
        <button class="tab-button" role="tab" aria-selected="false" data-tab="resources">
            Learning Resources
        </button>
        <button class="tab-button" role="tab" aria-selected="false" data-tab="usage">
            CORTEX Usage
        </button>
    </div>
    
    <div class="tab-content active" id="overview-tab">
        <!-- Overview content -->
    </div>
    <div class="tab-content" id="files-tab" hidden>
        <!-- Knowledge files accordion -->
    </div>
    <div class="tab-content" id="resources-tab" hidden>
        <!-- Educational resources -->
    </div>
    <div class="tab-content" id="usage-tab" hidden>
        <!-- How CORTEX uses this knowledge -->
    </div>
</div>
```

### Pattern 3: Expandable Cards
**Use Case:** Rules showcase on category pages

```html
<div class="rule-card" data-expandable>
    <div class="rule-header" onclick="toggleRule(this)">
        <span class="rule-icon">⚠️</span>
        <h4>Use Intention-Revealing Names</h4>
        <span class="badge badge-danger">HIGH</span>
        <button class="expand-btn" aria-label="Expand rule">+</button>
    </div>
    <div class="rule-body" hidden>
        <p><strong>Description:</strong> Names should reveal intent without comments...</p>
        <div class="rule-examples">
            <div class="example-good">
                <strong>✅ Good:</strong>
                <pre><code>elapsed_time_in_days = 365</code></pre>
            </div>
            <div class="example-bad">
                <strong>❌ Bad:</strong>
                <pre><code>d = 365  # elapsed time in days</code></pre>
            </div>
        </div>
    </div>
</div>
```

### Pattern 4: Sticky Breadcrumbs & Back Button
**Use Case:** All pages for easy navigation

```html
<nav class="breadcrumb-container sticky-nav" aria-label="Breadcrumb">
    <button class="back-button" onclick="history.back()" aria-label="Go back">
        ← Back
    </button>
    <ol class="breadcrumb">
        <li><a href="../index.html">Home</a></li>
        <li><a href="index.html">Knowledge Library</a></li>
        <li><a href="index.html#frontend-ui">Frontend & UI</a></li>
        <li aria-current="page">Frontend</li>
    </ol>
</nav>

<style>
.sticky-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(10, 14, 39, 0.95);
    backdrop-filter: blur(20px);
    padding: var(--spacing-sm) var(--spacing-md);
    border-bottom: 1px solid var(--glass-border);
}
</style>
```

### Pattern 5: Lazy Loading & Skeleton Screens
**Use Case:** Performance optimization for large content

```html
<div class="knowledge-files-container">
    <!-- Show skeleton while loading -->
    <div class="skeleton-loader" aria-busy="true">
        <div class="skeleton-card"></div>
        <div class="skeleton-card"></div>
        <div class="skeleton-card"></div>
    </div>
    
    <!-- Actual content (lazy loaded) -->
    <div class="knowledge-files-list" hidden data-lazy-load>
        <!-- Content loaded via Intersection Observer API -->
    </div>
</div>

<script>
// Lazy load content when scrolling into view
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            loadKnowledgeFiles(entry.target);
            observer.unobserve(entry.target);
        }
    });
});

document.querySelectorAll('[data-lazy-load]').forEach(el => {
    observer.observe(el);
});
</script>
```

---

## 📱 Mobile-First Responsive Design

### Touch-Optimized Zones

**Thumb-Friendly Navigation (Mobile):**
```
┌─────────────────────────┐
│  [Logo]   📚 Knowledge  │ ← Header (fixed)
├─────────────────────────┤
│ ← Back | Home > Library │ ← Sticky breadcrumb
├─────────────────────────┤
│                         │
│   [Domain Cards]        │ ← Main content
│   Large tap targets     │   (scrollable)
│   (min 48x48px)         │
│                         │
├─────────────────────────┤
│  [Tab Navigation]       │ ← Bottom nav (thumb zone)
└─────────────────────────┘
```

**Responsive Breakpoints:**
```css
/* Mobile: 320px-767px */
@media (max-width: 767px) {
    .domain-grid { grid-template-columns: 1fr; }
    .category-grid { grid-template-columns: 1fr; }
    .tabs-nav { overflow-x: auto; white-space: nowrap; }
    .back-button { display: block; }
    .breadcrumb { font-size: 0.875rem; }
}

/* Tablet: 768px-1023px */
@media (min-width: 768px) and (max-width: 1023px) {
    .domain-grid { grid-template-columns: repeat(2, 1fr); }
    .category-grid { grid-template-columns: repeat(3, 1fr); }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
    .domain-grid { grid-template-columns: repeat(3, 1fr); }
    .category-grid { grid-template-columns: repeat(4, 1fr); }
    .back-button { display: none; } /* Use breadcrumb only */
}
```

### Swipe Gestures (Mobile)
```javascript
// Swipe to navigate between categories
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    if (touchEndX < touchStartX - 50) {
        // Swipe left → Next category
        navigateNext();
    }
    if (touchEndX > touchStartX + 50) {
        // Swipe right → Previous category
        navigatePrevious();
    }
}
```

---

## 🗺️ Navigation Patterns

### Primary Navigation (All Pages)

**Breadcrumb Structure:**
```
Level 1: Home
Level 2: Home > Knowledge Library
Level 3: Home > Knowledge Library > [Domain Group] > [Category]
Level 4: Home > Knowledge Library > [Domain Group] > [Category] > [File]
```

**Example Breadcrumb Trails:**
```
Home > Knowledge Library > Frontend & UI > Frontend > React Best Practices
Home > Knowledge Library > Backend & APIs > Microservices > CQRS Pattern
Home > Knowledge Library > Infrastructure > Cloud > AWS Best Practices
```

### Secondary Navigation (Category Pages)

**Category Sidebar (Desktop) / Bottom Nav (Mobile):**
```html
<aside class="category-sidebar">
    <h3>Frontend & UI</h3>
    <nav class="category-nav">
        <a href="frontend.html" class="active">💻 Frontend (8 files)</a>
        <a href="ui-ux.html">🎨 UI/UX (2 files)</a>
        <a href="mobile.html">📱 Mobile (4 files)</a>
    </nav>
</aside>

<!-- Mobile: Bottom navigation bar -->
<nav class="bottom-nav" aria-label="Category navigation">
    <a href="frontend.html" class="active">💻 Frontend</a>
    <a href="ui-ux.html">🎨 UI/UX</a>
    <a href="mobile.html">📱 Mobile</a>
</nav>
```

### Deep Linking & Anchor Navigation

**URL Structure:**
```
docs/knowledge/index.html                    → Domain overview
docs/knowledge/index.html#frontend-ui         → Scroll to Frontend & UI domain
docs/knowledge/frontend.html                  → Frontend category
docs/knowledge/frontend.html#files            → Knowledge files tab
docs/knowledge/frontend/react.html            → React knowledge file
docs/knowledge/frontend/react.html#rule-123   → Specific rule
```

**Anchor Links:**
```html
<!-- On index.html -->
<a href="frontend.html#files">View all Frontend files →</a>

<!-- On category pages -->
<a href="#learning-resources">Jump to Learning Resources ↓</a>

<!-- Smooth scroll -->
<script>
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
</script>
```

---

## 📐 Implementation Phases (REVISED)

### CRITICAL: Styling Standards Compliance

**All pages MUST follow:**
1. **documentation-styling-standards.md v1.1.0** (PRIMARY authority)
2. **docgen.old v4.2** glassmorphism base (SECONDARY, overridden by standards)

**Key Requirements:**
- ✅ Logo: 300px desktop, 200px mobile (`.page-logo`)
- ✅ Icons: 2.4rem (phase-icon, tier-icon) - 20% larger than docgen base
- ✅ Panel spacing: var(--spacing-2xl) = 48px minimum between sections
- ✅ Typography: 1.0625rem (17px) lists, line-height 1.5 (lists), 1.7 (body)
- ✅ Bullets: CSS `::before` with `position: absolute`, 1.5rem, `--accent-primary`
- ✅ Zero inline styles (except story button image per docgen.old)
- ✅ Mobile breakpoints: 320px, 768px, 1024px
- ✅ Single CSS file: `docs/assets/css/main.css` (NO alternate CSS files)

**Conflict Resolution Matrix:**

| Element | docgen.old | documentation-styling-standards.md | WINNER |
|---------|------------|-----------------------------------|--------|
| Logo size | Not specified | 300px desktop, 200px mobile | **Standards** |
| Icon size | 2rem | 2.4rem (phase/tier icons) | **Standards** |
| Panel spacing | var(--spacing-xl) | var(--spacing-2xl) = 48px | **Standards** |
| List bullets | CSS ::before | CSS ::before + position: absolute | **Standards** |
| Bullet size | Not specified | 1.5rem | **Standards** |
| Line-height | 1.6 | 1.5 (lists), 1.7 (body) | **Standards** |
| Inline styles | ZERO (except story) | ZERO (except story) | **Agreement** |
| CSS centralization | main.css only | main.css only | **Agreement** |
| Mobile breakpoints | 768px, 1024px | 320px, 768px, 1024px | **Standards** (adds 320px) |
| Version numbers | Remove from UI | Remove from UI | **Agreement** |
| Navigation buttons | Desktop: text, Mobile: arrows | Desktop: text, Mobile: arrows | **Agreement** |

---

### Phase 0: Knowledge Library Audit & Expansion (Day 1 - 8 hours)
**No changes** - Create 42+ new YAML files

---

### Phase 1: Information Architecture & UX Design (Day 2 - 6 hours) 🆕

**Objectives:**
- Design 4-level information hierarchy
- Group 17 categories into 5 domains
- Create wireframes for all 4 levels
- Define navigation patterns (breadcrumbs, back buttons, deep linking)
- Design progressive disclosure patterns (accordions, tabs, expandable cards)

**Deliverables:**
- `context/information-architecture.md` (4-level hierarchy diagram)
- `context/domain-groups-mapping.yaml` (17 categories → 5 domains)
- `artifacts/wireframes/` (4 wireframe sketches: home, domain, category, file)
- `artifacts/navigation-patterns.html` (breadcrumb examples, tab UI mockup)
- `artifacts/progressive-disclosure-components.html` (accordion, expandable card mockups)

**Domain Grouping:**
```yaml
domains:
  frontend_ui:
    name: "Frontend & UI"
    icon: "🎨"
    categories: ["frontend", "ui-ux", "mobile"]
    description: "User-facing technologies and design patterns"
    
  backend_apis:
    name: "Backend & APIs"
    icon: "🔌"
    categories: ["api", "microservices", "messaging"]
    description: "Server-side architecture and integration patterns"
    
  data_storage:
    name: "Data & Storage"
    icon: "🗄️"
    categories: ["databases", "performance"]
    description: "Data modeling, storage, and optimization"
    
  infrastructure:
    name: "Infrastructure"
    icon: "☁️"
    categories: ["cloud", "containers", "devops"]
    description: "Deployment, orchestration, and operations"
    
  software_craft:
    name: "Software Craft"
    icon: "🏗️"
    categories: ["engineering", "ddd", "security", "testing", "domains"]
    description: "Core software engineering principles and practices"
```

**TDD Requirements:**
- Test: All 17 categories mapped to exactly 1 domain
- Test: Domain grouping makes logical sense (peer review)
- Test: Wireframes pass accessibility review (semantic HTML)

---

### Phase 1.5: 🔍 Quality Review & Styling Standards Compliance (Day 1.5 - 3 hours) 🆕

**CRITICAL: Execute AFTER Phase 4 (all 17 category pages complete) and BEFORE Phase 5**

**Objectives:**
- Comprehensive review of ALL generated knowledge library files
- Enforce compliance with **documentation-styling-standards.md v1.1.0** (PRIMARY authority)
- Override any conflicting rules from **docgen.old v4.2** (SECONDARY authority)
- Run automated HTML quality tools to detect violations
- Fix all styling inconsistencies before proceeding to Phase 5 (knowledge file pages)

**Scope:**
- 6 completed category pages: api-design.html, microservices.html, database.html, testing.html, engineering.html, ddd.html
- 11 pending category pages (once Phase 4 completes)
- 1 domain overview page (docs/knowledge/index.html, once created)
- 1 home page integration (docs/index.html tile, once updated)

**Deliverables:**
1. **Quality Review Checklist Report** (cortex-brain/documents/planning/active/knowledge-documentation/quality-review-checklist.md)
2. **HTML Validator Report** (automated via html_validator.py)
3. **Style Centralizer Report** (automated via html_style_centralizer.py)
4. **Compliance Matrix** (documents which files passed/failed each standard)
5. **Fix Log** (list of corrected violations with before/after examples)

---

#### **Automated Tools Execution (MANDATORY)**

**Location:** `cortex-toolkit/documentation/html-tools/`

**Step 1: HTML Syntax Validation**
```bash
# Run syntax validator on ALL knowledge library pages
python3 cortex-toolkit/documentation/html-tools/html_validator.py

# Expected Output:
# ✅ All 17 files are syntactically correct
# OR
# ❌ Syntax errors in X files:
#    - docs/knowledge/frontend.html: Line 42: Unclosed <div> tag
#    - docs/knowledge/api-design.html: Line 89: Missing closing </section>
```

**Step 2: Inline Style Removal**
```bash
# Remove ALL inline styles, centralize to main.css
python3 cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Expected Output:
# ✅ Processed 17 files
# ✅ Removed 0 inline styles (if already compliant)
# OR
# 🔧 Removed X inline styles from Y files:
#    - docs/knowledge/ddd.html: Removed 3 styles (lines 45, 67, 102)
#    - docs/knowledge/engineering.html: Removed 1 style (line 234)
```

**Allowed Exceptions (DO NOT flag as violations):**
1. `docs/story/viewer.html` - Legacy story viewer (3 inline styles preserved per docgen.old)
2. D3.js dynamic styling - `style="background: ${d.color}"` (runtime-generated, cannot be centralized)

**Failure Mode:**
- If html_validator.py reports errors: STOP, fix syntax errors before proceeding
- If html_style_centralizer.py removes >0 styles: Review changes, commit, re-validate

---

#### **Manual Compliance Checklist (Per File)**

**Use this checklist for EACH of 17 category pages + domain overview + home tile:**

**✅ Logo Compliance (documentation-styling-standards.md Section: Logo Standards)**
- [ ] Logo uses `.page-logo` class (NO inline width attribute)
- [ ] Desktop: Logo CSS width = 300px
- [ ] Mobile (<768px): Logo CSS width = 200px
- [ ] Logo has glow effect: `filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5))`
- [ ] Logo centered via `.logo-header` container

**✅ Icon Compliance (documentation-styling-standards.md Section: Icon Sizing Standards)**
- [ ] Phase icons use `.phase-icon` class with `font-size: 2.4rem`
- [ ] Tier/card icons use `.tier-icon` class with `font-size: 2.4rem`
- [ ] NO icons sized at 2rem (docgen.old base, must be 2.4rem per standards)

**✅ Panel Spacing (documentation-styling-standards.md Section: Spacing Standards)**
- [ ] All `.glass-card` have `margin-bottom: var(--spacing-2xl)` (48px)
- [ ] All major sections have `margin-top: var(--spacing-2xl)` (48px)
- [ ] NO panels with <48px spacing (prevents visual cramping)

**✅ Typography (documentation-styling-standards.md Section: Typography Standards)**
- [ ] Body text: `font-size: 1rem` (16px), `line-height: 1.7`
- [ ] Feature list items: `font-size: 1.0625rem` (17px)
- [ ] Phase titles: `font-size: 1.125rem` (18px)
- [ ] Tier titles: `font-size: 1.375rem` (22px)
- [ ] NO text smaller than 14px (accessibility minimum)

**✅ List & Bullet Compliance (documentation-styling-standards.md Section: List & Bullet Standards)**
- [ ] Lists use `.feature-list` class
- [ ] Bullets generated via CSS `::before` with `content: "•"`
- [ ] Bullets use `position: absolute`, `left: 0.5rem`, `top: 0.125rem`
- [ ] Bullet size: `font-size: 1.5rem` (24px)
- [ ] Bullet color: `color: var(--accent-primary)` (brand cyan)
- [ ] NO bullet characters in HTML markup (e.g., `<li>• Item</li>` is FORBIDDEN)
- [ ] List item padding: `padding: var(--spacing-xs) var(--spacing-sm) var(--spacing-xs) 2rem`
- [ ] NO margin-bottom between list items (`margin-bottom: 0`)
- [ ] Line-height: `line-height: 1.5` (compact for lists)

**✅ Mobile Responsiveness (documentation-styling-standards.md Section: Responsive Design Requirements)**
- [ ] Breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop)
- [ ] Logo scales: 200px at 768px and below
- [ ] Cards stack vertically: `grid-template-columns: 1fr` at 480px and below
- [ ] Touch targets: Minimum 44x44px (buttons, links)
- [ ] Text remains readable: Never below 14px on mobile

**✅ Color & Theme Compliance (documentation-styling-standards.md Section: Color & Visual Standards)**
- [ ] Background gradient: `linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)`
- [ ] Accent primary: `#00d4ff` (CORTEX cyan)
- [ ] Accent secondary: `#7b61ff` (purple)
- [ ] All cards use glassmorphism: `background: rgba(26, 31, 58, 0.7)`, `backdrop-filter: blur(10px)`
- [ ] Border: `border: 1px solid rgba(255, 255, 255, 0.1)`

**✅ Inline Style Prohibition (documentation-styling-standards.md Section: Glassmorphism Styling Enforcement)**
- [ ] ZERO inline `style=""` attributes (except story button image per docgen.old)
- [ ] ZERO page-specific `<style>` tags
- [ ] ALL styling via `<link rel="stylesheet" href="../assets/css/main.css">`
- [ ] NO alternate CSS files (e.g., `technical/assets/styles/glassmorphism.css` is FORBIDDEN)

**✅ Version Number Removal (documentation-styling-standards.md Section: Version Number Removal Policy)**
- [ ] NO version numbers in page titles (e.g., "Planning System 2.0" → "Planning System")
- [ ] NO version numbers in H1 headers
- [ ] NO "Production Ready" or status badges in main content
- [ ] Version metadata allowed in footer only

---

#### **Compliance Matrix Template**

**Create:** `cortex-brain/documents/planning/active/knowledge-documentation/compliance-matrix.md`

**Format:**
```markdown
# Knowledge Library Styling Standards Compliance Matrix

**Review Date:** December 28, 2025  
**Reviewer:** Asif Hussain  
**Standards Version:** documentation-styling-standards.md v1.1.0

| File | Logo | Icons | Spacing | Typography | Bullets | Mobile | Colors | Inline Styles | Status |
|------|------|-------|---------|------------|---------|--------|--------|---------------|--------|
| api-design.html | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| microservices.html | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| database.html | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | WARN |
| testing.html | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| engineering.html | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| ddd.html | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| devops.html | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | PENDING |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Legend:**
- ✅ PASS: Fully compliant
- ⚠️ WARN: Minor issues (document in Fix Log)
- ❌ FAIL: Major violations (MUST fix before Phase 5)
- ⏳ PENDING: Not yet reviewed

**Overall Compliance Rate:** 6/6 completed pages = 100% (as of Phase 4 completion)
```

---

#### **Fix Log Template**

**Create:** `cortex-brain/documents/planning/active/knowledge-documentation/fix-log.md`

**Format:**
```markdown
# Knowledge Library Styling Fixes Log

**Review Date:** December 28, 2025  
**Standards Version:** documentation-styling-standards.md v1.1.0

---

## File: database.html

**Issue #1: Bullet Characters in HTML**
- **Category:** List & Bullet Standards (CRITICAL)
- **Violation:** Line 67: `<li>• Use indexes for foreign keys</li>`
- **Standard:** Bullets MUST be CSS-generated via `::before`, NOT HTML text
- **Fix:** Remove "•" from HTML, ensure `.feature-list li::before` CSS exists
- **Before:**
  ```html
  <li>• Use indexes for foreign keys</li>
  ```
- **After:**
  ```html
  <li>Use indexes for foreign keys</li>
  ```
- **Status:** ✅ FIXED (Commit: abc123)

**Issue #2: Panel Spacing Too Tight**
- **Category:** Spacing Standards (MEDIUM)
- **Violation:** Line 102: `.glass-card` has `margin-bottom: 24px` (should be 48px)
- **Standard:** Minimum 48px (`var(--spacing-2xl)`) between panels
- **Fix:** Update CSS class usage
- **Before:**
  ```html
  <div class="glass-card" style="margin-bottom: 24px;">
  ```
- **After:**
  ```html
  <div class="glass-card">
  ```
- **Status:** ✅ FIXED (Commit: abc124)

---

## File: frontend.html

**No violations found.** ✅ FULLY COMPLIANT

---
```

---

#### **Validation Workflow**

**Execute in this order:**

1. **Run Automated Tools**
   ```bash
   # Step 1: Syntax validation
   python3 cortex-toolkit/documentation/html-tools/html_validator.py > validation-report.txt
   
   # Step 2: Inline style removal
   python3 cortex-toolkit/documentation/html-tools/html_style_centralizer.py > centralization-report.txt
   
   # Review reports
   cat validation-report.txt
   cat centralization-report.txt
   ```

2. **Manual Compliance Review**
   - Open each category page in browser
   - Go through checklist section by section
   - Use browser DevTools to inspect CSS (logo width, icon size, spacing)
   - Test mobile responsiveness (Chrome DevTools device emulation)
   - Record findings in Compliance Matrix

3. **Fix Violations**
   - Prioritize CRITICAL issues first (inline styles, HTML syntax errors)
   - Then MEDIUM issues (spacing, typography)
   - Finally LOW issues (version numbers, minor styling)
   - Document each fix in Fix Log

4. **Re-validate**
   - Re-run automated tools
   - Verify fixes in browser
   - Update Compliance Matrix status to PASS

5. **Git Commit**
   ```bash
   git add docs/knowledge/*.html
   git add cortex-brain/documents/planning/active/knowledge-documentation/compliance-matrix.md
   git add cortex-brain/documents/planning/active/knowledge-documentation/fix-log.md
   git commit -m "docs(knowledge): Phase 4.5 quality review - 100% styling standards compliance"
   ```

---

#### **Success Criteria (MUST PASS before Phase 5)**

- [ ] **html_validator.py:** 0 syntax errors across all 17 category pages
- [ ] **html_style_centralizer.py:** 0 inline styles detected (or 0 remaining after removal)
- [ ] **Compliance Matrix:** 100% PASS rate (all ✅, no ❌ FAIL status)
- [ ] **Fix Log:** All documented issues marked as ✅ FIXED with commit hashes
- [ ] **Manual Testing:**
  - [ ] All pages render correctly in Chrome/Safari/Firefox
  - [ ] Mobile responsive at 320px, 768px, 1024px breakpoints
  - [ ] Logo scales properly (300px desktop, 200px mobile)
  - [ ] Icons sized at 2.4rem (NOT 2rem)
  - [ ] Panel spacing ≥48px between sections
  - [ ] Bullets CSS-generated (absolute positioning, 1.5rem, brand color)
  - [ ] Typography matches standards (17px lists, line-height 1.5/1.7)
  - [ ] Zero inline styles (except story button)
  - [ ] Single CSS file (main.css) used across all pages

**If ANY criteria fails:** Fix issues, re-validate, and re-commit before proceeding to Phase 5.

---

### Phase 2: Home Page Integration (Day 2 - 2 hours)

**Objectives:**
- Add Knowledge Library tile to docs/index.html Core Capabilities
- Tile navigates to Level 2 (domain overview)

**Deliverables:**
- Updated `docs/index.html` with 7th tile

**Implementation:**
```html
<article class="glass-card">
    <h3>📚 Knowledge Library</h3>
    <p>80+ best practices across 17 categories: Frontend, APIs, Cloud, Microservices, Security—organized by domain with progressive drill-down navigation.</p>
    <a href="knowledge/index.html" class="btn-link">Explore Library →</a>
</article>
```

**TDD Requirements:**
- Test: Tile same height/width as existing tiles
- Test: Link navigates to knowledge/index.html
- Test: Mobile responsive

---

### Phase 3: Domain Overview Page (Day 3 - 8 hours) 🆕

**Objectives:**
- Create Level 2 page: docs/knowledge/index.html
- Display 5 domain groups as large cards
- Each domain card shows contained categories
- D3.js category relationship diagram (optional, below fold)
- Search functionality filters domains and categories

**Deliverables:**
- `docs/knowledge/index.html` (domain overview with 5 cards)
- Domain cards with category previews
- Sticky breadcrumb navigation
- Search bar with live filtering

**Page Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="../assets/css/main.css">
    <title>CORTEX Knowledge Library</title>
</head>
<body>
    <!-- Sticky Breadcrumb -->
    <nav class="breadcrumb-container sticky-nav">
        <button class="back-button" onclick="history.back()">← Back</button>
        <ol class="breadcrumb">
            <li><a href="../index.html">Home</a></li>
            <li aria-current="page">Knowledge Library</li>
        </ol>
    </nav>

    <!-- Logo Header -->
    <div class="logo-header">
        <img src="../assets/images/CORTEX-logo.png" class="page-logo" alt="CORTEX Logo">
    </div>

    <!-- Title -->
    <h1>📚 Knowledge Library</h1>

    <!-- Feature Benefit Panel -->
    <div class="feature-benefit-panel">
        <h2>Discover Industry-Standard Best Practices</h2>
        <p class="description">
            CORTEX references 80+ machine-readable knowledge files across 17 categories 
            organized into 5 domains. Explore by domain, drill down to categories, and 
            discover rules with examples and learning resources.
        </p>
    </div>

    <!-- Search Bar -->
    <div class="search-container">
        <input type="text" id="knowledge-search" 
               placeholder="Search domains, categories, or technologies..." 
               class="search-input">
    </div>

    <!-- Domain Groups Grid -->
    <div class="domain-grid">
        <!-- Frontend & UI Domain -->
        <article class="domain-card glass-card" data-domain="frontend-ui">
            <div class="domain-header">
                <span class="domain-icon">🎨</span>
                <h2>Frontend & UI</h2>
                <span class="badge badge-info">3 categories • 14 files</span>
            </div>
            <p class="domain-description">
                User-facing technologies and design patterns for web and mobile applications.
            </p>
            <div class="category-preview">
                <a href="frontend.html" class="category-chip">💻 Frontend (8)</a>
                <a href="ui-ux.html" class="category-chip">🎨 UI/UX (2)</a>
                <a href="mobile.html" class="category-chip">📱 Mobile (4)</a>
            </div>
            <a href="#frontend-ui" class="btn-link">Explore Domain →</a>
        </article>

        <!-- Backend & APIs Domain -->
        <article class="domain-card glass-card" data-domain="backend-apis">
            <div class="domain-header">
                <span class="domain-icon">🔌</span>
                <h2>Backend & APIs</h2>
                <span class="badge badge-info">3 categories • 17 files</span>
            </div>
            <p class="domain-description">
                Server-side architecture, integration patterns, and communication protocols.
            </p>
            <div class="category-preview">
                <a href="api.html" class="category-chip">🔌 API (6)</a>
                <a href="microservices.html" class="category-chip">🏗️ Microservices (7)</a>
                <a href="messaging.html" class="category-chip">📨 Messaging (4)</a>
            </div>
            <a href="#backend-apis" class="btn-link">Explore Domain →</a>
        </article>

        <!-- Data & Storage Domain -->
        <article class="domain-card glass-card" data-domain="data-storage">
            <div class="domain-header">
                <span class="domain-icon">🗄️</span>
                <h2>Data & Storage</h2>
                <span class="badge badge-info">2 categories • 11 files</span>
            </div>
            <p class="domain-description">
                Data modeling, storage strategies, and performance optimization techniques.
            </p>
            <div class="category-preview">
                <a href="databases.html" class="category-chip">🗄️ Databases (8)</a>
                <a href="performance.html" class="category-chip">⚡ Performance (3)</a>
            </div>
            <a href="#data-storage" class="btn-link">Explore Domain →</a>
        </article>

        <!-- Infrastructure Domain -->
        <article class="domain-card glass-card" data-domain="infrastructure">
            <div class="domain-header">
                <span class="domain-icon">☁️</span>
                <h2>Infrastructure</h2>
                <span class="badge badge-info">3 categories • 16 files</span>
            </div>
            <p class="domain-description">
                Cloud platforms, container orchestration, and deployment automation.
            </p>
            <div class="category-preview">
                <a href="cloud.html" class="category-chip">☁️ Cloud (6)</a>
                <a href="containers.html" class="category-chip">🐳 Containers (5)</a>
                <a href="devops.html" class="category-chip">⚙️ DevOps (5)</a>
            </div>
            <a href="#infrastructure" class="btn-link">Explore Domain →</a>
        </article>

        <!-- Software Craft Domain -->
        <article class="domain-card glass-card" data-domain="software-craft">
            <div class="domain-header">
                <span class="domain-icon">🏗️</span>
                <h2>Software Craft</h2>
                <span class="badge badge-info">6 categories • 27 files</span>
            </div>
            <p class="domain-description">
                Core engineering principles, architecture patterns, and quality practices.
            </p>
            <div class="category-preview">
                <a href="engineering.html" class="category-chip">🏗️ Engineering (8)</a>
                <a href="ddd.html" class="category-chip">📐 DDD (6)</a>
                <a href="security.html" class="category-chip">🔒 Security (4)</a>
                <a href="testing.html" class="category-chip">🧪 Testing (5)</a>
                <a href="domains.html" class="category-chip">🧠 AI Domains (4)</a>
            </div>
            <a href="#software-craft" class="btn-link">Explore Domain →</a>
        </article>
    </div>

    <!-- Optional: D3.js Diagram (below fold, lazy loaded) -->
    <section class="glass-card" data-lazy-load>
        <h2>Category Relationships</h2>
        <p>Visualize how knowledge categories interconnect across domains.</p>
        <div id="category-graph" style="width: 100%; height: 600px;"></div>
    </section>

</body>
</html>
```

**CSS for Domain Cards:**
```css
.domain-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-xl);
    margin: var(--spacing-2xl) 0;  /* 48px per styling standards */
}

.domain-card {
    padding: var(--spacing-xl);
    transition: transform var(--transition-base);
}

.domain-card:hover {
    transform: translateY(-8px);
}

.domain-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}

.domain-icon {
    font-size: 2.4rem;  /* Per styling standards (tier-icon sizing) */
}

.category-preview {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
    margin: var(--spacing-md) 0;
}

.category-chip {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    text-decoration: none;
    color: var(--accent-primary);
    transition: all var(--transition-base);
}

.category-chip:hover {
    background: rgba(0, 212, 255, 0.2);
    border-color: var(--accent-primary);
}

/* Mobile optimization */
@media (max-width: 767px) {
    .domain-grid {
        grid-template-columns: 1fr;
    }
    
    .domain-icon {
        font-size: 2.4rem;  /* Maintain size on mobile per standards */
    }
}
```

**TDD Requirements:**
- Test: All 5 domain cards render correctly
- Test: Category chips navigate to correct category pages
- Test: Search filters domains and categories
- Test: Mobile: Cards stack vertically
- Test: D3.js diagram lazy loads (Intersection Observer)
- Test: Icon sizing matches documentation-styling-standards.md (2.4rem)
- Test: Panel spacing matches standards (48px minimum)

---

### Phase 4: Category Detail Pages (Days 4-5 - 20 hours) 🆕

**Objectives:**
- Create 17 category pages (Level 3) with tabbed interface
- Each page has 4 tabs: Overview, Knowledge Files, Learning Resources, CORTEX Usage
- Knowledge files displayed as collapsible accordion
- Mermaid concept diagram in Overview tab
- Sticky breadcrumb with sibling navigation

**Deliverables:**
- 17 HTML files with tabbed UI and accordion
- Mermaid diagrams for each category
- Category sidebar/bottom nav for sibling navigation

**Page Structure (e.g., frontend.html):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="../assets/css/main.css">
    <title>CORTEX Knowledge - Frontend</title>
</head>
<body>
    <!-- Sticky Breadcrumb with Sibling Nav -->
    <nav class="breadcrumb-container sticky-nav">
        <button class="back-button" onclick="history.back()">← Back</button>
        <ol class="breadcrumb">
            <li><a href="../index.html">Home</a></li>
            <li><a href="index.html">Knowledge Library</a></li>
            <li><a href="index.html#frontend-ui">Frontend & UI</a></li>
            <li aria-current="page">Frontend</li>
        </ol>
    </nav>

    <!-- Main Content with Sidebar (Desktop) -->
    <div class="page-layout">
        <!-- Sidebar (Desktop only) -->
        <aside class="category-sidebar">
            <h3>Frontend & UI</h3>
            <nav class="category-nav">
                <a href="frontend.html" class="active">
                    <span class="nav-icon">💻</span>
                    <span class="nav-text">Frontend</span>
                    <span class="nav-badge badge badge-info">8</span>
                </a>
                <a href="ui-ux.html">
                    <span class="nav-icon">🎨</span>
                    <span class="nav-text">UI/UX</span>
                    <span class="nav-badge badge badge-info">2</span>
                </a>
                <a href="mobile.html">
                    <span class="nav-icon">📱</span>
                    <span class="nav-text">Mobile</span>
                    <span class="nav-badge badge badge-info">4</span>
                </a>
            </nav>
        </aside>

        <!-- Main Content Area -->
        <main class="category-content">
            <!-- Logo & Title -->
            <div class="category-header">
                <span class="category-icon">💻</span>
                <h1>Frontend Development</h1>
            </div>

            <!-- Feature Benefit Panel -->
            <div class="feature-benefit-panel">
                <h2>Master Modern Web Development</h2>
                <p class="description">
                    Build responsive, accessible web applications using HTML5, CSS3, JavaScript ES6+, 
                    TypeScript, and modern frameworks like React, Angular, and Vue. These best practices 
                    ensure your frontend code is maintainable, performant, and follows industry standards.
                </p>
            </div>

            <!-- Tabbed Interface -->
            <div class="tabs-container">
                <div class="tabs-nav" role="tablist">
                    <button class="tab-button active" role="tab" data-tab="overview">
                        📖 Overview
                    </button>
                    <button class="tab-button" role="tab" data-tab="files">
                        📄 Knowledge Files (8)
                    </button>
                    <button class="tab-button" role="tab" data-tab="resources">
                        🎓 Learning Resources
                    </button>
                    <button class="tab-button" role="tab" data-tab="usage">
                        🔗 CORTEX Usage
                    </button>
                </div>

                <!-- Tab 1: Overview -->
                <div class="tab-content active" id="overview-tab">
                    <section class="glass-card">
                        <h2>What is Frontend Development?</h2>
                        <ul class="feature-list">
                            <li><strong>Purpose:</strong> Build user-facing web applications</li>
                            <li><strong>Technologies:</strong> HTML, CSS, JavaScript, TypeScript, React/Angular/Vue</li>
                            <li><strong>Key Concepts:</strong> Semantic HTML, responsive design, component architecture</li>
                        </ul>
                    </section>

                    <!-- Mermaid Diagram -->
                    <section class="glass-card">
                        <h2>Frontend Technology Stack</h2>
                        <div class="mermaid-container">
                            <div class="mermaid">
graph LR
    HTML[HTML5 Semantic] --> CSS[CSS3 Modern]
    CSS --> JS[JavaScript ES6+]
    JS --> TS[TypeScript]
    TS --> REACT[React/Hooks]
    TS --> ANGULAR[Angular/RxJS]
    TS --> VUE[Vue/Composition]
    
    REACT --> API[REST/GraphQL]
    ANGULAR --> API
    VUE --> API
    
    style HTML fill:#e3f2fd
    style REACT fill:#61dafb
    style ANGULAR fill:#dd0031
    style VUE fill:#42b883
                            </div>
                        </div>
                    </section>

                    <!-- Quick Stats -->
                    <section class="glass-card">
                        <h2>Quick Stats</h2>
                        <div class="metrics-grid-3">
                            <div class="metric-card">
                                <div class="metric-value">8</div>
                                <div class="metric-label">Knowledge Files</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">~150</div>
                                <div class="metric-label">Total Rules</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">5+</div>
                                <div class="metric-label">Learning Resources</div>
                            </div>
                        </div>
                    </section>
                </div>

                <!-- Tab 2: Knowledge Files (Accordion) -->
                <div class="tab-content" id="files-tab" hidden>
                    <section class="glass-card">
                        <h2>Knowledge Files (8)</h2>
                        <p>Click to expand and view details, or navigate to full documentation.</p>
                        
                        <div class="knowledge-files-accordion">
                            <!-- Accordion Item 1 -->
                            <div class="accordion-item">
                                <button class="accordion-header" aria-expanded="false">
                                    <span class="accordion-icon">📄</span>
                                    <span class="accordion-title">HTML5 Best Practices</span>
                                    <span class="accordion-badge badge badge-info">~20 rules</span>
                                    <span class="accordion-chevron">▼</span>
                                </button>
                                <div class="accordion-content" hidden>
                                    <p>Semantic HTML, forms, validation, accessibility, SEO optimization.</p>
                                    <ul>
                                        <li><strong>HIGH:</strong> Use semantic elements (&lt;header&gt;, &lt;nav&gt;, &lt;main&gt;)</li>
                                        <li><strong>MEDIUM:</strong> Implement proper form validation</li>
                                    </ul>
                                    <a href="frontend/html5-best-practices.html" class="btn-link">View Full Details →</a>
                                </div>
                            </div>

                            <!-- Accordion Item 2 -->
                            <div class="accordion-item">
                                <button class="accordion-header" aria-expanded="false">
                                    <span class="accordion-icon">📄</span>
                                    <span class="accordion-title">CSS3 Modern Techniques</span>
                                    <span class="accordion-badge badge badge-info">~25 rules</span>
                                    <span class="accordion-chevron">▼</span>
                                </button>
                                <div class="accordion-content" hidden>
                                    <p>Flexbox, Grid, CSS Variables, animations, transitions.</p>
                                    <ul>
                                        <li><strong>HIGH:</strong> Use CSS Grid for layout</li>
                                        <li><strong>MEDIUM:</strong> Leverage CSS Variables for theming</li>
                                    </ul>
                                    <a href="frontend/css3-modern-techniques.html" class="btn-link">View Full Details →</a>
                                </div>
                            </div>

                            <!-- Repeat for all 8 files... -->
                        </div>
                    </section>
                </div>

                <!-- Tab 3: Learning Resources -->
                <div class="tab-content" id="resources-tab" hidden>
                    <section class="glass-card">
                        <h2>🎓 Learning Resources</h2>
                        
                        <div class="resource-list">
                            <div class="resource-item">
                                <span class="resource-icon">📺</span>
                                <div class="resource-content">
                                    <strong>YouTube:</strong> "JavaScript Tutorial for Beginners" - Mosh Hamedani
                                    <a href="https://youtube.com/..." target="_blank" rel="noopener">Watch →</a>
                                </div>
                            </div>
                            
                            <div class="resource-item">
                                <span class="resource-icon">📚</span>
                                <div class="resource-content">
                                    <strong>Book:</strong> Eloquent JavaScript (FREE online) - Marijn Haverbeke
                                </div>
                            </div>
                            
                            <div class="resource-item">
                                <span class="resource-icon">🔗</span>
                                <div class="resource-content">
                                    <strong>Official:</strong> MDN Web Docs
                                    <a href="https://developer.mozilla.org" target="_blank" rel="noopener">Visit →</a>
                                </div>
                            </div>
                            
                            <div class="resource-item">
                                <span class="resource-icon">🎓</span>
                                <div class="resource-content">
                                    <strong>Course:</strong> Frontend Masters - Complete Path (PAID)
                                    <a href="https://frontendmasters.com" target="_blank" rel="noopener">Enroll →</a>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>

                <!-- Tab 4: CORTEX Usage -->
                <div class="tab-content" id="usage-tab" hidden>
                    <section class="glass-card">
                        <h2>How CORTEX Uses Frontend Knowledge</h2>
                        <ul class="feature-list">
                            <li><strong>Code Review Orchestrator:</strong> Validates HTML semantics, CSS best practices</li>
                            <li><strong>Documentation Generator:</strong> Creates component documentation</li>
                            <li><strong>Sanitization:</strong> Removes company-specific CSS classes</li>
                        </ul>
                    </section>
                </div>
            </div>
        </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="bottom-nav" aria-label="Category navigation">
        <a href="frontend.html" class="active">
            <span class="nav-icon">💻</span>
            <span class="nav-text">Frontend</span>
        </a>
        <a href="ui-ux.html">
            <span class="nav-icon">🎨</span>
            <span class="nav-text">UI/UX</span>
        </a>
        <a href="mobile.html">
            <span class="nav-icon">📱</span>
            <span class="nav-text">Mobile</span>
        </a>
    </nav>

    <!-- JavaScript for Tabs & Accordions -->
    <script src="../assets/js/progressive-disclosure.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'dark' });
    </script>
</body>
</html>
```

**JavaScript (progressive-disclosure.js):**
```javascript
// Tab Switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });
        button.classList.add('active');
        button.setAttribute('aria-selected', 'true');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            content.hidden = true;
        });
        const activeContent = document.getElementById(`${tabId}-tab`);
        activeContent.classList.add('active');
        activeContent.hidden = false;
    });
});

// Accordion Toggle
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
        const isExpanded = header.getAttribute('aria-expanded') === 'true';
        const content = header.nextElementSibling;
        
        header.setAttribute('aria-expanded', !isExpanded);
        content.hidden = isExpanded;
        
        // Smooth height animation
        if (!isExpanded) {
            content.style.maxHeight = content.scrollHeight + 'px';
        } else {
            content.style.maxHeight = '0';
        }
    });
});

// Remember active tab in URL hash
window.addEventListener('load', () => {
    const hash = window.location.hash.slice(1);
    if (hash) {
        const button = document.querySelector(`[data-tab="${hash}"]`);
        if (button) button.click();
    }
});

// Update URL hash when tab changes
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        window.location.hash = button.dataset.tab;
    });
});
```

**TDD Requirements:**
- Test: All 17 category pages load without errors
- Test: Tab switching works (keyboard accessible)
- Test: Accordion expands/collapses smoothly
- Test: Breadcrumb navigation functional
- Test: Sidebar navigation highlights active category
- Test: Mobile: Bottom nav replaces sidebar
- Test: Mermaid diagrams render correctly
- Test: Icon sizing matches documentation-styling-standards.md (2.4rem for category icons)
- Test: Panel spacing matches standards (48px minimum between glass-card elements)
- Test: Typography matches standards (1.0625rem/17px for feature lists, line-height 1.5)
- Test: Bullets generated via CSS ::before with position: absolute (NO bullets in HTML)

---

### Phase 5: Knowledge File Detail Pages (Day 6 - 8 hours) 🆕

**Objectives:**
- Create Level 4 pages for individual knowledge files
- Show all rules with code examples
- Syntax highlighting for code snippets
- Cross-references to related knowledge files
- Sticky table of contents sidebar

**Deliverables:**
- 80+ HTML files (one per YAML file)
- Syntax-highlighted code examples
- Cross-reference links

**Page Structure (e.g., frontend/react-best-practices.html):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="../../assets/css/main.css">
    <link rel="stylesheet" href="../../assets/css/prism.css">
    <title>CORTEX Knowledge - React Best Practices</title>
</head>
<body>
    <!-- Sticky Breadcrumb -->
    <nav class="breadcrumb-container sticky-nav">
        <button class="back-button" onclick="history.back()">← Back</button>
        <ol class="breadcrumb">
            <li><a href="../../index.html">Home</a></li>
            <li><a href="../index.html">Knowledge Library</a></li>
            <li><a href="../index.html#frontend-ui">Frontend & UI</a></li>
            <li><a href="../frontend.html">Frontend</a></li>
            <li aria-current="page">React Best Practices</li>
        </ol>
    </nav>

    <div class="page-layout">
        <!-- Sticky Table of Contents (Desktop) -->
        <aside class="toc-sidebar">
            <h3>Contents</h3>
            <nav class="toc-nav">
                <a href="#overview">Overview</a>
                <a href="#rules">Rules (35)</a>
                <a href="#rule-001">Use Functional Components</a>
                <a href="#rule-002">Leverage Hooks</a>
                <a href="#rule-003">Implement Error Boundaries</a>
                <!-- ... -->
                <a href="#related">Related Knowledge</a>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="file-content">
            <h1>React Best Practices</h1>
            
            <!-- Metadata -->
            <div class="file-metadata">
                <span class="badge badge-info">35 rules</span>
                <span class="badge badge-secondary">Version 1.0</span>
                <span class="badge badge-secondary">Created: Dec 2025</span>
            </div>

            <!-- Overview -->
            <section class="glass-card" id="overview">
                <h2>Overview</h2>
                <p>React best practices covering Hooks, Context API, performance optimization...</p>
            </section>

            <!-- Rules Section -->
            <section class="glass-card" id="rules">
                <h2>Rules (35)</h2>
                
                <!-- Rule Card (Expandable) -->
                <div class="rule-card" id="rule-001">
                    <div class="rule-header">
                        <span class="rule-icon">⚠️</span>
                        <h3>Rule 001: Use Functional Components</h3>
                        <span class="badge badge-danger">HIGH</span>
                    </div>
                    <div class="rule-body">
                        <p><strong>Description:</strong> Prefer functional components with hooks over class components...</p>
                        
                        <div class="rule-examples">
                            <div class="example-good">
                                <strong>✅ Good Example:</strong>
                                <pre><code class="language-jsx">
function UserProfile({ user }) {
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    fetchUserData(user.id);
  }, [user.id]);
  
  return &lt;div&gt;{user.name}&lt;/div&gt;;
}
                                </code></pre>
                            </div>
                            
                            <div class="example-bad">
                                <strong>❌ Bad Example:</strong>
                                <pre><code class="language-jsx">
class UserProfile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { isLoading: false };
  }
  
  componentDidMount() {
    this.fetchUserData();
  }
  
  render() {
    return &lt;div&gt;{this.props.user.name}&lt;/div&gt;;
  }
}
                                </code></pre>
                            </div>
                        </div>
                        
                        <p><strong>Why:</strong> Functional components are simpler, more performant, and better supported...</p>
                    </div>
                </div>

                <!-- Repeat for all 35 rules... -->
            </section>

            <!-- Related Knowledge -->
            <section class="glass-card" id="related">
                <h2>Related Knowledge</h2>
                <ul class="related-list">
                    <li><a href="javascript-es6-plus.html">JavaScript ES6+ Guidelines</a> - Understand modern JS syntax</li>
                    <li><a href="typescript-guidelines.html">TypeScript Guidelines</a> - Type-safe React components</li>
                    <li><a href="../testing.html#files">Testing Best Practices</a> - Test React components effectively</li>
                </ul>
            </section>
        </main>
    </div>

    <!-- Syntax Highlighting -->
    <script src="../../assets/js/prism.js"></script>
</body>
</html>
```

**TDD Requirements:**
- Test: All 80+ knowledge file pages load
- Test: Syntax highlighting works (Prism.js)
- Test: Table of contents navigation functional
- Test: Cross-references link correctly
- Test: Mobile: TOC collapses into dropdown
- Test: Logo sizing matches standards (300px desktop, 200px mobile)
- Test: Panel spacing matches standards (48px between sections)

---

### Phase 6: Educational Resources Integration (Day 6 - 4 hours)

**No major changes** - Resources integrated into Tab 3 of category pages

---

### Phase 7: Styling & Responsiveness (Day 7 - 6 hours)

**Objectives:**
- Apply 100% glassmorphism styling
- Mobile optimization (accordions, tabs, bottom nav)
- Touch interactions (swipe gestures, tap targets ≥48px)
- Skeleton loaders for lazy-loaded content

**Deliverables:**
- Fully styled pages with centralized CSS
- Mobile-responsive validation report
- Touch interaction testing report

**TDD Requirements:**
- Test: ZERO inline styles (except story button per docgen.old)
- Test: Mobile: All touch targets ≥48px
- Test: Swipe gestures work on category pages
- Test: Accordions animate smoothly (CSS transitions)
- Test: Tabs keyboard accessible (Tab, Arrow keys)
- Test: Logo sizing validated (300px desktop, 200px mobile per standards)
- Test: Icon sizing validated (2.4rem per standards)
- Test: Panel spacing validated (48px minimum per standards)
- Test: Typography validated (17px lists, line-height 1.5/1.7 per standards)
- Test: Bullets validated (CSS ::before, position: absolute, 1.5rem, brand color)
- Test: Mobile breakpoints validated (320px, 768px, 1024px per standards)

---

### Phase 8: Search & Filtering (Day 7 - 3 hours)

**Objectives:**
- Search bar on domain overview page
- Filter domains, categories, and knowledge files
- Search results highlighted
- Search history saved in localStorage

**Deliverables:**
- Search functionality with live filtering
- Search results page (optional)

**TDD Requirements:**
- Test: Search filters domains/categories correctly
- Test: Case-insensitive matching
- Test: Search history persists across sessions

---

### Phase 9: Documentation & Validation (Day 8 - 4 hours)

**Objectives:**
- Final validation of all pages (1 home tile + 1 domain overview + 17 categories + 80+ files = 99+ pages)
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Performance testing (Lighthouse scores)
- Accessibility audit (WCAG AA compliance)

**Deliverables:**
- Validation report
- Completion summary
- Updated README files

**Validation Checklist:**
- [ ] All 99+ pages accessible
- [ ] Breadcrumb navigation functional on all pages
- [ ] Back button works correctly
- [ ] Deep linking works (URL hashes)
- [ ] Accordions/tabs work on all devices
- [ ] Mermaid diagrams render
- [ ] Syntax highlighting works (Prism.js)
- [ ] Touch interactions optimized
- [ ] Lighthouse Performance ≥90
- [ ] Lighthouse Accessibility ≥90
- [ ] No broken links
- [ ] HTML validation passed
- [ ] **Styling Standards Compliance:**
  - [ ] Logo sizing correct (300px desktop, 200px mobile)
  - [ ] Icon sizing correct (2.4rem for phase/tier icons)
  - [ ] Panel spacing correct (48px minimum between sections)
  - [ ] Typography correct (17px lists, line-height 1.5/1.7)
  - [ ] Bullets correct (CSS ::before, position: absolute, 1.5rem, brand color)
  - [ ] ZERO inline styles (except story button)
  - [ ] Mobile breakpoints correct (320px, 768px, 1024px)
  - [ ] Single CSS file (docs/assets/css/main.css only)
  - [ ] No version numbers in UI elements
  - [ ] Navigation buttons correct (desktop: text, mobile: arrows)

---

## 🎯 Definition of Ready (DoR)

- [x] Knowledge library structure stable (38 YAML files + 42 new planned)
- [x] Progressive disclosure patterns defined
- [x] 4-level information architecture designed
- [x] Domain grouping finalized (5 domains, 17 categories)
- [x] Navigation patterns specified (breadcrumbs, tabs, accordions)
- [x] Mobile-first responsive design principles established
- [x] **Styling standards defined** (documentation-styling-standards.md v1.1.0)
- [x] **Conflict resolution matrix** (standards override docgen.old)
- [ ] Phase 0: 42+ new YAML files created
- [ ] Wireframes created for all 4 levels
- [ ] Component library designed (accordion, tabs, cards)

---

## ✅ Definition of Done (DoD)

**Phase 0: Library Expansion:**
- [ ] 42+ new YAML files created across 8 categories
- [ ] All 80+ YAML files validate successfully
- [ ] Category relationships mapped

**Phase 1: Information Architecture:**
- [ ] 4-level hierarchy documented
- [ ] 17 categories grouped into 5 domains
- [ ] Wireframes created for 4 levels
- [ ] Navigation patterns documented

**Home Page Integration:**
- [ ] Knowledge Library tile added to docs/index.html

**Domain Overview Page (Level 2):**
- [ ] 5 domain cards with category previews
- [ ] Search functionality
- [ ] Sticky breadcrumb navigation
- [ ] Optional D3.js diagram

**Category Detail Pages (Level 3):**
- [ ] All 17 category pages with tabbed UI
- [ ] Accordions for knowledge files
- [ ] Mermaid diagrams
- [ ] Sidebar/bottom nav for sibling navigation
- [ ] 4 tabs per page (Overview, Files, Resources, Usage)

**Knowledge File Pages (Level 4):**
- [ ] All 80+ knowledge file pages
- [ ] Syntax-highlighted code examples
- [ ] Table of contents sidebar
- [ ] Cross-references to related files

**Progressive Disclosure:**
- [ ] Accordions expand/collapse smoothly
- [ ] Tabs switch without page reload
- [ ] Breadcrumbs show current location
- [ ] Back button functional everywhere
- [ ] Deep linking works (URL hashes)

**Mobile Optimization:**
- [ ] Touch targets ≥48px
- [ ] Swipe gestures implemented
- [ ] Bottom navigation on mobile
- [ ] Accordions/tabs touch-optimized
- [ ] Lazy loading with skeleton screens

**Styling & Responsiveness:**
- [ ] 100% glassmorphism compliance (ZERO inline styles except story button)
- [ ] Mobile responsive (320px, 768px, 1024px per standards)
- [ ] Typography consistent (17px lists, line-height 1.5/1.7 per standards)
- [ ] Bullets CSS-generated (::before, position: absolute, 1.5rem per standards)
- [ ] Logo sizing correct (300px desktop, 200px mobile per standards)
- [ ] Icon sizing correct (2.4rem phase/tier icons per standards)
- [ ] Panel spacing correct (48px minimum per standards)
- [ ] Single CSS file enforced (docs/assets/css/main.css only)
- [ ] No version numbers in UI elements (per standards policy)

**Educational Resources:**
- [ ] Learning resources in Tab 3 of all 17 category pages
- [ ] All external links validated (no 404s)

**Quality Assurance:**
- [ ] All 99+ pages accessible
- [ ] HTML validation passed
- [ ] CSS validation passed
- [ ] Lighthouse Performance ≥90
- [ ] Lighthouse Accessibility ≥90
- [ ] Cross-browser tested (Chrome, Firefox, Safari, Edge)
- [ ] No broken links
- [ ] **Styling standards validated:**
  - [ ] Logo: 300px desktop, 200px mobile
  - [ ] Icons: 2.4rem (phase/tier)
  - [ ] Spacing: 48px panels
  - [ ] Typography: 17px lists, line-height 1.5/1.7
  - [ ] Bullets: CSS ::before, absolute, 1.5rem
  - [ ] Zero inline styles (except story button)
  - [ ] Mobile breakpoints: 320px, 768px, 1024px

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Phase 0: Library Expansion** | | |
| New YAML Files Created | 42+ | 8 categories with files |
| Total YAML Files | 80+ | 38 existing + 42 new |
| Total Categories | 17 | 9 existing + 8 new |
| **Information Architecture** | | |
| Domain Groups | 5 | Frontend & UI, Backend & APIs, Data & Storage, Infrastructure, Software Craft |
| Hierarchy Levels | 4 | Home → Domain → Category → File |
| **Web Pages** | | |
| Total Pages | 99+ | 1 home + 1 domain + 17 categories + 80+ files |
| Progressive Disclosure Components | 3 | Accordions, Tabs, Expandable Cards |
| **Navigation** | | |
| Breadcrumb Levels | 4 | All pages have breadcrumbs |
| Deep Linking | 100% | All sections have URL hashes |
| Back Button | 100% | Functional on all pages |
| **Mobile Optimization** | | |
| Touch Target Size | ≥48px | All interactive elements |
| Responsive Breakpoints | 3 | 320px, 768px, 1024px |
| Swipe Gestures | Yes | Category navigation |
| Bottom Navigation | Yes | Mobile only |
| **Performance** | | |
| Lighthouse Performance | ≥90 | All pages |
| Lighthouse Accessibility | ≥90 | All pages |
| Page Load Time | <3s | GitHub Pages |
| Lazy Loading | Yes | D3.js diagrams, heavy content |
| **Educational Resources** | ≥5 per category | 85+ total (17 categories × 5) |
| External Link Validation | 100% | No 404 errors |
| **Styling Compliance** | | |
| Logo Sizing | 300px / 200px | Desktop / Mobile |
| Icon Sizing | 2.4rem | Phase/tier icons |
| Panel Spacing | 48px | Min between sections |
| Typography | 17px / 1.5-1.7 | Lists / Line-height |
| Bullet Styling | CSS ::before | Absolute, 1.5rem, brand |
| Inline Styles | 0 | Except story button |
| CSS Files | 1 | main.css only |
| Mobile Breakpoints | 3 | 320px, 768px, 1024px |

---

## 🔄 Progress Tracking

**Phase Status:**
- Phase 0: 🆕 Knowledge Library Audit & Expansion - NOT STARTED (8h)
- Phase 1: 🆕 Information Architecture & UX Design - NOT STARTED (6h)
- Phase 2: 🏠 Home Page Integration - NOT STARTED (2h)
- Phase 3: 🆕 Domain Overview Page (Level 2) - NOT STARTED (8h)
- Phase 4: 📖 Category Detail Pages (17 pages, Level 3) - IN PROGRESS (20h)
  - ✅ api-design.html (1,023 lines) - COMPLETE
  - ✅ microservices.html (1,071 lines) - COMPLETE
  - ✅ database.html (788 lines) - COMPLETE
  - ✅ testing.html (1,097 lines) - COMPLETE
  - ✅ engineering.html (1,191 lines) - COMPLETE
  - ✅ **ddd.html (1,128 lines) - COMPLETE**
  - ⏳ devops.html (next priority)
  - ⏳ cloud.html
  - ⏳ containers.html
  - ⏳ 11 remaining stub pages (frontend, ui-ux, mobile, messaging, performance, security, rag-domains, etc.)
- Phase 4.5: 🔍 **Quality Review & Styling Standards Compliance** - NOT STARTED (3h) 🆕
- Phase 5: 🆕 Knowledge File Pages (80+ pages, Level 4) - NOT STARTED (8h)
- Phase 6: 🎓 Educational Resources Integration - NOT STARTED (4h)
- Phase 7: 🎨 Styling & Responsiveness - NOT STARTED (6h)
- Phase 8: 🔍 Search & Filtering - NOT STARTED (3h)
- Phase 9: ✅ Documentation & Validation - NOT STARTED (4h)

**Overall Progress:** ~35% (6 of 17 category pages complete)

**Timeline:** 6-8 days (72 hours total) ← Updated with Phase 4.5

**Next Task:** Continue with devops.html, cloud.html, and containers.html

**Incremental Build Success:**
- ✅ engineering.html: 1,191 lines (6 steps, SOLID/patterns/clean code)
- ✅ ddd.html: 1,128 lines (strategic/tactical DDD, events)
- ✅ No length limit issues with incremental approach
- ✅ Pattern validated for remaining 11 pages

---

## 📱 Mobile-First Design Checklist

**Touch Optimization:**
- [ ] All buttons/links ≥48x48px
- [ ] Swipe gestures for navigation
- [ ] Bottom nav in thumb zone (mobile)
- [ ] Sticky header stays visible
- [ ] No hover-only interactions

**Responsive Components:**
- [ ] Domain cards stack on mobile
- [ ] Category chips wrap properly
- [ ] Accordions expand/collapse smoothly
- [ ] Tabs scroll horizontally (overflow-x: auto)
- [ ] Breadcrumb text truncates (ellipsis)
- [ ] Mermaid diagrams scroll horizontally

**Performance:**
- [ ] Lazy load images/diagrams
- [ ] Skeleton screens while loading
- [ ] Minimize JavaScript (vanilla JS preferred)
- [ ] Defer non-critical CSS
- [ ] Optimize font loading

---

## 🗺️ Navigation Flow Diagram

```
Level 1: Home (docs/index.html)
    └─ 📚 Knowledge Library tile
        ↓
Level 2: Domain Overview (docs/knowledge/index.html)
    ├─ 🎨 Frontend & UI
    │   ├─ 💻 Frontend (8 files)
    │   ├─ 🎨 UI/UX (2 files)
    │   └─ 📱 Mobile (4 files)
    ├─ 🔌 Backend & APIs
    │   ├─ 🔌 API (6 files)
    │   ├─ 🏗️ Microservices (7 files)
    │   └─ 📨 Messaging (4 files)
    ├─ 🗄️ Data & Storage
    │   ├─ 🗄️ Databases (8 files)
    │   └─ ⚡ Performance (3 files)
    ├─ ☁️ Infrastructure
    │   ├─ ☁️ Cloud (6 files)
    │   ├─ 🐳 Containers (5 files)
    │   └─ ⚙️ DevOps (5 files)
    └─ 🏗️ Software Craft
        ├─ 🏗️ Engineering (8 files)
        ├─ 📐 DDD (6 files)
        ├─ 🔒 Security (4 files)
        ├─ 🧪 Testing (5 files)
        └─ 🧠 AI Domains (4 files)
        ↓
Level 3: Category Detail (e.g., docs/knowledge/frontend.html)
    ├─ Tab 1: Overview (Mermaid diagram)
    ├─ Tab 2: Knowledge Files (Accordion with 8 files)
    ├─ Tab 3: Learning Resources
    └─ Tab 4: CORTEX Usage
        ↓
Level 4: Knowledge File Detail (e.g., docs/knowledge/frontend/react.html)
    ├─ Overview
    ├─ Rules (35 with code examples)
    └─ Related Knowledge (cross-references)
```

---

**Plan Status:** ✅ READY FOR EXECUTION

**Copyright © 2025 Asif Hussain. All rights reserved.**
