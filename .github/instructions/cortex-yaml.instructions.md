---
applyTo: "cortex-registry/**/*.yaml"
---

# CORTEX Registry YAML Rules

**These rules apply automatically when editing any YAML in `cortex-registry/`.**

## THIN INDEX CONTRACT (cortex-master.yaml)
- `cortex-master.yaml` is a reference index ONLY — ≤800 lines (alarm at 700)
- NEVER write these inline: `gap_catalogue`, `tdd_sequence`, `new_files`, `implementation`, `code_snippets`
- Phase detail goes in: `cortex-registry/planning/phases/planned/<phase-id>.yaml`
- Each entry: `id`, `title`, `status`, `priority`, `sweep_id`, `gaps`, `sub_phases`, `file`, `note`

## YAML Reader Routing
- All YAML access in `cortex/` MUST route through `RegistryYAMLReader`
- Never use `yaml.safe_load()` or `yaml.load()` directly in production code
- Exception: test files and scripts

## Path Format
- Use forward-slash (`/`) in all `path:` fields — Windows-compatible
- Never use backslash or drive letters

## No Versioning (CORE-NO-VERSION)
- No `version:` fields in governance, workflow, or template YAMLs
- No semver strings, `v1`/`v2` markers, or release tags
- Exception: Python package version references (`>=`, `==`)

## V2 Conventions
- Keep YAMLs thin and reference-oriented; avoid embedding implementation detail where a phase/workflow file exists
- Keep paths aligned to consolidated `cortex` package and registry SSOT locations only

## Workflow Templates
- Every code-modifying workflow MUST include these primitives:
  - `primitives/execution/ac-marker-emit.yaml`
  - `primitives/governance/holistic-validation-gate.yaml` (IMPLEMENT/FIX/REFACTOR)
  - `primitives/validation/detect-fix-rescan-loop.yaml` (CORE-068 convergence)
