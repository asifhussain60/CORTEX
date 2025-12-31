# 🛠️ Toolkit Scripts

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Document all docgen toolkit scripts and their usage

---

## Script Inventory

| Script | Purpose | Priority |
|--------|---------|----------|
| `governance_validator.py` | Build authorized entry points registry | RUN FIRST |
| `design_validator.py` | Validate glassmorphism standards | After generation |
| `docgen_discovery.py` | Discover documentable code elements | Phase 1 |
| `site_manifest.py` | Generate site map, detect missing docs | Phase 3 |
| `diagram_staleness.py` | Check diagram freshness | Phase 4 |

---

## governance_validator.py

**Purpose:** Parses `docs/index.html` and builds authorized entry point registry.

```bash
# Basic usage
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html

# Check specific page authorization
python cortex-toolkit/documentation/governance_validator.py --check orchestrators/planning-system.html

# JSON output
python cortex-toolkit/documentation/governance_validator.py --format json
```

**Output:** `cortex-brain/documents/authorized-entry-points.json`

---

## design_validator.py

**Purpose:** Validates generated pages against glassmorphism-design-standards-v2.md.

```bash
# Validate single page
python cortex-toolkit/documentation/design_validator.py --path docs/orchestrators/index.html --level 1

# Validate entire directory
python cortex-toolkit/documentation/design_validator.py --path docs/

# JSON report
python cortex-toolkit/documentation/design_validator.py --path docs/ --format json --output report.json
```

**Checks:**
- Logo size (200×200 for L1, 150×150 for L2)
- Footer presence (should be absent on L1/L2)
- Breadcrumb presence (required on L1/L2)
- Panel spacing CSS variables used
- Mobile responsiveness

---

## docgen_discovery.py

**Purpose:** Discovers all documentable code elements.

```bash
# Basic discovery
python cortex-toolkit/documentation/docgen_discovery.py

# With governance validation
python cortex-toolkit/documentation/docgen_discovery.py \
    --output cortex-brain/documents/docgen-manifest.json \
    --governance cortex-brain/documents/authorized-entry-points.json

# YAML format
python cortex-toolkit/documentation/docgen_discovery.py --format yaml
```

**Discovers:**
- All Python modules in `src/`
- Classes, methods, docstrings, type hints
- Orchestrator manifests in `cortex-brain/manifests/`
- Existing documentation pages in `docs/`

---

## site_manifest.py

**Purpose:** Generates site manifest and detects missing docs.

```bash
# Generate manifest
python cortex-toolkit/documentation/site_manifest.py

# Check for missing documentation
python cortex-toolkit/documentation/site_manifest.py --check-missing

# Check for broken links
python cortex-toolkit/documentation/site_manifest.py --check-links

# With governance validation
python cortex-toolkit/documentation/site_manifest.py \
    --check-missing \
    --governance cortex-brain/documents/authorized-entry-points.json
```

---

## diagram_staleness.py

**Purpose:** Checks diagram freshness against source changes.

```bash
# Default check (30 days)
python cortex-toolkit/documentation/diagram_staleness.py

# Custom max age
python cortex-toolkit/documentation/diagram_staleness.py --max-age 14

# Update manifest with staleness info
python cortex-toolkit/documentation/diagram_staleness.py --update-manifest
```

---

## Prerequisites

- **Python:** 3.9+ required
- **Git:** Optional but recommended (enables staleness detection)
- **Disk Space:** ~50MB for manifests and backups

**Verify:**
```bash
python3 --version  # Should be 3.9+
git --version      # Optional
```
