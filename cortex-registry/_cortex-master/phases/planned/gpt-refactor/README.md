# GPT Refactor — CORTEX Cohesive Brain Plan

## Purpose
Transform CORTEX from fragmented packages (3 top-level, 120 orchestrators, 9+ duplicate concept directories) into a **single cohesive brain**.

## Source Documents
- `gpt-review.txt` — GPT architectural review with kernel-first plugin recommendation
- `chat01.md` — Prior Copilot planning session with full capability manifest

## Plan Files

| File | Purpose |
|------|---------|
| `00-overview.yaml` | Master plan — DoD, architecture, workflow template spec, file factory spec |
| `capability-manifest.yaml` | ~100-item zero-regression checklist |
| `migration-tracker.yaml` | Component lifecycle: source → archive → target → validated |
| `consolidation-matrix.yaml` | All deduplication targets across the codebase |
| `phase-00-foundation.yaml` | Safety net — capability manifest, file factory, workflow engine |
| `phase-01-package-consolidation.yaml` | 3 packages → 1 |
| `phase-02-brain-deduplication.yaml` | Dissolve brain/ into proper domains |
| `phase-03-orchestrator-rationalization.yaml` | ~120 → ~40 orchestrators with workflow templates |
| `phase-04-directory-cleanup.yaml` | ~50 → ~15 canonical directories |
| `phase-05-test-consolidation.yaml` | 1,139 tests → high-value suite |
| `phase-06-registry-docs.yaml` | Registry as one-stop YAML shop |
| `phase-07-final-verification.yaml` | 5 verification stages, archive deletion |

## Governance
- Plan files live here permanently — NOT in the archive path
- Each phase is a self-contained PR with its own test gate
- No phase starts until the previous phase is 100% green
- Capability manifest is validated after every phase

## Status: APPROVED
