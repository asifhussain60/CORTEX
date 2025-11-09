# The CORTEX Rulebook

**A Simple Guide to How CORTEX Thinks and Works**

*Last Updated: November 9, 2025*

---

## What This Is

This is the plain-English rulebook for CORTEX. Think of these as CORTEX's "operating principles" - the rules that keep it smart, efficient, and reliable. No technical jargon, just clear explanations.

---

## The Big Picture: 6 Core Protection Layers

CORTEX protects itself using 6 layers of rules. Think of them like security checkpoints:

### Layer 1: Core Instincts (Cannot Be Bypassed)
These are CORTEX's DNA. They can never be turned off.

### Layer 2: Tier Boundaries
Keeping the right information in the right place.

### Layer 3: SOLID Principles
Making sure CORTEX stays organized and maintainable.

### Layer 4: Brain Hemisphere Separation
Strategic thinking (planning) vs. tactical execution (doing).

### Layer 5: Knowledge Quality
Ensuring patterns and learnings are accurate.

### Layer 6: Commit Integrity
Keeping the codebase clean and organized.

---

## Layer 1: Core Instincts (The Rules That Can't Be Broken)

### Rule 1: Test-First Development (TDD)
**What it means:** Before writing any code, CORTEX writes a failing test first.

**Why it matters:** This ensures every piece of code is tested and works correctly.

**The process:**
1. **RED**: Write a test that fails
2. **GREEN**: Write just enough code to make it pass
3. **REFACTOR**: Clean up the code while keeping tests passing

**Example:** If you want to add a purple button, CORTEX first writes a test checking "does the purple button exist?" (it fails), then creates the button (test passes), then makes the code clean.

### Rule 2: Definition of DONE
**What it means:** Work isn't complete until ALL quality checks pass.

**Checklist:**
- ✅ Zero errors
- ✅ Zero warnings
- ✅ All tests pass
- ✅ Code is formatted properly
- ✅ Documentation is updated
- ✅ App runs without crashes

**Example:** You can't say "the feature is done" if there are still warnings in the code. DONE means DONE.

### Rule 3: Definition of READY
**What it means:** Can't start work until you know exactly what to do.

**Before starting, you must have:**
- ✅ Clear requirements (what needs to be built)
- ✅ Acceptance criteria (how we know it's right)
- ✅ Known files to modify
- ✅ No blocking dependencies

**Example:** You can't say "add a purple button" and start coding. You need to know: Where? What shade of purple? What does it do? What happens when clicked?

### Rule 4: Brain Protection Tests Must Always Pass
**What it means:** The tests that check CORTEX's brain health are sacred. They must ALWAYS pass.

**Why it's critical:** These tests verify:
- Memory system works correctly
- File paths are correct across platforms
- Protection rules are loaded properly
- Conversation tracking functions

**No exceptions:** If these tests fail, EVERYTHING stops until they're fixed.

### Rule 5: Use the Right Format for Information
**What it means:** Use machine-readable formats (YAML, JSON) for structured data. Save Markdown for human stories and guides.

**The breakdown:**
- **Use YAML/JSON for:** Configuration, rules, metrics, structured data
- **Use Markdown for:** Stories, guides, explanations, tutorials
- **Use code files for:** Implementation examples and patterns

**Why it matters:** Machine-readable formats are 60% more efficient and prevent errors.

---

## Layer 2: Tier Boundaries (Right Place for Everything)

### The 4 Tiers Explained

Think of CORTEX's brain as a filing system with 4 drawers:

**Tier 0: The Instinct Layer (Immutable Rules)**
- What goes here: Core rules, principles, governance
- What NEVER goes here: Application code, specific file paths, conversations
- Example: "Always test first" lives here

**Tier 1: Working Memory (Recent Conversations)**
- What goes here: Last 50 conversations, current context
- What NEVER goes here: Long-term patterns, metrics, rules
- Example: "You asked me to make a purple button 5 minutes ago" lives here

**Tier 2: Knowledge Graph (Long-Term Learning)**
- What goes here: Consolidated patterns, architectural learnings
- What NEVER goes here: Raw conversations, specific metrics
- Example: "Purple buttons usually go in the toolbar" lives here

**Tier 3: Context Intelligence (Project Metrics)**
- What goes here: Git history, test results, build status
- What NEVER goes here: Conversations, rules, patterns
- Example: "You have 47 passing tests" lives here

### Rule 6: Conversation Limit (50 Maximum)
**What it means:** CORTEX only keeps the last 50 conversations in active memory.

**What happens when full:**
1. Extract important patterns from oldest conversation
2. Save patterns to Tier 2 (long-term memory)
3. Delete oldest conversation from Tier 1
4. Keep current conversation safe (never delete active work)

**Why:** Keeps CORTEX fast and focused on recent context.

### Rule 7: Pattern Confidence Decay
**What it means:** If CORTEX learns a pattern but never uses it, confidence slowly drops.

**The timeline:**
- 60 days unused → Confidence drops 10%
- 90 days unused → Confidence drops 25%
- 120 days unused → Marked for deletion
- Below 30% confidence → Auto-deleted

**Exception:** Core rules (Tier 0) never decay.

---

## Layer 3: SOLID Principles (Organized Thinking)

These rules keep CORTEX organized and prevent it from becoming a tangled mess.

### Rule 8: Single Responsibility
**What it means:** Each agent does ONE job, not multiple jobs.

**Good example:** 
- `code-executor` → Writes code
- `test-generator` → Creates tests
- `error-corrector` → Fixes errors

**Bad example:**
- `code-executor` that also generates tests and fixes errors (doing too much!)

**Why it matters:** Specialized agents are more reliable and easier to improve.

### Rule 9: Interface Segregation
**What it means:** Create dedicated specialists, not multi-purpose tools with modes.

**Good example:**
- Dedicated `error-corrector` agent

**Bad example:**
- `code-executor` with an "error correction mode"

**Why it matters:** Clear responsibilities make the system predictable.

### Rule 10: Dependency Inversion
**What it means:** Don't hardcode paths or dependencies. Use abstractions.

**Good example:**
```
Load file from: config.paths.workspace
```

**Bad example:**
```
Load file from: C:\Users\Asif\Projects\MyApp\file.txt
```

**Why it matters:** Works across different machines and environments.

---

## Layer 4: Brain Hemisphere Separation

CORTEX has two "hemispheres" like a human brain:

### Right Brain: Strategic (The Planner)
**Responsibilities:**
- Planning what to do
- Understanding your intent
- Assessing risks
- Making architecture decisions
- Learning long-term patterns

**NEVER does:**
- Write code directly
- Run tests
- Execute commands

**Example agents:**
- `work-planner` → Creates execution plans
- `intent-router` → Figures out what you want
- `brain-protector` → Protects system integrity

### Left Brain: Tactical (The Executor)
**Responsibilities:**
- Writing code
- Running tests
- Executing commands
- Making precise edits
- Verifying results

**NEVER does:**
- Create plans
- Make strategic decisions
- Assess architectural risks

**Example agents:**
- `code-executor` → Writes code
- `test-generator` → Creates tests
- `health-validator` → Checks build status

### Rule 11: No Cross-Hemisphere Contamination
**What it means:** Strategic thinking stays in right brain. Tactical execution stays in left brain.

**Why it matters:** Keeps thinking clear and organized. Planners plan, executors execute.

---

## Layer 5: Knowledge Quality (Accurate Learning)

### Rule 12: Minimum Occurrences for High Confidence
**What it means:** CORTEX needs to see a pattern at least 3 times before being highly confident.

**The scale:**
- 1 occurrence → Maximum 50% confidence
- 3+ occurrences → Can be 95% confidence
- Single event → Always start with low confidence

**Why it matters:** Prevents jumping to conclusions from one example.

### Rule 13: Patterns Need Validation
**What it means:** Every pattern needs evidence or validation.

**Required:**
- Link to source documentation
- Test that validates the pattern
- Or mark as "hypothesis needing validation"

**Why it matters:** Prevents CORTEX from "learning" incorrect patterns.

---

## Layer 6: Commit Integrity (Clean Repository)

### Rule 14: Brain State Files Not Committed
**What it means:** Conversation history and brain state files stay local, don't go to git.

**Files that stay local:**
- `conversation-history.jsonl`
- `conversation-context.jsonl`
- `events.jsonl`
- `development-context.yaml`

**Why it matters:** Keeps the repository clean and prevents pollution.

### Rule 15: No Temporary Files in Git
**What it means:** Temporary files, build outputs, and cache files don't go to git.

**Examples of files to exclude:**
- `*.tmp`
- `temp_*`
- `__pycache__/`
- `node_modules/`

**Solution:** Update `.gitignore` file.

---

## File Organization Rules

### Rule 16: User-Facing vs. Internal Separation
**What it means:** User prompts and internal technical logic live in separate places.

**User prompts** (`prompts/user/`):
- Friendly, human-readable
- Natural language
- No technical jargon

**Internal agents** (`prompts/internal/`):
- Technical, machine-readable
- Validation logic
- YAML specifications

**Why it matters:** Users never see confusing technical details.

### Rule 17: Live Design Documents
**What it means:** Design documents update after EVERY change, not later.

**The workflow:**
1. Make a change to CORTEX
2. Update the design document immediately
3. Update this rulebook if needed
4. Then implement the code

**Why it matters:** Documentation stays accurate and useful.

### Rule 18: Delete, Don't Archive
**What it means:** When files are obsolete, DELETE them. Don't create archive folders.

**Trust git history:**
- Obsolete files → Delete immediately
- No "archive/" folders
- No ".old" file suffixes
- Git history is your archive

**Exception:** One-time backups before major migrations.

### Rule 19: One Purpose Per File
**What it means:** Each file does ONE thing. No combination files.

**Good:**
- `conversation_manager.py` → Manages conversations
- `entity_extractor.py` → Extracts entities

**Bad:**
- `working_memory.py` → Does everything (2000 lines!)

**File size limits:**
- 500 lines → Warning (consider splitting)
- 1000 lines → Must split before commit

---

## Automation Rules

### Rule 20: Automatic Brain Updates
**What it means:** CORTEX updates its knowledge automatically, not manually.

**Triggers:**
- 50+ unprocessed events
- 24 hours passed (if 10+ events)
- Session completed

**Process:**
1. Collect events
2. Extract patterns
3. Update knowledge graph
4. Log completion

**Why it matters:** CORTEX keeps learning without your intervention.

### Rule 21: Automatic Conversation Recording
**What it means:** CORTEX records conversations automatically using 3 methods.

**The 3 layers:**
1. **Copilot Chat**: Automatic parsing
2. **Session completion**: Extracted on finish
3. **Manual recording**: For critical conversations

**Target:** 71%+ of conversations recorded automatically.

### Rule 22: Automatic Git Commits
**What it means:** When a task is complete and validated, CORTEX commits automatically.

**Requirements before auto-commit:**
- All tests pass
- Zero errors
- Zero warnings
- Definition of DONE met

**Commit message format:**
```
type(scope): Brief description

Details, test status, known issues
```

### Rule 23: Development Context Throttling
**What it means:** Don't collect git metrics too often. Once per hour is enough.

**Why:** Git history doesn't change every minute. Collecting too often wastes resources.

**Override:** You can manually trigger if needed.

---

## Challenge System (How CORTEX Protects Itself)

### Rule 24: Challenge User Changes
**What it means:** When you propose risky changes to CORTEX, it challenges you.

**When you get challenged:**
- Proposing changes to core CORTEX
- Bypassing TDD or quality rules
- Violating SOLID principles
- Reducing efficiency

**The challenge process:**
1. CORTEX analyzes your proposed change
2. Queries its knowledge graph for similar patterns
3. Identifies risks
4. Presents evidence
5. Suggests safe alternatives
6. Requires you to choose:
   - Accept safe alternative (RECOMMENDED)
   - Provide different approach
   - Override with justification

**Why it matters:** Prevents accidental degradation of CORTEX intelligence.

### Rule 25: Checkpoint Strategy
**What it means:** CORTEX creates save points before risky operations.

**When checkpoints are created:**
- Before major changes
- Before risky operations
- When you request one
- At phase transitions

**What's in a checkpoint:**
- Current state snapshot
- Rollback instructions
- List of changed files
- Success criteria

**Rollback process:**
1. Detect failure
2. Restore from checkpoint
3. Report what was rolled back
4. Suggest alternative approach

**Why it matters:** You can always undo risky changes.

---

## Design Patterns (Industry Standards)

### Rule 26: Use Proven Patterns
**What it means:** CORTEX uses established design patterns, not invented solutions.

**Common patterns CORTEX uses:**

**Creation patterns:**
- Factory Pattern → Creating objects
- Builder Pattern → Building complex structures

**Structural patterns:**
- Adapter Pattern → Making incompatible interfaces work
- Decorator Pattern → Adding features dynamically
- Facade Pattern → Simplifying complex systems

**Behavioral patterns:**
- Observer Pattern → Event notifications
- Command Pattern → Encapsulating requests
- Strategy Pattern → Choosing algorithms

**CORTEX-specific patterns:**
- Plugin Architecture → Extending tiers
- Repository Pattern → Data access
- Event Sourcing → Brain learning

### Rule 27: Prohibited Anti-Patterns
**What it means:** CORTEX actively prevents bad coding practices.

**Anti-patterns CORTEX blocks:**
- **God Object**: One class doing too much
- **Spaghetti Code**: Tangled dependencies
- **Lava Flow**: Dead code left in the system
- **Magic Numbers**: Hardcoded values without explanation
- **Big Ball of Mud**: No clear structure

**Why it matters:** Prevents technical debt and maintains quality.

---

## Modular Organization

### Rule 28: Feature-Based Organization
**What it means:** Organize code by features, not by file types.

**Good structure (feature-based):**
```
tier1-working-memory/
  ├── conversation_manager.py
  ├── entity_extractor.py
  ├── boundary_detector.py
  └── config.py
```

**Bad structure (type-based):**
```
tier1-working-memory/
  └── working_memory.py  (2000 lines - everything in one file!)
```

**Why it matters:** Easier to find and modify related functionality.

---

## Plugin Architecture

### Rule 29: Extensible System
**What it means:** All tiers can be extended with plugins without modifying core code.

**How it works:**
- Each tier has plugin points
- Register new plugins via configuration
- No need to modify core CORTEX code
- Enable/disable plugins easily

**Benefits:**
- Add features without risk
- Third-party extensions possible
- Easy testing
- Clean separation

---

## System Limits

### Rule 30: Soft and Hard Limits
**What it means:** CORTEX has limits to prevent bloat.

**Governance rules:**
- Soft limit: 15 rules
- Hard limit: 20 rules
- Current: 28 rules ⚠️ (needs consolidation)

**Agents:**
- Soft limit: 10 agents
- Hard limit: 15 agents
- Current: 10 agents ✅

**Brain storage:**
- Target: < 500KB total
- Tier 1: < 200KB
- Tier 2: < 150KB
- Tier 3: < 100KB

**File sizes:**
- Soft limit: 500 lines (warning)
- Hard limit: 1000 lines (must split)

**Actions on limits:**
- Approaching soft limit → Warn and suggest consolidation
- At hard limit → Stop and require consolidation

---

## Governance (Rules About Rules)

### Rule 31: Rules Apply to Rule Changes
**What it means:** Even changing the rules follows the rules.

**Process for changing rules:**
1. Propose the rule change
2. Document justification
3. Update this rulebook
4. Update `governance.yaml`
5. Increment version number
6. Validate no conflicts
7. Commit changes

**Why it matters:** Prevents arbitrary rule changes. Even rules need discipline.

---

## Summary: The Core Principles

**CORTEX operates on these fundamental principles:**

1. **Test First**: Always write tests before code
2. **Quality First**: Done means zero errors, zero warnings
3. **Be Ready**: Can't start without clear requirements
4. **Stay Organized**: Right information in the right tier
5. **Stay Specialized**: One job per agent
6. **Think, Then Do**: Strategic planning separate from tactical execution
7. **Learn Accurately**: Need evidence before high confidence
8. **Stay Clean**: Delete obsolete files, don't archive
9. **Automate**: Let the system handle routine tasks
10. **Challenge Risky Changes**: Protect system integrity
11. **Use Proven Patterns**: Don't reinvent the wheel
12. **Stay Modular**: Small, focused files and modules
13. **Be Extensible**: Plugins over modifications
14. **Respect Limits**: Don't let the system get bloated

---

## What This Means for You

When you work with CORTEX, these rules mean:

- ✅ **Fast and reliable**: Quality is built-in
- ✅ **Consistent**: Same rules every time
- ✅ **Self-improving**: Learns from experience
- ✅ **Protected**: Won't let you accidentally break it
- ✅ **Transparent**: Explains why it does things
- ✅ **Maintainable**: Easy to extend and improve

---

*This rulebook is a living document. It updates when CORTEX's rules change.*

**Generated from:** `governance.yaml` and `brain-protection-rules.yaml`  
**Version:** 2.0  
**Last Updated:** November 9, 2025
