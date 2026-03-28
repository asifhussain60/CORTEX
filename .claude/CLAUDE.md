# CORTEX Claude Code Instructions

@../.github/copilot-instructions.md

## 🎯 Singular Entry Point

`/cortex` is the one command for all CORTEX operations across all surfaces.

- **Claude Code CLI:** `/cortex [intent]` → `.claude/commands/cortex.md` → routes via IntentRouter
- **VS Code Copilot:** `/cortex [intent]` → `.github/skills/cortex/SKILL.md` → same routing
- **Cowork:** CORTEX skill auto-triggers on any CORTEX keyword or command

Do not invoke domain skills directly. All requests flow through `/cortex` → MasterOrchestrator.

## Runtime Positioning
- Claude Code is the primary execution backbone.
- CORTEX must preserve dual-surface compatibility with VS Code Copilot artifacts under `.github/`.

## Core Rules
- Enforce CORE-002, CORE-008, CORE-035, CORE-048, CORE-064, CORE-068.
- Never claim production readiness without evidence-backed validation.
- Prefer minimal deterministic edits; avoid policy duplication.

## Required Validation
- `python3 scripts/run_tests.py preflight`
- `python3 scripts/run_tests.py smoke`

## Backbone Artifacts (Required)
- `.claude/settings.json`
- `.claude/commands/cortex.md`
- `.claude/rules/*.md`
- `.claude/agents/.cortex-agents-readme`
- `.claude/skills/*/SKILL.md`
