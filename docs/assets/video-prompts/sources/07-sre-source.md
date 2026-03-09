> **Diagram references** — filenames below resolve from `docs/assets/diagrams/`.
> Update any diagram file in place; this source requires no edits.
> - Audit pipeline: `04-diagram-audit-audit-fix-pipeline.md`
> - Convergence gate: `12-diagram-governance-convergence-gate-core-068.md`
> - Threat model / STRIDE: `17-diagram-security-threat-model-stride-analysis.md`
> - Vacuum source protection: `21-diagram-governance-vacuum-source-protection.md`

# CORTEX for Site Reliability Engineers — Source Document
## Video 07 · Audience: Site Reliability Engineers

**Purpose:** NotebookLM source for steering prompt `07-sre-steering.md`.
Synthesised from `docs/.content/10-infrastructure-built-to-last.md`,
`docs/.content/08-learning-institutional-memory.md`, and
`docs/.content/03-governance-quality-that-enforces-itself.md`.

---

## The SRE's Nightmare

3 AM. Production is down. The runbook points to a service that was
refactored six weeks ago. The on-call engineer has been paged for the
third time this month for a failure that matches an incident from last
quarter — different surface, same root cause. The institutional memory
that would have prevented this left with the engineer who fixed it the
first time.

CORTEX makes institutional memory a system component, not a person.

---

## What CORTEX Does for SREs

### Health Orchestrator — Continuous, Not Periodic

CORTEX's Health Orchestrator monitors 350+ components in real time.
Not periodic polling — continuous signal. Anomalies surface before they
become incidents. The health dashboard shows the state of the system as
it is, not as it was 5 minutes ago when the last poll ran.

Every health endpoint is implemented by a dedicated orchestrator.
Every component has an observable health contract. Nothing is assumed healthy.

### RCA Memory Engine — Four Methodologies, One Memory

When an incident occurs, CORTEX's RCA Memory Engine selects the right
analysis methodology automatically based on incident category:

| Category | Methodology |
|----------|-------------|
| Technology failures | Five-Whys |
| Process / people factors | Fishbone (Ishikawa) |
| Safety-critical failures | Fault-Tree Analysis |
| Sequential causation | Causal-Chain |

Every completed RCA generates a Prevention Rule. That rule is stored in
the institutional memory (see `17-diagram-security-threat-model-stride-analysis.md`
for threat-surface context). The next time the same incident pattern surfaces,
CORTEX recognises it and surfaces the prevention rule before the engineer
even opens a runbook.

MTTR: from 4 hours to 12 minutes.
Recurrence: zero for any catalogued pattern.

### Vacuum Pipeline — Self-Healing Workspace

The Vacuum pipeline (Phase 141) is an 8-stage autonomous guardian running
on the workspace continuously. It handles:

1. Naming violations (snake_case enforcement)
2. Root clutter (stray files at repo root)
3. Empty files and directories
4. Orphan modules (unreachable imports)
5. Markdown sprawl (undiscoverable documentation)
6. Digest consolidation (stale content archives)
7. Build artefacts (leftover compiled output)
8. OS artefacts (`.DS_Store`, `Thumbs.db`, etc.)

15 source directories are permanently protected by SHA validation and
8 golden tests. Before every sweep, a git checkpoint creates a safe
rollback point. Workspace health stays at 100%.

---

## Role Propositions

| Proposition | Evidence |
|-------------|---------|
| Incidents found before users do | Health Orchestrator: 350+ components, continuous signal |
| MTTR: 4 hours → 12 minutes | RCA Memory Engine + four methodologies + automatic methodology selection |
| Recurrence: zero | Prevention Rules stored in institutional memory, surfaced automatically |
| Self-healing workspace | Vacuum 8-stage pipeline, 15 protected dirs, SHA validation, git rollback |
| Compliance without manual effort | 60+ governance rules enforced at pre-commit, CI, runtime — automated |

---

## Suggested Quotes (for narrator use)

> "Hope is not a strategy." — Google SRE Book

> "The goal of SRE is to make the work of reliability engineering
> sustainable by eliminating toil." — Niall Richard Murphy,
> *Site Reliability Engineering*

> "An ounce of prevention is worth a pound of cure." — Benjamin Franklin

---

## Visual Cues for NotebookLM

- **Health dashboard** *(implied by `04-diagram-audit-audit-fix-pipeline.md`)*:
  350+ component tiles pulsing green; one amber tile highlights — anomaly
  detected before incident; counter "Anomalies surfaced pre-incident: 12"
- **RCA tree building** *(see `17-diagram-security-threat-model-stride-analysis.md`
  for threat context)*: branching node animation — root cause node glows
  red, prevention rule materialises at the leaf, stored in memory bank
- **Incident timeline** *(see `12-diagram-governance-convergence-gate-core-068.md`)*:
  dark tense bar with MTTR ticking up; CORTEX activates; bar resolves to
  calm green; "MTTR: 12 minutes" badge materialises
- **Vacuum pipeline conveyor** *(see `21-diagram-governance-vacuum-source-protection.md`)*:
  8-station belt — files entering left, each station stamps action (RENAMED,
  ARCHIVED, DELETED, PROTECTED); workspace health badge fills to 100%;
  SHA shield glows over 15 protected directories
