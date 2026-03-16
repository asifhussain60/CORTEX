---
name: cortex-governance
description: 'CORTEX governance skill. Enforce CORE contracts, validate architecture drift locks, and preserve deterministic production-readiness behavior across execution surfaces.'
argument-hint: 'governance audit | governance enforce | governance drift-check'
---

# CORTEX Governance Skill

Use this skill to enforce governance contracts for prompts, agents, skills, workflows, and runtime validators.

## Responsibilities

- Enforce CORE contracts as non-negotiable rules.
- Validate drift locks for prompts, agents, and registry constants.
- Keep dual-surface behavior deterministic between Claude and GitHub surfaces.
- Block release when P0 governance violations exist.

## Primary Validation Commands

- `python3 scripts/validate_governance_alignment.py`
- `python3 scripts/validate-architecture-counts.py`
- `python3 scripts/run_tests.py preflight`

## Collaboration Contract

- Route code-modifying actions through TDD workflows.
- Route orchestration checks through Workflow Composer templates.
- Keep this skill aligned with `.claude/skills/cortex-governance/SKILL.md`.
