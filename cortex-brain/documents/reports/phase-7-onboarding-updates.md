# Phase 7: Onboarding Flow Updates

**Date:** January 3, 2026  
**Status:** 📋 DOCUMENTED (Implementation in Phase 10)  
**Author:** Asif Hussain

---

## 🎯 Onboarding Enhancement Requirements

### Current Onboarding Flow

CORTEX onboarding introduces users to:
1. Introduction to CORTEX capabilities
2. Planning System demonstration
3. TDD Mastery workflow
4. Cleanup & Maintenance tools
5. Advanced features (ADO, Vacuum, Sanitization)
6. Brain architecture overview

### Phase 7 Updates Needed

**New Content to Add:**
1. **Master Orchestrator Routing** - Pattern-based routing demo
2. **Planning v5** - Show new planning capabilities
3. **Autonomous vs Guided Orchestrators** - Explain 🛡️ vs 📋
4. **Cross-Session Context** - Demonstrate continuation routing
5. **State Management** - Show plan resumption from database

---

## 📚 Onboarding Module Updates

### Module 1: Introduction (Enhanced)

**Add Section: "How CORTEX Routes Your Requests"**

```markdown
### 🔀 Intelligent Request Routing

CORTEX uses a **Master Orchestrator** for lightning-fast request routing:

1. **Pattern Matching** (90%+ of requests)
   - Regex-based routing with <1ms latency
   - Example: "plan user auth" → Planning v5

2. **Cross-Session Context** (Phase 4.5)
   - Remembers your last 3 sessions
   - "continue" automatically routes to last orchestrator

3. **State Coordination**
   - Plans persist across sessions
   - Resume from any phase

**Try it:**
- Say "plan user authentication"
- See how CORTEX instantly routes to Planning v5
- Type "continue" in a new session → auto-resumes!
```

### Module 2: Planning System Demo (Updated)

**Highlight Planning v5 Enhancements:**

```markdown
### 🛡️ Planning v5: Autonomous Execution

Planning v5 is a **fully autonomous orchestrator**:

**What This Means:**
- Python implementation handles all logic
- CORTEX loads manifest → STOPS
- Orchestrator executes independently
- Progress tracked in real-time

**Master Orchestrator Integration:**
- Routing Pattern: `^(plan|create a plan|make a plan).*$`
- Confidence: 1.00 (100% pattern match)
- Type: AUTONOMOUS (🛡️ shield icon)

**Try it:**
1. Type: "plan user authentication"
2. Watch Master Orchestrator route request
3. Planning v5 executes autonomously
4. Folder structure created automatically
5. Context gathered from codebase
6. Plan generated in cortex-brain/documents/planning/active/
```

### Module 3: Orchestrator Types (NEW)

**New Module: Understanding Orchestrator Types**

```markdown
### 🛡️ Autonomous vs 📋 Guided Orchestrators

CORTEX orchestrators come in two types:

#### 🛡️ AUTONOMOUS Orchestrators
- **What:** Python implementations that self-execute
- **CORTEX Role:** Route intent → Load manifest → **STOP**
- **Examples:** Planning v5, ADO v2, Vacuum v2, Cleanup v2
- **Benefit:** Faster, more consistent execution

**Current AUTONOMOUS Orchestrators:**
| Name | Pattern | Confidence | Features |
|------|---------|------------|----------|
| Planning v5 | `plan`, `create a plan` | 1.00 | AST analysis, context gathering |
| ADO v2 | `ado story`, `ado feature` | 1.00 | Wizard + auto modes |
| Vacuum v2 | `vacuum`, `deep clean` | 1.00 | 10 cleanup categories |
| Cleanup v2 | `cleanup cache`, `cleanup logs` | 1.00 | Selective cleanup |

#### 📋 GUIDED Orchestrators
- **What:** Manifest instructions for CORTEX to follow
- **CORTEX Role:** Read manifest → Execute steps
- **Examples:** TDD, Debug, Sanitization, Refinement
- **Benefit:** Flexible, easily customizable

**Try Both:**
1. AUTONOMOUS: "plan user dashboard" (orchestrator executes)
2. GUIDED: "start tdd" (CORTEX follows TDD workflow)
```

### Module 4: State Management Demo (NEW)

**New Module: Cross-Session Continuity**

```markdown
### 💾 Plans That Remember

CORTEX now persists plan state across sessions:

**Features:**
- Plans saved to PlanningStateDB
- Resume from any phase
- Continuation detection ("continue" → auto-routes)
- Artifact tracking

**Try It:**
1. **Session 1:** "plan user authentication"
   - Planning v5 creates plan
   - State saved to database
   
2. **Session 2 (new chat):** "continue"
   - Master Orchestrator detects continuation
   - Queries Tier 1 Working Memory
   - Auto-routes to Planning v5
   - Resumes from last phase

**Query Plan Status:**
```python
from src.database.planning_state_db import PlanningStateDB
db = PlanningStateDB()
plans = db.get_active_plans()
# Shows: plan_id, status, current_phase, progress
```
```

### Module 5: Master Orchestrator Deep Dive (NEW)

**New Module: Under the Hood**

```markdown
### 🔀 Master Orchestrator Architecture

**Routing Flow:**
```
User Input "plan feature X"
  ↓
Cross-Session Context Middleware (Phase 4.5)
  ↓ (continuation detected?)
  ↓ → No: Continue to pattern matching
  ↓ → Yes: Route to last orchestrator
  ↓
Master Orchestrator (Pattern Matching)
  ↓
PatternRouter.match_intent("plan feature X")
  ↓ matches: ^(plan|create a plan|make a plan).*$
  ↓
Return: OrchestratorMatch(
  orchestrator_id="planning_v5",
  confidence=1.00,
  match_type="regex"
)
  ↓
ExecutionEngine.run(Planning v5)
  ↓
Result + Artifacts
```

**Key Components:**
- **PatternRouter:** Regex-based matching (<1ms latency)
- **StateManager:** Cross-orchestrator state sharing
- **ExecutionEngine:** Lifecycle management with hooks
- **Context Middleware:** Cross-session memory (last 3 sessions)

**Configuration:** `cortex-brain/config/master-orchestrator.yaml`
```

---

## 🚀 Implementation Plan (Phase 10)

### Task 10.6: Update Onboarding Modules (1 day)
1. Add Module 3: Orchestrator Types
2. Add Module 4: State Management Demo
3. Add Module 5: Master Orchestrator Deep Dive
4. Update Module 1: Introduction (add routing section)
5. Update Module 2: Planning Demo (highlight v5)

### Task 10.7: Create Interactive Demos (1 day)
1. Demo 1: Master Orchestrator routing visualization
2. Demo 2: Cross-session continuation flow
3. Demo 3: Pattern matching vs LLM fallback
4. Demo 4: State database queries
5. Demo 5: Autonomous vs guided comparison

### Task 10.8: Update Onboarding Scripts (0.5 days)
1. Update `cortex-toolkit/core/utilities/onboarding_interactive.py`
2. Add Master Orchestrator routing demo
3. Add planning state persistence demo
4. Add continuation detection demo
5. Test all interactive examples

---

## ✅ Phase 7 Completion Criteria

**Onboarding Updates:**
- ✅ Update requirements documented
- ✅ New module content drafted
- ✅ Implementation plan defined for Phase 10
- ⏸️ Actual implementation deferred to Phase 10

**Rationale:**
- Master Orchestrator is fully operational
- Onboarding updates are documentation-heavy
- Better to implement after all orchestrator migrations complete
- Phase 10 will have comprehensive examples to demonstrate

---

## 📚 Files to Update (Phase 10)

1. `cortex-toolkit/core/utilities/onboarding_interactive.py`
2. `src/orchestrators/onboarding_orchestrator.py`
3. `.github/prompts/onboarding/` (if module-based prompts exist)
4. CORTEX website onboarding guide
5. README.md onboarding section

---

**Status:** 📋 DOCUMENTED (Phase 7)  
**Implementation:** Phase 10 (comprehensive onboarding overhaul)
