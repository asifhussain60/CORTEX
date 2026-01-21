# Build Structure Reference

**Updated:** 2026-01-21  
**Architecture:** Hidden build output with centralized assets

---

## Folder Locations

### Source Folders (Committed to Git)
```
cortex/
├── docs/                    SOURCE documentation (markdown)
├── assets/                  CENTRALIZED assets (images, etc.)
├── mkdocs.yml               Build configuration
└── .gitignore               Git exclusion rules
```

### Build Output (Git-Ignored)
```
cortex/
└── _build/
    └── site/                GENERATED website (HTML)
        ├── index.html
        ├── assets/          AUTO-COPIED from root assets/
        └── (other pages)
```

---

## Key Paths

| Purpose | Path | Git Status |
|---------|------|-----------|
| Source docs | `docs/` | ✅ COMMITTED |
| Logo files | `assets/images/` | ✅ COMMITTED |
| Build config | `mkdocs.yml` | ✅ COMMITTED |
| Built HTML | `_build/site/` | 🚫 IGNORED |
| Build hook | `docs/_hooks/copy_assets.py` | ✅ COMMITTED |

---

## Build Process

```
Command: mkdocs build

Step 1: Generate HTML
  docs/ → _build/site/

Step 2: Copy Assets (Hook)
  assets/ → _build/site/assets/

Result: Complete site in _build/site/
```

---

## Important Notes

✅ **Root has only 3 visible folders:** docs, assets, cortex-gitpages (+ other project folders)  
✅ **_build/ is hidden:** Git ignores, not committed to repository  
✅ **All assets auto-copied:** No manual intervention needed  
✅ **Clean git history:** Generated files never pollute repository  

---

## Commands

```bash
# Build documentation (outputs to _build/site/)
mkdocs build

# Serve locally with live reload
mkdocs serve

# Clean build output
Remove-Item -Path '_build' -Recurse -Force
```

---

## CI/CD Integration

If your CI/CD pipeline references the site location, update to:
- **OLD:** `site/`
- **NEW:** `_build/site/`

The build output is now in `_build/site/` instead of root `site/`.
