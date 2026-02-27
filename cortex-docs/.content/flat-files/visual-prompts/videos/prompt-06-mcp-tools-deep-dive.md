# Video Prompt 06 — MCP Tools Deep Dive

> **Duration:** 10 minutes · **Audience:** Software Engineers, Tool Builders
> **Depth:** 🔴 Developer-level — real tool invocations, protocol details, authoring
> **No overlap:** Image prompt-06 shows MCP as a static nervous system anatomy; this video shows *live tool invocations*, message flows, and how to author a new tool

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 10-minute animated explainer video titled **"MCP Tools Deep Dive"** using the visual identity above. Explain the Model Context Protocol as CORTEX's extension system, show live tool interactions, and demonstrate how a new tool is built.

### Scene 1 — What Is MCP? (0:00 – 1:30)

**Open on:** A glassmorphic VS Code window with the Copilot Chat panel open. The user types a message. But instead of just getting text back, *tools activate*.

**The MCP concept builds:**
- Show VS Code on the left. Copilot Chat in the center. On the right, a glassmorphic sidebar labeled "MCP Server — CORTEX" with a green connection indicator.
- Explain: "MCP is the bridge between AI chat and real actions."

**Protocol visualization:**
- A glassmorphic pipe connects VS Code ↔ MCP Server. Inside the pipe, JSON messages flow as glowing data packets.
- Label the pipe: `stdio transport` (JetBrains Mono)
- Show the settings.json config floating above:
  ```json
  {
    "github.copilot.chat.mcpServers": {
      "cortex": {
        "command": "python3",
        "args": ["-m", "cortex.mcp"],
        "transport": "stdio"
      }
    }
  }
  ```

**Analogy overlay** (`#a0a6c0`): *"USB ports on your computer — MCP is the universal port that lets any tool plug in and talk to any AI. Same cable, different devices."*

**Narration:** "The Model Context Protocol is an open standard — like USB for AI tools. CORTEX implements an MCP server with 28 registered tools that give Copilot superpowers."

### Scene 2 — The Pylance-Style Architecture (1:30 – 3:00)

**Key differentiator animation:**

Show two approaches side by side:

**Left — "Manual Server" (other frameworks):**
- Terminal: `npm start-mcp-server` → user must remember to start it
- If it crashes, tools silently stop working
- Manual port management
- Panel is dim, amber-tinted

**Right — "Pylance-Style" (CORTEX):**
- VS Code opens → MCP server auto-starts (no user action)
- Like Pylance (Python language server) — always running, always connected
- Auto-restart on crash, stdio transport (no ports)
- Panel glows cyan

**Architecture diagram builds:**

```
┌─────────────────────────────────────────┐
│  VS Code                                │
│  ┌───────────────────────────────────┐  │
│  │  GitHub Copilot Chat              │  │
│  │  ┌───────────────────────────┐    │  │
│  │  │  MCP Client (built-in)    │    │  │
│  │  └──────────┬────────────────┘    │  │
│  └─────────────┼─────────────────────┘  │
│                │ stdio                   │
│  ┌─────────────▼────────────────────┐   │
│  │  CORTEX MCP Server               │   │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐    │   │
│  │  │Tool│ │Tool│ │Tool│ │ ...│    │   │
│  │  │ 1  │ │ 2  │ │ 3  │ │ 28 │    │   │
│  │  └────┘ └────┘ └────┘ └────┘    │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

This diagram renders as glassmorphic nested panels with cyan connection lines. Each "Tool" box is a small glass tile that glows as it's mentioned.

**Analogy overlay:** *"Pylance doesn't ask you to start it — you open a Python file and it's just there. CORTEX MCP works the same way."*

### Scene 3 — Tool Catalogue Tour (3:00 – 5:00)

**The 28 registered tools** appear as a grid of glassmorphic tiles, organized by category. Each tile has an icon, name, and one-line description.

**Animated category reveal:**

1. **Core Intelligence** (cyan border):
   - `cortex_ask` — Educational Q&A with truth verification
   - `cortex_total_recall` — Feature and component discovery
   - `cortex_verify_claim` — Claim verification against live code
   - Each tile slides in, icon animates

2. **Governance** (amber border):
   - `cortex_validate_compliance` — Code vs CORE rules
   - `cortex_execute_governance` — Enforcement actions
   - `cortex_query_governance` — Rule and state queries
   - `cortex_load_core_rules` — Load rule definitions

3. **Development Workflow** (green border):
   - `cortex_challenge` — AI-driven challenge analysis
   - `cortex_refactor` — Semantic refactoring
   - `cortex_onboard_repository` — Repository analysis
   - `cortex_audit_remediation_plan` — Auto-fix planning

4. **Environment** (purple border):
   - `cortex_verify_environment` — Setup verification
   - `cortex_validate_venv` — Virtual env check
   - `cortex_check_dependency_drift` — Package drift detection

5. **Dashboards & Metrics** (blue border):
   - `cortex_generate_dashboard_suite` — Full dashboard generation
   - `cortex_capture_metrics` — Development metrics
   - `cortex_metrics_report` — Export reports

**Counter in corner:** Tiles count up: 1... 5... 10... 15... 20... 25... 28.
Then a dashed border section: "+11 planned" with future tool names in muted text.

**Narration:** "28 tools registered today, 39 planned. Each one is a capability that Copilot can invoke autonomously."

### Scene 4 — Live Tool Invocation (5:00 – 7:00)

**Scenario:** User asks Copilot to validate their code's governance compliance.

**Step-by-step animation:**

1. **User types** in Copilot Chat (glassmorphic panel): "Check if my code follows CORTEX governance rules"

2. **Copilot recognizes** the intent → selects `cortex_validate_compliance` tool. Show a brief "thinking" animation — the tool tile glows and a selection arrow points to it.

3. **JSON request** flows through the stdio pipe:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "cortex_validate_compliance",
       "arguments": {
         "file_path": "cortex/discount.py"
       }
     }
   }
   ```
   The JSON renders in JetBrains Mono with syntax highlighting (keys in cyan, values in green, brackets in white).

4. **Server processing** — inside the MCP server box:
   - The tool function activates (glass tile glows)
   - It calls the `EnforcementOrchestrator` (connection line to orchestrator layer)
   - Rule checks execute (rapid green checkbox cascade)
   - Results compile

5. **JSON response** flows back:
   ```json
   {
     "result": {
       "compliant": true,
       "rules_checked": 38,
       "violations": 0,
       "details": [
         {"rule": "CORE-011", "status": "pass"},
         {"rule": "CORE-012", "status": "pass"}
       ]
     }
   }
   ```

6. **Copilot Chat** displays the result in a formatted, human-readable card: "✅ All 38 governance rules passed."

**The full round-trip** is then replayed in fast-forward (3 seconds), showing the complete flow: User → Copilot → MCP Client → stdio → MCP Server → Tool → Orchestrator → Result → stdio → Copilot → User.

**Analogy overlay:** *"Ordering food through a waiter — you tell the waiter what you want, the waiter tells the kitchen, the kitchen cooks, the waiter brings it back. MCP is the waiter."*

### Scene 5 — Authoring a New Tool (7:00 – 9:00)

**Narration:** "What if you need a tool that doesn't exist yet? Let's build one."

**Code-along animation** — building a hypothetical `cortex_count_todos` tool:

1. **Create the file** — file tree shows `cortex/mcp/tools/count_todos.py` being created (cyan highlight).

2. **Write the function** (JetBrains Mono, character-by-character):
   ```python
   from cortex.mcp.registry import register_tool


   @register_tool(
       name="cortex_count_todos",
       description="Count TODO comments across the workspace"
   )
   async def count_todos(
       directory: str = ".",
       orchestrator_context: dict | None = None,
   ) -> dict:
       """Count TODO comments in Python files.

       Args:
           directory: Root directory to scan.
           orchestrator_context: MCP routing context.

       Returns:
           Dict with file paths and TODO counts.
       """
       if orchestrator_context is not None:
           validate_orchestrator_context(orchestrator_context)
       # ... implementation ...
   ```

3. **Highlight the guard pattern** — zoom in on the `if orchestrator_context is not None:` line. A glassmorphic annotation appears: "Required by CORTEX authoring rules — allows direct test invocation without MasterOrchestrator."

4. **Register in `mcp_registry.py`** — show the registry file, the new tool appearing in the list.

5. **Write the test first** (callback to TDD):
   ```python
   def test_count_todos_finds_comments():
       result = await count_todos(directory="tests/fixtures/")
       assert result["total"] > 0
   ```

6. **Restart MCP server** — VS Code automatically restarts the server, the new tool tile appears in the grid: 29 tools.

**Analogy overlay:** *"Adding a new app to your phone — write it, register it in the app store, it's available to everyone."*

### Scene 6 — The MCP Ecosystem (9:00 – 10:00)

**Zoom out** to show MCP as an industry standard:

- CORTEX's MCP server is one of many — other tools and frameworks can also implement MCP.
- Show multiple MCP servers connected to VS Code: CORTEX (cyan), a database tool (amber), a deployment tool (green).
- The protocol is the same — `stdio` or HTTP transport, JSON-RPC messages, tool registration.

**Vision statement** (glassmorphic card):
- "MCP makes AI tools composable — like LEGO blocks that snap together"
- "CORTEX's 39 planned tools will form a complete AI engineering toolkit"

**Closing stats:**
- 28 tools registered today
- 39 planned (11 in active phases)
- stdio transport — zero configuration
- Pylance-style — always available

**Closing text** (Space Grotesk): **"Every tool you need. One protocol. Zero setup."**

Logo pulse. End card.

---

## Notes

- Image prompt-06 shows MCP as a static human nervous system diagram. This video shows **live tool invocations with real JSON flowing through the protocol** — completely different content.
- The tool authoring section (Scene 5) is unique to this video — not covered in any image prompt.
- JSON messages are syntactically correct and match the actual MCP protocol format.
- The `validate_orchestrator_context` guard pattern is explicitly highlighted — this is a CORTEX authoring requirement from the copilot-instructions.
- Sound design: JSON packets flowing = soft data-stream sound; tool selection = click; result delivery = pleasant notification.
