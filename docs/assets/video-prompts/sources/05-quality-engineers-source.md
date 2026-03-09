> **Diagram references** — filenames below resolve from `docs/assets/diagrams/`.
> Update any diagram file in place; this source requires no edits.
> - Testing pyramid: `07-diagram-testing-testing-strategy-pyramid.md`
> - Code review pipeline: `16-diagram-quality-code-review-multi-pass-pipeline.md`
> - Quality scoring: `18-diagram-quality-analysis-engine-scoring-dashboard.md`
> - Convergence gate: `12-diagram-governance-convergence-gate-core-068.md`
> - Sweep completeness: `06-diagram-governance-sweep-completeness-core-064.md`

# CORTEX for Quality Engineers — Source Document
## Video 05 · Audience: Quality Engineers & QA Leads

**Purpose:** NotebookLM source for steering prompt `05-quality-engineers-steering.md`.
Synthesised from `docs/.content/04-tdd-quality-flywheel.md`,
`docs/.content/02-intelligence-how-cortex-understands-code.md`, and
`docs/.content/03-governance-quality-that-enforces-itself.md`.

---

## The Quality Engineer's Burden

Quality engineers are asked to be the last line of defence for systems
they had no part in designing. Manual test matrices that nobody updates.
Regression suites that take 4 hours and still miss the regression that matters.
Flaky tests that everyone ignores until they can't. A "quality gate" that
is really just a checkbox.

CORTEX treats quality as a first-class engineering concern — designed in,
not tested in.

---

## What CORTEX Does for Quality Engineers

### Golden Tests — Quality as Proof, Not Opinion

CORTEX distinguishes golden tests from ordinary tests. A golden test
protects a critical business rule. It is not just an assertion — it is
a link in a chain:

```
Business Rule → Acceptance Criterion → Golden Test → CI Green
```

Each golden test card (see `07-diagram-testing-testing-strategy-pyramid.md`)
glows with the business rule it protects. When a golden test fails, the
business rule it protects is surfaced immediately — engineers know exactly
what they broke and why it matters.

### Quality Radar — Five Dimensions, One Score

CORTEX's quality analysis engine scores every codebase across five dimensions:
correctness, maintainability, testability, security, and performance.
The radar chart (see `18-diagram-quality-analysis-engine-scoring-dashboard.md`)
fills each axis in sequence to a composite score. The weakest dimension
flashes amber — not as a failure, but as a growth signal. The QE sees where
to invest next.

### Response Rendering Rules — Quality at the Output Layer

Phase 146 adds 14-rule Response Rendering validation — every CORTEX output
is validated against formatting constraints before it leaves the system.
Quality gates are not just at the input (pre-commit) and the pipeline (CI)
— they are at the output layer too. Nothing ships without passing the
rendering contract.

### Convergence Gate — No Partial Sweeps

CORTEX's Sweep Completeness Contract (CORE-064) is a governance rule:
every issue in the sweep catalogue must reach status CLOSED before the
sweep can complete. No partial passes. No deferred items.

The convergence gate (CORE-068) enforces this with a detect → fix → rescan
loop that iterates until `p0_count == 0 and p1_count == 0`. The SWEEP COMPLETE
gold seal stamps only when every issue is resolved.

---

## Role Propositions

| Proposition | Evidence |
|-------------|---------|
| Quality by design | Golden tests trace to business rules — quality is designed in, not tested in |
| Visible quality debt | 5-dimension radar chart makes quality debt tangible and directional |
| No escaped defects | CORE-068 convergence loop iterates until all issues resolved |
| No partial passes | CORE-064 Sweep Completeness Contract — every catalogue item CLOSED |
| Output quality enforced | 14-rule Response Rendering validation at the output layer (Phase 146) |

---

## Suggested Quotes (for narrator use)

> "Quality is not an act, it is a habit." — Aristotle (via W. Durant)

> "The best way to get a project done faster is to start out by making
> sure you're headed in the right direction." — W. Edwards Deming,
> *Out of the Crisis*

> "Testing shows the presence of bugs, not their absence."
> — Edsger W. Dijkstra

---

## Visual Cues for NotebookLM

- **Golden test card** *(see `07-diagram-testing-testing-strategy-pyramid.md`)*:
  card materialises with gold border, business rule text appears at top,
  test name below, green badge stamps — chain complete
- **Quality radar** *(see `18-diagram-quality-analysis-engine-scoring-dashboard.md`)*:
  five axes extending one by one; composite score 87/100 appears; weakest
  axis flashes amber with label "Growth opportunity: Testability"
- **Multi-pass code review** *(see `16-diagram-quality-code-review-multi-pass-pipeline.md`)*:
  PR enters pipeline; 3 review passes with distinct gate icons; final
  quality gate stamps APPROVED before merge
- **Convergence gate** *(see `12-diagram-governance-convergence-gate-core-068.md`)*:
  three rings — detect (red), fix (amber), rescan (green); violation counter
  15 → 8 → 2 → 0; SWEEP COMPLETE gold seal stamps; 1.5s strategic silence
- **Sweep catalogue** *(see `06-diagram-governance-sweep-completeness-core-064.md`)*:
  issue list with status — OPEN → IN PROGRESS → CLOSED — every row must
  reach CLOSED before gate opens
