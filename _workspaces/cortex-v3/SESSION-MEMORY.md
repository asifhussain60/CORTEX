# CORTEX v3.2 Unified Architecture Plan — Session Memory

> Last updated: 2026-03-27 | Consolidated for v3.2 package handoff

---

## Plan Status: PLANNING COMPLETE (Consolidated v3.2.0)

The canonical plan has been reconciled to the repo-validated v3.2 baseline. This memory file now reflects the same architecture shape and metrics as the YAML, Markdown, and HTML package.

---

## Canonical Files (SSOT)

| File | Role | Status |
|------|------|--------|
| `v3.2-unified-architecture-plan.yaml` | **Primary SSOT** — all metrics, phases, ADRs, agents, gates, and testing flow from here | Current |
| `v3.2-unified-architecture-plan.md` | Human-readable narrative companion | Current |
| `v32-plan/` | Multi-page HTML exhibit package | Current |

---

## Key Metrics (Canonical — v3.2.0)

| Metric | Value | Notes |
|--------|-------|-------|
| CORTEX Agents | 10 | Consolidated from a larger orchestrator surface |
| Total Agents (all repos) | 32 | 10 CORTEX + 12 WORKFLOW + 10 Knowledge |
| Total Skills | 137 | 19 CORTEX + 36 WORKFLOW + 82 Knowledge |
| ADRs | 14 | ADR-V3-001 through ADR-V3-014, with ADR-V3-013 and ADR-V3-014 withdrawn |
| Gate Skills | 4 | readiness, security, review, deployment |
| DoD Checks | 40 | Across 8 categories |
| Intent Types | 34 | Routed through the agent layer |
| Deployment Surfaces | 2 primary + 3 bonus | Claude Code CLI, VS Code Copilot; Cowork/Cursor/Gemini as bonus |
| Implementation Phases | 5 | P1 COMPLETE, P2-P5 PLANNED |
| Python Orchestrators | 381 | Incrementally deprecated in 3 waves |
| MCP Tool Files | 74 files / 35 logical tools | Python engine layer retained |
| Governance YAMLs | 59 | SKULL + CORE rules |
| Registry YAMLs | 802 | Current repo-validated count |
| Test Files | 1,428 | Preserved through migration |

---

## What Changed in v3.2

1. Repo counts were corrected to match the live Cortex state.
2. Release Evidence Mesh was removed as overengineered and ADR-V3-014 was withdrawn.
3. Plugin governance/signing was removed as premature and ADR-V3-013 was withdrawn.
4. Governance ceremony was reduced from 76 DoD checks and 7 gates to 40 DoD checks and 4 gates.
5. The feature lifecycle now explicitly delegates to workflow-repo rather than redefining it inside CORTEX.
6. Python orchestrators are deprecated incrementally instead of archived in a big-bang move.
7. Testing is now a 3-layer pragmatic model: smoke, agent-routing E2E, and self-onboard.

---

## 10 Consolidated CORTEX Agents

| Agent | Purpose | Key Intents |
|-------|---------|-------------|
| cortex-code | TDD implementation, bug fixing, refactoring, test generation | IMPLEMENT, FIX, REFACTOR, TEST |
| cortex-diagnose | Multi-stack debugging and root cause analysis | DEBUG, RCA |
| cortex-audit | Governance scanning, health, cleanup, YAML validation | AUDIT, TOTALRECALL, HEALTH, GOVERNANCE, VALIDATE, VACUUM |
| cortex-orchestrate | Feature delivery conductor with WORKFLOW delegation | PLAN, DESIGN, REQUIREMENTS, CHANGE_INTELLIGENCE, WORKFLOW, MIGRATE |
| cortex-intel | Onboarding, LENS 4-phase scan, model.yaml production | ONBOARD, ANALYZE, INVESTIGATE |
| cortex-distill | Digest, distillation, training, feedback | DIGEST, DISTILL, TRAIN, FEEDBACK, SYNC |
| cortex-present | PR walkthroughs, HTML exhibits, documentation | REVIEW, CONVERT_TO_HTML, DOCUMENT |
| cortex-lint | 13-dimension DoD enforcement and internal quality gate | internal invocation |
| cortex-interact | Q&A, codebase questions, requirement clarification | QUERY, INTRODUCE, REPHRASE |
| cortex-platform | CI/CD, skill catalog, deployment | DEPLOY, WORKFLOW_COMPOSE |

---

## HTML Package Notes

- Registry page was normalized so it no longer claims a non-canonical ADR-V3-015.
- Hub metadata was corrected to align with the v3.2 plan.
- Cross-page wording was cleaned up where it contradicted the canonical YAML/Markdown files.

---

## Decisions Preserved

1. 10 CORTEX agents is the intended consolidation target.
2. 381 orchestrators is the repo-validated baseline for deprecation planning.
3. 3-wave deprecation is the approved migration strategy.
4. WorkflowComposer remains part of the retained Python engine layer.
5. Cross-repo integration stays split across Cortex, workflow-repo, and knowledge-repo.

---

*Memory updated: 2026-03-27 | v3.2 package aligned*
