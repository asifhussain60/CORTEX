# Video Prompt 07 — Extensibility and Repository Onboarding

> **Duration:** 8 minutes · **Audience:** Platform Engineers, Tech Leads
> **Depth:** 🔴 Platform-level — shows how CORTEX grows with your organization
> **No overlap:** Image prompt-08 (extensibility neural growth) shows static extension points; this video shows a NEW extension being added live — from empty slot to functioning capability — plus onboarding a real external repository

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create an 8-minute animated explainer video titled **"Extensibility and Repository Onboarding"**. Show how CORTEX adapts to your organization and absorbs new codebases.

### Scene 1 — The Customization Problem (0:00 – 1:15)

**Open on:** Two scenarios, side by side:

**Left — Rigid Tool:** A glass box with a padlock. Team tries to add a custom workflow. Red X. "Not supported." Team builds a workaround. Workaround breaks on next update. Cycle repeats.

**Right — No Tool:** Total freedom. Team builds everything from scratch. Inconsistency across teams. No governance. Knowledge trapped in individuals.

**Center merge:** Both panels slide together. CORTEX logo materializes between them.

**Narration:** "The rigid tool problem is subtle — you don't feel it on day one. You feel it six months later when your workflow has bent itself around what the tool can't do."

### Scene 2 — The Extension Points (1:15 – 3:30)

**A neural network visualization.** Central node (CORTEX core) with 7 extending dendrites. Each dendrite represents an extension point:

**1. MCP Tools** (cyan dendrite):
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
- Security: P1 — no CSP headers configured.
- Patterns: Observer pattern in state management (0.92 confidence).
- Dashboard generated alongside Repository 1.

**Repository 3 — Legacy C# Service:**
- `/onboard` command. LENS: C#, .NET 6, extensive stored procedures.
- Security: P0 — SQL injection in 3 query builders. P1 — outdated NuGet packages.
- Patterns: Mediator pattern (MediatR) with custom extensions.
- Dashboard: higher priority items flagged in red.

**All three dashboards merge** into a unified landing page. Organization-wide health score. Cross-repository dependency graph. Shared vulnerability report.

**Narration:** "Three languages. Three security postures. One place to look. The cognitive load of maintaining cross-repository visibility without this is the kind of thing that only becomes obvious once it's gone."

### Scene 5 — The STS Transformation (7:00 – 7:30)

**Brief showcase** of the before → after:

| Before | After |
|---|---|
| Scattered docs | Unified knowledge base |
| Manual governance | Automated enforcement |
| Per-repo tooling | Shared MCP toolkit |
| Tribal knowledge | Searchable patterns |

**Narration:** "Repository onboarding isn't a one-time scan. It's the first step in transforming how your organization works."

**Narration (on the before/after table):** "The right column isn't aspirational. It's what teams report after onboarding. The shift from tribal to institutional knowledge is the one that compounds most — because it persists when people leave."

### Scene 6 — Closing (7:30 – 8:00)

**Three principles:**

1. **Extend, Don't Fork** — "Seven extension points, zero core changes"
2. **Onboard, Don't Rewrite** — "Understand existing code before changing it"
3. **Unify, Don't Fragment** — "One intelligence layer across all repositories"

**Closing text:** **"Your organization. Your rules. CORTEX adapts."**

**Narration:** "The reason CORTEX can adapt to your organization is because every extension point was designed for exactly this: the thing your organization does that no other organization does the same way."

---

## Notes
- This video is specifically for platform engineers and tech leads evaluating CORTEX for organizational adoption
- The live extension walkthrough (Scene 3) is concrete and practical — not theoretical
- Multi-language onboarding (Python, TypeScript, C#) demonstrates real cross-stack capability
- **No hardcoded counts** — extension points described by function
- The STS transformation is mentioned briefly; full detail is in the tutorials
