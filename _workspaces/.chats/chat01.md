User: Follow instructions in [create-skill.prompt.md](file:///Users/asifhussain/.vscode/extensions/github.copilot-chat-0.39.0/assets/prompts/create-skill.prompt.md).

GitHub Copilot: # 🧠 CORTEX Introducing
**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.

---

> *"Before software can be reusable it first has to be usable."*
> — Ralph Johnson, **Patterns of Enterprise Application Architecture**

---

Let me load the `agent-customization` skill first to follow the correct template and principles. 

Read skill [agent-customization](copilot-skill:/agent-customization/SKILL.md?vscodeLinkType%3Dskill)

Read skill `agent-customization`: [](copilot-skill:/agent-customization/references/skills.md)

No prior workflow emerged from the conversation to generalize. Let me interview you to design the right skill. 

Analyzing your answers...

Good. Let me explore the existing .github structure to avoid duplication and understand what's already there. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/scripts)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/scripts)

No existing `skills/` directory. I have everything I need to draft a comprehensive skill. Building now. 

Created 3 todos

Created [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md)

Starting: *Validate YAML frontmatter and file structure* (2/3)

Ran terminal command:  python3 -c "
import yaml, re

with open('/Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md', 'r') as f:
    content = f.read()

# Extract frontmatter
fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
if fm_match:
    try:
        fm = yaml.safe_load(fm_match.group(1))
        print('✅ Frontmatter valid')
        print(f'  name: {fm[\"name\"]}')
        print(f'  description length: {len(fm[\"description\"])} / 1024 chars')
        print(f'  argument-hint: {fm.get(\"argument-hint\", \"(none)\")}')
    except yaml.YAMLError as e:
        print(f'❌ YAML error: {e}')
else:
    print('❌ No frontmatter found')

# Check folder name matches
import os
folder = os.path.basename(os.path.dirname('/Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md'))
if folder == fm.get('name'):
    print(f'✅ Folder name matches name field: {folder}')
else:
    print(f'❌ Mismatch: folder={folder}, name={fm.get(\"name\")}')

# Line count
lines = content.count('\n')
print(f'✅ Line count: {lines} / 500 recommended max')
"


All validations pass. Let me now identify and address any weak spots. 

Starting: *Review weak spots and refine* (3/3)

The most ambiguous parts of the current draft are:

1. **Description keyword coverage** — `/frontend`, `/typescript`, `/csharp`, `/decompose`, `/train`, `/meta-audit` commands are missing from the description trigger list (agents search descriptions).
2. **Branching logic depth** — the Intent Classification Gateway table is good but could have a Decision Tree for when multiple intents overlap (e.g., "fix a failing test" → FIX or DEBUG?).
3. **`MCP tool: validate_orchestrator_context` guard** — the MCP authoring rule is missing from the Governance section.

Let me fix all three now:  

Using "Multi-Replace String in Files"

Replacing 1 lines with 1 lines in [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md)


```

```


Replacing 3 lines with 15 lines in [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md)


```

```


Replacing 2 lines with 40 lines in [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md)


```

```


Ran terminal command:  python3 -c "
import yaml, re
with open('/Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md') as f:
    content = f.read()
fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---', content, re.DOTALL).group(1))
print(f'description length: {len(fm[\"description\"])} / 1024')
print(f'line count: {content.count(chr(10))} (max 500 rec)')
"


532 lines — slightly over the 500 recommended soft limit, but within acceptable range for a framework this comprehensive. The 500 line cap is a guideline, not hard enforcement. Description is well within the 1024 char limit at 548. 

Completed: *Review weak spots and refine* (3/3)

---

The skill is created and validated at SKILL.md.

**What it produces:**
- A slash command cortex (and auto-loaded on any CORTEX-related request) that gives agents a structured routing guide across all 17+ CORTEX commands
- Intent Classification Gateway table — routes to the right section instantly
- Overlap Disambiguation table — resolves ambiguous cases (e.g. "failing test" → `/debug` vs `/fix`)
- Full procedure steps per command: audit, debug, implement, refactor, test, review, RCA, totalrecall, domain-specific workflows
- Embedded governance rules (CORE-002 through CORE-068) and MCP authoring guard

**Example prompts to try:**
```
/cortex audit          → routes to Audit & Quality section
/cortex debug          → routes to Debugging Pipeline with 8 strategies
/cortex implement      → routes to TDD workflow with CORE-008 enforcement
/cortex                → shows Intent Classification Gateway
```

**Suggested next customizations:**
1. **`.github/skills/cortex-tdd/SKILL.md`** — a dedicated TDD skill with the full red-green-refactor cycle and test tier guidance
2. **`.github/skills/cortex-rca/SKILL.md`** — deep-dive RCA skill with methodology selection trees and prevention rule templates
3. **`.github/instructions/cortex-governance.instructions.md`** — always-on governance rules applied to every file edit (applyTo: `cortex/**/*.py`)

✅ **All work is complete.** The skill is live and will be auto-discovered by Copilot Chat when any CORTEX command or workflow is mentioned.

Made changes.

User: how do the skills work?

GitHub Copilot: # 🧠 CORTEX Answering
**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.

---

> *"Simplicity is prerequisite for reliability."*
> — Edsger W. Dijkstra, **Selected Writings on Computing**

---

## 🔍 Analysis

> 💡 **Principle: Progressive Disclosure**
> Surface only what's needed at each stage. Overloading agents with context upfront burns tokens and degrades precision.

Skills use a **3-stage progressive loading** model:

### Stage 1 — Discovery (~100 tokens)
When you type in Copilot Chat, the agent reads only the `name` and `description` fields from every SKILL.md frontmatter. This is how it decides whether to load a skill — the description is the **discovery surface**. If your keywords aren't in it, the skill is invisible.

### Stage 2 — Load (<5,000 tokens)
When the description matches the request, the agent loads the full SKILL.md body into context. This contains procedures, tables, commands, decision trees.

### Stage 3 — Resources (on demand)
Additional files (scripts, reference docs, templates) are loaded **only when explicitly referenced** from within SKILL.md — e.g. `[See reference](./references/deep-dive.md)`. They are never loaded unless needed.

---

### Invocation — two ways

| Method | How |
|---|---|
| **Slash command** | Type cortex in chat → appears in the `/` menu |
| **Auto-loaded** | Agent detects the description matches → loads silently |

Control this with frontmatter:

```yaml
user-invocable: false          # hides from slash menu, still auto-loads
disable-model-invocation: true # appears in slash menu, never auto-loads
# both omitted = default: slash command + auto-load both on
```

---

### File layout

```
.github/skills/cortex/
├── SKILL.md           ← frontmatter (discovery) + body (procedures)
├── scripts/           ← executable assets loaded on demand
├── references/        ← deep-dive docs, loaded only when linked
└── assets/            ← templates / boilerplate
```

The `name` field in frontmatter **must match the folder name** exactly — a mismatch causes silent failure with no error.

---

### Why it beats putting everything in copilot-instructions.md

copilot-instructions.md is always-on — it burns context on every interaction regardless of relevance. Skills only load when relevant, keeping the context window lean for unrelated tasks.

✅ **All work is complete.**