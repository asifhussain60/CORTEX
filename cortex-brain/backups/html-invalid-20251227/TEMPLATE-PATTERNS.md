# HTML Template Patterns - Extracted from Valid Files
**Date:** December 27, 2025  
**Purpose:** Document template patterns from 26 valid HTML files for consistent regeneration

---

## 📋 Base Template Structure

### Complete HTML5 Document
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - CORTEX 4.0</title>
    <link rel="stylesheet" href="../assets/css/main.css">
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo.png">
</head>
<body>
    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb">
        <a href="../index.html">Home</a>
        <span class="breadcrumb-separator">›</span>
        <a href="index.html">Category</a>
        <span class="breadcrumb-separator">›</span>
        <span class="breadcrumb-current">Page Title</span>
    </nav>

    <!-- Hero Section (orchestrators/features only) -->
    <section class="section">
        <div class="container">
            <div class="glass-card">
                <div>
                    <div class="icon">🎯</div>
                    <div>
                        <h1>Page Title</h1>
                        <p>Natural language efficiency statement...</p>
                        <a href="../technical/orchestrators/page.html" class="btn btn-primary">
                            🎨 View Interactive Diagrams & Visualizations →
                        </a>
                    </div>
                </div>
                
                <!-- Key Metrics Grid -->
                <div class="metrics-grid">
                    <div>
                        <div class="metric-value">8</div>
                        <div class="metric-label">Phases</div>
                    </div>
                    <div>
                        <div class="metric-value">100%</div>
                        <div class="metric-label">Automated</div>
                    </div>
                    <div>
                        <div class="metric-value">&lt; 5min</div>
                        <div class="metric-label">Avg Execution</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Executive Summary -->
    <section class="section">
        <div class="container">
            <h2>Executive Summary</h2>
            <div class="glass-card">
                <p>Content here...</p>
            </div>
        </div>
    </section>

    <!-- Main Content Sections -->
    <section class="section">
        <div class="container">
            <h2>Section Title</h2>
            <div class="glass-card">
                <p>Content...</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <p>&copy; 2025 CORTEX 4.0 | <a href="../index.html">Home</a></p>
        </div>
    </footer>

    <script src="../assets/js/main.js" defer></script>
</body>
</html>
```

---

## 🎨 Glassmorphism Classes (from main.css)

### Layout Classes
- `.section` - Full-width section container
- `.container` - Centered content container (max-width)
- `.glass-card` - Primary glass morphism card with shadow
- `.glass-card-flat` - Flat glass card (no shadow, for nested content)

### Typography
- `h1`, `h2`, `h3` - Pre-styled headings (no custom styles needed)
- `.breadcrumb` - Navigation breadcrumb container
- `.breadcrumb-separator` - Breadcrumb separator (›)
- `.breadcrumb-current` - Current page in breadcrumb (no link)

### Components
- `.icon` - Icon container (emoji or SVG)
- `.btn` - Button base class
- `.btn-primary` - Primary action button (glassmorphism)
- `.metrics-grid` - Key metrics display (CSS Grid)
- `.metric-value` - Large metric number
- `.metric-label` - Metric description

### Interactive
- `.collapsible` - Collapsible section container
- `.collapsible-header` - Clickable header to expand/collapse
- `.collapsible-icon` - Expand/collapse indicator (▼)
- `.collapsible-content` - Hidden content (revealed on click)

### Code Blocks
- `<pre>` - Preformatted text (auto-styled)
- `<code>` - Inline code (auto-styled)
- Use plain HTML tags, NO `.code-block` class needed

---

## 📐 Layout Patterns

### 1. Hero Section with Icon + Title + Metrics
```html
<section class="section">
    <div class="container">
        <div class="glass-card">
            <div>
                <div class="icon">🎯</div>
                <div>
                    <h1>Feature Name</h1>
                    <p>Efficiency statement in natural language...</p>
                    <a href="../technical/orchestrators/page.html" class="btn btn-primary">
                        🎨 View Interactive Diagrams & Visualizations →
                    </a>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div>
                    <div class="metric-value">8</div>
                    <div class="metric-label">Phases</div>
                </div>
                <div>
                    <div class="metric-value">100%</div>
                    <div class="metric-label">Automated</div>
                </div>
                <div>
                    <div class="metric-value">&lt; 5min</div>
                    <div class="metric-label">Execution Time</div>
                </div>
            </div>
        </div>
    </div>
</section>
```

### 2. Collapsible Phase Breakdown
```html
<section class="section">
    <div class="container">
        <h2>Workflow Phases</h2>
        
        <!-- Phase 1 -->
        <div class="collapsible">
            <div class="collapsible-header glass-card">
                <h3>📊 Phase 1: Pre-Flight Checks</h3>
                <span class="collapsible-icon">▼</span>
            </div>
            <div class="collapsible-content glass-card-flat">
                <p><strong>Purpose:</strong> Validate system readiness</p>
                <p><strong>What happens:</strong></p>
                <ul>
                    <li><strong>Check 1:</strong> Description</li>
                    <li><strong>Check 2:</strong> Description</li>
                </ul>
                <p><strong>Sample output:</strong></p>
                <pre>✅ Pre-flight: 5/5 checks passed</pre>
            </div>
        </div>
        
        <!-- Phase 2 -->
        <div class="collapsible">
            <div class="collapsible-header glass-card">
                <h3>⚡ Phase 2: Execution</h3>
                <span class="collapsible-icon">▼</span>
            </div>
            <div class="collapsible-content glass-card-flat">
                <p>Content...</p>
            </div>
        </div>
    </div>
</section>
```

### 3. Executive Summary Section
```html
<section class="section">
    <div class="container">
        <h2>Executive Summary</h2>
        <div class="glass-card">
            <p>
                Brief overview of the feature/orchestrator in 2-3 sentences.
                Focus on business value and efficiency gains.
            </p>
        </div>
    </div>
</section>
```

### 4. Integration Section
```html
<section class="section">
    <div class="container">
        <h2>Ecosystem Integration</h2>
        <div class="glass-card">
            <h3>Connects with:</h3>
            <ul>
                <li>
                    <a href="planning-system.html">Planning System</a> - 
                    Shares plan manifest structure
                </li>
                <li>
                    <a href="tdd-orchestrator.html">TDD Orchestrator</a> - 
                    Auto-includes TDD in all plans
                </li>
            </ul>
        </div>
    </div>
</section>
```

### 5. Usage Examples Section
```html
<section class="section">
    <div class="container">
        <h2>Usage Examples</h2>
        <div class="glass-card">
            <h3>Example 1: Basic Usage</h3>
            <pre>User: plan feature authentication
CORTEX: Creating 8-phase plan with TDD...</pre>
            
            <h3>Example 2: Advanced Usage</h3>
            <pre>User: execute all phases autonomously
CORTEX: Autonomous execution engaged...</pre>
        </div>
    </div>
</section>
```

---

## 🚫 FORBIDDEN Patterns

### ❌ NO Self-Closing Tags
```html
<!-- ❌ WRONG -->
</br>
</img>
</script>

<!-- ✅ CORRECT -->
<br>
<br/>
<img src="..." alt="...">
<script src="..."></script>
```

### ❌ NO Inline Styles
```html
<!-- ❌ WRONG -->
<div style="width: 200px; margin: 10px;">

<!-- ✅ CORRECT -->
<div class="glass-card">
```

### ❌ NO Custom CSS Files
```html
<!-- ❌ WRONG -->
<link rel="stylesheet" href="custom.css">
<style>
    .custom-class { ... }
</style>

<!-- ✅ CORRECT -->
<link rel="stylesheet" href="../assets/css/main.css">
```

---

## 📊 Breadcrumb Patterns

### Features Page
```html
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">›</span>
    <a href="index.html">Features</a>
    <span class="breadcrumb-separator">›</span>
    <span class="breadcrumb-current">Feature Name</span>
</nav>
```

### Orchestrator Page (Technical)
```html
<nav class="breadcrumb">
    <a href="../../index.html">Home</a>
    <span class="breadcrumb-separator">›</span>
    <a href="../index.html">Technical</a>
    <span class="breadcrumb-separator">›</span>
    <a href="index.html">Orchestrators</a>
    <span class="breadcrumb-separator">›</span>
    <span class="breadcrumb-current">Orchestrator Name</span>
</nav>
```

### Architecture Page
```html
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">›</span>
    <a href="index.html">Architecture</a>
    <span class="breadcrumb-separator">›</span>
    <span class="breadcrumb-current">Component Name</span>
</nav>
```

### Getting Started Page
```html
<nav class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-separator">›</span>
    <a href="index.html">Getting Started</a>
    <span class="breadcrumb-separator">›</span>
    <span class="breadcrumb-current">Tutorial Step</span>
</nav>
```

---

## 🎯 Icon Selection Guide

| Category | Icon | Usage |
|----------|------|-------|
| Planning | 🎯 | Planning System, Strategic planning |
| TDD | ✅ | TDD Orchestrator, Test coverage |
| Execution | ⚡ | Autonomous execution, Fast operations |
| ADO | 📋 | Azure DevOps integration |
| Sanitization | 🔒 | Code sanitization, Security |
| Cleanup | 🧹 | Cleanup orchestrator, File removal |
| Debug | 🔍 | Debug orchestrator, Investigation |
| Git | 📦 | Git checkpoint, Version control |
| Dashboard | 📊 | Metrics, Analytics, Dashboards |
| Maintenance | 🔧 | System maintenance, Health checks |
| Pre-flight | ✈️ | Pre-flight checks, Validation |
| Refinement | ✨ | Code refinement, Optimization |
| Rollback | ↩️ | Rollback orchestrator, Undo |
| System Integrity | 🛡️ | Security, System checks |
| Architecture | 🏛️ | Architecture review, Design |
| Brain | 🧠 | Working memory, Intelligence |
| Agent | 🤖 | Agent system, AI agents |
| Tutorial | 📚 | Learning, Documentation |
| FAQ | ❓ | Questions, Help |

---

## 🔗 Cross-Reference Patterns

### Link to Related Orchestrator
```html
<p>
    See also: <a href="planning-system.html">Planning System</a> for 
    automated plan generation.
</p>
```

### Link to Architecture Document
```html
<p>
    Technical details: <a href="../architecture/four-tier-brain.html">
    Four-Tier Brain Architecture</a>
</p>
```

### Link to Getting Started
```html
<p>
    New to CORTEX? Start with our 
    <a href="../getting-started/tutorial.html">5-minute tutorial</a>
</p>
```

---

## 📱 Responsive Design (Auto-Applied)

All classes from main.css are responsive by default:

- **Mobile (320px-767px):** Single column, stacked cards
- **Tablet (768px-1023px):** 2 columns for metrics-grid
- **Desktop (1024px+):** 3-6 columns for metrics-grid

**NO media queries needed in HTML!**

---

## ♿ Accessibility (WCAG 2.1 Level AA)

### Required Attributes
```html
<!-- Images MUST have alt text -->
<img src="..." alt="Descriptive text">

<!-- Links MUST have descriptive text -->
<a href="...">Click here</a> <!-- ❌ WRONG -->
<a href="...">View Planning System documentation</a> <!-- ✅ CORRECT -->

<!-- Buttons MUST have aria-label if icon-only -->
<button aria-label="Expand section">▼</button>
```

### Color Contrast
- All text meets 4.5:1 contrast ratio (auto-applied by main.css)
- Focus indicators visible (auto-applied)

### Keyboard Navigation
- All interactive elements reachable by Tab key (auto-applied)
- Collapsible sections toggle with Enter/Space (main.js)

---

## 🎨 D3.js/Mermaid Diagram Integration

### D3.js Diagram Container
```html
<section class="section">
    <div class="container">
        <h2>Interactive Workflow Diagram</h2>
        <div class="glass-card">
            <div id="d3-diagram-container"></div>
        </div>
    </div>
</section>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
    // D3.js visualization code here
    // Use glassmorphism color palette from main.css
</script>
```

### Mermaid Diagram
```html
<section class="section">
    <div class="container">
        <h2>Workflow Diagram</h2>
        <div class="glass-card">
            <pre class="mermaid">
graph TD
    A[Start] --> B[Phase 1]
    B --> C[Phase 2]
    C --> D[End]
            </pre>
        </div>
    </div>
</section>

<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true });</script>
```

---

## ✅ Validation Checklist

Before committing regenerated HTML:

- [ ] DOCTYPE and HTML5 structure present
- [ ] meta charset and viewport tags included
- [ ] Title format: "Page Title - CORTEX 4.0"
- [ ] Link to main.css (correct relative path)
- [ ] Breadcrumb navigation (except home page)
- [ ] Icon in hero section (orchestrators/features only)
- [ ] NO inline styles (style="...")
- [ ] NO self-closing </br> or </img> tags
- [ ] NO custom CSS files or <style> tags
- [ ] Proper semantic HTML5 (section, nav, main, footer)
- [ ] All images have alt text
- [ ] All links have descriptive text
- [ ] Code examples use <pre> or <code> tags
- [ ] Cross-references work (no broken links)
- [ ] Footer includes copyright and home link
- [ ] Script tag for main.js at end of body

---

**End of Template Patterns Document**
