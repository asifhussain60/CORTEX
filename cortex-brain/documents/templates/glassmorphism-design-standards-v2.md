# CORTEX Glassmorphism Design Standards v2.0

**Version:** 2.0.0  
**Created:** December 28, 2025  
**Author:** Asif Hussain  
**Purpose:** Unified glassmorphism design system for all CORTEX documentation views  
**Supersedes:** `documentation-styling-standards.md` v1.1.0

---

## 🎯 Overview

This document establishes the definitive glassmorphism design standard for CORTEX documentation based on successful implementations in:
- ✅ **STS Showcase** (`/sts/index.html`, `/sts/security.html`) - Category navigation, code comparison
- ✅ **Orchestrator Index** (`/orchestrators/index.html`) - Interactive D3.js visualizations, breadcrumb navigation
- ✅ **Planning System** (`/orchestrators/planning-system.html`) - Feature documentation

**Key Precedence:** This document takes precedence over `documentation-styling-standards.md` for layout patterns, breadcrumb styling, and navigation standards.

### Core Design Principles

1. **Mobile-First Responsive:** All views MUST be fully responsive (320px to 1920px+)
2. **Touch-Friendly:** Interactive elements ≥44px for mobile accessibility
3. **Performance:** Optimized for fast loading on mobile networks
4. **Readability:** Text remains legible across all device sizes
5. **Glassmorphism:** Consistent blur and transparency effects
6. **Accessibility:** WCAG 2.1 AA compliant color contrast and navigation
7. **Icons:** Use FontAwesome icons instead of emojis for better browser compatibility

---

## 🎨 Icon Standards

### FontAwesome vs Emoji

**ALWAYS use FontAwesome icons** in production views for:
- ✅ **Universal browser support** (works in all browsers, all versions)
- ✅ **Consistent rendering** (same appearance across platforms)
- ✅ **Accessibility** (screen reader friendly with `aria-hidden="true"`)
- ✅ **Customization** (size, color, styling via CSS)
- ✅ **Professional appearance** (clean, crisp vector graphics)

**AVOID emojis** because:
- ❌ **Inconsistent rendering** (different on Windows/Mac/Linux/iOS/Android)
- ❌ **Font dependency** (missing glyphs if font doesn't support Unicode version)
- ❌ **Poor accessibility** (screen readers may not interpret correctly)
- ❌ **Limited styling** (can't change color or size reliably)

### FontAwesome Implementation

**Required CDN Link:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

**Usage in HTML:**
```html
<!-- Heading with icon -->
<h1><i class="fas fa-tools"></i> Sharpen The Saw</h1>

<!-- Button with icon -->
<button><i class="fas fa-download"></i> Download</button>

<!-- Navigation link -->
<a href="index.html"><i class="fas fa-home"></i> Home</a>

<!-- Icon with screen reader label -->
<i class="fas fa-check" aria-hidden="true"></i>
<span class="sr-only">Success</span>
```

### Common Icon Mappings

**Replace emojis with these FontAwesome equivalents:**

| Purpose | Emoji | FontAwesome Class | Icon |
|---------|-------|-------------------|------|
| **Tools/Build** | 🔧 🛠️ | `fa-tools` | <i class="fas fa-tools"></i> |
| **Security** | 🔒 🛡️ | `fa-shield-alt`, `fa-lock` | <i class="fas fa-shield-alt"></i> |
| **Architecture** | 📐 🏗️ | `fa-drafting-compass`, `fa-sitemap` | <i class="fas fa-drafting-compass"></i> |
| **Code Quality** | ✨ 💎 | `fa-gem`, `fa-code` | <i class="fas fa-gem"></i> |
| **Performance** | ⚡ 🚀 | `fa-tachometer-alt`, `fa-bolt` | <i class="fas fa-tachometer-alt"></i> |
| **Testing** | 🧪 ✅ | `fa-vial`, `fa-check-circle` | <i class="fas fa-vial"></i> |
| **Documentation** | 📖 📚 | `fa-book-open`, `fa-file-alt` | <i class="fas fa-book-open"></i> |
| **Home** | 🏠 | `fa-home` | <i class="fas fa-home"></i> |
| **Settings** | ⚙️ | `fa-cog` | <i class="fas fa-cog"></i> |
| **Success** | ✅ | `fa-check-circle` | <i class="fas fa-check-circle"></i> |
| **Error** | ❌ | `fa-times-circle` | <i class="fas fa-times-circle"></i> |
| **Warning** | ⚠️ | `fa-exclamation-triangle` | <i class="fas fa-exclamation-triangle"></i> |
| **Info** | ℹ️ | `fa-info-circle` | <i class="fas fa-info-circle"></i> |

### Icon Styling Standards

**CSS for icons in headings:**
```css
h1 i, h2 i, h3 i {
    color: var(--accent-primary); /* Cyan */
    margin-right: 0.5rem;
    font-size: 1em; /* Match heading size */
}

h1 i {
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5); /* Glow effect */
}
```

**Icon sizing:**
```html
<!-- Small icon -->
<i class="fas fa-check" style="font-size: 0.875rem;"></i>

<!-- Normal icon (default) -->
<i class="fas fa-check"></i>

<!-- Large icon -->
<i class="fas fa-check" style="font-size: 1.5rem;"></i>

<!-- Extra large icon -->
<i class="fas fa-check" style="font-size: 2rem;"></i>
```

**Accessibility:**
```html
<!-- Decorative icon (hide from screen readers) -->
<i class="fas fa-star" aria-hidden="true"></i>

<!-- Meaningful icon (include label) -->
<button aria-label="Close dialog">
    <i class="fas fa-times" aria-hidden="true"></i>
</button>
```

---

## 📐 Design System Architecture

### CSS File Structure (MANDATORY)

**Single Source of Truth:**
```
docs/
├── assets/
│   └── css/
│       ├── main.css           ← Primary glassmorphism theme (ALL pages)
│       └── sts.css            ← STS-specific enhancements (STS pages only)
```

**Usage Rules:**
- ✅ **ALL pages MUST link:** `<link rel="stylesheet" href="../assets/css/main.css">`
- ✅ **STS pages additionally link:** `<link rel="stylesheet" href="../assets/css/sts.css">`
- ✅ **REQUIRED meta tag:** `<meta name="viewport" content="width=device-width, initial-scale=1.0">` (mobile responsiveness)
- ❌ **FORBIDDEN:** Inline `style=""` attributes (except story button preservation)
- ❌ **FORBIDDEN:** Page-specific `<style>` tags (except D3.js positioning)
- ❌ **FORBIDDEN:** Alternate CSS files in subdirectories
- ❌ **FORBIDDEN:** Fixed pixel widths that break mobile layout

### CSS Class Verification (MANDATORY)

**Critical Rule:** Before adding any CSS class to HTML, CORTEX MUST verify the class exists in the corresponding CSS file.

**Decision Tree Workflow:**

```
START: Need to add CSS class to HTML
    |
    ├─→ Is it a standard class? (glass-card, section, container)
    |    └─→ ✅ YES: Use directly (pre-verified in main.css)
    |
    ├─→ Is it a grid class? (metrics-grid-*, feature-grid-*)
    |    └─→ Go to GRID VERIFICATION flowchart (see Grid System section)
    |
    └─→ Is it a custom/specific class?
         |
         ├─→ STEP 1: Identify target CSS file
         |    • Standard pages → docs/assets/css/main.css
         |    • STS pages → Check BOTH main.css AND sts.css
         |
         ├─→ STEP 2: Execute verification
         |    • Use grep_search with pattern: `.{class-name}`
         |    • Example: grep_search('.metrics-grid-2', 'docs/assets/css/main.css')
         |
         ├─→ STEP 3: Evaluate results
         |    |
         |    ├─→ CLASS FOUND with complete definition?
         |    |    └─→ ✅ Proceed with implementation
         |    |
         |    └─→ CLASS NOT FOUND?
         |         |
         |         ├─→ OPTION A: Add to CSS (preferred)
         |         |    • Add complete definition with properties
         |         |    • Include responsive breakpoints
         |         |    • Document in response to user
         |         |
         |         ├─→ OPTION B: Use existing alternative
         |         |    • Find similar class in CSS
         |         |    • Verify it meets requirements
         |         |    • Document substitution
         |         |
         |         └─→ OPTION C: Refactor approach
         |              • Reconsider if class is needed
         |              • Use inline positioning sparingly
         |              • Document rationale
         |
         └─→ STEP 4: Document action
              • Note in response what was verified/added/changed
              • Explain why specific class was chosen
```

**Pre-Verified Standard Classes (Safe to Use):**

| Category | Classes | Verification Status |
|----------|---------|--------------------|
| **Containers** | `.glass-card`, `.container`, `.section` | ✅ Verified in main.css |
| **Navigation** | `.breadcrumb`, `.logo-header`, `.nav-container` | ✅ Verified in main.css |
| **Cards** | `.metric-card`, `.feature-card`, `.concept-card` | ✅ Verified in main.css |
| **Typography** | `.section-title`, `.hero-subtitle` | ✅ Verified in main.css |
| **STS Specific** | `.sts-main`, `.comparison-section` | ✅ Verified in sts.css |

**Common Classes Requiring Verification:**

| Class Pattern | Where to Check | Common Issue |
|---------------|----------------|-------------|
| `metrics-grid-*` | main.css line ~2088 | Wrong number (2 vs 3) |
| `feature-grid-*` | main.css line ~2155 | Gap size mismatch |
| `.viz-btn-*` | main.css + D3.js section | Category-specific styles |
| Custom modifiers | Grep entire file | May not exist |

**Verification Command Examples:**
```bash
# Example 1: Check grid class
grep_search('.metrics-grid-2', 'docs/assets/css/main.css')

# Example 2: Check all grid variants
grep_search('metrics-grid-', 'docs/assets/css/main.css')

# Example 3: Check STS-specific class
grep_search('.comparison-section', 'docs/assets/css/sts.css')
```

**Consequences of Skipping Verification:**

| Issue | Symptom | Impact |
|-------|---------|--------|
| **Layout breaks** | Elements stack instead of grid | Poor visual hierarchy |
| **Missing styles** | No hover effects, wrong colors | Unprofessional appearance |
| **Inconsistent behavior** | Works on one page, breaks on another | User confusion |
| **Mobile failure** | Horizontal scroll, overlapping elements | Unusable on mobile |

---

## 🎨 Core Color Palette

### CSS Variables (from `main.css`)

```css
:root {
    /* Background Colors */
    --bg-primary: #0a0e27;          /* Dark navy blue */
    --bg-secondary: #1a1f3a;        /* Medium navy blue */
    --glass-bg: rgba(26, 31, 58, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Accent Colors */
    --accent-primary: #00d4ff;      /* CORTEX cyan */
    --accent-secondary: #7b61ff;    /* Purple */
    
    /* Text Colors */
    --text-primary: #ffffff;        /* White */
    --text-secondary: #a0a6c0;      /* Light gray */
    --text-muted: #6b7280;          /* Medium gray */
    
    /* Status Colors */
    --success: #00ff88;             /* Green */
    --warning: #ffa500;             /* Orange */
    --danger: #ff4444;              /* Red */
    --info: #3b82f6;                /* Blue */
    
    /* Effects */
    --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    --shadow-lg: 0 20px 60px 0 rgba(0, 0, 0, 0.5);
    --glow: 0 0 20px rgba(0, 212, 255, 0.3);
}
```

### Background Gradient (Universal)

**ALL pages MUST use this background:**
```css
body {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    background-attachment: fixed;
}
```

**Rationale:** Fixed gradient ensures consistency across scrolling and all pages.

### Responsive Body Settings

**MANDATORY for all pages:**
```css
body {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    background-attachment: fixed;
    margin: 0;
    padding: 0;
    min-height: 100vh;
    overflow-x: hidden; /* Prevent horizontal scroll on mobile */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

* {
    box-sizing: border-box; /* Consistent sizing across all elements */
}
```

**Rationale:**
- `overflow-x: hidden` prevents mobile horizontal scroll issues
- `box-sizing: border-box` ensures padding/borders don't break layouts
- Font smoothing improves text rendering on all devices

---

## 🧭 Navigation Standards

### Breadcrumb Navigation (TOP BAR - MANDATORY)

**Purpose:** Every page (except home) MUST have breadcrumb navigation at the top.

**HTML Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title | CORTEX</title>
    <link rel="stylesheet" href="../assets/css/main.css">
</head>
<body>
    <!-- Breadcrumb Navigation (ALWAYS FIRST) -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <a href="index.html">Section</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">Current Page</span>
    </nav>
    
    <!-- Logo Header (ALWAYS SECOND) -->
    <div class="logo-header">
        <a href="../index.html">
            <img src="../assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="page-logo">
        </a>
    </div>
    
    <!-- Main Content -->
    <main class="container">
        <!-- Content here -->
    </main>
</body>
</html>
```

**CSS (from `main.css` - already defined):**
```css
.breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--glass-border);
    font-size: 0.875rem;
    flex-wrap: wrap; /* Wrap on narrow screens */
}

.breadcrumb a {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color var(--transition-base);
    min-height: 44px; /* Touch-friendly target */
    display: inline-flex;
    align-items: center;
}

.breadcrumb a:hover {
    color: var(--accent-primary);
}

.breadcrumb-separator {
    color: var(--text-muted);
    user-select: none;
}

.breadcrumb-current {
    color: var(--text-primary);
    font-weight: 600;
}

/* Mobile optimization */
@media (max-width: 480px) {
    .breadcrumb {
        padding: 0.75rem 1rem;
        font-size: 0.8125rem; /* 13px for mobile */
        gap: 0.375rem;
    }
}
```

**Visual Design:**
- **Background:** Glassmorphic with blur effect (`var(--glass-bg)`)
- **Separator:** Right arrow (`→`) in muted gray
- **Hover State:** Links turn cyan (`var(--accent-primary)`)
- **Current Page:** White text, bold weight

**Examples:**
```html
<!-- Orchestrator page -->
<nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">→</span>
    <span class="breadcrumb-current">Orchestrators</span>
</nav>

<!-- Planning System page -->
<nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">→</span>
    <a href="index.html">Orchestrators</a>
    <span class="breadcrumb-separator">→</span>
    <span class="breadcrumb-current">Planning System</span>
</nav>

<!-- STS Security page -->
<nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">→</span>
    <a href="index.html">STS</a>
    <span class="breadcrumb-separator">→</span>
    <span class="breadcrumb-current">Security</span>
</nav>
```

### Alternative Header Style (STS Pages)

**When to Use:** STS showcase pages use a branded navigation header instead of breadcrumbs + logo.

**HTML Structure:**
```html
<body class="sts-showcase">
    <!-- Branded Navigation Header -->
    <header class="site-header">
        <nav class="nav-container">
            <a href="../index.html" class="nav-brand">
                <i class="fas fa-brain"></i> CORTEX 4.0
            </a>
            <div class="nav-links">
                <a href="index.html"><i class="fas fa-bullseye"></i> STS Hub</a>
                <a href="../documentation.html"><i class="fas fa-book"></i> Docs</a>
            </div>
        </nav>
    </header>
    
    <main class="sts-main">
        <!-- Content here -->
    </main>
</body>
```

**CSS (add to `main.css` if not present):**
```css
.site-header {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--glass-border);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem; /* Spacing for mobile wrap */
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-primary);
    text-decoration: none;
    font-size: 1.25rem;
    font-weight: 700;
    transition: color var(--transition-base);
    min-height: 44px; /* Touch target */
}

.nav-brand:hover {
    color: var(--accent-primary);
}

.nav-brand i {
    color: var(--accent-primary);
    font-size: 1.5rem;
}

.nav-links {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap; /* Stack on mobile if needed */
}

.nav-links a {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.875rem;
    transition: color var(--transition-base);
    min-height: 44px; /* Touch target */
    padding: 0.5rem;
}

.nav-links a:hover {
    color: var(--accent-primary);
}

.nav-links a i {
    font-size: 1rem;
}

/* Mobile optimization */
@media (max-width: 768px) {
    .nav-container {
        padding: 0 1rem;
    }
    
    .nav-brand {
        font-size: 1.125rem;
    }
    
    .nav-links {
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .nav-links a {
        font-size: 0.8125rem;
        padding: 0.375rem;
    }
}
```

**Usage Guidelines:**
- **Standard Pages:** Use breadcrumb + logo pattern (orchestrators, features, architecture)
- **Showcase Pages:** Use site-header pattern (STS, stories, demos)
- **Home Page:** No breadcrumb or site-header (hero section only)

---

## 📏 Logo Standards

### Page Logo (Below Breadcrumb)

**Desktop:**
```css
.logo-header {
    display: flex;
    justify-content: center;
    padding: 2rem 0;
}

.page-logo {
    width: 300px;
    height: auto;
    filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
    transition: filter var(--transition-base);
}

.page-logo:hover {
    filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.8));
}
```

**Mobile (max-width: 768px):**
```css
@media (max-width: 768px) {
    .page-logo {
        width: 200px;
    }
}
```

**Logo Display Rules by Page Level:**

| Page Level | Breadcrumb Path | Logo Display | Example |
|------------|-----------------|--------------|---------|
| **First Level** | `Home → Section` | ✅ SHOW LOGO | `/orchestrators/index.html` |
| **Second Level** | `Home → Section → Page` | ❌ NO LOGO | `/orchestrators/planning-system.html` |
| **Third Level** | `Home → Section → Page → Detail` | ❌ NO LOGO | `/sts/security.html` |
| **Home** | No breadcrumb | ✅ SHOW LOGO | `/index.html` |

**Guidelines:**
- Logo appears BELOW breadcrumb (if breadcrumb exists)
- Logo ONLY on home page and first-level section index pages
- Second and third level pages use breadcrumb navigation ONLY
- Always centered when shown
- Always includes cyan glow effect
- Scales to 200px on mobile

**Examples:**

✅ **Show Logo (First Level):**
```html
<!-- /orchestrators/index.html -->
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">→</span>
    <span class="breadcrumb-current">Orchestrators</span>
</nav>
<div class="logo-header">
    <a href="../index.html">
        <img src="../assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="page-logo">
    </a>
</div>
```

❌ **No Logo (Second Level):**
```html
<!-- /orchestrators/planning-system.html -->
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">→</span>
    <a href="index.html">Orchestrators</a>
    <span class="breadcrumb-separator">→</span>
    <span class="breadcrumb-current">Planning System</span>
</nav>
<!-- NO logo-header div here -->
<main class="container">
    <!-- Content starts directly -->
</main>
```

❌ **No Logo (Third Level):**
```html
<!-- /sts/security.html -->
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">→</span>
    <a href="index.html">STS</a>
    <span class="breadcrumb-separator">→</span>
    <span class="breadcrumb-current">Security</span>
</nav>
<!-- NO logo-header div here -->
<main class="sts-main">
    <!-- Content starts directly -->
</main>
```

---

## 📚 Knowledge Library Design Standards

### Content Strategy (Drill-Down Views)

**Purpose:** Knowledge Library pages should be educational and scannable, not code repositories.

**Content Hierarchy:**

| View Type | Code Display | Primary Focus | Visual Aids |
|-----------|--------------|---------------|-------------|
| **Overview** | ❌ No code | Concepts, definitions | Icons, diagrams, infographics |
| **Concept Detail** | ✅ Short snippets (5-10 lines) | Explanation, use cases | Flowcharts, architecture diagrams |
| **Implementation** | ✅ Pseudocode preferred | Logic flow, patterns | Sequence diagrams, state machines |
| **Reference** | ✅ Code snippets with annotations | Key examples only | Annotated code blocks |

### Code Display Rules

**❌ AVOID:**
- Full class implementations (>20 lines)
- Complete function dumps
- Raw code blocks without context
- Multiple consecutive code blocks

**✅ PREFER:**
```html
<!-- Pseudocode with visual clarity -->
<div class="pseudocode-block">
    <h4>Algorithm: Binary Search</h4>
    <pre class="pseudocode">
<span class="keyword">function</span> binarySearch(array, target):
    left ← 0
    right ← array.length - 1
    
    <span class="keyword">while</span> left ≤ right:
        mid ← (left + right) / 2
        
        <span class="keyword">if</span> array[mid] = target:
            <span class="keyword">return</span> mid
        <span class="keyword">else if</span> array[mid] < target:
            left ← mid + 1
        <span class="keyword">else</span>:
            right ← mid - 1
    
    <span class="keyword">return</span> NOT_FOUND
    </pre>
</div>

<!-- Annotated snippet (max 10 lines) -->
<div class="code-snippet">
    <div class="snippet-header">
        <span class="language-badge">Python</span>
        <span class="snippet-title">Factory Pattern Example</span>
    </div>
    <pre><code class="language-python"><span class="comment"># Factory creates objects without specifying exact class</span>
class ShapeFactory:
    def create_shape(self, shape_type):
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
    </code></pre>
    <div class="snippet-annotation">
        <i class="fas fa-lightbulb"></i> Factory encapsulates object creation logic
    </div>
</div>
```

### Visual Diagram Integration

**MANDATORY:** Every technical concept MUST have a visual aid.

**Diagram Types by Content:**

| Content Type | Recommended Diagram | Tool/Format |
|--------------|---------------------|-------------|
| Architecture | System diagram | Mermaid, D3.js |
| Process Flow | Flowchart | Mermaid flowchart |
| Data Flow | Pipeline diagram | Mermaid sequence |
| Relationships | Entity diagram | Mermaid ERD |
| State Management | State machine | Mermaid state |
| API Interactions | Sequence diagram | Mermaid sequence |
| Technology Landscape | Hierarchical graph | Mermaid graph TB |
| Circuit Breaker States | State diagram | Mermaid stateDiagram-v2 |

---

#### 📐 Diagram Layout & Orientation Rules

**Critical Design Decision:** Choose diagram orientation based on **node count and content complexity**, NOT visual preference.

| Node Count | Primary Layout | Secondary Layout | Rationale |
|------------|---------------|------------------|-----------|
| **≤ 6 nodes** | `graph TB` (top-bottom) | `graph LR` (left-right) | Compact, fits screen width |
| **7-12 nodes** | `graph LR` (left-right) | `graph TD` (top-down) | Better readability, prevents cramping |
| **13+ nodes** | Hierarchical D3.js | `graph LR` with subgraphs | Mermaid struggles at scale |

**Visual Clarity Assessment:**

✅ **Use Vertical (LR) When:**
- Node labels are longer than 20 characters
- 3+ levels of hierarchy present
- Diagram width would exceed 800px horizontally
- Mobile responsiveness is critical
- Multiple branches from single node (e.g., API Design with 3 main branches)

❌ **Avoid Horizontal (TB) When:**
- Complex labels get truncated
- Nodes overlap or compress visually
- Touch targets become too small on mobile (< 44px)

**Layout Syntax:**
```
graph LR    → Left-to-Right (vertical flow)
graph TB    → Top-to-Bottom (horizontal spread)
graph TD    → Top-Down (same as TB)
graph RL    → Right-to-Left (rare, RTL languages)
```

---

#### 🎨 Enhanced Diagram Styling Standards

**Container Styling (MANDATORY):**
```html
<!-- Enhanced container with dark backdrop for visual emphasis -->
<div style="background: rgba(0, 0, 0, 0.3); padding: 2rem; border-radius: 12px; margin: 1.5rem 0; overflow-x: auto; text-align: center;">
    <div class="mermaid">
        <!-- Diagram code here -->
    </div>
</div>
```

**Styling Property Breakdown:**

| Property | Value | Purpose | Visual Impact |
|----------|-------|---------|---------------|
| `background` | `rgba(0, 0, 0, 0.3)` | Dark backdrop | Separates diagram from page, improves contrast |
| `padding` | `2rem` (32px) | Breathing room | Prevents diagram from touching edges |
| `border-radius` | `12px` | Rounded corners | Matches glassmorphism aesthetic |
| `margin` | `1.5rem 0` (24px vertical) | Vertical spacing | Separates from surrounding content |
| `overflow-x` | `auto` | Horizontal scroll | Allows wide diagrams to scroll on mobile |
| **`text-align`** | **`center`** | **Diagram alignment** | **CRITICAL: Centers SVG (Mermaid renders inline)** |

**Centering Behavior Explained:**

```
WITHOUT text-align: center          WITH text-align: center
┌────────────────────────────┐      ┌────────────────────────────┐
│ ┌─────────────┐            │      │       ┌─────────────┐      │
│ │  Diagram    │            │      │       │  Diagram    │      │
│ │   (Left)    │            │      │       │ (Centered)  │      │
│ └─────────────┘            │      │       └─────────────┘      │
└────────────────────────────┘      └────────────────────────────┘
     ❌ Left-justified                    ✅ Centered
  (Poor visual hierarchy)          (Professional appearance)
```

**Why Centering Matters:**
1. **Mermaid renders inline:** SVG output respects `text-align` property
2. **Visual balance:** Centered diagrams feel intentional, not accidental
3. **Scannability:** Eyes naturally center-focus on diagrams
4. **Consistency:** All CORTEX diagrams use centered alignment
5. **Mobile UX:** Centered diagrams scroll evenly on small screens

**Diagram Alignment Rules:**
- ✅ **ALWAYS center diagrams** using `text-align: center` on container
- ✅ Mermaid SVGs render inline and respect text-align property
- ❌ **NEVER left-justify diagrams** (creates visual imbalance)
- ✅ Centered diagrams improve visual hierarchy and scannability

**Node Styling (Color + Stroke):**
```
style NodeID fill:#7b61ff,stroke:#9f87ff,stroke-width:3px,color:#fff
```

**Color Palette by Purpose:**

| Purpose | Fill Color | Stroke Color | Text Color | Use Case |
|---------|-----------|--------------|------------|----------|
| **Primary/Root** | `#7b61ff` | `#9f87ff` | `#fff` | Main entry point |
| **Category 1** | `#10b981` (green) | `#34d399` | `#fff` | Success, REST, GET |
| **Category 2** | `#3b82f6` (blue) | `#60a5fa` | `#fff` | Info, GraphQL, POST |
| **Category 3** | `#f59e0b` (orange) | `#fbbf24` | `#fff` | Warning, versioning |
| **Danger/Critical** | `#ef4444` (red) | `#f87171` | `#fff` | Errors, deletion |
| **Subcategory Dark** | `#064e3b` (dark green) | N/A | `#fff` | Child nodes for green category |
| **Subcategory Dark** | `#1e3a8a` (dark blue) | N/A | `#fff` | Child nodes for blue category |
| **Subcategory Dark** | `#78350f` (dark orange) | N/A | `#fff` | Child nodes for orange category |

**Stroke Width Guidelines:**
- **Primary nodes:** `stroke-width: 3px` (emphasize hierarchy)
- **Secondary nodes:** `stroke-width: 2px` (clear but not dominant)
- **Leaf nodes:** No stroke override (use default)

---

#### 🔤 Node Label Best Practices

**Multi-Line Labels (Vertical Orientation):**
```
A["[API] API Design<br/>Core Architecture"]
B["[REST] REST APIs<br/>Resource-Based"]
C["[GQL] GraphQL APIs<br/>Query Language"]
```

**Note:** In Mermaid diagrams, use **text-based icons in brackets** like `[API]`, `[REST]`, `[DB]` instead of emojis for consistency across browsers.

**Structure:**
1. **Icon Label** → Text identifier in brackets (e.g., `[API]`, `[SEC]`, `[DB]`)
2. **Primary Label** → Core concept (bold in mental model)
3. **Line Break** (`<br/>`) → Separator
4. **Subtitle/Context** → Additional detail (lighter weight)

**Character Limits:**
- **Primary label:** 2-4 words (max 30 characters)
- **Subtitle:** 1-3 words (max 25 characters)
- **Total node height:** Max 3 lines (prevents vertical expansion)

**Small Text Annotations:**
```
A["[INFO] Phase 1<br/>Announce Deprecation<br/><small>Public notification</small>"]
```

Use `<small>` tag for tertiary details (timestamps, counts, hints).

---

#### 🔗 D3.js vs Mermaid Decision Matrix

| Criteria | Use Mermaid | Use D3.js |
|----------|-------------|-----------|
| **Node count** | ≤ 12 nodes | 13+ nodes |
| **Interactivity** | Static view | Zoom, pan, click events |
| **Complexity** | Linear/tree hierarchies | Complex networks, force layouts |
| **Dev effort** | Low (declarative syntax) | High (custom JavaScript) |
| **Performance** | Fast render | Optimized for large graphs |
| **Accessibility** | SVG with text fallback | Requires ARIA implementation |
| **Mobile support** | Excellent (responsive SVG) | Requires touch event handling |

**When to Choose D3.js:**
1. **Interactive dashboards** (Orchestrator Index - force-directed layout)
2. **Drill-down navigation** (Click nodes to expand details)
3. **Real-time data visualization** (Animated updates)
4. **Complex relationships** (Many-to-many, cyclical dependencies)

**When to Choose Mermaid:**
1. **Documentation** (Knowledge library, concept explanations)
2. **Static architecture diagrams** (System overviews)
3. **Simple flows** (Process steps, state machines)
4. **Rapid prototyping** (Fast iteration without custom code)

**Best of Both Worlds:**
- Use **Mermaid** for initial design/documentation
- Upgrade to **D3.js** when interactivity adds significant value
- Maintain both versions if users need static exports (PDF/print)

---

#### 📱 Mobile Responsiveness for Diagrams

**Container Responsive Wrapper:**
```html
<div class="diagram-responsive-wrapper">
    <div style="background: rgba(0, 0, 0, 0.3); padding: 2rem; border-radius: 12px; margin: 1.5rem 0; overflow-x: auto;">
        <div class="mermaid">
            <!-- Diagram -->
        </div>
    </div>
    <p class="diagram-mobile-hint" style="font-size: 0.875rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">
        <i class="fas fa-hand-pointer"></i> Swipe horizontally to view full diagram on mobile
    </p>
</div>
```

**CSS Enhancements:**
```css
@media (max-width: 768px) {
    .mermaid svg {
        max-width: 200%; /* Allow diagram to be wider than viewport */
        height: auto;
    }
    
    .diagram-mobile-hint {
        display: block;
    }
}

@media (min-width: 769px) {
    .diagram-mobile-hint {
        display: none; /* Hide hint on desktop */
    }
}
```

---

#### ✅ Diagram Implementation Checklist

Before committing any diagram to production, verify:

- [ ] **Orientation**: Chosen based on node count matrix (≤6 TB, 7-12 LR, 13+ D3.js)
- [ ] **Container**: Dark backdrop with padding (`rgba(0, 0, 0, 0.3)`, `2rem`)
- [ ] **Alignment**: Diagram centered with `text-align: center` on container
- [ ] **Styling**: Primary nodes have stroke emphasis (`stroke-width: 3px`)
- [ ] **Labels**: Multi-line with icons, max 3 lines per node
- [ ] **Colors**: Follow purpose-based palette (primary purple, categories RGB)
- [ ] **Mobile**: Horizontal scroll enabled (`overflow-x: auto`)
- [ ] **Spacing**: 1.5rem vertical margin from surrounding content
- [ ] **Accessibility**: SVG rendered (Mermaid default) or ARIA labels (D3.js)

---

**Example: Complete Enhanced Diagram**
```html
<h3>API Design Landscape</h3>
<div style="background: rgba(0, 0, 0, 0.3); padding: 2rem; border-radius: 12px; margin: 1.5rem 0; overflow-x: auto; text-align: center;">
    <div class="mermaid">
graph LR
    A["🎯 API Design<br/>Core Architecture"]
    
    A --> B["🔷 REST APIs<br/>Resource-Based"]
    A --> C["💎 GraphQL APIs<br/>Query Language"]
    A --> D["🔄 API Versioning<br/>Evolution Strategy"]
    
    B --> B1["📦 Resource Naming"]
    B --> B2["⚡ HTTP Methods"]
    B --> B3["✅ Status Codes"]
    B --> B4["📄 Pagination"]
    
    C --> C1["📐 Schema Design"]
    C --> C2["🔍 Query Patterns"]
    C --> C3["✏️ Mutation Patterns"]
    C --> C4["🔄 DataLoader"]
    
    D --> D1["🔗 URI Versioning"]
    D --> D2["📝 Header Versioning"]
    D --> D3["⚠️ Deprecation"]
    D --> D4["🚀 Migration"]
    
    style A fill:#7b61ff,stroke:#9f87ff,stroke-width:3px,color:#fff
    style B fill:#10b981,stroke:#34d399,stroke-width:2px,color:#fff
    style C fill:#3b82f6,stroke:#60a5fa,stroke-width:2px,color:#fff
    style D fill:#f59e0b,stroke:#fbbf24,stroke-width:2px,color:#fff
    
    style B1 fill:#064e3b,color:#fff
    style B2 fill:#064e3b,color:#fff
    style B3 fill:#064e3b,color:#fff
    style B4 fill:#064e3b,color:#fff
    
    style C1 fill:#1e3a8a,color:#fff
    style C2 fill:#1e3a8a,color:#fff
    style C3 fill:#1e3a8a,color:#fff
    style C4 fill:#1e3a8a,color:#fff
    
    style D1 fill:#78350f,color:#fff
    style D2 fill:#78350f,color:#fff
    style D3 fill:#78350f,color:#fff
    style D4 fill:#78350f,color:#fff
    </div>
</div>
```

**Visual Result:**
- ✅ Vertical layout prevents horizontal cramping
- ✅ Dark backdrop emphasizes diagram against page background
- ✅ **Diagram centered within container (not left-justified)**
- ✅ Enhanced stroke widths create visual hierarchy
- ✅ Multi-line labels with icons improve scannability
- ✅ Color-coded categories with dark child nodes
- ✅ Mobile-friendly with horizontal scroll support

---

**Legacy Mermaid Container (DEPRECATED):**
```html
<!-- ❌ OLD: No container styling, poor mobile support -->
<div class="mermaid">
graph TB
    A[API Design]
    A --> B[REST APIs]
    <!-- ... -->
</div>
```

Replace all instances with enhanced container pattern shown above.

### Text Formatting Standards

**Typography Hierarchy:**

```css
/* Knowledge Library specific */
.knowledge-content {
    max-width: 900px;  /* Optimal reading width */
    margin: 0 auto;
    padding: 3rem 2rem;
}

.knowledge-content h1 {
    font-size: 2.25rem;
    line-height: 1.2;
    margin-bottom: 1.5rem;
    letter-spacing: -0.02em;
}

.knowledge-content h2 {
    font-size: 1.75rem;
    line-height: 1.3;
    margin-top: 3rem;
    margin-bottom: 1.25rem;
    padding-top: 2rem;
    border-top: 1px solid var(--glass-border);
}

.knowledge-content h3 {
    font-size: 1.375rem;
    line-height: 1.4;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: var(--accent-primary);
}

.knowledge-content p {
    font-size: 1.0625rem;  /* 17px - optimal reading */
    line-height: 1.75;     /* 1.75 for readability */
    margin-bottom: 1.5rem;
    color: var(--text-secondary);
}

.knowledge-content ul,
.knowledge-content ol {
    margin-bottom: 1.5rem;
    padding-left: 1.5rem;
}

.knowledge-content li {
    font-size: 1.0625rem;
    line-height: 1.7;
    margin-bottom: 0.75rem;
}

/* Visual breathing room */
.knowledge-content > * + * {
    margin-top: 1.5rem;
}

.knowledge-content section + section {
    margin-top: 4rem;
}
```

**Content Spacing (Industry Best Practices):**

| Element | Top Margin | Bottom Margin | Rationale |
|---------|------------|---------------|-----------|
| H1 | 0 | 1.5rem (24px) | Page entry point |
| H2 | 3rem (48px) | 1.25rem (20px) | Major section break |
| H3 | 2rem (32px) | 1rem (16px) | Subsection spacing |
| Paragraph | 0 | 1.5rem (24px) | Reading rhythm |
| List | 0 | 1.5rem (24px) | Consistent spacing |
| Code Block | 1.5rem | 2rem (32px) | Visual separation |
| Diagram | 2rem | 2rem (32px) | Emphasis + breathing room |
| Section | 4rem (64px) | 0 | Clear content boundaries |

### Content Modules (Knowledge Library Specific)

**Concept Card:**
```html
<div class="concept-card">
    <div class="concept-icon">
        <i class="fas fa-cube"></i>
    </div>
    <div class="concept-content">
        <h3>Dependency Injection</h3>
        <p class="concept-summary">
            A design pattern where objects receive dependencies from external sources 
            rather than creating them internally.
        </p>
        <div class="concept-benefits">
            <h4>Key Benefits:</h4>
            <ul>
                <li>✅ Testability - Easy to mock dependencies</li>
                <li>✅ Flexibility - Swap implementations without code changes</li>
                <li>✅ Decoupling - Reduces tight coupling between classes</li>
            </ul>
        </div>
    </div>
</div>
```

**CSS:**
```css
.concept-card {
    display: flex;
    gap: 2rem;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    margin-bottom: 2rem;
    transition: all var(--transition-base);
}

.concept-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.concept-icon {
    flex-shrink: 0;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    border-radius: 12px;
    font-size: 1.75rem;
    color: white;
}

.concept-content {
    flex: 1;
}

.concept-summary {
    font-size: 1.0625rem;
    line-height: 1.7;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}

.concept-benefits {
    background: rgba(0, 212, 255, 0.05);
    border-left: 3px solid var(--accent-primary);
    padding: 1rem 1.5rem;
    border-radius: 4px;
}

.concept-benefits h4 {
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent-primary);
    margin-bottom: 0.75rem;
}

.concept-benefits ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.concept-benefits li {
    font-size: 0.9375rem;
    line-height: 1.6;
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
}
```

**Comparison Table (Better than Code Blocks):**
```html
<div class="comparison-table">
    <h4>Pattern Comparison</h4>
    <table>
        <thead>
            <tr>
                <th>Pattern</th>
                <th>Use Case</th>
                <th>Complexity</th>
                <th>Performance</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Singleton</strong></td>
                <td>Global state management</td>
                <td><span class="badge-low">Low</span></td>
                <td><span class="badge-high">High</span></td>
            </tr>
            <tr>
                <td><strong>Factory</strong></td>
                <td>Object creation</td>
                <td><span class="badge-medium">Medium</span></td>
                <td><span class="badge-high">High</span></td>
            </tr>
            <tr>
                <td><strong>Observer</strong></td>
                <td>Event handling</td>
                <td><span class="badge-medium">Medium</span></td>
                <td><span class="badge-medium">Medium</span></td>
            </tr>
        </tbody>
    </table>
</div>
```

**CSS:**
```css
.comparison-table {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    margin-bottom: 2rem;
    overflow-x: auto;
}

.comparison-table table {
    width: 100%;
    border-collapse: collapse;
}

.comparison-table th {
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 2px solid var(--accent-primary);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent-primary);
}

.comparison-table td {
    padding: 1rem;
    border-bottom: 1px solid var(--glass-border);
    font-size: 0.9375rem;
    color: var(--text-secondary);
}

.comparison-table tbody tr:hover {
    background: rgba(0, 212, 255, 0.05);
}

.badge-low,
.badge-medium,
.badge-high {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-low { background: rgba(0, 255, 136, 0.2); color: var(--success); }
.badge-medium { background: rgba(255, 165, 0, 0.2); color: var(--warning); }
.badge-high { background: rgba(255, 68, 68, 0.2); color: var(--danger); }
```

### Mobile Optimization (Knowledge Library)

```css
@media (max-width: 768px) {
    .knowledge-content {
        padding: 2rem 1.5rem;
    }
    
    .knowledge-content h1 {
        font-size: 1.75rem;
    }
    
    .knowledge-content h2 {
        font-size: 1.5rem;
        margin-top: 2rem;
    }
    
    .knowledge-content p,
    .knowledge-content li {
        font-size: 1rem;  /* 16px minimum for mobile readability */
    }
    
    .concept-card {
        flex-direction: column;
        gap: 1rem;
    }
    
    .concept-icon {
        width: 50px;
        height: 50px;
        font-size: 1.5rem;
    }
}
```

---

## ♿ Accessibility Standards (WCAG 2.1 AA)

### Color Contrast Requirements

**MANDATORY minimum contrast ratios:**
- **Normal text (16px+):** 4.5:1
- **Large text (24px+):** 3:1
- **UI components:** 3:1
- **Active elements:** 3:1

**Verify contrast in `main.css`:**
```css
/* Text on dark background */
--text-primary: #ffffff;     /* White on #0a0e27 = 16:1 ✅ */
--text-secondary: #a0a6c0;   /* Light gray on #0a0e27 = 8.5:1 ✅ */
--text-muted: #6b7280;       /* Med gray on #0a0e27 = 4.6:1 ✅ */

/* Interactive elements */
--accent-primary: #00d4ff;   /* Cyan on #0a0e27 = 7.8:1 ✅ */
--accent-secondary: #7b61ff; /* Purple on #0a0e27 = 4.2:1 ✅ */
```

### Keyboard Navigation

**REQUIRED for all interactive elements:**
```css
/* Focus indicators MUST be visible */
*:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* Custom focus for glassmorphic elements */
.glass-card:focus-within {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3);
}

button:focus,
a:focus,
input:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* Never remove focus indicators */
/* ❌ FORBIDDEN: outline: none; */
```

**Tab order:**
```html
<!-- Logical tab order: breadcrumb → logo → main content → footer -->
<nav class="breadcrumb" tabindex="0">...</nav>
<div class="logo-header">
    <a href="../index.html" tabindex="0">...</a>
</div>
<main class="container" tabindex="0">...</main>
```

### ARIA Labels & Semantic HTML

**REQUIRED attributes:**
```html
<!-- Navigation -->
<nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="../index.html" aria-label="Return to home page">Home</a>
</nav>

<!-- Buttons with icons -->
<button aria-label="Close dialog">
    <i class="fas fa-times" aria-hidden="true"></i>
</button>

<!-- Images -->
<img src="logo.png" alt="CORTEX Logo - AI-Powered Code Intelligence">

<!-- Skip links for screen readers -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Landmarks -->
<header role="banner">...</header>
<main role="main" id="main-content">...</main>
<footer role="contentinfo">...</footer>
```

**CSS for skip links:**
```css
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--accent-primary);
    color: #000;
    padding: 0.5rem 1rem;
    text-decoration: none;
    z-index: 1000;
}

.skip-link:focus {
    top: 0;
}
```

### Screen Reader Optimization

**Hide decorative elements:**
```html
<!-- Decorative icons -->
<i class="fas fa-star" aria-hidden="true"></i>

<!-- Visually hidden but read by screen readers -->
<span class="sr-only">Additional context for screen readers</span>
```

**CSS for screen reader only content:**
```css
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
```

### Mobile Accessibility

**Touch target spacing:**
```css
/* Ensure adequate spacing between touch targets */
.button-group button {
    margin: 0.5rem; /* Minimum 8px spacing */
}

/* Increase padding for better touch accuracy */
@media (max-width: 768px) {
    button,
    a.button {
        padding: 0.75rem 1.5rem;
        min-height: 48px; /* iOS recommended */
    }
}
```

**Gesture alternatives:**
```html
<!-- Always provide button alternatives to swipe gestures -->
<div class="carousel">
    <button aria-label="Previous slide">←</button>
    <button aria-label="Next slide">→</button>
</div>
```

---

## 🎴 Card Components

### Glass Card (Primary Container)

**Usage:** Main content sections, feature descriptions, documentation panels.

**CSS (from `main.css`):**
```css
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    margin-bottom: var(--spacing-2xl);
    box-shadow: var(--shadow);
    transition: all var(--transition-base);
}

.glass-card:hover {
    border-color: rgba(0, 212, 255, 0.2);
    box-shadow: var(--shadow-lg);
}

/* Responsive padding */
@media (max-width: 768px) {
    .glass-card {
        padding: 1.5rem;
        margin-bottom: var(--spacing-xl);
        border-radius: var(--radius-md);
    }
}

@media (max-width: 480px) {
    .glass-card {
        padding: 1.25rem;
        margin-bottom: var(--spacing-lg);
    }
}
```

**HTML Examples:**
```html
<!-- Standard content card -->
<div class="glass-card">
    <h2>Section Title</h2>
    <p>Content goes here...</p>
</div>

<!-- Card with max-width (for centered layout) -->
<div class="glass-card" style="max-width: 1400px; margin: 0 auto var(--spacing-2xl);">
    <h2>Centered Content</h2>
</div>
```

### Metric Cards (Dashboard Stats)

**Usage:** Statistics, counts, performance metrics.

**CSS (from `main.css`):**
```css
.metric-card {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    text-align: center;
    transition: all var(--transition-base);
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent-primary);
    box-shadow: var(--glow);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--accent-primary);
    line-height: 1;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
```

**HTML Example:**
```html
<div class="sts-metrics" style="display: flex; gap: 1.5rem; justify-content: center;">
    <div class="metric-card">
        <div class="metric-value">40+</div>
        <div class="metric-label">Flaws Fixed</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">6</div>
        <div class="metric-label">Categories</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">100%</div>
        <div class="metric-label">Resolved</div>
    </div>
</div>
```

### Comparison Section (STS-Specific)

**Usage:** Before/after code examples, side-by-side comparisons.

**CSS (from `sts.css`):**
```css
.comparison-section {
    background: var(--sts-glass-bg);
    border: 1px solid var(--sts-glass-border);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2.5rem;
    backdrop-filter: blur(10px);
}

.comparison-section:hover {
    border-color: rgba(0, 212, 255, 0.2);
}
```

**HTML Example:**
```html
<section class="comparison-section">
    <div class="section-header">
        <h3>
            <i class="fas fa-shield-alt"></i> SQL Injection Prevention
        </h3>
        <span class="language-badge csharp">C#</span>
    </div>
    
    <div class="refactor-explanation">
        <h4><i class="fas fa-lightbulb"></i> How This Was Refactored</h4>
        <ul>
            <li>→Vulnerability: String concatenation allows SQL injection</li>
            <li>→Fix: Parameterized queries separate data from commands</li>
            <li>→Result: User input is treated as data, never executable code</li>
        </ul>
    </div>
    
    <!-- Code comparison here -->
</section>
```

### Feature Grid Layout (Standard Pattern)

**Usage:** The PRIMARY pattern for displaying features, operations, or capabilities across the site.

**When to Use:**
- ✅ Displaying 2-4 features/items of equal importance
- ✅ Each item is independently navigable (clickable card)
- ✅ Consistent with other feature sections on the page
- ✅ Need individual hover states and interactions
- ✅ **DEFAULT pattern for features pages**

**Grid System Reference (from `main.css` lines 2088-2190):**

| Grid Class | Columns | Gap | Responsive Behavior | Use Case |
|------------|---------|-----|---------------------|----------|
| `metrics-grid-2` | 2 | 0.75rem | 768px: 2 cols → 480px: 1 col | Feature pairs, comparisons |
| `metrics-grid-3` | 3 | 0.75rem | 768px: 2 cols → 480px: 1 col | Feature trios, balanced layouts |
| `metrics-grid-4` | 4 | 1.5rem | 768px: 2 cols → 480px: 1 col | Metrics, stats dashboards |
| `metrics-grid-6` | 6 | 1.5rem | 1200px: 3 cols → 768px: 2 cols → 480px: 1 col | Dense data displays |
| `feature-grid-2` | 2 | 2rem | 768px: 1 col | Large feature cards |
| `feature-grid-3` | 3 | 2rem | 1024px: 2 cols → 768px: 1 col | Standard feature grids |
| `feature-grid-4` | 4 | 2rem | 1024px: 2 cols → 768px: 1 col | Compact feature displays |

**Grid Selection Decision Tree:**

```
Need to display multiple items in a grid?
    |
    ├─→ Are items navigable features/operations?
    |    |
    |    ├─→ 2 items: Use metrics-grid-2 (tight spacing)
    |    ├─→ 3 items: Use metrics-grid-3 (balanced)
    |    └─→ 4 items: Use metrics-grid-4 (wider spacing)
    |
    ├─→ Are items large feature cards with extensive content?
    |    |
    |    ├─→ 2 items: Use feature-grid-2 (2rem gap)
    |    ├─→ 3 items: Use feature-grid-3 (2rem gap)
    |    └─→ 4 items: Use feature-grid-4 (2rem gap)
    |
    └─→ Are items metrics/stats (non-clickable)?
         |
         ├─→ 4-6 items: Use metrics-grid-4 or metrics-grid-6
         └─→ Wrap in single glass-card for dashboard effect
```

**Gap Size Rationale:**
- **0.75rem (12px):** Tight spacing for 2-3 column feature grids (visual cohesion)
- **1.5rem (24px):** Wider spacing for 4-6 column grids (prevent crowding)
- **2rem (32px):** Generous spacing for large feature cards (breathing room)
- **Mobile:** All grids collapse to 1 column at 480px (gap becomes vertical margin)

**VERIFICATION REQUIRED:** Before using any grid class, run:
```bash
grep_search('.metrics-grid-2|.metrics-grid-3|.feature-grid-3', 'docs/assets/css/main.css')
```

**Standard Feature Card Pattern:**

**HTML Structure (2-Column Example):**
```html
<!-- Standard Pattern: Individual Feature Cards -->
<section class="section">
    <!-- Section heading OUTSIDE cards -->
    <h2 style="font-size: 2rem; margin-bottom: 2rem; text-align: center;">
        <span style="color: var(--accent-primary);">🛠️</span> System Operations
    </h2>
    
    <!-- Grid of individual glass cards -->
    <div class="metrics-grid-2">
        <!-- Feature Card 1 (Entire card is clickable) -->
        <a href="../orchestrators/sanitization-engine.html" class="glass-card feature-card" style="text-decoration: none; color: inherit; display: block; transition: all 0.3s ease;">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">🧹</div>
            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--accent-primary);">Sanitization Engine</h3>
            <p style="font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">Code Privacy & Security</p>
            <p style="font-size: 1rem; line-height: 1.6; color: var(--text-secondary); margin-bottom: 1.5rem;">
                5-phase automated sanitization that removes sensitive data, PII, and proprietary information 
                while maintaining code functionality and architectural integrity.
            </p>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.9375rem;">
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border);">✓ PII detection & removal</li>
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border);">✓ Secret redaction</li>
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border);">✓ Generic naming</li>
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);">✓ Compliance validation</li>
            </ul>
        </a>

        <!-- Feature Card 2 (Entire card is clickable) -->
        <a href="git-operations.html" class="glass-card feature-card" style="text-decoration: none; color: inherit; display: block; transition: all 0.3s ease;">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">🔄</div>
            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--accent-primary);">Git Operations</h3>
            <p style="font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">Intelligent Version Control</p>
            <p style="font-size: 1rem; line-height: 1.6; color: var(--text-secondary); margin-bottom: 1.5rem;">
                Smart Git workflow automation with checkpoint creation, branch management, and commit 
                message generation following conventional commit standards.
            </p>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.9375rem;">
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border);">✓ Auto checkpoints</li>
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border);">✓ Branch strategies</li>
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border);">✓ Commit templates</li>
                <li style="padding: 0.5rem 0; border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);">✓ Rollback safety</li>
            </ul>
        </a>
    </div>
</section>
```

**Visual Design:**
- **Section heading outside cards** (h2 with icon, centered)
- **Each card is a clickable link** (entire card is `<a>` tag)
- **Individual glass-card** per feature with hover effects
- **Icon size: 3rem** (48px) for consistency across all features
- **Content flow:** Icon → Title → Subtitle → Description → Feature list
- **Border lists** with top borders create visual structure
- **Mobile responsive** via `metrics-grid-2/3/4` classes (auto-stacks)

**Feature Card Component Anatomy:**

```html
<a href="{url}" class="glass-card feature-card">
    <i class="{icon-class}" style="font-size: 3rem; color: var(--accent-primary);"></i>
    <h3 style="font-size: 1.5rem; margin: 1rem 0 0.5rem;">{Title}</h3>
    <p style="font-size: 0.875rem; color: var(--accent-secondary); margin-bottom: 1rem;">{Subtitle}</p>
    <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1.5rem;">{Description}</p>
    <ul style="list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--glass-border); padding-top: 1rem;">
        <li>✅ {Feature 1}</li>
        <li>✅ {Feature 2}</li>
        <li>✅ {Feature 3}</li>
    </ul>
</a>
```

**Component Specifications Table:**

| Element | CSS Class | Inline Style | Responsive Behavior |
|---------|-----------|--------------|--------------------|
| **Container** | `glass-card feature-card` | None | Full-width on mobile |
| **Icon** | FontAwesome class | `font-size: 3rem; color: var(--accent-primary)` | Scales to 2.5rem on mobile |
| **Title (H3)** | None | `font-size: 1.5rem; margin: 1rem 0 0.5rem` | Scales to 1.25rem on mobile |
| **Subtitle** | None | `font-size: 0.875rem; color: var(--accent-secondary)` | Remains 0.875rem |
| **Description** | None | `color: var(--text-secondary); line-height: 1.6` | Line-height increases to 1.7 |
| **Feature List** | None | `border-top: 1px solid var(--glass-border)` | Padding adjusts to 0.75rem |

**Key Design Principles:**

| Element | Specification | Rationale |
|---------|--------------|----------|
| **Heading Placement** | Outside cards, above grid | Section context, not per-card |
| **Card Interactivity** | Entire card is `<a>` tag | Larger click target, better UX |
| **Icon Size** | 3rem (48px) | Consistent across all feature sections |
| **Hover Effect** | `translateY(-4px)` + glow | Visual feedback on interaction |
| **Grid Class** | `metrics-grid-2/3/4` | Responsive, auto-stacking |
| **Grid Gap** | `0.75rem` (2-col), `1.5rem` (3-4 col) | Tighter spacing for 2 columns |
| **Spacing** | Section margins handle gaps | Consistent vertical rhythm |

**Real-World Examples from Features Page:**

```html
<!-- ✅ CORRECT: System Operations (2 features) -->
<section class="section">
    <h2 style="font-size: 2rem; margin-bottom: 2rem; text-align: center;">
        <span style="color: var(--accent-primary);">🛠️</span> System Operations
    </h2>
    <div class="metrics-grid-2">
        <a href="sanitization-engine.html" class="glass-card feature-card">...</a>
        <a href="git-operations.html" class="glass-card feature-card">...</a>
    </div>
</section>

<!-- ✅ CORRECT: Core Features (3 features) -->
<section class="section">
    <h2 style="font-size: 2rem; margin-bottom: 2rem; text-align: center;">
        <span style="color: var(--accent-primary);">🚀</span> Core Features
    </h2>
    <div class="metrics-grid-3">
        <a href="planning-system.html" class="glass-card feature-card">...</a>
        <a href="tdd-orchestrator.html" class="glass-card feature-card">...</a>
        <a href="dashboard-system.html" class="glass-card feature-card">...</a>
    </div>
</section>

<!-- ✅ CORRECT: Intelligence & Automation (3 features) -->
<section class="section">
    <h2 style="font-size: 2rem; margin-bottom: 2rem; text-align: center;">
        <span style="color: var(--accent-primary);">🧠</span> Intelligence & Automation
    </h2>
    <div class="metrics-grid-3">
        <a href="holistic-discovery.html" class="glass-card feature-card">...</a>
        <a href="response-templates.html" class="glass-card feature-card">...</a>
        <a href="token-optimization.html" class="glass-card feature-card">...</a>
    </div>
</section>
```

### Unified Container Pattern (Special Cases Only)

**Usage:** ONLY for content that should NOT be individually clickable and benefits from visual grouping.

**When to Use:**
- ✅ Integration Ecosystem (metric cards showing stats, not navigation)
- ✅ Benefits/Why sections (2-column text content comparison)
- ✅ Aggregate statistics or dashboard metrics
- ❌ **NEVER for navigable features/operations** (use individual cards)

**Example: Integration Ecosystem (Correct Use Case):**
```html
<section class="section">
    <div class="glass-card">
        <h2 style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem; justify-content: center;">
            <span style="font-size: 2rem;">🔗</span>
            Integration Ecosystem
        </h2>
        <div class="metrics-grid-4">
            <!-- Non-clickable metric cards -->
            <div class="metric-card">
                <div class="metric-value">Azure DevOps</div>
                <div class="metric-label">Work Items</div>
            </div>
            <!-- More metric cards... -->
        </div>
    </div>
</section>
```

**Why This Works:** Metric cards are informational displays, not navigation targets. The unified container creates a cohesive "dashboard" feel.

---

## 🎭 Interactive Components

### D3.js Visualizations

**Container Standards:**
```css
.orchestrator-viz-section {
    margin-bottom: var(--spacing-2xl);
}

.orchestrator-viz-section .glass-card {
    max-width: 1400px;
    margin: 0 auto;
}

#orchestratorMapMain {
    width: 100%;
    height: 600px;
    position: relative;
}
```

**Filter Buttons:**
```css
.viz-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    justify-content: center;
}

.viz-btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: var(--radius-sm);
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-base);
    font-size: 0.875rem;
}

.viz-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.viz-btn.active {
    box-shadow: 0 0 0 3px rgba(255,255,255,0.5);
}

.viz-all {
    background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
    color: white;
}
```

**Node Styling:**
```css
#orchestratorMapMain .node circle {
    cursor: pointer;
    stroke: #fff;
    stroke-width: 3px;
    transition: all 0.3s ease;
}

#orchestratorMapMain .node:hover circle {
    stroke-width: 5px;
    filter: brightness(1.2);
}

#orchestratorMapMain .node text {
    font-size: 11px;
    font-weight: 600;
    text-anchor: middle;
    pointer-events: none;
    fill: #ffffff;  /* ALWAYS white on dark backgrounds */
}
```

**Tooltip:**
```css
.viz-tooltip {
    position: absolute;
    background: rgba(0,0,0,0.9);
    color: white;
    padding: 15px;
    border-radius: 8px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
    max-width: 300px;
    font-size: 13px;
    z-index: 1000;
}

.viz-tooltip h3 {
    margin: 0 0 8px 0;
    font-size: 15px;
    border-bottom: 2px solid #00d4ff;
    padding-bottom: 5px;
}
```

**Guidelines:**
- All D3.js diagrams MUST use white text (`fill: #ffffff`) on dark backgrounds
- Interactive elements MUST have hover states
- Tooltips use dark background with cyan accents
- Filter buttons use brand gradient for "All" category

### Hierarchical Node Coloring (Knowledge Maps)

**Purpose:** Child nodes in expandable visualizations should be visually distinct from parent nodes while maintaining color relationships.

**Implementation Pattern:**
```javascript
// Helper function to lighten colors for child nodes
function lightenColor(color, amount) {
    // Convert hex to RGB
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // Lighten by blending with white
    const newR = Math.round(r + (255 - r) * amount);
    const newG = Math.round(g + (255 - g) * amount);
    const newB = Math.round(b + (255 - b) * amount);
    
    // Convert back to hex
    return '#' + [newR, newG, newB].map(x => {
        const hex = x.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }).join('');
}

// Apply to child nodes
const childColor = lightenColor(parentColor, 0.3); // 30% lighter
```

**Color Hierarchy Rules:**
- **Parent nodes (domains):** Use full saturation brand colors
- **Child nodes (topics):** Use 30% lightened version of parent color
- **Lightening amount:** `0.3` (30% blend with white) for optimal contrast
- **Maintain relationships:** Child colors must visually relate to parent

**Visual Examples:**

| Parent Color | Child Color (30% lighter) | Usage |
|--------------|---------------------------|-------|
| `#2196F3` (Blue) | `#6AB8F7` | Frontend & UI domain/topics |
| `#4CAF50` (Green) | `#7BC97F` | Backend & APIs domain/topics |
| `#FF9800` (Orange) | `#FFB84D` | Data & Storage domain/topics |
| `#9C27B0` (Purple) | `#B85FCC` | Cloud & Infrastructure |
| `#F44336` (Red) | `#F77B72` | Software Craft & Quality |

**Accessibility Note:** Ensure child colors maintain WCAG 2.1 AA contrast ratios (3:1 minimum for UI components) against dark backgrounds.

### Interactive Node Behavior

**Click vs. Double-Click Pattern:**

**❌ OLD PATTERN (Inconsistent):**
- Single click: Expand domains only
- Double-click: Navigate to topic pages

**✅ NEW PATTERN (Consistent):**
- **Domain nodes:** Single click to expand/collapse
- **Topic nodes:** Single click to navigate to page
- **All nodes:** Draggable for repositioning

**Rationale:**
- Single-click for all primary actions improves mobile usability
- Eliminates confusion about click vs. double-click
- Consistent with modern UI expectations
- Better touch-screen compatibility

**Tooltip Instructions:**
```javascript
if (d.type === 'domain') {
    tooltipContent += `<p>Click to ${expandedDomains.has(d.id) ? 'collapse' : 'expand'}</p>`;
} else {
    tooltipContent += `<p>Click to view</p>`; // NOT "Double-click"
}
```

---

## 📝 Typography Standards

### Font Sizes by Component

| Component | Size | Line Height | Use Case |
|-----------|------|-------------|----------|
| Hero Title | 3rem (48px) | 1.1 | Main hero headings |
| H1 | 2.5rem (40px) | 1.2 | Page titles |
| H2 | 1.75rem (28px) | 1.3 | Section headers |
| H3 | 1.375rem (22px) | 1.4 | Subsection headers |
| Body Text | 1rem (16px) | 1.7 | Paragraphs |
| Small Text | 0.875rem (14px) | 1.6 | Captions, labels |
| Phase Title | 1.125rem (18px) | 1.5 | Workflow phase headers |
| Phase Icon | 2.4rem (38.4px) | N/A | Phase/tier icons |
| Metric Value | 2.5rem (40px) | 1 | Dashboard metrics |
| Metric Label | 0.875rem (14px) | 1.4 | Metric descriptions |

### Font Weights

```css
:root {
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    --font-weight-extrabold: 800;
}
```

**Usage:**
- **Normal (400):** Body text, descriptions
- **Medium (500):** Navigation links
- **Semibold (600):** Section headers, buttons
- **Bold (700):** Page titles, metric values
- **Extrabold (800):** Hero titles

### Panel Section Titles (Knowledge Library)

**Problem:** Default h2 titles in `.glass-card` sections were not prominent enough and lacked visual hierarchy.

**Solution:** Enhanced panel titles with centered alignment, larger font, and CORTEX brand color.

**CSS Class Definition:**
```css
/* Enhanced panel section titles */
.glass-card h2.section-title {
    text-align: center;
    font-size: 2.5rem;
    color: var(--accent-primary); /* #00d4ff */
    margin-bottom: 2rem;
    font-weight: var(--font-weight-bold);
    letter-spacing: -0.02em;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .glass-card h2.section-title {
        font-size: 2rem; /* Smaller on mobile */
        margin-bottom: 1.5rem;
    }
}

@media (max-width: 480px) {
    .glass-card h2.section-title {
        font-size: 1.75rem; /* Even smaller on small mobile */
        margin-bottom: 1.25rem;
    }
}
```

**HTML Implementation:**
```html
<!-- ✅ CORRECT: Use section-title class -->
<div class="glass-card">
    <h2 class="section-title">🎯 Frontend Frameworks</h2>
    <h3>React</h3>
    <!-- Content here -->
</div>

<!-- ❌ WRONG: Don't use inline styles -->
<div class="glass-card">
    <h2 style="text-align: center; font-size: 2.5rem; color: #00d4ff;">🎯 Frontend Frameworks</h2>
</div>

<!-- ❌ WRONG: Don't use default h2 -->
<div class="glass-card">
    <h2>🎯 Frontend Frameworks</h2>
</div>
```

**Design Rationale:**
- **Centered alignment:** Creates clear visual focal points and improves scannability
- **Larger font (2.5rem):** Establishes clear hierarchy between section titles (h2) and subsection headers (h3)
- **CORTEX cyan (#00d4ff):** Reinforces brand identity and provides visual consistency
- **Large emoji icons:** Already present, work well with centered layout
- **Responsive scaling:** Ensures readability on mobile devices without overwhelming the viewport

**Usage Guidelines:**
- Apply `.section-title` class to ALL h2 elements in `.glass-card` containers
- Keep emojis at the beginning of the title for visual impact
- Maintain consistent spacing (2rem bottom margin) for rhythm
- Do NOT use inline styles (violates CSS precedence rules)
- Subsection headers (h3, h4) remain left-aligned for content flow

---

## 🎨 Special Effects

### Glassmorphism Effect (Core)

**Standard Glass Background:**
```css
background: rgba(26, 31, 58, 0.7);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 16px;
```

**Variations:**
- **Stronger glass:** `rgba(26, 31, 58, 0.9)` for emphasis
- **Lighter glass:** `rgba(26, 31, 58, 0.5)` for subtle backgrounds
- **More blur:** `blur(15px)` for overlay effects

### Glow Effects

**Cyan Glow (Brand Color):**
```css
box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
```

**Purple Glow (Secondary):**
```css
box-shadow: 0 0 20px rgba(123, 97, 255, 0.3);
```

**When to Use:**
- Logos: Always include cyan glow
- Hover states: Increase glow intensity
- Active elements: Cyan glow indicates interactivity
- Badges: Subtle glow for emphasis

### Gradient Backgrounds

**Primary Gradient (Buttons, Badges):**
```css
background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
```

**Text Gradient:**
```css
background: linear-gradient(135deg, #fff 0%, #00d4ff 50%, #7b61ff 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

---

## 🎯 Framework/Technology Panel Pattern

### 3-Column Framework Panels

**Usage:** Display framework comparisons (React, Vue, Angular), technology overviews, or feature sets in a visually balanced grid.

**CSS (add to `main.css`):**
```css
.framework-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    margin: 2rem 0;
}

@media (max-width: 1024px) {
    .framework-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
}

.framework-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    transition: all var(--transition-base);
}

.framework-panel:hover {
    transform: translateY(-4px);
    border-color: rgba(0, 212, 255, 0.3);
    box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
}

.framework-panel-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}

.framework-panel h3 {
    color: var(--accent-primary);
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.framework-panel .framework-subtitle {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-bottom: 1.5rem;
    font-style: italic;
}

.framework-panel h4 {
    color: var(--text-primary);
    font-size: 1rem;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
}

.framework-panel ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.framework-panel li {
    color: var(--text-secondary);
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.framework-panel li::before {
    content: "▸";
    color: var(--accent-primary);
    position: absolute;
    left: 0;
    font-weight: bold;
}
```

**HTML Implementation:**
```html
<div class="framework-grid">
    <!-- React Panel -->
    <div class="framework-panel">
        <span class="framework-panel-icon">⚛️</span>
        <h3>React</h3>
        <p class="framework-subtitle">Meta's Component-Based Library</p>
        
        <h4>Core Features</h4>
        <ul>
            <li><strong>Virtual DOM:</strong> Efficient UI updates</li>
            <li><strong>Hooks:</strong> State management</li>
            <li><strong>JSX:</strong> Declarative syntax</li>
        </ul>
        
        <h4>Best Practices</h4>
        <ul>
            <li>Use functional components</li>
            <li>Implement proper key props</li>
            <li>Memoize expensive computations</li>
        </ul>
        
        <h4>Ecosystem</h4>
        <ul>
            <li><strong>Next.js:</strong> Full-stack framework</li>
            <li><strong>React Query:</strong> Server state</li>
            <li><strong>Redux Toolkit:</strong> State container</li>
        </ul>
    </div>
    
    <!-- Vue Panel -->
    <div class="framework-panel">
        <span class="framework-panel-icon">🟢</span>
        <h3>Vue.js</h3>
        <p class="framework-subtitle">Progressive JavaScript Framework</p>
        
        <h4>Core Features</h4>
        <ul>
            <li><strong>Reactive System:</strong> Auto dependency tracking</li>
            <li><strong>SFC:</strong> Single file components</li>
            <li><strong>Composition API:</strong> Flexible logic</li>
        </ul>
        
        <h4>Best Practices</h4>
        <ul>
            <li>Use Composition API</li>
            <li>Keep components focused</li>
            <li>Leverage computed properties</li>
        </ul>
        
        <h4>Ecosystem</h4>
        <ul>
            <li><strong>Nuxt.js:</strong> Meta-framework</li>
            <li><strong>Pinia:</strong> State management</li>
            <li><strong>Vuetify:</strong> Component library</li>
        </ul>
    </div>
    
    <!-- Angular Panel -->
    <div class="framework-panel">
        <span class="framework-panel-icon">🅰️</span>
        <h3>Angular</h3>
        <p class="framework-subtitle">Enterprise-Grade Framework</p>
        
        <h4>Core Features</h4>
        <ul>
            <li><strong>TypeScript First:</strong> Built-in</li>
            <li><strong>DI System:</strong> Powerful injection</li>
            <li><strong>RxJS:</strong> Reactive programming</li>
        </ul>
        
        <h4>Best Practices</h4>
        <ul>
            <li>Use OnPush change detection</li>
            <li>Lazy load modules</li>
            <li>Follow style guide</li>
        </ul>
        
        <h4>Ecosystem</h4>
        <ul>
            <li><strong>Angular CLI:</strong> Code generation</li>
            <li><strong>NgRx:</strong> State management</li>
            <li><strong>Material:</strong> UI components</li>
        </ul>
    </div>
</div>
```

**Design Rationale:**
- **3-column grid:** Visual balance for framework comparisons
- **Icons:** Large emoji icons (2.5rem) for quick identification
- **Subtitle:** Italicized brief description under title
- **Sections:** h4 headers for Core Features, Best Practices, Ecosystem
- **Hover effects:** Lift and glow on hover for interactivity
- **Responsive:** Stacks to single column on tablet/mobile (<1024px)

**When to Use:**
- Framework comparisons (React vs Vue vs Angular)
- Technology stack overviews
- Feature set comparisons
- Service/tool comparisons

**Multi-Row Handling:**

When displaying MORE THAN 3 items:
- ✅ **CORRECT:** Use multiple `.framework-grid` containers (one per row of 3)
- ❌ **WRONG:** Extend single grid beyond 3 columns or use `grid-4col`, `grid-5col`, etc.

**Example: 6 Items (2 rows of 3):**
```html
<!-- First Row: Items 1-3 -->
<div class="framework-grid">
    <div class="framework-panel"><!-- Item 1 --></div>
    <div class="framework-panel"><!-- Item 2 --></div>
    <div class="framework-panel"><!-- Item 3 --></div>
</div>

<!-- Second Row: Items 4-6 -->
<div class="framework-grid">
    <div class="framework-panel"><!-- Item 4 --></div>
    <div class="framework-panel"><!-- Item 5 --></div>
    <div class="framework-panel"><!-- Item 6 --></div>
</div>
```

**Example: 4 Items (1 full row + 1 partial row):**
```html
<!-- First Row: Items 1-3 -->
<div class="framework-grid">
    <div class="framework-panel"><!-- Item 1 --></div>
    <div class="framework-panel"><!-- Item 2 --></div>
    <div class="framework-panel"><!-- Item 3 --></div>
</div>

<!-- Second Row: Item 4 (centered by grid) -->
<div class="framework-grid">
    <div class="framework-panel"><!-- Item 4 --></div>
</div>
```

**Rationale:**
- **Visual consistency:** Maintains 3-column rhythm across all pages
- **Responsive behavior:** Each row independently collapses on mobile
- **Grid balance:** CSS grid automatically centers partial rows
- **Readability:** Prevents overcrowding and maintains breathing room

**When NOT to Use Framework Panels:**

❌ **Simple Lists:** Use standard `<ul>` with `.feature-list` class
❌ **Code Examples:** Use `.code-snippet` or pseudocode blocks
❌ **Tables:** Use `.glass-table-bordered` for comparison data
❌ **Single Info Boxes:** Use `.info-box` variants for standalone callouts
❌ **Navigation Elements:** Use breadcrumb or site-header patterns
❌ **Mermaid Diagrams:** Standalone diagram containers

✅ **Use Framework Panels For:**
- Framework/technology comparisons (React vs Vue vs Angular)
- Feature breakdowns with 2-4+ items
- Architecture layer explanations
- Concept explanations with icons and lists
- Resource sections with multiple categories
- Pattern libraries and best practices

**Legacy Class Migration:**

All legacy grid classes have been removed:
- ❌ `.grid-2col` → ✅ `.framework-grid` (2 panels)
- ❌ `.grid-3col` → ✅ `.framework-grid` (3 panels)
- ❌ `.info-box-primary`, `.info-box-secondary` → ✅ `.framework-panel`

**Migration Complete:** All `docs/knowledge/*.html` files now use `framework-grid` and `framework-panel` exclusively.

---

## � Table Styling

### Standard Glass Table

**Basic table styling for data display:**
```css
.glass-table {
    width: 100%;
    border-collapse: collapse;
    margin: var(--spacing-lg) 0;
}

.glass-table th,
.glass-table td {
    padding: var(--spacing-md);
    text-align: left;
    border-bottom: 1px solid var(--glass-border);
}

.glass-table th {
    background: rgba(0, 212, 255, 0.1);
    color: var(--accent-primary);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.875rem;
    letter-spacing: 0.05em;
}

.glass-table tr:hover td {
    background: rgba(255, 255, 255, 0.03);
}
```

### Bordered Table (Decision Matrices, Comparisons)

**Enhanced table styling with prominent borders and padding:**
```css
.glass-table-bordered {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: var(--spacing-lg) 0;
    border: 2px solid var(--glass-border);
    border-radius: var(--radius-md);
    overflow: hidden;
}

.glass-table-bordered th,
.glass-table-bordered td {
    padding: 1rem 1.5rem;
    text-align: center;
    border: 1px solid var(--glass-border);
}

.glass-table-bordered th {
    background: rgba(0, 212, 255, 0.15);
    color: var(--accent-primary);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.9375rem;
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--accent-primary);
}

.glass-table-bordered th:first-child {
    text-align: left;
}

.glass-table-bordered td {
    background: rgba(26, 31, 58, 0.5);
    color: var(--text-primary);
}

.glass-table-bordered td:first-child {
    text-align: left;
    font-weight: 600;
    color: var(--text-secondary);
}

.glass-table-bordered tbody tr:hover td {
    background: rgba(0, 212, 255, 0.08);
}
```

**HTML Implementation:**
```html
<!-- ✅ CORRECT: Bordered table for decision matrices -->
<table class="glass-table-bordered">
    <thead>
        <tr>
            <th>Criteria</th>
            <th>Option A</th>
            <th>Option B</th>
            <th>Option C</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Performance</strong></td>
            <td>⭐⭐⭐⭐⭐</td>
            <td>⭐⭐⭐⭐</td>
            <td>⭐⭐⭐</td>
        </tr>
    </tbody>
</table>

<!-- ✅ CORRECT: Standard table for simple data -->
<table class="glass-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Value</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Item 1</td>
            <td>100</td>
        </tr>
    </tbody>
</table>
```

**When to Use:**
- **`.glass-table`:** Simple data tables, lists, basic comparisons
- **`.glass-table-bordered`:** Decision matrices, comparison charts, rating systems, feature comparisons

**Design Rationale:**
- **Borders:** Clear cell boundaries improve scannability for complex comparisons
- **Generous padding:** 1rem vertical, 1.5rem horizontal for comfortable reading
- **Centered content:** Ratings and values center-aligned for visual balance
- **Left-aligned labels:** First column remains left-aligned for readability
- **Hover effects:** Subtle background change on row hover for interactivity
- **Rounded corners:** Consistent with glassmorphism card styling

### Application Guidelines for Knowledge Views

**Identify Tables That Need Bordered Styling:**

Tables should use `.glass-table-bordered` when they contain:
- **Comparison matrices** (comparing multiple options across criteria)
- **Decision tables** (helping users choose between alternatives)
- **Rating/scoring systems** (star ratings, numerical scores, grades)
- **Feature comparisons** (showing which features different options have)
- **WCAG conformance levels** (accessibility requirement matrices)
- **Framework/tool comparisons** (pros/cons, capabilities across platforms)
- **Breakpoint definitions** (responsive design sizing tables)
- **Any table where cells contain ratings, symbols, or comparative values**

**Examples from Existing Knowledge Views:**

1. **mobile.html** - Already implemented:
   - ✅ Development Approaches Decision Matrix (line 117)
   - Comparison of Native, React Native, Flutter, PWA with ratings across performance, development speed, etc.

2. **frontend.html** - Potential candidates:
   - Framework comparison tables (React vs Vue vs Angular)
   - State management solution comparisons
   - Build tool feature matrices
   - Performance metrics tables

3. **ui-ux.html** - Potential candidates:
   - WCAG conformance level tables
   - Accessibility testing tool comparisons
   - Breakpoint/responsive sizing tables
   - Design system component matrices

**Implementation Checklist:**

When reviewing knowledge views for table styling:
1. **Scan for `<table>` elements** in each knowledge view file
2. **Evaluate table content:**
   - Is it comparing multiple options? → `.glass-table-bordered`
   - Is it helping users make decisions? → `.glass-table-bordered`
   - Does it contain ratings/symbols? → `.glass-table-bordered`
   - Is it a simple list of data? → `.glass-table`
3. **Apply class:** Replace `class="glass-table"` with `class="glass-table-bordered"`
4. **Verify rendering:** Check that borders and padding display correctly
5. **Test responsiveness:** Ensure table remains readable on mobile devices

**Consistency Principle:**

> All comparison and decision-making tables across the knowledge library should use `.glass-table-bordered` for visual consistency and improved scannability. This creates a predictable user experience where comparison-heavy content is immediately recognizable through its distinctive bordered styling.

---

## �📱 Responsive Design

### Breakpoints (Mobile-First Strategy)

```css
/* Mobile First Approach - Base styles optimized for 320px+ */

/* Small mobile (320px-479px) - Base styles */
/* All base CSS should work at this size */

/* Mobile (480px-767px) */
@media (min-width: 480px) {
    body { font-size: 16px; }
    .container { padding: 0 1.5rem; }
}

/* Tablet (768px-1023px) */
@media (min-width: 768px) {
    .page-logo { width: 250px; }
    .nav-links { gap: 1.5rem; }
    .glass-card { padding: 1.75rem; }
}

/* Desktop (1024px-1439px) */
@media (min-width: 1024px) {
    .container { max-width: 1200px; }
    .page-logo { width: 300px; }
    .glass-card { padding: 2rem; }
}

/* Large Desktop (1440px+) */
@media (min-width: 1440px) {
    .container { max-width: 1400px; }
}

/* Ultra-wide (1920px+) */
@media (min-width: 1920px) {
    .container { max-width: 1600px; }
}
```

### Container Width Standards

**MANDATORY container settings:**
```css
.container {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Responsive container padding */
@media (min-width: 480px) {
    .container { padding: 0 1.5rem; }
}

@media (min-width: 768px) {
    .container { padding: 0 2rem; }
}

@media (min-width: 1024px) {
    .container { padding: 0 2.5rem; }
}
```

### Touch Target Standards (Mobile Accessibility)

**WCAG 2.1 Level AAA Compliance:**
```css
/* All interactive elements MUST be touch-friendly */
button,
a,
input,
select,
textarea,
.interactive-element {
    min-height: 44px;  /* Apple/Google standard */
    min-width: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* Exception for inline text links */
p a,
li a {
    min-height: auto;
    min-width: auto;
    padding: 0.25rem 0; /* Still provide tap padding */
}
```

### Responsive Typography

```css
/* Base mobile typography (320px+) */
body {
    font-size: 16px; /* Never smaller - mobile readability */
    line-height: 1.6;
}

h1 {
    font-size: 1.75rem; /* 28px mobile */
    line-height: 1.2;
}

h2 {
    font-size: 1.5rem; /* 24px mobile */
    line-height: 1.3;
}

h3 {
    font-size: 1.25rem; /* 20px mobile */
    line-height: 1.4;
}

/* Tablet+ typography */
@media (min-width: 768px) {
    h1 { font-size: 2.25rem; } /* 36px */
    h2 { font-size: 1.75rem; } /* 28px */
    h3 { font-size: 1.375rem; } /* 22px */
}

/* Desktop typography */
@media (min-width: 1024px) {
    h1 { font-size: 2.5rem; } /* 40px */
    h2 { font-size: 1.875rem; } /* 30px */
    h3 { font-size: 1.5rem; } /* 24px */
}
```

### Responsive Images & Media

```css
/* All images MUST be responsive */
img {
    max-width: 100%;
    height: auto;
    display: block;
}

/* Logo responsive sizing */
.page-logo {
    width: 200px; /* Mobile default */
    height: auto;
    transition: filter var(--transition-base);
}

@media (min-width: 768px) {
    .page-logo { width: 250px; }
}

@media (min-width: 1024px) {
    .page-logo { width: 300px; }
}

/* Responsive video embeds */
.video-container {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    height: 0;
    overflow: hidden;
}

.video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
```

### Mobile-Specific Optimizations

```css
/* Reduce animations on mobile for performance */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Hide decorative elements on small screens */
@media (max-width: 480px) {
    .decorative-only {
        display: none;
    }
    
    /* Reduce blur intensity for mobile performance */
    .glass-card {
        backdrop-filter: blur(8px);
    }
}

/* Stack layouts on mobile */
@media (max-width: 768px) {
    .desktop-flex {
        flex-direction: column;
    }
    
    .grid-layout {
        grid-template-columns: 1fr;
    }
}
```

### Mobile Navigation (Story Viewer Pattern)

**Desktop:** Full text labels
```html
<div class="chapter-navigation">
    <button class="nav-button">
        <span class="arrow">←</span>
        <span class="text">Previous</span>
    </button>
    <button class="nav-button">
        <span class="text">Next</span>
        <span class="arrow">→</span>
    </button>
</div>
```

**Mobile (480px):** Arrow-only in glassmorphic panel
```css
@media (max-width: 480px) {
    .chapter-navigation {
        padding: var(--spacing-md);
        background: rgba(26, 31, 58, 0.6);
        backdrop-filter: blur(15px);
        border-radius: var(--radius-lg);
    }
    
    .nav-button .text { display: none; }
    .nav-button .arrow { display: block; }
    .nav-button { min-width: 60px; }
}
```

---

## ✅ Page Layout Checklist

Use this for every new documentation page:

### Standard Page Layout (First Level - Section Index)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section Index | CORTEX</title>
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo.png">
    <link rel="stylesheet" href="../assets/css/main.css">
</head>
<body>
    <!-- 1. BREADCRUMB (REQUIRED) -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">Section</span>
    </nav>
    
    <!-- 2. LOGO HEADER (REQUIRED for first level) -->
    <div class="logo-header">
        <a href="../index.html">
            <img src="../assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="page-logo">
        </a>
    </div>
    
    <!-- 3. MAIN CONTENT (REQUIRED) -->
    <main class="container">
        <div class="glass-card">
            <h1>Section Title</h1>
            <p class="text-secondary">Brief description</p>
            
            <!-- Content sections -->
            <h2><span>🏗️</span> Subsection Title</h2>
            <p>Section content...</p>
        </div>
    </main>
    
    <!-- 4. FOOTER (OPTIONAL) -->
    <footer style="text-align: center; padding: 2rem; color: var(--text-muted);">
        <p>© 2024-2025 CORTEX 4.0 - AI-Powered Code Intelligence by Asif Hussain</p>
    </footer>
</body>
</html>
```

### Standard Page Layout (Second/Third Level - Detail Pages)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title | CORTEX</title>
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo.png">
    <link rel="stylesheet" href="../assets/css/main.css">
</head>
<body>
    <!-- 1. BREADCRUMB (REQUIRED) -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">→</span>
        <a href="index.html">Section</a>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">Page</span>
    </nav>
    
    <!-- 2. NO LOGO for second/third level pages -->
    
    <!-- 3. MAIN CONTENT (REQUIRED) -->
    <main class="container">
        <div class="glass-card">
            <h1>Page Title</h1>
            <p class="text-secondary">Brief description</p>
            
            <!-- User benefit panel (feature pages) -->
            <div class="feature-benefit-panel">
                <span class="icon">🎯</span>
                <p class="description">
                    User-centric benefit explanation...
                </p>
            </div>
            
            <!-- Content sections -->
            <h2><span>🏗️</span> Section Title</h2>
            <p>Section content...</p>
        </div>
    </main>
    
    <!-- 4. FOOTER (OPTIONAL) -->
    <footer style="text-align: center; padding: 2rem; color: var(--text-muted);">
        <p>© 2024-2025 CORTEX 4.0 - AI-Powered Code Intelligence by Asif Hussain</p>
    </footer>
</body>
</html>
```

### STS Showcase Layout

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STS Page | CORTEX</title>
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo.png">
    <link rel="stylesheet" href="../assets/css/main.css">
    <link rel="stylesheet" href="../assets/css/sts.css">
</head>
<body class="sts-showcase">
    <!-- 1. SITE HEADER (REQUIRED for STS) -->
    <header class="site-header">
        <nav class="nav-container">
            <a href="../index.html" class="nav-brand">
                <i class="fas fa-brain"></i> CORTEX 4.0
            </a>
            <div class="nav-links">
                <a href="index.html"><i class="fas fa-bullseye"></i> STS Hub</a>
                <a href="../documentation.html"><i class="fas fa-book"></i> Docs</a>
            </div>
        </nav>
    </header>
    
    <!-- 2. MAIN CONTENT -->
    <main class="sts-main">
        <!-- Hero section -->
        <section class="sts-hero">
            <div class="hero-badge">
                <i class="fas fa-tools"></i> CATEGORY NAME
            </div>
            <h1>Page Title</h1>
            <p class="hero-subtitle">Description...</p>
        </section>
        
        <!-- Comparison sections -->
        <section class="comparison-section">
            <!-- Code examples -->
        </section>
    </main>
    
    <!-- 3. FOOTER -->
    <footer>
        <p>© 2024 CORTEX 4.0 by Asif Hussain</p>
    </footer>
</body>
</html>
```

---

## 🚫 Anti-Patterns (AVOID)

### ❌ Don't: Inline Styles
```html
<!-- WRONG -->
<div style="background: rgba(26, 31, 58, 0.7); border-radius: 16px;">
```

### ✅ Do: CSS Classes
```html
<!-- CORRECT -->
<div class="glass-card">
```

---

### ❌ Don't: Page-Specific Style Tags
```html
<!-- WRONG -->
<style>
.my-custom-card {
    background: var(--glass-bg);
}
</style>
```

### ✅ Do: Add to main.css
```css
/* In main.css */
.my-custom-card {
    background: var(--glass-bg);
}
```

---

### ❌ Don't: Multiple CSS Files in Subdirectories
```html
<!-- WRONG -->
<link rel="stylesheet" href="technical/assets/styles/glassmorphism.css">
<link rel="stylesheet" href="orchestrators/styles/theme.css">
```

### ✅ Do: Single main.css (+ sts.css if STS page)
```html
<!-- CORRECT -->
<link rel="stylesheet" href="../assets/css/main.css">
<!-- If STS page: -->
<link rel="stylesheet" href="../assets/css/sts.css">
```

---

### ❌ Don't: Breadcrumb After Logo
```html
<!-- WRONG ORDER -->
<div class="logo-header">...</div>
<nav class="breadcrumb">...</nav>
```

### ✅ Do: Breadcrumb Before Logo
```html
<!-- CORRECT ORDER -->
<nav class="breadcrumb">...</nav>
<div class="logo-header">...</div>
```

---

### ❌ Don't: Version Numbers in Titles
```html
<!-- WRONG -->
<h1>Planning System 2.0</h1>
```

### ✅ Do: Timeless Feature Names
```html
<!-- CORRECT -->
<h1>Planning System</h1>
```

---

## 🔄 Migration Checklist

When updating existing pages to v2.0 standards:

### Core Standards
- [ ] **1. Remove inline styles** - Run `html_style_centralizer.py`
- [ ] **2. Add breadcrumb navigation** - Place at top (before logo if first level)
- [ ] **3. Verify CSS links** - Only `main.css` (+ `sts.css` if STS)
- [ ] **4. Check logo placement** - First level only (remove from second/third level)
- [ ] **5. Standardize logo size** - 300px desktop, 200px mobile, with glow
- [ ] **6. Update card spacing** - 48px between major sections (`var(--spacing-2xl)`)
- [ ] **7. Fix icon sizes** - 2.4rem for phase/tier icons
- [ ] **8. Remove version numbers** - From titles and H1 tags
- [ ] **9. Validate HTML** - Run `html_validator.py`
- [ ] **10. Check D3.js text** - White (`#ffffff`) on dark backgrounds

### Responsive Design Checklist
- [ ] **1. Add viewport meta tag** - `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- [ ] **2. Test all breakpoints** - 320px, 375px, 480px, 768px, 1024px, 1440px, 1920px
- [ ] **3. Verify touch targets** - All interactive elements ≥44px on mobile
- [ ] **4. Check horizontal scroll** - Must be zero at all breakpoints
- [ ] **5. Test mobile navigation** - Breadcrumb wraps, links are tappable
- [ ] **6. Optimize images** - Use `srcset` for responsive images
- [ ] **7. Test text readability** - Minimum 16px on mobile, scales up on desktop
- [ ] **8. Verify card stacking** - Cards stack vertically on mobile
- [ ] **9. Test landscape mode** - Both portrait and landscape orientations
- [ ] **10. Check performance** - Page loads in <3s on 3G network
- [ ] **11. Reduce animations** - Respect `prefers-reduced-motion`
- [ ] **12. Test real devices** - iOS (iPhone) and Android (Samsung/Pixel)

### Accessibility Checklist
- [ ] **1. Color contrast** - Verify 4.5:1 for text, 3:1 for UI components
- [ ] **2. Keyboard navigation** - All interactive elements accessible via Tab
- [ ] **3. Focus indicators** - Visible 2px outline on all focusable elements
- [ ] **4. ARIA labels** - Add to navigation, buttons, and complex widgets
- [ ] **5. Alt text** - Descriptive alt text for all images
- [ ] **6. Semantic HTML** - Use `<nav>`, `<main>`, `<header>`, `<footer>`
- [ ] **7. Skip links** - Add "Skip to main content" for screen readers
- [ ] **8. Heading hierarchy** - Logical H1→H2→H3 structure (no skips)
- [ ] **9. Link text** - Descriptive text (avoid "click here")
- [ ] **10. Form labels** - All inputs have associated `<label>` elements

### Knowledge Library Specific Checklist

- [ ] **1. Replace large code blocks** - Max 10 lines, prefer pseudocode
- [ ] **2. Add visual diagrams** - Mermaid/D3.js for every concept
- [ ] **3. Use concept cards** - Replace text walls with structured cards
- [ ] **4. Optimize text spacing** - 1.75 line-height, 17px font size
- [ ] **5. Add comparison tables** - Better than side-by-side code
- [ ] **6. Verify max-width** - 900px for optimal reading
- [ ] **7. Check section spacing** - 4rem (64px) between major sections
- [ ] **8. Mobile text size** - Minimum 16px for body text
- [ ] **9. Annotate snippets** - Every code example needs context
- [ ] **10. Test readability** - Can user scan and understand without reading everything?
- [ ] **11. Responsive diagrams** - SVG/Mermaid scale on mobile
- [ ] **12. Test pseudocode** - Readable on small screens

---

## 📚 Reference Implementations

**Study these files for correct patterns:**

| Pattern | File | What to Learn |
|---------|------|---------------|
| Breadcrumb + Logo | `docs/orchestrators/index.html` | Top navigation structure |
| Site Header | `docs/sts/index.html` | Alternative navigation for showcases |
| D3.js Integration | `docs/orchestrators/index.html` | Interactive visualization styling |
| Code Comparison | `docs/sts/security.html` | Before/after layout |
| Hero Section | `docs/sts/index.html` | Metrics, badges, intro |
| Glassmorphism Cards | `docs/orchestrators/planning-system.html` | Content panel layout |
| Knowledge Library | `docs/knowledge/*.html` | Text-heavy educational content |

### Knowledge Library Best Practices

**✅ GOOD EXAMPLE - Concept-Driven:**
```html
<div class="glass-card">
    <h2><i class="fas fa-layer-group"></i> Layered Architecture</h2>
    
    <!-- Visual diagram FIRST -->
    <div class="diagram-container">
        <div class="mermaid">
        graph TD
            UI[Presentation Layer] --> BL[Business Logic Layer]
            BL --> DAL[Data Access Layer]
            DAL --> DB[(Database)]
        </div>
    </div>
    
    <!-- Text explanation -->
    <p>Layered architecture organizes code into horizontal layers, 
    where each layer has a specific responsibility and communicates 
    only with adjacent layers.</p>
    
    <!-- Concept card for details -->
    <div class="concept-card">
        <div class="concept-icon"><i class="fas fa-code"></i></div>
        <div class="concept-content">
            <h3>Implementation Pattern</h3>
            <div class="pseudocode-block">
                <pre class="pseudocode">
<span class="comment">// Presentation Layer</span>
Controller → receives user input
    ↓
<span class="comment">// Business Layer</span>
Service → processes business logic
    ↓
<span class="comment">// Data Layer</span>
Repository → handles data operations
                </pre>
            </div>
        </div>
    </div>
    
    <!-- Benefits list (not code) -->
    <div class="concept-benefits">
        <h4>Key Benefits:</h4>
        <ul>
            <li>✅ Separation of concerns</li>
            <li>✅ Independent testing</li>
            <li>✅ Easy to maintain</li>
        </ul>
    </div>
</div>
```

**❌ BAD EXAMPLE - Code-Heavy:**
```html
<!-- DON'T DO THIS in Knowledge Library -->
<div class="glass-card">
    <h2>Layered Architecture</h2>
    
    <!-- NO: Full class implementation -->
    <pre><code>
public class UserController : Controller
{
    private readonly IUserService _userService;
    
    public UserController(IUserService userService)
    {
        _userService = userService;
    }
    
    public async Task<IActionResult> GetUser(int id)
    {
        var user = await _userService.GetUserByIdAsync(id);
        if (user == null)
            return NotFound();
        return Ok(user);
    }
    
    public async Task<IActionResult> CreateUser([FromBody] UserDto dto)
    {
        var result = await _userService.CreateUserAsync(dto);
        return CreatedAtAction(nameof(GetUser), new { id = result.Id }, result);
    }
}
    </code></pre>
    
    <!-- User has to scroll through more code... -->
</div>
```

---

## 🎓 Quick Reference

### Design Decision Matrix

**Use this table to quickly determine the correct pattern for common scenarios:**

| Scenario | Pattern | Grid Class | Container |
|----------|---------|------------|----------|
| **2 navigable features** | Individual cards | `metrics-grid-2` | None (section only) |
| **3 navigable features** | Individual cards | `metrics-grid-3` | None (section only) |
| **4+ stats/metrics** | Unified container | `metrics-grid-4` | Single `glass-card` |
| **Large feature cards** | Individual cards | `feature-grid-3` | None (section only) |
| **Technical diagram** | Centered Mermaid | N/A | Dark backdrop div |
| **Interactive D3.js** | Custom viz | N/A | `glass-card` |
| **Code comparison** | Side-by-side | N/A | `comparison-section` (STS) |
| **Concept explanation** | Concept card | N/A | `.concept-card` |
| **Text-heavy content** | Knowledge panel | N/A | `glass-card` + max-width: 900px |

### Navigation Pattern Decision Tree

```
What level is this page?
    |
    ├─→ HOME PAGE
    |    • Hero section with logo
    |    • No breadcrumb
    |    • Pattern: Hero + feature grids
    |
    ├─→ FIRST LEVEL (e.g., /orchestrators/index.html)
    |    • Breadcrumb: Home → Section
    |    • Logo: YES (below breadcrumb)
    |    • Pattern: Breadcrumb + Logo + Content
    |
    ├─→ SECOND LEVEL (e.g., /orchestrators/planning-system.html)
    |    • Breadcrumb: Home → Section → Page
    |    • Logo: NO
    |    • Pattern: Breadcrumb + Content
    |
    └─→ STS SHOWCASE PAGE
         • Site header (branded navigation)
         • No breadcrumb
         • Pattern: Site-header + Hero + Comparisons
```

### CSS File Selection Guide

```
Which CSS file should I link?
    |
    ├─→ Is this an STS page?
    |    • Link: main.css + sts.css
    |    • Body class: sts-showcase
    |
    └─→ Is this a standard page?
         • Link: main.css only
         • No special body class
```

### Common Patterns

**Standard Content Card:**
```html
<div class="glass-card">
    <h2>Title</h2>
    <p>Content</p>
</div>
```

**Centered Content Card:**
```html
<div class="glass-card" style="max-width: 1400px; margin: 0 auto var(--spacing-2xl);">
    <h2>Title</h2>
</div>
```

**Metric Grid:**
```html
<div style="display: flex; gap: 1.5rem; justify-content: center;">
    <div class="metric-card">
        <div class="metric-value">40+</div>
        <div class="metric-label">Label</div>
    </div>
</div>
```

**Workflow Phases:**
```html
<div class="workflow-phases">
    <div class="phase-card">
        <span class="phase-number">1</span>
        <span class="phase-icon">📋</span>
        <div class="phase-title">Title</div>
        <p class="phase-description">Description</p>
    </div>
</div>
```

### Responsive Design Quick Reference

**Essential Meta Tags:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
```

**Breakpoint Reference:**
```
320px  = Small mobile (iPhone SE)
375px  = Mobile (iPhone 12/13/14)
480px  = Mobile landscape
768px  = Tablet portrait
1024px = Tablet landscape / Desktop
1440px = Laptop
1920px = Large desktop
```

**Touch Target Sizes:**
```
Minimum: 44px × 44px (Apple/Google standard)
Optimal: 48px × 48px (iOS recommendation)
Spacing: 8px minimum between targets
```

**Typography Scale:**
```
Mobile:  16px body, 28px H1, 24px H2
Tablet:  16px body, 36px H1, 28px H2
Desktop: 16px body, 40px H1, 30px H2
```

**Container Widths:**
```
Mobile:   100% (padding: 1rem)
Tablet:   100% (padding: 1.5rem)
Desktop:  1200px max-width (padding: 2rem)
Large:    1400px max-width (padding: 2.5rem)
```

**Performance Tips:**
- Use `srcset` for responsive images
- Lazy load images with `loading="lazy"`
- Reduce blur on mobile (8px vs 10px)
- Debounce resize events (150ms)
- Use `will-change` sparingly

---

## 🔧 Tools & Validation

### HTML Quality Tools (MANDATORY)

```bash
# Step 1: Remove inline styles
python3 cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Step 2: Validate HTML syntax
python3 cortex-toolkit/documentation/html-tools/html_validator.py
```

**Expected Output:**
```
✅ All files syntactically correct
✅ 0 inline styles found
```

### Browser Testing

**Breakpoints to Test:**
- 320px (iPhone SE, small mobile)
- 375px (iPhone 12/13/14)
- 414px (iPhone 12/13/14 Pro Max)
- 480px (mobile landscape)
- 768px (iPad portrait, tablet)
- 1024px (iPad landscape, desktop)
- 1440px (laptop)
- 1920px (large desktop)

**Device Testing Matrix:**

| Device Category | Screen Size | Test Focus |
|----------------|-------------|------------|
| Small Mobile | 320px-374px | Text readability, touch targets, card stacking |
| Mobile | 375px-479px | Navigation, content flow, button spacing |
| Mobile Landscape | 480px-767px | Horizontal layout, image scaling |
| Tablet Portrait | 768px-1023px | Grid layouts, sidebar positioning |
| Tablet Landscape | 1024px-1439px | Multi-column layouts, full features |
| Desktop | 1440px+ | Full experience, max-width constraints |

**Testing Checklist:**
- [ ] **Navigation:** Breadcrumb visible and functional on all sizes
- [ ] **Logo:** Scales appropriately (200px mobile → 300px desktop)
- [ ] **Cards:** Stack vertically on mobile, grid on desktop
- [ ] **Scroll:** No horizontal scroll at any breakpoint
- [ ] **Touch targets:** All interactive elements ≥44px on mobile
- [ ] **Text:** Readable without zooming (minimum 16px body)
- [ ] **Images:** Scale proportionally, no overflow
- [ ] **Forms:** Input fields full-width on mobile
- [ ] **Tables:** Scroll horizontally or stack rows on mobile
- [ ] **Diagrams:** Responsive SVG/D3.js, readable on small screens
- [ ] **Performance:** Fast load on 3G network (<3s)
- [ ] **Orientation:** Works in portrait and landscape

### Mobile Performance Optimization

**Image Optimization:**
```html
<!-- Use srcset for responsive images -->
<img 
    src="image-800w.jpg"
    srcset="image-400w.jpg 400w,
            image-800w.jpg 800w,
            image-1200w.jpg 1200w"
    sizes="(max-width: 480px) 100vw,
           (max-width: 1024px) 50vw,
           800px"
    alt="Description"
    loading="lazy">
```

**CSS Performance:**
```css
/* Use transform instead of position for animations */
.animated-element {
    transform: translateX(0);
    transition: transform 0.3s ease;
}

.animated-element:hover {
    transform: translateX(10px);
}

/* Optimize backdrop-filter for mobile */
@media (max-width: 768px) {
    .glass-card {
        backdrop-filter: blur(8px); /* Reduced from 10px */
    }
}

/* Use will-change sparingly */
.high-performance-animation {
    will-change: transform;
}
```

**JavaScript Optimization:**
```javascript
// Debounce resize events
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        // Handle resize
    }, 150);
});

// Use Intersection Observer for lazy loading
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Load content
        }
    });
});
```

---

## 📧 Contact

**Questions or Suggestions:**  
Asif Hussain | [GitHub](https://github.com/asifhussain60/CORTEX)

---

## 📊 Standards Summary

### What's New in v2.0

✅ **Mobile-First Responsive Design** - Complete breakpoint system (320px-1920px+)  
✅ **Accessibility Standards** - WCAG 2.1 AA compliance throughout  
✅ **Knowledge Library Guidelines** - Text-focused, diagram-driven content  
✅ **Logo Display Rules** - First-level only (reduces visual clutter)  
✅ **Touch Target Standards** - Minimum 44px for all interactive elements  
✅ **Performance Optimizations** - Lazy loading, reduced blur on mobile  
✅ **Comprehensive Testing Matrix** - Device-specific test requirements  

### Key Principles (The "CORTEX Way")

1. **Mobile-First:** Design starts at 320px, scales up
2. **Touch-Friendly:** All buttons/links ≥44px on mobile
3. **Accessible:** WCAG 2.1 AA contrast, keyboard navigation, ARIA labels
4. **Performant:** <3s load on 3G, lazy images, optimized blur
5. **Scannable:** Visual hierarchy, diagrams > code, concept cards
6. **Consistent:** Single CSS source (`main.css` + optional `sts.css`)
7. **Semantic:** Proper HTML5 landmarks, heading hierarchy

### Document Authority

This document is the **definitive source of truth** for:
- Layout patterns (breadcrumb, logo, cards)
- Responsive breakpoints and behavior
- Typography scales across devices
- Color contrast and accessibility
- Touch target sizing
- Knowledge Library content strategy
- Mobile optimization techniques

**Supersedes:** All previous styling documentation for CORTEX 4.0

---

**Version:** 2.0.0  
**Last Updated:** December 28, 2025  
**© 2025 Asif Hussain. All rights reserved.**
