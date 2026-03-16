---
name: cortex-rca
description: 'CORTEX root-cause analysis skill. Run structured RCA for recurring failures and convert findings into prevention rules and workflow-safe remediation plans.'
argument-hint: 'rca <failure> | rca analyze | rca prevention'
---

# CORTEX RCA Skill

Use this skill for rigorous root-cause analysis across implementation, debugging, and operations workflows.

## Methods

- Five-Whys
- Fishbone
- Fault-Tree
- Causal-Chain

## Execution Contract

- Start from runtime evidence and validation output.
- Identify root cause before proposing fixes.
- Convert recurring failure patterns into prevention guidance.
- Keep remediation plans aligned with TDD and Workflow Composer governance.

## Entry Points

- `cortex/intelligence/learning/rca_engine.py`
- `cortex/mcp/tools/learning_tool.py` (`op=rca`)
- `.github/skills/cortex-debug/SKILL.md` (debug + RCA integration)
