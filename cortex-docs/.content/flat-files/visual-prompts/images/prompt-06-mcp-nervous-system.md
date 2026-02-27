# Prompt 06 — MCP as a Nervous System

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a detailed anatomical illustration of a human nervous system reimagined as the MCP (Model Context Protocol) communication architecture.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow
- Human body silhouette outlined in subtle cyan rgba(0, 212, 255, 0.15)

THE BRAIN (at the head) — labeled "VS Code / IDE":
- Glowing with cyan (#00d4ff) corona
- Glassmorphic label: "Where the developer types requests"
- Muted caption (#a0a6c0): "Your brain sends the signal — the IDE sends the request"

THE SPINAL CORD (center channel) — labeled "MCP stdio Transport":
- Thick glowing cyan (#00d4ff) channel with 0 0 20px rgba(0,212,255,0.3) glow
- Small JSON-RPC 2.0 message packets flowing as cyan pulse orbs
- JetBrains Mono label: "JSON-RPC 2.0 · stdio (dev) / HTTP (prod)"
- Muted caption: "Like your spinal cord — the superhighway connecting brain to body"

THE NERVE CLUSTERS — 28 glowing nerve endpoints, each = an MCP tool:
- Left side (Core tools, cyan #00d4ff): cortex_process_request, cortex_validate, cortex_load, cortex_verify, cortex_ask
- Right side (Domain tools, purple #7b61ff): cortex_refactor, cortex_challenge, cortex_onboard, cortex_vision_analyze
- Lower left (Support tools, amber #ffa500): cortex_vacuum, cortex_audit_remediation_plan, cortex_capture_metrics
- Lower right (Intelligence tools, green #00ff88): cortex_learning, cortex_total_recall, cortex_tools_catalog
- Each nerve endpoint is a small glowing node with JetBrains Mono tool name

11 PLANNED TOOLS as dim, unconnected nerve endings (rgba(255,255,255,0.15)):
- Glassmorphic label: "11 planned · 39 total target"
- Muted caption: "Growing nerves — new capabilities being wired"

AT THE HANDS:
- Left hand: "File Operations" in glassmorphic panel
- Right hand: "Terminal Commands" in glassmorphic panel
- Muted caption: "The hands that do the work — but only after the brain decides"

THREE CHECKPOINT STATIONS along the spine (glassmorphic nodes):
1. "Validation" (neck level, cyan border)
2. "Rate Limiting" (chest level, amber border)
3. "Audit Logging" (waist level, green border)

Glassmorphic footer bar:
"28 Registered MCP Tools · Pylance-style Auto-Start · Zero Configuration"
Muted subtitle: "Like a nervous system — you don't consciously activate your nerves. They just work."

Style: Anatomical illustration with dark glassmorphism overlay. Leonardo da Vinci's Vitruvian Man meets CORTEX tech aesthetic. Cyan glow, frosted panels, deep navy background.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- MCP uses Pylance-style stdio transport — auto-starts with VS Code
- 28 tools are currently registered in `cortex/mcp/tools/`
- Configuration is in `.vscode/settings.json`
- The server is at `cortex/mcp/`
