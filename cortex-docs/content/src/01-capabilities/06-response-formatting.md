# Response Formatting & Content Blocks

---
title: CORTEX Response Formatting Standards
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex-registry/core/ + .github/templates/cortex-response-templates.md
order: 6
---

> **Brain analogy:** Response formatting is the **Broca's area** — the brain region responsible for speech production. It doesn't decide *what* to say (that's Reasoning); it decides *how* to say it clearly, consistently, and appropriately for the audience.

---

## Formatting Principles

CORTEX responses follow strict formatting standards (loaded from `cortex-registry/`):

1. **Inline delivery** — CORE-002: never create `.md` or `.txt` report files
2. **Structured output** — tables, code blocks, and hierarchical sections
3. **Role-aware** — different detail levels for Business Leaders, Product Owners, and Developers
4. **Silent execution** — CORE-049: progress bars only, no verbose chatter

---

## Response Structure

Every CORTEX response follows this structure:

```
## 🧠 CORTEX {Mode}
**Author:** Asif Hussain | **Orchestrator:** {OrchestratorName} ✅

---

**Here's what CORTEX heard:**

You've asked CORTEX to {one-line summary}:

1. **{Action}** — {plain-language description of what will happen}
2. **{Action}** — {plain-language description}
3. **{Action}** — {plain-language description, including any assumptions}

**CORTEX's confidence in this understanding:** 🟢 High

> ✅ This looks right? Type `proceed`. Need to correct something? Do it now before CORTEX acts.

---

{Content delivered inline}

---

### ✅ Summary
- Tests: {count} passing
- Governance: {PASS/WARNING}
- Duration: {time}
```

**Why plain language instead of a table?** The intent reflection block is written for you — not for the system. You should be able to read it in 10 seconds and immediately know whether CORTEX understood your request correctly. If anything is wrong, correct it before typing `proceed`.

---

## Workflow Templates

Workflow templates in `cortex-registry/workflows/templates/` define execution patterns:

| Template Category | Location | Purpose |
|------------------|----------|---------|
| **lifecycle/** | CORTEX-internal workflows | Phase execution, master plan orchestration |
| **production/** | External workflows | Production deployment, rollback |

Templates are read by the WorkflowEngine (`cortex/core/workflow_engine.py`) and executed as phase sequences.

---

## Practical Examples

**Product Owner:** "Every response starts by telling me in plain language what CORTEX is about to do. I can read it in ten seconds, confirm it's right, and type `proceed` — or correct it before anything runs. Then the actual content follows in the same session."

**Developer:** "Responses are inline (CORE-002). There's no generated report file to hunt for. CORTEX mirrors my intent back in plain English, I confirm, and execution begins — all right here in VS Code."

*Verified against response template standards · 22 February 2026*
