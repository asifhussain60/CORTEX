# CORTEX Claude Code Instructions

@../.github/copilot-instructions.md

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
- `.claude/rules/*.md`
- `.claude/agents/.cortex-agents-readme`
- `.claude/skills/*/SKILL.md`
