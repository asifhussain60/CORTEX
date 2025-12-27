# HTML Regeneration Plan - December 27, 2025

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

**STATUS:** ✅ **PHASE 4 COMPLETE** - All 31 HTML files validated with html5lib

---

## 🎉 FINAL VALIDATION RESULTS

**Date:** December 27, 2025  
**Validator:** html5lib 1.1+ (proper HTML5 parser)  
**Results:** ✅ **ALL 31 FILES VALID** (100% pass rate)

### Duplicate Filenames Found (By Design):
- **index.html** (6 locations): Root, orchestrators/, architecture/, technical/, technical/orchestrators/, validation/
- **planning-system.html** (2 locations): features/, orchestrators/
- **tdd-orchestrator.html** (2 locations): orchestrators/, technical/orchestrators/

**Note:** These are intentional duplicates serving different contexts (overview vs technical detail).

### Validation Method:
- **Old Parser:** Python's `html.parser.HTMLParser` (buggy with self-closing tags)
- **New Parser:** `html5lib` (proper HTML5 specification compliance)
- **Issue Fixed:** HTMLParser incorrectly treated `<img />` as both start AND end tag

---

## 🎯 Objective

Delete and recreate 32 invalid HTML files following `docgen.prompt.md` guidelines:
- ✅ 100% glassmorphism compliance (centralized CSS in main.css)
- ✅ Feature-benefit-panels on all feature/orchestrator pages
- ✅ ZERO inline styles (except story button preservation)
- ✅ DELETE → CREATE workflow (no partial updates)
- ✅ Proper HTML5 structure with semantic tags
- ✅ WCAG 2.1 Level AA accessibility

---

## 📊 Current State

**Total Files:** 58 HTML files  
**✅ Valid:** 26 (45%)  
**❌ Invalid:** 32 (55%)

### Error Breakdown
- **Self-closing </br> tags:** 17 files (~60 instances)
- **Invalid </img> closing tags:** 10 files
- **Mismatched tag structure:** 4 files (faq.html, tdd-orchestrator.html, tutorial.html, architecture/index.html)
- **Missing closing angle brackets:** 8 files

---

## 🗺️ Execution Strategy

### Critical Principles from docgen.prompt.md

1. **File Regeneration (Section 1.5):**
   ```bash
   # ✅ CORRECT: Delete first, then create fresh
   rm docs/index.html
   create_file docs/index.html [complete content]
   
   # ❌ WRONG: Partial update or replace_string_in_file on HTML
   replace_string_in_file docs/index.html [old] [new]  # FORBIDDEN
   ```

2. **Glassmorphism Enforcement (Section 2):**
   - ALL pages link to: `<link rel="stylesheet" href="../assets/css/main.css">`
   - ❌ FORBIDDEN: Inline `style=""` attributes (except story button image)
   - ❌ FORBIDDEN: Page-specific `<style>` tags
   - ❌ FORBIDDEN: Alternate CSS files in subdirectories

3. **Feature Benefit Panels (Section 3):**
   Every feature/orchestrator page MUST start with:
   ```html
   <div class="feature-benefit-panel">
       <div class="icon">🎯</div>
       <div class="description">
           Natural language efficiency statement...
       </div>
   </div>
   ```

4. **HTML Quality Tools (Section 2.5):**
   ```bash
   # Step 11a: Remove inline styles
   python3 cortex-toolkit/documentation/html-tools/html_style_centralizer.py
   
   # Step 11b: Validate syntax
   python3 cortex-toolkit/documentation/html-tools/html_validator.py
   ```

---

## 📋 10-Phase Execution Plan

### Phase 1: Backup & Source Discovery
**Duration:** 15 minutes  
**Risk:** Low

**Tasks:**
1. Create backup directory: `cortex-brain/backups/html-invalid-20251227/`
2. Copy all 32 invalid files to backup
3. Map each file to source documents:
   - Orchestrators → `src/orchestrators/*.py` + `cortex-operations.yaml`
   - Architecture → `cortex-brain/documents/archive/*-ARCHITECTURE.md`
   - Features → Discovery from CORTEX4-STATUS.md
   - FAQ → Extract from current faq.html content
4. Extract template patterns from 26 valid files

**Success Criteria:**
- ✅ Backup directory created with all 32 files
- ✅ Source mapping document created
- ✅ Template patterns documented

---

### Phase 2: Delete Invalid HTML Files (32 files)
**Duration:** 5 minutes  
**Risk:** Medium (requires backup verification)

**Files to Delete:**

**Critical (4 files):**
- `docs/faq.html`
- `docs/technical/orchestrators/tdd-orchestrator.html`
- `docs/getting-started/tutorial.html`
- `docs/architecture/index.html`

**Orchestrators (13 files):**
- `docs/technical/orchestrators/architectural-review.html`
- `docs/technical/orchestrators/autonomous-execution.html`
- `docs/technical/orchestrators/cleanup-orchestrator.html`
- `docs/technical/orchestrators/code-sanitization.html`
- `docs/technical/orchestrators/debug-orchestrator.html`
- `docs/technical/orchestrators/git-checkpoint.html`
- `docs/technical/orchestrators/intelligent-dashboard.html`
- `docs/technical/orchestrators/maintenance-orchestrator.html`
- `docs/technical/orchestrators/planning-system.html`
- `docs/technical/orchestrators/pre-flight.html`
- `docs/technical/orchestrators/refinement-orchestrator.html`
- `docs/technical/orchestrators/rollback-orchestrator.html`
- `docs/technical/orchestrators/system-integrity.html`

**Getting Started (4 files):**
- `docs/getting-started/deployment.html`
- `docs/getting-started/first-commands.html`
- `docs/getting-started/index.html`
- `docs/getting-started/multi-repo-setup.html`

**Architecture (5 files):**
- `docs/architecture/agent-system.html`
- `docs/architecture/four-tier-brain.html`
- `docs/architecture/orchestrator-ecosystem.html`
- `docs/architecture/working-memory.html`

**Features & Validation (6 files):**
- `docs/features/ado-operations.html`
- `docs/features/index.html`
- `docs/features/tdd-mastery.html`
- `docs/technical/toolkit/index.html`
- `docs/technical/toolkit/validation-tools.html`
- `docs/technical/validation/capabilities.html`
- `docs/validation/index.html`

**Commands:**
```bash
# Verify backup first
ls -la cortex-brain/backups/html-invalid-20251227/ | wc -l  # Should be 34 (32 files + . + ..)

# Delete critical files
rm docs/faq.html
rm docs/technical/orchestrators/tdd-orchestrator.html
rm docs/getting-started/tutorial.html
rm docs/architecture/index.html

# Delete orchestrators
rm docs/technical/orchestrators/architectural-review.html
rm docs/technical/orchestrators/autonomous-execution.html
rm docs/technical/orchestrators/cleanup-orchestrator.html
rm docs/technical/orchestrators/code-sanitization.html
rm docs/technical/orchestrators/debug-orchestrator.html
rm docs/technical/orchestrators/git-checkpoint.html
rm docs/technical/orchestrators/intelligent-dashboard.html
rm docs/technical/orchestrators/maintenance-orchestrator.html
rm docs/technical/orchestrators/planning-system.html
rm docs/technical/orchestrators/pre-flight.html
rm docs/technical/orchestrators/refinement-orchestrator.html
rm docs/technical/orchestrators/rollback-orchestrator.html
rm docs/technical/orchestrators/system-integrity.html

# Delete getting started
rm docs/getting-started/deployment.html
rm docs/getting-started/first-commands.html
rm docs/getting-started/index.html
rm docs/getting-started/multi-repo-setup.html

# Delete architecture
rm docs/architecture/agent-system.html
rm docs/architecture/four-tier-brain.html
rm docs/architecture/orchestrator-ecosystem.html
rm docs/architecture/working-memory.html

# Delete features & validation
rm docs/features/ado-operations.html
rm docs/features/index.html
rm docs/features/tdd-mastery.html
rm docs/technical/toolkit/index.html
rm docs/technical/toolkit/validation-tools.html
rm docs/technical/validation/capabilities.html
rm docs/validation/index.html
```

**Success Criteria:**
- ✅ All 32 files deleted
- ✅ Backup verified complete
- ✅ No broken directory structure

---

### Phase 3: Regenerate Critical Structure (4 files)
**Duration:** 60 minutes  
**Risk:** High (complex structure)

**Priority Order:**
1. **faq.html** (4 structural errors)
   - 8 categories with accordion UI
   - Cross-references to all documentation
   - FAQ search functionality
   - Proper section/div nesting with `.faq-container` wrappers

2. **tdd-orchestrator.html** (17 errors)
   - Feature benefit panel: "Writing tests first sounds great..."
   - RED-GREEN-REFACTOR cycle explanation
   - Phase-by-phase breakdown
   - D3.js TDD cycle diagram
   - No </br> tags, proper <br> self-closing

3. **tutorial.html** (2 errors)
   - Interactive walkthrough
   - Step-by-step with code examples
   - Cross-references to learning-paths/
   - Fix code tag mismatch (line 229-243)

4. **architecture/index.html** (2 errors)
   - Architecture overview with D3.js visualization
   - 4-Tier Brain introduction
   - Fix </img> and </script> mismatches
   - Proper semantic HTML5 structure

**Template Structure (from docgen.prompt.md):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title | CORTEX 4.0</title>
    <link rel="stylesheet" href="../assets/css/main.css">
</head>
<body>
    <!-- Logo Header (except home) -->
    <div class="logo-header">
        <a href="../index.html">
            <img src="../assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="page-logo">
        </a>
    </div>

    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb">
        <a href="../index.html">Home</a>
        <span class="separator">›</span>
        <a href="index.html">Category</a>
        <span class="separator">›</span>
        <span class="current">Page Title</span>
    </nav>

    <main>
        <!-- Feature Benefit Panel (orchestrators/features only) -->
        <div class="feature-benefit-panel">
            <div class="icon">🎯</div>
            <div class="description">
                Natural language efficiency statement...
            </div>
        </div>

        <!-- Content sections -->
        <section class="section-overview">
            <h1>Page Title</h1>
            <!-- Content -->
        </section>
    </main>

    <!-- Footer -->
    <footer>
        <p>&copy; 2025 CORTEX. All rights reserved.</p>
    </footer>

    <script src="../assets/js/main.js" defer></script>
</body>
</html>
```

**Success Criteria:**
- ✅ All 4 files recreated with complete content
- ✅ HTML validator reports 0 errors
- ✅ Feature benefit panels present
- ✅ NO inline styles
- ✅ Proper semantic structure

---

### Phase 4: Regenerate Orchestrator Pages (13 files)
**Duration:** 90 minutes  
**Risk:** Medium

**Content Source:** `src/orchestrators/*.py` + `cortex-operations.yaml`

**Template Sections (from docgen.prompt.md Section "Orchestrator Pages"):**
1. Feature Benefit Panel (ALWAYS FIRST)
2. Key Metrics Grid (execution time, efficiency gains)
3. Overview Section (purpose, capabilities, phase count)
4. Architecture Section (component diagram reference)
5. Workflow Section (phase-by-phase breakdown)
6. Integration Section (connections with other orchestrators)
7. Configuration Section (manifest structure, YAML config)
8. Usage Examples (3-5 real-world scenarios)
9. Testing Section (test coverage, validation approach)
10. Performance Section (metrics)
11. Interactive Diagram (D3.js/Mermaid)

**Files:**
- architectural-review.html
- autonomous-execution.html
- cleanup-orchestrator.html
- code-sanitization.html
- debug-orchestrator.html
- git-checkpoint.html
- intelligent-dashboard.html
- maintenance-orchestrator.html
- planning-system.html
- pre-flight.html
- refinement-orchestrator.html
- rollback-orchestrator.html
- system-integrity.html

**Icon Selection Guide:**
- Planning: 🎯
- TDD: ✅
- Execution: ⚡
- ADO: 📋
- Sanitization: 🔒
- Cleanup: 🧹
- Debug: 🔍
- Git: 📦
- Dashboard: 📊
- Maintenance: 🔧
- Pre-flight: ✈️
- Refinement: ✨
- Rollback: ↩️
- System Integrity: 🛡️

**Success Criteria:**
- ✅ All 13 files recreated
- ✅ Feature benefit panels with natural language
- ✅ NO </br> tags (use <br> or <br/>)
- ✅ All styling via main.css classes

---

### Phase 5: Regenerate Getting Started (4 files)
**Duration:** 45 minutes  
**Risk:** Low

**Content Focus:** User onboarding before deep-dive documentation

**Files:**
1. **deployment.html** - Installation instructions
2. **first-commands.html** - Essential commands (plan, start tdd, sanitize)
3. **index.html** - Quick start (5 min setup, 1:∞ repo support)
4. **multi-repo-setup.html** - Phase 11 configuration

**Template Requirements:**
- Step-by-step instructions
- Code examples with syntax highlighting
- Cross-references to orchestrators/, architecture/
- D3.js/Mermaid diagrams for visual learners

**Success Criteria:**
- ✅ All 4 files recreated
- ✅ NO </img> closing tags
- ✅ Clear step-by-step progression
- ✅ Cross-references functional

---

### Phase 6: Regenerate Architecture (5 files)
**Duration:** 60 minutes  
**Risk:** Medium

**Content Source:** `cortex-brain/documents/archive/*-ARCHITECTURE.md`

**Files:**
1. **agent-system.html** - 2 agents (Planning, Strategic Reasoning)
2. **four-tier-brain.html** - Tier 0-3 architecture
3. **index.html** - Architecture overview
4. **orchestrator-ecosystem.html** - BaseOrchestrator pattern
5. **working-memory.html** - 70-conversation FIFO queue

**Template Sections:**
1. Feature Benefit Panel (architecture impact on efficiency)
2. Conceptual Overview
3. Component Breakdown
4. Data Flow diagrams
5. Integration patterns
6. Design Patterns used
7. Performance metrics
8. Interactive D3.js visualization

**Success Criteria:**
- ✅ All 5 files recreated
- ✅ Missing closing angle brackets fixed
- ✅ D3.js diagrams integrated
- ✅ Semantic HTML5 structure

---

### Phase 7: Regenerate Features & Validation (6 files)
**Duration:** 45 minutes  
**Risk:** Low

**Files:**
1. **features/ado-operations.html** - Azure DevOps integration
2. **features/index.html** - Features overview
3. **features/tdd-mastery.html** - TDD workflow
4. **technical/toolkit/index.html** - Toolkit overview
5. **technical/toolkit/validation-tools.html** - Validation tools
6. **technical/validation/capabilities.html** - 9 validated capabilities
7. **validation/index.html** - Phase 13B STS validation

**Template Sections:**
1. Feature Benefit Panel (user-centric description)
2. What It Does
3. Why It Matters (business value)
4. How It Works (technical overview)
5. Integration (ecosystem fit)
6. Usage examples
7. Performance metrics

**Success Criteria:**
- ✅ All 7 files recreated (includes validation/index.html from earlier count)
- ✅ NO </img> closing tags
- ✅ Feature benefit panels with efficiency statements
- ✅ Cross-references to related docs

---

### Phase 8: Run HTML Quality Tools (MANDATORY)
**Duration:** 10 minutes  
**Risk:** Low

**Tools:**
```bash
# Step 1: Remove any remaining inline styles
python3 cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Expected Output:
# ✅ Processed 58 files
# ✅ Removed 0 inline styles (if compliant)

# Step 2: Validate all HTML syntax
python3 cortex-toolkit/documentation/html-tools/html_validator.py

# Expected Output:
# ✅ All 58 files are syntactically correct
```

**Manual Validation:**
```bash
# Verify NO inline styles (except story button)
grep -r 'style="' docs/**/*.html | grep -v 'story/viewer.html' | grep -v 'Awakening.png'
# Should return 0 results

# Verify all pages use main.css
grep -r 'stylesheet' docs/**/*.html | grep -v 'main.css' | grep -v 'story/'
# Should return 0 results (no alternate CSS files)
```

**Success Criteria:**
- ✅ html_validator.py reports 0 errors
- ✅ html_style_centralizer.py removed 0 styles (already compliant)
- ✅ Manual validation passes

---

### Phase 9: Cross-Link & Navigation Validation
**Duration:** 30 minutes  
**Risk:** Medium

**Validation Checklist:**

**Links:**
- [ ] All internal links resolve (no 404s)
- [ ] Breadcrumbs work on all pages (except home)
- [ ] Cross-references to related docs functional
- [ ] Story button preserved on home (story/index.html resolves)

**Visual:**
- [ ] CORTEX logo appears on all pages (except home) with `.page-logo` class
- [ ] Glassmorphism theme consistent (glass-bg, shadows, colors)
- [ ] Feature benefit panels styled correctly

**Responsive:**
- [ ] Mobile (320px): Single column, stacked cards
- [ ] Tablet (768px): 2 columns
- [ ] Desktop (1024px+): 3-6 columns

**Accessibility:**
- [ ] Lighthouse accessibility score >90
- [ ] Color contrast 4.5:1 minimum
- [ ] Keyboard navigation functional (Tab, Enter, Escape)
- [ ] Skip to main content link present
- [ ] Focus indicators visible
- [ ] ARIA labels for icon-only buttons
- [ ] Alt text for all images

**Tools:**
```bash
# Check for broken links
find docs -name "*.html" -exec grep -H 'href="' {} \; | grep -v 'http' | grep -v '#' > links.txt
# Manually verify each link resolves

# Test responsive design (use browser DevTools)
# Chrome: Cmd+Option+I → Toggle device toolbar (Cmd+Shift+M)

# Run Lighthouse audit
# Chrome: Cmd+Option+I → Lighthouse tab → Generate report
```

**Success Criteria:**
- ✅ All internal links resolve
- ✅ Responsive design works on all breakpoints
- ✅ Lighthouse accessibility >90
- ✅ WCAG 2.1 Level AA compliance

---

### Phase 10: Final Report & Commit
**Duration:** 20 minutes  
**Risk:** Low

**Report Sections:**

1. **Executive Summary**
   - Before: 32 invalid files (55%)
   - After: 0 invalid files (0%)
   - Method: DELETE → CREATE workflow

2. **File Mapping**
   - Source documents used for each file
   - Template patterns applied

3. **Validation Results**
   - HTML syntax: 0 errors (100% pass)
   - Glassmorphism compliance: 100%
   - Accessibility: Lighthouse >90

4. **Metrics**
   - Files regenerated: 32
   - Inline styles removed: ~150+
   - Self-closing tag errors fixed: ~60
   - Structural errors fixed: 4

5. **Next Steps**
   - Maintain template library for future regenerations
   - Automate validation in CI/CD
   - Add pre-commit hook for HTML validation

**Git Commit:**
```bash
git add docs/
git commit -m "docs: Regenerate 32 invalid HTML files with glassmorphism compliance

- DELETE → CREATE workflow (no partial updates)
- 100% centralized CSS in main.css (ZERO inline styles)
- Feature-benefit-panels on all orchestrator/feature pages
- Fixed structural errors (faq, tdd, tutorial, architecture)
- Removed all </br> and </img> closing tags
- WCAG 2.1 Level AA accessibility compliance
- Lighthouse score >90 on all pages

Validation: html_validator.py reports 0 errors across 58 files"
```

**Success Criteria:**
- ✅ HTML-REGENERATION-SUMMARY.md created
- ✅ Updated html-validation-report-20251227.md
- ✅ Git commit with detailed message
- ✅ All 32 files regenerated and validated

---

## 📊 Success Metrics

**Before:**
- ✅ Valid: 26 files (45%)
- ❌ Invalid: 32 files (55%)
- Inline styles: ~150+ instances
- Self-closing errors: ~60 instances
- Structural errors: 4 files

**After (Target):**
- ✅ Valid: 58 files (100%)
- ❌ Invalid: 0 files (0%)
- Inline styles: 0 (except story button preservation)
- Glassmorphism compliance: 100%
- Accessibility: Lighthouse >90

---

## 🚨 Risk Mitigation

### Backup Strategy
- Full backup of 32 files before deletion
- Verify backup completeness before proceeding
- Keep backup for 30 days in case of rollback

### Validation Gates
- Each phase requires validation before proceeding
- HTML validator must pass (0 errors) before moving to next file
- Manual visual inspection for critical pages

### Rollback Plan
- If regeneration fails: Restore from backup
- If validation fails: Delete invalid recreation, restore backup
- Document issues in HTML-REGENERATION-ISSUES.md

---

## 📚 Reference Documents

**Templates:**
- `docgen.prompt.md` - Complete documentation generation guidelines
- `cortex-brain/knowledge/ui-ux/ui-ux-best-practices.yaml` - Design system

**Content Sources:**
- `CORTEX4-STATUS.md` - Phase completion metrics
- `src/orchestrators/*.py` - Orchestrator implementations
- `cortex-operations.yaml` - Operation definitions
- `cortex-brain/documents/archive/*-ARCHITECTURE.md` - Architecture docs

---

**End of HTML Regeneration Plan**
