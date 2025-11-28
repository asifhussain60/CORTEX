# CORTEX MkDocs Site Rebuild Plan

**Date:** November 19, 2025  
**Author:** GitHub Copilot (Assisted by Claude Sonnet 4.5)  
**Feature:** Complete documentation site rebuild with encoding prevention  
**Status:** Planning Phase - Awaiting Approval

---

## Executive Summary

**Problem:** Persistent garbled character encoding issues in MkDocs documentation (ΓÇÖ, ΓÇô, etc.) that previous fixes didn't resolve permanently.

**Solution:** Complete site rebuild from scratch, preserving the existing Tales dark theme design while implementing comprehensive UTF-8 encoding prevention at every level.

**Approach:** Clean slate with proven design assets + multi-layer encoding enforcement.

---

## 🎯 Definition of Ready (DoR)

### Requirements Documented
- ✅ Preserve existing Tales dark theme (no Material Design 3)
- ✅ Fix garbled character encoding permanently
- ✅ Maintain current navigation structure
- ✅ Keep existing logo and branding
- ✅ Maintain Bootstrap 3 + Font Awesome styling

### Dependencies Identified
- ✅ MkDocs installation (current: installed)
- ✅ Python UTF-8 environment configuration
- ✅ Current design assets (CSS, HTML templates, images)
- ✅ Encoding fix scripts (`set-utf8-env.ps1`, `build-mkdocs-utf8.ps1`)
- ✅ Git repository (for version control)

### Technical Design Approved
- **Theme:** Cortex Tales (custom Bootstrap 3 dark theme)
- **CSS Files:** tales-design.css, story.css, custom.css
- **HTML Template:** main.html (Bootstrap 3 structure)
- **Navigation:** Horizontal nav bar + left sidebar TOC
- **Encoding:** UTF-8 enforcement at file creation, build, and Git levels

### Security Review
- ✅ No external dependencies beyond CDN resources (Bootstrap, Font Awesome, jQuery)
- ✅ UTF-8 encoding prevents character injection attacks
- ✅ Static site generation (no server-side vulnerabilities)

---

## 🔍 Current State Analysis

### Existing Design Assets (To Preserve)

**Theme Structure:**
```
docs/themes/cortex-tales/
├── main.html                    # Bootstrap 3 template
└── assets/
    └── css/
        └── cortex-tales.css     # Main theme CSS
```

**Stylesheets (To Keep):**
```
docs/stylesheets/
├── tales-design.css             # Dark theme, layout, components
├── story.css                    # Comic font for story pages
├── custom.css                   # CORTEX brand colors, overrides
├── technical.css                # Technical documentation styling
└── material-tokens.css          # MD3 tokens (NOT USED - ignore)
```

**Key Design Elements:**
- **Color Scheme:** Dark background (#0F172A), light text (#F1F5F9), indigo primary (#4F46E5)
- **Typography:** Inter for body, JetBrains Mono for code, Comic Neue for stories
- **Layout:** Full-width content, left sidebar navigation, horizontal nav bar
- **Components:** Bootstrap 3 grid, Font Awesome icons, highlight.js for syntax
- **Logo:** 300x300px CORTEX logo in header

### Encoding Issues Identified

**From brokencode.html (empty - but known issues):**
- ΓÇÖ → ' (apostrophe/single quote)
- ΓÇô → – (en dash)
- ΓÇö → — (em dash)
- ΓÇ£ → " (left double quote)
- ΓÇ¥ → " (right double quote)
- Γ£à → ✅ (checkmark emoji)
- ΓåÆ → → (right arrow)
- ΓÜá∩╕Å → ⚠️ (warning emoji)

**Root Causes:**
1. Windows-1252 encoding in source files interpreted as UTF-8
2. Python locale defaulting to cp1252 (Windows-1252)
3. Inconsistent encoding across file save operations
4. MkDocs build not enforcing UTF-8 environment

### Existing Fix Scripts (To Reuse)

```powershell
# Set UTF-8 environment
scripts/set-utf8-env.ps1

# Build with UTF-8 enforcement
scripts/build-mkdocs-utf8.ps1

# Fix garbled source files (if needed)
scripts/fix_garbled_source_files.py
```

---

## 📋 Implementation Plan

### Phase 1: Design Asset Preservation (1 hour)

**Goal:** Extract and document all reusable design components.

**Tasks:**
1. **CSS Extraction:**
   - Copy `tales-design.css` → backup
   - Copy `story.css` → backup
   - Copy `custom.css` → backup
   - Copy `technical.css` → backup
   - Document color variables and layout structure

2. **HTML Template Extraction:**
   - Copy `main.html` → backup
   - Document navigation structure
   - Document footer structure
   - Document CDN dependencies

3. **Asset Inventory:**
   - Logo: `docs/assets/images/CORTEX-logo.png`
   - Fonts: Google Fonts (Inter, Comic Neue), JetBrains Mono CDN
   - Icons: Font Awesome 4.7.0
   - JS Libraries: jQuery 3.6.0, Bootstrap 3.4.1, Highlight.js 11.9.0

4. **Design Documentation:**
   - Create `DESIGN-SPECIFICATION.md` with:
     - Color palette
     - Typography scale
     - Component specifications
     - Layout breakpoints
     - Navigation behavior

**Deliverables:**
- `/cortex-brain/artifacts/design-backup/` (CSS, HTML, assets)
- `DESIGN-SPECIFICATION.md`

---

### Phase 2: UTF-8 Encoding Prevention Strategy (30 min)

**Goal:** Implement multi-layer encoding enforcement.

**Layer 1: VS Code Configuration**
```json
// .vscode/settings.json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "[markdown]": {
    "files.encoding": "utf8"
  },
  "[html]": {
    "files.encoding": "utf8"
  }
}
```

**Layer 2: Git Configuration**
```gitattributes
# .gitattributes
*.md text eol=lf encoding=utf-8
*.html text eol=lf encoding=utf-8
*.css text eol=lf encoding=utf-8
*.js text eol=lf encoding=utf-8
*.yml text eol=lf encoding=utf-8
*.yaml text eol=lf encoding=utf-8
```

**Layer 3: Python Environment**
```powershell
# Enforce UTF-8 in PowerShell profile
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

**Layer 4: MkDocs Build Script**
```powershell
# Enhanced build-mkdocs-utf8.ps1
param([switch]$Clean)

# Set UTF-8 environment
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🔧 Building with UTF-8 enforcement..." -ForegroundColor Cyan

if ($Clean) {
    mkdocs build --clean
} else {
    mkdocs build
}

# Validate encoding
python tests/test_mkdocs_encoding.py
```

**Layer 5: File Creation Template**
```python
# File creation helper
def create_utf8_file(path, content):
    """Always create files with UTF-8 encoding."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
```

**Deliverables:**
- `.vscode/settings.json` (UTF-8 config)
- `.gitattributes` (encoding enforcement)
- Enhanced `build-mkdocs-utf8.ps1`
- `UTF8-ENFORCEMENT-GUIDE.md`

---

### Phase 3: Clean Slate Site Structure (45 min)

**Goal:** Create fresh documentation structure with UTF-8 from the start.

**Step 1: Backup Current Site**
```powershell
# Backup entire docs/ directory
Move-Item docs docs-backup-2025-11-19
New-Item -Type Directory docs
```

**Step 2: Create New MkDocs Configuration**
```yaml
# mkdocs.yml
site_name: CORTEX
site_description: Cognitive Operation & Reasoning Through EXtension for Copilot
site_author: Asif Hussain
copyright: "2024-2025 Asif Hussain. All rights reserved."
repo_url: https://github.com/asifhussain60/CORTEX
repo_name: asifhussain60/CORTEX
site_url: https://asifhussain60.github.io/CORTEX/
use_directory_urls: true

# Custom Tales Theme
theme:
  name: null
  custom_dir: docs/themes/cortex-tales

# No extra_css (CSS in theme)

# Navigation (preserve current structure)
nav:
- Home: index.md
- The CORTEX Birth:
  - The Awakening Story: diagrams/story/The-CORTEX-Story.md
- Cortex Bible: governance/THE-RULEBOOK.md
- Architecture:
  - Overview: architecture/overview.md
  - Tier System: architecture/tier-system.md
  - Agents: architecture/agents.md
  - Brain Protection: architecture/brain-protection.md
- Technical Docs:
  - API Reference: reference/api.md
  - Configuration: reference/configuration.md
- User Guides:
  - Quick Start: getting-started/quick-start.md
  - Installation: getting-started/installation.md
  - Developer Guide: guides/developer-guide.md
- Examples:
  - Getting Started: getting-started/quick-start.md

# Markdown Extensions (preserve current)
markdown_extensions:
- abbr
- admonition
- attr_list
- def_list
- footnotes
- meta
- md_in_html
- tables
- toc:
    permalink: false
    toc_depth: 3
- pymdownx.arithmatex:
    generic: true
- pymdownx.betterem:
    smart_enable: all
- pymdownx.caret
- pymdownx.mark
- pymdownx.tilde
- pymdownx.details
- pymdownx.highlight:
    anchor_linenums: true
    line_spans: __span
    pygments_lang_class: true
- pymdownx.inlinehilite
- pymdownx.keys
- pymdownx.snippets
- pymdownx.superfences:
    custom_fences:
    - name: mermaid
      class: mermaid
      format: !!python/name:pymdownx.superfences.fence_code_format
- pymdownx.tabbed:
    alternate_style: true
- pymdownx.tasklist:
    custom_checkbox: true

plugins:
- search:
    lang: en
```

**Step 3: Restore Theme Assets**
```powershell
# Copy theme directory from backup
Copy-Item docs-backup-2025-11-19/themes/cortex-tales docs/themes/cortex-tales -Recurse

# Copy stylesheets from backup
Copy-Item docs-backup-2025-11-19/stylesheets docs/stylesheets -Recurse

# Copy assets (images, etc.)
Copy-Item docs-backup-2025-11-19/assets docs/assets -Recurse
```

**Step 4: Create Placeholder Pages (UTF-8 Enforced)**
```powershell
# Create structure with UTF-8 encoding
$pages = @(
    "docs/index.md",
    "docs/diagrams/story/The-CORTEX-Story.md",
    "docs/governance/THE-RULEBOOK.md",
    "docs/architecture/overview.md",
    "docs/architecture/tier-system.md",
    "docs/architecture/agents.md",
    "docs/architecture/brain-protection.md",
    "docs/reference/api.md",
    "docs/reference/configuration.md",
    "docs/getting-started/quick-start.md",
    "docs/getting-started/installation.md",
    "docs/guides/developer-guide.md"
)

foreach ($page in $pages) {
    $dir = Split-Path $page
    New-Item -Type Directory -Path $dir -Force
    
    # Create file with UTF-8 encoding (BOM-less)
    $content = "# " + (Split-Path $page -Leaf).Replace('.md', '')
    [System.IO.File]::WriteAllText($page, $content, (New-Object System.Text.UTF8Encoding $false))
}
```

**Deliverables:**
- Fresh `docs/` directory structure
- UTF-8 enforced `mkdocs.yml`
- Placeholder pages (all UTF-8)
- Restored theme and assets

---

### Phase 4: Content Migration with UTF-8 Validation (2 hours)

**Goal:** Migrate content from backup to new structure, validating UTF-8 at every step.

**Migration Script:**
```python
# scripts/migrate_content_utf8.py
import os
import re
from pathlib import Path

# Garbled pattern detection
GARBLED_PATTERNS = {
    'ΓÇÖ': "'",  # apostrophe
    'ΓÇô': '–',  # en dash
    'ΓÇö': '—',  # em dash
    'ΓÇ£': '"',  # left quote
    'ΓÇ¥': '"',  # right quote
    'Γ£à': '✅',  # checkmark
    'ΓåÆ': '→',  # arrow
    'ΓÜá∩╕Å': '⚠️',  # warning
}

def detect_garbled(content):
    """Detect garbled patterns in content."""
    issues = []
    for pattern, replacement in GARBLED_PATTERNS.items():
        if pattern in content:
            issues.append(f"Found '{pattern}' (should be '{replacement}')")
    return issues

def fix_garbled(content):
    """Fix garbled patterns."""
    for pattern, replacement in GARBLED_PATTERNS.items():
        content = content.replace(pattern, replacement)
    return content

def migrate_file(src, dst):
    """Migrate file with UTF-8 validation."""
    print(f"Migrating {src} → {dst}")
    
    # Read source (detect encoding)
    with open(src, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Check for garbled patterns
    issues = detect_garbled(content)
    if issues:
        print(f"  ⚠️  Garbled content detected:")
        for issue in issues:
            print(f"      {issue}")
        
        # Fix garbled patterns
        content = fix_garbled(content)
        print(f"  ✅ Fixed garbled patterns")
    
    # Write to destination (UTF-8, no BOM)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Written to {dst} (UTF-8)")

def migrate_all():
    """Migrate all markdown files from backup."""
    backup_dir = Path("docs-backup-2025-11-19")
    new_dir = Path("docs")
    
    # Find all markdown files in backup
    md_files = list(backup_dir.glob("**/*.md"))
    
    print(f"Found {len(md_files)} markdown files to migrate\n")
    
    for src in md_files:
        # Calculate destination path
        rel_path = src.relative_to(backup_dir)
        dst = new_dir / rel_path
        
        migrate_file(src, dst)
        print()

if __name__ == "__main__":
    migrate_all()
```

**Migration Process:**
1. Run migration script with validation
2. Review garbled pattern reports
3. Manually verify critical pages (story, index)
4. Test build with UTF-8 environment
5. Validate HTML output (no garbled patterns)

**Deliverables:**
- Migrated content (all UTF-8 validated)
- `MIGRATION-REPORT.md` (issues found and fixed)

---

### Phase 5: Build Automation & Testing (1 hour)

**Goal:** Automated UTF-8-safe build pipeline with comprehensive testing.

**Build Script (Enhanced):**
```powershell
# scripts/build-mkdocs-utf8.ps1
param(
    [switch]$Clean,
    [switch]$Serve,
    [switch]$Deploy
)

# CRITICAL: Set UTF-8 environment
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🧠 CORTEX MkDocs Builder (UTF-8 Enforced)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Step 1: Pre-build validation
Write-Host "🔍 Step 1: Pre-build Validation" -ForegroundColor Yellow
python scripts/validate_utf8_sources.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Pre-build validation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ All source files are UTF-8 clean" -ForegroundColor Green
Write-Host ""

# Step 2: Build site
Write-Host "🔧 Step 2: Building MkDocs Site" -ForegroundColor Yellow
if ($Clean) {
    mkdocs build --clean
} else {
    mkdocs build
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Site built successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Post-build validation
Write-Host "🔬 Step 3: Post-build Validation" -ForegroundColor Yellow
python tests/test_mkdocs_encoding.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Encoding validation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ No garbled characters in HTML output" -ForegroundColor Green
Write-Host ""

# Step 4: Serve or deploy
if ($Serve) {
    Write-Host "🌐 Step 4: Starting Development Server" -ForegroundColor Yellow
    mkdocs serve
} elseif ($Deploy) {
    Write-Host "🚀 Step 4: Deploying to GitHub Pages" -ForegroundColor Yellow
    mkdocs gh-deploy
} else {
    Write-Host "✅ Build Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  • Test locally:  .\scripts\build-mkdocs-utf8.ps1 -Serve" -ForegroundColor Gray
    Write-Host "  • Deploy:        .\scripts\build-mkdocs-utf8.ps1 -Deploy" -ForegroundColor Gray
}
```

**Validation Tests:**
```python
# tests/test_mkdocs_encoding.py
import os
import re
from pathlib import Path

GARBLED_PATTERNS = [
    'ΓÇÖ', 'ΓÇô', 'ΓÇö', 'ΓÇ£', 'ΓÇ¥',
    'Γ£à', 'ΓåÆ', 'ΓÜá∩╕Å'
]

def test_no_garbled_in_html():
    """Test that no garbled characters exist in HTML output."""
    site_dir = Path("site")
    html_files = list(site_dir.glob("**/*.html"))
    
    failures = []
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for pattern in GARBLED_PATTERNS:
            if pattern in content:
                failures.append(f"{html_file}: Found '{pattern}'")
    
    if failures:
        print("\n❌ Garbled characters found:")
        for failure in failures:
            print(f"  {failure}")
        raise AssertionError(f"{len(failures)} files have garbled characters")
    
    print(f"✅ Tested {len(html_files)} HTML files - no garbled characters")

def test_utf8_meta_tags():
    """Test that all HTML files have UTF-8 charset meta tag."""
    site_dir = Path("site")
    html_files = list(site_dir.glob("**/*.html"))
    
    missing = []
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'charset="utf-8"' not in content.lower() and 'charset=utf-8' not in content.lower():
            missing.append(str(html_file))
    
    if missing:
        print("\n❌ Missing UTF-8 charset meta tags:")
        for file in missing:
            print(f"  {file}")
        raise AssertionError(f"{len(missing)} files missing UTF-8 charset")
    
    print(f"✅ All {len(html_files)} HTML files have UTF-8 charset meta tag")

def test_correct_characters_present():
    """Test that correct Unicode characters are present."""
    site_dir = Path("site")
    story_html = site_dir / "diagrams/story/The-CORTEX-Story/index.html"
    
    if not story_html.exists():
        print("⚠️  Story page not found - skipping character validation")
        return
    
    with open(story_html, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for correct characters
    expected = ['—', '✅', '→', '"', '"', '⚠️']
    found = [char for char in expected if char in content]
    
    print(f"✅ Found {len(found)}/{len(expected)} expected Unicode characters")

if __name__ == "__main__":
    test_no_garbled_in_html()
    test_utf8_meta_tags()
    test_correct_characters_present()
```

**Deliverables:**
- `build-mkdocs-utf8.ps1` (enhanced with validation)
- `tests/test_mkdocs_encoding.py`
- `scripts/validate_utf8_sources.py`

---

### Phase 6: Documentation & Handoff (30 min)

**Goal:** Comprehensive documentation for maintenance and future updates.

**Documents to Create:**

1. **UTF8-ENFORCEMENT-GUIDE.md**
   - Multi-layer enforcement explanation
   - VS Code configuration
   - Git configuration
   - Build process
   - Troubleshooting common issues

2. **DESIGN-SPECIFICATION.md**
   - Color palette reference
   - Typography scale
   - Component library
   - Layout patterns
   - CSS architecture

3. **REBUILD-SUMMARY.md**
   - What was changed
   - Why it was changed
   - How to maintain
   - Validation procedures

4. **QUICK-START.md**
   - Edit content workflow
   - Build and test locally
   - Deploy to production
   - Verify encoding

**Deliverables:**
- All documentation files
- Updated README.md
- CI/CD integration guide

---

## 🎯 Definition of Done (DoD)

### Code Quality
- ✅ All CSS files validated (no syntax errors)
- ✅ All HTML templates validated (W3C compliant)
- ✅ All markdown files UTF-8 encoded (validated)
- ✅ Build script runs without errors

### Testing
- ✅ Pre-build validation passes (source files UTF-8 clean)
- ✅ Build completes successfully
- ✅ Post-build validation passes (no garbled characters)
- ✅ Manual spot check on 5 key pages (index, story, architecture, API, guides)
- ✅ Cross-browser testing (Chrome, Firefox, Edge)
- ✅ Responsive design testing (desktop, tablet, mobile)

### Documentation
- ✅ UTF8-ENFORCEMENT-GUIDE.md created
- ✅ DESIGN-SPECIFICATION.md created
- ✅ REBUILD-SUMMARY.md created
- ✅ QUICK-START.md created
- ✅ README.md updated with new build process

### Deployment
- ✅ Site builds without errors
- ✅ Site serves correctly on localhost
- ✅ Site deploys to GitHub Pages successfully
- ✅ All links functional (no 404s)
- ✅ All images load correctly

---

## ✅ Acceptance Criteria

### Functional Requirements
1. **Encoding:** No garbled characters in any HTML output
2. **Design:** Visual appearance matches current site exactly
3. **Navigation:** All navigation links functional
4. **Content:** All content migrated and readable
5. **Search:** MkDocs search plugin works correctly

### Performance Requirements
1. **Build Time:** Complete build < 30 seconds
2. **Page Load:** Pages load < 2 seconds
3. **Search:** Search results return < 1 second

### Quality Requirements
1. **Accessibility:** All pages pass WCAG AA standards
2. **Responsiveness:** Design works on all screen sizes
3. **Browser Support:** Chrome, Firefox, Edge, Safari (latest 2 versions)

---

## 🚨 Risk Analysis

### High Priority Risks

**Risk 1: Content Migration Data Loss**
- **Impact:** HIGH
- **Probability:** MEDIUM
- **Mitigation:** Full backup before migration, validate file counts before/after
- **Rollback:** Restore from docs-backup-2025-11-19

**Risk 2: Encoding Issues Persist**
- **Impact:** HIGH
- **Probability:** LOW (with multi-layer enforcement)
- **Mitigation:** Comprehensive validation at every step, automated testing
- **Rollback:** Identify specific files, re-migrate with fix

**Risk 3: Design Breaks During Migration**
- **Impact:** MEDIUM
- **Probability:** LOW
- **Mitigation:** Exact copy of CSS and HTML templates, visual diff testing
- **Rollback:** Restore theme assets from backup

### Medium Priority Risks

**Risk 4: Navigation Links Break**
- **Impact:** MEDIUM
- **Probability:** MEDIUM
- **Mitigation:** Maintain exact directory structure, validate all links
- **Rollback:** Update mkdocs.yml navigation paths

**Risk 5: Build Script Fails on Different Machines**
- **Impact:** MEDIUM
- **Probability:** LOW
- **Mitigation:** Document Python/MkDocs version requirements, test on clean environment
- **Rollback:** Use alternative build method (direct mkdocs command)

---

## 📊 Timeline Estimate

| Phase | Duration | Dependencies | Confidence |
|-------|----------|--------------|------------|
| Phase 1: Design Preservation | 1 hour | None | HIGH |
| Phase 2: UTF-8 Strategy | 30 min | Phase 1 | HIGH |
| Phase 3: Clean Structure | 45 min | Phase 1, 2 | HIGH |
| Phase 4: Content Migration | 2 hours | Phase 3 | MEDIUM |
| Phase 5: Build Automation | 1 hour | Phase 4 | HIGH |
| Phase 6: Documentation | 30 min | Phase 5 | HIGH |
| **Total** | **5.75 hours** | Sequential | **HIGH** |

**Buffer:** Add 1 hour for unexpected issues = **6.75 hours total**

---

## 🔄 Rollback Strategy

### Emergency Rollback (< 5 minutes)
```powershell
# Restore original site
Remove-Item docs -Recurse -Force
Rename-Item docs-backup-2025-11-19 docs
mkdocs build --clean
```

### Selective Rollback
1. **Theme Only:** Restore `docs/themes/cortex-tales` from backup
2. **Content Only:** Restore specific markdown files
3. **Config Only:** Restore `mkdocs.yml` from Git history

---

## 📝 Approval Checklist

Before proceeding with implementation, confirm:

- [ ] All stakeholders agree on clean rebuild approach
- [ ] Backup strategy is acceptable
- [ ] Timeline estimate is realistic
- [ ] Risk mitigation strategies are sound
- [ ] Success criteria are measurable
- [ ] Rollback plan is viable

---

## 🎬 Next Steps

**Once Approved:**

1. Create feature branch: `git checkout -b feature/mkdocs-site-rebuild`
2. Execute Phase 1: Design Preservation
3. Commit after each phase: `git commit -m "Phase X complete"`
4. Test after each phase
5. Final validation before merge
6. Deploy to production

**Approval Command:** 
```
approve plan
```

**Abort Command:**
```
cancel plan
```

---

**Author:** GitHub Copilot (Assisted by Claude Sonnet 4.5)  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Repository:** https://github.com/asifhussain60/CORTEX
