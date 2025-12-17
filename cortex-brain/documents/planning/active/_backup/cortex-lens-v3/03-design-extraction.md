# CORTEX Lens v3.0 - Design Extraction Strategy

**Version:** 1.0  
**Date:** December 14, 2025  
**Author:** Asif Hussain  
**Phase:** Phase 0 - Planning & Preparation  
**Status:** Strategy Defined

---

## 🎯 Objective

Extract all design patterns, CSS architecture, component styles, and glassmorphism patterns from CORTEX Admin Dashboard for migration to CORTEX Lens v3.0 with zero external dependencies.

---

## 📋 Admin Dashboard CSS Architecture

**Source Location:** `cortex-brain/dashboards/ui/styles/`

### 8-Layer CSS Architecture

```
styles/
├── 1-reset.css           # Browser normalization (reset margins, box-sizing)
├── 2-variables.css       # CSS custom properties (colors, spacing, typography)
├── 3-typography.css      # Font definitions, text styles, headings
├── 4-layouts.css         # Grid systems, flexbox utilities, spacing
├── 5-components.css      # Card, button, form, badge, tab components
├── 6-utilities.css       # Helper classes (text-center, mb-4, etc.)
├── 7-animations.css      # Keyframes, transitions, loading animations
└── 8-accessibility.css   # Screen reader, focus states, skip links
```

**Extraction Priority:**
1. **Layer 2 (variables.css):** ~200 CSS variables (colors, spacing, shadows, borders)
2. **Layer 3 (typography.css):** Font scales, line heights, letter spacing
3. **Layer 5 (components.css):** ~30 component styles (cards, buttons, badges, forms, tabs)
4. **Layer 7 (animations.css):** Loading spinners, skeleton loaders, transitions

---

## 🌟 Glassmorphism Pattern Extraction

**Glassmorphism Characteristics:**
- `backdrop-filter: blur(10px) saturate(180%)`
- `background: rgba(255, 255, 255, 0.1)`
- `border: 1px solid rgba(255, 255, 255, 0.18)`
- `box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37)`

### Pattern Categories

1. **Card Glassmorphism**
   ```css
   .glass-card {
     backdrop-filter: blur(10px) saturate(180%);
     background: rgba(255, 255, 255, 0.1);
     border: 1px solid rgba(255, 255, 255, 0.18);
     border-radius: 12px;
     box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
   }
   ```

2. **Sidebar Glassmorphism**
   ```css
   .glass-sidebar {
     backdrop-filter: blur(20px) saturate(150%);
     background: rgba(255, 255, 255, 0.08);
     border-right: 1px solid rgba(255, 255, 255, 0.12);
   }
   ```

3. **Modal Glassmorphism**
   ```css
   .glass-modal {
     backdrop-filter: blur(15px) saturate(170%);
     background: rgba(0, 0, 0, 0.5);
   }
   ```

4. **Button Glassmorphism**
   ```css
   .glass-button {
     backdrop-filter: blur(5px);
     background: rgba(255, 255, 255, 0.15);
     border: 1px solid rgba(255, 255, 255, 0.2);
   }
   ```

**Extraction Method:**
- Grep search: `backdrop-filter|rgba\(.*0\.[0-9]`
- Manual catalog of all glassmorphism instances
- Document blur amounts, opacity values, border colors
- Create pattern library with named classes

---

## 🎨 CSS Variable Extraction

**Target:** Extract ~200 CSS variables from admin dashboard

### Variable Categories

1. **Colors (60 variables)**
   - Primary, secondary, accent colors
   - Gray scale (50-900)
   - Semantic colors (success, warning, error, info)
   - Background colors (light, dark, glassmorphism)
   - Text colors (primary, secondary, disabled, link)

2. **Spacing (30 variables)**
   - Spacing scale: xs, sm, md, lg, xl, 2xl, 3xl (4px → 96px)
   - Container padding, margin utilities
   - Gap utilities for grid/flex

3. **Typography (40 variables)**
   - Font families (primary, secondary, monospace)
   - Font sizes: xs, sm, base, md, lg, xl, 2xl, 3xl, 4xl, 5xl
   - Line heights: tight, normal, relaxed, loose
   - Font weights: 300, 400, 500, 600, 700, 800
   - Letter spacing: tight, normal, wide

4. **Shadows (20 variables)**
   - Box shadows: sm, md, lg, xl, 2xl
   - Glassmorphism shadows (RGBA with blur)
   - Inner shadows for depth

5. **Borders (15 variables)**
   - Border radius: xs, sm, md, lg, xl, full, circle
   - Border widths: thin, default, thick
   - Border colors (RGBA for glassmorphism)

6. **Z-Index (10 variables)**
   - Layer stacking: base, dropdown, sticky, fixed, modal, popover, tooltip

7. **Transitions (10 variables)**
   - Duration: fast, normal, slow
   - Easing: ease-in, ease-out, ease-in-out, linear

8. **Breakpoints (5 variables)**
   - Mobile, tablet, desktop, wide, ultrawide

9. **Glassmorphism (10 variables)**
   - Blur amounts: light, medium, heavy
   - Background opacity: subtle, medium, strong
   - Border opacity

**Extraction Method:**
1. Parse `styles/2-variables.css` with regex: `:root\s*{([^}]+)}`
2. Group variables by category (prefix-based: `--color-`, `--spacing-`, `--font-`)
3. Document usage examples for each variable
4. Create mapping: admin variable → lens variable (with 125% scale for fonts)

---

## 🧩 Component Style Extraction

**Target:** Extract ~30 component styles

### Component Inventory

| Component | Admin Location | Lens Destination | Priority |
|-----------|----------------|------------------|----------|
| **Card** | `5-components.css` (`.card`) | `src/cortex_lens/templates/base/components/card.css` | HIGH |
| **Button** | `5-components.css` (`.btn-*`) | `base/components/button.css` | HIGH |
| **Badge** | `5-components.css` (`.badge-*`) | `base/components/badge.css` | MEDIUM |
| **Form** | `5-components.css` (`.form-*`) | `base/components/form.css` | MEDIUM |
| **Tab** | `5-components.css` (`.tab-*`) | `base/components/tab.css` | HIGH |
| **Modal** | `5-components.css` (`.modal`) | `base/components/modal.css` | MEDIUM |
| **Tooltip** | `5-components.css` (`.tooltip`) | `base/components/tooltip.css` | LOW |
| **Toast** | `5-components.css` (`.toast`) | `base/components/toast.css` | LOW |
| **Dropdown** | `5-components.css` (`.dropdown`) | `base/components/dropdown.css` | MEDIUM |
| **Sidebar** | `5-components.css` (`.sidebar`) | `base/components/sidebar.css` | HIGH |
| **Progress** | `5-components.css` (`.progress`) | `base/components/progress.css` | MEDIUM |
| **Spinner** | `7-animations.css` (`.spinner`) | `base/components/spinner.css` | HIGH |
| **Skeleton** | `7-animations.css` (`.skeleton`) | `base/components/skeleton.css` | HIGH |
| **Accordion** | `5-components.css` (`.accordion`) | `base/components/accordion.css` | LOW |
| **Breadcrumb** | `5-components.css` (`.breadcrumb`) | `base/components/breadcrumb.css` | LOW |

**Extraction Process:**
1. Read `5-components.css` line by line
2. Identify component classes (pattern: `.component-name`)
3. Extract complete selector block with all modifiers (`.component--variant`)
4. Document dependencies (variables used, other components referenced)
5. Create standalone CSS file per component
6. Validate no circular dependencies

---

## 🎬 Loading Animation Extraction

**Target:** Extract loading animations and skeleton loaders

### Animation Inventory

1. **Spinner Animations**
   - Rotating spinner (border-based)
   - Dot spinner (3 dots bouncing)
   - Pulse spinner (scale animation)
   - Ring spinner (SVG-based)

2. **Skeleton Loaders**
   - Card skeleton (shimmer effect)
   - List skeleton
   - Table skeleton
   - Text skeleton

3. **Transition Animations**
   - Fade in/out
   - Slide in/out (top, right, bottom, left)
   - Scale in/out
   - Rotate

**Extraction Method:**
1. Parse `7-animations.css` for `@keyframes` blocks
2. Extract animation definitions with timing functions
3. Document trigger classes (`.loading`, `.skeleton`, `.fade-in`)
4. Create animation library: `src/cortex_lens/templates/base/animations/`

---

## 🧠 Three.js 3D Brain Visualization

**Source:** `cortex-brain/dashboards/ui/components/brain-3d.js`

**Extraction Tasks:**
1. Identify Three.js version used (check CDN link or package.json)
2. Extract brain mesh geometry (vertices, faces)
3. Document material properties (color, opacity, shininess)
4. Extract rotation animation logic (requestAnimationFrame loop)
5. Document health score color mapping (red → yellow → green)
6. Extract particle effects (if any)
7. Document camera position, FOV, controls

**Implementation Guide Structure:**
```markdown
# Three.js Brain Visualization Implementation

## Dependencies
- Three.js v{version} (vendored to avoid external dependency)

## Setup
- Canvas element creation
- Scene, camera, renderer initialization

## Brain Mesh
- Geometry: IcosahedronGeometry(radius, detail)
- Material: MeshPhongMaterial with glassmorphism
- Wireframe: EdgesGeometry for outline

## Animation
- Rotation: rotate on X and Y axes
- Health score color: interpolate between red (0) and green (100)

## Performance
- Use requestAnimationFrame
- Dispose geometry/material on cleanup
```

---

## 📐 Typography 125% Scale Mapping

**Admin Dashboard Base Sizes → CORTEX Lens 125% Sizes**

| Admin (px) | Lens (px) | Variable Name | Use Case |
|------------|-----------|---------------|----------|
| 12px | 15px | `--font-size-xs` | Captions, labels |
| 14px | 17.5px | `--font-size-sm` | Secondary text |
| 16px | 20px | `--font-size-base` | Body text |
| 18px | 22.5px | `--font-size-md` | Emphasized text |
| 24px | 30px | `--font-size-lg` | H3 headings |
| 32px | 40px | `--font-size-xl` | H2 headings |
| 40px | 50px | `--font-size-2xl` | H1 headings |
| 48px | 60px | `--font-size-3xl` | Hero text |
| 56px | 70px | `--font-size-4xl` | Large hero |
| 72px | 90px | `--font-size-5xl` | Extra large hero |

**Scale Factor CSS Variable:**
```css
:root {
  --scale-factor: 1.25; /* Easy adjustment point */
  --font-size-base: calc(16px * var(--scale-factor)); /* 20px */
}
```

**Rationale for 125% Scale:**
- Admin dashboard designed for dense information display
- CORTEX Lens focuses on readability for code analysis reports
- Larger text reduces eye strain during long report reviews
- Glassmorphism benefits from larger text (better contrast)

---

## 🗂️ Extraction Workflow

### Phase 1: Automated Extraction (Day 1)

1. **CSS Variable Extraction Script**
   ```python
   # scripts/extract_admin_css_variables.py
   import re
   
   def extract_variables(css_file):
       with open(css_file) as f:
           content = f.read()
       
       # Find :root { ... } block
       root_match = re.search(r':root\s*{([^}]+)}', content, re.DOTALL)
       if root_match:
           variables = re.findall(r'(--[a-z0-9-]+):\s*([^;]+);', root_match.group(1))
           return variables
   ```

2. **Component Extraction Script**
   ```python
   # scripts/extract_admin_components.py
   def extract_component_styles(css_file, component_name):
       # Find all selectors starting with .component_name
       # Extract complete CSS blocks
       # Save to separate file
   ```

3. **Glassmorphism Pattern Script**
   ```python
   # scripts/extract_glassmorphism_patterns.py
   def find_glassmorphism(css_file):
       # Search for backdrop-filter properties
       # Extract complete selector with all properties
       # Group by pattern type (card, sidebar, modal, button)
   ```

### Phase 2: Manual Review & Documentation (Day 2-3)

1. Review extracted CSS variables
2. Document usage examples for each variable
3. Create pattern library with visual examples
4. Validate glassmorphism browser support (Safari requires -webkit-backdrop-filter)
5. Document Three.js brain implementation
6. Create loading animation library

### Phase 3: Lens Integration Planning (Day 3-4)

1. Map admin components to lens components
2. Identify missing components (need to be created)
3. Define component API (props, variants, states)
4. Plan CSS organization (one file per component vs monolithic)
5. Define naming conventions (BEM, utility-first, semantic)

### Phase 4: Validation & Testing (Day 4-5)

1. Create visual regression tests (compare admin vs lens rendering)
2. Test glassmorphism in all target browsers (Chrome, Firefox, Safari, Edge)
3. Validate 125% typography scale readability
4. Test loading animations performance
5. Validate Three.js brain renders correctly

---

## 📊 Success Criteria

**Phase 0 - Sub-Plan 1 (Design Extraction) Complete When:**

- [ ] All 200+ CSS variables extracted and documented
- [ ] ~30 component styles cataloged with dependencies
- [ ] Glassmorphism patterns documented (4+ pattern types)
- [ ] Three.js brain implementation guide created
- [ ] Loading animation library extracted (8+ animations)
- [ ] Typography 125% scale mapping validated
- [ ] Extraction scripts created and tested
- [ ] Design pattern library document created (~1,200 LOC)

---

## 🔗 References

- **Admin Dashboard:** `cortex-brain/dashboards/ui/`
- **CSS Styles:** `cortex-brain/dashboards/ui/styles/`
- **Components:** `cortex-brain/dashboards/ui/components/`
- **Target Location:** `src/cortex_lens/templates/base/`

---

**Next Steps:** Execute extraction scripts, create pattern library, validate browser compatibility.
