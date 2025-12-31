# 🛡️ Governance Rules

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Define documentation generation governance rules

---

## `docs/index.html` as Source of Truth

**⛔ CRITICAL:** Documentation generation is GOVERNED by `docs/index.html`. Only generate documentation for:
1. **Tiles** - Links in `hero-cta-grid` (KEY FEATURES section)
2. **Anchors** - Navigation links elsewhere in index.html
3. **Story Viewer** - `story/viewer.html` narrative

---

## Authorized Entry Points (from docs/index.html)

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

---

## ⛔ FORBIDDEN Actions

- ❌ Creating documentation for features NOT linked from `docs/index.html`
- ❌ Adding new tiles/anchors to index.html without user approval
- ❌ Generating orphan pages (no parent navigation)
- ❌ Creating Level 3+ pages (2-level max enforced)

---

## Governance Validation

**Toolkit Script:** `cortex-toolkit/documentation/governance_validator.py`

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

---

## Registry Format

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
