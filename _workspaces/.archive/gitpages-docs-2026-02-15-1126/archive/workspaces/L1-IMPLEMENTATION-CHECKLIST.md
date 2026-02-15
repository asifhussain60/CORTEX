# L1 Implementation Checklist

**Plan:** L1-ARCH-V2  
**Status:** ✅ APPROVED  
**Start Date:** 2026-01-31  
**Target Completion:** 2026-02-07 (7 days)

---

## Phase 1: Immediate Fixes (30 minutes) ⏱️

### Task 1.1: Fix Orchestrator Count
- [ ] Open `docs/index.html`
- [ ] Find line ~536: `<span class="bwc-mini-value">8</span>`
- [ ] Replace with: `<span class="bwc-mini-value">15</span>`
- [ ] Update label: `<span class="bwc-mini-label">Orchestrators Wired</span>`
- [ ] Test: Verify stats panel displays "15 Orchestrators Wired"

### Task 1.2: Add Vision API to LENS Description
- [ ] Open `docs/index.html`
- [ ] Find line ~357 (LENS description in Discovery & TOOLKIT panel)
- [ ] Update text to: "Universal code intelligence with AST analysis across 6+ languages, **Vision API for image analysis** (screenshots, diagrams, UI elements), crawlers for architecture/complexity/dependencies..."
- [ ] Test: Verify description mentions Vision API

### Task 1.3: Add Vision API Tag
- [ ] Find line ~364 (category-tags section under LENS)
- [ ] Add after "LENS Overview" tag:
  ```html
  <a class="category-tag animation-t2" data-icon="👁️" href="lens/vision-api.html">
      <span>Vision API</span>
  </a>
  ```
- [ ] Test: Verify Vision API tag appears with eye emoji

### Task 1.4: Update Key Features Tiles
- [ ] Find CORTEX LENS tile (~line 724)
- [ ] Update caption: "AST Analysis, Vision API & Reverse Engineering"
- [ ] Find Governance & Audit tile (~line 729)
- [ ] Update caption: "4‑Tier Merger • Hash‑Chain Audit • 15 MCP Tools"
- [ ] Find Security Layer tile (~line 759)
- [ ] Update caption: "Action Classification • 6 CWE Patterns • Approval Gates"
- [ ] Test: Verify all tile captions updated

### Phase 1 Validation
- [ ] All 4 critical fixes applied
- [ ] No broken HTML/CSS
- [ ] Visual design unchanged (glassmorphism intact)
- [ ] Git commit: "Phase 1: Critical fixes (orchestrator count, Vision API)"

**Estimated Time:** 30 minutes  
**Completion:** ☐

---

## Phase 2: Section Reorder + Awakening Redesign (3 hours) ⏱️

### Task 2.1: Move Awakening Story Section
- [ ] Locate current Awakening section (line ~488-489)
- [ ] Cut HTML block (Full `<div class="level0-container">` with button)
- [ ] Find "Built with CORTEX" section end (line ~610)
- [ ] Paste Awakening section AFTER Built with CORTEX
- [ ] Test: Verify section appears after social proof panel

### Task 2.2: Redesign Awakening Story Panel
- [ ] Replace simple button with immersive hero panel
- [ ] Create HTML structure (see `L1-DOCUMENTATION-ARCHITECTURE-PLAN.yaml` section 4)
- [ ] Components needed:
  - [ ] Background gradient container
  - [ ] 400x400 Awakening image (check if `assets/images/Awakening-400.png` exists, else upscale 200px)
  - [ ] Story hook headline: "The Awakening Of CORTEX"
  - [ ] Emotional hook paragraph (2-3 sentences)
  - [ ] Prominent CTA button
- [ ] Test: Verify visual prominence (should grab attention)

### Task 2.3: Add CSS for Awakening Hero
- [ ] Open `docs/assets/css/main.css`
- [ ] Add awakening-hero-section classes:
  ```css
  .awakening-hero-section { margin: 4rem 0; }
  .awakening-hero-panel { 
      padding: 4rem; 
      background: linear-gradient(135deg, rgba(123, 97, 255, 0.15), rgba(0, 212, 255, 0.15)); 
      position: relative;
      overflow: hidden;
  }
  .awakening-content-wrapper { 
      display: grid; 
      grid-template-columns: 400px 1fr; 
      gap: 3rem; 
      align-items: center; 
  }
  .awakening-image-large { 
      width: 400px; 
      height: 400px; 
      filter: drop-shadow(0 0 40px rgba(123, 97, 255, 0.6)); 
      transition: filter 0.3s ease;
  }
  .awakening-image-large:hover {
      filter: drop-shadow(0 0 60px rgba(123, 97, 255, 0.9));
  }
  .awakening-title { 
      font-size: 2.5rem; 
      margin-bottom: 1.5rem; 
      color: #ffffff;
  }
  .awakening-label {
      display: inline-block;
      padding: 0.5rem 1rem;
      background: rgba(123, 97, 255, 0.2);
      border: 1px solid rgba(123, 97, 255, 0.4);
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: #7b61ff;
  }
  .awakening-description { 
      font-size: 1.125rem; 
      line-height: 1.8; 
      margin-bottom: 1rem; 
      color: var(--text-secondary);
  }
  .awakening-hook {
      font-size: 1rem;
      line-height: 1.7;
      margin-bottom: 2rem;
      color: var(--text-muted);
  }
  .btn-awakening-primary { 
      display: inline-flex;
      align-items: center;
      gap: 1rem;
      padding: 1.5rem 2.5rem; 
      background: linear-gradient(135deg, #7b61ff, #00d4ff); 
      border: none;
      border-radius: 12px;
      color: #ffffff;
      font-size: 1.125rem;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.3s ease;
      box-shadow: 0 4px 20px rgba(123, 97, 255, 0.3);
  }
  .btn-awakening-primary:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 32px rgba(123, 97, 255, 0.5);
  }
  .btn-awakening-primary .btn-caption {
      display: block;
      font-size: 0.875rem;
      opacity: 0.9;
      font-weight: 400;
  }
  ```
- [ ] Test: Verify glassmorphism compliance, no layout breaks

### Task 2.4: Move Demo Videos Section
- [ ] Locate Demo Videos section (line ~1016-1234)
- [ ] Cut entire `<div class="demo-showcase-container">` block
- [ ] Find Key Features Grid end (line ~771)
- [ ] Paste Demo Videos section AFTER Key Features Grid
- [ ] Test: Verify videos appear after features, navigation still works

### Task 2.5: Update Internal Navigation
- [ ] Check for any anchor links pointing to moved sections
- [ ] Update anchor IDs if necessary (keep existing IDs if possible)
- [ ] Test: Click all navigation links, verify no broken anchors

### Phase 2 Validation
- [ ] Awakening Story visually prominent
- [ ] Demo Videos appear after features
- [ ] All internal navigation works
- [ ] Design consistency maintained
- [ ] Mobile responsive (test 375px, 768px, 1024px)
- [ ] Git commit: "Phase 2: Section reorder + Awakening redesign"

**Estimated Time:** 3 hours  
**Completion:** ☐

---

## Phase 3: Role Gateway + L3 Pages (5 hours) ⏱️

### Task 3.1: Redesign Persona Tiles as Interactive Gateway
- [ ] Locate current persona tiles (line ~448-487)
- [ ] Replace static tiles with interactive gateway cards
- [ ] Add hover effects and click handlers
- [ ] Add "Choose Your Journey" section header
- [ ] Link each card to L3 role-specific landing page
- [ ] Test: Hover effects work, cards are clickable

### Task 3.2: Add Role Gateway CSS
- [ ] Open `docs/assets/css/main.css`
- [ ] Add role-gateway classes:
  ```css
  .role-gateway-section { margin: 4rem 0; }
  .role-gateway-header { text-align: center; margin-bottom: 3rem; }
  .role-gateway-grid { 
      display: grid; 
      grid-template-columns: repeat(3, 1fr); 
      gap: 2rem; 
  }
  .role-gateway-card { 
      display: block;
      padding: 2.5rem;
      text-decoration: none;
      color: inherit;
      cursor: pointer; 
      transition: all 0.3s ease; 
      border: 2px solid rgba(255, 255, 255, 0.1);
  }
  .role-gateway-card:hover { 
      transform: translateY(-8px); 
      box-shadow: 0 12px 40px rgba(0, 212, 255, 0.3); 
      border-color: rgba(0, 212, 255, 0.5);
  }
  .role-gateway-card--leadership:hover {
      border-color: rgba(255, 193, 7, 0.6);
  }
  .role-gateway-card--product:hover {
      border-color: rgba(76, 175, 80, 0.6);
  }
  .role-gateway-card--engineers:hover {
      border-color: rgba(0, 212, 255, 0.6);
  }
  .role-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
  }
  .role-title {
      font-size: 1.75rem;
      margin-bottom: 0.5rem;
  }
  .role-tagline {
      font-size: 1.125rem;
      color: var(--accent-primary);
      margin-bottom: 1.5rem;
  }
  .role-benefits {
      list-style: none;
      padding: 0;
      margin-bottom: 2rem;
  }
  .role-benefits li {
      padding: 0.5rem 0;
      font-size: 0.9375rem;
  }
  .role-benefits li::before {
      content: "✓";
      color: var(--success);
      margin-right: 0.75rem;
      font-weight: bold;
  }
  .role-cta { 
      display: flex; 
      justify-content: space-between; 
      align-items: center; 
      font-weight: 600; 
      color: var(--accent-primary);
  }
  ```
- [ ] Test: Cards render correctly, hover effects smooth

### Task 3.3: Create L3 Leadership Landing Page
- [ ] Create directory: `docs/for-leadership/`
- [ ] Copy template from: `docs/orchestrators/index.html`
- [ ] Customize for leadership:
  - [ ] 300px logo (left-justified)
  - [ ] NO hero section
  - [ ] Header: "CORTEX for Business Leadership"
  - [ ] Curated feature tiles (8 tiles):
    - Governance & Audit
    - Orchestrators (MasterOrchestrator focus)
    - Token Optimization
    - Architecture
    - Planning System
    - ADO Integration
    - Security
    - Metrics Dashboard
  - [ ] D3.js visualization: ROI impact chart
- [ ] Test: Page renders, navigation works, tiles clickable

### Task 3.4: Create L3 Product Owner Landing Page
- [ ] Create directory: `docs/for-product/`
- [ ] Copy template from: `docs/orchestrators/index.html`
- [ ] Customize for product owners:
  - [ ] 300px logo (left-justified)
  - [ ] NO hero section
  - [ ] Header: "CORTEX for Product Owners"
  - [ ] Curated feature tiles (8 tiles):
    - Planning System
    - ADO Operations
    - ADO Planning
    - Execution Orchestrator
    - TDD Orchestrator
    - Evidence Bundles
    - Audit Infrastructure
    - Dashboard
  - [ ] D3.js visualization: Sprint workflow diagram
- [ ] Test: Page renders, navigation works, tiles clickable

### Task 3.5: Create L3 Engineer Landing Page
- [ ] Create directory: `docs/for-engineers/`
- [ ] Copy template from: `docs/orchestrators/index.html`
- [ ] Customize for engineers:
  - [ ] 300px logo (left-justified)
  - [ ] NO hero section
  - [ ] Header: "CORTEX for Software Engineers"
  - [ ] Curated feature tiles (9 tiles):
    - TDD Orchestrator
    - CORTEX LENS
    - Vision API
    - Refactoring Orchestrator
    - Git Checkpoint
    - Token Optimization
    - CORTEX TOOLKIT
    - Debug Orchestrator
    - Learning Paths
  - [ ] D3.js visualization: TDD workflow cycle
- [ ] Test: Page renders, navigation works, tiles clickable

### Task 3.6: Update Role Gateway Navigation
- [ ] Verify all 3 role cards link correctly:
  - Leadership → `for-leadership/index.html`
  - Product → `for-product/index.html`
  - Engineers → `for-engineers/index.html`
- [ ] Add "View All Features" fallback link
- [ ] Test: Click each role card, lands on correct L3 page

### Phase 3 Validation
- [ ] Role gateway interactive and visually appealing
- [ ] All 3 L3 pages created and functional
- [ ] Navigation flow: Landing → Role → L3 → Features
- [ ] Curated tiles relevant to each role
- [ ] D3.js visualizations load correctly
- [ ] Mobile responsive
- [ ] Git commit: "Phase 3: Role gateway + L3 landing pages"

**Estimated Time:** 5 hours  
**Completion:** ☐

---

## Phase 4: Token Optimization Page (6 hours) ⏱️

### Task 4.1: Extract Archived Prototype
- [ ] Locate: `docs/archives/prototypes-20260103-101816/prototypes/token-optimization/index.html`
- [ ] Copy to: `docs/token-optimization/index.html`
- [ ] Review content for accuracy
- [ ] Test: Page loads without errors

### Task 4.2: Modernize to Glassmorphism v4.0.1
- [ ] Apply approved L1 pattern:
  - [ ] 300px CORTEX logo (left-justified)
  - [ ] NO hero section
  - [ ] Clean header with title: "Token Optimization"
- [ ] Update CSS references to `glass-level1.css`
- [ ] Ensure backdrop-filter and glass-bg classes used
- [ ] Test: Design matches `docs/orchestrators/index.html`

### Task 4.3: Cross-Reference with Documentation
- [ ] Open: `docs/01-cortex-brain/05-token-optimization.md`
- [ ] Verify metrics match:
  - [ ] 96% compression ratio
  - [ ] $8.6K annual savings
  - [ ] 6,950 tokens saved per request
  - [ ] 7,240 → 290 tokens
- [ ] Update any outdated stats
- [ ] Test: All metrics accurate

### Task 4.4: Create D3.js Pipeline Visualization
- [ ] Convert Mermaid diagram to D3.js:
  - Source: `docs/01-cortex-brain/diagrams/03-token-optimization-flow.mmd`
  - Output: Interactive D3.js flow diagram
- [ ] Visualize 4 stages:
  1. Rule Compression (1,450 → 200 tokens)
  2. AC-ID Condensing (200 → 25 tokens)
  3. Template Reference (150 → 5 tokens)
  4. Knowledge Abstraction (80 → 10 tokens)
- [ ] Add interactive hover effects (show details per stage)
- [ ] Test: Visualization renders, animations smooth

### Task 4.5: Add Metrics Section
- [ ] Create "Efficiency Metrics" panel
- [ ] Display key stats:
  - Total compression: 96%
  - Annual savings: $8.6K
  - Tokens saved: 6,950 per request
  - Input: 7,240 tokens
  - Output: 290 tokens
- [ ] Add comparison chart (before/after)
- [ ] Test: Stats visually prominent

### Task 4.6: Add Deep-Dive Link
- [ ] Link to: `docs/01-cortex-brain/05-token-optimization.md`
- [ ] Button text: "Read Technical Deep-Dive"
- [ ] Include caption: "620 lines of comprehensive documentation"
- [ ] Test: Link works, opens in same window

### Task 4.7: Responsive Design Testing
- [ ] Test 375px (mobile): Layout stacks correctly
- [ ] Test 768px (tablet): Grid adjusts appropriately
- [ ] Test 1024px+ (desktop): Full grid visible
- [ ] Test D3.js visualization on all breakpoints
- [ ] Test: No horizontal scroll, all content accessible

### Phase 4 Validation
- [ ] Page exists at `docs/token-optimization/index.html`
- [ ] Glassmorphism v4.0.1 compliant
- [ ] Metrics accurate and current
- [ ] D3.js visualization functional
- [ ] Deep-dive documentation linked
- [ ] Mobile responsive
- [ ] Git commit: "Phase 4: Token optimization page creation"

**Estimated Time:** 6 hours  
**Completion:** ☐

---

## Phase 5: L4 Detail Pages (Iterative - 2-4 hours per page) ⏱️

### Leadership L4 Pages
- [ ] `docs/for-leadership/governance.html` - Risk reduction via governance
- [ ] `docs/for-leadership/velocity-metrics.html` - Delivery acceleration proof
- [ ] `docs/for-leadership/cost-savings.html` - $8.6K ROI breakdown
- [ ] `docs/for-leadership/compliance.html` - Security & audit compliance

### Product Owner L4 Pages
- [ ] `docs/for-product/sprint-planning.html` - Sprint workflow guide
- [ ] `docs/for-product/ado-integration.html` - Azure DevOps sync
- [ ] `docs/for-product/evidence-bundles.html` - Proof tracking
- [ ] `docs/for-product/velocity-tracking.html` - Team metrics

### Engineer L4 Pages
- [ ] `docs/for-engineers/tdd-workflow.html` - RED→GREEN→REFACTOR tutorial
- [ ] `docs/for-engineers/lens-tutorial.html` - Code intelligence guide
- [ ] `docs/for-engineers/vision-api-guide.html` - Screenshot analysis
- [ ] `docs/for-engineers/refactoring-patterns.html` - Automated refactoring

**Note:** Phase 5 is iterative. Create 1-2 L4 pages per role per sprint based on priority.

**Estimated Time:** 2-4 hours per page  
**Completion:** ☐

---

## Final Validation & Testing ✅

### Design Compliance
- [ ] Glassmorphism v4.0.1 compliance (100%)
- [ ] Color palette consistent (#00d4ff, #7b61ff)
- [ ] Animations T1-T5 only (no T6+ on landing)
- [ ] Backdrop-filter blur effects working
- [ ] Glass background rgba values correct

### Accessibility
- [ ] WCAG 2.1 AA compliance (target 95/100)
- [ ] Keyboard navigation functional
- [ ] ARIA labels on interactive elements
- [ ] Focus indicators visible
- [ ] Alt text on all images
- [ ] Color contrast ratios meet standards

### Performance
- [ ] Lighthouse Performance: 90+ score
- [ ] First Contentful Paint < 1.5s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Cumulative Layout Shift < 0.1
- [ ] Demo videos lazy-loaded
- [ ] Images optimized (WebP format)

### Functionality
- [ ] All internal navigation works
- [ ] Role gateway cards clickable
- [ ] L3 pages load correctly
- [ ] Multi-panel tabs functional
- [ ] Demo videos play
- [ ] D3.js visualizations render
- [ ] Mobile menu works

### Browser Compatibility
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Responsive Design
- [ ] 375px (iPhone SE)
- [ ] 768px (iPad)
- [ ] 1024px (iPad Pro)
- [ ] 1440px (Desktop)
- [ ] 1920px (Full HD)

---

## Git Commits Summary

```bash
# Phase 1 Commit
git add docs/index.html docs/assets/css/main.css
git commit -m "Phase 1: Critical fixes (orchestrator count 8→15, Vision API mentions, tile updates)"

# Phase 2 Commit
git add docs/index.html docs/assets/css/main.css docs/assets/images/Awakening-400.png
git commit -m "Phase 2: Section reorder + Awakening Story redesign (immersive panel)"

# Phase 3 Commit
git add docs/index.html docs/assets/css/main.css docs/for-leadership/ docs/for-product/ docs/for-engineers/
git commit -m "Phase 3: Role-based navigation gateway + L3 landing pages (3 personas)"

# Phase 4 Commit
git add docs/token-optimization/ docs/assets/css/main.css
git commit -m "Phase 4: Token optimization page creation (D3.js visualization, metrics)"

# Phase 5 Commits (Iterative)
git add docs/for-{role}/{page}.html
git commit -m "Phase 5: L4 detail page - {role} {feature}"
```

---

## Success Criteria ✅

### Must-Have (Phases 1-4)
- [x] Awakening Story visually prominent after social proof
- [x] Role gateway interactive with navigation to L3 pages
- [x] Demo videos moved after architecture context
- [x] Token optimization page created and linked
- [x] All critical fixes applied (orchestrator count, Vision API)

### Nice-to-Have (Phase 5)
- [ ] L3 role-specific landing pages fully functional
- [ ] L4 detail pages started (2-3 per role)
- [ ] A/B testing framework for role gateway
- [ ] Analytics tracking for new user journeys

---

## Analytics Tracking (Optional)

### Events to Track
- `awakening_story_click` - CTA click on Awakening panel
- `role_gateway_click` - Role card selection (leadership/product/engineers)
- `demo_video_play` - Video start
- `demo_video_complete` - Video completion
- `feature_tile_click` - Feature discovery
- `l3_navigation` - Role-specific page visits
- `l4_navigation` - Detail page visits

### Metrics Dashboard
- Awakening Story CTR
- Role selection distribution
- Demo completion rate
- Feature discovery rate
- Bounce rate
- Time on page
- Scroll depth

---

**Total Estimated Time (Phases 1-4):** 14-17 hours  
**Phase 5:** Iterative (2-4 hours per L4 page)  
**Target Completion:** 2026-02-07 (7 days)  
**Status:** ✅ APPROVED - Ready to Execute
