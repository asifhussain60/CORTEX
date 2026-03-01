# NotebookLM Video Prompt — Software Engineer — MCP tools + workflow templates (architecture-in-action)

**Target length:** 10–15 minutes

## Purpose
Explain how MCP exposure + registry-driven workflow templates make CORTEX extensible and testable.

## Factual constraints
- MCP server is **stdio** and configured in `.vscode/settings.json`.
- MCP tools are registered in `mcp_registry.py`.
- Workflow templates live under `cortex-registry/workflows/templates/`.
- No claims about cloud deployment unless backed by repo evidence.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a 10–15 minute technical walkthrough for engineers explaining how CORTEX exposes capabilities via MCP tools (stdio, VS Code configured) and executes registry-driven workflow templates. Focus on extensibility and testability. Calm, technical narrator. Use only the provided sources; don’t speculate beyond them."

## Diagram inputs (render + animate)
1) `cortex-docs/assets/diagrams/02-architecture-mcp-gateway-architecture.md`
2) `cortex-docs/assets/diagrams/10-workflow-template-engine.md`
3) `cortex-docs/assets/diagrams/10-workflow-template-engine.md`

## Demo beats (conceptual but concrete)
1) A tool call appears in chat: “cortex_load rules” / “cortex_verify mcp”.
2) Show registry + tool discovery.
3) Show a workflow template composed of primitives: gates, checkpoints, convergence loop.
4) Explain why this matters: predictable automation, codebase-scale consistency.

## Visual language
- “X-ray” view: reveal layers (MCP → orchestrators → registry → tests).
- Cinematic traversal through diagram wall.
- Gentle UI beeps when a tool invocation occurs.

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** and a **scene/slide outline** using the demo beats above.

For each scene include:
- which layer is emphasized (MCP → orchestrators → registry → tests)
- which diagram ingredient is shown
- which single element is emphasized
- on-screen callouts with file paths only when helpful

## Audio guidance
- Technical narrator.
- Subtle electronic ambience.
- Realistic UI/terminal foley.

## CORTEX voice (architecture-in-action)
- Narrator should sound like a **senior engineer** doing an internal tech talk: factual and calm.
- Avoid “magic” framing; describe tool calls + templates as observable mechanisms.

## SDLC templates should look like config
- Any template visuals should be **YAML/JSON config** cards (registry path, primitives, gates) to reinforce governance-as-code.

## Define Audit → Fix → Rescan (even if this video is about MCP)
- **Audit**: run validation and produce violations.
- **Fix**: apply constrained changes via workflow templates.
- **Rescan**: confirm via revalidation/tests; close only at **0** critical violations.

## Recommended hybrid workflow (best quality)
- Use NotebookLM for narrative + first-cut slides.
- Record any real chat/tool output via screen capture.
- Stitch in an editor for timing and inserts.
