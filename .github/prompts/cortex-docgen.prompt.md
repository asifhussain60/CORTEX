# 📚 CORTEX Documentation Generator

**Version:** 2.0.0 | **Author:** Asif Hussain  
**Purpose:** Generate and maintain documentation for CORTEX documentation site  
**Design Standard:** `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`

---

## 🎯 Objective

Automate documentation generation for `http://localhost:8000` and GitHub Pages including:
1. **Governance Validation** - Validate all generation against `docs/index.html` entry points
2. **Code Discovery** - Auto-discover modules, classes, functions, docstrings
3. **Site Map Management** - Track pages, detect missing documentation
4. **Diagram Staleness** - Flag outdated D3.js and Mermaid diagrams
5. **Design Standardization** - Enforce glassmorphism 2-level view hierarchy
6. **Story Generator** - Update CORTEX narrative chapters
7. **User Approval** - Request approval for NEW documentation not in index.html

---

## 🛡️ GOVERNANCE RULE (MANDATORY)

### `docs/index.html` as Source of Truth

**⛔ CRITICAL:** Documentation generation is GOVERNED by `docs/index.html`. Only generate documentation for:
1. **Tiles** - Links in `hero-cta-grid` (KEY FEATURES section)
2. **Anchors** - Navigation links elsewhere in index.html
3. **Story Viewer** - `story/viewer.html` narrative

### Authorized Entry Points (from docs/index.html)

| Entry Point | Path | Level |
|-------------|------|-------|
| Architecture | `architecture/index.html` | Level 1 |
| Security | `security/index.html` | Level 1 |
| Orchestrators | `orchestrators/index.html` | Level 1 |
| Token Optimization | `token-optimization/index.html` | Level 1 |
| Sharpen The Saw | `sts/index.html` | Level 1 |
| Knowledge | `knowledge/index.html` | Level 1 |
| CORTEX LENS | `lens/index.html` | Level 1 |
| Get Started | `getting-started/index.html` | Level 1 |
| Story Viewer | `story/viewer.html` | Special |

**Level 2 pages** are governed by their parent Level 1 index pages (e.g., `orchestrators/planning-system.html` governed by `orchestrators/index.html`).

### ⛔ FORBIDDEN Actions

- ❌ Creating documentation for features NOT linked from `docs/index.html`
- ❌ Adding new tiles/anchors to index.html without user approval
- ❌ Generating orphan pages (no parent navigation)
- ❌ Creating Level 3+ pages (2-level max enforced)

---

## 🙋 User Approval Protocol (NEW Documentation)

### When Discovery Finds Undocumented Features

**If a feature is discovered but NOT in `docs/index.html`:**

1. **DO NOT** generate documentation automatically
2. **PRESENT** the approval template below to user
3. **WAIT** for explicit user selection
4. **ONLY THEN** generate documentation + update index.html

### User Approval Response Template

```markdown
## 📋 New Documentation Request

**Discovered Feature:** {feature_name}
**Source:** `{source_file_path}`
**Description:** {brief_description}

---

### 🎯 Action Required

This feature is NOT currently linked from `docs/index.html`. 
Documentation generation requires your approval.

**Select an option:**

| Option | Action | Command |
|--------|--------|---------|
| **A** | ✅ Approve & Add to Key Features | Reply: `approve A` |
| **B** | ✅ Approve as Level 2 under existing section | Reply: `approve B: {parent_section}` |
| **C** | ⏸️ Defer (do not generate now) | Reply: `defer` |
| **D** | ❌ Reject (not needed) | Reply: `reject` |

**Example responses:**
- `approve A` → Adds new tile to KEY FEATURES grid
- `approve B: orchestrators` → Adds as Level 2 under Orchestrators
- `defer` → Skips generation, logs for future
- `reject` → Removes from consideration

---

### 📍 If Approved (Option A or B)

1. Documentation will be generated following glassmorphism standards
2. `docs/index.html` will be updated with new entry point
3. Breadcrumb navigation will be configured
```

---

## 🏗️ Design Standards Enforcement

### Reference Document
**MANDATORY:** All generated views MUST follow `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`

### 2-Level View Hierarchy (ENFORCED)

| Level | Example | Logo Size | Footer | Breadcrumb |
|-------|---------|-----------|--------|------------|
| **Home** | `index.html` | N/A | ✅ YES | ❌ NO |
| **Level 1** | `/orchestrators/index.html` | 200×200 | ❌ NO | ✅ YES |
| **Level 2** | `/orchestrators/planning-system.html` | 150×150 | ❌ NO | ✅ YES |

**⛔ Level 3+ pages are FORBIDDEN** - Restructure content into Level 2 if needed.

### Panel Spacing (from glassmorphism-design-standards-v2.md)

```css
:root {
    --panel-gap-xs: 0.5rem;    /* 8px - Tight grouping */
    --panel-gap-sm: 1rem;      /* 16px - Within sections */
    --panel-gap-md: 1.5rem;    /* 24px - Between panels */
    --panel-gap-lg: 2rem;      /* 32px - Between sections */
    --panel-gap-xl: 3rem;      /* 48px - Hero separation */
}
```

### Required Elements per Level

**Level 1 Pages:**
- ✅ Breadcrumb bar at top
- ✅ 200×200 CORTEX logo in top-left
- ✅ Large icon + title centered
- ✅ Category cards for Level 2 pages
- ❌ NO footer

**Level 2 Pages:**
- ✅ Breadcrumb bar at top
- ✅ 150×150 CORTEX logo in top-left
- ✅ Detailed content, D3.js/Mermaid diagrams
- ❌ NO footer

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

### Phase 0: Governance Validation (NEW - MANDATORY FIRST)

**Before ANY discovery or generation:**

```bash
# Parse index.html for authorized entry points
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html
```

**Outputs:**
- `cortex-brain/documents/authorized-entry-points.json`
- List of Level 1 tiles from KEY FEATURES
- List of Level 2 pages linked from Level 1 indexes

**Validation Logic:**
1. Parse `docs/index.html` for all `href` attributes in `hero-cta-grid`
2. For each Level 1 page, parse its `index.html` for Level 2 links
3. Build authorized entry point registry
4. Any discovered feature NOT in registry → triggers User Approval Protocol

### Phase 1: Discovery
**Toolkit Script:** `cortex-toolkit/documentation/docgen_discovery.py`

```bash
# Run discovery WITH governance check
python cortex-toolkit/documentation/docgen_discovery.py \
    --output cortex-brain/documents/docgen-manifest.json \
    --governance cortex-brain/documents/authorized-entry-points.json
```

**Discovers:**
- All Python modules in `src/`
- Classes, methods, docstrings, type hints
- Orchestrator manifests in `cortex-brain/manifests/`
- Existing documentation pages in `docs/`

**New Behavior:**
- Flags features NOT in authorized entry points
- Queues them for User Approval Protocol
- Does NOT auto-generate unauthorized docs

### Phase 2: Site Map Audit
**Toolkit Script:** `cortex-toolkit/documentation/site_manifest.py`

```bash
# Generate site manifest with governance validation
python cortex-toolkit/documentation/site_manifest.py \
    --check-missing \
    --governance cortex-brain/documents/authorized-entry-points.json
```

**Outputs:**
- `cortex-brain/documents/docgen-manifest.json` - Complete site map
- List of features without documentation (requires approval)
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

**Validation Checklist:**

| Check | Level 1 | Level 2 |
|-------|---------|---------|
| Logo size correct | 200×200 | 150×150 |
| Breadcrumb present | ✅ | ✅ |
| Footer absent | ✅ | ✅ |
| Panel spacing vars used | ✅ | ✅ |
| Mobile responsive | ✅ | ✅ |
| FontAwesome icons (not emojis) | ✅ | ✅ |

### Phase 5: Story Generator (Manual)
**Location:** `docs/story/`

When new features discovered, update narrative:
- Opening banter (Asif + Miss G)
- Whiteboard pseudo-code session
- Solution discovery
- Victory celebration

---

## 🛠️ Toolkit Scripts

### governance_validator.py (NEW - RUN FIRST)
Parses `docs/index.html` and builds authorized entry point registry.

**Usage:**
```bash
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html
```

**Outputs:**
- `cortex-brain/documents/authorized-entry-points.json`

**Registry Format:**
```json
{
  "level_1": [
    {"path": "architecture/index.html", "title": "Architecture", "icon": "🧠"},
    {"path": "orchestrators/index.html", "title": "Orchestrators", "icon": "🎯"}
  ],
  "level_2": {
    "orchestrators": [
      {"path": "orchestrators/planning-system.html", "title": "Planning System"},
      {"path": "orchestrators/tdd-mastery.html", "title": "TDD Mastery"}
    ]
  },
  "special": ["story/viewer.html"]
}
```

### docgen_discovery.py
Discovers all documentable code elements.

**Usage:**
```bash
python cortex-toolkit/documentation/docgen_discovery.py \
    [--output FILE] \
    [--format json|yaml] \
    [--governance FILE]  # NEW: validates against authorized-entry-points.json
```

### site_manifest.py
Generates site manifest and detects missing docs.

**Usage:**
```bash
python cortex-toolkit/documentation/site_manifest.py \
    [--check-missing] \
    [--check-links] \
    [--governance FILE]  # NEW: validates against authorized-entry-points.json
```

### diagram_staleness.py
Checks diagram freshness against source changes.

**Usage:**
```bash
python cortex-toolkit/documentation/diagram_staleness.py [--max-age DAYS] [--update-manifest]
```

### design_validator.py (NEW)
Validates generated pages against glassmorphism-design-standards-v2.md.

**Usage:**
```bash
python cortex-toolkit/documentation/design_validator.py --path docs/ --level 1|2
```

**Checks:**
- Logo size (200×200 for L1, 150×150 for L2)
- Footer presence (should be absent on L1/L2)
- Breadcrumb presence (required on L1/L2)
- Panel spacing CSS variables used
- Mobile responsiveness

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

- [ ] `cortex-brain/documents/authorized-entry-points.json` exists (governance registry)
- [ ] `cortex-brain/documents/docgen-manifest.json` exists
- [ ] `cortex-brain/documents/diagram-manifest.json` exists
- [ ] All toolkit scripts executable
- [ ] Diagram staleness detection working
- [ ] Site map complete with missing doc detection
- [ ] **Governance validation passes** (all generated docs have index.html entry points)
- [ ] **2-level hierarchy enforced** (no Level 3+ pages)
- [ ] **Glassmorphism standards applied** (logo sizes, no footers on L1/L2)

---

## 🔄 Workflow

```
0. Governance Check → governance_validator.py (MANDATORY FIRST)
   ↓
1. Run Discovery    → docgen_discovery.py --governance authorized-entry-points.json
   ↓
2. User Approval    → Present approval template for unauthorized features
   ↓
3. Audit Site Map   → site_manifest.py --check-missing --governance
   ↓
4. Check Diagrams   → diagram_staleness.py
   ↓
5. Design Validate  → Check glassmorphism-design-standards-v2.md compliance
   ↓
6. Generate Docs    → Only for APPROVED entry points
   ↓
7. Update index.html → Add tiles/anchors for newly approved docs
```

**Key Decision Points:**
- Step 0: If governance file missing, create from index.html
- Step 2: WAIT for user response before proceeding
- Step 6: Skip unauthorized features (defer to future approval)

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

