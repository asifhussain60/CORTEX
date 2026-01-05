# CORTEX Documentation Manifests

**Generated:** 2026-01-05  
**Purpose:** Comprehensive documentation structure and relationship manifests for validation scripts and cortex-docs prompt  
**Generator:** `scripts/generate-docs-manifest.py`

---

## 📊 Overview

- **Total Pages:** 324
  - Level 0 (Root): 119 pages
  - Level 1 (Hubs): 12 pages
  - Level 2 (Detail): 193 pages
- **Total Links:** 1,108 navigation links
- **Categories:** 12 Level 1 categories

---

## 📁 Manifest Files

### 1. `site-structure-manifest.yaml`

**Purpose:** Complete hierarchical structure of all documentation pages

**Contents:**
- Metadata (counts, generation date)
- Level 0 pages (root-level pages)
- Level 1 pages (hub/index pages)
- Level 2 pages (detail/child pages)

**Use Cases:**
- Site-wide navigation validation
- Completeness checks
- Level detection algorithms

---

### 2. `level1-pages-manifest.yaml`

**Purpose:** All Level 1 hub pages with metadata

**Contents:**
- 12 hub pages with:
  - File path
  - Title
  - Description
  - Category
  - Outbound link count

**Categories:**
1. `architecture` - 4-Tier Brain System
2. `features` - Core capabilities
3. `getting-started` - Setup guides
4. `knowledge` - Best practices
5. `learning-paths` - Interactive tutorials
6. `lens` - Analysis dashboard
7. `orchestrators` - Workflow coordinators
8. `security` - Security guides
9. `story` - Project narrative
10. `sts` - STS integration
11. `token-optimization` - Cost savings
12. `toolkit-manager` - Tool management

**Use Cases:**
- Level 1 glassmorphism standardization (Phase 16c)
- Hub page validation
- Navigation menu generation
- Pattern C52 (Level 1 Hero Header) application

---

### 3. `level2-pages-manifest.yaml`

**Purpose:** All Level 2 detail pages grouped by category

**Contents:**
- 193 detail pages organized by parent category
- Each page includes:
  - File path
  - Title
  - Description (truncated)
  - Outbound link count

**Use Cases:**
- Level 2 batch processing (Phase 16d)
- Category-based navigation
- Parent-child relationship validation

---

### 4. `navigation-links-manifest.yaml`

**Purpose:** All navigation links across entire documentation

**Contents:**
- 1,108 links with:
  - Source file path
  - Target href
  - Source level (0, 1, or 2)
  - Source category

**Use Cases:**
- Broken link detection
- Parent-child link validation
- Breadcrumb validation
- `fix-parent-child-links.ps1` script generation

---

## 🔧 Usage in Scripts

### Validation Scripts

```powershell
# Load manifest
$manifest = Get-Content "manifests/level1-pages-manifest.yaml" | ConvertFrom-Yaml

# Iterate Level 1 pages
foreach ($page in $manifest.pages) {
    Write-Host "Validating: $($page.file)"
    # Apply Pattern C52, C50, C51, C53 validations
}
```

### cortex-docs Prompt

The prompt should reference these manifests for:
- Holistic standardization (find all pages in scope)
- Pattern application (Level 1 vs Level 2 detection)
- Link integrity validation
- Completeness checks

**Auto-Standardization Algorithm:**
```python
def detect_standardization_scope(current_page: str) -> List[str]:
    """Use manifest to find similar pages"""
    manifest = load_yaml("manifests/level1-pages-manifest.yaml")
    
    # If current page is Level 1, find all Level 1 pages
    if is_level1(current_page):
        return [p['file'] for p in manifest['pages']]
    
    # If Level 2, find pages in same category
    category = get_category(current_page)
    level2_manifest = load_yaml("manifests/level2-pages-manifest.yaml")
    return level2_manifest['pages_by_category'][category]
```

---

## 🔄 Regeneration

**When to regenerate:**
- After adding/removing pages
- After restructuring navigation
- Before Phase 16 standardization work
- After major content updates

**How to regenerate:**
```powershell
python scripts/generate-docs-manifest.py
```

**Validation:**
- Check `metadata.total_pages` matches expected count
- Verify all Level 1 categories present
- Confirm navigation links count reasonable

---

## 📊 Statistics

### Level 1 Pages (12 Hubs)

| Category | File | Link Count |
|----------|------|------------|
| architecture | architecture/index.html | 4 |
| features | features/index.html | 12 |
| getting-started | getting-started/index.html | 4 |
| knowledge | knowledge/index.html | 55 |
| learning-paths | learning-paths/index.html | 13 |
| lens | lens/index.html | 4 |
| orchestrators | orchestrators/index.html | 11 |
| security | security/index.html | TBD |
| story | story/index.html | TBD |
| sts | sts/index.html | TBD |
| token-optimization | token-optimization/index.html | TBD |
| toolkit-manager | toolkit-manager/index.html | TBD |

### Level 2 Pages by Category

| Category | Page Count |
|----------|------------|
| archives | 171 |
| cortex-lens-output | 6 |
| design-system | 2 |
| development | 1 |
| examples | 2 |
| governance | 1 |
| reports | 3 |
| toolkit-manager | 7 |

---

## 🎯 Integration with SNOWBALL Strategy

**Phase 16c (Level 1 Orchestrators):**
- Use `level1-pages-manifest.yaml` to find `orchestrators/index.html`
- Validate against patterns C50, C51, C52, C53

**Phase 16d (Level 2 Detail Pages):**
- Use `level2-pages-manifest.yaml` to batch process by category
- Apply learned patterns at 0.5h/page velocity

**Link Integrity:**
- Use `navigation-links-manifest.yaml` to generate `fix-parent-child-links.ps1`
- Validate all parent links (← Back to)
- Validate all child links (→ View)
- Validate breadcrumbs

---

## 📚 Related Files

- **Generator Script:** `scripts/generate-docs-manifest.py`
- **Usage Guide:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/CORTEX-DOCS-USAGE-GUIDE.md`
- **SNOWBALL Strategy:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/SNOWBALL-STRATEGY.md`
- **Validation Scripts:** `cortex-toolkit/*.ps1`

---

**Maintained By:** CORTEX Planning System v5  
**Last Updated:** 2026-01-05
