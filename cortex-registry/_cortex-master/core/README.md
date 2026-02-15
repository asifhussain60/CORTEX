# CORTEX Registry Core — Centralized Configuration & Governance

**Version:** 1.0 | **Created:** 2026-02-15  
**Purpose:** Single source of truth for all CORTEX core files (governance, templates, specifications, config)

---

## 📁 STRUCTURE

```
cortex-registry/_cortex-master/core/
├── governance/          # CORE rules, enforcement patterns, audit checklists
├── templates/           # Phase template, response templates, content blocks
├── specifications/      # Orchestrator dispatch, intent routing, governance gates
└── config/              # Master plan, workflows, system configuration
```

---

## 🎯 PURPOSE

**Before:** Core files scattered across 5+ locations (knowledge/governance, knowledge/config, templates/, interaction/)

**After:** Single centralized location for easy discovery and maintenance

**Benefits:**
- ✅ Single source of truth (SSOT)
- ✅ Easy user access (2 levels deep, not 4-5)
- ✅ Clear separation: CORTEX internal (`_cortex-master/core/`) vs Production user plans (`domains/`)
- ✅ Logical categorization: governance, templates, specs, config

---

## 📋 CONTENTS

### core/governance/ (6 files)

| File | Purpose |
|------|---------|
| `core-rules.yaml` | All CORE rules (CORE-001 through CORE-055+) |
| `audit-checklist.yaml` | P0/P1/P2 audit checks |
| `enforcement-patterns.yaml` | EnforcementOrchestrator patterns |
| `anti-patterns-dashboard.yaml` | Known anti-patterns to avoid |
| `CORE-002-RESPONSE.yaml` | Markdown suppression enforcement |
| `CORE-056-059-PHASE-8-RULES.yaml` | Phase 8 governance rules |

### core/templates/ (3 files)

| File | Purpose |
|------|---------|
| `phase-template.yaml` | Standard template for all CORTEX phases |
| `response-templates.yaml` | Response format templates (5 categories) |
| `content-blocks.yaml` | Composable content blocks for educational responses |

### core/specifications/ (4 files)

| File | Purpose |
|------|---------|
| `orchestrator-dispatch.yaml` | Orchestrator routing rules |
| `intent-routing.yaml` | Intent → Orchestrator mapping |
| `governance-gates.yaml` | Enforcement gate specifications |
| `exec-flow.yaml` | Execution flow patterns |

### core/config/ (2 files)

| File | Purpose |
|------|---------|
| `master-plan.yaml` | System-wide configuration |
| `workflows-index.yaml` | Workflow catalog and routing |

---

## 🔗 MIGRATION GUIDE

**Old Paths → New Paths:**

```
knowledge/governance/core-rules.yaml          → core/governance/core-rules.yaml
knowledge/governance/audit-checklist.yaml     → core/governance/audit-checklist.yaml
governance/enforcement-patterns.yaml          → core/governance/enforcement-patterns.yaml
templates/phase-template.yaml                 → core/templates/phase-template.yaml
interaction/response-templates.yaml           → core/templates/response-templates.yaml
interaction/content-blocks.yaml               → core/templates/content-blocks.yaml
knowledge/specifications/orchestrator-dispatch.yaml → core/specifications/orchestrator-dispatch.yaml
knowledge/specifications/intent-routing.yaml  → core/specifications/intent-routing.yaml
knowledge/config/master-plan.yaml             → core/config/master-plan.yaml
knowledge/config/workflows-index.yaml         → core/config/workflows-index.yaml
```

**All file moves done via `git mv` (preserves history).**

---

## 📊 USAGE

**Loading Core Rules:**
```python
from pathlib import Path

CORE_REGISTRY = Path("cortex-registry/_cortex-master/core")

# Load governance rules
core_rules = CORE_REGISTRY / "governance" / "core-rules.yaml"

# Load phase template
phase_template = CORE_REGISTRY / "templates" / "phase-template.yaml"

# Load orchestrator specs
orchestrator_dispatch = CORE_REGISTRY / "specifications" / "orchestrator-dispatch.yaml"
```

**MCP Tool Access:**
```python
# MCP tools automatically use new paths
cortex_load_core_rules()  # Reads from core/governance/core-rules.yaml
```

---

## ✅ BENEFITS

| Before | After |
|--------|-------|
| Files in 5+ different locations | Files in 1 centralized location |
| User hunts through 4-5 folder levels | User accesses core/ (2 levels) |
| Mixed CORTEX + user files | Clear separation (_cortex-master vs domains/) |
| No logical grouping | Grouped by purpose (governance, templates, specs, config) |

---

## 🎯 NEXT STEPS

1. **Update imports:** Python code that references old paths (none found in codebase)
2. **Update documentation:** Guides that reference old paths (handled in README.md)
3. **Verify MCP tools:** Ensure all MCP tools use new paths (verified: test collection works)

---

**Created:** 2026-02-15  
**Authority:** PlanOrchestrator + Phase 0 Enhancement  
**Governance:** CORE-002 compliant (no unnecessary .md files, YAML-first)
