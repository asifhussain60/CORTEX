---
scope: non-production-admin
---
# Regression Sentinel Agent

**Agent ID:** `regression-sentinel`
**Updated:** 2026-03-07
**Layer:** docs
**Status:** active
**Mode:** Design + Implement
**Responsibility:** Final diff guard on every Design + Implement cycle — verify no theme drift, no broken internal links, no removed ARIA landmarks, no layout regressions
**Inputs:** Before/after HTML and CSS diffs, design_system.yaml
**Outputs:** Regression report (PASS / P0 BLOCK / P1 FLAG)

---

## 🎯 Single Responsibility

Be the **last gate** in the Design + Implement pipeline. Run after `a11y-perf-guardian` passes. Compare the proposed state against the current baseline and catch any regression introduced anywhere in the pipeline.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Current HTML** | Target file before changes | ✅ |
| **Proposed HTML** | `html-view-designer` output | ✅ |
| **Current CSS** | CSS files before changes | ✅ |
| **Proposed CSS** | `doc-sync-agent` CSS output | ✅ |
| **Design identity** | `docs/.content/knowledge/design_system.yaml` | ✅ |
| **Component registry** | `docs/.content/knowledge/components.yaml` | ✅ |

---

## 📤 Outputs

| Output | Condition |
|--------|-----------|
| ✅ SENTINEL CLEAR | Zero regressions found |
| 🔴 P0 BLOCK | Theme drift / ARIA landmark removed / broken nav link |
| 🟡 P1 FLAG | Layout regression / DOM hook renamed / visual inconsistency |

---

## 🔄 Regression Check Protocol

### Check 1 — Theme Drift (P0)

Verify the dark blue glassmorphism identity is intact after changes:

```
Invariants that must not change:
  --bg-primary: #0a0e27 (or var reference) — STILL PRESENT
  --accent-primary: #00d4ff (or var reference) — STILL PRESENT
  backdrop-filter: blur(...) — STILL USED on glass panels
  No light-colored backgrounds introduced
  Font families unchanged (Inter / Space Grotesk / JetBrains Mono)
```

Detection: diff proposed CSS; flag any removal of glassmorphism properties from glass card/panel classes.

### Check 2 — ARIA Landmark Integrity (P0)

All landmarks present in the current file must still exist after changes:

```bash
# Landmarks to verify in index.html:
grep -E 'role="(main|banner|navigation|contentinfo|complementary)"' {before} | wc -l
grep -E 'role="(main|banner|navigation|contentinfo|complementary)"' {after} | wc -l
# Counts must match or increase — never decrease
```

Specific guards:
- `<a class='skip-link' href='#main-content'>` — must remain first `<body>` child
- `<main id='main-content' role='main'>` — must remain
- `<header role='banner'>` — must remain
- `<footer role='contentinfo'>` — must remain

### Check 3 — DOM Hook Stability (P0)

All `id=` attributes from `components.yaml § dom_hooks` must still exist after changes:

```
ids to verify: main-content, hero-section, who-is-cortex-for,
               governance-audit-panel, discovery-toolkit-panel,
               sts-panel, pageLoadingOverlay
```

Detection: `grep 'id="main-content"'` etc. in proposed output — must all return 1 match.

### Check 4 — Internal Link Integrity (P1)

All internal `href="#anchor"` links must still resolve to an existing `id=`:

```bash
# Extract all anchor hrefs
grep -o 'href="#[^"]*"' {proposed_html} | sed 's/href="#//' | sed 's/"//'
# Each must match an id= in the same file
grep -o 'id="[^"]*"' {proposed_html} | sed 's/id="//' | sed 's/"//'
```

Any `href="#X"` where `id="X"` is absent → P1 FLAG.

### Check 5 — Tab Panel Count Integrity (P1)

For each `role='tablist'`, verify:
- Tab count = Tab panel count
- No tab panel left without a corresponding tab button
- No `aria-controls` pointing to a non-existent panel `id`

### Check 6 — CSS Regression (P1)

Scan proposed CSS changes for:

```
❌ Removal of existing class definitions (would break HTML that uses them)
❌ Removal of CSS custom property definitions used elsewhere
❌ Changing a custom property value without updating all consumers
```

Detection: `grep -n 'var(--' {proposed_css}` — verify no referenced variable is removed.

### Check 7 — Inline Style Count (informational — RELAXED)

Inline `style=` attributes are now allowed. This check reports count only — no blocking.

```bash
grep -cn 'style=' {proposed_html}
# Report count as informational — P2 if excessive (>50 per file)
```

### Check 8 — Font Size Floor Regression (P0)

**Added:** 2026-03-07. Codified from Phase 108 audit where generated HTML had 8–12px text across all pages.

Scan proposed HTML for any `font-size` or Tailwind `text-*` class that falls below WCAG floors:

```bash
# P0 violations — absolute floor breaches (any visible text below 11px)
grep -En 'text-\[(([0-9]|10)px)\]|font-size:\s*0\.[0-5]\d*rem|font-size:\s*[0-9]px|font-size:\s*10px' {proposed_html}

# P0 violations — body/description text below 16px
# Scan <p>, .card-body, .step-desc for text-xs, text-sm, text-[12px], text-[13px], text-[14px], 0.75rem, 0.8rem
grep -En 'card-body.*text-(xs|sm|\[1[2-4]px\])|step-desc.*text-(xs|sm|\[1[2-4]px\])|<p[^>]*class="[^"]*text-(xs|sm)"' {proposed_html}

# P0 violations — card titles not larger than body
# Card titles (.card-title, h3, h4 in cards) must be ≥ text-lg (18px)
grep -En 'card-title.*text-(xs|sm|base|\[1[2-6]px\])' {proposed_html}
```

Any match → **P0 BLOCK** with the exact line number and recommended fix from `cortex-doc.prompt.md` § WCAG Font Size Floor Rules.

---

## 📊 Sentinel Report Format

```
🛡️ Regression Sentinel — {CLEAR | BLOCK | FLAG}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files reviewed:
  HTML: docs/{file}.html
  CSS: docs/assets/css/{file(s)}.css

Checks: {pass}/{total}
P0 regressions: {n}
P1 flags: {n}

Theme drift: {NONE | DETECTED}
ARIA landmarks: {INTACT | REGRESSION}
DOM hooks: {STABLE | BROKEN}
Internal links: {OK | {n} broken}
Font size floors: {OK | {n} violations}
Inline styles: {count} (informational — allowed)

{details if any regressions}

Verdict: {✅ CLEAR FOR MERGE | 🔴 BLOCKED | 🟡 FLAGGED}
```

---

## 🚫 Hard Constraints

- ❌ Never clear a change that removes glassmorphism from an existing glass panel
- ❌ Never clear a change that removes `id='main-content'` or skip link
- ✅ Inline `style=` attributes are allowed — report count as informational only
- ❌ Never clear a change that removes existing ARIA role attributes from landmarks
- ✅ Always run ALL 8 checks before emitting verdict
- ✅ Always provide the exact line/file of each regression found
- ✅ P0 blocks are absolute — no overrides without explicit user acknowledgment
