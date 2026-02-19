# CORTEX Refactor — CORTEX Cohesive Brain Plan

## Purpose
Transform CORTEX from fragmented packages (3 top-level, 120+ orchestrators, 9+ duplicate concept directories) into a **single cohesive brain**.

## Source Documents
- `gpt-review.txt` — GPT architectural review with kernel-first plugin recommendation
- `chat01.md` — Prior Copilot planning session with full capability manifest

## Plan Files (14 files)

### Support Files

| File | Purpose |
|------|---------|
| `00-overview.yaml` | Master plan — DoD, architecture, EA principles, SQLite spec, MCP consolidation, workflow templates, file factory, phase index |
| `capability-manifest.yaml` | ~100-item zero-regression checklist (MCP tools, orchestrators, governance, intelligence, infrastructure, workflows, design patterns, SDLC coverage) |
| `consolidation-matrix.yaml` | All deduplication targets — packages, concepts, orchestrators, brain dissolution, directories, files, tests |
| `README.md` | This file — plan directory index |

### Phase Files (10 phases, sequential)

| # | File | Purpose |
|---|------|---------|
| 01 | `phase-01-foundation.yaml` | Safety net — capability manifest, file factory, workflow engine, SQLite audit, MCP consolidation map |
| 02 | `phase-02-governance-alignment.yaml` | Rules review, 6 new rules (CORE-058–063), CCL GovernanceCrystal, tier alignment |
| 03 | `phase-03-package-consolidation.yaml` | 3 packages → 1 (`cortex_intelligence/`, `cortex_lens/` → `cortex/`) |
| 04 | `phase-04-brain-deduplication.yaml` | Dissolve `brain/` (261 files, 28 subdirs) into proper domains |
| 05 | `phase-05-orchestrator-rationalization.yaml` | ~120 → ~40 orchestrators, 34 → ~22 MCP tools, workflow templates |
| 06 | `phase-06-directory-cleanup.yaml` | 59 → ~15 canonical directories, small dir merges, phase-named archives |
| 07 | `phase-07-test-consolidation.yaml` | 55 test dirs → ~15, high-value only, golden test promotion |
| 08 | `phase-08-registry-docs.yaml` | Registry as one-stop YAML shop, cortex-docs alignment, infrastructure catalog |
| 09 | `phase-09-final-verification.yaml` | 5 verification stages, full refactoring sweep, archive deletion |
| 10 | `phase-10-production-readiness.yaml` | Performance benchmarking, chaos testing, disaster recovery, SLOs, go-live |

## Execution Order

```
Phase 01 (Foundation) → Phase 02 (Governance) → Phase 03 (Packages)
  → Phase 04 (Brain) → Phase 05 (Orchestrators) → Phase 06 (Directories)
  → Phase 07 (Tests) → Phase 08 (Registry/Docs) → Phase 09 (Verification)
  → Phase 10 (Production)
```

Each phase depends on the previous — no phase starts until predecessor is 100% green.

## Governance
- Plan files live here permanently — NOT in the archive path
- Each phase is a self-contained PR with its own test gate
- Capability manifest is validated after every phase
- All operations comply with CORE governance rules (CORE-002, CORE-008, CORE-011, CORE-012, CORE-028, CORE-035)

## Deleted Files (removed during plan cleanup)
- `EXECUTION-BLUEPRINT.md` — CORE-002 violation, duplicated phase content
- `context-summary.yaml` — Stale data, duplicated in `00-overview.yaml`
- `migration-tracker.yaml` — Thin content, overlapped with per-phase execution sequences

## Status: APPROVED
