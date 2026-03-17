---
name: cortex-architecture-review
description: 'CORTEX architecture review skill. Use when: running architecture review, tutorial mode review, Claude backbone review, cross-cutting YAML review, explainability review, regression comparison against origin/CORTEX, or capacity and consolidation analysis. Covers runtime architecture, prompts, agents, skills, governance, knowledge YAMLs, LENS, onboarding, SQLite tracing, and tooling-footprint reduction.'
argument-hint: 'architecture review | tutorial mode | claude backbone | origin/CORTEX | consolidation'
---

# CORTEX Architecture Review Skill

Use this skill to run repeatable, holistic architecture reviews of CORTEX with the same rigor expected from audit and Claude-readiness work.

---

## Review Goals

The review MUST determine whether CORTEX is operating at full capacity across:
- runtime architecture
- prompt/agent/skill composition
- Claude-primary execution
- Tutorial Mode and explainability
- governance and registry cross-cuts
- knowledge YAML quality and actual usage
- onboarding and LENS intelligence
- test and golden coverage
- SQLite traceability and observability
- historical regression resistance
- simplification and footprint reduction

---

## Evidence Sources

Always gather evidence from:
- `cortex/`
- `.github/prompts/`
- `.github/agents/`
- `.github/skills/`
- `.github/templates/`
- `.claude/`
- `cortex-registry/core/`
- `cortex-registry/governance/`
- `cortex-registry/workflows/`
- `cortex-registry/knowledge/`
- `tests/`
- `scripts/`
- git history and `origin/CORTEX`

Never rely on a single surface.

---

## Review Pipeline

### 1. Baseline

- Establish current execution model from runtime code and active prompt surfaces.
- Identify the canonical entry points, routing layers, and response-format authorities.

### 2. Cross-Cutting Matrix

Build a matrix for these concerns:
- orchestration and routing
- agent/subagent delegation
- skill discovery and loading
- Tutorial Mode decision tracing
- knowledge YAML reachability
- governance and workflow YAML enforcement
- LENS and onboarding intelligence
- response template usage
- SQLite logging and trace persistence
- tests and golden coverage
- tool footprint and duplication

### 3. Tutorial Mode Review

Verify:
- trigger wiring
- explanation quality
- decision-to-knowledge mapping
- template consistency
- parity of truth between tutorial and normal modes
- golden test coverage for outputs

### 4. Historical Regression Review

Compare current state to `origin/CORTEX` and recent branch history.

Always distinguish:
- intentional simplification
- migration drift
- capability loss
- naming-only change

### 5. Consolidation Review

Identify opportunities to reduce:
- prompt sprawl
- agent duplication
- redundant skill layers
- registry duplication
- overlapping explanation pathways
- tool and token footprint

---

## Finding Format

Every finding MUST include:
- severity: `critical`, `high`, `medium`, `low`
- why it matters
- evidence
- recommended fix

Prioritize developer trust, explainability truthfulness, governance coherence, and regression containment.

---

## Output Shape

1. Executive Summary
2. Architecture Review
3. Implementation Review
4. Agent / Subagent / Skill Model Review
5. Onboarding and Repo Analysis Review
6. Tutorial Mode & Explainability Review
7. Testing Review
8. SQLite Logging Review
9. Archived Branch Comparison
10. Consolidation Plan
11. Prioritized Action Plan
12. Appendix

Findings come before summary commentary.

---

## Reuse Contract

When rerunning this skill after new enhancements:
- inspect the new delta through git history
- identify newly introduced prompts, agents, skills, workflows, YAMLs, tests, and runtime paths
- rescan the surrounding cross-cuts, not only the changed files
- verify that Tutorial Mode, knowledge usage, governance, and logging were updated with the change
- record net gains, regressions, and new duplication introduced by the enhancement

This skill is for recurring architecture health reviews, not a one-off snapshot.

---

## Validation

If the review results in file changes, run:
- `python3 scripts/run_tests.py preflight`
- `python3 scripts/run_tests.py smoke`