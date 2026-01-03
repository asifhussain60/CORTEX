# 🎨 Glassmorphism Design Standard

**Version:** 4.2.6 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Last Updated:** January 3, 2026 (Icon-Title Spacing Toolkit Validation)  
**Copyright © 2026 Asif Hussain. All rights reserved.**

**🛠️ TOOLKIT VALIDATION:** Use `validate-icon-title-spacing.ps1` to enforce compliance

---

## 🔒 CSS BACKUP & RECOVERY

**⚠️ CRITICAL: Before modifying any CSS, read this section!**

**Backup Location:** `backups/css-backup-20260103_093835/`

**What's Backed Up:**
- All 14 CSS files from `docs/assets/css/`
- Complete pre-cleanup state (2,043 classes, 865 unused identified)
- Includes: main.css, generated-classes.css, intentional-classes.css, learning-hub.css, etc.

**When to Restore from Backup:**

| Issue | Symptom | Recovery Action |
|-------|---------|----------------|
| **Missing Styles** | Elements lose styling after cleanup | Copy specific class from backup CSS file |
| **Broken Layout** | Page layout breaks after CSS changes | Restore entire CSS file from backup |
| **Lost Custom Styles** | Unique styles accidentally removed | Extract class from backup, add to intentional-classes.css |
| **Regression After Update** | New CSS breaks existing pages | Diff backup vs current, restore safe classes |

**Recovery Commands:**

```powershell
# Restore specific CSS file
Copy-Item "backups\css-backup-20260103_093835\main.css" "docs\assets\css\main.css" -Force

# Restore all CSS files
Copy-Item "backups\css-backup-20260103_093835\*.css" "docs\assets\css\" -Force

# Extract specific class from backup
Select-String -Path "backups\css-backup-20260103_093835\*.css" -Pattern "\.your-class-name\s*\{" -Context 0,10
```

**Best Practices:**
1. **Always backup before cleanup:** Create timestamped backup in `backups/`
2. **Test incrementally:** Remove small batches of unused CSS, validate after each
3. **Check dynamic usage:** Some classes used by JavaScript may appear "unused"
4. **Preserve state classes:** Keep classes like `.active`, `.hidden`, `.loading`, etc.
5. **Document custom classes:** Add comments explaining purpose of rarely-used classes

**Current CSS State (Post-Cleanup):**
- **Inline Styles:** 0 (100% eliminated)
- **Generated Classes:** 335 auto-generated from inline styles
- **Intentional Classes:** 209 glassmorphism-compliant patterns
- **Unused Classes:** 865 identified (42.34%) - backup preserved
- **Missing Classes:** 143 need definitions

---

## 📋 Purpose

This standard defines **modern glassmorphism patterns** for CORTEX documentation and UI components, incorporating **cutting-edge 2025 design techniques** including multi-layer depth, dynamic lighting, micro-interactions, performance optimization, and **CSS quality enforcement**.

**Target:** HTML documentation, dashboards, STS showcases, interactive visualizations  
**Compatibility:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+  
**Reference Implementation:** See `/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex-documentation/artifacts/Level1-spec.md` for detailed page specifications.

**✨ NEW in v4.2.0: CSS Quality Rules**
- **Zero Duplicates:** Enforce no exact/partial duplicate CSS rules (<2% redundancy)
- **100% Usage:** All CSS classes must be used in HTML (unused classes = dead code)
- **Zero Missing:** All HTML class attributes must have CSS definitions
- **Mobile-First:** A+ grade (95%+) mobile-friendliness mandatory
- **Toolkit Enforcement:** Automated validation via `validate-css-*.ps1` scripts

**⚠️ Animation Philosophy (v4.0.0):**
- **Subtle & Modern:** All animations designed to be non-distracting
- **Level 1 Detail Pages:** ONLY T1 subtle animations (0.2-0.3s transitions, no dramatic effects)
- **Clickable Elements:** Glowing border + lift + pointer cursor on hover
- **Display Elements:** Slow glass reflection (8s) + default cursor, NO glow
- **Consistent Styling:** Clear visual differentiation between interactive and display elements
- **⛔ NO Dramatic Animations:** borderGlowSweep, blobMorph, and other T3 effects ONLY on Level 0 (Home page)

**Scope:** Applies to ALL 9 CORTEX home page tiles and their hierarchies:
1. 🧠 Architecture → SKULL, Knowledge Graph, Brain Tiers, Context, Orchestrator Ecosystem
2. 🛡️ Security → 13 pages across 4 categories (Protection, Assessment, Compliance, Response)
3. 🎯 Orchestrators → 22 pages across 5 categories (Planning, Execution, System, Analysis, Debug) + Master Orchestrator Hub
4. 💰 Token Optimization → Analysis, Strategies, Savings, Cross-Session Context
5. 🔧 Sharpen The Saw → 6 best practice pages (Security, SOLID, Code Quality, Performance, Testing, Docs)
6. 📚 CORTEX Best Practices → 17 Learning Hubs with 80 Level 2 modules (22 implemented, 58 stubs)
7. 🛠️ Toolkit Manager → Master Orchestrator Routing Layer, Pattern Matching, LLM Fallback
8. 🔍 CORTEX LENS → AST, Reverse Engineering, Intelligence
9. 🚀 Get Started → Installation, Configuration, First Steps

**v5.0 Architecture (NEW):**
- 🎛️ **Master Orchestrator Hub** → Pattern Router, State Manager, Execution Engine, Lifecycle Hooks, LLM Fallback
- 📋 **Planning v5 (Level 2)** → 10 phase pages with comprehensive visualizations (Score: 195)
- 🎯 **ADO v2 (Level 2)** → 13 feature pages with work item generation flows (Score: 178)

---

## 🚀 Quick Reference

### Content-Driven Layout Decision Matrix

**⚠️ CRITICAL:** Choose layout based on content volume, not arbitrary preferences.

| Content Metric | Layout Choice | Rationale |
|----------------|---------------|-----------|
| **3-5 items, <50 chars each** | 3-column grid | Short labels, horizontal space efficient |
| **3-5 items, 50-150 chars each** | 2-column grid | Medium content needs breathing room |
| **4+ items, >150 chars each** | 2-column grid | Long descriptions require vertical space |
| **Single-line labels** | Horizontal flex | Quick scan, icon+title inline |
| **Multi-line descriptions** | Vertical stack | Left-aligned text, icon+title centered |

### Visual Pattern Decision Matrix

| Question | Answer → Pattern |
|----------|------------------|
| Does tile have 4+ categories? | YES → **Multi-Panel** / NO → **Standard Tile** |
| How many categories? | 4 → **2x2 grid** / 5 → **2x3 grid** / 6 → **3x2 grid** |
| Are subpanel links single or multiple? | Single → `.single-tag` compact / Multiple → default height |
| Is element clickable? | YES → `.glass-card-clickable` + `.animation-t1` / NO → `.glass-card-display` |
| What page level? | Level 0 → T3 animations OK / Level 1 → T1 only / NO Level 2 |
| List vs Cards? | **Always prefer cards** over bullet lists for visual prominence |
| Icon placement? | **Centered with title** for short content / **Inline left** for long content |
| Description length? | <100 chars → center / **>100 chars → left-align** |

### Critical CSS Classes

| Class | Purpose | When to Use |
|-------|---------|-------------|
| `.glass-card-clickable` | Interactive tiles/cards | Navigational elements, buttons |
| `.glass-card-display` | Static content cards | Information display, non-interactive panels |
| `.animation-t1` | Subtle hover effects | ALL Level 1 pages (required) |
| `.principle-card-grid` | 2-3 column card grid | Principle/feature showcases (strict grid) |
| `.principle-card-grid.columns-2` | 2-column strict grid | 4-tier brain, 2-agent system (2x2 or 1x2 layout) |
| `.principle-card-grid.columns-3` | 3-column strict grid | 5+ principles, short-label content |
| `.capability-tiles` | Vertical card stack | Detailed capabilities with long descriptions |
| `.capability-tile` | Individual capability card | Left border accent, icon+text |
| `.tier-header` | Inline icon+title | Horizontal flex layout |
| `.two-column-grid` | 2-column responsive grid (auto-fit) | DEPRECATED: Use `.principle-card-grid.columns-2` for strict 2-panel |
| `.orchestrator-tags` | Horizontal pill layout | Tags, labels, categories |

### Spacing Quick Reference

| Element Type | Property | Value | Use Case |
|--------------|----------|-------|----------|
| **Icon-Title Pairs** | `gap` | `var(--spacing-sm)` (8px) | Tight coupling: section-title, page-title, tier-header, capability-tile |
| Stacked cards | `margin-bottom` | `var(--space-lg)` (24px) | Between consecutive cards |
| Multi-panel grids | `gap` | `var(--space-lg)` (24px) | All panel gaps |
| Major sections | `margin-bottom` | `var(--space-2xl)` (48px) | Between sections |
| Key features | `margin-bottom` | `var(--space-3xl)` (64px) | After feature sections |
| Mobile (< 768px) | `gap` | `var(--space-md)` (16px) | Tighter mobile spacing |

**⚠️ CRITICAL: Icon-Title Spacing Rule (v4.2.6)**
All icon+title combinations MUST use `gap: var(--spacing-sm)` (8px) for tight visual coupling. This applies to:
- `.section-title` - Main section headers with icons
- `.page-title` - Page title headers with icons  
- `.tier-header` - Tier card headers with icons
- `.capability-tile` - Capability items with icons
- `.principles-header` - Principle section headers with icons

**Before (WRONG):** `gap: var(--spacing-md)` (16px) - Too much space  
**After (CORRECT):** `gap: var(--spacing-sm)` (8px) - Tight coupling

**HTML Pattern Requirements:**
- Icons and titles MUST be inline within the same container (no separate lines)
- ❌ **WRONG:** `<h2>\n  <i class="fas fa-icon"></i>\n  Title\n</h2>`
- ✅ **CORRECT:** `<h2><i class="fas fa-icon"></i> Title</h2>`

**Automated Validation:**
```powershell
# Detect issues only
.\cortex-toolkit\validate-icon-title-spacing.ps1 -DetectOnly

# Auto-fix all issues
.\cortex-toolkit\validate-icon-title-spacing.ps1 -AutoFix
```

**Toolkit Tool:** `validate-icon-title-spacing.ps1` (v1.0.0)
- Scans 317 HTML files + 14 CSS files
- Detects icons on separate lines from titles
- Validates CSS gap values (must be `var(--spacing-sm)`)
- Auto-fixes issues with backup creation
- Generates JSON validation report

### Animation Decision Tree

```
Is it Level 0 (Home)?
├── YES → T3 animations allowed (dramatic effects)
└── NO → Is it clickable?
    ├── YES → T1 subtle (glow + lift + pointer)
    └── NO → Static or slow reflection only
```

---

## 🏗️ View Hierarchy (SIMPLIFIED: 2-Level Max)

**Architecture:** `Level 0 (Home) → Level 1 Detail Pages`

**⛔ NO Level 2 PAGES:** Discovery analysis confirms all content fits within Level 1. Use expandable sections, tabs, or modals for deeper content within pages.

**Level 0 Tile Patterns:**

| Tile | Pattern | Grid Layout | Pages | Rationale |
|------|---------|-------------|-------|-----------|
| **Security** | Multi-Panel | 2x2 (4 subpanels) | 13 | 4 categories require visual separation |
| **Orchestrators** | Multi-Panel | 2x3 (5 subpanels) | 19 | 5 categories, most complex tile |
| **Sharpen The Saw** | Multi-Panel | 3x2 (6 subpanels) | 6 | 6 single-link categories, compact layout |
| **All Others** | Standard Tile | N/A | 3-35 | Simple structure, direct navigation |

### Multi-Panel Pattern (3 Tiles Only)

**When to Use:** Security, Orchestrators, Sharpen The Saw (tiles with 4+ categories)

**Grid Layout Rules:**
- **4 subpanels:** 2x2 grid (Security: Protection, Assessment, Compliance, Response)
- **5 subpanels:** 2x3 grid (Orchestrators: Planning, Execution, System, Analysis, Debug)
- **6 subpanels:** 3x2 grid (STS: Security, SOLID, Code Quality, Performance, Testing, Docs)

**Implementation:**
```html
<!-- Multi-panel wrapper (non-clickable) -->
<article class="glass-card-display main-panel-wrapper">
    <div class="category-panels-grid grid-3x2">
        <div class="category-subpanel single-tag">
            <div class="category-icon">🛡️</div>
            <h3>Security</h3>
            <p class="category-description">Best practices for secure code</p>
            <a href="sts/security.html" class="category-tag">View Security Guide</a>
        </div>
        <!-- Repeat for all 6 subpanels -->
    </div>
</article>
```

**CSS Classes:**
- `.main-panel-wrapper` - Outer wrapper (non-clickable display card)
- `.category-panels-grid` - Grid container (default 2x2)
- `.grid-3x2` - Modifier for 3x2 layout (6 subpanels)
- `.grid-2x3` - Modifier for 2x3 layout (5 subpanels)
- `.category-subpanel` - Individual category panel
- `.single-tag` - Compact styling for single-link panels
- `.category-tag` - Clickable link within subpanel

### Standard Tile Pattern (6 Tiles)

**When to Use:** Architecture, Token Optimization, Best Practices, Toolkit Manager, CORTEX Lens, Get Started

**Implementation:**
```html
<!-- Standard clickable tile -->
<article class="glass-card-clickable animation-t1">
    <div class="card-icon">🧠</div>
    <h3>Architecture</h3>
    <p>CORTEX brain structure and cognitive framework</p>
</article>
```

### Architecture Page Pattern (2-Panel Grid Structure)

**When to Use:** Architecture page (`/architecture/index.html`) showing 4-tier brain system

**Grid Layout Examples:**

| Section | Content Count | Grid Class | Layout |
|---------|---------------|------------|--------|
| Key Architectural Principles | 5 principles | `.principle-card-grid.columns-3` | 3-column for balanced layout |
| Tier Deep Dive | 4 tiers (Tier 0-3) | `.principle-card-grid.columns-2` | **2x2 strict grid** (2-panel) |
| Agent System | 2 agents | `.principle-card-grid.columns-2` | **1x2 strict grid** (side-by-side) |

**Implementation:**
```html
<!-- Tier Deep Dive (2x2 Panel Grid) -->
<section class="glass-card-display animation-t1">
    <h2 class="section-title">
        <i class="fas fa-layer-group pulse-glow-glass--fast"></i>
        Tier Deep Dive
    </h2>
    
    <div class="principle-card-grid columns-2">
        <!-- Tier 0: SKULL Governance -->
        <div class="glass-card-clickable animation-t1">
            <div class="tier-header">
                <div class="card-icon tier-icon">
                    <i class="fas fa-shield-alt pulse-glow-glass--fast"></i>
                </div>
                <div>
                    <h3 class="card-title">Tier 0: SKULL Governance</h3>
                    <p class="card-subtitle">Brain Protection & Safety Validation</p>
                </div>
            </div>
            
            <div class="capability-tiles">
                <!-- Capability items -->
            </div>
        </div>
        
        <!-- Repeat for Tier 1, 2, 3 -->
    </div>
</section>
```

**Critical Differences:**

| Class | Grid Behavior | Use Case |
|-------|---------------|----------|
| `.two-column-grid` | `auto-fit` responsive (fluid) | DEPRECATED: Use only for legacy pages |
| `.principle-card-grid.columns-2` | **Strict 2-column** (fixed) | Architecture tiers, agent system (2-panel structure) |

**Why Strict 2-Panel?**
- Enforces visual symmetry for brain tier hierarchy (Tier 0/1 | Tier 2/3)
- Prevents layout shifting on different screen sizes
- Aligns with glassmorphism multi-panel pattern philosophy

---

## 🎯 Core Principles

1. **Multi-Layer Depth** - Stacked glass layers with varying opacity
2. **Dynamic Lighting** - Simulated light sources for realism
3. **Smooth Interactions** - Micro-animations with cubic-bezier easing
4. **GPU Acceleration** - Hardware-accelerated transforms
5. **Performance First** - Conditional blur, lazy loading
6. **Accessibility** - WCAG 2.1 AA compliance, reduced-motion support
7. **Subtle by Default** - T1 animations for ALL Level 1 detail pages (v4.0.0)
8. **Simplified Hierarchy** - Level 0 → Level 1 only, no Level 2 pages (v4.0.2)
9. **NO Inline Styles** - All styling via CSS classes (zero tolerance for `style=""` attributes)
10. **Responsive Mandatory** - Mobile-first design (375px base, 768px tablet, 1440px desktop)
11. **Proper Spacing** - Minimum 1.5rem (24px) vertical gap between stacked cards/panels (v4.0.1)
12. **Cross-Document Consistency** - Align with Level1-spec.md for implementation details (v4.0.2)
13. **Content-Driven Pattern Selection** - Choose bullets vs cards intelligently based on content characteristics (v4.2.3)
14. **Content-Driven Layouts** - Choose grid columns (2 vs 3) based on description length, not preference (v4.1.3)
15. **Smart Icon Placement** - Centered for short content (<100 chars), inline-left for long content (v4.1.3)
16. **Left-Align Long Text** - Descriptions >100 characters must be left-justified for readability (v4.1.3)
17. **Zero CSS Duplicates** - Exact/partial duplicate CSS rules forbidden (<2% redundancy tolerance) (v4.2.0)
18. **100% CSS Usage** - Unused CSS classes = dead code, must be removed (v4.2.0)
19. **Zero Missing CSS** - All HTML class attributes must have CSS definitions (v4.2.0)
20. **Mobile-First Compliance** - A+ grade (95%+) mobile-friendliness score mandatory (v4.2.0)
21. **Font Awesome 6.x Compliance** - All icons require style prefix (`fas`, `far`, `fab`, `fal`, `fad`) + icon name (v4.2.2)

---

## 🎯 Principle 21: Font Awesome Icon Implementation (v4.2.2)

**Purpose:** Ensure all Font Awesome icons render correctly with proper class prefix format required by Font Awesome 6.x.

### Icon Format Requirements

**Font Awesome 6.x Syntax:**
```html
<!-- ✅ CORRECT: Style prefix + icon name + optional classes -->
<i class="fas fa-code-branch pulse-glow-glass--fast"></i>
<i class="far fa-heart animation-t1"></i>
<i class="fab fa-github"></i>

<!-- ❌ WRONG: Missing style prefix -->
<i class="fa-code-branch pulse-glow-glass--fast"></i>
<i class="fa-heart animation-t1"></i>
<i class="fa-github"></i>
```

### Style Prefix Reference

| Prefix | Style | Usage | Example |
|--------|-------|-------|---------|
| `fas` | Solid | Default icons (90% of use cases) | `fas fa-shield-alt` |
| `far` | Regular | Outlined icons | `far fa-heart` |
| `fab` | Brands | Company/product logos | `fab fa-github` |
| `fal` | Light | Thin/light weight icons | `fal fa-star` |
| `fad` | Duotone | Two-tone icons | `fad fa-code` |

### Implementation Guidelines

**1. Always Use Style Prefix:**
```html
<!-- Navigation icons -->
<i class="fas fa-home"></i>
<i class="fas fa-cog"></i>
<i class="fas fa-search"></i>

<!-- Card icons -->
<div class="card-icon ast-icon">
    <i class="fas fa-code-branch pulse-glow-glass--fast"></i>
</div>

<!-- Stat icons -->
<span class="stat-item">
    <i class="fas fa-language pulse-glow-glass--fast"></i> Multi-Language
</span>
```

**2. Combine with Animation Classes:**
```html
<!-- T1 Animation + Icon -->
<i class="fas fa-brain animation-t1"></i>

<!-- Pulse Glow + Icon -->
<i class="fas fa-microscope pulse-glow-glass--fast"></i>

<!-- Multiple utility classes -->
<i class="fas fa-shield-alt pulse-glow-glass--fast animation-t1"></i>
```

**3. Section Icons:**
```html
<!-- Section headers -->
<h2 class="section-title">
    <i class="fas fa-brain"></i>
    Intelligence Extraction Flow
</h2>

<!-- Tier headers -->
<div class="tier-header">
    <i class="fas fa-sitemap"></i>
    <h4>Tier 0: Governance</h4>
</div>
```

### Validation Methods

**Method 1: PowerShell Search (Should Return 0 Matches):**
```powershell
# Search for icons missing fas/far/fab/fal/fad prefix
Select-String -Path "docs/**/*.html" -Pattern 'class="[^"]*\bfa-[a-z-]+' | 
    Where-Object { $_.Line -notmatch '\bfas\b|\bfar\b|\bfab\b|\bfal\b|\bfad\b' }
```

**Method 2: Grep Search (Should Return 0 Matches):**
```bash
# Search for broken icon patterns
grep -r 'class="[^"]*\bfa-[a-z-]' docs/**/*.html | grep -v '\bfas\b\|\bfar\b\|\bfab\b\|\bfal\b\|\bfad\b'
```

**Method 3: Visual Verification:**
- Open any page in browser
- Check DevTools Console for Font Awesome warnings
- Verify icons render correctly (not showing empty boxes)

### Common Patterns

**Glassmorphism Cards:**
```html
<div class="glass-card-clickable animation-t1">
    <div class="card-icon security-icon">
        <i class="fas fa-shield-alt"></i>
    </div>
    <h4 class="card-title">Security Scanning</h4>
    <p class="card-description">Detect security vulnerabilities</p>
    <div class="card-stats">
        <span class="stat-item"><i class="fas fa-lock"></i> 12 Checks</span>
        <span class="stat-item"><i class="fas fa-exclamation-triangle"></i> CVE Database</span>
    </div>
</div>
```

**Multi-Panel Subpanels:**
```html
<div class="category-subpanel">
    <h3 class="subpanel-title">
        <i class="fas fa-shield-alt"></i> Protection
    </h3>
    <div class="category-links">
        <a href="security/skull-protection.html" class="category-tag">
            <i class="fas fa-skull-crossbones"></i> SKULL Protection
        </a>
    </div>
</div>
```

**Navigation Breadcrumbs:**
```html
<nav class="glass-breadcrumb">
    <a href="../index.html">
        <i class="fas fa-home"></i> Home
    </a>
    <span class="breadcrumb-separator"><i class="fas fa-chevron-right"></i></span>
    <a href="index.html">
        <i class="fas fa-brain"></i> Architecture
    </a>
</nav>
```

### CDN Reference

**Required in `<head>`:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

**Version Compatibility:**
- Font Awesome 6.x: Requires style prefix (mandatory)
- Font Awesome 5.x: Style prefix optional but recommended
- Font Awesome 4.x: Uses different `fa fa-` prefix (legacy)

### Fix Script

**Automated Icon Fix:** `scripts/fix-fontawesome-icons.ps1`

Corrects all instances of missing `fas` prefix across documentation:
- Scans all HTML files in `docs/`
- Adds `fas` prefix to `fa-xxxxx` patterns
- Creates `.bak` backup files
- Handles edge cases (duplicate prefixes, multiple classes)

**Usage:**
```powershell
.\scripts\fix-fontawesome-icons.ps1
```

---

## 🎯 Principle 13: Content-Driven Pattern Selection (v4.2.3)

**Purpose:** Intelligently choose between bullet lists and card layouts based on content characteristics, semantic context, and user experience goals.

### Decision Matrix: Bullets vs Cards

#### ✅ USE BULLETS when:

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Short Items** | Each item <50 characters | "Accelerate delivery velocity" |
| **List Semantics** | Natural sequential/unordered list | Benefits, features, steps |
| **Contained Context** | List inside styled parent (card/tile) | `<ul class="persona-benefits">` |
| **Item Count** | 3-6 concise items | Quick reference lists |
| **Scannable Content** | User needs fast visual scanning | Navigation, quick benefits |
| **Semantic HTML** | Accessibility requires `<ul>/<ol>` | Screen reader optimization |

#### ✅ USE CARDS when:

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Long Descriptions** | Each item >100 characters | Detailed feature explanations |
| **Visual Prominence** | Content needs individual emphasis | Product showcases |
| **Action Items** | Each card triggers interaction | Click-to-learn-more scenarios |
| **Rich Content** | Items contain icons, images, links | Integration tiles, tool cards |
| **Grid Layout** | Content benefits from 2D arrangement | Feature comparison, portfolio |
| **Individual Identity** | Each item is self-contained entity | Team members, case studies |

### Class-Based Preservation Rules

**NEVER convert to cards if parent has:**
- `.persona-benefits` - Persona tile benefit lists
- `.feature-list` - Quick feature references  
- `.navigation-list` - Menu/nav items
- `.step-list` - Sequential instructions
- `.benefits-container` - Contained benefit lists

**ALWAYS convert to cards if parent has:**
- `.feature-showcase` - Detailed feature displays
- `.integration-grid` - Integration/tool tiles
- `.capability-highlights` - Prominent capabilities
- `.team-members` - People cards
- `.case-studies` - Case study showcases

### Content Analysis Algorithm

```yaml
bullet_to_card_decision:
  analyze:
    - item_count: 3-6 items → bullets | 7+ items → evaluate further
    - avg_char_length: <50 chars → bullets | >100 chars → cards
    - parent_class: check preservation/conversion lists
    - semantic_context: <ul>/<ol> in styled container → bullets
    - visual_prominence: standalone emphasis needed → cards
    - accessibility: list semantics valuable → bullets
  
  decision_tree:
    if parent_class in preservation_list:
      return "keep_bullets"
    elif parent_class in conversion_list:
      return "convert_to_cards"
    elif avg_char_length < 50 and item_count <= 6:
      return "keep_bullets"
    elif avg_char_length > 100:
      return "convert_to_cards"
    else:
      return "evaluate_semantic_context"
```

### Examples: Correct Pattern Usage

#### Example 1: Persona Tiles (BULLETS ✅)
```html
<div class="persona-tile persona-tile-leadership">
    <div class="persona-icon">👔</div>
    <h3 class="persona-title">Business Leadership</h3>
    <p class="persona-tagline">Ship Faster, Ship Better</p>
    <ul class="persona-benefits">
        <li>Accelerate delivery velocity with autonomous workflows</li>
        <li>Reduce technical debt through enforced standards</li>
        <li>Gain visibility into code quality metrics</li>
        <li>Predictable outcomes from AI-assisted development</li>
    </ul>
</div>
```
**Why bullets?** Short items (37-53 chars), list semantics, contained in styled parent, 4 items, scannable benefits.

#### Example 2: Feature Showcase (CARDS ✅)
```html
<div class="feature-showcase">
    <div class="glass-card">
        <div class="card-icon">🧠</div>
        <h3 class="card-title">Long-Term Memory</h3>
        <p class="card-description">
            CORTEX maintains context across sessions using a 4-tier brain architecture. 
            Tier 0 stores governance rules, Tier 1 tracks working memory, Tier 2 builds 
            knowledge graphs, and Tier 3 preserves development context. This enables 
            truly stateful AI assistance that remembers your codebase, preferences, 
            and project history over weeks and months.
        </p>
        <a href="#" class="card-cta">Learn More →</a>
    </div>
</div>
```
**Why cards?** Long description (>250 chars), visual prominence needed, includes CTA, self-contained entity.

#### Example 3: Quick Reference List (BULLETS ✅)
```html
<div class="glass-panel">
    <h3>Quick Setup</h3>
    <ul class="step-list">
        <li>Install Python 3.11+</li>
        <li>Run <code>pip install -r requirements.txt</code></li>
        <li>Configure <code>cortex.config.json</code></li>
        <li>Launch with <code>python -m cortex</code></li>
    </ul>
</div>
```
**Why bullets?** Sequential steps, short commands, semantic list, 4 items, contained in panel.

---

## 🎨 CSS Quality Rules (v4.2.0 - MANDATORY)

**Problem:** CSS bloat, duplicates, unused classes, missing definitions, and poor mobile responsiveness degrade performance and maintainability.  
**Solution:** Automated validation via toolkit scripts enforcing quality thresholds.

### Rule 1: Zero CSS Duplicates

**Threshold:** <2% redundancy (exact + partial + scattered duplicates)

**Categories:**
- **Exact Duplicates:** Same selector, same properties (DELETE immediately)
- **Partial Duplicates:** Same selector, overlapping properties (MERGE)
- **Scattered Patterns:** Same property:value repeated (EXTRACT to utility class)

**Validation:**
```powershell
.\cortex-toolkit\validate-css-duplicates.ps1 -Detailed -ThresholdPercentage 2
```

**Action:**
- **CRITICAL:** Delete exact duplicates within 24 hours
- **HIGH:** Merge partial duplicates within 1 week
- **MEDIUM:** Extract scattered patterns within 2 weeks

**Example Violation:**
```css
/* main.css:8695 */
.principle-card {
    background: rgba(0, 0, 0, 0.3);
    padding: var(--spacing-lg);
}

/* main.css:8772 - DUPLICATE */
.principle-card {
    background: rgba(0, 0, 0, 0.3);
    padding: var(--spacing-lg);
}
```

**Fix:** Delete second instance (lines saved: 5)

---

### Rule 2: 100% CSS Usage

**Threshold:** <5% unused CSS classes

**Definition:** CSS class defined in `.css` files but NEVER used in `.html` files = dead code

**Validation:**
```powershell
.\cortex-toolkit\validate-css-usage.ps1 -IncludeOrphans -StrictMode
```

**Action:**
- **CRITICAL:** Delete unused classes with >6 months no usage
- **HIGH:** Archive unused classes with <6 months no usage
- **MEDIUM:** Document intentionally unused utility classes

**Example Violation:**
```css
/* main.css:5420 */
.legacy-nav-item {  /* NEVER USED IN HTML */
    color: white;
}
```

**Fix:** Delete class (lines saved: 8)

---

### Rule 3: Zero Missing CSS

**Threshold:** 0 missing CSS classes (100% HTML-CSS alignment)

**Definition:** HTML `class="..."` attribute referencing CSS class that doesn't exist = broken styling

**Validation:**
```powershell
.\cortex-toolkit\validate-css-usage.ps1 -DetectCompound -StrictMode
```

**Action:**
- **CRITICAL:** Fix within 24 hours (broken styling blocks users)
- **Compound Selectors:** Verify `.parent.child` patterns exist

**Example Violation:**
```html
<!-- architecture/index.html:58 -->
<div class="principle-card-grid columns-2">  <!-- columns-2 NOT DEFINED -->
```

**Fix:** Add `.principle-card-grid.columns-2 { grid-template-columns: repeat(2, 1fr); }`

---

### Rule 4: Mobile-First Compliance

**Threshold:** A+ grade (95%+ mobile-friendliness score)

**Components (weighted):**
- **Viewport Meta Tag:** 30% weight (100% required)
- **Responsive CSS:** 30% weight (media queries @ 375px, 768px, 1440px)
- **Touch Targets:** 20% weight (44px × 44px minimum)
- **Grid Systems:** 20% weight (mobile breakpoints required)

**Validation:**
```powershell
.\cortex-toolkit\validate-responsive-design.ps1 -IncludeTouchTargets -StrictMode -StandardBreakpoints
```

**Action:**
- **CRITICAL:** Add viewport meta tag to ALL HTML files
- **HIGH:** Add mobile breakpoints to ALL grid systems
- **MEDIUM:** Increase touch target sizes to 44px minimum
- **LOW:** Standardize breakpoints (remove 900px, 1200px non-standard)

**Example Violation:**
```html
<!-- Missing viewport meta tag -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <!-- ❌ NO VIEWPORT TAG -->
</head>
```

**Fix:** Add `<meta name="viewport" content="width=device-width, initial-scale=1.0">`

---

### Enforcement Pipeline

**Pre-Commit Validation:**
1. Run `validate-css-duplicates.ps1` → PASS <2% redundancy
2. Run `validate-css-usage.ps1` → PASS 0 missing classes
3. Run `validate-responsive-design.ps1` → PASS A+ grade (95%+)

**CI/CD Integration:**
```powershell
# Run all CSS quality checks
$duplicate = .\cortex-toolkit\validate-css-duplicates.ps1 -ThresholdPercentage 2
$usage = .\cortex-toolkit\validate-css-usage.ps1 -StrictMode
$responsive = .\cortex-toolkit\validate-responsive-design.ps1 -StrictMode

if ($duplicate.ExitCode -ne 0 -or $usage.ExitCode -ne 0 -or $responsive.ExitCode -ne 0) {
    Write-Error "CSS Quality Validation FAILED"
    exit 1
}
```

**Monthly Audits:**
- Generate comprehensive CSS quality reports
- Track redundancy trends over time
- Identify top CSS bloat contributors
- Set reduction targets (e.g., reduce main.css from 10,505 to <9,000 lines)

---

## 📏 SPACING SYSTEM (v4.0.1 - CRITICAL)

**Problem:** Cards/panels stacking without adequate vertical spacing creates cramped layouts.  
**Solution:** Enforce minimum spacing using CSS variables.

### Spacing Variables

```css
:root {
    --space-xs: 0.25rem;   /* 4px */
    --space-sm: 0.5rem;    /* 8px */
    --space-md: 1rem;      /* 16px */
    --space-lg: 1.5rem;    /* 24px - DEFAULT for stacked cards */
    --space-xl: 2rem;      /* 32px */
    --space-2xl: 3rem;     /* 48px - Section spacing */
    --space-3xl: 4rem;     /* 64px - Major sections */
}
```

### Stacked Element Rules

**REQUIRED:**
- **Cards/Panels:** `margin-bottom: var(--space-lg)` (24px minimum)
- **Category Sections:** `margin-bottom: var(--space-2xl)` (48px)
- **Multi-Panel Grids:** `gap: var(--space-lg)` (24px between all panels)
- **Grid Rows:** `row-gap: var(--space-lg)` (prevents cramped rows)

### Implementation Example

```css
/* Multi-panel grids (Security, Orchestrators, STS) */
.category-panels-grid {
    display: grid;
    gap: var(--space-lg);  /* 24px all around */
    margin-bottom: var(--space-2xl);  /* 48px after grid */
}

/* 3x2 Grid (STS) - MUST have row-gap */
.category-panels-grid.grid-3x2 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, auto);
    row-gap: var(--space-lg);  /* CRITICAL: 24px between rows */
    column-gap: var(--space-lg);
}

/* Stacked cards on detail pages */
.glass-card + .glass-card {
    margin-top: var(--space-lg);  /* 24px between cards */
}
```

**Responsive Spacing:**
```css
@media (max-width: 767px) {
    .category-panels-grid {
        grid-template-columns: 1fr;
        gap: var(--space-md);  /* 16px on mobile */
    }
}
```

---

## 🎨 Header & Footer Standardization

### Required Structure

**⚠️ CRITICAL: Logo only on Level 0 (Home Page)**

#### Level 0 Glass Header (WITH LOGO)
```html
<header class="glass-header">
    <div class="header-content">
        <a href="index.html" class="header-brand">
            <i class="fas fa-brain"></i>
            <h1>CORTEX</h1>
        </a>
        <nav class="header-nav">
            <a href="#features" class="nav-link">Features</a>
            <a href="#documentation" class="nav-link">Documentation</a>
            <a href="https://github.com/asifhussain60/CORTEX" class="nav-link" target="_blank">
                <i class="fab fa-github"></i> GitHub
            </a>
        </nav>
    </div>
</header>
```

#### Level 1 & Level 2 Glass Header (NO LOGO - Home Link Only)
```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav">
            <a href="../index.html" class="nav-link"><i class="fas fa-home"></i> Home</a>
        </nav>
    </div>
</header>
```

#### Glass Footer
```html
<footer class="glass-footer">
    <div class="footer-content">
        <div class="footer-copyright">
            <p>© 2025 Asif Hussain. All rights reserved.</p>
        </div>
        <div class="footer-links">
            <a href="https://github.com/asifhussain60/CORTEX" target="_blank">
                <i class="fab fa-github"></i> GitHub
            </a>
            <a href="https://asifhussain60.github.io/CORTEX/" target="_blank">
                <i class="fas fa-home"></i> Website
            </a>
            <span class="footer-version">CORTEX v4.0</span>
        </div>
    </div>
</footer>
```

### CSS Classes

```css
/* Glass Header */
.glass-header {
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    transition: all 0.3s ease;
}

/* Level 0: Header with logo and navigation (space-between) */
.glass-header .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Level 1 & 2: Header with navigation only (centered) */
.glass-header .header-content:has(.header-nav:only-child) {
    justify-content: center;
}

.header-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
}

.header-brand i {
    font-size: 1.5rem;
    color: var(--accent-primary);
}

.header-brand h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.header-nav {
    display: flex;
    gap: 2rem;
    align-items: center;
}

.nav-link {
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
    cursor: pointer;
}

.nav-link:hover {
    color: var(--accent-primary);
}

.nav-link i {
    margin-right: 0.25rem;
}

/* Mermaid Diagram Container */
.mermaid-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: var(--spacing-xl, 2rem) 0;
    width: 100%;
}

.mermaid {
    max-width: 800px;
    width: 100%;
}

/* Glass Footer */
.glass-footer {
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem;
    margin-top: 4rem;
    transition: all 0.3s ease;
}

.footer-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.footer-copyright p {
    color: var(--text-muted);
    margin: 0;
    font-size: 0.875rem;
}

.footer-links {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}

.footer-links a {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.2s ease;
}

.footer-links a:hover {
    color: var(--accent-primary);
}

.footer-version {
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    background: rgba(0, 212, 255, 0.1);
    border-radius: 12px;
    border: 1px solid rgba(0, 212, 255, 0.2);
}

/* Responsive Breakpoints */
@media (max-width: 768px) {
    .header-content,
    .footer-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .header-nav {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .footer-links {
        flex-direction: column;
        gap: 0.75rem;
    }
}
```

### Mobile-First Responsive Design

**Base:** 375px (mobile)
- Single column layouts
- Stacked navigation
- Touch-friendly 44px minimum tap targets

**Tablet:** 768px breakpoint
- 2-column grids for multi-panels
- Horizontal navigation
- Expanded spacing

**Desktop:** 1440px breakpoint
- 2-column grids with wider gaps
- Full navigation with icons
- Maximum content width: 1400px

**Implementation Rule:**
```css
/* Mobile-first approach */
.component {
    /* Mobile styles (default) */
}

@media (min-width: 768px) {
    .component {
        /* Tablet enhancements */
    }
}

@media (min-width: 1440px) {
    .component {
        /* Desktop enhancements */
    }
}
```
| **T2** | Accent | Interactive elements requiring feedback | 0.1-0.2s | Button press, form focus, selection highlight | UI elements |
| **T3** | Dramatic | ONLY Level 0 (docs/index.html hero) | 2-10s | borderGlowSweep, blobMorph, particle effects | Home only |

### T1: Subtle Animations (DEFAULT)

**✅ REQUIRED for all Level 1, Level 2, and Level 3 pages**

#### Clickable Tiles (Interactive Cards, Buttons, Links)

**Visual Indicators:**
- ✅ Glowing border on hover (subtle accent)
- ✅ `cursor: pointer` (large hand)
- ✅ Slight lift effect (`translateY(-2px)`)
- ❌ NO glass reflections
- ❌ NO infinite animations

```css
/* T1 Clickable Tile - APPROVED */
.glass-card-clickable {
    position: relative;
    cursor: pointer;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.glass-card-clickable:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3); /* Subtle glow */
}

/* Large hand pointer */
.glass-card-clickable:hover {
    cursor: pointer;
}
```

#### Non-Clickable Tiles (Display Cards, Info Panels)

**Visual Indicators:**
- ✅ Static glass highlight (top edge glow)
- ✅ `cursor: default` (no pointer)
- ✅ NO lift effect
- ❌ NO glowing borders
- ❌ NO hover glow
- ❌ NO infinite animations (REMOVED in v4.0.0)

```css
/* T1 Non-Clickable Tile - APPROVED */
.glass-card-display {
    position: relative;
    cursor: default;
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
}

/* T1 Subtle: Static glass highlight (NO animation) */
.glass-card-display::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    pointer-events: none;
}

/* NO hover effects on display cards */
.glass-card-display:hover {
    /* No transform, no glow, no border change */
}
```

#### Subtle Focus States (All Interactive Elements)

```css
/* T1 Focus - APPROVED */
.interactive-element:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
    transition: outline-color 0.2s ease;
}

/* T1 Nav Link - APPROVED */
.nav-link {
    cursor: pointer;
    transition: color 0.2s ease, background-color 0.2s ease;
}
```

**T1 Properties Summary:**
- `transition-duration: 0.2s - 0.3s` (fast, responsive)
- **Clickable:** Glow border + lift + pointer cursor
- **Non-Clickable:** Glass reflection (8s) + default cursor
- NO infinite animations on clickable tiles
- NO keyframe animations on clickable cards
- NO glow on non-clickable tiles

### T2: Accent Animations (Interactive Feedback)

**✅ APPROVED for buttons, forms, tabs**

```css
/* T2 Button Feedback - APPROVED */
.btn-glass:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}

/* T2 Form Focus - APPROVED */
input:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
    transition: all 0.2s ease;
}

/* T2 Tab Selection - APPROVED */
.tab-active {
    border-bottom: 2px solid var(--accent-primary);
    transition: border-color 0.2s ease;
}
```

### T3: Dramatic Animations (RESTRICTED)

**⛔ ONLY ALLOWED ON:**
- `docs/index.html` (Home page hero section)
- Landing page hero sections
- Explicitly marked showcase pages

**❌ FORBIDDEN ON:**
- Level 2 feature pages
- Documentation content pages
- Architecture visualization pages
- Orchestrator detail pages
- Any page with primary content focus

```css
/* T3 Dramatic - HERO SECTIONS ONLY */
@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}

@keyframes blobMorph {
    0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}

@keyframes lightLeakPrimary {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
    100% { transform: translate(-30%, -30%) scale(1.2); opacity: 0.5; }
}

@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
    50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); }
}
```

### Animation Tier Quick Reference

| Animation | Tier | Allowed Pages |
|-----------|------|---------------|
| `transition: transform 0.2s` | T1 | ✅ All pages |
| `transition: opacity 0.2s` | T1 | ✅ All pages |
| `transform: translateY(-2px)` | T1 | ✅ All pages |
| `transform: scale(0.98)` | T2 | ✅ Buttons only |
| `outline` focus states | T2 | ✅ All interactive elements |
| `borderGlowSweep` | T3 | ⛔ Hero only |
| `blobMorph` | T3 | ⛔ Hero only |
| `lightLeakPrimary` | T3 | ⛔ Hero only |
| `glowPulse` | T3 | ⛔ Hero only |
| Infinite animations | T3 | ⛔ Hero only |
| SVG filter glow effects | T3 | ⛔ Hero only |

### Migration from T3 to T1

When simplifying dramatic animations:

```css
/* ❌ BEFORE (T3 Dramatic) */
.glass-card::after {
    animation: borderGlowSweep 2s ease-in-out infinite;
}

.glass-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(0, 212, 255, 0.5);
}

/* ✅ AFTER (T1 Subtle) */
.glass-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
/* Remove ::after with borderGlowSweep entirely */
```

---

## 🏗️ Pattern Library

### Pattern 1: Multi-Layer Glass Card (PRIMARY)

**Use Case:** Default card pattern for all content containers

**⚠️ LEVEL 1 & LEVEL 2 IMPLEMENTATION (T1 Subtle):**
```css
.glass-card {
    position: relative;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: var(--space-lg);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

/* T1 Hover: Simple lift + glow (NO animation) */
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 212, 255, 0.15);
    border-color: rgba(0, 212, 255, 0.3);
}

/* NO animated border glow on Level 1/2 pages */
/* NO ::after pseudo-elements with borderGlowSweep animations */
/* NO infinite keyframe animations */
```

**⚠️ LEVEL 0 ONLY (T3 Dramatic - Hero Sections):**
```css
.glass-card-hero {
    /* Layer 1: Frosted background with gradient */
    position: relative;
    background: linear-gradient(
        135deg,
        rgba(26, 31, 58, 0.7) 0%,
        rgba(26, 31, 58, 0.4) 100%
    );
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: var(--space-lg);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Layer 2: Inner glow (light source) */
.glass-card-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 40%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.15) 0%, transparent 100%);
    border-radius: inherit;
    pointer-events: none;
}

/* Layer 3: Animated border glow (HERO ONLY) */
.glass-card-hero::after {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(45deg, transparent 30%, rgba(0, 212, 255, 0.3) 50%, transparent 70%);
    background-size: 200% 200%;
    border-radius: inherit;
    opacity: 0;
    z-index: -1;
}

.glass-card-hero:hover::after {
    opacity: 1;
    animation: borderGlowSweep 2s ease-in-out infinite;
}

@keyframes borderGlowSweep {
    0%, 100% { background-position: -200% 0; }
    50% { background-position: 200% 0; }
}
```

**HTML Structure:**
```html
<div class="glass-card">
    <h2>Card Title</h2>
    <p>Content goes here...</p>
</div>
```

**Variables Used:**
- `--space-lg`: 1.5rem (24px) - DEFAULT for stacked cards/grids
- `--accent-primary`: #00d4ff (cyan)

---

### Pattern 2: Neuglass Card (Neumorphism + Glass)

**Use Case:** Dashboard widgets, settings panels, interactive controls

**Implementation:**
```css
.neuglass-card {
    background: linear-gradient(
        145deg,
        rgba(26, 31, 58, 0.8) 0%,
        rgba(16, 20, 40, 0.9) 100%
    );
    backdrop-filter: blur(15px) saturate(150%);
    border-radius: 24px;
    padding: var(--space-lg);
    
    /* Soft neumorphic shadows */
    box-shadow: 
        12px 12px 24px rgba(0, 0, 0, 0.6),
        -12px -12px 24px rgba(255, 255, 255, 0.05),
        inset 2px 2px 4px rgba(255, 255, 255, 0.1),
        inset -2px -2px 4px rgba(0, 0, 0, 0.3);
    
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
}

.neuglass-card:hover {
    box-shadow: 
        6px 6px 12px rgba(0, 0, 0, 0.7),
        -6px -6px 12px rgba(255, 255, 255, 0.03),
        inset 4px 4px 8px rgba(0, 0, 0, 0.4),
        inset -2px -2px 4px rgba(255, 255, 255, 0.1);
    transform: translateY(2px);
}
```

---

### Pattern 3: Morphing Glass Card

**Use Case:** Expandable content, detail views, interactive showcases

**Implementation:**
```css
.morph-card {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: var(--space-lg);
    cursor: pointer;
    transition: 
        border-radius 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55),
        transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55),
        box-shadow 0.6s ease;
}

.morph-card:hover {
    border-radius: 50px;
    transform: scale(1.05);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 40px rgba(0, 212, 255, 0.3);
}

.morph-card.expanded {
    position: fixed;
    inset: 20px;
    border-radius: 0;
    transform: scale(1);
    z-index: 9999;
    animation: morphToFullscreen 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes morphToFullscreen {
    0% {
        border-radius: 50px;
        transform: scale(1.05);
    }
    100% {
        border-radius: 0;
        transform: scale(1);
    }
}
```

**JavaScript Toggle:**
```javascript
document.querySelectorAll('.morph-card').forEach(card => {
    card.addEventListener('click', () => {
        card.classList.toggle('expanded');
    });
});
```

---

### Pattern 4: Light Leak Glass

**Use Case:** Hero sections, feature highlights, ambient backgrounds

**Implementation:**
```css
.light-leak-glass {
    position: relative;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(15px);
    overflow: hidden;
    border-radius: 16px;
    padding: var(--space-xl);
}

/* Light source top-left (cyan) */
.light-leak-glass::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 30% 30%,
        rgba(0, 212, 255, 0.3) 0%,
        transparent 50%
    );
    pointer-events: none;
    mix-blend-mode: overlay;
    animation: lightLeakPrimary 8s ease-in-out infinite alternate;
}

@keyframes lightLeakPrimary {
    0% {
        transform: translate(0, 0);
        opacity: 0.5;
    }
    100% {
        transform: translate(10%, 10%);
        opacity: 0.8;
    }
}

/* Light source bottom-right (purple) */
.light-leak-glass::after {
    content: '';
    position: absolute;
    bottom: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 70% 70%,
        rgba(123, 97, 255, 0.2) 0%,
        transparent 50%
    );
    pointer-events: none;
    mix-blend-mode: overlay;
    animation: lightLeakSecondary 8s ease-in-out infinite alternate-reverse;
}

@keyframes lightLeakSecondary {
    0% {
        transform: translate(0, 0);
        opacity: 0.4;
    }
    100% {
        transform: translate(-10%, -10%);
        opacity: 0.7;
    }
}
```

---

### Pattern 5: Liquid Blob Glass

**Use Case:** Decorative elements, hero backgrounds, feature showcases

**Implementation:**
```css
.liquid-blob {
    background: linear-gradient(
        135deg,
        rgba(0, 212, 255, 0.3) 0%,
        rgba(123, 97, 255, 0.3) 100%
    );
    backdrop-filter: blur(40px) saturate(200%);
    border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%;
    padding: 3rem;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.4),
        inset 0 0 40px rgba(255, 255, 255, 0.1);
    animation: blobMorph 10s ease-in-out infinite;
    will-change: border-radius;
}

@keyframes blobMorph {
    0%, 100% {
        border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%;
    }
    25% {
        border-radius: 60% 40% 40% 60% / 40% 60% 40% 60%;
    }
    50% {
        border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%;
    }
    75% {
        border-radius: 40% 60% 40% 60% / 60% 40% 60% 40%;
    }
}

.liquid-blob:hover {
    border-radius: 30% 70% 70% 30% / 70% 30% 70% 30%;
    animation-play-state: paused;
}
```

---

## 🎨 UI Component Patterns

### Modal/Dialog
```css
.glass-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 14, 39, 0.8);
    backdrop-filter: blur(20px) saturate(180%);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease;
}

.glass-modal {
    background: rgba(26, 31, 58, 0.9);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 3rem;
    max-width: 600px;
    width: 90%;
    box-shadow: 
        0 30px 80px rgba(0, 0, 0, 0.6),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    animation: modalSlideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalSlideUp {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}
```

### Toast Notification
```css
.glass-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(26, 31, 58, 0.95);
    backdrop-filter: blur(20px);
    border-left: 4px solid var(--accent-primary);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    animation: toastSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    z-index: 10000;
}

@keyframes toastSlideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Auto-dismiss after 5s */
.glass-toast.dismissing {
    animation: toastSlideOut 0.3s ease forwards;
}

@keyframes toastSlideOut {
    to {
        transform: translateX(400px);
        opacity: 0;
    }
}
```

### Sidebar/Drawer
```css
.glass-drawer {
    position: fixed;
    top: 0;
    right: 0;
    width: 400px;
    height: 100vh;
    background: rgba(26, 31, 58, 0.85);
    backdrop-filter: blur(30px) saturate(200%);
    border-left: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
    transform: translateX(100%);
    transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    z-index: 9998;
    overflow-y: auto;
}

.glass-drawer.open {
    transform: translateX(0);
}
```

### Dropdown/Select
```css
.glass-dropdown {
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    width: 100%;
    background: rgba(26, 31, 58, 0.95);
    backdrop-filter: blur(25px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    max-height: 300px;
    overflow-y: auto;
    animation: dropdownFadeIn 0.2s ease;
    z-index: 1000;
}

@keyframes dropdownFadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.glass-dropdown-item {
    padding: 0.75rem 1rem;
    transition: background 0.2s ease;
    cursor: pointer;
}

.glass-dropdown-item:hover {
    background: rgba(0, 212, 255, 0.15);
}

.glass-dropdown-item:active {
    background: rgba(0, 212, 255, 0.25);
}
```

### Enhanced Tooltip
```css
.glass-tooltip {
    position: absolute;
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(15px);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
    border: 1px solid rgba(0, 212, 255, 0.3);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
    pointer-events: none;
    opacity: 0;
    transform: translateY(-5px);
    transition: all 0.2s ease;
    z-index: 10001;
    white-space: nowrap;
}

.glass-tooltip::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid rgba(0, 212, 255, 0.3);
}

[data-tooltip]:hover .glass-tooltip {
    opacity: 1;
    transform: translateY(0);
}
```

---

## 🎨 Tile-Specific Patterns (v4.0.0)

### Pattern 8: Architecture Component Cards

**Use Cases:** SKULL Protection layers, Knowledge Graph nodes, Brain Tiers, Development Context modules

**⚠️ T1 SUBTLE ANIMATIONS ONLY (Level 1 & Level 2 pages)**

**HTML Structure:**
```html
<div class="glass-card architecture-component">
    <div class="component-header">
        <i class="fas fa-brain"></i>
        <h3>SKULL Protection Layer 1</h3>
        <span class="badge">118 Rules</span>
    </div>
    <div class="component-body">
        <p>Protection layer description...</p>
    </div>
    <div class="component-footer">
        <button class="btn-glass">View Details</button>
    </div>
</div>
```

**CSS (T1 Subtle - NO infinite animations):**
```css
.architecture-component {
    border-left: 4px solid var(--accent-primary);
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(20px);
    cursor: pointer;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

/* T1 Clickable: Simple glow on hover (NO animation) */
.architecture-component:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 
                0 0 40px rgba(0, 212, 255, 0.15);
    border-color: rgba(0, 212, 255, 0.5);
    cursor: pointer;
}

.architecture-component .component-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.architecture-component .badge {
    background: rgba(0, 212, 255, 0.2);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-left: auto;
}
```

**D3.js Integration:**
- **SKULL Protection:** Concentric rings (15 layers)
- **Knowledge Graph:** Force-directed graph (54 nodes)
- **Brain Tiers:** Sankey diagram (Tier 0→1→2→3)
- **Dev Context:** Hierarchical tree

### Pattern 9: Orchestrator Workflow Cards

**Use Cases:** 17 orchestrator detail pages (TDD, Planning, Debug, ADO, Cleanup, Refinement, etc.)

**HTML Structure:**
```html
<div class="glass-card orchestrator-workflow">
    <div class="workflow-phase-indicator">
        <span class="phase active">1</span>
        <span class="phase-connector"></span>
        <span class="phase">2</span>
        <span class="phase-connector"></span>
        <span class="phase">3</span>
    </div>
    <h3>TDD Orchestrator: RED Phase</h3>
    <p>Write failing test first...</p>
    <div class="workflow-actions">
        <button class="btn-glass">Next Phase</button>
    </div>
</div>
```

**CSS:**
```css
.orchestrator-workflow .workflow-phase-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-xl);
}

.orchestrator-workflow .phase {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.2);
    font-weight: 700;
}

.orchestrator-workflow {
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.orchestrator-workflow:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    cursor: pointer;
}

.orchestrator-workflow .phase.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.orchestrator-workflow .phase-connector {
    width: 24px;
    height: 2px;
    background: rgba(255, 255, 255, 0.2);
}
```

**Mermaid Diagrams:** Each orchestrator uses specific diagram type (see Phase 5 in plan)

### Pattern 10: STS Category Grid

**Use Cases:** Sharpen The Saw 6 categories (Code Quality, SOLID, Testing, Performance, Security, Documentation)

**HTML Structure:**
```html
<div class="sts-category-grid">
    <div class="glass-card sts-category">
        <i class="fas fa-code-quality fa-3x"></i>
        <h3>Code Quality</h3>
        <p class="metric-value">92%</p>
        <p class="metric-label">Compliance</p>
        <a href="code-quality.html" class="btn-glass">Explore</a>
    </div>
    <!-- Repeat for 6 categories -->
</div>
```

**CSS:**
```css
.sts-category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-xl);
    margin: var(--spacing-2xl) 0;
}

.sts-category {
    text-align: center;
    padding: var(--spacing-2xl);
    cursor: pointer;
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.sts-category:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    cursor: pointer;
}

.sts-category i {
    color: var(--accent-primary);
    margin-bottom: var(--spacing-lg);
    opacity: 0.8;
}

.sts-category .metric-value {
    font-size: var(--font-3xl);
    font-weight: 800;
    color: var(--accent-primary);
    margin: var(--spacing-md) 0;
}
```

**D3.js Visuals:**
- **Code Quality:** Radar chart (6 dimensions)
- **SOLID:** Force-directed graph (5 principles)
- **Testing:** Bar chart (coverage %)
- **Performance:** Line chart (latency)
- **Security:** Treemap (vulnerabilities)
- **Documentation:** Bar chart (doc coverage)

### Pattern 11: Best Practices Guideline Cards

**Use Cases:** 35 guidelines organized into 3 Level 2 pages

**HTML Structure:**
```html
<div class="glass-card guideline-card">
    <div class="guideline-number">23</div>
    <h4>Always Use Type Hints</h4>
    <p class="guideline-category">Code Quality</p>
    <div class="guideline-content">
        <p>Type hints improve code readability...</p>
        <pre><code class="language-python">
def calculate(x: int, y: int) -> int:
    return x + y
        </code></pre>
    </div>
    <div class="guideline-footer">
        <span class="badge">Recommended</span>
    </div>
</div>
```

**CSS:**
```css
.guideline-card {
    position: relative;
    padding-left: calc(var(--spacing-xl) + 40px);
    cursor: default;
    overflow: hidden;
}

/* Glass reflection (non-clickable display) */
.guideline-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        135deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    animation: glassReflection 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.guideline-card > * {
    position: relative;
    z-index: 1;
}

.guideline-card .guideline-number {
    position: absolute;
    top: var(--spacing-xl);
    left: var(--spacing-xl);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 212, 255, 0.2);
    border: 2px solid var(--accent-primary);
    border-radius: 50%;
    font-weight: 700;
    font-size: 1.125rem;
}

.guideline-card .guideline-category {
    font-size: 0.875rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--spacing-md);
}

.guideline-card pre {
    background: rgba(0, 0, 0, 0.3);
    padding: var(--spacing-md);
    border-radius: 8px;
    overflow-x: auto;
    margin: var(--spacing-md) 0;
}
```

**Visual Organization:** Accordion or tabbed interface with expandable sections

### Pattern 12: Toolkit Tool Cards

**Use Cases:** Tool Discovery, Tool Orchestration, Tool Integration pages

**HTML Structure:**
```html
<div class="glass-card toolkit-tool">
    <div class="tool-header">
        <i class="fas fa-wrench"></i>
        <h3>Semantic Search Tool</h3>
        <span class="tool-status active">ACTIVE</span>
    </div>
    <div class="tool-capabilities">
        <span class="capability-badge">Code Analysis</span>
        <span class="capability-badge">Pattern Detection</span>
        <span class="capability-badge">Context Retrieval</span>
    </div>
    <div class="tool-description">
        <p>Searches codebase using natural language queries...</p>
    </div>
    <div class="tool-stats">
        <div class="stat">
            <span class="stat-value">1,234</span>
            <span class="stat-label">Searches</span>
        </div>
        <div class="stat">
            <span class="stat-value">98%</span>
            <span class="stat-label">Accuracy</span>
        </div>
    </div>
</div>
```

**CSS:**
```css
.toolkit-tool {
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.toolkit-tool:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    cursor: pointer;
}

.toolkit-tool .tool-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.toolkit-tool .tool-status {
    margin-left: auto;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.toolkit-tool .tool-status.active {
    background: rgba(0, 255, 127, 0.2);
    color: #00ff7f;
    border: 1px solid #00ff7f;
}

.toolkit-tool .tool-capabilities {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.toolkit-tool .capability-badge {
    background: rgba(255, 255, 255, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
    font-size: 0.75rem;
}

.toolkit-tool .tool-stats {
    display: flex;
    gap: var(--spacing-xl);
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.toolkit-tool .stat {
    text-align: center;
}

.toolkit-tool .stat-value {
    display: block;
    font-size: var(--font-2xl);
    font-weight: 700;
    color: var(--accent-primary);
}

.toolkit-tool .stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
}
```

**D3.js Visuals:**
- **Tool Discovery:** Treemap (tool categories)
- **Tool Orchestration:** Sankey diagram (tool chain)
- **Tool Integration:** Force-directed graph (dependencies)

### Pattern 13: LENS Analysis Cards

**Use Cases:** AST Analysis, Reverse Engineering, Code Intelligence pages

**HTML Structure:**
```html
<div class="glass-card lens-analysis">
    <div class="analysis-header">
        <i class="fas fa-search-code"></i>
        <h3>Function Complexity Analysis</h3>
    </div>
    <div class="code-preview">
        <pre><code class="language-python">
def complex_function(data, config):
    # Analyzed code...
    pass
        </code></pre>
    </div>
    <div class="analysis-results">
        <div class="metric">
            <span class="metric-label">Cyclomatic Complexity</span>
            <span class="metric-value warning">12</span>
        </div>
        <div class="metric">
            <span class="metric-label">Lines of Code</span>
            <span class="metric-value">45</span>
        </div>
        <div class="metric">
            <span class="metric-label">Dependencies</span>
            <span class="metric-value">8</span>
        </div>
    </div>
    <div class="analysis-insights">
        <p><i class="fas fa-lightbulb"></i> Consider extracting helper functions to reduce complexity.</p>
    </div>
</div>
```

**CSS:**
```css
.lens-analysis {
    cursor: default;
    overflow: hidden;
}

/* Glass reflection (non-clickable display) */
.lens-analysis::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        135deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    animation: glassReflection 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.lens-analysis > * {
    position: relative;
    z-index: 1;
}

.lens-analysis .code-preview {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 8px;
    padding: var(--spacing-md);
    margin: var(--spacing-lg) 0;
    max-height: 300px;
    overflow-y: auto;
}

.lens-analysis .analysis-results {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-lg);
    margin: var(--spacing-lg) 0;
}

.lens-analysis .metric {
    flex: 1;
    min-width: 120px;
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.lens-analysis .metric-value {
    display: block;
    font-size: var(--font-2xl);
    font-weight: 700;
    margin-top: var(--spacing-xs);
}

.lens-analysis .metric-value.warning {
    color: #ffa500;
}

.lens-analysis .analysis-insights {
    background: rgba(0, 212, 255, 0.1);
    border-left: 4px solid var(--accent-primary);
    padding: var(--spacing-md);
    border-radius: 8px;
    margin-top: var(--spacing-lg);
}

.lens-analysis .analysis-insights i {
    color: var(--accent-primary);
    margin-right: var(--spacing-xs);
}
```

**D3.js Visuals:**
- **AST Analysis:** Hierarchical tree diagram
- **Reverse Engineering:** Force-directed graph (modules)
- **Code Intelligence:** Heatmap (file complexity)

### Pattern 14: Get Started Step Cards

**Use Cases:** Installation, Configuration, First Steps pages

**HTML Structure:**
```html
<div class="glass-card step-card">
    <div class="step-number">1</div>
    <h3>Install CORTEX</h3>
    <p>Run the following command to install CORTEX:</p>
    <div class="code-block">
        <button class="copy-btn" aria-label="Copy code">
            <i class="fas fa-copy"></i>
        </button>
        <pre><code class="language-bash">pip install cortex-ai</code></pre>
    </div>
    <div class="step-footer">
        <p class="time-estimate"><i class="far fa-clock"></i> ~2 minutes</p>
    </div>
</div>
```

**CSS:**
```css
.step-card {
    position: relative;
    padding-top: calc(var(--spacing-xl) + 50px);
    cursor: default;
    overflow: hidden;
}

/* Glass reflection (non-clickable display) */
.step-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        135deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    animation: glassReflection 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

.step-card > * {
    position: relative;
    z-index: 1;
}

.step-card .step-number {
    position: absolute;
    top: var(--spacing-xl);
    left: var(--spacing-xl);
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    border-radius: 50%;
    font-size: 1.5rem;
    font-weight: 800;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

.step-card .code-block {
    position: relative;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 8px;
    padding: var(--spacing-md);
    margin: var(--spacing-lg) 0;
}

.step-card .copy-btn {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.1);
    border: none;
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.step-card .copy-btn:hover {
    background: rgba(0, 212, 255, 0.3);
}

.step-card .time-estimate {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-top: var(--spacing-md);
}

.step-card .time-estimate i {
    margin-right: var(--spacing-xs);
}
```

**Visual Elements:** Step-by-step numbered cards with copy-to-clipboard functionality

---

### Pattern 15: Level 0 Multi-Panel System (Security, Orchestrators, STS)

**Use Cases:** Home page tiles with many Level 2 pages requiring categorization
- **Security:** 13 pages/4 categories
- **Orchestrators:** 19 pages/5 categories
- **Sharpen The Saw:** 6 pages/6 categories

**Design Philosophy:**
- **Progressive Disclosure**: Show categories first, then links within categories
- **Visual Hierarchy**: Main panel → Category sub-panels → Links (Tetris grid for multi-tag, full-width for single-tag)
- **Non-Clickable Containers**: Sub-panels are display only, links within are clickable
- **Glassmorphism**: Layered glass effects with gradients and shadows
- **Intelligent Layout**: Adaptive grid based on panel count and tag density

**Grid Layout Intelligence (v4.0.1):**

| Subpanels | Grid Layout | CSS Class | Tag Layout | Use Case |
|-----------|-------------|-----------|------------|----------|
| 4 | 2x2 | (default) | Tetris/masonry | Security pattern |
| 5 | 2x3 (1 odd) | (default) | Tetris/masonry | Orchestrators pattern |
| 6 | 3x2 | `.grid-3x2` | Single full-width | STS pattern |

**Single-Tag Subpanel Styling:**
- Add `.single-tag` class to subpanels with only 1 link
- More compact sizing: `min-height: 280px` (vs 380px for multi-tag)
- Smaller icons: 60x60px (vs 70x70px)
- Full-width link (no Tetris grid needed)

**HTML Structure:**

**Example 1: Security Panel (4 subpanels, multi-tag, 2x2 grid):**
```html
<section class="key-features-section" id="security-panel">
    <div class="main-panel-wrapper">
        <div class="panel-header-centered">
            <h2 class="panel-title-main">
                <span>🛡️</span>
                <span>SECURITY</span>
            </h2>
            <p class="panel-subtitle-main">Comprehensive threat modeling, compliance standards, and security assessments</p>
        </div>

        <div class="category-panels-grid">
            <!-- Protection Category (multi-tag) -->
            <div class="category-subpanel">
                <div class="category-icon-wrapper">
                    <span class="category-icon">🔒</span>
                </div>
                <h3 class="category-title">Protection</h3>
                <p class="category-description">Role-based access control, data encryption, privacy safeguards, and comprehensive activity tracking.</p>
                <div class="category-tags">
                    <a href="security/access-control.html" class="category-tag">
                        <span>Access Control</span>
                    </a>
                    <a href="security/data-protection.html" class="category-tag">
                        <span>Data Protection</span>
                    </a>
                    <a href="security/audit-logging.html" class="category-tag">
                        <span>Audit Logging</span>
                    </a>
                </div>
            </div>
            <!-- Repeat for Assessment, Compliance, Response categories -->
        </div>
    </div>
</section>
```

**Example 2: STS Panel (6 subpanels, single-tag, 3x2 grid):**
```html
<section class="key-features-section" id="sts-panel">
    <div class="main-panel-wrapper">
        <div class="panel-header-centered">
            <h2 class="panel-title-main">
                <span>🔧</span>
                <span>SHARPEN THE SAW</span>
            </h2>
            <p class="panel-subtitle-main">Continuous improvement through security, SOLID principles, and quality standards</p>
        </div>

        <!-- 3x2 Grid with single-tag subpanels -->
        <div class="category-panels-grid grid-3x2">
            <div class="category-subpanel single-tag">
                <div class="category-icon-wrapper">
                    <span class="category-icon">🛡️</span>
                </div>
                <h3 class="category-title">Security</h3>
                <p class="category-description">Security-first development practices, threat modeling integration, and defensive coding patterns.</p>
                <div class="category-tags">
                    <a href="sts/security.html" class="category-tag">
                        <span>Security Best Practices</span>
                    </a>
                </div>
            </div>
            <!-- Repeat for SOLID, Code Quality, Performance, Testing, Documentation -->
        </div>
    </div>
</section>
```

**CSS (defined in `docs/index.html` or external stylesheet):**
```css
/* Main panel wrapper */
.main-panel-wrapper {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(0, 212, 255, 0.10));
    border: 1px solid rgba(123, 97, 255, 0.4);
    border-radius: 16px;
    padding: 2.5rem;
    backdrop-filter: blur(10px);
}

/* Category panels grid - Intelligent layout */
.category-panels-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}

@media (min-width: 768px) {
    /* Default: 2x2 grid for 4-5 panels */
    .category-panels-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    /* 3x2 grid for 6 panels (STS pattern) */
    .category-panels-grid.grid-3x2 {
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(3, 1fr);
    }
}

/* Category sub-panel (non-clickable) */
.category-subpanel {
    background: linear-gradient(135deg, rgba(10, 14, 39, 0.8), rgba(26, 31, 58, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    cursor: default; /* Non-clickable */
    min-height: 380px;
}

/* Single-tag subpanels: More compact */
.category-subpanel.single-tag {
    min-height: 280px;
    padding: 1.5rem 1.25rem;
}

.category-subpanel.single-tag .category-icon-wrapper {
    width: 60px;
    height: 60px;
    font-size: 2rem;
}

.category-subpanel.single-tag .category-tag {
    grid-column: span 3; /* Full width */
    font-size: 0.95rem;
    padding: 0.75rem 1rem;
}

/* Tetris/masonry grid for category tags */
.category-tags {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 60px;
    gap: 0.75rem;
}

/* Individual tag (clickable link) */
.category-tag {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(123, 97, 255, 0.15));
    border: 1px solid rgba(0, 212, 255, 0.35);
    cursor: pointer;
    transition: all 0.3s ease;
}

.category-tag:hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 97, 255, 0.25));
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}
```

/* 🎨 COLOR VARIATIONS (Complementary Palette) */
/* Randomized distribution across panels for visual variety */

/* Cyan - Default base color */
.level0-category-tag {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(123, 97, 255, 0.15));
    border-color: rgba(0, 212, 255, 0.35);
    color: rgba(0, 212, 255, 0.95);
}
.level0-category-tag:hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 97, 255, 0.25));
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

/* Purple - Secondary accent */
.level0-category-tag.tag-purple {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}
.level0-category-tag.tag-purple:hover {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.3), rgba(186, 85, 211, 0.25));
    border-color: rgba(123, 97, 255, 0.6);
    box-shadow: 0 6px 20px rgba(123, 97, 255, 0.4);
}

/* Teal - Tertiary accent */
.level0-category-tag.tag-teal {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-tag.tag-teal:hover {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.3), rgba(0, 212, 255, 0.25));
    border-color: rgba(20, 184, 166, 0.6);
    box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);
}

/* 🎲 RANDOMIZED COLOR DISTRIBUTION (Anti-Monotony Pattern) */
/* Apply colors pseudo-randomly across categories to avoid predictable patterns */
/* Example for 4-category panel (Security): */

/* Protection category - Mixed colors */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(2) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(3) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}

/* Assessment category - Different mix */
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(1) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(2) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(3) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(4) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}

/* Compliance category - Another mix */
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(1) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(2) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(3) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}

/* Response category - Final mix */
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(1) { /* Cyan */ }
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(2) { 
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(0, 212, 255, 0.15));
    border-color: rgba(20, 184, 166, 0.35);
    color: rgba(20, 184, 166, 0.95);
}
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(3) { 
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(186, 85, 211, 0.15));
    border-color: rgba(123, 97, 255, 0.35);
    color: rgba(186, 85, 211, 0.95);
}

/* Apply hover states to randomized colors */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(3):hover,
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(2):hover,
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(1):hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(123, 97, 255, 0.25));
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(2):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(2):hover,
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(3):hover,
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(3):hover {
    background: linear-gradient(135deg, rgba(123, 97, 255, 0.3), rgba(186, 85, 211, 0.25));
    border-color: rgba(123, 97, 255, 0.6);
    box-shadow: 0 6px 20px rgba(123, 97, 255, 0.4);
}

.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(3):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(1):hover,
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(4):hover,
.level0-category-subpanel:nth-of-type(3) .level0-category-tag:nth-child(1):hover,
.level0-category-subpanel:nth-of-type(4) .level0-category-tag:nth-child(2):hover {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.3), rgba(0, 212, 255, 0.25));
    border-color: rgba(20, 184, 166, 0.6);
    box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);
}

/* Tetris layout patterns (see glassmorphism.css for full specs) */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1) { 
    grid-column: span 1; grid-row: span 3; font-size: 1.2rem; 
}
/* ... additional patterns for dynamic sizing */
```

**Key Features:**
- **2-column grid** on desktop (768px+), **1-column** on mobile
- **Tetris/masonry layout** within each category for visual interest
- **Dynamic font sizing** based on tag importance (1rem - 1.2rem)
- **Shimmer hover effect** on tags (light sweep animation)
- **Glassmorphism layers**: Main panel → Sub-panels → Tags (3 depth levels)
- **🎨 Color Variations**: Apply `.tag-purple`, `.tag-teal`, `.tag-indigo`, or `.tag-pink` to create visual variety while maintaining the blue glassmorphism theme

**Color Variation Usage (Anti-Monotony Pattern):**

**🎲 Randomized Distribution:** Instead of applying sequential color patterns (1st=cyan, 2nd=purple, 3rd=teal), distribute colors pseudo-randomly across categories to avoid visual monotony.

**Implementation Strategy:**
```css
/* BAD: Sequential pattern - looks monotonous */
.level0-category-tag:nth-child(3n+1) { color: cyan; }
.level0-category-tag:nth-child(3n+2) { color: purple; }
.level0-category-tag:nth-child(3n+3) { color: teal; }

/* GOOD: Randomized pattern - visual variety */
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(1) { color: cyan; }
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(2) { color: purple; }
.level0-category-subpanel:nth-of-type(1) .level0-category-tag:nth-child(3) { color: teal; }
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(1) { color: teal; }
.level0-category-subpanel:nth-of-type(2) .level0-category-tag:nth-child(2) { color: purple; }
/* ... randomized across panels */
```

**Color Palette (7-color system):**
- **Cyan**: `rgba(0, 212, 255)` - Primary accent, complements blue theme
- **Purple**: `rgba(123, 97, 255) → rgba(186, 85, 211)` - Warmth accent
- **Teal**: `rgba(20, 184, 166)` - Bridge accent  
- **Indigo**: `rgba(79, 70, 229) → rgba(99, 102, 241)` - Deep accent
- **Pink**: `rgba(236, 72, 153) → rgba(244, 114, 182)` - Vibrant accent
- **Emerald**: `rgba(16, 185, 129) → rgba(52, 211, 153)` - Success accent
- **Amber**: `rgba(245, 158, 11) → rgba(251, 191, 36)` - Energy accent

**Design Rationale:**
- **Anti-Monotony**: Randomized 7-color distribution prevents predictable visual patterns
- **Complementary**: All 7 colors harmonize with blue glassmorphism base theme
- **Accessibility**: Sufficient contrast ratios maintained across all variants (WCAG 2.1 AA)
- **Visual Hierarchy**: Color variety aids visual scanning and tile distinction
- **Extended Palette**: 7 colors provide maximum diversity for large multi-panel sections

**Usage Guidelines:**
1. Use randomized distribution across all multi-panel sections (Security, Orchestrators, STS)
2. Distribute colors pseudo-randomly via nth-of-type/nth-child CSS selectors
3. Aim for balanced distribution (~14% per color across entire panel)
4. Apply to ALL levels (Level 0, Level 1, Level 2) for consistency
5. Available as `.tag-purple`, `.tag-teal`, `.tag-indigo`, `.tag-pink`, `.tag-emerald`, `.tag-amber` modifier classes

```html
<!-- Example: Security Protection category with randomized colors -->
```html
<!-- Example: Security Protection category with randomized colors -->
<div class="level0-category-tags">
    <a href="security/access-control.html" class="level0-category-tag">Access Control</a> <!-- Cyan -->
    <a href="security/data-protection.html" class="level0-category-tag">Data Protection</a> <!-- Purple -->
    <a href="security/audit-logging.html" class="level0-category-tag">Audit Logging</a> <!-- Teal -->
</div>

<!-- Assessment category - Different distribution -->
<div class="level0-category-tags">
    <a href="security/threat-modeling.html" class="level0-category-tag">Threat Modeling</a> <!-- Teal -->
    <a href="security/risk-assessment.html" class="level0-category-tag">Risk Assessment</a> <!-- Purple -->
    <a href="security/vulnerability-assessment.html" class="level0-category-tag">Vulnerability Assessment</a> <!-- Cyan -->
    <a href="security/penetration-testing.html" class="level0-category-tag">Penetration Testing</a> <!-- Teal -->
</div>
```

**Accessibility:**
- Sub-panels use `cursor: default` (non-interactive containers)
- Tags use `cursor: pointer` (clickable links)
- Semantic HTML with proper heading hierarchy
- Keyboard navigation via tab

**Performance:**
- CSS-only animations (GPU-accelerated)
- No JavaScript required
- Responsive with minimal media queries

---

**Visual Elements:** Step-by-step numbered cards with copy-to-clipboard functionality

---

## ✨ Micro-Interactions Library

### Ripple Effect (Click Feedback)
```css
.ripple-glass {
    position: relative;
    overflow: hidden;
}

.ripple-glass::after {
    content: '';
    position: absolute;
    top: var(--ripple-y, 50%);
    left: var(--ripple-x, 50%);
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transform: translate(-50%, -50%);
    animation: rippleEffect 0.6s ease-out;
    pointer-events: none;
}

@keyframes rippleEffect {
    0% {
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        width: 300px;
        height: 300px;
        opacity: 0;
    }
}
```

**JavaScript (Optional - for click position):**
```javascript
document.querySelectorAll('.ripple-glass').forEach(el => {
    el.addEventListener('click', (e) => {
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--ripple-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--ripple-y', `${e.clientY - rect.top}px`);
    });
});
```

### 3D Tilt Effect (Hover)
```css
.tilt-glass {
    transform-style: preserve-3d;
    transition: transform 0.3s ease;
}

.tilt-glass:hover {
    transform: perspective(1000px) rotateX(5deg) rotateY(5deg);
}
```

### Glow Pulse (Focus/Active)
```css
.pulse-glow-glass:focus,
.pulse-glow-glass.active {
    animation: glowPulse 2s ease-in-out infinite;
    outline: none;
}

@keyframes glowPulse {
    0%, 100% {
        box-shadow: 
            0 0 20px rgba(0, 212, 255, 0.3),
            0 0 40px rgba(0, 212, 255, 0.2);
    }
    50% {
        box-shadow: 
            0 0 40px rgba(0, 212, 255, 0.5),
            0 0 80px rgba(0, 212, 255, 0.3);
    }
}
```

### Shimmer Effect (Loading)
```css
.shimmer-glass {
    background: linear-gradient(
        90deg,
        rgba(26, 31, 58, 0.6) 0%,
        rgba(255, 255, 255, 0.1) 50%,
        rgba(26, 31, 58, 0.6) 100%
    );
    background-size: 200% 100%;
    animation: shimmerSlide 2s linear infinite;
}

@keyframes shimmerSlide {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

### Magnetic Hover (Cursor Pull)
```css
.magnetic-glass {
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.magnetic-glass:hover {
    transform: scale(1.05);
}
```

---

## 🚀 Performance Optimization

### GPU Acceleration
```css
/* Apply to all glass elements */
.glass-optimized {
    transform: translateZ(0);
    will-change: transform, opacity;
    backface-visibility: hidden;
    perspective: 1000px;
}
```

### Conditional Blur (Device-Aware)
```css
/* Disable blur on low-end devices */
@media (max-width: 768px) and (max-resolution: 1dppx) {
    .glass-card {
        backdrop-filter: none;
        background: rgba(26, 31, 58, 0.95); /* More opaque */
    }
}

/* Enhanced blur on high-DPI displays */
@media (min-resolution: 2dppx) {
    .glass-card {
        backdrop-filter: blur(25px) saturate(200%);
    }
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
    .glass-card,
    .morph-card,
    .liquid-blob,
    .light-leak-glass::before,
    .light-leak-glass::after {
        animation: none !important;
        transition: none !important;
    }
}
```

### Lazy Animation Loading
```javascript
// Only animate visible elements
const glassObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-glass');
            glassObserver.unobserve(entry.target);
        }
    });
}, { rootMargin: '50px' });

document.querySelectorAll('.glass-card').forEach(card => {
    glassObserver.observe(card);
});
```

---

## 🎨 CSS Variables (Design Tokens)

```css
:root {
    /* Colors */
    --accent-primary: #00d4ff;
    --accent-secondary: #7b61ff;
    --glass-bg: rgba(26, 31, 58, 0.6);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Spacing */
    --space-xs: 0.5rem;   /* 8px */
    --space-sm: 1rem;     /* 16px */
    --space-md: 1.5rem;   /* 24px */
    --space-lg: 2rem;     /* 32px */
    --space-xl: 3rem;     /* 48px */
    
    /* Blur Levels */
    --blur-sm: 10px;
    --blur-md: 20px;
    --blur-lg: 30px;
    
    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 16px;
    --radius-lg: 24px;
    
    /* Transitions */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 320px) {
    /* Small mobile */
    .glass-card { padding: var(--space-sm); }
}

@media (min-width: 480px) {
    /* Mobile landscape */
    .glass-card { padding: var(--space-md); }
}

@media (min-width: 768px) {
    /* Tablet */
    .glass-card { padding: var(--space-lg); }
}

@media (min-width: 1024px) {
    /* Desktop */
    .glass-card { padding: var(--space-lg); }
}

@media (min-width: 1440px) {
    /* Large desktop */
    .glass-card { padding: var(--space-xl); }
}
```

---

## 🧪 Testing Checklist

### Visual Testing
- [ ] Blur effect renders correctly (Chrome DevTools → Rendering → Show layer borders)
- [ ] Border gradients display properly
- [ ] Animations run at 60fps (Performance monitor)
- [ ] Hover states trigger smoothly

### Cross-Browser Testing
- [ ] Chrome 90+ (backdrop-filter support)
- [ ] Firefox 88+ (backdrop-filter support)
- [ ] Safari 14+ (webkit-backdrop-filter)
- [ ] Edge 90+ (chromium-based)

### Performance Testing
- [ ] Page load <3s on 3G
- [ ] Animation FPS ≥60
- [ ] GPU memory <50MB
- [ ] No layout thrashing (DevTools → Performance)

### Accessibility Testing
- [ ] Keyboard navigation works (Tab, Enter, Esc)
- [ ] Focus indicators visible
- [ ] Reduced-motion respected
- [ ] Screen reader compatible (ARIA labels)

---

## 🛠️ Implementation Scripts

### Auto-Apply Glass Classes (JavaScript)
```javascript
// Automatically apply glass patterns to elements
class GlassManager {
    constructor() {
        this.applyGlassPatterns();
        this.initInteractions();
    }
    
    applyGlassPatterns() {
        // Auto-detect card containers
        document.querySelectorAll('[data-glass="card"]').forEach(el => {
            el.classList.add('glass-card');
        });
        
        // Auto-detect modals
        document.querySelectorAll('[data-glass="modal"]').forEach(el => {
            el.classList.add('glass-modal');
        });
        
        // Auto-detect tooltips
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            this.createTooltip(el);
        });
    }
    
    initInteractions() {
        // Ripple effect
        document.querySelectorAll('.ripple-glass').forEach(el => {
            el.addEventListener('click', this.createRipple.bind(this));
        });
        
        // Modal triggers
        document.querySelectorAll('[data-modal-trigger]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.dataset.modalTrigger;
                this.openModal(modalId);
            });
        });
    }
    
    createRipple(e) {
        const el = e.currentTarget;
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--ripple-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--ripple-y', `${e.clientY - rect.top}px`);
    }
    
    createTooltip(el) {
        const text = el.dataset.tooltip;
        const tooltip = document.createElement('div');
        tooltip.className = 'glass-tooltip';
        tooltip.textContent = text;
        el.style.position = 'relative';
        el.appendChild(tooltip);
    }
    
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('open'), 10);
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('open');
            setTimeout(() => modal.style.display = 'none', 300);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.glassManager = new GlassManager();
});
```

### Performance Monitor
```javascript
// Monitor glassmorphism performance
class GlassPerformanceMonitor {
    constructor() {
        this.fpsSamples = [];
        this.lastFrame = performance.now();
        this.monitoring = false;
    }
    
    start() {
        this.monitoring = true;
        this.measure();
    }
    
    stop() {
        this.monitoring = false;
        return this.getReport();
    }
    
    measure() {
        if (!this.monitoring) return;
        
        const now = performance.now();
        const delta = now - this.lastFrame;
        const fps = 1000 / delta;
        
        this.fpsSamples.push(fps);
        if (this.fpsSamples.length > 60) {
            this.fpsSamples.shift();
        }
        
        this.lastFrame = now;
        requestAnimationFrame(() => this.measure());
    }
    
    getReport() {
        const avgFps = this.fpsSamples.reduce((a, b) => a + b, 0) / this.fpsSamples.length;
        const minFps = Math.min(...this.fpsSamples);
        const maxFps = Math.max(...this.fpsSamples);
        
        return {
            average: avgFps.toFixed(2),
            min: minFps.toFixed(2),
            max: maxFps.toFixed(2),
            status: avgFps >= 55 ? '✅ GOOD' : '⚠️ NEEDS OPTIMIZATION'
        };
    }
}

// Usage:
// const monitor = new GlassPerformanceMonitor();
// monitor.start();
// ... interact with glass elements ...
// const report = monitor.stop();
// console.log('Glass Performance:', report);
```

---

## 📐 Layout Patterns

### Pattern 6: Metrics Dashboard (Centered Flexbox)

**Use Case:** Hero section KPI cards, statistics displays, feature highlights

**Implementation:**
```css
.metrics-dashboard {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-lg);
    width: 100%;
    margin: 0 auto var(--spacing-3xl);
    padding: 0 var(--spacing-lg);
}

.metric-card {
    text-align: center;
    padding: var(--spacing-xl) var(--spacing-2xl);
    min-width: 140px;
    flex: 0 1 auto;
}

.metric-value {
    font-size: var(--font-3xl);
    font-weight: 800;
    margin-bottom: var(--spacing-xs);
}

.metric-label {
    font-size: var(--font-sm);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
```

**Why Flexbox over Grid:**
- Grid with `auto-fit` creates unequal spacing when cards don't fill row
- Flexbox with `justify-content: center` ensures cards are always centered
- `flex: 0 1 auto` prevents cards from stretching

---

### Pattern 7: Balanced Navigation Footer

**Use Case:** Page-to-page navigation with prev/next buttons

**Implementation:**
```css
/* Container */
.nav-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto var(--spacing-2xl);
    padding: var(--spacing-xl);
}

/* Navigation Links - Equal Width for Visual Balance */
.nav-link {
    min-width: 220px;
    text-align: center;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    text-decoration: none;
    transition: all 0.3s ease;
}

.nav-link:hover {
    background: rgba(0, 212, 255, 0.1);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}
```

**Inline Override (for existing pages):**
```html
<nav class="nav-footer" style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto var(--spacing-2xl); padding: var(--spacing-xl);">
    <a href="prev.html" class="nav-link prev" style="min-width: 220px; text-align: center;">
        ← Previous Page
    </a>
    <a href="next.html" class="nav-link next" style="min-width: 220px; text-align: center;">
        Next Page →
    </a>
</nav>
```

**Key Requirements:**
- Equal `min-width` on both buttons (220px)
- Centered text within each button
- `max-width: 1200px` on container with `margin: 0 auto` for page centering
- `justify-content: space-between` pushes buttons to edges
- Bottom margin (`margin-bottom: var(--spacing-2xl)`) for page breathing room

---

## 🎓 Best Practices

### DO ✅
- Use `backdrop-filter` for glass effect (not just opacity)
- Add GPU acceleration hints (`transform: translateZ(0)`)
- Provide reduced-motion fallbacks
- Test on mobile devices (blur is expensive)
- Use CSS variables for consistency
- **Clickable tiles:** Glow border + lift + `cursor: pointer`
- **Non-clickable tiles:** Glass reflection (8s) + `cursor: default`
- Add subtle animations (0.3s duration max)
- Keep animations modern and non-distracting

### DON'T ❌
- Overuse blur (>30px becomes unreadable)
- Animate backdrop-filter directly (use transform/opacity instead)
- Forget vendor prefixes (`-webkit-backdrop-filter`)
- Apply glass to text-heavy content (readability issues)
- Use glass on low-contrast backgrounds
- Chain multiple backdrop-filters (performance hit)
- Ignore mobile performance (disable blur on low-end devices)

---

## 📊 Pattern Selection Guide

| Use Case | Pattern | Interactivity | Animation | Level |
|----------|---------|---------------|-----------|-------|
| **Level 0 multi-category tile (13-19 pages)** | Pattern 15 (Multi-Panel) | Sub-panels: non-interactive, Tags: clickable | Tetris grid, shimmer on hover | Level 0 |
| **Level 0 simple tile (3-6 pages)** | Standard Tile | Interactive | Glow border + lift | Level 0 |
| Clickable tile/card | Multi-Layer Glass Card (Variant A) | Interactive | Glow border + lift on hover | All levels |
| Display card/panel | Multi-Layer Glass Card (Variant B) | Non-interactive | Glass reflection (8s) | All levels |
| Dashboard widget | Neuglass Card | Interactive | Soft shadow + lift | Level 1-2 |
| Architecture tile | Pattern 8 | Interactive | Left border glow + lift | Level 1-2 |
| Orchestrator card | Pattern 9 | Interactive | Phase glow + lift | Level 1-2 |
| STS category | Pattern 10 | Interactive | Icon glow + lift | Level 1-2 |
| Guideline card | Pattern 11 | Non-interactive | Glass reflection only | Level 1-2 |
| Tool card | Pattern 12 | Interactive | Tool icon glow + lift | Level 1-2 |
| Analysis result | Pattern 13 | Non-interactive | Glass reflection only | Level 1-2 |
| Setup step | Pattern 14 | Non-interactive | Glass reflection only | Level 1-2 |
| Modal overlay | Glass Modal | Interactive | Focus + backdrop blur | All levels |
| Notification | Glass Toast | Non-interactive | Slide-in animation | All levels |
| Form control | Glass Dropdown | Interactive | Border glow on focus | All levels |

**Key Differentiation:**
- **Interactive (Clickable):** `cursor: pointer` + glowing border on hover + `translateY(-2px)` lift
- **Non-Interactive (Display):** `cursor: default` + slow glass reflection (8s) + NO hover glow
- **Level 0 Multi-Panel:** Reserved for tiles with 10+ pages requiring categorization

---| Use Case | Pattern | Interactivity | Animation |
|----------|---------|---------------|------------|
| Clickable tile/card | Multi-Layer Glass Card (Variant A) | Interactive | Glow border + lift on hover |
| Display card/panel | Multi-Layer Glass Card (Variant B) | Non-interactive | Glass reflection (8s) |
| Dashboard widget | Neuglass Card | Interactive | Soft shadow + lift |
| Architecture tile | Pattern 8 | Interactive | Left border glow + lift |
| Orchestrator card | Pattern 9 | Interactive | Phase glow + lift |
| STS category | Pattern 10 | Interactive | Icon glow + lift |
| Guideline card | Pattern 11 | Non-interactive | Glass reflection only |
| Tool card | Pattern 12 | Interactive | Tool icon glow + lift |
| Analysis result | Pattern 13 | Non-interactive | Glass reflection only |
| Setup step | Pattern 14 | Non-interactive | Glass reflection only |
| Modal overlay | Glass Modal | Interactive | Focus + backdrop blur |
| Notification | Glass Toast | Non-interactive | Slide-in animation |
| Form control | Glass Dropdown | Interactive | Border glow on focus |

---

## 🔄 Migration from v2.x

**Breaking Changes:**
- Removed single-layer `.glass-basic` (use `.glass-card` instead)
- Renamed `--glass-opacity` → `--glass-bg`
- Changed default blur from 10px → 20px
- Updated transition timing (now uses cubic-bezier)

**Migration Script:**
```javascript
// Auto-migrate v2.x to v3.0
document.querySelectorAll('.glass-basic').forEach(el => {
    el.classList.remove('glass-basic');
    el.classList.add('glass-card');
});

// Update CSS variables
document.documentElement.style.setProperty('--glass-bg', 'rgba(26, 31, 58, 0.6)');
```

---

## 📚 External Resources

- **MDN backdrop-filter:** https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter
- **Can I Use:** https://caniuse.com/css-backdrop-filter
- **Performance Guide:** https://web.dev/backdrop-filter/
- **Glassmorphism.com:** Design inspiration

---

## 📊 Interactive Visualizations (D3.js Patterns)

**Version:** 4.1.2 | **Added:** January 3, 2026

### Purpose

This section defines **D3.js visualization patterns** that enhance glassmorphism UI with interactive data representations. Used when static lists or grids lack visual impact.

**Use Cases:**
- Architecture diagrams (force-directed graphs)
- Principle showcases (interactive card grids)
- System relationships (node-link diagrams)
- Metric dashboards (animated charts)

**Reference Implementation:** `docs/architecture/index.html` (Principles + Architecture Overview)

---

### Pattern A: Interactive Principle Cards (D3.js Grid)

**Replaces:** Bullet lists with icons  
**Visual Impact:** Cards with hover glow, lift effects, and color-coded icons

**When to Use:**
- 3-6 key principles or features
- Each principle has icon, title, and description
- Need prominent visual presentation
- Touch-friendly interactions required

**HTML Structure:**
```html
<div class="principles-header">
    <h3><i class="fas fa-key"></i> Key Architectural Principles</h3>
</div>
<div id="principles-viz" class="d3-viz-container"></div>
```

**JavaScript Implementation:**
```javascript
// Data structure
const principles = [
    {
        id: 'protection',
        icon: '\uf3ed', // FontAwesome unicode
        title: 'Brain Protection First',
        description: 'Tier 0 SKULL rules enforce safety at governance layer',
        color: '#ef4444'
    },
    // ... more principles
];

// Render cards in responsive 3-column grid
const cardWidth = Math.min(280, (containerWidth - 80) / 3);
const cardHeight = 180;

// Card interactions: hover → glow + lift (-4px translateY)
// Touch targets: 280x180px minimum
```

**CSS Requirements:**
```css
.d3-viz-container {
    width: 100%;
    min-height: 400px;
    background: rgba(10, 14, 39, 0.2);
    border-radius: var(--radius-md);
    padding: var(--spacing-xl);
}

.principles-header h3 {
    font-size: 1.5rem;
    color: var(--accent-primary);
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
}
```

**Animation Tier:** T1 Subtle
- Hover: Card lift (-4px) + glow (0.4 opacity) + stroke width increase
- Duration: 200ms ease
- No infinite animations

**Responsive Breakpoints:**
- Desktop (1440px+): 3 cards per row
- Tablet (768px-1439px): 2 cards per row
- Mobile (<768px): 1 card per row

**Accessibility:**
- SVG `<title>` elements for screen readers
- Keyboard focus states (outline: 2px solid)
- Touch targets: 180px height minimum

---

### Pattern B: Force-Directed Architecture Graph

**Replaces:** Static stat grids or Mermaid diagrams  
**Visual Impact:** Interactive node-link diagram with drag, hover, and legend

**When to Use:**
- System architecture overview (10-20 components)
- Complex relationships between entities
- Need interactive exploration (drag nodes)
- Showcase technical complexity visually

**HTML Structure:**
```html
<div id="architecture-overview" class="d3-viz-container architecture-graph"></div>
```

**JavaScript Implementation:**
```javascript
// Node types with visual encoding
const nodes = [
    { id: 'cortex', label: 'CORTEX', icon: '\uf49e', size: 60, color: '#7b61ff', type: 'core' },
    { id: 't0', label: 'Tier 0\nSKULL', icon: '\uf3ed', size: 45, color: '#ef4444', type: 'brain' },
    // ... brain tiers, agents, orchestrators
];

// Force simulation with collision detection
const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).distance(120))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => d.size + 10));

// Hover: Node glow (0.4 opacity) + stroke width increase (3px → 5px)
// Drag: Update fx/fy positions, restart simulation
```

**CSS Requirements:**
```css
.d3-viz-container.architecture-graph {
    min-height: 500px;
    padding: 0;
    background: rgba(10, 14, 39, 0.2);
}

#architecture-overview .node circle {
    stroke: currentColor;
    stroke-width: 3px;
    transition: stroke-width 0.2s ease;
}

#architecture-overview .node:hover circle {
    stroke-width: 5px;
}
```

**Visual Elements:**
1. **Nodes:**
   - Core: 60px diameter, center position
   - Brain Tiers: 45px diameter, color-coded (T0: red, T1: green, T2: blue, T3: orange)
   - Agents: 40px diameter, cyan/purple gradient
   - Orchestrators: 35px diameter, teal/green shades

2. **Links:**
   - Gradient strokes (purple → cyan)
   - 2px width, 0.4 opacity
   - Dynamic positions (updates on simulation tick)

3. **Labels:**
   - Multi-line support (split on `\n`)
   - 11px font size, white text
   - Positioned below node (y = size + 18px)

4. **Legend:**
   - Bottom-left corner (20px from edges)
   - 4 categories with color circles
   - 12px font, gray text

**Animation Tier:** T1 Subtle
- Hover: Glow effect + stroke width increase
- Drag: Smooth position updates (no snapping)
- Simulation: Automatic stabilization after drag

**Responsive Breakpoints:**
- Desktop (1440px+): 500px height
- Tablet (768px-1439px): 400px height
- Mobile (<768px): 350px height, smaller node sizes

**Performance:**
- 10-20 nodes: Smooth (60fps)
- 20-50 nodes: Good (45fps)
- 50+ nodes: Use clustering or filtering

**Accessibility:**
- Keyboard drag: Arrow keys move focused node
- Screen reader: SVG `<title>` for each node/link
- Focus states: 2px outline on focused nodes

---

### Pattern Selection Guide

| Scenario | Pattern | Rationale |
|----------|---------|-----------|
| 3-6 features/principles | **Interactive Cards (A)** | Prominent showcase, touch-friendly |
| 10-20 system components | **Force Graph (B)** | Complex relationships, exploration |
| <3 items | Standard bullet list | Overkill for D3.js |
| 20+ items | Hierarchical tree or clustering | Force graph too crowded |
| Static content | Mermaid diagram | No interactivity needed |

---

### Implementation Checklist

**Before adding D3.js visualization:**
1. ✅ Is dataset complex enough? (3+ items minimum)
2. ✅ Does interactivity add value? (vs static image)
3. ✅ Are touch targets 44px+ for mobile?
4. ✅ Is page loading <3s with D3.js?
5. ✅ Does visualization scale to mobile?

**Required files:**
- `docs/assets/js/{page-name}-viz.js` - D3.js implementation
- `docs/assets/css/main.css` - Visualization-specific CSS
- CDN: `<script src="https://d3js.org/d3.v7.min.js"></script>`

**Color Palette:**
- Core System: `#7b61ff` (purple)
- Brain Tiers: `#ef4444` (red), `#10b981` (green), `#3b82f6` (blue), `#f59e0b` (orange)
- Agents: `#06b6d4` (cyan), `#8b5cf6` (purple)
- Orchestrators: `#14b8a6` (teal), `#10b981` (green)

**Font Awesome Icons:**
- Use unicode characters in D3.js text elements
- Font family: `'Font Awesome 6 Free'`, weight: `900`
- Example: `\uf49e` = brain icon

---

### Testing Requirements

**Browser Compatibility:**
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Test touch interactions on iOS/Android

**Performance Metrics:**
- Initial render: <500ms
- Hover response: <50ms
- Drag smoothness: 45fps minimum

**Responsive Testing:**
- 375px mobile (iPhone SE)
- 768px tablet (iPad)
- 1440px desktop

**Accessibility:**
- Keyboard navigation: Tab + arrow keys
- Screen reader: NVDA/JAWS/VoiceOver
- Color contrast: WCAG 2.1 AA (4.5:1 minimum)

---

### Pattern D: Principle Card Grid (2-Column, Centered Icons, Left-Aligned Text)

**Replaces:** Bullet lists with check icons  
**Visual Impact:** Prominent card grid with centered icons and professional left-aligned descriptions

**When to Use:**
- 3-5 key principles, features, or architectural concepts
- Medium-length descriptions (50-150 characters)
- Need visual prominence and scannability
- Content spans multiple lines

**⚠️ CRITICAL RULE:** Use **2-column layout** for descriptions >100 characters. 3-column only for short labels.

**HTML Structure:**
```html
<!-- 2-Column Grid for Medium-Long Content -->
<div class="principle-card-grid columns-2">
    <div class="principle-card">
        <div class="principle-icon">
            <i class="fas fa-shield-alt"></i>
        </div>
        <h3 class="principle-title">Brain Protection First</h3>
        <p class="principle-description">
            Tier 0 SKULL rules enforce safety at governance layer
        </p>
    </div>
    <!-- Repeat 3-5 cards -->
</div>
```

**CSS Requirements:**
```css
/* 2-Column Grid (DEFAULT for medium-long content) */
.principle-card-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-lg);
    margin: var(--spacing-xl) 0;
}

/* 3-Column Override (ONLY for short labels <50 chars) */
.principle-card-grid.columns-3 {
    grid-template-columns: repeat(3, 1fr);
}

.principle-card {
    padding: var(--spacing-xl);
    background: rgba(26, 31, 58, 0.6);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-md);
    text-align: center;
    transition: all 0.2s ease;
}

.principle-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* Icon: Always Centered */
.principle-icon {
    width: 60px;
    height: 60px;
    margin: 0 auto var(--spacing-md);
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 212, 255, 0.15);
    border-radius: var(--radius-full);
}

.principle-icon i {
    font-size: 1.75rem;
    color: var(--accent-primary);
}

/* Title: Always Centered */
.principle-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-sm);
    text-align: center;
}

/* Description: LEFT-ALIGNED for readability */
.principle-description {
    font-size: 0.9375rem;
    color: var(--text-secondary);
    line-height: 1.6;
    text-align: left; /* CRITICAL: Multi-line text must be left-aligned */
}
```

**Layout Decision Logic:**
```javascript
// Determine columns based on description length
const cards = document.querySelectorAll('.principle-card');
const avgLength = Array.from(cards)
    .map(card => card.querySelector('.principle-description').textContent.length)
    .reduce((a, b) => a + b) / cards.length;

const grid = document.querySelector('.principle-card-grid');
if (avgLength > 100) {
    grid.classList.add('columns-2'); // Long descriptions
} else if (avgLength > 50) {
    grid.classList.add('columns-2'); // Medium descriptions (SAFEST)
} else {
    grid.classList.add('columns-3'); // Short labels only
}
```

**Visual Elements:**
1. **Icon Circle:**
   - 60px diameter
   - Centered above title
   - Accent color background (15% opacity)
   - 1.75rem icon size

2. **Title:**
   - 1.125rem font size
   - Centered text
   - 600 weight
   - 8px margin below

3. **Description:**
   - **LEFT-ALIGNED** (not centered) for multi-line readability
   - 0.9375rem font size
   - 1.6 line-height for comfortable reading
   - Secondary color for hierarchy

**Animation Tier:** T1 Subtle
- Hover: Lift (-4px) + border glow + shadow
- Duration: 200ms ease
- No infinite animations

**Responsive Breakpoints:**
- Desktop (1440px+): 2 columns (3 only if short content)
- Tablet (768px-1439px): 2 columns
- Mobile (<768px): 1 column

**Examples:**

**✅ CORRECT (2-column for long content):**
```
Card 1: "Tier 0 SKULL rules enforce safety at governance layer" (55 chars)
Card 2: "TDD mandatory for all production code (RED→GREEN→REFACTOR)" (60 chars)
→ Average: 57.5 chars → 2 columns
```

**❌ WRONG (3-column for long content):**
```
Card 1: "Tier 0 SKULL rules enforce..." (text cramped)
Card 2: "TDD mandatory for all..." (text cramped)
→ 3 columns causes line wrapping and poor readability
```

**Reference Implementation:** `docs/architecture/index.html` (Executive Summary - Key Architectural Principles)

---

### Pattern C: Simplified 2-Column Tier Layout

**Replaces:** 4-column masonry grids with excessive text  
**Visual Impact:** Clean 2-column layout with inline icons and card capabilities

**When to Use:**
- 4 related components/tiers with detailed information
- Need horizontal icon+title layout (not stacked)
- Card-based capability lists (not bullets)
- Reduce visual verbosity

**HTML Structure:**
```html
<div class="two-column-grid">
    <div class="glass-card-clickable animation-t1">
        <!-- Inline Icon + Title Header -->
        <div class="tier-header">
            <div class="card-icon tier0-icon">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div>
                <h3 class="card-title">Tier 0: SKULL Governance</h3>
                <p class="card-subtitle">Brain Protection & Safety Validation</p>
            </div>
        </div>
        
        <!-- Card-based Capabilities (not bullets) -->
        <div class="capability-tiles">
            <div class="capability-tile">
                <i class="fas fa-check-circle"></i>
                <div>
                    <strong>TDD_ENFORCEMENT</strong>
                    <span>RED→GREEN→REFACTOR mandatory</span>
                </div>
            </div>
            <!-- More tiles... -->
        </div>
    </div>
</div>
```

**CSS Requirements:**
```css
/* Inline Icon + Title Header */
.tier-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.tier-header .card-icon {
    flex-shrink: 0;
}

.tier-header > div {
    flex: 1;
}

/* Card-based Capability Tiles */
.capability-tiles {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
}

.capability-tile {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: rgba(10, 14, 39, 0.4);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--accent-primary);
    transition: all 0.2s ease;
}

.capability-tile:hover {
    background: rgba(10, 14, 39, 0.6);
    transform: translateX(4px);
}

.capability-tile > i {
    font-size: 1.25rem;
    color: var(--accent-primary);
    flex-shrink: 0;
}

.capability-tile strong {
    display: block;
    color: var(--text-primary);
    font-size: 0.9375rem;
}

.capability-tile span {
    display: block;
    color: var(--text-secondary);
    font-size: 0.875rem;
}
```

**Visual Elements:**
1. **Header:**
   - Icon (40-60px circle) + Title + Subtitle in horizontal flex
   - Icon floats left, text fills remaining space
   - 16px gap between icon and text

2. **Capability Tiles:**
   - Each tile is a mini card with left border accent
   - Icon (20px) + Text (title + description)
   - Hover: Slide right 4px + darken background
   - 3px left border (accent color)

3. **Used By Section:**
   - Horizontal tag layout (not bullets)
   - Pills with accent background/border
   - Hover: Lift 1px + brighten

**Animation Tier:** T1 Subtle
- Hover: Tile slide right (4px) + background transition
- Duration: 200ms ease
- No infinite animations

**Responsive Breakpoints:**
- Desktop (1440px+): 2 columns
- Tablet (768px-1439px): 2 columns (narrower)
- Mobile (<768px): 1 column, smaller padding

**Advantages Over 4-Column:**
- 50% less visual clutter
- Easier to scan (2 columns vs 4)
- Inline icons improve readability
- Card tiles feel more modern than bullets

---

## 📄 Version History

### v4.1.4 (January 3, 2026) - Content-Driven Layout Intelligence
- 🎯 **BREAKING:** Added Content-Driven Layout Decision Matrix (choose 2 vs 3 columns by content length)
- 🎯 **BREAKING:** Core Principle #13-16 - Cards over bullets, smart icon placement, left-align long text
- ✨ **NEW:** Pattern D - Principle Card Grid (2-column with centered icons, left-aligned descriptions)
- ✨ Added intelligent column selection algorithm (avgLength >100 chars → 2 columns)
- 📚 Updated Quick Reference with content metrics and layout rationale
- 📚 Added icon placement rules: centered for short content, inline-left for long content
- 📚 Added text alignment rules: descriptions >100 chars MUST be left-aligned
- 📚 Added visual pattern decision matrix expansion (list vs cards, icon placement, description length)
- 🎨 Emphasized "Always prefer cards over bullet lists" philosophy
- 🎨 Added CSS for `.principle-card-grid`, `.principle-card`, `.principle-icon`
- 🎯 Reference implementation: `docs/architecture/index.html` (Executive Summary + Tier Deep Dive)
- ⚠️ CRITICAL: 2-column is SAFEST default for 50-150 char descriptions

### v4.1.3 (January 3, 2026) - Simplified Layout Patterns
- ✨ **NEW:** Pattern C - Simplified 2-Column Tier Layout
- ✨ Inline icon+title header (horizontal flex, not stacked)
- ✨ Card-based capability tiles (replaces bullet lists)
- ✨ "Used By" section with pill tags (not bullets)
- 📚 Added CSS for `.tier-header`, `.capability-tiles`, `.capability-tile`
- 📚 Added hover effects: slide right (4px) + background darken
- 📚 Responsive: 2-col desktop, 1-col mobile
- 🎯 Reference implementation: `docs/architecture/index.html` (Tier Deep Dive + Agent System)

### v4.1.2 (January 3, 2026) - D3.js Visualization Patterns
- ✨ **NEW:** Added interactive D3.js visualization patterns section
- ✨ **NEW:** Pattern A - Interactive Principle Cards (3-column grid with hover effects)
- ✨ **NEW:** Pattern B - Force-Directed Architecture Graph (node-link diagram)
- 📚 Added implementation checklists and testing requirements
- 📚 Added color palette and icon references for D3.js
- 📚 Added responsive breakpoints for visualizations
- 📚 Added accessibility requirements (keyboard nav, screen readers, WCAG 2.1 AA)
- 📚 Added pattern selection guide (when to use D3.js vs static)
- 🎯 Reference implementation: `docs/architecture/index.html`

### v4.0.2 (January 1, 2026) - Major Optimization
- 🎯 **BREAKING:** Simplified hierarchy to Level 0 → Level 1 only (removed Level 2 references)
- 🎯 **OPTIMIZATION:** Removed 177 lines of redundant spacing documentation
- ✨ **NEW:** Added Quick Reference section with decision matrices and class tables
- ✨ **NEW:** Added cross-reference to Level1-spec.md for implementation details
- 🔄 **REFACTOR:** Consolidated spacing rules into single section at top (v4.0.1 content)
- 🔄 **REFACTOR:** Simplified multi-panel pattern descriptions (removed redundancy)
- 📚 **CLARITY:** Updated Core Principle #8 (2-level → simplified hierarchy)
- 📚 **CLARITY:** Updated Core Principle #12 (added cross-document consistency)
- 📚 **CONSISTENCY:** Aligned all terminology with Level1-spec.md (Level 1 Detail Pages)
- 🐛 **FIX:** Corrected copyright year (2025 → 2026)


### v4.0.1 (January 1, 2026)
- 🎯 **NEW:** Added Core Principle #12 - Proper Spacing rule
- ✨ Enforced minimum 1.5rem (24px) vertical gap between stacked cards/panels
- 🐛 **FIX:** Resolved cramped spacing in multi-panel layouts (Security, Orchestrators, STS)
- 📚 Updated spacing requirements for grid layouts and stacked elements

### v4.0.0 (January 1, 2026)
- 🎯 **BREAKING:** Enforced 2-level maximum hierarchy (Level 0 → Level 1 → Level 2)
- 🎯 **BREAKING:** Animation Tier System v4.0.0 with strict scope enforcement
- 🎨 **NEW:** Subtle & modern animation philosophy - non-distracting by design
- 🎨 **NEW:** Clear differentiation between clickable (glow border + pointer) vs non-clickable (glass reflection + default cursor)
- ✨ Added scope for all 9 CORTEX tiles (Architecture, Security, Orchestrators, Token Optimization, STS, Best Practices, Toolkit Manager, LENS, Get Started)
- ✨ Documented 42 Level 2 pages across 9 tiles with specific D3.js/Mermaid visualizations
- ✨ Added T1 (Subtle) as universal default for ALL Level 1/2 pages
- ✨ Added T3 (Dramatic) restriction to ONLY Level 0 (Home hero)
- ✨ Pattern 1 split into Variant A (Clickable) and Variant B (Display) with distinct hover behaviors
- ✨ Updated Pattern 8-14 with consistent clickable/non-clickable styling
- ⛔ Deprecated Level 3 pages (use inline/modal instead)
- 📚 Added tile-specific visual patterns with clear interactivity indicators
- 📚 Added animation migration guide (T3→T1) for existing pages
- 📚 Updated Pattern Selection Guide with interactivity column
- 🔄 Updated view hierarchy architecture diagram
- 🔄 Removed all dramatic animations from standard page patterns

### v3.2.0 (December 31, 2025)
- ✨ Added Animation Tier System (T1/T2/T3)
- ✨ Added Layout Pattern Collection
- 📚 Updated Pattern 6 (Metrics Dashboard) with flexbox vs grid guidance
- 📚 Updated Pattern 7 (Navigation Footer) with balanced layout

### v3.1.0 (December 31, 2025)
- ✨ Added Pattern 6: Metrics Dashboard (Centered Flexbox)
- ✨ Added Pattern 7: Balanced Navigation Footer
- 📚 Documented flexbox vs grid trade-offs for centered layouts
- 📚 Added inline override examples for existing pages

### v3.0.0 (December 31, 2025)
- ✨ Added multi-layer glassmorphism system
- ✨ Added neuglass, morphing, light leak, liquid blob patterns
- ✨ Added 5 UI component patterns (modal, toast, drawer, dropdown, tooltip)
- ✨ Added micro-interactions library (ripple, tilt, glow, shimmer, magnetic)
- ✨ Added performance optimization (GPU acceleration, conditional blur, lazy loading)
- ✨ Added GlassManager and GlassPerformanceMonitor scripts
- 🔄 Changed default blur from 10px → 20px
- 🔄 Updated transitions to cubic-bezier easing
- 📚 Added pattern selection guide

### v2.3.0 (December 31, 2025)
- Added Contained Action Panel pattern
- Added Adaptive Code Panel Height Algorithm
- Added D3.js Layout Pattern Selection Guide

### v2.2.0 (Previous)
- Added STS Code Panel Height Algorithm
- Added responsive breakpoints

### v2.1.0 (Previous)
- Added FontAwesome icon standards
- Added breadcrumb navigation

### v2.0.0 (Previous)
- Initial glassmorphism design system
- Basic glass card pattern
- Mobile responsiveness

---

**Generated by:** CORTEX Optimization Engine v2.0.0  
**Standard Version:** 4.0.1  
**Last Review:** January 1, 2026  
**Next Review:** Q2 2026
