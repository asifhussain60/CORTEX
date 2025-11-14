# CORTEX 3.0: GitBook Migration Plan

**Author:** Asif Hussain  
**Version:** 1.1  
**Date:** 2025-11-13 (Updated: 2025-11-14)  
**Status:** 🎯 PLANNING PHASE + Investigation Architecture Analysis  
**Target:** CORTEX 3.0 Release

---

## 📋 Executive Summary

**Objective:** Complete migration from MkDocs to GitBook for CORTEX documentation with full removal of MkDocs dependencies.

**Scope:** All user-facing documentation, API references, guides, and story content.

**Duration:** Estimated 4-6 weeks (phased approach)

**Risk Level:** MEDIUM (controlled rollout with rollback capability)

---

## 🎯 Strategic Rationale

### Why GitBook?

| Benefit | Impact | Priority |
|---------|--------|----------|
| **Professional UI/UX** | Better first impressions, easier navigation | HIGH |
| **Collaboration** | Multiple contributors, version control integration | HIGH |
| **Versioning** | Native CORTEX 2.0/3.0/4.0 documentation branches | HIGH |
| **Search** | Advanced search across all docs | MEDIUM |
| **Analytics** | Usage tracking, popular pages | MEDIUM |
| **Custom Domain** | cortex-docs.dev or similar | LOW |
| **Zero Maintenance** | No local build infrastructure | HIGH |

### Why Remove MkDocs?

| Reason | Current Pain Point | Resolution |
|--------|-------------------|------------|
| **Build Complexity** | Requires Python env, dependencies | GitBook auto-builds from GitHub |
| **Maintenance Overhead** | CSS fixes, theme updates, plugin conflicts | GitBook handles all styling |
| **Limited Collaboration** | Local builds only | GitBook web-based editing |
| **No Versioning** | Manual version management | GitBook native versioning |
| **Local Testing Required** | `mkdocs serve` for preview | GitBook live preview |

---

## 📊 Phase 1: Discovery & Analysis

**Duration:** 1 week  
**Status:** ⏳ PENDING

### 1.1 Current State Inventory

**MkDocs Infrastructure:**
```yaml
Files to Analyze:
  - mkdocs.yml (121 lines, complex nav structure)
  - requirements.txt (mkdocs, mkdocs-material, mkdocs-mermaid2-plugin)
  - docs/stylesheets/custom.css
  - docs/stylesheets/story.css
  - docs/stylesheets/technical.css
  - .github/workflows/deploy-docs.yml (CI/CD automation)

Dependencies:
  - mkdocs>=1.5.0
  - mkdocs-material>=9.4.0
  - mkdocs-mermaid2-plugin>=1.1.0
```

**Content Inventory:**
```
docs/ (708 total markdown files)
├── index.md (landing page)
├── awakening-of-cortex.md (complete story)
├── getting-started/ (4 files)
├── operations/ (6 files)
├── api/ (20+ files)
├── story/ (chapter navigation)
├── plugins/ (7 files)
├── architecture/ (5 files)
├── guides/ (5 files)
├── reference/ (tier documentation)
├── performance/ (metrics, CI/CD)
├── human-readable/ (user guides)
└── [Additional directories...]

prompts/shared/ (modular documentation for CORTEX entry point)
├── story.md (456 lines - narrative)
├── setup-guide.md (installation)
├── technical-reference.md (API docs)
├── agents-guide.md (system explanation)
├── tracking-guide.md (memory setup)
├── configuration-reference.md (config options)
└── operations-reference.md (command reference)
```

**MkDocs Usage in Codebase:**
```python
References Found:
  - tests/test_css_styles.py (7 references)
  - tests/test_css_browser_loading.py (4 references)
  - tests/docs/test_css_fixes.py (4 references)
  - src/operations/modules/build_mkdocs_site_module.py
  - src/operations/modules/update_mkdocs_index_module.py
  - cortex-brain/mkdocs-refresh-config.yaml
  - scripts/cortex/record-mkdocs-session.py
```

### 1.2 GitBook Requirements Analysis

**GitBook Plan Selection:**
- **Free Tier:** Public documentation (recommended for open-source)
- **Pro Tier:** Private docs + custom domain ($80/month if needed)

**Technical Requirements:**
- GitHub repository integration
- Markdown compatibility (✅ existing content is markdown)
- Custom domain setup (optional)
- Migration scripts for bulk import
- Redirect strategy for old URLs

### 1.3 Gap Analysis

**Content Compatibility:**

| Feature | MkDocs | GitBook | Migration Action |
|---------|--------|---------|------------------|
| Markdown | ✅ Standard | ✅ Standard | Direct copy |
| Mermaid Diagrams | ✅ Plugin | ✅ Native | Remove plugin, test rendering |
| Custom CSS | ✅ Full control | ⚠️ Limited | Extract brand colors, adapt |
| Code Highlighting | ✅ Pygments | ✅ Native | Test language support |
| Search | ✅ Basic | ✅ Advanced | Upgrade (no action) |
| Navigation | ✅ YAML config | ✅ Folder structure | Restructure `docs/` |

**Breaking Changes:**

| Current Feature | GitBook Equivalent | Mitigation |
|----------------|-------------------|------------|
| `#file:` references in prompts | Relative paths | Update all prompt file references |
| Local `mkdocs serve` | GitBook live preview | Update developer workflow docs |
| CSS customization | GitBook theming | Migrate brand colors to theme |
| Build artifacts in CI/CD | GitHub integration | Remove deploy-docs.yml workflow |

### 1.4 Deliverables

- ✅ Content inventory (708 files cataloged)
- ⏳ MkDocs dependency map
- ⏳ GitBook account setup (free tier)
- ⏳ Gap analysis report
- ⏳ Risk assessment matrix

---

## 🏗️ Phase 2: GitBook Architecture Design

**Duration:** 1.5 weeks  
**Status:** 🔜 NOT STARTED

### 2.1 Information Architecture

**Proposed GitBook Navigation:**

```
CORTEX Documentation (Root Space)
│
├── 🏠 Home
│   └── Welcome & Quick Start
│
├── 📖 Getting Started
│   ├── Installation
│   ├── Configuration
│   ├── First Task
│   └── Platform Setup (Mac/Windows/Linux)
│
├── 🧠 Core Concepts
│   ├── Four-Tier Brain Architecture
│   │   ├── Tier 0: Instinct Layer (SKULL Protection)
│   │   ├── Tier 1: Working Memory (SQLite)
│   │   ├── Tier 2: Knowledge Graph (YAML)
│   │   └── Tier 3: Context Intelligence
│   ├── 10 Specialist Agents
│   │   ├── Left Brain (Tactical)
│   │   └── Right Brain (Strategic)
│   └── Plugin System
│
├── 📚 User Guides
│   ├── Operations
│   │   ├── Environment Setup
│   │   ├── CORTEX Tutorial
│   │   ├── Help Command
│   │   └── Story Refresh
│   ├── Conversation Tracking
│   ├── Memory Management
│   └── Agent Workflows
│
├── 🔧 API Reference
│   ├── Entry Point API
│   ├── Brain System API
│   ├── Plugins
│   │   ├── Base Plugin
│   │   ├── Plugin Registry
│   │   ├── Command Registry
│   │   └── Hooks
│   ├── Agents
│   │   ├── Executor
│   │   ├── Tester
│   │   ├── Validator
│   │   └── Architect
│   └── Tiers API
│       ├── Tier 0 Governance
│       ├── Tier 1 Memory
│       ├── Tier 2 Knowledge
│       └── Tier 3 Context
│
├── 🧚 The Awakening Story
│   ├── Complete Story (Single Page)
│   └── Chapter Navigation
│
├── 🔌 Plugin Development
│   ├── Overview
│   ├── Creating Plugins
│   ├── Command System
│   ├── Platform Switch
│   ├── Doc Refresh
│   └── Code Review
│
├── 🏛️ Architecture
│   ├── System Design
│   ├── Agent Coordination
│   ├── Memory System
│   ├── Protection Layer (SKULL)
│   ├── Token Optimization
│   └── Investigation Patterns
│       ├── Guided Deep Dive Architecture
│       ├── Context Injection Strategy
│       ├── Token Budget Management
│       └── Phase-Based Analysis
│
├── 🧪 Testing & Quality
│   ├── Test Strategy
│   ├── SKULL Protection Rules
│   ├── Performance Budgets
│   └── CI/CD Integration
│
├── 📊 Performance
│   ├── Token Optimization (97.2% reduction)
│   ├── Cost Analysis ($8,636/year savings)
│   ├── Telemetry Guide
│   └── Benchmarks
│
└── 🆘 Troubleshooting
    ├── Common Issues
    ├── Limitations & Status
    └── Support
```

**Version Strategy:**

```
Main Space: CORTEX 3.0 (current/latest)
├── Version 3.0 (GitBook migration, current)
├── Version 2.1 (MkDocs, archived)
├── Version 2.0 (Modular architecture, archived)
└── Version 1.0 (Original, archived)
```

### 2.2 Content Mapping

**docs/ → GitBook Structure:**

| Current Path | GitBook Path | Action |
|-------------|-------------|---------|
| `docs/index.md` | `README.md` (root) | Move + update links |
| `docs/getting-started/*` | `getting-started/*` | Direct copy |
| `docs/operations/*` | `user-guides/operations/*` | Restructure |
| `docs/api/*` | `api-reference/*` | Direct copy |
| `docs/awakening-of-cortex.md` | `the-story/complete.md` | Move |
| `docs/plugins/*` | `plugin-development/*` | Restructure |
| `docs/architecture/*` | `architecture/*` | Direct copy |
| `cortex-brain/GUIDED-DEEP-DIVE-PATTERN.md` | `architecture/investigation-patterns/guided-deep-dive.md` | Move + format |
| `cortex-brain/GUIDED-DEEP-DIVE-INTEGRATION-POINTS.md` | `architecture/investigation-patterns/integration-points.md` | Move + format |
| `docs/guides/*` | `user-guides/*` | Merge |
| `docs/reference/*` | `api-reference/tiers/*` | Restructure |
| `docs/performance/*` | `performance/*` | Direct copy |
| `docs/human-readable/*` | `user-guides/*` | Merge |

**prompts/shared/ → GitBook:**

| Current File | GitBook Location | Strategy |
|-------------|-----------------|----------|
| `story.md` | `the-story/complete.md` | Duplicate (keep prompt version) |
| `setup-guide.md` | `getting-started/installation.md` | Duplicate |
| `technical-reference.md` | `api-reference/overview.md` | Duplicate |
| `agents-guide.md` | `core-concepts/agents.md` | Duplicate |
| `tracking-guide.md` | `user-guides/conversation-tracking.md` | Duplicate |
| `configuration-reference.md` | `getting-started/configuration.md` | Duplicate |

**Rationale for Duplication:**
- `prompts/shared/` files remain for CORTEX entry point (Copilot Chat)
- GitBook versions optimized for web reading (longer, more examples)
- Allows independent evolution of prompt context vs web docs

### 2.2.1 NEW: Investigation Architecture Documentation

**Added 2025-11-14: Guided Deep Dive Pattern Analysis**

Based on architectural analysis of CORTEX 3.0's selective context injection system, the following new documentation sections will be added:

**Investigation Patterns Section:**
```
architecture/investigation-patterns/
├── guided-deep-dive.md               # Phased investigation architecture
├── integration-points.md             # Health Validator, Intent Router integration  
├── token-budget-management.md        # 5K token limits, efficiency controls
├── context-injection-strategy.md     # Current selective vs proposed guided approach
├── phase-based-analysis.md           # 3-phase investigation workflow
└── pattern-learning-system.md        # Tier 2 Knowledge Graph integration
```

**Key Documentation Additions:**
1. **Guided Deep Dive Architecture** - Complete pattern design for "investigate why this view..." commands
2. **Token Budget Management** - 5,000 token limits with phase allocation (1,500/2,000/1,500)
3. **Integration Mapping** - Exact hooks into Intent Router, Health Validator, Pattern Matcher
4. **User Experience Design** - Phase prompts, choice points, efficiency transparency
5. **Pattern Learning System** - Investigation result storage and retrieval from Tier 2

**Content Sources:**
- Analysis findings: Current CORTEX 3.0 selective context injection limitations
- Proposed solution: Phased investigation with user guidance and token budgets  
- Integration requirements: File relationship mapping, pattern storage
- Implementation roadmap: 8-hour development plan with validation metrics

**Documentation Priority:** HIGH - Critical for CORTEX 3.0 investigation capabilities

This analysis demonstrates CORTEX's ability to challenge architectural assumptions, propose efficiency-balanced solutions, and create comprehensive implementation plans.

### 2.3 Brand & Styling

**GitBook Theme Configuration:**

```yaml
Brand Colors (from CORTEX palette):
  Primary: "#8b5cf6" (Deep Purple - Tier 0)
  Accent: "#4ecdc4" (Teal - Tier 1)
  Secondary: "#45b7d1" (Blue - Tier 2)
  Success: "#96ceb4" (Green - Tier 3)

Typography:
  Headings: "Inter" or "Roboto"
  Body: "Roboto"
  Code: "Roboto Mono"

Logo:
  - Use CORTEX brain diagram (to be created)
  - Favicon: Tier 0 red icon
```

**Custom CSS Equivalents:**

| MkDocs Custom Style | GitBook Equivalent | Action |
|--------------------|-------------------|---------|
| `docs/stylesheets/story.css` | GitBook theme | Extract font families, test |
| `docs/stylesheets/technical.css` | Native code blocks | Test syntax highlighting |
| `docs/stylesheets/custom.css` | GitBook customization | Migrate brand colors |

### 2.4 Integration Points

**GitHub Integration:**
```yaml
Repository: github.com/asifhussain60/CORTEX
Branch Sync:
  - main → CORTEX 3.0 (live docs)
  - CORTEX-2.1 → Version 2.1 (archived)
  
Auto-Deploy:
  - Trigger: Push to main branch
  - Source: docs/ directory
  - Build: GitBook auto-build
```

**Search Configuration:**
```yaml
GitBook Search:
  - Index all content
  - Enable suggestions
  - Highlight matches
  - Search API for extensions (future)
```

### 2.5 Deliverables

- ⏳ Complete navigation structure (YAML/JSON)
- ⏳ Content mapping spreadsheet
- ⏳ GitBook space setup (free tier)
- ⏳ Theme configuration
- ⏳ GitHub integration configured

---

## 🚀 Phase 3: Migration Execution

**Duration:** 2 weeks  
**Status:** 🔜 NOT STARTED

### 3.1 Content Transfer Strategy

**Batch Migration Approach:**

```
Week 1:
  Day 1-2: Core content
    - Home page (index.md)
    - Getting Started (4 files)
    - Core Concepts (brain architecture, agents)
  
  Day 3-4: User guides
    - Operations (6 files)
    - Tracking guide
    - Configuration guide
  
  Day 5: API Reference (Phase 1)
    - Entry point
    - Brain system API
    - Plugin base classes

Week 2:
  Day 6-7: API Reference (Phase 2)
    - All agent APIs
    - Tier APIs (4 files)
    - Plugin system docs
  
  Day 8-9: Story & Plugins
    - Awakening story (complete)
    - Plugin development guides (7 files)
    - Architecture docs (5 files)
    - Investigation patterns (NEW: 6 files)
      ├── Guided Deep Dive architecture
      ├── Integration points mapping
      ├── Token budget management
      └── Context injection strategy
  
  Day 10: Testing & Performance
    - Test strategy
    - Performance metrics
    - Troubleshooting guides
```

**Migration Script:**

```python
# scripts/migrate_to_gitbook.py

import os
import re
from pathlib import Path

def migrate_content():
    """
    Automated content migration script.
    
    Tasks:
    1. Copy markdown files from docs/ to gitbook/
    2. Update internal links (../relative → absolute)
    3. Fix image paths (docs/images → .gitbook/assets)
    4. Convert #file: references (for duplicated content)
    5. Generate SUMMARY.md (GitBook navigation)
    6. Validate all links
    """
    
    # Content mapping from Phase 2.2
    mapping = {
        "docs/index.md": "README.md",
        "docs/getting-started/": "getting-started/",
        "docs/operations/": "user-guides/operations/",
        # ... (full mapping)
    }
    
    # Process each file
    for src, dest in mapping.items():
        # Copy + transform
        pass
    
    # Generate navigation
    generate_summary_md()
    
    # Validate
    validate_links()
    validate_images()
```

**Manual Steps:**

| Task | Complexity | Time Est. | Owner |
|------|-----------|-----------|-------|
| Create GitBook space | Low | 30 min | Admin |
| Configure GitHub sync | Low | 1 hour | Admin |
| Run migration script | Medium | 2 hours | Dev |
| Review all pages | High | 8 hours | Team |
| Fix broken links | Medium | 4 hours | Dev |
| Test navigation | Low | 2 hours | QA |
| Style adjustments | Medium | 4 hours | Designer |

### 3.2 Reference Updates

**Files Requiring Updates:**

**1. Prompt Files (CRITICAL):**
```markdown
File: .github/prompts/CORTEX.prompt.md
Current:
  #file:prompts/shared/story.md

Options:
  A. Keep #file: references (prompt files stay in repo)
  B. Update to GitBook URLs (https://cortex.gitbook.io/...)
  
Recommendation: Option A (keep prompts in repo for offline use)
```

**2. CI/CD Workflows:**
```yaml
File: .github/workflows/deploy-docs.yml
Action: DELETE (replaced by GitBook auto-deploy)

File: .github/workflows/cortex-ci.yml
Action: REMOVE mkdocs build steps

File: .github/workflows/check-dor.yml
Action: REMOVE doc link validation (GitBook handles)
```

**3. Python Scripts:**
```python
Files to Update:
  - src/operations/modules/build_mkdocs_site_module.py → DEPRECATE
  - src/operations/modules/update_mkdocs_index_module.py → DEPRECATE
  - scripts/cortex/record-mkdocs-session.py → DEPRECATE or adapt
  - cortex-brain/mkdocs-refresh-config.yaml → DEPRECATE
```

**4. Test Files:**
```python
Files to Update:
  - tests/test_css_styles.py → REMOVE (no CSS to test)
  - tests/test_css_browser_loading.py → REMOVE
  - tests/docs/test_css_fixes.py → REMOVE
  
New Tests Needed:
  - tests/docs/test_gitbook_links.py (validate external links)
  - tests/docs/test_content_parity.py (ensure all content migrated)
```

### 3.3 Rollback Plan

**Rollback Triggers:**
- GitBook performance issues
- Critical content loss
- User complaints > 50%
- Search functionality broken

**Rollback Steps:**
```bash
# 1. Revert GitHub integration
git revert <migration-commit>

# 2. Restore MkDocs workflow
git checkout CORTEX-2.1 .github/workflows/deploy-docs.yml

# 3. Rebuild MkDocs site
mkdocs build --clean
mkdocs gh-deploy

# 4. Notify users
echo "Rolled back to MkDocs due to: $REASON"
```

**Rollback Decision Matrix:**

| Severity | User Impact | Time to Fix | Decision |
|----------|------------|-------------|----------|
| P0: Critical | >80% broken links | >2 days | ROLLBACK |
| P1: High | >50% complaints | >1 week | ROLLBACK |
| P2: Medium | <30% issues | <3 days | FIX FORWARD |
| P3: Low | Minor styling | <1 day | FIX FORWARD |

### 3.4 Deliverables

- ⏳ Migrated content in GitBook
- ⏳ All links validated
- ⏳ Navigation tested
- ⏳ Rollback plan tested
- ⏳ User acceptance testing (UAT)

---

## 🧹 Phase 4: Deprecation & Cleanup

**Duration:** 1 week  
**Status:** 🔜 NOT STARTED

### 4.1 MkDocs Removal Plan

**Files to Delete:**

```bash
# Documentation infrastructure
rm mkdocs.yml
rm -rf docs/stylesheets/
rm -rf site/  # Build artifacts

# Dependencies (requirements.txt)
- mkdocs>=1.5.0
- mkdocs-material>=9.4.0
- mkdocs-mermaid2-plugin>=1.1.0

# CI/CD
rm .github/workflows/deploy-docs.yml

# Scripts
rm src/operations/modules/build_mkdocs_site_module.py
rm src/operations/modules/update_mkdocs_index_module.py
rm scripts/cortex/record-mkdocs-session.py
rm cortex-brain/mkdocs-refresh-config.yaml

# Tests
rm tests/test_css_styles.py
rm tests/test_css_browser_loading.py
rm tests/docs/test_css_fixes.py
```

**Files to Preserve (Archive):**

```bash
# Move to archive for historical reference
mkdir archive/mkdocs-legacy/
mv mkdocs.yml archive/mkdocs-legacy/
mv docs/stylesheets/ archive/mkdocs-legacy/stylesheets/

# Tag in git
git tag -a mkdocs-final -m "Final MkDocs version before GitBook migration"
git push origin mkdocs-final
```

### 4.2 Dependency Cleanup

**requirements.txt Update:**

```diff
# CORTEX Dependencies
# Phase 0: Tier 0 (Instinct Layer)

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# YAML parsing
PyYAML>=6.0.1

- # Documentation (Phase 0)
- mkdocs>=1.5.0
- mkdocs-material>=9.4.0
- mkdocs-mermaid2-plugin>=1.1.0
+ # Documentation: GitBook (hosted)
+ # No dependencies - GitHub integration handles build

# Phase 1 & 2: SQLite with FTS5 (coming soon)
# ... (rest unchanged)
```

**Impact Analysis:**

| Dependency Removed | Downstream Impact | Mitigation |
|-------------------|-------------------|------------|
| mkdocs | No local doc builds | GitBook web preview |
| mkdocs-material | No theme customization | GitBook theme config |
| mkdocs-mermaid2-plugin | Mermaid diagrams | GitBook native support |

### 4.3 Code Refactoring

**Module Deprecation:**

```python
# src/operations/modules/build_mkdocs_site_module.py
# Mark as deprecated, remove in CORTEX 3.1

import warnings

def build_mkdocs_site():
    warnings.warn(
        "build_mkdocs_site is deprecated. Documentation now hosted on GitBook.",
        DeprecationWarning,
        stacklevel=2
    )
    raise NotImplementedError("MkDocs removed in CORTEX 3.0")
```

**Plugin Registry Update:**

```python
# If any plugins reference MkDocs
# src/plugins/doc_refresh_plugin.py

def execute(self, request: str, context: Dict) -> Dict:
    # Old: Rebuild MkDocs site
    # os.system("mkdocs build --clean")
    
    # New: Trigger GitBook rebuild via API (if needed)
    # GitBook auto-rebuilds on GitHub push, so no action needed
    
    return {
        "status": "success",
        "message": "Documentation auto-rebuilds via GitBook GitHub integration"
    }
```

### 4.4 Documentation Updates

**Files to Update:**

| File | Section | Change |
|------|---------|--------|
| `README.md` | Documentation | Update link from MkDocs → GitBook |
| `.github/copilot-instructions.md` | Setup | Remove MkDocs references |
| `prompts/shared/setup-guide.md` | Installation | Remove `mkdocs serve` instructions |
| `docs/getting-started/installation.md` | Local docs | Update to GitBook links |
| `CONTRIBUTING.md` | Doc contributions | Update workflow (PR → GitBook) |

**Migration Notice:**

```markdown
# docs/MIGRATION-NOTICE.md

# Documentation Migration Notice

**Effective:** 2025-12-01 (CORTEX 3.0 release)

## What Changed?

CORTEX documentation has migrated from MkDocs to GitBook:

**Old:** https://asifhussain60.github.io/CORTEX/  
**New:** https://cortex.gitbook.io/cortex/ (or custom domain)

## Why?

- Better collaboration and versioning
- Professional UI/UX
- Zero local build infrastructure
- Advanced search and analytics

## For Contributors

**Old workflow:**
1. Edit `docs/*.md`
2. Run `mkdocs serve` locally
3. Run `mkdocs build`
4. Push to GitHub
5. GitHub Actions deploys

**New workflow:**
1. Edit `docs/*.md`
2. Push to GitHub
3. GitBook auto-rebuilds (30 seconds)

No local testing needed - GitBook provides live preview.

## For Users

All existing links redirect to GitBook automatically.

Bookmarks still work (301 redirects configured).

## Questions?

See GitBook migration FAQ: [link]
```

### 4.5 Testing & Validation

**Post-Cleanup Tests:**

```bash
# 1. Verify MkDocs fully removed
pytest tests/test_mkdocs_removal.py

# 2. Confirm GitBook integration
curl -I https://cortex.gitbook.io/cortex/
# Expect: 200 OK

# 3. Validate all redirects
python scripts/validate_redirects.py

# 4. Check broken links
python scripts/check_gitbook_links.py

# 5. Performance test
python scripts/benchmark_doc_load_time.py
```

**New Test Suite:**

```python
# tests/docs/test_gitbook_integration.py

def test_gitbook_accessible():
    """GitBook site is online and responsive."""
    response = requests.get("https://cortex.gitbook.io/cortex/")
    assert response.status_code == 200
    assert "CORTEX" in response.text

def test_no_mkdocs_references():
    """No MkDocs references remain in codebase."""
    result = subprocess.run(
        ["grep", "-r", "mkdocs", "src/", "scripts/"],
        capture_output=True
    )
    assert result.returncode != 0, "Found MkDocs references"

def test_all_docs_migrated():
    """All documentation files exist in GitBook."""
    # Fetch GitBook sitemap
    sitemap = fetch_gitbook_sitemap()
    
    # Compare with old docs/ structure
    expected_pages = get_expected_pages()
    
    for page in expected_pages:
        assert page in sitemap, f"Missing: {page}"
```

### 4.6 Deliverables

- ⏳ MkDocs fully removed
- ⏳ Dependencies cleaned
- ⏳ Code refactored
- ⏳ Documentation updated
- ⏳ Tests passing (100%)
- ⏳ Performance validated

---

## 📅 Timeline & Milestones

```
Week 1-2: Phase 1 (Discovery & Analysis)
├── Day 1-3: Content inventory ✅
├── Day 4-5: GitBook setup
├── Day 6-7: Gap analysis
└── Day 8-10: Risk assessment

Week 3-4: Phase 2 (Architecture Design)
├── Day 11-13: Navigation structure
├── Day 14-15: Content mapping
├── Day 16-17: GitHub integration
└── Day 18-20: Theme configuration

Week 5-6: Phase 3 (Migration Execution)
├── Day 21-22: Core content transfer
├── Day 23-24: User guides transfer
├── Day 25-26: API reference transfer
├── Day 27-28: Story & plugins transfer
└── Day 29-30: Testing & validation

Week 7: Phase 4 (Deprecation & Cleanup)
├── Day 31-32: MkDocs removal
├── Day 33-34: Dependency cleanup
├── Day 35: Code refactoring
├── Day 36: Documentation updates
└── Day 37: Final testing

Week 8: Buffer & Launch
├── Day 38-39: User acceptance testing (UAT)
├── Day 40-41: Bug fixes
└── Day 42: CORTEX 3.0 RELEASE 🚀
```

**Critical Milestones:**

| Milestone | Date | Success Criteria | Gate |
|-----------|------|------------------|------|
| M1: GitBook Setup | Week 2 | Account configured, GitHub synced | GO/NO-GO |
| M2: Content Migrated | Week 6 | All 708 files transferred, validated | GO/NO-GO |
| M3: MkDocs Removed | Week 7 | No dependencies, tests pass | GO/NO-GO |
| M4: Launch Ready | Week 8 | UAT passed, rollback tested | LAUNCH |

---

## 🎯 Success Metrics

### Quantitative Metrics

| Metric | Baseline (MkDocs) | Target (GitBook) | Measurement |
|--------|------------------|------------------|-------------|
| **Page Load Time** | 2.3s avg | <1.5s | Google Analytics |
| **Search Speed** | 0.8s | <0.3s | User timing |
| **Build Time** | 12s (local) | <30s (auto) | CI/CD logs |
| **Broken Links** | 5% | 0% | Link checker |
| **User Satisfaction** | N/A | >90% | Survey (1 month) |
| **Documentation PRs** | 2/month | 10/month | GitHub stats |

### Qualitative Metrics

| Dimension | Current State | Target State |
|-----------|--------------|--------------|
| **First Impressions** | "Looks basic" | "Professional & polished" |
| **Navigation** | "Hard to find things" | "Intuitive structure" |
| **Contributor Experience** | "Need local setup" | "Edit in browser" |
| **Versioning** | "Manual branches" | "Native version switching" |
| **Mobile Experience** | "Not optimized" | "Fully responsive" |

### Business Impact

| Impact Area | Expected Outcome |
|-------------|------------------|
| **Developer Onboarding** | 40% faster (better docs = faster ramp-up) |
| **Support Requests** | 30% reduction (better search = self-service) |
| **Contributor Growth** | 5x increase (easier to contribute) |
| **Community Engagement** | 2x increase (better discoverability) |

---

## ⚠️ Risk Assessment

### Risk Matrix

| Risk | Probability | Impact | Severity | Mitigation |
|------|------------|--------|----------|------------|
| **Content loss during migration** | LOW | CRITICAL | HIGH | Automated backup, validation scripts |
| **Broken links (internal)** | MEDIUM | HIGH | MEDIUM | Link checker, redirect mapping |
| **GitBook downtime** | LOW | HIGH | MEDIUM | Rollback plan, cache strategy |
| **User confusion (new UI)** | MEDIUM | MEDIUM | MEDIUM | Migration guide, redirect notices |
| **Search quality degradation** | LOW | MEDIUM | LOW | Test search before launch |
| **Custom CSS loss** | HIGH | LOW | LOW | Brand colors in theme config |
| **Cost overruns (Pro plan)** | LOW | LOW | LOW | Start with free tier |
| **GitHub integration failure** | LOW | CRITICAL | MEDIUM | Test before migration, rollback ready |

### Contingency Plans

**Plan A: GitBook Performance Issues**
- Trigger: Page load >3s consistently
- Action: Enable CDN, optimize images, contact GitBook support
- Timeline: 48 hours to resolve

**Plan B: Content Loss**
- Trigger: Missing pages detected
- Action: Restore from git backup, re-run migration script
- Timeline: 4 hours to restore

**Plan C: User Revolt**
- Trigger: >50% negative feedback
- Action: Survey users, identify issues, fix or rollback
- Timeline: 1 week assessment period

---

## 💰 Cost Analysis

### MkDocs Cost (Current)

| Item | Annual Cost | Notes |
|------|------------|-------|
| Developer time (maintenance) | $2,400 | 2 hours/month @ $100/hour |
| CI/CD compute (GitHub Actions) | $120 | ~10 min/build, 100 builds/year |
| CSS fixes & theme updates | $800 | Ad-hoc work |
| **Total** | **$3,320/year** | - |

### GitBook Cost (Proposed)

| Item | Annual Cost | Notes |
|------|------------|-------|
| GitBook Free Plan | $0 | Open-source, unlimited public docs |
| GitBook Pro Plan (optional) | $960 | $80/month if custom domain needed |
| Developer time (initial setup) | $4,000 | 40 hours @ $100/hour (one-time) |
| Developer time (maintenance) | $600 | 0.5 hours/month @ $100/hour |
| **Total (Free Plan)** | **$600/year recurring** | ($4,000 one-time setup) |
| **Total (Pro Plan)** | **$1,560/year recurring** | ($4,000 one-time setup) |

### Net Savings

| Scenario | Annual Savings | ROI Timeline |
|----------|---------------|--------------|
| **Free Plan** | $2,720/year | 1.5 years (after initial investment) |
| **Pro Plan** | $1,760/year | 2.3 years (after initial investment) |

**Recommendation:** Start with Free Plan, upgrade to Pro only if custom domain is critical.

---

## 📋 Checklist

### Phase 1: Discovery ✅ (IN PROGRESS)

- [x] Content inventory (708 files)
- [x] Investigation architecture analysis (NEW: 2025-11-14)
- [ ] MkDocs dependency map
- [ ] GitBook account setup
- [ ] Gap analysis
- [ ] Risk assessment

### Phase 2: Architecture Design

- [ ] Navigation structure finalized
- [ ] Content mapping complete
- [ ] GitBook space configured
- [ ] Theme customization
- [ ] GitHub integration tested

### Phase 3: Migration Execution

- [ ] Core content transferred
- [ ] User guides transferred
- [ ] API reference transferred
- [ ] Story & plugins transferred
- [ ] All links validated
- [ ] Navigation tested

### Phase 4: Deprecation & Cleanup

- [ ] MkDocs files removed
- [ ] Dependencies cleaned
- [ ] Code refactored
- [ ] Documentation updated
- [ ] Tests passing (100%)
- [ ] Performance validated

### Launch Readiness

- [ ] UAT completed
- [ ] Rollback plan tested
- [ ] Redirect strategy deployed
- [ ] Migration notice published
- [ ] User communication sent
- [ ] Analytics configured

---

## 🎓 Lessons Learned (Post-Migration)

*To be filled after completion*

### What Went Well

- TBD

### What Could Be Improved

- TBD

### Unexpected Challenges

- TBD

### Recommendations for Future Migrations

- TBD

---

## 📞 Stakeholders & Communication

### Key Stakeholders

| Role | Name | Responsibility | Contact |
|------|------|---------------|---------|
| **Project Lead** | Asif Hussain | Overall migration | GitHub @asifhussain60 |
| **Technical Lead** | TBD | Implementation | TBD |
| **Content Lead** | TBD | Documentation review | TBD |
| **QA Lead** | TBD | Testing & validation | TBD |

### Communication Plan

| Audience | Message | Channel | Timing |
|----------|---------|---------|--------|
| **Users** | Migration notice | GitHub README, Discord | 2 weeks before |
| **Contributors** | Workflow changes | CONTRIBUTING.md, email | 1 week before |
| **Community** | FAQ & benefits | Blog post, social media | Launch day |
| **Support Team** | Known issues | Internal docs | 1 week before |

---

## 📚 References

### Documentation

- **GitBook Docs:** https://docs.gitbook.com/
- **GitHub Integration:** https://docs.gitbook.com/integrations/git-sync
- **Migration Guide:** https://docs.gitbook.com/getting-started/import
- **MkDocs Docs:** https://www.mkdocs.org/ (legacy reference)

### Internal Documents

- `mkdocs.yml` - Current MkDocs configuration
- `cortex-brain/CORTEX-2.0-PRODUCTION-READINESS-REPORT.md` - Architecture context
- `prompts/validation/PHASE-3-VALIDATION-REPORT.md` - Modular architecture validation
- `.github/copilot-instructions.md` - Baseline context for Copilot
- `cortex-brain/GUIDED-DEEP-DIVE-PATTERN.md` - Investigation architecture analysis (NEW: 2025-11-14)
- `cortex-brain/GUIDED-DEEP-DIVE-INTEGRATION-POINTS.md` - Integration mapping analysis (NEW: 2025-11-14)

---

**Next Steps:** Proceed with Phase 1 execution (GitBook setup, dependency analysis).

---

*Document Version: 1.0*  
*Last Updated: 2025-11-13*  
*Status: PLANNING PHASE - Awaiting approval to proceed*

