# CORTEX Documentation Architecture - Optimized

**Date:** 2026-01-21  
**Status:** ✅ Implemented  
**Governance:** TIER 0 Compliant

---

## Problem Statement

**Original Issue:**
- Redundant documentation folders (`docs/` and `site/`)
- Asset duplication across sites
- Poor organization of shared resources

**Goal:**
- Single source of truth for assets
- Automatic asset distribution to built sites
- Minimal folder redundancy

---

## Solution Implemented

### Architecture

```
Repository Root
├── assets/                     ← CENTRALIZED ASSETS
│   ├── images/
│   │   ├── CORTEX-logo-64.png
│   │   ├── CORTEX-logo-128.png
│   │   ├── cortex-logo-200.png
│   │   ├── CORTEX-logo-512.png
│   │   ├── CORTEX-logo.png
│   │   ├── cortex-logo.svg
│   │   └── cortex-logo-white.svg
│   ├── README.md
│   └── INDEX.md
│
├── docs/                       ← SOURCE MARKDOWN
│   ├── 0-README.md
│   ├── 01-getting-started/
│   ├── 02-architecture/
│   ├── 03-api-reference/
│   ├── 04-guides/
│   ├── 05-reference/
│   ├── 06-tutorials/
│   ├── 07-contributing/
│   ├── _archive/
│   ├── _diagrams/
│   ├── _manifests/
│   ├── _unsorted/
│   └── _hooks/
│       └── copy_assets.py      ← POST-BUILD HOOK
│
├── _build/ (git-ignored)       ← BUILD ARTIFACTS
│   └── site/                   ← GENERATED OUTPUT
│       ├── index.html
│       ├── assets/             ← AUTO-COPIED
│       │   └── images/ (7 files)
│       └── (other generated files)
│
├── cortex-gitpages/            ← STATIC SITE (if used)
│   └── _archive/
│
└── mkdocs.yml                  ← WITH HOOK CONFIG
```

---

## Key Components

### 1. **Central Assets** (`assets/`)
- **7 Logo Files:** PNG (5 variants) + SVG (2 variants)
- **Single Source:** One location for all static assets
- **No Duplication:** Files only exist once in repository

### 2. **MkDocs Build Hook** (`docs/_hooks/copy_assets.py`)
```python
def on_post_build(config):
    """Auto-copies assets/ to _build/site/assets/ after build"""
```

**What it does:**
- Runs after `mkdocs build` completes
- Copies entire `assets/` folder to `_build/site/assets/`
- Ensures built site has access to all assets
- No manual intervention needed

### 3. **MkDocs Configuration** (`mkdocs.yml`)
```yaml
hooks:
  - docs/_hooks/copy_assets.py
```

---

## Usage

### Accessing Assets in Markdown

**From `docs/` (source):**
```markdown
![Logo](../assets/images/cortex-logo.svg)
```

**In MkDocs (will be in site):**
```markdown
![Logo](../assets/images/cortex-logo.svg)
```

**From `cortex-gitpages/` (if used):**
```html
<img src="../assets/images/CORTEX-logo-64.png" alt="Logo">
```

### Building Documentation

```bash
cd d:\PROJECTS\CORTEX

# Build with automatic asset copying
mkdocs build

# Serve locally
mkdocs serve
```

**Result:**
```
✅ Assets copied: assets/ → site/assets/
```

---

## Git Management

### What's Committed
- ✅ `assets/` - Central asset repository
- ✅ `docs/` - All source documentation
- ✅ `docs/_hooks/` - Build automation scripts

### What's Ignored
- ❌ `site/` - Regenerated on every build
- ❌ `docs/_site/` - Not used (MkDocs prevents nesting)

**`.gitignore` entries:**
```
docs/_site/
site/
```

---

## Advantages

| Aspect | Benefit |
|--------|---------|
| **Single Source** | Assets only exist in `assets/`, not duplicated |
| **Auto-Distribution** | Hook automatically copies to built site |
| **No Manual Steps** | Build process handles asset management |
| **Clean Repository** | Generated files ignored, not committed |
| **Scalable** | Easy to add new assets to central location |
| **Multi-Site Ready** | Works with docs/, cortex-gitpages/, any site |

---

## Governance Compliance

✅ **TIER 0 Rules Applied:**
- **CORE-005:** No hardcoded paths (relative references via hook)
- **CORE-001:** Clean, organized structure
- **CORE-029:** Documented and maintained
- **Infrastructure:** Deterministic builds (same input = same output)

---

## Troubleshooting

### Hook Not Running?
```bash
# Verify Python can access hook
python -c "import docs._hooks.copy_assets"
```

### Assets Not in Site?
```bash
# Check if assets folder exists
ls -la assets/

# Rebuild
mkdocs clean
mkdocs build
```

### Git Showing site/ as Changes?
```bash
# Ensure site/ is in .gitignore
git check-ignore site/
# Should output: site/

# Remove from tracking
git rm --cached -r site/
```

---

## Migration Path

This solution replaces the previous architecture:
- ❌ Old: Duplicated assets in `docs/` and `site/`
- ❌ Old: Multiple documentation folders
- ✅ New: Single `assets/` with automatic distribution
- ✅ New: Clean separation of source and built output

---

## Next Steps

1. ✅ Central `assets/` created
2. ✅ All 7 logo files migrated
3. ✅ Build hook implemented
4. ✅ MkDocs configured
5. 🔄 Optional: Set up CI/CD to auto-build and deploy
6. 🔄 Optional: Create additional asset categories (styles, fonts, etc.)

---

**Created By:** CORTEX System Agent  
**Last Updated:** 2026-01-21  
**Status:** ✅ Production Ready
