# 🚀 CI/CD Integration

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** GitHub Actions integration for automated documentation audits

---

## GitHub Actions Workflow

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
      
      - name: Run Governance Validation
        run: python3 cortex-toolkit/documentation/governance_validator.py --index docs/index.html
      
      - name: Run DocGen Discovery
        run: python3 cortex-toolkit/documentation/docgen_discovery.py
      
      - name: Check Diagram Staleness
        run: python3 cortex-toolkit/documentation/diagram_staleness.py --max-age 30
        continue-on-error: true  # Don't fail build, just warn
      
      - name: Validate Design Standards
        run: python3 cortex-toolkit/documentation/design_validator.py --path docs/
      
      - name: Upload Manifests
        uses: actions/upload-artifact@v4
        with:
          name: doc-manifests
          path: cortex-brain/documents/*.json
```

---

## Pipeline Triggers

| Trigger | When | Action |
|---------|------|--------|
| `src/**` change | Code modified | Re-discover documentable elements |
| `docs/**` change | Docs modified | Validate design standards |
| `cortex-brain/manifests/**` | Orchestrator updated | Update orchestrator docs |

---

## Failure Handling

| Step | On Failure | Action |
|------|------------|--------|
| Governance Validation | FAIL BUILD | Index.html is source of truth |
| DocGen Discovery | FAIL BUILD | Can't generate without manifest |
| Diagram Staleness | WARN ONLY | Continue build, create issue |
| Design Standards | FAIL BUILD | Standards are mandatory |

---

## Artifact Outputs

The pipeline produces:
- `authorized-entry-points.json` - Governance registry
- `docgen-manifest.json` - Discovered elements
- `site-manifest.json` - Site map with links
- `design-validation-report.json` - Standards compliance
