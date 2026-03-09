---
scope: non-production-admin
---
# Diagram Regeneration Agent

**Agent ID:** `diagram-regeneration-agent`  
**Updated:** 2026-03-08 (Phase 109.1 — motion_ux_standards wired for D3 transitions; content_writing_standards wired for caption copy; wcag22_delta wired for WCAG 2.2 touch target checks)
**Layer:** docs  
**Status:** active  
**Responsibility:** Regenerate D3.js SVG diagrams and CSS-based visuals when architecture changes  
**Inputs:** Change manifest (architectural shifts), drift report (stale diagrams), live file system, motion_ux_standards.yaml, content_writing_standards.yaml, wcag22_delta_checklist.yaml
**Outputs:** Updated D3.js HTML/SVG diagram files  
**Library Policy:** D3.js v7.9.0 ONLY — Mermaid.js is BANNED (see `visualization_standards.yaml`)

---

## 🎯 Single Responsibility

Detect when architecture diagrams no longer reflect the live system and regenerate them using D3.js SVG and CSS visuals. This agent owns all diagram files in `docs/assets/diagrams/`.

**⛔ Mermaid.js is permanently banned.** Zero `.mmd` files exist in this workspace. All diagrams are D3.js SVG or CSS-based. See `docs/.content/knowledge/visualization_standards.yaml` for the full library policy.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Change manifest** | `git-discovery-agent` → `architectural_shifts` | ✅ |
| **Drift report** | `drift-detection-agent` → `stale_diagrams` | ✅ |
| **Live orchestrator list** | `cortex/orchestrators/` directory scan | ✅ |
| **Live MCP tool list** | `cortex/mcp/mcp_registry.py` | ✅ |
| **Governance rule list** | `cortex-registry/core/*.yaml` | ✅ |
| **Workflow templates** | `cortex-registry/workflows/templates/` | ✅ |
| **Visualization standards** | `docs/.content/knowledge/visualization_standards.yaml` | ✅ |

---

## 📤 Outputs

All outputs are D3.js SVG rendered inside HTML files. Zero `.mmd` files.

| Output | Path | Format | D3.js Method |
|--------|------|--------|--------------|
| Architecture overview | `docs/assets/diagrams/d3/architecture-overview.html` | HTML + D3.js v7 SVG | `d3.forceSimulation` (force-directed) |
| Request flow | `docs/assets/diagrams/d3/request-flow.html` | HTML + D3.js v7 SVG | `d3.sankey` (Sankey flow) |
| Orchestrator tier map | `docs/assets/diagrams/d3/orchestrator-tier-map.html` | HTML + D3.js v7 SVG | `d3.tree` (layered hierarchy) |
| LENS pipeline | `docs/assets/diagrams/d3/lens-pipeline.html` | HTML + D3.js v7 SVG | Custom SVG pipeline |
| Governance flow | `docs/assets/diagrams/d3/governance-flow.html` | HTML + D3.js v7 SVG | `d3.tree` + animated paths |
| MCP transport | `docs/assets/diagrams/d3/mcp-transport.html` | HTML + D3.js v7 SVG | Custom SVG sequence |
| TDD workflow | `docs/assets/diagrams/d3/tdd-workflow.html` | HTML + D3.js v7 SVG | Custom SVG cycle |
| Testing pyramid | `docs/assets/diagrams/d3/testing-pyramid.html` | HTML + D3.js v7 SVG | `d3.treemap` / stacked |
| Governance pyramid | `docs/assets/diagrams/d3/governance-pyramid.html` | HTML + D3.js v7 SVG | `d3.partition` (sunburst) |
| Request lifecycle Sankey | `docs/assets/diagrams/d3/request-lifecycle-sankey.html` | HTML + D3.js v7 SVG | `d3.sankey` |

---

## 🔍 Regeneration Triggers

A diagram is regenerated when ANY of the following occur:

| Trigger | Detection Method | Affected Diagrams |
|---------|-----------------|-------------------|
| **Orchestrator count change** | File count in `cortex/orchestrators/` changed | `architecture-overview`, `orchestrator-tier-map` |
| **New orchestrator tier** | New subdirectory in `cortex/orchestrators/` | `orchestrator-tier-map`, `request-flow` |
| **MCP tool count change** | Registry entries changed in `mcp_registry.py` | `mcp-transport`, `architecture-overview` |
| **Governance rule change** | Files changed in `cortex-registry/core/` | `governance-flow` |
| **Intelligence facade change** | `cortex/intelligence/facade.py` modified | `lens-pipeline`, `architecture-overview` |
| **Workflow template change** | Files changed in `cortex-registry/workflows/` | `request-flow` |
| **Intent routing change** | `cortex/orchestrators/core/intent_router.py` modified | `request-flow`, `orchestrator-tier-map` |
| **Debug strategy change** | Files changed in `cortex/orchestrators/support/debugging/` | `architecture-overview` |

---

## 📐 Diagram Standards

### Approved Library: D3.js v7.9.0 ONLY

| Property | Value |
|----------|-------|
| **Library** | D3.js v7.9.0 |
| **CDN** | `https://d3js.org/d3.v7.min.js` |
| **Rendering** | All output is `<svg>` inside HTML — never `<canvas>` |
| **Theme** | Dark glassmorphism (page bg `#0a0e27`, glass `rgba(26,31,58,0.7)`) |
| **Banned** | Mermaid.js, Chart.js, Plotly, Recharts, Vis.js, GoJS, JointJS, Cytoscape.js |

### D3.js SVG Standards

All D3.js diagram HTML files MUST include:

```yaml
d3_standards:
  version: "v7.9.0"
  cdn: "https://d3js.org/d3.v7.min.js"
  rendering: svg_only  # NEVER canvas
  features:
    - filter_buttons        # Show/hide layers
    - hover_tooltip         # Node description on hover
    - drag_nodes            # Rearrange layout (d3.drag)
    - zoom_pan              # D3 zoom behavior (d3.zoom)
  glassmorphism_theme:
    page_bg: "#0a0e27"
    svg_bg: "transparent"    # SVG bg inherits page
    glass_panel: "rgba(26,31,58,0.7)"
    glass_border: "rgba(0,212,255,0.15)"
    glass_blur: "backdrop-filter: blur(12px)"
    node_colors:
      core: "#00d4ff"        # Cyan for core components
      domain: "#7b61ff"      # Purple for domain components
      support: "#10b981"     # Emerald for support components
      governance: "#f59e0b"  # Amber for governance
      external: "#6b7280"    # Gray for external systems
    edge_color: "rgba(148,163,184,0.4)"
    glow_filter: true        # SVG feGaussianBlur for depth
  node_labels:
    style: full_english      # No abbreviations or truncations
    casing: PascalCase       # For component names
    counts: exact            # Must match live system counts
  validation:
    no_orphan_nodes: true    # Every node must be connected
    no_dead_flows: true      # Every arrow must lead somewhere
```

### SVG Text Accessibility Font Floors (P0 — IMMUTABLE)

**SSOT:** `docs/.content/knowledge/visualization_standards.yaml` § `svg_text_accessibility`

All SVG `<text>` elements MUST meet these minimum sizes. Dark backgrounds require larger sizes than light themes for equivalent readability.

| SVG Element | Minimum `font-size` | Font Family | `fill` Colour |
|-------------|---------------------|-------------|----------------|
| Node labels | `14px` | Inter, sans-serif | `#e2e8f0` (slate-200) |
| Edge labels | `12px` | Inter, sans-serif | `#94a3b8` (slate-400) |
| Axis labels | `12px` | Inter, sans-serif | `#94a3b8` |
| Tooltip text | `14px` | Inter, sans-serif | `#f1f5f9` (slate-100) |
| Title / heading | `18px` | Space Grotesk, sans-serif | `#f8fafc` (slate-50) |
| Legend text | `12px` | Inter, sans-serif | `#cbd5e1` (slate-300) |
| Stat numbers | `28px` | Space Grotesk, sans-serif | `#00d4ff` (accent) |
| Code / mono text | `13px` | JetBrains Mono, monospace | `#e2e8f0` |
| Annotations | `11px` | Inter, sans-serif | `#64748b` (slate-500) |

**Absolute floor:** No SVG text below `11px` for any visible element.

### SVG Colour & Contrast Rules

| Rule | Value |
|------|-------|
| **Text on dark bg** | Contrast ≥ 4.5:1 (WCAG AA) |
| **Large text (≥18px)** | Contrast ≥ 3:1 |
| **Accent vs bg** | `#00d4ff` on `#0a0e27` = 8.3:1 ✅ |
| **Never use** | `#64748b` on `#0a0e27` for primary text (2.8:1 — fails AA) |
| **Glow effects** | Decorative only — never sole distinguishing feature |

### ARIA & Screen Reader Rules for SVG

| Rule | Implementation |
|------|---------------|
| SVG `role` | `role="img"` on root `<svg>` |
| SVG `aria-labelledby` | Points to `<title>` + `<desc>` inside SVG |
| `<title>` | Diagram name (e.g. "CORTEX Architecture Overview") |
| `<desc>` | 1-sentence purpose (e.g. "Force-directed graph showing 5 orchestrator tiers") |
| Interactive nodes | `role="button"` + `aria-label="{node name}"` + `tabindex="0"` |
| Keyboard navigation | `Tab` to focus nodes, `Enter/Space` to activate, `Escape` to dismiss tooltip |

---

## 🔄 Regeneration Process

### Step 1: Inventory Live Architecture

```
1. Count orchestrator files per tier:
   find cortex/orchestrators/core -name "*.py" | wc -l → core_count
   find cortex/orchestrators/domain -name "*.py" | wc -l → domain_count
   find cortex/orchestrators/support -name "*.py" | wc -l → support_count
   (repeat for all tiers)

2. List registered MCP tools:
   grep "register" cortex/mcp/mcp_registry.py → tool_list

3. List governance rules:
   find cortex-registry/core -name "*.yaml" → rule_list

4. List intent types:
   grep IntentType cortex/models/canonical_enums.py → intent_list
```

### Step 2: Compare Against Current Diagrams

```
For each D3.js diagram HTML file:
  1. Parse existing SVG nodes and edges
  2. Compare against live inventory
  3. Identify missing nodes (new components)
  4. Identify orphaned nodes (deleted components)
  5. Identify label mismatches (renamed components)
```

### Step 3: Regenerate

```
For each stale diagram:
  1. Preserve layout intent (approximate positions, groupings)
  2. Update D3.js data arrays to match live architecture
  3. Update edges/links to match current flow
  4. Update counts in labels
  5. Add version annotation (data-generated timestamp)
  6. Enforce SVG font floors from visualization_standards.yaml
  7. Write updated .html file to docs/assets/diagrams/d3/
```

### Step 4: Validate

```
For each regenerated diagram:
  1. Verify all live components are represented as SVG nodes
  2. Verify no deleted components remain
  3. Verify counts in labels match live system
  4. Verify D3.js HTML loads without JS console errors
  5. Verify SVG text font-size >= 11px (absolute floor)
  6. Verify ARIA attributes present (role, aria-labelledby, title, desc)
  7. Verify keyboard navigation works (Tab + Enter)
  8. Verify contrast ratios meet WCAG AA (4.5:1 for normal text)
  9. Verify responsive rendering:
     a. Mobile (≤480px): diagram readable, nodes ≥44×44px touch target,
        no horizontal overflow, labels not truncated below 13px
     b. Tablet (≤768px): layout condensed, legends stacked if needed,
        font scaling applied (node labels ≥15px, edge labels ≥13px)
     c. Desktop (≥769px): full layout, all interactions enabled
     d. SVG container has width:100%, height:auto, max-width:1200px
     e. No overflow:hidden on .cortex-diagram — use overflow-x:auto
 10. Verify section spacing:
     a. Diagram has ≥2rem margin before/after surrounding text
     b. Stacked diagrams have ≥3rem separation
     c. Container padding ≥1.5rem (≥1rem on mobile)
     d. SVG internal content has ≥20px from viewBox edges (≥12px on mobile)
 11. Verify glassmorphism colour harmony:
     a. Node fills use rgba() with 0.6–0.8 opacity (never solid)
     b. Edge strokes use 0.3–0.5 opacity
     c. Glow filter stdDeviation ≤ 4
     d. No warm/cool accent mixing in same diagram
     e. Colour triad: #00d4ff + #7b61ff + #10b981 only
 12. Verify motion safety (motion_ux_standards.yaml):
     a. safeTransition() helper present and used for all .transition() calls
     b. prefersReducedMotion flag declared at top of script
     c. No animation durations outside CORTEX scale (100/150/200/300/400/500ms)
     d. No backdrop-filter in any transition or animation
     e. Composited-only: only transform + opacity animated
 13. Verify WCAG 2.2 touch targets (wcag22_delta_checklist.yaml SC 2.5.8):
     a. All interactive SVG nodes ≥ 24×24px minimum touch target
     b. Preferred: ≥ 44×44px for primary interactive nodes
     c. Legend toggle buttons ≥ 44×44px on mobile
 14. Verify figcaption copy (content_writing_standards.yaml):
     a. Active voice, present tense
     b. No "Shown above is…" or "This diagram depicts…" patterns
     c. Max 120 characters
```

---

## 📊 Diagram Catalog (18 Diagrams — All D3.js SVG)

### Architecture Diagrams (8)

| # | Diagram | Purpose | D3.js Method | Audience |
|---|---------|---------|--------------|----------|
| 1 | `architecture-overview` | High-level 5-tier system view | `d3.forceSimulation` | All |
| 2 | `request-flow` | End-to-end request lifecycle | `d3.sankey` | Engineer, Product |
| 3 | `orchestrator-tier-map` | Tier hierarchy with counts | `d3.tree` | Engineer |
| 4 | `lens-pipeline` | LENS 4-phase analysis | Custom SVG pipeline | Engineer |
| 5 | `governance-flow` | Rule enforcement lifecycle | `d3.tree` + animated paths | Engineer, Leader |
| 6 | `mcp-transport` | MCP communication flow | Custom SVG sequence | Engineer |
| 7 | `tdd-workflow` | TDD RED→GREEN→REFACTOR cycle | Custom SVG cycle | Engineer |
| 8 | `testing-pyramid` | Test tier hierarchy | `d3.treemap` stacked | Engineer |

### Data Visualization Diagrams (6)

| # | Diagram | Purpose | D3.js Method | Audience |
|---|---------|---------|--------------|----------|
| 9 | `governance-pyramid` | Sunburst of governance tiers | `d3.partition` (sunburst) | Leader, Product |
| 10 | `request-lifecycle-sankey` | Request flow with volume | `d3.sankey` | Product, Engineer |
| 11 | `domain-distribution` | Orchestrator domain bubble grid | `d3.pack` (bubble) | Leader |
| 12 | `test-coverage-heatmap` | Coverage by module | `d3.scaleBand` (heatmap) | Engineer |
| 13 | `intent-routing-chord` | Intent→Orchestrator routing | `d3.chord` | Engineer |
| 14 | `phase-burndown` | Phase completion timeline | `d3.scaleTime` (timeline) | Product, Leader |

### Mind Map / Conceptual Diagrams (4)

| # | Diagram | Purpose | D3.js Method | Audience |
|---|---------|---------|--------------|----------|
| 15 | `capability-mind-map` | Feature exploration tree | `d3.tree` (radial) | Learner |
| 16 | `brain-region-mapping` | Brain analogy → domain map | `d3.pack` (nested circles) | Learner, Leader |
| 17 | `sdlc-pipeline` | CSS flexbox phase cards | CSS Grid + CSS only | All |
| 18 | `tdd-knowledge-cycle` | Circular learning flow | Custom SVG arc cycle | Learner |

---

## 🛡️ Safety

- **Non-destructive** — old diagrams are backed up before overwrite
- **Validated** — SVG structure + font floors + ARIA + responsive + motion + caption checks before write
- **Versioned** — every diagram includes `data-generated` timestamp
- **Auditable** — regeneration logged to `.cortex-runtime/traces/orchestrator-traces.db`
- **Accessible** — WCAG 2.2 AA compliant (contrast, keyboard, screen reader, touch targets ≥ 24px per wcag22_delta_checklist.yaml SC 2.5.8)
- **Motion-safe** — all D3 `.transition()` calls gated by `prefers-reduced-motion` check (motion_ux_standards.yaml); composited-only properties (transform + opacity); CORTEX duration scale enforced
- **Responsive** — validated at mobile (≤480px), tablet (≤768px), and desktop breakpoints
- **Glassmorphism-harmonised** — rgba() fills, approved colour triad, glow ≤ 4 stdDeviation
- **Copy-compliant** — all `<figcaption>` and `<desc>` text follows active voice + present tense (content_writing_standards.yaml): "The LENS pipeline analyzes…" not "Shown above is the LENS pipeline…"

### Caption & Description Copy Standards (from `content_writing_standards.yaml`)

Every `<figcaption>` and SVG `<desc>` generated by this agent MUST follow:

| Rule | Example |
|------|---------|
| Active voice | ✅ "Fifteen orchestrator domains route 35+ intent types." ❌ "35+ intent types are routed by the 15 orchestrator domains." |
| Present tense | ✅ "The convergence gate loops until all P0 issues resolve." ❌ "The gate will loop until all issues are resolved." |
| Outcome-led | ✅ "The TDD cycle enforces RED→GREEN→REFACTOR discipline." ❌ "This diagram shows the TDD cycle." |
| Max 120 chars | Captions are scannable — never paragraph-length |
| No "shown above" | ❌ "Shown above is…" / "The diagram above depicts…" → always describe directly |

### Motion Safety Contract (from `motion_ux_standards.yaml`)

All generated D3.js diagram JavaScript MUST include the canonical motion safety pattern:

```javascript
// Required at top of every generated diagram script
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function safeTransition(selection, duration = 200, easeFn = d3.easeCubicInOut) {
  return prefersReducedMotion
    ? selection
    : selection.transition().duration(duration).ease(easeFn);
}
// Use safeTransition() for ALL node enters, updates, and layout changes
```

**D3 animation properties — composited-only (P1 violation if non-composited):**
- ✅ Animate: `opacity`, `transform` (via `attr('transform', ...)`)
- ❌ NEVER animate: `r` (circle radius), `width`, `height`, `x`, `y` directly on non-transform attributes (use transform instead), `fill`, `stroke-width`
