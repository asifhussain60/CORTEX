# NotebookLM Video Prompt — 03 — How CORTEX works (architecture tour)

**Target length:** 8–12 minutes

## Purpose
Generate an accessible architecture walkthrough that’s still technically honest.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create an 8–12 minute architecture walkthrough for technical leaders. Explain the request journey: Stage 0 governance audit, intent routing, LENS context gathering, workflow template execution, and validation via tests/compliance. Use a calm professional narrator. Use only the provided sources; avoid speculation and secrets."

## Factual anchors (use as on-screen lower-thirds)
- “Single canonical Python package: `cortex.*`”
- “Pylance-style MCP stdio server (auto-detected in VS Code)”
- “Workflow templates + primitives (YAML registry)”

## Visual ingredients (upload as images for best results)
1) `cortex-docs/assets/diagrams/08-architecture-package-and-directory-map.md`
2) `cortex-docs/assets/diagrams/09-orchestration-request-sequence.md`
3) `cortex-docs/assets/diagrams/02-architecture-mcp-gateway-architecture.md`
4) `cortex-docs/assets/diagrams/10-workflow-template-engine.md`

Visual guidance:
- “Wall of diagrams” → push in is a good motif, but keep motion illustrative, not prescriptive.
- Emphasize one node/arrow at a time.
- Use macro close-ups of **generic** YAML-like text and module trees (avoid secrets).

## Story beats (must remain consistent with repo patterns)
1) Request comes in → Stage 0 governance audit
2) Intent routing → choose a workflow
3) Intelligence (LENS) gathers context
4) Execution runs templates + gates
5) Tests + compliance validate changes

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** (define each term on first use) and a **scene/slide outline**.

For each scene include:
- diagram ingredient used
- which single element is emphasized
- which lower-third factual anchor is used

## Audio guidance
- Instructional narrator.
- Subtle “data center” ambience under architecture shots.
- Light risers for transitions.

## CORTEX voice (calm, architect-grade)
- Narrator should sound like a **senior architect**: measured, exact, and not promotional.
- Prefer concrete nouns: *stage, gate, template, registry, validation, trace*, and avoid hype.

## SDLC templates must look like config
- Any template shown should visually read as a **YAML/JSON workflow config file** (primitives, gates, convergence loop), not a generic flowchart.

## Define the “Audit → Fix → Rescan” closure rule
Even in an architecture tour, call out the reliability loop explicitly:
- **Audit** produces violations.
- **Fix** is executed under templates/rules.
- **Rescan** repeats validation (compliance + tests) until critical violations are **0**.

## Recommended hybrid workflow (best quality)
- Use NotebookLM for narrative + architecture slides.
- If you want a true VS Code UI moment, capture it via screen recording (don’t fake it).
