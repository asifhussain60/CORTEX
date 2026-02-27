# Video Prompt 05 — The Collaborative Engine

> **Series:** CORTEX: The Enterprise Intelligence Series (Video 05 of 10)
> **Duration:** 8 minutes · **Audience:** Platform Engineers, Tech Leads, Engineering Managers
> **Depth:** � Platform-level — shows how CORTEX enables team collaboration and grows with your organization
> **Core Executive Theme:** Showcasing shared context, cross-functional workflows, knowledge persistence across teams, review transparency, and extensibility
> **No overlap:** Image prompt-08 (extensibility neural growth) shows static extension points; this video shows team collaboration in action — shared context flowing between teams, cross-functional workflows, and a NEW extension being added live

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

## ⚠️ VIDEO DESIGN BEST PRACTICES — MANDATORY

> **VBP-001:** One idea per frame — each extension point gets its OWN frame, never two at once.
> **VBP-004:** Progressive disclosure — 7 extension points reveal one dendrite at a time.
> **VBP-007:** Scene transitions every ~90-120 seconds to maintain attention.
> **VBP-009:** Data visualizations animated incrementally — onboarding dashboards build chart-by-chart.
> **VBP-010:** Live extension walkthrough (Scene 3) shows 15-minute timeline — compress to 90 seconds.
> **VBP-011:** Strategic silence when all 7 dendrites pulse simultaneously (neural network alive moment).
> See `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` for the full codified reference.

## ⚠️ HERO INTRO SLIDE — MANDATORY (VBP-014)

> **Scene 0 — Title Card (0:00 – 0:05):** Full-screen `#0a0e27` deep navy background. CORTEX logo (`cortex-docs/assets/images/cortex-logo-200.png`) displayed as a **large central hero image** with a subtle cyan glow pulse. Above the logo: **"The Collaborative Engine"** in Space Grotesk Bold, white. Below the logo: **"Shared Context. Cross-Functional Workflows. Knowledge That Persists."** in Inter, `#a0a6c0`. Hold 5 seconds. Transition: logo shrinks to watermark position as Scene 1 fades in.

## ⚠️ BREADCRUMB NAVIGATION — MANDATORY (VBP-015)

> **Scene 2 presents 7 extension points (dendrites) sequentially.** Display a persistent **breadcrumb bar**:
> `MCP Tools → Orchestrators → Governance Rules → Workflow Templates → Knowledge Base → Company Overrides → Pattern Library`
> - **Current dendrite:** Full brightness, bold, dendrite-specific color (cyan/purple/red/amber/green/teal/violet)
> - **Completed dendrites:** ✅ checkmark, dimmed to 60% opacity
> - **Upcoming dendrites:** Muted outlines at 30% opacity
>
> **Scene 3 presents 5-step MCP tool creation.** Display a breadcrumb:
> `Define → Implement → Register → Test → Use`
> - Each step checks off as completed. Timeline bar at bottom shows elapsed time.
>
> **Scene 4 presents 3-repository onboarding.** Display a breadcrumb:
> `Repo 1 (Python) → Repo 2 (TypeScript) → Repo 3 (C#) → Unified Dashboard`

## ⚠️ TYPOGRAPHY, COLOR & VOICE — MANDATORY (VBP-016, VBP-017, VBP-018, VBP-019)

> **Bold Key Words:** On every text card, **bold the 1–3 most important words** in cyan (`#00d4ff`).
> **Color Intelligence:** Each dendrite has its own color (matching Scene 2 assignments). Use consistently when that extension type is referenced throughout the video.
> **Voice:** 🎙️ **Female narrator** (odd-numbered video). Confident, conversational, honest tone.
> **Acronym Expansion (first use in this video):**
> - CORTEX = **CO**gnitive **R**eal-**T**ime **EX**ecution (Scene 1)
> - MCP = **M**odel **C**ontext **P**rotocol (Scene 2, first dendrite)
> - TDD = **T**est-**D**riven **D**evelopment (Scene 3, Step 4)
> - LENS = **L**anguage → **E**xamination → **N**avigation → **S**ynthesis (Scene 4, onboarding scan)
> - YAML = YAML configuration files (Scene 2)
> - CSP = **C**ontent **S**ecurity **P**olicy (Scene 4, Repo 2)
> - ECG = **E**lectro**c**ardio**g**ram heartbeat rhythm analogy (Scene 3, Step 4)

---

## PROMPT

Create an 8-minute animated explainer video titled **"The Collaborative Engine — Shared Context, Cross-Functional Workflows, and Knowledge Persistence"**. Show how CORTEX transforms isolated developer workflows into a collaborative engineering platform where context, knowledge, and governance flow seamlessly across teams.

### Scene 1 — The Collaboration Problem (0:00 – 1:15)

**Open on:** Three scenarios, animated as glassmorphic panels:

**Panel 1 — Knowledge Silos:** Developer A discovers a critical anti-pattern in the codebase. They fix it locally. Developer B, on a different team, introduces the same anti-pattern three weeks later. The knowledge never traveled.

**Panel 2 — Context Loss:** A senior engineer leaves the team. Their understanding of the architecture, the why behind key decisions, the patterns they established — all gone. The wiki page they wrote is outdated and incomplete.

**Panel 3 — Review Bottleneck:** Two teams need to collaborate on a shared service. Each team has different standards, different review practices, different tooling. Integration takes weeks of negotiation.

**All three panels dim and merge into a single question:** *"What if the knowledge, the context, and the standards traveled with the code — not with the people?"*

**Narration:** "The rigid tool problem is subtle — you don't feel it on day one. You feel it six months later when your workflow has bent itself around what the tool can't do. But the collaboration problem is worse — you feel it when someone leaves and takes the context with them."

### Scene 2 — The Extension Points (1:15 – 3:30)

**A neural network visualization.** Central node (CORTEX core) with 7 extending dendrites. Each dendrite represents an extension point:

**1. Model Context Protocol (MCP) Tools** (cyan dendrite):
- Show an empty tool slot in a glassmorphic toolbar.
- A new tool definition writes itself (YAML → Python function → registration).
- The tool appears in the toolbar, available immediately.
- *"Add capabilities without touching core code."*

**2. Orchestrators** (purple dendrite):
- Show a new orchestrator slot in the orchestrator ring.
- It implements the standard protocol (IOrchestrator interface shimmer).
- Routes light up — IntentRouter recognizes the new orchestrator.
- *"Specialized processing for your domain."*

**3. Governance Rules** (red dendrite):
- A new YAML rule definition appears.
- It slots into the appropriate tier (Tier 1 — Business Logic).
- Pre-commit hook automatically includes it.
- *"Your standards, enforced automatically."*

**4. Workflow Templates** (amber dendrite):
- A workflow YAML defines a custom pipeline: scan → validate → deploy.
- Glass pipeline assembles from the template.
- *"Repeatable processes, versioned as code."*

**5. Knowledge Base** (green dendrite):
- Enterprise patterns and domain knowledge added as YAML entries.
- LENS picks them up in the next scan — pattern detection enriched.
- *"Your organization's wisdom, searchable."*

**6. Company Overrides** (teal dendrite):
- Company-specific configuration overrides default behavior.
- Naming conventions, import restrictions, team-specific rules.
- *"Customize without forking."*

**7. Pattern Library** (violet dendrite):
- Custom architecture patterns defined and scored.
- LENS recognizes them in future scans.
- *"Teach CORTEX your architecture language."*

**Each dendrite pulses as it's described.** At the end, all 7 pulse simultaneously — the neural network is alive and growing.

**Narration:** "Seven extension points — none of them require touching core CORTEX code. That's not just convenient; it's the thing that makes organizational adoption possible without creating a maintenance nightmare for your platform team."

### Scene 3 — Live Extension: Adding a Custom MCP Tool (3:30 – 5:00)

**Hands-on walkthrough** (still animated, not screen recording):

**Step 1 — Define:** A tool YAML spec appears:
```yaml
name: cortex_deploy_check
description: Verify deployment prerequisites
```

**Step 2 — Implement:** A Python function materializes with type hints and docstring (governance-compliant from the start):
```python
def cortex_deploy_check(environment: str) -> dict:
    """Verify deployment prerequisites for target environment."""
```

**Step 3 — Register:** The tool registers in the MCP registry. A new slot fills in the toolbar.

**Step 4 — Test:** TDD cycle fires: RED (test for the new tool) → GREEN (tool passes) → REFACTOR. ECG heartbeat: red-green-blue.

**Step 5 — Use:** The tool appears in Copilot Chat. Developer invokes it. Results return.

**Timeline bar** at the bottom shows elapsed time: ~15 minutes from idea to working tool.

**Narration:** "Fifteen minutes. That's the cost of having a capability gap, realizing it, and closing it. Not a ticket. Not a sprint. Fifteen minutes."

### Scene 4 — Repository Onboarding (5:00 – 7:00)

**Scenario:** An organization has 3 existing repositories. They want CORTEX to understand them.

**Repository 1 — Python API:**
- `/onboard` command fires. LENS scan. Language: Python. Framework: FastAPI. 
- Security assessment: P0 — exposed debug endpoint in production config.
- Pattern detection: Strategy pattern in route handlers (0.85 confidence).
- Dashboard generated: glassmorphic panel with health scores, dependency graph.

**Repository 2 — TypeScript Frontend:**
- `/onboard` command. LENS: TypeScript, React, 847 components.
- Security: P1 — no CSP (Content Security Policy) headers configured.
- Patterns: Observer pattern in state management (0.92 confidence).
- Dashboard generated alongside Repository 1.

**Repository 3 — Legacy C# Service:**
- `/onboard` command. LENS: C#, .NET 6, extensive stored procedures.
- Security: P0 — SQL injection in 3 query builders. P1 — outdated NuGet packages.
- Patterns: Mediator pattern (MediatR) with custom extensions.
- Dashboard: higher priority items flagged in red.

**All three dashboards merge** into a unified landing page. Organization-wide health score. Cross-repository dependency graph. Shared vulnerability report.

**Narration:** "Three languages. Three security postures. One place to look. The cognitive load of maintaining cross-repository visibility without this is the kind of thing that only becomes obvious once it's gone."

### Scene 5 — Knowledge Continuity: When People Leave, Context Stays (7:00 – 7:30)

**Brief showcase** of the collaboration transformation:

| Before (Isolated) | After (Collaborative Engine) |
|---|---|
| Knowledge trapped in individuals | Searchable patterns + anti-patterns in shared knowledge base |
| Manual, inconsistent reviews | Automated governance + transparent review history |
| Per-repo, per-team tooling | Shared MCP toolkit + cross-functional workflows |
| Context lost on team changes | Persistent context in audit trail + knowledge base |
| Standards in a wiki nobody reads | Standards enforced in the commit pipeline |

**Narration:** "Repository onboarding isn't a one-time scan. It's the first step in building a collaborative engine where knowledge persists, context travels with the code, and no team is an island."

**Narration (on the before/after table):** "The right column isn't aspirational. It's what teams report after onboarding. The shift from tribal to institutional knowledge is the one that compounds most — because it persists when people leave."

### Scene 6 — Closing (7:30 – 8:00)

**Three principles:**

1. **Share, Don't Silo** — "Context persists in the platform, not in people's heads"
2. **Extend, Don't Fork** — "Seven extension points, zero core changes"
3. **Onboard, Don't Rewrite** — "Understand existing code before changing it"

**Closing text:** **"Your teams. Your knowledge. Always connected."**

**Narration:** "Collaboration at enterprise scale isn't about meetings and Slack threads. It's about building a shared intelligence layer where every team's patterns become every team's advantage — and knowledge survives every re-org, every departure, every pivot."

---

## Animated Diagram Flow Directives

### 📐 Mermaid Diagram Sources (bundle with this prompt in NotebookLM)

| Diagram File | Type | Scene Reference | Purpose |
|---|---|---|---|
| `05-d-common-utilities-overview.mmd` | C4-Component | Scene 2 — Extension Points (context) | Shows the STABLE foundation layer all extensions build upon — "Extend, Don't Fork" |
| `01-d-c4-container-full-system.mmd` | C4-Container | Scene 2 — Where extensions plug in | Full system architecture showing tiers where each extension type integrates |

> **Video Producer:** Import `05-d-common-utilities-overview.mmd` alongside this prompt in NotebookLM. This diagram shows the STABLE CORE (Tier 1 Common Utilities) that all 7 extension points build upon — it proves extensions don't require touching core code. Use it in Scene 2 as the foundation layer BEFORE showing the 7 dendrites. Import `01-d-c4-container-full-system.mmd` as supplementary context showing the full system where extensions plug in at different tiers. Both files contain `animation_notes` in their frontmatter.

**Diagram: Neural Network Extension Points (Scene 2)**
- Central node (CORTEX core) with 7 extending dendrites
- Each dendrite reveals one at a time as narration introduces it
- MCP Tools (cyan) → Orchestrators (purple) → Governance (red) → Workflows (amber) → Knowledge (green) → Company Overrides (teal) → Patterns (violet)
- Final pulse: all 7 simultaneously — the neural network is alive and growing

**Diagram: Multi-Repo Onboarding (Scene 4)**
- Three glass cubes (Python, TypeScript, C#) scan sequentially
- Each generates a dashboard panel
- All three merge into unified landing page — organization-wide health score

---

## Notes
- **Collaborative Engine framing** — The original Extensibility & Onboarding video is preserved in full (7 extension points, live walkthrough, multi-repo onboarding). The collaborative engine theme adds a *why* layer: extensibility enables team collaboration, onboarding enables knowledge continuity, and the combination creates a shared intelligence platform. This reframing elevates the same capabilities for enterprise audiences evaluating cross-functional value.
- This video is specifically for platform engineers, tech leads, and engineering managers evaluating CORTEX for organizational adoption
- The live extension walkthrough (Scene 3) is concrete and practical — not theoretical
- Multi-language onboarding (Python, TypeScript, C#) demonstrates real cross-stack capability and cross-functional team support
- **No hardcoded counts** — extension points described by function
- The STS transformation is mentioned briefly; full detail is in the tutorials
- **Voice:** Female (V05 — odd-numbered)
