# 📚 CORTEX Documentation Generator

**Version:** 1.1.0 | **Author:** Asif Hussain  
**Purpose:** Generate and maintain documentation for CORTEX documentation site

---

## 🎯 Objective

Automate documentation generation for `http://localhost:8000` and GitHub Pages including:
1. **Code Discovery** - Auto-discover modules, classes, functions, docstrings
2. **Site Map Management** - Track pages, detect missing documentation
3. **Diagram Staleness** - Flag outdated D3.js and Mermaid diagrams
4. **Design Standardization** - Enforce glassmorphism view hierarchy
5. **Story Generator** - Update CORTEX narrative chapters

---

## ⚠️ Prerequisites

- **Python:** 3.9+ required
- **Git:** Optional but recommended (enables staleness detection)
- **Disk Space:** ~50MB for manifests and backups

**Verify:**
```bash
python3 --version  # Should be 3.9+
git --version      # Optional
```

---

## 🛡️ Security Considerations

| Risk | Mitigation |
|------|------------|
| Path traversal | All paths validated to stay within project root |
| Subprocess injection | Git commands use list args, not shell strings |
| Manifest tampering | Checksums included in manifests |
| Concurrent access | Atomic file writes prevent corruption |

---

## 📋 Execution Phases

### Phase 1: Discovery
**Toolkit Script:** `cortex-toolkit/documentation/docgen_discovery.py`

```bash
# Run discovery
python cortex-toolkit/documentation/docgen_discovery.py --output cortex-brain/documents/docgen-manifest.json
```

**Discovers:**
- All Python modules in `src/`
- Classes, methods, docstrings, type hints
- Orchestrator manifests in `cortex-brain/manifests/`
- Existing documentation pages in `docs/`

### Phase 2: Site Map Audit
**Toolkit Script:** `cortex-toolkit/documentation/site_manifest.py`

```bash
# Generate site manifest with missing docs detection
python cortex-toolkit/documentation/site_manifest.py --check-missing
```

**Outputs:**
- `cortex-brain/documents/docgen-manifest.json` - Complete site map
- List of features without documentation
- Broken internal links

### Phase 3: Diagram Staleness Check
**Toolkit Script:** `cortex-toolkit/documentation/diagram_staleness.py`

```bash
# Check diagram freshness
python cortex-toolkit/documentation/diagram_staleness.py
```

**Logic:**
- Compare diagram file mtime to related source files
- Flag diagrams >30 days old with changed source code
- Report which diagrams need update

### Phase 4: Design Standards Enforcement
**Reference:** `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`

**View Hierarchy:**
| Level | Logo Size | Footer | Example |
|-------|-----------|--------|---------|
| Home | N/A | ✅ YES | `index.html` |
| Level 1 | 200×200 | ❌ NO | `/orchestrators/index.html` |
| Level 2 | 150×150 | ❌ NO | `/orchestrators/planning-system.html` |

**Panel Spacing:** Use `--panel-gap-*` CSS variables (xs/sm/md/lg/xl)

### Phase 5: Story Generator (Manual)
**Location:** `docs/story/`

When new features discovered, update narrative:
- Opening banter (Asif + Miss G)
- Whiteboard pseudo-code session
- Solution discovery
- Victory celebration

---

## 🛠️ Toolkit Scripts

### docgen_discovery.py
Discovers all documentable code elements.

**Usage:**
```bash
python cortex-toolkit/documentation/docgen_discovery.py [--output FILE] [--format json|yaml]
```

### site_manifest.py
Generates site manifest and detects missing docs.

**Usage:**
```bash
python cortex-toolkit/documentation/site_manifest.py [--check-missing] [--check-links]
```

### diagram_staleness.py
Checks diagram freshness against source changes.

**Usage:**
```bash
python cortex-toolkit/documentation/diagram_staleness.py [--max-age DAYS] [--update-manifest]
```

---

## 📊 Diagram Quality Standards

### D3.js Visualizations
- ✅ Interactive (hover, click, tooltips)
- ✅ Data-driven (from codebase metrics)
- ✅ Responsive (fit viewport)
- ✅ Animated (300-500ms transitions)
- ✅ Accessible (ARIA labels)

### Mermaid Diagrams
- ✅ Accurate (current architecture)
- ✅ Readable (clear labels)
- ✅ Styled (glassmorphism theme)
- ✅ Focused (one concept each)

**Mermaid Theme:**
```javascript
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#1a1f3a',
      'primaryTextColor': '#ffffff',
      'primaryBorderColor': '#00d4ff',
      'lineColor': '#00d4ff',
      'secondaryColor': '#2a2f4a',
      'tertiaryColor': '#0a0e27'
    }
  }
}%%
```

---

## 🦶 Footer Standards

| View Level | Footer | Rationale |
|------------|--------|-----------|
| Home Page | ✅ YES | Landing needs full nav/credits |
| Level 1 | ❌ NO | Breadcrumbs provide navigation |
| Level 2 | ❌ NO | Breadcrumbs provide navigation |

---

## 📖 Story Generator Guidelines

### Character Voices
| Character | Voice | Color |
|-----------|-------|-------|
| **Asif Codenstein** | First-person, self-deprecating humor | `#00d4ff` (blue) |
| **Miss G** | Sassy AI, witty comebacks | `#ff00ff` (magenta) |

### Whiteboard Code Panels
Use `.whiteboard-panel` class for pseudo-code in story chapters.

---

## ✅ Success Criteria

- [ ] `cortex-brain/documents/docgen-manifest.json` exists
- [ ] `cortex-brain/documents/diagram-manifest.json` exists
- [ ] All toolkit scripts executable
- [ ] Diagram staleness detection working
- [ ] Site map complete with missing doc detection

---

## 🔄 Workflow

```
1. Run Discovery    → docgen_discovery.py
2. Audit Site Map   → site_manifest.py --check-missing
3. Check Diagrams   → diagram_staleness.py
4. Update Stale     → Manual updates flagged
5. Generate Docs    → generate_docs_from_code.py
```

---

## ⚠️ Error Handling & Recovery

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Stale diagrams found (warning) |
| 2 | Invalid arguments |
| 3 | Project root not found |
| 4 | Permission denied |
| 5 | Git not available (non-fatal) |

### Recovery Procedures

**Corrupted Manifest:**
```bash
# Restore from backup
cp cortex-brain/documents/docgen-manifest.json.bak.* cortex-brain/documents/docgen-manifest.json

# Or regenerate from scratch
python3 cortex-toolkit/documentation/docgen_discovery.py --force
```

**Failed Mid-Execution:**
```bash
# Check for temp files
ls -la cortex-brain/documents/*.tmp

# Remove stale temps
rm -f cortex-brain/documents/*.tmp
```

---

## 🚀 CI/CD Integration

**GitHub Actions Example:**
```yaml
name: Documentation Audit
on:
  push:
    paths:
      - 'src/**'
      - 'docs/**'
      - 'cortex-brain/manifests/**'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run DocGen Discovery
        run: python3 cortex-toolkit/documentation/docgen_discovery.py
      
      - name: Check Diagram Staleness
        run: python3 cortex-toolkit/documentation/diagram_staleness.py --max-age 30
        continue-on-error: true  # Don't fail build, just warn
      
      - name: Upload Manifests
        uses: actions/upload-artifact@v4
        with:
          name: doc-manifests
          path: cortex-brain/documents/*.json
```

---

## 🔍 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Could not analyze X: syntax error` | Invalid Python file | Fix syntax or add to `.docgenignore` |
| `Git not available` | Git not installed | Install Git or run with `--no-git` |
| `Permission denied` | File permissions | Check write access to `cortex-brain/documents/` |
| `Manifest checksum mismatch` | File corrupted | Regenerate manifest |

