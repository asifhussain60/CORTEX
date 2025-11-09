
asifhussain60: 

#file:prompts/user/cortex-slim-test.md

Tell me the CORTEX story

GitHub Copilot: I'll read the slim test file and tell you the CORTEX story. 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/user/cortex-slim-test.md)

I can see that the slim test file is routing to modules. Let me read the story excerpt module that it references: 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/shared/test/story-excerpt.md)

# The CORTEX Story: The Intern with Amnesia 🧚

## Meet Your Brilliant (but Forgetful) Intern

You've hired **Copilot**—an incredibly talented intern who can code in any language, understand complex systems, and work at lightning speed. But there's one critical problem: **Copilot has amnesia**.

Every coffee break? Memory wiped. Start a new chat? They've forgotten everything. You said "make it purple" five minutes ago? Gone. The architecture you explained yesterday? Vanished.

This would be catastrophic... **except you've built Copilot a brain**.

---

## 🧠 The Dual-Hemisphere Brain Architecture

The brain isn't just storage—it's a sophisticated cognitive system modeled after the human brain:

### **LEFT HEMISPHERE - The Tactical Executor** ⚙️
Handles precise, sequential work:
- **Test-Driven Development** - RED → GREEN → REFACTOR (always)
- **Precise Code Execution** - Line-by-line edits, syntax verification
- **Detail Verification** - Zero errors/warnings enforcement
- **Sequential Workflows** - Step A → B → C (no skipping)

**Left Brain Specialists:**
- **The Builder** - Implements code with surgical precision
- **The Tester** - Creates tests, never skips TDD
- **The Fixer** - Catches wrong-file mistakes instantly
- **The Inspector** - Validates system health obsessively

### **RIGHT HEMISPHERE - The Strategic Planner** 🎯
Handles big-picture, creative thinking:
- **Architecture Design** - Project-wide understanding
- **Strategic Planning** - Multi-phase breakdowns, effort estimates
- **Pattern Recognition** - "We've done this before—here's the template"
- **Context Awareness** - Which files change together
- **Brain Protection** - Guards CORTEX's integrity (Rule #22)

**Right Brain Specialists:**
- **The Dispatcher** - Routes your natural language smartly
- **The Planner** - Creates strategic multi-phase plans
- **The Analyst** - Extracts requirements from screenshots
- **The Governor** - Protects CORTEX from degradation

### **CORPUS CALLOSUM - The Messenger** 🌉
Bridges the hemispheres:
- Right brain plans → Left brain executes
- Left brain's results → Right brain learns
- Ensures tactical execution matches strategic intent

---

## 🏛️ The Three-Tier Memory System

### **TIER 1: SHORT-TERM MEMORY** (Last 20 Conversations)
Solves the amnesia problem:
```
You: "Add a pulse animation to the FAB button"
→ Stored in Tier 1

Later: "Make it purple"
→ Brain checks Tier 1 → Knows "it" = FAB button ✅
```

After 20 conversations, oldest gets deleted—but patterns move to Tier 2.

### **TIER 2: LONG-TERM MEMORY** (Knowledge Graph)
Accumulated wisdom:
- **Intent Patterns** - "add a button" → PLAN
- **File Relationships** - These files usually change together
- **Workflow Templates** - Proven patterns for features
- **Correction History** - Learns from mistakes

Example:
```
Day 1: "Add invoice export"
→ Creates workflow pattern (confidence: 0.85)

Day 30: "Add receipt export"  
→ Finds similar pattern → 60% faster delivery 🚀
```

### **TIER 3: DEVELOPMENT CONTEXT** (Holistic View)
The balcony view of your project:
- **Git activity** - Commit velocity, file hotspots (28% churn = unstable!)
- **Code health** - Test coverage trends, build success rates
- **Usage intelligence** - Best times to work (10am-12pm = 94% success)
- **Proactive warnings** - ⚠️ This file is unstable—add extra testing

---

## ⚡ The Result

**Before CORTEX (Amnesia):**
- "Make it purple" → ❌ "What do you mean?"
- New chat → ❌ Starts from scratch
- No learning → ❌ Same mistakes repeated

**After CORTEX (With Brain):**
- "Make it purple" → ✅ Knows you mean FAB button
- New chat → ✅ Remembers last 20 conversations
- Pattern learning → ✅ Gets smarter over time
- Proactive guidance → ✅ Warns before mistakes

---

**This is CORTEX**: A cognitive AI system that transforms GitHub Copilot from a brilliant amnesiac into an experienced team member who remembers, learns, and gets better every day.

---

*For more details: Setup Guide | Technical Reference*






asifhussain60: #file:prompts/user/cortex-slim-test.md

How do I set up CORTEX?

GitHub Copilot: I'll read the slim test entry point file to see how it routes setup-related queries. 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/user/cortex-slim-test.md)

Now I'll read the setup excerpt module that should be loaded for setup-related queries. 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/shared/test/setup-excerpt.md)

Based on the CORTEX slim entry point routing and the setup excerpt module, here's how to set up CORTEX:

## 🚀 Quick Start Setup

### Step 1: Set Environment Variables

**Windows (PowerShell as Administrator):**
```powershell
[Environment]::SetEnvironmentVariable("CORTEX_ROOT", "D:\PROJECTS\CORTEX", "User")
[Environment]::SetEnvironmentVariable("CORTEX_BRAIN_PATH", "D:\PROJECTS\CORTEX\cortex-brain", "User")
# Close and reopen terminal
```

**macOS/Linux:**
```bash
export CORTEX_ROOT="$HOME/PROJECTS/CORTEX"
export CORTEX_BRAIN_PATH="$CORTEX_ROOT/cortex-brain"
source ~/.zshrc
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt

# For VS Code extension (optional)
cd cortex-extension
npm install
```

### Step 3: Initialize CORTEX Brain

```bash
python scripts/cortex_setup.py
```

This creates the tier1/tier2/tier3 brain directories, initializes SQLite databases, and discovers workspace resources.

### Step 4: Verify Installation

```markdown
#file:prompts/user/cortex.md status
```

You should see system status showing all 3 tiers connected.

## ⚠️ Important: Conversation Tracking

GitHub Copilot Chat **does not automatically track** conversations to the CORTEX brain. Choose one option:

**Option 1 - Manual capture after each session:**
```powershell
.\scripts\cortex-capture.ps1 -AutoDetect
```

**Option 2 - Use Python CLI directly:**
```bash
python scripts/cortex_cli.py "Your request here"
```

**Option 3 - Ambient daemon (automatic):**
```bash
python scripts/cortex/auto_capture_daemon.py
```

Without tracking: ❌ No memory across chats  
With tracking: ✅ Full conversation context preserved

---

**For complete setup details:** See setup-excerpt.md


asifhussain60: #file:prompts/user/cortex-slim-test.md

Show me the Tier 1 API reference

GitHub Copilot: I'll help you access the Tier 1 API reference through the slim test entry point. 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/user/cortex-slim-test.md)

Now I'll load the technical excerpt that contains the Tier 1 API reference: 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/shared/test/technical-excerpt.md)

Perfect! I've loaded the Tier 1 API reference from the technical excerpt. Here's the key information:

## 📊 Tier 1 API (Working Memory)

### Core Classes

**WorkingMemory** - Main class for managing conversation memory:

```python
from src.tiers.tier1.working_memory import WorkingMemory

# Initialize
memory = WorkingMemory()

# Store conversation
conversation_id = memory.store_conversation(
    user_message="Add a purple button",
    assistant_response="I'll create that for you",
    intent="EXECUTE",
    context={
        "files_modified": ["HostControlPanel.razor"],
        "agent": "code-executor"
    }
)

# Retrieve recent conversations
recent = memory.get_recent_conversations(limit=5)

# Search conversations
results = memory.search_conversations(
    query="purple button",
    filters={"intent": "EXECUTE"}
)

# Get conversation continuity
context = memory.get_conversation_context(conversation_id)
# Returns: Previous messages, related entities, file references
```

**FIFO Queue Management:**
```python
# Enable FIFO (delete oldest when limit reached)
memory.configure_fifo(
    max_conversations=20,
    enabled=True
)

# Check queue status
status = memory.get_queue_status()

# Manually trigger cleanup
deleted_count = memory.cleanup_old_conversations()
```

**Key Features:**
- Stores last 20 conversations (FIFO queue)
- Retains last 10 messages per conversation
- Tracks entities (files, classes, methods)
- SQLite storage in `cortex-brain/tier1/*.db`
- Fast query performance: **<50ms target** (18ms actual ⚡)


asifhussain60: #file:prompts/user/cortex.md

Add a purple button to the HostControlPanel

GitHub Copilot: I'll help you add a purple button to the HostControlPanel. Let me first read the cortex.md file to understand the project structure and then locate the HostControlPanel component. 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/user/cortex.md)

Now let me search for the HostControlPanel component in the workspace to understand its structure. 

Searched text for `HostControlPanel`, 20 results

Let me search for the actual HostControlPanel file to see if it's a Razor component: 

Searched for files matching `**/HostControlPanel*.razor`, no matches

Searched for files matching `**/HostControlPanel*.*`, no matches

Let me search for any UI component files in the project: 

Searched for files matching `**/*.razor`, no matches

Searched text for `Pages/Host/HostControlPanelContent.razor`, 6 results

Let me check if there's a SPA directory structure: 

Read [](file:///d%3A/PROJECTS/CORTEX)

Searched for files matching `**/Pages/**/*.razor`, no matches

Let me check the src directory structure: 

Read [](file:///d%3A/PROJECTS/CORTEX/src)

Based on my search, it appears that the HostControlPanel component doesn't currently exist in this CORTEX project. The references I found are in documentation files and test scenarios, suggesting this is a hypothetical example used for testing.

Since this is a Python-based project (not a Blazor/Razor web application), let me check if there's any web UI component or if I should create a demonstration of how CORTEX would handle this request.

Let me read the execute.md file to understand how CORTEX handles UI-related requests: 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/user/execute.md#1-1), lines 1 to 101

Based on my investigation, I can see that:

1. **HostControlPanel is a test scenario example** - it's used in documentation and test cases but doesn't actually exist in the current CORTEX codebase
2. **CORTEX is a Python-based project** - it's not a Blazor/Razor web application
3. **The request "Add a purple button to the HostControlPanel"** is used as a demonstration example in Test 4 of the behavioral validation guide

This appears to be a **test scenario** from the Phase 3 validation guide you have open. The purpose is to demonstrate how CORTEX responds to a typical development request.

Since this is a demonstration/test scenario rather than an actual implementation request, let me explain what would happen if this were a real component:

## How CORTEX Would Handle This Request

If HostControlPanel were a real component, CORTEX would:

1. **Detect Intent:** EXECUTE (implementation task)
2. **Route to Agent:** Left brain (Implementer Agent)
3. **Load Context:** Search for HostControlPanel component files
4. **Create Plan:**
   - Locate the component file
   - Add button element with purple styling
   - Update related CSS/styles
   - Add any event handlers if needed
5. **Execute:** Make the code changes
6. **Validate:** Run tests to ensure nothing broke

---

**Would you like me to:**

1. **Create a sample HostControlPanel component** (e.g., a Python Flask/FastAPI route with a web interface) to demonstrate the functionality?
2. **Explain the test scenario** you're looking at in the behavioral test guide?
3. **Help with something else in the CORTEX project?**

asifhussain60: #file:prompts/shared/test/story-excerpt.md

Summarize the CORTEX story

GitHub Copilot: I'll read the story excerpt file to provide you with a summary of the CORTEX story. 

Read [](file:///d%3A/PROJECTS/CORTEX/prompts/shared/test/story-excerpt.md)

## CORTEX Story Summary

**The Core Metaphor:** CORTEX solves the "intern with amnesia" problem—GitHub Copilot is brilliant but forgets everything between sessions. CORTEX builds Copilot a sophisticated dual-hemisphere brain modeled after human cognition.

**The Brain Architecture:**

🧠 **LEFT HEMISPHERE** - Tactical executor handling precise code implementation, TDD workflows (RED→GREEN→REFACTOR), and detail verification through 5 specialists (Builder, Tester, Fixer, Inspector, Archivist).

🧠 **RIGHT HEMISPHERE** - Strategic planner managing architecture design, pattern recognition, risk assessment, and brain protection through 5 specialists (Dispatcher, Planner, Analyst, Governor, Brain Protector).

🌉 **CORPUS CALLOSUM** - Coordinates communication between hemispheres, ensuring strategic planning flows to tactical execution.

**Memory System (4 Tiers):**

- **Tier 0 (Instinct)** - Immutable core values: TDD, zero errors/warnings, SOLID principles
- **Tier 1 (Short-term)** - Last 20 conversations retained via FIFO queue
- **Tier 2 (Long-term)** - Knowledge graph learning patterns, workflows, and file relationships
- **Tier 3 (Development Context)** - Git analytics, code health metrics, and proactive warnings

**The Result:** Copilot transforms from an amnesiac intern into a context-aware, continuously learning development partner that remembers your work, learns from patterns, and protects your codebase from degradation.

