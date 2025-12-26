# CSS Centralization Rule - Implementation Guide

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 9, 2025  
**Status:** PRODUCTION  
**Tier 0 Rule:** INLINE_CSS_PROHIBITION

---

## 🎯 Problem Statement

**Current Behavior:** CORTEX (and developers) create inline CSS during rapid prototyping for convenience, leading to:
- Scattered styles across hundreds of files
- Duplicate color/spacing definitions (same value repeated 50+ times)
- Impossible maintenance ("Where is this blue coming from?")
- No theming capability (can't swap dark mode)
- Performance issues (inline styles can't be cached)

**Root Cause:** No enforcement mechanism to prevent inline CSS or mandate centralization.

---

## 🏗️ Solution: INLINE_CSS_PROHIBITION Rule

### Overview

A Tier 0 governance rule that BLOCKS inline CSS and mandates centralization to CSS files. Integrated with Planning System REFACTOR phase for automatic validation.

### Rule Structure

```
┌─────────────────────────────────────────────────────────────┐
│              INLINE_CSS_PROHIBITION WORKFLOW                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  GREEN Phase: Rapid prototyping (inline CSS allowed)         │
│     │                                                         │
│     └─→ Focus: Get functionality working                     │
│                                                               │
│  REFACTOR Phase: CSS Centralization (MANDATORY)              │
│     │                                                         │
│     ├─→ Step 1: Detect inline styles (grep patterns)         │
│     ├─→ Step 2: Extract to CSS files                         │
│     ├─→ Step 3: Replace inline with classes                  │
│     ├─→ Step 4: Verify visual parity (screenshots)           │
│     ├─→ Step 5: Run tests (SKULL_TEST_BEFORE_CLAIM)          │
│     └─→ Step 6: Commit only if zero inline styles            │
│                                                               │
│  Enforcement: Brain Protector blocks commit with inline CSS  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detection Patterns

### Pattern 1: HTML/JSX Inline Styles

**Blocked:**
```html
<!-- ❌ BLOCKED: Inline style attribute -->
<div style="color: blue; margin: 10px;">Content</div>

<!-- ❌ BLOCKED: JSX inline styles -->
<div style={{ color: 'blue', margin: '10px' }}>Content</div>
```

**Correct:**
```html
<!-- ✅ CORRECT: CSS class -->
<div class="content-box">Content</div>
```

```css
/* styles.css */
.content-box {
  color: blue;
  margin: 10px;
}
```

---

### Pattern 2: Embedded `<style>` Tags

**Blocked:**
```html
<!-- ❌ BLOCKED: Embedded style block -->
<head>
  <style>
    .header { background: red; }
    .footer { color: blue; }
  </style>
</head>
```

**Correct:**
```html
<!-- ✅ CORRECT: External CSS -->
<head>
  <link rel="stylesheet" href="styles.css">
</head>
```

```css
/* styles.css */
.header { background: red; }
.footer { color: blue; }
```

---

### Pattern 3: JavaScript Style Manipulation

**Blocked:**
```javascript
// ❌ BLOCKED: Direct style manipulation
element.style.color = 'red';
element.style.display = 'none';
element.style.fontSize = '16px';
element.setAttribute('style', 'color: red; margin: 10px');
element.style.cssText = 'color: red; margin: 10px';
```

**Correct:**
```javascript
// ✅ CORRECT: CSS class toggling
element.classList.add('text-danger');
element.classList.add('hidden');
element.classList.toggle('active');
element.classList.remove('visible');
```

```css
/* styles.css */
.text-danger { color: red; }
.hidden { display: none; }
.active { font-size: 16px; }
.visible { display: block; }
```

---

### Pattern 4: jQuery/Framework Style Methods

**Blocked:**
```javascript
// ❌ BLOCKED: jQuery .css()
$('.element').css('color', 'red');
$('.element').css({ color: 'red', margin: '10px' });

// ❌ BLOCKED: Angular/Vue inline styles
<div [style.color]="'red'">Content</div>
<div :style="{ color: 'red' }">Content</div>
```

**Correct:**
```javascript
// ✅ CORRECT: jQuery class toggling
$('.element').addClass('text-danger');
$('.element').toggleClass('hidden');

// ✅ CORRECT: Angular/Vue class binding
<div [class.text-danger]="isError">Content</div>
<div :class="{ 'text-danger': isError }">Content</div>
```

---

## 📁 CSS Organization Patterns

### Pattern 1: Component-Scoped CSS (Recommended)

**Structure:**
```
src/
├── components/
│   ├── Header/
│   │   ├── Header.jsx
│   │   └── Header.module.css    ← Scoped to Header
│   ├── Button/
│   │   ├── Button.jsx
│   │   └── Button.module.css    ← Scoped to Button
│   └── Card/
│       ├── Card.jsx
│       └── Card.module.css      ← Scoped to Card
└── App.jsx
```

**Benefits:**
- ✅ Encapsulation (styles don't leak)
- ✅ No naming conflicts (`.button` in multiple components OK)
- ✅ Clear ownership (styles live with component)
- ✅ Easy to delete (delete folder = delete all related code)

**Example:**
```jsx
// Button.jsx
import styles from './Button.module.css';

function Button({ children, variant = 'primary' }) {
  return (
    <button className={`${styles.btn} ${styles[`btn-${variant}`]}`}>
      {children}
    </button>
  );
}
```

```css
/* Button.module.css */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-secondary {
  background: var(--color-secondary);
  color: white;
}
```

---

### Pattern 2: Feature-Based CSS

**Structure:**
```
src/
├── features/
│   ├── authentication/
│   │   ├── components/
│   │   │   ├── LoginForm.jsx
│   │   │   └── RegisterForm.jsx
│   │   └── styles/
│   │       ├── login.css
│   │       └── register.css
│   └── dashboard/
│       ├── components/
│       │   ├── DashboardHeader.jsx
│       │   └── DashboardWidget.jsx
│       └── styles/
│           └── dashboard.css
```

**Benefits:**
- ✅ Feature cohesion (all auth styles together)
- ✅ Easy to locate (styles in feature folder)
- ✅ Team ownership (frontend team owns feature CSS)

---

### Pattern 3: Atomic/Utility CSS (Tailwind-style)

**Structure:**
```
src/
├── styles/
│   ├── global.css       ← Global resets, base styles
│   ├── variables.css    ← CSS variables (colors, spacing, fonts)
│   ├── utilities.css    ← Utility classes (.flex, .grid, .hidden)
│   └── components.css   ← Component classes (.btn, .card, .modal)
└── index.js
```

**Benefits:**
- ✅ Highly reusable (compose utilities)
- ✅ Minimal CSS duplication (define once)
- ✅ Fast development (use existing utilities)

**Example:**
```css
/* utilities.css */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-4 { gap: 16px; }
.hidden { display: none; }
.text-center { text-align: center; }
.text-danger { color: var(--color-danger); }
.bg-primary { background: var(--color-primary); }
.p-4 { padding: 16px; }
.m-4 { margin: 16px; }
```

Usage:
```html
<div class="flex items-center justify-between gap-4 p-4">
  <h1 class="text-center">Title</h1>
  <button class="bg-primary text-white p-4">Click</button>
</div>
```

---

## 🎨 CSS Variables for Theming

### Design Tokens (variables.css)

```css
/* variables.css */
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-danger: #dc3545;
  --color-info: #17a2b8;
  
  --color-background: #ffffff;
  --color-text: #212529;
  --color-border: #dee2e6;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-mono: 'Courier New', monospace;
  
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 20px;
  --font-size-xl: 24px;
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Border Radius */
  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 8px;
  --radius-full: 9999px;
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}

/* Dark mode override */
[data-theme="dark"] {
  --color-primary: #0d6efd;
  --color-background: #1a1a1a;
  --color-text: #ffffff;
  --color-border: #343a40;
}
```

### Usage in Components

```css
/* Button.module.css */
.btn {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
```

---

## 🔄 Migration Workflow

### Step 1: Detect Inline Styles

**Command:**
```bash
# Find HTML style attributes
grep -r 'style="' src/

# Find JSX inline styles
grep -r 'style={{' src/

# Find JS style manipulation
grep -r '\.style\.' src/

# Find jQuery .css()
grep -r '\.css(' src/

# Find embedded <style> tags
grep -r '<style>' src/
```

**Expected Output:**
```
src/components/Header.jsx:15:    <div style={{ background: 'blue' }}>
src/pages/Dashboard.jsx:42:      element.style.display = 'none';
src/templates/index.html:8:      <style>.header { color: red; }</style>
```

---

### Step 2: Extract to CSS Files

**Before (inline styles):**
```jsx
// Header.jsx
function Header({ userName }) {
  return (
    <header style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '20px',
      backgroundColor: '#007bff',
      color: 'white',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h1 style={{ fontSize: '24px', margin: 0 }}>My App</h1>
      <span style={{ fontSize: '14px' }}>Welcome, {userName}</span>
    </header>
  );
}
```

**After (centralized CSS):**
```jsx
// Header.jsx
import './Header.module.css';

function Header({ userName }) {
  return (
    <header className="header">
      <h1 className="header-title">My App</h1>
      <span className="header-user">Welcome, {userName}</span>
    </header>
  );
}
```

```css
/* Header.module.css */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  background-color: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-md);
}

.header-title {
  font-size: var(--font-size-xl);
  margin: 0;
}

.header-user {
  font-size: var(--font-size-sm);
}
```

---

### Step 3: Replace JavaScript Style Manipulation

**Before:**
```javascript
// modal.js
function openModal() {
  const modal = document.getElementById('modal');
  const overlay = document.getElementById('overlay');
  const body = document.body;
  
  modal.style.display = 'block';
  modal.style.opacity = '1';
  overlay.style.display = 'block';
  overlay.style.opacity = '0.5';
  body.style.overflow = 'hidden';
}

function closeModal() {
  modal.style.display = 'none';
  modal.style.opacity = '0';
  overlay.style.display = 'none';
  overlay.style.opacity = '0';
  body.style.overflow = 'auto';
}
```

**After:**
```javascript
// modal.js
function openModal() {
  const modal = document.getElementById('modal');
  const overlay = document.getElementById('overlay');
  const body = document.body;
  
  modal.classList.add('modal-visible');
  overlay.classList.add('overlay-active');
  body.classList.add('no-scroll');
}

function closeModal() {
  modal.classList.remove('modal-visible');
  overlay.classList.remove('overlay-active');
  body.classList.remove('no-scroll');
}
```

```css
/* modal.css */
.modal {
  display: none;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.modal-visible {
  display: block;
  opacity: 1;
}

.overlay {
  display: none;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.overlay-active {
  display: block;
  opacity: 0.5;
}

body.no-scroll {
  overflow: hidden;
}
```

---

## 🔧 Planning System Integration

### REFACTOR Phase Validation

**Location:** `cortex-brain/manifests/orchestrators/planning-system-manifest.yaml`

**Add to REFACTOR phase checklist:**
```yaml
refactor_phase:
  mandatory_validations:
    - orphaned_code_removal       # REFACTOR_CODE_CLEANUP_ENFORCEMENT
    - duplicate_code_detection    # HOLISTIC_CODE_DISCOVERY_ENFORCEMENT
    - inline_css_migration        # INLINE_CSS_PROHIBITION ← NEW
    - test_coverage_verification
    - documentation_update
    - visual_regression_check     # SKULL_VISUAL_REGRESSION
```

### Implementation Code

**File:** `src/orchestrators/planning_system_2.py`

```python
def validate_refactor_phase_complete(project_path: str) -> dict:
    """Validate REFACTOR phase completion including CSS centralization"""
    
    validations = {
        'orphaned_code_removed': validate_no_orphaned_code(project_path),
        'duplicates_consolidated': validate_no_duplicates(project_path),
        'inline_css_migrated': validate_no_inline_css(project_path),  # NEW
        'tests_passing': run_tests(project_path),
        'documentation_updated': validate_docs(project_path)
    }
    
    all_passed = all(validations.values())
    
    return {
        'passed': all_passed,
        'validations': validations,
        'message': 'REFACTOR phase complete' if all_passed else 'REFACTOR phase incomplete'
    }


def validate_no_inline_css(project_path: str) -> bool:
    """
    Validate no inline CSS exists in project
    
    Detection patterns:
    - HTML: style="..."
    - JSX: style={{...}}
    - JS: .style.property = 
    - JS: .css(...)
    - HTML: <style>...</style>
    """
    
    patterns = [
        r'style="[^"]+"',                    # HTML style attribute
        r'style={{[^}]+}}',                  # JSX inline styles
        r'\.style\.[a-zA-Z]+\s*=',           # JS .style.property
        r'\.css\(["\'][^"\']*["\']',         # jQuery .css()
        r'<style[^>]*>',                     # Embedded <style> tags
        r'\.setAttribute\(["\']style["\']',  # setAttribute('style')
        r'\.cssText\s*=',                    # .style.cssText
    ]
    
    violations = []
    
    # Search source files
    extensions = ['.html', '.jsx', '.tsx', '.js', '.ts', '.vue']
    for root, dirs, files in os.walk(project_path):
        # Skip node_modules, dist, build
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '.git']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        if matches:
                            violations.append({
                                'file': os.path.relpath(file_path, project_path),
                                'pattern': pattern,
                                'matches': matches[:5],  # First 5 matches
                                'count': len(matches)
                            })
    
    if violations:
        # Print detailed violation report
        print("❌ INLINE_CSS_PROHIBITION: Inline styles detected")
        print("\nViolations:")
        for v in violations:
            print(f"\n  File: {v['file']}")
            print(f"  Pattern: {v['pattern']}")
            print(f"  Count: {v['count']}")
            print(f"  Examples: {v['matches']}")
        
        print("\n→ Run CSS centralization migration")
        print("→ Extract inline styles to CSS files")
        print("→ Replace with CSS classes")
        
        return False
    
    print("✅ INLINE_CSS_PROHIBITION: No inline styles detected")
    return True
```

---

## 🚨 Exceptions (Rare Cases)

### Exception 1: Dynamic Values from Backend

**Scenario:** Color/position values from API

**Allowed (with comment):**
```jsx
{/* INLINE_CSS_PROHIBITION exception: Dynamic color from user profile */}
<div style={{ backgroundColor: user.themeColor }}>
  User content
</div>
```

**Better Alternative (CSS variables):**
```javascript
// Set CSS variable instead
document.documentElement.style.setProperty('--user-theme-color', user.themeColor);
```

```css
/* styles.css */
.user-content {
  background-color: var(--user-theme-color, #007bff);
}
```

---

### Exception 2: Canvas/SVG Animations

**Scenario:** Computed positions/transforms

**Allowed:**
```javascript
// Animation frame updates
canvas.style.transform = `translate(${x}px, ${y}px) rotate(${angle}deg)`;
```

**Better Alternative (CSS animations with variables):**
```javascript
// Update CSS variables
canvas.style.setProperty('--x', `${x}px`);
canvas.style.setProperty('--y', `${y}px`);
canvas.style.setProperty('--angle', `${angle}deg`);
```

```css
.canvas {
  transform: translate(var(--x, 0), var(--y, 0)) rotate(var(--angle, 0deg));
}
```

---

### Exception 3: Third-Party Libraries

**Scenario:** Library requires inline styles

**Approach:** Wrap in component, isolate inline styles

```jsx
// ChartWrapper.jsx
{/* INLINE_CSS_PROHIBITION exception: Chart.js requires inline styles */}
<div className="chart-container">
  <canvas ref={chartRef} />
</div>
```

---

## 📊 Success Metrics

```yaml
success_criteria:
  inline_css_elimination:
    target: 0 instances
    measurement: "Inline style patterns in source code"
    baseline: "~150 instances (pre-rule)"
  
  css_file_organization:
    target: 100%
    measurement: "Components with dedicated CSS files"
    baseline: "~40% (pre-rule)"
  
  maintenance_efficiency:
    target: 60%
    measurement: "Reduction in 'where is this style?' debug time"
    baseline: "~3 hours/week on style debugging"
  
  theming_capability:
    target: "Full dark mode support"
    measurement: "Theme switching without code changes"
    baseline: "No theming support"
```

---

## 🔗 Related Documentation

- **Rule Definition:** `cortex-brain/brain-protection-rules.yaml` (INLINE_CSS_PROHIBITION)
- **Planning System:** `cortex-brain/manifests/orchestrators/planning-system-manifest.yaml`
- **Visual Regression:** SKULL_VISUAL_REGRESSION rule
- **Code Style:** CODE_STYLE_CONSISTENCY rule

---

**Version History:**
- **1.0** (2025-12-09): Initial implementation

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
