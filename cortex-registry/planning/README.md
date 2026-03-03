# CORTEX Planning — Phase Registry

This directory is the **thin-index planning hub** for all CORTEX phases.

## Structure

```
planning/
  phases/
    completed/    ← Completed phase detail files (archived)
    planned/      ← Upcoming sub-phase YAML files (active)
    _template.yaml  ← Scaffold for new phase files
```

## THIN INDEX CONTRACT

`cortex-master.yaml` (parent dir) is a **reference index only** — ≤800 lines.
All detail lives in individual `phases/planned/<phase-id>.yaml` files.

## Key Files

| File | Purpose |
|------|---------|
| `phases/_template.yaml` | Template for new phase files |
| `phases/planned/phase-111*.yaml` | CORE-035 duplicate sweep (active) |
| `phases/planned/phase-102*.yaml` | Orphan package cleanup (active) |
| `phases/planned/phase-103*.yaml` | God object decomposition (active) |
| `phases/planned/phase-108*.yaml` | Registry namespace consolidation (active) |
| `phases/completed/` | Completed phase archives |

## Governance

- THIN INDEX CONTRACT: `cortex-registry/workflows/templates/governance/master-plan-phase-lifecycle.yaml`
- Template: `phases/_template.yaml`
- Authority: `cortex-master.yaml` § THIN INDEX CONTRACT
