# CORTEX Certification Agents

**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
**Updated:** 2026-03-12 | **Authority:** `.github/agents/certification/`

---

## Structure

```
certification/
├── README.md                              # This file
├── cortex-certification-coordinator.md    # Pipeline orchestrator (dispatches to agents)
├── cortex-certification-workers.md        # Phase 3–6: Regression + refactor + memory worker duties
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
       audit  workers  vac  db  cert
       coord  agent    agent agent agent
       (P1-2) (P3-6)   (P7)  (P8)  (P9-10)
```

## Token Budget

| Agent | Tokens |
|-------|--------|
| Prompt (total-recall.prompt.md) | ~5,500 |
| Coordinator | ~1,200 |
| Audit Coordinator | ~1,600 |
| Certification Workers | ~2,800 |
| DB Agent | ~1,400 |
| Certification Agent | ~1,800 |
| **Total (all loaded)** | **~15,300** |
| **Typical run (prompt + coordinator + 2 agents)** | **~8,500** |
