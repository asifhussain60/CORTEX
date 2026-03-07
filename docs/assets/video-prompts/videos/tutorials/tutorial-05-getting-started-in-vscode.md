# NotebookLM Video Prompt -- Tutorial 05 -- Getting Started in VS Code

**Target length:** ~6 minutes
**Audience:** First-time users who installed CORTEX and want to navigate VS Code confidently
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent)
**Prerequisite:** Tutorial 01 complete (installation and smoke test passing)
**Narrator gender:** Female (T05 -- odd)
**Goal:** Viewer can navigate the VS Code workspace, confirm MCP is active, and run first verification commands

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- VS Code workspace orientation: cortex/, cortex-registry/, tests/ as the three pillars
- MCP detection within VS Code: how to confirm the server is active from the UI
- First safe verification commands from Copilot Chat
- The "VS Code awakening" visual motif: CORTEX activating within the VS Code panel

Does NOT repeat: installation steps (T01), command catalogue (T02), E2E feature build (T03), multi-repo onboarding (T04), chat workflow sequencing (T06), result interpretation (T07).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create a ~6 minute hands-on tutorial for first-time users opening the CORTEX workspace in VS Code. Cover: workspace orientation (three key folders), confirming MCP is active in Copilot Chat, and running the first three safe verification commands. Narration must explain what each panel and folder is for -- not describe UI navigation steps. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never describes where to click. Every narration line explains what a panel or command is for, what to look for, and what it means if it is missing.

---

## Cinematic treatment -- "VS Code Awakening"

**Unique opening (VS Code panel activation -- T05's visual identity):**
A VS Code window appears -- dark, minimal. The CORTEX workspace is open but no panels are highlighted.
A soft amber glow begins at the bottom-left: the file explorer.
Three folders illuminate sequentially with amber outlines: cortex/ ... cortex-registry/ ... tests/
On-screen label appears beside each:
  cortex/ -- "The framework"
  cortex-registry/ -- "The rules"
  tests/ -- "The proof"
Then: the Copilot Chat panel icon illuminates amber in the sidebar.
On-screen label: "And here is where CORTEX speaks."
This is T05's signature: the IDE coming alive around CORTEX, not the other way around.

### Visual Physics
- Background: actual VS Code dark theme with amber amber highlights overlaid
- Amber outline: 2px amber glow on file explorer items as they activate
- Copilot Chat icon: amber pulse when referenced
- Command cards: glassmorphic amber panels overlaid when commands are run

---

## Scene-by-scene breakdown

**SCENE 1 -- "VS Code Awakening" [0:00-0:45]**
VS Code opens. Three folder illuminations. Copilot Chat icon pulses.
Narrator: "CORTEX lives in three places in VS Code. The framework code in cortex/, the governance rules in cortex-registry/, and the test suite in tests/. Keep these three coherent and the system is healthy. Let any one drift and the audit will tell you."

**SCENE 2 -- "Confirming MCP is Active" [0:45-2:00]**
Copilot Chat opens. User types @cortex -- tool suggestion list appears.
Camera zooms: `.vscode/settings.json` MCP server block shown briefly.
Narrator: "MCP tools appear in Copilot Chat as suggestions when the server is active. You do not start a server manually. You do not check a port. If you see the cortex tools in the suggestion list, MCP is running. If you do not see them, reload VS Code -- the server starts on workspace load."
Lower-third: "No suggestions? Reload VS Code. MCP starts on workspace open."

**SCENE 3 -- "First Safe Verification Commands" [2:00-4:30]**
Three commands, each shown as a glassmorphic command card activating in Copilot Chat:

Card 1: `cortex_verify op=mcp`
Response: MCP server active, 29 tools registered.
Narrator: "This confirms the MCP server is running and all tools are registered. The 29 tool count is the expected value -- if you see fewer, a tool file may have a syntax error."

Card 2: `cortex_tools_catalog`
Response: Tool list renders -- grouped by category.
Narrator: "The tools catalog shows you what CORTEX can do from chat. It is also your first check that the tool registry is complete. Each tool listed here corresponds to a registered function in mcp_registry.py."

Card 3: `cortex_load op=rules`
Response: Governance rules render -- 32 rules listed.
Narrator: "Loading rules confirms the governance registry is healthy. If a YAML file in cortex-registry/core/ has a syntax error, this call will show fewer rules. Thirty-two is the expected count."

**SCENE 4 -- "Run a Smoke Test from the Terminal" [4:30-5:30]**
VS Code terminal panel opens (amber border). `make test-smoke` runs.
Progress bar fills amber. PASSED.
Narrator: "The smoke test is faster from the terminal than from chat. It runs directly against the test suite without the MCP round-trip. Use it as your daily sanity gate -- 60 seconds before any significant work."

**SCENE 5 -- "What to Do Next" [5:30-End]**
Amber outro card:
- cortex/ -- framework -- do not modify without tests
- cortex-registry/ -- rules -- extend in company/ not core/
- tests/ -- proof -- always growing, never shrinking
"Next: Tutorial 06 -- Your First Chat Workflows"
Narrator: "You have a working VS Code setup, confirmed MCP, and a passing smoke test. That is the complete readiness baseline. Everything in Tutorial 06 builds on this."

---

## Audio direction
- Folder illumination: three sequential soft amber tones, ascending
- Copilot Chat icon: a warm amber pulse sound
- Command card activation: amber click, response = green chime
- No cold start -- environment is already warm

---

## Production note
The VS Code awakening opening requires actual VS Code UI for credibility. Plan screen-capture inserts for Scene 1 and Scene 2 -- stitch after NotebookLM export. The glassmorphic command cards for Scene 3 can be generated by NotebookLM as slides. Do not use placeholder UI mockups for the VS Code panels.
