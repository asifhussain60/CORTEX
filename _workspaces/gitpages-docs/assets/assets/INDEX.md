# CORTEX Assets Index

## Central Asset Repository

**Location:** `/assets/`  
**Status:** ✅ Active and Centralized  
**Last Updated:** 2026-01-21

---

## Asset Inventory

### Logo Assets (7 files)

#### PNG Variants
- **`CORTEX-logo-64.png`** (6.4 KB)
  - Use: Favicon, browser tabs, small icons
  - Dimensions: 64×64 pixels
  - Source: Archive CORTEX-5.5 branch

- **`CORTEX-logo-128.png`** (21.6 KB)
  - Use: Thumbnail displays, social media
  - Dimensions: 128×128 pixels
  - Source: Archive CORTEX-5.5 branch

- **`cortex-logo-200.png`** (21.6 KB)
  - Use: Medium-sized displays
  - Dimensions: 200×200 pixels
  - Source: Archive CORTEX-5.5 branch

- **`CORTEX-logo-512.png`** (292 KB)
  - Use: High-resolution displays, print
  - Dimensions: 512×512 pixels
  - Source: Archive CORTEX-5.5 branch

- **`CORTEX-logo.png`** (1813.6 KB)
  - Use: Full resolution source
  - Dimensions: Full size
  - Source: Archive CORTEX-5.5 branch

#### SVG Variants (Recommended for Web)
- **`cortex-logo.svg`** (2.4 KB)
  - Use: Scalable, responsive web displays
  - Colors: Standard (cyan/green gradient)
  - Dimensions: Scalable
  - Source: Archive CORTEX-4.0 branch

- **`cortex-logo-white.svg`** (2.5 KB)
  - Use: Dark mode displays, inverted backgrounds
  - Colors: White variant
  - Dimensions: Scalable
  - Source: Archive CORTEX-4.0 branch

---

## Access Patterns

### From Documentation (`docs/`)
```markdown
![Logo](../../assets/images/cortex-logo.svg)
```

### From Git Pages (`cortex-gitpages/`)
```html
<img src="../assets/images/CORTEX-logo-64.png" alt="CORTEX">
```

### From Root Directory
```
./assets/images/{filename}
```

---

## Migration History

| Date | Action | Source | Destination |
|------|--------|--------|-------------|
| 2026-01-21 | Moved PNG files | `docs/` | `assets/images/` |
| 2026-01-21 | Moved SVG files | `docs/` | `assets/images/` |
| 2026-01-21 | Created central repo | - | `assets/` |

---

## Governance Compliance

✅ **TIER 0 Rules Applied:**
- Central single-source location (CORE-005: no hardcoded paths)
- Git-tracked with relative references
- Multi-site accessible
- Documented and organized
- No duplicates across sites

---

## Related Documentation

- [Assets README](./README.md)
- [MkDocs Configuration](../mkdocs.yml)
- [Documentation Structure](../docs/0-README.md)

---

**Custodian:** CORTEX System Agent  
**Status:** ✅ Production Ready
