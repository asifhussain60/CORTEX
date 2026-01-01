# 🎨 Level 2 Documentation Glassmorphism Standardization Plan

**Version:** 2.1.0 | **Status:** 🟡 ACTIVE  
**Author:** Asif Hussain | **Created:** December 31, 2025  
**Updated:** December 31, 2025  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 📋 Executive Summary

This plan standardizes the **entire CORTEX documentation hierarchy** (Levels 0-3) to follow the **Glassmorphism Design Standard v3.1.0**, with distinct visual treatments per level. **Maximum nesting depth is Level 3** — no deeper views allowed.

---

## 🏗️ View Hierarchy Architecture

### ⛔ CRITICAL RULE: Maximum 3 Levels Deep
```
Level 0 → Level 1 → Level 2 → Level 3 (MAX)
   ↓         ↓         ↓         ↓
 Home    Category   Feature    Detail
```

**NO Level 4+ views permitted.** If content requires deeper nesting, consolidate into Level 3 with expandable sections.

---

## 🎬 Animation Tier System (NEW v2.1.0)

### ⛔ CRITICAL: Subtle Animations by Default

**User Directive:** "I want glassmorphism to have subtle animation, not the kind used on skull protector tiles and knowledge graph."

### Animation Tiers

| Tier | Name | Use Case | Examples |
|------|------|----------|----------|
| **T1** | **Subtle** (DEFAULT) | All standard pages, documentation, feature pages | Hover opacity, light transforms, simple transitions |
| **T2** | **Accent** | Interactive elements requiring user feedback | Button press, form focus, selection highlight |
| **T3** | **Dramatic** | HERO sections, landing pages, special showcases ONLY | borderGlowSweep, blobMorph, particle effects |

### Tier 1: Subtle Animations (DEFAULT FOR ALL PAGES)

```css
/* ✅ APPROVED - Subtle hover effects */
.glass-card {
    transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    opacity: 0.95;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* ✅ APPROVED - Simple focus states */
.interactive-element:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* ✅ APPROVED - Gentle transitions */
.nav-link {
    transition: color 0.2s ease, background-color 0.2s ease;
}
```

**Subtle Animation Properties:**
- `transition-duration: 0.2s - 0.3s` (fast, responsive)
- `transform: translateY(-2px to -4px)` (minimal lift)
- `opacity: 0.9 - 1.0` (slight dimming on hover)
- No infinite animations
- No keyframe animations on cards
- No glow pulses or sweeps

### Tier 2: Accent Animations (Interactive Feedback)

```css
/* ✅ APPROVED - Button feedback */
.btn-glass:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}

/* ✅ APPROVED - Form focus */
input:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
    transition: all 0.2s ease;
}

/* ✅ APPROVED - Selection indicator */
.tab-active {
    border-bottom: 2px solid var(--accent-primary);
    transition: border-color 0.2s ease;
}
```

### Tier 3: Dramatic Animations (RESTRICTED)

**⛔ ONLY ALLOWED ON:**
- `docs/index.html` (Home page hero)
- Landing page hero sections
- Special showcase pages (explicitly marked)

**❌ FORBIDDEN ON:**
- Level 2 feature pages
- Documentation content pages
- Architecture visualization pages
- Orchestrator detail pages

```css
/* ❌ DEPRECATED for standard pages */
@keyframes borderGlowSweep { /* HERO ONLY */ }
@keyframes blobMorph { /* HERO ONLY */ }
@keyframes lightLeakPrimary { /* HERO ONLY */ }
@keyframes glowPulse { /* HERO ONLY */ }
```

### Pages Requiring Animation Simplification

| Page | Current | Target | Action |
|------|---------|--------|--------|
| `skull-protection.html` | T3 (borderGlowSweep, pulse) | T1 (subtle hover) | 🔴 SIMPLIFY |
| `knowledge-graph.html` | T3 (glow filters, sweeps) | T1 (subtle hover) | 🔴 SIMPLIFY |
| `architecture/index.html` | T1 | T1 | ✅ OK |
| `orchestrators/index.html` | T1 | T1 | ✅ OK |

---

## 📊 Visual Progress Tracking

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 OVERALL PROGRESS                                            │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ 10%       │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
│  PHASE 0: Functionality Discovery         [✓] 6/6 tasks ✅     │
│  PHASE 1: Foundation (CSS/Variables)      [✓] 4/4 tasks ✅     │
│  PHASE 2: High Priority Views             [■] 3/5 views        │
│  PHASE 3: Medium Priority Views           [ ] 0/6 views        │
│  PHASE 4: D3.js Visualizations            [■] 2/10 components  │
│  PHASE 5: Mermaid Diagrams                [ ] 0/8 diagrams     │
│  PHASE 6: Micro-Interactions              [ ] 0/5 patterns     │
│  PHASE 7: Mobile Responsiveness           [ ] 0/6 tasks        │
│  PHASE 8: Testing & Validation            [ ] 0/4 checks       │
│  PHASE 9: REFACTOR (Animation Cleanup)    [ ] 0/3 tasks        │
│                                                                 │
│  LEVEL 0: Home Page                       [✓] APPROVED ✅       │
│  LEVEL 1: Category Index Pages            [✓] 9/9 APPROVED ✅   │
│  LEVEL 2: Feature Pages                   [■] 3/29 views       │
│  LEVEL 3: Detail Pages                    [✓] Use modals       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Phase Breakdown

### Phase 0: Functionality Discovery ✅ COMPLETE
**Duration:** 1-2 sessions | **Completed:** December 31, 2025

| Task | Description | Output | Status |
|------|-------------|--------|--------|
| 0.1 | Orchestrator Inventory | 20 orchestrators documented | ✅ |
| 0.2 | SKULL Rules Audit | 15 layers, 118 rules | ✅ |
| 0.3 | Knowledge Graph Metrics | 54 patterns (YAML-based) | ✅ |
| 0.4 | TDD Workflow Analysis | 3 phases documented | ✅ |
| 0.5 | Memory Tier Structure | 3 active tiers | ✅ |
| 0.6 | API & Command Mapping | 15 command routes | ✅ |

---

### Phase 1: Foundation Setup ✅ COMPLETE
**Duration:** 1 session | **Completed:** December 31, 2025

| Task | Description | Status |
|------|-------------|--------|
| 1.1 | Update `main.css` with v3.0 glass patterns | ✅ |
| 1.2 | Create `variables.css` design tokens | ✅ |
| 1.3 | Create `glass-patterns.css` component library | ✅ |
| 1.4 | Add `micro-interactions.css` library | ✅ |

**Files Created:**
- `docs/assets/css/variables.css` - 230+ lines of design tokens
- `docs/assets/css/glass-patterns.css` - 5 glass patterns + 5 UI components
- `docs/assets/css/micro-interactions.css` - Ripple, tilt, glow, shimmer effects

---

### Phase 2: High Priority Views (Architecture)
**Duration:** 2-3 sessions | **Priority:** 🔴 HIGH

| View | File | Status | Notes |
|------|------|--------|-------|
| Architecture Overview | `architecture/index.html` | ✅ | D3.js 4-tier diagram |
| SKULL Protection | `architecture/skull-protection.html` | ✅ | 15 layers, 118 rules - **NEEDS ANIMATION SIMPLIFICATION** |
| Knowledge Graph | `architecture/knowledge-graph.html` | ✅ | D3.js force-directed (54 patterns) - **NEEDS ANIMATION SIMPLIFICATION** |
| Development Context | `architecture/development-context.html` | ⬜ | D3.js heatmap |
| Orchestrator Map | `orchestrators/index.html` | ✅ | Enhanced D3.js |

**Layout Requirements (v3.1.0):**
- **Metrics Dashboard:** Pattern 6 (Centered Flexbox) - NOT CSS Grid
- **Navigation Footer:** Pattern 7 (Balanced Navigation) with equal-width buttons
- **Animations:** T1 (Subtle) ONLY - no borderGlowSweep, no glow pulses

---

### Phase 3: Medium Priority Views
**Duration:** 2-3 sessions | **Priority:** 🟡 MEDIUM

| View | File | Status |
|------|------|--------|
| Holistic Discovery | `features/holistic-discovery.html` | ⬜ |
| Token Optimization | `features/token-optimization.html` | ⬜ |
| TDD Orchestrator | `orchestrators/tdd-orchestrator.html` | ⬜ |
| Planning System | `orchestrators/planning-system.html` | ⬜ |
| Debug Orchestrator | `orchestrators/debug-orchestrator.html` | ⬜ |
| Intelligent Dashboard | `orchestrators/intelligent-dashboard.html` | ⬜ |

---

### Phase 4: D3.js Visualization Components
**Duration:** 3-4 sessions | **Priority:** 🟡 MEDIUM

| Component | Target View | Status |
|-----------|-------------|--------|
| 4-Tier Sankey | Architecture Overview | ✅ |
| Force-Directed Graph | Knowledge Graph | ✅ |
| Concentric Rings | SKULL Protection | ✅ |
| Thermal Treemap | Development Context | ⬜ |
| Token Distribution Bar | Token Optimization | ⬜ |
| TDD Cycle Ring | TDD Orchestrator | ⬜ |
| Root Cause Tree | Debug Orchestrator | ⬜ |
| Pipeline Flow | Intelligent Dashboard | ⬜ |
| Complexity Tier Chart | Planning System | ⬜ |
| Enhanced Orchestrator Map | Orchestrators Index | ⬜ |

**Animation Standard for D3.js:**
- Node hover: `opacity` and `stroke-width` only
- Transitions: `0.2s ease` duration
- No infinite glow animations
- No filter effects on hover

---

### Phase 5: Mermaid Diagram Integration
**Duration:** 1-2 sessions | **Priority:** 🟢 STANDARD

| Diagram | Target View | Type | Status |
|---------|-------------|------|--------|
| 4-Phase Planning Flow | Planning System | stateDiagram-v2 | ⬜ |
| TDD Cycle | TDD Orchestrator | flowchart LR | ⬜ |
| Debug Loop | Debug Orchestrator | sequenceDiagram | ⬜ |
| 3-Step Discovery | Holistic Discovery | flowchart TD | ⬜ |
| 15-Layer Shield | SKULL Protection | graph LR | ⬜ |
| Token Tiers | Token Optimization | pie | ⬜ |
| Sanitization Pipeline | Sanitization Orchestrator | flowchart LR | ⬜ |
| ADO Work Item Flow | ADO Operations | flowchart TD | ⬜ |

---

### Phase 6: Micro-Interactions Implementation
**Duration:** 1 session | **Priority:** 🟢 STANDARD

| Interaction | Pattern | Animation Tier | Status |
|-------------|---------|----------------|--------|
| Hover Effects | Simple transform | T1 (Subtle) | ⬜ |
| Focus States | Outline + shadow | T2 (Accent) | ⬜ |
| Button Feedback | Scale on press | T2 (Accent) | ⬜ |
| Form Validation | Border color | T2 (Accent) | ⬜ |
| Loading States | Opacity pulse | T1 (Subtle) | ⬜ |

**⛔ DEPRECATED Interactions (remove from standard pages):**
- ~~Ripple Effect (`ripple-glass`)~~ → Too dramatic
- ~~3D Tilt (`tilt-glass`)~~ → Too dramatic
- ~~Glow Pulse (`pulse-glow-glass`)~~ → Too dramatic
- ~~Magnetic Hover (`magnetic-glass`)~~ → Too dramatic

---

### Phase 7: Mobile Responsiveness 📱
**Duration:** 2 sessions | **Priority:** 🔴 HIGH

| Task | Description | Status |
|------|-------------|--------|
| 7.1 | Viewport Meta Tags | ⬜ |
| 7.2 | Mobile-First CSS | ⬜ |
| 7.3 | Touch-Friendly Targets (44x44px min) | ⬜ |
| 7.4 | D3.js Responsive SVGs | ⬜ |
| 7.5 | Conditional Blur (disable on low-end) | ⬜ |
| 7.6 | Navigation Adaptation | ⬜ |

---

### Phase 8: Testing & Validation
**Duration:** 1 session | **Priority:** 🔴 REQUIRED

| Test | Tool | Pass Criteria | Status |
|------|------|---------------|--------|
| Visual Regression | Percy/Chromatic | No unexpected changes | ⬜ |
| Performance | Lighthouse | Score ≥90 | ⬜ |
| Accessibility | axe DevTools | 0 violations | ⬜ |
| Cross-Browser | BrowserStack | Chrome, Firefox, Safari, Edge | ⬜ |

---

### Phase 9: REFACTOR (Animation Cleanup) ⚠️ SKULL ENFORCED
**Duration:** 1 session | **Priority:** 🔴 MANDATORY

| Task | Description | Status |
|------|-------------|--------|
| 9.1 | Remove `borderGlowSweep` from all Level 2 pages | ⬜ |
| 9.2 | Remove `blobMorph` from all Level 2 pages | ⬜ |
| 9.3 | Replace `glowPulse` with simple hover transitions | ⬜ |
| 9.4 | Audit all pages for T3 animations on non-hero sections | ⬜ |
| 9.5 | Consolidate duplicate glass patterns | ⬜ |
| 9.6 | Update inline styles to CSS variables | ⬜ |

**SKULL Rule Enforcement:**
- ✅ `REFACTOR_CLEANUP`: Remove orphaned dramatic animation styles
- ✅ `HOLISTIC_DISCOVERY`: Verify no duplicate patterns created
- ✅ `TDD_ENFORCEMENT`: All changes tested before merge

---

## 📁 Complete File Inventory

### Level 0 (1 file)
```
docs/index.html                      # ✅ APPROVED - Dramatic animations OK (hero)
```

### Level 1 (9 files) - ALL APPROVED
```
docs/
├── architecture/index.html          # ✅ Modernized
├── security/index.html              # ✅ Approved
├── orchestrators/index.html         # ✅ EXEMPLAR
├── token-optimization/index.html    # ✅ Approved
├── sts/index.html                   # ✅ Approved
├── knowledge/index.html             # ✅ Approved
├── toolkit-manager/index.html       # ✅ Approved
├── lens/index.html                  # ✅ Approved
└── getting-started/index.html       # ✅ Approved
```

### Level 2 (29 files) - 3/29 COMPLETE
```
docs/architecture/
├── skull-protection.html            # ✅ Done - NEEDS ANIMATION SIMPLIFICATION
├── knowledge-graph.html             # ✅ Done - NEEDS ANIMATION SIMPLIFICATION
└── development-context.html         # ⬜

docs/orchestrators/
├── tdd-orchestrator.html            # ⬜
├── planning-system.html             # ⬜
├── debug-orchestrator.html          # ⬜
├── ado-operations.html              # ⬜
├── sanitization-orchestrator.html   # ⬜
├── execution-orchestrator.html      # ⬜
├── intelligent-dashboard.html       # ⬜
├── cleanup-orchestrator.html        # ⬜
├── refinement-orchestrator.html     # ⬜
├── onboarding-orchestrator.html     # ⬜
├── cortex-lens.html                 # ⬜
├── git-checkpoint.html              # ⬜
├── pre-flight.html                  # ⬜
├── rollback-orchestrator.html       # ⬜
├── system-integrity.html            # ⬜
├── upgrade.html                     # ⬜
└── architectural-review.html        # ⬜

docs/sts/
├── code-quality.html                # ⬜
├── solid.html                       # ⬜
├── testing.html                     # ⬜
├── performance.html                 # ⬜
├── security.html                    # ⬜
└── documentation.html               # ⬜

docs/features/
├── holistic-discovery.html          # ⬜
├── token-optimization.html          # ⬜
└── dashboard-system.html            # ⬜
```

### Level 3 (Inline/Modal - No separate files)
```
# Use expandable sections, modals, or drawers instead of separate pages
# Example: Rule details in skull-protection.html are inline expandable
```

---

## 🔧 Layout Standards (MANDATORY)

### Pattern 6: Metrics Dashboard (Centered Flexbox)
```css
.metrics-dashboard {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-lg);
    width: 100%;
    margin: 0 auto var(--spacing-3xl);
    padding: 0 var(--spacing-lg);
}

.metric-card {
    text-align: center;
    padding: var(--spacing-xl) var(--spacing-2xl);
    min-width: 140px;
    flex: 0 1 auto;
}
```

### Pattern 7: Balanced Navigation Footer
```html
<nav class="nav-footer" style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto var(--spacing-2xl); padding: var(--spacing-xl);">
    <a href="prev.html" class="nav-link prev" style="min-width: 220px; text-align: center;">
        ← Previous Page
    </a>
    <a href="next.html" class="nav-link next" style="min-width: 220px; text-align: center;">
        Next Page →
    </a>
</nav>
```

---

## ⚠️ Constraints

1. **No Level 4+ views** - Consolidate into Level 3 with expandable content
2. **Colors unchanged** - Level 1 approved colors must be preserved
3. **Pattern compliance** - All views must use Pattern 6 (metrics) and Pattern 7 (nav)
4. **Animation Tier T1** - All Level 2 pages use Subtle animations ONLY
5. **CSS imports required** - `variables.css`, `main.css`, `glass-patterns.css`, `micro-interactions.css`

---

## ✅ Definition of Done

- [ ] All Level 1 pages verified against exemplar checklist
- [ ] All Level 2 pages use Pattern 6 (metrics) and Pattern 7 (nav)
- [ ] All Level 2 pages use T1 (Subtle) animations only
- [ ] No view deeper than Level 3
- [ ] Visual differentiation clear between levels
- [ ] Colors preserved from approved designs
- [ ] Mobile responsive (320px minimum)
- [ ] Lighthouse performance ≥90
- [ ] `skull-protection.html` animations simplified to T1
- [ ] `knowledge-graph.html` animations simplified to T1

---

## 📚 Reference Documents

- `cortex-brain/documents/standards/glassmorphism-design-standard.md` (v3.1.0)
- Exemplar: `http://localhost:8000/orchestrators/index.html`
- CSS Stack: `variables.css`, `glass-patterns.css`, `micro-interactions.css`

---

## 🤖 copilot_instructions

```yaml
response_template: autonomous_execution_progress
tdd_enforcement: true
final_refactor_required: true
max_nesting_depth: 3
level_1_colors: preserve_existing
level_1_exemplar: orchestrators/index.html
animation_tier_default: T1 (Subtle)
animation_tier_hero_only: T3 (Dramatic)
mandatory_patterns:
  - Pattern 6 (Centered Flexbox Metrics)
  - Pattern 7 (Balanced Navigation)
skull_rules:
  - REFACTOR_CLEANUP
  - HOLISTIC_DISCOVERY
completion_marker: "# 🎉 CONGRATULATIONS"
```

---

## 🚀 Server Launch

```bash
./scripts/launch_docs.sh
# Opens http://localhost:8000
```

---

**Plan Status:** 🟡 ACTIVE  
**Next Action:** Simplify animations in `skull-protection.html` and `knowledge-graph.html` (Phase 9 tasks)

---

*Generated by CORTEX Planning System v4.0*  
*Updated: December 31, 2025 - Added Animation Tier System v2.1.0*  
*Reference: `response-templates-v4.yaml:863`*
