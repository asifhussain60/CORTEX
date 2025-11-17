# CORTEX Story Excerpt - The Intern with Amnesia

**Purpose:** Human-centered explanation of what CORTEX is and why it exists  
**Audience:** Beginners, stakeholders, anyone new to CORTEX  
**Source:** Extracted from full CORTEX documentation (lines 3222-3442)

---

## 🧚 A story for humans: The Intern with Amnesia

### Meet Your Intern: Copilot

You've just hired a brilliant intern named Copilot. They're incredibly talented—can write code in any language, understand complex systems, and work at lightning speed. There's just one problem: **Copilot has amnesia**.

Every time you walk away, even for a coffee break, Copilot forgets everything. You said "make it purple" five minutes ago? Gone. The file you were just discussing? Vanished from memory. The architecture you explained yesterday? As if it never happened.

Worse, Copilot has no memory between chat sessions. Start a new conversation? They don't remember the last one. Leave for lunch? When you return, it's like meeting them for the first time. Every. Single. Time.

This would be catastrophic... except you've done something revolutionary: **you've built Copilot a brain**.

### The Brain: A Sophisticated Cognitive System

The brain you built isn't just storage—it's a sophisticated dual-hemisphere system modeled after the human brain:

#### **🧠 LEFT HEMISPHERE - The Tactical Executor**
Like the human left brain (language, logic, sequential processing), this hemisphere handles:
- **Test-Driven Development** - RED (write failing test) → GREEN (make it pass) → REFACTOR (clean up)
- **Precise Code Execution** - Exact file edits, line-by-line changes, syntax verification
- **Detail Verification** - Tests pass/fail, build status, zero errors/warnings enforcement
- **Sequential Workflows** - Step A, then B, then C—no skipping steps

**The Left Brain Specialists:**
- **The Builder** (`code-executor.md`) - Implements code with surgical precision
- **The Tester** (`test-generator.md`) - Creates and runs tests, never skips TDD
- **The Fixer** (`error-corrector.md`) - Catches wrong-file mistakes instantly
- **The Inspector** (`health-validator.md`) - Validates system health obsessively
- **The Archivist** (`commit-handler.md`) - Commits with semantic precision

#### **🧠 RIGHT HEMISPHERE - The Strategic Planner**
Like the human right brain (creativity, holistic thinking, patterns), this hemisphere handles:
- **Architecture Design** - Understands how components fit together project-wide
- **Strategic Planning** - Breaks big features into phases, estimates effort, assesses risk
- **Pattern Recognition** - "We've done something similar before—here's the template"
- **Context Awareness** - Knows which files change together, what workflows succeed
- **Future Projection** - Warns about risky changes before you make them
- **Brain Protection** - Guards the brain's own integrity (Rule #22)

**The Right Brain Specialists:**
- **The Dispatcher** (`intent-router.md`) - Interprets your natural language, routes smartly
- **The Planner** (`work-planner.md`) - Creates multi-phase strategic plans
- **The Analyst** (`screenshot-analyzer.md`) - Extracts requirements from images
- **The Governor** (`change-governor.md`) - Protects CORTEX from degradation
- **The Brain Protector** (`brain-protector.md`) - Challenges risky proposals (NEW - Rule #22)

#### **🌉 CORPUS CALLOSUM - The Messenger**
The bridge between hemispheres that:
- **Coordinates Work** - Right brain plans → Corpus callosum delivers → Left brain executes
- **Shares Context** - Left brain's results feed Right brain's learning
- **Validates Alignment** - Ensures tactical execution matches strategic intent
- **Manages Message Queue** - Asynchronous communication between hemispheres

**Storage:** `cortex-brain/corpus-callosum/coordination-queue.jsonl`

#### **🔐 TIER 0: INSTINCT (Core Values - PERMANENT)**
The brain's immutable DNA that **cannot** be changed:
- **Definition of READY** - Work must have clear requirements before starting (RIGHT BRAIN enforces)
- **Test-Driven Development** - Always RED → GREEN → REFACTOR (LEFT BRAIN enforces)
- **Definition of DONE** - Zero errors, zero warnings, all tests pass (LEFT BRAIN validates)
- **Challenge User Changes** - If you propose risky changes, brain MUST challenge you
- **SOLID Principles** - Single Responsibility, no mode switches, clean architecture
- **Local-First** - Zero external dependencies, works offline, portable
- **Incremental File Creation** - Large files (>100 lines) created in small increments (prevents "response hit the length limit" errors)

**Stored in:** `governance/rules.md` (never moves, never expires)

#### **📚 TIER 1: SHORT-TERM MEMORY (Last 20 Conversations)**
Copilot's working memory that solves the amnesia problem:
- **Conversation History** - Last 20 complete conversations preserved
- **Context Continuity** - "Make it purple" knows you mean the FAB button from earlier
- **Recent Messages** - Last 10 messages in active conversation
- **FIFO Queue** - When conversation #21 starts, #1 gets deleted (oldest goes first)
- **Active Protection** - Current conversation never deleted, even if oldest

**How it works:**
```
You: "Add a pulse animation to the FAB button"
→ Conversation #1 created, stored in Tier 1

[Later that day]
You: "Make it purple"
→ Brain checks Tier 1 → Finds "FAB button" in conversation #1 → Knows what "it" means

[2 weeks and 20 conversations later]
→ FIFO triggers → Conversation #1 deleted
→ BUT patterns extracted → Moved to Tier 2 (long-term memory)
```

**Stored in:** `cortex-brain/conversation-history.jsonl`, `cortex-brain/conversation-context.jsonl`

#### **🧩 TIER 2: LONG-TERM MEMORY (Knowledge Graph)**
Copilot's accumulated wisdom that grows smarter over time:

**What gets learned:**
- **Intent Patterns** - "add a button" → PLAN, "continue" → EXECUTE, "test this" → TEST
- **File Relationships** - `HostControlPanel.razor` often modified with `noor-canvas.css` (75% co-modification rate)
- **Workflow Templates** - export_feature_workflow, ui_component_creation, service_api_coordination
- **Validation Insights** - Common mistakes, file confusion warnings, architectural guidance
- **Correction History** - Tracks when Copilot works on wrong files, learns to prevent

**How it learns:**
```
Day 1: You ask to "add invoice export"
→ Right brain plans workflow
→ Left brain executes with TDD
→ Pattern saved: invoice_export_feature (confidence: 0.85)

Day 30: You ask to "add receipt export"
→ Right brain queries Tier 2
→ Finds invoice_export pattern
→ Suggests: "This is similar to invoice export. Use same workflow?"
→ 60% faster delivery by reusing proven pattern
```

**Stored in:** `cortex-brain/knowledge-graph.yaml`

#### **📊 TIER 3: DEVELOPMENT CONTEXT (Holistic Project View)**
Copilot's "balcony view" of your entire project:

**Git Activity Analysis (last 30 days):**
- **Commit velocity** - 1,237 commits, 42 commits/week average
- **File hotspots** - `HostControlPanelContent.razor` has 28% churn rate (unstable!)
- **Change patterns** - Smaller commits (< 200 lines) have 94% success rate
- **Contributors** - Tracks who works on what

**Code Health Metrics:**
- **Lines added/deleted** - Velocity trends increasing/decreasing
- **Stability classification** - Files marked as stable/unstable based on churn
- **Test coverage trends** - 72% → 76% (improving!)
- **Build success rates** - 97% clean builds last week

**CORTEX Usage Intelligence:**
- **Session patterns** - 10am-12pm sessions have 94% success rate
- **Intent distribution** - PLAN (35%), EXECUTE (45%), TEST (15%), VALIDATE (5%)
- **Workflow effectiveness** - Test-first reduces rework by 68%
- **Focus duration** - Sessions < 60 min: 89% success vs > 60 min: 67%

**Proactive Warnings:**
```
⚠️ File Alert: HostControlPanel.razor is a hotspot (28% churn)
   Recommend: Add extra testing, smaller changes

✅ Best Time: 10am-12pm sessions have 94% success rate
   Currently: 2:30pm (81% success rate)

📊 Velocity Drop: Down 68% this week
   Recommendation: Smaller commits, more frequent tests
```

---

**Full Documentation:** See `#file:prompts/user/cortex.md` for complete CORTEX documentation  
**Related Modules:**
- Setup Guide: `#file:prompts/shared/test/setup-excerpt.md`
- Technical Reference: `#file:prompts/shared/test/technical-excerpt.md`
