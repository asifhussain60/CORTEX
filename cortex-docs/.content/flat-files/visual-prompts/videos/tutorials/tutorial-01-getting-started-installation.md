```markdown
# Tutorial 01 — Getting Started: Installation

> **Duration:** 5 minutes · **Audience:** Everyone (zero prior knowledge assumed)
> **Depth:** 🟢 Tutorial — practical, step-by-step, no jargon
> **Prerequisites:** None — this is where new users START (watch concept Videos 1-8 first for full context)
> **Goal:** User has CORTEX running in VS Code by the end of the video

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 5-minute animated tutorial video titled **"Getting Started: Installation"** using the visual identity above. Guide the viewer from zero to a working CORTEX installation in VS Code.

### Scene 1 — What You'll Achieve (0:00 – 0:30)

**Open on:** A glassmorphic "Before/After" split panel.

**Left (Before):**
- Generic VS Code window with Copilot Chat open
- Text overlay: "Standard AI assistant — helpful, but basic"
- Dimmed, static

**Right (After):**
- VS Code with CORTEX MCP tools active in Copilot Chat
- 28 tools listed in a glassmorphic sidebar
- Governance badges glowing, test indicators green
- Text overlay: "Governed, tested, orchestrated AI development"
- Vibrant cyan/purple glow

**Narration:** "In the next 5 minutes, you'll transform VS Code from a basic code assistant into a fully governed AI development platform. No prior experience needed."

### Scene 2 — Prerequisites Check (0:30 – 1:15)

**A glassmorphic checklist** appears with four items:

1. **VS Code** — Icon appears, checkbox animates to ✅
   - Text: "Download from code.visualstudio.com if needed"

2. **GitHub Copilot** — Copilot icon appears, checkbox ✅
   - Text: "Active subscription required"

3. **Python 3.9+** — Python logo appears, terminal shows `python3 --version → 3.11.5`, checkbox ✅
   - Text: "Check with `python3 --version` in terminal"

4. **Git** — Git icon appears, terminal shows `git --version → 2.43.0`, checkbox ✅
   - Text: "For repository management"

Each item animates in sequence with a subtle pop sound.

**Analogy overlay** (`#a0a6c0`): *"Like checking you have ingredients before cooking — these four things must be ready first."*

### Scene 3 — Clone the Repository (1:15 – 2:00)

**Glassmorphic terminal** expands to center screen.

**Commands type in character-by-character:**

```bash
# Clone CORTEX
git clone https://github.com/asifhussain60/CORTEX.git

# Enter the directory
cd CORTEX
```

**Animation shows:**
- Repository downloading — progress bar with file count
- File tree materializing on the left panel
- Highlight key directories: `cortex/`, `cortex-registry/`, `tests/`

**Info card appears:**
> "The CORTEX repository contains everything — the framework, documentation, and configuration. No separate packages to install."

### Scene 4 — Set Up the Python Environment (2:00 – 3:00)

**Terminal continues:**

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# OR on Windows
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Visual indicators:**
- Virtual environment: glassmorphic "bubble" forms around the project
- Dependencies installing: progress bar fills, package names scroll (pytest, pyyaml, etc.)
- Final state: 47 packages installed ✅

**Troubleshooting tip** (amber info card):
> "If `python3` isn't found, try `python`. On Windows, you may need to add Python to your PATH."

### Scene 5 — Configure MCP for VS Code (3:00 – 4:00)

**The magic step.** Show VS Code opening the workspace.

**Commands in terminal:**

```bash
# Run the automated setup script
python3 scripts/setup-mcp.py
```

**Animation shows:**
- Script detecting the operating system
- `.vscode/settings.json` being created/updated
- The MCP configuration block appearing:

```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Key point** (glassmorphic highlight):
> "This is Pylance-style MCP. Unlike other frameworks, you never manually start a server. Open VS Code → CORTEX is ready."

**VS Code reloads.** Show the MCP server status indicator in the corner turning green.

### Scene 6 — Verify It Works (4:00 – 4:45)

**Open Copilot Chat** in VS Code.

**Type the verification command:**
```
/cortex verify environment
```

**The MCP tool activates.** Show:
- Tool selection animation (from Video 6)
- Response appearing in chat:

```
✅ CORTEX Environment Verified

Python: 3.11.5 ✅
Dependencies: 47/47 satisfied ✅
MCP Server: running ✅
Governance Rules: 38 loaded ✅
Orchestrators: 51 wired ✅
MCP Tools: 28 registered ✅

Status: READY FOR DEVELOPMENT
```

Each line appears with a pleasant chime.

**Narration:** "That's it. CORTEX is running. Every tool, every orchestrator, every governance rule — all available in Copilot Chat."

### Scene 7 — What's Next? (4:45 – 5:00)

**Three glassmorphic cards** slide in:

1. **Video 9: Your First Command** — Learn to use `/audit`, `/challenge`, `/ask`
2. **Video 10: Customizing CORTEX** — Add your own rules and tools
3. **Documentation** — Visit `cortex-docs/` for detailed guides

**Closing text** (Space Grotesk):
**"Five minutes to install. A career of engineering leverage."**

**Vision callback** (from index.html):
> *"From this moment, every line of code you write is tested, governed, and orchestrated. You just freed yourself from the legwork."*

Logo pulse. End card with URL: `https://asifhussain60.github.io/CORTEX/`

---

## Notes

- This video assumes ZERO prior knowledge — no CORTEX concepts are explained, only installation steps.
- All commands are real and match the actual CORTEX repository structure.
- The setup script (`scripts/setup-mcp.py`) is the canonical installation method — don't show manual configuration.
- Windows users are explicitly addressed with alternative commands where needed.
- Troubleshooting tips appear in amber cards — not buried in narration.
- Sound design: terminal typing = soft keystrokes; success = chime; progress = subtle ticking.
- This video is SHORT (5 minutes) because installation should be fast — if it takes longer, CORTEX has a UX problem.

```
