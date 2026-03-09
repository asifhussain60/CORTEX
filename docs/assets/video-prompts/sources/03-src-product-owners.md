> **Diagram references** — filenames below resolve from `docs/assets/diagrams/`.
> Update any diagram file in place; this source requires no edits.
> - Delivery pipeline: `03-diagram-workflow-sdlc-pipeline.md`
> - Sweep completeness: `06-diagram-governance-sweep-completeness-core-064.md`
> - Convergence gate: `12-diagram-governance-convergence-gate-core-068.md`
> - PO change intelligence: `19-diagram-orchestration-po-change-intelligence-pipeline.md`

# CORTEX for Product Owners — Source Document
## Video 03 · Audience: Product Owners & Delivery Leads

**Purpose:** NotebookLM source for steering prompt `03-steer-product-owners.md`.
Synthesised from `docs/.content/09-lifecycle-from-idea-to-production.md`,
`docs/.content/04-tdd-quality-flywheel.md`, and
`docs/.content/03-governance-quality-that-enforces-itself.md`.

---

## The Product Owner's Pain

Every product owner has lived this: a story moves to Done, demo goes well,
then production fails. The acceptance criteria existed — written in Jira,
agreed in refinement — but nobody could prove they were met. "Done" was
trust, not evidence.

Multiply that across 40 stories a sprint, 8 engineers, 6 teams. The gap
between what POs intend and what ships is not a communication problem.
It is a traceability problem. CORTEX closes it.

---

## What CORTEX Does for Product Owners

### Acceptance Criteria → Passing Tests (Automatic)

CORTEX enforces Test-Driven Development as infrastructure. Before a single
line of implementation is written, the acceptance criterion becomes a test.
The test fails first (Red). Then implementation is written to make it pass
(Green). The acceptance criterion and the test are permanently linked.

The product owner can see the chain at any point:

```
User Story → Acceptance Criterion → Test → Green CI Badge
```

This is not a report. It is a live, queryable trace. The PO does not need
to trust the engineer — the evidence is in the system.

### Change Intelligence — Impact Before Commitment

Product owners change requirements. It is the job. The problem is not
change — it is invisible impact. CORTEX's PO Change Intelligence pipeline
(see `19-diagram-orchestration-po-change-intelligence-pipeline.md`)
propagates a requirement change through the dependency graph and surfaces:

- Which tests are now invalidated
- Which stories are affected
- What the engineering effort estimate is

Before the PO commits the change to the sprint. Impact is quantified, not
guessed.

### Why Every Engineering Decision Was Made

DecisionTraceabilityLogger links every significant engineering decision
to the knowledge principle that justified it. Six months after a sprint,
when a stakeholder asks "why did we build it this way?", the answer is
in the system — not in someone's memory.

---

## Role Propositions

| Proposition | Evidence |
|-------------|---------|
| "Done" means done | Acceptance criterion → passing test — automatic chain, not manual verification |
| Change without surprise | PO Change Intelligence pipeline quantifies impact before commitment |
| Traceable decisions | Every engineering decision linked to a knowledge principle permanently |
| No escaped defects | Convergence gate (CORE-068) iterates until all issues are resolved before ship |
| Governance on autopilot | 60+ rules enforced at pre-commit, CI, runtime — PO never chases compliance |

---

## Suggested Quotes (for narrator use)

> "Software is a conversation between what the customer wants and what the
> system does. The gap is where bugs live." — Jeff Patton, *User Story Mapping*

> "If you don't know what done looks like, you can't get there."
> — Mike Cohn, *Succeeding with Agile*

---

## Visual Cues for NotebookLM

- **Story-to-test chain** *(see `19-diagram-orchestration-po-change-intelligence-pipeline.md`)*:
  user story card animates to acceptance criterion text, which morphs into a
  glowing test spec, which resolves to a green CI badge — one smooth flow
- **Change impact graph** *(see `03-diagram-workflow-sdlc-pipeline.md`)*:
  requirement change ripples through dependency graph; affected stories amber,
  unaffected stories grey; impact count materialises: "3 tests affected, 1 story"
- **Convergence gate** *(see `12-diagram-governance-convergence-gate-core-068.md`)*:
  violation counter dropping to zero, gold seal stamping "SHIP APPROVED"
- **Sweep completeness** *(see `06-diagram-governance-sweep-completeness-core-064.md`)*:
  every open issue in the catalogue ticked CLOSED before the gate opens
