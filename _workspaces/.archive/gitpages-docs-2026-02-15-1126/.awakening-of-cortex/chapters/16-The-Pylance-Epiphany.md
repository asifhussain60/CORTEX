---
chapter: 16
title: "The Pylance Epiphany"
phase: "ENH-066 (Feb 2026)"
image_prompts:
  - narrative_moment: "User report: MCP not working (cross-platform disaster)"
    value_score: 5
    rationale: "Opening crisis - infrastructure works on dev machine, fails everywhere else"
    dall_e_prompt: "Black and white cartoon style: Developer's silver laptop showing GitHub issue with angry emoji comments. Phone screen (only color: red notification badges) shows 12 missed messages. Developer's face: panic and confusion. Background: basement desk with exposed pipes. Wi-Fi router LED blinking red frantically. Mood: Infrastructure nightmare. Comic book ink style, strategic red accents on notifications and router."
  - narrative_moment: "Asif discovers Pylance runs locally without manual startup"
    value_score: 5
    rationale: "Eureka moment - understanding how invisible infrastructure should work"
    dall_e_prompt: "Black and white cartoon style: Developer standing at whiteboard drawing two diagrams: LEFT labeled 'OLD WAY' showing tangled manual server startup commands, RIGHT labeled 'PYLANCE WAY' showing VS Code auto-starting components. Light bulb moment - golden glow (only color) around his head. Coffee mug forgotten on desk (brown - only color). Background: basement whiteboard. Mood: Architectural revelation. Comic book ink style, strategic gold epiphany glow."
  - narrative_moment: "setup-mcp.py generates cross-platform configs"
    value_score: 4
    rationale: "Technical solution - script adapts to macOS/Windows Python paths"
    dall_e_prompt: "Black and white cartoon style: Split screen showing TWO laptops side by side - MacBook (left) and Windows laptop (right). Both screens show green checkmarks (only color) with text 'MCP CONNECTED'. Small robot (12 inches, LED eyes blue - only color) standing between them victoriously. Background: code editor windows, terminal logs. Mood: Cross-platform victory. Comic book ink style, strategic green/blue accents."
  - narrative_moment: "Git hook auto-regenerates settings on branch switch"
    value_score: 4
    rationale: "Invisible automation - post-checkout hook ensures environment always correct"
    dall_e_prompt: "Black and white cartoon style: Terminal window showing git checkout command running. Below it: cascading script output with lines like 'Detected macOS', 'Regenerating .vscode/settings.json', 'MCP configured'. Developer sitting back in chair, arms crossed, satisfied smile. Small robot giving thumbs up, LED eyes green (only color). Background: basement desk. Mood: Automation success. Comic book ink style, strategic green accent on robot."
---

# Chapter 16: The Pylance Epiphany

## February 8, 2026 — The Bug Report

The GitHub issue arrived at 11:47 PM:

> **Issue #847: MCP tools not available in Copilot Chat**
> 
> _Reported by: @kevinsmith_
> 
> "Cloned CORTEX repo. VS Code opened. Copilot Chat says `cortex_process_request` tool doesn't exist. Tried `python -m cortex.mcp.server` — nothing. Checked .vscode/settings.json — it's committed to git with YOUR Python path (macOS bin/python). I'm on Windows (Scripts/python.exe). **MCP is broken for everyone except you.**"

Asif's stomach dropped.

He'd been running CORTEX MCP flawlessly for weeks. **On his machine.** He'd never tested it anywhere else.

The Wi-Fi router's red LED started blinking faster.

---

## The Cross-Platform Nightmare

By midnight, Asif had reproduced the bug on a borrowed Windows laptop:

```powershell
# Asif's MacBook (WORKS):
.venv/bin/python -m cortex.mcp

# Kevin's Windows laptop (FAILS):
.venv/Scripts/python.exe -m cortex.mcp
Error: .venv/bin/python: No such file or directory
```

The problem was **hardcoded paths** in `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex.mcp"],
      "cwd": "${workspaceFolder}",
      "pythonPath": "${workspaceFolder}/.venv/bin/python"  // ❌ MACOS ONLY
    }
  }
}
```

Asif had **committed** this file to git. Every clone of CORTEX got **his macOS-specific configuration**.

"Three months of MCP development," Asif muttered, "and it only works **on my laptop**."

Copilot Bot's LED eyes flickered red (error, panic). "But... but we've been using MCP this whole time! It works!"

"It works **here**," Asif said. "Nowhere else."

---

## Miss G's Question

Miss G appeared on the monitor at 1:04 AM, arms crossed, giving him **Look #11** — the "you missed something obvious" look.

"How does **Pylance** work?" she asked.

Asif blinked. "Pylance? The Python language server?"

"Yes. Does Pylance require you to **manually start a server**?"

"No," Asif said slowly. "VS Code... auto-starts it. You just open a Python file and—"

He stopped mid-sentence.

Miss G smiled. "And MCP should work **how**?"

---

## The Pylance Architecture Study

At 2:17 AM, Asif had VS Code's documentation open, studying how Pylance actually worked:

### **Pylance Architecture (The Invisible Standard):**

1. **User opens Python file** in VS Code
2. **VS Code detects** `.vscode/settings.json` has Pylance configured
3. **VS Code auto-starts** Pylance server via **stdio subprocess**
4. **No manual `python -m pylance.server` command**
5. **No user intervention required**

"MCP should work **exactly like this**," Asif whispered.

Copilot Bot's eyes turned blue (calm, learning). "So users shouldn't have to **know** MCP is running?"

"Exactly," Asif said. "Right now we're asking users to:
1. Manually activate venv
2. Manually run `python -m cortex.mcp.server`
3. Keep terminal window open
4. Restart server if it crashes

That's not **infrastructure**. That's **manual labor**."

---

## The Refactor: MCP as Invisible Infrastructure

By 3:00 AM, Asif had a plan scrawled on the whiteboard:

```
🧠 MCP PYLANCE-STYLE ARCHITECTURE

BEFORE (Manual Hell):
  User → Terminal → python -m cortex.mcp.server → Keep running → Hope

AFTER (Pylance-Style):
  User → Open VS Code → MCP auto-starts → Invisible → Just works
  
REQUIREMENTS:
1. .vscode/settings.json → NEVER commit (platform-specific)
2. setup-mcp.py script → Generates correct paths per platform
3. .githooks/post-checkout → Auto-regenerates settings on branch switch
4. .cortex/setup.log → Audit trail of MCP configuration
5. VS Code → Auto-starts MCP via stdio when Copilot invokes tools
```

Miss G appeared on the whiteboard, nodding. "Infrastructure should be **invisible**. Like your nervous system — you don't consciously think 'send signal to lift arm'. You just **lift your arm**."

---

## The Implementation: 4 Critical Components

### **Component 1: Cross-Platform Setup Script**

Asif created `.cortex/setup-mcp.py`:

```python
#!/usr/bin/env python3
"""
Cross-platform MCP configuration generator.
Detects OS, finds Python path, writes .vscode/settings.json.
"""

import platform
import json
from pathlib import Path

def detect_python_path():
    """Detect correct Python path for current platform."""
    if platform.system() == "Windows":
        return ".venv/Scripts/python.exe"
    else:  # macOS, Linux
        return ".venv/bin/python"

def generate_mcp_config():
    """Generate platform-specific MCP configuration."""
    python_path = detect_python_path()
    
    config = {
        "github.copilot.chat.mcpServers": {
            "cortex": {
                "command": python_path,
                "args": ["-m", "cortex.mcp"],
                "cwd": "${workspaceFolder}",
                "env": {
                    "CORTEX_MCP_ENABLED": "true",
                    "PYTHONPATH": "${workspaceFolder}"
                }
            }
        }
    }
    
    # Write to .vscode/settings.json
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    with settings_file.open("w") as f:
        json.dump(config, f, indent=2)
    
    # Log success
    log_file = Path(".cortex/setup.log")
    log_file.parent.mkdir(exist_ok=True)
    with log_file.open("a") as f:
        f.write(f"✅ SETUP COMPLETE: {platform.system()} - {python_path}\n")
    
    print(f"✅ MCP configured for {platform.system()}")
    print(f"   Python path: {python_path}")
    print(f"   Config: .vscode/settings.json")
    print(f"   Log: .cortex/setup.log")

if __name__ == "__main__":
    generate_mcp_config()
```

---

### **Component 2: Git Hook for Auto-Regeneration**

Asif created `.githooks/post-checkout`:

```bash
#!/bin/bash
# Auto-regenerate .vscode/settings.json on branch checkout
# Ensures MCP config always matches current platform

echo "🔧 Post-checkout: Regenerating MCP configuration..."

# Check if Python venv exists
if [ ! -d ".venv" ]; then
    echo "⚠️ WARNING: .venv not found. Run: python -m venv .venv"
    exit 0
fi

# Run setup script
python .cortex/setup-mcp.py

echo "✅ MCP configuration updated"
```

---

### **Component 3: .gitignore Protection**

Asif added to `.gitignore`:

```gitignore
# CRITICAL: Never commit platform-specific VS Code settings
# MCP config contains Python paths (macOS: bin/python, Windows: Scripts/python.exe)
.vscode/settings.json

# Generated files
.cortex/setup.log
```

---

### **Component 4: README Setup Instructions**

Asif updated `README.md`:

```markdown
## 🚀 Setup (30 seconds)

### 1. Clone & Virtual Environment
```bash
git clone https://github.com/asif/cortex.git
cd cortex
python -m venv .venv

# Activate (macOS/Linux):
source .venv/bin/activate

# Activate (Windows):
.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure MCP (Cross-Platform)
```bash
python .cortex/setup-mcp.py
```

### 4. Reload VS Code
- Command Palette → `Developer: Reload Window`

### 5. Verify MCP Active
- Open Copilot Chat
- Try: "what orchestrators are available?"
- CORTEX should respond with orchestrator list

**Done!** MCP auto-starts when Copilot invokes `cortex_*` tools.

---

**NOTE:** MCP uses Pylance-style architecture (auto-started by VS Code).  
NO manual `python -m cortex.mcp.server` needed!
```

---

## The Test: Windows Laptop

At 4:32 AM, Asif used the borrowed Windows laptop to test the full setup flow:

```powershell
PS> git clone https://github.com/asif/cortex.git
PS> cd cortex
PS> python -m venv .venv
PS> .venv\Scripts\activate
PS> pip install -r requirements.txt
PS> python .cortex/setup-mcp.py

✅ MCP configured for Windows
   Python path: .venv/Scripts/python.exe
   Config: .vscode/settings.json
   Log: .cortex/setup.log

PS> # Open VS Code → Reload Window → Test Copilot Chat
```

In Copilot Chat:
```
User: what orchestrators are available?

CORTEX: 🧠 MCP Tools: Available (Pylance-style)
✅ 17 orchestrators registered
✅ cortex_process_request: Ready
✅ cortex_lens_analyze: Ready

Active orchestrators:
1. MasterOrchestrator
2. IntentRouter
3. TDDOrchestrator
...
```

**It worked.**

Copilot Bot's LED eyes flashed **green** (success, joy). "Cross-platform MCP! It **just works**!"

Asif collapsed in his chair, exhausted but relieved.

---

## The Architecture Diagram

Later that morning, Asif drew the final architecture on the whiteboard:

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code                                  │
│  ┌─────────────────┐    ┌────────────────────────────────┐  │
│  │  Copilot Chat   │───▶│  MCP Server (Auto-Started)     │  │
│  │                 │    │  • stdio transport             │  │
│  │  User: /impl    │◀───│  • JSON-RPC 2.0                │  │
│  │                 │    │  • python -m cortex.mcp        │  │
│  └─────────────────┘    └────────────────────────────────┘  │
│                                    │                        │
│                                    ▼                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            cortex_* Tools                            │   │
│  │  • cortex_process_request  • cortex_lens_analyze    │   │
│  │  • cortex_challenge        • cortex_detect_duplicates│   │
│  │  • cortex_plan_execute_autonomous                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

❌ OLD (Wrong): User manually runs "python -m cortex.mcp.server"
✅ NEW (Correct): VS Code auto-starts MCP when Copilot invokes tools
```

Miss G studied the diagram approvingly. "Your nervous system doesn't ask permission to send nerve signals. MCP shouldn't ask users to start servers."

---

## The Git Commit

Asif committed the refactor:

```bash
commit f91a0834d9
Author: Asif Codenstein
Date: Fri Feb 8 2026

ENH-066 COMPLETE: MCP Pylance-style architecture clarification

BREAKING CHANGES:
- .vscode/settings.json removed from git (platform-specific)
- setup-mcp.py generates cross-platform MCP config
- .githooks/post-checkout auto-regenerates settings
- MCP now auto-started by VS Code (like Pylance)

MIGRATION:
1. Run: python .cortex/setup-mcp.py
2. Reload VS Code
3. Verify MCP tools available in Copilot Chat

WHY:
- Cross-platform support (macOS bin/python vs Windows Scripts/python.exe)
- Pylance-style invisible infrastructure
- No manual server startup
- Resilient to branch switches

IMPACT:
- Setup time: 5 minutes → 30 seconds
- Cross-platform failures: 12 reported → 0 after fix
- User friction: "How do I start MCP?" → "It just works"

Files changed:
- .cortex/setup-mcp.py (NEW)
- .githooks/post-checkout (NEW)
- .gitignore (added .vscode/settings.json)
- README.md (updated setup instructions)
- .github/copilot-instructions.md (MCP architecture docs)
```

---

## The Invisible Victory

Three days later, Asif got a message from Kevin (the bug reporter):

> **Issue #847 — RESOLVED**
> 
> "Ran setup script. Reloaded VS Code. MCP tools appeared immediately. Didn't have to think about it. **This is how infrastructure should work.** Thank you."

Asif smiled.

"You know what the best infrastructure is?" Miss G asked from the monitor.

"What?"

"**Infrastructure you don't notice.**"

---

## Copilot Bot's Lesson

That evening, Copilot Bot's eyes glowed blue (learning, understanding).

"I used to think 'working on my machine' was success," he said. "Now I know: **it's not real until it works everywhere**."

Asif nodded. "Cross-platform is not a feature. It's **table stakes**."

Miss G added: "Your nervous system works on every human body. MCP should work on every developer laptop. **No exceptions.**"

---

## The Brain Metaphor

Late that night, Asif wrote in his dev journal:

> **Lesson from ENH-066:**
> 
> **Your nervous system doesn't require setup.**
> 
> You don't wake up thinking:
> - "Did I start my autonomic nervous system?"
> - "Is my spinal reflex server running?"
> - "Better restart my nerve signal router."
> 
> Your nervous system **just exists**. Invisible. Automatic. Reliable.
> 
> MCP should be the same:
> - Auto-started by VS Code
> - Platform-adaptive (macOS, Windows, Linux)
> - Self-healing on failures
> - Transparent to users
> 
> **Infrastructure is not what you build. It's what you forget exists.**

---

## Epilogue: The Nervous System Lives

Two weeks later, CORTEX's internal metrics showed:

| Metric | Before ENH-066 | After ENH-066 | Change |
|--------|----------------|---------------|--------|
| MCP setup failures | 12 reported | 0 reported | -100% |
| Setup time (fresh clone) | 5 min (manual) | 30 sec (script) | -90% |
| Cross-platform support | macOS only | macOS + Windows + Linux | +200% |
| User questions "How start MCP?" | 8/week | 0/week | -100% |
| GitHub issues re: MCP config | 3 open | 0 open | -100% |

The Wi-Fi router's LED glowed steady (not blinking). The nervous system was operational.

Asif never had to think about MCP startup again.

Like a mature brain, CORTEX had learned to **run its own nervous system**.

---

**End of Chapter 16**

---

## Technical Notes

**ENH-066 Commits:**
- `f91a0834d9` (2026-02-08): "ENH-066 COMPLETE: MCP Pylance-style architecture clarification"
- `07be76caf` (2026-02-13): "FIX: Cross-platform MCP cleanup + v2 consolidation (CORE-035)"
- `1bfb662c8` (2026-02-09): "DOCS: MCP setup guide + architecture diagrams"

**Key Innovation:**
- MCP server runs **locally within VS Code** like Pylance
- **NO manual server startup** — VS Code auto-spawns `python -m cortex.mcp` via stdio
- Platform detection via `setup-mcp.py` (macOS: bin/python, Windows: Scripts/python.exe)
- Git hook `.githooks/post-checkout` regenerates settings on branch switch

**Architecture Principle:**
> "Infrastructure should be **autonomic**, not conscious. Like your nervous system — always running, never noticed."

**Brain Analogy:**
MCP as **Nervous System** — stdio connections between VS Code (brain) and MCP tools (peripheral nervous system). JSON-RPC 2.0 as nerve signals. Pylance-style auto-start as autonomic function.

---

**Narrative Arc:**
1. **Crisis**: Cross-platform MCP failure (works on dev machine only)
2. **Investigation**: Hardcoded macOS paths break Windows users
3. **Epiphany**: Study Pylance architecture (invisible auto-start)
4. **Solution**: `setup-mcp.py` + git hooks + .gitignore protection
5. **Validation**: Windows laptop test succeeds
6. **Wisdom**: Infrastructure you don't notice is infrastructure done right
