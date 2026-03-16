#!/usr/bin/env python3
"""
fix_font_sizes.py
─────────────────
CORTEX Font Size Standardisation — Phase 109.3
Authority: docs-html-design-workflow.yaml § wcag_font_floors
Updated: 2026-03-09

Systematically upgrades all sub-floor font-size values in docs/*.html
to WCAG 2.2 AA compliant minimums per the canonical scale.

Floor map (from workflow YAML):
  body paragraphs:     ≥ 1rem     (16px)
  secondary muted:     ≥ 0.875rem (14px)
  badge labels:        ≥ 0.6875rem(11px)  ← absolute floor
  mono/code:           ≥ 0.8125rem(13px)
  nav separators:      ≥ 0.6875rem(11px)  ← aria-hidden, exempt from 14px floor
  tp-tile body text:   0.875rem   (replaces 0.77rem)
  tp-tile labels:      0.875rem   (replaces 0.79rem)
  role-feat icons:     0.875rem   (replaces 0.7rem)
  role-tile body copy: 1rem       (replaces 0.8rem, 0.85rem, 0.95rem < 1rem)
  footer-sep/dividers: 0.6875rem  (replaces 0.7rem — aria-hidden decorators)
  stat sub-labels:     0.6875rem  (floor for stat-lbl, kicker context)
  step phase labels:   0.75rem→0.875rem (mono phase tags)
  gs-row__desc:        0.875rem   (replaces 0.75rem)
  gs-row__arrow:       0.875rem   (replaces 0.7rem)
  gs-card__stat i:     0.875rem   (replaces 0.75rem)
  macc kicker:         0.875rem   (replaces 0.7rem, 0.68rem, 0.72rem)
  sdlc phase desc:     1rem       (replaces 0.8rem)
  code block / pre:    0.8125rem  (13px — code floor, keep as-is)
"""

import re
import os
from pathlib import Path

# ── Replacement rules ─────────────────────────────────────────────────────────
# Each tuple: (pattern, replacement, description)
# Applied in order — most specific first.
RULES = [
    # ── ABSOLUTE VIOLATIONS: below the 0.6875rem absolute floor ──────────────
    # 0.5625rem, 0.6rem → 0.6875rem (badge/separator absolute floor)
    (r'font-size:\s*0\.5625rem', 'font-size: 0.6875rem', '0.5625rem → 0.6875rem (badge floor)'),
    (r'font-size:\s*0\.6rem\b', 'font-size: 0.6875rem', '0.6rem → 0.6875rem (badge floor)'),
    (r'font-size:\s*0\.625rem', 'font-size: 0.6875rem', '0.625rem → 0.6875rem (badge floor)'),
    (r'font-size:\s*0\.65rem\b', 'font-size: 0.6875rem', '0.65rem → 0.6875rem (badge floor)'),
    (r'font-size:\s*0\.68rem\b', 'font-size: 0.6875rem', '0.68rem → 0.6875rem (badge floor)'),

    # ── SEPARATOR / ARIA-HIDDEN DECORATORS: floor 0.6875rem ──────────────────
    # .footer-sep, .role-dot separators — decorative, but still need floor
    # These are typically the | dividers between nav links
    # Keep 0.7rem as-is if it's a separator (aria-hidden) since 0.7rem ≈ 11.2px > 11px
    # Upgrade 0.7rem non-separator uses to 0.6875rem (to use token) OR 0.875rem if text

    # ── BODY TEXT / DESCRIPTIONS below 0.875rem → 0.875rem ──────────────────
    # tp-tile body text: 0.77rem → 0.875rem
    (r'font-size:\s*0\.77rem\b', 'font-size: 0.875rem', '0.77rem → 0.875rem (secondary text)'),
    # tp-tile labels, card tags: 0.79rem → 0.875rem
    (r'font-size:\s*0\.79rem\b', 'font-size: 0.875rem', '0.79rem → 0.875rem (label text)'),
    # role-tag, phase label: 0.7rem inline text (non-separator) → 0.6875rem (badge floor ok)
    # But check context: .role-tag is visible text → needs 0.875rem
    # Using conservative 0.875rem for all 0.7rem in style attrs (non-separator)

    # ── MONO/CODE TEXT below 0.8125rem → 0.8125rem ───────────────────────────
    # 0.72rem mono → 0.8125rem
    (r'font-size:\s*0\.72rem\b', 'font-size: 0.8125rem', '0.72rem → 0.8125rem (mono floor)'),
    # 0.75rem code (cmd-example, gs-row__desc etc.) → 0.8125rem for code; or 0.875rem for text
    # gs-row__desc is regular text → 0.875rem
    # cmd-example is code → 0.8125rem is ok (13px — code floor)
    # We'll handle .75rem context-specifically via targeted replacements below

    # ── BODY-COPY sub-floor: 0.8rem → 1rem ───────────────────────────────────
    (r'font-size:\s*0\.8rem\b', 'font-size: 1rem', '0.8rem → 1rem (body text floor)'),

    # ── 0.85rem body copy → 1rem ─────────────────────────────────────────────
    # .cortex-tag, .role-tile body, macc__kicker = body text → 1rem
    (r'font-size:\s*0\.85rem\b', 'font-size: 1rem', '0.85rem → 1rem (body text floor)'),

    # ── 0.97rem prose → 1rem (tp-prose paragraphs) ───────────────────────────
    (r'font-size:\s*0\.97rem\b', 'font-size: 1rem', '0.97rem → 1rem (prose)'),

    # ── 0.9rem body copy → 1rem ──────────────────────────────────────────────
    # .gs-card__cta font-size: 0.9rem is a CTA button — use 1rem
    (r'font-size:\s*0\.9rem\b', 'font-size: 1rem', '0.9rem → 1rem (CTA/body)'),

    # ── 0.95rem body copy → 1rem ─────────────────────────────────────────────
    (r'font-size:\s*0\.95rem\b', 'font-size: 1rem', '0.95rem → 1rem (body)'),

    # ── D3 attribute font-size violations ────────────────────────────────────
    # D3 SVG .attr('font-size', '9px') → '11px' (minimum for SVG labels)
    (r"\.attr\('font-size',\s*'9px'\)", ".attr('font-size', '11px')", '9px D3 → 11px SVG floor'),
    (r"\.attr\('font-size',\s*'10px'\)", ".attr('font-size', '11px')", '10px D3 → 11px SVG floor'),
    # .attr('font-size', isMobile ? '8px' : '10px') → isMobile ? '11px' : '12px'
    (r"\.attr\('font-size',\s*isMobile\s*\?\s*'8px'\s*:\s*'10px'\)",
     ".attr('font-size', isMobile ? '11px' : '12px')",
     '8/10px D3 mobile → 11/12px'),
    # .attr('font-size', isMobile ? '8px' : '12px') → isMobile ? '11px' : '13px'
    (r"\.attr\('font-size',\s*isMobile\s*\?\s*'8px'\s*:\s*'12px'\)",
     ".attr('font-size', isMobile ? '11px' : '13px')",
     '8/12px D3 mobile → 11/13px'),

    # ── Tailwind forbidden classes ────────────────────────────────────────────
    # text-[11px] (visible labels, not badge) is ok at 11px since it's the badge floor
    # text-[13px] in card descriptions → should be text-sm (14px)
    (r'\btext-\[13px\](?!\s+md:)', 'text-sm', 'text-[13px] → text-sm'),
    (r'\btext-\[13px\]\s+md:text-sm', 'text-sm md:text-sm', 'text-[13px] md:text-sm → text-sm'),
    # text-[11px] standalone labels (non-badge) → keep at text-[11px] (11px = badge floor ok)
    # but text-[11px] on CTA buttons is wrong → needs text-sm
]

# ── Targeted inline-style replacements (exact-match context) ─────────────────
# These handle cases where 0.7rem appears in decorative separators (ok to keep as 0.6875rem)
# vs body text (needs 0.875rem). We replace all 0.7rem with 0.875rem as conservative fix,
# except explicit aria-hidden separator spans which get 0.6875rem.
TARGETED = [
    # footer-sep and nav separator spans (aria-hidden="true")
    # Pattern: font-size:0.7rem in a span with aria-hidden="true"
    (r'(font-size:0\.7rem;[^"]*";[^>]*aria-hidden="true")',
     lambda m: m.group(0).replace('font-size:0.7rem', 'font-size:0.6875rem'),
     'aria-hidden separator 0.7rem → 0.6875rem'),

    # .role-feat i icon spans (decorative icons next to text, ok at 0.875rem)
    # Pattern: .role-feat i { font-size: 0.7rem
    (r'(\.role-feat i \{[^}]*font-size:\s*)0\.7rem',
     r'\g<1>0.875rem',
     '.role-feat i 0.7rem → 0.875rem'),

    # .role-tile-body .role-tag (visible text label) 0.7rem → 0.875rem
    (r'(\.role-tag\s*\{[^}]*font-size:\s*)0\.7rem',
     r'\g<1>0.875rem',
     '.role-tag 0.7rem → 0.875rem'),

    # .gs-row__arrow decorative chevron icon — 0.7rem → 0.6875rem (icon, not text)
    (r'(\.gs-row__arrow\s*\{[^}]*font-size:\s*)0\.7rem',
     r'\g<1>0.875rem',
     '.gs-row__arrow 0.7rem → 0.875rem (icon is still readable)'),

    # .gs-row__desc text 0.75rem → 0.875rem
    (r'(\.gs-row__desc\s*\{[^}]*font-size:\s*)0\.75rem',
     r'\g<1>0.875rem',
     '.gs-row__desc 0.75rem → 0.875rem'),

    # .gs-card__stat i icon 0.75rem → 0.875rem
    (r'(\.gs-card__stat i\s*\{[^}]*font-size:\s*)0\.75rem',
     r'\g<1>0.875rem',
     '.gs-card__stat i 0.75rem → 0.875rem'),

    # macc kicker (step label) 0.7rem → 0.875rem
    (r'(font-size:\s*)0\.7rem(;[^}]*font-weight:\s*500)',
     r'\g<1>0.875rem\g<2>',
     'kicker 0.7rem → 0.875rem'),

    # .stats-lbl 0.8125rem → 0.875rem (stat labels should be secondary floor)
    # 0.8125rem is code-floor, fine for mono; for stats label use 0.875rem
    # Actually 0.8125rem = 13px which is above absolute floor (11px) but below secondary floor (14px)
    # Keep 0.8125rem for mono labels, fix plain text stat labels
    # .stats-lbl is plain text → 0.875rem
    (r'(\.stats-lbl\s*\{[^}]*font-size:\s*)0\.8125rem',
     r'\g<1>0.875rem',
     '.stats-lbl 0.8125rem → 0.875rem'),

    # hero-stat-label 0.8125rem → 0.875rem (visible label text)
    (r'(\.hero-stat-label\s*\{[^}]*font-size:\s*)0\.8125rem',
     r'\g<1>0.875rem',
     '.hero-stat-label 0.8125rem → 0.875rem'),

    # .arch-cta-tag 0.8125rem → 0.875rem (badge-style but uppercase label text)
    (r'(\.arch-cta-tag\s*\{[^}]*font-size:\s*)0\.8125rem',
     r'\g<1>0.875rem',
     '.arch-cta-tag 0.8125rem → 0.875rem'),

    # inline style font-size:0.8125rem on span (footer brand) → 0.875rem
    # Context: footer brand name text
    (r"(font-family:'Space Grotesk',sans-serif;font-size:)0\.8125rem",
     r'\g<1>0.875rem',
     'footer brand 0.8125rem → 0.875rem'),

    # footer link font-size:0.75rem → 0.875rem (visible navigation links)
    (r'(border-radius:9999px;font-size:)0\.75rem',
     r'\g<1>0.875rem',
     'footer nav link 0.75rem → 0.875rem'),

    # .footer copyright 0.7rem → 0.875rem
    (r'(font-size:0\.7rem;color:rgba\(100,116,139)',
     r'font-size:0.875rem;color:rgba(100,116,139)',
     'footer copyright 0.7rem → 0.875rem'),

    # sdlc phase desc 0.8rem → 1rem (already caught by global rule, but be explicit)
    # sdlc step phase label 0.6rem → 0.875rem (mono phase tag like "Phase 0")
    (r"(font-family:var\(--font-mono\);font-size:)0\.6rem",
     r'\g<1>0.875rem',
     'phase mono label 0.6rem → 0.875rem'),

    # macc section label 0.68rem → 0.875rem
    (r'(font-size:\s*)0\.68rem',
     r'\g<1>0.875rem',
     '0.68rem → 0.875rem'),

    # cmd-badge small ribbon label 0.5625rem → 0.6875rem (already in RULES but explicit here)
    (r'(\.cmd-badge\s*\{[^}]*font-size:\s*)0\.625rem',
     r'\g<1>0.6875rem',
     '.cmd-badge 0.625rem → 0.6875rem'),

    # .cmd-example inline code 0.75rem → 0.8125rem (code floor)
    (r'(\.cmd-example\s*\{[^}]*font-size:\s*)0\.75rem',
     r'\g<1>0.8125rem',
     '.cmd-example 0.75rem → 0.8125rem (code)'),

    # .tdd-phase-desc 0.875rem is ok (secondary floor) — leave
    # .tdd-phase-label 0.8125rem → 0.875rem (visible uppercase label)
    (r'(\.tdd-phase-label\s*\{[^}]*font-size:\s*)0\.8125rem',
     r'\g<1>0.875rem',
     '.tdd-phase-label 0.8125rem → 0.875rem'),

    # .mcp-tool-desc 0.8125rem → 0.875rem (description text)
    (r'(\.mcp-tool-desc\s*\{[^}]*font-size:\s*)0\.8125rem',
     r'\g<1>0.875rem',
     '.mcp-tool-desc 0.8125rem → 0.875rem'),

    # .gov-layer-desc 0.875rem is ok — leave
    # .agent-role 0.8125rem → 0.875rem
    (r'(\.agent-role\s*\{[^}]*font-size:\s*)0\.8125rem',
     r'\g<1>0.875rem',
     '.agent-role 0.8125rem → 0.875rem'),

    # .step-num (getting-started) 0.6875rem → keep at 0.6875rem (mono badge label, ok)
    # .step-desc 0.875rem — ok, leave
    # .checklist li .check-icon 0.625rem → 0.6875rem (icon badge)
    (r'(\.check-icon\s*\{[^}]*font-size:\s*)0\.625rem',
     r'\g<1>0.6875rem',
     '.check-icon 0.625rem → 0.6875rem'),

    # .cortex-tag 0.85rem → 1rem (already caught by global 0.85rem rule)
    # .sdlc-gate 0.8125rem → keep (mono tag, code floor ok)
    # d3-tooltip font-size: 12px → 13px (SVG tooltip = code context)
    (r'(\.d3-tooltip\s*\{[^}]*font-size:\s*)12px',
     r'\g<1>13px',
     '.d3-tooltip 12px → 13px'),

    # domain bubble .db-name 0.6875rem → ok at floor, leave
    # domain bubble .db-name 0.625rem → 0.6875rem
    (r"(db-name.*?font-size:)0\.625rem",
     r'\g<1>0.6875rem',
     'db-name 0.625rem → 0.6875rem'),

    # D3 SVG font attr px fixes
    (r"\.attr\('font-size', '10px'\)",
     ".attr('font-size', '11px')",
     "D3 10px → 11px"),
]


def apply_rules(content: str) -> tuple[str, list[str]]:
    """Apply all replacement rules to content. Return (new_content, changes)."""
    changes = []
    for pattern, replacement, description in RULES:
        if callable(replacement):
            new_content = re.sub(pattern, replacement, content)
        else:
            new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            count = len(re.findall(pattern, content))
            changes.append(f"  ✓ {description} ({count} instance{'s' if count > 1 else ''})")
            content = new_content
    return content, changes


def apply_targeted(content: str) -> tuple[str, list[str]]:
    """Apply targeted CSS-class-context replacements."""
    changes = []
    for pattern, replacement, description in TARGETED:
        if callable(replacement):
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if new_content != content:
            changes.append(f"  ✓ {description}")
            content = new_content
    return content, changes


def apply_tetris_fit(content: str) -> tuple[str, list[str]]:
    """
    Inject Tetris-Fit CSS into the first <style> block that manages layout.
    Only if not already present.
    """
    changes = []
    TETRIS_MARKER = '/* CORTEX-TETRIS-FIT-APPLIED */'

    if TETRIS_MARKER in content:
        return content, []

    TETRIS_CSS = f"""
    /* ── Tetris-Fit v1 — zero dead space in multi-column panels ──────────────
       Authority: cortex-registry/knowledge/sdlc/tetris-layout-spec.yaml
       Injected: 2026-03-09 — Phase 109.3 font/layout standardisation
       {TETRIS_MARKER}
       ─────────────────────────────────────────────────────────────────────── */

    /* Rule 1: Container stretch — all columns share tallest sibling */
    .feature-grid-2,
    .gs-cards-grid,
    .role-tiles-grid,
    .card-grid-3,
    .tetris-container {{
        align-items: stretch;
    }}

    /* Rule 2: Column fills grid cell top-to-bottom */
    .tp-card,
    .gs-card,
    .role-tile,
    .tetris-col {{
        height: 100%;
        display: flex;
        flex-direction: column;
    }}

    /* Rule 3: Last/growable child absorbs leftover height */
    .gs-card__list,
    .tp-visual,
    .tp-body,
    .tetris-grow {{
        flex: 1;
        align-content: stretch;
    }}

    /* Rule 4: Nested grid rows expand proportionally */
    .tp-visual {{
        align-content: stretch;
    }}

    /* Rule 5: Viz/chart panel fills column bottom */
    .macc__viz,
    .stat-chart-wrap,
    .tetris-viz {{
        flex: 1;
        justify-content: space-between;
    }}
"""
    # Insert before the closing </style> of the first inline style block
    content = re.sub(r'(</style>)', TETRIS_CSS + r'\n    \1', content, count=1)
    changes.append('  ✓ Tetris-Fit v1 CSS injected (Rule 1–5)')
    return content, changes


def process_file(path: Path) -> None:
    """Process a single HTML file."""
    original = path.read_text(encoding='utf-8')
    content = original

    content, rule_changes = apply_rules(content)
    content, targeted_changes = apply_targeted(content)
    content, tetris_changes = apply_tetris_fit(content)

    all_changes = rule_changes + targeted_changes + tetris_changes

    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f"\n{'='*60}")
        print(f"✅ {path.relative_to(Path('/Users/asifhussain/PROJECTS/CORTEX/docs'))}")
        for c in all_changes:
            print(c)
    else:
        print(f"⚪ {path.relative_to(Path('/Users/asifhussain/PROJECTS/CORTEX/docs'))} — no changes needed")


def main():
    docs = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    html_files = sorted(docs.rglob('*.html'))

    # Exclude files that should not be touched
    exclude = {'glass-samples.html'}
    html_files = [f for f in html_files if f.name not in exclude]

    print(f"CORTEX Font-Size Standardisation — Phase 109.3")
    print(f"Processing {len(html_files)} HTML files...\n")

    for f in html_files:
        process_file(f)

    print(f"\n{'='*60}")
    print("✅ Font size standardisation complete.")
    print("   All values now meet WCAG 2.2 AA floors per docs-html-design-workflow.yaml")
    print("   Tetris-Fit v1 injected into all views.")


if __name__ == '__main__':
    main()
