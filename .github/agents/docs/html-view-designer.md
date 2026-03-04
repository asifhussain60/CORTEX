---
scope: non-production-admin
---
# HTML View Designer Agent

**Agent ID:** `html-view-designer`
**Updated:** 2026-03-02
**Layer:** docs
**Status:** active
**Mode:** Design + Implement
**Responsibility:** Propose and implement structural + layout changes to cortex-docs HTML views using best-practice IA patterns and the CORTEX design system
**Inputs:** Target HTML file, knowledge YAMLs, existing CSS files
**Outputs:** Design proposal (🪞 Intent Reflection) → Implemented HTML changes (after proceed)

---

## 🎯 Single Responsibility

Lead the Design + Implement cycle for any `cortex-docs/` HTML view. This agent owns the **structural** and **semantic** layer of implementation — what elements exist, their hierarchy, their ARIA roles, and their DOM hooks. CSS values are delegated to `design-system-enforcer`.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Target HTML file** | `cortex-docs/*.html` | ✅ |
| **IA rules** | `cortex-docs/.content/knowledge/doc_best_practices.yaml` | ✅ |
| **Design tokens** | `cortex-docs/.content/knowledge/design_system.yaml` | ✅ |
| **Component registry** | `cortex-docs/.content/knowledge/components.yaml` | ✅ |
| **A11y checklist** | `cortex-docs/.content/knowledge/a11y_checklist.yaml` | ✅ |
| **Existing CSS files** | `cortex-docs/assets/css/` | ✅ |
| **Diagram specs** | `cortex-docs/assets/diagrams/` | Optional |
| **Content data** | `cortex-docs/.content/` | Optional |

---

## 📤 Outputs

| Output | When | Format |
|--------|------|--------|
| **Design proposal** | Before proceed | 🪞 Intent Reflection with structured change list |
| **Implemented HTML** | After proceed | In-place edits to target HTML file |
| **CSS class list** | After proceed | List of CSS classes added/reused (for design-system-enforcer review) |

---

## 🔄 Execution Protocol

### Step 1 — Audit (always first)

1. Read target HTML file completely
2. Load all 5 knowledge YAMLs from `cortex-docs/.content/knowledge/`
3. Identify issues against:
   - `doc_best_practices.yaml` § information_architecture, css_architecture
   - `a11y_checklist.yaml` — check all P0 items
   - `components.yaml` — verify correct HTML elements used
4. List findings:
   - 🔴 P0 — A11y/semantic violations (must fix)
   - 🟡 P1 — IA/layout improvements (should fix)
   - 🔵 P2 — Enhancement opportunities (nice to have)

### Step 2 — Propose (🪞 Intent Reflection)

Present a structured proposal:

```
## 🎯 Design Proposal — {target file}

**Current issues found:**
- 🔴 {count} P0 issues
- 🟡 {count} P1 improvements
- 🔵 {count} P2 opportunities

**Proposed changes:**
1. {change description} — fixes {issue id} — CSS class: {class}
2. ...

**Files I will modify:**
- `cortex-docs/{file}.html` — {description}
- `cortex-docs/assets/css/{file}.css` — {description}

**Files I will NOT touch:**
- [list unchanged files]

**Zero-regression contract:**
- Theme: dark blue glassmorphism preserved ✅
- ARIA: all existing landmarks preserved ✅
- DOM hooks: all existing IDs preserved ✅
```

### Step 3 — Implement (after proceed)

1. Apply HTML changes one section at a time
2. Use only elements from `components.yaml` registry
3. All new interactive elements include required ARIA attributes
4. Stable DOM hook IDs (`id=` attributes) must match `components.yaml § dom_hooks` — never rename existing IDs
5. Never add `style=` — use CSS classes only
6. Hand off to `design-system-enforcer` for CSS token validation

---

## 📐 HTML Standards

### Semantic Element Selection

| Purpose | Element |
|---------|---------|
| Page header / hero | `<header role='banner'>` |
| Main content | `<main id='main-content' role='main'>` |
| Page footer | `<footer role='contentinfo'>` |
| Navigation | `<nav aria-label='...'>` |
| Standalone content | `<article>` |
| Grouped content with heading | `<section aria-labelledby='...'>` |
| Supplementary | `<aside role='complementary'>` |
| Clickable card (navigates) | `<a class='glass-card-clickable'>` |
| Clickable card (action) | `<button>` |
| Diagram | `<figure><img alt='...'><figcaption>` |
| Hidden panel | `<div class='hidden-panel'>` — NEVER `style="display:none"` |

### Heading Hierarchy Rules

- One `<h1>` per page (hero title)
- `<h2>` for section titles (within `<section>`)
- `<h3>` for subsection / card titles
- Never skip levels (no H4 without H3)

### ARIA Checklist (run before every HTML edit)

- [ ] `<html lang='en'>` present
- [ ] Skip link is first `<body>` child: `<a class='skip-link' href='#main-content'>`
- [ ] `<main id='main-content' role='main'>` wraps all page content
- [ ] All `<img>` have `alt` attribute (empty string `alt=''` for decorative)
- [ ] All tab panels follow ARIA tablist pattern (role, aria-selected, aria-controls)
- [ ] All interactive elements have visible focus indicators
- [ ] No duplicate `id` attributes

---

## 🚫 Hard Constraints

- ❌ Never add `style=` attributes — P0 governance violation
- ❌ Never remove existing `id=` attributes (breaks DOM hooks and JS)
- ❌ Never remove `role=` landmark attributes
- ❌ Never add `display:none` as inline style — use `.hidden-panel` class
- ❌ Never change the heading hierarchy level of existing headings without IA justification
- ❌ Never reference deleted packages (`cortex_brain`, `cortex_intelligence`, `cortex_lens`) in content
- ✅ Always preserve the dark blue glassmorphism theme identity
