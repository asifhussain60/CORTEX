# NotebookLM Video Steering Prompts — CORTEX Cinematic Explainer Series

**Series:** CORTEX — The Governed AI Engineering Partner
**Videos:** 5 (one per role)
**Visual Style:** Whiteboard (selected in NotebookLM Customise Video Overview dialog)
**Duration Target:** 7–10 minutes per video
**Generator:** Google NotebookLM → Customise Video Overview → paste prompt below → Generate

> **How to use:** Open NotebookLM, load the relevant sources listed under each video,
> open "Customise Video Overview", select **Whiteboard** visual style, paste the
> steering prompt into "What should the AI hosts focus on?", then click **Generate**.

---

## 🎬 VIDEO 1 OF 5 — Platform Introduction (All Roles)

**Sources to load in NotebookLM:**
- `docs/assets/video-prompts/01-video-prompt-what-is-cortex.md`
- `docs/.content/01-platform-what-is-cortex.md`
- `docs/.content/02-intelligence-how-cortex-understands-code.md`
- `docs/.content/03-governance-quality-that-enforces-itself.md`
- `docs/.content/05-orchestration-the-engine-room.md`
- `docs/assets/diagrams/01-diagram-architecture-system-architecture-layers.md`
- `docs/assets/diagrams/11-diagram-intelligence-lens-analysis-pipeline.md`
- `docs/assets/diagrams/12-diagram-governance-convergence-gate-core-068.md`
- `_workspaces/recommendations/mission-statement.md`

**Steering Prompt — paste into "What should the AI hosts focus on?":**

```
This is a 7–10 minute cinematic executive explainer for C-suite leaders, VPs of Engineering, and business stakeholders who own delivery risk.

Start with the problem: modern software ecosystems are vast, most engineers operate with only fragments of the full picture, and AI tools today make teams type faster without guardrails — creating invisible technical debt. Name the hidden force slowing great teams: Fear. Fear of breaking production. Fear of changing legacy systems. Fear of costly architectural mistakes.

Then introduce CORTEX as an advanced orchestration framework — not a replacement for GitHub Copilot, but an intelligence layer that sits around it. Transform raw generative AI into a governed engineering partner that thinks, enforces, learns, and executes.

Structure the body around three pillars from the mission:

PILLAR 1 — UNDERSTAND EVERYTHING: Show the System Architecture Layer view and LENS Intelligence Pipeline. CORTEX reads the entire repository before a single line is written — understanding enterprise patterns, security posture, and domain rules. Quote Deming: "It is not enough to do your best; you must know what to do, and then do your best."

PILLAR 2 — EMPOWER EVERYONE: Show the Intelligence Diamond. CORTEX is a network of 290+ specialised reasoning engines in the IDE. For engineers: senior pair-programmer with TDD enforcement. For architects: automated guardian of design patterns. For product owners: backlog turned into traceable delivery. For business leaders: rigorous auditability on every commit. Quote Covey: "An empowered organization is one in which individuals have the knowledge, skill, desire, and opportunity to personally succeed."

PILLAR 3 — BUILD FEARLESSLY: Show the Universal Convergence Gate (CORE-068). Governance as infrastructure, not friction. Detect → fix → rescan loop. Threat models before production. RCA memory preventing repeat failures. Quote Collins: "Technology is an accelerator of momentum, not a creator of it."

Close with strategic silence, then: "CORTEX doesn't make AI smarter. It makes AI-assisted development accountable — at every step, for every team member, in every commit." End tagline: Governance. Orchestration. Reliability.

Narrator: female, calm, authoritative, unhurried. Allow quotes to land. No dramatic music stings. Ambient synth bed at 60 BPM only.
```

---

## 🎬 VIDEO 2 OF 5 — Product Owner

**Sources to load in NotebookLM:**
- `docs/assets/video-prompts/03-video-prompt-what-is-cortex-product-owners.md`
- `docs/.content/01-platform-what-is-cortex.md`
- `docs/.content/03-governance-quality-that-enforces-itself.md`
- `docs/.content/04-tdd-quality-flywheel.md`
- `docs/.content/05-orchestration-the-engine-room.md`
- `docs/.content/09-lifecycle-from-idea-to-production.md`
- `docs/assets/diagrams/03-diagram-workflow-sdlc-pipeline.md`
- `docs/assets/diagrams/05-diagram-workflow-tdd-cycle-and-fsm.md`
- `docs/assets/diagrams/06-diagram-governance-sweep-completeness-core-064.md`
- `docs/assets/diagrams/19-diagram-orchestration-po-change-intelligence-pipeline.md`
- `_workspaces/recommendations/mission-statement.md`

**Steering Prompt — paste into "What should the AI hosts focus on?":**

```
This is a 7–10 minute cinematic explainer exclusively for Product Owners, Business Analysts, Delivery Managers, and Scrum Masters. Do not include developer-centric explanations.

Start with the Product Owner's core pain: you write an acceptance criterion, the developer implements it, but does the implementation actually match what you meant? Show three outcomes that happen without CORTEX — edge case missed, fix applied in one endpoint while the bug lives in three others, and tests written after the fact covering only the happy path. Use this tension to introduce CORTEX.

Structure the content across five sections:

SECTION 1 — FROM ACCEPTANCE CRITERIA TO TESTS: Show the TDD cycle diagram. CORTEX converts every acceptance criterion into a failing test before implementation begins. The developer cannot proceed without a failing test. Walk through one concrete AC: "The system must validate email format before submission" becomes a test that fails, then implementation that passes it. No test, no code.

SECTION 2 — SWEEP COMPLETENESS (CORE-064): Show the sweep completeness diagram. When CORTEX finds an issue, it scans the entire codebase for every instance of that pattern, catalogues each occurrence, and closes all of them before declaring the sweep complete. No partial fixes. No "we'll catch the others next sprint." Show the sweep catalogue: 4 files found, 4 files fixed, sweep complete.

SECTION 3 — THE DOr TO DOD PIPELINE: Show the SDLC pipeline diagram. Walk the PO through the seven-phase lifecycle: Definition of Ready → Intent Classification → LENS Analysis → Governance Gate → TDD Red/Green/Refactor → Sweep Completeness → Definition of Done. Every phase is observable and traceable. The PO's original AC appears as evidence in the final audit trail.

SECTION 4 — PO CHANGE INTELLIGENCE PIPELINE: Show the PO Change Intelligence Pipeline diagram. Demonstrate a realistic workflow: stakeholder requests a change → CORTEX maps current application behaviour → analyses the requested change against best practice → generates implementation requirements → evaluates change impact → produces ROI insight → generates training documentation. The PO receives structured intelligence, not a developer's verbal estimate.

SECTION 5 — TRANSFORMATION: Before CORTEX: sprint velocity unpredictable, AC traceability manual, partial fixes common. After CORTEX: every AC generates tests, every fix is complete, every delivery is evidenced. Connect to the mission — "Empower Everyone" means POs get the same intelligence as senior engineers.

End with: "CORTEX transforms backlog management into decision intelligence. One platform. Your requirements. Traceable delivery." Narrator: female, calm, strategic, PO-vocabulary throughout (no class names, no file paths).
```

---

## 🎬 VIDEO 3 OF 5 — Software Engineer

**Sources to load in NotebookLM:**
- `docs/assets/video-prompts/04-video-prompt-what-is-cortex-software-engineers.md`
- `docs/.content/01-platform-what-is-cortex.md`
- `docs/.content/02-intelligence-how-cortex-understands-code.md`
- `docs/.content/04-tdd-quality-flywheel.md`
- `docs/.content/05-orchestration-the-engine-room.md`
- `docs/.content/06-mcp-tools-in-your-ide.md`
- `docs/.content/08-learning-institutional-memory.md`
- `docs/assets/diagrams/11-diagram-intelligence-lens-analysis-pipeline.md`
- `docs/assets/diagrams/05-diagram-workflow-tdd-cycle-and-fsm.md`
- `docs/assets/diagrams/09-diagram-orchestration-request-sequence.md`
- `docs/assets/diagrams/14-diagram-debugging-multi-stack-pipeline.md`
- `docs/assets/image-prompts/shared/02-lens-intelligence-pipeline.prompt.md`
- `docs/assets/image-prompts/shared/05-intelligence-diamond-three-tiers.prompt.md`
- `_workspaces/recommendations/mission-statement.md`

**Steering Prompt — paste into "What should the AI hosts focus on?":**

```
This is a 7–10 minute cinematic explainer exclusively for Software Engineers, developers, architects, and tech leads at all experience levels. Do not repeat Product Owner messaging.

Start with the contrast that engineers feel immediately: a generic AI tool responds to "implement authentication middleware" with a generic JWT snippet. CORTEX responds with a LENS analysis result — your specific OAuth2 pattern, your FastAPI version, your existing test coverage, your governance requirements — all in under one second. What comes back fits your codebase, not someone else's.

Structure the content across five sections:

SECTION 1 — LENS: NINE ANALYSERS IN PARALLEL: Show the LENS Intelligence Pipeline diagram. Walk through all nine analysers: structure, history, documentation, dependencies, security, patterns, complexity, business domain, technology stack — all running simultaneously in under one second. This is not a scan of a generic codebase. It is a scan of yours. Highlight the four-stage cycle: Language → Examination → Navigation → Synthesis.

SECTION 2 — TDD ENFORCED, NOT SUGGESTED: Show the TDD cycle FSM diagram. CORTEX verifies a failing test exists before allowing implementation. A test that passes before implementation is flagged as vacuous. Show a real example: test_auth_middleware_rejects_expired_token — FAIL before implementation, PASS after. No configuration option skips this. Every behaviour that matters is tested before it ships.

SECTION 3 — 290+ ORCHESTRATORS AND 35+ IDE TOOLS: Show the request sequence diagram. Walk through one request lifecycle: intent classification in under 40ms → LENS analysis → governance gate → TDD RED phase → implementation → sweep completeness → audit trail. Show the 35+ tools accessible directly in the IDE — no context switching, no separate dashboards.

SECTION 4 — MULTI-STACK DEBUG PIPELINE: Show the multi-stack debug pipeline diagram. Eight injection strategies: three Python and five multi-stack (Frontend, HTML-Vision, API, SQL, .NET). Markers inject, capture, analyse, produce a fix plan, and auto-clean. Engineers get structured root cause analysis, not scattered console logs.

SECTION 5 — INSTITUTIONAL MEMORY: RCA captures every failure pattern. The learning engine surfaces prior failures before engineers repeat them. When the same mistake was made three months ago, CORTEX surfaces it before the next implementation begins — with the fix that resolved it. Show the learning loop: emit → decay → promote → quarantine.

End with: "CORTEX is the senior engineering partner who has read every line of your codebase, never forgets a failure, and is always available inside your editor." Narrator: male, technical, peer-to-peer tone — not a sales pitch. Engineers trust evidence, show the evidence.
```

---

## 🎬 VIDEO 4 OF 5 — Security Engineer

**Sources to load in NotebookLM:**
- `docs/assets/video-prompts/05-video-prompt-what-is-cortex-security-engineers.md`
- `docs/.content/01-platform-what-is-cortex.md`
- `docs/.content/03-governance-quality-that-enforces-itself.md`
- `docs/.content/07-security-built-in-not-bolted-on.md`
- `docs/.content/09-lifecycle-from-idea-to-production.md`
- `docs/assets/diagrams/15-diagram-governance-rule-enforcement-tiers.md`
- `docs/assets/diagrams/17-diagram-security-threat-model-stride-analysis.md`
- `docs/assets/diagrams/12-diagram-governance-convergence-gate-core-068.md`
- `docs/assets/diagrams/01-diagram-architecture-system-architecture-layers.md`
- `docs/assets/image-prompts/shared/06-governance-shield-defence-in-depth.prompt.md`
- `_workspaces/recommendations/mission-statement.md`

**Steering Prompt — paste into "What should the AI hosts focus on?":**

```
This is a 7–10 minute cinematic explainer exclusively for Security Engineers, AppSec teams, penetration testers, compliance architects, and DevSecOps practitioners. Avoid general engineering explanations.

Start with the problem security teams live every day: security enters the development lifecycle at the end — a scan before release, a review before production. Show a traditional SDLC timeline where security appears only at stage six of seven. Then show three real consequences: a secret committed six weeks ago has propagated through the build system; an OWASP injection vulnerability survived three code reviews; a dependency CVE sat in production for weeks undetected. CORTEX moves security to where it costs nothing to fix — the very beginning.

Structure the content across five sections:

SECTION 1 — FIVE LAYERS OF DEFENCE-IN-DEPTH: Show the governance shield diagram and the rule enforcement tiers diagram. Walk through each of the five security layers: (1) Before Commit — secrets, PII, credentials blocked before version control; (2) Governance Rules — bare exception catches, WAL enforcement; (3) Code Intelligence — SQL injection, XSS, credential exposure; (4) Static Analysis and CVE scanning — SAST plus dependency vulnerability database; (5) Release Gate — OWASP Top 10 and STRIDE threat model review. A clean commit passes all five. A threat is stopped at the first layer it fails.

SECTION 2 — SECRET SANITISATION BEFORE COMMIT: Show a pre-commit hook firing. CORTEX scans every staged file for secrets across hundreds of detection patterns — API keys, credentials, private keys, tokens. A commit containing a detected secret is blocked immediately with a CRITICAL severity alert. The same redaction engine runs through every log output. Secrets never reach git history.

SECTION 3 — STRIDE THREAT MODELLING ON DEMAND: Show the STRIDE threat model diagram. Walk through the six STRIDE categories: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege — applied to the actual system architecture, not a generic template. For each new component or architecture change, CORTEX generates a threat model automatically. DREAD scores surface the highest-risk threats first.

SECTION 4 — CONVERGENCE GATE AND AUDIT TRAIL: Show the convergence gate diagram. CORTEX refuses to let code proceed until all P0 and P1 security violations are resolved. The detect → fix → rescan loop runs until the violation count reaches zero — maximum three cycles. Every security event, every governance check, every threat model result is logged to a tamper-evident SQLite audit trail with AC markers. Show the audit trail structure: AC_START, AC_COMPLETE, with timestamps and event classification.

SECTION 5 — TRANSFORMATION: Before CORTEX: security is a post-hoc gate, findings arrive late, remediation is expensive, audit evidence is assembled manually. After CORTEX: security is structural — baked into every commit, every review, every deployment. Compliance evidence is generated automatically. Connect to the mission pillar — "Build Fearlessly" means security engineers stop being the team that slows delivery down and become the team that makes fearless delivery possible.

End with: "CORTEX makes security the foundation of delivery velocity, not the obstacle to it." Narrator: female, authoritative, precise — security professionals respect exactness. Use the correct OWASP and STRIDE terminology throughout.
```

---

## 🎬 VIDEO 5 OF 5 — Quality Engineer / SDET

**Sources to load in NotebookLM:**
- `docs/assets/video-prompts/06-video-prompt-what-is-cortex-quality-engineers.md`
- `docs/.content/01-platform-what-is-cortex.md`
- `docs/.content/03-governance-quality-that-enforces-itself.md`
- `docs/.content/04-tdd-quality-flywheel.md`
- `docs/.content/05-orchestration-the-engine-room.md`
- `docs/.content/09-lifecycle-from-idea-to-production.md`
- `docs/assets/diagrams/05-diagram-workflow-tdd-cycle-and-fsm.md`
- `docs/assets/diagrams/06-diagram-governance-sweep-completeness-core-064.md`
- `docs/assets/diagrams/07-diagram-testing-testing-strategy-pyramid.md`
- `docs/assets/diagrams/18-diagram-quality-analysis-engine-scoring-dashboard.md`
- `docs/assets/diagrams/16-diagram-quality-code-review-multi-pass-pipeline.md`
- `_workspaces/recommendations/mission-statement.md`

**Steering Prompt — paste into "What should the AI hosts focus on?":**

```
This is a 7–10 minute cinematic explainer exclusively for Quality Engineers, Test Engineers, SDET practitioners, quality leads, and test architects. Do not repeat Product Owner or Software Engineer workflows.

Start with the quality team's structural problem: "Tests will be added next sprint" becomes "we never got around to it." Show three sprint boards where the same sticky note migrates from DONE to BLOCKED to "Technical Debt — no tests." The final card: "Bug found in production. No tests caught it." CORTEX eliminates this pattern structurally — not through culture change, through enforcement.

Structure the content across five sections:

SECTION 1 — ENFORCED TDD: THE GATE THAT CANNOT BE BYPASSED: Show the TDD cycle FSM diagram. CORTEX enforces the three-phase cycle on every change — every feature, every bug fix, no exceptions. The enforcement gate verifies: does a failing test exist? Did it fail before implementation? A test that passes before implementation is flagged as vacuous and must be rewritten. Walk through the gate logic on screen. You cannot skip to green without earning it.

SECTION 2 — TEST QUALITY SCORING: FIVE DIMENSIONS: Show the quality scoring dashboard diagram. CORTEX scores every test across five dimensions: Impact (does this protect a critical behaviour?), Likelihood (realistic failure path?), Detection (verifies the right output?), Efficiency (is it concise?), Maintenance (will it stay relevant?). Show a high-score test (76/100 — P1 HIGH VALUE) and a low-score test (18/100 — Candidate for Removal). Not all tests are equal. CORTEX scores every one so quality teams know which tests to trust and which to retire.

SECTION 3 — SWEEP COMPLETENESS (CORE-064): Show the sweep completeness diagram. When CORTEX identifies a quality violation, it scans the entire codebase for every instance of that pattern. The sweep catalogue tracks every occurrence — open or closed. The operation is not complete until every item in the catalogue reaches CLOSED status. Walk through: 4 instances found across 4 files, 4 instances fixed, sweep complete. Quality engineers stop chasing partial fixes across sprints.

SECTION 4 — TESTING STRATEGY PYRAMID AND COVERAGE INTELLIGENCE: Show the testing strategy pyramid diagram and the multi-pass code review pipeline diagram. CORTEX maps every change against a five-tier testing model: unit, integration, contract, system, and acceptance. Coverage gap analysis identifies which tiers are under-represented for each change. Risk-based testing surfaces the highest-risk behavioural gaps first. Quality teams receive structured coverage intelligence, not a raw line-coverage percentage.

SECTION 5 — THE GOLDEN TEST CONTRACT: CORTEX maintains a Golden Test set — the minimum tests that must always pass for critical system behaviours. No refactoring, no architectural change, no dependency upgrade may break a Golden Test without an explicit, reviewed exception. This is the regression guarantee. Show the golden test gate in the convergence loop: if a golden test fails, the convergence gate does not open. The team never learns about a critical regression from a customer.

End with: "Quality that enforces itself. Every test meaningful. Every fix complete. Every critical behaviour protected." Connect to the mission — "Build Fearlessly" is only possible when quality teams trust the safety net. CORTEX is that safety net. Narrator: male, methodical, precise — quality engineers think in systems; show the system.
```

---

## 📋 Production Checklist

Before generating each video in NotebookLM:

| Step | Action |
|------|--------|
| ✅ 1 | Load all sources listed for that video into the NotebookLM notebook |
| ✅ 2 | Open "Customise Video Overview" |
| ✅ 3 | Select **Whiteboard** visual style |
| ✅ 4 | Paste the steering prompt for that video into "What should the AI hosts focus on?" |
| ✅ 5 | Click **Generate** |
| ✅ 6 | Review generated video against the corresponding `docs/assets/video-prompts/` source file |
| ✅ 7 | Re-generate with refined prompt if key sections are missing or out of order |

**Visual style note:** Whiteboard is selected for all five videos (consistent visual language across the series). The dark-blue glassmorphism identity described in the video prompt files applies to any custom production post-processing outside NotebookLM.
