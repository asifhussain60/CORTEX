# Planning Directory

**Purpose:** User-facing planning for **production GitHub repositories** (NOT CORTEX internal development)

---

## 📁 Structure

```
planning/
├── phases/          # User-defined phases for production repos
├── workflows/       # User workflow templates
└── templates/       # User planning templates
```

---

## 🎯 Use Cases

### ✅ Correct Usage

```yaml
# planning/phases/api-v2-migration.yaml
id: "api-v2-migration"
name: "Migrate API to v2"
repo: "mycompany/production-api"  # External production repo
stages:
  - id: "S1"
    name: "Update GraphQL Schema"
    tasks:
      - "Add new resolvers"
      - "Update tests"
```

### ❌ Incorrect Usage

```yaml
# ❌ DO NOT PUT CORTEX PHASES HERE
# planning/phases/phase-103-registry-consolidation.yaml  ← WRONG
# CORTEX phases belong in: cortex-registry/_cortex-master/phases/
```

---

## 🔗 Related

- **CORTEX Internal Plans:** See `cortex-registry/_cortex-master/phases/`
- **CORTEX Governance:** See `cortex-registry/_cortex-master/core/governance/`
- **Knowledge Base:** See `cortex-registry/knowledge-base/` (for onboarded repos)

---

**Last Updated:** 2026-02-17 (Phase 103 Correction)
