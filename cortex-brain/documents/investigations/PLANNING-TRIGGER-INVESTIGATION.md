# CORTEX Planning Trigger Investigation

**Date:** 2025-11-17  
**Issue:** CORTEX didn't activate planning template for "let's plan Azure DevOps enhancements"  
**Conversation:** #file:CC01  
**Investigator:** CORTEX (Assistant Analysis)

---

## 🎯 Executive Summary

**Problem:** When user invoked `let's plan "Azure DevOps (ADO) enhancements"`, CORTEX bypassed the interactive planning module and went straight to task execution mode, creating todos and documents without using the custom planning template.

**Expected Behavior:** CORTEX should have:
1. Detected "let's plan" trigger
2. Loaded planning template from `response-templates-condensed.yaml`
3. Activated Work Planner agent
4. Followed interactive planning workflow (questions → plan generation → execution option)

**Actual Behavior:** CORTEX:
1. Read CORTEX.prompt.md ✅
2. Searched for existing Azure DevOps content ✅
3. Created todos immediately ❌
4. Started creating planning document ❌
5. Never activated planning template or Work Planner workflow ❌

---

## 🔍 Root Cause Analysis

### Issue 1: Missing Planning Triggers in Response Templates

**Location:** `cortex-brain/response-templates.yaml` and `cortex-brain/response-templates-condensed.yaml`

**Finding:** No explicit trigger mapping for planning keywords

```yaml
# Current routing section (response-templates.yaml lines 200-215)
routing:
  default: fallback
  help_triggers:
    - help
    - /help
    - what can cortex do
  status_triggers:
    - status
    - where are we
  quick_start_triggers:
    - quick start
    - get started
```

**Missing:**
```yaml
  planning_triggers:  # ❌ DOES NOT EXIST
    - plan
    - let's plan
    - plan a feature
    - help me plan
    - planning
```

**Impact:** CORTEX has no way to match user input "let's plan" to the planning template system. The template detection relies on explicit trigger keywords.

---

### Issue 2: Template vs. Module Workflow Disconnect

**Template Location:** `cortex-brain/response-templates-condensed.yaml` (lines 534-562)
**Module Location:** `prompts/shared/help_plan_feature.md`

**Disconnect:**
1. **Templates define response format** (how to display planning stages)
2. **Module defines workflow logic** (what steps to execute)
3. **No bridge between them** - missing orchestration layer

**Current Template Structure:**
```yaml
planning_activation:      # When planning starts
planning_started:         # Confidence assessment
planning_question:        # Each question during discovery
planning_plan_ready:      # Generated plan presentation
planning_complete:        # Success state
planning_aborted:         # User cancellation
```

**Module Workflow:**
```markdown
1. Intent Detection (identifies PLAN intent)
2. Confidence Assessment (80%+ → direct, <80% → questions)
3. Work Planner Agent activation
4. Phase 1: Discovery (questions)
5. Phase 2: Breakdown (tasks/phases)
6. Phase 3: Risk Analysis
7. Phase 4: Roadmap Generation
```

**Problem:** Templates exist, module exists, but **no triggering mechanism** connects them.

---

### Issue 3: CORTEX.prompt.md References Planning But Doesn't Implement Detection

**Location:** `.github/prompts/CORTEX.prompt.md`

**References to Planning:**

1. **Line 20-21:** "📋 **Planning** | Interactive feature planning guide | #file:../../prompts/shared/help_plan_feature.md"
2. **Line 365+:** Multiple planning examples in MANDATORY RESPONSE FORMAT section
3. **Line 746:** "🎯 Intent Detection & Module Structure" mentions auto-routing

**Quote from CORTEX.prompt.md:**
> **Auto-routing:** "Tell me CORTEX story" → story.md | "How do I install?" → setup-guide.md | "Show Tier 1 API" → technical-reference.md

**Problem:** Planning is **documented** but not **implemented** in auto-routing logic.

---

### Issue 4: GitHub Copilot Doesn't Execute Intent Detection by Default

**Critical Insight:** The CORTEX.prompt.md instructions assume intent detection happens automatically, but:

1. **GitHub Copilot Chat** responds directly without intermediate orchestration
2. **No agent dispatcher** intercepts and routes requests
3. **Templates are passive data** - they don't execute themselves
4. **Module references (#file:...) are documentation links**, not executable routing

**What Actually Happens:**
```
User: "let's plan Azure DevOps enhancements"
        ↓
GitHub Copilot: [Reads CORTEX.prompt.md context]
        ↓
GitHub Copilot: [Interprets as direct planning request]
        ↓
GitHub Copilot: [Executes immediate planning behavior]
        ↓
Result: Creates todos and documents (standard execution)
        ❌ Never checks for "planning" triggers
        ❌ Never loads planning templates
        ❌ Never activates Work Planner workflow
```

**What Should Happen:**
```
User: "let's plan Azure DevOps enhancements"
        ↓
Intent Detector: [Matches "let's plan" trigger]
        ↓
Template Loader: [Loads planning_activation template]
        ↓
Work Planner Agent: [Assesses confidence]
        ↓
Interactive Planning Workflow: [Questions → Plan → Execute]
```

---

## 📊 Evidence from Conversation

**User Input:**
```
Follow instructions in CORTEX.prompt.md.
let's plan "Azure DevOps (ADO) enhancements"
```

**CORTEX Response:**
```
I'll read the CORTEX.prompt.md file to understand the instructions 
and then help you plan the Azure DevOps enhancements.

Read CORTEX.prompt.md
Searched codebase for "Azure DevOps ADO enhancements..."
Searched text for `Azure DevOps|ADO`...
Read azure_devops_integration.py
Read capabilities.yaml
Searched for roadmap files
Created 6 todos
Now let me create the comprehensive planning document...
```

**Analysis:**
- ✅ Correctly read CORTEX.prompt.md
- ✅ Correctly gathered context (search, read files)
- ❌ Skipped confidence assessment
- ❌ Skipped interactive questions phase
- ❌ Went straight to todo creation (execution mode)
- ❌ Never referenced planning templates or Work Planner agent

---

## 🎯 Why This Happened

### The Architectural Gap

**CORTEX 2.0/2.1 has three layers:**

1. **Documentation Layer** (CORTEX.prompt.md)
   - Describes how planning *should* work
   - References modules and templates
   - Status: ✅ Complete

2. **Template Layer** (response-templates.yaml)
   - Defines response formats for planning stages
   - Contains trigger keywords (but not planning triggers)
   - Status: 🟡 Incomplete (missing planning triggers)

3. **Execution Layer** (GitHub Copilot Chat behavior)
   - Direct LLM response generation
   - No intermediate routing/orchestration
   - Status: ❌ Not connected to templates or modules

**Missing Component:** Intent detection and routing orchestration between layers

---

## 🔧 Technical Diagnosis

### What Exists

✅ **Planning Module Documentation** (`prompts/shared/help_plan_feature.md`)
- Complete workflow definition
- Examples and best practices
- Agent coordination logic

✅ **Planning Response Templates** (`cortex-brain/response-templates-condensed.yaml`)
- 6 planning-specific templates
- Proper formatting structures
- Placeholders for dynamic content

✅ **Planning Examples in CORTEX.prompt.md**
- Multiple examples (high/low confidence, phases, etc.)
- Next Steps formatting rules
- Challenge/Accept patterns

### What's Missing

❌ **Trigger Keywords for Planning** in response-templates.yaml routing section
❌ **Intent Detection Logic** that matches user input to planning triggers
❌ **Orchestration Layer** that loads templates and activates Work Planner
❌ **Explicit Instruction** in CORTEX.prompt.md to check triggers before responding

---

## 🛠️ Solution Design

### Fix 1: Add Planning Triggers to Response Templates

**File:** `cortex-brain/response-templates.yaml`

**Add to routing section:**
```yaml
routing:
  default: fallback
  help_triggers:
    - help
    - /help
    - what can cortex do
  status_triggers:
    - status
    - where are we
  quick_start_triggers:
    - quick start
    - get started
  planning_triggers:  # ← NEW
    - plan
    - let's plan
    - plan a feature
    - plan this
    - help me plan
    - planning
    - feature planning
    - i want to plan
```

**Impact:** Gives CORTEX explicit keywords to match

---

### Fix 2: Add Template Detection Instruction to CORTEX.prompt.md

**File:** `.github/prompts/CORTEX.prompt.md`

**Insert after line 10 (Response Templates section):**

```markdown
## 🎯 CRITICAL: Template Trigger Detection

**BEFORE responding to ANY user request:**

1. **Check for template triggers:**
   - Load #file:../../cortex-brain/response-templates.yaml
   - Match user input against trigger keywords in `routing` section
   - If match found: Load corresponding template and follow its structure

2. **Planning Detection (PRIORITY):**
   - Keywords: "plan", "let's plan", "planning", "plan a feature"
   - If detected: Load `planning_activation` template
   - Activate Work Planner agent workflow
   - Follow interactive planning process from #file:../../prompts/shared/help_plan_feature.md

3. **If no trigger match:**
   - Proceed with standard CORTEX response format
   - Use appropriate Next Steps format for work type

**Examples:**
- User: "help" → Match `help_triggers` → Load `help_table` template
- User: "let's plan auth" → Match `planning_triggers` → Load `planning_activation` template
- User: "add button" → No match → Standard response format
```

---

### Fix 3: Enhance Planning Module with Explicit Trigger Reference

**File:** `prompts/shared/help_plan_feature.md`

**Add at the top (after copyright):**

```markdown
---

## 🚨 ACTIVATION TRIGGERS

**This module is automatically activated when user input matches:**

- "plan" or "planning"
- "let's plan [something]"
- "plan a feature"
- "help me plan"
- "I want to plan"

**Trigger keywords defined in:** `cortex-brain/response-templates.yaml` → `routing.planning_triggers`

**When activated:**
1. Load `planning_activation` template
2. Assess confidence level
3. Begin interactive planning workflow
4. Use templates for each stage (question, plan_ready, complete)

---
```

---

### Fix 4: Add Condensed Trigger Section to response-templates-condensed.yaml

**File:** `cortex-brain/response-templates-condensed.yaml`

**Add after line 8 (before templates section):**

```yaml
schema_version: 2.1.0
last_updated: '2025-11-17'
optimization_note: Condensed for token efficiency - full examples in response-templates-docs/

# Trigger routing configuration
routing:
  planning_triggers:
    - plan
    - let's plan
    - plan a feature
    - planning
    - help me plan

templates:
  # ... existing templates ...
```

---

## 📋 Implementation Checklist

### Phase 1: Template Configuration (15 minutes)

- [ ] Add `planning_triggers` to `cortex-brain/response-templates.yaml` routing section
- [ ] Add `routing` section to `cortex-brain/response-templates-condensed.yaml`
- [ ] Validate YAML syntax (no errors)
- [ ] Test trigger keywords cover common planning phrases

### Phase 2: Documentation Updates (20 minutes)

- [ ] Add "Template Trigger Detection" section to CORTEX.prompt.md (after line 10)
- [ ] Add "ACTIVATION TRIGGERS" section to `prompts/shared/help_plan_feature.md`
- [ ] Update examples to reference trigger matching
- [ ] Add troubleshooting section for "planning not activated"

### Phase 3: Testing (15 minutes)

- [ ] Test: "plan a feature" → Should activate planning template
- [ ] Test: "let's plan authentication" → Should activate planning template
- [ ] Test: "help me plan API" → Should activate planning template
- [ ] Test: "add button" → Should NOT activate planning (standard response)
- [ ] Test: Edge case: "Can you plan..." → Should activate if contains "plan"

### Phase 4: Validation (10 minutes)

- [ ] Verify templates load correctly
- [ ] Verify interactive questions are asked
- [ ] Verify plan generation happens
- [ ] Verify Work Planner workflow is mentioned
- [ ] Verify standard format is used for non-planning requests

---

## 🎓 Lessons Learned

### Design Insights

1. **Templates need explicit triggering mechanism** - They don't self-activate
2. **Documentation ≠ Implementation** - Module references must be executable
3. **LLM context != Code execution** - GitHub Copilot reads prompts but doesn't auto-route
4. **Triggers must be comprehensive** - Cover natural language variations

### Architectural Implications

**CORTEX 2.1 needs explicit orchestration instructions:**
- Template detection BEFORE response generation
- Trigger keyword matching as first step
- Module activation based on intent
- Clear precedence rules (planning > standard response)

**Current limitation:** GitHub Copilot Chat doesn't have middleware/routing layer, so orchestration must be embedded in prompt instructions

---

## 🚀 Expected Outcome After Fixes

### Before (Current Behavior)

```
User: "let's plan Azure DevOps enhancements"
        ↓
CORTEX: [Reads prompt] → [Searches] → [Creates todos] → [Generates document]
Result: Direct execution, no planning workflow
```

### After (Fixed Behavior)

```
User: "let's plan Azure DevOps enhancements"
        ↓
CORTEX: [Checks triggers] → [Matches "let's plan"]
        ↓
CORTEX: [Loads planning_activation template]
        ↓
CORTEX: [Displays] "🧠 CORTEX Interactive Planning"
        ↓
CORTEX: [Assesses confidence] Medium (70%) - need clarity
        ↓
CORTEX: [Asks questions]
   1. Which ADO capabilities to enhance? (work items, pipelines, repos?)
   2. Integration depth? (basic API, full workflow automation?)
   3. Timeline constraints?
        ↓
User: [Answers questions]
        ↓
CORTEX: [Generates phase-based plan]
   Phase 1: API Enhancement (Tasks 1-4)
   Phase 2: UI Integration (Tasks 5-8)
   Phase 3: Testing & Docs (Tasks 9-12)
        ↓
CORTEX: "Ready to proceed with all phases, or focus on specific phase?"
```

---

## 📊 Impact Assessment

### User Experience

**Before:**
- User says "let's plan"
- Gets immediate execution
- No opportunity to clarify or refine
- Misses interactive planning benefits

**After:**
- User says "let's plan"
- Gets guided questions
- Collaborative plan creation
- Clear phase-based roadmap
- Choice to execute or refine

### Development Workflow

**Benefits:**
1. ✅ Planning becomes a distinct, recognizable operation
2. ✅ Consistent planning experience across all features
3. ✅ Templates ensure quality and completeness
4. ✅ Work Planner agent explicitly activated
5. ✅ Follows CORTEX 2.1 Interactive Planning design

---

## 🔗 Related Documents

| Document | Relevance |
|----------|-----------|
| `.github/prompts/CORTEX.prompt.md` | Entry point - needs trigger detection instructions |
| `prompts/shared/help_plan_feature.md` | Planning workflow - needs activation trigger reference |
| `cortex-brain/response-templates.yaml` | Full templates - needs planning_triggers added |
| `cortex-brain/response-templates-condensed.yaml` | Condensed templates - needs routing section |
| `CORTEX-2.1-TRACK-A-COMPLETE.md` | Planning feature implementation report |

---

## ✅ Next Steps

1. **Implement Fix 1:** Add planning_triggers to response-templates.yaml
2. **Implement Fix 2:** Add trigger detection section to CORTEX.prompt.md
3. **Implement Fix 3:** Add activation triggers to help_plan_feature.md
4. **Implement Fix 4:** Add routing to response-templates-condensed.yaml
5. **Test with original request:** "let's plan Azure DevOps enhancements"
6. **Validate:** Planning template activates correctly
7. **Document:** Update CORTEX-2.1 completion report with fix

---

**Investigation Complete:** 2025-11-17  
**Status:** Root cause identified, solution designed, ready for implementation  
**Estimated Fix Time:** 60 minutes (4 phases)  
**Priority:** HIGH (affects core CORTEX 2.1 planning feature)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
