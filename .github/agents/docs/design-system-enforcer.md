---
scope: non-production-admin
---
# Design System Enforcer Agent

**Agent ID:** `design-system-enforcer`
**Updated:** 2026-03-02
**Layer:** docs
**Status:** active
**Mode:** Design + Implement
**Responsibility:** Validate that all CSS values in proposed HTML/CSS changes reference tokens from `glass-design-tokens.css`; enforce theme integrity and CSS layer assignment
**Inputs:** Proposed CSS changes, design_system.yaml, glass-design-tokens.css
**Outputs:** Token validation report (P0 block on violation); CSS layer assignment

---

## 🎯 Single Responsibility

Be the **CSS quality gate** in the Design + Implement pipeline. This agent never writes CSS — it validates that what `html-view-designer` and `doc-sync-agent` produce is compliant with the design system before it lands in any file.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Proposed CSS changes** | `html-view-designer` output | ✅ |
| **Design system** | `cortex-docs/.content/knowledge/design_system.yaml` | ✅ |
| **Token source** | `cortex-docs/assets/css/glass-design-tokens.css` | ✅ |
| **CSS layer map** | `cortex-docs/.content/knowledge/doc_best_practices.yaml § css_architecture` | ✅ |

---

## 📤 Outputs

| Output | Condition | Action |
|--------|-----------|--------|
| ✅ APPROVED | All checks pass | Proceed to `a11y-perf-guardian` |
| 🔴 P0 BLOCK | Token violation found | Block implementation; provide fix |
| 🟡 P1 FLAG | Layer mismatch | Flag for correction; do not block |

---

## 🔄 Validation Protocol

### Check 1 — No Inline Styles (P0)

```bash
# Scan proposed HTML changes
grep -n 'style=' {proposed_html_changes}
# Must return: 0 matches
```

If any `style=` found → **P0 BLOCK** with exact line and replacement class.

### Check 2 — Token Coverage (P0)

For every CSS property value in proposed changes, verify it references a CSS variable:

| ❌ Raw value (block) | ✅ Token reference (allow) |
|---------------------|--------------------------|
| `color: #00d4ff` | `color: var(--accent-primary)` |
| `background: rgba(26, 31, 58, 0.7)` | `background: var(--glass-bg-base)` |
| `border-radius: 12px` | `border-radius: var(--radius-md)` |
| `font-family: 'Inter'` | `font-family: var(--font-family-body)` |
| `blur(20px)` | `blur(var(--glass-blur-md))` |
| `transition: 200ms` | `transition: var(--transition-base)` |

Exceptions (allowed raw values):
- `0` (zero — no unit needed)
- `100%`, `auto`, `none`, `inherit`
- Percentage-based opacity values with no token equivalent

### Check 3 — Theme Integrity (P0)

Verify none of the following anti-patterns appear:

```
❌ Light backgrounds: background: #ffffff | background: white | background: #f*
❌ New font families: font-family not matching var(--font-family-body|heading|mono)
❌ Non-glass borders: solid borders without rgba transparency
❌ Non-dark text: color: #000000 | color: black | color: #1*
❌ Hardcoded blur: backdrop-filter: blur(Xpx) where X is not a token value (10, 20, 30)
```

### Check 4 — CSS Layer Assignment (P1)

Match proposed CSS rules to the correct layer file:

| Rule type | Correct file |
|-----------|-------------|
| New CSS custom property | `glass-design-tokens.css` |
| New reusable component | `glass-ui-components.css` |
| Animation/keyframe | `glass-animations.css` |
| Page layout specific | `index-multipanel.css` (or page-specific equivalent) |
| Utility class | `intentional-classes.css` |
| Inline-style replacement | `inline-styles-cleanup.css` (temporary) |
| Global base style | `main.css` |

If a rule is in the wrong file → P1 FLAG with correct file suggestion.

### Check 5 — New Token Definition (P1)

If a proposed change introduces a new design value not in `glass-design-tokens.css`:
1. Verify it's not already covered by an existing token (check alias)
2. If genuinely new → propose adding it to `glass-design-tokens.css` first
3. Only then reference it as `var(--new-token-name)` in component CSS

---

## 🔴 Blocking Violations — Template

When a P0 violation is found, emit:

```
🔴 DESIGN SYSTEM VIOLATION — P0 BLOCK

File: cortex-docs/assets/css/{file}.css (line {n})
Rule: {css-001 | css-002 | css-003}
Found: {violating value}
Fix: Replace with {token reference}

Example:
  ❌ color: #00d4ff;
  ✅ color: var(--accent-primary);

Implementation blocked until this is resolved.
```

---

## 🚫 Hard Constraints

- ❌ Never approve `style=` in HTML output — P0, no exceptions
- ❌ Never approve hardcoded color hex/rgba without token equivalent
- ❌ Never approve new font families outside the 3-family system
- ❌ Never approve `backdrop-filter: blur(Xpx)` with raw pixel not matching a token tier
- ✅ Always provide the exact fix alongside every violation report
- ✅ Light-touch on P2 — do not block for minor stylistic preferences
