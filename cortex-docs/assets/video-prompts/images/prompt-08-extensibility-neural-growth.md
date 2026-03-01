# Prompt 08 — Extensibility — Neural Growth

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a technical illustration showing a brain forming new neural connections, reimagined as CORTEX's extensibility architecture — how new capabilities (tools, orchestrators, patterns, knowledge) plug in without modifying the core.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle organic neural texture in rgba(0, 212, 255, 0.03)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff). Success: Green (#00ff88)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: All labels in #ffffff on dark pill backgrounds. Extension point names in cyan #00d4ff JetBrains Mono. Descriptions in #ffffff Inter
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px

CENTER — THE CORTEX CORE (stable, glowing cyan brain structure):
- A stylized brain outline in cyan (#00d4ff) with established neural pathways
- Label: "Core Platform — Stable, Versioned, Protected"
- The core does NOT change when extensions are added

SEVEN GROWTH POINTS — new neural dendrites extending outward from the core, each a different color:

1. "MCP Tools" (cyan #00d4ff dendrite growing upward):
   - Shows a new tool icon plugging into the MCP server
   - Label: "Drop a file in mcp/tools/ → auto-discovered on restart"
   - "Like installing a new app on your phone"

2. "Domain Orchestrators" (purple #7b61ff dendrite):
   - Shows a new orchestrator node connecting to the galaxy
   - Label: "Inherit the protocol mixin → registered in wiring contract"
   - "Like hiring a new specialist doctor for the hospital"

3. "Workflow Templates" (amber #ffa500 dendrite):
   - Shows a new YAML scroll being added to a library shelf
   - Label: "Add a YAML file → WorkflowEngine reads it immediately"
   - "Like adding a new recipe to the cookbook"

4. "Enterprise Patterns" (blue #3b82f6 dendrite):
   - Shows a new pattern signature being detected
   - Label: "Define signatures in YAML → Perception tier detects automatically"

5. "Knowledge Base" (green #00ff88 dendrite):
   - Shows a new knowledge entry glowing green
   - Label: "Add knowledge files → intelligence layer indexes them"

6. "Company Overrides" (warm amber dendrite):
   - Shows a company-specific YAML file overriding a default
   - Label: "Company templates take precedence → no code change required"
   - "Like customizing your workspace without touching the OS"

7. "Governance Rules" (red #ff4444 border, carefully placed dendrite):
   - Shows a new rule shield being added to the wall
   - Label: "Define in YAML → enforced at pre-commit, CI, and runtime"

ALL EXTENSION POINTS share one characteristic:
- A small "HOT RELOAD" badge in green (#00ff88) — no restart required (or minimal restart)
- No modification to existing core files

Glassmorphic footer:
"Seven Extension Points · Hot-Reload Discovery · Core Never Modified · Grow Without Breaking"
Caption: "Like neuroplasticity — the brain forms new connections without rewiring existing ones"

Style: Organic neural growth illustration with dark glassmorphism tech panels. Cyan core brain with multicolored dendrites extending. Professional and inspiring — shows that CORTEX grows with your team.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- CORTEX is designed for extensibility — new capabilities plug in without changing core code
- All extensions are discovered automatically (file-based discovery, no manual registration for most)
- Company-specific overrides take precedence over defaults — key for enterprise adoption
- This image answers the question: "Can I customize CORTEX for my team?"
