---
name: cortex-plan
description: 'CORTEX planning and lifecycle skill. Use when: running /plan, /totalrecall, /digest, /distill, /onboard, /decompose, editing cortex-master.yaml, creating or completing phases, or managing the master plan. Covers THIN INDEX CONTRACT, phase lifecycle, phase templates, production certification, content digestion, and service decomposition.'
argument-hint: 'plan <feature> | totalrecall | digest <path> | onboard <repo>'
---

# CORTEX Planning & Lifecycle

---

## Master Plan — THIN INDEX CONTRACT

**`cortex-master.yaml` is a REFERENCE INDEX only — never a detail document.**

| Rule | Detail |
|---|---|
| **Max size** | ≤ 800 lines (alarm at 700) |
| **Prohibited inline** | `phases`, `gap_catalogue`, `tdd_sequence`, `rewrites`, `new_files`, `implementation`, `code_snippets` |
| **Allowed per entry** | `id`, `title`, `status`, `priority`, `sweep_id`, `gaps`, `sub_phases`, `file`, `note` |
| **Detail location** | `cortex-registry/planning/phases/planned/<phase-id>.yaml` |
| **Completed detail** | `cortex-registry/planning/phases/completed/<phase-id>.yaml` |
| **Template** | `cortex-registry/planning/phases/_template.yaml` |

### Phase Lifecycle

**BEFORE adding:**
1. Create `cortex-registry/planning/phases/planned/<phase-id>.yaml`
2. Use `_template.yaml` as scaffold
3. ALL detail in the dedicated file
4. Add ONLY thin reference to `cortex-master.yaml`
5. Verify ≤ 800 lines: `wc -l cortex-registry/cortex-master.yaml`

**BEFORE marking COMPLETE:**
1. All gaps `status: CLOSED` (CORE-064)
2. Move `planned/` → `completed/`
3. Update `file:` reference + `status: COMPLETE`
4. `make test-smoke`

---

## `/totalrecall` — Production Certification

10-phase autonomous pipeline:
1. Delta scan
2. Drift detection
3. Regression testing
4. Optimization
5. Wiring validation
6. Memory consolidation
7. Vacuum cleanup
8. Database maintenance
9. Hardening
10. Certification

**Workflow:** `cortex-registry/workflows/templates/lifecycle/totalrecall-workflow.yaml`

---

## `/digest {path}` — Content Ingestion

3-pipeline intelligent ingestion:
- **Pipeline 1:** Chat session → extract decisions, code changes, lessons
- **Pipeline 2:** Document → summarize, extract key facts
- **Pipeline 3:** Codebase → LENS analysis, dependency mapping

---

## `/distill {file}` — Chat Distillation

Distills chat transcripts into synthesised executable prompts.

---

## `/onboard {repo}` — Repository Onboarding

LENS analysis + SQLite dashboard for new repository understanding.

---

## `/decompose` — Service Decomposition

Break monolithic services into microservices with boundary analysis.

**Workflow:** `cortex-registry/workflows/templates/lifecycle/service-decomposition-workflow.yaml`

---

## Lifecycle Workflow Templates

| Command | Template |
|---|---|
| `/totalrecall` | `lifecycle/totalrecall-workflow.yaml` |
| `/digest` | `lifecycle/digest-workflow.yaml` |
| `/distill` | `lifecycle/distill-workflow.yaml` |
| `/onboard` | `lifecycle/onboarding-workflow.yaml` |
| `/decompose` | `lifecycle/service-decomposition-workflow.yaml` |
| `/sync` | `lifecycle/sync-workflow.yaml` |
| `/train` | `lifecycle/train-workflow.yaml` |
