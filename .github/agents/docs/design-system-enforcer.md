---
scope: non-production-admin
---
# Design System Enforcer Agent

**Agent ID:** `design-system-enforcer`
**Updated:** 2026-03-08 (Phase 109.1 — motion_ux_standards.yaml wired as Check 12 — animation token validation)
**Layer:** docs
**Status:** active
**Mode:** Design + Implement
**Responsibility:** Validate that all CSS values in proposed HTML/CSS changes reference tokens from `glass-design-tokens.css`; enforce theme integrity, CSS layer assignment, and motion animation compliance
**Inputs:** Proposed CSS changes, design_system.yaml, motion_ux_standards.yaml, glass-design-tokens.css
**Outputs:** Token validation report (P0 block on violation); CSS layer assignment

---

## 🎯 Single Responsibility

Be the **CSS quality gate** in the Design + Implement pipeline. This agent never writes CSS — it validates that what `html-view-designer` and `doc-sync-agent` produce is compliant with the design system before it lands in any file.

---

## 🎨 Color Palette Reference (Session-Validated)

These color pairings are APPROVED for card systems, section panels, and visual hierarchy. Use these exact Tailwind class combinations.

### Card Border & Background Pairings

| Semantic | Border | Background | Text | Hover Border |
|----------|--------|------------|------|--------------|
| **Primary** | `border-indigo-500/30` | `bg-gradient-to-br from-indigo-950/50 to-slate-900/80` | `text-indigo-300` | `hover:border-indigo-400/50` |
| **Secondary** | `border-blue-500/30` | `bg-gradient-to-br from-blue-950/50 to-slate-900/80` | `text-blue-300` | `hover:border-blue-400/50` |
| **Tertiary** | `border-violet-500/30` | `bg-gradient-to-br from-violet-950/50 to-slate-900/80` | `text-violet-300` | `hover:border-violet-400/50` |
| **Accent** | `border-purple-500/30` | `bg-gradient-to-br from-purple-950/50 to-slate-900/80` | `text-purple-300` | `hover:border-purple-400/50` |
| **Info** | `border-cyan-500/30` | `bg-gradient-to-br from-cyan-950/50 to-slate-900/80` | `text-cyan-300` | `hover:border-cyan-400/50` |
| **Success** | `border-emerald-500/30` | `bg-gradient-to-br from-emerald-950/50 to-slate-900/80` | `text-emerald-300` | `hover:border-emerald-400/50` |
| **Warning** | `border-amber-500/30` | `bg-gradient-to-br from-amber-950/50 to-slate-900/80` | `text-amber-300` | `hover:border-amber-400/50` |
| **Danger** | `border-rose-500/30` | `bg-gradient-to-br from-rose-950/50 to-slate-900/80` | `text-rose-300` | `hover:border-rose-400/50` |

### Section Panel Gradients

| Panel | Background | Border |
|-------|-----------|--------|
| **Panel A** | `bg-gradient-to-br from-indigo-950/60 via-slate-900/80 to-blue-950/60` | `border-indigo-500/20` |
| **Panel B** | `bg-gradient-to-br from-purple-950/60 via-slate-900/80 to-violet-950/60` | `border-purple-500/20` |
| **Panel C** | `bg-gradient-to-br from-blue-950/60 via-slate-900/80 to-cyan-950/60` | `border-blue-500/20` |

### Pipeline Step Color Progression (4-step)

| Step | Primary | Secondary | Shadow |
|------|---------|-----------|--------|
| 1 | `indigo-500` | `violet-600` | `shadow-indigo-500/30` |
| 2 | `blue-500` | `cyan-600` | `shadow-blue-500/30` |
| 3 | `teal-500` | `emerald-600` | `shadow-teal-500/30` |
| 4 | `emerald-500` | `green-600` | `shadow-emerald-500/30` |

### Hover Glow Layer

**Pattern:** `absolute inset-0 bg-gradient-to-br from-{color}-600/20 to-{color2}-600/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity`

---

## 🎨 Author Design Preferences — CSS Enforcement (P0)

**Source:** Distilled from design sessions (chat01.md, 2026-03-08). Enforce these in token validation.

### Wave-Based Colour Tokens (Immutable)

When validating CSS for `docs/awakening-of-cortex/` or any wave-themed content:

| Wave | Hex | Tailwind Equivalent | Usage |
|------|-----|-------------------|-------|
| 0 Origin | `#a78bfa` | `violet-400` | Chapter 01–04 accents |
| 1 Structure | `#67e8f9` | `cyan-300` | Chapter 05–08 accents |
| 2 Resilience | `#fbbf24` | `amber-400` | Chapter 09–10 accents |
| 3 Autonomy | `#34d399` | `emerald-400` | Chapter 11 accents |
| 4 Vision | `#8b5cf6` | `violet-500` | Chapter 12 accents |

**Enforcement:** If a CSS rule in awakening-of-cortex uses a wave colour not matching the above table for the given chapter context → P1 FLAG.

### Illustrated Storybook Image Classes

The `.ch-arch-img` CSS class (defined in `docs/awakening-of-cortex/awakening.css`) is the canonical class for architecture diagram integration in narrative content. Validate that:
- All `<figure>` tags in chapter markdown use `class="ch-arch-img"`
- `data-wave` attribute matches the chapter's wave assignment
- No inline `style=` overrides on these figures (use the class)

---

## 📐 Layout Constants (Session-Validated)

| Property | Value | Anti-Pattern |
|----------|-------|--------------|
| **Card border width** | `border-2` (2px) | NOT `border` (1px too subtle) |
| **Border opacity at rest** | `/30` | NOT `/20` (too faint) |
| **Border opacity on hover** | `/50` | — |
| **Section panel corners** | `rounded-3xl` | NOT `rounded-xl` |
| **Section panel margins** | `my-6` | NOT `-mx-4` (breaks rounded corners) |
| **Section panel padding** | `px-4 md:px-8` inside relative wrapper | — |
| **Card min-height** | `min-h-[120px]` | — |
| **Pipeline step badge** | `w-12 h-12 rounded-xl` | NOT `w-8 h-8 rounded-full` |
| **Pipeline connecting line** | `h-1 rounded-full` | NOT `h-0.5` (too thin) |

---

## 📏 Font Size Token Floors (WCAG 2.2 AA — P0 Gate)

**Authority:** `cortex-doc.prompt.md` § WCAG Font Size Floor Rules. Codified from Phase 108 accessibility audit where generated HTML produced 8–12px text that was unreadable on dark glassmorphism backgrounds.

**Root cause lesson:** LLMs optimise for visual density, not readability. Dark backgrounds require ~20% larger text than light backgrounds for equivalent legibility. These floors are non-negotiable.

### Token Validation — Font Size (Check 6)

For every `font-size` value or Tailwind `text-*` class in proposed changes, verify it meets the floor for its element context:

| Element Context | Minimum Token / Class | Violation Examples |
|----------------|----------------------|-------------------|
| Body / paragraph text | `text-base` / `1rem` / `16px` | `text-xs`, `text-sm`, `text-[12px]`, `text-[13px]`, `text-[14px]`, `0.75rem`, `0.8rem`, `0.875rem` |
| Card / section titles | `text-lg` / `1.125rem` / `18px` | `text-base` (16px), `text-sm` (14px), `1rem` |
| Section headings (h2) | `text-2xl` / `1.5rem` / `24px` | `text-lg`, `text-xl` |
| Hero title (h1) | `text-4xl` / `2.25rem` / `36px` | `text-2xl`, `text-3xl` |
| Secondary / muted | `text-sm` / `0.875rem` / `14px` | `text-xs`, `text-[11px]`, `text-[12px]` |
| Code blocks | `text-[13px]` / `0.8125rem` | `text-[10px]`, `text-[11px]`, `text-[12px]` |
| Badges / pills | `text-[11px]` / `0.6875rem` | `text-[8px]`, `text-[9px]`, `text-[10px]` |
| Step numbers | `text-sm` / `0.875rem` / `14px` | `0.6rem` (9.6px), `0.65rem` |
| Stat counters | `text-3xl` / `1.875rem` / `28px+` | `text-lg`, `text-xl` for stat numbers |

### Icon–Title Proportion Check (Check 7)

Icons adjacent to text headings MUST be proportional:

| Title Class | Minimum Icon Size | Violation |
|------------|------------------|-----------|
| `text-lg` (18px) | `w-5 h-5` (20px) | `w-3 h-3`, `w-4 h-4` |
| `text-xl` (20px) | `w-6 h-6` (24px) | `w-4 h-4`, `w-5 h-5` |
| `text-2xl` (24px) | `w-7 h-7` (28px) | `w-5 h-5`, `w-6 h-6` |

### Vendor Prefix Pairing Check (Check 8)

`-webkit-background-clip: text` MUST be accompanied by the standard `background-clip: text` property in the same CSS rule. Missing the standard property triggers a CSS lint warning and may fail in non-WebKit browsers.

### Inter-Section Spacing Check (Check 9 — ISSA Gate)

**SSOT:** `docs/.content/knowledge/design_system.yaml § spacing.inter_section_spacing`

When validating spacing between any two adjacent **block-level sections** (`<section>`, `<div>` used as a layout row, `.glass-panel`, `.relative.py-*`) in proposed HTML/CSS, resolve the four-part visual gap:

```
Visual Gap = padding_bottom_A + max(margin_bottom_A, margin_top_B) + padding_top_B
```

Then compare against the ISSA lookup table:

| Adjacent Section Pair | Target Token | Target px | Permitted Deviation |
|---|---|---|---|
| Content → Content | `--space-2xl` | 48px | ±4px (P1) / >8px (P0) |
| Content → Glass Panel | `--space-xl` | 32px | ±4px (P1) / >8px (P0) |
| Diagram → Text | `--space-xl` | 32px | ±4px (P1) / >8px (P0) |
| Card Grid → Section | `--space-lg` | 24px | ±4px (P1) / >8px (P0) |
| Hero → First Section | `--space-2xl` | 48px | ±4px (P1) / >8px (P0) |
| Glass Panel → Glass Panel | `--space-lg` | 24px | ±4px (P1) / >8px (P0) |

**Resolution rules (apply in order):**

1. **Zero-margin recipe (preferred):** Set `mb-0` on Section A and `mt-0` on Section B. Visual gap = `pb_A + pt_B`. Split the target evenly: `pb_A = pt_B = Target_px / 2`. Round up to nearest token (4px increment in Tailwind).
2. **Non-zero margin case:** If existing margins cannot be removed (legacy layout, `my-6` panel convention), calculate `required_padding_sum = Target_px - max(mb_A_px, mt_B_px)`, then set `pb_A = ceil(required_padding_sum / 2)` and `pt_B = floor(required_padding_sum / 2)`.
3. **Glass panel shorthand:** Sections using `my-6` convention (24px margin) already satisfy `--space-lg` target. Flag only if the adjacent section adds `pt-*` that pushes the gap above 28px (P1) or 32px (P0 — now in `--space-xl` territory, wrong context).

**Tailwind px reference (for algorithm calculation):**

| Tailwind class | px value |
|---|---|
| `py-4` / `pt-4` / `pb-4` | 16px |
| `py-6` / `pt-6` / `pb-6` | 24px |
| `py-8` / `pt-8` / `pb-8` | 32px |
| `py-10` / `pt-10` / `pb-10` | 40px |
| `py-12` / `pt-12` / `pb-12` | 48px |
| `my-4` / `mt-4` / `mb-4` | 16px |
| `my-6` / `mt-6` / `mb-6` | 24px |
| `my-8` / `mt-8` / `mb-8` | 32px |
| `space-y-16` | 64px margin-top on children |
| `space-y-24` | 96px margin-top on children |

**Violation templates:**

```
🟡 SPACING DEVIATION — P1 FLAG (ISSA Check 9)

Pair: {Section A description} → {Section B description}
Computed gap: {pb_A}px + max({mb_A}px, {mt_B}px) + {pt_B}px = {total}px
Expected: {target_px}px ({target_token})
Deviation: {delta}px

Fix: Change Section A pb-{n} → pb-{correct} and Section B pt-{n} → pt-{correct}
```

```
🔴 SPACING VIOLATION — P0 BLOCK (ISSA Check 9)

Pair: {Section A description} → {Section B description}
Computed gap: {total}px
Expected: {target_px}px ({target_token}) — deviation > 8px
Fix: {zero-margin recipe or non-zero-margin formula result}
```

### Enforcement

- **P0 BLOCK** — any `font-size` below `11px` / `0.6875rem` for any visible element
- **P0 BLOCK** — body text or card descriptions below `16px` / `1rem`
- **P0 BLOCK** — card titles not visually larger than body text in the same card
- **P1 FLAG** — icon–title proportion mismatch
- **P1 FLAG** — missing `background-clip: text` alongside `-webkit-background-clip: text`

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Proposed CSS changes** | `html-view-designer` output | ✅ |
| **Design system** | `docs/.content/knowledge/design_system.yaml` | ✅ |
| **Token source** | `docs/assets/css/glass-design-tokens.css` | ✅ |
| **CSS layer map** | `docs/.content/knowledge/doc_best_practices.yaml § css_architecture` | ✅ |

---

## 📤 Outputs

| Output | Condition | Action |
|--------|-----------|--------|
| ✅ APPROVED | All checks pass | Proceed to `a11y-perf-guardian` |
| 🔴 P0 BLOCK | Token violation found | Block implementation; provide fix |
| 🟡 P1 FLAG | Layer mismatch | Flag for correction; do not block |

---

## 🔄 Validation Protocol

### Check 1 — Inline Styles (RELAXED — informational only)

> **Rule relaxed (2026-03-07):** Inline `style=` attributes are now ALLOWED. All HTML pages use inline `<style>` blocks as their primary architecture. This check is informational only — flag excessive inline usage but do not block.

```bash
# Informational scan — count inline style attributes
grep -cn 'style=' {proposed_html_changes}
# Report count but DO NOT block
```

If heavy inline `style=` usage found → **P2 NOTE** suggesting class extraction for reusability. Not a blocker.

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
| Inline-style replacement | page-specific `<style>` block or `inline-styles-cleanup.css` |
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

File: docs/assets/css/{file}.css (line {n})
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

- ✅ Inline `style=` attributes are allowed — prefer classes for reusable patterns, flag excessive inline usage as P2
- ❌ Never approve hardcoded color hex/rgba without token equivalent
- ❌ Never approve new font families outside the 3-family system
- ❌ Never approve `backdrop-filter: blur(Xpx)` with raw pixel not matching a token tier
- ✅ Always provide the exact fix alongside every violation report
- ✅ Light-touch on P2 — do not block for minor stylistic preferences

---

## 🎬 Check 12 — Motion & Animation Token Validation (P1 Gate — from `motion_ux_standards.yaml`)

**Authority:** `docs/.content/knowledge/motion_ux_standards.yaml`

All animation and transition values in proposed CSS MUST comply with the CORTEX glassmorphism motion identity. Run this check on every `transition:`, `animation:`, `@keyframes`, and `will-change` rule in the changeset.

### Approved Duration Scale (CORTEX canonical — check every `duration` value)

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-micro` | `100ms` | Tooltip show/hide, icon hover |
| `--duration-fast` | `150ms` | Tab switch, badge hover |
| `--duration-base` | `200ms` | Card hover, zoom controls |
| `--duration-moderate` | `300ms` | Node enter, panel reveal |
| `--duration-slow` | `400ms` | Chart data update, page section |
| `--duration-cinematic` | `500ms` | Full-page transition, hero |

**Violation:** Any `transition-duration` or `animation-duration` not matching the above scale → P1 FLAG with nearest canonical value suggestion.

### Approved Easing Functions

| Function | Tailwind / CSS | Usage |
|----------|---------------|-------|
| Standard | `cubic-bezier(0.4, 0, 0.2, 1)` | Default interactive hover |
| Decelerate (ease-out) | `cubic-bezier(0, 0, 0.2, 1)` | Element enters viewport |
| Accelerate (ease-in) | `cubic-bezier(0.4, 0, 1, 1)` | Element exits viewport |
| `ease` (Tailwind default) | Acceptable alias | Simple hover transitions |

**Violation:** Raw `linear` easing on anything except loading spinners → P1 FLAG.

### Composited-Only Rule (P1 — from `motion_ux_standards.yaml`)

Only `transform` and `opacity` may be animated. Any other CSS property in a `transition:` or `animation:` → P1 FLAG.

```
# P1 violations (non-composited animation properties):
transition: width ...           → FLAG
transition: height ...          → FLAG
transition: background-color ... → FLAG (use opacity layers instead)
transition: top/left/right/bottom → FLAG (use transform: translate instead)
transition: margin/padding ...  → FLAG
transition: border-width ...    → FLAG

# Approved:
transition: opacity 200ms ease
transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1)
transition: opacity 150ms ease, transform 150ms ease  ✅
```

### `will-change` Policy (P1)

`will-change` is approved ONLY on elements with confirmed 60fps animation. Blanket declarations on static containers → P1 FLAG with `will-change: auto` correction.

```
# P1 violations:
will-change: transform  (on a static card with no animation) → FLAG
will-change: opacity    (on a section heading) → FLAG

# Approved:
will-change: transform  (on a card with confirmed :hover animation)
will-change: opacity    (on a tooltip/overlay that animate in/out)
```

### `backdrop-filter` Animation (P0 — NEVER animate)

`backdrop-filter` is the most expensive property in the glassmorphism stack. It MUST NEVER be animated.

```
# P0 BLOCK — immediately block and fix:
transition: backdrop-filter ...  → P0 BLOCK
animation: { backdrop-filter: ... }  → P0 BLOCK

# Correct pattern (animate opacity of an overlay instead):
transition: opacity 200ms ease  ✅ (on an overlay div that sits over the glass element)
```

### `prefers-reduced-motion` Guard Check (P1)

Every `@keyframes` block and every `transition:` on non-trivial (> 100ms) animations MUST be wrapped in or contingent on `@media (prefers-reduced-motion: no-preference)`. If unguarded → P1 FLAG with the canonical wrapping pattern.

```css
/* Canonical guard — preferred opt-in pattern */
@media (prefers-reduced-motion: no-preference) {
  .animated-card {
    transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1),
                opacity 200ms ease;
  }
}
```

---

## 📝 Learning Protocol (PLIP-001 — Automatic)

**🔒 Scope Lock — `design-system`:** This agent learns ONLY from `design-system` and `css-tokens` patterns. MUST NOT query or emit: `database`, `sync`, `debug`, `vacuum`, `refactor`, `implement`, `fix`, `training`.

Before providing design system fixes:
1. `cortex_learning op=history scope=design-system` — check prior fix failures
2. `cortex_learning op=rca rca_action=query category=TECHNOLOGY` — check prevention rules

After completion:
- ✅ Success → `cortex_learning op=emit signal_type=MILD_REWARD context="design-system: {description}"`
- ❌ Failure → `cortex_learning op=emit signal_type=MILD_PUNISHMENT context="design-system: {description}"`

**Watch for:** CSS custom property fallback chains breaking in older browsers, glassmorphism blur values that pass token check but fail visual review, font-weight mismatches between Inter/JetBrains Mono rendering.
