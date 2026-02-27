# Video Prompt 03 **Narration:** "The word 'intelligence' is doing a lot of work in AI right now — much of it dishonest. Here's what CORTEX's intelligence actually is, and equally importantly, what it isn't."ligence Engine

> **Duration:** 8 minutes · **Audience:** Product Owners → Software Engineers (bridge)
> **Depth:** 🟡→🔴 Starts conceptual, ends with real analysis output
> **No overlap:** Image prompt-03 shows LENS anatomy; this video shows LENS performing a *live scan* with results building in real-time, plus how the Brain tiers make decisions

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create an 8-minute animated explainer video titled **"The Intelligence Engine"**. Show how CORTEX *thinks* — from understanding a workspace to generating recommendations.

### Scene 1 — What "Intelligence" Means (0:00 – 1:30)

**Open on:** The word "Intelligence" in Space Grotesk. It shimmers between cyan and purple.

**Clarification:** Cross out "Neural Network" (red strikethrough), cross out "Machine Learning Model" (red strikethrough). Replace with: **"Heuristic + LLM-Orchestrated Pipelines"** in cyan.

Glassmorphic info card: "CORTEX doesn't contain AI models. It orchestrates your existing AI — structuring problems, routing to specialists, and validating results."

**Diagram builds:** LLM (large orb at top) → CORTEX sends structured prompts UP → LLM sends results DOWN → CORTEX validates, routes, applies.

**Analogy:** *"CORTEX is not the surgeon — it's the operating room coordinator who hands the surgeon the right tools at the right time."*

### Scene 2 — LENS: The Diagnostic Scan (1:30 – 3:30)

**LENS acronym builds** letter by letter:
- **L**anguage → File extensions light up by language (`.py` cyan, `.yaml` amber, `.ts` purple)
- **E**xamination → Magnifying glass scans files; complexity scores float out
- **N**avigation → Dependency graph materializes — nodes are files, edges are imports
- **S**ynthesis → All data compresses into a unified "workspace profile" card

**Live scan animation (2:30–3:30):** A realistic workspace file tree appears. LENS beam sweeps top-to-bottom. As it passes each area, badges appear: orchestrator count, test coverage percentage, governance rule status, dependency health. Results aggregate into a **Workspace Intelligence Card**.

**Narration:** "By the time you've typed a request, LENS already knows which files are involved, what patterns they use, and what the test coverage looks like. That context is what separates a useful response from a generic one."

### Scene 3 — The Three Brain Tiers (3:30 – 5:00)

**From the workspace profile, the three tiers activate sequentially:**

**Tier 1 — Perception (cyan):**
- Enterprise pattern icons light up as signatures match: Mediator, Strategy, Observer, Factory, etc.
- Each matched pattern shows a confidence score (0.0 – 1.0)
- "What patterns exist in this code?"

**Tier 2 — Reasoning (purple):**
- A strategy ranking table materializes. Strategies sorted by historical success rate.
- Candidate strategies: "tdd-incremental" (89%), "refactor-extract-service" (76%), "security-audit-first" (92%)
- "Which approach will work best based on past outcomes?"

**Tier 3 — Action (amber):**
- A step-by-step execution plan with numbered steps, TDD gates between each, and rollback checkpoints
- "How exactly should we execute this?"

**Narration:** "Perception reads the signals. Reasoning selects the strategy. Action builds the plan. Three tiers, working in sequence — and the difference between each tier is the difference between a guess and a judgment."

### Scene 4 — Intelligence in Action: Repository Onboarding (5:00 – 7:00)

**Scenario:** `/onboard https://github.com/example/project`

**Step-by-step:**

1. **Clone & Scan** — Repository appears as a glass cube. LENS beam scans it. File counts, language distribution, and structure materialize.

2. **Security Assessment** — Three priority tiers as concentric shields:
   - P0 (red): "Hardcoded API key in config" — flashing danger
   - P1 (amber): "No input sanitization in API routes"
   - P2 (blue): "Dependencies need updating"

3. **Pattern Detection** — Enterprise patterns detected with confidence scores. Architecture diagram auto-generates.

4. **Dashboard Generation** — Findings compress into a database icon. A glassmorphic dashboard materializes with charts, tables, health scores.

**Narration:** "A security finding at onboarding costs minutes to fix. The same finding in production costs days of incident response, customer trust, and sleep. That's the real value of what you just watched."

### Scene 5 — Closing: Intelligence You Can Trust (7:00 – 8:00)

Three trust principles as glassmorphic cards:

1. **Transparent** — "Every recommendation traces back to evidence" (citation animation)
2. **Governed** — "Governance rules validate every intelligence output" (shield shimmer)
3. **Learning** — "Outcomes feed back to improve future confidence scores" (circular arrow)

**Closing text:** **"Intelligence isn't magic. It's orchestrated methodology."**

**Narration:** "Every output from this system traces back to evidence — a pattern, a rule, a historical outcome. That traceability is what makes it trustworthy, not just impressive."

---

## Notes
- This video bridges product owners and engineers — starts conceptual, ends with real output
- The LLM-orchestration diagram in Scene 1 prevents the "embedded AI" misconception
- Repository onboarding in Scene 4 is a practical capability that makes CORTEX immediately useful
- **No hardcoded counts** — analyzers and patterns described by function, not number
