---
applyTo: ".github/**/*.md"
---

# CORTEX Prompt & Agent Rules

**These rules apply when editing prompts, agents, or templates under `.github/`.**

## Response Header
- Product icon is FIXED: 🧠 for `CORTEX.prompt.md`, 🛠️ for `cortex-architect.prompt.md`
- Never use mode-specific icons (⚡ 🔧 ♻️) in H1 headings
- Author line verbatim: `**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.`
- No `**Orchestrator:**` or `**Via:**` fields — use `🧭 Orchestration:` only

## Language Rules
- Use imperative verbs in governance sections: MUST, SHALL, ALWAYS, NEVER
- No hedging language: never use 'may', 'might', 'could', 'optionally', 'if available'
- Business language for violations: explain what the rule prevents, not just the code

## Deleted Path References — NEVER use these
- `cortex/brain/`, `cortex/cortex.intelligence/`, `cortex_intelligence/`, `cortex_lens/`, `_archive/`
- `cortex_process_request`, `cortex_lens_analyze`, `cortex_manage_todo` (removed MCP tools)
- Phase 49 / CCL / `CrystallizedContext` (removed constructs)

## Counts — Keep Current
- Use `python3 scripts/refresh_prompt_suite.py --counts-only` for live orchestrator/tool/test counts
- Never hard-code counts without verifying against the live codebase first

## V2 Conventions
- Treat prompt/agent/skill references as consolidated surfaces (avoid references to retired split ownership)
- Prefer SSOT references over duplicated policy blocks
- Keep routing aligned with the 5-skill model (`cortex`, `cortex-tdd`, `cortex-audit`, `cortex-debug`, `cortex-plan`)

## All Output Inline (CORE-002)
- Never create `.md` or `.txt` report files from prompt/agent operations
- All output renders directly in Copilot Chat
