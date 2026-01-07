# 🎨 CORTEX Design Specification - Purpose-Driven Layouts

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** January 4, 2026  
**Copyright:** © 2026 Asif Hussain. All rights reserved.

---

## 🎯 Design Philosophy

**Core Principle:** Each page level serves a distinct purpose with **thematic consistency** but **purpose-driven variation** to avoid monotony.

**Hierarchy:**
- **Level 0 (Home)** - Portal/Gateway design
- **Level 1 (Hubs)** - Category navigation with overview
- **Level 2 (Detail)** - Deep-dive content with rich visualizations

---

## 🏠 Level 0: Home Page (`index.html`)

### Purpose
Gateway portal showcasing all 9 CORTEX capabilities.

### Design Pattern
**Multi-panel grid** (3x3 or 2-column responsive) with large clickable tiles.

### Key Features
- **9 capability tiles** with distinct icons and colors
- **Tetris-style metrics** showing system stats
- **Animated glass effects** (T3 animations allowed)
- **Hero section** with CORTEX logo and tagline

### Color Scheme
```css
--level0-primary: #00d4ff;      /* Electric blue */
--level0-accent: #7c7cff;       /* Purple */
--level0-success: #00ff88;      /* Green */
--level0-warning: #ffd700;      /* Gold */
```

### Example Structure
```html
<section class="hero-banner">
  <img src="CORTEX-logo.png" />
  <h1>CORTEX Enterprise Intelligence</h1>
</section>

<section class="capability-grid multi-panel-grid">
  <!-- 9 large tiles -->
  <div class="glass-card-clickable level0-tile">
    <i class="fas fa-brain"></i>
    <h2>Architecture</h2>
  </div>
  <!-- ... 8 more -->
</section>

<section class="tetris-metrics">
  <!-- System-wide statistics -->
</section>
```

---

## 🎯 Level 1: Hub Pages (Category Index)

### Purpose
Navigation hub for a specific category with subcategory overview.

### Design Variations by Category

#### 1. **Architecture Hub** (`architecture/index.html`)
**Layout:** Hierarchical tetris tiles (4-tier brain visualization)

```html
<section class="page-title-card">
  <h1>🧠 Architecture</h1>
  <div class="tetris-panel">
    <!-- 6 tiles: 4-Tier Brain, Tier 0, Agents, Orchestrators, Access, Graph -->
  </div>
</section>

<section class="tier-panels principle-card-grid columns-2">
  <!-- Tier 0/1 | Tier 2/3 in 2-column strict layout -->
</section>
```

**Color Scheme:**
```css
--arch-primary: #7c7cff;        /* Purple (brain) */
--arch-accent: #00d4ff;         /* Blue (connections) */
--arch-tier0: #ff6b6b;          /* Red (governance) */
--arch-tier1: #ffd700;          /* Gold (working memory) */
```

#### 2. **Security Hub** (`security/index.html`)
**Layout:** Multi-panel grid (4 categories: Protection, Assessment, Compliance, Response)

```html
<section class="page-title-card">
  <h1>🛡️ Security</h1>
  <p>13 security domains across 4 categories</p>
</section>

<section class="multi-panel-grid columns-2">
  <div class="category-panel">
    <h2>🔒 Protection</h2>
    <div class="category-links">
      <a href="skull-protection.html">SKULL Rules</a>
      <a href="access-control.html">Access Control</a>
      <!-- ... -->
    </div>
  </div>
  <!-- 3 more panels -->
</section>
```

**Color Scheme:**
```css
--security-primary: #ff6b6b;    /* Red (alert) */
--security-accent: #ffd700;     /* Gold (shield) */
--security-protect: #00ff88;    /* Green (safe) */
--security-risk: #ff9f40;       /* Orange (warning) */
```

#### 3. **Orchestrators Hub** (`orchestrators/index.html`)
**Layout:** Workflow-based tetris (5 categories: Planning, Execution, System, Analysis, Debug)

```html
<section class="page-title-card">
  <h1>🎯 Orchestrators</h1>
  <div class="tetris-panel">
    <!-- 5 workflow tiles -->
  </div>
</section>

<section class="orchestrator-showcase">
  <!-- Master Orchestrator diagram (D3 force-directed) -->
  <div class="d3-visualization"></div>
</section>

<section class="orchestrator-grid columns-3">
  <!-- 22 orchestrator cards -->
</section>
```

**Color Scheme:**
```css
--orch-primary: #00d4ff;        /* Blue (orchestration) */
--orch-planning: #7c7cff;       /* Purple (strategy) */
--orch-execution: #00ff88;      /* Green (action) */
--orch-analysis: #ffd700;       /* Gold (insight) */
```

#### 4. **Knowledge Hub** (`knowledge/index.html`)
**Layout:** Domain-based cards (17 learning hubs)

```html
<section class="page-title-card">
  <h1>📚 Knowledge</h1>
  <p>80 modules across 17 domains</p>
</section>

<section class="knowledge-grid columns-3">
  <!-- 17 domain cards with module counts -->
  <div class="glass-card-clickable">
    <i class="fas fa-code"></i>
    <h3>API Design</h3>
    <span class="module-count">8 modules</span>
  </div>
  <!-- ... -->
</section>
```

**Color Scheme:**
```css
--knowledge-primary: #ffd700;   /* Gold (wisdom) */
--knowledge-accent: #7c7cff;    /* Purple (learning) */
--knowledge-hub: #00d4ff;       /* Blue (modules) */
--knowledge-progress: #00ff88;  /* Green (completed) */
```

### Common Level 1 Features
- **Page title card** with tetris metrics or category overview
- **Navigation breadcrumbs** (Home > Category)
- **Category-specific icon** and color theme
- **1 overview diagram** (Mermaid mindmap or D3 visualization)
- **Subcategory cards/panels** with counts and descriptions
- **T1 animations** (subtle, 0.2-0.3s transitions)

---

## 📄 Level 2: Detail Pages

### Purpose
Deep-dive content with comprehensive information and rich visualizations.

### Design Variations by Content Type

#### Type A: **Conceptual Pages** (e.g., `four-tier-brain.html`)
**Layout:** Hierarchical cards with Mermaid diagrams

```html
<section class="hero-section">
  <h1>🧠 Four-Tier Brain</h1>
  <p>Intelligent memory architecture</p>
</section>

<section class="glass-card-display">
  <h2>Architecture Overview</h2>
  <div class="mermaid">
    <!-- Mindmap or flowchart -->
  </div>
</section>

<section class="tier-breakdown columns-2">
  <!-- 4 tier cards (2x2 grid) -->
  <div class="glass-card-display">
    <h3>🛡️ Tier 0: Governance</h3>
    <p>SKULL rules and brain protection</p>
  </div>
  <!-- ... -->
</section>
```

**Color Scheme:** Inherits from parent category + tier-specific accents

#### Type B: **Technical Pages** (e.g., `access-control.html`)
**Layout:** Workflow-focused with D3/Mermaid sequence diagrams

```html
<section class="hero-section">
  <h1>🔒 Access Control</h1>
</section>

<section class="glass-card-display">
  <h2>RBAC Architecture</h2>
  <div class="mermaid">
    <!-- Sequence diagram -->
  </div>
</section>

<section class="implementation-cards columns-2">
  <!-- Code examples, best practices -->
</section>

<section class="d3-visualization-container">
  <!-- Interactive D3 diagram -->
</section>
```

**Color Scheme:** Inherits from parent category + workflow colors

#### Type C: **Feature Pages** (e.g., `planning-v5.html`)
**Layout:** Phase-based with timeline visualizations

```html
<section class="hero-section">
  <h1>📋 Planning v5</h1>
  <div class="feature-badges">
    <span class="badge">10 Phases</span>
    <span class="badge">Autonomous</span>
  </div>
</section>

<section class="glass-card-display">
  <h2>Planning Pipeline</h2>
  <div class="d3-timeline"></div>
</section>

<section class="phase-cards columns-3">
  <!-- 10 phase cards -->
</section>
```

**Color Scheme:** Inherits from parent category + phase progress colors

### Common Level 2 Features
- **Hero section** with icon, title, and subtitle
- **Breadcrumb navigation** (Home > Category > Page)
- **2-4 visualizations** (mix of D3 and Mermaid based on content)
- **Card-based sections** (glass-card-display or glass-card-clickable)
- **Related pages** footer navigation
- **T1 animations only** (no dramatic effects)
- **Color variations** within parent theme

---

## 🎨 Color Theme System

### Level 0 (Home) - Vibrant Gateway
```css
.level0-tile {
  --tile-primary: var(--level0-primary);
  --tile-glow: 0 0 20px var(--tile-primary);
}
```

### Level 1 (Hubs) - Category Themes
Each hub has a distinct primary color with consistent secondary palette:

| Category | Primary | Accent | Use Case |
|----------|---------|--------|----------|
| Architecture | `#7c7cff` | `#00d4ff` | Brain, structure |
| Security | `#ff6b6b` | `#ffd700` | Protection, alerts |
| Orchestrators | `#00d4ff` | `#7c7cff` | Workflows, coordination |
| Knowledge | `#ffd700` | `#7c7cff` | Learning, wisdom |
| Features | `#00ff88` | `#00d4ff` | Capabilities, actions |
| Token Opt | `#ffd700` | `#00ff88` | Efficiency, savings |
| STS | `#7c7cff` | `#ffd700` | Best practices, quality |
| Lens | `#00d4ff` | `#ff6b6b` | Analysis, insights |
| Toolkit | `#ff9f40` | `#00d4ff` | Tools, utilities |

### Level 2 (Detail) - Subtle Variations
Inherit parent category colors with 20% lighter/darker variations:

```css
.level2-section {
  --section-bg: color-mix(in srgb, var(--category-primary) 10%, transparent);
  --section-border: color-mix(in srgb, var(--category-primary) 30%, transparent);
}
```

---

## 📐 Layout Decision Matrix

| Content Type | Layout Choice | Diagram Type | Grid Columns |
|--------------|---------------|--------------|--------------|
| **Home** | Multi-panel tiles | System overview | 3 (responsive to 2/1) |
| **Hub (4-8 items)** | Multi-panel grid | Mindmap/Force | 2 columns strict |
| **Hub (9+ items)** | Card grid | Category overview | 3 columns |
| **Detail (Conceptual)** | Hierarchical cards | Mindmap/Tree | 2 columns |
| **Detail (Technical)** | Workflow cards | Sequence/Sankey | 2 columns |
| **Detail (Process)** | Phase cards | Timeline/Flowchart | 3 columns |

---

## 🚀 Implementation Priority

### Phase 1: Level 1 Hubs (High Priority)
1. Architecture hub → Tetris + tier panels
2. Security hub → Multi-panel (4 categories)
3. Orchestrators hub → Workflow tetris + force diagram
4. Knowledge hub → Domain cards grid

### Phase 2: High-Value Level 2 Pages (Medium Priority)
Based on value scoring (score ≥50):
- `planning-v5.html` → Timeline + phase cards
- `ado-v2.html` → Workflow + sequence diagrams
- `four-tier-brain.html` → Mindmap + tier breakdown
- `access-control.html` → RBAC diagram + implementation

### Phase 3: Remaining Level 2 Pages (Low Priority)
Batch process with template-based generation.

---

## ✅ Compliance Checklist

Every page MUST include:
- ✅ **Glassmorphism classes** (glass-card-clickable/display)
- ✅ **Font Awesome 6.x icons** with style prefix (fas/far/fab)
- ✅ **Zero inline styles** (use CSS classes)
- ✅ **Breadcrumb navigation** (except Home)
- ✅ **Mobile-responsive** (375px-1440px)
- ✅ **WCAG 2.1 AA** accessibility
- ✅ **T1 animations** for Level 1/2 (T3 for Level 0 only)
- ✅ **Category-appropriate colors** from theme system

---

**Next Step:** Run `python cortex-toolkit/page-refresh-tool.py` to identify pages needing updates, then selectively apply purpose-driven designs based on this specification.
