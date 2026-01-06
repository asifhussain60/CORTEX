# Panel Styling Commands - Examples & Reference

**CORTEX Glassmorphism Panel Styler**  
**Version:** 1.0 | **Created:** 2026-01-03  
**Plan:** glassmorphism-css-standardization (Phase 6)

---

## 🎨 Quick Start

The Panel Styler enables natural language styling commands using the glassmorphism named panel taxonomy.

**Import Required CSS:**
```html
<link rel="stylesheet" href="../assets/css/cortex-glass-system.css">
```

**Basic Command Structure:**
```
style X like Y
make X look like Y panel
use Y layout
apply Y to X
```

---

## 📋 Available Panel Styles (11 Total)

| Panel Name | Class | Use Case | Visual Signature |
|------------|-------|----------|------------------|
| **tetris** | `.panel-tetris` | Metrics dashboards | 6+ tiles with icon+value |
| **intro** | `.panel-intro` | Hero sections | Centered card with gradient |
| **compact-cards** | `.panel-compact-cards` | Feature highlights | 5-6 horizontal cards |
| **grid-cards** | `.panel-grid-cards` | Analysis views | 2x3/3x3 detailed grid |
| **hero-glass** | `.panel-hero-glass` | Landing pages | Full-width with strong blur |
| **sidebar-glass** | `.panel-sidebar-glass` | Navigation | Vertical sticky sidebar |
| **modal-glass** | `.panel-modal-glass` | Dialogs | Centered overlay |
| **toast-glass** | `.panel-toast-glass` | Notifications | Floating alerts (4 variants) |
| **blob-glass** | `.panel-blob-glass` | Decorations | Organic morphing shapes |
| **neon-glass** | `.panel-neon-glass` | CTAs | Glowing accent panels |
| **agent-showcase** | `.panel-agent-showcase` | Agent cards | 2x2 grid with header/tags |

---

## 💬 Command Examples

### Pattern 1: "style X like Y"
```
style dashboard like tetris
→ Apply .panel-tetris to dashboard

style hero section like intro
→ Apply .panel-intro to hero section

style metrics like tetris panel
→ Apply .panel-tetris to metrics
```

### Pattern 2: "make X look like Y"
```
make card look like intro panel
→ Apply .panel-intro to card

make sidebar look like sidebar-glass
→ Apply .panel-sidebar-glass to sidebar

make notification look like toast
→ Apply .panel-toast-glass to notification
```

### Pattern 3: "use Y panel/layout/style"
```
use grid-cards layout
→ Apply .panel-grid-cards

use tetris panel
→ Apply .panel-tetris

use neon-glass style
→ Apply .panel-neon-glass
```

### Pattern 4: "apply Y to X"
```
apply neon-glass to button
→ Apply .panel-neon-glass to button

apply hero-glass to landing section
→ Apply .panel-hero-glass to landing section

apply compact-cards to features
→ Apply .panel-compact-cards to features
```

### Pattern 5: "Y style for X"
```
tetris style for metrics
→ Apply .panel-tetris to metrics

intro style for hero
→ Apply .panel-intro to hero

grid-cards style for analysis
→ Apply .panel-grid-cards to analysis
```

---

## 🔍 Panel Details

### 1. Tetris Panel (Metrics Grid)

**Command:**
```
style dashboard like tetris
```

**HTML Example:**
```html
<div class="panel-tetris">
    <div class="panel-tetris__grid">
        <div class="panel-tetris__tile">
            <i class="panel-tetris__tile-icon fas fa-chart-line"></i>
            <div class="panel-tetris__tile-content">
                <div class="panel-tetris__tile-value">87%</div>
                <div class="panel-tetris__tile-label">Performance</div>
            </div>
        </div>
        <!-- Add 5+ more tiles -->
    </div>
</div>
```

**Use Case:** Dashboard KPIs, compact metrics, token monitoring

---

### 2. Intro Panel (Hero Card)

**Command:**
```
make hero look like intro panel
```

**HTML Example:**
```html
<div class="panel-intro">
    <h1 class="panel-intro__title">Welcome to CORTEX</h1>
    <p class="panel-intro__description">
        AI-powered development orchestration
    </p>
    <div class="panel-intro__actions">
        <button class="panel-intro__cta">Get Started</button>
    </div>
</div>
```

**Use Case:** Landing sections, feature descriptions, about cards

---

### 3. Compact Cards (Feature Row)

**Command:**
```
use compact-cards layout
```

**HTML Example:**
```html
<div class="panel-compact-cards">
    <div class="panel-compact-cards__card">
        <i class="panel-compact-cards__icon fas fa-brain"></i>
        <h3 class="panel-compact-cards__title">AI Planning</h3>
        <p class="panel-compact-cards__description">
            Autonomous plan generation
        </p>
    </div>
    <!-- Add 4-5 more cards -->
</div>
```

**Use Case:** Capability highlights, feature lists, service overviews

---

### 4. Grid Cards (Analysis View)

**Command:**
```
apply grid-cards to analysis section
```

**HTML Example:**
```html
<div class="panel-grid-cards">
    <div class="panel-grid-cards__card">
        <div class="panel-grid-cards__header">
            <i class="panel-grid-cards__icon fas fa-search"></i>
            <h3 class="panel-grid-cards__title">Code Analysis</h3>
        </div>
        <p class="panel-grid-cards__description">
            Deep AST-based intelligence
        </p>
        <div class="panel-grid-cards__badges">
            <span class="panel-grid-cards__badge">Python</span>
            <span class="panel-grid-cards__badge">TypeScript</span>
        </div>
    </div>
    <!-- Add 5+ more cards -->
</div>
```

**Use Case:** Detailed listings, analysis capabilities, tech stacks

---

### 5. Hero Glass (Full-Width Hero)

**Command:**
```
use hero-glass layout
```

**HTML Example:**
```html
<div class="panel-hero-glass">
    <div class="panel-hero-glass__content">
        <h1 class="panel-hero-glass__title">CORTEX 5.0</h1>
        <p class="panel-hero-glass__subtitle">
            The Future of AI-Assisted Development
        </p>
        <div class="panel-hero-glass__actions">
            <button class="panel-hero-glass__primary-cta">Explore</button>
            <button class="panel-hero-glass__secondary-cta">Learn More</button>
        </div>
    </div>
</div>
```

**Use Case:** Landing page heroes, product launches, announcements

---

### 6. Sidebar Glass (Navigation)

**Command:**
```
make sidebar look like sidebar-glass
```

**HTML Example:**
```html
<aside class="panel-sidebar-glass">
    <nav class="panel-sidebar-glass__nav">
        <div class="panel-sidebar-glass__section">
            <h3 class="panel-sidebar-glass__section-title">Navigation</h3>
            <ul class="panel-sidebar-glass__list">
                <li><a href="#">Dashboard</a></li>
                <li><a href="#">Projects</a></li>
            </ul>
        </div>
    </nav>
</aside>
```

**Use Case:** Vertical navigation, filters, sidebar metadata

---

### 7. Modal Glass (Dialog)

**Command:**
```
apply modal-glass to confirmation dialog
```

**HTML Example:**
```html
<div class="panel-modal-glass">
    <div class="panel-modal-glass__header">
        <h2 class="panel-modal-glass__title">Confirm Action</h2>
        <button class="panel-modal-glass__close">&times;</button>
    </div>
    <div class="panel-modal-glass__content">
        <p>Are you sure you want to proceed?</p>
    </div>
    <div class="panel-modal-glass__footer">
        <button class="panel-modal-glass__button panel-modal-glass__button--cancel">Cancel</button>
        <button class="panel-modal-glass__button panel-modal-glass__button--confirm">Confirm</button>
    </div>
</div>
```

**Use Case:** Confirmations, forms, detailed views

---

### 8. Toast Glass (Notifications)

**Command:**
```
use toast-glass for notifications
```

**HTML Example:**
```html
<div class="panel-toast-glass panel-toast-glass--success">
    <i class="panel-toast-glass__icon fas fa-check-circle"></i>
    <div class="panel-toast-glass__content">
        <div class="panel-toast-glass__title">Success!</div>
        <div class="panel-toast-glass__message">Operation completed</div>
    </div>
    <button class="panel-toast-glass__close">&times;</button>
</div>
```

**Variants:**
- `.panel-toast-glass--success` (green)
- `.panel-toast-glass--error` (red)
- `.panel-toast-glass--warning` (orange)
- `.panel-toast-glass--info` (blue)

**Use Case:** Alerts, status messages, user feedback

---

### 9. Blob Glass (Decorative)

**Command:**
```
apply blob-glass to background
```

**HTML Example:**
```html
<div class="panel-blob-glass panel-blob-glass--md">
    <!-- Decorative blob with liquid morphing animation -->
</div>
```

**Variants:**
- `.panel-blob-glass--sm` (200px)
- `.panel-blob-glass--md` (400px)
- `.panel-blob-glass--lg` (600px)

**Use Case:** Background decorations, ambient effects, visual interest

---

### 10. Neon Glass (Glowing Accent)

**Command:**
```
neon-glass style for premium card
```

**HTML Example:**
```html
<div class="panel-neon-glass">
    <div class="panel-neon-glass__content">
        <h3 class="panel-neon-glass__title">Premium Feature</h3>
        <p class="panel-neon-glass__description">
            Unlock advanced capabilities
        </p>
        <button class="panel-neon-glass__cta">Upgrade Now</button>
    </div>
</div>
```

**Use Case:** CTAs, premium cards, attention-grabbing sections

---

### 11. Agent Showcase (Agent Cards)

**Command:**
```
style agent card like agent-showcase
```

**HTML Example:**
```html
<div class="panel-agent-showcase">
    <div class="panel-agent-showcase__header">
        <i class="panel-agent-showcase__icon fas fa-robot"></i>
        <div class="panel-agent-showcase__header-content">
            <h3 class="panel-agent-showcase__title">Planning Agent</h3>
            <p class="panel-agent-showcase__subtitle">Autonomous Plan Generation</p>
        </div>
    </div>
    <div class="panel-agent-showcase__grid">
        <div class="panel-agent-showcase__capability">
            <i class="fas fa-brain"></i>
            <span>Context Analysis</span>
        </div>
        <!-- Add 3 more capabilities -->
    </div>
    <div class="panel-agent-showcase__tags">
        <span class="panel-agent-showcase__tag">AI-Powered</span>
        <span class="panel-agent-showcase__tag">Autonomous</span>
    </div>
</div>
```

**Use Case:** Agent documentation, capability showcases, AI features

---

## 🔧 Advanced Usage

### Listing All Panels
```
list panels
show available panels
what panel styles exist
```

### Fuzzy Matching
```
style X like tetris-panel
→ Automatically resolves to "tetris"

make Y look like intro-card
→ Automatically resolves to "intro"
```

### Error Handling
```
style X like unknown-panel
→ Shows "Did you mean: tetris, intro, compact-cards?"
```

---

## 📚 Resources

**Interactive Viewer:**  
`docs/design-system/panel-viewer.html`

**CSS System:**  
`docs/assets/css/cortex-glass-system.css`

**Design Tokens:**  
`docs/assets/css/glass-design-tokens.css`

**Named Panels:**  
`docs/assets/css/glass-named-panels.css`

**Plan Documentation:**  
`cortex-brain/documents/planning/active/glassmorphism-css-standardization/`

**Manifest:**  
`cortex-brain/manifests/orchestrators/panel-styling-manifest.yaml`

---

## 🎯 Use Cases by Industry

### SaaS Dashboard
```
style metrics like tetris
use compact-cards for features
apply sidebar-glass to navigation
```

### Marketing Landing Page
```
use hero-glass layout
make features look like compact-cards
apply neon-glass to CTA button
```

### Documentation Site
```
use intro for page header
apply grid-cards to content sections
make sidebar look like sidebar-glass
```

### AI Product Showcase
```
style agents like agent-showcase
use tetris for performance metrics
apply neon-glass to premium features
```

---

**Author:** Asif Hussain  
**Copyright:** © 2025-2026 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
