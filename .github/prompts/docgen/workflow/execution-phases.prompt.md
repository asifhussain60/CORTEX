# 📋 Execution Phases

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Define the 6-phase documentation generation workflow

---

## Workflow Overview

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

---

## Phase 0: Governance Validation (MANDATORY FIRST)

**Before ANY discovery or generation:**

```bash
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html
```

**Outputs:**
- `cortex-brain/documents/authorized-entry-points.json`

**Decision Point:** If governance file missing, create from index.html

---

## Phase 1: Discovery

**Toolkit Script:** `cortex-toolkit/documentation/docgen_discovery.py`

```bash
python cortex-toolkit/documentation/docgen_discovery.py \
    --output cortex-brain/documents/docgen-manifest.json \
    --governance cortex-brain/documents/authorized-entry-points.json
```

**Discovers:**
- All Python modules in `src/`
- Classes, methods, docstrings, type hints
- Orchestrator manifests in `cortex-brain/manifests/`
- Existing documentation pages in `docs/`

**Behavior:**
- Flags features NOT in authorized entry points
- Queues them for User Approval Protocol
- Does NOT auto-generate unauthorized docs

---

## Phase 2: User Approval

**Decision Point:** WAIT for user response before proceeding

See `docgen/core/user-approval-protocol.prompt.md` for template.

---

## Phase 3: Site Map Audit

**Toolkit Script:** `cortex-toolkit/documentation/site_manifest.py`

```bash
python cortex-toolkit/documentation/site_manifest.py \
    --check-missing \
    --governance cortex-brain/documents/authorized-entry-points.json
```

**Outputs:**
- `cortex-brain/documents/docgen-manifest.json` - Complete site map
- List of features without documentation (requires approval)
- Broken internal links

---

## Phase 4: Diagram Staleness Check

**Toolkit Script:** `cortex-toolkit/documentation/diagram_staleness.py`

```bash
python cortex-toolkit/documentation/diagram_staleness.py
```

See `docgen/standards/diagram-quality.prompt.md` for staleness thresholds.

---

## Phase 5: Design Standards Enforcement

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

```bash
python cortex-toolkit/documentation/design_validator.py --path docs/
```

---

## Phase 6: Generate Documentation

**Decision Point:** Skip unauthorized features (defer to future approval)

Only generate documentation for:
1. Features in `authorized-entry-points.json`
2. Features explicitly approved by user in Phase 2

---

## Phase 7: Update index.html

Add tiles/anchors for newly approved documentation.

After update, regenerate governance registry:
```bash
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html
```
