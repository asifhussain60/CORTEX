---
name: cortex-claude-readiness
description: 'Claude-primary production readiness skill for CORTEX. Use when: verifying or fixing Claude Code backbone wiring, enforcing dual-surface compatibility, remediating prompt-agent-skill drift, and certifying P0/P1 convergence before release.'
argument-hint: 'audit | fix | certify | challenge'
---

# CORTEX Claude Readiness Skill

**Intent:** Make Claude Code the primary backbone without losing production safety across CORTEX execution surfaces.

## When to Use

Use this skill for:
- Claude backbone readiness checks (`.claude/` + `CLAUDE.md`)
- Prompt/agent/skill wiring verification
- Automated fix plans for production-readiness drift
- Final certification that requires `P0=0` and `P1=0`

## Challenge & Recommendation

If asked for Claude-only architecture, challenge with a safer alternative:

- **Requested path:** Claude-only primary backbone
- **Recommended path:** Claude-primary with Copilot-compatible fallback
- **Why:** Keeps one primary runtime while preserving execution continuity, governance portability, and reduced blast radius during tool/runtime outages

## Execution Contract

1. Run readiness audit and build gap catalogue
2. Classify findings by severity (P0/P1/P2)
3. Apply minimal deterministic fixes
4. Re-scan until convergence (`detect-fix-rescan`, max 3 loops)
5. Gate completion on preflight + zero P0/P1

## Validation Commands

- `python3 scripts/run_tests.py preflight`
- `python3 scripts/run_tests.py smoke`
- `python3 scripts/validate-production.py` (if scope includes release certification)

## Required Artifacts

- `.claude/settings.json`
- `CLAUDE.md` or `.claude/CLAUDE.md`
- `.claude/rules/*.md` for path-scoped governance
- `.claude/agents/*.md` and/or `.github/agents/**/*.md` with coherent routing
- `.github/skills/cortex-claude-readiness/SKILL.md` (this file)

## Related Agent

- `.github/agents/support/cortex-claude-readiness-agent.md`
