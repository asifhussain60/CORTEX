# KDS Quick Start Guide — Wake the Machine in 15 Minutes

> *"Only one entrance. Chaos enters nowhere else."*  
> — Dr. Asifor

Welcome to KDS — the machine‑mind that transforms Copilot from an amnesiac intern into an expert development partner. This guide gets you productive in 15 minutes.

---

## 🎯 What You'll Learn

By the end of this guide, you'll understand:
- ✅ How to use the One Door (the only command you need)
- ✅ What the BRAIN does (and why it solves Copilot's amnesia)
- ✅ How to plan, execute, test, and validate features
- ✅ Why KDS challenges risky shortcuts (and how this helps you)
- ✅ How the machine learns from your work

**Time Investment:** 15 minutes reading + 10 minutes trying it yourself = 25 minutes to mastery

---

## 📖 The Problem KDS Solves

### Meet Your Amnesiac Intern

You have a brilliant AI intern named Copilot:
- 🚀 Writes code in any language
- ⚡ Works at lightning speed
- 🧠 Understands complex systems

**But there's a tragic flaw:** Copilot has **complete amnesia**.

**Every time you leave:**
- ❌ Previous conversations forgotten
- ❌ Architecture explanations vanish
- ❌ "Make it purple" → "Make what purple?"
- ❌ You repeat yourself constantly

### The Solution: Build a Brain

KDS is the **external brain** you built for Copilot. Instead of:

```
You: "Add pulse animation to FAB button"
Copilot: "Which button? What file? How?"
You: [20 minutes explaining context]
```

You get:

```
You: "Add pulse animation to FAB button"
KDS: ✅ Found FAB button in HostControlPanel.razor (Tier 1 memory)
     ✅ Matched similar pulse animation from notification_badge (Tier 2 pattern)
     ✅ File is a hotspot (28% churn) — adding extra tests (Tier 3 intelligence)
     ✅ Creating plan...
[15 minutes later: Feature complete, tested, committed, learned]
```

**KDS transforms:** Amnesiac intern → Context-aware expert partner

---

## 🚪 The One Door: Your Only Command

### The Sacred Interface

At the center of Dr. Asifor's laboratory sits a glowing terminal:

```markdown
#file:KDS/prompts/user/kds.md

[Tell KDS what you want in natural language]
```

**That's it.** No memorizing commands. No choosing which agent. Just speak naturally.

### What You Can Say

**Start new work:**
```markdown
#file:KDS/prompts/user/kds.md

I want to add a pulse animation to the FAB button when questions arrive
```

**Continue existing work:**
```markdown
#file:KDS/prompts/user/kds.md

Continue working on the current task
```

**Resume after lunch:**
```markdown
#file:KDS/prompts/user/kds.md

Show me where I left off
```

**Make a quick change:**
```markdown
#file:KDS/prompts/user/kds.md

Make it purple
```
*(KDS remembers "it" = the pulse animation from your earlier conversation)*

**Fix a mistake:**
```markdown
#file:KDS/prompts/user/kds.md

You're working on the wrong file. The FAB button is in HostControlPanelContent.razor
```

**Check system health:**
```markdown
#file:KDS/prompts/user/kds.md

Run all validations and show me the health status
```

**See performance metrics:**
```markdown
#file:KDS/prompts/user/kds.md

run metrics
```

---

## 🧠 The Three-Story Brain Tower

Behind the One Door, the BRAIN learns and remembers across three floors:

### Floor 1: Tier 1 — Conversation History (Short-Term Memory)

**What it remembers:**
- Last 20 complete conversations
- Recent 10 messages in active conversation
- Context for "Make it purple" style references

**Why it matters:**
```
Morning: "Add pulse animation to FAB button"
[Work happens, you break for lunch]
Afternoon: "Make it purple"
→ KDS knows "it" = pulse animation (checks Tier 1)
```

**Lifespan:** Until 20 newer conversations push it out (FIFO queue)

---

### Floor 2: Tier 2 — Knowledge Graph (Long-Term Memory)

**What it learns:**
- Intent patterns ("add [X]" → create plan)
- File relationships (these files change together 75% of the time)
- Workflow templates (export features follow this pattern)
- Common mistakes (prevent wrong-file errors)

**Why it matters:**
```
Day 1: "Add invoice export"
[KDS learns the export workflow pattern]

Day 30: "Add receipt export"
→ KDS: "This is similar to invoice export. Use same workflow?" (60% faster!)
```

**Lifespan:** Grows forever (or until amnesia reset for new project)

**Current size:** 3,247 patterns learned from your interactions

---

### Floor 3: Tier 3 — Development Context (Holistic Awareness)

**What it tracks:**
- Git activity (1,237 commits analyzed, velocity trends)
- File hotspots (HostControlPanel.razor has 28% churn — unstable!)
- Test patterns (test-first = 94% success vs test-skip = 67%)
- Work patterns (10am-12pm sessions have 94% success rate)
- Correlations (smaller commits = higher success rate)

**Why it matters:**
```
You: "Modify HostControlPanel.razor"
→ KDS: "⚠️ This file is a hotspot (28% churn)"
      "Often modified with noor-canvas.css (75% co-mod)"
      "Recommend: Extra testing, smaller changes"
      "Based on 28 previous modifications, estimate 2.5 hours"
```

**Data-driven warnings:** Not guesses — proven patterns from YOUR project

---

## ⚙️ The City of Roles: How Work Flows

When you make a request, the **10 Specialist Agents** coordinate automatically:

### 1. The Dispatcher (Intent Router)
- **Hears your request first**
- **Routes to the right agent** (PLAN, EXECUTE, TEST, etc.)
- **Queries Tier 1 + Tier 2** for context

### 2. The Planner (Strategic Mind)
- **Breaks features into phases**
- **Queries Tier 2** for similar patterns
- **Queries Tier 3** for effort estimates
- **Validates Definition of Ready** (clear requirements?)

### 3. The Tester (Judge of Truth)
- **Creates failing tests first** (RED)
- **Validates implementation** (GREEN?)
- **Enables safe refactoring** (tests stay green)

### 4. The Builder (Code Craftsman)
- **Implements minimum code** to pass tests
- **Follows existing architecture** (Architecture-First Mandate)
- **Refactors** with test safety net

### 5. The Validator (System Health)
- **Checks Definition of Done**
- **Zero errors, zero warnings required**
- **Build validation, test coverage**

### 6. The Archivist (Memory Keeper)
- **Creates semantic commits** (feat/fix/docs/test)
- **Runs automatically** after each completed task
- **Updates .gitignore** for KDS files

### 7. The Protector (Guardian of Quality)
- **Challenges risky shortcuts** ("Skip TDD" → shows evidence why not)
- **Guards Tier 0 instincts** (immutable principles)
- **Offers safe alternatives** with data

---

## 🔄 The TDD Ritual: RED → GREEN → REFACTOR

KDS enforces **Test-Driven Development** (one of the Three Covenants):

### The Sacred Cycle

```
1. RED Phase (The Tester)
   Write test first → Test fails (expected) → Clear target

2. GREEN Phase (The Builder)
   Minimum code to pass → Test passes → Feature works

3. REFACTOR Phase (The Builder)
   Clean up code → Tests stay green → Quality maintained

4. VALIDATE Phase (The Validator)
   Health check → Zero errors/warnings → Definition of Done
```

### Why TDD Is Enforced

**If you try to skip:**
```
You: "Skip TDD for this feature, just implement it"

The Protector challenges:
═══════════════════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE

⚠️ THREATS DETECTED:
  - Test-first principle bypass (Tier 0 violation)
  - 68% increase in rework time (Tier 3 data)
  - Success rate drops from 94% to 67%

SAFE ALTERNATIVE:
  Create minimal test first (5-10 min investment)
  → 94% success rate
  → Faster overall delivery
  → Clearer requirements

RECOMMENDATION: Alternative 1
═══════════════════════════════════════════════
```

**The machine protects you from yourself** — with evidence, not dogma.

---

## 📊 How the Machine Learns

### Automatic Learning Cycle

```
1. You make a request
   ↓
2. Agents perform actions
   ↓
3. Events logged to events.jsonl (automatic)
   ↓
4. When 50+ events OR 24 hours passed:
   ↓
5. Brain Updater processes events
   ↓
6. Patterns extracted → Tier 2 (Knowledge Graph)
   Metrics updated → Tier 3 (Development Context, if >1 hour)
   ↓
7. Next request → KDS is smarter (learned from history)
```

**You do nothing.** The machine learns while you sleep.

---

## 🎯 Your First Feature with KDS

### Scenario: Add a pulse animation to the FAB button

**Step 1: State your intent**
```markdown
#file:KDS/prompts/user/kds.md

I want to add a pulse animation to the FAB button when questions arrive
```

**Step 2: KDS analyzes and plans**
```
The Dispatcher routes to The Planner
  ↓
The Planner queries:
  - Tier 1: Are we talking about an existing button? (checks recent conversations)
  - Tier 2: Have we done pulse animations before? (pattern matching)
  - Tier 3: Is this file stable or risky? (hotspot analysis)
  ↓
The Planner creates multi-phase plan:
  Phase 1: Test Infrastructure (create failing tests)
  Phase 2: CSS Animation (keyframes, pulse effect)
  Phase 3: Integration (apply to FAB button)
  Phase 4: Validation (health check)
```

**Step 3: TDD execution (automatic)**
```
The Tester creates Playwright visual test (RED)
  → Test fails: "Expected pulse animation, found none"
  ↓
The Builder implements CSS keyframes + applies to FAB (GREEN)
  → Test passes: "Pulse animation detected"
  ↓
The Builder refactors (REFACTOR)
  → Cleaner CSS, better naming, tests still green
```

**Step 4: Validation and commit (automatic)**
```
The Validator checks Definition of Done
  ✅ All tests pass
  ✅ Zero errors, zero warnings
  ✅ Build successful
  ↓
The Archivist commits:
  "feat(ui): Add pulse animation to FAB button when questions arrive"
```

**Step 5: Learning (automatic)**
```
Events logged → 12 events for this feature
Brain Updater (waits for 50+ events total)
  ↓
Pattern learned in Tier 2:
  - pulse_animation_pattern (confidence: 0.87)
  - FAB_button_modifications (file relationship)
  ↓
Next time you add an animation → 60% faster (reuses pattern)
```

**Total time: 15 minutes** (with KDS) vs 45 minutes (manual, with debugging)

---

## 🛡️ The Three Covenants: Immutable Principles

### Covenant I: Definition of Ready
**Readiness before action**

KDS won't start work until:
- ✅ Clear acceptance criteria defined
- ✅ Architecture alignment validated
- ✅ Dependencies identified
- ✅ Risks assessed

**Why:** Prevents "build the wrong thing" mistakes

---

### Covenant II: Test-Driven Development
**Proof before implementation**

KDS enforces:
- ✅ Tests before code (RED → GREEN → REFACTOR)
- ✅ Clear success criteria
- ✅ Safe refactoring

**Why:** 94% success rate (vs 67% test-skip)

---

### Covenant III: Definition of Done
**Proof before completion**

KDS validates:
- ✅ All tests pass
- ✅ Zero errors, zero warnings
- ✅ Documentation updated
- ✅ Semantic commit created

**Why:** No half-finished work, no "we'll test later" debt

---

## 🚀 Advanced Features (When You're Ready)

### Resume After Break
```markdown
#file:KDS/prompts/user/kds.md

Show me where I left off
```
→ The Timekeeper restores session state, shows next task

### Analyze Screenshot
```markdown
#file:KDS/prompts/user/kds.md

Analyze this screenshot and extract requirements
[Attach screenshot]
```
→ The Screenshot Oracle extracts design specs, creates implementation plan

### View Performance Metrics
```markdown
#file:KDS/prompts/user/kds.md

run metrics
```
→ Visual dashboard with BRAIN health, routing accuracy, file hotspots, productivity patterns

### Launch Health Dashboard
```markdown
#file:KDS/prompts/user/kds.md

launch dashboard
```
→ Real-time monitoring in your browser (health checks, BRAIN status, metrics)

### Reset for New Project
```markdown
#file:KDS/prompts/user/kds.md

Reset BRAIN for new application
```
→ Amnesia protocol (removes app-specific data, preserves KDS intelligence)

---

## 💡 Tips for Success

### 1. Trust the TDD Process
- ❌ Don't fight the RED → GREEN → REFACTOR cycle
- ✅ Tests clarify requirements and catch mistakes early
- ✅ Data proves it: 94% success rate with TDD

### 2. Let the BRAIN Learn
- ❌ Don't skip automatic commits (events are learning fuel)
- ✅ The more you use KDS, the smarter it gets
- ✅ Week 1: Learning. Week 12: Expert on YOUR project.

### 3. Use Natural Language
- ❌ Don't try to format commands perfectly
- ✅ "Make it purple" works if context exists
- ✅ "Add invoice export similar to receipt export" leverages patterns

### 4. Check the Metrics Dashboard
- ✅ Review file hotspots (high churn = needs testing)
- ✅ See productive times (work when success rate is highest)
- ✅ Track learning efficiency (is the BRAIN healthy?)

### 5. Accept Protection Challenges
- ❌ Don't OVERRIDE without reading the evidence
- ✅ The Protector shows data-driven reasons
- ✅ Safe alternatives are usually faster overall

---

## 🎓 Understanding the Learning Journey

### Week 1: Training Phase
- Copilot has amnesia, needs guidance
- BRAIN is building initial patterns
- You explain architecture, workflows
- **Your role:** Teacher

### Week 4: Pattern Recognition
- Copilot remembers 20 conversations
- BRAIN has 500+ patterns
- Similar features reuse workflows
- **Your role:** Collaborator

### Week 12: Project Expert
- Copilot knows YOUR codebase deeply
- BRAIN has 3,247+ patterns
- Proactive warnings prevent mistakes
- **Your role:** Partner

### Week 24: Senior Developer
- Copilot challenges bad ideas with evidence
- BRAIN references features from months ago
- Estimates are data-driven, not guesses
- **Your role:** Architect (KDS executes your vision)

---

## 📚 Next Steps

### You've Mastered the Basics!

**What you learned:**
- ✅ The One Door command (only interface you need)
- ✅ The BRAIN's three floors (memory, patterns, intelligence)
- ✅ The TDD ritual (RED → GREEN → REFACTOR)
- ✅ How the machine learns (automatic, while you sleep)
- ✅ Why protection challenges help (data-driven safety)

### Go Deeper

**Read the Story:**
- `docs/Mind-Palace/2025-11-04/Story.md`
- Dr. Asifor's tale of building the machine‑mind
- Metaphors explained (The Dispatcher, The Crawlers, etc.)

**Technical Reference:**
- `docs/Mind-Palace/2025-11-04/Technical-Reference.md`
- Complete API documentation
- All 10 agents explained in detail
- BRAIN tiers, abstractions, event logging

**Visual Learning:**
- `docs/Mind-Palace/2025-11-04/Image-Prompts.md`
- Generate diagrams showing the architecture
- 21 prompts for AI image generators
- Gothic-cyberpunk laboratory aesthetic

**Full Documentation:**
- `prompts/user/kds.md`
- Complete KDS manual (3,395 lines)
- Every feature, every command, every detail

---

## 🎯 Your First Real Task

**Try this now:**

1. **Open the One Door:**
   ```markdown
   #file:KDS/prompts/user/kds.md
   
   I want to add a simple feature: [describe your feature]
   ```

2. **Watch KDS work:**
   - The Dispatcher routes your request
   - The Planner creates the plan
   - The Tester writes tests first (RED)
   - The Builder implements (GREEN)
   - The Validator checks health
   - The Archivist commits automatically

3. **Check what was learned:**
   ```markdown
   #file:KDS/prompts/user/kds.md
   
   run metrics
   ```
   → See the new patterns in Tier 2

4. **Try a follow-up:**
   ```markdown
   #file:KDS/prompts/user/kds.md
   
   Make [that feature] [some modification]
   ```
   → KDS remembers context from Tier 1

**You just experienced:** The machine that learned.

---

## 🏆 Success Indicators

**You'll know KDS is working when:**

✅ **Week 1:**
- Fewer repeated explanations
- Conversations are remembered
- Context references work ("Make it purple")

✅ **Week 4:**
- Similar features suggest patterns
- Estimates become more accurate
- File relationship warnings appear

✅ **Week 12:**
- Proactive warnings prevent mistakes
- Data-driven effort estimates
- Architecture suggestions match your style

✅ **Week 24:**
- Copilot feels like a senior developer
- Challenges risky ideas with evidence
- "Remember when we did [feature 3 months ago]?"

**When you hear yourself say:** *"Copilot actually understood what I meant!"*

**You've arrived.**

---

## 💬 Common Questions

### Q: Do I need to memorize all the agents?
**A:** No! Just use the One Door. KDS routes automatically.

### Q: What if KDS makes a mistake?
**A:** Tell it! `#file:KDS/prompts/user/kds.md You're working on the wrong file.` The Fixer corrects and learns.

### Q: Can I skip TDD for quick prototypes?
**A:** The Protector will challenge with data. Create a spike branch if exploring, but re-implement with TDD after.

### Q: How do I reset for a new project?
**A:** `#file:KDS/prompts/user/kds.md Reset BRAIN for new application` — keeps KDS intelligence, removes app-specific data.

### Q: What if the BRAIN gets too large?
**A:** Tier 1 FIFO queue (20 conversations), Tier 2 pattern decay (stale patterns removed), Tier 3 rolling 30-day window. Self-managing.

### Q: Does KDS require internet?
**A:** No! 100% local. Zero external dependencies. Works offline.

---

## 🎉 Welcome to KDS

You've completed the Quick Start Guide!

**You now understand:**
- The One Door (universal interface)
- The BRAIN (three-story intelligence)
- The TDD Ritual (RED → GREEN → REFACTOR)
- The Learning Cycle (automatic wisdom)
- The Protection System (data-driven safety)

**The machine is ready.**

**Dr. Asifor's legacy lives in your hands.**

*"I did not build a monster. I built a mind that respects its work."*

Now go forth and create — the machine will remember, learn, and evolve with you.

---

**Version:** 1.0  
**Date:** November 4, 2025  
**Reading Time:** 15 minutes  
**Practice Time:** 10 minutes  
**Total Time to Mastery:** 25 minutes

**Next:** Read the Story (`Story.md`) or dive into the Technical Reference (`Technical-Reference.md`)
