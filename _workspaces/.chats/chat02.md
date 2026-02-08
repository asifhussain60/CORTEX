# CORTEX CHANGE REQUEST — Fix Copilot Chat Verbosity + Enforce 3-Section Business Summary + Ban Markdown Report Files

Follow instructions in #file:.github/prompts/cortex-architect.prompt.md and all applicable governance rules in the active CORTEX phase registry.

## Objective
Update CORTEX so that, during autonomous plan execution in VS Code GitHub Copilot Chat Sessions, Copilot responses:
1) stay **high-signal and concise** (no “in the weeds” narration),
2) consolidate findings/challenges/recommendations into **no more than 3 sections**, written in **easy business language** for **all roles** (Business Leaders, Product Owners, Production Owners, Engineers), using the **LLM Business Language Orchestrator**, and
3) **aggressively prevent** creation of markdown report files (summaries, completion reports, status docs). All reporting is **inline in chat only**.

---

## Hard Constraints (Non-Negotiable)
1. **Inline-only reporting**: All progress, findings, challenges, recommendations, and completion info must be presented inline in the Copilot Chat response. No “final report” documents.
2. **Aggressive markdown ban for reporting artifacts**:
   - Do **not** create/update/generate ANY markdown files as reports, summaries, progress logs, completion docs, post-run writeups, or execution plans.
   - Specifically forbidden patterns (report intent):
     - `**/report*.md`, `**/summary*.md`, `**/*status*.md`, `**/*completion*.md`, `**/*progress*.md`, `**/*run*.md`, `**/docs/**.md` when created for reporting
   - If documentation already exists and must be updated for product correctness, do so only when explicitly required by acceptance criteria. Otherwise, keep docs unchanged.
3. **No preference questions**: After “continue autonomously”, the only valid forward path is **PROCEED**. Do not offer options, menus, or “which approach do you prefer?”
4. **No stubs**: Implement fully or mark blocked with a single targeted question (only if truly hard-blocked).
5. **File write minimization**: Touch only files required to implement the UX/policy enforcement.

---

## Deliverable
A working CORTEX implementation that automatically enforces:
- **3-section business summary responses**
- **Plan execution progress that is concise and scan-friendly**
- **Markdown report artifact prevention**
…across all orchestrators/agents used in plan execution.

---

## Required Chat Response Contract (MANDATORY)

### A) Response Structure (Exactly 3 Sections)
Every Copilot response during plan execution must contain ONLY these three sections, with short bullets:

#### 1) What was asked
- 2–5 bullets max
- Plain language summary of the user request and scope

#### 2) What’s recommended and why
- 3–7 bullets max
- Consolidate: findings, risks, challenges, key decisions already made, and recommendations
- Must be role-inclusive language (Business/PO/Prod/Engineering)
- No deep technical step-by-step unless absolutely required (keep tech details as short bullets)

#### 3) Next steps (PROCEED only)
- 1–4 bullets max
- Must end with a single directive:
  - `Next Step: PROCEED`
- No alternative paths, no choices, no “Option 1/2/3”, no questions unless hard-blocked

> If blocked, still use the 3 sections, but in section 3 include exactly one blocking question and a default:
> `BLOCKED: <reason>. Default if no answer: <default>. Next Step: PROCEED`

---

## Required Concise Progress UX (Embedded, Not a 4th Section)
If progress must be shown, it must be compact and embedded inside section 2 as a short bullet, not as a separate section, and never longer than ~8 lines.

Use this ASCII Plan Spine format:

Glyphs:
- `[✓]` completed
- `[→]` active
- `[!]` blocked
- `[~]` revisiting
- `[ ]` not started

Example (must remain short):
Plan Progress:
├─ [✓] Phase 1 Profile schema & store
├─ [→] Phase 2 KSESSIONS onboarding (active)
├─ [ ] Phase 3 MCP gateway
└─ [ ] Phase 4+ remaining


Do NOT print large banners, tables, “read file…” narration, or long step logs.

---

## Aggressive Prevention: Markdown Report File Generation

### Requirements
1. Identify all current pathways where CORTEX/Copilot generates “helpful” markdown outputs:
   - completion summaries
   - progress reports
   - execution logs
   - documentation bursts created during/after execution
   - any agent that writes `_workspaces/.../*.md` or `docs/.../*.md` as run artifacts
2. Implement a centralized enforcement layer:
   - `FileWritePolicy` or `ArtifactPolicy` (name flexible)
   - Intercepts any tool/agent action that writes files
   - Blocks markdown writes when the intent is reporting/progress/summary/completion
3. When blocked, output inline error guidance (chat only):
   - “Inline chat output only. Do not create markdown summary/report files.”
4. If persistent reporting is truly required internally:
   - prefer existing audit logs or DB event trail
   - otherwise JSON in an existing non-report store only when necessary
   - never markdown

### Test Coverage (Minimum)
Add unit tests validating:
- Attempted markdown report generation is rejected (at least 5 representative patterns)
- Responses contain exactly 3 sections (basic heuristic ok)
- “Next steps” contains only `PROCEED` (and no options)
- Plan spine glyph set is enforced (no random emojis/banners)

---

## Behavior Suppression Rules (Stop the “Weeds”)
The following must be suppressed from Copilot chat outputs:
- “Let me read…”, “Perfect!”, “Great!”, “Now I will…”
- tool call narration (“Read file…”, “Searched for…”, “Using Replace String…”, etc.)
- long tables (discouraged)
- repeated headers each turn
- “Due to length and complexity, here is a comprehensive summary…” (NO comprehensive summaries)

Instead, consolidate into business bullets.

---

## Implementation Instructions
1. Locate where CORTEX forms Copilot responses:
   - response templates
   - orchestrator message builders
   - agent output formatters
2. Introduce a `ChatResponsePolicy` (name flexible) that:
   - enforces exactly 3 sections
   - routes wording through the **LLM Business Language Orchestrator**
   - compresses technical narration into plain-language bullets
   - injects compact Plan Spine only when necessary
   - removes preference prompts (Options/Which do you prefer)
   - forces `Next Step: PROCEED`
3. Introduce a `MarkdownReportBanPolicy` that:
   - blocks report-intent markdown file creation
   - blocks auto-generation of docs during execution unless explicitly required
4. Wire both policies into:
   - MasterOrchestrator
   - any agent that emits progress/finalization output
   - any tool wrapper that can write files
5. Run targeted tests. Do not create new report docs.

---

## Acceptance Criteria
- All autonomous plan execution chat responses follow EXACTLY the 3-section structure.
- Language is business-friendly and role-inclusive (Business/PO/Prod/Engineering).
- “Next steps” contains only `Next Step: PROCEED` and no alternative choices.
- No markdown report files are created (summaries, completion reports, progress logs).
- Attempts to create report markdown are blocked with a clear inline directive.
- Unit tests validate the formatting and markdown-ban policy.

---

## Execute
Proceed with implementation now. Do not pause to ask for preferences. Only ask a question if truly hard-blocked, and still end with `Next Step: PROCEED`.
