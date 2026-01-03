# 📊 CORTEX Documentation Link Analysis Report
**Generated:** 2026-01-03  
**Analysis Scope:** Complete recursive scan of docs/ folder

---

## 🎯 Executive Summary

### Statistics
- **Total Files:** 393
- **HTML Files:** 199
- **Linked HTML Files:** 331 (some non-HTML files linked)
- **Root-Level Files:** 15
  - **Linked:** 3 (20%)
  - **Unlinked:** 12 (80%)
- **Orphaned HTML Files:** 37 (in subfolders but not linked)

---

## 🔗 Root-Level Files Analysis

### ✅ LINKED Root Files (Keep in Root)
These files ARE properly linked and should remain at root level:

1. **index.html** - Main entry point (273 incoming links)
2. **sitemap.html** - Site navigation (2 incoming links)
3. **faq.html** - FAQ page (2 incoming links)

### ❌ UNLINKED Root Files (Candidates for Action)

#### Infrastructure Files (Keep - Required)
- `.deployment-trigger` - GitHub Pages deployment
- `.nojekyll` - GitHub Pages config
- `.trigger` - Build trigger
- `404.md` - Error page
- `DEPLOYMENT.md` - Deployment docs
- `QUICK-LAUNCH.md` - Quick start guide
- `README.md` - Repository documentation
- `search-index.json` - Search functionality

#### HTML/MD Files (SHOULD MOVE)
These are actual content files that should be organized into subfolders:

| Current Location | Suggested Move | Reason |
|-----------------|----------------|--------|
| `dashboard-diagnostic.html` | `development/dashboard-diagnostic.html` | Development tool |
| `test-tabs.html` | `testing/test-tabs.html` | Testing artifact |
| `testing-planning-orchestrator.md` | `testing/testing-planning-orchestrator.md` | Testing docs |
| `visual-differentiation-demo.html` | `prototypes/visual-differentiation-demo.html` | Prototype demo |

---

## 🏗️ Hub Pages (Most Referenced)

These pages are the primary navigation hubs:

| Rank | File | Incoming Links | Category |
|------|------|----------------|----------|
| 1 | `index.html` | 273 | Main entry |
| 2 | `knowledge/index.html` | 93 | Knowledge hub |
| 3 | `knowledge/engineering.html` | 25 | Engineering |
| 4 | `architecture/index.html` | 22 | Architecture |
| 5 | `knowledge/design-patterns-hub.html` | 19 | Patterns |
| 6 | `knowledge/security-hub.html` | 18 | Security |
| 7 | `knowledge/api-design-hub.html` | 18 | API Design |
| 8 | `orchestrators/index.html` | 17 | Orchestrators |
| 9 | `knowledge/testing-hub.html` | 17 | Testing |
| 10 | `features/index.html` | 14 | Features |

---

## 🏝️ Orphaned HTML Files (37 Total)

These HTML files exist in subfolders but are NOT linked from anywhere:

### Architecture (2)
- `architecture/brain-tiers.html`
- `architecture/index-old.html`

### Best Practices (1)
- `best-practices/index.html`

### CORTEX Lens Output (2)
- `cortex-lens-output/index.html`
- `cortex-lens-output/mock-landing/tests/test-runner.html`

### Future (1)
- `future/index.html`

### Getting Started (1)
- `getting-started/index-old.html`

### Knowledge Base (3)
- `knowledge/database/oracle-best-practices.html`
- `knowledge/ddd/ddd-fundamentals.html`
- `knowledge/index-old.html`
- `knowledge/testing/tdd.html`

### Lens (1)
- `lens/index-old.html`

### Orchestrators (1)
- `orchestrators/onboarding-orchestrator.html`

### Prototypes (2)
- `prototypes/home-redesign-v2.html`
- `prototypes/mega-menu-prototype.html`

### ROI Calculator (1)
- `roi-calculator/index.html`

### Story Chapters (13)
- `story/Prologue/index.html`
- `story/Chapter-01/index.html`
- `story/Chapter-02/index.html`
- `story/Chapter-03/index.html`
- `story/Chapter-04/index.html`
- `story/Chapter-05/index.html`
- `story/Chapter-06/index.html`
- `story/Chapter-07/index.html`
- `story/Chapter-08/index.html`
- `story/Chapter-09/index.html`
- `story/Chapter-10/index.html`
- `story/Chapter-11/index.html`
- `story/Chapter-12/index.html`
- `story/Chapter-13/index.html`
- `story/tests/index.html`

### Technical (3)
- `technical/orchestrators/ado-planning.html`
- `technical/orchestrators/architectural-review.html`
- `technical/security/dashboard.html`

### Token Optimization (1)
- `token-optimization/index-old.html`

### Toolkit Manager (1)
- `toolkit-manager/index-old.html`

### Validation (1)
- `validation/index.html`

---

## 📋 Direct Links from index.html

The main `index.html` directly links to 55 files. Key page links:

### Navigation Pages
1. `architecture/index.html`
2. `features/index.html`
3. `getting-started/index.html`
4. `governance/skull-rulebook.html`
5. `knowledge/index.html`
6. `learning-paths/index.html`
7. `lens/index.html`

### Orchestrator Pages
- `orchestrators/ado-operations.html`
- `orchestrators/ado-orchestrator.html`
- `orchestrators/ado-planning.html`
- `orchestrators/architectural-review.html`
- `orchestrators/cleanup-orchestrator.html`
- `orchestrators/cortex-lens.html`
- `orchestrators/debug-orchestrator.html`
- `orchestrators/execution-orchestrator.html`
- `orchestrators/git-checkpoint.html`
- `orchestrators/planning-system.html`
- `orchestrators/refinement-orchestrator.html`
- `orchestrators/rollback-orchestrator.html`
- `orchestrators/sanitization-orchestrator.html`

### Resources
- `faq.html`
- Various assets (CSS, JS, images)

---

## 🎯 Recommended Actions

### IMMEDIATE (High Priority)

1. **Move Root-Level Content Files**
   ```
   dashboard-diagnostic.html → development/dashboard-diagnostic.html
   test-tabs.html → testing/test-tabs.html
   testing-planning-orchestrator.md → testing/testing-planning-orchestrator.md
   visual-differentiation-demo.html → prototypes/visual-differentiation-demo.html
   ```

2. **Review Orphaned Files with "-old" suffix (5 files)**
   - These appear to be outdated versions
   - **Recommended:** Delete or archive
   - Files: `**/index-old.html`

3. **Review Story Chapter Structure (15 files)**
   - All 13 chapters + prologue + tests are orphaned
   - **Decision needed:** Are these still active content?
   - **If active:** Add navigation from `story/viewer.html`
   - **If obsolete:** Move to archive or delete

### MEDIUM Priority

4. **Link or Archive Orphaned Features**
   - `best-practices/index.html` - Should be linked from knowledge hub
   - `roi-calculator/index.html` - Should be linked from features
   - `validation/index.html` - Should be linked from development
   - `future/index.html` - Should be linked from roadmap

5. **Consolidate Technical Docs**
   - Files in `technical/` folder are duplicates of `orchestrators/`
   - **Recommended:** Remove `technical/` folder, use canonical URLs

### LOW Priority

6. **Clean Up Test Artifacts**
   - `cortex-lens-output/mock-landing/tests/test-runner.html`
   - Evaluation: Keep if actively used for testing, else delete

---

## 📊 Link Graph Insights

### Most Connected Pages (Navigation Importance)
The pages with highest incoming link counts are the primary navigation hubs. The knowledge base (`knowledge/index.html` with 93 links) is second only to the homepage, indicating it's a critical navigation point.

### Isolated Content
37 HTML files (19% of all HTML files) are completely unreachable from the main navigation tree starting at `index.html`. This suggests either:
- Outdated content that should be archived/deleted
- Work-in-progress that needs navigation added
- Test/prototype files that should be moved

---

## 🔍 Data Files

Full analysis data available in:
- **Complete:** `docs-link-analysis-report.json` (large file with full link graph)
- **Summary:** `docs-link-analysis-SUMMARY.json` (focused insights)

---

## ✅ Verification Steps

To implement changes:

1. **Before moving files:** Check if they're referenced in:
   - JavaScript code
   - CSS files
   - External documentation
   - Bookmarks/shortcuts

2. **After moving files:** Run the analysis again to verify:
   ```bash
   python analyze_docs_links.py
   ```

3. **Test navigation:** Manually verify all hub pages still load correctly

---

**Report Generated By:** CORTEX Link Analysis Tool  
**Script:** `analyze_docs_links.py`  
**Verification:** `summarize_link_analysis.py`
