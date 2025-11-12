# Your First Task

Walk through a complete CORTEX workflow from start to finish.

## Scenario: Add a Share Button

We'll add a share button with a pulse animation to a web application. This task demonstrates:

- ✅ Natural language interaction
- ✅ Test-driven development (RED → GREEN → REFACTOR)
- ✅ Automatic learning
- ✅ Semantic commits

**Time:** 5-10 minutes

---

## Step 1: Make Your Request

Open GitHub Copilot Chat and type:

```markdown
#file:prompts/user/cortex.md

Add a share button with a pulse animation to the header component
```

Press Enter.

---

## Step 2: Watch RIGHT BRAIN Analyze

CORTEX's RIGHT BRAIN (strategic planner) springs into action:

**What You'll See:**

```
🧠 CORTEX RIGHT BRAIN - Strategic Analysis

Intent: PLAN (confidence: 0.95)
Request: Add share button with pulse animation

📊 Tier 3 Analysis (Development Context):
  - header.jsx: 12% churn rate (stable file ✅)
  - Similar features: 8 button additions in last 30 days
  - Average completion: 18 minutes
  - Success rate with tests: 96%

🧩 Tier 2 Pattern Match (Knowledge Graph):
  - Pattern found: "button_with_animation" (confidence: 0.87)
  - Previous: FAB button pulse (3 weeks ago)
  - Components: CSS keyframes + JSX + event handler
  - Element ID required for tests ✅

📚 Tier 1 Context (Recent Memory):
  - Conversation #7: Added like button to header (2 days ago)
  - Same component, same workflow
  - Element ID pattern: "header-{action}-btn"

Strategic Plan Created:
  Phase 1: Test Preparation (Element ID mapping)
  Phase 2: RED (Create failing tests)
  Phase 3: GREEN (Implement feature)
  Phase 4: REFACTOR (Validate & commit)

Estimated time: 18 minutes
Ready for execution ✅
```

---

## Step 3: LEFT BRAIN Executes (Phase 1)

**Test Preparation:**

```
🧪 TESTER AGENT (Phase 1: Preparation)

Element ID Assignment:
  Suggested: "header-share-btn"
  Pattern: Follows existing convention
  Purpose: Enable robust Playwright selectors

Documenting in knowledge graph...
  File: cortex-brain/knowledge-graph.yaml
  Section: ui_element_ids
  Entry created ✅

Ready for test creation.
```

---

## Step 4: RED Phase - Failing Tests

```
🧪 TESTER AGENT (Phase 2: RED)

Creating test: tests/ui/header-share-button.spec.js

Test Cases:
  1. Share button exists with ID
  2. Share button has pulse animation
  3. Share button triggers share action

Running tests...
  ❌ Share button exists with ID
     Error: Element '#header-share-btn' not found
  ❌ Share button has pulse animation
     (Skipped - button doesn't exist)
  ❌ Share button triggers share action
     (Skipped - button doesn't exist)

Status: ✅ RED phase complete (tests failing as expected)
Event logged to Tier 4
```

---

## Step 5: GREEN Phase - Implementation

```
⚙️ BUILDER AGENT (Phase 3: GREEN)

Files to modify:
  1. src/components/Header.jsx
  2. src/styles/header.css

Changes:
  [Header.jsx]
  + <button 
  +   id="header-share-btn"
  +   className="share-btn pulse-animation"
  +   onClick={handleShare}
  +   aria-label="Share this page">
  +   <ShareIcon />
  + </button>

  [header.css]
  + @keyframes pulse {
  +   0%, 100% { transform: scale(1); }
  +   50% { transform: scale(1.1); }
  + }
  + 
  + .pulse-animation {
  +   animation: pulse 2s infinite;
  + }

Running tests...
  ✅ Share button exists with ID (1.2s)
  ✅ Share button has pulse animation (890ms)
  ✅ Share button triggers share action (1.5s)

Status: ✅ GREEN phase complete (all tests passing)
Event logged to Tier 4
```

---

## Step 6: REFACTOR Phase - Validation

```
🔍 INSPECTOR AGENT (Phase 4: REFACTOR)

Health Validation:

Build Check:
  npm run build
  ✅ Build successful (0 errors, 0 warnings)

Test Suite:
  npm test
  ✅ All 127 tests passing

Accessibility:
  ✅ Button has aria-label
  ✅ Keyboard accessible (focusable)
  ✅ Color contrast: 4.8:1 (WCAG AA ✅)

Code Quality:
  ✅ No linting errors
  ✅ Proper naming conventions
  ✅ Element ID follows pattern

Status: ✅ REFACTOR phase complete
Ready for commit
```

---

## Step 7: Semantic Commit

```
🗂️ ARCHIVIST AGENT (Commit Handler)

Commit Analysis:
  Type: feat (new feature)
  Scope: header (component affected)
  Files: 2 modified, 1 test created

Creating commit...

git add src/components/Header.jsx src/styles/header.css tests/ui/header-share-button.spec.js
git commit -m "feat(header): Add share button with pulse animation

- Added share button with ID #header-share-btn
- Implemented pulse animation (2s infinite)
- Created 3 Playwright tests (all passing)
- WCAG AA compliant (4.8:1 contrast)
- Test-driven implementation (RED → GREEN → REFACTOR)

Element ID documented in brain for future reference."

✅ Committed successfully
Event logged to Tier 4
```

---

## Step 8: Brain Learning

```
🧠 BRAIN UPDATE (Automatic)

Events logged: 5
  - test_created (RED)
  - implementation_complete (GREEN)
  - validation_complete (REFACTOR)
  - commit_complete
  - pattern_reinforced

Tier 1 (Conversation Memory):
  Conversation #8 created
  Topic: "Add share button with pulse animation"
  Status: Complete ✅
  Duration: 6 minutes 12 seconds

Tier 2 (Knowledge Graph):
  Pattern reinforced: button_with_animation
  Confidence: 0.87 → 0.89 ↑
  File relationship: Header.jsx + header.css
  Co-modification: 14 → 15 occurrences

Tier 3 (Development Context):
  Commits this week: 42 → 43
  Test-first adoption: 94% (excellent!)
  Average feature time: 18 min → 17.5 min ↓

Next similar task will be even faster! 🚀
```

---

## What You Accomplished

In under 10 minutes, CORTEX:

1. ✅ **Analyzed** your request using 3-tier brain intelligence
2. ✅ **Planned** a strategic 4-phase approach
3. ✅ **Created** element ID for robust testing
4. ✅ **Wrote** failing tests first (RED)
5. ✅ **Implemented** minimum code (GREEN)
6. ✅ **Validated** health and accessibility (REFACTOR)
7. ✅ **Committed** with semantic message
8. ✅ **Learned** patterns for next time

All with a single natural language request!

---

## Try More Commands

### Resume After a Break

```markdown
#file:prompts/user/cortex.md

Where did I leave off?
```

Response:
```
📚 Last Session Summary

Conversation #8 (6 minutes ago):
  Topic: Add share button with pulse animation
  Status: ✅ Complete
  Files modified: Header.jsx, header.css
  Tests: 3 new (all passing)

Current state:
  - Build: ✅ Green
  - Tests: ✅ 127/127 passing
  - Branch: feature/share-button
  - Last commit: "feat(header): Add share button..."

Ready for next feature! What would you like to work on?
```

### Ask for Context

```markdown
#file:prompts/user/cortex.md

What are the most unstable files in this project?
```

Response (from Tier 3):
```
📊 File Stability Report (last 30 days)

High Churn (⚠️ Unstable):
  1. UserProfile.jsx - 28% churn, 47 edits
  2. AuthService.js - 24% churn, 39 edits
  3. Dashboard.jsx - 22% churn, 35 edits

Recommendations:
  - Extra validation for high-churn files
  - Consider refactoring (extract components)
  - Add integration tests for stability

Stable Files (✅ Safe to modify):
  - Header.jsx - 12% churn
  - Footer.jsx - 8% churn
  - NotFound.jsx - 3% churn
```

### Request Architecture Insights

```markdown
#file:prompts/user/cortex.md

Show me which files are commonly modified together
```

Response (from Tier 2):
```
🧩 File Relationships (co-modification patterns)

Strong relationships (>70%):
  - AuthService.js ↔ LoginForm.jsx (89%)
  - BillingService.js ↔ InvoiceList.jsx (75%)
  - Header.jsx ↔ header.css (85%)

Recommendation: When modifying one, check the other!

Workflow templates available:
  - auth_flow (sign in/sign out coordination)
  - billing_export (invoice + email integration)
  - ui_component (component + styles + tests)
```

---

## Next Steps

Now that you've completed your first task:

- **[Configuration](configuration.md)** - Customize CORTEX settings
- **[Understanding Agents](../guides/agent-workflows.md)** - Learn about specialist agents
- **[Memory Tiers](../guides/memory-tiers.md)** - Deep dive into the brain system

## Key Takeaways

1. **One command does everything** - No need to memorize agent names
2. **Test-first is automatic** - RED → GREEN → REFACTOR enforced
3. **Brain learns continuously** - Each task improves the next
4. **Quality is non-negotiable** - Zero errors, zero warnings, all tests pass

Welcome to development with a brain! 🧠✨
