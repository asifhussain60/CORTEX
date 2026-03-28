# CORTEX — Singular Entry Point

**This is the one command that routes everything.**

Load the full CORTEX framework and execute the request below.

@../../.github/skills/cortex/SKILL.md

---

## User Request

$ARGUMENTS

---

## Routing Contract

If `$ARGUMENTS` is empty or contains only `/cortex`, render the CORTEX introduction:
- Display the 🧠 CORTEX header
- List the 20 available commands with one-line descriptions
- Show the DoR gate and proceed instructions
- End with `⚡ If you say proceed [intent], I will:` + top 3 recommended next actions

If `$ARGUMENTS` contains a natural-language request, classify intent via IntentRouter and execute the appropriate domain orchestrator directly. No additional user prompt needed.

## Command Pass-Through

Any CORTEX sub-command typed as `/cortex [command]` is equivalent to typing `[command]` directly:

| Typed | Equivalent |
|---|---|
| `/cortex audit fix` | `/audit fix` |
| `/cortex implement {desc}` | `/implement {desc}` |
| `/cortex fix {desc}` | `/fix {desc}` |
| `/cortex debug {path}` | `/debug {path}` |
| `/cortex rca {failure}` | `/rca {failure}` |
| `/cortex plan` | `/plan` |
| `/cortex review {pr}` | `/review {pr}` |
| `/cortex vacuum` | `/vacuum` |
| `/cortex health` | `/health` |
| `/cortex totalrecall` | `/totalrecall` |
| `/cortex refactor {desc}` | `/refactor {desc}` |
| `/cortex onboard {path}` | `/onboard {path}` |
| `/cortex challenge {req}` | `/challenge {req}` |
| `/cortex distill {file}` | `/distill {file}` |
| `/cortex digest {path}` | `/digest {path}` |
