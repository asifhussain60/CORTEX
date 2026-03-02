# CORTEX Certification Agents

**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
**Updated:** 2026-03-02 | **Authority:** `.github/agents/certification/`

---

## Structure

```
certification/
├── README.md                              # This file
├── cortex-certification-coordinator.md    # Pipeline orchestrator (dispatches to agents)
├── cortex-audit-agent.md                  # Phase 1–2: Delta analysis + drift detection
├── cortex-regression-agent.md             # Phase 3: Regression + dead code + bloat
├── cortex-refactor-agent.md               # Phase 4–5: Prompt optimization + intelligence wiring
├── cortex-memory-agent.md                 # Phase 6: Adaptive learning + document lifecycle
├── cortex-db-agent.md                     # Phase 7: SQLite integrity + self-healing
└── cortex-certification-agent.md          # Phase 8–9: Hardening + scoring + sign-off
```

## Prompt

**Prompt:** `.github/prompts/cortex-total-recall.prompt.md`
**Trigger:** `/totalrecall`
**Workflow:** `cortex-registry/workflows/templates/lifecycle/totalrecall-workflow.yaml`

## Agent Interaction Diagram

```
User → /totalrecall
         │
         ▼
  cortex-total-recall.prompt.md  (defines the 10-phase pipeline)
         │
         ▼
  certification-coordinator.md   (orchestrates execution order)
         │
    ┌────┼────┬────┬────┬────┬────┐
    ▼    ▼    ▼    ▼    ▼    ▼    ▼
  audit  regr  refact  mem  vac  db  cert
  agent  agent agent  agent agent agent agent
  (P1-2) (P3)  (P4-5) (P6) (P7) (P8-9)
```

## Token Budget

| Agent | Tokens |
|-------|--------|
| Prompt (total-recall.prompt.md) | ~5,500 |
| Coordinator | ~1,200 |
| Audit Agent | ~1,500 |
| Regression Agent | ~1,200 |
| Refactor Agent | ~1,500 |
| Memory Agent | ~1,200 |
| DB Agent | ~1,400 |
| Certification Agent | ~1,800 |
| **Total (all loaded)** | **~15,300** |
| **Typical run (prompt + coordinator + 2 agents)** | **~8,500** |
