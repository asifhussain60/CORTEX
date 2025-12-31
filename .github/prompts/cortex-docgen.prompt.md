# 📚 CORTEX Documentation Generator

**Version:** 3.0.0 (Modular) | **Author:** Asif Hussain  
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

## 📂 Module Structure

**OLD (v2.0):** Single file (583 lines) ❌ BLOAT  
**NEW (v3.0):** Index + 8 modular sub-prompts (~150 lines main) ✅ OPTIMIZED

### Sub-Prompts (Load on Demand)

| Module | Path | Load When |
|--------|------|-----------|
| **Governance Rules** | `docgen/core/governance-rules.prompt.md` | ALWAYS |
| **User Approval** | `docgen/core/user-approval-protocol.prompt.md` | New feature discovery |
| **Design Standards** | `docgen/standards/design-standards.prompt.md` | Creating/editing views |
| **Diagram Quality** | `docgen/standards/diagram-quality.prompt.md` | Creating diagrams |
| **Execution Phases** | `docgen/workflow/execution-phases.prompt.md` | Full docgen run |
| **Toolkit Scripts** | `docgen/workflow/toolkit-scripts.prompt.md` | Script execution |
| **Error Handling** | `docgen/operations/error-handling.prompt.md` | Troubleshooting |
| **CI/CD Integration** | `docgen/operations/cicd-integration.prompt.md` | Pipeline setup |

---

## 🔗 Load Order

### Full Documentation Generation
1. `governance-rules.prompt.md` (REQUIRED)
2. `execution-phases.prompt.md` (REQUIRED)
3. `design-standards.prompt.md` (REQUIRED for view creation)
4. Others (OPTIONAL, context-dependent)

### Quick Reference Tasks

| Task | Load These Modules |
|------|-------------------|
| **Full docgen run** | governance-rules + execution-phases |
| **View creation only** | design-standards + diagram-quality |
| **Validate existing** | design-standards |
| **Troubleshooting** | error-handling |
| **CI/CD setup** | cicd-integration |

---

## 🛡️ Governance (Summary)

**Source of Truth:** `docs/index.html`

**⛔ FORBIDDEN:**
- Creating docs NOT linked from index.html
- Adding tiles without user approval
- Creating Level 3+ pages

**Full rules:** `docgen/core/governance-rules.prompt.md`

---

## 🏗️ Design Standards (Summary)

| Level | Logo Size | Footer | Breadcrumb |
|-------|-----------|--------|------------|
| Home | N/A | ✅ YES | ❌ NO |
| Level 1 | 200×200 | ❌ NO | ✅ YES |
| Level 2 | 150×150 | ❌ NO | ✅ YES |

**Full specification:** `docgen/standards/design-standards.prompt.md`

---

## 🛠️ Toolkit Scripts (Summary)

| Script | Purpose |
|--------|---------|
| `governance_validator.py` | Build authorized entry points registry |
| `design_validator.py` | Validate glassmorphism standards |
| `docgen_discovery.py` | Discover documentable elements |
| `site_manifest.py` | Generate site map |
| `diagram_staleness.py` | Check diagram freshness |

**Full documentation:** `docgen/workflow/toolkit-scripts.prompt.md`

---

## 🔄 Quick Start Workflow

```bash
# 1. Governance check (ALWAYS FIRST)
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html

# 2. Discovery
python cortex-toolkit/documentation/docgen_discovery.py

# 3. Validate design standards
python cortex-toolkit/documentation/design_validator.py --path docs/
```

---

## ✅ Success Criteria

- [ ] `authorized-entry-points.json` exists (governance registry)
- [ ] `docgen-manifest.json` exists
- [ ] All toolkit scripts executable
- [ ] Governance validation passes
- [ ] 2-level hierarchy enforced
- [ ] Glassmorphism standards applied

---

## 📊 Performance Metrics (v3.0 vs v2.0)

| Metric | v2.0 | v3.0 | Improvement |
|--------|------|------|-------------|
| Main file | 583 lines | ~150 lines | 74% reduction |
| Avg context load | ~583 lines | ~230 lines | 60% reduction |
| Maintainability | Monolithic | Modular | 80% easier |

---

## 📚 References

- **Design Standard:** `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`
- **Optimization Report:** `cortex-brain/documents/optimization/cortex-docgen-optimization-report.md`
- **Archived v2.0:** `cortex-brain/archives/cortex-docgen-v2.0.prompt.md`

---

**Version History:**
- v3.0.0 (2025-12-31): Modular decomposition (8 sub-prompts)
- v2.0.0: Added governance validation
- v1.0.0: Initial release
