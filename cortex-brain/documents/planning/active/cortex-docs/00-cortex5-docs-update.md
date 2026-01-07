# CORTEX5 Holistic Documentation Update Plan

**Plan ID:** `cortex-docs`  
**Version:** 1.0.0  
**Status:** 🟡 READY FOR APPROVAL  
**Created:** 2026-01-06  
**Timeline:** 4 weeks (8 phases, 2 parallel tracks)  
**Complexity:** Tier 4 (Multi-System Integration)  
**Dependencies:** cortex5-enhancement-epic Phase 0 completion

---

## ⚠️ CRITICAL: Phase 0 Dependency

**This plan REQUIRES cortex5-enhancement-epic Phase 0 to be COMPLETE before execution.**

**Why:** Documentation updates must reflect CORTEX-5.5 clean architecture (not CORTEX-5.0 technical debt). Phase 0 establishes:
- Clean file structure (~150 essential files)
- Master Orchestrator v7 routing patterns
- Knowledge Extension Layer architecture
- Pull-on-demand strategy (0/20 budget)

**Verification Before Starting:**
```powershell
# Verify CORTEX-5.5 branch exists
git branch -a | Select-String "CORTEX-5.5"

# Verify Phase 0 completion marker
Test-Path "cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/phase-0-complete.json"
```

---

## 📋 Executive Summary

**Vision:** Regenerate all CORTEX documentation to reflect CORTEX5 architecture enhancements while maintaining glassmorphism theme, accessibility standards (WCAG AA), and admin dashboard design parity.

### Strategic Objectives

1. **Architecture Alignment:** Update all content to reflect 12-phase execution model, Knowledge Extension Layer, Orchestrator Registry, Rule Layering, and Intermittent Thoughts Capture
2. **Theme Standardization:** Enforce glassmorphism CSS across all pages (home, Level 1, Level 2 views)
3. **Parser Automation:** Rebuild content generators to auto-update from YAML manifests
4. **Accessibility Compliance:** Maintain WCAG AA standards with responsive design
5. **Admin Parity:** Match admin dashboard visual patterns and UX

### Scope

**Documentation Hierarchy:**
- **Level 0 (Home):** `/docs/index.html` - Landing page with system overview
- **Level 1 (Categories):** `/docs/orchestrators/index.html` - Orchestrator map, brain tiers, planning system
- **Level 2 (Details):** Individual orchestrator pages, API docs, guides

**Content Types:**
- Technical Documentation (architecture, orchestrators, brain system)
- User Guides (quick start, command reference, troubleshooting)
- API Documentation (orchestrator interfaces, knowledge APIs, brain queries)
- Deployment Guides (setup, configuration, maintenance)
- Testing Documentation (coverage reports, validation checklists)

### Key Deliverables

1. **Updated Home Page:** Reflect CORTEX5 vision, 12-phase model, Phase 0 importance
2. **Orchestrator Index (L1):** Interactive D3.js map with all 10+ orchestrators
3. **Individual Pages (L2):** Per-orchestrator details with YAML-sourced content
4. **CSS Theme Files:** Standardized glassmorphism.css, shared-styles.css
5. **Parser Scripts:** YAML-to-HTML generators (Python + JavaScript)
6. **Validation Suite:** Automated tests for content accuracy, theme consistency
7. **Migration Guide:** Step-by-step content update procedures
8. **Deployment Checklist:** Pre-launch validation steps

---

## 🎯 Success Criteria

### Documentation Accuracy (Phase 1-2)

- [ ] All references to "11 phases" updated to "12 phases (Phase 0 + Phases 1-11)"
- [ ] Phase 0 documented as mandatory first step with 15-minute execution time
- [ ] Knowledge Extension Layer architecture explained with examples
- [ ] Orchestrator Registry System documented with custom orchestrator guide
- [ ] Rule Layering Architecture documented (Core/Company/Domain priority)
- [ ] Intermittent Thoughts Capture System explained with user-facing instructions
- [ ] Pull-on-demand strategy documented (0/20 budget tracking)
- [ ] Master Orchestrator v7 routing patterns documented
- [ ] Request transformation pipeline explained with examples

### Visual Consistency (Phase 3-4)

- [ ] Glassmorphism theme applied to all pages (home, L1, L2)
- [ ] `backdrop-filter: blur(10px)` on all glass cards
- [ ] `rgba(26, 31, 58, 0.7)` background color standardized
- [ ] Box shadows consistent: `0 20px 60px rgba(0,0,0,0.3)`
- [ ] Border radius standardized: `20px` (large cards), `12px` (small cards)
- [ ] Color palette consistent with admin dashboard
- [ ] Typography: Inter font family, consistent sizing (1.3rem tagline, 3rem h1)
- [ ] Accessibility: Touch targets ≥44px, contrast ratio ≥4.5:1

### Parser Automation (Phase 5-6)

- [ ] Python YAML parser extracts orchestrator metadata from manifests
- [ ] JavaScript D3.js generates orchestrator map from JSON
- [ ] HTML generator creates L2 pages from YAML templates
- [ ] CSS preprocessor generates glassmorphism theme from variables
- [ ] Automated validation checks YAML schema compliance
- [ ] Parser runs on pre-commit hook (optional, configurable)
- [ ] Manual trigger: `python regenerate_docs.py --target all`

### Testing & Validation (Phase 7)

- [ ] Content accuracy tests (12 phases mentioned, Phase 0 explained)
- [ ] Visual regression tests (Playwright screenshots)
- [ ] Accessibility tests (WCAG AA compliance, axe-core)
- [ ] Mobile responsiveness tests (320px to 1920px viewports)
- [ ] Link integrity tests (no 404s, all internal links valid)
- [ ] Performance tests (Lighthouse score ≥90 all categories)
- [ ] Cross-browser tests (Chrome, Firefox, Safari, Edge)

### Deployment (Phase 8)

- [ ] Staging environment deployed (http://localhost:8000/)
- [ ] Production deployment checklist complete
- [ ] Rollback plan documented
- [ ] Post-deployment smoke tests pass
- [ ] GitHub Pages deployment successful
- [ ] CDN cache invalidated (if applicable)

---

## 🏗️ Epic Architecture Integration

### CORTEX5 Enhancement Epic Context

**Source Epic:** `cortex5-enhancement-epic-v2` (Phase 0 + Phases 1-11)

**Key Architecture Changes to Document:**

#### 1. Knowledge Extension Layer (Phase 1)
- **Location:** `cortex-brain/tier2/company-knowledge/{company-id}/`
- **Format:** Markdown + YAML (no databases)
- **Query Priority:** CORTEX Core → Company Override → Merge
- **API:** `CompanyKnowledgeProvider` interface
- **Example:** Custom coding standards override CORTEX defaults

**Doc Impact:**
- Add "Knowledge Extension" section to architecture docs
- Create API reference for `CompanyKnowledgeProvider`
- Add tutorial: "How to Add Company-Specific Knowledge"
- Update orchestrator pages with knowledge extension examples

#### 2. Orchestrator Registry System (Phase 2)
- **Registry:** `cortex-brain/tier0/orchestrator-registry.yaml`
- **Custom Location:** `src/orchestrators/custom/{company-id}/`
- **Registration:** Manifest-based with inheritance
- **Routing:** Master Orchestrator queries registry (no hardcoded patterns)

**Doc Impact:**
- Document orchestrator registration process
- Create guide: "Building Custom Orchestrators"
- Update Master Orchestrator routing documentation
- Add orchestrator registry schema reference

#### 3. Rule Layering Architecture (Phase 3)
- **Tier 1:** Core Rules (TDD, Git Isolation) - highest priority, immutable
- **Tier 2:** Company Rules (coding standards, tech stack) - extends core
- **Tier 3:** Domain Rules (PCI-DSS, HIPAA) - scoped to orchestrators
- **Conflict Resolution:** Priority-based merging

**Doc Impact:**
- Document 3-tier rule system
- Create conflict resolution examples
- Add rule priority visualization (D3.js)
- Update brain protection rules documentation

#### 4. Intermittent Thoughts Capture (Phase 4)
- **User Interface:** `intermittent-thoughts.txt` (workspace root)
- **System Tracking:** `cortex-brain/tier1/intermittent-thoughts.yaml`
- **Check Points:** Phase transitions (≤15% impact auto-incorporated)
- **Visual Feedback:** 🛡️ shield icon in chat + plan viewer

**Doc Impact:**
- Create user guide: "Using Intermittent Thoughts During Execution"
- Document system behavior (check points, impact thresholds)
- Add examples of incorporated vs deferred thoughts
- Update plan viewer with thoughts integration indicator

#### 5. Phase 0: Clean Branch Migration
- **Purpose:** 85% file reduction (1000 → 150 essential files)
- **Execution:** `create-cortex-5.5-branch.ps1` (15 minutes)
- **Validation:** 7 GO criteria, 6 NO-GO criteria
- **Pull Strategy:** `pull-from-cortex-5.0.ps1` (0/20 budget)

**Doc Impact:**
- Add Phase 0 documentation (mandatory first step)
- Document pull-on-demand strategy with budget tracking
- Create migration validation checklist
- Update getting started guide with Phase 0 prerequisite

#### 6. Master Orchestrator v7
- **Routing:** Pattern-based + LLM classification fallback
- **Invocation:** GitHub Copilot transforms → invokes Python via terminal
- **Execution:** 100% autonomous (all orchestrators Python-implemented)
- **Progress:** Live progress bars via `autonomous_execution_progress` template

**Doc Impact:**
- Update Master Orchestrator architecture documentation
- Document request transformation pipeline
- Explain GitHub Copilot routing proxy behavior
- Add terminal invocation examples

---

## 📊 Phase Breakdown

### Track 1: Content & Architecture (Weeks 1-3)

#### Phase 1: Architecture Analysis & Content Inventory (Week 1, Days 1-3)

**Objective:** Analyze current documentation, identify gaps, and create content migration strategy.

**Tasks:**
1. **Content Inventory**
   - Audit all HTML files in `docs/` (home, orchestrators, technical, story)
   - Identify outdated references (11 phases → 12 phases, CORTEX-5.0 → CORTEX-5.5)
   - Map content to source manifests (YAML files)
   - Create content gap analysis report

2. **Architecture Mapping**
   - Extract all architecture changes from cortex5-enhancement-epic
   - Map changes to documentation sections (intro, architecture, guides, API)
   - Identify cross-references requiring updates
   - Create architecture change matrix

3. **Theme Analysis**
   - Audit current glassmorphism implementation (CSS files, inline styles)
   - Identify inconsistencies (color palette, blur values, shadows)
   - Document admin dashboard patterns for parity
   - Create theme standardization specification

**Deliverables:**
- `analysis/content-inventory.md` (all files, line counts, update priority)
- `analysis/architecture-change-matrix.md` (epic changes → doc sections)
- `analysis/theme-audit-report.md` (CSS inconsistencies, admin parity gaps)
- `context/current-doc-structure.json` (machine-readable inventory)

**Success Criteria:**
- All 50+ HTML/MD files inventoried
- 12 architecture changes mapped to doc sections
- Theme inconsistencies identified (≥10 expected)
- Content gap list prioritized (HIGH/MEDIUM/LOW)

---

#### Phase 2: Content Rewriting - Home & Core Docs (Week 1, Days 4-7)

**Objective:** Rewrite home page, architecture overview, and getting started guide.

**Tasks:**
1. **Home Page Update (`docs/index.html`)**
   - Update hero section: "CORTEX5 with 12-Phase Execution Model"
   - Add Phase 0 callout: "Start Clean: 85% File Reduction"
   - Update feature cards: Knowledge Extension, Orchestrator Registry, Rule Layering
   - Add Intermittent Thoughts teaser
   - Preserve glassmorphism theme, ensure mobile responsive

2. **Architecture Overview (`docs/architecture.html`)**
   - Document 4-Tier Brain architecture with Knowledge Extension Layer
   - Explain Master Orchestrator v7 routing (pattern matching + LLM fallback)
   - Visualize request transformation pipeline (strip → match → transform → invoke)
   - Document pull-on-demand strategy with budget tracking
   - Add architecture diagrams (D3.js or static SVG)

3. **Getting Started Guide (`docs/quick-start.html`)**
   - Add Phase 0 prerequisite section (mandatory first step)
   - Update installation steps for CORTEX-5.5 branch
   - Document first command examples with transformation
   - Add intermittent-thoughts.txt usage guide
   - Update troubleshooting section

**Deliverables:**
- `docs/index.html` (updated home page)
- `docs/architecture.html` (new architecture documentation)
- `docs/quick-start.html` (updated getting started)
- `artifacts/home-page-diff.md` (before/after comparison)

**Success Criteria:**
- Phase 0 mentioned prominently (home page hero + getting started)
- 12-phase model replaces all "11 phases" references
- Knowledge Extension Layer explained with code examples
- All links functional (no 404s)
- Mobile responsive (tested 320px to 1920px)

---

#### Phase 3: Orchestrator Documentation - Level 1 (Week 2, Days 1-4)

**Objective:** Update orchestrator index page with interactive D3.js map reflecting all orchestrators.

**Tasks:**
1. **Orchestrator Inventory**
   - Extract all orchestrators from `cortex-brain/config/master-orchestrator.yaml`
   - Parse manifests: `cortex-brain/manifests/orchestrators/*.yaml`
   - Create orchestrator registry JSON (name, version, type, patterns, priority)
   - Identify new orchestrators (Holistic Review, Investigation v2, Sanitization v2)

2. **Interactive Map Update (`docs/orchestrators/index.html`)**
   - Rebuild D3.js visualization with all 10+ orchestrators
   - Color code by type: 🛡️ AUTONOMOUS (blue), 📋 GUIDED (green)
   - Add hover tooltips (version, description, example command)
   - Add filter controls (by type, by track, by complexity)
   - Ensure glassmorphism theme consistency

3. **Orchestrator Overview Cards**
   - Create summary cards for each orchestrator
   - Include: icon, name, version, type, pattern, example usage
   - Link to Level 2 detail pages
   - Add "NEW" badge for CORTEX5 orchestrators

**Deliverables:**
- `docs/orchestrators/index.html` (updated Level 1 page)
- `artifacts/orchestrator-registry.json` (all orchestrators metadata)
- `artifacts/d3-map-config.js` (D3.js visualization config)
- `analysis/orchestrator-inventory.md` (full list with metadata)

**Success Criteria:**
- All 10+ orchestrators visible on map
- D3.js filters functional (type, track, complexity)
- Glassmorphism theme applied (glass cards, blur effects)
- Mobile responsive (collapsible map on small screens)
- No JavaScript errors (console clean)

---

#### Phase 4: Orchestrator Documentation - Level 2 (Week 2, Days 5-7)

**Objective:** Generate individual orchestrator detail pages from YAML manifests.

**Tasks:**
1. **Template Design**
   - Create HTML template for orchestrator detail pages
   - Sections: Overview, Architecture, Usage, Examples, API Reference, Configuration
   - Include glassmorphism styling
   - Add breadcrumb navigation (Home → Orchestrators → [Name])

2. **YAML Parser (Python)**
   - Parse `cortex-brain/manifests/orchestrators/{name}.yaml`
   - Extract: description, patterns, phases, inputs, outputs, examples
   - Generate HTML from Jinja2 template
   - Handle special cases (Planning v5 folder structure, ADO dual-mode)

3. **Page Generation**
   - Generate pages for all orchestrators (10+ files)
   - Planning v5: Document 5-subfolder structure, plan-viewer.html auto-generation
   - ADO v2: Document wizard vs auto mode
   - Vacuum/Cleanup: Document risk classification, dry-run mode
   - Investigation: Document hypothesis generation, Master Orch integration
   - TDD v4: Document RED→GREEN→REFACTOR enforcement

**Deliverables:**
- `docs/orchestrators/{name}.html` (10+ detail pages)
- `artifacts/orchestrator-template.html` (Jinja2 template)
- `artifacts/yaml-parser.py` (Python generator)
- `reports/page-generation-log.md` (generation audit trail)

**Success Criteria:**
- All orchestrators have detail pages
- Content auto-generated from YAML (no hardcoded text)
- Code examples syntax-highlighted
- API reference sections complete (inputs, outputs, config)
- Cross-links functional (L1 → L2, L2 → L2)

---

### Track 2: Theme, Parsers & Validation (Weeks 3-4)

#### Phase 5: CSS Theme Standardization (Week 3, Days 1-3)

**Objective:** Enforce glassmorphism theme across all pages with CSS preprocessing.

**Tasks:**
1. **CSS Audit & Consolidation**
   - Audit all CSS files: `assets/css/*.css`, `docs/**/*.css`
   - Identify inline styles in HTML files
   - Extract glassmorphism patterns (blur, background, shadows, borders)
   - Create CSS variables for theme tokens

2. **Glassmorphism Theme File (`assets/styles/glassmorphism.css`)**
   - Define CSS custom properties (variables):
     - `--glass-bg: rgba(26, 31, 58, 0.7);`
     - `--glass-blur: blur(10px);`
     - `--glass-border: 1px solid rgba(255, 255, 255, 0.1);`
     - `--glass-shadow: 0 20px 60px rgba(0,0,0,0.3);`
     - `--glass-radius-lg: 20px;`
     - `--glass-radius-sm: 12px;`
   - Create utility classes: `.glass-card`, `.glass-card-sm`, `.glass-panel`
   - Ensure WCAG AA contrast compliance

3. **Theme Application**
   - Replace inline styles with utility classes
   - Update all HTML files to use `.glass-card`
   - Remove duplicate CSS rules
   - Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)

**Deliverables:**
- `assets/styles/glassmorphism.css` (standardized theme file)
- `artifacts/css-variables.json` (theme tokens)
- `reports/css-audit-report.md` (before/after comparison)
- `artifacts/inline-styles-removed.md` (cleanup log)

**Success Criteria:**
- Single source of truth for glassmorphism styles
- All pages use `.glass-card` utility class
- No inline styles (except rare exceptions with comments)
- WCAG AA contrast ratio ≥4.5:1 verified
- Cross-browser parity (visual regression tests pass)

---

#### Phase 6: Parser Automation & Content Generation (Week 3, Days 4-7)

**Objective:** Build automated parsers to regenerate documentation from YAML sources.

**Tasks:**
1. **Python YAML Parser (`regenerate_docs.py`)**
   - Parse all YAML manifests in `cortex-brain/manifests/orchestrators/`
   - Extract orchestrator metadata (name, version, patterns, phases, examples)
   - Parse `cortex-brain/config/master-orchestrator.yaml` for routing config
   - Parse `cortex-brain/brain-protection-rules.yaml` for SKULL rules
   - Generate JSON intermediate format

2. **HTML Generator (Python + Jinja2)**
   - Load Jinja2 templates (home, L1, L2)
   - Inject YAML-sourced data
   - Generate static HTML files
   - Preserve manual content sections (tagged with `<!-- MANUAL -->`)
   - Apply glassmorphism CSS classes

3. **D3.js Data Generator (JavaScript)**
   - Convert orchestrator registry JSON to D3.js-compatible format
   - Generate node/edge data for orchestrator map
   - Add metadata for tooltips and filters
   - Export to `artifacts/orchestrator-map-data.json`

4. **CLI Tool**
   ```bash
   python regenerate_docs.py --target all         # Regenerate all docs
   python regenerate_docs.py --target home        # Home page only
   python regenerate_docs.py --target orchestrators  # L1 + L2
   python regenerate_docs.py --validate           # Validate YAML schemas
   ```

**Deliverables:**
- `regenerate_docs.py` (CLI tool)
- `artifacts/yaml-parser.py` (YAML extraction logic)
- `artifacts/html-generator.py` (Jinja2 rendering)
- `artifacts/d3-data-generator.js` (D3.js data prep)
- `artifacts/orchestrator-map-data.json` (D3.js data)

**Success Criteria:**
- Parser successfully extracts data from all YAML manifests
- HTML generation creates valid, linted HTML
- D3.js data format matches visualization requirements
- CLI tool runs without errors
- Regenerated docs match manual content (no data loss)

---

#### Phase 7: Testing & Validation Suite (Week 4, Days 1-4)

**Objective:** Comprehensive testing for content accuracy, visual consistency, and accessibility.

**Tasks:**
1. **Content Accuracy Tests (Python + pytest)**
   - Test: "12 phases" mentioned (not "11 phases")
   - Test: Phase 0 documented as mandatory
   - Test: Knowledge Extension Layer explained
   - Test: Orchestrator Registry documented
   - Test: All orchestrators listed (10+ expected)
   - Test: Code examples syntax-valid

2. **Visual Regression Tests (Playwright)**
   - Capture screenshots: home, L1, all L2 pages
   - Compare against baseline (pixel-diff)
   - Test responsive breakpoints (320px, 768px, 1024px, 1920px)
   - Verify glassmorphism effects (blur, shadows) render correctly

3. **Accessibility Tests (axe-core + Lighthouse)**
   - WCAG AA compliance checks (contrast, labels, semantics)
   - Touch target sizes ≥44px
   - Keyboard navigation functional
   - Screen reader compatibility (ARIA labels)
   - Lighthouse accessibility score ≥90

4. **Link Integrity Tests**
   - Crawl all internal links (L0 → L1 → L2)
   - Check external links (HTTP 200 status)
   - Validate anchor links (#section-id)
   - Report broken links

5. **Performance Tests (Lighthouse)**
   - Performance score ≥90
   - First Contentful Paint (FCP) <2s
   - Largest Contentful Paint (LCP) <2.5s
   - Cumulative Layout Shift (CLS) <0.1
   - Total Blocking Time (TBT) <300ms

**Deliverables:**
- `tests/test_content_accuracy.py` (pytest suite)
- `tests/test_visual_regression.spec.js` (Playwright tests)
- `tests/test_accessibility.spec.js` (axe-core + Lighthouse)
- `tests/test_link_integrity.py` (link crawler)
- `reports/test-results.md` (comprehensive report)

**Success Criteria:**
- All content accuracy tests pass (100%)
- Visual regression diffs ≤1% (minor rendering differences acceptable)
- WCAG AA compliance: 0 violations, 0 serious issues
- Link integrity: 0 broken links
- Lighthouse scores: Performance ≥90, Accessibility ≥95, Best Practices ≥90, SEO ≥90

---

#### Phase 8: Deployment & Rollback Plan (Week 4, Days 5-7)

**Objective:** Deploy updated documentation to staging/production with rollback capability.

**Tasks:**
1. **Staging Deployment (http://localhost:8000/)**
   - Deploy to local HTTP server (`python -m http.server 8000`)
   - Smoke test: homepage loads, orchestrator map functional, L2 pages accessible
   - Share staging URL with stakeholders for review
   - Collect feedback (Google Form or GitHub Issues)

2. **Production Deployment Checklist**
   - [ ] All Phase 7 tests pass
   - [ ] Stakeholder approval received
   - [ ] Backup current production docs (Git tag: `docs-pre-cortex5`)
   - [ ] Deploy to GitHub Pages (`docs/` branch)
   - [ ] Update DNS/CDN if applicable
   - [ ] Invalidate CDN cache
   - [ ] Post-deployment smoke tests

3. **Rollback Plan**
   - **Trigger:** Critical bug, broken links, visual regression
   - **Action:** Revert Git commit, redeploy previous version
   - **Time to Rollback:** <10 minutes (automated script)
   - **Validation:** Smoke tests pass on rolled-back version
   - **Post-Mortem:** Document issue, update tests to prevent recurrence

4. **Post-Deployment Monitoring**
   - Monitor Lighthouse scores (daily for 1 week)
   - Check Google Analytics (traffic, bounce rate, page views)
   - Monitor error logs (JavaScript console errors)
   - User feedback survey (embedded in docs)

**Deliverables:**
- `deployment-checklist.md` (pre-deployment validation)
- `rollback-procedure.md` (step-by-step rollback)
- `artifacts/deployment-script.sh` (automated deployment)
- `reports/post-deployment-report.md` (monitoring results)

**Success Criteria:**
- Staging deployment successful (0 critical issues)
- Production deployment: <5 minutes downtime
- Rollback plan tested (dry-run successful)
- Post-deployment smoke tests: 100% pass rate
- User feedback: ≥80% positive (4-5 stars)

---

## 📁 Folder Structure

```
cortex-brain/documents/planning/active/cortex-docs/
├── 00-cortex5-docs-update.md          # This file (master plan)
├── README.md                           # Quick start guide
│
├── analysis/                           # Deep analysis reports
│   ├── content-inventory.md            # All docs audited
│   ├── architecture-change-matrix.md   # Epic changes → doc sections
│   ├── theme-audit-report.md           # CSS inconsistencies
│   └── orchestrator-inventory.md       # All orchestrators metadata
│
├── artifacts/                          # Generated code & assets
│   ├── orchestrator-registry.json      # All orchestrators (machine-readable)
│   ├── orchestrator-template.html      # Jinja2 template for L2 pages
│   ├── yaml-parser.py                  # YAML → JSON parser
│   ├── html-generator.py               # Jinja2 → HTML generator
│   ├── d3-data-generator.js            # D3.js data prep
│   ├── orchestrator-map-data.json      # D3.js visualization data
│   ├── css-variables.json              # Theme tokens
│   ├── deployment-script.sh            # Automated deployment
│   └── home-page-diff.md               # Before/after comparison
│
├── context/                            # Context discovery
│   ├── current-doc-structure.json      # Existing docs inventory
│   ├── glassmorphism-reference.md      # Admin dashboard patterns
│   └── cortex5-epic-summary.md         # Architecture changes summary
│
├── reports/                            # Progress & completion reports
│   ├── phase-1-complete.md             # Architecture analysis report
│   ├── phase-2-complete.md             # Content rewrite report
│   ├── phase-3-complete.md             # L1 update report
│   ├── phase-4-complete.md             # L2 generation report
│   ├── phase-5-complete.md             # CSS standardization report
│   ├── phase-6-complete.md             # Parser automation report
│   ├── phase-7-complete.md             # Testing validation report
│   ├── phase-8-complete.md             # Deployment report
│   ├── test-results.md                 # Comprehensive test results
│   ├── post-deployment-report.md       # Monitoring results
│   ├── css-audit-report.md             # CSS before/after
│   └── page-generation-log.md          # HTML generation audit trail
│
└── tracking/                           # Progress tracking
    ├── progress-tracker.json           # JSON progress tracker
    └── CONTINUATION-PROMPT.md          # Resume guidance
```

---

## 🔗 Dependencies

### Upstream Dependencies (Must Complete First)

1. **cortex5-enhancement-epic Phase 0** (BLOCKING)
   - CORTEX-5.5 branch created
   - ~150 essential files migrated
   - Pull-on-demand system operational
   - Phase 1 scaffolding ready

### Downstream Dependencies (Blocked By This Plan)

1. **cortex5-enhancement-epic Phase 1-11 Documentation**
   - User guides for Knowledge Extension Layer
   - API documentation for custom orchestrators
   - Rule layering tutorials

2. **GitHub Pages Deployment**
   - Public documentation site
   - SEO optimization
   - Google Analytics integration

---

## 📊 Timeline & Milestones

| Week | Milestone | Phases | Status |
|------|-----------|--------|--------|
| **1** | Content Analysis & Core Rewrites | Phase 1-2 | 🟡 Not Started |
| **2** | Orchestrator Documentation (L1 + L2) | Phase 3-4 | 🟡 Not Started |
| **3** | Theme Standardization & Parsers | Phase 5-6 | 🟡 Not Started |
| **4** | Testing, Validation & Deployment | Phase 7-8 | 🟡 Not Started |

### Parallel Execution

**Track 1 (Content):** Phases 1-4 (sequential dependencies)  
**Track 2 (Theme/Parsers):** Phases 5-6 (can start after Phase 2 complete)  
**Track 3 (Validation):** Phases 7-8 (requires Phases 1-6 complete)

---

## 🛡️ Brain Protection (SKULL Enforcement)

### Planning Isolation

✅ **This plan creates documentation ONLY** - No code implementation  
✅ Parser scripts generate HTML from YAML (automation, not manual coding)  
✅ CSS standardization applies existing patterns (no new architecture)

### Holistic Discovery

Before creating new files, search:
```bash
# Check for existing documentation parsers
rg "YAML.*parser" --type py

# Check for existing glassmorphism CSS
rg "glassmorphism" --type css

# Check for existing D3.js orchestrator maps
rg "d3.*orchestrator.*map" --type js
```

### Git Isolation

✅ Documentation changes commit to CORTEX repository only  
✅ No cross-repo commits (user repos unaffected)  
✅ Branch: `CORTEX-5.5` (not `CORTEX-5.0`)

### TDD Enforcement

✅ Phase 7 creates comprehensive test suite BEFORE deployment  
✅ Tests written before content regeneration (RED → GREEN)  
✅ Parsers tested with sample YAML before production run

---

## 📚 Reference Documents

### Source Manifests (Read-Only, Do Not Modify)

- `cortex-brain/manifests/orchestrators/*.yaml` (46 files)
- `cortex-brain/config/master-orchestrator.yaml`
- `cortex-brain/brain-protection-rules.yaml`
- `cortex-brain/response-templates-v4.yaml`

### Upstream Context

- `cortex5-enhancement-epic/00-cortex5-epic.md` (Epic master plan)
- `cortex5-enhancement-epic/PHASE-0-INTEGRATION-SUMMARY.md` (Phase 0 details)
- `cortex5-enhancement-epic/tracking/progress-tracker.json` (Epic state)

### Existing Documentation

- `docs/index.html` (current home page - to be updated)
- `docs/orchestrators/index.html` (current L1 - to be updated)
- `docs/technical/README.md` (technical docs guide)
- `docs/README.md` (documentation overview)

---

## 🎯 Next Steps

### For Immediate Execution

1. **Verify Phase 0 Completion:**
   ```powershell
   git branch -a | Select-String "CORTEX-5.5"
   Test-Path "cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/phase-0-complete.json"
   ```

2. **Review & Approve Plan:**
   - Review all 8 phases (scope, timeline, deliverables)
   - Confirm glassmorphism theme standardization approach
   - Approve parser automation strategy
   - Sign off on testing requirements

3. **Execute Phase 1:**
   ```bash
   # Start content inventory
   python scripts/audit_docs.py --output analysis/content-inventory.md
   
   # Extract architecture changes
   python scripts/extract_epic_changes.py cortex5-enhancement-epic --output analysis/architecture-change-matrix.md
   ```

### For Continuation (If Session Ends)

**Resume Prompt:**
```
Continue CORTEX5 holistic documentation update plan from Phase [N]

Context:
- Plan: cortex5-docs-holistic-update
- Location: cortex-brain/documents/planning/active/cortex5-docs-holistic-update/
- Last Phase: [Phase N - Name]
- Next Action: [Specific task from Phase N+1]
```

---

## 📋 Approval Checklist

**Before starting execution, confirm:**

- [ ] cortex5-enhancement-epic Phase 0 COMPLETE (CORTEX-5.5 branch exists)
- [ ] All 8 phases reviewed and scope approved
- [ ] Timeline realistic (4 weeks with parallel tracks)
- [ ] Deliverables clearly defined (60+ artifacts)
- [ ] Success criteria measurable (100% test pass rate, WCAG AA compliance)
- [ ] Dependencies mapped (upstream/downstream)
- [ ] Brain protection rules understood (Planning Isolation, TDD, Git Isolation)
- [ ] Reference documents accessible (YAML manifests, epic plans)

**Approved By:** [Pending]  
**Approval Date:** [Pending]  
**Start Date:** [After Phase 0 complete]

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
