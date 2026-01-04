# 🔄 HTML View Standardization - Snowball Strategy

**Date:** 2026-01-04  
**Status:** 🚀 ACTIVE (Phase 16a)  
**Approach:** Iterative Live Refinement

---

## 🎯 Strategy Overview

**Problem:** Preview-based approach (Phase 14) failed - isolated files don't reflect production CSS environment.

**Solution:** Work directly on production files with live browser feedback loop.

---

## 🏗️ Snowball Phases

### Phase 16a: L1 Architecture Pages (4 pages) ✅ COMPLETE
**Duration:** 8 hours | **Status:** ✅ APPROVED - Standards Recorded

**Approved Standards:**
- ✅ **Level 1 Header**: 200x200px CORTEX logo linking to home
- ✅ **Level 2 Header**: 100x100px logo + Level 1 breadcrumb (1.5rem, 600 weight, cyan)
- ✅ **Mermaid Diagrams**: Glassmorphism theme (base, rgba colors, Inter 15px)
- ✅ **No Inline CSS**: All styles from intentional-classes.css
- ✅ **Accordion Pattern**: Progressive disclosure with glass cards
- ✅ **Cache Busting**: Versioned mermaid imports

**Pages:**
1. ✅ `architecture/index.html` - **COMPLETE** (accordion + mermaid + 200px header logo)
2. ⏳ `architecture/four-tier-brain.html`
3. ⏳ `architecture/agent-system.html`
4. ⏳ `architecture/orchestrator-ecosystem.html`

**Design Standard Established:** `MERMAID-DIAGRAM-STANDARD.md` + `LEVEL-1-AUTOMATION-STRATEGY.md`

**Live URL:** http://localhost:8000/architecture/index.html

---

### Phase 16b: L1 Token Optimization Hub 🚀 ACTIVE
**Duration:** 2 hours | **Current Page:** `token-optimization/index.html`

**Pages:**
1. 🚀 `token-optimization/index.html` - **ACTIVE NOW** (fix broken piece)

**Live URL:** http://localhost:8000/token-optimization/index.html

---

### Phase 16c: L1 Feature Pages (4 pages) ⏳ PENDING
**Duration:** 6 hours

**Pages:**
1. `features/index.html`
2. `features/planning-system.html`
3. `features/tdd-mastery.html`
4. `features/ado-operations.html`

**Design Standard:** `MERMAID-DIAGRAM-STANDARD.md` (approved 2026-01-04)

**Requirements:**
- ✅ Mermaid diagrams use glassmorphism theme (base + rgba colors)
- ✅ No inline CSS styles (use intentional-classes.css only)
- ✅ `.mermaid-container` wrapper with backdrop-filter blur
- ✅ Modern Inter/Segoe UI font stack (15px)
- ✅ Accordion progressive disclosure pattern
- ✅ Hard browser refresh required after changes

---

### Phase 16c: L1 Orchestrator Hub (2 pages) ⏳ PENDING
**Duration:** 4 hours

**Pages:**
1. `orchestrators/index.html`
2. `orchestrators/planning-v5.html`

---

### Phase 16d: L2 Detail Pages (24 pages) ⏳ PENDING
**Duration:** 12 hours (0.5h/page with patterns)

---

### Phase 17: Production QA ⏳ PENDING
**Duration:** 3 hours

---

## 🔄 Iterative Workflow (PER PAGE)

```
1. Open file in VSCode: architecture/index.html
2. Open in browser: http://localhost:8000/architecture/index.html
3. User reviews current state
4. User identifies issues (one section at a time)
5. CORTEX applies fixes
6. User refreshes browser to validate
7. Iterate until section perfect
8. Move to next section
9. When page complete → git commit
10. Move to next page
```

---

## 🎨 Focus Areas (architecture/index.html)

### 1. Brain Tiers Section (#brain-tiers)
**Current Issues to Review:**
- Tetris tile layout
- Icon + title spacing (should use `gap: var(--spacing-sm)`)
- Hover effects on clickable tiles
- Color theme consistency (level1-architecture)

**Expected Structure:**
```html
<a href="#tier0" class="token-metric-tile tile-governance">
  <i class="fas fa-shield-alt pulse-glow-glass--fast"></i>
  <div>
    <span class="metric-value">Tier 0</span>
    <span class="metric-label">Governance</span>
  </div>
</a>
```

---

### 2. SKULL Rules Section (#skull-rules)
**Expected:** 6 tetris tiles
- TDD Enforcement
- Holistic Discovery
- Refactor Cleanup
- Git Isolation
- Planning Isolation
- Hand-Off Protocol

---

### 3. Agents Section (#agents)
**Expected:** 2 agent cards
- Planning Agent (glass-card-display or glass-card-clickable?)
- Strategic Reasoning Agent

---

### 4. Orchestrators Section (#orchestrators)
**Expected:** 22 orchestrator tiles
- 3-4 column grid layout
- Consistent icon sizing
- glass-card-clickable with hover

---

### 5. Memory Access Section (#memory-access)
**Expected:** Performance metrics
- Sub-100ms working memory access
- Progress bars for tier speeds
- Benchmark comparisons

---

## ✅ Quality Checklist (PER SECTION)

Before moving to next section, validate:

- [ ] All CSS classes from `intentional-classes.css`
- [ ] No inline styles
- [ ] Icon + title inline (not separate lines)
- [ ] `gap: var(--spacing-sm)` for icon containers
- [ ] Hover effects work correctly
- [ ] Color theme applied (`level1-architecture`)
- [ ] Responsive on mobile (320px breakpoint)
- [ ] Accessible (WCAG AA - color contrast 4.5:1)
- [ ] User confirms "this looks perfect"

---

## 📊 Progress Tracking

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      SNOWBALL STRATEGY PROGRESS                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Phase 16a: L1 Architecture (4 pages)    [░░░░░░░░░░]   0%  🚀 ACTIVE     ║
║   └─ architecture/index.html             [░░░░░░░░░░]   0%  🚀 NOW       ║
║ Phase 16b: L1 Features (4 pages)        [░░░░░░░░░░]   0%  ⏳ PENDING    ║
║ Phase 16c: L1 Orchestrators (2 pages)   [░░░░░░░░░░]   0%  ⏳ PENDING    ║
║ Phase 16d: L2 Detail Pages (24 pages)   [░░░░░░░░░░]   0%  ⏳ PENDING    ║
║ Phase 17: Production QA                 [░░░░░░░░░░]   0%  ⏳ PENDING    ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Total Pages: 34 | Completed: 0 | Remaining: 34                            ║
║ Estimated Time: 33 hours | Elapsed: 0h | Remaining: 33h                   ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Current Task

**PAGE:** `architecture/index.html`  
**SECTION:** #brain-tiers (Tier 0-3 cards)  
**USER ACTION:** Open http://localhost:8000/architecture/index.html in browser  
**NEXT STEP:** User reviews current state and describes what needs refinement

---

## 📝 Git Commit Strategy

**Format:** `Phase 16a: Refine [page-name] - [section changes]`

**Examples:**
- `Phase 16a: Refine architecture/index.html - Brain tiers tetris layout`
- `Phase 16a: Refine architecture/index.html - SKULL rules section complete`
- `Phase 16a: Complete architecture/index.html - All sections validated`

---

## 🚀 Expected Velocity

**Initial (first 4 pages):** 2 hours/page (learning patterns)  
**Accelerated (L2 pages):** 0.5 hours/page (pattern application)  
**Efficiency Gain:** 30% reduction after pattern recognition kicks in

---

## 💡 Key Insights

1. **Live feedback is essential** - Preview files are disconnected
2. **One section at a time** - Prevents overwhelming changes
3. **User validation required** - "Looks perfect" before proceeding
4. **Patterns emerge quickly** - First 4 pages teach the rest
5. **Git commits per page** - Atomic, rollback-safe changes

---

**Ready to Start:** YES  
**User Opens:** http://localhost:8000/architecture/index.html  
**CORTEX Awaits:** User feedback on current #brain-tiers section
